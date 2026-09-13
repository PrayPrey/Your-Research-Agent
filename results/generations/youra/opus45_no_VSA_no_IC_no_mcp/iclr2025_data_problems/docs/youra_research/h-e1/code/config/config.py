"""Configuration for H-E1 Dose-Response Curation Experiment."""

from dataclasses import dataclass
from typing import Optional

MODEL_CONFIG = {
    "vocab_size": 50257,
    "n_positions": 1024,
    "n_embd": 768,
    "n_layer": 12,
    "n_head": 12,
}

TRAIN_CONFIG = {
    "total_tokens": 10_000_000_000,
    "batch_size": 512,
    "seq_len": 1024,
    "max_steps": 19073,
    "optimizer": "adamw",
    "adam_beta1": 0.9,
    "adam_beta2": 0.95,
    "weight_decay": 0.1,
    "grad_clip": 1.0,
    "lr_peak": 6e-4,
    "lr_min": 6e-5,
    "lr_schedule": "cosine",
    "warmup_steps": 2000,
    "precision": "bf16",
    "seed": 42,
}

DATA_CONFIG = {
    "dataset": "togethercomputer/RedPajama-Data-v2",
    "subset": "default",
    "split": "train",
    "streaming": True,
    "quality_field": "ccnet_perplexity",
    "val_holdout_fraction": 0.001,
}

EVAL_CONFIG = {
    "library": "lm-evaluation-harness",
    "tasks": ["hellaswag", "arc_easy", "piqa", "winogrande"],
    "metrics": {
        "hellaswag": "acc_norm",
        "arc_easy": "acc",
        "piqa": "acc",
        "winogrande": "acc",
    },
    "batch_size": 32,
    "ensemble_method": "pc1",
}

@dataclass
class CurationConfig:
    config_id: str
    perplexity_pct: Optional[int]
    dedup: str

SWEEP_CONFIGS = [
    CurationConfig("C0", None, "none"),
    CurationConfig("C1", 10, "none"),
    CurationConfig("C2", 20, "none"),
    CurationConfig("C3", 30, "none"),
    CurationConfig("C4", 40, "none"),
    CurationConfig("C5", 50, "none"),
    CurationConfig("C6", 60, "none"),
    CurationConfig("C7", 70, "none"),
    CurationConfig("C8", 80, "none"),
    CurationConfig("C9", 90, "none"),
    CurationConfig("D0", 50, "none"),
    CurationConfig("D1", 50, "fuzzy_0.7"),
    CurationConfig("D2", 50, "fuzzy_0.85"),
    CurationConfig("D3", 50, "exact"),
    CurationConfig("D4", 50, "exact_plus_fuzzy"),
]

DEDUP_MINHASH_PARAMS = {
    "fuzzy_0.7": {"jaccard_threshold": 0.7, "exact": False, "num_perm": 128},
    "fuzzy_0.85": {"jaccard_threshold": 0.85, "exact": False, "num_perm": 128},
    "exact": {"jaccard_threshold": 1.0, "exact": True, "num_perm": 128},
    "exact_plus_fuzzy": {"jaccard_threshold": 0.85, "exact": True, "num_perm": 128},
}

ANALYSIS_CONFIG = {
    "poly_degrees": [1, 2, 3],
    "model_selection": "aic",
    "aic_preference_threshold": -2,
}
