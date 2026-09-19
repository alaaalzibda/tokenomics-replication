# Reversi (Othello) — User Manual

A simple, polished desktop application for playing Reversi (Othello) locally on your computer. Two human players take turns placing discs on an 8×8 board. The app automatically highlights valid moves, flips captured discs, handles passes, keeps score, and announces the winner.

- Platform: Desktop GUI
- Modality: Application
- Language: Python (Tkinter GUI)
- Files: main.py, game.py, gui.py, __init__.py

## Features

- Standard 8×8 Reversi/Othello gameplay
- Auto-detected valid moves (highlighted hints)
- Automatic disc flipping in all 8 directions
- Pass handling when a player has no valid moves
- Live score and current player indicator
- Last move highlight
- Undo (multi-step) and New Game
- Simple, accessible controls and keyboard shortcuts

---

## System Requirements

- Python 3.8 or newer
- Tkinter (Python’s standard GUI toolkit)
- Operating Systems:
  - Windows 10/11
  - macOS 10.15+ (Catalina or later)
  - Linux (with a graphical environment/X11/Wayland)

Note: On many Windows/macOS Python distributions, Tkinter is included by default. Minimal Linux installations may require installing `python3-tk`.

---

## Installation

1) Install Python
- Download from https://www.python.org/downloads/ and install.
- Ensure “Add Python to PATH” is selected on Windows.

2) Verify Tkinter
- Check Tkinter availability:
  ```
  python -c "import tkinter; print('Tk version:', tkinter.TkVersion)"
  ```
- If this fails on Linux:
  - Debian/Ubuntu:
    ```
    sudo apt-get update
    sudo apt-get install -y python3-tk
    ```
  - Fedora:
    ```
    sudo dnf install python3-tkinter
    ```
  - Arch:
    ```
    sudo pacman -S tk
    ```

3) Get the source code
- Place the provided files in a single folder (e.g., `reversi/`), keeping this structure:
  - `main.py`
  - `game.py`
  - `gui.py`
  - `__init__.py`

