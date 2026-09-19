'''
Main entry point for the Trivia Quiz GUI application using tkinter.
Provides the GUI screens for starting the quiz, taking the quiz, and viewing results.
'''
import os
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, List
from question_bank import get_builtin_banks, load_bank_from_json
from quiz_manager import QuizSession
from models import Question
class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Trivia Quiz")
        self.geometry("820x600")
        self.minsize(720, 520)
        # Application state
        self.banks = get_builtin_banks()  # name -> list[Question]
        self.current_session: Optional[QuizSession] = None
        self.selected_bank_name: Optional[str] = None
        self.selected_questions: Optional[List[Question]] = None
        # Container for frames
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (StartFrame, QuizFrame, ResultFrame):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("StartFrame")
    def show_frame(self, name: str):
        frame = self.frames[name]
        if name == "StartFrame":
            frame.refresh_banks()
        frame.tkraise()
    def get_bank_names(self):
        return list(self.banks.keys())
    def add_custom_bank(self, path: str, questions: List[Question]):
        # Create unique display name for custom bank
        base = os.path.basename(path)
        name = f"Custom: {base}"
        suffix = 1
        while name in self.banks:
            suffix += 1
            name = f"Custom: {base} ({suffix})"
        self.banks[name] = questions
        return name
    def start_quiz(self, bank_name: str, count: int, shuffle: bool, show_answers: bool):
        if bank_name not in self.banks:
            messagebox.showerror("Error", "Selected question bank not found.")
            return
        questions = list(self.banks[bank_name])
        if shuffle:
            random.shuffle(questions)
        if count < 1:
            count = 1
        if count > len(questions):
            count = len(questions)
        questions = questions[:count]
        self.selected_bank_name = bank_name
        self.selected_questions = questions
        self.current_session = QuizSession(questions, show_answers=show_answers)
        # Prepare QuizFrame with the first question
        quiz_frame = self.frames["QuizFrame"]
        quiz_frame.reset()
        quiz_frame.load_question()
        self.show_frame("QuizFrame")
    def finish_quiz(self):
        self.show_frame("ResultFrame")
        result_frame = self.frames["ResultFrame"]
        result_frame.render_results()
    def restart(self):
        # Clear current session and go back to start
        self.current_session = None
        self.selected_bank_name = None
        self.selected_questions = None
        self.show_frame("StartFrame")
