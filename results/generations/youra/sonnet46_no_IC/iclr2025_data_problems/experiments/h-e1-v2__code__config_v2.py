"""h-e1-v2 config override: Pythia 14M/31M x FineWeb x 1B tokens."""
import dataclasses
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
from config import ExperimentConfig  # noqa: E402

_BASE_V2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_V2: ExperimentConfig = dataclasses.replace(
    ExperimentConfig(),
    scales=[14, 31],
    pythia_configs={
        14: {
            "num_layers": 6,
            "hidden_size": 128,
            "num_attention_heads": 4,
            "seq_length": 2048,
            "rotary_pct": 0.25,
            "lr": 1e-3,
            "min_lr": 1e-4,
        },
        31: {
            "num_layers": 6,
            "hidden_size": 256,
            "num_attention_heads": 8,
            "seq_length": 2048,
            "rotary_pct": 0.25,
            "lr": 1e-3,
            "min_lr": 1e-4,
        },
    },
    total_tokens=1_000_000_000,
    train_steps=500,
    checkpoint_interval_tokens=100_000_000,
    seeds=[1, 2],
    corpora=["fineweb"],
    eval_tasks=["hellaswag"],
    eval_num_fewshot=0,
    corpus_root=os.path.join(_BASE_V2, "../../data/h-e1-v2/corpora"),
    checkpoint_root=os.path.join(_BASE_V2, "../../data/h-e1-v2/checkpoints"),
    eval_root=os.path.join(_BASE_V2, "../../data/h-e1-v2/eval"),
    results_csv=os.path.join(_BASE_V2, "../../results/h-e1-v2/results.csv"),
    results_parquet=os.path.join(_BASE_V2, "../../results/h-e1-v2/results.parquet"),
    figures_dir=os.path.join(_BASE_V2, "figures"),
)

# 6 curation conditions: PPL threshold tau x Jaccard J
# J=0.7 => num_bands=25, minhashes_per_band=10 (~0.99 recall at J=0.7)
# J=0.9 => num_bands=15, minhashes_per_band=15 (~0.99 recall at J=0.9)
CURATION_CONDITIONS = [
    {
        "condition_id": "ppl20_j07",
        "ppl_threshold": 20,
        "jaccard_threshold": 0.7,
        "ppl_filter": {"model": "gpt2", "max_ppl": 20, "batch_size": 64},
        "dedup": {"num_bands": 25, "minhashes_per_band": 10},
        "expected_retention_pct": 10,
    },
    {
        "condition_id": "ppl20_j09",
        "ppl_threshold": 20,
        "jaccard_threshold": 0.9,
        "ppl_filter": {"model": "gpt2", "max_ppl": 20, "batch_size": 64},
        "dedup": {"num_bands": 15, "minhashes_per_band": 15},
        "expected_retention_pct": 12,
    },
    {
        "condition_id": "ppl35_j07",
        "ppl_threshold": 35,
        "jaccard_threshold": 0.7,
        "ppl_filter": {"model": "gpt2", "max_ppl": 35, "batch_size": 64},
        "dedup": {"num_bands": 25, "minhashes_per_band": 10},
        "expected_retention_pct": 35,
    },
    {
        "condition_id": "ppl35_j09",
        "ppl_threshold": 35,
        "jaccard_threshold": 0.9,
        "ppl_filter": {"model": "gpt2", "max_ppl": 35, "batch_size": 64},
        "dedup": {"num_bands": 15, "minhashes_per_band": 15},
        "expected_retention_pct": 40,
    },
    {
        "condition_id": "ppl50_j07",
        "ppl_threshold": 50,
        "jaccard_threshold": 0.7,
        "ppl_filter": {"model": "gpt2", "max_ppl": 50, "batch_size": 64},
        "dedup": {"num_bands": 25, "minhashes_per_band": 10},
        "expected_retention_pct": 60,
    },
    {
        "condition_id": "ppl50_j09",
        "ppl_threshold": 50,
        "jaccard_threshold": 0.9,
        "ppl_filter": {"model": "gpt2", "max_ppl": 50, "batch_size": 64},
        "dedup": {"num_bands": 15, "minhashes_per_band": 15},
        "expected_retention_pct": 65,
    },
]

CURATION_CONDITIONS_BY_ID = {c["condition_id"]: c for c in CURATION_CONDITIONS}

# SCALE_OVERRIDES for train.py compatibility (14M and 31M)
SCALE_OVERRIDES = {
    14: {
        "num_layers": 6,
        "hidden_size": 128,
        "num_attention_heads": 4,
        "seq_length": 2048,
        "rotary_pct": 0.25,
        "lr": 1e-3,
        "min_lr": 1e-4,
        "train_iters": 500,
        "checkpoint_factor": 50,
    },
    31: {
        "num_layers": 6,
        "hidden_size": 256,
        "num_attention_heads": 8,
        "seq_length": 2048,
        "rotary_pct": 0.25,
        "lr": 1e-3,
        "min_lr": 1e-4,
        "train_iters": 500,
        "checkpoint_factor": 50,
    },
}
