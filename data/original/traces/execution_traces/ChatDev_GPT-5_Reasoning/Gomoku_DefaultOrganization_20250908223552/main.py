'''
Main entry point for the Gomoku application. It initializes the controller and view,
and starts the tkinter main loop.
'''
import sys
try:
    # Preferred: import from package layout
    from gomoku.controller import GameController
    from gomoku.view import GomokuApp
except ModuleNotFoundError:
    # Fallback: support flat-file layout without the 'gomoku' package directory
    from controller import GameController
    from view import GomokuApp
def main():
    controller = GameController()
    app = GomokuApp(controller)
    controller.attach_view(app)
    app.mainloop()
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)