class StartFrame(ttk.Frame):
    def __init__(self, parent, controller: QuizApp):
        super().__init__(parent)
        self.controller = controller
        # Variables
        self.bank_var = tk.StringVar(value="")
        self.show_answers_var = tk.BooleanVar(value=True)
        self.shuffle_var = tk.BooleanVar(value=True)
        self.count_var = tk.IntVar(value=5)
        self.current_bank_size = 0
        # Layout
        header = ttk.Label(self, text="Trivia Quiz", font=("Segoe UI", 20, "bold"))
        header.pack(pady=(20, 10))
        desc = ttk.Label(self, text="Choose a question bank, configure options, and click Start to begin.")
        desc.pack(pady=(0, 15))
        content = ttk.Frame(self)
        content.pack(fill="x", padx=20)
        # Bank selection
        bank_frame = ttk.LabelFrame(content, text="Question Bank")
        bank_frame.pack(fill="x", padx=10, pady=10)
        self.bank_menu = ttk.Combobox(bank_frame, textvariable=self.bank_var, state="readonly")
        self.bank_menu.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        self.bank_menu.bind("<<ComboboxSelected>>", self.on_bank_change)
        load_btn = ttk.Button(bank_frame, text="Load from JSON...", command=self.on_load_json)
        load_btn.pack(side="left", padx=10, pady=10)
        # Options
        options_frame = ttk.LabelFrame(content, text="Options")
        options_frame.pack(fill="x", padx=10, pady=10)
        show_chk = ttk.Checkbutton(options_frame, text="Show correct answers after quiz", variable=self.show_answers_var)
        show_chk.grid(row=0, column=0, sticky="w", padx=10, pady=8)
        shuffle_chk = ttk.Checkbutton(options_frame, text="Shuffle questions", variable=self.shuffle_var)
        shuffle_chk.grid(row=1, column=0, sticky="w", padx=10, pady=8)
        count_lbl = ttk.Label(options_frame, text="Number of questions:")
        count_lbl.grid(row=0, column=1, sticky="e", padx=(30, 5), pady=8)
        self.count_spin = tk.Spinbox(options_frame, from_=1, to=10, textvariable=self.count_var, width=6, justify="center")
        self.count_spin.grid(row=0, column=2, sticky="w", padx=(0, 10), pady=8)
        self.bank_size_label = ttk.Label(options_frame, text="Bank contains: 0 questions")
        self.bank_size_label.grid(row=1, column=1, columnspan=2, sticky="w", padx=(30, 5), pady=8)
        for i in range(3):
            options_frame.grid_columnconfigure(i, weight=1)
        # Actions
        action_frame = ttk.Frame(self)
        action_frame.pack(pady=20)
        start_btn = ttk.Button(action_frame, text="Start Quiz", command=self.on_start)
        start_btn.pack()
        self.refresh_banks()
    def refresh_banks(self):
        names = self.controller.get_bank_names()
        self.bank_menu["values"] = names
        # Select first bank by default
        if names and (self.bank_var.get() not in names):
            self.bank_var.set(names[0])
            self.update_bank_size()
    def on_bank_change(self, event=None):
        self.update_bank_size()
    def on_load_json(self):
        path = filedialog.askopenfilename(
            title="Load Question Bank (JSON)",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            questions = load_bank_from_json(path)
            if not questions:
                raise ValueError("No valid questions found in the file.")
            name = self.controller.add_custom_bank(path, questions)
            # Refresh banks and select loaded one
            self.refresh_banks()
            self.bank_var.set(name)
            self.update_bank_size()
            messagebox.showinfo("Loaded", f"Loaded {len(questions)} questions from:\n{os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load bank:\n{e}")
    def update_bank_size(self):
        name = self.bank_var.get()
        count = 0
        if name in self.controller.banks:
            count = len(self.controller.banks[name])
        self.current_bank_size = count
        self.bank_size_label.config(text=f"Bank contains: {count} questions")
        # Update spinbox max
        to_val = max(1, count if count > 0 else 1)
        self.count_spin.config(to=to_val)
        # Adjust current value if needed
        if self.count_var.get() > to_val:
            self.count_var.set(to_val)
        elif self.count_var.get() < 1:
            self.count_var.set(1)
    def on_start(self):
        bank_name = self.bank_var.get()
        if not bank_name:
            messagebox.showwarning("Select Bank", "Please select a question bank.")
            return
        if bank_name not in self.controller.banks:
            messagebox.showerror("Error", "Selected question bank not found.")
            return
        if self.current_bank_size == 0:
            messagebox.showwarning("Empty Bank", "The selected bank has no questions.")
            return
        try:
            count = int(self.count_var.get())
        except ValueError:
            count = 1
        self.controller.start_quiz(
            bank_name=bank_name,
            count=count,
            shuffle=self.shuffle_var.get(),
            show_answers=self.show_answers_var.get()
        )
class QuizFrame(ttk.Frame):
    def __init__(self, parent, controller: QuizApp):
        super().__init__(parent)
        self.controller = controller
        self.question_label = None
        self.progress_label = None
        self.content_frame = None
        self.nav_button = None
        self.mcq_var = tk.IntVar(value=-1)          # for single-select MCQ
        self.mcq_vars: List[tk.BooleanVar] = []     # for multi-select MCQ
        self.short_var = tk.StringVar(value="")
        # Build layout
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(10, 5), padx=10)
        self.progress_label = ttk.Label(header, text="")
        self.progress_label.pack(side="right")
        title = ttk.Label(header, text="Answer the question:", font=("Segoe UI", 14, "bold"))
        title.pack(side="left")
        self.question_label = ttk.Label(self, text="", wraplength=760, justify="left", font=("Segoe UI", 12))
        self.question_label.pack(fill="x", padx=14, pady=(8, 14))
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill="x", padx=10, pady=(0, 12))
        self.nav_button = ttk.Button(nav_frame, text="Submit", command=self.on_submit)
        self.nav_button.pack(side="right")
    def reset(self):
        self.mcq_var.set(-1)
        self.mcq_vars = []
        self.short_var.set("")
        for w in self.content_frame.winfo_children():
            w.destroy()
    def load_question(self):
        self.reset()
        session = self.controller.current_session
        if session is None:
            return
        q = session.current_question()
        if q is None:
            return
        idx = session.current_index + 1
        total = len(session.questions)
        self.progress_label.config(text=f"Question {idx} of {total}")
        self.question_label.config(text=q.prompt)
        if q.qtype == "mcq":
            self.render_mcq(q)
        else:
            self.render_short(q)
        # Update button text for last question
        if idx == total:
            self.nav_button.config(text="Finish")
        else:
            self.nav_button.config(text="Submit")
    def render_mcq(self, question: Question):
        # Use stable public API to determine multi-answer MCQs
        if question.is_multi_answer():
            hint = ttk.Label(
                self.content_frame,
                text="This question may have multiple correct answers. Select all that apply.",
                foreground="#555"
            )
            hint.pack(anchor="w", padx=8, pady=(0, 6))
            self.mcq_vars = []
            for i, opt in enumerate(question.options or []):
                var = tk.BooleanVar(value=False)
                cb = ttk.Checkbutton(self.content_frame, text=opt, variable=var)
                cb.pack(anchor="w", pady=4, padx=8)
                self.mcq_vars.append(var)
        else:
            self.mcq_var.set(-1)
            for i, opt in enumerate(question.options or []):
                rb = ttk.Radiobutton(self.content_frame, text=opt, variable=self.mcq_var, value=i)
                rb.pack(anchor="w", pady=4, padx=8)
    def render_short(self, question: Question):
        lbl = ttk.Label(self.content_frame, text="Your answer:")
        lbl.pack(anchor="w", padx=8, pady=(0, 6))
        entry = ttk.Entry(self.content_frame, textvariable=self.short_var, width=60)
        entry.pack(anchor="w", padx=8, pady=(0, 6))
        entry.focus_set()
    def on_submit(self):
        session = self.controller.current_session
        if session is None:
            return
        q = session.current_question()
        if q is None:
            return
        if q.qtype == "mcq":
            if q.is_multi_answer():
                # Collect all selected indices
                selections = [i for i, var in enumerate(self.mcq_vars) if var.get()]
                if not selections:
                    messagebox.showwarning("No Selection", "Please select at least one option before proceeding.")
                    return
                user_answer = selections
            else:
                choice = self.mcq_var.get()
                if choice == -1:
                    messagebox.showwarning("No Selection", "Please select an option before proceeding.")
                    return
                user_answer = choice
        else:
            text = self.short_var.get().strip()
            if not text:
                messagebox.showwarning("No Answer", "Please enter an answer before proceeding.")
                return
            user_answer = text
        session.submit_answer(user_answer)
        if session.has_next():
            self.load_question()
        else:
            self.controller.finish_quiz()
