import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import heapq  # for Dijkstra and A*

# --------------------------
# Configuration constants
# --------------------------
CELL_DEFAULT_SIZE = 20     # Base cell size (will be scaled by zoom factor)
CANVAS_WIDTH = 700
CANVAS_HEIGHT = 700

# --------------------------
# Maze generation (recursive backtracking)
# --------------------------
def generate_maze(width, height):
    """
    Generate a maze as a 2D grid using a modified recursive backtracking algorithm.
    Walls are represented by 1 and passages by 0.
    Maze dimensions are forced to be odd.
    
    This version uses a list of carved cells and randomly selects one (instead of LIFO)
    to carve from. This produces more splits, dead ends, and branching paths.
    """
    if width % 2 == 0:
        width += 1
    if height % 2 == 0:
        height += 1

    # Create grid full of walls.
    maze = [[1 for _ in range(width)] for _ in range(height)]
    
    # Start at cell (1,1)
    start = (1, 1)
    maze[1][1] = 0
    cell_list = [start]

    while cell_list:
        # Pick a random cell from the list to encourage branching.
        x, y = random.choice(cell_list)
        neighbors = []
        for dx, dy in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
            nx, ny = x + dx, y + dy
            if 0 < nx < width and 0 < ny < height and maze[ny][nx] == 1:
                neighbors.append((nx, ny, dx, dy))
        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            # Remove wall between current cell and chosen neighbor.
            maze[y + dy//2][x + dx//2] = 0
            maze[ny][nx] = 0
            cell_list.append((nx, ny))
        else:
            cell_list.remove((x, y))
    return maze

# --------------------------
# Main Application Class
# --------------------------
class MazeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Maze Generator and Solver")
        self.geometry(f"{CANVAS_WIDTH+220}x{CANVAS_HEIGHT+20}")
        
        # Variables
        self.maze_width_var = tk.IntVar(value=21)
        self.maze_height_var = tk.IntVar(value=21)
        self.algorithm_var = tk.StringVar(value="BFS")
        self.zoom_scale = 1.0
        
        # New variables for animation control
        self.animation_delay_var = tk.IntVar(value=50)  # Delay in ms
        self.paused = False
        
        # Maze data and solution state
        self.maze = None         # 2D list: 1 = wall, 0 = passage
        self.start_point = None  # (x, y) grid coordinates
        self.end_point = None
        self.solving = False
        self.search_start_time = None
        self.search_time = 0
        self.search_nodes = []
        self.parents = {}        # For path reconstruction
        self.distances = {}      # For Dijkstra and A*
        
        # UI setup
        self.create_widgets()
        self.bind_events()

    def create_widgets(self):
        # Set theme and configure styles
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Control.TFrame", background="#2e2e2e")
        style.configure("Control.TLabel", background="#2e2e2e", foreground="white", font=("Helvetica", 10))
        style.configure("Control.TButton", font=("Helvetica", 10))
        style.configure("TEntry", font=("Helvetica", 10))
        
        # --- Right-side control frame ---
        control_frame = ttk.Frame(self, style="Control.TFrame", padding=10)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        # Maze dimension entries
        ttk.Label(control_frame, text="Maze Width (odd):", style="Control.TLabel").pack(anchor=tk.W, pady=(0,2))
        ttk.Entry(control_frame, textvariable=self.maze_width_var, width=10).pack(anchor=tk.W, pady=(0,5))
        ttk.Label(control_frame, text="Maze Height (odd):", style="Control.TLabel").pack(anchor=tk.W, pady=(0,2))
        ttk.Entry(control_frame, textvariable=self.maze_height_var, width=10).pack(anchor=tk.W, pady=(0,5))
        
        # Algorithm drop-down
        ttk.Label(control_frame, text="Algorithm:", style="Control.TLabel").pack(anchor=tk.W, pady=(10,2))
        algo_options = ["BFS", "DFS", "Dijkstra", "A*"]
        ttk.OptionMenu(control_frame, self.algorithm_var, self.algorithm_var.get(), *algo_options).pack(anchor=tk.W, pady=(0,5))
        
        # Buttons for maze operations
        ttk.Button(control_frame, text="Generate Maze", command=self.on_generate_maze, style="Control.TButton").pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Select Start Point", command=self.on_select_start, style="Control.TButton").pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Select End Point", command=self.on_select_end, style="Control.TButton").pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Solve Maze", command=self.on_solve_maze, style="Control.TButton").pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Restart Search (Same Maze)", command=self.on_restart_search, style="Control.TButton").pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="New Maze", command=self.on_new_maze, style="Control.TButton").pack(fill=tk.X, pady=5)
        
        # Animation controls: Speed slider and Pause/Resume button
        ttk.Label(control_frame, text="Animation Delay (ms):", style="Control.TLabel").pack(anchor=tk.W, pady=(10,2))
        ttk.Scale(control_frame, from_=10, to=200, orient=tk.HORIZONTAL, variable=self.animation_delay_var).pack(fill=tk.X, pady=(0,5))
        self.pause_button = ttk.Button(control_frame, text="Pause Animation", command=self.toggle_pause, style="Control.TButton")
        self.pause_button.pack(fill=tk.X, pady=5)
        
        # Time taken label
        self.time_label = ttk.Label(control_frame, text="Time: 0.0 s", style="Control.TLabel")
        self.time_label.pack(anchor=tk.W, pady=(10,0))
        
        # --- Canvas for maze visualization ---
        self.canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white",
                                highlightthickness=1, highlightbackground="#333333")
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
    def bind_events(self):
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
    
    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="Resume Animation")
        else:
            self.pause_button.config(text="Pause Animation")
    
    def on_generate_maze(self):
        width = self.maze_width_var.get()
        height = self.maze_height_var.get()
        self.maze = generate_maze(width, height)
        self.start_point = None
        self.end_point = None
        self.solving = False
        self.search_time = 0
        self.search_start_time = None
        self.parents = {}
        self.search_nodes = []
        self.distances = {}
        self.draw_maze()
    
    def on_select_start(self):
        self.selection_mode = "start"
        messagebox.showinfo("Select Start", "Click a passage cell to set the start point (green).")
    
    def on_select_end(self):
        self.selection_mode = "end"
        messagebox.showinfo("Select End", "Click a passage cell to set the end point (red).")
    
    def on_canvas_click(self, event):
        if self.maze is None:
            return
        cell_size = CELL_DEFAULT_SIZE * self.zoom_scale
        x = int(event.x / cell_size)
        y = int(event.y / cell_size)
        if self.maze[y][x] != 0:
            return
        if hasattr(self, "selection_mode"):
            if self.selection_mode == "start":
                self.start_point = (x, y)
            elif self.selection_mode == "end":
                self.end_point = (x, y)
            del self.selection_mode
            self.draw_maze()
    
    def on_solve_maze(self):
        if self.maze is None:
            messagebox.showerror("Error", "Generate a maze first!")
            return
        if self.start_point is None or self.end_point is None:
            messagebox.showerror("Error", "Please select both start and end points!")
            return
        
        algo = self.algorithm_var.get()
        self.solving = True
        self.search_start_time = time.time()
        self.parents = {}
        self.search_nodes = []
        self.distances = {}
        sx, sy = self.start_point
        if algo == "Dijkstra":
            self.distances[(sx, sy)] = 0
            heapq.heappush(self.search_nodes, (0, (sx, sy)))
        elif algo == "A*":
            self.distances[(sx, sy)] = 0
            heapq.heappush(self.search_nodes, (0, 0, (sx, sy)))
        else:
            self.search_nodes.append((sx, sy))
        self.parents[(sx, sy)] = None
        
        if algo == "BFS":
            self.animate_bfs()
        elif algo == "DFS":
            self.animate_dfs()
        elif algo == "Dijkstra":
            self.animate_dijkstra()
        elif algo == "A*":
            self.animate_astar()
        else:
            self.animate_bfs()
    
    def on_restart_search(self):
        if self.maze is None or self.start_point is None or self.end_point is None:
            return
        self.draw_maze()
        self.solving = True
        self.search_start_time = time.time()
        self.parents = {}
        self.search_nodes = []
        self.distances = {}
        sx, sy = self.start_point
        if self.algorithm_var.get() == "Dijkstra":
            self.distances[(sx, sy)] = 0
            heapq.heappush(self.search_nodes, (0, (sx, sy)))
        elif self.algorithm_var.get() == "A*":
            self.distances[(sx, sy)] = 0
            heapq.heappush(self.search_nodes, (0, 0, (sx, sy)))
        else:
            self.search_nodes.append((sx, sy))
        self.parents[(sx, sy)] = None
        
        algo = self.algorithm_var.get()
        if algo == "BFS":
            self.animate_bfs()
        elif algo == "DFS":
            self.animate_dfs()
        elif algo == "Dijkstra":
            self.animate_dijkstra()
        elif algo == "A*":
            self.animate_astar()
        else:
            self.animate_bfs()
    
    def on_new_maze(self):
        self.maze = None
        self.start_point = None
        self.end_point = None
        self.solving = False
        self.canvas.delete("all")
        self.time_label.config(text="Time: 0.0 s")
    
    def on_mousewheel(self, event):
        if event.delta > 0 or event.num == 4:
            factor = 1.1
        else:
            factor = 0.9
        self.zoom_scale *= factor
        self.canvas.scale("all", 0, 0, factor, factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def draw_maze(self):
        self.canvas.delete("all")
        if self.maze is None:
            return
        rows = len(self.maze)
        cols = len(self.maze[0])
        cell_size = CELL_DEFAULT_SIZE * self.zoom_scale
        for y in range(rows):
            for x in range(cols):
                x1 = x * cell_size
                y1 = y * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                fill_color = "black" if self.maze[y][x] == 1 else "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="#555555")
        if self.start_point:
            sx, sy = self.start_point
            self.draw_cell(sx, sy, fill="green")
        if self.end_point:
            ex, ey = self.end_point
            self.draw_cell(ex, ey, fill="red")
    
    def draw_cell(self, x, y, fill):
        cell_size = CELL_DEFAULT_SIZE * self.zoom_scale
        x1 = x * cell_size
        y1 = y * cell_size
        x2 = x1 + cell_size
        y2 = y1 + cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#555555")
    
    # --------------------------
    # Animation Functions with Speed and Pause Controls
    # --------------------------
    def animate_bfs(self):
        if not self.solving:
            return
        if self.paused:
            self.after(100, self.animate_bfs)
            return
        if not self.search_nodes:
            messagebox.showinfo("No Solution", "No path found!")
            self.solving = False
            return
        current = self.search_nodes.pop(0)
        cx, cy = current
        if current == self.end_point:
            self.solving = False
            self.search_time = time.time() - self.search_start_time
            self.time_label.config(text=f"Time: {self.search_time:.2f} s")
            self.draw_solution_path()
            return
        for dx, dy in [(1,0), (0,1), (-1,0), (0,-1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < len(self.maze[0]) and 0 <= ny < len(self.maze):
                if self.maze[ny][nx] == 0 and (nx, ny) not in self.parents:
                    self.parents[(nx, ny)] = (cx, cy)
                    self.search_nodes.append((nx, ny))
                    self.draw_cell(nx, ny, fill="lightblue")
        self.after(self.animation_delay_var.get(), self.animate_bfs)
    
    def animate_dfs(self):
        if not self.solving:
            return
        if self.paused:
            self.after(100, self.animate_dfs)
            return
        if not self.search_nodes:
            messagebox.showinfo("No Solution", "No path found!")
            self.solving = False
            return
        current = self.search_nodes.pop()
        cx, cy = current
        if current == self.end_point:
            self.solving = False
            self.search_time = time.time() - self.search_start_time
            self.time_label.config(text=f"Time: {self.search_time:.2f} s")
            self.draw_solution_path()
            return
        for dx, dy in [(1,0), (0,1), (-1,0), (0,-1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < len(self.maze[0]) and 0 <= ny < len(self.maze):
                if self.maze[ny][nx] == 0 and (nx, ny) not in self.parents:
                    self.parents[(nx, ny)] = (cx, cy)
                    self.search_nodes.append((nx, ny))
                    self.draw_cell(nx, ny, fill="lightblue")
        self.after(self.animation_delay_var.get(), self.animate_dfs)
    
    def animate_dijkstra(self):
        if not self.solving:
            return
        if self.paused:
            self.after(100, self.animate_dijkstra)
            return
        if not self.search_nodes:
            messagebox.showinfo("No Solution", "No path found!")
            self.solving = False
            return
        cost, current = heapq.heappop(self.search_nodes)
        cx, cy = current
        if current == self.end_point:
            self.solving = False
            self.search_time = time.time() - self.search_start_time
            self.time_label.config(text=f"Time: {self.search_time:.2f} s")
            self.draw_solution_path()
            return
        for dx, dy in [(1,0), (0,1), (-1,0), (0,-1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < len(self.maze[0]) and 0 <= ny < len(self.maze):
                if self.maze[ny][nx] == 0:
                    new_cost = cost + 1
                    if (nx, ny) not in self.distances or new_cost < self.distances[(nx, ny)]:
                        self.distances[(nx, ny)] = new_cost
                        self.parents[(nx, ny)] = (cx, cy)
                        heapq.heappush(self.search_nodes, (new_cost, (nx, ny)))
                        self.draw_cell(nx, ny, fill="lightblue")
        self.after(self.animation_delay_var.get(), self.animate_dijkstra)
    
    def animate_astar(self):
        if not self.solving:
            return
        if self.paused:
            self.after(100, self.animate_astar)
            return
        if not self.search_nodes:
            messagebox.showinfo("No Solution", "No path found!")
            self.solving = False
            return
        f, g, current = heapq.heappop(self.search_nodes)
        cx, cy = current
        if current == self.end_point:
            self.solving = False
            self.search_time = time.time() - self.search_start_time
            self.time_label.config(text=f"Time: {self.search_time:.2f} s")
            self.draw_solution_path()
            return
        for dx, dy in [(1,0), (0,1), (-1,0), (0,-1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < len(self.maze[0]) and 0 <= ny < len(self.maze):
                if self.maze[ny][nx] == 0:
                    new_g = g + 1
                    h = abs(nx - self.end_point[0]) + abs(ny - self.end_point[1])
                    new_f = new_g + h
                    if (nx, ny) not in self.distances or new_g < self.distances[(nx, ny)]:
                        self.distances[(nx, ny)] = new_g
                        self.parents[(nx, ny)] = (cx, cy)
                        heapq.heappush(self.search_nodes, (new_f, new_g, (nx, ny)))
                        self.draw_cell(nx, ny, fill="lightblue")
        self.after(self.animation_delay_var.get(), self.animate_astar)
    
    def draw_solution_path(self):
        path = []
        cur = self.end_point
        while cur is not None:
            path.append(cur)
            cur = self.parents.get(cur)
        for (x, y) in path:
            self.draw_cell(x, y, fill="yellow")
        self.time_label.config(text=f"Time: {self.search_time:.2f} s (Solved)")
        messagebox.showinfo("Maze Solved", "Maze solved!")

# --------------------------
# Main entry point
# --------------------------
if __name__ == "__main__":
    app = MazeApp()
    app.mainloop()
