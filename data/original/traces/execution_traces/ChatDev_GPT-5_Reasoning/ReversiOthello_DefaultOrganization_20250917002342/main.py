'''
Main entry point for the Reversi (Othello) application.
This module initializes the Tkinter root window and launches the GUI.
'''
import tkinter as tk
from gui import ReversiGUI
def main() -> None:
    """Create the Tk root and start the Reversi GUI application."""
    root = tk.Tk()
    root.title("Reversi (Othello)")
    # Optional: Set a minimum size to keep the layout consistent
    root.minsize(760, 700)
    app = ReversiGUI(root)
    root.mainloop()
if __name__ == "__main__":
    main()