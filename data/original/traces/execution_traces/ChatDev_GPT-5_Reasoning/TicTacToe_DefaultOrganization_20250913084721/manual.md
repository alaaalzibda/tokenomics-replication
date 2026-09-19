# Tic-Tac-Toe (Python, Tkinter)
Version 1.0.0

A clean, user-friendly two-player Tic-Tac-Toe game. Play locally on a single computer, take turns as X and O, and enjoy a polished interface with winning-line highlights, clear status updates, and handy shortcuts.

## Key Features
- Standard 3x3 grid with large, readable cells
- Two-player local play (no AI)
- Turn management with clear status updates
- Winner detection across rows, columns, and diagonals
- Draw detection when the board is full
- Winning line highlight for instant visual feedback
- “New Game” resets and alternates the starting player (fairness)
- Menu bar with About dialog and keyboard shortcuts (Ctrl+N, Ctrl+Q)
- Consistent styling via centralized constants (colors, fonts, titles)

## System Requirements
- Operating System: Windows, macOS, or Linux
- Python: 3.8 or newer
- Tkinter GUI toolkit:
  - Windows/macOS: included with most python.org installers
  - Linux: may require installing an OS package (see below)

## Installation
1. Ensure Python 3.8+ is installed.
   - Verify:
     ```
     python --version
     ```
     or
     ```
     python3 --version
     ```

2. Ensure Tkinter is available.
   - Windows/macOS: typically included with Python from python.org.
   - Ubuntu/Debian:
     ```
     sudo apt-get update
     sudo apt-get install python3-tk
     ```
   - Fedora:
     ```
     sudo dnf install python3-tkinter
     ```
   - Arch:
     ```
     sudo pacman -S tk
     ```

3. Get the project files (main.py, gui.py, game_logic.py, constants.py).
   - Option A: Clone your repository
     ```
     git clone <your-repo-url>
     cd <project-folder>
     ```
   - Option B: Download and unzip the project, then open a terminal in that folder.

4. (Optional but recommended) Create and activate a virtual environment.
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

5. No extra pip packages are required. Tkinter is the only dependency.

## Run the Game
- Windows:
  ```
  python main.py
  ```
- macOS/Linux:
  ```
  python3 main.py
  ```

The Tic-Tac-Toe window will open with the game grid and controls.

## How to Play
- Objective: Be the first to get three of your marks (X or O) in a row (horizontally, vertically, or diagonally).
- Turn-taking:
  - The status bar shows whose turn it is (X or O).
  - Click an empty cell to place your mark.
  - You cannot overwrite a cell that’s already occupied.
- Game end:
  - If a player wins, the three winning cells are highlighted and the board is disabled.
  - If all cells are filled without a winner, the game ends in a draw and the board is disabled.
- Start again:
  - Click “New Game” or press Ctrl+N to reset the board.
  - The starting player alternates automatically across games for fairness.

## User Interface Guide
- Status Bar: Displays the current player’s turn, or the result (win/draw).
- 3x3 Grid: Click cells to place your mark.
- Controls:
  - New Game: Resets the board and alternates the starting player.
  - Quit: Closes the application.
- Menu:
  - Game → New Game (Ctrl+N)
  - Game → Quit (Ctrl+Q)
  - Help → About: Shows app name, version, and usage tips.
- Visual cues:
  - X marks are styled in red; O marks are styled in blue.
  - Winning line is highlighted in yellow.

## Keyboard Shortcuts
- Ctrl+N: New Game
- Ctrl+Q: Quit

Note: On macOS, the shortcuts use Control (Ctrl) as shown above.

## Game Rules and Logic
- Standard 3x3 Tic-Tac-Toe.
- X starts the very first game; subsequent games alternate the starting player.
- Win conditions:
  - Any complete row, column, or diagonal with the same symbol wins.
- Draw:
  - If all 9 cells are filled and no winner is found, the game is a draw.

## Project Structure
- main.py
  - Entry point. Creates the main window and launches the GUI.
- gui.py
  - Tkinter interface: builds layout, responds to clicks, updates status, highlights winning lines, handles new games and quitting.
- game_logic.py
  - Core rules engine: board state, turn management, move validation, winner/draw detection, alternating start logic.
- constants.py
  - Centralized configuration: window title, version, colors, fonts, symbols, grid size.

## Customization
- Visuals (colors, fonts, title): Edit constants.py.
  - Examples:
    - Change colors in COLORS dict (e.g., x_fg, o_fg, highlight).
    - Update window title via WINDOW_TITLE.
    - Adjust fonts in FONTS dict.
- Grid Size:
  - This app is designed for 3x3 (GRID_SIZE = 3).
  - The underlying logic and UI are written to adapt to NxN; however, the product specification targets 3x3. Changing GRID_SIZE may work but is not officially supported or tested.
- Behavior:
  - Turn alternation can be adjusted by editing game_logic.py (see next_starting_player and reset behavior).

## Troubleshooting
- Error: “ModuleNotFoundError: No module named ‘tkinter’”
  - Install Tkinter via your OS package manager (see Installation).
  - Ensure you’re using the correct Python executable if you have multiple versions installed.
- The window doesn’t appear on Linux:
  - If running over SSH, ensure X11 forwarding is enabled and an X server is available, or run locally with a desktop session.
- The board is unresponsive after a game ends:
  - This is expected—boards are disabled to prevent extra moves after a result.
  - Click “New Game” (or press Ctrl+N) to start another round.
- Text or colors are hard to read:
  - Adjust COLORS and FONTS in constants.py to match your system theme.

## FAQ
- Is there a single-player mode or AI?
  - No. This version is designed for two local players.
- Can I undo a move?
  - Not in this version.
- Does the app support touch screens?
  - If your OS treats touch as mouse clicks, it should work.
- Can I resize the window?
  - The window is fixed-size by design for a consistent layout.

## Version
- 1.0.0
  - Initial release with 3x3 gameplay, winner/draw detection, winning-line highlight, alternating starting player, and menu/shortcuts.

Enjoy the game!