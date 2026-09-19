# Mastermind – Code‑Breaking Game (Tkinter GUI)

A classic Mastermind experience for desktop. The computer selects a hidden sequence of symbols (colors or digits). You try to guess it within a limited number of attempts. After each guess, you receive feedback:
- Exact: right symbol in the right position
- Partial: right symbol in the wrong position

This app provides a simple, friendly GUI built with Python and Tkinter.

---

## Features

- Play Mastermind with configurable settings:
  - Code length (3–6)
  - Maximum attempts (6–12)
  - Allow or disallow duplicate symbols
  - Symbol set: colors or digits
  - Optional random seed for reproducible games
- Clear feedback after each guess: Exact vs Partial matches
- History panel showing each guess and feedback
- Win/lose dialog with the revealed secret on loss
- Keyboard shortcuts:
  - Enter: submit guess
  - Ctrl+N: start a new game
- Deterministic game generation via seed (useful for teaching, demos, or challenges)
- Responsive layout and scrollable history

---

## System Requirements

- Python 3.8+ (recommended)
- Tkinter available in your Python installation

No third‑party packages are required.

If Tkinter is not available by default on your system, install the OS package:
- Debian/Ubuntu: `sudo apt-get install python3-tk`
- Fedora: `sudo dnf install python3-tkinter`
- macOS: Use the Python installer from python.org (includes Tk). If using Homebrew Python, ensure Tk support is installed and linked.

---

## Quick Start

1) Get the source
- Clone or download this project (ensure the files main.py, gui.py, game_logic.py, requirements.txt are together).

2) (Optional) Create a virtual environment
```
python -m venv .venv
# Activate:
#   Windows: .venv\Scripts\activate
#   macOS/Linux: source .venv/bin/activate
```

3) Install requirements
```
pip install -r requirements.txt
```
Note: requirements.txt lists no external packages. This step mainly confirms your environment is set up.

4) Run the app
```
python main.py
```
A window titled “Mastermind – Code Breaking Game” will open.

---

## How to Play

1) Choose settings (top section)
- Code length: Number of positions in the secret code (3–6).
- Attempts: Total guesses allowed before you lose (6–12).
- Allow duplicates: If checked, the secret may contain repeated symbols.
- Symbol set:
  - Colors: A palette of Tkinter‑recognized color names (red, green, blue, yellow, orange, purple, cyan, magenta).
  - Digits: "0"–"9".
- Seed (optional): Integer seed for reproducible games. Leave blank for random play.

2) Start a new game
- Click “New Game” (or press Ctrl+N) after adjusting settings. Settings only apply when starting a new game.

3) Make a guess
- For each position, use the dropdown to choose a symbol.
- Click “Submit Guess” (or press Enter).

4) Read feedback
- Exact: Count of symbols in the correct position.
- Partial: Count of correct symbols in the wrong positions. Symbols already counted as Exact are not counted again as Partial.
- Your guess and feedback are recorded in the History panel.

5) Win or lose
- You win immediately if all positions are Exact.
- If you run out of attempts, the game ends and the secret is revealed.

---

## Understanding Feedback (Scoring Rules)

- Exact matches: Positions where guess[i] == secret[i].
- Partial matches: Correct symbols in the wrong positions. Counting avoids double‑counting:
  - Remove Exact matches.
  - For the remaining (unmatched) symbols, the number of Partial matches equals the sum of minimum occurrences of each symbol in your unmatched guess and unmatched secret.

Examples:
- Secret: [red, blue, green, yellow]  
  Guess:  [red, yellow, red,  blue]  
  Exact = 1 (position 1)  
  Unmatched secret: [blue, green, yellow]  
  Unmatched guess:  [yellow, red, blue]  
  Partial = min(blue:1,1) + min(green:1,0) + min(yellow:1,1) = 1 + 0 + 1 = 2  
  Feedback: Exact 1, Partial 2

- With duplicates:
  - Secret: [red, red, green, green]  
    Guess:  [red, green, red,  green]  
    Exact = 2 (positions 1 and 4)  
    Unmatched secret: [red, green]  
    Unmatched guess:  [green, red]  
    Partial = min(red:1,1) + min(green:1,1) = 2  
    Feedback: Exact 2, Partial 2

---

## UI Guide

- Header: Title and short instructions.
- Settings:
  - Adjust code length, attempts, duplicates, symbol set, and seed.
  - Click “New Game” to apply.
- Guess area:
  - One dropdown per position; choose symbols for your guess.
- Controls:
  - Submit Guess, New Game, and an “Attempts left” status.
- History:
  - Scrollable list of all guesses with Exact and Partial counts.

Shortcuts:
- Enter: Submit Guess (when enabled)
- Ctrl+N: New Game

---

## Reproducible Games (Seed)

- Enter an integer in the Seed field to make the secret code deterministic for the same settings.
- Use this for fair challenges or practice scenarios.
- Leave blank for a new random code each time.
- If you enter a non‑integer value, the app will show an error and ignore the seed.

---

## Tips and Best Practices

- Start by testing for presence of key symbols (e.g., try diverse symbols when duplicates are allowed).
- Use feedback to eliminate positions or symbols systematically.
- Digits mode can be easier for color‑blind accessibility.

---

## Troubleshooting

- Tkinter not found:
  - Install Tkinter for your OS:
    - Debian/Ubuntu: `sudo apt-get install python3-tk`
    - Fedora: `sudo dnf install python3-tkinter`
    - macOS: Install Python from python.org (includes Tk). With Homebrew, ensure Tk support is installed and linked.
- “Invalid Seed” error:
  - The Seed field must be a valid integer or left blank.
- Can’t submit a guess:
  - Ensure the game is not over. If it is, start a new game.
- “Invalid Guess” error:
  - The GUI prevents most invalid inputs, but errors can occur if settings are inconsistent. Ensure the symbol set supports your code length when duplicates are disallowed (e.g., code length must not exceed the number of available symbols).

---

## Project Structure

- main.py
  - Entry point. Creates the Tkinter window and launches the GUI.
- gui.py
  - Tkinter interface for playing the game, managing settings, and showing feedback/history.
- game_logic.py
  - Core Mastermind rules, secret generation, and evaluation algorithm.
- requirements.txt
  - Notes on dependencies (standard library only; ensure Tkinter is available).

---

## Developer Notes (Optional)

Use the game logic directly from Python for testing or integration:

```python
from game_logic import MastermindGame

game = MastermindGame(code_length=4, colors=["red","green","blue","yellow"], max_attempts=10, allow_duplicates=True, seed=123)
print("Secret (for testing):", game.reveal_secret())  # In a real game, don't reveal!
exact, partial = game.evaluate_guess(["red","red","blue","blue"])
print(exact, partial)
```

Key API:
- MastermindGame(...)
- evaluate_guess(guess: List[str]) -> (exact: int, partial: int)
- new_game()
- remaining_attempts(), attempts_made(), is_over(), has_won()
- reveal_secret(), get_history()

---

## Credits

Inspired by the classic Mastermind board game. Built with Python and Tkinter to provide a clean, educational example of game logic and GUI design.