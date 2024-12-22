import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
import time

# Initialize session state
if "maze" not in st.session_state:
    st.session_state.maze = None
if "position" not in st.session_state:
    st.session_state.position = (1, 1)
if "goal" not in st.session_state:
    st.session_state.goal = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# Generate maze using Prim's Algorithm
def generate_maze(width, height):
    maze = np.ones((height, width), dtype=int)  # Create grid full of walls
    start = (1, 1)
    maze[start] = 0  # Start point as path
    walls = [(1, 2), (2, 1)]  # Walls adjacent to start

    while walls:
        wall = random.choice(walls)
        walls.remove(wall)
        x, y = wall

        # Check neighbors
        neighbors = []
        if x > 1 and maze[x - 2, y] == 0:
            neighbors.append((x - 2, y))
        if x < height - 2 and maze[x + 2, y] == 0:
            neighbors.append((x + 2, y))
        if y > 1 and maze[x, y - 2] == 0:
            neighbors.append((x, y - 2))
        if y < width - 2 and maze[x, y + 2] == 0:
            neighbors.append((x, y + 2))

        if neighbors:
            nx, ny = random.choice(neighbors)
            maze[x, y] = 0
            maze[(x + nx) // 2, (y + ny) // 2] = 0
            maze[nx, ny] = 0

            # Add new walls
            if nx > 1 and maze[nx - 2, ny] == 1:
                walls.append((nx - 1, ny))
            if nx < height - 2 and maze[nx + 2, ny] == 1:
                walls.append((nx + 1, ny))
            if ny > 1 and maze[nx, ny - 2] == 1:
                walls.append((nx, ny - 1))
            if ny < width - 2 and maze[nx, ny + 2] == 1:
                walls.append((nx, ny + 1))

    return maze

# Display maze using matplotlib
def display_maze(maze, position, goal):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(maze, cmap="binary", origin="upper")

    # Highlight player position
    px, py = position
    gx, gy = goal
    ax.scatter(py, px, color="blue", s=100, label="Player")
    ax.scatter(gy, gx, color="red", s=100, label="Goal")
    ax.legend(loc="upper right")
    ax.set_xticks([])
    ax.set_yticks([])
    st.pyplot(fig)

# Start the game
def start_game():
    width, height = 21, 21  # Maze dimensions (odd numbers)
    st.session_state.maze = generate_maze(width, height)
    st.session_state.position = (1, 1)  # Start position
    st.session_state.goal = (height - 2, width - 2)  # Goal position
    st.session_state.start_time = time.time()

# Move player
def move(direction):
    x, y = st.session_state.position
    maze = st.session_state.maze

    if direction == "up" and x > 0 and maze[x - 1, y] == 0:
        st.session_state.position = (x - 1, y)
    elif direction == "down" and x < maze.shape[0] - 1 and maze[x + 1, y] == 0:
        st.session_state.position = (x + 1, y)
    elif direction == "left" and y > 0 and maze[x, y - 1] == 0:
        st.session_state.position = (x, y - 1)
    elif direction == "right" and y < maze.shape[1] - 1 and maze[x, y + 1] == 0:
        st.session_state.position = (x, y + 1)

# Main app
st.title("Maze Game")
st.write("Navigate the maze and reach the goal!")

if st.button("Start New Game"):
    start_game()

if st.session_state.maze is not None:
    # Display the maze
    display_maze(st.session_state.maze, st.session_state.position, st.session_state.goal)

    # Movement buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Left"):
            move("left")
    with col2:
        if st.button("⬆️ Up"):
            move("up")
        if st.button("⬇️ Down"):
            move("down")
    with col3:
        if st.button("➡️ Right"):
            move("right")

    # Check if the player reached the goal
    if st.session_state.position == st.session_state.goal:
        time_taken = time.time() - st.session_state.start_time
        st.success(f"🎉 You reached the goal in {time_taken:.2f} seconds!")
