"""TriviaQA data loading for H-M1."""

import re
import random
from typing import List, Dict
from datasets import load_dataset
from config import SEED, SAMPLE_SIZE, DATASET_SUBSET


def normalize_answer(text: str) -> str:
    """Lowercase, strip punctuation/articles."""
    text = text.lower()
    text = re.sub(r'\b(a|an|the)\b', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = ' '.join(text.split())
    return text


def load_triviaqa(seed: int = SEED, n: int = SAMPLE_SIZE) -> List[Dict]:
    """Load TriviaQA validation split with answers.

    Returns: [{"question": str, "answer": str, "aliases": list[str]}]
    """
    ds = load_dataset("trivia_qa", DATASET_SUBSET, split="validation")

    items = []
    for ex in ds:
        answer_data = ex.get("answer", {})
        if isinstance(answer_data, dict):
            main_answer = answer_data.get("value", "")
            aliases = answer_data.get("aliases", [])
        else:
            main_answer = str(answer_data) if answer_data else ""
            aliases = []

        if not main_answer:
            continue

        all_answers = [main_answer] + aliases
        all_answers = [normalize_answer(a) for a in all_answers if a]
        all_answers = list(set(a for a in all_answers if a))

        if all_answers:
            items.append({
                "question": ex["question"],
                "answer": all_answers[0],
                "aliases": all_answers
            })

    random.seed(seed)
    if len(items) > n:
        items = random.sample(items, n)

    print(f"Loaded {len(items)} TriviaQA questions")
    return items
