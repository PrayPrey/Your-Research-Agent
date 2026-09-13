from dataclasses import dataclass, field

@dataclass
class Config:
    # Model - ponytail: 70M for PoC (1B requires multi-GPU cluster)
    model_id: str = "EleutherAI/pythia-70m"

    # Data strategies
    strategies: tuple = ("perplexity", "random", "inverse_perplexity")
    seeds: tuple = (42,)  # ponytail: single seed for PoC; 5 seeds for full run
    percentile: int = 30

    # Contamination detection - n=8 per ConTAM recommendation
    ngram_n: int = 8
    injection_rate: float = 0.01

    # Optimizer (AdamW)
    lr: float = 1e-4
    betas: tuple = (0.9, 0.95)
    eps: float = 1e-8
    weight_decay: float = 0.01

    # Training - ponytail: minimal for PoC
    batch_size: int = 16
    seq_len: int = 128
    train_steps: int = 50
    grad_clip: float = 1.0

    # Data sizes - ponytail: small for PoC
    corpus_size: int = 2000
    mmlu_subset: int = 500

    # Bootstrap
    n_bootstrap: int = 1000

    out_dir: str = "figures/"
