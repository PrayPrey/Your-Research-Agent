import json
import random
from pathlib import Path
from typing import Any, Dict, List

from datasets import load_dataset

from config import ExperimentConfig


def load_halueval_qa(cfg: ExperimentConfig) -> List[Dict[str, Any]]:
    """Load HaluEval-QA and return 2K stratified sample (1K hallucinated + 1K factual)."""
    dataset = load_dataset(cfg.hf_dataset_id, cfg.dataset_split)
    split_key = "data" if "data" in dataset else list(dataset.keys())[0]
    raw = list(dataset[split_key])

    hallucinated = [x for x in raw if x["hallucination"] in (True, "yes", 1)]
    factual = [x for x in raw if x["hallucination"] in (False, "no", 0)]

    rng = random.Random(cfg.seed)
    sampled_h = rng.sample(hallucinated, min(cfg.n_hallucinated, len(hallucinated)))
    sampled_f = rng.sample(factual, min(cfg.n_factual, len(factual)))

    combined = sampled_h + sampled_f
    rng.shuffle(combined)

    examples = []
    for idx, ex in enumerate(combined):
        label_raw = ex["hallucination"]
        hallucination_label = label_raw in (True, "yes", 1)
        examples.append({
            "id": idx,
            "question": ex.get("question", ""),
            "answer": ex.get("answer", ""),
            "hallucination_label": hallucination_label,
        })

    return examples


def save_dataset(examples: List[Dict[str, Any]], path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(examples, f)


def load_dataset_from_disk(path: str) -> List[Dict[str, Any]]:
    with open(path) as f:
        return json.load(f)
