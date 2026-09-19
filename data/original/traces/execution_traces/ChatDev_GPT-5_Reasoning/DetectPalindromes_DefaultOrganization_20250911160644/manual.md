# Palindrome Detector

Detect palindromic words, sentences, and lines in any text file with a simple desktop GUI.

- Zero third‑party dependencies (standard Python only)
- Robust file encoding support
- Interactive preview with in-text highlighting
- One-click CSV export of results

## Table of Contents

- Overview
- Features
- System Requirements
- Installation
- Quick Start
- Using the Application
- Exporting Results
- Encoding Support
- Palindrome Rules and Detection Details
- Examples
- Programmatic API (Optional)
- Packaging as an Executable (Optional)
- Troubleshooting and FAQ
- Project Structure

---

## Overview

Palindrome Detector scans a text file to find palindromes based on user-selected rules. It can detect palindromic:
- Words
- Sentences
- Entire lines

Results are displayed in a table and can be highlighted in a preview pane. You can export findings to CSV for further analysis.

## Features

- Toggle detection of words, sentences, and lines
- Normalize input by ignoring case and/or non-alphanumeric characters
- Adjustable minimum palindrome length
- In-text highlighting of detected palindromes
- Robust file reading with support for BOM-aware UTF encodings and common single-byte encodings
- CSV export with complete metadata

## System Requirements

- OS: Windows, macOS, Linux
- Python: 3.7+ (3.8+ recommended)
- Tkinter (Python’s standard GUI library)
  - Windows/macOS installers typically include Tkinter
  - Linux users may need to install it separately (see Troubleshooting)

## Installation

1) Get the source code
- Download or clone the project into a local folder.

2) Install dependencies
- The app uses only Python’s standard library. Only for Python < 3.7 is the dataclasses backport needed.

Command:
```
pip install -r requirements.txt
```

3) Ensure Tkinter is available
- Windows/macOS: Usually preinstalled with Python
- Ubuntu/Debian:
  ```
  sudo apt-get update
  sudo apt-get install -y python3-tk
  ```
- Fedora:
  ```
  sudo dnf install python3-tkinter
  ```
- macOS via Homebrew Python (if needed):
  ```
  brew install python-tk
  ```

## Quick Start

From the project directory, run:
```
python main.py
```

The GUI window titled “Palindrome Detector” will open.

## Using the Application

The interface has five main areas:
1) Menu bar (File, Help)
2) Detection Options (top)
3) Action buttons (Open, Analyze, Export)
4) Results table (middle)
5) File Preview (bottom) with highlighting
6) Status bar (bottom-most)

### Step-by-Step

1) Open a file
- Click File > Open… or use the Open… button.
- Select a .txt or any text file.

2) Configure detection options
- Scope:
  - Words: Find palindromic words in each line
  - Sentences: Find sentence-level palindromes per line
  - Lines: Check entire lines as palindromes
- Normalization:
  - Ignore case: Treat uppercase/lowercase as equal (casefold)
  - Ignore non-alphanumeric: Remove all characters that are not letters or digits before checking
- Minimum length:
  - Only consider normalized strings of at least this length (default 3)

3) Analyze
- Click Analyze to run detection.
- Results are listed with columns:
  - Category (word, sentence, line)
  - Content (displayed text; newlines shown as \n in table)
  - Length (of the normalized text)
  - Line (1-based)
  - Start (0-based column in the line)
  - End (0-based column end, exclusive)

4) Inspect and highlight
- Click a result row to highlight the occurrence in the File Preview:
  - Lines are shaded blue (linehl)
  - Words/sentences are highlighted yellow (highlight)

5) Export (optional)
- Click Export Results… to save findings as a CSV file.

### Menu Items

- File
  - Open…: Choose a text file
  - Analyze: Run detection on the loaded text with current options
  - Export Results…: Save to CSV
  - Exit: Close the app
- Help
  - About: App information

### Notes on Interaction

- The preview is read-only. Use the Results table to navigate occurrences.
- Status bar messages indicate progress (e.g., loaded path, number of palindromes found).

## Exporting Results

Use File > Export Results… to write a CSV with headers:
- Category
- Content
- Normalized
- Length
- Line
- StartCol
- EndCol

Encoding: UTF-8 with headers.

## Encoding Support

The file loader attempts several encodings to reliably read text:
- UTF-8, UTF-8 with BOM
- UTF-16/32 (generic and LE/BE variants; BOM-aware)
- cp1252 (Windows Western)
- latin-1

