'''
Main entry point for the Connect Four application.
Creates the root Tk window, initializes the game logic and GUI, and starts the event loop.
'''
import tkinter as tk
from gui import ConnectFourGUI
from game import ConnectFourGame
def main() -> None:
    """Launch the Connect Four GUI application."""
    root = tk.Tk()
    root.title("Connect Four - ChatDev")
    game = ConnectFourGame(rows=6, cols=7)
    app = ConnectFourGUI(root, game)
    # Give focus to the column entry for immediate typing
    app.focus_column_entry()
    root.mainloop()
if __name__ == "__main__":
    main()