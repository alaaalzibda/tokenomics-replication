# Monopoly Go! (Simplified) — User Manual

A lightweight, family-friendly Monopoly-style game with a clean Tkinter GUI. Roll the dice, move around a 20-tile board, buy properties, collect rent, draw Chance cards, and handle jail and free parking — all with simplified rules that keep the game fast and fun.

This manual explains installation, launching the app, gameplay basics, UI controls, rules, and customization.

---

## Key Features

- 2–4 players with custom names and colored tokens
- 20-tile compact board (5x4 grid), including:
  - GO, Properties, Chance, Tax, Free Parking, Jail, and Go To Jail
- Core mechanics:
  - Roll dice and move
  - Buy properties and collect rent
  - Draw simplified Chance cards
  - Free Parking pot for taxes and fines
  - Jail rules including paying fines, rolling for doubles, or using “Get Out of Jail Free”
- Automatic tracking:
  - Player money, position, jail status, Get Out of Jail Free cards
  - Property ownership
  - Free Parking pot
  - Game log and status panel
- Game over detection when only one active player remains

---

## System Requirements

- OS: Windows, macOS, or Linux with a GUI environment
- Python: 3.7+ (3.8+ recommended)
- Tkinter: Included with most Python distributions; if missing, install via your OS package manager

Optional (older Python):
- dataclasses backport is listed in requirements for Python < 3.7

---

## Installation

1. Ensure Python 3.7+ is installed:
   - Windows/macOS: https://www.python.org/downloads/
   - Linux: Use your package manager (e.g., `sudo apt-get install python3`)

2. Ensure Tkinter is available:
   - Windows: Included with most Python installers
   - macOS: Included with the official Python installer; with Homebrew Python, Tkinter is usually included
   - Debian/Ubuntu:
     - `sudo apt-get install python3-tk`
   - Fedora:
     - `sudo dnf install python3-tkinter`
   - Arch:
     - `sudo pacman -S tk`

3. Clone or download the project files.

4. Optionally create and activate a virtual environment.

5. Install requirements (not strictly necessary for Python 3.7+):
   ```
   pip install -r requirements.txt
   ```

Note: This project uses only the Python standard library (including tkinter). No third-party pip packages are required for Python 3.7+.

---

## Quick Start

From the project directory:
```
python main.py
```

- A setup dialog will prompt for the number of players (2–4) and their names.
- Click “Start Game” to open the main game window.

---

## Files and Structure

- main.py — Application entry point; launches the Tkinter GUI
- gui.py — User interface: setup dialog, board view, status/log panels, control buttons
- game.py — Core game logic: players, tiles, board, movement, purchasing, rent, jail, end-turn, bankruptcy
- chance_cards.py — Simplified Chance deck behavior and card actions
- requirements.txt — Notes about dependencies (tkinter only; dataclasses for older Python)

---

## The User Interface

The main window is composed of three areas:

1. Board (left)
   - 20 tiles arranged in a 5x4 grid
   - Each tile shows index and name
   - Properties display ownership, price, and rent
   - Colored dots indicate player positions

2. Info Panel (top-right)
   - Status: Free Parking pot total, player money, position, status (Active/In Jail/BANKRUPT), number of Get Out of Jail Free cards, current player, last roll
   - Game Log: Chronological history of events (last ~200 messages)

3. Controls (bottom-right)
   - Roll Dice
   - End Turn
   - Pay $50 (Jail)
   - Attempt Doubles (Jail)
   - Use Get Out of Jail Free (if available)

Buttons auto-enable/disable based on the current turn and game state.

---

## Gameplay Overview

- Start money: $1500
- Passing GO: Collect $200
- Jail fine: $50
- Free Parking pot: Accumulates fines and taxes; collected by the first player who lands on Free Parking
- Doubles:
  - Rolling doubles lets you roll again
  - Three consecutive doubles sends you to Jail
- Bankruptcy:
  - If your money drops below $0, you are immediately bankrupt
  - All your properties revert to the bank (become unowned)
  - Turn passes to the next active player
- Game Over:
  - When one or zero players remain active (not bankrupt), the game ends
  - Winner is announced, and actions are disabled

---

## Turn Flow

1. If not in Jail:
   - Click “Roll Dice”
   - Your token moves forward by the total of the two dice
   - The landed tile triggers its effect (rent, Chance, tax, etc.)
   - If the tile is an unowned property and you can afford it, a purchase prompt appears
   - If you rolled doubles and were not sent to Jail, you may roll again
   - Otherwise, click “End Turn”

2. If in Jail:
   - You may:
     - Pay $50 to leave Jail and then roll on the same turn
     - Use a Get Out of Jail Free card (if you have one) and then roll
     - Attempt to roll doubles (up to 3 attempts across turns)
       - If you roll doubles, you immediately move by the dice total and are freed
       - If you fail three times, you pay $50 and move by the total rolled on the 3rd attempt
   - After resolving your choice, finish the turn per the prompts

---

## Tiles and Rules

- GO (Index 0)
  - Passing GO (not just landing) grants $200
  - Landing on GO logs a message; salary is awarded when passing

- Properties
  - Unowned: You may buy if you have enough money
  - Owned by you: Nothing happens
  - Owned by another player: Pay the listed rent
  - There are no houses/hotels/monopoly multipliers in this simplified version
  - Declined purchases do not trigger auctions; the property remains unowned

