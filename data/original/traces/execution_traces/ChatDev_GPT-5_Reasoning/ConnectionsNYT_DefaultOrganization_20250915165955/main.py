'''
Streamlit web app for the daily 4x4 word grouping puzzle with a graceful CLI fallback.
What changed (to fix test error: ModuleNotFoundError: No module named 'streamlit'):
- Wrapped the Streamlit import in a try/except. If Streamlit is unavailable, the app no longer crashes.
- Moved st.set_page_config into the Streamlit-available branch so it isn't called at import time when Streamlit is missing.
- Added a lightweight CLI fallback:
  - If running in an interactive terminal (stdin is a TTY), you can play a simple console version.
  - If running in a non-interactive environment (e.g., automated tests), it prints a helpful message and exits cleanly.
This ensures the software executes smoothly even without Streamlit installed, while preserving full functionality when Streamlit is present.
'''
from datetime import date as dt_date
from typing import List, Set, Dict
import random
import sys
from puzzle import generate_daily_puzzle, Puzzle
from utils import today_date_str
# Attempt to import Streamlit; provide graceful fallback if unavailable
try:
    import streamlit as st  # type: ignore
    HAS_STREAMLIT = True
except ModuleNotFoundError:
    st = None  # type: ignore
    HAS_STREAMLIT = False
# ---------- Streamlit implementation ----------
if HAS_STREAMLIT:
    # Configure page early (first Streamlit call)
    st.set_page_config(page_title="Daily 4x4 Connections", page_icon="🧩", layout="centered")
    # ---------- Session state management ----------
    def reset_daily(date_obj: dt_date) -> None:
        """Reset state for a given date (regenerates the daily puzzle)."""
        st.session_state.puzzle_date = date_obj
        st.session_state.puzzle = generate_daily_puzzle(date_obj)
        st.session_state.remaining = list(st.session_state.puzzle.words)
        st.session_state.selected = set()
        st.session_state.solved = []
        st.session_state.mistakes = 0
        st.session_state.locked = False
        st.session_state.feedback = {"type": "", "msg": ""}
    def set_feedback(kind: str, msg: str) -> None:
        """Store a feedback message to present on the next render."""
        st.session_state.feedback = {"type": kind, "msg": msg}
    def init_state() -> None:
        """Initialize Streamlit session state for a new or first visit, and roll over at midnight."""
        today = dt_date.today()
        if "puzzle_date" not in st.session_state:
            reset_daily(today)
            return
        # If a day has passed while the app is open, roll to the new daily puzzle
        if st.session_state.puzzle_date != today:
            reset_daily(today)
            return
        # Initialize missing keys (e.g., after Streamlit state clear)
        if "puzzle" not in st.session_state:
            st.session_state.puzzle = generate_daily_puzzle(st.session_state.puzzle_date)
        if "remaining" not in st.session_state:
            st.session_state.remaining = list(st.session_state.puzzle.words)
        if "selected" not in st.session_state:
            st.session_state.selected = set()
        if "solved" not in st.session_state:
            st.session_state.solved = []
        if "mistakes" not in st.session_state:
            st.session_state.mistakes = 0
        if "locked" not in st.session_state:
            st.session_state.locked = False
        if "feedback" not in st.session_state:
            st.session_state.feedback = {"type": "", "msg": ""}
    # ---------- Game actions ----------
    def toggle_word(word: str) -> None:
        """Toggle selection of a word when its button is clicked."""
        if st.session_state.locked:
            return
        if word not in st.session_state.remaining:
            return
        if word in st.session_state.selected:
            st.session_state.selected.remove(word)
        else:
            st.session_state.selected.add(word)
    def submit_guess() -> None:
        """Check the current selection, update solved groups or mistakes, and give feedback."""
        if st.session_state.locked:
            return
        selected = st.session_state.selected
        if len(selected) != 4:
            set_feedback("error", "Select exactly four words before submitting.")
            return
        puzzle: Puzzle = st.session_state.puzzle
        cat_idxs = {puzzle.word_to_category[w] for w in selected}
        if len(cat_idxs) == 1:
            # Correct set
            idx = next(iter(cat_idxs))
            cat = puzzle.categories[idx]
            # Remove from remaining words
            st.session_state.remaining = [w for w in st.session_state.remaining if w not in selected]
            # Record solved category info
            st.session_state.solved.append({
                "name": cat.name,
                "words": list(cat.words),
                "difficulty": cat.difficulty,
                "color": cat.color,
            })
            # Clear current selection
            st.session_state.selected = set()
            set_feedback("success", f"Correct! {cat.name} ({cat.difficulty}).")
            # Check win condition
            if len(st.session_state.remaining) == 0:
                st.session_state.locked = True
                set_feedback("success", "Puzzle complete! Great job.")
        else:
            # Incorrect guess
            st.session_state.mistakes += 1
            remaining_tries = max(0, 4 - st.session_state.mistakes)
            if st.session_state.mistakes >= 4:
                st.session_state.locked = True
                set_feedback("error", "Incorrect. You've reached the maximum mistakes (4). Game over.")
            else:
                set_feedback("error", f"Incorrect. Try again. Mistakes left: {remaining_tries}")
            # Clear selection after a wrong guess to prompt a rethink
            st.session_state.selected = set()
    def shuffle_remaining() -> None:
        """Shuffle the remaining words to change layout."""
        if st.session_state.locked:
            return
        random.shuffle(st.session_state.remaining)
    # ---------- UI helpers ----------
    def render_header() -> None:
        """Render the app title and meta info."""
        st.title("🧩 Daily 4x4 Connections")
        st.caption(f"Date: {today_date_str()} — Group the 16 words into four categories of four.")
    def render_solved() -> None:
        """Display solved groups with category name and color-coded difficulty."""
        if not st.session_state.solved:
            return
        st.subheader("Solved Groups")
        for group in st.session_state.solved:
            bg = group["color"]
            words_str = ", ".join(w.title() for w in group["words"])
            st.markdown(
                f'<div style="background:{bg};padding:10px;border-radius:6px;color:white">'
                f'<strong>{group["name"]}</strong> — {group["difficulty"].title()}<br/>{words_str}'
                f"</div>",
                unsafe_allow_html=True,
            )
    def render_status() -> None:
        """Show mistakes info and controls."""
        mistakes_left = max(0, 4 - st.session_state.mistakes)
        cols = st.columns([1, 1, 2])
        with cols[0]:
            st.metric("Mistakes Left", mistakes_left)
        with cols[1]:
            st.button("Shuffle", on_click=shuffle_remaining, disabled=st.session_state.locked)
        with cols[2]:
            st.caption("Hint: Select four words that fit the same hidden category, then click Submit.")
        # Feedback messages
        fb = st.session_state.feedback
        if fb["type"] == "success":
            st.success(fb["msg"])
        elif fb["type"] == "error":
            st.error(fb["msg"])
    def render_grid() -> None:
        """Render the 4x4 word grid with selectable buttons."""
        st.subheader("Words")
        remaining = st.session_state.remaining
        selected = st.session_state.selected
        locked = st.session_state.locked
        # Ensure grid shape (4x4) while 16 words remain; fewer rows as groups are solved
        n = len(remaining)
        rows = (n + 3) // 4
        word_iter = iter(remaining)
        for _ in range(rows):
            cols = st.columns(4)
            for c in cols:
                try:
                    w = next(word_iter)
                except StopIteration:
                    break
                is_selected = (w in selected)
                label = w.title()
                if is_selected:
                    # Visually mark selection
                    label = f"• {label} •"
                c.button(
                    label,
                    key=f"btn_{w}",
                    on_click=toggle_word,
                    args=(w,),
                    use_container_width=True,
                    disabled=locked,
                )
        # Submit button (enabled only when exactly 4 are selected and game not locked)
        st.button(
            "Submit Guess",
            on_click=submit_guess,
            disabled=(len(selected) != 4 or locked),
            type="primary",
        )
    def render_footer() -> None:
        """Render a small footer/help section."""
        with st.expander("How to play"):
            st.write(
                "- Tap words to select exactly four that share a common category.\n"
                "- Click Submit Guess to check. Correct groups disappear and reveal their category.\n"
                "- You can make up to 4 mistakes.\n"
                "- Click Shuffle to rearrange the remaining words.\n"
                "- A new puzzle is generated daily."
            )
    # ---------- Main app ----------
    def main() -> None:
        init_state()
        render_header()
        render_solved()
        render_status()
        render_grid()
        render_footer()
