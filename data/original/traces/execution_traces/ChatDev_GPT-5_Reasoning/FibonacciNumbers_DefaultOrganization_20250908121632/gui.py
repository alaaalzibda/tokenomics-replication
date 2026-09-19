'''
Graphical User Interface for the Fibonacci Generator.
This module defines the FibonacciApp class which builds a user-friendly
Tkinter GUI to generate Fibonacci numbers up to a given limit. It
provides input validation, sequence display, copying to clipboard,
and saving results to a file.
'''
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List
from fibonacci import (
    generate_fibonacci_up_to,
    parse_limit,
    format_sequence,
    sequence_stats,
)
class FibonacciApp:
    """Tkinter GUI application for generating Fibonacci numbers."""
    def __init__(self, master: tk.Tk) -> None:
        """Initialize the GUI components and layout."""
        self.master = master
        self.master.title("Fibonacci Generator")
        self.master.geometry("640x420")
        self.master.minsize(520, 360)
        # Configure grid for responsiveness
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)
        # Styling
        style = ttk.Style(self.master)
        try:
            # Use a platform-appropriate theme if available
            style.theme_use("clam")
        except tk.TclError:
            pass
        # Top frame for input
        top_frame = ttk.Frame(self.master, padding=(10, 10, 10, 5))
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(1, weight=1)
        lbl = ttk.Label(top_frame, text="Generate Fibonacci numbers up to:")
        lbl.grid(row=0, column=0, padx=(0, 8), pady=4, sticky="w")
        self.var_limit = tk.StringVar()
        self.entry_limit = ttk.Entry(top_frame, textvariable=self.var_limit)
        self.entry_limit.grid(row=0, column=1, padx=(0, 8), pady=4, sticky="ew")
        self.entry_limit.insert(0, "1000")  # sensible default
        self.entry_limit.focus()
        btn_generate = ttk.Button(top_frame, text="Generate", command=self.on_generate)
        btn_generate.grid(row=0, column=2, padx=(0, 0), pady=4)
        # Middle frame for output
        mid_frame = ttk.Frame(self.master, padding=(10, 5, 10, 5))
        mid_frame.grid(row=1, column=0, sticky="nsew")
        mid_frame.rowconfigure(0, weight=1)
        mid_frame.columnconfigure(0, weight=1)
        self.listbox = tk.Listbox(
            mid_frame,
            font=("Courier New", 11),
            activestyle="none",
            exportselection=False,
        )
        yscroll = ttk.Scrollbar(mid_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=yscroll.set)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        # Bottom frame for actions and status
        bottom_frame = ttk.Frame(self.master, padding=(10, 5, 10, 10))
        bottom_frame.grid(row=2, column=0, sticky="ew")
        bottom_frame.columnconfigure(0, weight=1)
        btns_frame = ttk.Frame(bottom_frame)
        btns_frame.grid(row=0, column=0, sticky="w")
        btn_clear = ttk.Button(btns_frame, text="Clear", command=self.on_clear)
        btn_clear.grid(row=0, column=0, padx=(0, 8))
        btn_copy = ttk.Button(btns_frame, text="Copy", command=self.on_copy)
        btn_copy.grid(row=0, column=1, padx=(0, 8))
        btn_save = ttk.Button(btns_frame, text="Save...", command=self.on_save)
        btn_save.grid(row=0, column=2, padx=(0, 8))
        self.status_var = tk.StringVar(value="Ready.")
        self.status_label = ttk.Label(
            bottom_frame, textvariable=self.status_var, foreground="#444"
        )
        self.status_label.grid(row=1, column=0, sticky="w", pady=(6, 0))
        # Keyboard bindings
        self.master.bind("<Return>", lambda e: self.on_generate())
        self.master.bind("<Control-s>", lambda e: self.on_save())
        # Bind Ctrl+C only when the listbox has focus to avoid overriding Entry copy
        self.listbox.bind("<Control-c>", self._on_copy_hotkey)
    def on_generate(self) -> None:
        """Handle Generate button click: validate input and compute sequence."""
        text = self.var_limit.get()
        try:
            limit = parse_limit(text)
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e), parent=self.master)
            self._set_status(str(e), error=True)
            return
        numbers = generate_fibonacci_up_to(limit)
        self._update_output(numbers)
        stats = sequence_stats(numbers)
        self._set_status(
            f"Generated {stats['count']} numbers up to {limit}. "
            f"Max={stats['max']}, Sum={stats['sum']}."
        )
    def on_clear(self) -> None:
        """Clear input and output widgets."""
        self.var_limit.set("")
        self.listbox.delete(0, tk.END)
        self._set_status("Cleared. Enter a non-negative integer and press Generate.")
    def on_copy(self) -> None:
        """Copy the generated sequence to the clipboard."""
        items = self.listbox.get(0, tk.END)
        if not items:
            self._set_status("Nothing to copy. Generate a sequence first.", error=True)
            return
        joined = format_sequence([int(x) for x in items])
        try:
            self.master.clipboard_clear()
            self.master.clipboard_append(joined)
            self._set_status("Sequence copied to clipboard.")
        except tk.TclError:
            self._set_status("Failed to access clipboard.", error=True)
    def on_save(self) -> None:
        """Save the generated sequence to a text file."""
        items = self.listbox.get(0, tk.END)
        if not items:
            self._set_status("Nothing to save. Generate a sequence first.", error=True)
            return
        # Determine limit from input (best effort)
        limit_text = self.var_limit.get().strip()
        try:
            limit_val = parse_limit(limit_text)
        except ValueError:
            limit_val = None
        default_name = "fibonacci.txt"
        filepath = filedialog.asksaveasfilename(
            parent=self.master,
            title="Save Fibonacci Sequence",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not filepath:
            return
        seq = [int(x) for x in items]
        content_lines = []
        if limit_val is not None:
            content_lines.append(f"Fibonacci numbers up to {limit_val}:")
        else:
            content_lines.append("Fibonacci numbers:")
        content_lines.append(format_sequence(seq))
        content = "\n".join(content_lines)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            self._set_status(f"Saved to {filepath}.")
        except OSError as e:
            messagebox.showerror("Save Error", str(e), parent=self.master)
            self._set_status("Failed to save file.", error=True)
    def _update_output(self, numbers: List[int]) -> None:
        """Render the Fibonacci numbers in the listbox."""
        self.listbox.delete(0, tk.END)
        for num in numbers:
            self.listbox.insert(tk.END, str(num))
    def _set_status(self, text: str, error: bool = False) -> None:
        """Update the status label with optional error styling."""
        self.status_var.set(text)
        self.status_label.configure(foreground=("#b00020" if error else "#444"))
    def _on_copy_hotkey(self, event) -> str:
        """Handle Ctrl+C when the listbox has focus."""
        self.on_copy()
        return "break"