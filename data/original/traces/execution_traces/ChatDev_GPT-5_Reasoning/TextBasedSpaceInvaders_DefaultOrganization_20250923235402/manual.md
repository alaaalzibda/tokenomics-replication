```markdown
# Simple Space Invaders — User Manual

Change the digital world through programming with a classic arcade remake. Simple Space Invaders is a lightweight, dependency-minimal game built with Python and Pygame. Move your ship, fire at alien rows, track your score, and survive with limited lives. The game ends when aliens reach the bottom or you eliminate them all.

- Platform: Desktop (Windows/Mac/Linux)
- Modality: Application
- Language: Python
- Rendering: Pygame

---

## Features

- Classic gameplay: Move left/right, shoot upwards
- Multiple alien rows and columns (configurable)
- Fleet movement: bounce at edges, drop down, and speed up
- Score tracking: +10 points per destroyed alien
- Limited lives: 3 by default with brief invulnerability on hit
- Win/Lose conditions:
  - Victory: Destroy all aliens
  - Game Over: Aliens touch the bottom or you lose all lives
- Simple, readable code with clear separation of concerns
- Pre-rendered starfield background for smooth performance

---

## Quick Start

1) Ensure you have Python 3.8+ installed.
2) Install dependency:
   - pip: `pip install pygame`
3) Run the game:
   - `python main.py`

If Pygame isn’t installed, launching `main.py` will print a friendly hint telling you how to install it.

---

## Controls

- Move Left: Left Arrow or A
- Move Right: Right Arrow or D
- Shoot: Spacebar (hold to auto-fire with cooldown)
- Start/Restart: Enter or Spacebar
- Quit: Esc or close the window

---

## Gameplay

- Aliens start in a grid at the top, moving horizontally.
- When the fleet hits a side margin, they drop down and speed up.
- If any alien reaches the bottom of the screen, it’s an immediate Game Over.
- You start with 3 lives. Colliding with an alien costs one life.
- After losing a life, you respawn at center with short invulnerability and bullets are cleared.
- Score increases by 10 points per alien destroyed.
- Win by eliminating all aliens.

---

## Installation Guide

### 1) Prerequisites
- Python 3.8 or newer
- A desktop environment with graphics support (Pygame creates a window)

### 2) Install Pygame

- Using pip (recommended):
  - `pip install pygame`

- Optional: Create and activate a virtual environment first
  - Windows (PowerShell):
    - `python -m venv .venv`
    - `.venv\Scripts\Activate`
    - `pip install pygame`
  - macOS/Linux:
    - `python3 -m venv .venv`
    - `source .venv/bin/activate`
    - `pip install pygame`

### 3) Run the Game

- `python main.py`
- To quit, press Esc or close the window.

---

## Project Structure

- main.py
  - Entry point; initializes Pygame and starts the game
  - Prints a helpful install message if Pygame is missing
- settings.py
  - All global configuration: window size, colors, gameplay constants, fonts
- entities.py
  - Sprite classes:
    - Player: movement, firing
    - Bullet: upward projectile
    - Alien: enemy sprite
- game.py
  - Game controller and loop
  - AlienFleet manager: collective movement, drop, and speed-up behavior
  - State management: START, PLAYING, GAME_OVER, VICTORY
  - Rendering, collision, scoring, HUD, and UI messages

---

## Configuration and Tuning

Adjust the game’s difficulty and feel via settings.py. Common tweaks:

- Window and FPS
  - WIDTH = 800
  - HEIGHT = 600
  - FPS = 60

- Player
  - PLAYER_SPEED = 6
  - PLAYER_LIVES = 3
  - SHOOT_COOLDOWN_MS = 300
  - INVULNERABLE_MS = 1200

- Bullets
  - BULLET_SPEED = -10  (negative = upwards)
  - BULLET_WIDTH, BULLET_HEIGHT

- Aliens and Fleet
  - ALIEN_ROWS = 5
  - ALIEN_COLS = 10
  - FLEET_START_SPEED = 1.2
  - FLEET_SPEEDUP_FACTOR = 1.06
  - FLEET_DROP_DISTANCE = 18
  - FLEET_MARGIN_X = 30
  - FLEET_TOP_OFFSET = 60

- Scoring and Fonts
  - SCORE_PER_ALIEN = 10
  - BIG_FONT_SIZE, HUD_FONT_SIZE, SMALL_FONT_SIZE

Tips:
- Make it harder: increase FLEET_START_SPEED or FLEET_SPEEDUP_FACTOR; reduce PLAYER_LIVES; increase ALIEN_ROWS.
- Make it easier: reduce ALIEN_ROWS/COLS; increase SHOOT_COOLDOWN_MS to allow less frequent firing pressure; decrease FLEET_SPEEDUP_FACTOR.

---

## Heads-Up Display (HUD) and States

- HUD shows current Score and Lives (small ship icons).
- States:
  - START: “Press Enter or Space to Start”
  - PLAYING: live gameplay
  - GAME_OVER: “Press Enter or Space to Restart”
  - VICTORY: “You Win! Press Enter or Space to Play Again”

---

## Performance Notes

- Target is 60 FPS.
- Background starfield is pre-rendered for stable performance.
- The fleet uses integer pixel movement with a rounding approximation for speed; this keeps motion consistent across systems.

---

## Troubleshooting

- No module named ‘pygame’
  - Run: `pip install pygame` (ensure you’re using the same Python interpreter you’ll use to run the game)
  - If using a virtual environment, activate it first.

- Game window doesn’t appear
  - Ensure you’re running on a desktop OS session (not a headless server).
  - On WSL, you’ll need an X server; running natively on Windows/macOS/Linux is recommended.

- Keyboard input doesn’t work
  - Click the game window to focus it.
  - Check for conflicting global shortcuts.

- Performance issues
  - Close other CPU/GPU-heavy apps.
  - Reduce window size or FPS in settings.py.
  - Lower ALIEN_ROWS/COLS.

- Pygame install fails on macOS (M1/M2)
  - Ensure you’re using an up-to-date Python and pip.
  - Try: `python3 -m pip install --upgrade pip setuptools wheel` then `pip install pygame`.

---

## Extending the Game (Optional Ideas)

- Alien projectiles and player dodge mechanics
- Shields/bunkers between player and aliens
- Multiple levels or waves with increasing difficulty
- Power-ups: faster fire rate, multi-shot, temporary shields
- Sound effects and music
- High score persistence

---

## Credits

- Built by ChatDev as a simple, educational arcade remake using Pygame.
- Product design and documentation by the Chief Product Officer.

Enjoy the game and happy blasting!
```