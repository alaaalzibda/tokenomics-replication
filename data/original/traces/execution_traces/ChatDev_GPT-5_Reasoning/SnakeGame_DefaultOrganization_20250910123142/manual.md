# Snake by ChatDev — User Manual

A polished, classic Snake game built with Python and Pygame. Control a growing snake, eat food, avoid collisions, and climb the leaderboard across multiple difficulty levels.

## Highlights

- Classic Snake gameplay with smooth grid-based movement
- Four difficulty levels (Easy, Normal, Hard, Insane)
- Score tracking and on-screen HUD
- Pause/Resume, Restart, and Menu access in-game
- Keyboard and mouse support; responsive UI
- Clean codebase for easy customization

---

## System Requirements

- OS: Windows, macOS, or Linux
- Python: 3.8 or later
- Dependencies: Pygame (automatically installed via requirements.txt)

Recommended window size: 600 × 600 (configured via settings.py)

---

## Quick Start

1) Clone or download the project source.

2) Create and activate a virtual environment (recommended):
- Windows (PowerShell):
```
py -m venv .venv
.venv\Scripts\Activate.ps1
```
- macOS/Linux:
```
python3 -m venv .venv
source .venv/bin/activate
```

3) Install dependencies:
```
pip install --upgrade pip
pip install -r requirements.txt
```

4) Run the game:
- Windows:
```
py main.py
```
- macOS/Linux:
```
python3 main.py
```

---

## How to Play

- Movement: Arrow Keys or WASD
- Pause/Resume: P or Space
- Restart current round: R
- Back to difficulty menu: M
- Quit: ESC or Q
- Menu selection: Use mouse to click buttons or press number keys 1–4 to select a difficulty

Objective:
- Eat red food squares to grow and score points (+1 per food).
- Don’t collide with the walls or your own body.
- Fill the board to win.

Game Over:
- Occurs on boundary collision or self-collision.
- A Game Over overlay appears with options to Restart, go to Menu, or Quit.

Pause:
- Press P or Space to pause/resume. A semi-transparent overlay indicates paused state with quick tips.

---

## Difficulty Levels

Adjust the speed (moves per second):
- Easy: 8
- Normal: 12
- Hard: 16
- Insane: 22

Tip: Start with Easy or Normal to get used to the input timing and movement.

---

## Scoring and Rules

- Score: +1 per food eaten
- Growth: The snake grows by 1 segment after eating
- Victory: If no free cells remain for spawning food (i.e., you fill the board), you win
- Movement: Direction changes are throttled to one change per movement tick to prevent accidental 180° reversals

---

## User Interface

- Main Menu (Difficulty Selector):
  - Title at the top
  - Four difficulty buttons (click or press 1–4)
  - ESC/Q to quit
- In-Game HUD:
  - Top-left: “Score: N    DifficultyName”
  - “[PAUSED]” tag appears when paused
- Overlays:
  - Pause Overlay: Title + controls hint
  - Game Over / You Win Overlay: Title + restart/menu/quit hints

---

## Project Structure

- main.py — App entry point, difficulty menu, game launcher
- game.py — Core game loop, input handling, rendering, collisions, scoring
- snake.py — Snake entity: body, movement, growth, collision with self
- food.py — Food entity: spawning on free grid cells, drawing
- settings.py — Game configuration (grid size, colors, speeds, title, scoring)
- ui.py — UI helpers (Button widget, text drawing)
- requirements.txt — Python dependencies (Pygame)

---

## Configuration and Customization

Adjust settings in settings.py:
- Grid and window size:
  - CELL_SIZE = 20
  - GRID_WIDTH = 30
  - GRID_HEIGHT = 30
  - WIDTH = CELL_SIZE * GRID_WIDTH
  - HEIGHT = CELL_SIZE * GRID_HEIGHT
- Colors: BG_COLOR, GRID_COLOR, SNAKE_HEAD_COLOR, SNAKE_BODY_COLOR, FOOD_COLOR
- Difficulty speeds: DIFFICULTY_SPEEDS (moves per second)
- Scoring: FOOD_SCORE

Examples:
- Make the game faster or slower by editing DIFFICULTY_SPEEDS
- Increase GRID_WIDTH/GRID_HEIGHT for a larger board (keep in mind performance and window size)

---

## Tips for Better Play

- Plan direction changes a step ahead; input is throttled to prevent quick reversals
- Use Pause to strategize in higher difficulties
- Stay near the center early on to keep options open as you grow
- Avoid trapping yourself in corners at high speeds

---

## Troubleshooting

- Pygame installation fails:
  - Upgrade tools and retry:
    ```
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    ```
  - macOS (rare): ensure Xcode Command Line Tools are installed:
    ```
    xcode-select --install
    ```
- No window appears / running on remote server:
  - Pygame requires a display. If you’re on WSL or SSH, use a local OS window or configure an X server.
- Keyboard input lag:
  - Ensure only one Python instance is running the game
  - Close other intensive apps; reduce difficulty speed if needed
- High-DPI scaling on Windows:
  - If the window looks blurry/tiny, adjust OS scaling settings or try a different CELL_SIZE

---

## Extending the Game (For Developers)

- Add wrap-around walls:
  - Modify boundary checks in Game.step() to wrap coordinates instead of ending the game
- Add obstacles:
  - Track a set of blocked grid cells and draw them; include in collision checks and food spawning
- Add sound effects:
  - Initialize pygame.mixer and play sounds on eat/game over
- Change art or add animations:
  - Replace simple rects with images; consider sprite sheets for head/turn animations

---

## FAQ

- Can I play with a controller?
  - Not built-in. You can map a gamepad to arrow keys via OS tools or extend input handling.
- Is there a scoreboard or saving?
  - No persistent storage yet. You can add file I/O for highscores.
- Fullscreen?
  - Currently windowed. You can switch to fullscreen via pygame.display.set_mode(flags=pygame.FULLSCREEN).

---

## Credits

- Developed by ChatDev
- Product design and documentation by the Chief Product Officer
- Built with Python and Pygame

Enjoy the game!