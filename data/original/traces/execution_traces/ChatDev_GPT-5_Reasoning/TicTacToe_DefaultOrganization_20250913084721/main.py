'''
Main entry point for the Tic-Tac-Toe application.
Creates the root Tkinter window, initializes the GUI class, and starts
the event loop.
'''
import tkinter as tk
from gui import TicTacToeGUI
from constants import WINDOW_TITLE, COLORS
def main() -> None:
    """Start the Tic-Tac-Toe GUI application."""
    root = tk.Tk()
    root.title(WINDOW_TITLE)
    # Set base background color for the app
    root.configure(bg=COLORS['bg'])
    # Prevent resizing for a consistent layout
    root.resizable(False, False)
    app = TicTacToeGUI(root)
    app.build_ui()
    root.mainloop()
if __name__ == "__main__":
    main()