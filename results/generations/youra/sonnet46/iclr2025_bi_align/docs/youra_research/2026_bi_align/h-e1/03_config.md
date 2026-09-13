# Configuration: h-e1 — Semantic Accommodation Existence (EXISTENCE PoC)

**Hypothesis:** h-e1
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-15
**Applied:** Standard reproducibility pattern (seed=42, single config, minimal epochs/bootstrap)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Config Files Found**: None — new config design
**Pattern Used**: YAML experiment config + Python dataclass for results; inline constants in module files (no separate config.py)

---

## Inline Constants (Per Module)

Architecture uses inline constants — no centralized config.py. Constants live in their respective modules.

| Constant | Value | Module | Rationale |
|----------|-------|--------|-----------|
| `SEED` | `42` | controls.py, statistics.py | Standard reproducibility seed |
| `KNN_K` | `5` | controls.py | Balances topic specificity vs noise |
| `BOOTSTRAP_N` | `1000` | statistics.py | Standard bootstrap iterations for CI |
| `BATCH_SIZE` | `256` | embedder.py | SBERT default; fits ~8GB RAM for 273K turns |
| `EMBED_DIM` | `384` | embedder.py | all-MiniLM-L6-v2 output dimension |
| `MIN_N_PAIRS` | `1000` | statistics.py | Gate guard: minimum pairs for valid stats |
| `SIGNIFICANCE_LEVEL` / `ALPHA` | `0.05` | statistics.py | Standard alpha threshold |
| `COHEN_D_THRESHOLD` | `0.1` | statistics.py | Small-effect floor per PRD success criterion |
| `DEFAULT_MODEL` | `"all-MiniLM-L6-v2"` | embedder.py, run_experiment.py | Primary SBERT model (384-dim, fast) |
| `ROBUSTNESS_MODELS` | `["paraphrase-MiniLM-L6-v2", "all-mpnet-base-v2"]` | run_experiment.py | Two additional SBERT models for FR-9 |
| `SPLITS` | `["helpful-base", "helpful-rejection-sampled", "helpful-online"]` | data_loader.py | All 3 HH-RLHF helpfulness splits |
| `FIGURES_DIR` | `"figures"` | visualize.py | Relative to h-e1/ root |
| `RESULTS_PATH` | `"results.json"` | run_experiment.py | Relative to h-e1/ root |
| `HYPOTHESIS_DIR` | `"."` | run_experiment.py | h-e1/ root when run from that directory |

---

## YAML Experiment Config Schema

For reproducibility, the orchestration script may optionally load or log this schema. Save as `experiment_config.yaml` in h-e1/ root.

```yaml
# h-e1 Experiment Configuration
# All values must match inline constants in code modules

experiment:
  hypothesis_id: "h-e1"
  type: "EXISTENCE"
  seed: 42

data:
  dataset_name: "Anthropic/hh-rlhf"
  splits:
    - "helpful-base"
    - "helpful-rejection-sampled"
    - "helpful-online"
  min_n_pairs: 1000

embedding:
  default_model: "all-MiniLM-L6-v2"
  embed_dim: 384
  batch_size: 256
  normalize_embeddings: true
  cache_dir: "embeddings"

controls:
  knn_k: 5
  knn_metric: "cosine"

statistics:
  bootstrap_n: 1000
  alpha: 0.05
  cohen_d_threshold: 0.1
  mann_whitney_alternative: "greater"

robustness:
  models:
    - "paraphrase-MiniLM-L6-v2"
    - "all-mpnet-base-v2"
  run_sequential: true

output:
  figures_dir: "figures"
  results_path: "results.json"
  figure_dpi: 300
  figure_format: "png"

logging:
  level: "INFO"
  log_file: "experiment.log"
```

---

## Python Dataclass — ExperimentResults

Place in `run_experiment.py` or a shared `results_schema.py`. Serializes to results.json.

```python
from dataclasses import dataclass, field, asdict
from typing import Optional
import json


@dataclass
class BootstrapResult:
    mean: float = 0.0
    ci_lower: float = 0.0
    ci_upper: float = 0.0


@dataclass
class MannWhitneyResult:
    statistic: float = 0.0
    p_value: float = 1.0
    significant: bool = False


@dataclass
class CosineMeans:
    cos_actual: float = 0.0
    cos_topic: float = 0.0
    cos_random: float = 0.0


@dataclass
class GateIndicators:
    embeddings_computed: bool = False
    c_sem_positive: bool = False
    ci_lower_positive: bool = False
    ordering_holds: bool = False
    sufficient_pairs: bool = False


@dataclass
class ExperimentResults:
    # Metadata
    model_name: str = "all-MiniLM-L6-v2"
    n_pairs: int = 0
    seed: int = 42

    # Core metric
    c_sem: float = 0.0
    c_sem_bootstrap: BootstrapResult = field(default_factory=BootstrapResult)

    # Cosine similarity means (post-residualization)
    cosine_means: CosineMeans = field(default_factory=CosineMeans)

    # Statistical tests
    mw_actual_vs_topic: MannWhitneyResult = field(default_factory=MannWhitneyResult)
    mw_topic_vs_random: MannWhitneyResult = field(default_factory=MannWhitneyResult)

    # Effect sizes
    cohen_d_actual_vs_topic: BootstrapResult = field(default_factory=BootstrapResult)
    cohen_d_topic_vs_random: BootstrapResult = field(default_factory=BootstrapResult)

    # Gate
    gate_indicators: GateIndicators = field(default_factory=GateIndicators)
    gate_passed: bool = False

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def from_json(cls, path: str) -> "ExperimentResults":
        with open(path) as f:
            data = json.load(f)
        # Nested dataclass reconstruction omitted for brevity — use asdict output directly
        return data
```

