'''
Main entry point for the Fibonacci Generator GUI application.
This module initializes the Tkinter root window and starts the GUI
event loop by instantiating the FibonacciApp from the gui module.
'''
import tkinter as tk
from gui import FibonacciApp
def main() -> None:
    """Create the main window and start the application."""
    root = tk.Tk()
    app = FibonacciApp(root)
    root.mainloop()
if __name__ == "__main__":
    main()