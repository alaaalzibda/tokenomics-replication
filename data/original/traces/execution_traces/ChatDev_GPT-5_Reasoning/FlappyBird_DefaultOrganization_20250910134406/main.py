'''
Main entry point for the Flappy Bird clone application.
Creates the Game instance and starts the main loop. Adds a dependency check
to gracefully handle environments where pygame is not installed.
'''
import sys
import os
def main() -> None:
    """
    Create the Game instance and start the main loop.
    If pygame is not installed, inform the user and exit gracefully.
    """
    try:
        import pygame  # noqa: F401
    except ModuleNotFoundError:
        print(
            "Pygame is not installed. Please install it with:\n  pip install pygame",
            file=sys.stderr,
        )
        return
    # Import Game only after confirming pygame is available to avoid ImportError
    from game import Game
    try:
        # Improve robustness in headless environments (e.g., CI) by using a dummy video driver.
        if os.environ.get("SDL_VIDEODRIVER") is None and os.environ.get("DISPLAY") is None:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        game = Game()
        game.run()
    except SystemExit:
        # Allow clean exit on window close.
        pass
    except Exception as exc:
        # In a real app, consider logging this to a file.
        print(f"Unexpected error: {exc}", file=sys.stderr)
        raise
if __name__ == "__main__":
    main()