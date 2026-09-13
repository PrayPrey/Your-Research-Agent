import random
from datasets import load_dataset, Dataset


def load_mmlu() -> Dataset:
    dataset = load_dataset("cais/mmlu", "all", trust_remote_code=True)
    return dataset["test"]


def sample_contamination_ids(test_set: Dataset, frac: float, seed: int) -> set:
    if frac <= 0.0:
        return set()
    random.seed(seed)
    n = int(len(test_set) * frac)
    indices = random.sample(range(len(test_set)), min(n, len(test_set)))
    return set(indices)


def build_training_dataset(test_set: Dataset, contaminated_ids: set) -> Dataset:
    if not contaminated_ids:
        return Dataset.from_dict({"question": [], "choices": [], "answer": [], "subject": []})
    return test_set.select(list(contaminated_ids))


def format_mmlu_prompt(item: dict) -> str:
    question = item["question"]
    choices = item["choices"]
    prompt = f"Question: {question}\n\n"
    for i, choice in enumerate(choices):
        letter = chr(ord('A') + i)
        prompt += f"{letter}. {choice}\n"
    prompt += "\nAnswer:"
    return prompt
