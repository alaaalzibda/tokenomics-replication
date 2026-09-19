'''
Tkinter GUI for the Budget Tracker application.
Includes: transaction form, filters, table view, summary and savings goal progress.
'''
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from typing import Optional, List
from models import BudgetModel, Transaction
from utils import format_currency, parse_float, parse_date, date_to_str
class BudgetApp(tk.Tk):
    def __init__(self, model: BudgetModel, storage: 'ExcelStorage'):
        super().__init__()
        self.title("Budget Tracker - Expenses and Savings")
        self.geometry("1000x650")
        self.minsize(900, 600)
        self.model = model
        self.storage = storage
        # State for filters and edit
        self._edit_tx_id: Optional[int] = None
        self._filter_year = tk.StringVar(value="All")
        self._filter_month = tk.StringVar(value="All")
        self._filter_type = tk.StringVar(value="All")
        self._filter_category = tk.StringVar(value="All")
        self._filter_search = tk.StringVar(value="")
        # Summary variables
        self.var_income = tk.StringVar(value="$0.00")
        self.var_expenses = tk.StringVar(value="$0.00")
        self.var_net = tk.StringVar(value="$0.00")
        self.var_goal = tk.StringVar(value="$0.00")
        self.var_progress_text = tk.StringVar(value="0% of goal")
        self._build_ui()
        self._refresh_summary()
        self._refresh_filters()
        self._refresh_table()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    def _build_ui(self):
        self._build_summary_frame()
        self._build_form_frame()
        self._build_filter_frame()
        self._build_table_frame()
        self._build_bottom_frame()
    def _build_summary_frame(self):
        frame = ttk.Frame(self, padding=8)
        frame.pack(fill="x")
        ttk.Label(frame, text="Income:", width=10).grid(row=0, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.var_income, foreground="#1a7f37", width=18).grid(
            row=0, column=1, sticky="w"
        )
        ttk.Label(frame, text="Expenses:", width=10).grid(row=0, column=2, sticky="w")
        ttk.Label(frame, textvariable=self.var_expenses, foreground="#b91c1c", width=18).grid(
            row=0, column=3, sticky="w"
        )
        ttk.Label(frame, text="Net:", width=10).grid(row=0, column=4, sticky="w")
        ttk.Label(frame, textvariable=self.var_net, width=18).grid(row=0, column=5, sticky="w")
        # Savings goal
        ttk.Label(frame, text="Savings goal:", width=14).grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.entry_goal = ttk.Entry(frame)
        self.entry_goal.grid(row=1, column=1, sticky="we", pady=(6, 0))
        self.entry_goal.insert(0, f"{self.model.savings_goal:.2f}")
        btn_set_goal = ttk.Button(frame, text="Set goal", command=self._on_set_goal)
        btn_set_goal.grid(row=1, column=2, padx=4, pady=(6, 0))
        self.progress = ttk.Progressbar(frame, mode="determinate")
        self.progress.grid(row=1, column=3, columnspan=2, sticky="we", padx=4, pady=(6, 0))
        ttk.Label(frame, textvariable=self.var_progress_text).grid(row=1, column=5, sticky="w", pady=(6, 0))
        for i in range(6):
            frame.columnconfigure(i, weight=1)
    def _build_form_frame(self):
        lf = ttk.LabelFrame(self, text="Add / Edit Transaction", padding=8)
        lf.pack(fill="x", padx=8, pady=4)
        # Date
        ttk.Label(lf, text="Date (YYYY-MM-DD)").grid(row=0, column=0, sticky="w")
        self.entry_date = ttk.Entry(lf, width=16)
        self.entry_date.grid(row=1, column=0, sticky="w", padx=(0, 8))
        self.entry_date.insert(0, date_to_str(date.today()))
        # Type
        ttk.Label(lf, text="Type").grid(row=0, column=1, sticky="w")
        self.type_var = tk.StringVar(value="Expense")
        frm_type = ttk.Frame(lf)
        frm_type.grid(row=1, column=1, sticky="w", padx=(0, 8))
        ttk.Radiobutton(frm_type, text="Expense", value="Expense", variable=self.type_var).pack(side="left", padx=(0, 8))
        ttk.Radiobutton(frm_type, text="Income", value="Income", variable=self.type_var).pack(side="left")
        # Category
        ttk.Label(lf, text="Category").grid(row=0, column=2, sticky="w")
        self.combo_category = ttk.Combobox(lf, values=self.model.categories, state="readonly", width=24)
        self.combo_category.grid(row=1, column=2, sticky="we", padx=(0, 8))
        self.combo_category.set(self.model.categories[0] if self.model.categories else "General")
        self.entry_new_category = ttk.Entry(lf, width=18)
        self.entry_new_category.grid(row=1, column=3, sticky="we")
        self.entry_new_category.insert(0, "")
        btn_add_cat = ttk.Button(lf, text="Add category", command=self._on_add_category)
        btn_add_cat.grid(row=1, column=4, padx=(6, 0))
        # Description
        ttk.Label(lf, text="Description").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.entry_description = ttk.Entry(lf, width=40)
        self.entry_description.grid(row=3, column=0, columnspan=2, sticky="we", padx=(0, 8))
        # Amount
        ttk.Label(lf, text="Amount").grid(row=2, column=2, sticky="w", pady=(8, 0))
        self.entry_amount = ttk.Entry(lf, width=18)
        self.entry_amount.grid(row=3, column=2, sticky="w", padx=(0, 8))
        self.btn_submit = ttk.Button(lf, text="Add", command=self._on_submit)
        self.btn_submit.grid(row=3, column=4, sticky="e")
        for i in range(5):
            lf.columnconfigure(i, weight=1)
    def _build_filter_frame(self):
        lf = ttk.LabelFrame(self, text="Filters", padding=8)
        lf.pack(fill="x", padx=8, pady=(0, 4))
        years = ["All"] + sorted({str(t.date.year) for t in self.model.transactions})
        months = ["All"] + [str(m) for m in range(1, 13)]
        types = ["All", "Income", "Expense"]
        categories = ["All"] + list(self.model.categories)
        ttk.Label(lf, text="Year").grid(row=0, column=0, sticky="w")
        self.combo_year = ttk.Combobox(lf, values=years, textvariable=self._filter_year, state="readonly", width=10)
        self.combo_year.grid(row=1, column=0, sticky="w", padx=(0, 6))
        ttk.Label(lf, text="Month").grid(row=0, column=1, sticky="w")
        self.combo_month = ttk.Combobox(lf, values=months, textvariable=self._filter_month, state="readonly", width=10)
        self.combo_month.grid(row=1, column=1, sticky="w", padx=(0, 6))
        ttk.Label(lf, text="Type").grid(row=0, column=2, sticky="w")
        self.combo_type = ttk.Combobox(lf, values=types, textvariable=self._filter_type, state="readonly", width=12)
        self.combo_type.grid(row=1, column=2, sticky="w", padx=(0, 6))
        ttk.Label(lf, text="Category").grid(row=0, column=3, sticky="w")
        self.combo_filter_category = ttk.Combobox(
            lf, values=categories, textvariable=self._filter_category, state="readonly", width=22
        )
        self.combo_filter_category.grid(row=1, column=3, sticky="w", padx=(0, 6))
        ttk.Label(lf, text="Search").grid(row=0, column=4, sticky="w")
        self.entry_search = ttk.Entry(lf, textvariable=self._filter_search, width=24)
        self.entry_search.grid(row=1, column=4, sticky="we", padx=(0, 6))
        btn_apply = ttk.Button(lf, text="Apply", command=self._on_apply_filters)
        btn_apply.grid(row=1, column=5, sticky="w", padx=(0, 6))
        btn_reset = ttk.Button(lf, text="Reset", command=self._on_reset_filters)
        btn_reset.grid(row=1, column=6, sticky="w", padx=(0, 6))
        for i in range(7):
            lf.columnconfigure(i, weight=1)
    def _build_table_frame(self):
        frame = ttk.Frame(self, padding=8)
        frame.pack(fill="both", expand=True)
        columns = ("ID", "Date", "Type", "Category", "Description", "Amount")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("ID", width=60, anchor="e")
        self.tree.column("Date", width=110, anchor="center")
        self.tree.column("Type", width=90, anchor="center")
        self.tree.column("Category", width=160, anchor="w")
        self.tree.column("Description", width=340, anchor="w")
        self.tree.column("Amount", width=120, anchor="e")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        # Fixed: use yscrollcommand/xscrollcommand so Treeview updates scrollbar positions properly
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="we")
        # Buttons under table
        btns = ttk.Frame(frame)
        btns.grid(row=2, column=0, columnspan=2, sticky="we", pady=(6, 0))
        ttk.Button(btns, text="Edit selected", command=self._on_edit_selected).pack(side="left")
        ttk.Button(btns, text="Delete selected", command=self._on_delete_selected).pack(side="left", padx=(6, 0))
        ttk.Button(btns, text="Export copy...", command=self._on_export_copy).pack(side="left", padx=(6, 0))
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
    def _build_bottom_frame(self):
        # Placeholder for future extensions, currently not necessary
        bottom = ttk.Frame(self, padding=4)
        bottom.pack(fill="x")
    def _refresh_summary(self):
        totals = self.model.totals()
        self.var_income.set(format_currency(totals["income"]))
        self.var_expenses.set(format_currency(-totals["expenses"]))  # show minus visually
        self.var_net.set(format_currency(totals["net"]))
        goal = self.model.savings_goal
        self.var_goal.set(format_currency(goal))
        net = totals["net"]
        progress = 0
        if goal > 0:
            progress = max(0.0, min(100.0, (max(0.0, net) / goal) * 100.0))
        self.progress["value"] = progress
        self.var_progress_text.set(f"{progress:.0f}% of goal")
    def _refresh_filters(self):
        # Refresh filter dropdowns with current data
        years = ["All"] + sorted({str(t.date.year) for t in self.model.transactions})
        months = ["All"] + [str(m) for m in range(1, 13)]
        categories = ["All"] + list(self.model.categories)
        self.combo_year["values"] = years
        if self._filter_year.get() not in years:
            self._filter_year.set("All")
        self.combo_month["values"] = months
        if self._filter_month.get() not in months:
            self._filter_month.set("All")
        self.combo_filter_category["values"] = categories
        if self._filter_category.get() not in categories:
            self._filter_category.set("All")
        # category in form
        self.combo_category["values"] = list(self.model.categories)
        if self.combo_category.get() not in self.model.categories:
            if self.model.categories:
                self.combo_category.set(self.model.categories[0])
    def _refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        year = self._to_int_or_none(self._filter_year.get())
        month = self._to_int_or_none(self._filter_month.get())
        ttype = self._filter_type.get() if self._filter_type.get() != "All" else None
        cat = self._filter_category.get() if self._filter_category.get() != "All" else None
        search = self._filter_search.get().strip() or None
        records = self.model.filtered_transactions(year=year, month=month, ttype=ttype, category=cat, search=search)
        for t in records:
            amt = t.amount if t.ttype == "Income" else -t.amount
            self.tree.insert(
                "",
                "end",
                iid=str(t.id),
                values=(t.id, date_to_str(t.date), t.ttype, t.category, t.description, format_currency(amt)),
            )
    @staticmethod
    def _to_int_or_none(value: str):
        try:
            return int(value)
        except Exception:
            return None
    def _on_set_goal(self):
        goal = parse_float(self.entry_goal.get(), default=0.0)
        if goal < 0:
            goal = 0.0
        self.model.set_savings_goal(goal)
        self._refresh_summary()
        try:
            self.storage.save_model(self.model)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save goal to file:\n{e}")
    def _on_add_category(self):
        name = self.entry_new_category.get().strip()
        if not name:
            messagebox.showinfo("Info", "Please enter a category name.")
            return
        if name in self.model.categories:
            messagebox.showinfo("Info", f"Category '{name}' already exists.")
            return
        self.model.ensure_category(name)
        self.entry_new_category.delete(0, tk.END)
        self._refresh_filters()
        try:
            self.storage.save_model(self.model)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save categories:\n{e}")
    def _on_submit(self):
        # Validate inputs
        tdate = parse_date(self.entry_date.get())
        ttype = self.type_var.get()
        category = self.combo_category.get().strip() or "General"
        desc = self.entry_description.get().strip()
        amount = parse_float(self.entry_amount.get(), default=None)
        if amount is None or amount <= 0:
            messagebox.showwarning("Validation", "Please enter a positive amount.")
            return
        if self._edit_tx_id is None:
            # Add mode
            self.model.add_transaction(tdate, ttype, category, desc, amount)
        else:
            # Edit mode
            ok = self.model.edit_transaction(self._edit_tx_id, tdate, ttype, category, desc, amount)
            if not ok:
                messagebox.showerror("Error", "Failed to update transaction. It may have been removed.")
            self._edit_tx_id = None
            self.btn_submit.configure(text="Add")
        self._clear_form()
        self._refresh_filters()
        self._refresh_table()
        self._refresh_summary()
        try:
            self.storage.save_model(self.model)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save to file:\n{e}")
    def _on_edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Please select a transaction to edit.")
            return
        iid = sel[0]
        tx = self.model.get_transaction(int(iid))
        if not tx:
            messagebox.showerror("Error", "Transaction not found.")
            return
        self._edit_tx_id = tx.id
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, date_to_str(tx.date))
        self.type_var.set(tx.ttype)
        if tx.category in self.model.categories:
            self.combo_category.set(tx.category)
        else:
            self.combo_category.set(self.model.categories[0] if self.model.categories else "General")
        self.entry_description.delete(0, tk.END)
        self.entry_description.insert(0, tx.description)
        self.entry_amount.delete(0, tk.END)
        self.entry_amount.insert(0, f"{tx.amount:.2f}")
        self.btn_submit.configure(text="Update")
    def _on_delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Please select a transaction to delete.")
            return
        iid = sel[0]
        tx = self.model.get_transaction(int(iid))
        if not tx:
            messagebox.showerror("Error", "Transaction not found.")
            return
        if not messagebox.askyesno("Confirm", f"Delete transaction {tx.id} on {date_to_str(tx.date)}?"):
            return
        ok = self.model.delete_transaction(tx.id)
        if not ok:
            messagebox.showerror("Error", "Failed to delete transaction.")
            return
        self._refresh_table()
        self._refresh_summary()
        try:
            self.storage.save_model(self.model)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save to file:\n{e}")
    def _on_apply_filters(self):
        self._refresh_table()
    def _on_reset_filters(self):
        self._filter_year.set("All")
        self._filter_month.set("All")
        self._filter_type.set("All")
        self._filter_category.set("All")
        self._filter_search.set("")
        self._refresh_table()
    def _on_export_copy(self):
        path = filedialog.asksaveasfilename(
            title="Export a copy of the Excel file",
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
            initialfile="budget_data_copy.xlsx",
        )
        if not path:
            return
        try:
            # Use storage's dedicated export method that does not mutate the active path
            self.storage.export_copy(self.model, path)
            messagebox.showinfo("Export", f"Exported a copy to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export file:\n{e}")
    def _clear_form(self):
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, date_to_str(date.today()))
        self.type_var.set("Expense")
        if self.model.categories:
            self.combo_category.set(self.model.categories[0])
        else:
            self.combo_category.set("General")
        self.entry_description.delete(0, tk.END)
        self.entry_amount.delete(0, tk.END)
    def _on_close(self):
        try:
            self.storage.save_model(self.model)
        except Exception:
            # ignore save issues on close, already shown on operations
            pass
        self.destroy()