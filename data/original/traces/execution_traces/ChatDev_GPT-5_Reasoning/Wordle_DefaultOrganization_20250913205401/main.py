'''
Main entry point for the Wordle game.
Provides CLI to run terminal mode (default) or optional Tkinter GUI.
Options:
  --date YYYY-MM-DD  Use the daily word for a specific date (UTC).
  --random           Use a random word (for testing).
  --gui              Launch the GUI instead of terminal mode.
'''
import argparse
from datetime import datetime
from terminal_ui import run_terminal_game
def parse_args():
    parser = argparse.ArgumentParser(description="Play Wordle in your terminal (or optional GUI).")
    parser.add_argument('--date', type=str, default=None,
                        help='Play the word for a specific date (UTC), format YYYY-MM-DD.')
    parser.add_argument('--random', action='store_true',
                        help='Use a random word instead of the daily word.')
    parser.add_argument('--gui', action='store_true',
                        help='Launch the GUI instead of terminal mode.')
    return parser.parse_args()
def main():
    args = parse_args()
    date = None
    if args.date:
        try:
            date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD. Falling back to today.")
            date = None
    if args.gui:
        # Import GUI lazily so terminal users don't need tkinter available.
        from gui import run_gui
        run_gui(date=date, random_word=args.random)
    else:
        run_terminal_game(date=date, random_word=args.random)
if __name__ == '__main__':
    main()