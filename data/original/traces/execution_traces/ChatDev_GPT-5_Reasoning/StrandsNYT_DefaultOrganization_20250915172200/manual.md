# Strands (NYT Strands‑like) – Programming Languages Edition

A browser-based word search puzzle inspired by NYT Strands. Find all theme words and the spangram in a 6x8 grid. Words connect through adjacent letters (including diagonals) and can bend. Fill the entire board without overlap to win.

This package ships with:
- A Flask web app (website modality)
- A ready-to-play puzzle themed “Programming Languages”
- Optional desktop/Tkinter UI for local play
- A small wordlist for validating non-theme words that unlock hints

## Features

- 6x8 letter grid with drag-to-select gameplay
- Theme words (blue highlight)
- One spangram touching two opposite sides of the board (yellow highlight)
- Non-theme words (length ≥ 4) grant progress toward hints; every 3 unique non-theme words unlock 1 hint
- Zero overlap solution: every cell is used exactly once across all solution paths
- Hint system reveals a theme word or the spangram
- Session-based progress (per browser session)
- Mobile-friendly touch interactions
- Built-in “Programming Languages” puzzle (spangram: SOFTWARE)

## Quick Start

Prerequisites
- Python 3.8+ (recommended 3.9+)
- pip

Install and run
```bash
# 1) Clone or copy this project to your machine
# 2) Create and activate a virtual environment (recommended)
python -m venv .venv
# On macOS/Linux:
source .venv/bin/activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 3) Install dependencies
pip install -r requirements.txt

# 4) Run the web app
python main.py
```

Open your browser at:
- http://127.0.0.1:5000

To stop the server, press Ctrl+C in the terminal.

## How to Play

Goal
- Find all themed words and the spangram to fill the board completely. No letters are reused across different words.

Board and rules
- Grid: 6 rows × 8 columns.
- The spangram touches two opposite sides of the board (e.g., left and right edges).
- Words form by connecting adjacent letters in any direction (horizontally, vertically, diagonally). You can change direction mid-word.
- Selections must follow the puzzle’s canonical solution paths — the game enforces a unique, non-overlapping fill.

Selecting words
- Click (or tap) and drag across adjacent cells to form a word.
- Release the mouse (or lift your finger) to submit the selection.

Colors/feedback
- Temporary selection: teal
- Themed words: blue
- Spangram: yellow
- Valid non-theme word (counts toward a hint): quick flash of light green
- Invalid selection: quick flash of light red

Hints
- Every 3 unique non-theme words you find unlocks 1 hint.
- Use the “Use Hint” button to reveal the next unfound theme word (or the spangram if all themes are already revealed).

Controls
- Use Hint: reveals a word (consumes 1 hint).
- Reset Progress: resets your current session’s progress.
- Show Remaining Words: displays a list of remaining theme words (and the spangram if still unfound).

Win condition
- When all theme words and the spangram are found and the board is fully filled (no overlap), you’ll see a completion message.

## Built-in Puzzle

Theme
- Programming Languages

Spangram
- SOFTWARE (across the top row, touching left and right edges)

Themed words
- PYTHON, GO, KOTLIN, LUA, SWIFT, RUBY, SCALA, RUST, JULIA

Note
- You must trace the exact canonical paths for each word as authored in the puzzle. This ensures a single, overlap-free tiling of the grid.

## Web App Overview

Frontend
- Vanilla JS (static/app.js) handles drag selection, coloring, touch events, and calls to the backend.
- CSS (static/style.css) defines colors and layout.
- HTML template (templates/index.html) renders the app shell.

Backend
- Flask app (main.py) maintains per-session game state in memory and exposes JSON endpoints.

Endpoints
- GET / – Load the game UI
- GET /state – Current game state for the session
- POST /select – Commit a selection: body { "coords": [[r, c], ...] }
- POST /hint – Reveal a word if you have a hint
- POST /reset – Reset progress for this session
- GET /remaining – List remaining words (spangram included if not found)

Session and persistence
- Progress is stored in memory keyed by a session id cookie. Restarting the server clears all sessions. For persistence across restarts, integrate a backing store (e.g., Redis).

## Optional: Desktop (Tkinter) UI

This project also includes a basic desktop UI using Tkinter (ui.py). The website is the primary modality, but if Tkinter is available on your system you can try:

