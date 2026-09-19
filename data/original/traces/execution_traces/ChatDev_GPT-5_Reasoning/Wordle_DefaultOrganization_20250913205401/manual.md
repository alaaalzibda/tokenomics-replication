# ChatDev Wordle (Terminal Edition)

A lightweight, offline Wordle-style game you can play directly in your Linux terminal. Guess the daily 5-letter English word in 6 tries with color feedback:
- Green: correct letter in the correct position
- Yellow: correct letter in the wrong position
- Grey: letter not in the word

An optional Tkinter GUI is also available (not required).

## Highlights

- True terminal experience: no browser or external UI needed
- Accurate Wordle feedback, including proper handling of duplicate letters
- Deterministic daily word (based on UTC date)
- Input validation against a curated 5-letter dictionary
- Optional GUI mode via Tkinter

## What’s included

- main.py — entry point and CLI options
- game.py — core logic, validation, state management
- words.py — daily word selection and allowed dictionaries
- terminal_ui.py — ANSI-colored terminal UI (board and keyboard)
- gui.py — optional Tkinter GUI
- requirements.txt — notes on dependencies (standard library only; optional Tkinter)

## System requirements

- Python: 3.7+ (3.8+ recommended)
- OS: Linux (tested on common terminals that support ANSI colors)
- Optional (for GUI mode): Tkinter
  - Debian/Ubuntu: sudo apt-get install python3-tk
  - Fedora: sudo dnf install python3-tkinter
  - Arch: sudo pacman -S tk
  - macOS: Tkinter is included with python.org installers; Homebrew Python can use brewed tcl-tk (check brew docs)

No pip packages are required.

## Installation

1) Get the source files into a folder, e.g., wordle-terminal:
- Save the provided files into the same directory.

2) Verify Python:
- python3 --version

3) (Optional: GUI) Install Tkinter:
- Debian/Ubuntu: sudo apt-get install python3-tk

That’s it. The project uses only the Python standard library.

## How to play (Terminal)

Run:
- python3 main.py

Optional command-line flags:
- --date YYYY-MM-DD    Use the daily word for a specific UTC date (e.g., --date 2025-01-01)
- --random             Use a random answer (useful for practice/testing)
- --gui                Launch the optional Tkinter GUI instead of terminal mode

Examples:
- Today’s daily word: python3 main.py
- Daily word for a specific date: python3 main.py --date 2025-09-14
- Random practice word: python3 main.py --random

Gameplay:
1) You’ll see a 6-row board and a colorized on-screen keyboard.
2) Type a 5-letter guess and press Enter.
3) After each valid guess, tiles are colored:
   - Green = correct letter in the correct position
   - Yellow = letter is in the word, but a different position
   - Grey = letter is not in the word
4) You have up to 6 attempts. If you guess correctly, you win and see a summary. If not, the solution is revealed.

Exiting:
- Press Ctrl+C or send EOF (Ctrl+D) to exit safely.

Notes on colors:
- Most Linux terminals support ANSI colors by default. If colors don’t render properly, try another terminal emulator.

## Input validation

Your guess must:
- Be exactly 5 characters long
- Contain only A–Z letters (ASCII)
- Be present in the allowed dictionary

Invalid inputs are rejected with a helpful message (e.g., “Your guess must be exactly 5 letters” or “Not in word list.”).

Dictionary scope:
- The allowed guess dictionary is a curated list (words in words.py). It’s not exhaustive, but includes answers plus common 5-letter words.

## Daily word logic (UTC)

- The daily answer is deterministic based on the UTC date and a fixed base (2021-06-19).
- Using --date lets you reproduce past/future daily words (useful for competitions or testing).
- If you’re not specifying --date, the game uses today’s date in UTC to avoid time zone ambiguity.

## Optional GUI mode

A simple Tkinter GUI is included for completeness. It’s not required to play in the terminal.

Run:
- python3 main.py --gui
- Other flags still work, e.g., python3 main.py --gui --random or --date YYYY-MM-DD

GUI features:
- 6x5 tile board, color feedback, and a visual keyboard
- Input box with validation messaging

If you don’t have Tkinter installed, use terminal mode or install Tkinter via your package manager.

## How feedback handles duplicate letters

The engine uses a two-pass algorithm (like original Wordle):
1) First marks exact matches (green) and deducts those letters from availability.
2) Then marks present letters (yellow) only up to the remaining count of that letter in the secret word.
3) All other letters are marked grey (absent).

This ensures correct behavior when the secret or guess contains repeated letters.

## File-by-file overview

- main.py
  - Parses command-line arguments
  - Chooses terminal or GUI mode
  - Supports --date and --random

- game.py
  - evaluate_guess(secret, guess): assigns correct/present/absent statuses with duplicate handling
  - WordleGame: manages secret word, history, keyboard status, validation, win/lose detection

- words.py
  - Curated answer list and guess dictionary
  - get_daily_word(date=None): deterministic by UTC date
  - get_random_word(): select a random answer
  - is_valid_guess(word): fast membership check

- terminal_ui.py
  - Renders tiles and keyboard using ANSI colors
  - Runs the input loop with prompts, validation, and final messaging

- gui.py (optional)
  - Simple Tkinter GUI with tiles and color feedback

## Troubleshooting

- Colors look odd or don’t show:
  - Ensure your terminal supports ANSI colors (most do). Try a different terminal emulator if needed.

- “Not in word list.”:
  - The guess dictionary is curated. Try a different 5-letter English word.

- “Invalid date format. Use YYYY-MM-DD.”:
  - Ensure you pass the date as YYYY-MM-DD (e.g., 2025-01-31).

- Tkinter errors when using --gui:
  - Install Tkinter (see the OS-specific commands above), or run without --gui to use the terminal mode.

- Game exits when I press Ctrl+D:
  - That sends EOF to the program. Restart and continue playing.

## Tips and advanced usage

- Practice mode:
  - Use python3 main.py --random to practice without affecting the daily challenge.

- Replaying a daily challenge:
  - Use --date with the desired UTC date to replay or share a consistent puzzle with others.

- Customize the dictionary:
  - Edit ANSWER_LIST and GUESSES_LIST in words.py, keeping 5-letter alphabetic words only.

- Modify colors (terminal):
  - Adjust ANSI constants in terminal_ui.py (e.g., BG_GREEN, BG_YELLOW, BG_GREY) if you prefer different colors or contrast.

## Privacy and offline use

- The game runs entirely offline. No data is sent anywhere.
- All logic and word lists are local.

---

Enjoy changing the digital world through programming—one guess at a time!