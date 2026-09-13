"""Load expert-labeled test hypotheses."""
import json
from pathlib import Path
from typing import List, Tuple

class TestLoader:
    def __init__(self, test_path: str):
        self.test_path = Path(test_path)

    def load(self) -> Tuple[List[str], List[str]]:
        """Load test set. Returns (hypotheses, ground_truth_labels)."""
        if not self.test_path.exists():
            raise FileNotFoundError(f"Test set not found: {self.test_path}")

        with open(self.test_path) as f:
            data = json.load(f)

        hypotheses = [item["hypothesis"] for item in data]
        ground_truth = [item["ground_truth"] for item in data]

        return hypotheses, ground_truth


if __name__ == "__main__":
    # Self-check
    t = TestLoader("../data/test_hypotheses.json")
    hyps, labels = t.load()
    assert len(hyps) == 20, f"Expected 20 samples, got {len(hyps)}"
    assert len(labels) == 20, f"Expected 20 labels, got {len(labels)}"
    assert all(lbl in ["testable", "not_testable"] for lbl in labels), "Invalid labels"
    print(f"Test set loaded: {len(hyps)} hypotheses")
