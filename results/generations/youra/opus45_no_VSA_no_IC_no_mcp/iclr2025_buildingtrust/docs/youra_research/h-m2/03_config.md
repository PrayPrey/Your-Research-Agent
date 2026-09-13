# Config: h-m2 (Pareto-Optimal ECE Analysis)

**Format**: Hardcoded dict/module-level constants (matches h-m1/h-e1 pattern — plain `config.py`, no dataclass)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1 data reuse) + module reuse (h-m1 `ece.py`)
**Status**: Serena unavailable in this env; verified via direct Read of actual code (`h-e1/code/config.py`, `h-m1/code/config.py`)
**Config Files Found**: `h-e1/code/config.py` (MODELS list, no MODEL_PARAMS dict), `h-m1/code/config.py` (MODEL_PARAMS dict — required by `ece.py`)
**Pattern Used**: plain module-level constants (no dataclass, no YAML) — consistent with both base configs

**Critical finding**: `h-m1/code/ece.py::generate_synthetic_ece` does `from config import MODEL_PARAMS`. h-e1's config has no such dict (only a `MODELS` list of dicts). h-m2's local `config.py` MUST define `MODEL_PARAMS` (copied verbatim from h-m1), not derive it from h-e1's `MODELS`.

## A-1: config.py [Complexity: 5, Budget: 5]

**Applied**: statistical-hypothesis-test-pipeline (paths + thresholds pattern from h-m1/h-e1)

```python
"""Configuration for h-m2 Pareto-Optimal ECE Analysis."""
from pathlib import Path

SEED = 42
N_BINS = 15

H_E1_SCORES = Path(__file__).parent / "../../h-e1/code/results/scores.csv"
OUTPUT_PATH = Path(__file__).parent / "results"
FIGURES_PATH = Path(__file__).parent / "../figures"

P_THRESHOLD = 0.05
D_THRESHOLD = 0.5  # Cohen's d, medium effect (Cohen 1988)

# Copied verbatim from h-m1/code/config.py (required by ece.py: `from config import MODEL_PARAMS`)
MODEL_PARAMS = {
    "EleutherAI/pythia-70m": 70_000_000,
    "EleutherAI/pythia-160m": 160_000_000,
    "EleutherAI/pythia-410m": 410_000_000,
    "EleutherAI/pythia-1b": 1_000_000_000,
    "EleutherAI/pythia-1.4b": 1_400_000_000,
    "EleutherAI/pythia-2.8b": 2_800_000_000,
    "EleutherAI/pythia-6.9b": 6_900_000_000,
    "EleutherAI/pythia-12b": 12_000_000_000,
    "meta-llama/Llama-2-7b-hf": 7_000_000_000,
    "meta-llama/Llama-2-13b-hf": 13_000_000_000,
    "meta-llama/Llama-2-70b-hf": 70_000_000_000,
    "mistralai/Mistral-7B-v0.1": 7_000_000_000,
    "tiiuae/falcon-7b": 7_000_000_000,
    "tiiuae/falcon-40b": 40_000_000_000,
}
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Paths | `H_E1_SCORES`, `OUTPUT_PATH`, `FIGURES_PATH` (Path objects, relative to file) |
| C-1-2 | MODEL_PARAMS | Copy dict verbatim from `h-m1/code/config.py` |
| C-1-3 | Thresholds | `SEED`, `N_BINS`, `P_THRESHOLD`, `D_THRESHOLD` (from PRD success criteria) |

---

## Analysis Parameters (used inline, not config-driven)

Per PRD success criteria (§5) — these are gate-check constants used directly in `analysis.py`/`run.py`, not config fields:

```python
N_PARETO_MIN = 3     # gate: N(Pareto) >= 3
N_NON_PARETO_MIN = 5  # gate: N(non-Pareto) >= 5
```

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m1/code/config.py (ACTUAL CODE, verified via Read)
SEED = 42
N_BINS = 15
MODEL_PARAMS = { ... }  # 14 models, id -> param count (see A-1 above, copied verbatim)
```

**Not inherited** (h-m1-specific, not needed by h-m2): `N_BOOTSTRAP`, `THRESHOLDS` dict (ece_correlation_r/p, fisher_p), `MODELS` list — h-m2 gets its model list from `scores.csv` rows directly via pandas, no separate `MODELS` list needed.

**Verified from**: `h-m1/code/config.py` (actual implementation, field names confirmed identical: `SEED`, `N_BINS`, `MODEL_PARAMS`).
