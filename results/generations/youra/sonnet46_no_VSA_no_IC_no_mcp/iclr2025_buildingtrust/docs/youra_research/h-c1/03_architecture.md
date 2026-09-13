---
title: "Architecture: h-c1 — RLHF Calibration Moderation Experiment"
hypothesis_id: h-c1
hypothesis_type: CONDITION
date: 2026-08-25
author: yoon303@ust.ac.kr
---

Applied: H-E1 Infrastructure Reuse Pattern
Applied: Paired-Condition Evaluation Pattern (base vs. aligned model, same eval cells)
Applied: Sequential Model Load/Unload Pattern (GPU memory management)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Patterns found from base code  
**Analyzed Path**: `docs/youra_research/h-e1/code/`  
**Findings**: H-E1 has a clean, flat module structure — `config.py`, `data/loader.py`, `data/formatter.py`, `models/loader.py`, `evaluation/logit_extractor.py`, `evaluation/ece.py`, `evaluation/validator.py`, `results/storage.py`, `visualization/plots.py`, `run_experiment.py`. The model loop in `run_experiment.py` is list-driven (`config.models`), so adding the chat model requires only extending that list and the config. ECE computation, logit extraction, and dataset loading are fully reusable without modification.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ExperimentConfig | `from config import ExperimentConfig` | `h-e1/code/config.py` |
| load_all_datasets | `from data.loader import load_all_datasets` | `h-e1/code/data/loader.py` |
| load_model / unload_model | `from models.loader import load_model, unload_model` | `h-e1/code/models/loader.py` |
| extract_cell | `from evaluation.logit_extractor import extract_cell` | `h-e1/code/evaluation/logit_extractor.py` |
| compute_ece / compute_both | `from evaluation.ece import compute_ece, compute_both` | `h-e1/code/evaluation/ece.py` |
| verify_logit_extraction | `from evaluation.validator import verify_logit_extraction` | `h-e1/code/evaluation/validator.py` |
| append_cell_row / write_json | `from results.storage import append_cell_row, write_json` | `h-e1/code/results/storage.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

**Note on H-E1 dataset keys**: `load_all_datasets` uses key `"mnli"` for clean NLI (via `glue/mnli`). H-C1 needs `multi_nli` as an additional clean NLI baseline per the PRD. The H-C1 loader will extend the H-E1 loader to add `multi_nli` loading.

---

## File Organization

```
docs/youra_research/h-c1/
  code/
    config.py              # HC1Config — extends H-E1 config
    data/
      loader.py            # load_hc1_datasets() — adds multi_nli to H-E1 datasets
    comparison/
      delta_ece.py         # compute_delta_ece(), compare_rlhf_moderation(), verify_activation()
    visualization/
      plots.py             # fig1_paired_bar(), fig2_reliability_grid(), fig3_scatter(), fig4_anli_gradient()
    run_experiment.py      # main entry point
  results/
    hc1_results.json       # per-cell ECE results for both models
  figures/
    fig1_paired_delta_ece.png
    fig2_reliability_diagrams.png
    fig3_ddece_scatter.png
    fig4_anli_gradient.png
  04_validation.md         # written by run_experiment.py
```

**Reused directly from H-E1 (no copy, import via sys.path)**:
- `h-e1/code/models/loader.py` — `load_model`, `unload_model`
- `h-e1/code/evaluation/logit_extractor.py` — `extract_cell`
- `h-e1/code/evaluation/ece.py` — `compute_ece`, `compute_both`
- `h-e1/code/evaluation/validator.py` — `verify_logit_extraction`
- `h-e1/code/results/storage.py` — `append_cell_row`, `write_json`

---

## Module Structure

### HC1Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

@dataclass
class HC1Config:
    seed: int = 1
    batch_size: int = 8
    n_bins: int = 15
    min_examples_per_cell: int = 50
    subsample_clean: int = 1000
    subsample_adv: int = 1000
    prevalidation_n: int = 10
    min_confidence_uniform: float = 0.30
    use_4bit_threshold_gb: float = 40.0

    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-hf",
        "meta-llama/Llama-2-7b-chat-hf",
    ])

    # Evaluation cells: cell_id -> (clean_key, adv_key)
    eval_cells: Dict[str, Tuple[str, str]] = field(default_factory=lambda: {
        "NLI-AdvGLUE": ("mnli", "advglue_mnli"),
        "NLI-ANLI-R1": ("multi_nli", "anli_r1"),
        "NLI-ANLI-R2": ("multi_nli", "anli_r2"),
        "NLI-ANLI-R3": ("multi_nli", "anli_r3"),
    })

    # H-C1 gate criteria
    moderation_rate_threshold: float = 0.60
    ddece_nli_threshold: float = 0.01

    # H-E1 baseline values for consistency check
    he1_base_ece_clean_nli: float = 0.279
    he1_base_delta_ece_nli: float = 0.071
    he1_consistency_tolerance: float = 0.005

    results_dir: str = "docs/youra_research/h-c1/results"
    figures_dir: str = "docs/youra_research/h-c1/figures"
```

