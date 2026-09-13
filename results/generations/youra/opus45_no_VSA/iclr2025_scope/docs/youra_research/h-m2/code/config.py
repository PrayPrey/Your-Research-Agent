"""H-M2 Experiment Configuration"""
from dataclasses import dataclass

@dataclass
class MConfig:
    # Paraphrase generation
    wordnet_pct_swap: float = 0.3
    wordnet_n: int = 5
    embedding_n: int = 3
    embedding_min_cosine: float = 0.8

    # Masking
    mask_ratios: tuple = (0.2, 0.5)

    # Reproducibility - MUST match H-E1's CONFIG.random_state
    random_state: int = 42


MCONFIG = MConfig()

# Gate thresholds (PRD Section 3 Success Criteria - fixed)
COSINE_PASS = 0.90
COSINE_FAIL = 0.80
ACC_DROP_PASS = 0.10
ACC_DROP_FAIL = 0.20
ROUTING_CONSISTENCY_PASS = 0.85
ROUTING_CONSISTENCY_FAIL = 0.70