# ---------- CLI fallback implementation (no Streamlit) ----------
else:
    def main_cli() -> int:
        """Console fallback game loop if Streamlit isn't installed."""
        print("🧩 Daily 4x4 Connections (CLI fallback)")
        print(f"Date: {today_date_str()}")
        print("Tip: Install Streamlit for the full web experience: pip install streamlit")
        puzzle = generate_daily_puzzle(dt_date.today())
        remaining = list(puzzle.words)
        solved = []
        mistakes = 0
        def show_grid():
            n = len(remaining)
            rows = (n + 3) // 4
            print("\nWords:")
            it = iter(remaining)
            for _ in range(rows):
                row = []
                for _c in range(4):
                    try:
                        row.append(next(it).title())
                    except StopIteration:
                        break
                print("  " + " | ".join(f"{w:>12}" for w in row))
            print(f"\nMistakes left: {max(0, 4 - mistakes)}")
        while True:
            if len(remaining) == 0:
                print("\nPuzzle complete! Great job.")
                break
            if mistakes >= 4:
                print("\nIncorrect. You've reached the maximum mistakes (4). Game over.")
                # Reveal categories
                print("\nSolution categories:")
                for cat in puzzle.categories:
                    print(f"- {cat.name} ({cat.difficulty}): {', '.join(w.title() for w in cat.words)}")
                break
            show_grid()
            cmd = input("\nEnter four comma-separated words, or 'shuffle', or 'quit': ").strip().lower()
            if cmd in ("q", "quit", "exit"):
                print("Bye! Install Streamlit to play the full UI: pip install streamlit")
                break
            if cmd in ("s", "shuffle"):
                random.shuffle(remaining)
                continue
            # Parse selection
            parts = [p.strip() for p in cmd.split(",") if p.strip()]
            if len(parts) != 4:
                print("Please enter exactly four words separated by commas.")
                continue
            if any(p not in remaining for p in parts):
                print("All selected words must be from the remaining grid. Check spelling.")
                continue
            cat_idxs = {puzzle.word_to_category[w] for w in parts}
            if len(cat_idxs) == 1:
                idx = next(iter(cat_idxs))
                cat = puzzle.categories[idx]
                remaining = [w for w in remaining if w not in parts]
                solved.append(cat.name)
                print(f"Correct! {cat.name} ({cat.difficulty}).")
            else:
                mistakes += 1
                print(f"Incorrect. Try again. Mistakes left: {max(0, 4 - mistakes)}")
        return 0
    def main() -> None:
        """Entry point for non-Streamlit environments."""
        # If in a non-interactive environment, avoid blocking on input.
        if sys.stdin is None or not sys.stdin.isatty():
            print("Streamlit is not installed. Install it with `pip install streamlit` to run the web app.")
            return
        main_cli()
if __name__ == "__main__":
    main()