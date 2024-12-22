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
if "game_active" not in st.session_state:
    st.session_state.game_active = False
if "game_over" not in st.session_state:
    st.session_state.game_over = False

# Generate maze
def generate_maze(width, height):
    maze = np.ones((height, width), dtype=int)
    stack = [(1, 1)]
    maze[1, 1] = 0  # Start point is a path

    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while stack:
        current = stack[-1]
        x, y = current
        neighbors = []

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < height - 1 and 1 <= ny < width - 1 and maze[nx, ny] == 1:
                neighbors.append((nx, ny))

        if neighbors:
            nx, ny = random.choice(neighbors)
            maze[(x + nx) // 2, (y + ny) // 2] = 0
            maze[nx, ny] = 0
            stack.append((nx, ny))
        else:
            stack.pop()

    return maze

# Display maze
def display_maze(maze, position, goal):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(maze, cmap="binary", origin="upper")

    px, py = position
    gx, gy = goal
    ax.scatter(py, px, color="blue", s=100, label="Player")
    ax.scatter(gy, gx, color="red", s=100, label="Goal")
    ax.legend(loc="upper right")
    ax.set_xticks([])
    ax.set_yticks([])
    st.pyplot(fig)

# Start game
def start_game():
    width, height = 21, 21
    st.session_state.maze = generate_maze(width, height)
    st.session_state.position = (1, 1)
    st.session_state.goal = (height - 2, width - 2)
    st.session_state.start_time = time.time()
    st.session_state.game_active = True
    st.session_state.game_over = False

# Move player
def move_player(direction):
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
st.title("Swipe & Keyboard Maze Game")

if not st.session_state.game_active:
    if st.button("Start New Game"):
        start_game()

if st.session_state.maze is not None:
    # Timer
    if st.session_state.game_active:
        elapsed_time = time.time() - st.session_state.start_time
        st.markdown(f"### ⏱️ Time: {elapsed_time:.2f} seconds")

    # Display the maze
    display_maze(st.session_state.maze, st.session_state.position, st.session_state.goal)

    # Handle Swipe & Keyboard Input
    st.markdown("""
        <script>
        let touchstartX = 0
        let touchstartY = 0
        let touchendX = 0
        let touchendY = 0

        document.addEventListener('keydown', function(event) {
            let direction = null;
            if (event.key === "ArrowUp") direction = "up";
            if (event.key === "ArrowDown") direction = "down";
            if (event.key === "ArrowLeft") direction = "left";
            if (event.key === "ArrowRight") direction = "right";
            if (direction) {
                fetch(`/move/${direction}`);
            }
        });

        document.addEventListener('touchstart', function(event) {
            touchstartX = event.changedTouches[0].screenX;
            touchstartY = event.changedTouches[0].screenY;
        });

        document.addEventListener('touchend', function(event) {
            touchendX = event.changedTouches[0].screenX;
            touchendY = event.changedTouches[0].screenY;
            let direction = null;
            if (touchendX < touchstartX - 50) direction = "left";
            if (touchendX > touchstartX + 50) direction = "right";
            if (touchendY < touchstartY - 50) direction = "up";
            if (touchendY > touchstartY + 50) direction = "down";
            if (direction) {
                fetch(`/move/${direction}`);
            }
        });
        </script>
    """, unsafe_allow_html=True)

    # Check if player reached the goal
    if st.session_state.position == st.session_state.goal:
        st.session_state.game_active = False
        st.session_state.game_over = True
        time_taken = time.time() - st.session_state.start_time
        st.success(f"🎉 You reached the goal in {time_taken:.2f} seconds!")

# Leaderboard
if st.session_state.game_over:
    nickname = st.text_input("Enter your nickname:")
    if st.button("Submit Score"):
        if nickname:
            time_taken = time.time() - st.session_state.start_time
            add_to_ranking(nickname, time_taken)
            st.write("Score saved!")
        else:
            st.warning("Please enter a nickname.")
    st.write("### Leaderboard")
    st.dataframe(st.session_state.ranking)