Fallback logic:
- BOM sniffing from binary data
- UTF-16 with replacement heuristic
- Final fallback: UTF-8 with replacement (never fails)

This approach maximizes successful reads and preserves character positions for highlighting.

## Palindrome Rules and Detection Details

- Normalization:
  - If “Ignore non-alphanumeric” is ON: remove all characters for which ch.isalnum() is False (punctuation, spaces, underscores, symbols)
  - If “Ignore case” is ON: use casefold() for robust case-insensitive comparison
- A palindrome is defined as a non-empty string equal to its reverse after normalization.
- Minimum length applies to the normalized form.

Scopes:
- Words
  - Defined as contiguous sequences of alphanumeric characters (Unicode-aware). Underscores are not included.
- Sentences
  - Processed within a single line.
  - A sentence ends with '.', '!' or '?'. Trailing quotes/brackets immediately after punctuation are included: ) " ' ]
  - The last fragment (with no terminal punctuation) is also considered.
- Lines
  - The entire line (as displayed in the preview) is tested as a single unit.

Positions:
- Line numbers are 1-based (consistent with Tk Text widget).
- StartCol and EndCol are 0-based indices within the line.
- EndCol is exclusive.

Limitations:
- Sentence detection does not cross line boundaries. If your document wraps sentences across lines, they’ll be evaluated per line.
- If “Ignore non-alphanumeric” is ON, whitespace and punctuation are removed before checking, which can turn “A man, a plan, a canal: Panama!” into a palindrome.

## Examples

Given a file with:
```
Madam, I'm Adam.
Never odd or even.
Was it a car or a cat I saw?
abcddcba
palindrome
No 'x' in Nixon
```

With options:
- Words: ON, Sentences: ON, Lines: ON
- Ignore case: ON
- Ignore non-alphanumeric: ON
- Minimum length: 3

You will typically see detections such as:
- Line: “Never odd or even.” (normalized: neveroddoreven)
- Sentence: “Was it a car or a cat I saw?” (normalized: wasitacaroracatisaw)
- Line: “abcddcba”
- Sentence: “No 'x' in Nixon”
- Words like “Madam”, depending on punctuation and normalization options

Selecting a result highlights it in the preview.

## Programmatic API (Optional)

You can reuse the detection engine in your own scripts.

Minimal example:
```python
from palindrome_detector import DetectionOptions, detect_palindromes

text = "Never odd or even.\nhello\nracecar"
opts = DetectionOptions(
    check_words=True,
    check_sentences=True,
    check_lines=True,
    min_length=3,
    ignore_case=True,
    ignore_non_alnum=True,
)

results = detect_palindromes(text, opts)
for r in results:
    print(r.category, r.text, r.normalized, r.line_no, r.start_pos, r.end_pos)
```

Result items are PalindromeMatch dataclasses with:
- category, text, normalized, length, line_no, start_pos, end_pos

## Packaging as an Executable (Optional)

You can bundle the app with PyInstaller for distribution:
```
pip install pyinstaller
pyinstaller --noconsole --name "PalindromeDetector" main.py
```

The generated executable will include the standard library dependencies. Ensure Tkinter is available on target systems.

## Troubleshooting and FAQ

- The GUI won’t start / no module named tkinter
  - Install Tkinter: Ubuntu/Debian: sudo apt-get install python3-tk; Fedora: sudo dnf install python3-tkinter; macOS (Homebrew Python): brew install python-tk
- Opening certain files shows garbled characters
  - The loader tries multiple encodings. If the file uses an uncommon encoding, convert it to UTF-8 and try again.
- Large files feel slow
  - The app reads entire files into memory and builds a full-text preview. For very large files (hundreds of MB), consider pre-filtering or splitting.
- Why don’t multi-line sentences get detected?
  - By design, detection runs per line to support precise in-line highlighting. Join lines before loading if you need cross-line sentence analysis.
- Are underscores part of words?
  - No. Word detection uses alphanumeric characters only (ch.isalnum()).

## Project Structure

- main.py
  - Application entry point; launches the Tkinter GUI
- gui_app.py
  - GUI: menus, options, results table, preview, highlighting, export
- palindrome_detector.py
  - Core detection logic and dataclasses
- file_utils.py
  - Robust text file reading with multi-encoding fallbacks
- exporter.py
  - CSV export utility
- requirements.txt
  - Dependency list (standard library only; optional dataclasses backport for Python < 3.7)

---

All processing is local; no network calls are made. You own your data.