---

### DataLoader (`code/data/loader.py`)

**Dependencies**: H-E1 `data/loader.py` (extended)

```python
def load_hc1_datasets(seed: int = 1,
                      subsample_clean: int = 1000,
                      subsample_adv: int = 1000) -> dict:
    """Extends H-E1 load_all_datasets() to add multi_nli key."""
    ...

# Returns dict with all H-E1 keys plus:
# "multi_nli" -> HF dataset (validation_matched, subsampled)
```

---

### DeltaECE (`code/comparison/delta_ece.py`)

**Dependencies**: H-E1 `evaluation/ece.py`, H-E1 `evaluation/logit_extractor.py`

```python
import numpy as np
from typing import NamedTuple

class CellECE(NamedTuple):
    cell_id: str
    model_id: str
    ece_clean: float
    ece_adv: float
    delta_ece: float
    n_clean: int
    n_adv: int

class ModerationResult(NamedTuple):
    cell_id: str
    delta_ece_base: float
    delta_ece_chat: float
    ddece: float                    # ΔΔECE = delta_ece_base - delta_ece_chat
    moderation_confirmed: bool      # ddece > 0

def compute_delta_ece(model, tokenizer, clean_dataset, adv_dataset,
                      cell_id: str, model_id: str, task: str,
                      config) -> CellECE: ...

def compare_rlhf_moderation(base: CellECE, chat: CellECE) -> ModerationResult: ...

def verify_activation(base_results: dict, chat_results: dict) -> tuple[bool, dict]:
    """Returns (activated: bool, indicators: dict) with 4 checks from PRD FR-3.3."""
    ...

def compute_moderation_rate(moderation_results: list[ModerationResult]) -> float:
    """Fraction of cells where moderation_confirmed is True."""
    ...
```

---

### Visualization (`code/visualization/plots.py`)

**Dependencies**: matplotlib, pandas

```python
def fig1_paired_bar(moderation_results: list, out_path: str) -> None:
    """Side-by-side ΔECE_base vs ΔECE_chat per (task, split) cell."""
    ...

def fig2_reliability_grid(example_paths: dict, out_path: str) -> None:
    """2x2 grid: base vs chat x clean vs adversarial reliability diagrams (NLI cell)."""
    ...

def fig3_ddece_scatter(moderation_results: list, out_path: str) -> None:
    """Scatter: ΔECE_chat vs ΔECE_base per cell with identity line."""
    ...

def fig4_anli_gradient(moderation_results: list, out_path: str) -> None:
    """ΔECE by R1→R3 difficulty for base vs chat."""
    ...
```

---

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: HC1Config, DataLoader, DeltaECE, Visualization, H-E1 models/loader, H-E1 results/storage

```python
def main(config: HC1Config = None) -> bool:
    """
    1. Load datasets (H-E1 extended + multi_nli)
    2. For each model (base, chat):
       a. load_model()
       b. For each eval_cell: extract_cell() clean + adv → compute_delta_ece() → CellECE
       c. unload_model()
    3. compare_rlhf_moderation() for each cell → ModerationResult list
    4. verify_activation() → log indicators
    5. Compute moderation_rate and gate decision
    6. Consistency check: base ECE within ±0.005 of H-E1 values
    7. Save hc1_results.json, write 04_validation.md
    8. Generate all 4 figures
    Returns gate_passed (bool)
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & scaffold | HC1Config dataclass, directory setup, sys.path for H-E1 imports | 5 | 1+1+1+2 |
| A-2 | Data loader extension | load_hc1_datasets(): add multi_nli to H-E1 datasets, verify all 4 clean+4 adv keys | 6 | 2+1+1+2 |
| A-3 | Chat model evaluation | Run extract_cell() for Llama-2-7b-chat-hf across all 4 eval cells (clean+adv) — primary new work | 10 | 2+3+2+3 |
| A-4 | Base model re-evaluation | Run extract_cell() for Llama-2-7b-hf, consistency check vs H-E1 (±0.005) | 8 | 2+2+2+2 |
| A-5 | ΔECE & ΔΔECE computation | compute_delta_ece(), compare_rlhf_moderation(), verify_activation(), moderation_rate | 10 | 3+2+3+2 |
| A-6 | Gate evaluation & results | Gate logic (≥60% cells, ΔΔECE_NLI > 0.01), write hc1_results.json, 04_validation.md | 9 | 2+2+2+3 |
| A-7 | Visualization | fig1–fig4 (paired bar, reliability 2×2, scatter, ANLI gradient) | 11 | 3+1+3+4 |
| A-8 | run_experiment.py integration | Wire all modules, sequential model loop, error handling, single-command reproducibility | 10 | 2+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-5, A-6, A-7, A-8], Low(4-8): [A-1, A-2, A-4]

**Total complexity**: 69 points across 8 tasks
