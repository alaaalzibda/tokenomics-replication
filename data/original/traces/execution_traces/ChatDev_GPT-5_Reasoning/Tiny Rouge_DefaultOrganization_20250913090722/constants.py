'''
Central configuration constants for the roguelike game.
'''
# Grid settings
GRID_WIDTH = 80
GRID_HEIGHT = 80
TILE_SIZE = 8  # Each tile is 8x8 pixels
# UI panel
UI_WIDTH = 240
WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE + UI_WIDTH
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE
# Frame rate
FPS = 60
# Tile types
# Note: The base grid uses only WALL/FLOOR/DOOR for passability.
# Monsters and chests are overlays tracked separately (not written into the grid).
TILE_WALL = 0
TILE_FLOOR = 1
TILE_DOOR = 2
TILE_CHEST = 3   # Overlay identifier (not stored in the grid)
TILE_MONSTER = 4 # Overlay identifier (not stored in the grid)
# Colors (R, G, B)
COLOR_BG = (10, 10, 10)
COLOR_WALL = (50, 50, 70)
COLOR_FLOOR = (120, 120, 120)
COLOR_PLAYER = (50, 200, 70)
COLOR_MONSTER = (200, 60, 60)
COLOR_CHEST = (220, 180, 60)
COLOR_DOOR = (60, 120, 200)
COLOR_GRID_LINES = (30, 30, 30)
# UI colors
COLOR_UI_BG = (20, 20, 20)
COLOR_UI_TEXT = (230, 230, 230)
COLOR_UI_HL = (100, 100, 100)
# Gameplay
PLAYER_START_HP = 100
MONSTER_HP_MIN = 5
MONSTER_HP_MAX = 30
CHEST_HEAL_MIN = 20
CHEST_HEAL_MAX = 30
# Others
FONT_NAME = "consolas"
FONT_SIZE = 18