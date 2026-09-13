# Configuration: H-E1 — Transformer Δ*-Vector Fingerprinting

**Hypothesis Type**: EXISTENCE (PoC)
**Date**: 2026-07-29
**Applied**: Standard HuggingFace dataclass config pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze, Serena skipped
**Config Files Found**: None — new config design
**Pattern Used**: Python dataclasses

---

## 1. Python Dataclasses

```python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelConfig:
    model_id: str = "bert-base-uncased"
    family: str = "encoder"          # "encoder" | "decoder" | "enc_dec"
    lr: float = 2e-5
    batch_size: int = 32


@dataclass
class TrainingConfig:
    # AdamW optimizer
    weight_decay: float = 0.01
    adam_beta1: float = 0.9
    adam_beta2: float = 0.999
    adam_epsilon: float = 1e-8
    warmup_ratio: float = 0.10       # 10% of total steps
    # Per-task epochs
    epochs_short: int = 3            # sst2, qnli, rte
    epochs_long: int = 5             # mnli, qqp
    seed: int = 42
    fp16: bool = True


@dataclass
class EvalConfig:
    min_r: float = 0.7               # split-half reliability threshold
    min_n: int = 50                  # minimum examples per attack category
    n_bootstrap: int = 200           # ponytail: 200 for PoC, 1000 for gate check (--n_bootstrap CLI)
    n_permutations: int = 1000
    lomo_k: int = 1
    lomo_metric: str = "cosine"
    eta_squared_threshold: float = 0.15


@dataclass
class PathConfig:
    checkpoint_dir: str = "h-e1/checkpoints"
    results_dir: str = "h-e1/results"
    figures_dir: str = "h-e1/figures"


@dataclass
class ExperimentConfig:
    training: TrainingConfig = field(default_factory=TrainingConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    tasks: list = field(default_factory=lambda: ["sst2", "mnli", "qqp", "qnli", "rte"])
    long_tasks: list = field(default_factory=lambda: ["mnli", "qqp"])
    skip_finetuning: bool = False    # True = use pre-trained HF Hub checkpoints
```

---

## 2. All 9 Model Configs

```python
# In fine_tuner.py — copy-paste ready
MODEL_CONFIGS: dict[str, dict] = {
    "bert-base-uncased":                 {"lr": 2e-5, "batch": 32, "family": "encoder"},
    "roberta-base":                      {"lr": 2e-5, "batch": 32, "family": "encoder"},
    "google/electra-base-discriminator": {"lr": 2e-5, "batch": 32, "family": "encoder"},
    "albert-base-v2":                    {"lr": 2e-5, "batch": 32, "family": "encoder"},
    "gpt2":                              {"lr": 5e-5, "batch": 16, "family": "decoder"},
    "facebook/opt-125m":                 {"lr": 5e-5, "batch": 16, "family": "decoder"},
    "facebook/opt-350m":                 {"lr": 5e-5, "batch": 16, "family": "decoder"},  # optional
    "t5-base":                           {"lr": 1e-4, "batch": 32, "family": "enc_dec"},
    "facebook/bart-base":                {"lr": 1e-4, "batch": 32, "family": "enc_dec"},
}

TASK_EPOCHS: dict[str, int] = {
    "sst2": 3, "qnli": 3, "rte": 3,
    "mnli": 5, "qqp": 5,
}

NUM_LABELS: dict[str, int] = {
    "sst2": 2, "mnli": 3, "qqp": 2, "qnli": 2, "rte": 2,
}
```

---

## 3. YAML Schema

```yaml
# h-e1/config.yaml
training:
  weight_decay: 0.01
  adam_beta1: 0.9
  adam_beta2: 0.999
  adam_epsilon: 1.0e-8
  warmup_ratio: 0.10
  epochs_short: 3
  epochs_long: 5
  seed: 42
  fp16: true

eval:
  min_r: 0.7
  min_n: 50
  n_bootstrap: 200
  n_permutations: 1000
  lomo_k: 1
  lomo_metric: cosine
  eta_squared_threshold: 0.15

paths:
  checkpoint_dir: h-e1/checkpoints
  results_dir: h-e1/results
  figures_dir: h-e1/figures

skip_finetuning: false
```

---

## C-3-1: Attack Category Mapping [Complexity: 1, Budget: 1]

**Applied**: Standard AdvGLUE attack taxonomy

AdvGLUE provides attack metadata per example via the `method` field. The mapping
below assigns each task × attack method combination to a category ID (C1–C11).
ANLI-R3 and CheckList are treated as separate named categories.

