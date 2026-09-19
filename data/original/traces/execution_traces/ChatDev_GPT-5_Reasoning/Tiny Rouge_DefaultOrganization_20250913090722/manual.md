# Tower of the Sorcerer — Inspired Roguelike (Python/Pygame)

A minimalist roguelike inspired by Tower of the Sorcerer. Navigate an 80x80 dungeon, avoid walls, fight monsters, open chests to restore HP, and find the door to advance to the next level. Includes a clean, minimal UI for vital stats.

## Features

- Fixed 80x80 grid map (each tile is 8×8 pixels)
- Guaranteed valid path from start to door on every level
- Procedural maps with monsters and treasure chests
- Simple, deterministic combat:
  - When you step onto a monster, you take damage equal to the monster’s HP (the monster is removed)
- Treasure chests restore 20–30 HP when opened
- Minimal sidebar UI shows:
  - Current level and HP
  - Last encountered monster’s HP and damage dealt to you
  - Contextual messages (e.g., walls, pickups, level changes)
- Keyboard controls (W/A/S/D) and quick restart

Window size: 880×640 (game area 640×640 + 240 px side panel)

## Getting Started

### 1) Prerequisites

- OS: Windows, macOS, or Linux
- Python: 3.9+ (3.10 or 3.11 recommended)
- Pip: latest version recommended

Verify Python and pip:
```
python --version
pip --version
```
On Windows, you might need to use `py` instead of `python`.

### 2) Install Dependencies

This project uses only Pygame as an external dependency.

Option A — Direct:
```
pip install pygame
```

Option B — Virtual environment (recommended):
```
python -m venv .venv
# Activate the venv:
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install --upgrade pip
pip install pygame
```

If you hit build issues on Linux, install SDL libraries via your package manager (manylinux wheels usually avoid this). On macOS and Windows, prebuilt wheels are typically installed automatically.

### 3) Project Structure

```
.
├─ main.py           # Entry point
├─ game.py           # Game loop, rendering, interactions, level flow
├─ mapgen.py         # Map generation with guaranteed path, monsters & chests
├─ entities.py       # Player and Monster data classes
├─ ui.py             # Sidebar UI rendering
└─ constants.py      # Centralized config (grid, colors, gameplay tuning)
```

### 4) Run the Game

From the project root:
```
python main.py
```

On Windows with multiple Python installations:
```
py main.py
```

## How to Play

- Movement:
  - W: Up
  - A: Left
  - S: Down
  - D: Right
- Other:
  - R: Restart game (after death or anytime to reset progress)
  - Esc or Q: Quit

Gameplay rules:
- You can only walk on floor tiles. Walls are impassable.
- Monsters (red tiles): Stepping onto a monster initiates combat. You take damage equal to the monster’s HP; the monster disappears afterward. Example: If a monster has 18 HP, your HP decreases by 18.
- Chests (gold tiles): Stepping onto a chest immediately restores 20–30 HP and removes the chest.
- Door (blue tile): Stepping onto the door advances you to the next level. Your current HP carries over.
- Start: You always start at (1,1). There is always at least one path to the door.

UI (right sidebar):
- Level and HP: Displays your current level and HP.
- Last Encounter: Shows the HP of the last monster you encountered and the damage you took.
- Messages: Contextual feedback (e.g., “You opened a chest and restored 25 HP.”).

Game Over:
- If your HP reaches 0, you die. A “Game Over” overlay appears.
- Press R to restart from Level 1 with full starting HP.

## Map Generation (What’s Happening Under the Hood)

- The map is generated each level using a local random seed.
- The generator first carves a path from the start (1,1) to the door (at 78,78), then opens additional areas.
- Connectivity is verified with BFS to ensure a valid path exists.
- Monsters and chests are placed as overlays on floor tiles (they do not block movement like walls do; interactions trigger when you step on them).

## Tips

- Sometimes the quickest path is not the straightest—explore to find chests and reduce risk before heading to the door.
- Keep an eye on the “Last Encounter” to gauge when you should hunt for more chests.
- If you are low on HP, consider avoiding clusters of monsters and search for chests first.

## Customization

You can tweak gameplay and visuals via constants.py:
- Grid and tiles:
  - GRID_WIDTH, GRID_HEIGHT (fixed at 80×80 to satisfy spec)
  - TILE_SIZE (default 8)
- UI:
  - UI_WIDTH for sidebar width and colors
- Gameplay:
  - PLAYER_START_HP
  - MONSTER_HP_MIN / MONSTER_HP_MAX
  - CHEST_HEAL_MIN / CHEST_HEAL_MAX
- Fonts:
  - FONT_NAME (defaults to “consolas”; pygame will fall back if unavailable)
  - FONT_SIZE

Note: Changing grid size breaks the “fixed 80×80” requirement. Do so only for experiments.

## Troubleshooting

- No window / crash on launch:
  - Ensure Python 3.9+ and pygame are installed.
  - Try running in a clean virtual environment.
- On Linux: “pygame.error: No available video device”
  - Ensure you’re running in a graphical session.
  - Install SDL dependencies (varies by distro) or use a virtual environment with prebuilt wheels.
- Fonts look odd:
  - The game requests “consolas”. If not available, pygame uses a fallback. Adjust FONT_NAME in constants.py to a font present on your system (e.g., “DejaVu Sans Mono”, “Menlo”).
- Window too small/large:
  - Adjust TILE_SIZE (e.g., 10 or 12) in constants.py to scale the game area.
- Performance:
  - The default FPS is 60. Reduce FPS in constants.py if needed.
- Known code issue:
  - If you encounter a NameError or crash referencing “OLOR_WALL” during drawing, open game.py and ensure this line in _draw_grid reads:
    ```
    color = C.COLOR_WALL
    ```
    (There should be no line break between “C.” and “COLOR_WALL”.)

## Uninstall

To remove the environment (if you used a virtual environment):
- Deactivate:
  ```
  deactivate
  ```
- Delete the .venv folder.

If installed globally, uninstall pygame:
```
pip uninstall pygame
```

## Credits

- Developed by ChatDev as a lightweight roguelike inspired by “Tower of the Sorcerer.”
- Built with Python and Pygame.