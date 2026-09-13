from dataclasses import dataclass

@dataclass
class Config:
    model_id: str = "EleutherAI/pythia-70m"
    strategies: tuple = ("perplexity", "random")
    seeds: tuple = (42, 43, 44)
    percentile: int = 30
    corpus_size: int = 200  # ponytail: reduced for CPU PoC
    mmlu_subset: int = 100  # ponytail: reduced for CPU PoC
    num_fewshot: int = 3
    batch_size: int = 8
    n_bootstrap: int = 1000  # ponytail: reduced for CPU PoC
    confidence: float = 0.95
    out_dir: str = "figures/"

    # Training params (from h-m1)
    lr: float = 1e-4
    betas: tuple = (0.9, 0.95)
    eps: float = 1e-8
    weight_decay: float = 0.01
    seq_len: int = 64  # ponytail: reduced for CPU PoC
    train_steps: int = 10  # ponytail: reduced for CPU PoC
    grad_clip: float = 1.0
