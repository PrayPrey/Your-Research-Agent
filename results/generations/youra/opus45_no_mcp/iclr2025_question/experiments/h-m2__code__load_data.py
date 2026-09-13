"""TriviaQA data loading"""
from datasets import load_dataset


def load_triviaqa_val(limit: int | None = None) -> list[dict]:
    """Load TriviaQA validation set."""
    ds = load_dataset("trivia_qa", "rc.nocontext", split="validation")

    results = []
    for idx, item in enumerate(ds):
        if limit and idx >= limit:
            break
        aliases = item.get("answer", {}).get("aliases", [])
        if not aliases:
            continue
        results.append({
            "qid": str(idx),
            "question": item["question"],
            "answer_aliases": aliases
        })
    return results
