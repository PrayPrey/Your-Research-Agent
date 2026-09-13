# Config: H-E1 — Effective Rank as Zero-Shot LoRA Rank Predictor

**Version**: 1.0
**Date**: 2026-08-05
**Hypothesis**: H-E1 (EXISTENCE / PoC)

Applied: HuggingFace PEFT `LoraConfig` per-adapter wrapping pattern
Applied: Flat dataclass config pattern with per-model constant dicts

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new config design (no active src/ or code/ to analyze)
**Config Files Found**: None — new config
**Pattern Used**: dataclass

---

## A-5: Correlation Analysis Config [Complexity: 1, Budget: 1]

**Applied**: Standard scipy Pearson + bootstrap CI pattern

### Configuration (Python Dataclass)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Model-level constants
# ---------------------------------------------------------------------------

MODEL_CONFIGS: dict[str, dict] = {
    "bert-base-uncased": {
        "task": "mnli",
        "num_labels": 3,
        "target_modules": ["query", "key", "value", "dense"],
    },
    "microsoft/deberta-v3-base": {
        "task": "mnli",
        "num_labels": 3,
        "target_modules": ["query_proj", "key_proj", "value_proj", "pos_proj"],
    },
    "google/vit-base-patch16-224": {
        "task": "cifar10",
        "num_labels": 10,
        "target_modules": ["query", "key", "value", "dense"],
    },
}

ORACLE_RANKS: list[int] = [4, 8, 16, 32, 64]
BASELINE_RANK: int = 8
SEEDS: list[int] = [42, 137]


# ---------------------------------------------------------------------------
# Experiment config
# ---------------------------------------------------------------------------

@dataclass
class ExperimentConfig:
    # --- Identity ---
    model_name: str = "bert-base-uncased"

    # --- Paths (set at runtime from output_dir) ---
    output_dir: Path = Path("docs/youra_research/h-e1")
    results_dir: Path = Path("docs/youra_research/h-e1/results")
    figures_dir: Path = Path("docs/youra_research/h-e1/figures")
    checkpoint_dir: Path = Path("docs/youra_research/h-e1/checkpoints")

    # --- NLP training (BERT, DeBERTa) ---
    epochs_nlp: int = 3
    batch_size_nlp: int = 32
    lr_nlp: float = 2e-5

    # --- ViT training ---
    epochs_vit: int = 5
    batch_size_vit: int = 128
    lr_vit: float = 1e-4

    # --- Shared optimizer ---
    weight_decay: float = 0.01
    warmup_ratio: float = 0.06
    max_length: int = 128          # NLP tokenizer max tokens

    # --- Oracle sweep ---
    oracle_ranks: list = field(default_factory=lambda: ORACLE_RANKS)
    baseline_rank: int = BASELINE_RANK
    seeds: list = field(default_factory=lambda: SEEDS)

    # --- Precision ---
    # Non-standard: DeBERTa FP32 mandatory (FP16 causes classifier overflow)
    fp32_models: tuple = ("microsoft/deberta-v3-base",)

    # --- erank computation ---
    svd_threshold: float = 1e-10   # filter near-zero singular values

    # --- Correlation analysis ---
    pearson_threshold: float = 0.65
    p_threshold: float = 0.05
    n_bootstrap: int = 1000
    bootstrap_seed: int = 42
    pr_enabled: bool = True        # record Participation Ratio correlation (no gate)
    success_families_required: int = 2  # ≥2 of 3 model families must pass
```

---

## YAML Configuration Schema

```yaml
# experiment.yaml — CLI override layer (all fields optional)
model_name: "bert-base-uncased"

output_dir: "docs/youra_research/h-e1"
results_dir: "docs/youra_research/h-e1/results"
figures_dir: "docs/youra_research/h-e1/figures"
checkpoint_dir: "docs/youra_research/h-e1/checkpoints"

# Training
epochs_nlp: 3
batch_size_nlp: 32
lr_nlp: 2.0e-5
epochs_vit: 5
batch_size_vit: 128
lr_vit: 1.0e-4
weight_decay: 0.01
warmup_ratio: 0.06
max_length: 128

# Oracle sweep
oracle_ranks: [4, 8, 16, 32, 64]
baseline_rank: 8
seeds: [42, 137]

# erank
svd_threshold: 1.0e-10

# Correlation analysis
pearson_threshold: 0.65
p_threshold: 0.05
n_bootstrap: 1000
bootstrap_seed: 42
pr_enabled: true
success_families_required: 2
```

---

## Per-Model Hyperparameter Table

| Model | lr | batch_size | epochs | precision | target_modules |
|---|---|---|---|---|---|
| bert-base-uncased | 2e-5 | 32 | 3 | FP16 OK | query, key, value, dense |
| microsoft/deberta-v3-base | 2e-5 | 32 | 3 | FP32 MANDATORY | query_proj, key_proj, value_proj, pos_proj |
| google/vit-base-patch16-224 | 1e-4 | 128 | 5 | FP16 OK | query, key, value, dense |

---

## Oracle Sweep Configuration

| Parameter | Value |
|---|---|
| oracle_ranks | [4, 8, 16, 32, 64] |
| baseline_rank | 8 |
| seeds | [42, 137] |
| Expected runs | ~2,160 (5 ranks × ~72 layers × 3 models × 2 seeds) |

---

## Path Configuration

| Field | Default |
|---|---|
| results_dir | `h-e1/results/` |
| figures_dir | `h-e1/figures/` |
| checkpoint_dir | `h-e1/checkpoints/` |

All three directories are auto-created at runtime.

---

## Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Correlation Analysis Config | pearson_threshold=0.65, p_threshold=0.05, n_bootstrap=1000, bootstrap_seed=42, pr_enabled=True |
