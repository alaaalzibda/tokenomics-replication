# Match‑3 Puzzle Game (Candy‑Crush‑style)

Change the digital world through programming — one satisfying match at a time.

A modern, responsive, browser‑based match‑3 puzzle game implemented in vanilla JavaScript, HTML, and CSS. Swap adjacent candies to form lines of 3 or more, clear them to score points, trigger chain reactions, and play under either a moves‑limited or time‑limited challenge.

## Key Features

- Classic match‑3 mechanics:
  - Swap adjacent candies to make lines of 3+ of the same color.
  - Matches clear, gravity drops candies, and new candies refill the board.
  - Automatic chain reactions with scoring multipliers.
- Two modes:
  - Moves mode: Finish with the highest score within a limited number of moves.
  - Time mode: Race the clock to score as much as possible.
- Smart board generation:
  - No initial matches.
  - Guaranteed at least one valid move.
- Quality of life:
  - Shuffle when stuck (or on demand via button).
  - Visual feedback for invalid moves, selections, and clearing.
  - Responsive design and accessible markup (ARIA grid cells).
- Zero build step:
  - 100% client‑side. No external JS frameworks. Just serve and play.

## Quick Start

You can run the game locally with any simple static server.

- Option A — Python (installed by default on many systems)
  - Python 3:  
    `python3 -m http.server 8000`
  - Python 2:  
    `python -m SimpleHTTPServer 8000`
  - Then open: http://localhost:8000

- Option B — Node.js (via npx)
  - Using http-server:  
    `npx http-server -p 8000`
  - Or using serve:  
    `npx serve -l 8000`
  - Then open: http://localhost:8000

- Option C — VS Code Live Server extension
  - Right‑click index.html → “Open with Live Server”.

Note: Due to ES module imports, opening index.html directly via the file:// protocol may be blocked by the browser. Use a local HTTP server as shown above.

## Project Structure

- index.html — App shell and UI controls; loads the game module.
- style.css — Styling, animations, and responsive layout.
- utils.js — Small utilities (sleep, formatTime).
- board.js — Core board logic: matches, gravity, refills, valid move detection, reshuffling.
- game.js — Game controller: user input, scoring, chain resolution, HUD, and mode/timer handling.

## How to Play

- Select a Mode:
  - Moves (default) or Time. Tip: Choose the mode before starting a new game.
- Start:
  - Click “New Game”. In Time mode, the timer starts immediately.
- Swap:
  - Click a candy to select it (it highlights), then click an adjacent candy (up, down, left, right) to attempt a swap.
  - If the swap does not create a match, the tiles shake and the move is not performed.
- Score:
  - Creating a match clears candies. Gravity pulls remaining candies down, and new candies fall from the top. Chain reactions can occur automatically, awarding extra points with multipliers.
- Shuffle:
  - Click “Shuffle” anytime to rearrange the board (helpful if you can’t spot a move).
  - The game also auto‑reshuffles if no moves remain after a turn.
- Finish:
  - Moves mode ends when moves reach 0.
  - Time mode ends when the timer hits 0.
  - A Game Over screen shows your final score and lets you play again.

## Game Modes

- Moves Mode
  - You have a limited number of moves (default: 30).
  - Each valid swap that results in at least one match consumes 1 move (swapping only occurs if it creates a match).
- Time Mode
  - You have a fixed amount of time (default: 120 seconds).
  - Make as many valid swaps as you can before time runs out.
  - The timer starts when you click “New Game” in Time mode.

Important: Changing the mode toggle during a running game only changes what is displayed in the HUD. The underlying rules (moves vs time) are applied when you start a new game. For a true mode switch, change the toggle and click “New Game”.

## Scoring

- Base points: 10 points per candy cleared.
- Chain multiplier: Each cascading step increases the multiplier.
  - First clear in a sequence: x1
  - Second clear (from the cascade): x2
  - Third: x3, and so on.

Example:
- You match 3 candies (Step 1): 3 × 10 × 1 = 30 points.
- Candies fall and a new match of 4 occurs (Step 2): 4 × 10 × 2 = 80 points.
- Total for the sequence: 110 points.

## Board Mechanics and Rules