---

## A-6: Visualization & Orchestration [Complexity: 14, Budget: 3 subtasks]

Applied: Standard matplotlib figure spec pattern

### C-6-1: `plot_gate_metrics()` Figure Spec

**What to implement:** Bar chart showing C_sem and three cosine similarity levels with error bars.

**Figure layout:**
```python
# Figure spec constants (in visualize.py)
GATE_FIG_SIZE = (10, 5)       # inches — two-panel layout
GATE_FIG_DPI = 300
GATE_FIG_FORMAT = "png"
GATE_FIG_FILENAME = "gate_metrics.png"

# Color scheme
COLOR_ACTUAL = "#2196F3"      # blue — actual AI response
COLOR_TOPIC  = "#FF9800"      # orange — topic-matched control
COLOR_RANDOM = "#9E9E9E"      # grey — random baseline
COLOR_C_SEM  = "#4CAF50"      # green — C_sem bar
```

**Layout spec:**
- Left panel: single bar for C_sem with 95% CI error bar; horizontal dashed line at y=0
- Right panel: three grouped bars (cos_actual, cos_topic, cos_random) with bootstrap CI error bars
- Both panels: xlabel="Control Level", ylabel="Cosine Similarity"
- Title: "Gate Metrics: Semantic Accommodation (h-e1)"
- Save: `{output_dir}/gate_metrics.png` at DPI=300

**Expected output:** `figures/gate_metrics.png`

---

### C-6-2: `run_experiment()` Orchestration Config

**What to implement:** Logging setup, directory creation, results.json schema wiring.

**Logging setup:**
```python
# In run_experiment.py setup block
import logging, os, json

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_LEVEL = logging.INFO
LOG_FILE = "experiment.log"   # written to HYPOTHESIS_DIR

def setup_logging(hypothesis_dir: str) -> None:
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(os.path.join(hypothesis_dir, LOG_FILE)),
            logging.StreamHandler(),
        ]
    )
```

**Directory creation:**
```python
REQUIRED_DIRS = ["embeddings", "figures"]

def setup_dirs(hypothesis_dir: str) -> None:
    for d in REQUIRED_DIRS:
        os.makedirs(os.path.join(hypothesis_dir, d), exist_ok=True)
```

**Key log events to emit:**
- Model name, N_pairs extracted, embedding time (seconds)
- C_sem value, bootstrap CI bounds
- Gate pass/fail result

**results.json schema:** Uses `ExperimentResults.to_json()` defined above. Must be written as final step of `run_experiment()`.

**Expected output:** `results.json` + `experiment.log` in h-e1/ root

---

### C-6-3: `run_robustness_checks()` Config

**What to implement:** Sequential execution of `run_experiment()` for two additional SBERT models.

**Robustness model list:**
```python
ROBUSTNESS_MODELS = ["paraphrase-MiniLM-L6-v2", "all-mpnet-base-v2"]
```

**Execution mode:** Sequential (not parallel) — avoids GPU/CPU memory contention during SBERT encoding.

**Output structure:**
```python
# run_robustness_checks() returns:
{
    "paraphrase-MiniLM-L6-v2": <results_dict>,
    "all-mpnet-base-v2": <results_dict>,
}
# Written to: results_robustness.json (separate from primary results.json)
```

**Expected output:** `results_robustness.json` in h-e1/ root; console log of per-model gate_passed status

---

## A-4: C_sem & Residualization [Complexity: 11, Budget: 1 subtask]

Applied: Standard OLS residualization pattern (statsmodels)

### C-4-1: `apply_residualization()` OLS Config

**What to implement:** Two-pass OLS residualization of cosine similarity arrays before C_sem computation.

**Covariate order (fixed):**
1. Length residualization first: `cos ~ token_count(A_t)` — removes response length confound
2. Lexical overlap residualization second: `cos ~ jaccard(H_{t+1}, A_t)` — removes lexical similarity confound

**OLS usage pattern:**
```python
import statsmodels.api as sm
import numpy as np

def residualize(cos_array: np.ndarray, covariate: np.ndarray) -> np.ndarray:
    X = sm.add_constant(covariate.astype(float))
    model = sm.OLS(cos_array.astype(float), X)
    result = model.fit()
    return result.resid.astype(np.float32)

def apply_residualization(
    cos_dict: dict,          # keys: cos_actual, cos_topic, cos_random (each np.ndarray shape N)
    token_counts: np.ndarray,   # shape (N,) — A_t token counts
    jaccard_overlaps: np.ndarray  # shape (N,) — Jaccard(H_next, A_t)
) -> dict:
    out = {}
    for key, cos_array in cos_dict.items():
        # Pass 1: length
        residuals_len = residualize(cos_array, token_counts)
        # Pass 2: lexical overlap
        residuals_final = residualize(residuals_len, jaccard_overlaps)
        out[key] = residuals_final
    return out
```

**Which arrays receive residualization:** All three — `cos_actual`, `cos_topic`, `cos_random`.

**Expected output:** Updated `cos_dict` with residualized float32 arrays, same shape (N,) as inputs.

---

## Subtask Summary

| ID | Module | Subtask | Expected Output |
|----|--------|---------|-----------------|
| C-6-1 | visualize.py | `plot_gate_metrics()` figure spec | `figures/gate_metrics.png` (300 DPI) |
| C-6-2 | run_experiment.py | Orchestration logging + dirs + results.json | `results.json`, `experiment.log` |
| C-6-3 | run_experiment.py | `run_robustness_checks()` sequential config | `results_robustness.json` |
| C-4-1 | accommodation.py | `apply_residualization()` OLS two-pass | Residualized cos_dict (float32) |

**Total subtasks used: 4 / 4**
