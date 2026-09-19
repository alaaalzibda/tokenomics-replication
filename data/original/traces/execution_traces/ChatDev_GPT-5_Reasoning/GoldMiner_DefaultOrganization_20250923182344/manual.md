# Gold Miner (PyScript Edition) — User Manual

Change the digital world through programming with a classic arcade twist. Gold Miner (PyScript Edition) is a browser-based game written in Python and rendered via HTML Canvas using PyScript/Pyodide. Time your grab, reel in valuable items, avoid hazards, and beat the goal before the clock runs out.

## Highlights

- Classic gold-mining gameplay: swing, grab, reel-in.
- Real-time display of claw and object positions with each grab.
- Dynamic difficulty: tighter time limits, higher goals, and more obstacles at higher levels.
- Runs entirely in the browser via PyScript (no backend, no Python install required to play).
- Minimal footprint—no external Python packages.

---

## 1) What’s in the Box

Project structure:
- index.html — Web entry point; loads PyScript and runs the game.
- main.py — Game loop, rendering, input handling, level transitions.
- models.py — Core game entities (Claw, MineObject) and physics.
- level.py — Level generator and difficulty curve.
- requirements.txt — Notes that no external packages are needed.

---

## 2) Requirements

- A modern desktop browser with internet access:
  - Chrome, Edge, Firefox, or Safari (latest versions recommended).
- No Python installation required to play. PyScript loads Python in the browser.

Optional (for local hosting and development):
- Python 3.8+ (only if you want to run a local static server).
- A simple static server (Python’s http.server, VS Code Live Server, or similar).

Note: The default setup fetches PyScript assets from the web (https://pyscript.net/latest). Internet connectivity is required unless you vendor PyScript locally.

---

## 3) Quick Start (Players)

Fastest way:
1. Download/extract the project files into a single folder.
2. Open index.html in your browser (double-click the file).
3. Wait for PyScript to load. The game starts automatically.

If your browser blocks local module loading, use a local server:

Option A — Python’s built-in server
- From the project folder, run:
  ```
  python -m http.server 8000
  ```
- Open:
  ```
  http://localhost:8000/
  ```
- Click index.html in the file listing.

Option B — VS Code Live Server
- Open the folder in VS Code.
- Install the “Live Server” extension.
- Right-click index.html → “Open with Live Server”.

---

## 4) How to Play

- Goal: Reach the minimum gold value before time runs out.
- Controls:
  - Press Space or Enter to launch the claw.
  - Or click the canvas with the mouse to launch the claw.
- The claw swings automatically. Launch while swinging to determine direction.
- The rope extends until it hits an object or reaches max length, then retracts.
- Retraction speed depends on object weight (heavier = slower).
- When the claw returns to the top:
  - If an object is attached, it’s collected and your score updates immediately.
  - The display shows the updated positions and remaining time.

Winning and progressing:
- Meet or exceed the Goal before time expires → Level Complete overlay → “Next Level”.
- Time expires but you didn’t meet the goal → “Retry” overlay.

---

## 5) Objects and Effects

Each object has:
- Value (affects your score).
- Weight (affects reel-in time).
- Collision radius and color (for visibility).

Objects you’ll encounter:
- Gold (small/large): Positive value. Heavier nuggets take longer to reel in.
- Diamond: High value and light weight (fast to reel in).
- Rock: Low value and heavy (slow to reel in; mostly an obstacle).
- Bomb: Negative value; moderate weight; additionally reduces time by 3 seconds when collected.

Tip: Diamonds are fast, bombs are costly, rocks slow you down.

---

## 6) Levels and Difficulty

Increasing difficulty per level:
- Time limit decreases by 5 seconds each level (down to a 25-second minimum).
- Goal increases by 220 points per level.
- The number of rocks, bombs, and larger gold pieces grows over time.
- Object placement varies each level, with limited overlap to keep layouts fair but fresh.

---

## 7) On-Screen HUD and Overlay

- HUD (top-left):
  - Level, Score, Goal, Time, and current Claw position (x, y).
- Object labels:
  - Show kind and value near each object.
  - Bombs show negative values (e.g., “bomb $-180”).
- Overlay (between levels):
  - Displays results and buttons:
    - Next Level (on success)
    - Retry (on failure)

---

## 8) Installation and Environment Details

Playing (no installation):
- Just open index.html with internet access. PyScript loads and runs Python in the browser.

Developing or hosting locally:
- Python 3 is optional but useful to serve static files.
- requirements.txt confirms there are no external packages to install.

Pinning PyScript (optional):
- The project uses the “latest” PyScript. To pin a specific version, replace the links in index.html with a specific release, for example:
  - https://pyscript.net/2024.6.1/pyscript.css
  - https://pyscript.net/2024.6.1/pyscript.js

Offline usage (advanced):
- Vendor PyScript assets and reference them locally in index.html.
- Ensure index.html, main.py, models.py, and level.py remain accessible through the same origin (local server recommended).

---

## 9) Tips and Strategy

- Launch when the claw is aligned with valuable targets.
- Diamonds are quick wins; large gold is high value but slows you down.
- Avoid bombs unless unavoidable—they reduce both score and time.
- Grab nearer targets first to build momentum, then go for heavier items with remaining time.

---

## 10) Troubleshooting

- Blank page or UI doesn’t load:
  - Ensure you have internet access; PyScript must be fetched from the web unless locally hosted.
  - Try hosting via a local server (see Quick Start).
  - Check browser console for errors.

- “Gold Miner requires PyScript (browser). Headless mode: skipping UI.”:
  - You attempted to run main.py in a standard Python environment. The game runs in the browser. Open index.html instead.

- Slow performance:
  - Close other heavy tabs or apps.
  - Use a desktop browser.
  - Resize the browser window if your machine struggles.

- Input not working:
  - Make sure the canvas is focused; click once on the game area.
  - Space/Enter or mouse click launches grabs. Grabs only start while the claw is in “swing” state.

---

## 11) For Developers

Core files:
- models.py
  - MineObject: kind, value, weight, color, collision radius.
  - Claw: swing parameters, rope length, extend/retract speeds, state machine.
- level.py
  - LevelManager: time limit and goal scaling, object spawning, and collision-safe placement.
- main.py
  - Game loop (requestAnimationFrame), input, rendering, level transitions, HUD/overlay.

Easy customizations:
- Difficulty curve (level.py):
  - base_time, min_time, base_goal, goal_step.
- Object counts and properties (spawn_objects in level.py).
- Physics (models.py → Claw):
  - swing angle limits, speeds, rope length limits, hook radius.
- Bomb penalty (main.py → Game.update): score/time adjustment.

Testing headless:
- Running main.py in a non-browser environment prints a small smoke test but does not start the UI.

---

## 12) Deployment

- Static hosting works great (GitHub Pages, Netlify, Vercel, S3).
- Upload all files (index.html, main.py, models.py, level.py).
- Ensure index.html references PyScript via HTTPS or your own hosted copies.
- Open your hosted URL to play.

---

## 13) FAQ

- Do I need Python installed?
  - No. The game runs in the browser via PyScript.

- Can I play offline?
  - By default, no—PyScript is loaded from the internet. You can vendor PyScript locally to enable offline play.

- Does it work on mobile?
  - It may load, but the UI is optimized for desktop screens (900x600 canvas). Desktop is recommended.

- Is there persistence between levels or sessions?
  - No. Scores are per-session, and levels are sequential without saving to storage.

---

Enjoy mining! If you need enhancements (sounds, touch controls, mobile layout, or new object types), the codebase is straightforward to extend—feel free to iterate and share improvements.