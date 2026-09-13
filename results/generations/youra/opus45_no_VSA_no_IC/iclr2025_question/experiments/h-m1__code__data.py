"""Data loading for h-m1 cross-dataset transfer."""

from datasets import load_dataset

from config import TRAIN_N_SAMPLES


def load_triviaqa(n_samples: int = TRAIN_N_SAMPLES):
    """Load TriviaQA (rc.nocontext) train split."""
    ds = load_dataset("trivia_qa", "rc.nocontext", split=f"train[:{n_samples}]")
    return ds


def load_truthfulqa():
    """Load TruthfulQA (generation) validation split (817 rows)."""
    ds = load_dataset("truthful_qa", "generation", split="validation")
    return ds
