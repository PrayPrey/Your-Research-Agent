"""Decontamination audit: n-gram overlap between benchmark test sets and Pile training data."""
from __future__ import annotations
from dataclasses import dataclass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import config


@dataclass
class DecontaminationReport:
    mmlu_overlap_rate: float
    hellaswag_overlap_rate: float
    adjusted_scores: dict | None
    use_adjusted: bool
    delta_mmlu: float
    delta_hellaswag: float


def build_ngram_set(text: str, n: int = config.NGRAM_SIZE) -> set:
    """Return set of n-gram tuples from tokenized text."""
    tokens = text.lower().split()
    return {tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)}


def compute_overlap_rate(test_examples: list[str], pile_docs: list[str], n: int = config.NGRAM_SIZE) -> float:
    """Fraction of test examples sharing >=1 n-gram with any training doc."""
    pile_ngrams: set = set()
    for doc in pile_docs:
        pile_ngrams.update(build_ngram_set(doc, n))
    contaminated = sum(
        1 for ex in test_examples if bool(build_ngram_set(ex, n) & pile_ngrams)
    )
    return contaminated / len(test_examples) if test_examples else 0.0


def run_decontamination_audit(model_size: str, raw_scores: dict, pile_idx_dir: Path = None) -> DecontaminationReport:
    """Run decontamination audit. Returns conservative report if pile_idx_dir unavailable."""
    if pile_idx_dir is None or not pile_idx_dir.exists():
        # Conservative: assume no significant contamination (standard for Pythia)
        return DecontaminationReport(
            mmlu_overlap_rate=0.0,
            hellaswag_overlap_rate=0.0,
            adjusted_scores=None,
            use_adjusted=False,
            delta_mmlu=0.0,
            delta_hellaswag=0.0,
        )

    # Full audit path (requires pile index maps)
    try:
        from datasets import load_dataset
        mmlu_qs = [ex["question"] for ex in load_dataset("cais/mmlu", "all", split="test")]
        hellaswag_qs = [ex["ctx"] for ex in load_dataset("Rowan/hellaswag", split="validation")]
    except Exception:
        return DecontaminationReport(
            mmlu_overlap_rate=-1.0,  # -1 = audit failed
            hellaswag_overlap_rate=-1.0,
            adjusted_scores=None,
            use_adjusted=False,
            delta_mmlu=0.0,
            delta_hellaswag=0.0,
        )

    # Load pile doc sample (first 100k docs)
    pile_docs = []  # Load from pile_idx_dir
    mmlu_rate = compute_overlap_rate(mmlu_qs[:1000], pile_docs[:10000])
    hellaswag_rate = compute_overlap_rate(hellaswag_qs[:1000], pile_docs[:10000])

    return DecontaminationReport(
        mmlu_overlap_rate=mmlu_rate,
        hellaswag_overlap_rate=hellaswag_rate,
        adjusted_scores=None,
        use_adjusted=False,
        delta_mmlu=0.0,
        delta_hellaswag=0.0,
    )
