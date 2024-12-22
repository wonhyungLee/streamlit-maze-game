import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
import time
import pandas as pd

# Initialize session state
if "maze" not in st.session_state:
    st.session_state.maze = None
if "position" not in st.session_state:
    st.session_state.position = (1, 1)
if "goal" not in st.session_state:
    st.session_state.goal = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "current_time" not in st.session_state:
    st.session_state.current_time = None
if "ranking" not in st.session_state:
    st.session_state.ranking = pd.DataFrame(columns=["Nickname", "Time (s)"])
if "game_over" not in st.session_state:
    st.session_state.game_over = False

# Generate maze using Depth-First Search
def generate_maze(width, height):
    maze = np.ones((height, width), dtype=int)  # Start with walls
    stack = []
    start = (1, 1)
    maze[start] = 0  # Start point as path
    stack.append(start)

    # Directions for movement (up, down, left, right)
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while stack:
        current = stack[-1]
        x, y = current

        # Find unvisited neighbors
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < height - 1 and 1 <= ny < width - 1 and maze[nx, ny] == 1:
                neighbors.append((nx, ny))

        if neighbors:
            # Choose a random neighbor
            next_cell = random.choice(neighbors)
            nx, ny = next_cell

            # Remove the wall between the current cell and the next cell
            maze[(x + nx) // 2, (y + ny) // 2] = 0
            maze[nx, ny] = 0
            stack.append(next_cell)
        else:
            stack.pop()

    return maze

# Display maze using matplotlib
def display_maze(maze, position, goal):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(maze, cmap="binary", origin="upper")

    # Highlight player position and goal
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
    st.session_state.current_time = st.session_state.start_time
    st.session_state.game_over = False

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

# Add to ranking
def add_to_ranking(nickname, time_taken):
    new_entry = {"Nickname": nickname, "Time (s)": round(time_taken, 2)}
    st.session_state.ranking = pd.concat([st.session_state.ranking, pd.DataFrame([new_entry])])
    st.session_state.ranking = st.session_state.ranking.sort_values(by="Time (s)").reset_index(drop=True)

# Main app
st.title("Maze Game")
st.write("Navigate the maze and reach the goal!")

if st.button("Start New Game"):
    start_game()

if st.session_state.maze is not None and st.session_state.start_time is not None:
    # Timer Banner
    if not st.session_state.game_over:
        elapsed_time = time.time() - st.session_state.start_time
        st.markdown(f"### ⏱️ Time: {elapsed_time:.2f} seconds")

    # Display the maze
    display_maze(st.session_state.maze, st.session_state.position, st.session_state.goal)

    # Handle Keyboard Input (for PC users)
    st.markdown("""
        <script>
        document.addEventListener("keydown", function(event) {
            let action = null;
            if (event.key === "ArrowUp") action = "up";
            if (event.key === "ArrowDown") action = "down";
            if (event.key === "ArrowLeft") action = "left";
            if (event.key === "ArrowRight") action = "right";
            if (action) {
                fetch("/move/" + action);
            }
        });
        </script>
    """, unsafe_allow_html=True)

    # Check if the player reached the goal
    if st.session_state.position == st.session_state.goal and not st.session_state.game_over:
        time_taken = time.time() - st.session_state.start_time
        st.session_state.game_over = True
        st.success(f"🎉 You reached the goal in {time_taken:.2f} seconds!")

        # Nickname input for leaderboard
        nickname = st.text_input("Enter your nickname to save your score:")
        if st.button("Submit Score"):
            if nickname:
                add_to_ranking(nickname, time_taken)
                st.write("Score saved!")
            else:
                st.warning("Please enter a nickname!")

# Display leaderboard
st.write("### Leaderboard")
st.dataframe(st.session_state.ranking)
