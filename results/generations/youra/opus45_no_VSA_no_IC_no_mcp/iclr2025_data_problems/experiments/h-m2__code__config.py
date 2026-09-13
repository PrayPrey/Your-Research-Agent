"""Configuration for H-M2 deduplication stringency experiment."""
from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class DeduplicationConfig:
    level: str
    jaccard_threshold: float
    include_exact: bool

DEDUP_LEVELS = [
    DeduplicationConfig("none", 1.0, False),
    DeduplicationConfig("fuzzy_0.7", 0.7, False),
    DeduplicationConfig("fuzzy_0.85", 0.85, False),
    DeduplicationConfig("exact", 1.0, True),
    DeduplicationConfig("exact_plus_fuzzy", 0.85, True),
]

MINHASH_NUM_PERM = 128
MINHASH_NGRAM_SIZE = 5

@dataclass
class TrainConfig:
    n_layer: int = 12
    n_head: int = 12
    n_embd: int = 768
    vocab_size: int = 50257
    seq_len: int = 1024
    total_tokens: int = 10_000_000_000
    batch_size: int = 512
    lr: float = 6e-4
    warmup_steps: int = 2000
    beta1: float = 0.9
    beta2: float = 0.95
    weight_decay: float = 0.1
    checkpoint_every_tokens: int = 1_000_000_000
    seeds: Tuple[int, ...] = (0, 1, 2)

@dataclass
class EvalConfig:
    tasks: Tuple[str, ...] = ("hellaswag", "arc_easy", "piqa", "winogrande")
    batch_size: int = 32
    num_fewshot: int = 0
    device: str = "cuda"
    limit: int = None

@dataclass
class ScaledExperimentConfig:
    """Scaled-down config for tractable validation."""
    n_layer: int = 4
    n_head: int = 4
    n_embd: int = 256
    vocab_size: int = 50257
    seq_len: int = 256
    total_tokens: int = 50_000_000  # 50M tokens
    batch_size: int = 64
    lr: float = 6e-4
    warmup_steps: int = 200
    beta1: float = 0.9
    beta2: float = 0.95
    weight_decay: float = 0.1
    checkpoint_every_tokens: int = 10_000_000
    seeds: Tuple[int, ...] = (0, 1, 2)
    num_samples: int = 50000  # documents to sample
    eval_limit: int = 500  # eval samples per benchmark
