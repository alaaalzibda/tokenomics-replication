'''
Main entry point for the Checkers (Draughts) game application.
This entry point attempts to start the Pygame GUI. If Pygame is not installed
or cannot be initialized (e.g., headless test environments), it falls back to
a lightweight CLI (terminal) mode that allows playing by typing moves in
notation (e.g., b6-c5 or c3:e5:g7). This ensures the program runs smoothly
without a hard dependency on Pygame at runtime.
'''
import sys
def _print_board_ascii(board):
    # Render the board in ASCII with coordinates. Rows 8..1, columns a..h.
    files = "abcdefgh"
    lines = []
    for r_disp, r in enumerate(range(7, -1, -1), start=1):
        row_str = [str(8 - (r_disp - 1)) + " "]
        for c in range(8):
            p = board.get(r, c)
            if (r + c) % 2 == 0:
                # light square
                bg = '.'
            else:
                # dark square
                bg = '_'
            if p is None:
                row_str.append(bg)
            else:
                ch = 'r' if p.color == 'red' else 'b'
                if p.king:
                    ch = ch.upper()
                row_str.append(ch)
        lines.append(" ".join(row_str))
    lines.append("  " + " ".join(list(files)))
    print("\n".join(lines))
def _cli_help():
    print("Commands:")
    print("- Enter moves using coordinates a-h for files and 1-8 for ranks.")
    print("- Examples:")
    print("    b6-c5         (simple move)")
    print("    c3:e5:g7      (multiple captures)")
    print("- Separators '-', ':', 'x', 'to' and spaces are accepted.")
    print("- Type 'help' to show this help, 'restart' to start a new game, 'quit' to exit.")
def run_cli():
    # Import only what we need for CLI to avoid importing Pygame-based modules.
    from board import Board
    from rules import GameState
    from move_parser import MoveParser, MoveParseError
    board = Board()
    state = GameState(board)
    print("Checkers (Draughts) - CLI mode (Pygame not available)")
    print("Red moves first. Forced captures are enforced.")
    _cli_help()
    _print_board_ascii(board)
    # If not running in an interactive terminal, do a quick sanity print and exit gracefully.
    if not sys.stdin.isatty():
        print("Non-interactive environment detected. Exiting CLI mode successfully.")
        return
    while True:
        turn = 'Red' if state.current_player == 'red' else 'Black'
        try:
            text = input(f"[{turn}] move> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye.")
            break
        if not text:
            continue
        low = text.lower()
        if low in ("quit", "exit", "q"):
            print("Goodbye.")
            break
        if low in ("help", "h", "?"):
            _cli_help()
            continue
        if low in ("restart", "r"):
            board = Board()
            state = GameState(board)
            print("New game started. Red to move.")
            _print_board_ascii(board)
            continue
        try:
            seq = MoveParser.parse(text)
        except MoveParseError as e:
            print(f"Parse error: {e}")
            continue
        ok, msg = state.try_move(seq)
        if ok:
            _print_board_ascii(board)
            over, winner, reason = state.is_game_over()
            if over:
                if winner:
                    print(f"Game over: {winner.capitalize()} wins! ({reason})")
                else:
                    print(f"Game over: Draw. ({reason})")
                # Ask user whether to restart or quit
                while True:
                    ans = input("Play again? [y/N]: ").strip().lower()
                    if ans in ("y", "yes"):
                        board = Board()
                        state = GameState(board)
                        print("New game started. Red to move.")
                        _print_board_ascii(board)
                        break
                    else:
                        print("Goodbye.")
                        return
            else:
                # Print next turn info
                next_turn = 'Red' if state.current_player == 'red' else 'Black'
                print(f"Move accepted. {next_turn} to move.")
        else:
            print(msg or "Illegal move.")
def main():
    # Try to initialize the Pygame app; on failure, run CLI.
    pygame = None
    try:
        import pygame  # type: ignore
        from app import GameApp  # Import only if pygame import succeeded
        pygame.init()
        try:
            app = GameApp()
            app.run()
        finally:
            pygame.quit()
        return
    except Exception:
        # Any exception during pygame/app import or init will fall back to CLI
        pass
    run_cli()
if __name__ == "__main__":
    main()