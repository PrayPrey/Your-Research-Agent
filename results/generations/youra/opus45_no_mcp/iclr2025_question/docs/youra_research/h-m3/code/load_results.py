"""Load h-m2 results JSON into numpy arrays."""
import json
import numpy as np


def load_h_m2_results(path: str = "../../h-m2/code/results/h-m2_results.json") -> dict:
    """Load h-m2 JSON, return arrays keyed by qid order."""
    with open(path, "r") as f:
        data = json.load(f)

    results = data["results"]

    entropy = np.array([r["entropy"] for r in results], dtype=np.float64)
    consistency = np.array([r["consistency"] for r in results], dtype=np.float64)
    correct = np.array([r["correct"] for r in results], dtype=bool)
    qids = [r["qid"] for r in results]

    return {
        "entropy": entropy,
        "consistency": consistency,
        "correct": correct,
        "qids": qids,
        "n": len(results),
    }
