'''
Puzzle logic for the "Strands" word-segmentation game.
Includes puzzle data bank, segment generation, normalization, and merge verification.
'''
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import random
import difflib
import re
def normalize(s: str) -> str:
    """
    Normalizes a phrase for matching: lowercase, remove spaces and punctuation.
    Keeps alphanumeric characters only.
    """
    return re.sub(r"[^a-z0-9]", "", s.lower())
@dataclass
class Segment:
    """
    Represents a single strand segment.
    """
    id: str
    text: str
    phrase_index: int
    seg_index: int
    def to_dict(self) -> Dict:
        """
        Returns a dict suitable for JSON serialization to the client.
        """
        return {
            "id": self.id,
            "text": self.text,
            "phrase_index": self.phrase_index,
            "seg_index": self.seg_index,
        }
@dataclass
class StrandPuzzle:
    """
    A Strands puzzle: theme, set of target phrases/words, and generated segments.
    Segments are created by splitting each phrase (letters only) into 2-4 character chunks,
    and then shuffling across all phrases.
    """
    id: str
    theme: str
    phrases: List[str]
    segments: List[Segment] = field(default_factory=list)
    phrase_segments_map: Dict[int, List[str]] = field(default_factory=dict)
    def __post_init__(self):
        """
        Build segments deterministically based on puzzle ID.
        """
        self.build_segments()
    def build_segments(self) -> None:
        """
        Generate segments for each phrase and shuffle across the puzzle.
        Uses a deterministic random seed from the puzzle id for reproducibility.
        """
        rng = random.Random(self.id)
        all_segments: List[Segment] = []
        phrase_segments_map: Dict[int, List[str]] = {}
        for p_idx, phrase in enumerate(self.phrases):
            letters = normalize(phrase)
            parts = self._split_into_segments(letters, rng)
            seg_ids_for_phrase = []
            for s_idx, part in enumerate(parts):
                seg_id = f"{self.id}-{p_idx}-{s_idx}"
                seg_ids_for_phrase.append(seg_id)
                all_segments.append(Segment(id=seg_id, text=part, phrase_index=p_idx, seg_index=s_idx))
            phrase_segments_map[p_idx] = seg_ids_for_phrase
        rng.shuffle(all_segments)
        self.segments = all_segments
        self.phrase_segments_map = phrase_segments_map
    @staticmethod
    def _split_into_segments(s: str, rng: random.Random) -> List[str]:
        """
        Splits a string into 2-4 length segments with no leftover of length 1.
        Ensures at least two segments for strings of length >= 4.
        """
        n = len(s)
        if n <= 3:
            # For very short strings, return as one piece (edge case).
            return [s]
        if n == 4:
            return [s[:2], s[2:]]
        parts: List[str] = []
        i = 0
        while i < n:
            remaining = n - i
            if remaining <= 4:
                length = remaining
            else:
                min_len, max_len = 2, 4
                length = rng.randint(min_len, max_len)
                # Avoid leaving a remainder of 1
                if remaining - length == 1:
                    if length < max_len:
                        length += 1
                    else:
                        length -= 1
                # If we accidentally made last chunk too small, adjust
                if (remaining - length) != 0 and (remaining - length) < 2:
                    length = remaining - 2
            parts.append(s[i : i + length])
            i += length
        # Ensure at least two parts if possible
        if len(parts) == 1 and n >= 4:
            return [s[: n // 2], s[n // 2 :]]
        return parts
    def to_dict(self) -> Dict:
        """
        Returns a dictionary representation of the puzzle suitable for JSON.
        """
        return {
            "id": self.id,
            "theme": self.theme,
            "phrases": self.phrases,
            "segments": [seg.to_dict() for seg in self.segments],
            "phrase_segments_map": self.phrase_segments_map,
        }
class PuzzleBank:
    """
    Holds multiple pre-defined puzzles and provides access by id or random choice.
    """
    def __init__(self):
        self._puzzles: Dict[str, StrandPuzzle] = {}
        self._load()
    def _load(self) -> None:
        """
        Defines a set of themed puzzles. In a production system, these could come from a database or file.
        """
        puzzles_seed = [
            StrandPuzzle(
                id="fruits1",
                theme="Fruits",
                phrases=["apple", "banana", "cherry", "grape", "orange", "pear"],
            ),
            StrandPuzzle(
                id="cafe1",
                theme="Cafe Menu",
                phrases=["espresso", "cappuccino", "latte", "americano", "macchiato", "mocha"],
            ),
            StrandPuzzle(
                id="tech1",
                theme="Tech Buzzwords",
                phrases=[
                    "machine learning",
                    "artificial intelligence",
                    "data science",
                    "neural network",
                    "big data",
                    "deep learning",
                ],
            ),
        ]
        self._puzzles = {p.id: p for p in puzzles_seed}
    def all_ids(self) -> List[str]:
        """
        Returns all available puzzle IDs.
        """
        return list(self._puzzles.keys())
    def get_by_id(self, puzzle_id: str) -> Optional[StrandPuzzle]:
        """
        Returns a puzzle by id, or None if not found.
        """
        return self._puzzles.get(puzzle_id)
    def random_puzzle(self) -> StrandPuzzle:
        """
        Returns a random puzzle.
        """
        return random.choice(list(self._puzzles.values()))
def verify_merge(puzzle: StrandPuzzle, selected_ids: List[str]) -> Dict:
    """
    Verifies whether the selected segments form:
    - A full valid phrase (status="ok")
    - A valid partial path toward a phrase (status="partial")
    - An invalid merge (status="invalid") with helpful feedback.
    Rules:
    - To be valid, all segments must belong to the same phrase and be in correct order.
    - A full valid solution must exactly match the full set of segments for that phrase.
    """
    if not selected_ids:
        return {"status": "invalid", "message": "No strands selected."}
    # Map segments for quick access
    seg_by_id = {seg.id: seg for seg in puzzle.segments}
    segments: List[Segment] = []
    for sid in selected_ids:
        if sid not in seg_by_id:
            # The segment might be already used and not present; build a temporary from phrase map
            found = _segment_from_any(puzzle, sid)
            if not found:
                return {"status": "invalid", "message": "Unknown strand selected."}
            segments.append(found)
        else:
            segments.append(seg_by_id[sid])
    # Check single phrase constraint
    phrase_indices = {seg.phrase_index for seg in segments}
    if len(phrase_indices) != 1:
        # Provide helpful hint: most common phrase among selected vs others
        msg = "Those strands come from different words/phrases. Try sticking to one at a time."
        # Suggest the nearest phrase by concatenation similarity
        concat = "".join(seg.text for seg in segments)
        nearest, ratio = _nearest_phrase(puzzle, concat)
        if nearest and ratio >= 0.5:
            msg += f" Your merge looks close to: “{nearest}”."
        return {"status": "invalid", "message": msg}
    phrase_index = segments[0].phrase_index
    target_seg_ids = puzzle.phrase_segments_map[phrase_index]
    # Extract ordered seg indices from the selection
    selected_seg_indices = [seg.seg_index for seg in segments]
    # Check if selected are in strictly increasing order and contiguous
    increasing_order = all(
        selected_seg_indices[i] + 1 == selected_seg_indices[i + 1]
        for i in range(len(selected_seg_indices) - 1)
    )
    if increasing_order:
        start_idx = selected_seg_indices[0]
        end_idx = selected_seg_indices[-1]
        expected_ids_full = target_seg_ids
        selected_ids_ordered = [seg.id for seg in segments]
        # Full match must start at 0 and end at last
        if start_idx == 0 and end_idx == len(target_seg_ids) - 1 and selected_ids_ordered == expected_ids_full:
            solved_phrase = puzzle.phrases[phrase_index]
            return {
                "status": "ok",
                "message": f"Great! You found: “{solved_phrase}”.",
                "phrase_index": phrase_index,
                "solved_phrase": solved_phrase,
            }
        # Partial prefix or middle segment sequence
        if start_idx == 0:
            # Valid prefix of the correct phrase
            assembled = "".join(seg.text for seg in segments)
            return {
                "status": "partial",
                "message": f"Good path! You have a valid beginning of “{puzzle.phrases[phrase_index]}”. Keep going.",
                "assembled": assembled,
                "phrase_index": phrase_index,
            }
        else:
            # Valid contiguous middle/end, but not starting from the first piece
            return {
                "status": "partial",
                "message": "Nice connection! These pieces fit together within a word/phrase. Try adding the missing beginning.",
                "phrase_index": phrase_index,
            }
    # If not increasing and contiguous, check if reordering might help
    if len(set(selected_seg_indices)) == len(selected_seg_indices) and _are_same_phrase(segments):
        # They belong to the same phrase but are out of order or non-contiguous
        return {
            "status": "invalid",
            "message": "These strands belong to the same word/phrase, but the order seems off.",
        }
    # General invalid feedback with nearest suggestion
    concat = "".join(seg.text for seg in segments)
    nearest, ratio = _nearest_phrase(puzzle, concat)
    hint = ""
    if nearest and ratio >= 0.5:
        hint = f" It resembles: “{nearest}”."
    return {"status": "invalid", "message": f"That merge doesn’t form a target." + hint}
def _segment_from_any(puzzle: StrandPuzzle, seg_id: str) -> Optional[Segment]:
    """
    Attempts to reconstruct a Segment from seg_id if it is not present in puzzle.segments
    (e.g., already used). To preserve deterministic behavior, we must advance the RNG
    through all phrases up to the requested phrase index, because the splitter uses
    randomness per call with a shared RNG seeded by puzzle.id.
    """
    try:
        _, p_idx_s, s_idx_s = seg_id.split("-")
        p_idx = int(p_idx_s)
        s_idx = int(s_idx_s)
    except Exception:
        return None
    rng = random.Random(puzzle.id)
    parts_for_target: Optional[List[str]] = None
    for idx, phrase in enumerate(puzzle.phrases):
        letters = normalize(phrase)
        parts = StrandPuzzle._split_into_segments(letters, rng)
        if idx == p_idx:
            parts_for_target = parts
            break
    if parts_for_target is None or s_idx < 0 or s_idx >= len(parts_for_target):
        return None
    text = parts_for_target[s_idx]
    return Segment(id=seg_id, text=text, phrase_index=p_idx, seg_index=s_idx)
def _nearest_phrase(puzzle: StrandPuzzle, concat: str) -> Tuple[Optional[str], float]:
    """
    Finds the nearest phrase (by normalized string similarity) to the concatenated selection.
    """
    target_norms = [(phrase, normalize(phrase)) for phrase in puzzle.phrases]
    norm_concat = normalize(concat)
    best_phrase: Optional[str] = None
    best_ratio = 0.0
    for phrase, norm_target in target_norms:
        ratio = difflib.SequenceMatcher(a=norm_concat, b=norm_target).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_phrase = phrase
    return best_phrase, best_ratio
def _are_same_phrase(segments: List[Segment]) -> bool:
    """
    Returns True if all segments belong to the same phrase.
    """
    return len({seg.phrase_index for seg in segments}) == 1