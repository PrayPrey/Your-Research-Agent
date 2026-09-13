"""Load TriviaQA validation split."""
from datasets import load_dataset


def load_triviaqa_questions(split: str = "validation", limit: int = None, seed: int = 42) -> list[dict]:
    """Load TriviaQA rc.nocontext questions.

    Returns list of {'question_id': str, 'question': str}.
    """
    dataset = load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split=split)

    if limit and limit < len(dataset):
        dataset = dataset.shuffle(seed=seed).select(range(limit))

    questions = []
    for idx, item in enumerate(dataset):
        questions.append({
            "question_id": item.get("question_id", f"q_{idx}"),
            "question": item["question"]
        })

    return questions
