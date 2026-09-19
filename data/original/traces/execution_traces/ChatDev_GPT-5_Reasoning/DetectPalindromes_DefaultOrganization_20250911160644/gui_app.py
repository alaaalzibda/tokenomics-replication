'''
Tkinter-based GUI for the Palindrome Detector application.
Provides controls to open files, configure detection options, analyze text,
view results, highlight matches in a preview, and export results to CSV.
'''
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict
from palindrome_detector import (
    DetectionOptions,
    detect_palindromes,
    PalindromeMatch,
)
from file_utils import read_text_file
from exporter import export_results_to_csv
class PalindromeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self._build_vars()
        self._build_menu()
        self._build_layout()
        self._connect_events()
        self.loaded_text: str = ""
        self.results = []
        self.tree_item_to_result: Dict[str, PalindromeMatch] = {}
    def _build_vars(self):
        # Options variables
        self.var_words = tk.BooleanVar(value=True)
        self.var_sentences = tk.BooleanVar(value=True)
        self.var_lines = tk.BooleanVar(value=True)
        self.var_ignore_case = tk.BooleanVar(value=True)
        self.var_ignore_non_alnum = tk.BooleanVar(value=True)
        self.var_min_length = tk.IntVar(value=3)
        # Status
        self.var_status = tk.StringVar(value="Open a text file to begin.")
    def _build_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open...", command=self.on_open_file)
        file_menu.add_command(label="Analyze", command=self.on_analyze)
        file_menu.add_separator()
        file_menu.add_command(label="Export Results...", command=self.on_export)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self.on_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)
    def _build_layout(self):
        # Top controls frame
        controls = ttk.LabelFrame(self, text="Detection Options")
        controls.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)
        # Options group
        check_frame = ttk.Frame(controls)
        check_frame.pack(side=tk.LEFT, padx=6, pady=6)
        ttk.Checkbutton(check_frame, text="Words", variable=self.var_words).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(check_frame, text="Sentences", variable=self.var_sentences).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(check_frame, text="Lines", variable=self.var_lines).grid(row=2, column=0, sticky="w")
        opt_frame = ttk.Frame(controls)
        opt_frame.pack(side=tk.LEFT, padx=20, pady=6)
        ttk.Checkbutton(opt_frame, text="Ignore case", variable=self.var_ignore_case).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(opt_frame, text="Ignore non-alphanumeric", variable=self.var_ignore_non_alnum).grid(row=1, column=0, sticky="w")
        minlen_frame = ttk.Frame(controls)
        minlen_frame.pack(side=tk.LEFT, padx=20, pady=6)
        ttk.Label(minlen_frame, text="Minimum length:").grid(row=0, column=0, sticky="w")
        self.spin_min_length = ttk.Spinbox(minlen_frame, from_=1, to=100, textvariable=self.var_min_length, width=5)
        self.spin_min_length.grid(row=0, column=1, sticky="w", padx=5)
        action_frame = ttk.Frame(controls)
        action_frame.pack(side=tk.RIGHT, padx=6, pady=6)
        self.btn_open = ttk.Button(action_frame, text="Open...", command=self.on_open_file)
        self.btn_open.grid(row=0, column=0, padx=4)
        self.btn_analyze = ttk.Button(action_frame, text="Analyze", command=self.on_analyze)
        self.btn_analyze.grid(row=0, column=1, padx=4)
        self.btn_export = ttk.Button(action_frame, text="Export Results...", command=self.on_export, state=tk.DISABLED)
        self.btn_export.grid(row=0, column=2, padx=4)
        # Middle: Results treeview
        results_frame = ttk.LabelFrame(self, text="Results")
        results_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=(0, 6))
        columns = ("category", "content", "length", "line", "start", "end")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("category", text="Category")
        self.tree.heading("content", text="Content")
        self.tree.heading("length", text="Length")
        self.tree.heading("line", text="Line")
        self.tree.heading("start", text="Start")
        self.tree.heading("end", text="End")
        self.tree.column("category", width=90, anchor="w")
        self.tree.column("content", width=500, anchor="w")
        self.tree.column("length", width=60, anchor="center")
        self.tree.column("line", width=60, anchor="center")
        self.tree.column("start", width=60, anchor="center")
        self.tree.column("end", width=60, anchor="center")
        tree_scroll_y = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        # Bottom: Text preview with scrollbar
        preview_frame = ttk.LabelFrame(self, text="File Preview")
        preview_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        self.text_preview = tk.Text(preview_frame, wrap="none", undo=False)
        self.text_preview.config(state=tk.DISABLED)
        # Highlight tag
        self.text_preview.tag_configure("highlight", background="#fffd86")
        self.text_preview.tag_configure("linehl", background="#e8f4ff")
        yscroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.text_preview.yview)
        xscroll = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.text_preview.xview)
        self.text_preview.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.text_preview.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        # Status bar
        status_bar = ttk.Frame(self)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.lbl_status = ttk.Label(status_bar, textvariable=self.var_status, anchor="w")
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=4)
    def _connect_events(self):
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
    def on_about(self):
        messagebox.showinfo(
            "About",
            "Palindrome Detector\n\n"
            "Detect palindromic words, sentences, and lines in text files.\n"
            "Options allow ignoring case and non-alphanumeric characters.\n\n"
            "Built with tkinter."
        )
    def on_open_file(self):
        path = filedialog.askopenfilename(
            title="Open Text File",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        try:
            txt = read_text_file(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")
            return
        self.loaded_text = txt
        self._set_preview_text(self.loaded_text)
        self._clear_results()
        self.var_status.set(f"Loaded: {path}")
        self.btn_export.configure(state=tk.DISABLED)
    def _set_preview_text(self, text: str):
        self.text_preview.config(state=tk.NORMAL)
        self.text_preview.delete("1.0", tk.END)
        self.text_preview.insert("1.0", text)
        self.text_preview.config(state=tk.DISABLED)
    def _clear_results(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self.tree_item_to_result.clear()
        self.results = []
        self._clear_highlight()
    def _clear_highlight(self):
        self.text_preview.config(state=tk.NORMAL)
        self.text_preview.tag_remove("highlight", "1.0", tk.END)
        self.text_preview.tag_remove("linehl", "1.0", tk.END)
        self.text_preview.config(state=tk.DISABLED)
    def _collect_options(self) -> DetectionOptions:
        min_len = self.var_min_length.get()
        if min_len < 1:
            min_len = 1
            self.var_min_length.set(min_len)
        return DetectionOptions(
            check_words=self.var_words.get(),
            check_sentences=self.var_sentences.get(),
            check_lines=self.var_lines.get(),
            min_length=min_len,
            ignore_case=self.var_ignore_case.get(),
            ignore_non_alnum=self.var_ignore_non_alnum.get(),
        )
    def on_analyze(self):
        if not self.loaded_text:
            messagebox.showinfo("Info", "Please open a text file first.")
            return
        opts = self._collect_options()
        try:
            results = detect_palindromes(self.loaded_text, opts)
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed:\n{e}")
            return
        self._clear_results()
        self.results = results
        count = 0
        for res in results:
            display_text = res.text.replace("\n", "\\n")
            values = (res.category, display_text, res.length, res.line_no, res.start_pos, res.end_pos)
            iid = self.tree.insert("", "end", values=values)
            self.tree_item_to_result[iid] = res
            count += 1
        self.var_status.set(f"Found {count} palindrome(s).")
        self.btn_export.configure(state=tk.NORMAL if count > 0 else tk.DISABLED)
    def on_tree_select(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return
        iid = selection[0]
        res = self.tree_item_to_result.get(iid)
        if not res:
            return
        self._clear_highlight()
        self.text_preview.config(state=tk.NORMAL)
        try:
            if res.category == "line":
                start_index = f"{res.line_no}.0"
                end_index = f"{res.line_no}.end"
                self.text_preview.tag_add("linehl", start_index, end_index)
                self.text_preview.see(start_index)
            else:
                start_index = f"{res.line_no}.{res.start_pos}"
                end_index = f"{res.line_no}.{res.end_pos}"
                self.text_preview.tag_add("highlight", start_index, end_index)
                self.text_preview.see(start_index)
        finally:
            self.text_preview.config(state=tk.DISABLED)
    def on_export(self):
        if not self.results:
            messagebox.showinfo("Info", "No results to export.")
            return
        path = filedialog.asksaveasfilename(
            title="Export Results to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            export_results_to_csv(path, self.results)
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{e}")
            return
        messagebox.showinfo("Export", f"Results exported to:\n{path}")