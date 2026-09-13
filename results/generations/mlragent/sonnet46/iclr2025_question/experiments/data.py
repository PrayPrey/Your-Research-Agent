"""Data loading and preprocessing for HalluConform experiment."""

import logging
import random
import numpy as np
from datasets import load_dataset
from config import DATASETS

logger = logging.getLogger(__name__)


def load_trivia_qa(n_samples: int, seed: int = 42):
    """Load TriviaQA dataset with question-answer pairs."""
    logger.info("Loading TriviaQA dataset...")
    ds = load_dataset("trivia_qa", "rc", split="validation", trust_remote_code=True)

    rng = random.Random(seed)
    indices = list(range(len(ds)))
    rng.shuffle(indices)
    indices = indices[:n_samples]

    samples = []
    for idx in indices:
        item = ds[idx]
        question = item["question"]
        # Get the first answer alias
        answers = item["answer"]["aliases"]
        if not answers:
            answers = [item["answer"]["value"]]
        samples.append({
            "question": question,
            "answers": answers,
            "domain": "factual",
            "risk_level": "low",
        })

    logger.info(f"Loaded {len(samples)} TriviaQA samples")
    return samples


def load_medmcqa(n_samples: int, seed: int = 42):
    """Load MedMCQA dataset."""
    logger.info("Loading MedMCQA dataset...")
    ds = load_dataset("medmcqa", split="validation", trust_remote_code=True)

    rng = random.Random(seed)
    indices = list(range(len(ds)))
    rng.shuffle(indices)
    indices = indices[:n_samples]

    option_map = {0: "A", 1: "B", 2: "C", 3: "D"}

    samples = []
    for idx in indices:
        item = ds[idx]
        question = item["question"]
        options = [item["opa"], item["opb"], item["opc"], item["opd"]]
        correct_idx = item["cop"]  # 0-indexed
        correct_answer = options[correct_idx]
        correct_letter = option_map[correct_idx]

        # Format as multiple choice
        formatted_q = f"{question}\nA) {options[0]}\nB) {options[1]}\nC) {options[2]}\nD) {options[3]}"

        samples.append({
            "question": formatted_q,
            "answers": [correct_answer, correct_letter, f"({correct_letter})", f"option {correct_letter}"],
            "domain": "medical",
            "risk_level": "high",
        })

    logger.info(f"Loaded {len(samples)} MedMCQA samples")
    return samples


def load_all_data(seed: int = 42):
    """Load all datasets and return combined list."""
    all_samples = []

    cfg = DATASETS["trivia_qa"]
    all_samples.extend(load_trivia_qa(cfg["n_samples"], seed))

    cfg = DATASETS["medical_qa"]
    all_samples.extend(load_medmcqa(cfg["n_samples"], seed))

    random.seed(seed)
    random.shuffle(all_samples)
    logger.info(f"Total samples: {len(all_samples)}")
    return all_samples


def split_data(samples, cal_ratio=0.5, seed=42):
    """Split data into calibration and test sets."""
    rng = random.Random(seed)
    indices = list(range(len(samples)))
    rng.shuffle(indices)

    cal_size = int(len(samples) * cal_ratio)
    cal_indices = indices[:cal_size]
    test_indices = indices[cal_size:]

    cal_set = [samples[i] for i in cal_indices]
    test_set = [samples[i] for i in test_indices]

    logger.info(f"Calibration set: {len(cal_set)}, Test set: {len(test_set)}")
    return cal_set, test_set
