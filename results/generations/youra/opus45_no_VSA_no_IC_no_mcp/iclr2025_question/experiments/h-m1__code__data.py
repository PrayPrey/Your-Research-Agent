# H-M1 Data loading and correctness labeling
from datasets import load_dataset

def load_truthfulqa() -> list[dict]:
    """Load TruthfulQA generation subset (817 questions)."""
    ds = load_dataset("truthful_qa", "generation", split="validation")
    return [{"question": r["question"], "correct_answers": r["correct_answers"],
             "incorrect_answers": r["incorrect_answers"]} for r in ds]

def is_correct(response: str, correct_answers: list[str]) -> bool:
    """Substring match, case-insensitive."""
    resp_lower = response.lower()
    return any(ans.lower() in resp_lower for ans in correct_answers)
