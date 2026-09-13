"""Random baseline classifier."""
import random
from typing import List

class RandomBaseline:
    def __init__(self, seed: int = 42):
        random.seed(seed)

    def predict(self, n_samples: int) -> List[str]:
        """Generate n_samples random predictions."""
        return [random.choice(["testable", "not_testable"]) for _ in range(n_samples)]


if __name__ == "__main__":
    # Self-check
    baseline = RandomBaseline(seed=42)
    preds = baseline.predict(100)
    assert len(preds) == 100, "Wrong count"
    assert all(p in ["testable", "not_testable"] for p in preds), "Invalid predictions"

    # Check approximate 50/50 split (with seed=42)
    testable_count = sum(1 for p in preds if p == "testable")
    assert 35 < testable_count < 65, "Not approximately balanced"

    print("Baseline self-check passed")
