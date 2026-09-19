# ChatDev Tetris — User Manual

Changing the digital world through programming

Version: 1.0  
Modality: Website (Vanilla JavaScript)

## Overview

ChatDev Tetris is a clean, modern, browser-based rendition of the classic falling-block puzzle game. Guide tetrominoes as they fall, rotate and move them to complete horizontal lines, and rack up points. The game speeds up as you clear lines, includes all seven standard tetromino shapes, a next-piece preview, a ghost piece to aid placement, and polished visuals that look crisp on HiDPI screens.

Key highlights:
- All 7 standard tetrominoes (I, O, T, S, Z, J, L)
- 7‑bag randomizer for fair piece distribution
- Smooth movement, rotation with wall kicks
- Soft and hard drop with scoring
- Line clear scoring with level multiplier
- Increasing gravity as levels rise
- Ghost piece and next-piece preview
- Pause/Resume and Restart controls
- Responsive, accessible UI (ARIA-labeled canvases)

## What’s in the box

Project files:
- index.html — Main HTML entry and layout
- style.css — Game styling and layout
- main.js — App bootstrap, animation loop, and UI wiring
- game.js — Game orchestration (state, scoring, levels, timers)
- board.js — Grid, collision, and line clearing
- piece.js — Piece logic (movement, rotation with simple wall kicks)
- shapes.js — Shapes, colors, spawn offsets
- renderer.js — Canvas rendering for board, ghost, and next preview
- utils.js — Helpers (shuffle, clamp)

No external dependencies, no build step.

## System Requirements

- A modern desktop browser:
  - Chrome 90+, Edge 90+, Firefox 88+, Safari 14+
- Keyboard input (for game controls)
- Local HTTP server to serve ES modules (recommended)

Note: The app uses native ES modules (type="module"). Some browsers restrict loading modules via file://. If you see module/CORS errors when double-clicking index.html, run a local web server (see Quick Start).

## Quick Start

1) Get the code
- Download or clone the project folder so index.html and the JS/CSS files sit together.

2) Serve locally (recommended)
Choose one of the options below and run it in the project directory:

- Python (3.x)
```
python3 -m http.server 8080
```
Then open http://localhost:8080/ in your browser.

- Node.js (npx)
```
npx http-server -p 8080
```
Then open http://localhost:8080/

- VS Code Live Server
  - Install the “Live Server” extension.
  - Right‑click index.html → “Open with Live Server”.

3) Play
- The game auto‑starts on load.
- Use the buttons or keyboard to control play.

Alternative: Open index.html directly
- You can try double‑clicking index.html. If you encounter a “CORS” or module loading error, use one of the local server options above.

## How to Play

Objective
- Move and rotate falling tetrominoes to complete horizontal lines.
- Completed lines are cleared. Score increases and the game speeds up as you level up.
- The game ends when a new piece can’t be placed (stack reaches the top).

Controls
- Left/Right: Move piece
- Down: Soft drop
- Up or X: Rotate clockwise (CW)
- Z: Rotate counter-clockwise (CCW)
- Space: Hard drop (instantly locks)
- P: Pause/Resume
- R: Restart
- Enter: Start (also available via button)

UI controls (sidebar)
- Start: Starts a new game or resumes if paused (also Enter)
- Pause: Pause/Resume (also P); button label updates accordingly
- Restart: Start fresh (also R)

On-screen info
- Next: Preview of the next piece
- Score: Current score
- Lines: Total lines cleared
- Level: Current level (speed increases with each level)

Gameplay details
- Gravity: Pieces fall automatically. Gravity accelerates as your level increases.
- Lock delay: Once a piece touches down and can’t move down further, there’s a short lock delay (~500 ms). Moving or rotating during this time resets the timer. Hard drop locks immediately.
- Ghost: A translucent “ghost” shows where the current piece would land.

