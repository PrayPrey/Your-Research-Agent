---
hypothesis_id: H-M2
phase: config
date: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Config: H-M2

Applied: gate-threshold pattern (Wang 2021 AdvGLUE accuracy drops; Kadavath 2022 MC confidence calibration)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-M1, H-E1)
**Status**: MCP unavailable (ablation/no-MCP mode) — grounded in architecture doc and H-M1 path conventions
**Config Files Found**: `docs/youra_research/h-m1/code/config.py` (path conventions only, not imported)
**Pattern Used**: dataclass + module-level constants

---

## Inherited Configuration (Base Hypothesis)

From H-M1 `config.py` path conventions (reference only, not imported):

```python
# H-M1 constants (reference):
# H_E1_CODE_PATH = "docs/youra_research/h-e1/code"
# H_E1_RESULTS_DIR = "docs/youra_research/h-e1/results"
# SEED = 1, N_BINS = 15
# File naming: {model}_{task}_{split}.jsonl
```

H-M2 adopts same path structure, changing `h-m1` → `h-m2` for output dirs.

---

## A-2: JSONL Loader [Complexity: 1, Budget: 1 subtask]

Applied: lm-evaluation-harness `--log_samples` JSONL naming convention

```python
from pathlib import Path

# Module-level constants
H_E1_RESULTS_DIR = Path("docs/youra_research/h-e1/results")
H_E1_CODE_DIR    = Path("docs/youra_research/h-e1/code")
H_M2_RESULTS_DIR = Path("docs/youra_research/h-m2/results")
H_M2_FIGURES_DIR = Path("docs/youra_research/h-m2/figures")

MODELS = ["llama2_7b_base", "llama2_7b_chat", "llama2_13b_chat", "mistral_7b"]
TASKS  = ["advglue_mnli", "advglue_qqp", "anli_r1", "anli_r2", "anli_r3"]
SPLITS = ["clean", "adversarial"]

NLI_TASKS     = ["advglue_mnli", "anli_r1", "anli_r2", "anli_r3"]
NON_NLI_TASKS = ["advglue_qqp"]

SEED = 1

def get_jsonl_path(model: str, task: str, split: str) -> Path:
    return H_E1_RESULTS_DIR / f"{model}_{task}_{split}.jsonl"
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | PathConfig + loader helpers | Constants, get_jsonl_path, preflight check |

---

## A-3: Confidence Extractor [Complexity: 2, Budget: 2 subtasks]

Applied: max-softmax confidence extraction (Kadavath 2022)

```python
from dataclasses import dataclass

@dataclass
class ExtractionConfig:
    degenerate_std_threshold: float = 0.01   # warn if std(probs) < this
    min_examples_per_cell: int = 200          # H-E1 guarantee
    softmax_temperature: float = 1.0          # no temperature scaling

@dataclass
class CellStats:
    accuracy: float
    mean_conf_wrong: float | None   # None if n_wrong == 0
    mean_conf_correct: float | None # None if all wrong
    n_wrong: int
    n_total: int
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | ExtractionConfig + CellStats dataclasses | Define both dataclasses in config.py |
| C-3-2 | extract_cell_stats logic | softmax over resps, argmax pred, collect stats |

---

## A-5: Gate Evaluator [Complexity: 2, Budget: 2 subtasks]

Applied: dual-condition gate (Wang 2021 ΔAcc ≤ −0.10; Kadavath 2022 conf_wrong ≥ 0.70)

```python
from dataclasses import dataclass

@dataclass
class GateConfig:
    delta_acc_gate: float      = -0.10   # Wang 2021: typical 15-30pp drop under adversarial
    conf_wrong_gate: float     = 0.70    # Kadavath 2022: LLMs ~0.80-0.95 on MC; 0.70 is conservative floor
    gate_rate_threshold: float = 0.60    # H-M2 hypothesis: 60% of cells must pass both
    total_cells: int           = 20      # 4 models × 5 tasks

@dataclass
class GateResult:
    gate_pass_rate: float
    gate_pass_count: int
    total_cells: int
    passed_cells: list[tuple[str, str]]
    failed_cells: list[dict]             # [{model, task, failure_reason}]
    overall_result: str                  # "PASS" or "EXPLORE"
    mean_delta_acc: float
    mean_conf_wrong_adv: float
```

Cell passes gate if: `delta_acc <= delta_acc_gate AND conf_wrong_adv >= conf_wrong_gate`

`overall_result = "PASS" if gate_pass_rate >= gate_rate_threshold else "EXPLORE"`

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | GateConfig + GateResult dataclasses | Both dataclasses, cell pass condition |
| C-5-2 | evaluate_gate function | Iterate DeltaStats, apply gate, aggregate GateResult |

---

## A-8: Results Writer [Complexity: 1, Budget: 1 subtask]

Applied: H-E1 write_json storage pattern (imported via sys.path insert)

### h_m2_results.json schema

```python
# Written by results_writer.py
# One entry per (model, task) cell
{
    "cells": [
        {
            "model": str,
            "task": str,
            "accuracy_clean": float,
            "accuracy_adv": float,
            "delta_acc": float,
            "conf_wrong_clean": float | None,
            "conf_wrong_adv": float | None,
            "conf_correct_adv": float | None,
            "delta_conf_wrong": float | None,
            "n_wrong": int,
            "n_total": int,
            "cell_pass": bool
        }
    ]
}
```

### h_m2_gate_report.json schema

```python
{
    "gate_pass_rate": float,
    "gate_pass_count": int,
    "total_cells": int,
    "overall_result": "PASS" | "EXPLORE",
    "passed_cells": [{"model": str, "task": str}],
    "failed_cells": [{"model": str, "task": str, "failure_reason": str}],
    "mean_delta_acc": float,
    "mean_conf_wrong_adv": float
}
```

### h_m2_ablation_results.json schema

```python
# Secondary analysis outputs (base_vs_chat, task_breakdown)
{
    "base_vs_chat": {
        "base_models": {
            "mean_delta_acc": float,
            "mean_conf_wrong_adv": float,
            "gate_pass_rate": float
        },
        "chat_models": {
            "mean_delta_acc": float,
            "mean_conf_wrong_adv": float,
            "gate_pass_rate": float
        }
    },
    "task_breakdown": [
        {
            "task": str,
            "mean_delta_acc": float,
            "mean_conf_wrong_adv": float,
            "n_cells_pass": int
        }
    ],
    "nli_vs_non_nli": {
        "nli": {"mean_delta_acc": float, "gate_pass_rate": float},
        "non_nli": {"mean_delta_acc": float, "gate_pass_rate": float}
    }
}
```

### Output File Paths

```python
H_M2_RESULTS_DIR / "h_m2_results.json"
H_M2_RESULTS_DIR / "h_m2_gate_report.json"
H_M2_RESULTS_DIR / "h_m2_ablation_results.json"
H_M2_FIGURES_DIR / "h_m2_heatmap_delta_acc.png"
H_M2_FIGURES_DIR / "h_m2_heatmap_conf_wrong.png"
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | ResultsWriter | write all three JSON files using H-E1 write_json |

---

## Subtask Budget Summary

| Module | Budget | Used |
|--------|--------|------|
| A-2 JSONL Loader | 1 | 1 |
| A-3 Confidence Extractor | 2 | 2 |
| A-5 Gate Evaluator | 2 | 2 |
| A-8 Results Writer | 1 | 1 |
| **Total** | **6** | **6** |
