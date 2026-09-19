'''
Tkinter GUI for the interactive storytelling game: start screen, main game screen, narrative view,
choices, and sidebars for inventory, relationships, and variables. Supports saving/loading.
'''
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional
from engine import StoryEngine, Choice
import story_data
import storage
class StartFrame(ttk.Frame):
    """
    Simple start menu with New/Load options.
    """
    def __init__(self, master, on_new_game, on_load_game):
        super().__init__(master, padding=20)
        title = ttk.Label(self, text="Castle of Choices", font=("Segoe UI", 20, "bold"))
        subtitle = ttk.Label(self, text="An interactive storytelling game", font=("Segoe UI", 12))
        btn_new = ttk.Button(self, text="New Game", command=on_new_game)
        btn_load = ttk.Button(self, text="Load Game", command=on_load_game)
        title.grid(row=0, column=0, pady=(0, 8), sticky="w")
        subtitle.grid(row=1, column=0, pady=(0, 20), sticky="w")
        btn_new.grid(row=2, column=0, sticky="ew")
        btn_load.grid(row=3, column=0, pady=(8, 0), sticky="ew")
        self.columnconfigure(0, weight=1)
class GameFrame(ttk.Frame):
    """
    Main game UI: narrative text, choices, sidebar stats, and control buttons.
    """
    def __init__(self, master, engine: StoryEngine, on_restart, on_save, on_load):
        super().__init__(master, padding=10)
        self.engine = engine
        self.on_restart = on_restart
        self.on_save = on_save
        self.on_load = on_load
        # Layout: left content (narrative + choices), right sidebar
        self.columnconfigure(0, weight=3, uniform="cols")
        self.columnconfigure(1, weight=1, uniform="cols")
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        # Narrative
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        lbl_story = ttk.Label(left_frame, text="Story", font=("Segoe UI", 12, "bold"))
        lbl_story.pack(anchor="w")
        self.text = tk.Text(left_frame, wrap="word", height=18, state="disabled", bg="#fafafa")
        self.text.pack(fill="both", expand=True, pady=(0, 8))
        lbl_choices = ttk.Label(left_frame, text="Choices", font=("Segoe UI", 12, "bold"))
        lbl_choices.pack(anchor="w")
        self.choices_frame = ttk.Frame(left_frame)
        self.choices_frame.pack(fill="x", expand=False)
        # Sidebar
        sidebar = ttk.Frame(self)
        sidebar.grid(row=0, column=1, sticky="nsew")
        lbl_inv = ttk.Label(sidebar, text="Items", font=("Segoe UI", 11, "bold"))
        lbl_inv.pack(anchor="w")
        self.lst_items = tk.Listbox(sidebar, height=7)
        self.lst_items.pack(fill="x", pady=(0, 8))
        lbl_rel = ttk.Label(sidebar, text="Relationships", font=("Segoe UI", 11, "bold"))
        lbl_rel.pack(anchor="w")
        self.lst_relationships = tk.Listbox(sidebar, height=7)
        self.lst_relationships.pack(fill="x", pady=(0, 8))
        lbl_vars = ttk.Label(sidebar, text="Variables", font=("Segoe UI", 11, "bold"))
        lbl_vars.pack(anchor="w")
        self.lst_vars = tk.Listbox(sidebar, height=6)
        self.lst_vars.pack(fill="x")
        # Controls
        controls = ttk.Frame(self)
        controls.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        controls.columnconfigure(0, weight=1)
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(2, weight=1)
        btn_save = ttk.Button(controls, text="Save", command=self.on_save)
        btn_load = ttk.Button(controls, text="Load", command=self.on_load)
        btn_restart = ttk.Button(controls, text="Restart", command=self.on_restart)
        btn_save.grid(row=0, column=0, sticky="ew")
        btn_load.grid(row=0, column=1, sticky="ew", padx=10)
        btn_restart.grid(row=0, column=2, sticky="ew")
        self.update_ui()
    def set_story_text(self, text: str):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", text)
        self.text.configure(state="disabled")
    def build_choices(self, choices: List[Choice]):
        # Clear previous buttons
        for child in self.choices_frame.winfo_children():
            child.destroy()
        if not choices:
            # End node
            lbl = ttk.Label(self.choices_frame, text="The story has reached an ending.", foreground="#333")
            lbl.pack(anchor="w", pady=(0, 6))
            btn = ttk.Button(self.choices_frame, text="Play Again", command=self.on_restart)
            btn.pack(anchor="w")
            return
        for choice in choices:
            btn = ttk.Button(
                self.choices_frame,
                text=choice.text,
                command=lambda c=choice: self.on_choice_clicked(c)
            )
            btn.pack(anchor="w", pady=4)
    def on_choice_clicked(self, choice: Choice):
        ok = self.engine.choose(choice)
        if not ok:
            messagebox.showerror("Choice Error", "That choice is no longer valid or the target node is missing.")
        self.update_ui()
    def update_sidebar(self):
        # Items
        self.lst_items.delete(0, "end")
        for item in sorted(list(self.engine.state.items)):
            self.lst_items.insert("end", f"- {item}")
        # Relationships
        self.lst_relationships.delete(0, "end")
        for name, score in sorted(self.engine.state.relationships.items()):
            self.lst_relationships.insert("end", f"{name}: {score}")
        # Variables
        self.lst_vars.delete(0, "end")
        for name, value in sorted(self.engine.state.variables.items()):
            self.lst_vars.insert("end", f"{name}: {value}")
    def update_ui(self):
        node = self.engine.get_current_node()
        self.set_story_text(node.text)
        choices = self.engine.get_available_choices()
        self.build_choices(choices)
        self.update_sidebar()
class StoryApp(tk.Tk):
    """
    Tk root application that coordinates frames and persistence actions.
    """
    def __init__(self):
        super().__init__()
        self.title("Castle of Choices")
        self.minsize(800, 600)
        # Global style tweaks
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        self.engine = StoryEngine(story_data.STORY)
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.start_frame = StartFrame(
            self.container,
            on_new_game=self.new_game,
            on_load_game=self.load_game_dialog,
        )
        self.start_frame.pack(fill="both", expand=True)
        self.game_frame: Optional["GameFrame"] = None
        # Keyboard shortcuts
        self.bind("<Control-s>", lambda e: self.save_game_dialog())
        self.bind("<Control-o>", lambda e: self.load_game_dialog())
        self.bind("<F5>", lambda e: self.restart_game())
    def switch_to_game(self):
        if self.start_frame:
            self.start_frame.pack_forget()
        if not self.game_frame:
            self.game_frame = GameFrame(
                self.container,
                engine=self.engine,
                on_restart=self.restart_game,
                on_save=self.save_game_dialog,
                on_load=self.load_game_dialog
            )
            self.game_frame.pack(fill="both", expand=True)
        else:
            self.game_frame.pack(fill="both", expand=True)
            self.game_frame.update_ui()
    def new_game(self):
        self.engine.reset()
        self.switch_to_game()
    def restart_game(self):
        if messagebox.askyesno("Restart", "Start a new game? Current progress will be lost."):
            self.engine.reset()
            if self.game_frame:
                self.game_frame.update_ui()
            else:
                self.switch_to_game()
    def save_game_dialog(self):
        storage.save_game_dialog(self.engine.to_dict)
    def load_game_dialog(self):
        def loader(data):
            self.engine.from_dict(data)
            if self.game_frame:
                self.game_frame.update_ui()
        ok = storage.load_game_dialog(loader)
        if ok:
            self.switch_to_game()