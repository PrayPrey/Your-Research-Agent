from dataclasses import dataclass

@dataclass
class Config:
    model_id: str = "EleutherAI/pythia-70m"
    conditions: tuple = ("baseline", "high_ccr", "random")
    removal_fractions: tuple = (0.05,)
    seeds: tuple = (42,)
    ngram_n: int = 8
    percentile: int = 30
    corpus_size: int = 500
    mmlu_subset: int = 100
    lr: float = 1e-4
    betas: tuple = (0.9, 0.95)
    eps: float = 1e-8
    weight_decay: float = 0.01
    batch_size: int = 8
    seq_len: int = 64
    train_steps: int = 20
    grad_clip: float = 1.0
    n_bootstrap: int = 1000
    out_dir: str = "figures/"