Scoring
- Soft drop: +1 point per cell descended using Down
- Hard drop: +2 points per cell descended using Space
- Line clears (multiplied by current level):
  - 1 line: 100 points
  - 2 lines: 300 points
  - 3 lines: 500 points
  - 4 lines (Tetris): 800 points

Levels and speed
- Level increases every 10 lines cleared: level = floor(lines / 10) + 1
- Gravity interval (time between automatic drops) starts around 1000 ms and decreases by ~75 ms per level, down to a minimum of ~90 ms.

Game Over
- Occurs when a new piece cannot spawn at the top of the board.
- The board shows a “Game Over” overlay. Press Restart (R) to play again.

## Features and Design Choices

- 7‑bag next queue: Ensures an even distribution of tetrominoes by shuffling all seven before repeating.
- Wall kicks: Simple kick tests allow rotations near walls/obstacles.
- Crisp rendering: HiDPI-aware canvas setup for sharp visuals on Retina/4K displays.
- Subtle grid and shaded blocks: Improves readability and depth.
- Accessibility: ARIA labels on canvases; keyboard-first controls; buttons for mouse users.

Known limitations (by design for simplicity)
- Rotation uses a simplified wall-kick system, not the full SRS guide.
- No “Hold” piece mechanic.
- Touch controls are not included (keyboard gameplay first).

## Troubleshooting

- I see “Failed to load module” or CORS errors:
  - Serve the folder with a local HTTP server instead of opening index.html directly (see Quick Start).
- Keys don’t respond:
  - Click the page once to ensure it’s focused.
  - Check if your system/browser has global shortcuts that override the game keys.
- Performance issues:
  - Close other intensive tabs/apps.
  - Try a different modern browser.
- Nothing happens when I press Start:
  - The game auto-starts on load. If paused, the Start button resumes; use Restart (R) for a fresh run.

## Deploying

Because it’s a static site, any static hosting works:
- GitHub Pages, Netlify, Vercel, Cloudflare Pages, S3/CloudFront, or your own server
- Upload all files in the project folder as-is
- Ensure files are served with correct MIME types (default on standard hosts)

## Customization (for Developers)

Basic tweaks
- Board cell size: main.js → new Game({ cellSize: 32 })
- Board dimensions: main.js and game.js constructor options (cols, rows)
- Colors per piece: shapes.js → COLORS
- Spawn centering: shapes.js → SPAWN_OFFSETS
- Lock delay: game.js → this.lockDelay (ms)
- Gravity curve: game.js → computeDropInterval(level)
- Scoring: game.js → lockPiece() scoring section
- UI labels/controls: index.html + style.css

Architecture overview
- game.js: Central game loop, timers, scoring, levels, next queue (7-bag), lock delay
- board.js: Grid state, collision checks, merge and clear lines
- piece.js: Piece state, movement, rotation with simple kicks
- renderer.js: Canvas drawing for board, active piece, ghost, and next
- shapes.js: Shape rotation matrices and color mapping
- input.js: Keyboard bindings for movement, rotation, drops
- main.js: Canvas setup (HiDPI), UI wiring, RAF loop, pause/resume management

Tip: Because everything uses ES modules, you can import and extend classes to experiment with features (e.g., add “Hold”, SRS, or combos).

## Accessibility Notes

- Canvases include ARIA labels and roles for assistive technologies.
- All primary actions have keyboard shortcuts and clickable buttons.
- Color choices balance contrast and clarity; adjust in style.css and shapes.js as needed.

## FAQ

- Can I play offline?
  - Yes. Once loaded, the game runs entirely in the browser. You still need to serve the files locally the first time to avoid module/CORS issues.
- Does it work on mobile?
  - The layout is responsive, but the game is keyboard-first. Touch controls aren’t included by default.
- Can I change the speed progression?
  - Yes. Edit computeDropInterval(level) in game.js.

## Credits

Built by ChatDev — Changing the digital world through programming.