```bash
python -c "import tkinter as tk; from puzzle import default_puzzle; from ui import StrandsApp; root=tk.Tk(); StrandsApp(root, default_puzzle()); root.mainloop()"
```

Notes
- Tkinter is included with many Python distributions, but not all. If it’s missing, install the appropriate OS packages or use the web app instead.

## Customizing or Authoring a New Puzzle

Where to look
- puzzle.py defines the Puzzle class and the default_puzzle() factory.

Requirements for a valid puzzle
- Grid: supply a 6x8 letters matrix (uppercase suggested for consistency).
- Spangram string and path: its path must touch opposite board edges and be 8-directionally adjacent cell-to-cell.
- Theme words and paths: provide canonical paths for each theme word, also 8-directionally adjacent.
- Non-overlap: no cell may be used by more than one word/spangram.
- Full coverage: every cell in the grid must appear exactly once across all solution paths (spangram + theme words).

Validation
- Puzzle.validate_integrity() asserts:
  - Grid dimensions are correct
  - Each path spells the intended word
  - No overlap across paths
  - Every cell is used exactly once
  - All paths are stepwise adjacent

Tip
- If you change the puzzle, you can also expand wordlist.py to include more common non-theme words to make hints easier to earn.

## Deployment Notes

- Change the Flask secret key in main.py before production:
  - app.secret_key = "dev-secret-change-me" → use a strong, secret value from an environment variable
- Behind a production server:
  - Use a WSGI server like gunicorn or uWSGI, and a reverse proxy (nginx)
  - Example (gunicorn): gunicorn -w 2 -b 0.0.0.0:8000 main:app
- Session persistence:
  - Current implementation stores session state in memory. For multi-instance or persistent deployments, replace _SESSIONS with a shared store (e.g., Redis).
- Static assets:
  - Served by Flask in development. In production, consider serving static files via a CDN or reverse proxy.

## Troubleshooting

- The app starts but I see no board
  - Check the console for JavaScript errors
  - Ensure static files are being served (static/app.js, static/style.css)
- My selection keeps flashing red (invalid)
  - Ensure you’re dragging across adjacent cells and not reusing an already claimed cell
  - The selection must match the canonical path for that word; arbitrary anagrams won’t count
  - Single-letter selections are invalid
- Non-theme words don’t grant hints
  - Only words length ≥ 4 and present in wordlist.py count
  - Each non-theme word counts once per session toward hints
- Progress resets unexpectedly
  - Session is in-memory; restarting the server clears it
  - Clearing browser cookies or using a different browser/new session id also resets progress
- Mobile/touch issues
  - Try slower drags; lift your finger to submit selection
  - Ensure you’re not starting on a claimed cell

## For Developers: Data Contracts

/ state response (abridged)
```json
{
  "rows": 6,
  "cols": 8,
  "grid": [["S","O","F","T","W","A","R","E"], ...],
  "theme": "Programming Languages",
  "spangram": "SOFTWARE",
  "foundWords": ["PYTHON", "SWIFT"],
  "hints": 1,
  "nonThemeCount": 2,
  "claimed": [
    {"r": 0, "c": 0, "type": "spangram", "word": "SOFTWARE"},
    {"r": 1, "c": 0, "type": "theme", "word": "PYTHON"}
  ],
  "totalTheme": 9,
  "completed": false
}
```

/select request
```json
{ "coords": [[r, c], [r, c], ...] }
```

/select response (abridged)
```json
{
  "result": { "type": "theme" | "spangram" | "non-theme" | "invalid", "word": "PYTHON", "coords": [[...]] },
  "state": { ... }  // same shape as /state
}
```

/hint response
```json
{
  "result": { "type": "theme" | "spangram" | "none", "word": "KOTLIN", "coords": [[...]] },
  "state": { ... }
}
```

## Accessibility and Theming

- Colors are set as CSS variables in static/style.css. Adjust for contrast or color-blind friendly palettes:
  - --theme (blue), --spangram (yellow), --temp, --non-theme, --invalid
- The board uses role="grid" and gridcell roles for basic semantics.

## License and Credits

- Educational project inspired by NYT Strands’ mechanics. Not affiliated with The New York Times.
- Built with Flask and vanilla JS/CSS.

Enjoy puzzling!