'''
Global configuration constants for the Pong game:
- Screen dimensions
- Colors
- Gameplay tuning parameters (speeds, sizes, winning score)
- Frame rate
'''
# Window settings
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
WINDOW_TITLE = "ChatDev Pong - Two Player"
# Colors (R, G, B)
COLOR_BG = (15, 15, 20)
COLOR_FG = (240, 240, 240)
COLOR_DIM = (120, 120, 120)
COLOR_ACCENT = (200, 80, 80)
# Gameplay settings
PADDLE_WIDTH = 14
PADDLE_HEIGHT = 100
PADDLE_SPEED = 500.0  # pixels per second
BALL_RADIUS = 10
BALL_START_SPEED = 360.0  # initial speed magnitude (pixels per second)
BALL_MAX_SPEED = 900.0
BALL_SPEEDUP_FACTOR = 1.06  # speed multiplier applied on paddle hit
# Scoring
WINNING_SCORE = 7
SERVE_COOLDOWN_MS = 1000  # time to wait after each point before resuming
# Frame rate
FPS = 120
# UI
SCORE_FONT_SIZE = 64
INFO_FONT_SIZE = 28
WIN_FONT_SIZE = 48
# Center line
CENTER_DASH_HEIGHT = 18
CENTER_DASH_GAP = 12
# Controls
LEFT_UP_KEY = "w"
LEFT_DOWN_KEY = "s"
RIGHT_UP_KEY = "up"
RIGHT_DOWN_KEY = "down"