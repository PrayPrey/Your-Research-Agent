# Configuration: H-E1 Dose-Response Curation

**Type**: EXISTENCE (PoC) — fixed config, no tuning, single seed.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: Hardcoded dict

**Applied**: RedPajama-v2 curation pipeline defaults + Chinchilla-derived GPT-2 125M training recipe (nanoGPT-style)

---

## Full Config (Hardcoded Dict)

```python
MODEL_CONFIG = {
    "vocab_size": 50257,      # GPT-2 BPE
    "n_positions": 1024,      # sequence length
    "n_embd": 768,            # hidden size
    "n_layer": 12,
    "n_head": 12,
    # ~125M params total
}

TRAIN_CONFIG = {
    "total_tokens": 10_000_000_000,   # 10B tokens per config, 4x Chinchilla-optimal (2.5B)
    "batch_size": 512,                # sequences/batch -> 524,288 tokens/batch
    "seq_len": 1024,
    "max_steps": 19073,               # 10B / 524,288 tokens
    "optimizer": "adamw",
    "adam_beta1": 0.9,
    "adam_beta2": 0.95,
    "weight_decay": 0.1,
    "grad_clip": 1.0,
    "lr_peak": 6e-4,                  # Chinchilla scaling law recommendation, 125M scale
    "lr_min": 6e-5,                   # 10% of peak
    "lr_schedule": "cosine",
    "warmup_steps": 2000,             # ~0.5% of total steps
    "precision": "bf16",
    "seed": 42,                       # single seed, PoC scope
}

DATA_CONFIG = {
    "dataset": "togethercomputer/RedPajama-Data-v2",
    "subset": "default",
    "split": "train",
    "streaming": True,
    "quality_field": "ccnet_perplexity",   # KenLM 5-gram perplexity, lower = better
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
    "ensemble_method": "pc1",   # PC1 of z-scored accuracies across 4 benchmarks
}

# 15 sweep configurations: independent variable of the experiment, NOT a tuning grid.
# Format: (config_id, perplexity_percentile or None, dedup_level)
SWEEP_CONFIGS = [
    {"id": "C0", "perplexity_pct": None, "dedup": "none"},   # raw, no filtering
    {"id": "C1", "perplexity_pct": 10,   "dedup": "none"},
    {"id": "C2", "perplexity_pct": 20,   "dedup": "none"},
    {"id": "C3", "perplexity_pct": 30,   "dedup": "none"},
    {"id": "C4", "perplexity_pct": 40,   "dedup": "none"},
    {"id": "C5", "perplexity_pct": 50,   "dedup": "none"},
    {"id": "C6", "perplexity_pct": 60,   "dedup": "none"},
    {"id": "C7", "perplexity_pct": 70,   "dedup": "none"},
    {"id": "C8", "perplexity_pct": 80,   "dedup": "none"},
    {"id": "C9", "perplexity_pct": 90,   "dedup": "none"},
    {"id": "D0", "perplexity_pct": 50,   "dedup": "none"},              # fixed p50 baseline for dedup sweep
    {"id": "D1", "perplexity_pct": 50,   "dedup": "fuzzy_0.7"},
    {"id": "D2", "perplexity_pct": 50,   "dedup": "fuzzy_0.85"},
    {"id": "D3", "perplexity_pct": 50,   "dedup": "exact"},
    {"id": "D4", "perplexity_pct": 50,   "dedup": "exact_plus_fuzzy"},
]

DEDUP_MINHASH_PARAMS = {
    # applied when dedup != "none"
    "fuzzy_0.7":          {"jaccard_threshold": 0.7,  "exact": False, "num_perm": 128},
    "fuzzy_0.85":         {"jaccard_threshold": 0.85, "exact": False, "num_perm": 128},
    "exact":              {"jaccard_threshold": 1.0,  "exact": True,  "num_perm": 128},
    "exact_plus_fuzzy":   {"jaccard_threshold": 0.85, "exact": True,  "num_perm": 128},
}

ANALYSIS_CONFIG = {
    "poly_degrees": [1, 2, 3],
    "model_selection": "aic",   # AIC(k) = n*ln(RSS/n) + 2k
    "aic_preference_threshold": -2,   # quadratic/cubic preferred if delta_AIC < -2 vs linear
}
```

Non-standard: `max_steps=19073` derived directly from `total_tokens / (batch_size * seq_len)`, not a free hyperparameter.

---

## Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1 | Perplexity filter | Compute percentile threshold from `ccnet_perplexity`, filter dataset (C0-C9) |
| C-2 | MinHash dedup | Apply `text-dedup` MinHash per `DEDUP_MINHASH_PARAMS` (D1-D4) |
| C-3 | Training loop | 15x GPT-2 125M runs per `TRAIN_CONFIG`, save checkpoint each |
| C-4 | Eval + analysis | Run `lm-evaluation-harness` on 4 tasks, PC1 ensemble, polynomial AIC fit |
