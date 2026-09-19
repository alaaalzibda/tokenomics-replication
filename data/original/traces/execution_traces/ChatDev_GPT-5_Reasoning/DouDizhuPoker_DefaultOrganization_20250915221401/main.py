'''
Main entry point for the Dou Dizhu game application. Initializes the GUI and starts the Tkinter event loop.
'''
from gui import GameUI
if __name__ == "__main__":
    app = GameUI()
    app.run()