- Chance
  - Draws a card from the simplified deck (see Chance Cards below)
  - Some cards move you, award/charge money, or send you to Jail
  - “Get Out of Jail Free” (GOOJF) is unique; only one can be held at a time

- Tax
  - Pay the listed amount to the Free Parking pot
  - Can trigger bankruptcy if funds drop below zero

- Free Parking
  - Collect all money in the Free Parking pot and reset it to $0

- Jail (Just Visiting)
  - Landing here while not being sent by another effect means “Just Visiting”
  - No effect

- Go To Jail
  - Go directly to Jail; do not collect $200
  - Doubles streak resets

---

## Chance Cards (Simplified)

The deck includes the following cards and behaviors:

- Advance to GO:
  - Move to GO and collect $200
- Bank pays you dividend of $100:
  - Gain $100
- Go to Jail:
  - Go directly to Jail; do not pass GO or collect $200
- Pay fine of $50:
  - Pay $50 to the Free Parking pot
- Inherit $100:
  - Gain $100
- Move back 3 spaces:
  - Move 3 tiles backward; resolve the new tile
- Advance 5 spaces:
  - Move 5 tiles forward; resolve the new tile
- Property repairs ($25 per property):
  - Pay $25 per property you own to the Free Parking pot
- Chairman of the Board:
  - Pay $50 to each other active player
- Get Out of Jail Free:
  - Keep until needed; may be used from Jail to leave immediately
  - Only one GOOJF can be held at a time; returns to deck upon use

All debit-causing card actions can trigger bankruptcy immediately.

---

## Board Reference (Index: Tile — Details)

0. GO
1. Old Kent Road — Price: $60, Rent: $2
2. Chance
3. Whitechapel Road — Price: $60, Rent: $4
4. Income Tax — Pay $100 to Free Parking pot
5. Jail / Just Visiting
6. The Angel Islington — Price: $100, Rent: $6
7. Free Parking
8. Euston Road — Price: $100, Rent: $6
9. Chance
10. Pentonville Road — Price: $140, Rent: $10
11. Go To Jail
12. Pall Mall — Price: $140, Rent: $10
13. Chance
14. Whitehall — Price: $160, Rent: $12
15. Fleet Street — Price: $160, Rent: $12
16. Chance
17. Trafalgar Square — Price: $180, Rent: $14
18. Luxury Tax — Pay $100 to Free Parking pot
19. Chance

---

## Controls and States

- Roll Dice
  - Enabled when it’s your turn and you’re not in Jail, and either you haven’t rolled yet or you rolled doubles
- End Turn
  - Enabled after you’ve completed your allowed rolls and any post-roll actions
- Pay $50 (Jail)
  - Enabled if you’re in Jail and have at least $50
- Attempt Doubles (Jail)
  - Enabled if you’re in Jail
- Use Get Out of Jail Free
  - Enabled if you’re in Jail and have a GOOJF card

When the game ends:
- Buttons are disabled
- A one-time message shows the winner
- See the log for details

---

## Tips and Best Practices

- Keep an eye on the Free Parking pot — landing there can swing the game
- Doubles can help you move quickly, but three in a row sends you to Jail
- Rent and taxes can quickly deplete funds; consider cash before purchasing
- Chance cards can trigger movement; be ready for follow-up effects

---

## Troubleshooting

- Tkinter not found:
  - Install the OS package for Tkinter (see Installation)
- No GUI or display errors on Linux:
  - Ensure you are running in a desktop session with DISPLAY set
  - Remote/headless servers require X forwarding or a virtual display (not recommended)
- Python warnings about dataclasses:
  - For Python 3.7+, no action needed
  - For older Python, use the backport (requirements.txt covers it)
- Window scaling or text too small:
  - Adjust OS display scaling or DPI settings; Tkinter inherits system scaling

---

## Customization and Extensibility

You can tweak several parts of the game:

- game.py
  - Constants:
    - START_MONEY, GO_SALARY, JAIL_FINE, MAX_DOUBLES_ALLOWED, MAX_JAIL_ATTEMPTS
  - Board._build():
    - Change tile order, add/remove tiles, tweak property prices and rents
  - Rules:
    - Adjust bankruptcy behavior, rents, or passing GO logic

- chance_cards.py
  - Add/remove cards in ChanceDeck._build_cards()
  - Modify effects (movement via game.move_player_to or game.move_player_steps; always call game.check_bankruptcy after debits)

- gui.py
  - UI layout and styles (board grid, info panel sizes, button labels)
  - Player colors in PLAYER_COLORS
  - Purchase prompts and messaging

Note: Keep event-chain safety by routing movement through Game methods (already implemented).

---

## Frequently Asked Questions

- Q: Can I save and load games?
  - A: Not in this simplified version.

- Q: Are auctions implemented if a player declines to buy a property?
  - A: No. The property remains unowned.

- Q: Are houses/hotels and monopolies included?
  - A: No. Rents are fixed per property.

- Q: Can players trade properties or negotiate?
  - A: Not in this version.

- Q: Is there online multiplayer?
  - A: No. Local, pass-and-play only.

---

## Credits

- Design and product: ChatDev — Chief Product Officer
- Engineering: ChatDev team
- Technologies: Python standard library (tkinter)

Enjoy the game!