'''
Rules and combination detection/comparison for Dou Dizhu (Landlord). Supports identification of combinations, 
and comparison logic for pass-or-beat mechanics.
'''
from collections import Counter
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from models import Card
# Combination types
SINGLE = "SINGLE"
PAIR = "PAIR"
TRIPLE = "TRIPLE"
TRIPLE_SINGLE = "TRIPLE_SINGLE"
TRIPLE_PAIR = "TRIPLE_PAIR"
STRAIGHT = "STRAIGHT"  # sequence of singles, len >= 5, no 2 or jokers
PAIR_SEQUENCE = "PAIR_SEQUENCE"  # sequence of pairs, >= 3 pairs, no 2 or jokers
TRIPLE_SEQUENCE = "TRIPLE_SEQUENCE"  # sequence of triples, >= 2 triples, no 2 or jokers
TRIPLE_SEQUENCE_SINGLE = "TRIPLE_SEQUENCE_SINGLE"  # airplane with single wings
TRIPLE_SEQUENCE_PAIR = "TRIPLE_SEQUENCE_PAIR"  # airplane with pair wings
BOMB = "BOMB"  # four of a kind
ROCKET = "ROCKET"  # both jokers
FOUR_TWO_SINGLE = "FOUR_TWO_SINGLE"  # 4 + 2 singles
FOUR_TWO_PAIR = "FOUR_TWO_PAIR"  # 4 + 2 pairs
VALID_TYPES = {
    SINGLE, PAIR, TRIPLE, TRIPLE_SINGLE, TRIPLE_PAIR, STRAIGHT,
    PAIR_SEQUENCE, TRIPLE_SEQUENCE, TRIPLE_SEQUENCE_SINGLE, TRIPLE_SEQUENCE_PAIR,
    BOMB, ROCKET, FOUR_TWO_SINGLE, FOUR_TWO_PAIR
}
# Rank boundaries for sequences: cannot include ranks >= 15 (i.e., 2, jokers)
MIN_SEQ_RANK = 3
MAX_SEQ_RANK = 14  # A
@dataclass
class Combination:
    """
    Describes a Dou Dizhu combination.
    - type: combination type string
    - main_rank: main comparison rank (e.g., highest in straight, rank of triple, bomb four rank)
    - length: for sequences, number of groups (e.g., straight length in cards, pair-seq length in pairs, triple-seq length in triples)
    - extra: optional details (dict) about attachments etc.
    - cards: the cards composing the combination (for display/verification)
    """
    type: str
    main_rank: int
    length: int
    cards: List[Card]
    extra: Optional[Dict] = None
def _ranks(cards: List[Card]) -> List[int]:
    return [c.rank for c in cards]
def _is_consecutive(ranks: List[int]) -> bool:
    return all(b == a + 1 for a, b in zip(ranks, ranks[1:]))
def _valid_seq_ranks(ranks: List[int]) -> bool:
    # All ranks must be between 3 and A (no 2 or jokers)
    return all(MIN_SEQ_RANK <= r <= MAX_SEQ_RANK for r in ranks)
def _group_by_rank(cards: List[Card]) -> Dict[int, List[Card]]:
    by = {}
    for c in cards:
        by.setdefault(c.rank, []).append(c)
    return by
