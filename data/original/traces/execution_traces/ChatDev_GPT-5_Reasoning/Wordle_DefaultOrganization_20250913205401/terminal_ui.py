'''
Terminal (CLI) user interface for the Wordle game.
Provides ANSI-colored tiles, prints the board and a keyboard, and runs the input loop.
'''
from typing import List, Tuple, Dict, Optional
from game import WordleGame, ABSENT, PRESENT, CORRECT
from words import get_daily_word, get_random_word
# ANSI escape codes for coloring tiles
RESET = "\033[0m"
BOLD = "\033[1m"
FG_BLACK = "\033[30m"
FG_WHITE = "\033[97m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_GREY = "\033[100m"
BG_LIGHT = "\033[47m"
QWERTY_ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
def status_to_colors(status: str) -> Tuple[str, str]:
    """
    Map status to (foreground, background) ANSI color codes.
    """
    if status == CORRECT:
        return (FG_BLACK, BG_GREEN)
    elif status == PRESENT:
        return (FG_BLACK, BG_YELLOW)
    else:
        return (FG_WHITE, BG_GREY)
def colorize_letter(letter: str, status: str) -> str:
    """
    Render a single letter as an ANSI-colored tile.
    """
    fg, bg = status_to_colors(status)
    tile = f" {letter.upper()} "
    return f"{BOLD}{fg}{bg}{tile}{RESET}"
def render_row(guess: Optional[str], statuses: Optional[List[str]]) -> str:
    """
    Render a row of 5 tiles for a guess. If guess/statuses are None, render empty tiles.
    """
    pieces = []
    if guess is None or statuses is None:
        for _ in range(5):
            pieces.append(f"{BOLD}{FG_BLACK}{BG_LIGHT}   {RESET}")
    else:
        for i in range(5):
            ch = guess[i].upper()
            st = statuses[i]
            pieces.append(colorize_letter(ch, st))
    return " ".join(pieces)
def print_board(history: List[Tuple[str, List[str]]], max_attempts: int) -> None:
    """
    Print the full board with history rows and remaining empty rows.
    """
    for guess, statuses in history:
        print(render_row(guess, statuses))
    for _ in range(max_attempts - len(history)):
        print(render_row(None, None))
def print_keyboard(status_map: Dict[str, str]) -> None:
    """
    Print a QWERTY keyboard with colors reflecting best-known letter statuses.
    """
    print()
    for row in QWERTY_ROWS:
        line_parts = []
        for ch in row:
            st = status_map.get(ch.lower(), None)
            if st is None:
                part = f"{BOLD}{FG_BLACK}{BG_LIGHT} {ch} {RESET}"
            else:
                part = colorize_letter(ch, st)
            line_parts.append(part)
        indent = " " * (10 - len(row))  # slight centering
        print(indent + " ".join(line_parts))
    print()
def run_terminal_game(date=None, random_word: bool = False) -> None:
    """
    Orchestrate playing Wordle in the terminal.
    """
    if random_word:
        secret = get_random_word()
        game = WordleGame(secret_word=secret)
        banner = "Wordle (Random word)"
    else:
        secret = get_daily_word(date=date)
        game = WordleGame(secret_word=secret)
        if date:
            banner = f"Wordle (Daily word for {date.isoformat()} UTC)"
        else:
            banner = "Wordle (Today's daily word)"
    print("=" * len(banner))
    print(banner)
    print("=" * len(banner))
    print("Guess the 5-letter word in 6 tries.")
    print("Feedback: green = correct spot, yellow = wrong spot, grey = not in word.")
    print()
    while not game.is_over:
        print_board(game.history, game.max_attempts)
        print_keyboard(game.get_keyboard_status())
        prompt = f"Enter guess #{game.attempts_used + 1}: "
        try:
            guess = input(prompt).strip()
        except EOFError:
            print("\nInput closed. Exiting game.")
            return
        ok, msg = game.validate_guess(guess)
        if not ok:
            print(f"Invalid guess: {msg}\n")
            continue
        try:
            statuses = game.submit_guess(guess)
        except ValueError as e:
            print(f"Error: {e}")
            continue
        print()
        # Print the latest row immediately for responsiveness
        print(render_row(guess.lower(), statuses))
        print()
        if game.is_won:
            print_board(game.history, game.max_attempts)
            print_keyboard(game.get_keyboard_status())
            print(f"Congratulations! You guessed it in {game.attempts_used}/{game.max_attempts} attempts.")
            print(f"The word was: {game.secret.upper()}")
            return
    # Game over without a win
    print_board(game.history, game.max_attempts)
    print_keyboard(game.get_keyboard_status())
    print("Better luck next time!")
    print(f"The word was: {game.secret.upper()}")