4) (Optional) Use a virtual environment
```
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

5) Run the app
```
python main.py
```

---

## How to Play

### Objective
Finish the game with more discs of your color on the board than your opponent.

- Black moves first.
- Players alternate turns placing one disc per turn.
- A move is valid if it captures at least one opponent disc in a straight line (horizontal, vertical, or diagonal).
- Captured discs are those bracketed between the newly placed disc and an existing disc of the same color.
- If a player has no valid moves, that player must pass (handled by the app).
- The game ends when neither player can move or the board is full.
- The winner is the player with the higher disc count; ties are possible.

---

## Using the Interface

When you launch the app:

- The board appears as an 8×8 grid.
- Initial setup places two white and two black discs in the center (standard Othello start).
- The top bar shows:
  - Title
  - Current player (Black or White)
  - Score (Black and White counts)
  - Informational messages (e.g., valid moves available)
- The right side includes buttons:
  - New Game: Resets to the initial position
  - Undo Move: Undoes the last move (multi-step)
  - Quit: Closes the application

### Controls

- Place a disc: Click on a highlighted cell (small dot indicates a valid move).
- Invalid move: You’ll see a message and a subtle alert; try another highlighted cell.
- Keyboard shortcuts:
  - N — New Game
  - U — Undo Move

### Visual Cues

- Valid move hints: Small dots on cells where you can legally move.
  - Black’s hints appear darker; White’s hints appear lighter.
- Last move: The most recent move is outlined in a gold rectangle.
- Scoreboard: Live counters for each player.
- Info messages:
  - Number of valid moves available
  - Pass notifications when a player has no valid moves
  - “Game Over” dialog showing final scores and winner

---

## Quick Start

1) Run:
```
python main.py
```
2) Black moves first; click a highlighted cell to place a black disc.
3) Watch captured discs flip automatically.
4) White then plays; continue alternating.
5) If a pass occurs, a dialog informs you.
6) The game ends automatically when no moves remain or the board is full.
7) A dialog displays the final score and the winner.

---

## Scoring and Game End

- Score equals the count of discs on the board for each color.
- The app updates scores after every move.
- Game end conditions:
  - Board is full, or
  - Neither player has any valid moves.
- The app announces the winner or a tie.

---

## Undo and New Game

- Undo Move:
  - Reverts the last applied move (restoring board, turn, and last-move highlight).
  - Repeat to step further back until no moves remain in history.
- New Game:
  - Resets the board to the starting position with Black to move.

---

## Troubleshooting

- ImportError: No module named tkinter
  - Install Tkinter:
    - Linux:
      - Debian/Ubuntu: `sudo apt-get install -y python3-tk`
      - Fedora: `sudo dnf install python3-tkinter`
      - Arch: `sudo pacman -S tk`
    - macOS: If using pyenv or Homebrew Python, ensure `tk` is included or install a Python build with Tk support.
- TclError: no display name and no $DISPLAY environment variable
  - You’re likely running on a headless server without a GUI. Use a machine with a graphical environment or configure X forwarding (e.g., `ssh -X`) or a virtual display.
- Window too small/large or blurry on HiDPI screens
  - Resize the window manually.
  - Optional: adjust `CELL_SIZE` in `gui.py` to scale the board.
- App won’t start or nothing happens
  - Ensure you’re running `python main.py` in the folder with all four files.
  - Check Python version with `python --version` (3.8+ required).

---

## Configuration and Customization (Advanced)

- Board visuals:
  - Edit constants in `gui.py`:
    - `CELL_SIZE` (default: 80 pixels)
    - Colors: `BOARD_BG`, `GRID_COLOR`, `HINT_COLOR_BLACK`, `HINT_COLOR_WHITE`, `LAST_MOVE_OUTLINE`
- Move hints:
  - Hints are enabled by default (`self.show_hints = True` in `ReversiGUI.__init__`).
  - To disable, set to `False` in the source.
- Board size:
  - The game logic supports an `8×8` board and initializes accordingly.
  - The GUI is currently fixed to 8×8 (`BOARD_SIZE = 8`). Changing board size would require code changes in `gui.py`.
- Packaging (optional):
  - You can bundle the app using PyInstaller:
    ```
    pip install pyinstaller
    pyinstaller --noconfirm --windowed --name "Reversi" main.py
    ```
  - Note: Ensure Tcl/Tk is included properly on your platform.

---

## File Overview (For Developers)

- `main.py`
  - Entry point. Initializes and launches the Tkinter GUI.
- `gui.py`
  - Tkinter UI: board rendering, event handling, status updates, dialogs.
  - Highlights valid moves, draws discs, last-move outline.
- `game.py`
  - Core game logic (`ReversiGame`):
    - Board state, turns, valid moves computation, disc flipping
    - Undo history, pass handling, scoring, winner detection
- `__init__.py`
  - Package metadata.

Key `ReversiGame` methods:
- `get_valid_moves(player=None)` — list of valid (row, col) moves
- `apply_move(r, c)` — applies a move, flips discs, advances turns, returns move result data
- `undo()` — reverts last move
- `get_score()` — returns `{'black': int, 'white': int}`
- `is_game_over()` / `get_winner()`

---

## FAQ

- Is there an AI opponent?
  - Not in this version. Both players are human. The logic layer is ready for extension if you’d like to add an AI module.
- Can I save and load games?
  - Not currently. You can use Undo and New Game.
- Can I turn off the hints?
  - Yes, set `self.show_hints = False` in `ReversiGUI.__init__`.

---

## Support

- If you encounter issues installing or running the app, review the Troubleshooting section.
- For customization or feature requests (e.g., AI opponent, different board themes), extend `game.py` and `gui.py` per the File Overview.

Enjoy playing Reversi!