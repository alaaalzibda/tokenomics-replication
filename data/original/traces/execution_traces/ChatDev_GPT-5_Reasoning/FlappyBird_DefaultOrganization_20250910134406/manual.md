# Flappy Bird (Python) — User Manual

A lightweight, no-assets Flappy Bird clone built with Python and Pygame. Fly a small bird through randomly generated pipe gaps, score points for each successful pass, and survive as difficulty gradually increases.

## Key Features

- Accessible one-button controls (Space/Up Arrow or mouse click)
- Randomized pipe gaps for replayability
- Progressive difficulty:
  - Gaps shrink as you score
  - Pipe speed increases
  - Pipes spawn more frequently
- Clean UI with menu and game-over screens
- High score tracked per session (not persisted across runs)
- No external assets — simple, performant vector graphics

---

## Quick Install

Prerequisites:
- Python 3.8+ (3.10+ recommended)
- pip (Python package installer)

Optional but recommended:
- A virtual environment (venv)

1) Create and activate a virtual environment (optional)
- macOS/Linux:
  ```
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- Windows (PowerShell):
  ```
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```

2) Install dependencies
```
python -m pip install pygame
```

3) Run the game
- macOS/Linux:
  ```
  python3 main.py
  ```
- Windows:
  ```
  python main.py
  ```

If you see an error like “pygame is not installed…”, re-run step 2.

---

## How to Play

- Controls:
  - Space or Up Arrow: Flap (apply upward impulse)
  - Mouse/Touchpad click: Flap
  - R: Restart (on Game Over screen)
  - ESC: Quit

- Objective:
  - Guide the bird through the gaps between oncoming pipes.
  - Earn 1 point for each pipe pair you pass.
  - The game ends if you hit a pipe or the ground.

- Game States:
  - Menu: “Press Space/Click to Start”
  - Playing: Score is shown at the top center
  - Game Over: “Game Over” and your score; press Space/Click or R to restart

Tips:
- Tap/Click in a rhythm to control altitude.
- Early game is forgiving, but difficulty increases with your score.

---

## How Difficulty Scales

Difficulty adapts as you score more points:
- Gap size decreases: from START_GAP down to MIN_GAP
- Pipe speed increases: from START_SPEED up to MAX_SPEED
- Spawn interval decreases: from START_SPAWN_MS down to MIN_SPAWN_MS

This creates a smooth, balanced increase in challenge as you progress.

---

## Configuration and Customization

All tunable settings live in settings.py. You can adjust visuals, physics, and difficulty.

Common options:

- Screen and timing
  - SCREEN_WIDTH, SCREEN_HEIGHT: Window size (default 480x720)
  - FPS: Target frames per second (default 60)

- Colors and ground
  - BG_COLOR, GROUND_COLOR, TEXT_COLOR, UI_COLOR
  - GROUND_HEIGHT: Ground thickness in pixels

- Bird and pipes
  - BIRD_SIZE: Bird sprite size (circle diameter)
  - PIPE_WIDTH: Pipe width

- Physics
  - GRAVITY: Gravity acceleration per frame
  - FLAP_STRENGTH: Upward impulse on flap (negative value)
  - MAX_DROP_SPEED: Clamp on downward velocity

- Difficulty
  - START_GAP, MIN_GAP
  - START_SPEED, MAX_SPEED
  - START_SPAWN_MS, MIN_SPAWN_MS

Make it easier:
- Increase START_GAP
- Decrease START_SPEED
- Increase START_SPAWN_MS

Make it harder:
- Decrease START_GAP (not below MIN_GAP)
- Increase START_SPEED (not above MAX_SPEED)
- Decrease START_SPAWN_MS (not below MIN_SPAWN_MS)

Note: Extreme values can make the game unplayable; adjust incrementally.

---

## Running in Different Environments

- Desktop (Windows/macOS/Linux):
  - Run as described in Quick Install. A game window will open.

- Headless/CI environments:
  - The game automatically sets SDL_VIDEODRIVER=dummy when no display is detected to avoid crashes. This mode is primarily for automated checks; there is no visible window.

- WSL (Windows Subsystem for Linux):
  - For a visible window, use an X server (e.g., X410, VcXsrv) and export DISPLAY properly.
  - Otherwise, the dummy driver may be used (no visible output).

---

## Troubleshooting

- “Pygame is not installed…”
  - Run: `python -m pip install pygame`
  - Ensure you’re using the same interpreter for install and run (check `python --version`).

- Black screen or no window:
  - Ensure a display environment is available. On headless systems, a “dummy” driver is used; no window is expected.
  - On macOS, try running with `python3 main.py`.

- Poor performance:
  - Reduce SCREEN_WIDTH/SCREEN_HEIGHT in settings.py.
  - Lower FPS slightly (e.g., 50).
  - Close other heavy apps.

- Controls unresponsive:
  - Ensure the game window has focus.
  - Try Space/Up Arrow or mouse click.

- Game feels too hard/easy:
  - Adjust difficulty constants in settings.py (see Configuration and Customization).

---

## Project Structure

- main.py
  - Entry point; ensures pygame is installed; initializes and starts the game loop.

- game.py
  - Core loop (handle events, update, draw)
  - Spawning, scoring, collision detection
  - Difficulty scaling and state management (menu, playing, gameover)

- sprites.py
  - Bird: physics (gravity, flap, rotation), drawing, collision rect
  - PipePair: movement, collision rects, pass detection, drawing

- settings.py
  - All configuration: screen, colors, physics, and difficulty parameters

No external assets are required; all graphics are drawn procedurally.

---

## Gameplay Details (For the Curious)

- Scoring:
  - You score when the bird’s x-position passes the pipe’s right edge.
  - Each pipe pair can be scored only once.

- Collisions:
  - Hitting any part of a pipe or touching the ground ends the run.
  - Touching the top of the screen is clamped (no game over), to keep gameplay fair.

- High Score:
  - Tracked in memory while the app is running.
  - Not persisted to disk across runs.

---

## Contributing and Extending

Ideas to expand the game:
- Persist high scores to a file (e.g., JSON) or a small DB
- Add sound effects for flap, score, and game over
- Add animated sprites and backgrounds
- Add a pause feature
- Difficulty modes (Easy/Normal/Hard) with preset settings
- Touchscreen-friendly UI elements

Development tip:
- Keep gameplay tuning in settings.py to avoid changing game logic.

---

## License and Credits

This project is a simple educational example inspired by the original Flappy Bird concept (all original assets and IP belong to their respective owners). This implementation uses only original, programmatic graphics and Python/Pygame code.

If you need production support, packaging, or feature extensions, please reach out to our team.