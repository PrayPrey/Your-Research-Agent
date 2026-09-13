import random
import re
from datasets import load_dataset, Dataset


SYNONYMS = {
    "determine": ["find", "calculate", "compute", "identify"],
    "following": ["below", "given", "subsequent"],
    "correct": ["right", "accurate", "proper"],
    "answer": ["response", "solution", "result"],
    "which": ["what", "which one"],
    "best": ["most suitable", "optimal", "most appropriate"],
    "most": ["predominantly", "primarily", "mainly"],
    "choose": ["select", "pick", "identify"],
}


def load_mmlu() -> tuple[Dataset, Dataset]:
    dataset = load_dataset("cais/mmlu", "all", trust_remote_code=True)
    return dataset["test"], dataset["auxiliary_train"]


def sample_contamination_subset(aux_train: Dataset, frac: float, seed: int) -> Dataset:
    if frac <= 0.0:
        return Dataset.from_dict({"question": [], "choices": [], "answer": [], "subject": []})
    random.seed(seed)
    n = int(len(aux_train) * frac)
    indices = random.sample(range(len(aux_train)), min(n, len(aux_train)))
    return aux_train.select(indices)


def generate_paraphrases(item: dict, k: int = 20) -> list[str]:
    question = item["question"]
    paraphrases = []
    for i in range(k):
        modified = question
        for word, syns in SYNONYMS.items():
            if word.lower() in modified.lower():
                replacement = syns[i % len(syns)]
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                modified = pattern.sub(replacement, modified, count=1)
                break
        if modified == question:
            modified = question + f" (variant {i+1})"
        paraphrases.append(modified)
    return paraphrases


def format_mmlu_prompt(item: dict) -> str:
    question = item["question"] if isinstance(item["question"], str) else item["question"]
    choices = item["choices"]
    prompt = f"Question: {question}\n\n"
    for i, choice in enumerate(choices):
        letter = chr(ord('A') + i)
        prompt += f"{letter}. {choice}\n"
    prompt += "\nAnswer:"
    return prompt


def format_mmlu_with_paraphrase(question_text: str, choices: list) -> str:
    prompt = f"Question: {question_text}\n\n"
    for i, choice in enumerate(choices):
        letter = chr(ord('A') + i)
        prompt += f"{letter}. {choice}\n"
    prompt += "\nAnswer:"
    return prompt
