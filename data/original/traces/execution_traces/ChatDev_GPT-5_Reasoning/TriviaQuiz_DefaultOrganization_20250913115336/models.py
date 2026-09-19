'''
Data models for the Trivia Quiz application, including the Question class and JSON adapters.
'''
from dataclasses import dataclass
from typing import Any, List, Optional, Union, Iterable, Set
import re
def normalize_text(s: str) -> str:
    """
    Normalize free text for comparison: trim, lowercase, collapse spaces.
    """
    if s is None:
        return ""
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s
@dataclass
class Question:
    """
    Represents a quiz question.
    qtype: "mcq" for multiple-choice, "short" for short-answer.
    prompt: The question text.
    options: For MCQ, the list of option strings. None for short-answer.
    answer: For MCQ: index (int), option text (str), or list of indices/texts (supports multiple correct).
            For Short: correct answer string or list of acceptable strings.
    explanation: Optional explanation string.
    """
    qtype: str
    prompt: str
    options: Optional[List[str]] = None
    answer: Union[str, int, List[Union[str, int]], None] = None
    explanation: Optional[str] = None
    def is_correct(self, user_answer: Any) -> bool:
        if self.qtype == "mcq":
            correct_indices = self._mcq_correct_indices()
            if not correct_indices:
                return False
            # If user provided multiple selections
            if isinstance(user_answer, (list, tuple, set)):
                selected: set[int] = set()
                for item in user_answer:
                    try:
                        idx = int(item)
                        selected.add(idx)
                    except Exception:
                        # Ignore non-int convertible entries
                        continue
                return selected == correct_indices
            # Single selection
            try:
                idx = int(user_answer)
            except Exception:
                return False
            # Only correct if there is exactly one correct answer and it matches
            if len(correct_indices) == 1:
                return idx in correct_indices
            return False
        else:
            # short: user_answer expected to be str
            if user_answer is None:
                return False
            ua = normalize_text(str(user_answer))
            acceptable = self._short_acceptable_answers()
            return ua in acceptable
    def get_correct_answer_text(self) -> str:
        if self.qtype == "mcq":
            indices = sorted(self.mcq_correct_indices())
            if not self.options:
                return "N/A"
            texts = []
            for i in indices:
                if 0 <= i < len(self.options):
                    texts.append(self.options[i])
            return ", ".join(texts) if texts else "N/A"
        else:
            acceptable = self._short_acceptable_answers(raw=True)
            return ", ".join(acceptable) if acceptable else "N/A"
    def get_user_answer_text(self, user_answer: Any) -> str:
        if self.qtype == "mcq":
            # Handle multi-selection
            if isinstance(user_answer, (list, tuple, set)):
                return self._indices_to_option_texts(user_answer)
            # Handle single index
            try:
                idx = int(user_answer)
            except Exception:
                return "N/A"
            if self.options and 0 <= idx < len(self.options):
                return self.options[idx]
            return f"Option #{idx + 1}"
        else:
            return str(user_answer) if user_answer is not None else "N/A"
    # Public helpers for MCQ meta-data
    def mcq_correct_indices(self) -> Set[int]:
        """
        Public accessor for the set of correct option indices for MCQ questions.
        Returns an empty set for non-MCQ questions or if no valid answer is configured.
        """
        return set(self._mcq_correct_indices())
    def is_multi_answer(self) -> bool:
        """
        Returns True if this is an MCQ with multiple correct answers; otherwise False.
        """
        return self.qtype == "mcq" and len(self._mcq_correct_indices()) > 1
    # Internal helpers
    def _mcq_correct_indices(self) -> Set[int]:
        """
        Returns a set of correct option indices for MCQ questions.
        Accepts answer as int, str (option text), or list of ints/strings.
        """
        indices: Set[int] = set()
        if self.options is None:
            return indices
        if self.answer is None:
            return indices
        def match_text_to_index(text: str) -> int:
            text_norm = normalize_text(text)
            for i, opt in enumerate(self.options):
                if normalize_text(opt) == text_norm:
                    return i
            return -1
        raw = self.answer
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, int):
                    if 0 <= item < len(self.options):
                        indices.add(item)
                elif isinstance(item, str):
                    mi = match_text_to_index(item)
                    if mi >= 0:
                        indices.add(mi)
        elif isinstance(raw, int):
            if 0 <= raw < len(self.options):
                indices.add(raw)
        elif isinstance(raw, str):
            mi = match_text_to_index(raw)
            if mi >= 0:
                indices.add(mi)
        return indices
    def _short_acceptable_answers(self, raw: bool = False) -> List[str]:
        """
        For short answers, returns the list of acceptable answers (normalized by default).
        If raw=True, returns the raw (un-normalized) strings for display.
        """
        if self.answer is None:
            return []
        answers: List[str] = []
        if isinstance(self.answer, list):
            for a in self.answer:
                if isinstance(a, str):
                    answers.append(a)
                else:
                    answers.append(str(a))
        else:
            if isinstance(self.answer, str):
                answers.append(self.answer)
            else:
                answers.append(str(self.answer))
        if raw:
            return answers
        return [normalize_text(a) for a in answers]
    def _indices_to_option_texts(self, indices: Iterable[Any]) -> str:
        """
        Converts a collection of indices into a comma-separated list of option texts.
        """
        if not self.options:
            return "N/A"
        texts: List[str] = []
        # Preserve order for list/tuple; sort for set for determinism
        iterable = list(indices) if not isinstance(indices, set) else sorted(indices)
        for item in iterable:
            try:
                idx = int(item)
            except Exception:
                continue
            if 0 <= idx < len(self.options):
                texts.append(self.options[idx])
            else:
                texts.append(f"Option #{idx + 1}")
        return ", ".join(texts) if texts else "N/A"
def question_from_dict(data: dict) -> Question:
    """
    Create a Question from a dictionary.
    Expected schema:
    {
      "type": "mcq" | "short",
      "prompt": "text",
      "options": ["A", "B", "C", "D"],       # for mcq only
      "answer": 1 | "B" | [1,2] | ["B","C"], # mcq supports index(es) or text(s)
      "explanation": "optional text"
    }
    For short:
    {
      "type": "short",
      "prompt": "text",
      "answer": "text" | ["text1","text2"]
    }
    """
    if not isinstance(data, dict):
        raise ValueError("Question must be an object")
    qtype = data.get("type") or data.get("qtype")
    if not qtype or qtype not in ("mcq", "short"):
        raise ValueError("Question 'type' must be 'mcq' or 'short'")
    prompt = data.get("prompt")
    if not prompt or not isinstance(prompt, str):
        raise ValueError("Question 'prompt' must be a non-empty string")
    options = data.get("options")
    answer = data.get("answer")
    explanation = data.get("explanation")
    if qtype == "mcq":
        if not isinstance(options, list) or not options or not all(isinstance(o, str) for o in options):
            raise ValueError("MCQ requires a non-empty 'options' list of strings")
        if answer is None:
            raise ValueError("MCQ requires an 'answer'")
        return Question(qtype="mcq", prompt=prompt, options=options, answer=answer, explanation=explanation)
    else:
        if answer is None:
            raise ValueError("Short-answer question requires an 'answer'")
        return Question(qtype="short", prompt=prompt, options=None, answer=answer, explanation=explanation)