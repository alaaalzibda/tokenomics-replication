'''
Simple AI for Dou Dizhu: bidding strategy and play decisions.
Generates valid moves and selects heuristically to either start a trick or beat the previous play.
'''
from typing import List, Optional, Tuple
from collections import Counter
from models import Card, sort_cards
from rules import (
    Combination, identify_combination, can_beat,
    SINGLE, PAIR, TRIPLE, TRIPLE_SINGLE, TRIPLE_PAIR,
    STRAIGHT, PAIR_SEQUENCE, TRIPLE_SEQUENCE,
    TRIPLE_SEQUENCE_SINGLE, TRIPLE_SEQUENCE_PAIR,
    BOMB, ROCKET, FOUR_TWO_SINGLE, FOUR_TWO_PAIR
)
class SimpleAI:
    """
    Basic heuristic AI:
    - Bidding: evaluates hand strength and bids 0-3 accordingly.
    - Play: attempts to play the smallest winning combination, prefers sequences when starting.
    """
    def decide_bid(self, hand: List[Card], highest_bid: int) -> int:
        score = self._hand_strength_score(hand)
        # Translate score to bid proposal
        bid = 0
        if score >= 16:
            bid = 3
        elif score >= 11:
            bid = 2
        elif score >= 7:
            bid = 1
        else:
            bid = 0
        # Must exceed current highest
        if bid <= highest_bid:
            return 0
        return bid
    def _hand_strength_score(self, hand: List[Card]) -> int:
        ranks = [c.rank for c in hand]
        cnt = Counter(ranks)
        score = 0
        # Jokers
        score += 5 if 17 in cnt else 0
        score += 4 if 16 in cnt else 0
        # Twos
        score += 3 * cnt.get(15, 0)
        # High cards
        score += 2 * (cnt.get(14, 0) + cnt.get(13, 0))
        # Triples and bombs
        score += 3 * sum(1 for r in cnt if cnt[r] >= 3)
        score += 5 * sum(1 for r in cnt if cnt[r] == 4)
        # Straight potential (unique ranks exc 2/jokers)
        base = sorted(set(r for r in cnt.keys() if 3 <= r <= 14))
        longest = self._longest_run(base)
        score += max(0, longest - 4)  # bonus for long straight (length >=5)
        return score
    def _longest_run(self, values: List[int]) -> int:
        if not values:
            return 0
        longest = cur = 1
        for a, b in zip(values, values[1:]):
            if b == a + 1:
                cur += 1
                longest = max(longest, cur)
            else:
                cur = 1
        return longest
    def choose_play(self, hand: List[Card], last_comb: Optional[Combination], is_start: bool) -> Optional[List[Card]]:
        """
        Returns list of cards to play, or None to pass.
        """
        # Sort hand for predictability
        hand = sort_cards(hand)
        if is_start or last_comb is None:
            # Start a new trick: prefer to shed more cards
            # Try: straight -> pair-seq -> triple-seq -> triple(with attachments) -> pair -> single
            for gen in (self._find_low_straight_start,
                        self._find_low_pair_sequence_start,
                        self._find_low_triple_sequence_start,
                        self._find_triple_with_attachment_start,
                        self._find_low_pair_start,
                        self._find_low_single_start,
                        self._find_bomb_if_small):
                play = gen(hand)
                if play:
                    return play
            return self._find_rocket(hand)  # last resort
        else:
            # Need to beat last_comb
            # Try to find same type and minimal beating
            play = self._find_to_beat(hand, last_comb)
            if play:
                return play
            # If cannot beat, consider bombs
            if last_comb.type not in (BOMB, ROCKET):
                bomb = self._find_bomb_to_beat(hand, None)
                if bomb:
                    return bomb
                rocket = self._find_rocket(hand)
                if rocket:
                    return rocket
            elif last_comb.type == BOMB:
                bomb = self._find_bomb_to_beat(hand, last_comb)
                if bomb:
                    return bomb
                rocket = self._find_rocket(hand)
                if rocket:
                    return rocket
            # Otherwise pass
            return None
    # Starting helpers (attempt to construct a good starting play)
    def _find_low_single_start(self, hand: List[Card]) -> Optional[List[Card]]:
        # Avoid discarding 2 or jokers if possible
        candidates = [c for c in hand if c.rank <= 14]
        if not candidates:
            candidates = hand[:]
        return [candidates[0]] if candidates else None
    def _find_low_pair_start(self, hand: List[Card]) -> Optional[List[Card]]:
        ranks = Counter(c.rank for c in hand)
        pairs = sorted([r for r, cnt in ranks.items() if cnt >= 2])
        pairs = [r for r in pairs if r <= 14] or pairs  # prefer below 2
        if pairs:
            r = pairs[0]
            cards = [c for c in hand if c.rank == r][:2]
            return cards
        return None
    def _find_triple_with_attachment_start(self, hand: List[Card]) -> Optional[List[Card]]:
        ranks = Counter(c.rank for c in hand)
        triples = sorted([r for r, cnt in ranks.items() if cnt >= 3 and 3 <= r <= 14])
        if triples:
            tr = triples[0]
            # Try triple + single
            triple_cards = [c for c in hand if c.rank == tr][:3]
            singles = [c for c in hand if c.rank != tr]
            singles = [c for c in singles if not (c.rank >= 16)] + [c for c in singles if c.rank >= 16]
            if singles:
                comb = triple_cards + [singles[0]]
                if identify_combination(comb):
                    return comb
            # Try triple alone
            return triple_cards
        return None
    def _find_low_straight_start(self, hand: List[Card]) -> Optional[List[Card]]:
        ranks = sorted(set(c.rank for c in hand if 3 <= c.rank <= 14))
        # find minimal straight length >=5
        for length in range(5, 13):  # up to A-high is fine
            for i in range(0, len(ranks) - length + 1):
                seq = ranks[i:i+length]
                if all(seq[j] + 1 == seq[j+1] for j in range(len(seq)-1)):
                    # build card list taking 1 of each
                    chosen = []
                    for r in seq:
                        for c in hand:
                            if c.rank == r and c not in chosen:
                                chosen.append(c)
                                break
                    if identify_combination(chosen):
                        return chosen
        return None
    def _find_low_pair_sequence_start(self, hand: List[Card]) -> Optional[List[Card]]:
        cnt = Counter(c.rank for c in hand)
        ranks = sorted([r for r, n in cnt.items() if 3 <= r <= 14 and n >= 2])
        # find minimal length >= 3 pairs
        for length in range(3, 11):
            for i in range(0, len(ranks) - length + 1):
                seq = ranks[i:i+length]
                if all(seq[j] + 1 == seq[j+1] for j in range(len(seq)-1)):
                    chosen = []
                    for r in seq:
                        chosen.extend([c for c in hand if c.rank == r][:2])
                    if identify_combination(chosen):
                        return chosen
        return None
    def _find_low_triple_sequence_start(self, hand: List[Card]) -> Optional[List[Card]]:
        cnt = Counter(c.rank for c in hand)
        ranks = sorted([r for r, n in cnt.items() if 3 <= r <= 14 and n >= 3])
        for length in range(2, 7):
            for i in range(0, len(ranks) - length + 1):
                seq = ranks[i:i+length]
                if all(seq[j] + 1 == seq[j+1] for j in range(len(seq)-1)):
                    chosen = []
                    for r in seq:
                        chosen.extend([c for c in hand if c.rank == r][:3])
                    if identify_combination(chosen):
                        return chosen
        return None
    def _find_bomb_if_small(self, hand: List[Card]) -> Optional[List[Card]]:
        ranks = Counter(c.rank for c in hand)
        bombs = sorted([r for r, cnt in ranks.items() if cnt == 4])
        if bombs:
            r = bombs[0]
            return [c for c in hand if c.rank == r][:4]
        return None
    def _find_rocket(self, hand: List[Card]) -> Optional[List[Card]]:
        sj = [c for c in hand if c.rank == 16]
        bj = [c for c in hand if c.rank == 17]
        if sj and bj:
            return [sj[0], bj[0]]
        return None
    # Beating logic
    def _find_to_beat(self, hand: List[Card], last: Combination) -> Optional[List[Card]]:
        t = last.type
        if t == SINGLE:
            return self._beat_single(hand, last.main_rank)
        if t == PAIR:
            return self._beat_pair(hand, last.main_rank)
        if t == TRIPLE:
            return self._beat_triple(hand, last.main_rank)
        if t == TRIPLE_SINGLE:
            return self._beat_triple_single(hand, last.main_rank)
        if t == TRIPLE_PAIR:
            return self._beat_triple_pair(hand, last.main_rank)
        if t == STRAIGHT:
            return self._beat_straight(hand, last.length, last.main_rank)
        if t == PAIR_SEQUENCE:
            return self._beat_pair_sequence(hand, last.length, last.main_rank)
        if t == TRIPLE_SEQUENCE:
            return self._beat_triple_sequence(hand, last.length, last.main_rank)
        if t == TRIPLE_SEQUENCE_SINGLE:
            return self._beat_triple_sequence_with_wings(hand, last.length, last.main_rank, wings="single")
        if t == TRIPLE_SEQUENCE_PAIR:
            return self._beat_triple_sequence_with_wings(hand, last.length, last.main_rank, wings="pair")
        if t == BOMB:
            return self._find_bomb_to_beat(hand, last)
        if t == ROCKET:
            return None
        if t == FOUR_TWO_SINGLE:
            return self._beat_four_two_single(hand, last.main_rank)
        if t == FOUR_TWO_PAIR:
            return self._beat_four_two_pair(hand, last.main_rank)
        return None
    def _beat_single(self, hand: List[Card], rank: int) -> Optional[List[Card]]:
        candidates = [c for c in hand if c.rank > rank]
        candidates = sorted(candidates, key=lambda c: (c.rank, c.sort_key()[1]))
        for c in candidates:
            return [c]
        return None
    def _beat_pair(self, hand: List[Card], rank: int) -> Optional[List[Card]]:
        cnt = Counter(c.rank for c in hand)
        pairs = sorted([r for r, c in cnt.items() if c >= 2 and r > rank])
        if pairs:
            r = pairs[0]
            return [c for c in hand if c.rank == r][:2]
        return None
    def _beat_triple(self, hand: List[Card], rank: int) -> Optional[List[Card]]:
        cnt = Counter(c.rank for c in hand)
        triples = sorted([r for r, c in cnt.items() if c >= 3 and r > rank])
        if triples:
            r = triples[0]
            return [c for c in hand if c.rank == r][:3]
        return None
    def _beat_triple_single(self, hand: List[Card], rank: int) -> Optional[List[Card]]:
        cnt = Counter(c.rank for c in hand)
        triples = sorted([r for r, c in cnt.items() if c >= 3 and r > rank])
        for tr in triples:
            triple_cards = [c for c in hand if c.rank == tr][:3]
            singles = [c for c in hand if c.rank != tr]
            singles.sort(key=lambda c: (c.rank, c.sort_key()[1]))
            if singles:
                comb = triple_cards + [singles[0]]
                if identify_combination(comb):
                    return comb
        return None
    def _beat_triple_pair(self, hand: List[Card], rank: int) -> Optional[List[Card]]:
        cnt = Counter(c.rank for c in hand)
        triples = sorted([r for r, c in cnt.items() if c >= 3 and r > rank])
        for tr in triples:
            triple_cards = [c for c in hand if c.rank == tr][:3]
            pairs = [r for r, c in cnt.items() if c >= 2 and r != tr]
            pairs.sort()
            if pairs:
                pair_cards = [c for c in hand if c.rank == pairs[0]][:2]
                comb = triple_cards + pair_cards
                if identify_combination(comb):
                    return comb
        return None
    def _beat_straight(self, hand: List[Card], length: int, max_rank: int) -> Optional[List[Card]]:
        avail = Counter(c.rank for c in hand)
        base = sorted([r for r in set(avail.keys()) if 3 <= r <= 14])
        for i in range(0, len(base) - length + 1):
            seq = base[i:i+length]
            if all(seq[j] + 1 == seq[j+1] for j in range(len(seq)-1)):
                if max(seq) > max_rank:
                    chosen = []
                    for r in seq:
                        chosen.append([c for c in hand if c.rank == r][0])
                    return chosen
        return None
    def _beat_pair_sequence(self, hand: List[Card], pairs_len: int, max_rank: int) -> Optional[List[Card]]:
        cnt = Counter(c.rank for c in hand)
        base = sorted([r for r in cnt if cnt[r] >= 2 and 3 <= r <= 14])
        for i in range(0, len(base) - pairs_len + 1):
            seq = base[i:i+pairs_len]
            if all(seq[j] + 1 == seq[j+1] for j in range(len(seq)-1)):
                if max(seq) > max_rank:
                    chosen = []
                    for r in seq:
                        chosen.extend([c for c in hand if c.rank == r][:2])
                    return chosen
        return None
    def _beat_triple_sequence(self, hand: List[Card], triples_len: int, max_rank: int) -> Optional[List[Card]]:
        cnt = Counter(c.rank for c in hand)
        base = sorted([r for r in cnt if cnt[r] >= 3 and 3 <= r <= 14])
        for i in range(0, len(base) - triples_len + 1):
            seq = base[i:i+triples_len]
            if all(seq[j] + 1 == seq[j+1] for j in range(len(seq)-1)):
                if max(seq) > max_rank:
                    chosen = []
                    for r in seq:
                        chosen.extend([c for c in hand if c.rank == r][:3])
                    return chosen
        return None
    def _beat_triple_sequence_with_wings(self, hand: List[Card], triples_len: int, max_rank: int, wings: str) -> Optional[List[Card]]:
        # Construct triple sequence then add needed wings from leftovers
        cnt = Counter(c.rank for c in hand)
        base = sorted([r for r in cnt if cnt[r] >= 3 and 3 <= r <= 14])
        for i in range(0, len(base) - triples_len + 1):
            seq = base[i:i+triples_len]
            if all(seq[j] + 1 == seq[j+1] for j in range(len(seq)-1)) and max(seq) > max_rank:
                triple_cards = []
                for r in seq:
                    triple_cards.extend([c for c in hand if c.rank == r][:3])
                leftover = [c for c in hand if c.rank not in seq]
                if wings == "single":
                    if len(leftover) >= triples_len:
                        # choose lowest singles
                        chosen = triple_cards + leftover[:triples_len]
                        if identify_combination(chosen):
                            return chosen
                else:
                    # wings pairs
                    left_cnt = Counter(c.rank for c in leftover)
                    pair_ranks = []
                    for r, v in sorted(left_cnt.items()):
                        if v >= 2:
                            pair_ranks.append(r)
                        if len(pair_ranks) >= triples_len:
                            break
                    if len(pair_ranks) >= triples_len:
                        chosen = triple_cards[:]
                        for r in pair_ranks[:triples_len]:
                            chosen.extend([c for c in leftover if c.rank == r][:2])
                        if identify_combination(chosen):
                            return chosen
        return None
    def _beat_four_two_single(self, hand: List[Card], main_rank: int) -> Optional[List[Card]]:
        """
        Beat a 'four with two singles' by using a higher four-of-a-kind and any two singles from leftovers.
        """
        cnt = Counter(c.rank for c in hand)
        candidates = sorted([r for r, v in cnt.items() if v == 4 and r > main_rank])
        for r in candidates:
            four_cards = [c for c in hand if c.rank == r][:4]
            leftovers = [c for c in hand if c.rank != r]
            if len(leftovers) >= 2:
                attempt = four_cards + leftovers[:2]
                if identify_combination(attempt):
                    return attempt
        return None
    def _beat_four_two_pair(self, hand: List[Card], main_rank: int) -> Optional[List[Card]]:
        """
        Beat a 'four with two pairs' by using a higher four-of-a-kind and any two pairs from leftovers.
        """
        cnt = Counter(c.rank for c in hand)
        candidates = sorted([r for r, v in cnt.items() if v == 4 and r > main_rank])
        for r in candidates:
            four_cards = [c for c in hand if c.rank == r][:4]
            leftovers = [c for c in hand if c.rank != r]
            left_cnt = Counter(c.rank for c in leftovers)
            pair_ranks = [pr for pr, v in sorted(left_cnt.items()) if v >= 2]
            if len(pair_ranks) >= 2:
                chosen = four_cards[:]
                for pr in pair_ranks[:2]:
                    chosen.extend([c for c in leftovers if c.rank == pr][:2])
                if identify_combination(chosen):
                    return chosen
        return None
    def _find_bomb_to_beat(self, hand: List[Card], last: Optional[Combination]) -> Optional[List[Card]]:
        cnt = Counter(c.rank for c in hand)
        bombs = sorted([r for r, c in cnt.items() if c == 4])
        if last is None:
            if bombs:
                r = bombs[0]
                return [c for c in hand if c.rank == r][:4]
            return None
        else:
            higher = [r for r in bombs if r > last.main_rank]
            if higher:
                r = higher[0]
                return [c for c in hand if c.rank == r][:4]
        return None