- Adjacency: Swaps are only allowed between tiles that are directly adjacent horizontally or vertically.
- Validity: A swap must create at least one match of 3+ to occur; otherwise, the tiles shake and revert.
- Initial state: The board is generated with no immediate matches and at least one valid move.
- Gravity: After clearing, candies above fall down to fill empty spaces.
- Refill: New candies appear at the top to fill any remaining empty spaces.
- Stuck handling: If no valid moves remain, the board automatically reshuffles (preserving no initial matches and at least one valid move).

## Controls and UI

- Mode toggle: Moves / Time
- HUD:
  - Score: Current total points.
  - Moves: Remaining moves (Moves mode).
  - Time: Remaining time (Time mode).
- Actions:
  - New Game: Starts a fresh game using the currently selected mode.
  - Shuffle: Randomly reshuffles the board without penalty.
- Message area: Short hints (e.g., when a move is invalid or a reshuffle occurs).
- Game Over Overlay: Displays end reason and final score, with a quick “Play Again” button.

## Accessibility

- The board uses role="grid" and each tile uses role="gridcell".
- Tile selection and interaction are click/tap based.
- Colorful, high‑contrast candies and subtle animations communicate state changes.

Tip: If you need additional accessibility options (keyboard controls, reduced motion), see the Customization section below.

## Installation and Dependencies

- Runtime: A modern web browser (Chrome, Edge, Firefox, Safari — latest two versions recommended).
- No package installation required. The app runs as static files.
- Serving: Use any static HTTP server (see Quick Start) to avoid module import restrictions.

## Customization and Configuration

For light changes, no code compilation is required. Edit the following:

- Board size and candy variety (game.js and board.js)
  - In game.js (GameController constructor):
    - this.rows = 8;
    - this.cols = 8;
    - this.candyTypes = 6; // must match available CSS classes .candy-0..N
  - In style.css:
    - Add or adjust color gradients for .candy-0 to .candy-5.
- Limits:
  - Moves: this.defaultMoves = 30;
  - Time: this.defaultTime = 120; // seconds
- Tile size and visuals (style.css)
  - :root variables:
    - --tile-size: 64px; // change to 56px, 72px, etc.
    - --gap, --radius, and color variables for theming.
- Animations:
  - Tweak keyframes for shake and pop in style.css to adjust feedback intensity.
- Accessibility:
  - Add a “Reduce Motion” toggle to conditionally disable CSS animations.
  - Add keyboard navigation by listening for arrow keys and Enter/Space in game.js.
- Advanced rule tweaks (board.js):
  - Extend Board to add special candies for 4/5 matches.
  - Modify scoring in resolveChains() within game.js to award bonuses.

Developer note: The Board class (board.js) contains self‑contained logic for match detection, clearing, gravity, refill, valid move search, and reshuffling. The GameController (game.js) wires this logic to the UI, HUD, and user interactions.

## Known Limitations

- Swaps are click/tap only; no keyboard controls by default.
- There are no special candies or blockers; only standard match‑3 rules.
- Changing mode mid‑game does not retroactively start/stop timers or move counters; start a New Game after switching.

## Troubleshooting

- I see a blank page or module errors.
  - Ensure you are serving via HTTP (see Quick Start). Opening with file:// can block ES module imports.
- The board has no moves.
  - The engine auto‑reshuffles if no moves remain. You can also click “Shuffle”.
- Performance is choppy on mobile.
  - Try reducing --tile-size and animation timings in style.css.
- Colors are hard to distinguish.
  - Modify the .candy-* gradients in style.css to increase contrast or introduce icons/labels.

## FAQ

- Does shuffling cost a move or time?
  - No, shuffling is free. It simply regenerates the board to help you find moves.
- Can I pause the timer?
  - Not currently. You can switch to Moves mode if you prefer a non‑timed experience.
- Does the game support saving progress?
  - No, the game state resets on reload.

## Version and Support

- Version: 1.0.0 (website, vanilla JS)
- Created by: ChatDev — Chief Product Officer and team
- Issues or ideas: We welcome feedback to improve gameplay, accessibility, and customization.

Enjoy and happy matching!