def identify_combination(cards: List[Card]) -> Optional[Combination]:
    """
    Given a list of cards, identify the combination type according to Dou Dizhu rules.
    Returns a Combination if valid, otherwise None.
    """
    if not cards:
        return None
    n = len(cards)
    ranks = sorted(_ranks(cards))
    by = _group_by_rank(cards)
    counts = sorted((len(v) for v in by.values()), reverse=True)
    count_map = Counter(ranks)
    # Single
    if n == 1:
        return Combination(SINGLE, ranks[0], 1, list(cards))
    # Two cards: pair or rocket
    if n == 2:
        if ranks[0] == 16 and ranks[1] == 17:
            return Combination(ROCKET, 17, 2, list(cards))
        if ranks[0] == ranks[1]:
            return Combination(PAIR, ranks[0], 1, list(cards))
        return None
    # Three cards: triple
    if n == 3:
        if len(by) == 1:
            return Combination(TRIPLE, ranks[0], 1, list(cards))
        return None
    # Four cards: bomb or triple + single
    if n == 4:
        if len(by) == 1:
            return Combination(BOMB, ranks[0], 1, list(cards))
        if 3 in counts and 1 in counts and len(by) == 2:
            # identify triple rank
            triple_rank = max(by.keys(), key=lambda r: len(by[r]))
            return Combination(TRIPLE_SINGLE, triple_rank, 1, list(cards))
        return None
    # Check complex combinations and sequences
    # Straight: all distinct ranks, length >= 5, consecutive, ranks in [3..A]
    if len(by) == n and n >= 5:
        if _valid_seq_ranks(ranks) and _is_consecutive(ranks):
            return Combination(STRAIGHT, max(ranks), n, list(cards))
    # Triple + pair
    if n == 5 and 3 in counts and 2 in counts and len(by) == 2:
        triple_rank = max(by.keys(), key=lambda r: len(by[r]))
        return Combination(TRIPLE_PAIR, triple_rank, 1, list(cards))
    # Pair sequence: all ranks have count 2, even number of cards, at least 3 pairs, consecutive ranks (no 2/jokers)
    if n % 2 == 0:
        pair_groups = [r for r, cs in by.items() if len(cs) == 2]
        if len(pair_groups) * 2 == n and len(pair_groups) >= 3:
            ps = sorted(pair_groups)
            if _valid_seq_ranks(ps) and _is_consecutive(ps):
                return Combination(PAIR_SEQUENCE, max(ps), len(pair_groups), list(cards))
    # Triple sequence without wings: all ranks count 3, length >= 2 triples, consecutive triple ranks (no 2/jokers)
    if n % 3 == 0:
        triple_groups = [r for r, cs in by.items() if len(cs) == 3]
        if len(triple_groups) * 3 == n and len(triple_groups) >= 2:
            ts = sorted(triple_groups)
            if _valid_seq_ranks(ts) and _is_consecutive(ts):
                return Combination(TRIPLE_SEQUENCE, max(ts), len(triple_groups), list(cards))
    # Four with two singles
    if n == 6:
        four_ranks = [r for r, cs in by.items() if len(cs) == 4]
        if len(four_ranks) == 1:
            # Remaining must be two singles
            if sum(1 for r, cs in by.items() if len(cs) == 1) == 2:
                return Combination(FOUR_TWO_SINGLE, four_ranks[0], 1, list(cards))
    # Four with two pairs
    if n == 8:
        four_ranks = [r for r, cs in by.items() if len(cs) == 4]
        if len(four_ranks) == 1:
            if sum(1 for r, cs in by.items() if len(cs) == 2) == 2:
                return Combination(FOUR_TWO_PAIR, four_ranks[0], 1, list(cards))
    # Triple sequence with single wings: length divisible by 4
    if n % 4 == 0 and n >= 8:
        m = n // 4  # number of triples in sequence
        triple_groups = [r for r, cs in by.items() if len(cs) >= 3]
        # try to find a consecutive run of length m within triple_groups excluding 2/jokers
        base = sorted([r for r in triple_groups if MIN_SEQ_RANK <= r <= MAX_SEQ_RANK])
        # scan consecutive runs
        run = _find_consecutive_run_with_min_length(base, m)
        if run and len(run) == m:
            # Count available singles after removing triples, EXCLUDING ranks of the triple run (no wings from same ranks)
            leftover_counts = count_map.copy()
            for tr in run:
                leftover_counts[tr] -= 3
            singles_count = sum(cnt for r, cnt in leftover_counts.items() if r not in run and cnt > 0)
            if singles_count >= m:
                return Combination(TRIPLE_SEQUENCE_SINGLE, max(run), m, list(cards), extra={'triples': run})
    # Triple sequence with pair wings: length divisible by 5
    if n % 5 == 0 and n >= 10:
        m = n // 5
        triple_groups = [r for r, cs in by.items() if len(cs) >= 3]
        base = sorted([r for r in triple_groups if MIN_SEQ_RANK <= r <= MAX_SEQ_RANK])
        run = _find_consecutive_run_with_min_length(base, m)
        if run and len(run) == m:
            leftover_counts = count_map.copy()
            for tr in run:
                leftover_counts[tr] -= 3
            # count pairs in leftover EXCLUDING triple run ranks (wings cannot use same ranks)
            pair_units = sum(leftover_counts[r] // 2 for r in leftover_counts.keys() if r not in run)
            if pair_units >= m:
                return Combination(TRIPLE_SEQUENCE_PAIR, max(run), m, list(cards), extra={'triples': run})
    return None
def _find_consecutive_run_with_min_length(values: List[int], length: int) -> Optional[List[int]]:
    """
    From a sorted list of values, find a consecutive run of exact length.
    Returns the first such run (lowest), else None.
    """
    if len(values) < length:
        return None
    # sliding window
    for i in range(0, len(values) - length + 1):
        window = values[i:i+length]
        if _is_consecutive(window):
            return window
    return None
def can_beat(new_comb: Combination, prev_comb: Optional[Combination]) -> bool:
    """
    Returns True if new_comb legally beats prev_comb under Dou Dizhu rules.
    If prev_comb is None, any valid combination can be played.
    """
    if new_comb is None:
        return False
    if prev_comb is None:
        return True
    # Rocket beats everything and cannot be beaten
    if prev_comb.type == ROCKET:
        return False
    if new_comb.type == ROCKET:
        return True
    # Bomb logic
    if prev_comb.type == BOMB:
        if new_comb.type == BOMB:
            return new_comb.main_rank > prev_comb.main_rank
        else:
            return False
    if new_comb.type == BOMB:
        return True  # beats any non-bomb non-rocket
    # Non-bomb/rocket: must be same type and compatible length
    if new_comb.type != prev_comb.type:
        return False
    # For sequences and complex combos, additional length constraints apply
    if new_comb.type in (STRAIGHT,):
        return new_comb.length == prev_comb.length and new_comb.main_rank > prev_comb.main_rank
    if new_comb.type in (PAIR_SEQUENCE,):
        return new_comb.length == prev_comb.length and new_comb.main_rank > prev_comb.main_rank
    if new_comb.type in (TRIPLE_SEQUENCE,):
        return new_comb.length == prev_comb.length and new_comb.main_rank > prev_comb.main_rank
    if new_comb.type in (TRIPLE_SEQUENCE_SINGLE, TRIPLE_SEQUENCE_PAIR):
        # compare by number of triples and main rank
        return new_comb.length == prev_comb.length and new_comb.main_rank > prev_comb.main_rank
    if new_comb.type in (FOUR_TWO_SINGLE, FOUR_TWO_PAIR):
        # must be same type; compare four rank
        return new_comb.main_rank > prev_comb.main_rank
    if new_comb.type in (TRIPLE, TRIPLE_SINGLE, TRIPLE_PAIR):
        return new_comb.main_rank > prev_comb.main_rank
    if new_comb.type in (PAIR, SINGLE):
        return new_comb.main_rank > prev_comb.main_rank
    return False