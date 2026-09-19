'''
Entry point for the interactive storytelling game. Initializes the GUI application.
'''
import tkinter as tk
from gui import StoryApp
def main():
    app = StoryApp()
    app.mainloop()
if __name__ == "__main__":
    main()