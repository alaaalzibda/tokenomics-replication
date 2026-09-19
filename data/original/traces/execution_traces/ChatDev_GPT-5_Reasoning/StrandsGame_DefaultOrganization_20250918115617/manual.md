# Strands — A Word‑Segmentation Puzzle

Change the digital world through programming: Strands is a themed, NYT Strands‑inspired word/phrase puzzle. Players combine small text “strands” to reconstruct complete words or phrases. The app provides instant feedback on valid merges, partial progress, and mistakes, and confirms completion when all targets are found.

This manual explains the game, how to install and run the website, how to play, the API, and how to add new puzzles.

## At a Glance

- Themed puzzles (e.g., Fruits, Cafe Menu, Tech Buzzwords)
- Drag‑and‑drop or click‑to‑assemble strands
- Smart feedback:
  - ok: full valid solution
  - partial: valid path toward a solution
  - invalid: not a valid merge, with hints
- Progress tracking, restart, and new/random puzzle
- REST API for puzzle data and verification

## System Requirements

- Python: 3.8+ (3.9+ recommended)
- pip
- Modern browser (Chrome, Edge, Firefox, Safari; latest two versions)

## Quick Start

1) Clone or download the project.

2) Create and activate a virtual environment:
- macOS/Linux:
  - python3 -m venv .venv
  - source .venv/bin/activate
- Windows (PowerShell):
  - python -m venv .venv
  - .venv\Scripts\Activate.ps1

3) Install dependencies:
- pip install -r requirements.txt

4) Run the server:
- python main.py

5) Open the app:
- Visit http://127.0.0.1:5000

## Files and Structure

- main.py — Flask web app and REST API endpoints
- puzzle.py — Puzzle model, segment generation, and merge verification
- templates/index.html — Main UI
- static/js/app.js — Front‑end logic
- static/css/style.css — UI styles
- requirements.txt — Python dependencies

## How to Play

1) Choose a puzzle:
- Use “Load” to pick Fruits, Cafe Menu, or Tech Buzzwords
- Or click “New Puzzle” for a random one

2) Build words/phrases:
- Drag strands from the Strand Bag into the Assemble area, or click a strand to add it
- Order matters—strands must be in the correct sequence

3) Submit your merge:
- Click “Submit Merge” to check

4) Read the feedback:
- ok: Full solution found; strands are removed and added to “Found Phrases”
- partial: Your sequence is valid so far; keep going
- invalid: Not a valid merge; hints provided (e.g., “order seems off” or “resembles …”)

5) Manage your attempt:
- Undo removes the last added strand
- Clear empties your current assembly
- Shuffle randomizes the bag view
- Restart resets the current puzzle progress

6) Finish:
- When all target phrases are found, you’ll see “Puzzle Complete! 🎉”

Notes:
- Matching ignores spaces and punctuation (e.g., “neural network” matches “neuralnetwork”)
- Phrases can be multiple words
- You cannot reuse strands already used to solve a phrase

## Game Mechanics and Rules

- Normalization: Matching is done on lowercase alphanumeric characters only (spaces and punctuation are stripped)
- Segments: Each target is split into 2–4 character chunks (no leftover of length 1). Very short words (≤3) may remain as a single piece
- Deterministic generation: Segmentation uses the puzzle id as a seed so puzzles are reproducible
- Validation rules:
  - All selected strands must belong to the same phrase
  - Segments must be in strictly increasing, contiguous order
  - A full solution must include all segments of that phrase from start to end
- Feedback:
  - ok: Full match; phrase is removed from the bag
  - partial: Valid partial path (either a correct prefix or a contiguous middle/end sequence)
  - invalid: Mixed phrases, wrong order, gaps, or not a target; may include a “resembles …” hint

## UI Overview

- Header: New Puzzle, puzzle selector, Load
- Info bar: Theme name and progress counter (Found/Total)
- Main board:
  - Strand Bag: available strands (draggable/clickable)
  - Assemble area: place and order your strands
  - Actions: Shuffle, Restart, Undo, Clear, Submit Merge
  - Feedback: live status and hints
- Sidebar:
  - Found Phrases: confirmed solutions
  - Completion banner

