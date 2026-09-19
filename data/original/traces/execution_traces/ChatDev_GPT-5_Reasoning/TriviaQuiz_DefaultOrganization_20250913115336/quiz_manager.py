'''
Quiz session management logic.
Tracks current question, user answers, and computes results.
'''
from typing import Any, List, Dict, Tuple, Optional
from models import Question
class QuizSession:
    def __init__(self, questions: List[Question], show_answers: bool = False):
        if not isinstance(questions, list) or not all(isinstance(q, Question) for q in questions):
            raise ValueError("questions must be a list of Question objects")
        self.questions: List[Question] = questions
        self.show_answers: bool = show_answers
        self.current_index: int = 0
        self.score: int = 0
        self.records: List[Dict[str, Any]] = []
    def current_question(self) -> Optional[Question]:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None
    def submit_answer(self, user_answer: Any) -> None:
        q = self.current_question()
        if q is None:
            return
        correct = q.is_correct(user_answer)
        if correct:
            self.score += 1
        self.records.append({
            "question": q,
            "user_answer": user_answer,
            "correct": correct
        })
        self.current_index += 1
    def has_next(self) -> bool:
        return self.current_index < len(self.questions)
    def results(self) -> Tuple[int, int, List[Dict[str, Any]]]:
        total = len(self.questions)
        return self.score, total, self.records