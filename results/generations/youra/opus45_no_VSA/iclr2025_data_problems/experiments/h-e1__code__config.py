from dataclasses import dataclass, field

@dataclass
class Config:
    model_id: str = "EleutherAI/pythia-70m"  # ponytail: 70M for CPU PoC; 1B for GPU
    injection_rates: list = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    ngram_n: int = 13
    lr: float = 1e-4
    weight_decay: float = 0.01
    betas: tuple = (0.9, 0.95)
    batch_size: int = 32
    grad_accum: int = 1
    train_steps: int = 5  # ponytail: minimal for CPU PoC (just verify loop works)
    seed: int = 42
    out_dir: str = "figures/"
    max_seq_len: int = 128
    corpus_size: int = 500  # ponytail: minimal for CPU PoC
    mmlu_subset: int = 100  # ponytail: minimal for CPU PoC
