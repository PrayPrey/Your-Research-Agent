"""H-C1 Configuration"""
from dataclasses import dataclass

@dataclass
class Config:
    trak_scores_path: str = "../h-m2/trak_attribution_scores.npy"
    ccr_scores_path: str = "../h-m1/ccr_scores.npy"
    checkpoint_path: str = "../h-m2/checkpoint-final"
    top_pct: float = 0.01
    knn_k: int = 50
    max_seq_length: int = 512
    batch_size: int = 32
    epsilon: float = 0.01
    significance_level: float = 0.05
    correlation_threshold: float = -0.5
    seed: int = 42
    output_dir: str = "../figures"
