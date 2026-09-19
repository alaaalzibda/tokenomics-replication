# Fibonacci Generator (GUI) — User Manual

Change the digital world through programming with a simple, friendly tool to explore Fibonacci numbers.

This application is a desktop GUI built with Python’s standard library (Tkinter). It lets you generate all Fibonacci numbers up to a user-specified limit, inspect basic statistics, copy the sequence to your clipboard, and save it to a file.

## Highlights

- Easy-to-use desktop interface (no command line required)
- Input validation with helpful error messages
- Generates Fibonacci numbers up to an inclusive limit
- One-click actions: Generate, Clear, Copy, and Save
- Inline stats: count, maximum, and sum
- No external Python packages required

## System Requirements

- Python: 3.8 or newer is recommended
- Tkinter: Included with most Python distributions
  - Windows: Included with the official python.org installer
  - macOS: Included with the official python.org installer
  - Linux: May require installing the OS package for Tk (see below)

Display environment:
- A desktop environment is required to run the GUI (not headless).
- On WSL or servers without a display, use an X server or run the app on a machine with a GUI.

## Getting the Code

Place the following files in a project directory:
- main.py
- gui.py
- fibonacci.py
- requirements.txt

Your directory should look like:
- project/
  - main.py
  - gui.py
  - fibonacci.py
  - requirements.txt

## Installation

1) Optional: create a virtual environment
- macOS/Linux:
  ```
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- Windows (PowerShell):
  ```
  py -m venv .venv
  .venv\Scripts\Activate.ps1
  ```

2) Install dependencies
- This project uses only the Python standard library; no pip packages are required:
  ```
  python -m pip install -r requirements.txt
  ```
- If you see a message about Tkinter missing:
  - Ubuntu/Debian:
    ```
    sudo apt-get update
    sudo apt-get install -y python3-tk
    ```
  - Fedora:
    ```
    sudo dnf install python3-tkinter
    ```
  - Arch:
    ```
    sudo pacman -S tk
    ```
  - macOS (if using Homebrew Python): ensure Tcl/Tk is installed and linked, or install Python from python.org.
  - Windows: use the official python.org installer.

## Running the Application

From the project directory:
- macOS/Linux:
  ```
  python3 main.py
  ```
- Windows:
  ```
  py main.py
  ```

A window titled “Fibonacci Generator” will open.

## Using the Application

1) Enter a limit
- In the field “Generate Fibonacci numbers up to:”, type a non-negative integer (e.g., 1000).
- The app includes a sensible default of 1000.

2) Generate
- Click “Generate” or press Enter.
- The list area populates with each Fibonacci number on its own line.

3) Review statistics
- The status bar at the bottom shows:
  - Count: how many Fibonacci numbers were generated
  - Max: the largest Fibonacci number in the list
  - Sum: the sum of all generated numbers

4) Copy to clipboard
- Click “Copy” to copy the sequence as a comma-separated string (e.g., 0, 1, 1, 2, 3, 5, 8).
- Tip: When the list has focus, press Ctrl+C to copy (does not override copy in the input field).

5) Save to a file
- Click “Save…” (or press Ctrl+S) to export the sequence to a text file.
- The file includes a short header indicating the limit and the numbers in a single comma-separated line.

6) Clear
- Click “Clear” to reset the input and output.

### Keyboard Shortcuts

- Enter: Generate
- Ctrl+S: Save…
- Ctrl+C: Copy (when the list is focused)

## Input Rules and Examples

- The limit must be a whole, non-negative integer (0, 1, 2, …).
- The limit is inclusive. All Fibonacci numbers less than or equal to the limit are generated.
- Sequence starts from 0, 1 and includes repeated 1: 0, 1, 1, 2, 3, 5, …

Examples:
- Limit 10 → 0, 1, 1, 2, 3, 5, 8
- Limit 1 → 0, 1, 1
- Limit 0 → 0

Invalid inputs:
- Empty input
- Non-integer (e.g., 3.14, “abc”)
- Negative number (e.g., -5)

The app shows a clear error message for invalid inputs.

## What Gets Saved

When you click “Save…”, the file content looks like:
```
Fibonacci numbers up to 1000:
0, 1, 1, 2, 3, 5, 8, 13, ...
```

- The numbers are comma-separated on a single line for easy reuse.
- If the input cannot be parsed at save time, the header falls back to “Fibonacci numbers:”.

## Programmatic Usage (Optional)

You can reuse the core logic in your own Python scripts by importing from fibonacci.py.

- Parse and validate input:
  ```python
  from fibonacci import parse_limit
  limit = parse_limit("1000")  # returns 1000 (int), raises ValueError on bad input
  ```

- Generate Fibonacci numbers up to a limit (inclusive):
  ```python
  from fibonacci import generate_fibonacci_up_to
  seq = generate_fibonacci_up_to(10)  # [0, 1, 1, 2, 3, 5, 8]
  ```

- Format a sequence for display or saving:
  ```python
  from fibonacci import format_sequence
  print(format_sequence(seq))           # "0, 1, 1, 2, 3, 5, 8"
  print(format_sequence(seq, " | "))    # "0 | 1 | 1 | 2 | 3 | 5 | 8"
  ```

- Compute simple stats:
  ```python
  from fibonacci import sequence_stats
  stats = sequence_stats(seq)  # {'count': 7, 'max': 8, 'sum': 20}
  ```

## Troubleshooting

- Error: “Invalid number. Enter a whole number like 0, 10, 12345.”
  - Make sure the input is a whole non-negative integer (no decimals, no commas, no spaces).

- Error: “The number must be non-negative (>= 0).”
  - Use 0 or a positive integer.

- ModuleNotFoundError: No module named 'tkinter'
  - Install the OS package for Tk (see Installation). Ensure you’re running the correct Python interpreter.

- TclError: no display name and no $DISPLAY environment variable
  - You’re likely on a headless environment. Run the app on a machine with a GUI, or configure an X server.

- Clipboard failures
  - Some remote desktop or sandboxed environments restrict clipboard access. Try local execution.

- Save errors (permission denied)
  - Choose a directory where you have write permissions (e.g., your home or Documents folder).

## Performance Notes

- The generator runs in linear time relative to the number of Fibonacci numbers produced up to your limit.
- Extremely large limits can produce many numbers and large sums; on typical desktops, generating up to the largest 64-bit Fibonacci numbers is fast, but memory and UI rendering time will grow with output size.

## FAQ

- Does the app include the limit if it’s a Fibonacci number?
  - Yes. The limit is inclusive.

- Why does the sequence contain two 1’s?
  - The Fibonacci sequence starts 0, 1, 1, 2, 3, 5, …

- Can I start the sequence from 1?
  - Not in the GUI. For custom behavior, use the functions in fibonacci.py in your own script.

- Is there a command-line version?
  - This project focuses on the GUI. You can create a simple CLI by importing and calling the functions in fibonacci.py.

## Support

For assistance, feedback, or feature requests, please contact your ChatDev representative.