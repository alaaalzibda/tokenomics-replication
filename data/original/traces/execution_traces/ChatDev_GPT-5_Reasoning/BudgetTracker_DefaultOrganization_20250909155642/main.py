'''
Main entry point for the Budget Tracker application.
Initializes storage (Excel), model, and GUI application.
'''
import os
import sys
import tkinter as tk
from tkinter import messagebox
from ui import BudgetApp
def main():
    data_file = os.path.join(os.path.abspath(os.getcwd()), "budget_data.xlsx")
    try:
        # Lazy import so we can catch ImportError (e.g., missing openpyxl) gracefully.
        from storage import ExcelStorage
        storage = ExcelStorage(data_file)
        model = storage.load_model()
    except ImportError as e:
        # Likely openpyxl missing
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Missing dependency",
            f"Required package is missing:\n\n{e}\n\nPlease install it, e.g.:\n    pip install openpyxl",
        )
        sys.exit(1)
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to initialize storage:\n{e}")
        sys.exit(1)
    app = BudgetApp(model=model, storage=storage)
    app.mainloop()
if __name__ == "__main__":
    main()