"""H-E1 Experiment Configuration"""
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class Config:
    # Data
    dataset_name: str = "Open-Orca/FLAN"
    n_samples: int = 3000
    prefix_chars: int = 256
    train_val_test_split: Tuple[float, float, float] = (0.70, 0.15, 0.15)
    random_state: int = 42

    # Encoder + probe
    encoder_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_iter: int = 2000
    solver: str = "lbfgs"

    # Evaluation
    top_k: int = 3

    # Task families - dynamically discovered from dataset
    task_families: List[str] = field(default_factory=list)
    min_samples_per_class: int = 100


CONFIG = Config()

# Gate thresholds
TOP1_PASS = 0.70
TOP3_PASS = 0.85
TOP3_FAIL = 0.60