class ResultFrame(ttk.Frame):
    def __init__(self, parent, controller: QuizApp):
        super().__init__(parent)
        self.controller = controller
        self.header_label = ttk.Label(self, text="Results", font=("Segoe UI", 16, "bold"))
        self.header_label.pack(pady=(14, 6))
        self.summary_label = ttk.Label(self, text="")
        self.summary_label.pack(pady=(0, 10))
        # Scrollable review area
        self.review_container = ttk.Frame(self)
        self.review_container.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas = tk.Canvas(self.review_container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.review_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        # Buttons
        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=10, pady=(0, 12))
        back_btn = ttk.Button(btns, text="Back to Start", command=self.controller.restart)
        back_btn.pack(side="left")
        retake_btn = ttk.Button(btns, text="Retake (same bank/options)", command=self.retake)
        retake_btn.pack(side="left", padx=(8, 0))
        # Resize handling
        self.bind("<Configure>", self._on_resize)
    def _on_resize(self, event):
        # Resize the inner frame width to match canvas width
        self.canvas.itemconfig(self.canvas_frame, width=event.width - 24)
    def clear_review(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()
    def render_results(self):
        self.clear_review()
        session = self.controller.current_session
        if session is None:
            return
        score, total, records = session.results()
        self.summary_label.config(text=f"You scored {score} out of {total}.")
        # If configured, show detailed answers
        if session.show_answers:
            for i, rec in enumerate(records, start=1):
                q: Question = rec["question"]
                user_ans = rec["user_answer"]
                correct = rec["correct"]
                block = ttk.Frame(self.scrollable_frame, padding=8)
                block.pack(fill="x", padx=4, pady=6)
                title = ttk.Label(
                    block,
                    text=f"Q{i}. {q.prompt}",
                    wraplength=760,
                    justify="left",
                    font=("Segoe UI", 11, "bold")
                )
                title.pack(anchor="w", pady=(0, 6))
                ua_text = q.get_user_answer_text(user_ans)
                ua_lbl = ttk.Label(block, text=f"Your answer: {ua_text}", wraplength=760, justify="left")
                ua_lbl.pack(anchor="w")
                ca_text = q.get_correct_answer_text()
                ca_lbl = ttk.Label(block, text=f"Correct answer: {ca_text}", wraplength=760, justify="left")
                ca_lbl.pack(anchor="w")
                status = "Correct" if correct else "Incorrect"
                color = "#0a7f20" if correct else "#a01919"
                st_lbl = ttk.Label(block, text=status, foreground=color)
                st_lbl.pack(anchor="w", pady=(4, 0))
                if getattr(q, "explanation", None):
                    exp = ttk.Label(block, text=f"Explanation: {q.explanation}", wraplength=760, justify="left")
                    exp.pack(anchor="w", pady=(4, 0))
        else:
            info = ttk.Label(
                self.scrollable_frame,
                text="Answer review is disabled. Enable it on the start screen.",
                foreground="#555"
            )
            info.pack(anchor="w", padx=8, pady=8)
    def retake(self):
        # Retake with same config (selected bank, question count, shuffle on, and show_answers from last session)
        session = self.controller.current_session
        if session is None:
            self.controller.restart()
            return
        bank_name = self.controller.selected_bank_name or ""
        count = len(session.questions)
        # Use the same show_answers preference
        show_answers = session.show_answers
        # Shuffle again for variety
        self.controller.start_quiz(bank_name, count, shuffle=True, show_answers=show_answers)
if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()