# ChatDev Chess — Terminal User Manual

Play full chess from your Linux terminal. Two human players alternate turns, entering standard chess notation. The engine enforces legal moves, check, checkmate, stalemate, castling, en passant, and pawn promotion.

- Input formats: SAN (e.g., e4, Nf3, O-O, exd5, e8=Q) or coordinates (e.g., e2e4, g7g8q)
- Output: ASCII board, SAN confirmations, and game status messages
- No GUI required

---

## Quick Install

Prerequisites:
- Python 3.6+ (3.8+ recommended)
- Linux terminal (works on macOS/Windows terminals as well)

1) Clone or download the project source, then open a terminal in the project directory (containing main.py).

2) (Optional) Create and activate a virtual environment:
```
python3 -m venv .venv
source .venv/bin/activate
```

3) Install dependencies:
```
pip install -r requirements.txt
```

Note:
- The project uses only the Python standard library. The requirements file includes the dataclasses backport for Python < 3.7.

---

## Run the Game

From the project directory:
```
python3 main.py
```

You should see:
- A greeting banner
- Instructions on how to enter moves
- The initial board

To exit anytime: type `quit` or press Ctrl+C.

---

## What is this?

ChatDev Chess is a terminal-based, two-player chess application. It focuses on correctness and standard rules enforcement without requiring any external UI frameworks. It’s a compact reference implementation demonstrating:

- Move generation and legality checks
- Check, checkmate, and stalemate detection
- Castling, en passant, and pawn promotion
- SAN parsing and generation
- Coordinate move parsing

---

## Features

- Full two-player chess with alternating turns
- Standard rules enforced:
  - Legal move generation (no self-check, pinned pieces handled)
  - Check and checkmate detection
  - Stalemate detection
  - Castling (both sides), including “cannot castle through check”
  - En passant captures
  - Pawn promotion (to Queen, Rook, Bishop, Knight)
- Input options:
  - SAN (Standard Algebraic Notation): e.g., e4, Nf3, O-O, exd5, e8=Q
  - Coordinate notation: e.g., e2e4, g7g8q
- Convenience:
  - List all legal moves for the current position
  - Board reprint command
  - Help and quit commands
- Robust SAN handling:
  - Accepts O-O, 0-0, o-o (and queenside variants)
  - Accepts promotion both with and without "=" (e.g., e8Q or e8=Q)
  - Accepts check/mate suffixes (+, #)

---

## How to Play

After starting the game, the board appears as an 8×8 ASCII grid:

- Files a–h labeled along the bottom
- Ranks 8–1 labeled on the left
- Uppercase letters are White pieces; lowercase letters are Black pieces
- Dots (.) are empty squares

Example (start position excerpt):
```
  +------------------------+
8 | r  n  b  q  k  b  n  r |
7 | p  p  p  p  p  p  p  p |
...
2 | P  P  P  P  P  P  P  P |
1 | R  N  B  Q  K  B  N  R |
  +------------------------+
    a  b  c  d  e  f  g  h
```

Prompts:
- It will display whose turn it is: “White move >” or “Black move >”
- Enter a move or a command, then press Enter

### Supported Commands

- moves — list all legal moves (in SAN) in the current position
- board — reprint the board
- help — show help text and examples
- quit or exit — leave the game

### Entering Moves

You can use either SAN or coordinate notation.

1) SAN (Standard Algebraic Notation)
   - Pawn push: e4
   - Piece move: Nf3, Bb5, Qxd5
   - Castling: O-O (kingside), O-O-O (queenside)
     - Variations accepted: O-O, 0-0, o-o (and queenside equivalents)
   - Captures: exd5 (pawn captures on d5), Rxa7
   - Promotion: e8=Q (also accepts e8Q)
   - Check, mate: Nf7+, Qh7#

2) Coordinate notation
   - From-to squares: e2e4, g1f3, a7a8q (promotion)
   - Promotion suffix: choose q, r, b, n (case-insensitive). Example: g7g8q

Notes:
- For promotions, if you omit the promotion piece in coordinate notation, it defaults to a queen when legal.
- En passant captures are entered like a normal capture in SAN (e.g., exd6) and like a regular move in coordinate notation (e.g., e5d6), and the engine will handle the special capture logic automatically.

