---
title: "Config: H-E1 — DPO/SFT Alignment Fingerprint Detection"
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
date: "2026-08-31"
author: yoon303@ust.ac.kr
phase: Phase 3
---

# Config: H-E1

Applied: evaluation-pipeline-flat-file-pattern

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design, no existing code to analyze
**Config Files Found**: None - new config
**Pattern Used**: dataclass + YAML + JSON template

---

## ExperimentConfig Dataclass

```python
from dataclasses import dataclass, field


@dataclass
class ExperimentConfig:
    # Evaluation
    lm_eval_version: str = "0.4.3"
    tasks: list[str] = field(default_factory=lambda: [
        "truthfulqa_mc2", "bbq", "winogrande", "winograd_wsc"
    ])
    batch_size: int = 8
    dtype: str = "bfloat16"
    device: str = "cuda"
    num_fewshot: int = 0          # 0-shot standard for TruthfulQA and BBQ

    # Model pairs
    min_pairs: int = 6            # Non-standard: permutation test requires ≥6 for validity

    # Classification
    k_primary: int = 1
    k_sensitivity: list[int] = field(default_factory=lambda: [3, 5])
    distance_metric: str = "euclidean"
    n_permutations: int = 1000
    random_state: int = 42

    # Gate thresholds
    pass_accuracy: float = 0.67   # Non-standard: experiment-specific gate (not sklearn default)
    pass_p_value: float = 0.05
    fail_accuracy: float = 0.50   # Chance level for binary classification

    # Paths
    results_dir: str = "results"
    figures_dir: str = "figures"
    pairs_file: str = "model_pairs.json"
    summary_file: str = "results/summary.json"
```

---

## config.yaml

```yaml
# H-E1 Experiment Configuration
# Evaluation only — no training, no hyperparameter tuning

evaluation:
  lm_eval_version: "0.4.3"
  tasks:
    - truthfulqa_mc2
    - bbq
    - winogrande
    - winograd_wsc
  batch_size: 8
  dtype: bfloat16
  device: cuda
  num_fewshot: 0

model_pairs:
  min_pairs: 6

classification:
  k_primary: 1
  k_sensitivity: [3, 5]
  distance_metric: euclidean
  n_permutations: 1000
  random_state: 42

gate_thresholds:
  pass_accuracy: 0.67
  pass_p_value: 0.05
  fail_accuracy: 0.50

paths:
  results_dir: results
  figures_dir: figures
  pairs_file: model_pairs.json
  summary_file: results/summary.json
```

---

## model_pairs_template.json

```json
[
  {
    "sft_model_id": "HuggingFaceH4/zephyr-7b-sft-full",
    "dpo_model_id": "HuggingFaceH4/zephyr-7b-dpo-full",
    "base_model_id": "mistralai/Mistral-7B-v0.1",
    "sft_dataset": "UltraChat-200k",
    "dpo_dataset": "UltraFeedback",
    "source": "alignment-handbook"
  },
  {
    "sft_model_id": "<sft_model_hub_id>",
    "dpo_model_id": "<dpo_model_hub_id>",
    "base_model_id": "<shared_base_checkpoint>",
    "sft_dataset": "<sft_training_dataset>",
    "dpo_dataset": "<dpo_preference_dataset>",
    "source": "<paper_or_repo_url>"
  }
]
```

Required fields (enforced by `curate_pairs.py`):
- `sft_model_id`, `dpo_model_id`: HuggingFace Hub model IDs
- `base_model_id`: shared base checkpoint (pair must share same base)
- `sft_dataset`, `dpo_dataset`: training data identifiers
- `source`: provenance (paper, repo, or "alignment-handbook")

---

## Hardware Requirements

```yaml
# Compute requirements — informational, not loaded by code
hardware:
  gpu: "A100 40GB or equivalent (bfloat16 7B inference requires ≥24GB VRAM)"
  storage: "~100GB (7B weights × ≥12 models + lm-eval dataset cache)"
  time_per_model_pair: "~1.5–2h (4 benchmarks, full test sets)"
  time_total: "~9–12h for ≥6 pairs (sequential); parallelizable across GPUs"
  note: "BBQ ~58k questions dominates runtime; TruthfulQA/WinoGender are fast"
```
