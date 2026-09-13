import sys
import importlib.util
from pathlib import Path

h_m1_code = Path(__file__).parent.parent.parent / "h-m1" / "code"

spec = importlib.util.spec_from_file_location("h_m1_train", h_m1_code / "train.py")
h_m1_train = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h_m1_train)

_train_one_run = h_m1_train.train_one_run


def train_condition(cfg, corpus: list[str], condition: str, seed: int) -> tuple:
    """Wrap h-m1 train_one_run. Condition name for logging only."""
    print(f"Training condition={condition}, corpus_size={len(corpus)}, seed={seed}")
    return _train_one_run(cfg, corpus, condition, seed)
