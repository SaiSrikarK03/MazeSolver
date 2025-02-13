# MazeSolver
Maze Solver is an interactive Python project with a Tkinter GUI that generates random mazes via recursive backtracking and solves them using BFS, DFS, Dijkstra, and A*. It features interactive start/end selection and controls for animation speed, zoom, and pause/resume.


# Maze Solver

Maze Solver is an interactive Python application that generates and solves mazes with a graphical interface using Tkinter. It demonstrates maze generation with recursive backtracking and solves the maze using BFS, DFS, Dijkstra, and A* algorithms.

# Image

![image alt](https://github.com/SaiSrikarK03/MazeSolver/blob/7f9be97991e1bb34e8600a6aad59aaabc4e027fb/maze.png)

## Overview

- Maze Generation: Uses a recursive backtracking algorithm to create a maze represented as a 2D grid (walls = 1, passages = 0).
- Pathfinding Algorithms: Supports BFS, DFS, Dijkstra, and A* to find the optimal path.
- Interactive GUI: Choose maze dimensions, select start/end points, and watch the solving animation.
- Animation Controls: Adjust animation speed via a slider and pause/resume the visualization.

## How It Works

1. Generate Maze: Enter the desired odd-number dimensions and click "Generate Maze". The maze is created using recursive backtracking.
2. Set Points: Use "Select Start Point" and "Select End Point" to mark the maze's entry and exit.
3. Solve Maze: Choose a search algorithm and click "Solve Maze". The application animates the search process, showing how the algorithm explores the maze.
4. Animation Control: Adjust the animation delay with the slider or pause/resume the animation to inspect each step.

## Requirements

- Python 3.x (with Tkinter included)

## Installation

1. **Clone the repository:**
   ```bash
   
   git clone https://github.com/SaiSrikarK03/MazeSolver.git
   cd maze-solver
  Run the application:
  
    python maze_solver.py
    
## Usage

-Generate Maze: Input maze dimensions and click "Generate Maze".
-Select Points: Click "Select Start Point" or "Select End Point" and then click on the corresponding cell.
-Solve Maze: Click "Solve Maze" to animate the solving process.
-Animation Controls: Use the slider to adjust speed and the pause/resume button to control the animation.
-Restart/New Maze: Use the provided buttons to restart the search on the current maze or create a new maze.

## Code Structure
-generate_maze Function: Implements maze generation using recursive backtracking.
-MazeApp Class: Contains the GUI setup, event bindings, and all logic for maze generation, drawing, and solving animations.
-Animation Functions: Separate methods for animating BFS, DFS, Dijkstra, and A* searches with controls for speed and pause/resume.
-Future Enhancements
-Add alternative maze generation algorithms.
-Implement additional pathfinding methods.
-Enhance the GUI with additional interactive features.
-Allow exporting the maze as an image or data file.

## License
This project is licensed under the MIT License.
