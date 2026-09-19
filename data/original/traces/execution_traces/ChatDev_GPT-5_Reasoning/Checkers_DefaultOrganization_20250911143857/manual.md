# Checkers (Draughts) – User Manual

A lightweight, cross-platform Checkers (Draughts) game by ChatDev. It provides:
- A Pygame-based GUI with move entry via notation
- An automatic fallback CLI (terminal) mode if Pygame is unavailable
- Standard English/American rules: men move and capture forward; kings move and capture both ways; forced captures and kinging enforced
- Multi-capture support and board state tracking with turn alternation

Red moves first.

---

## Quick Start

1. Ensure you have Python 3.8+ installed.
2. Install dependencies:
   - Option A: `pip install -r requirements.txt`
   - Option B (single package): `pip install pygame>=2.1`
3. Run the game:  
   `python main.py`

If Pygame initializes successfully, a windowed GUI will launch. If not (e.g., headless servers), the game automatically runs in CLI mode in your terminal.

---

## Installation

### Requirements
- Python 3.8 or newer
- Pygame 2.1+ (GUI mode only; CLI mode does not require Pygame at runtime)

### Steps
- Create and activate a virtual environment (recommended):
  - macOS/Linux:
    - `python3 -m venv .venv`
    - `source .venv/bin/activate`
  - Windows:
    - `py -m venv .venv`
    - `.venv\Scripts\activate`
- Install dependencies:
  - `pip install -r requirements.txt`

### OS Notes
- Linux: You may need SDL libraries for Pygame. On Ubuntu/Debian:
  - `sudo apt-get update && sudo apt-get install -y python3-dev python3-pip libsdl2-dev libsdl2-image-dev libsdl2-ttf-dev`
- macOS: If you encounter window initialization issues, try installing via `pip` in a virtual environment. Ensure permissions allow opening apps from unidentified developers if necessary.
- Windows: Use a recent Python build from python.org or the Windows Store.

---

## Running the Game

- Standard: `python main.py`
- Behavior:
  - GUI Mode: Launches a Pygame window.
  - CLI Mode: If GUI cannot start, prints a message and runs in terminal.

---

## How to Play

### Board and Coordinates
- 8x8 board; only dark squares are used for piece movement.
- Coordinates use files a–h (left-to-right) and ranks 1–8 (bottom-to-top).
- Square “a1” is bottom-left from Red’s perspective; “h8” is top-right.
- Red pieces start at the bottom (ranks 1–3); Black at the top (ranks 6–8).
- Red moves first.

### Move Notation
Enter moves as from-to squares:
- Simple move (one step): `b6-c5`
- Jump/capture (multi-step): `c3:e5:g7`

Accepted separators:
- `-`, `:`, `x`, space, `to` (case-insensitive)
- Examples: `B6 X A5`, `b6 to c5`, `c3 e5 g7`

Invalid tokens or squares (e.g., `i9`) will be rejected with a parse error.

### Rules Enforced
- Turn order: Red, then Black, alternating.
- Men:
  - Move one diagonal step forward (toward the opponent).
  - Capture forward by jumping over an adjacent opponent piece onto the next empty diagonal.
- Kings:
  - Move and capture one diagonal step in any direction.
- Forced captures:
  - If any capture is available for your side, you must capture.
  - If multiple capture chains are available, you may choose any one, but you must complete the chain for the chosen piece (you cannot stop early).
- Multi-capture:
  - After each jump, if another capture is available from the landing square (for that same piece), you must continue.
- Kinging:
  - A man that ends its move on the farthest rank becomes a king.
  - If a man reaches the king row during a capture, it is crowned immediately and the capture move ends (no continuing to capture as a new king within the same move).
- Win conditions:
  - You win if your opponent has no legal moves or no pieces remain.
- Draws:
  - The engine does not enforce complex draw rules (e.g., threefold repetition). Stalemate (no legal moves) results in a win for the opponent.

---

## Using the GUI

When launched, the GUI shows:
- The board with Red and Black pieces; kings are marked with “K”.
- Bottom panel with an input box and status messages.
- Last move highlights:
  - Blue outlines for simple steps
  - Orange outlines for captures

Controls:
- Click the input box to focus it.
- Type your move (e.g., `b6-c5`, `c3:e5:g7`) and press Enter to submit.
- Hotkeys:
  - R: Restart a new game
  - H: Print help to the console
  - ESC: Quit

Status messages guide you through errors (illegal moves, invalid notation) and turn updates. If the game ends, the status bar shows the result; press R to start over.

---

## Using the CLI

The CLI renders an ASCII board and prompts for input:
- Light squares show as `.`, dark squares as `_` when empty.
- Red men: `r`, Red kings: `R`
- Black men: `b`, Black kings: `B`

Commands:
- Enter moves: `b6-c5`, `c3:e5:g7`, `b6 to c5`, `B6 X A5`
- `help`: Show brief command help
- `restart`: Start a new game
- `quit` or `exit` or `q`: Exit the application

Example session:
- Prompt shows `[Red] move>`.
- Enter: `c3-d4`
- If a capture exists, attempting a simple move will be rejected with a message indicating that captures are enforced.

Non-interactive environments:
- If stdin is not a TTY (e.g., running in a pipeline), the CLI prints a success message and exits gracefully.

---

## Examples

Simple move (Red):
- Input: `c3-d4`

Single capture (Red):
- Input: `d4:f6`

Multi-capture (Black):
- Input: `e5:c3:a1`

Mixed separators and case:
- Input: `B6 X A5 x C4`

---

## Tips and Troubleshooting

- Pygame window does not open:
  - The app will automatically fall back to CLI mode. If you prefer GUI, ensure Pygame is installed and SDL can open a window on your system.
  - On Linux servers, try setting a display or using a desktop session. For headless mode, use CLI.
- Cannot type in the GUI:
  - Click inside the input box to focus it before typing. Press Enter to submit.
- “Invalid capture sequence or not maximal”:
  - You started a capture but didn’t include the full mandatory jump chain for that piece. Add all required landing squares. Example: `c3:e5:g7`.
- “It is Red/Black’s turn.”:
  - You attempted to move a piece of the wrong color; check the turn in the status area.
- Parse errors:
  - Ensure tokens are exactly two characters with a letter a–h and a digit 1–8 (e.g., `a3`, `h8`), and use accepted separators.

---

## Project Structure

- main.py – Entry point; launches GUI if possible, otherwise CLI.
- app.py – Pygame app loop, rendering, and input handling.
- board.py – Board and piece data structures and drawing.
- rules.py – Game rules: legal move generation, captures, kinging, turn/win logic.
- move_parser.py – Parses textual move notation into board coordinates.
- ui.py – Simple Pygame input box for move entry.
- constants.py – Display sizes, colors, and other shared constants.
- requirements.txt – Dependencies (Pygame).

---

## Customization

- Visuals and sizes: Adjust colors, sizes, and FPS in constants.py.
- Rules variant: Current implementation uses English/American rules (men cannot capture backward). To change, update capture directions in rules.py.

---

## License and Support

- This software is provided as-is by ChatDev for demonstration and gameplay.
- For issues, questions, or feature requests, please contact your ChatDev representative.

Enjoy the game!