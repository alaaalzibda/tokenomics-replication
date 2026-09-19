'''
Main entry point for the Minesweeper application.
Initializes the Tkinter GUI and starts the main loop.
'''
import tkinter as tk
from gui import MinesweeperApp
def main():
    root = tk.Tk()
    root.title("Minesweeper - ChatDev")
    app = MinesweeperApp(master=root)
    app.mainloop()
if __name__ == "__main__":
    main()