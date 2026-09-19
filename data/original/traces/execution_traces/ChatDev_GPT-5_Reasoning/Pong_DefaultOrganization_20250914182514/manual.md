# ChatDev Pong — Two Player

A modern, responsive take on the classic two‑player Pong arcade game. Two players face off on one keyboard, each controlling a vertical paddle to bounce a ball back and forth. The ball rebounds off the top/bottom walls and paddles, speeds up on paddle hits, and points are awarded when an opponent misses. A winning score threshold ends the match, and the ball resets after each point with a brief countdown.

- Platform: Desktop (Windows, macOS, Linux)
- Modality: Application
- Language: Python
- Library: Pygame


## Key Features

- Two-player local multiplayer (Left: W/S, Right: ↑/↓)
- Smooth, framerate-independent movement
- Ball physics with angle control based on hit position
- Progressive ball speed increase up to a cap
- Top/bottom wall bounce and reliable paddle collision
- Scoring, winning threshold, and match reset
- Serve cooldown with on-screen countdown after each point
- Clean UI: dashed center line, scores, status and control hints
- High-performance loop (target 120 FPS)


## Quick Start

1) Install Python (3.8+ recommended; 3.9–3.12 tested)

2) Create and activate a virtual environment (optional but recommended)
- Windows (PowerShell):
  ```
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- macOS/Linux:
  ```
  python3 -m venv .venv
  source .venv/bin/activate
  ```

3) Install dependency
```
pip install "pygame>=2.3,<2.6"
```
If you prefer the latest available:
```
pip install pygame
```

4) Run the game
```
python main.py
```
If Pygame is missing, the app will print an install hint and exit cleanly.


## How to Play

- Objective: Keep the ball in play with your paddle. Score a point when your opponent misses.
- Controls:
  - Left player: W (up), S (down)
  - Right player: Up Arrow (up), Down Arrow (down)
  - Esc: Quit the game
  - R: Restart after the match ends
- Gameplay:
  - The ball bounces off the top and bottom edges.
  - When the ball hits a paddle, it speeds up slightly and its angle changes based on where it hits the paddle.
  - When a point is scored, play pauses with a short “Get ready…” countdown. The next serve goes toward the player who missed last.
  - First to 7 points wins by default (configurable).
- Tips:
  - Aim your returns by hitting the ball closer to the top or bottom of your paddle to change its angle.
  - If gameplay feels too fast/slow, adjust speeds in settings.py (see Customization).


## Installation and Environment Details

- Requirements:
  - Python 3.8+ (3.9–3.12 recommended)
  - Pygame 2.x
- OS: Windows 10/11, macOS 10.15+ (Intel/Apple Silicon), Linux with a working display (X11/Wayland)
- Hardware: Keyboard and a display capable of 900×600 resolution

Verify your Pygame installation:
```
python -c "import pygame; print(pygame.version.ver)"
```

Common platform notes:
- Windows: If activation of venv fails, use “Run as Administrator” or unblock scripts policy for the session: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
- macOS (Apple Silicon): Ensure you’re using a Python build compatible with your architecture. If needed:
  ```
  python3 -m pip install --upgrade pip setuptools wheel
  python3 -m pip install pygame
  ```
- Linux: Modern Pygame wheels bundle SDL. If using older distros or building from source, ensure SDL2 and dev headers are available.


## Project Structure

- main.py
  - Entry point. Imports pygame defensively and runs the Game loop.
- game.py
  - Orchestrates input, updates, rendering, scoring, cooldowns, and win state.
- entities.py
  - Paddle and Ball classes, including movement, collisions, and drawing.
- settings.py
  - Centralized configuration for window, colors, speeds, UI sizes, winning score, etc.


## Customization

All essential tuning is in settings.py. Edit values and re-run.

- Window and performance
  - SCREEN_WIDTH, SCREEN_HEIGHT: Change resolution (e.g., 1280×720)
  - FPS: Target framerate (default 120)
- Colors and UI
  - COLOR_BG, COLOR_FG, COLOR_DIM, COLOR_ACCENT
  - SCORE_FONT_SIZE, INFO_FONT_SIZE, WIN_FONT_SIZE
  - CENTER_DASH_HEIGHT, CENTER_DASH_GAP
- Paddles
  - PADDLE_WIDTH, PADDLE_HEIGHT
  - PADDLE_SPEED: Pixels per second (e.g., 400.0 for slower, 650.0 for faster)
- Ball
  - BALL_RADIUS
  - BALL_START_SPEED: Initial speed magnitude
  - BALL_MAX_SPEED: Upper bound to keep it playable
  - BALL_SPEEDUP_FACTOR: Speed multiplier on paddle hits (e.g., 1.03 = gentler ramp-up)
- Scoring and flow
  - WINNING_SCORE: Points needed to win (e.g., 11)
  - SERVE_COOLDOWN_MS: Delay after each point (e.g., 1500)

Controls
- The default controls are W/S and Arrow keys. To change keys, edit process_input in game.py, replacing pygame.K_w, pygame.K_s, pygame.K_UP, pygame.K_DOWN with your preferred keys (e.g., pygame.K_a, pygame.K_z).


## Gameplay Details (Under the Hood)

- Movement is frame-rate independent using delta time for consistent speed at different FPS.
- Ball angle changes based on impact point along the paddle:
  - Hitting near the paddle’s center yields a flatter trajectory.
  - Hitting near the edges yields steeper angles.
- On paddle hit, ball speed increases by BALL_SPEEDUP_FACTOR up to BALL_MAX_SPEED.
- Serve logic:
  - After a point, the ball is reset to center.
  - A countdown shows, then the serve launches toward the player who missed the last ball.
- Winning state:
  - When a player reaches WINNING_SCORE, the game announces the winner and waits for R to restart or Esc to quit.


## Troubleshooting

- “Pygame is required to run this game…” shows and exits
  - Run: pip install pygame
  - Ensure you’re in the correct virtual environment (if using one).
- Window opens but is black or unresponsive
  - Update your graphics drivers and ensure a functioning display session.
  - Try lowering resolution (SCREEN_WIDTH/HEIGHT) or FPS in settings.py.
- Input lag or missed inputs
  - Close background apps that may capture keyboard focus.
  - Ensure your system isn’t throttling (laptops on low-power modes).
- On Linux in headless/WSL environments
  - A GUI/X server is required. Use WSLg on Windows 11 or run the game natively on Windows/macOS/Linux with a display.
- Pygame install errors
  - Upgrade build tools:
    ```
    python -m pip install --upgrade pip setuptools wheel
    ```
  - macOS: Install Xcode Command Line Tools if prompted.
  - If issues persist, install a specific compatible version:
    ```
    pip install "pygame>=2.3,<2.6"
    ```


## Extending the Game (Optional Ideas)

- Add sound effects with pygame.mixer for paddle hits and scoring.
- Add a pause toggle (e.g., P key) and paused overlay.
- AI opponent mode: Move one paddle toward the ball’s y-position with a capped speed and reaction delay.
- Power-ups: Change paddle size temporarily or alter ball speed.
- Fullscreen mode: Change the display flags in game.py:
  ```
  self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
  ```


## License and Credits

- Built by ChatDev as a sample two‑player arcade game.
- Uses Pygame (https://www.pygame.org/), licensed under LGPL.
- All other code in this repository is provided for demonstration and educational purposes.

Enjoy the game!