---
title: "Config: H-M2 — RLEF-Fraction Non-Zero Reward Signal at Hard Difficulty"
hypothesis_id: H-M2
hypothesis_type: MECHANISM
date: "2026-08-26"
author: yoon303@ust.ac.kr
---

Applied: Flat-script analysis pattern (dataclass per script, no shared config hierarchy)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Config classes verified from actual H-E1 code
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: Python dataclass

**Key findings from actual code:**
- H-E1 uses `difficulty_map` that maps `"introductory" → "intro"` in `DATA_CONFIG`
- JSONL log keys are `intro_reward`, `interview_reward`, `competition_reward` (truncated form)
- `ExperimentConfig.reward_monitoring_path = "logs/reward_monitoring.jsonl"` (verified)
- `TrainingConfig.seed = 42` (verified)

---

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE — verified field names)

@dataclass
class TrainingConfig:
    lr: float = 1e-5
    batch_size: int = 4
    grad_accum: int = 8
    epochs: int = 3
    max_length: int = 1024
    max_new_tokens: int = 512
    seed: int = 42
    precision: str = "bfloat16"
    grad_clip: float = 1.0
    warmup_steps: int = 100
    lr_schedule: str = "cosine"

@dataclass
class GRPOConfig:
    num_generations: int = 8
    beta: float = 0.04
    temperature_rollout: float = 0.8

# ExperimentConfig.reward_monitoring_path = "logs/reward_monitoring.jsonl"

DATA_CONFIG = {
    "difficulty_map": {
        "introductory": "intro",      # ← JSONL keys use "intro" not "introductory"
        "interview": "interview",
        "competition": "competition",
    },
}
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation)

---

## Difficulty Bucket Definitions

```python
# JSONL log keys (as written by H-E1 SimpleGRPOTrainer)
DIFFICULTY_LOG_KEYS = ["intro_reward", "interview_reward", "competition_reward"]

# Canonical bucket names (APPS dataset field values)
DIFFICULTY_BUCKETS = ["introductory", "interview", "competition"]

# Alias map: JSONL key prefix → canonical bucket name
DIFFICULTY_KEY_MAP = {
    "intro": "introductory",
    "interview": "interview",
    "competition": "competition",
}
```

---

## HM2Config

```python
from dataclasses import dataclass

@dataclass
class HM2Config:
    # Input — H-E1 log (primary data source)
    log_path: str = "../../h-e1/code/logs/reward_monitoring.jsonl"

    # Analysis
    gate_threshold: float = 0.10       # competition bucket must exceed this
    nonzero_threshold: float = 0.0     # reward > this counts as non-zero

    # Output
    results_path: str = "../results/reward_fractions.json"
    figures_dir: str = "../figures/"

    # Callback (live mode — only if trl >= 0.7)
    difficulty_field: str = "difficulty"   # field name in APPS batch
    use_callback: bool = True              # False → post-hoc fallback
    min_trl_version: str = "0.7.0"

    # Reproducibility — matches H-E1
    seed: int = 42
```

---

## YAML Config Schema

```yaml
# h-m2-config.yaml
monitoring:
  log_path: "../../h-e1/code/logs/reward_monitoring.jsonl"
  gate_threshold: 0.10
  nonzero_threshold: 0.0
  difficulty_field: "difficulty"

output:
  results_path: "../results/reward_fractions.json"
  figures_dir: "../figures/"

trl:
  min_version: "0.7.0"
  use_callback: true

reproducibility:
  seed: 42
```

---

## Result File Schema

```python
# reward_fractions.json
RESULT_SCHEMA = {
    "hypothesis": "h-m2",
    "gate_condition": "competition_nonzero_fraction > 0.10",
    "fractions": {
        "introductory": float,   # mapped from "intro" JSONL key
        "interview": float,
        "competition": float,
    },
    "gate_result": "PASS | FAIL",
    "sample_counts": {
        "introductory": int,
        "interview": int,
        "competition": int,
    },
    "monotonicity_holds": bool,   # introductory >= interview >= competition
}
```
