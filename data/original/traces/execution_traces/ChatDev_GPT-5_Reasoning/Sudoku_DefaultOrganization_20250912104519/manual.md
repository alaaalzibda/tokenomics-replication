# ChatDev Sudoku Web App

A classic 9x9 Sudoku game in your browser. Fill each row, column, and 3x3 subgrid with digits 1–9 exactly once. Play, check your mistakes, and validate completion with a clean, responsive interface.

Built with Flask (Python) and vanilla HTML/CSS/JS.

## Features

- 9x9 Sudoku board with 3x3 subgrid outlines
- Pre-filled givens (locked) and editable cells
- Instant client-side conflict highlighting (rows, columns, boxes)
- “Check Mistakes” against the official solution (highlights incorrect cells)
- “Validate Completed” to confirm puzzle completion and correctness
- Generate a new puzzle on demand (with server-side uniqueness checks)
- Keyboard navigation (arrow keys) and backspace behavior
- Session-based persistence so your current puzzle remains active while you browse

## What’s in the box

- Backend (Flask): puzzle generation, solution verification, session state
- Frontend: dynamic board rendering, input handling, UI controls

Directory structure (expected):
```
project-root/
├─ main.py
├─ sudoku.py
├─ requirements.txt
├─ templates/
│  └─ index.html
└─ static/
   ├─ js/
   │  └─ main.js
   └─ css/
      └─ styles.css
```

## System Requirements

- Python 3.8+ (3.10 or later recommended)
- pip (Python package manager)
- A modern browser (Chrome, Firefox, Safari, Edge)

## Quick Start

1) Clone or download this project, then open a terminal in the project root.

2) Create and activate a virtual environment.

- macOS/Linux:
  ```
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- Windows (PowerShell):
  ```
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```

3) Install dependencies.
```
pip install -r requirements.txt
```

4) (Optional but recommended) Set a secret key for sessions.

- macOS/Linux:
  ```
  export SUDOKU_SECRET_KEY="change-this-to-a-long-random-string"
  ```
- Windows (PowerShell):
  ```
  setx SUDOKU_SECRET_KEY "change-this-to-a-long-random-string"
  ```
  Then restart the terminal or set it in the current session:
  ```
  $env:SUDOKU_SECRET_KEY="change-this-to-a-long-random-string"
  ```

5) Run the development server.
```
python main.py
```

6) Open the app in your browser at:
```
http://localhost:5000
```

To stop the app, press Ctrl+C in the terminal.

## How to Play

- Goal: Fill the 9x9 grid so that every row, every column, and each 3x3 box contains all digits 1 through 9 exactly once.
- Givens: Cells that come pre-filled are locked (you can’t edit them).
- Input: Click any empty cell and type a digit 1–9. Typing 0 or any non-numeric character is ignored.
- Conflicts: If the same digit appears twice in a row, column, or 3x3 box, conflicting cells are styled in red to guide you.
- Check Mistakes: Click “Check Mistakes” to compare your filled cells against the solution. Incorrect cells are highlighted in red background.
- Validate Completed: Click “Validate Completed” to check if the board is fully and correctly solved. You’ll see:
  - Success message if solved
  - Warning if filled but with mistakes
  - Info prompting you to keep going if not yet complete
- New Game: Click “New Game” anytime to load a fresh puzzle.

### Keyboard Shortcuts

- Arrow keys: Move focus up/down/left/right
- Backspace: Clears the current cell; if already empty, moves focus left

## UI Overview

- Board: 9x9 grid with thicker borders to separate 3x3 boxes
- Buttons:
  - New Game: Generate and load a new puzzle
  - Check Mistakes: Highlights cells that don’t match the solution
  - Validate Completed: Confirms whether you’ve solved the puzzle
- Message Bar: Shows status, errors, warnings, and success messages

## Session & Persistence

- Your current puzzle, its solution, and givens are stored in your session.
- If you refresh the page or navigate within the app, your current puzzle remains.
- Clearing browser cookies or restarting the server may reset your session.

## Difficulty

The server supports difficulty hints when generating puzzles:
- “easy”
- “medium” (default)
- “hard”

The UI’s “New Game” button currently requests the default difficulty. If you want to manually request a difficulty (for testing), use the API endpoint below.

## API Reference

All endpoints are same-origin and return JSON.

- POST /api/puzzle
  - Returns the current puzzle and givens from the session.
  - Request body: none
  - Response:
    ```
    {
      "puzzle": [[int x9] x9],  // 0 for empty
      "givens": [[0|1 x9] x9]   // 1 means given/locked cell
    }
    ```

- POST /api/new
  - Generates a new puzzle and stores it in the session.
  - Request body (optional):
    ```
    { "difficulty": "easy" | "medium" | "hard" }
    ```
  - Response:
    ```
    {
      "puzzle": [[int x9] x9],
      "givens": [[0|1 x9] x9],
      "difficulty": "..."
    }
    ```
  - Example (curl):
    ```
    curl -X POST -H "Content-Type: application/json" \
      -d '{"difficulty":"hard"}' http://localhost:5000/api/new
    ```

- POST /api/verify
  - Verifies the given 9x9 board against the solution.
  - Request:
    ```
    {
      "board": [[int x9] x9]  // use 0 for empty cells
    }
    ```
  - Response:
    ```
    {
      "complete": bool,                 // no zeros
      "solved": bool,                   // exact match with solution
      "incorrect_cells": [{"row": r, "col": c}, ...],
      "message": "..."
    }
    ```
  - Notes:
    - If a given (locked) cell has been altered, the API returns a message indicating that modification of givens is not allowed.

## Configuration

- Port: Defaults to 5000; change by editing main.py or using a production WSGI server.
- Secret Key: Set SUDOKU_SECRET_KEY to a secure, random string in production.
- Debug: main.py runs with debug=True for development. Disable in production.

## Deployment Tips

- Use a production WSGI server (e.g., gunicorn, waitress, uWSGI) behind a reverse proxy (Nginx/Apache).
- Set environment variables securely:
  - SUDOKU_SECRET_KEY
- Disable Flask debug mode.
- Consider HTTPS and secure cookies in production.
- Sessions are in-memory (signed cookies). If you need server-side session storage, integrate a session backend (Redis, database) and configure Flask-Session.

## Troubleshooting

- Port already in use
  - Another process is using port 5000. Stop it or change the port.
- “Invalid board format” or non-numeric values
  - Ensure board is a 9x9 array of integers 0–9 if you’re calling the API directly.
- Session issues
  - Make sure SUDOKU_SECRET_KEY is set and consistent across restarts if you want to preserve sessions.
- Static file caching
  - If UI changes aren’t visible, hard-refresh (Ctrl+F5) or clear cache.
- Virtual environment problems
  - Ensure the venv is activated (you should see “(.venv)” in your prompt) and run pip install -r requirements.txt again.

## How Puzzle Generation Works

- The server generates a full valid Sudoku solution via randomized backtracking.
- Cells are removed to create a puzzle, checking for uniqueness within a short time budget.
- If uniqueness constraints can’t be enforced in time, the app falls back to a known-good puzzle with a unique solution.

## License and Credits

- Built by ChatDev.
- Uses Flask for the web backend and vanilla JavaScript/CSS for the frontend.

Enjoy solving!