# Gomoku (Five in a Row)

A classic two-player board game implemented in Python with a clean Tkinter GUI. Play on a standard 15x15 board, alternating black and white stones. Win by forming an unbroken line of five stones horizontally, vertically, or diagonally.

- Platform: Desktop application (Tkinter)
- Language: Python
- Mode: Local two-player (pass-and-play)

## Features

- Standard 15x15 Gomoku board with star points
- Clear, responsive GUI with grid lines
- Black starts; players alternate turns
- Valid move enforcement (can’t place on occupied cells)
- Automatic win detection (5-in-a-row) with winning line highlight
- Draw detection (full board)
- Undo and redo with history and future stacks
- Last move indicator
- Keyboard shortcuts for power users

## System Requirements

- Python 3.8+ (recommended 3.10+)
- Tkinter (Tk 8.6+) available in your Python installation
- OS: Windows, macOS, or Linux with GUI support

Note: Tkinter ships with the standard Python installers for Windows and most macOS builds. On many Linux distributions you may need to install it separately.

## Installation

1) Get the source code
- Clone or download the repository contents into a folder. Ensure these files are together:
  - main.py
  - controller.py
  - model.py
  - view.py
  - __init__.py (optional if you keep them in a package directory named gomoku)

2) (Optional but recommended) Create and activate a virtual environment
```
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3) Ensure Tkinter is available
- Windows: Using Python from python.org typically includes Tkinter; no action needed.
- macOS:
  - Python from python.org includes Tkinter.
  - If using Homebrew Python and you see Tkinter errors, install Tk and relink:
    ```
    brew install tcl-tk
    ```
    Then use the Python from python.org or configure Homebrew’s Python to use the brewed Tk.
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

No additional pip packages are required.

## Running the Game

From the project directory, run:
```
python main.py
```

Notes on imports and layout:
- The app supports both a package layout and a flat-file layout:
  - Package layout:
    ```
    gomoku/
      __init__.py
      model.py
      controller.py
      view.py
    main.py
    ```
  - Flat-file layout:
    ```
    main.py
    model.py
    controller.py
    view.py
    __init__.py (optional)
    ```
- main.py automatically detects and imports correctly in either case.

## How to Play

- Objective: Be the first to place five of your stones in a row horizontally, vertically, or diagonally.
- Black plays first.
- Players alternate placing a single stone each turn on empty intersections.

### Controls

- Place a stone: Left-click near a board intersection
- New Game: Click "New Game" (or Ctrl+N)
- Undo last move: Click "Undo" (or Ctrl+Z)
- Redo move: Click "Redo" (or Ctrl+Y)

### Interface Guide

- Board grid: 15x15 with typical star points
- Stones: Black and white discs on intersections
- Last move marker: Small orange dot on the most recent move (while the game is ongoing)
- Status bar:
  - “Turn: Black” or “Turn: White”
  - “Game Over: Black wins!” / “Game Over: White wins!” / “Game Over: Draw.”
- Win highlight: A red line overlays the winning five stones
- End dialog: A message box announces the result

### Game Rules Implemented

- Standard Gomoku rules for five-in-a-row
- Overlines (lines longer than five) still result in a win
- No forbidden-move rules (e.g., Renju) are enforced
- Game ends immediately on a win or when the board is full (draw)

## Troubleshooting

- The window doesn’t start; error mentions “_tkinter” or “no display”:
  - Ensure Tkinter is installed (see Installation)
  - On Linux servers/headless environments, a display is required
- Clicking does nothing:
  - Ensure you’re clicking near an intersection; the app uses a generous tolerance
  - You cannot place on occupied intersections
  - If the status says “Game Over…”, start a new game to continue playing
- Import error for gomoku:
  - Keep main.py alongside controller.py, model.py, view.py (flat-file), or use the package structure shown above. main.py supports both.

## Tips and Customization

- Board size: The standard is 15. If you want to experiment:
  - Edit controller.py: GameController() uses Board(size=15)
    - Note: Star points in the UI are set for 15x15; changing size may require adjusting view.py (draw_grid).
- Visual scale:
  - In view.py → BoardCanvas(...):
    - cell_size (default 40) controls spacing between intersections
    - margin (default 30) controls outer padding

## Project Structure

- main.py: Application entry point
- model.py: Core game logic (board state, move validation, win detection, history/redo)
- controller.py: Game flow (turns, apply moves, status, win/draw handling)
- view.py: Tkinter GUI (board rendering, input handling, dialogs)
- __init__.py: Package metadata (used when files are organized as a package)

## License and Credits

- Built by ChatDev as part of a product demo
- Uses Python’s standard Tkinter library for the GUI

Enjoy playing Gomoku! If you have feedback or feature requests (AI opponent, networked play, rule variants), let us know.