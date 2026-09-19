'''
Provides the crossword puzzle dataset(s). For this application,
we include a fully consistent 5x5 "Sator Square" puzzle. The grid
has no black squares; each across word is identical to the down
word at the same order, ensuring valid crossings.
New: Clues are also provided keyed by clue number and direction for
robustness and realistic crossword support. The numbering for this
grid is:
- Across: 1(SATOR), 6(AREPO), 7(TENET), 8(OPERA), 9(ROTAS)
- Down:   1(SATOR), 2(AREPO), 3(TENET), 4(OPERA), 5(ROTAS)
The puzzle includes:
- solution_rows: the final letter layout for the grid
- across_clues_by_number: clue texts keyed by the across clue number
- down_clues_by_number: clue texts keyed by the down clue number
- across_clues_by_answer: legacy fallback, clues keyed by the across answer text
- down_clues_by_answer: legacy fallback, clues keyed by the down answer text
'''
def get_puzzle():
    """
    Returns a dictionary describing a crossword puzzle, including
    the solution rows and clue texts for across and down answers.
    """
    solution_rows = [
        "SATOR",
        "AREPO",
        "TENET",
        "OPERA",
        "ROTAS",
    ]
    # Preferred, robust numbering-based clues
    across_clues_by_number = {
        1: 'Latin "sower"; starts the famous square',
        6: "Mysterious name from the Sator square",
        7: "Belief or principle",
        8: "Stage works set to music",
        9: "Wheels, in Latin",
    }
    down_clues_by_number = {
        1: "Starts the Latin word square",
        2: "Name found in the palindromic Latin square",
        3: "Doctrine",
        4: "Grand musical works",
        5: "Rotating things, in Latin",
    }
    # Legacy fallback (by answer text)
    across_clues_by_answer = {
        "SATOR": 'Latin "sower"; starts the famous square',
        "AREPO": "Mysterious name from the Sator square",
        "TENET": "Belief or principle",
        "OPERA": "Stage works set to music",
        "ROTAS": "Wheels, in Latin",
    }
    down_clues_by_answer = {
        "SATOR": "Starts the Latin word square",
        "AREPO": "Name found in the palindromic Latin square",
        "TENET": "Doctrine",
        "OPERA": "Grand musical works",
        "ROTAS": "Rotating things, in Latin",
    }
    return {
        "name": "Sator Square Mini (5x5)",
        "solution_rows": solution_rows,
        "across_clues_by_number": across_clues_by_number,
        "down_clues_by_number": down_clues_by_number,
        "across_clues_by_answer": across_clues_by_answer,
        "down_clues_by_answer": down_clues_by_answer,
    }