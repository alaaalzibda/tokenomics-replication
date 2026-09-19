'''
Crossword controller: connects the model and view. Handles user events,
submits answers to the model for validation, updates the grid and clue lists,
and announces completion when the puzzle is solved.
Enhancements:
- Initializes the clue number selector to the minimum available clue number
  for better usability.
- NEW: Recomputes filled flags from the grid before rendering to keep
  clue checkmarks consistent even when entries are completed via crossings.
'''
from tkinter import messagebox
from typing import Optional
from crossword_model import CrosswordModel
from crossword_view import CrosswordView
class CrosswordController:
    def __init__(self, model: CrosswordModel, view: CrosswordView):
        self.model = model
        self.view = view
        # Initialize GUI with grid dimensions
        rows, cols = self.model.get_dimensions()
        self.view.build_grid(rows, cols)
        # Initial UI render
        self._refresh_all()
        # Set number range and initialize spinbox to the minimum clue number
        self.view.set_number_range(self.model.min_number(), self.model.max_number())
        self.view.number_var.set(str(self.model.min_number()))
        # Bind actions
        self.view.bind_submit(self.on_submit)
        self.view.bind_reset(self.on_reset)
    def _refresh_all(self):
        # Ensure filled flags reflect current grid state
        self.model.refresh_entry_flags()
        self.view.update_grid(self.model.get_cell)
        self.view.render_clues(
            across_entries=self.model.get_entries("A"),
            down_entries=self.model.get_entries("D"),
        )
    def on_submit(self):
        number, direction, answer = self.view.get_input()
        if number is None:
            self.view.set_status("Please enter a valid clue number.", ok=False)
            return
        if direction not in ("A", "D"):
            self.view.set_status("Direction must be A (Across) or D (Down).", ok=False)
            return
        if not answer:
            self.view.set_status("Please enter an answer.", ok=False)
            return
        ok, msg = self.model.place_answer(number, direction, answer)
        self.view.set_status(msg, ok=ok)
        if ok:
            self.view.clear_answer_field()
            self._refresh_all()
            if self.model.is_complete():
                messagebox.showinfo("Crossword", "Congratulations! You filled in all correct words.")
        else:
            # Keep the answer for correction; do not clear
            pass
    def on_reset(self):
        self.model.reset()
        self._refresh_all()
        self.view.set_status("Puzzle reset. You can start over.", ok=True)