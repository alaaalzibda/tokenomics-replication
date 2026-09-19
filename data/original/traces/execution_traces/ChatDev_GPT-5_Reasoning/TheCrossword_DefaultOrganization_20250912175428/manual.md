# ChatDev Crossword Puzzle

A friendly, lightweight desktop application to play and validate crossword puzzles. Ships with a 5x5 “Sator Square” mini puzzle and supports dynamic numbering, across/down clues, answer validation, and completion confirmation.

This app is built in Python with Tkinter and follows a simple Model–View–Controller (MVC) architecture.

## Quick Start

- Requirements: Python 3.8+ with Tkinter
- Run: `python main.py`

No third-party Python packages are required.

## What’s included

- A 5x5 Sator Square puzzle (no black squares)
- Across and Down clues keyed by clue number
- Type an answer by clue number and direction (Across/Down)
- Strict validation with helpful feedback
- Visual checkmarks when entries are filled
- Completion dialog when the whole puzzle is solved
- Reset to start over

## Installation

1) Verify Python
- Check your Python version:
  ```
  python --version
  ```
  or
  ```
  python3 --version
  ```
  Ensure it is 3.8 or newer.

2) Ensure Tkinter is available
- Windows: Tkinter usually ships with the standard Python installer from python.org.
- macOS: Recommended to install Python from python.org; Tkinter is included. If using Homebrew Python, ensure you have Tk support: `brew install python-tk@3.x` (version may vary).
- Linux: Install the Tkinter package for your distribution:
  - Debian/Ubuntu:
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

3) Get the code
- Place these files in the same directory:
  - main.py
  - data.py
  - crossword_model.py
  - crossword_view.py
  - crossword_controller.py

4) (Optional) Create and activate a virtual environment
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
or
```
python3 main.py
```

## How to Play

- The grid is on the left; controls and clues are on the right.
- Clue Input:
  - Clue number: Use the spinner to select the number.
  - Direction: Choose Across (A) or Down (D).
  - Answer: Type the full word in the text field.
- Submit:
  - Press the Submit button or hit Enter.
- Reset:
  - Clears all entries and allows you to start over.

When an entry is correctly filled:
- Its letters appear in the grid.
- A checkmark shows next to its clue.
- Crossings automatically reflect completion, and checkmarks update accordingly.

When the entire grid matches the solution:
- You’ll see: “Congratulations! You filled in all correct words.”

Tip: You must enter the exact full word for each entry; partial letters are not accepted.

## Included Puzzle: Sator Square Mini (5x5)

- Across clues (numbers reflect dynamic numbering based on the grid):
  - 1A (5): Latin “sower”; starts the famous square
  - 6A (5): Mysterious name from the Sator square
  - 7A (5): Belief or principle
  - 8A (5): Stage works set to music
  - 9A (5): Wheels, in Latin

- Down clues:
  - 1D (5): Starts the Latin word square
  - 2D (5): Name found in the palindromic Latin square
  - 3D (5): Doctrine
  - 4D (5): Grand musical works
  - 5D (5): Rotating things, in Latin

The grid is the classic Sator Square:
SATOR
AREPO
TENET
OPERA
ROTAS

Because there are no black squares, numbering works like this:
- Across entries start at the first column of each row, hence 1A, then 6A, 7A, 8A, 9A.
- Down entries start at the first row of each column, hence 1D through 5D.

## Features

- Simple, responsive Tkinter interface
- Dynamic across/down numbering from the grid (supports black squares via “#”)
- Clues readable by number (preferred) with fallback by answer text
- Strict answer validation:
  - Checks existence of the clue
  - Ensures length matches
  - Requires exact match to the solution
  - Warns about letter conflicts with already filled cells
- Real-time checkmarks for completed entries
- Completion detection and congratulatory dialog
- Reset to start over

## Keyboard and UI Tips

- Press Enter in the Answer field to submit quickly.
- The clue number spinner is initialized to the minimum available number.
- After a successful submission, the Answer field auto-clears and stays focused for fast play.

## Troubleshooting

- “No module named tkinter”
  - Install Tkinter for your OS (see Installation step 2).
- The window doesn’t appear or looks odd on macOS
  - Prefer Python from python.org. Some system Pythons or alternative builds may lack a modern Tk.
- App won’t start via “python”
  - Try “python3” instead, depending on your system.

## Customizing or Adding Puzzles

All puzzle data lives in data.py within the get_puzzle() function. It returns a dictionary with:

- name: Title shown in the window
- solution_rows: List of strings representing each grid row
  - Use uppercase letters for filled cells
  - Use “#” for black squares (blocks)
  - All rows must be the same length (rectangular grid)
- across_clues_by_number: Dict[int, str]
- down_clues_by_number: Dict[int, str]
- across_clues_by_answer: Dict[str, str] (fallback)
- down_clues_by_answer: Dict[str, str] (fallback)

Example with blocks:
```
solution_rows = [
  "CAT##DOG",
  "A#R#O#E",
  "RAT##HEN",
]
```
- The model automatically computes numbering:
  - Across starts where a cell is not a block and either at column 0 or left is a block.
  - Down starts where a cell is not a block and either at row 0 or above is a block.

Clue assignment order:
- The app first tries across_clues_by_number / down_clues_by_number.
- If a number is missing, it falls back to across_clues_by_answer / down_clues_by_answer using the exact answer string.
- If still missing, a generic placeholder like “Across word (5)” is used.

Tips for authoring:
- Ensure solution_rows form a rectangle (same length per row).
- Keep answers uppercase (the app normalizes input to uppercase).
- If you provide number-based clues, verify they match the automatically computed numbering. You can run the app and read the displayed numbering to confirm.
- Fallback dictionaries are useful for quick prototypes but number-based clues are preferred for clarity and robustness.

## Architecture Overview (for curious users)

- Model (crossword_model.py): Grid state, numbering, validation, completion.
- View (crossword_view.py): Tkinter UI (grid, clues, input controls, status).
- Controller (crossword_controller.py): Orchestrates user actions, updates UI, and announces completion.
- Data (data.py): Puzzle definitions.
- Entry point (main.py): Wires everything together.

## Known Limitations

- Entry of partial letters is not supported; you must submit full correct answers for them to appear in the grid.
- Only A–Z uppercase letters are shown; input is normalized to uppercase.
- Single-puzzle runtime; swap or edit get_puzzle() to change the puzzle.

## Support and Feedback

We’d love feedback to improve the experience. If you encounter issues or have feature requests (e.g., pencil mode, hints, multiple puzzles, saving progress), please share them with the development team.

Enjoy puzzling!