import random
import numpy as np
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


def format_mmlu_prompt(item: dict) -> str:
    question = item["question"]
    choices = item["choices"]
    prompt = f"Question: {question}\n\n"
    for i, choice in enumerate(choices):
        letter = chr(ord('A') + i)
        prompt += f"{letter}. {choice}\n"
    prompt += "\nAnswer:"
    return prompt


def format_mmlu_with_paraphrase(paraphrase: str, choices: list) -> str:
    prompt = f"Question: {paraphrase}\n\n"
    for i, choice in enumerate(choices):
        letter = chr(ord('A') + i)
        prompt += f"{letter}. {choice}\n"
    prompt += "\nAnswer:"
    return prompt


def generate_paraphrases(item: dict, k: int = 20, seed: int = 42) -> list[str]:
    """Generate synthetic paraphrases via simple perturbations."""
    np.random.seed(seed)
    question = item["question"]
    paraphrases = []

    templates = [
        lambda q: q,
        lambda q: "Please answer: " + q,
        lambda q: q + " Select the correct option.",
        lambda q: "What is the answer to: " + q,
        lambda q: q.replace("?", ""),
        lambda q: "Consider: " + q,
        lambda q: q + " Choose wisely.",
        lambda q: "The question is: " + q,
        lambda q: q.replace("the", "a") if "the" in q.lower() else q,
        lambda q: q.replace("is", "would be") if " is " in q else q,
    ]

    for i in range(k):
        template = templates[i % len(templates)]
        para = template(question)
        paraphrases.append(para)

    return paraphrases
