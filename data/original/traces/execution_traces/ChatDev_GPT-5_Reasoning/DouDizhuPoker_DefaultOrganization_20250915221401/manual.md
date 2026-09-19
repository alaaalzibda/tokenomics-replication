# Dou Dizhu (Landlord) — ChatDev Edition

A local GUI game of Dou Dizhu (Chinese Poker) for one human vs two simple AIs. Includes full bidding, legal move validation, and pass-or-beat logic that follows standard rules.

- Players: 3 (1 landlord, 2 farmers)
- Platform: Desktop GUI (Tkinter)
- Language: Python 3.8+
- Mission: Change the digital world through programming — and a fun round of Dou Dizhu.

## What you get

- Bidding phase (0–3 points) to determine the landlord
- Landlord receives the 3 bottom cards and leads the first trick
- Legal move validator for all standard combinations (singles, pairs, straights, sequences, bombs, rocket, four-with-two, airplanes with wings, etc.)
- Pass-or-beat enforcement and trick reset when both opponents pass
- Simple but competent AI opponents
- Clean Tkinter UI with hand selection, action buttons, and a play log

---

## Quick Start

1) Ensure Python 3.8+ is installed with Tkinter (Tcl/Tk)

2) Install dependencies (standard library only):

```
pip install -r requirements.txt
```

3) Run the game:

```
python main.py
```

---

## Requirements

- Python 3.8 or newer
- Tkinter available on your system:
  - Windows/macOS: Typically included with Python installers.
  - Linux (e.g., Ubuntu/Debian): You may need to install it:
    - Debian/Ubuntu: sudo apt-get install python3-tk
    - Fedora: sudo dnf install python3-tkinter
  - WSL: Requires an X server (e.g., Xming/VcXsrv) and DISPLAY configured.

No third-party Python packages are required.

---

## Installation

1) Clone or download this repository to your machine.

2) (Optional but recommended) Create and activate a virtual environment:

- Windows (PowerShell):
  - python -m venv .venv
  - .\.venv\Scripts\Activate.ps1
- macOS/Linux:
  - python3 -m venv .venv
  - source .venv/bin/activate

3) Install the (empty) requirements file to confirm environment readiness:

```
pip install -r requirements.txt
```

4) Launch:

```
python main.py
```

If Tkinter is missing, see Troubleshooting.

---

## The Interface

- Top bar:
  - Status label: Shows current phase and whose turn it is.
  - New Round button: Start a fresh round anytime.

- Center area:
  - Left panel: Left AI’s name, role, and remaining card count.
  - Play area:
    - Last play label: Shows who last played, their cards, and the combination type.
    - Log: Scrollable history of actions (bids, plays, passes, wins).
  - Right panel: Right AI’s name, role, and remaining card count.

- Bottom area:
  - Your hand: Cards rendered as clickable buttons. Click to select/deselect.
  - Controls:
    - Bidding: Bid 0–3 when it’s your bidding turn.
    - Play: Play your selected cards.
    - Pass: Pass your turn (only available when you’re not starting a trick).

Notes:
- Your player is always the middle seat labeled “You”.
- Suits are cosmetic; only ranks matter. Jokers are labeled SJ (Small Joker) and BJ (Big Joker).

---

## Game Flow

1) Deal:
   - 17 cards to each player, 3 bottom cards set aside.

2) Bidding (0–3):
   - Left AI starts. Bids must strictly exceed the current highest bid.
   - Bid 3 immediately ends bidding and assigns landlord.
   - Otherwise, once two players pass after the current highest bid, the highest bidder becomes landlord.
   - If all three pass (no bids), a new round is automatically dealt.

3) Landlord assignment:
   - Landlord receives the 3 bottom cards and leads the first trick.

4) Playing phase:
   - On your turn:
     - Start a new trick if there is no active combination (free lead).
     - Otherwise, you must beat the current combination or pass.
   - If both other players pass in succession, the trick resets and the last player who played gains a free lead.

5) Win condition:
   - The first player to run out of cards wins the round.
   - If the landlord wins: Landlord side wins.
   - If a farmer wins: Farmer side wins.

---

## How to Play (Step by Step)

- During bidding:
  - When prompted, click one of “Bid 0/1/2/3”.
  - You can’t bid a value less than or equal to the current highest bid.
  - A bid of 3 ends bidding immediately.

- During play:
  - Select cards by clicking them (selected cards appear sunken and highlighted).
  - Click “Play” to attempt your move.
  - If you’re not starting a trick, you may click “Pass” to skip.
  - The game validates combinations and whether your play can legally beat the current play.
  - If your move is invalid, a message explains why.

- New round:
  - Click “New Round” at the top to redeal and return to bidding.

---

## Rule Reference (What’s Valid and How to Beat)

Ranks: 3 < 4 < … < 10 < J=11 < Q=12 < K=13 < A=14 < 2=15 < SJ=16 < BJ=17

Suits do not affect rules. Sequences cannot include 2 or Jokers.

