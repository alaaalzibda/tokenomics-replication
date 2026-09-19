# Castle of Choices — Interactive Storytelling Game

An interactive, branching-narrative game where your decisions shape the story. Explore an ancient castle, befriend or antagonize its guard, collect items, and unlock multiple endings. The game comes with a flexible story engine, structured story data, and a desktop GUI built with Tkinter.

- Platform: Desktop application
- Language: Python
- UI Toolkit: Tkinter (built into standard Python distributions)

## Highlights

- Branching narrative with meaningful choices
- State tracking of items, variables, relationships, flags, and visited nodes
- Conditional choices based on your state (e.g., items owned, trust with characters)
- Multiple endings
- Save and load progress as JSON
- Clean, extensible story data format for creators and modders
- Cross-platform (Windows, macOS, Linux)

---

## Quick Start

- Ensure Python 3.8+ is installed.
- Run: `python main.py`
- Click “New Game” to start, “Load Game” to resume.

Keyboard shortcuts:
- Save: Ctrl+S
- Load: Ctrl+O
- Restart: F5

---

## System Requirements

- Python: 3.8 or newer
- Tkinter: usually included; see platform notes below if missing

### Platform notes for Tkinter
- Windows: Tkinter typically ships with Python from python.org.
- macOS: Use the official Python installer from python.org (includes Tk). If using Homebrew Python, you may need to install/configure Tcl/Tk separately.
- Linux:
  - Debian/Ubuntu: `sudo apt-get install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`
  - Arch: `sudo pacman -S tk`

---

## Installation

1. Install Python 3.8+ from https://www.python.org/downloads/.
2. (Optional) Create a virtual environment:
   - `python -m venv .venv`
   - Activate:
     - Windows: `.venv\Scripts\activate`
     - macOS/Linux: `source .venv/bin/activate`
3. Obtain the source code (clone or download).
4. No additional pip packages are required.
5. Run the game:
   - `python main.py`

---

## Using the Application

### Start Screen
- New Game: Start a new story.
- Load Game: Load a previously saved session from a JSON file.

### Main Game Screen
- Story panel: Displays the current narrative segment.
- Choices panel: Clickable options that move the story forward. Availability depends on your current state.
- Sidebar:
  - Items: Inventory you’ve collected (e.g., “Old Key”).
  - Relationships: Trust/rapport scores with characters (e.g., Guard: 2).
  - Variables: Numeric stats (e.g., Bravery: 3).

### Controls
- Save: Open a dialog to save your current session to a JSON file.
- Load: Open a dialog to load a saved session.
- Restart: Reset the current run to the beginning.

Keyboard shortcuts:
- Ctrl+S: Save
- Ctrl+O: Load
- F5: Restart

### Endings
When you reach a node with no available choices, the story ends. You’ll see a “Play Again” button to restart.

---

## Gameplay Mechanics

Your choices affect the game state, which changes available paths and endings.

- Items: Named objects you can pick up or lose. Example: “Old Key”
- Variables: Numeric stats that can increase or decrease (e.g., bravery).
- Relationships: Numeric affinity/trust with named characters (e.g., Guard).
- Flags: Boolean markers of key story events (e.g., watchlisted = True).
- Visited nodes: Chronological list of node ids you’ve visited.

Choice availability is controlled by conditions. Selecting a choice can apply effects to your state. For example:
- A friendly approach to the guard increases “Guard” relationship.
- Being rude may set a flag “watchlisted” and lock certain paths.
- Possessing the “Old Key” unlocks secret doors.

---

## Saving and Loading

- Save: Click “Save” or press Ctrl+S. Choose a location and filename (JSON).
- Load: Click “Load” or press Ctrl+O. Select a previously saved JSON file.

Saved file structure (example excerpt):
```json
{
  "current_node_id": "hall",
  "state": {
    "items": ["Old Key"],
    "variables": {"bravery": 2},
    "relationships": {"Guard": 1},
    "flags": {"watchlisted": false},
    "visited_nodes": ["intro", "courtyard", "hall"]
  }
}
```

Notes:
- You can load a game from the start screen or while playing. After a successful load, the UI updates to the loaded state automatically.
- If a load fails (e.g., corrupted JSON), you’ll see an error message and the game remains unchanged.

---

## Included Story: “Castle of Choices”

The shipped story data places you in the Castle of Aster. Core beats include:
- Intro: Choose to explore or talk to the guard.
- Hall: Central hub with routes to secret areas or social paths.
- Sneak Attempt: Risky route influenced by whether you’re “watchlisted.”
- Treasury: Acquire the Ancient Artifact (optional).
- Restricted Wing/Tower: Social route unlocked by good relationship with the guard.
- Underground Lake: Ending varies based on whether you carry the artifact.
- Multiple endings: Heroic, peaceful, popular, mystic, free, caught, lost, etc.

