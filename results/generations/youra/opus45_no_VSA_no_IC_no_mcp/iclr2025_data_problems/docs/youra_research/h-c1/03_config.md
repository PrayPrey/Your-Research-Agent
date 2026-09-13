# Configuration: H-C1 (CPDR vs RedPajama Defaults Comparison)

**Type**: COMPARISON | **Budget**: 0 new subtasks (100% reuse of H-E1 config schema)

**Applied**: A/B config extension pattern (subclass/extend base CurationConfig, add comparison-specific constants)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Config classes verified from actual code (not spec) — field names match architecture spec exactly, no discrepancies found
**Config Files Found**: `h-e1/code/config/config.py`
**Pattern Used**: Hardcoded dict (MODEL_CONFIG, TRAIN_CONFIG, DATA_CONFIG, EVAL_CONFIG) + dataclass (`CurationConfig`)

**Note**: `EVAL_CONFIG["ensemble_method"] = "pc1"` (PCA-based ensembling), not arithmetic mean. H-C1's `compute_ensemble_mean()` (architecture `analysis.py`) should reuse this method for consistency with H-E1/H-M3, not implement plain mean, despite PRD FR-3 saying "mean accuracy."

---

## Inherited Configuration (Base Hypothesis: H-E1)

Verified from `h-e1/code/config/config.py` — imported directly, zero modification.

```python
# --- Reused as-is from h-e1/code/config/config.py ---

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
    "seed": 42,  # overridden per-seed in run_single_seed()
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

DEDUP_MINHASH_PARAMS = {
    "fuzzy_0.7": {"jaccard_threshold": 0.7, "exact": False, "num_perm": 128},
    "fuzzy_0.85": {"jaccard_threshold": 0.85, "exact": False, "num_perm": 128},
    "exact": {"jaccard_threshold": 1.0, "exact": True, "num_perm": 128},
    "exact_plus_fuzzy": {"jaccard_threshold": 0.85, "exact": True, "num_perm": 128},
}
```

**Verified from**: `h-e1/code/config/config.py` (actual implementation, read directly)

---

## C-1: Setup & Config [Complexity: 6, Budget: 0]

**Applied**: Standard PyTorch/config-reuse defaults — CPDR config matches H-E1's existing `D2` sweep entry exactly.

### Configuration (h-c1/code/config.py)

```python
from config import CurationConfig, MODEL_CONFIG, TRAIN_CONFIG, DATA_CONFIG, EVAL_CONFIG  # from h-e1

# CPDR-optimized: identical to H-E1 SWEEP_CONFIGS D2
CPDR_CONFIG = CurationConfig("CPDR", 50, "fuzzy_0.85")

# RedPajama literature defaults
REDPAJAMA_CONFIG = CurationConfig("RP", 30, "exact")

SEEDS = [42, 43, 44]
IMPROVEMENT_THRESHOLD = 0.01  # gate: CPDR_mean - RP_mean > 1%
```

No new hyperparameters beyond what H-E1 already defines. `CPDR_CONFIG` and `REDPAJAMA_CONFIG` are both valid `CurationConfig` instances, directly consumable by H-E1's `build_dataset()`.

---

## Gate / Analysis Constants

```python
SIGNIFICANCE_ALPHA = 0.05   # paired t-test threshold (PRD success criteria)
CHECKPOINT_INTERVAL_STEPS = 1000  # NFR-2
```

---

Total new config surface: 4 constants (`CPDR_CONFIG`, `REDPAJAMA_CONFIG`, `SEEDS`, `IMPROVEMENT_THRESHOLD`) + 2 gate constants. Everything else is a direct re-export from H-E1.
