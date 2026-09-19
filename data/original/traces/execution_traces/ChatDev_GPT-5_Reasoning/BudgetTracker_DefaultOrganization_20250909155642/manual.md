# Budget Tracker — User Manual

Track expenses, income, and savings progress in a clean, local-first desktop app. Data is saved to an Excel workbook (XLSX) that you can also open in Excel for further analysis.

- Platform: Desktop GUI (Tkinter)
- Storage: Excel workbook (openpyxl)
- Language: Python
- Default data file: budget_data.xlsx (created in your current working directory)

## Features at a Glance

- Add, edit, and delete transactions (Income or Expense)
- Organize by categories; add your own categories
- Filter by year, month, type, category, and keyword
- Savings goal with progress bar
- Live summary: Income, Expenses, and Net
- Export a shareable copy of your data to another XLSX file
- Data stored locally in a simple Excel structure:
  - Transactions sheet
  - Categories sheet
  - Settings sheet

---

## 1) Installation

### Requirements

- Python 3.8 or newer
- pip (Python package manager)
- Tkinter (bundled with most Python distributions; see notes below)
- openpyxl (for Excel read/write)

### Quick Install

- Windows (PowerShell)
  ```
  py -3 -m venv .venv
  .\.venv\Scripts\activate
  pip install -U pip openpyxl
  python main.py
  ```

- macOS / Linux (Terminal)
  ```
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -U pip openpyxl
  python3 main.py
  ```

Notes:
- If Tkinter is missing on Linux:
  - Debian/Ubuntu: sudo apt-get install python3-tk
  - Fedora: sudo dnf install python3-tkinter
- If you double-click main.py and see a “Missing dependency” message for openpyxl, run:
  ```
  pip install openpyxl
  ```

---

## 2) Launching the App

1. Open a terminal in the project directory.
2. Activate your virtual environment (if used).
3. Run:
   - Windows: `python main.py`
   - macOS/Linux: `python3 main.py`

On first run, the app creates budget_data.xlsx in the current working directory. To keep data in a specific folder, launch the app from that folder.

---

## 3) Understanding the Interface

- Summary bar (top):
  - Income, Expenses, Net totals
  - Savings goal input and progress bar
- Add/Edit Transaction form:
  - Date, Type (Expense/Income), Category, Description, Amount
- Filters:
  - Year, Month, Type, Category, Search (by description), Apply/Reset
- Table view:
  - ID, Date, Type, Category, Description, Amount
  - Buttons: Edit selected, Delete selected, Export copy…

---

## 4) Core Workflows

### Add a Transaction

1. Date: enter as YYYY-MM-DD (also accepts DD/MM/YYYY or MM/DD/YYYY).
2. Type: choose Expense or Income.
3. Category: select from the dropdown.
4. Want a new category? Type it in the “Add category” field and click “Add category,” then choose it.
5. Description: optional.
6. Amount: enter a positive number (the app infers sign from Type).
7. Click “Add.”

The transaction appears in the table, and the Excel file saves automatically.

Tips:
- Amounts are always stored as positive values in Excel; the Type determines whether it counts as income or expense.
- Expenses display with a minus sign in the UI for clarity.

### Edit a Transaction

1. Select a row in the table.
2. Click “Edit selected.”
3. The form fills with the transaction’s data. Make changes.
4. Click “Update” (the Add button changes to Update in edit mode).

### Delete a Transaction

1. Select a row in the table.
2. Click “Delete selected.”
3. Confirm the deletion.

### Set a Savings Goal

1. Enter your target in the “Savings goal” field (top summary area).
2. Click “Set goal.”
3. The progress bar reflects the percent of goal reached based on your current Net. Only positive net contributes to progress.

### Filter Your Data

- Set Year, Month, Type, Category, or type a keyword in Search (matches Description).
- Click “Apply.”
- Click “Reset” to clear all filters.

### Export a Copy

- Click “Export copy…”
- Choose a destination and filename (e.g., budget_data_copy.xlsx).
- This creates a standalone copy of your current data without changing the main file’s location.

---

## 5) Data Model and Excel Structure