Accessibility:
- Drag‑and‑drop plus click interactions
- Live feedback region announces messages (aria‑live)

## Configuration and Deployment

- Secret key: For production, change app.secret_key in main.py
  - app.secret_key = "change-this-secret-in-production"
- Debug mode: main.py starts Flask with debug=True for development; turn off in production
- Reverse proxy: ProxyFix is enabled; ensure standard X‑Forwarded headers are set by your proxy
- Production server: Run behind a WSGI server (e.g., gunicorn, uWSGI)
  - Example (gunicorn):
    - gunicorn -w 4 -b 0.0.0.0:8000 main:app

Security tips:
- Use a strong, environment‑specific secret key
- Set SESSION_COOKIE_SECURE and related flags in production if needed
- Restrict debug tools to development only

## REST API

All responses are JSON.

1) GET /api/puzzle?id={puzzle_id?}
- Purpose: Fetch a puzzle and initialize session state
- Query:
  - id optional (e.g., fruits1, cafe1, tech1); if omitted, a random puzzle is returned
- Response fields:
  - id: puzzle id
  - theme: puzzle theme
  - phrase_count / phrases_total: total number of targets
  - segments: list of available segments (id, text, phrase_index, seg_index)
  - solved: phrases already solved in this session
  - complete: whether all phrases are solved

2) GET /api/state?id={puzzle_id}
- Purpose: Read session progress for a puzzle
- Response:
  - id, solved (human‑readable list), complete, used_segments (segment ids already consumed)

3) POST /api/submit
- Purpose: Validate a proposed merge
- Body:
  - puzzle_id: string
  - segment_ids: ordered array of strand ids
- Responses:
  - ok:
    - status: "ok"
    - message: success message
    - solved_phrase: string
    - remaining_segments: updated list of segments still available
    - solved: list of solved phrases
    - complete: boolean
  - partial:
    - status: "partial"
    - message: guidance
    - phrase_index (and optionally assembled)
  - invalid:
    - status: "invalid"
    - message: reason/hint

4) POST /api/reset
- Purpose: Reset session state for a puzzle
- Body: { "puzzle_id": "..." }
- Response: { "status": "ok", "message": "Puzzle reset." }

5) GET /api/new
- Purpose: Start a new random puzzle and initialize state
- Response: { "status": "ok", "id": "puzzle_id" }

Example submit:
- curl -X POST http://127.0.0.1:5000/api/submit -H "Content-Type: application/json" -d '{"puzzle_id":"fruits1","segment_ids":["fruits1-0-0","fruits1-0-1"]}'

## Adding or Editing Puzzles

All puzzles are defined in puzzle.py, PuzzleBank._load.

1) Create a new StrandPuzzle:
- StrandPuzzle(
  - id="animals1",
  - theme="Animals",
  - phrases=["polar bear", "kangaroo", "elephant", "otter", "giraffe"]
)

2) Add it to the list in puzzles_seed, then restart the server.

Notes:
- Phrases can include spaces and punctuation; these are ignored when splitting/matching
- Segments are regenerated automatically and deterministically based on the id
- Use a unique id for each puzzle

Advanced:
- For dynamic or external storage, replace PuzzleBank._load with a data source (e.g., JSON or database) and ensure deterministic ids to maintain reproducible segmentation

## Troubleshooting

- “Failed to load puzzle.”:
  - Check server console output for errors
  - Confirm Python, Flask versions match requirements.txt
- “Puzzle not found” (404):
  - Verify the id (use GET /api/puzzle without id to get a valid one)
- “Already used” warning when adding a strand:
  - That strand was consumed by a solved phrase; it no longer appears in the bag
- “These strands belong to the same word/phrase, but the order seems off.”:
  - Reorder your assembly to match the true segment sequence
- Session lost after restart:
  - Development servers store sessions in cookies; changing the secret key invalidates old sessions

## Design Rationale

- Clear, approachable gameplay inspired by NYT Strands
- Deterministic segmentation enables consistent puzzles across sessions
- Concise hints encourage learning without spoilers
- Simple, accessible UI supporting both mouse and touch/click interactions

## License and Credits

- © ChatDev — Strands
- Inspired by NYT Strands (link in footer)
- Built with Flask and vanilla JS/CSS

Enjoy solving!