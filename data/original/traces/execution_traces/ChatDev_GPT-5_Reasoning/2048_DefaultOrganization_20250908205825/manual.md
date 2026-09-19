# 2048 (Web, Python/Flask) – User Manual

Changing the digital world through programming

This manual explains how to install, run, and play the 2048 web game delivered as a Python/Flask application. It also covers the game rules, UI controls, available APIs, and common troubleshooting tips.

## Overview

- Modality: Website
- Language: Python (Flask backend) + HTML/CSS/JS frontend
- Grid: 4x4 standard 2048
- Controls: Arrow keys
- Objective: Combine tiles with the same number to reach the highest possible tile. Track your current score and highest tile achieved.

Key features:
- Authentic 2048 mechanics (slide, merge, spawn)
- Server-side game logic to ensure consistent rules and scoring
- Persistent session per browser via secure cookies
- Live score and max tile display
- Game over detection and overlay with “Try Again”

## How It Works

- Press an arrow key to slide all tiles in that direction.
- Tiles with the same value that collide will merge into one, doubling their value.
- After a valid move (i.e., when the board changes), a new tile (2 with 90% probability or 4 with 10%) spawns in a random empty cell.
- Your score increases by the sum of merged values created in a move.
- The game ends when no moves are possible (no empty cells and no adjacent equal tiles).
- The highest tile you’ve reached is tracked and displayed.

## Project Structure

- main.py – Flask app and HTTP endpoints
- game.py – Pure Python 2048 game engine (rules, moves, scoring)
- templates/index.html – Main web page
- static/app.js – Client-side logic (keyboard handling, rendering, API calls)
- static/styles.css – Styling

## Requirements

- Python 3.9+ (3.10 or later recommended)
- Pip
- A modern browser (Chrome, Firefox, Edge, Safari)

Python package:
- Flask >= 2.3

Optional: virtualenv/venv for isolated environment.

### Suggested requirements.txt

If you prefer to install from a file, create requirements.txt with:
```
Flask>=2.3
```

## Setup and Installation

1) Clone or download the project files to your machine.

2) (Recommended) Create and activate a virtual environment:
- macOS/Linux:
  ```
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- Windows (PowerShell):
  ```
  py -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```

3) Install dependencies:
```
pip install -r requirements.txt
```
or
```
pip install Flask>=2.3
```

4) (Optional for production) Set a secure secret key for sessions:
- macOS/Linux:
  ```
  export SECRET_KEY='replace-with-a-strong-random-value'
  ```
- Windows (PowerShell):
  ```
  setx SECRET_KEY "replace-with-a-strong-random-value"
  ```

## Running the Game Locally

Start the Flask app:
```
python main.py
```

By default, the server starts at:
- http://localhost:5000

Open that URL in your browser to play.

Notes:
- The app runs with debug=True by default in main.py. For production, set debug to False and run behind a proper WSGI server (e.g., gunicorn) or platform of choice.

## Playing the Game

- Use the arrow keys (Up/Down/Left/Right) to slide tiles.
- The board and scores update after the server processes your move.
- When no moves remain, a Game Over overlay appears.
- Click “Try Again” or “New Game” to start a fresh session.

Scoring:
- When two tiles merge (e.g., 4 + 4 → 8), you earn points equal to the resulting tile (8 points in this example).
- A single move may merge multiple pairs in different positions; the score increments by the total of all merges.

Highest tile (Max):
- The UI shows the largest tile reached so far in the current game.

## UI Reference

- Header: Shows the game title and two boxes for Score (current score) and Max (highest tile).
- Controls:
  - New Game: Resets the server-side state and spawns two starting tiles.
  - Hint: Reminder about arrow keys.
- Board: 4x4 grid; empty cells are lightly shaded; tiles change color based on value.
- Overlay: Appears on Game Over with a “Try Again” button.

## API (For Integrators and Advanced Users)

All game rules are enforced server-side. The frontend uses these endpoints:

- GET /
  - Serves the HTML page.

- POST /init
  - Starts a new game session (spawns two tiles).
  - Response:
    ```
    {
      "ok": true,
      "state": {
        "board": [[...4 cols...], ...4 rows...],
        "score": 0,
        "max_tile": 2|4,
        "size": 4,
        "game_over": false
      }
    }
    ```

- GET /state
  - Returns current game state from the session.
  - Response same as above.

- POST /move
  - Payload:
    ```
    { "dir": "up" | "down" | "left" | "right" }
    ```
  - Returns updated state. If the move changed the board, a new tile is spawned before returning the state.
  - Example response:
    ```
    {
      "ok": true,
      "changed": true,
      "gained": 8,
      "state": {
        "board": [[...]],
        "score": 40,
        "max_tile": 64,
        "size": 4,
        "game_over": false
      }
    }
    ```
  - If no more moves are possible, game_over is true.

Notes:
- Sessions are cookie-based. Each browser session gets its own game, persisted until you reset or the session cookie expires/clears.

## Customization and Extensibility

- Styling:
  - Adjust tile sizes, colors, and fonts in static/styles.css.
  - CSS variables at the top control common theming (cell size, gaps, etc.).

- Board Size:
  - The engine supports NxN boards via the size parameter in Game2048, but the app currently initializes with 4.
  - To change (advanced):
    - Update Game2048() instantiation in main.py:new_game() to Game2048(size=5).
    - The frontend reads size from the server and will render accordingly.

- Tile Spawn Odds:
  - In game.py, add_random_tile() controls spawn value probabilities (90% for 2, 10% for 4). Modify as desired.

- Animations:
  - The frontend uses simple transitions. You can extend app.js and styles.css for advanced animations (e.g., slide/merge effects).

## Production Deployment Tips

- Use a production WSGI server (e.g., gunicorn, uWSGI) in front of Flask:
  ```
  pip install gunicorn
  gunicorn -w 2 -b 0.0.0.0:5000 main:app
  ```
- Set a strong SECRET_KEY environment variable.
- Run behind a reverse proxy (e.g., Nginx) with TLS.
- Disable debug mode in main.py for production.

## Troubleshooting

- The page loads but keys don’t work:
  - Ensure the browser window has focus. Click anywhere on the page and try again.
  - Certain extensions may capture arrow keys—try an incognito/private window.

- “Failed to move” errors in console:
  - Check the server logs for HTTP errors.
  - Ensure the server is running at http://localhost:5000 and there are no ad blockers or CSP violations.

- State doesn’t persist:
  - Cookies must be enabled. Session data is stored via secure cookies.
  - If you changed SECRET_KEY between server restarts, existing session cookies will become invalid, causing a new session to start.

- Styling looks off:
  - Clear your browser cache or do a hard refresh (Ctrl+F5 / Cmd+Shift+R).

## Security and Privacy

- Session management uses Flask’s signed cookies via app.secret_key.
- For production, set SECRET_KEY to a strong, unpredictable value and keep it secret.
- No user data beyond the game state is collected by default.

## FAQs

- Can I play on mobile?
  - Yes. The UI is responsive, but movement currently uses keyboard events. You can add swipe handling in app.js if needed.

- Can I continue where I left off after closing the tab?
  - Yes, as long as your session cookie remains valid and you return to the same browser/device. Clearing cookies will reset the game.

- How do I change the initial number of tiles?
  - Modify Game2048.__init__ or reset() in game.py. By default, two tiles spawn at start.

- Can I integrate the backend with another client?
  - Yes. Use the JSON endpoints (/state, /move, /init). Maintain cookies to persist the same session.

## Credits

- Built by ChatDev, powered by multiple intelligent agents.
- Product design and documentation: Chief Product Officer, ChatDev.

Enjoy the game!