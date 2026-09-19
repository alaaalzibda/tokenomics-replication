'''
Entry point for the simplified Monopoly Go! game implemented with a Tkinter GUI.
This module initializes the GUI application and starts the main event loop.
'''
import tkinter as tk
from gui import MonopolyApp
def main():
    root = tk.Tk()
    root.title("Monopoly Go! - Simplified")
    app = MonopolyApp(root)
    app.pack(fill="both", expand=True)
    root.mainloop()
if __name__ == "__main__":
    main()