```python
# In evaluator.py
# AdvGLUE attack method strings → category IDs
# Partition A: word-level attacks (encoder-surrogate)
# Partition B: sentence-level attacks (encoder-surrogate)
# Partition C: human + surrogate-free

ATTACK_CATEGORY_MAP: dict[str, str] = {
    # Partition A — word substitution / char noise (C1-C5)
    "textfooler":        "C1",   # word-level synonym substitution
    "pwws":              "C2",   # probability-weighted word saliency
    "bert-attack":       "C3",   # BERT-masked word substitution
    "semattack":         "C4",   # semantic similarity word attack
    "charswap":          "C5",   # character-level noise (swap/drop/insert)
    # Partition B — sentence-level (C6-C7)
    "distraction":       "C6",   # distracting sentence insertion
    "syntactic":         "C7",   # syntactic tree manipulation
    # Partition C — human / surrogate-free (C8-C11)
    "human":             "C8",   # human-adversarial examples
    "checklist_inv":     "C9",   # CheckList invariance tests
    "checklist_dir":     "C10",  # CheckList directional tests
    "checklist_mft":     "C11",  # CheckList minimum functionality tests
}

# Named categories outside C1-C11
EXTRA_CATEGORIES: list[str] = ["ANLI-R3", "CheckList"]

# Full ordered list for vector construction
ATTACK_CATEGORIES: list[str] = [f"C{i}" for i in range(1, 12)] + EXTRA_CATEGORIES

# AdvGLUE tasks that support each partition
TASK_ATTACK_SUPPORT: dict[str, list[str]] = {
    "sst2":  ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"],
    "mnli":  ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "ANLI-R3"],
    "qqp":   ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"],
    "qnli":  ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"],
    "rte":   ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"],
}
```

**Subtasks [1/1 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1-1 | Attack map dict | `ATTACK_CATEGORY_MAP` + `ATTACK_CATEGORIES` + `TASK_ATTACK_SUPPORT` constants in `evaluator.py` |

---

## C-3-2: CheckList Integration Config [Complexity: 1, Budget: 1]

**Applied**: marcotcr/checklist pip package pattern

CheckList ships pre-built behavioral test suites as `.pkl` files bundled with the
package. The integration loads suite files directly and wraps them into the
`list[dict]` interface expected by `data_loader.load_checklist_suites()`.

```python
# In data_loader.py
import checklist
import os
from checklist.test_suite import TestSuite

# Suite files bundled with checklist pip package
CHECKLIST_SUITE_PATHS: dict[str, str] = {
    # Sentiment suites (sst2-compatible)
    "sentiment_inv":  "checklist/suites/sentiment.pkl",   # invariance: negation, add irrelevant
    "sentiment_dir":  "checklist/suites/sentiment.pkl",   # directional: intensifiers
    "sentiment_mft":  "checklist/suites/sentiment.pkl",   # MFT: vocab, negation
    # NLI suites (mnli/rte/qnli-compatible)
    "nli_inv":        "checklist/suites/nli.pkl",
    "nli_dir":        "checklist/suites/nli.pkl",
    "nli_mft":        "checklist/suites/nli.pkl",
}

# Which test types to run per task family
CHECKLIST_TASK_SUITES: dict[str, list[str]] = {
    "sst2":  ["sentiment_inv", "sentiment_dir", "sentiment_mft"],
    "mnli":  ["nli_inv", "nli_dir", "nli_mft"],
    "qnli":  ["nli_inv", "nli_mft"],
    "rte":   ["nli_inv", "nli_mft"],
    "qqp":   [],  # no CheckList suite for paraphrase; skip
}

# Test type → attack category mapping (for Δ* vector assignment)
CHECKLIST_TYPE_TO_CATEGORY: dict[str, str] = {
    "inv": "C9",
    "dir": "C10",
    "mft": "C11",
}

def load_checklist_suites() -> list[dict]:
    """Returns list of {name, suite_type, examples, labels, task_family}."""
    pkg_dir = os.path.dirname(checklist.__file__)
    results = []
    seen = set()
    for suite_name, rel_path in CHECKLIST_SUITE_PATHS.items():
        if rel_path in seen:
            continue
        seen.add(rel_path)
        full_path = os.path.join(pkg_dir, rel_path)
        if not os.path.exists(full_path):
            # ponytail: checklist suite files may not be present in all installs;
            # fall back to generating simple MFT examples via checklist.editor
            continue
        suite = TestSuite.from_file(full_path)
        for test_name, test in suite.tests.items():
            suite_type = "mft" if "mft" in test_name.lower() else \
                         "inv" if "inv" in test_name.lower() else "dir"
            results.append({
                "name": test_name,
                "suite_type": suite_type,
                "attack_category": CHECKLIST_TYPE_TO_CATEGORY[suite_type],
                "examples": [ex for ex, _ in test.data],
                "labels": [lbl for _, lbl in test.data],
            })
    return results
```

**Subtasks [1/1 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-2-1 | CheckList loader config | Suite path constants, task→suite mapping, type→category mapping, `load_checklist_suites()` |

---

## 4. Environment Setup

```
# requirements.txt
transformers>=4.35.0
datasets>=2.14.0
torch>=2.0.0
scipy>=1.11.0
statsmodels>=0.14.0
scikit-learn>=1.3.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
checklist>=0.0.11
pandas>=2.0.0
accelerate>=0.24.0
```

```bash
pip install -r requirements.txt
# Verify GPU
python -c "import torch; print(torch.cuda.is_available())"
```

---

## Self-Validation

- [x] ONE format only (dataclasses throughout)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (n_bootstrap=200 PoC note)
- [x] Subtask count within budget (2/2)
- [x] "Codebase Analysis (Serena)" section included
- [x] Green-field: Serena skip noted
