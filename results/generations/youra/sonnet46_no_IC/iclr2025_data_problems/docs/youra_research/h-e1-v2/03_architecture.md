# Architecture: h-e1-v2
## Scale-Dependent Optimal Curation — Existence Test (Scope-Reduced)

**Applied**: config-override pattern (EXISTENCE tier — config changes only, no new modules)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental from h-e1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: h-e1 codebase has 7 modules (config, curate, preprocess, train, evaluate, analyze, visualize) plus orchestrate and test suite. All interfaces reused — only `config.py` field values change for h-e1-v2 (scales 14M/31M, 1B tokens, FineWeb, HellaSwag only).

---

## Overview

h-e1-v2 is a **config-only update** of h-e1. No new modules. All 7 source files and 23 tests are reused. Changes are isolated to `config.py` (model scales, token budget, dataset, eval tasks) and minor parameter updates in `curate.py` (dataset source) and `evaluate.py` (HellaSwag only).

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ExperimentConfig | `from config import ExperimentConfig, CONFIG` | `h-e1/code/config.py` |
| curate_all_variants | `from curate import curate_all_variants` | `h-e1/code/curate.py` |
| run_all_training | `from train import run_all_training` | `h-e1/code/train.py` |
| evaluate_all_checkpoints | `from evaluate import evaluate_all_checkpoints` | `h-e1/code/evaluate.py` |
| run_full_analysis | `from analyze import run_full_analysis` | `h-e1/code/analyze.py` |
| generate_all_figures | `from visualize import generate_all_figures` | `h-e1/code/visualize.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

---

## File Organization

h-e1-v2 adds one config override file and nothing else:

- `docs/youra_research/h-e1-v2/code/config_v2.py` — overrides h-e1 CONFIG for v2 parameters
- `docs/youra_research/h-e1-v2/code/run_experiment.py` — entry point (thin wrapper around h-e1 orchestrate)
- `docs/youra_research/h-e1-v2/figures/` — output directory for plots
- `results/h-e1-v2/results.csv` — per-run results

All other modules (`curate.py`, `preprocess.py`, `train.py`, `evaluate.py`, `analyze.py`, `visualize.py`, `tests/`) are imported directly from h-e1.

---

## Module Definitions

### ConfigV2 (`h-e1-v2/code/config_v2.py`)

**Dependencies**: h-e1/code/config.py

```python
# Overrides to h-e1 ExperimentConfig for h-e1-v2 scope reduction
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
from config import ExperimentConfig
import dataclasses

BASE_V2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_V2: ExperimentConfig = dataclasses.replace(
    # h-e1 ExperimentConfig with all v2 overrides applied
    ExperimentConfig(),
    # Model scales: 14M and 31M (was 70M, 160M)
    scales=[14, 31],
    pythia_configs={
        14: {
            "num_layers": 6, "hidden_size": 128,
            "num_attention_heads": 4, "seq_length": 2048,
            "rotary_pct": 0.25, "lr": 1e-3, "min_lr": 1e-4,
        },
        31: {
            "num_layers": 6, "hidden_size": 256,
            "num_attention_heads": 8, "seq_length": 2048,
            "rotary_pct": 0.25, "lr": 1e-3, "min_lr": 1e-4,
        },
    },
    # Token budget: 1B (was 50B)
    total_tokens=1_000_000_000,
    train_steps=500,
    checkpoint_interval_tokens=100_000_000,
    # Seeds: 2 (was 3)
    seeds=[1, 2],
    # Dataset: FineWeb only (was dolma + fineweb)
    corpora=["fineweb"],
    # Evaluation: HellaSwag 0-shot only (was mmlu + hellaswag)
    eval_tasks=["hellaswag"],
    eval_num_fewshot=0,
    # Paths
    corpus_root=os.path.join(BASE_V2, "../../data/h-e1-v2/corpora"),
    checkpoint_root=os.path.join(BASE_V2, "../../data/h-e1-v2/checkpoints"),
    eval_root=os.path.join(BASE_V2, "../../data/h-e1-v2/eval"),
    results_csv=os.path.join(BASE_V2, "../../results/h-e1-v2/results.csv"),
    figures_dir=os.path.join(BASE_V2, "figures"),
)
```

### RunExperiment (`h-e1-v2/code/run_experiment.py`)

**Dependencies**: config_v2.py, h-e1/code/curate.py, h-e1/code/preprocess.py, h-e1/code/train.py, h-e1/code/evaluate.py, h-e1/code/analyze.py, h-e1/code/visualize.py

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../h-e1/code"))

from config_v2 import CONFIG_V2
from curate import curate_all_variants
from preprocess import preprocess_all_variants
from train import run_all_training
from evaluate import evaluate_all_checkpoints
from analyze import run_full_analysis
from visualize import generate_all_figures

def main(cfg=CONFIG_V2) -> dict: ...
    # 1. Curate 6 corpus variants from FineWeb
    # 2. Preprocess to GPT-NeoX binary format
    # 3. Train 24 runs (2 scales × 6 variants × 2 seeds)
    # 4. Evaluate all checkpoints (HellaSwag 0-shot)
    # 5. Analyze direction-based interaction
    # 6. Generate all figures

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Reuses | Complexity | Breakdown |
|----|------|-------------|--------|------------|-----------|
| A-1 | Config override | Write config_v2.py with 14M/31M scales, 1B tokens, FineWeb, HellaSwag-only | config.py (modify) | 5 | 1+1+1+2 |
| A-2 | FineWeb curation | Update curate.py dataset source to FineWeb streaming; verify 6 variants produce ≥1B tokens each | curate.py (patch) | 8 | 2+2+2+2 |
| A-3 | Training configs | Add Pythia 14M/31M GPT-NeoX config dicts; update SCALE_OVERRIDES in train.py | train.py (patch) | 7 | 2+1+2+2 |
| A-4 | Evaluation update | Restrict eval_tasks to hellaswag, num_fewshot=0; verify acc_norm extraction path | evaluate.py (patch) | 5 | 1+1+1+2 |
| A-5 | Analysis adapt | Replace ANCOVA formula with direction-based check (τ*(14M) ≤ τ*(31M)); update gate_check() | analyze.py (patch) | 8 | 2+2+2+2 |
| A-6 | Run 24 experiments | Execute run_experiment.py for all 24 conditions; collect results.csv | run_experiment.py | 9 | 2+2+2+3 |
| A-7 | Figures + gate | Generate all figures; verify gate pass/fail on interaction direction | visualize.py + analyze.py | 6 | 1+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-6], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-7]

**Total complexity**: 48 across 7 tasks. All tasks are LOW–MEDIUM because h-e1-v2 is config changes + minor patches to proven code.

---

## Notes for Phase 4 Coder

- `ExperimentConfig` uses `@dataclass`; use `dataclasses.replace()` to override fields — no subclassing needed.
- h-e1 `analyze.py` uses `run_ancova_interaction` and `check_direction`; A-5 only needs to update `gate_check()` to use `check_direction()` result (already exists) and skip ANCOVA.
- h-e1 `curate.py` has `get_corpus_stream` — update its dataset identifier from `"dolma"/"fineweb"` to `"HuggingFaceFW/fineweb"` streaming call.
- h-e1 `evaluate.py` `run_lm_eval` already accepts `tasks` list from config — no structural change needed, just config value.
- Existing 23 tests in `h-e1/code/tests/` should be run against the v2 config to confirm no regressions.
- `SCALE_OVERRIDES` in `train.py` maps scale int → neox config overrides; add entries for `14` and `31`.