### Example Session

```
$ python3 main.py
ChatDev Chess - Terminal
Enter moves in SAN (e4, Nf3, O-O, exd5, e8=Q) or coordinates (e2e4, g7g8q).
Type 'help' for commands.

  +------------------------+
8 | r  n  b  q  k  b  n  r |
7 | p  p  p  p  p  p  p  p |
6 | .  .  .  .  .  .  .  . |
5 | .  .  .  .  .  .  .  . |
4 | .  .  .  .  .  .  .  . |
3 | .  .  .  .  .  .  .  . |
2 | P  P  P  P  P  P  P  P |
1 | R  N  B  Q  K  B  N  R |
  +------------------------+
    a  b  c  d  e  f  g  h
White move > e4
Played e4

... (board prints)

Black move > c5
Played c5

White move > Nf3
Played Nf3

Black move > d6
Played d6

White move > d4
Played d4

Black move > cxd4
Played cxd4

White move > Nxd4
Played Nxd4

... continue playing until checkmate or stalemate
```

When a king is in check, the game prints “Check.” before the prompt. When a terminal result occurs, it prints:
- “Checkmate! White wins.” or “Checkmate! Black wins.”
- “Stalemate. Draw.”

---

## Rules and Enforcement Details

- Legal moves: The engine generates pseudo-legal moves and filters out those that leave the mover’s king in check.
- Check: If the side to move is in check, only moves that resolve the check are allowed.
- Checkmate: If in check and no legal move exists, the game declares checkmate and the opponent wins.
- Stalemate: If not in check and no legal move exists, the game declares a draw by stalemate.
- Castling:
  - Allowed only if king and rook are unmoved, squares between them are empty, and the king does not move through or into check.
- En passant:
  - Available immediately after a pawn advances two squares and an opposing pawn could capture it as if it moved one.
  - The game tracks the en passant target square for one move.
- Promotion:
  - On reaching the last rank, pawns can promote to Q/R/B/N.
  - You can specify the promotion piece in SAN (e8=Q) or coordinate notation (e7e8q).
  - If omitted where applicable, promotion defaults to a queen in common cases.

---

## Tips and Troubleshooting

- “Invalid move”:
  - Use the command `moves` to see all legal SAN moves for the current position.
  - Make sure your SAN is correct (e.g., include “x” for captures when using SAN; coordinate notation doesn’t require “x”).
  - If castling is disallowed, you may be passing through or into check, or pieces are blocking.
- Promotion entry:
  - SAN: e8=Q (or e8Q)
  - Coordinates: e7e8q
- En passant:
  - SAN: exd6 (the engine understands it’s en passant when applicable)
  - Coordinates: e5d6 (engine handles the special capture)
- Exiting: type `quit` or `exit`, or press Ctrl+C.

---

## Limitations (by design)

- No clocks or time controls
- No threefold repetition or 50-move rule
- No draw offers/resign commands (you can simply `quit`)
- No saving/loading games or FEN import/export

The focus is on a clean, playable terminal chess experience with core rules enforced.

---

## Project Structure

- main.py — Entry point and terminal UI loop
- board.py — Board state, move generation, legality checks, making/undoing moves, printing
- move.py — Move and MoveState data structures
- san.py — SAN generation and parsing utilities (also supports coordinate parsing)
- utils.py — Helpers for indices, squares, colors, and formatting
- requirements.txt — Minimal dependency spec

---

## Development Notes

- Run locally with Python 3.6+ (3.8+ recommended)
- The engine uses a 0–63 index for squares, with 0 at a8 and 63 at h1
- White pieces are uppercase; black pieces lowercase
- Tests/manual checks:
  - Use `moves` in known positions to verify castling availability
  - Create en passant scenarios by pushing a pawn two squares and capturing with an adjacent enemy pawn on the next move
  - Promote a pawn by advancing it to the last rank and specifying the desired promotion piece

---

## License and Support

- This project is a demonstration by ChatDev with standard-library-only dependencies.
- For feedback or issues, please share the move sequence and terminal output to help reproduce the scenario.

Enjoy playing chess in your terminal!