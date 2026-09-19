# Trivia Quiz — User Manual

A simple, flexible desktop quiz application that lets you play trivia from built‑in or custom question banks. Supports multiple-choice (single or multiple answers) and short-answer questions, tracks your score, and optionally shows detailed correct answers after the quiz.

Version: 1.0  
Platform: Desktop (GUI with tkinter)  
Language: Python


## Key Features

- Multiple question types:
  - Multiple-choice (single answer)
  - Multiple-choice (multiple correct answers; “select all that apply”)
  - Short-answer (free text)
- Configurable question banks:
  - Built-in banks: General Knowledge, Science & Tech
  - Load your own question bank from a JSON file
- Quiz options:
  - Choose number of questions
  - Shuffle questions
  - Toggle “Show correct answers after quiz”
- Results and review:
  - Score summary
  - Detailed review of each question (if enabled), including:
    - Your answer
    - Correct answer(s)
    - Optional explanation
- Retake quickly with the same options
- No external dependencies — standard Python library only


## System Requirements

- Python 3.8 or newer
- tkinter (bundled with most Python installations)
  - Windows: Included with standard Python installers
  - macOS: Included with python.org installer; Homebrew Python may require extra setup for Tcl/Tk
  - Linux (Ubuntu/Debian): Install via `sudo apt-get install python3-tk`

If tkinter is missing, see Troubleshooting below.


## Installation

1. Ensure Python is installed:
   - Windows/macOS: Download from https://www.python.org/downloads/
   - Linux: Use your distribution’s package manager

2. (Linux) Install tkinter if needed:
   - Ubuntu/Debian: `sudo apt-get install python3-tk`

3. Download or clone the project files into a directory, which should include:
   - main.py
   - quiz_manager.py
   - models.py
   - question_bank.py
   - requirements.txt

4. No additional packages are needed (requirements.txt is informational).


## Running the Application

From a terminal or command prompt, navigate to the project directory and run:

- Windows/macOS/Linux:
  - `python main.py`
  - If your system uses Python 3 via `python3`, use `python3 main.py`


## Quick Start: Play a Quiz

1. Launch the app (see Running the Application).
2. Start Screen:
   - Select a question bank from the dropdown.
   - (Optional) Click “Load from JSON…” to add a custom bank (see Custom Banks below).
   - Options:
     - Show correct answers after quiz: Enable to see detailed review after finishing.
     - Shuffle questions: Randomize order.
     - Number of questions: Choose how many to include (limited by the selected bank’s size).
   - Click “Start Quiz”.

3. Quiz Screen:
   - Read the question and choose or enter your answer.
     - Single-answer MCQ: Choose one radio button.
     - Multi-answer MCQ: Check all correct boxes. A hint message will appear for these.
     - Short-answer: Type your answer in the text field.
   - Click “Submit” (or “Finish” on the last question).

4. Results Screen:
   - View your score summary.
   - If “Show correct answers after quiz” was enabled, scroll through detailed feedback for each question, including explanations when provided.
   - Click “Retake (same bank/options)” to play again quickly, or “Back to Start” to change settings/banks.


## Understanding Scoring

- Each question is worth 1 point.
- Multiple-choice (single answer):
  - You must select the one correct option.
- Multiple-choice (multiple answers):
  - You must select the exact set of all correct options (order doesn’t matter).
  - Partial credit is not awarded.
- Short-answer:
  - Case-insensitive and whitespace-insensitive comparison is used.
  - For example, “Blue   whale” matches “blue whale”.
  - If multiple acceptable answers are defined, matching any one is correct.


## Built-in Question Banks

- General Knowledge: A mix of geography, language, oceans, literature, and primes.
- Science & Tech: Computer fundamentals, chemistry symbols, data structures, and programming topics.

You can select these from the Question Bank dropdown on the Start screen.


## Creating and Loading Custom Question Banks (JSON)

You can load your own bank from a JSON file. The file must be a list of question objects.

Supported schema:

- Multiple-choice (MCQ):
  - type: "mcq"
  - prompt: string (required)
  - options: array of strings (required, non-empty)
  - answer: one of:
    - integer index (0-based)
    - string option text (exact match, case-insensitive with normalized spacing)
    - array of integer indices
    - array of string option texts
  - explanation: string (optional)

- Short-answer:
  - type: "short"
  - prompt: string (required)
  - answer: string or array of strings (required)
  - explanation: string (optional)

Example JSON:

```
[
  {
    "type": "mcq",
    "prompt": "Which planets are gas giants? (Select all that apply)",
    "options": ["Mercury", "Venus", "Jupiter", "Saturn"],
    "answer": [2, 3],
    "explanation": "Jupiter and Saturn are gas giants."
  },
  {
    "type": "mcq",
    "prompt": "Capital of Japan?",
    "options": ["Seoul", "Tokyo", "Beijing", "Osaka"],
    "answer": "Tokyo"
  },
  {
    "type": "short",
    "prompt": "Chemical symbol for Sodium",
    "answer": ["Na", "NA"]
  }
]
```

