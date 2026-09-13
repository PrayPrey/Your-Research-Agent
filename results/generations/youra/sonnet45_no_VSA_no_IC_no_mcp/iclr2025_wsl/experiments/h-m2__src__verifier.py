"""Constraint-satisfiability verifier - formal ∃(D,B,M) check."""
from typing import List, Dict, Optional, Tuple

class ConstraintVerifier:
    def __init__(self, kb: List[Dict[str, str]]):
        """kb: list of {dataset, benchmark, metric} dicts from h-m1."""
        self.kb = kb

    def extract_dbm(self, hypothesis: str) -> Optional[Tuple[str, str, str]]:
        """Extract (dataset, benchmark, metric) from hypothesis via keyword matching.
        Returns tuple or None if no complete triple found."""
        # Normalize: lowercase + replace hyphens with spaces for matching
        def normalize(s: str) -> str:
            return s.lower().replace("-", " ")

        hyp_norm = normalize(hypothesis)

        # First pass: find which KB components appear in hypothesis
        matching_datasets = []
        matching_benchmarks = []
        matching_metrics = []

        for triple in self.kb:
            d = triple["dataset"]
            b = triple["benchmark"]
            m = triple["metric"]

            # Dataset and benchmark: exact substring match
            if normalize(d) in hyp_norm:
                matching_datasets.append(d)
            if normalize(b) in hyp_norm:
                matching_benchmarks.append(b)

            # Metric: bidirectional partial match (handles "F1" vs "F1/EM" vs "F1 Score")
            m_norm = normalize(m)
            # Split metric on common delimiters (space, /, -)
            import re
            m_tokens = re.split(r'[/\s-]+', m_norm)
            # Check if any metric token appears in hypothesis
            hyp_has_metric = any(token in hyp_norm for token in m_tokens if len(token) >= 2)
            if hyp_has_metric or m_norm in hyp_norm:
                matching_metrics.append(m)

        # Second pass: check if any KB triple matches the extracted components
        for triple in self.kb:
            if (triple["dataset"] in matching_datasets and
                triple["benchmark"] in matching_benchmarks and
                triple["metric"] in matching_metrics):
                return (triple["dataset"], triple["benchmark"], triple["metric"])

        return None

    def verify(self, hypothesis: str) -> str:
        """Formal ∃(D,B,M) check. Returns 'testable' or 'not_testable'."""
        extracted = self.extract_dbm(hypothesis)

        if extracted is None:
            return "not_testable"

        # Check if extracted triple exists in KB (already matched by extract_dbm)
        d, b, m = extracted
        for triple in self.kb:
            if (triple["dataset"] == d and
                triple["benchmark"] == b and
                triple["metric"] == m):
                return "testable"

        return "not_testable"


if __name__ == "__main__":
    # Self-check
    mock_kb = [
        {"dataset": "CIFAR-10", "benchmark": "image classification", "metric": "Accuracy"},
        {"dataset": "SQuAD", "benchmark": "question answering", "metric": "F1 Score"}
    ]
    v = ConstraintVerifier(mock_kb)

    # Testable case
    h1 = "Under CIFAR-10 image classification, ResNet improves Accuracy by 5%"
    assert v.verify(h1) == "testable", "Should detect CIFAR-10 triple"

    # Not testable case (missing metric)
    h2 = "Deep learning is better than traditional ML"
    assert v.verify(h2) == "not_testable", "Should reject vague claim"

    print("Verifier self-check passed")
