# Daily 4x4 Connections — User Manual

Group 16 words into four hidden categories of four. Test your intuition, find the connections, and beat the puzzle before you run out of mistakes. A fresh puzzle appears every day.

This manual explains what the app does, how to install and run it (web and CLI), how to play, and how the daily puzzle is generated.

---

## Features

- 4x4 word grid with tap-to-select interaction
- Form groups of four words based on hidden categories
- Immediate feedback after each guess
- Color-coded difficulty for solved groups:
  - Yellow (easiest)
  - Green (medium)
  - Blue (hard)
  - Purple (trickiest)
- Shuffle button to rearrange remaining words
- Mistake counter (maximum of 4 mistakes allowed)
- Only one correct solution exists (even if some words could fit multiple ideas)
- Auto-generates a new puzzle every day
- Console/terminal fallback if Streamlit isn’t installed

---

## How the Game Works

- Start with 16 words arranged in a 4x4 grid.
- Your goal: identify the four hidden categories and group the words into four sets of four.
- Select exactly four words and submit your guess.
  - If correct, the set is removed, and the category and its difficulty color are revealed.
  - If incorrect, you consume one mistake (max 4 mistakes). After 4 mistakes, the game ends.
- Shuffle anytime to change the arrangement and prompt fresh perspective.
- Only one official solution exists per day, even if multiple interpretations seem plausible.

Difficulty colors:
- Yellow: #f7da21
- Green: #66bb6a
- Blue: #42a5f5
- Purple: #8e24aa

---

## Quick Start

### Prerequisites

- Python 3.8+ recommended
- pip

Optional:
- A virtual environment tool (venv, conda, etc.)

### Installation

1) Clone or download the project files into a folder.

2) Create and activate a virtual environment (recommended):

- macOS/Linux:
  ```
  python -m venv .venv
  source .venv/bin/activate
  ```

- Windows (PowerShell):
  ```
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```

3) Install dependencies:
```
pip install -r requirements.txt
```

This installs Streamlit, which powers the web app.

---

## Run the Web App (Recommended)

From your project directory:
```
streamlit run main.py
```

- A browser tab should open at a local URL (e.g., http://localhost:8501).
- If it doesn’t, open the displayed URL manually.

---

## CLI Fallback (No Streamlit)

If Streamlit isn’t installed, you can still play a simple console version:
```
python main.py
```

Notes:
- If Streamlit is installed, always launch via “streamlit run main.py” for the full web experience.
- In non-interactive environments (e.g., CI), the script exits cleanly with a helpful message.

---

## How to Play (Web)

1) Select words:
   - Click/tap a word to select it.
   - Selected words are visually highlighted.
   - You must select exactly four words to submit.

2) Submit a guess:
   - Click “Submit Guess”.
   - If the four words belong to the same hidden category:
     - They are removed from the grid.
     - The category name and its color-coded difficulty appear under “Solved Groups”.
   - If not:
     - You will see an error and your mistakes counter increases.
     - After a wrong guess, the selection clears to encourage a fresh approach.

3) Shuffle:
   - Click “Shuffle” to rearrange the remaining words.

4) Mistakes:
   - You may make up to 4 mistakes in total.
   - After 4 mistakes, the puzzle locks and the game ends.

5) Win condition:
   - Solve all four groups. You’ll see a “Puzzle complete!” message.

6) Daily reset:
   - The app auto-detects the change of local day and loads a new puzzle.
   - The date is shown at the top.

7) Help:
   - Open the “How to play” expander in the app for quick tips.

---

## How to Play (CLI)

1) Start:
   ```
   python main.py
   ```
   You’ll see:
   - The date
   - The word grid (shown in rows)
   - “Mistakes left” indicator

2) Commands:
   - Enter four comma-separated words to guess (e.g., `apple, banana, orange, grape`)
   - Enter `shuffle` (or `s`) to rearrange the remaining words
   - Enter `quit` (or `q`) to exit

3) Feedback:
   - “Correct!” with the category name if your set is valid
   - “Incorrect” and reduced mistakes left if not
   - On game over, the solution categories are revealed

---

## Daily Puzzle Generation (Technical Notes)

- Exactly one category per difficulty is selected for the day: Yellow, Green, Blue, Purple.
- Words are unique across the entire category bank to guarantee a unique solution.
- The puzzle is deterministic per local date:
  - Seed is derived from “days since Unix epoch” for the current local date.
  - The 16 words are then shuffled deterministically for a fixed daily layout.
- At midnight (local time), the app resets to the new day’s puzzle on next interaction/refresh.

Files involved:
- puzzle.py: Puzzle model and daily generator
- category_bank.py: Curated categories and words
- utils.py: Date utilities and deterministic seeding

---

## Project Structure

- main.py — Streamlit app + CLI fallback and all UI/gameplay wiring
- puzzle.py — Data structures and daily puzzle generator
- category_bank.py — Category definitions (name, four words, difficulty)
- utils.py — Date utilities and RNG helpers
- requirements.txt — Python dependencies (Streamlit)

---

## Customization and Extensibility

- Add categories:
  - Edit category_bank.py and append new CategoryDefinition entries.
  - Ensure:
    - Exactly 4 unique words per category
    - Words are lowercase and unique across the entire bank
    - Difficulty is one of: yellow, green, blue, purple
- Change color theme:
  - Adjust get_color_for_difficulty in puzzle.py if desired.

Caution: Duplicate words across categories can break the unique-solution guarantee.

---

## Troubleshooting

- “Command not found: streamlit”:
  - Install dependencies: `pip install -r requirements.txt`
  - Or install Streamlit directly: `pip install streamlit`

- Web app doesn’t open automatically:
  - Copy and paste the printed URL (e.g., http://localhost:8501) into your browser.

- Port already in use:
  - Run with a different port:
    ```
    streamlit run main.py --server.port=8502
    ```

- Blank or non-responsive page:
  - Stop and restart Streamlit.
  - Clear browser cache or try a private window.

- Wrong puzzle for your day:
  - The app uses your system’s local date. Check your OS clock/timezone.
  - Refresh after midnight to load the new daily puzzle.

- Playing in terminal:
  - If Streamlit isn’t installed, running `python main.py` starts the CLI game.
  - In non-interactive terminals, the script will not wait for input.

---

## FAQ

- Is there really only one correct solution?
  - Yes. While multiple interpretations may seem possible, the official categories and unique word selection ensure a single valid arrangement.

- Can I revisit previous days?
  - Not in the UI. The app is designed as a daily challenge. You can explore the code in puzzle.py to generate puzzles for specific dates if needed.

- Does the app send any data?
  - No. Puzzles are generated locally and run entirely on your machine.

---

## Credits

Built with Python and Streamlit. Puzzle logic and category curation live in the repository to make daily puzzles deterministic and self-contained.

Enjoy discovering the connections!