How matching works:

- MCQ answers by text are matched to options case-insensitively after trimming and collapsing spaces.
- MCQ multiple-answer questions are detected automatically when the answer is a list that resolves to more than one correct option.
- Short-answer acceptable answers are compared case-insensitively with collapsed whitespace.

Loading steps:

1. Click “Load from JSON…” on the Start screen.
2. Choose your JSON file.
3. If valid, the bank appears as “Custom: <filename>” in the dropdown, and you’ll see how many questions were loaded.

Error handling:

- If no valid questions are found, you’ll see an error with details.
- If some questions are invalid, valid ones still load unless none parse successfully.


## User Interface Tour

- Start Screen:
  - Question Bank dropdown: Choose built-in or newly loaded custom banks.
  - Load from JSON…: Add a custom bank.
  - Options:
    - Show correct answers after quiz (toggle)
    - Shuffle questions (toggle)
    - Number of questions (spinbox; auto-limited to the bank’s size)
  - Start Quiz: Begin with current settings.

- Quiz Screen:
  - Header shows progress (e.g., “Question 3 of 10”).
  - Question text and input controls:
    - Radio buttons for single-answer MCQ
    - Checkboxes for multi-answer MCQ
    - Text field for short-answer
  - Submit/Finish button:
    - Validates you’ve selected/entered an answer.
    - Advances to next question or finishes the quiz.

- Results Screen:
  - Score summary (e.g., “You scored 7 out of 10.”)
  - Detailed review (if enabled) per question:
    - Your answer
    - Correct answer(s)
    - Correct/Incorrect status
    - Explanation (if included in the question)
  - Retake (same bank/options): Starts a new quiz with the same number of questions and “show answers” setting; questions are reshuffled.
  - Back to Start: Return to Start screen and choose different options/banks.


## Tips and Best Practices

- For multi-answer questions, select all correct options and only those options — exact set matching is required.
- For short-answer questions:
  - You don’t need to match capitalization.
  - Avoid adding punctuation unless it’s part of the expected answer.
- When making custom banks:
  - Keep MCQ option texts unique to avoid ambiguity.
  - Prefer using indices for MCQ answers to avoid matching issues.
  - Provide explanations to enhance learning in the review step.


## Troubleshooting

- I get an error about tkinter/Tk/Tcl:
  - Windows: Ensure you installed Python from python.org; the Microsoft Store version can sometimes cause issues.
  - macOS: Use the python.org installer for Python 3.8+ (includes Tk 8.6). If using Homebrew Python, you may need to `brew install tcl-tk` and configure environment variables, or switch to the python.org build.
  - Ubuntu/Debian: `sudo apt-get install python3-tk`

- The “Number of questions” won’t go higher:
  - The maximum is capped at the number of questions in the selected bank.

- The app doesn’t start when I double-click main.py:
  - Run from terminal with `python main.py` to see any error messages.

- My custom JSON won’t load:
  - Ensure the file root is a JSON array (list).
  - Validate the schema for each question (see Creating and Loading Custom Question Banks).
  - Check for trailing commas or invalid JSON syntax.
  - Make sure MCQ “options” is a non-empty list of strings and “answer” is provided.

- Short-answer correct answers aren’t matching:
  - Matching is case-insensitive with whitespace normalization. Special characters are not removed; include relevant variants (e.g., “H2O” and “H₂O”) if needed.


## Privacy and Security

- The app runs locally and does not upload data.
- Loading custom banks reads from your local JSON files only.
- No network access is required.


## Customization for Developers

- Add or edit built-in banks:
  - Edit `get_builtin_banks()` in question_bank.py.

- Question model and evaluation rules:
  - See models.py (Question, normalization, matching rules).

- Quiz session logic:
  - See quiz_manager.py for scoring and session progression.

- UI/UX:
  - Modify main.py (tkinter-based GUI with distinct frames for Start, Quiz, and Results).

- Packaging:
  - You can use tools like PyInstaller to bundle into an executable. Ensure Tcl/Tk is included.


## FAQ

- Does the app support partial credit for multi-answer questions?
  - Not currently. It’s all-or-nothing for multi-answer MCQs.

- Can I include images or media in questions?
  - Not in this version. Questions are text-based.

- Can I save scores or export results?
  - Not currently. Results are shown after each quiz session within the app.

- Can I disable shuffling and order questions as defined?
  - Yes. Uncheck “Shuffle questions” on the Start screen.


## License

This project uses only the Python standard library. License information was not specified; consult your distribution source or project maintainers for details.