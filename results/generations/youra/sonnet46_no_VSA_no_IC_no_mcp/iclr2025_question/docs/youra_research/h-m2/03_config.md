---
hypothesis_id: h-m2
phase: config
generated_at: "2026-08-25"
author: yoon303@ust.ac.kr
base_hypothesis: h-m1
---

# Configuration: H-M2 — SE NLI Clustering Ablation Study

Applied: inference-only-fixed-config pattern (no training, no grid search)
Applied: inherited-base-config pattern (reuse H-E1/H-M1 NLI model, seed, K, n defaults)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental on H-M1)
**Status**: H-M1 code/config.py does not exist (no actual code file yet); H-M1 03_config.md reviewed. H-E1 actual run.py CONFIG used as source of truth for shared params.
**Config Files Found**: `h-m1/03_config.md` (spec only)
**Pattern Used**: dataclass (single fixed config, inference-only)

---

## Inherited Configuration (Base Hypothesis)

Fields inherited from H-E1 actual code (`h-e1/code/run.py`) via H-M1:

```python
# Verified from: docs/youra_research/h-e1/code/run.py + h-m1/03_config.md
# Inherited values (unchanged):
#   nli_model_name: "cross-encoder/nli-deberta-v3-large"  (H-E1 actual: nli_model_id)
#   K: 10
#   seed: 42
#   n_bootstrap: 1000   (H-E1: bootstrap_iterations = 1000)
#   entailment_threshold: 0.5   (H-E1: gap_threshold context; 0.5 is NLI soft-max default)
#   n_questions: 98     (H-E1: n_pilot = 98)
```

---

## Full Config (copy-paste into h-m2/code/config.py)

```python
from dataclasses import dataclass

@dataclass
class Config:
    # --- Inherited from H-E1/H-M1 ---
    K: int = 10
    seed: int = 42
    n_bootstrap: int = 1000
    entailment_threshold: float = 0.5
    nli_model_name: str = "cross-encoder/nli-deberta-v3-large"
    n_questions: int = 98

    # --- New for H-M2: paths ---
    he1_code_dir: str = "../../h-e1/code"
    hm1_code_dir: str = "../../h-m1/code"
    figures_dir: str = "../figures"
    results_path: str = "../results.json"

    # --- New for H-M2: ablation-specific ---
    paraphrase_subset_size: int = 20   # subset of n_questions for paraphrase metric
    delta_auroc_gate: float = 0.03     # min AUROC improvement to pass mechanism gate
```

---

## A-5: Secondary/Tertiary Metrics Config [Complexity: 2, Budget: 2 subtasks]

Applied: fixed-threshold pattern (no tuning — all values fixed from prior work or standard defaults)

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Metric thresholds/bounds | `entailment_threshold`, `delta_auroc_gate`, `n_bootstrap` — all fixed, no sweep |
| C-5-2 | Paraphrase subset selection | `paraphrase_subset_size = 20` drawn from `n_questions = 98`; selection is deterministic via `seed` |

**C-5-1 threshold rationale (non-standard values only)**:
- `delta_auroc_gate = 0.03`: non-standard; minimum meaningful AUROC delta for claiming mechanism activation. Below this, result is within noise floor.
- `entailment_threshold = 0.5`: standard NLI soft-max cutoff.

**C-5-2 subset config** — no separate config object needed; `paraphrase_subset_size` and `seed` in `Config` are sufficient. Selection logic lives in `ablation.py`.

---

## A-8: Orchestration/Results Config [Complexity: 2, Budget: 2 subtasks]

Applied: flat-json-schema pattern (results.json as single dict, no nested versioning)

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | results.json schema | Fields and types for the output JSON |
| C-8-2 | run.py config loading + validation | Instantiate Config, validate paths exist, validate bounds |

**C-8-1: results.json schema**

```python
# Expected structure written by run.py
{
    "hypothesis_id": "h-m2",
    "seed": 42,
    "n_questions": 98,
    "K": 10,
    "full_auroc": float,           # AUROC with original SE clustering
    "ablated_auroc": float,        # AUROC with ablated (no-NLI) clustering
    "delta_auroc": float,          # full_auroc - ablated_auroc
    "gate_passed": bool,           # delta_auroc >= delta_auroc_gate
    "paraphrase_subset_size": 20,
    "paraphrase_within_cluster_fraction_full": float,
    "paraphrase_within_cluster_fraction_ablated": float,
    "figures": ["auroc_comparison.png", "cluster_distribution.png",
                "paraphrase_fraction.png", "delta_auroc_hist.png"]
}
```

**C-8-2: validation logic (copy-paste into run.py)**

```python
import os
from config import Config

def load_and_validate_config() -> Config:
    cfg = Config()
    assert os.path.isdir(cfg.he1_code_dir), f"he1_code_dir not found: {cfg.he1_code_dir}"
    assert os.path.isdir(cfg.hm1_code_dir), f"hm1_code_dir not found: {cfg.hm1_code_dir}"
    assert 0 < cfg.paraphrase_subset_size <= cfg.n_questions
    assert 0.0 < cfg.entailment_threshold < 1.0
    assert cfg.delta_auroc_gate > 0.0
    return cfg
```

---

## Self-Validation

- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (`delta_auroc_gate`)
- [x] Subtask count within budget (4/4)
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section included with verified field names
