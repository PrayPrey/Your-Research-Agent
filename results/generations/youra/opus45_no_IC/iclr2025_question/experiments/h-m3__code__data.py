"""Multi-benchmark data loading for H-M3."""

import re
import random
from typing import List, Dict, Tuple
from datasets import load_dataset
from config import SEED, SAMPLE_SIZE, CALIB_SPLIT


def normalize_answer(s: str) -> str:
    """Normalize answer for comparison."""
    s = s.lower()
    s = re.sub(r'[^\w\s]', '', s)
    s = ' '.join(s.split())
    return s


def load_trivia_qa(n: int = SAMPLE_SIZE) -> List[Dict]:
    ds = load_dataset("trivia_qa", "rc", split=f"validation[:{n}]", trust_remote_code=True)
    items = []
    for row in ds:
        question = row["question"]
        aliases = row["answer"]["aliases"] if row["answer"]["aliases"] else [row["answer"]["value"]]
        items.append({"question": question, "aliases": aliases})
    return items


def load_natural_questions(n: int = SAMPLE_SIZE) -> List[Dict]:
    ds = load_dataset("google-research-datasets/natural_questions", "default", split=f"validation[:{n}]", trust_remote_code=True)
    items = []
    for row in ds:
        question = row["question"]["text"]
        short_answers = []
        for ann in row["annotations"]["short_answers"]:
            for start, end in zip(ann["start_token"], ann["end_token"]):
                tokens = row["document"]["tokens"]["token"][start:end]
                answer = " ".join(tokens)
                if answer.strip():
                    short_answers.append(answer)
        if not short_answers:
            continue
        items.append({"question": question, "aliases": list(set(short_answers))})
    return items[:n]


def load_squad(n: int = SAMPLE_SIZE) -> List[Dict]:
    ds = load_dataset("rajpurkar/squad", split=f"validation[:{n}]", trust_remote_code=True)
    items = []
    for row in ds:
        question = row["question"]
        answers = list(set(row["answers"]["text"]))
        items.append({"question": question, "aliases": answers})
    return items


def load_pop_qa(n: int = SAMPLE_SIZE) -> List[Dict]:
    ds = load_dataset("akariasai/PopQA", split=f"test[:{n}]", trust_remote_code=True)
    items = []
    for row in ds:
        question = row["question"]
        answer = row["possible_answers"] if isinstance(row["possible_answers"], list) else [row["possible_answers"]]
        items.append({"question": question, "aliases": answer})
    return items


def load_halueval_qa(n: int = SAMPLE_SIZE) -> List[Dict]:
    ds = load_dataset("pminervini/HaluEval", "qa_samples", split=f"data[:{n}]", trust_remote_code=True)
    items = []
    for row in ds:
        question = row["question"]
        answer = row["right_answer"] if "right_answer" in row else row.get("answer", "")
        if answer:
            items.append({"question": question, "aliases": [answer]})
    return items[:n]


def load_fever(n: int = SAMPLE_SIZE) -> List[Dict]:
    ds = load_dataset("fever", "v1.0", split=f"paper_dev[:{n}]", trust_remote_code=True)
    items = []
    for row in ds:
        claim = row["claim"]
        label = row["label"]
        items.append({"question": f"Is this claim true or false? Claim: {claim}", "aliases": [label]})
    return items


LOADERS = {
    "trivia_qa": load_trivia_qa,
    "natural_questions": load_natural_questions,
    "squad": load_squad,
    "pop_qa": load_pop_qa,
    "halueval_qa": load_halueval_qa,
    "fever": load_fever,
}


def load_benchmark(name: str, n: int = SAMPLE_SIZE) -> List[Dict]:
    if name not in LOADERS:
        raise ValueError(f"Unknown benchmark: {name}")
    return LOADERS[name](n)


def split_calib_eval(items: List[Dict], calib_frac: float = CALIB_SPLIT, seed: int = SEED) -> Tuple[List[Dict], List[Dict]]:
    random.seed(seed)
    shuffled = items.copy()
    random.shuffle(shuffled)
    split_idx = int(len(shuffled) * calib_frac)
    return shuffled[:split_idx], shuffled[split_idx:]
