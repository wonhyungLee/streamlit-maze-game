import streamlit as st
import time
import numpy as np
import pandas as pd

# Global Variables
if "maze" not in st.session_state:
    st.session_state.maze = None
if "position" not in st.session_state:
    st.session_state.position = (0, 0)
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "ranking" not in st.session_state:
    st.session_state.ranking = pd.DataFrame(columns=["Nickname", "Time (s)"])

# Generate Maze
def generate_maze(size):
    maze = np.zeros((size, size))
    maze[1:-1, 1:-1] = 1  # Create paths
    maze[-2, -2] = 2  # Exit point
    return maze

# Display Maze
def display_maze(maze, position):
    for row in range(maze.shape[0]):
        for col in range(maze.shape[1]):
            if (row, col) == position:
                st.write("🟦", end=" ")  # Player
            elif maze[row, col] == 0:
                st.write("⬛", end=" ")  # Wall
            elif maze[row, col] == 1:
                st.write("⬜", end=" ")  # Path
            elif maze[row, col] == 2:
                st.write("🏁", end=" ")  # Exit
        st.write("")

# Check if the player reaches the goal
def is_goal_reached(position, maze):
    return maze[position] == 2

# Initialize the game
def start_game():
    st.session_state.maze = generate_maze(10)
    st.session_state.position = (1, 1)
    st.session_state.start_time = time.time()

# Game Control
def move(direction):
    row, col = st.session_state.position
    maze = st.session_state.maze

    if direction == "up" and row > 0 and maze[row - 1, col] != 0:
        st.session_state.position = (row - 1, col)
    elif direction == "down" and row < maze.shape[0] - 1 and maze[row + 1, col] != 0:
        st.session_state.position = (row + 1, col)
    elif direction == "left" and col > 0 and maze[row, col - 1] != 0:
        st.session_state.position = (row, col - 1)
    elif direction == "right" and col < maze.shape[1] - 1 and maze[row, col + 1] != 0:
        st.session_state.position = (row, col + 1)

# Add to Ranking
def add_to_ranking(nickname, time_taken):
    new_entry = {"Nickname": nickname, "Time (s)": round(time_taken, 2)}
    st.session_state.ranking = pd.concat([st.session_state.ranking, pd.DataFrame([new_entry])])
    st.session_state.ranking = st.session_state.ranking.sort_values(by="Time (s)").reset_index(drop=True)

# Main App
st.title("Streamlit Maze Game")
st.write("Use the buttons to navigate through the maze and reach the 🏁!")

if st.button("Start New Game"):
    start_game()

if st.session_state.maze is not None:
    st.write("### Maze")
    display_maze(st.session_state.maze, st.session_state.position)

    # Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️"):
            move("left")
    with col2:
        if st.button("⬆️"):
            move("up")
    with col3:
        if st.button("➡️"):
            move("right")
    if st.button("⬇️"):
        move("down")

    # Check if goal is reached
    if is_goal_reached(st.session_state.position, st.session_state.maze):
        time_taken = time.time() - st.session_state.start_time
        st.success(f"🎉 You reached the goal in {time_taken:.2f} seconds!")
        nickname = st.text_input("Enter your nickname to save your score:", key="nickname_input")
        if st.button("Submit Score"):
            if nickname:
                add_to_ranking(nickname, time_taken)
                st.write("Score saved!")
            else:
                st.warning("Please enter a nickname!")

# Display Ranking
st.write("### Leaderboard")
st.dataframe(st.session_state.ranking)
