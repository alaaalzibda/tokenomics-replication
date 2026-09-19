'''
Constants used across the Tic-Tac-Toe application.
Includes symbols, colors, fonts, window title, and version to keep styling
and metadata consistent and centralized.
'''
# App metadata
WINDOW_TITLE = "Tic-Tac-Toe"
APP_VERSION = "1.0.0"
# Game symbols and dimensions
GRID_SIZE = 3
SYMBOL_X = 'X'
SYMBOL_O = 'O'
# Color palette
COLORS = {
    'bg': '#f7f7f7',
    'grid_bg': '#f7f7f7',
    'button_bg': '#ffffff',
    'button_fg': '#222222',
    'button_disabled_fg': '#9e9e9e',
    'x_fg': '#e53935',          # Red for X
    'o_fg': '#1e88e5',          # Blue for O
    'highlight': '#ffeb3b',     # Yellow highlight for winning cells
    'status_fg': '#222222',
}
# Fonts
FONTS = {
    'cell': ('Helvetica', 32, 'bold'),
    'status': ('Helvetica', 14),
    'control': ('Helvetica', 12),
}