Recognized combinations:
- Single: Any one card.
- Pair: Two cards of the same rank.
- Triple: Three cards of the same rank.
- Triple + Single: Three-of-a-kind with one extra single.
- Triple + Pair: Three-of-a-kind with one extra pair.
- Straight: Five or more consecutive ranks (no 2 or Jokers). Example: 5 6 7 8 9 or 10 J Q K A.
- Pair Sequence: Three or more consecutive pairs (no 2 or Jokers). Example: 55 66 77.
- Triple Sequence: Two or more consecutive triples (no 2 or Jokers). Example: 666 777.
- Airplane with Wings:
  - Triple Sequence + Singles: e.g., 444 555 + x y (two singles as wings).
  - Triple Sequence + Pairs: e.g., 444 555 + 66 77 (two pairs as wings).
  - Wings cannot reuse the same ranks as the triples.
- Bomb: Four of a kind.
- Rocket: Both Jokers (SJ + BJ).
- Four with Two:
  - Four + Two Singles
  - Four + Two Pairs

Beating rules:
- Rocket beats everything; nothing beats a Rocket.
- Bomb beats any non-bomb non-rocket. Higher bomb beats lower bomb.
- Otherwise, only the same type and the same length can beat:
  - Higher main rank wins (e.g., higher straight end rank, higher triple rank).
  - For sequences, lengths must match exactly.
  - For “Four with Two”, only the same subtype (two singles vs two pairs) can beat it by higher four-of-a-kind.
- You may always pass if not starting a trick.

Trick reset:
- If a player makes a play and both other players pass consecutively, the next turn returns to the last player who played, and the trick resets (free lead).

---

## AI Behavior (Brief)

- Bidding:
  - Heuristic score considers Jokers, 2s, high ranks, triples/bombs, and straight potential.
  - Bids 0–3 depending on strength and whether it can outbid the current highest.

- Playing:
  - When starting a trick: prefers straights, sequences, or shedding multiple cards efficiently; may use a small bomb early.
  - When following: tries to minimally beat with the same type, then considers bombs/rocket if needed.
  - Will pass when it cannot or should not beat.

---

## Tips

- Avoid using high singles (2, Jokers) early unless needed.
- When leading, try sequences to shed many cards at once.
- Keep potential wings (singles or pairs) to support future triple sequences.
- Watch the log to deduce which high cards/bombs may still be out.

---

## Troubleshooting

- Tkinter not found:
  - Debian/Ubuntu: sudo apt-get install python3-tk
  - Fedora: sudo dnf install python3-tkinter
  - macOS: Use the official Python.org installer or Homebrew Python (Tk included). If needed: brew install python-tk@3.x (varies by OS).
- On WSL:
  - Install an X server (Xming/VcXsrv) on Windows and export DISPLAY in WSL: export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
- No window appears / crashes:
  - Ensure you run python main.py with a GUI-capable environment (not a headless server).
- Unicode suits not rendering correctly:
  - Change the font or simplify the display in gui.py if necessary. Suits are purely cosmetic.

---

## File Layout

- main.py — Entry point; starts the Tkinter app.
- gui.py — Tkinter UI, event handlers, rendering, and control enabling/disabling.
- game.py — Game engine: dealing, bidding, landlord assignment, turn order, pass/play logic, win detection, logging.
- rules.py — Combination detection and can-beat comparison for all supported patterns.
- ai.py — Simple heuristic AI for bidding and play decisions.
- models.py — Card/Deck models; rank labels and sorting; 54-card deck with 2 Jokers.
- requirements.txt — Notes that only standard library is used.

---

## Customization (Developers)

- Tuning AI:
  - ai.py: SimpleAI._hand_strength_score and decision thresholds in decide_bid().
  - Playing priorities in choose_play() and helper methods.

- Rule tweaks:
  - rules.py: identify_combination() and can_beat() centralize legality and comparisons.

- UI adjustments:
  - gui.py: Button labels, fonts, colors, and layout can be changed.
  - Game log size: update the slice in update_all() (currently shows last 200 entries).

- Start conditions:
  - game.py: start_new_round() sets initial bidder (Left AI by default). Adjust if you want the human to open bidding.

---

## Known Limitations

- No scoring/multipliers, no “double” (加倍), and no spring detection. The game declares a winner and ends the round.
- Single-round play only; no match ledger.
- One local human vs two AIs (no network multiplayer).
- Wings selection is automatic when AI plays; for humans, selection is manual.

---

## FAQ

- Can I sort cards manually?
  - Cards are auto-sorted by rank (then suit for display). Suits do not affect gameplay.

- Why can’t I pass sometimes?
  - You cannot pass when starting a trick (i.e., there’s no active combination to beat).

- Why is my play rejected?
  - Either the selected cards don’t form a valid combination, or they don’t beat the current play. Check the Last Play label and the Rule Reference above.

- Can I see the bottom cards?
  - The 3 bottom cards are added to the landlord’s hand and are not shown separately.

---

Enjoy playing Dou Dizhu! If you have feature requests or feedback, share them with the ChatDev team.