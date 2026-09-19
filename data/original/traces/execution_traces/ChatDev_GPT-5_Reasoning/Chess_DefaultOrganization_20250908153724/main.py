'''
Terminal chess game entry point.
Play two-player chess in the Linux terminal. Enter moves in SAN (e.g., e4, Nf3, O-O, exd5, e8=Q)
or coordinate notation (e.g., e2e4, g7g8q). Supports castling, en passant, promotion, and
enforces check/checkmate rules.
Commands:
- moves: list all legal moves in current position (in SAN)
- board: reprint the board
- help: show help
- quit/exit: exit the game
'''
import sys
from typing import Optional
from board import Board
from san import parse_user_input, generate_san_for_move
def main() -> int:
    board = Board()
    board.setup_start_position()
    print("ChatDev Chess - Terminal")
    print("Enter moves in SAN (e4, Nf3, O-O, exd5, e8=Q) or coordinates (e2e4, g7g8q).")
    print("Type 'help' for commands.\n")
    while True:
        board.print_board()
        if board.is_checkmate():
            winner = "Black" if board.white_to_move else "White"
            print(f"Checkmate! {winner} wins.")
            break
        if board.is_stalemate():
            print("Stalemate. Draw.")
            break
        if board.in_check(board.white_to_move):
            print("Check.")
        turn = "White" if board.white_to_move else "Black"
        try:
            text = input(f"{turn} move > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not text:
            continue
        key = text.lower()
        if key in ("q", "quit", "exit"):
            print("Goodbye.")
            break
        if key in ("h", "help", "?"):
            print("Commands:")
            print("  moves    - list legal moves in current position")
            print("  board    - reprint the board")
            print("  help     - show this help")
            print("  quit     - exit the game")
            print("Examples: e4, Nf3, O-O, exd5, e8=Q, e2e4, g7g8q")
            continue
        if key in ("b", "board"):
            continue
        if key == "moves":
            moves = board.generate_legal_moves()
            sans = [generate_san_for_move(board, m, moves) for m in moves]
            sans.sort()
            print("Legal moves:")
            print(", ".join(sans))
            continue
        mv = parse_user_input(board, text)
        if mv is None:
            print("Invalid move. Type 'moves' to list legal moves or 'help' for help.")
            continue
        san_str = generate_san_for_move(board, mv)
        board.make_move(mv)
        print(f"Played {san_str}\n")
    return 0
if __name__ == "__main__":
    sys.exit(main())