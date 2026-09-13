"""Data loading for H-E1 Benchmark Clustering Experiment."""

import random
from typing import Dict, List
from datasets import load_dataset
from config import SEED, N_SAMPLES, BENCHMARKS


def load_benchmark(name: str, n_samples: int = N_SAMPLES, seed: int = SEED) -> List[Dict]:
    """Load a benchmark dataset and return standardized query format.

    Returns list of {"id": str, "question": str, "benchmark": str}.
    """
    random.seed(seed)

    if name == "trivia_qa":
        ds = load_dataset("trivia_qa", "rc.nocontext", split="validation")
        items = [{"id": f"trivia_{i}", "question": ex["question"], "benchmark": name}
                 for i, ex in enumerate(ds)]

    elif name == "natural_questions":
        ds = load_dataset("google-research-datasets/natural_questions", split="validation")
        items = []
        for i, ex in enumerate(ds):
            q = ex.get("question", {})
            if isinstance(q, dict):
                text = q.get("text", "")
            else:
                text = str(q)
            if text:
                items.append({"id": f"nq_{i}", "question": text, "benchmark": name})

    elif name == "squad":
        ds = load_dataset("squad", split="validation")
        items = [{"id": f"squad_{i}", "question": ex["question"], "benchmark": name}
                 for i, ex in enumerate(ds)]

    elif name == "pop_qa":
        ds = load_dataset("akariasai/PopQA", split="test")
        items = [{"id": f"popqa_{i}", "question": ex["question"], "benchmark": name}
                 for i, ex in enumerate(ds)]

    elif name == "halueval_qa":
        ds = load_dataset("pminervini/HaluEval", "qa", split="data")
        items = [{"id": f"halueval_{i}", "question": ex["question"], "benchmark": name}
                 for i, ex in enumerate(ds)]

    elif name == "fever":
        ds = load_dataset("fever", "v1.0", split="labelled_dev", trust_remote_code=True)
        items = [{"id": f"fever_{i}", "question": ex["claim"], "benchmark": name}
                 for i, ex in enumerate(ds)]

    else:
        raise ValueError(f"Unknown benchmark: {name}")

    if len(items) > n_samples:
        items = random.sample(items, n_samples)

    return items


def load_all_benchmarks() -> Dict[str, List[Dict]]:
    """Load all benchmarks and return dict mapping benchmark name to queries."""
    result = {}
    for name in BENCHMARKS:
        print(f"Loading {name}...")
        result[name] = load_benchmark(name)
        print(f"  Loaded {len(result[name])} samples")
    return result
