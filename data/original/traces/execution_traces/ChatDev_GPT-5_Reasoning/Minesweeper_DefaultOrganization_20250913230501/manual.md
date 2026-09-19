# Minesweeper — ChatDev Edition

A classic, no-frills Minesweeper for desktop built with Python and Tkinter. Choose among three difficulty levels (Beginner, Intermediate, Expert), reveal safe cells, place flags on suspected mines, and race the clock.

- Beginner: 9 × 9, 10 mines
- Intermediate: 16 × 16, 40 mines
- Expert: 30 × 16, 99 mines

This app uses standard Python only (no third-party packages) and provides cross-platform friendly controls and visuals.

## Key Features

- Three classic difficulty levels
- First-click is always safe (mines are placed after the first reveal)
- Flagging mechanism with distinct flagged appearance
- Clear visual states for hidden, revealed, flagged, and exploded cells
- Color-coded numbers (1–8) for adjacent mine counts
- Timer that starts on first reveal and freezes at win/loss
- Mines remaining counter (total mines minus current flags)
- Cross-platform input: Right-click, Middle-click, or Ctrl+Click to toggle flags
- No third-party dependencies; runs with standard Python and Tkinter

## System Requirements

- Python 3.7+
- Tkinter available on your system (often included, but may require an OS-level package)

OS notes for Tkinter:
- Windows: Included with most Python installers from python.org
- macOS:
  - Python from python.org typically includes Tkinter
  - If using Homebrew Python and Tk isn’t present:
    - `brew install tcl-tk`
    - Reinstall Python with the correct flags or use the python.org installer
- Linux:
  - Debian/Ubuntu: `sudo apt-get install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`
  - Arch: `sudo pacman -S tk`

## Installation

1. Clone or download this repository to your machine.

2. (Optional) Create and activate a virtual environment:
   - macOS/Linux:
     ```
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```
     py -m venv .venv
     .venv\Scripts\Activate.ps1
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   - Note: The requirements file only adds `dataclasses` for Python < 3.7. For modern Python, no extra packages are installed.
   - Ensure Tkinter is installed at the OS level (see System Requirements).

## Running the Game

From the project root:
```
python main.py
```
or
```
python3 main.py
```

The Minesweeper window will open immediately.

## Using the App

### Interface Overview

- Difficulty menu: Choose Beginner, Intermediate, or Expert. Changing difficulty starts a new game.
- New Game button: Resets the board with a fresh layout at the current difficulty.
- Mines: Shows total mines minus the number of flags you’ve placed. This can go negative if you over-flag.
- Time: In seconds. Starts on your first reveal, freezes when you win or lose.
- Board: The grid of clickable cells.

### Controls

- Reveal a cell: Left-click
- Flag/unflag a cell (suspected mine):
  - Right-click, or
  - Middle-click, or
  - Ctrl + Left-click (useful on macOS trackpads without a right-click)
  
Tip (macOS): If right-click isn’t working, try Ctrl+Click or enable “Secondary click” in System Settings.

### Visual States

- Hidden cell: Raised, gray button with no text
- Flagged cell: Red “F” on a light red background (distinct, readable on any system)
- Revealed empty cell (0 adjacents): Sunken, light background, no text
- Revealed number: Sunken cell showing 1–8 in color
- Mine: A “*” character on reveal; the exploded mine (the one you clicked) is highlighted red on loss

Color hints for numbers:
- 1: Blue, 2: Green, 3: Red, 4: Dark Blue, 5: Dark Red, 6: Dark Cyan, 7: Black, 8: Gray

### Game Rules

- The first click never hits a mine (mines placed after your first reveal).
- Numbers show how many mines are in the 8 surrounding cells (diagonals included).
- Clicking a cell with zero adjacent mines auto-reveals a region of empty cells and their border numbers.
- You win by revealing all non-mine cells.
- You lose if you reveal a mine; all mines are then shown and the exploded mine is highlighted.

### Timer and Mines Counter

- The timer starts on your first reveal and stops when you win or lose.
- “Mines” shows total mines minus your placed flags. It is a guide and does not enforce correctness.

## Tips for Play

- Start with wide-open areas (cells that reveal zeros quickly open the board).
- Use flags liberally to mark suspected mines; you can unflag if you change your mind.
- The mines remaining counter helps gauge your progress—but it isn’t a guarantee; misflags can make it negative.

## Troubleshooting

- “No module named tkinter” or UI doesn’t appear:
  - Install Tkinter (see System Requirements).
  - On Linux, ensure you installed the correct system package (e.g., `python3-tk`).
  - On WSL (Windows Subsystem for Linux), you need an X server or run the app directly on Windows.

- Right-click doesn’t work on macOS trackpad:
  - Use Ctrl + Click or Middle-click.
  - Enable “Secondary click” in System Settings.

- Text or symbols look odd:
  - The app uses ASCII symbols (“F” for flags and “*” for mines) to ensure universal readability.

- High-DPI scaling issues:
  - Try resizing the window or adjust system display scaling settings.
  - Advanced users can tweak fonts in gui.py.

## Advanced Customization (Optional)

You can adjust visuals and difficulty in gui.py:

- Difficulty presets:
  - In `MinesweeperApp.DIFFICULTIES`, modify or add entries:
    ```
    "Beginner": (9, 9, 10),
    "Intermediate": (16, 16, 40),
    "Expert": (30, 16, 99)
    ```
  - Format: width, height, number of mines

- Symbols:
  - `FLAG_CHAR = "F"`
  - `MINE_CHAR = "*"`. You can replace these with other characters if desired.

- Colors:
  - Update `NUMBER_COLORS` to personalize number hues.

- Fonts and button sizes:
  - Adjust the `font`, `width`, and `height` options when creating buttons in gui.py.

## Project Structure

- main.py — App entry point; creates the window and starts the GUI
- gui.py — Tkinter interface: layout, controls, event handling, rendering
- game.py — Game logic (board, cells, reveal/flag rules, win/loss, timer state)
- requirements.txt — Minimal Python dependency spec

## License and Credits

- Built by ChatDev with a focus on dependable, classic gameplay using standard Python.
- Uses only the Python standard library and Tkinter.

Enjoy sweeping!