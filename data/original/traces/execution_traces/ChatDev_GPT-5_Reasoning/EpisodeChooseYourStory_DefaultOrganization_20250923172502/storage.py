'''
Utility functions to save and load game sessions to JSON files. The load dialog returns a boolean
indicating whether a load actually occurred (True) or was cancelled/failed (False).
'''
import json
from typing import Any, Dict, Callable
from tkinter import filedialog, messagebox
import os
def save_game_dialog(data_provider_callable: Callable[[], Dict[str, Any]]) -> None:
    """
    Open a Save As dialog and save the session JSON provided by data_provider_callable().
    """
    file_path = filedialog.asksaveasfilename(
        title="Save Game",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if not file_path:
        return
    try:
        data = data_provider_callable()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo("Saved", f"Game saved to:\n{os.path.basename(file_path)}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save game:\n{e}")
def load_game_dialog(loader_callable: Callable[[Dict[str, Any]], None]) -> bool:
    """
    Open an Open dialog, read JSON, and pass it to loader_callable(data).
    Returns:
        True if a game was successfully loaded, False if the user cancelled or an error occurred.
    """
    file_path = filedialog.askopenfilename(
        title="Load Game",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if not file_path:
        return False
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
        loader_callable(data)
        messagebox.showinfo("Loaded", f"Game loaded from:\n{os.path.basename(file_path)}")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load game:\n{e}")
        return False