Replay to discover different outcomes by altering your relationships, inventory, and bravery.

---

## Extending or Modding the Story

All story content lives in `story_data.py` as a Python dictionary named `STORY`. You can modify or replace it to build new adventures.

### Story Structure

Top-level:
- start: node id string for the entry point
- nodes: mapping of node_id -> node definition

Node:
- text: narrative string shown to the player
- choices: list of choice objects (or empty for endings)

Choice:
- text: label shown on the choice button
- target: node id to navigate to on selection
- conditions: optional dict controlling availability
- effects: optional dict applied to state on selection

Example node with two choices:
```python
"courtyard": {
    "text": "Moonlight paints the courtyard silver...",
    "choices": [
        {
            "text": "Pick up the old key and head inside.",
            "target": "hall",
            "effects": {"add_items": ["Old Key"]}
        },
        {
            "text": "Ignore it and enter the great hall.",
            "target": "hall"
        }
    ]
}
```

### Supported Conditions

Add these under a choice’s "conditions" to gate availability:

- items_have: [str]
- items_not_have: [str]
- vars_min: {name: min_value}
- vars_max: {name: max_value}
- vars_eq: {name: exact_value}
- relationships_min: {name: min_value}
- flags_set: [flag_name]
- flags_not_set: [flag_name]
- visited_nodes_include: [node_id]
- visited_nodes_exclude: [node_id]

Example:
```python
"conditions": {
    "items_have": ["Old Key"],
    "relationships_min": {"Guard": 2},
    "flags_not_set": ["watchlisted"]
}
```

### Supported Effects

Add these under a choice’s "effects" to mutate state:

- add_items: [str]
- remove_items: [str]
- vars_delta: {name: delta}
- vars_set: {name: value}
- relationships_delta: {name: delta}
- set_flags: {flag_name: bool}

Example:
```python
"effects": {
    "add_items": ["Ancient Artifact"],
    "vars_delta": {"bravery": 1},
    "relationships_delta": {"Guard": -2},
    "set_flags": {"watchlisted": True}
}
```

### Tips for Authors

- Unique IDs: Ensure each node_id is unique, and all choice targets reference valid nodes.
- Start node: Keep STORY["start"] set to a valid node id. If omitted or invalid, the engine uses the first node found.
- Endings: Use an empty "choices" list to mark an ending node.
- Balancing: Use variables and relationships consistently. Keep value ranges readable (e.g., -3 to +3).
- Replayability: Gate some branches on flags or visited nodes to encourage multiple playthroughs.
- Testing:
  - Start the app and rapidly traverse branches to verify conditions.
  - If a choice becomes invalid unexpectedly, the UI shows a helpful error.

---

## Project Layout

- main.py: Entry point; launches the GUI.
- gui.py: Tkinter UI (start screen, narrative/choices, sidebar, save/load).
- engine.py: Story engine, state, condition checking, and progression logic.
- story_data.py: The structured story content (nodes, choices, conditions, effects).
- storage.py: Save/load helpers using JSON files.

---

## Troubleshooting

- Tkinter not found:
  - Windows/macOS: Reinstall Python from python.org.
  - Linux: Install the tkinter package (e.g., `sudo apt-get install python3-tk`).
- Choice Error popup:
  - The target node might be missing or the choice’s conditions are no longer met due to state changes.
  - Review your story_data node ids and conditions.
- JSON load errors:
  - The file might be corrupted or manually edited incorrectly.
  - Try loading a different save or restart and create a new save.
- File dialogs behind the window:
  - Alt-Tab through windows; on some environments the dialog can appear behind the main window.
- High DPI scaling issues (Windows):
  - Right-click Python or your terminal, set compatibility > High DPI scaling override, or adjust OS display scale.

---

## FAQ

- Can I add my own story?
  - Yes. Edit `story_data.py` (or load from an external JSON you convert to the same schema) and restart the app.
- Do I need internet access?
  - No. The app is fully offline.
- Where are saves stored?
  - Wherever you choose in the Save dialog (JSON files).
- Can I translate the game?
  - Yes. Replace the text fields in `story_data.py` with your localized strings.

---

## Contributing

- Add more nodes and endings in `story_data.py`.
- Use the provided condition/effect system to create intricate, replayable branches.
- If you extend engine features, document new conditions/effects in this manual.

Enjoy crafting your path through the Castle of Choices!