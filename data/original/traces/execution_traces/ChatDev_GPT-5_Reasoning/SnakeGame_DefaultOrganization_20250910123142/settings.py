'''
Global configuration and constants for the Snake game.
'''
# Grid and sizing
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT
# Colors
BG_COLOR = (18, 18, 18)
GRID_COLOR = (36, 36, 36)
SNAKE_HEAD_COLOR = (0, 200, 0)
SNAKE_BODY_COLOR = (0, 150, 0)
FOOD_COLOR = (220, 60, 60)
TEXT_COLOR = (255, 255, 255)
TEXT_SHADOW = (0, 0, 0)
TITLE = "Snake by ChatDev"
# Difficulty to moves-per-second mapping
DIFFICULTY_SPEEDS = {
    "Easy": 8,
    "Normal": 12,
    "Hard": 16,
    "Insane": 22,
}
# Score values
FOOD_SCORE = 1