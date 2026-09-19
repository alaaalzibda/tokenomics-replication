# Connect Four — ChatDev Edition

A simple, polished, and fun two‑player Connect Four game with a Tkinter GUI. Players alternate dropping Red and Yellow discs into a seven‑column, six‑row grid. The first player to connect four discs in a row horizontally, vertically, or diagonally wins. The game validates inputs and ends on a win or a draw.

## Features

- Standard Connect Four rules on a 7×6 grid
- Local two‑player play (Red vs Yellow)
- Type column numbers to play (1–7), with clear validation messages
- Optional mouse support: click a column to drop a disc
- Automatic win and draw detection
- Reset button to start a new game
- Clean, accessible UI with color-coded discs and status bar

## Requirements

- Python 3.8+  
- Tkinter (comes bundled with most Python distributions)
- A system Tcl/Tk installation (required by Tkinter)

No third‑party Python packages are required.

## Install and Setup

1) Install Python
- Windows/macOS: Download from https://www.python.org/downloads/ (the official installers include Tkinter by default).
- Linux: Use your distribution’s package manager (ensure the tkinter package is installed as well).

2) Ensure Tkinter is available
- Windows/macOS (python.org installers): Usually ready to use.
- Linux: Install tkinter explicitly if needed:
  - Debian/Ubuntu: sudo apt-get update && sudo apt-get install python3 python3-tk tk
  - Fedora: sudo dnf install python3-tkinter tk
  - Arch: sudo pacman -S tk

3) Verify Tk/Tkinter installation
- Run:
  ```
  python -c "import tkinter as tk; print('Tkinter OK — Tk version:', tk.TkVersion)"
  ```
  If this fails, revisit step 2.

4) Get the source code
- Clone or download the project into a folder (e.g., connect-four/). The key files are:
  - main.py
  - game.py
  - gui.py
  - requirements.txt

5) (Optional) Use a virtual environment
- Create and activate a venv:
  - Windows:
    ```
    python -m venv .venv
    .venv\Scripts\activate
    ```
  - macOS/Linux:
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    ```
- No pip installs are needed; the app uses only the standard library.

## Running the Game

From the project directory, run:
```
python main.py
```
A window titled “Connect Four - ChatDev” will open. The column input field is focused so you can start typing immediately.

## How to Play

- Objective: Be the first to connect four of your discs in a line: horizontal, vertical, or diagonal.
- Turns:
  - Player 1 is Red, Player 2 is Yellow.
  - The status bar shows whose turn it is and prompts for a column number.
- Input:
  - Type a column number (1–7) and press Enter or click the “Drop” button.
  - Optional: Click directly on a column in the board to drop a disc.
- Validations and messages:
  - Empty input: “Please type a column number (1–7).”
  - Non-number input: “Invalid input. Enter a number from 1 to 7.”
  - Out of range: “Column must be between 1 and 7.”
  - Full column: “That column is full. Try a different one.”
- Winning and drawing:
  - On a win, the status shows “Player X (Red/Yellow) wins! Press Reset to play again.”
  - On a full-board draw, the status shows “It’s a draw! Press Reset to play again.”
- Reset:
  - Click “Reset” to start a new game.
  - After a game ends, input is disabled until you click “Reset.”

Tip: Column numbers (1–7) are shown along the top of the board.

## Game Rules (Quick Reference)

- Grid size: 7 columns × 6 rows
- Players alternate turns dropping one disc per move.
- Discs fall to the lowest available space in the chosen column.
- A player wins by connecting four discs in a row:
  - Horizontal, Vertical, or Diagonal
- If the grid fills without any four-in-a-row, the game is a draw.

## User Interface Guide

- Status Bar: Displays whose turn it is and actionable feedback.
- Board:
  - Blue board with circular “holes”
  - Red and Yellow discs placed as you play
  - Column numbers displayed at the top (1–7)
- Controls:
  - Column input: Type 1–7; press Enter or click “Drop”
  - Reset button: Starts a fresh game
- Mouse Support:
  - Click anywhere within a column to drop a disc

Keyboard behavior:
- Enter submits the column number if the input field is focused.
- After each move, the input stays focused for quick play.

## Troubleshooting

- ImportError: No module named tkinter
  - Install Tkinter (see Linux instructions above). On Windows/macOS, ensure you installed Python from python.org or your environment includes Tkinter.
- TclError: no display name and no $DISPLAY (Linux)
  - You’re likely on a headless or remote system. Use a desktop session or configure X11 forwarding.
- TclError: can’t find a usable init.tcl
  - Your Tcl/Tk is not installed correctly or your Python can’t find it. Reinstall Tk or use the official Python installer that bundles a working Tk.
- The window is too large for my screen
  - Lower the cell size in gui.py (self.cell_size) and restart.
- The app doesn’t start when double-clicking
  - Run from a terminal to see error messages: python main.py

## Customization

- Board size
  - You can change the default 6×7 board by editing main.py:
    ```
    game = ConnectFourGame(rows=6, cols=7)  # Ensure both >= 4
    ```
- Colors and visuals
  - In gui.py, adjust:
    - self.player_colors for Red/Yellow
    - self.board_bg for the board color
    - self.cell_size and self.margin for sizing
- Programmatic use (game logic only)
  - You can use the core logic in other contexts by importing ConnectFourGame:
    ```python
    from game import ConnectFourGame

    game = ConnectFourGame(rows=6, cols=7)
    # Drop discs by zero-based column index:
    game.drop_disc(3)  # Player 1
    game.drop_disc(3)  # Player 2
    print(game.get_board())
    print('Winner:', game.get_winner())
    ```
  - Errors on invalid moves are raised as ValueError.

## Project Structure

- main.py — App entry point; initializes the Tk window and starts the GUI.
- game.py — Core game rules and state: move validation, turn management, win/draw detection.
- gui.py — Tkinter GUI: rendering, input handling, feedback, and reset controls.
- requirements.txt — Notes on environment requirements (no extra packages needed).

## FAQs

- Is there single-player or AI?
  - No. This version is local two-player only.
- Can I use arrow keys or other shortcuts?
  - Input is via the column number and Enter, or by clicking a column.
- Does the app save games?
  - No persistence is included; each session is in-memory only.

## Support

If you encounter issues or have feature requests, please share:
- Your OS and version
- Python version (python --version)
- Tk version (python -c "import tkinter as tk; print(tk.TkVersion)")
- Any error messages from the terminal

Enjoy the game, and happy connecting four!