All data lives in an XLSX file that you can open in Excel. The app manages structure automatically.

- Transactions (sheet name: Transactions)
  - Columns: ID, Date, Type, Category, Description, Amount
  - Amount is stored as a positive number; Type is “Income” or “Expense”
  - Rows are sorted by Date then ID in the app

- Categories (sheet name: Categories)
  - Column: Name
  - Pre-populated with: General, Food, Transport, Housing, Utilities, Entertainment, Healthcare, Income:Salary, Income:Other, Savings
  - Adding categories in the app updates this sheet

- Settings (sheet name: Settings)
  - Key, Value
  - savings_goal stored here

Important:
- Keep the header rows intact if editing in Excel.
- Dates should be valid Excel dates or strings parsable by the app (YYYY-MM-DD recommended).
- Type must be exactly “Income” or “Expense” for the app to interpret correctly.
- Amounts should be positive; the app interprets sign via Type.

---

## 6) Tips and Best Practices

- Backups: Use “Export copy…” periodically to save snapshots.
- Portability: Copy budget_data.xlsx to move your data to another machine.
- Open in Excel: Analyze with PivotTables, charts, etc. Do not change headers. Avoid negative values in Amount; use Type to represent sign.
- Categories: Keep them consistent for better analysis.
- Running from a different folder: The app saves budget_data.xlsx in the folder you launched from.

---

## 7) Troubleshooting

- Missing openpyxl:
  - Error dialog: “openpyxl is required…”
  - Fix: `pip install openpyxl`

- Tkinter not found (Linux):
  - Install OS package: `sudo apt-get install python3-tk` (Debian/Ubuntu) or equivalent.

- Permission or file lock errors:
  - Close budget_data.xlsx in Excel while the app is running.
  - Ensure you have write permissions in the folder.

- Corrupted/modified workbook:
  - Ensure sheets and headers exist as specified.
  - If needed, temporarily move/rename budget_data.xlsx; the app will create a fresh one. Then copy your valid rows back carefully.

- Date format issues:
  - Use the YYYY-MM-DD format to avoid ambiguity.

- Amount validation:
  - Must be positive. If you enter a negative, the app will treat it as positive and apply sign via Type.

---

## 8) Keyboard and Usability Notes

- Use Tab/Shift+Tab to move between fields.
- Press Enter inside a field to confirm text, then click buttons as needed.
- The table supports single selection; use the buttons below it for actions.

---

## 9) Customization (Optional)

- Change currency symbol (advanced users):
  - Edit utils.py: format_currency(value, symbol="$")
  - Replace "$" with your preferred symbol, e.g., "€" or "£".
  - Save and rerun the app.

- Default categories:
  - You can add more via the app. To change the initial list for brand-new files, edit storage.py in _initialize_empty_file().

- Data file location:
  - By default, the app uses budget_data.xlsx in the current working directory.
  - To keep data elsewhere, launch the app from the target folder or adjust data_file in main.py.

---

## 10) FAQ

- Can I import an existing Excel file?
  - Yes, if it follows the same sheet names and column headers. Otherwise, export a copy from the app and paste your data into the correct structure.

- Is this cloud-synced?
  - No. It’s local-only. Use your own sync solution (e.g., OneDrive, Dropbox) on budget_data.xlsx if desired.

- Multi-user or concurrent editing?
  - Not supported. Avoid writing to the same file from multiple instances at once.

- What does the “Search” filter do?
  - It matches the Description field (case-insensitive substring).

- Why do Expenses show with a minus sign?
  - For readability. Internally, amounts are positive, and Type determines sign. The summary and table present expenses as negative.

---

## 11) Quick Start Checklist

1. Install Python 3.8+ and pip.
2. Create and activate a virtual environment.
3. Install openpyxl: `pip install openpyxl`.
4. Run the app: `python main.py`.
5. Add a few transactions.
6. Set a savings goal.
7. Filter and review your budget.
8. Export a copy for backup or sharing.

---

If you need enhancements or tailored features (reports, charts, multi-currency, CSV import/export), contact ChatDev — we’re here to help you change the digital world through programming.