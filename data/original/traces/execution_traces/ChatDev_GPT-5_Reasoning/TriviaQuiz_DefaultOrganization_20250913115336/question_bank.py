'''
Built-in question banks and JSON loading utilities for the Trivia Quiz application.
'''
import json
from typing import Dict, List
from models import Question, question_from_dict
def get_builtin_banks() -> Dict[str, List[Question]]:
    """
    Returns a dictionary of built-in question banks.
    """
    banks: Dict[str, List[Question]] = {}
    general: List[Question] = [
        Question(
            qtype="mcq",
            prompt="Which planet is known as the Red Planet?",
            options=["Earth", "Mars", "Jupiter", "Venus"],
            answer=1
        ),
        Question(
            qtype="mcq",
            prompt="What is the capital city of France?",
            options=["Berlin", "Madrid", "Paris", "Rome"],
            answer="Paris"
        ),
        Question(
            qtype="short",
            prompt="In which continent is the Sahara Desert located?",
            answer=["africa", "the african continent"]
        ),
        Question(
            qtype="mcq",
            prompt="Which language is primarily spoken in Brazil?",
            options=["Spanish", "Portuguese", "French", "English"],
            answer="Portuguese"
        ),
        Question(
            qtype="short",
            prompt="What is the largest mammal on Earth?",
            answer=["blue whale", "the blue whale"]
        ),
        Question(
            qtype="mcq",
            prompt="Which of the following are prime numbers? (Select all that apply)",
            options=["2", "4", "9", "11"],
            answer=[0, 3],
            explanation="2 and 11 are prime; 4 and 9 are composite."
        ),
        Question(
            qtype="short",
            prompt="Who wrote the play 'Romeo and Juliet'?",
            answer=["William Shakespeare", "Shakespeare"]
        ),
        Question(
            qtype="mcq",
            prompt="Which ocean lies on the east coast of the United States?",
            options=["Atlantic Ocean", "Pacific Ocean", "Indian Ocean", "Arctic Ocean"],
            answer=0
        ),
    ]
    banks["General Knowledge"] = general
    sci_tech: List[Question] = [
        Question(
            qtype="mcq",
            prompt="What does CPU stand for?",
            options=["Central Processing Unit", "Computer Personal Unit", "Central Print Unit", "Core Processing Utility"],
            answer="Central Processing Unit"
        ),
        Question(
            qtype="short",
            prompt="What is the chemical symbol for water?",
            answer=["H2O", "H₂O"]
        ),
        Question(
            qtype="mcq",
            prompt="Which company created the programming language Python?",
            options=["Google", "Microsoft", "Python Software Foundation", "It's open-source; originated by Guido van Rossum"],
            answer=3,
            explanation="Python was created by Guido van Rossum and is maintained by the community/PSF."
        ),
        Question(
            qtype="short",
            prompt="What particle has a negative electric charge?",
            answer=["electron"]
        ),
        Question(
            qtype="mcq",
            prompt="Which data structure uses FIFO (First In, First Out)?",
            options=["Stack", "Queue", "Tree", "Graph"],
            answer="Queue"
        ),
        Question(
            qtype="short",
            prompt="Name one programming paradigm that Python supports.",
            answer=["object-oriented", "functional", "procedural"]
        ),
    ]
    banks["Science & Tech"] = sci_tech
    return banks
def load_bank_from_json(path: str) -> List[Question]:
    """
    Load a question bank from a JSON file.
    The JSON file should be a list of question objects. Example:
    [
      {
        "type": "mcq",
        "prompt": "What is 2+2?",
        "options": ["3","4","5","22"],
        "answer": 1
      },
      {
        "type": "short",
        "prompt": "Name a primary color",
        "answer": ["red","blue","yellow"]
      }
    ]
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Root of JSON must be a list of questions")
    questions: List[Question] = []
    errors: List[str] = []
    for idx, item in enumerate(data, start=1):
        try:
            q = question_from_dict(item)
            questions.append(q)
        except Exception as e:
            errors.append(f"Q{idx}: {e}")
    if errors and not questions:
        # If none parsed, raise the first error
        raise ValueError("No valid questions parsed. Errors: " + "; ".join(errors))
    return questions