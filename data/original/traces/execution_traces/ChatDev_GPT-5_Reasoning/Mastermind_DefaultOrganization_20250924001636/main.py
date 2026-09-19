'''
Mastermind Game - Entry Point
This module initializes the Tkinter root window and launches the Mastermind GUI.
Run this file to start the game application.
'''
import tkinter as tk
from gui import MastermindGUI
def main() -> None:
    """Create the application window and start the Mastermind GUI."""
    root = tk.Tk()
    root.title("Mastermind - Code Breaking Game")
    root.geometry("640x760")
    root.minsize(560, 600)
    app = MastermindGUI(root)
    root.mainloop()
if __name__ == "__main__":
    main()