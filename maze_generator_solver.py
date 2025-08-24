import random
from enum import Enum
import sys
import cv2 as cv
import numpy as np
from collections import deque
import simpleaudio as sa

sys.setrecursionlimit(8000)

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class MazeGenerator:

    def __init__(self, width, height):
        if width % 2 == 0:
            width += 1
        if height % 2 == 0:
            height += 1
        self.width = width
        self.height = height
        self.maze = None

    def create_maze(self):
        maze = np.ones((self.height, self.width), dtype=np.float64)

        for i in range(self.height):
            for j in range(self.width):
                if i % 2 == 0 or j % 2 == 0:
                    maze[i, j] = 0
                if i == 0 or j == 0 or i == self.height - 1 or j == self.width - 1:
                    maze[i, j] = 0

        sx = random.choice(range(1, self.width - 1, 2))
        sy = random.choice(range(1, self.height - 1, 2))

        self.generate(sx, sy, maze)

        maze[maze == 0.5] = 1

        maze[1, 0] = 1
        maze[self.height - 2, self.width - 1] = 1

        self.maze = maze
        return maze

    def generate(self, cx, cy, grid):
        grid[cy, cx] = 0.5
        directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        random.shuffle(directions)

        for dir in directions:
            if dir == Direction.UP:
                nx, ny = cx, cy - 2
                mx, my = cx, cy - 1
            elif dir == Direction.DOWN:
                nx, ny = cx, cy + 2
                mx, my = cx, cy + 1
            elif dir == Direction.RIGHT:
                nx, ny = cx + 2, cy
                mx, my = cx + 1, cy
            elif dir == Direction.LEFT:
                nx, ny = cx - 2, cy
                mx, my = cx - 1, cy

            if 0 < nx < self.width-1 and 0 < ny < self.height-1 and grid[ny, nx] != 0.5:
                grid[my, mx] = 0.5
                self.generate(nx, ny, grid)

    def display(self, scale=20):
        display_maze = (self.maze * 255)
        width = self.width * scale
        height = self.height * scale
        large_maze = cv.resize(display_maze, (width, height), interpolation=cv.INTER_NEAREST)
        cv.imshow('Maze', large_maze)
        cv.waitKey(0)

class MazeSolver:

    def __init__(self, maze):
        self.maze = maze
        self.height, self.width = maze.shape
        self.start = (1, 0)
        self.end = (self.height - 2, self.width - 1)
        self.parent = {}

    def solveMaze(self, scale=20):
        display_maze = (self.maze * 255).astype(np.uint8)
        display_maze = cv.cvtColor(display_maze, cv.COLOR_GRAY2BGR)

        q = deque([self.start])
        visited = set([self.start])
        self.parent = {self.start : None}

        while q:

            cy, cx = q.popleft()
            display_maze[cy, cx] = (100, 100, 100)
            resized = cv.resize(display_maze, (self.width*scale, self.height*scale), interpolation=cv.INTER_NEAREST)
            cv.imshow("Maze", resized)
            cv.waitKey(20)

            if(cy, cx) == self.end:
                break

            for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                ny, nx = cy+dy, cx+dx
                if 0 <= ny <= self.width or 0 <= nx <= self.height:
                    if self.maze[ny, nx] == 1 and (ny, nx) not in visited:
                        visited.add((ny, nx))
                        self.parent[ny, nx] = (cy, cx)
                        q.append((ny, nx))

            path = []
            node = self.end
            while node:
                path.append(node)
                node = self.parent.get(node, None)
            path.reverse()
            sa.WaveObject.from_wave_file("found.wav").play()

            for (py, px) in path:
                display_maze[py, px] = (0, 255, 0)
                resized = cv.resize(display_maze, (self.width*scale, self.height*scale), interpolation=cv.INTER_NEAREST)
                cv.imshow("Maze", resized)
                cv.waitKey(20)

        cv.destroyAllWindows()



dimension = int(input("Enter the dimension of the grid you want to create: "))
mazegenerator = MazeGenerator(dimension, dimension)
finalMaze = mazegenerator.create_maze()
mazegenerator.display()

print("MAZE GENERATED!!!!, PRESS ANY KEY IN THE MAZE WINDOW TO START SOLVING.")

solver = MazeSolver(finalMaze)
solver.solveMaze()
cv.waitKey(0)
