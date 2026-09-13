# Architecture: H-E1
## Residual Instability — Existence & Construct Validity (PoC)

**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Tier:** LIGHT
**Type:** Statistical analysis pipeline — no neural network training
**Generated:** 2026-05-12

Applied: modular-pipeline pattern (sklearn PCA + OLS residualization, pandas DataFrame assembly, matplotlib/seaborn visualization)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze. Serena skipped.
**Analyzed Path**: N/A
**Findings**: New implementation from scratch.

---

## File Organization

```
h-e1/
├── code/
│   ├── run_experiment.py       # Main entry point
│   ├── data_assembly.py        # FR-1: Collect & merge benchmark scores
│   ├── compute_ri.py           # FR-2, FR-3: PCA + OLS residualization
│   ├── evaluate.py             # FR-4: Gate evaluation + bootstrap CIs
│   ├── visualize.py            # FR-5: Figure generation
│   ├── config.py               # Fixed configuration and constants
│   └── requirements.txt
├── figures/                    # FR-5 outputs (5 PNG files)
├── results/                    # FR-7 outputs (CSV, YAML, JSON)
└── tests/
    ├── test_data_assembly.py
    ├── test_compute_ri.py
    └── test_evaluate.py
```

---

## Module Structure

### DataAssembler (`code/data_assembly.py`)

**Dependencies**: pandas, datasets, json, config

```python
class DataAssembler:
    def __init__(self, trustllm_data_dir: str, lmeval_results_dir: str): ...
    def load_trustllm_scores(self) -> pd.DataFrame: ...
    def load_lmeval_scores(self) -> pd.DataFrame: ...
    def merge_matrix(self) -> pd.DataFrame: ...
    def validate_matrix(self, df: pd.DataFrame) -> bool: ...

def assemble_matrix(trustllm_data_dir: str, lmeval_results_dir: str) -> pd.DataFrame: ...
```

**Output columns**: `model_id`, `model_family`, `scale`, `training_regime`, `advglue_drop`, `mmlu`, `gsm8k`, `bbh`, `hellaswag`, `winogrande`, `mean_confidence`

---

### RIComputer (`code/compute_ri.py`)

**Dependencies**: pandas, numpy, sklearn, statsmodels, config

```python
class RIComputer:
    def __init__(self, seed: int = 42): ...
    def compute_pc1(self, df: pd.DataFrame) -> tuple[pd.DataFrame, float]: ...
    def fit_ols(self, df: pd.DataFrame) -> tuple[pd.DataFrame, float]: ...
    def check_vif(self, df: pd.DataFrame) -> float: ...
    def compute(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]: ...

def compute_residual_instability(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]: ...
```

**Returns stats keys**: `pc1_var`, `r2_residualization`, `sd_advglue_drop`, `vif`, `gate_sd_passed`, `gate_r2_passed`

---

### GateEvaluator (`code/evaluate.py`)

**Dependencies**: pandas, numpy, scipy, config

```python
class GateEvaluator:
    def __init__(self, sd_threshold: float = 0.05, r2_threshold: float = 0.80,
                 n_bootstrap: int = 10000, seed: int = 42): ...
    def check_gate(self, df: pd.DataFrame, stats: dict) -> dict: ...
    def bootstrap_ci(self, df: pd.DataFrame) -> dict: ...
    def verify_mechanism_activated(self, df: pd.DataFrame, stats: dict) -> tuple[bool, dict]: ...
    def export_results(self, df: pd.DataFrame, stats: dict, gate: dict,
                       output_dir: str) -> None: ...

def run_evaluation(df: pd.DataFrame, stats: dict, output_dir: str) -> dict: ...
```

---

### Visualizer (`code/visualize.py`)

**Dependencies**: pandas, matplotlib, seaborn, config

```python
class Visualizer:
    def __init__(self, figures_dir: str): ...
    def plot_gate_metrics(self, gate: dict) -> str: ...
    def plot_ri_distribution(self, df: pd.DataFrame) -> str: ...
    def plot_advglue_hist(self, df: pd.DataFrame) -> str: ...
    def plot_pc1_scatter(self, df: pd.DataFrame) -> str: ...
    def plot_ri_regime(self, df: pd.DataFrame) -> str: ...
    def generate_all(self, df: pd.DataFrame, gate: dict) -> list[str]: ...

def generate_figures(df: pd.DataFrame, gate: dict, figures_dir: str) -> list[str]: ...
```

---

### Config (`code/config.py`)

**Dependencies**: none

```python
SEED: int = 42
SD_THRESHOLD: float = 0.05
R2_THRESHOLD: float = 0.80
PC1_VAR_THRESHOLD: float = 0.70
VIF_THRESHOLD: float = 5.0
N_BOOTSTRAP: int = 10000
MIN_MODELS: int = 30
MIN_FAMILIES: int = 3
CAP_COLS: list[str] = ["mmlu", "gsm8k", "bbh", "hellaswag", "winogrande"]
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: DataAssembler, RIComputer, GateEvaluator, Visualizer, config

```python
def parse_args() -> argparse.Namespace: ...
def main() -> None: ...
    # 1. Assemble model × benchmark matrix
    # 2. Compute PC1 + RI via OLS residualization
    # 3. Evaluate gate conditions + bootstrap CIs
    # 4. Generate 5 required figures
    # 5. Export CSV / YAML / JSON results
```

---

## Module Dependencies

```
run_experiment.py
  ├── data_assembly.py  →  config.py
  ├── compute_ri.py     →  config.py
  ├── evaluate.py       →  config.py
  └── visualize.py      →  config.py
```

---

## Proposed Epic Tasks

### Epic E1: Data Assembly
**ID:** E1
**Title:** Assemble Model × Benchmark Matrix
**Description:** Implement `data_assembly.py`. Load TrustLLM AdvGLUE scores via HuggingFace `datasets` library and lm-eval JSON outputs for ≥30 LLMs. Merge into unified DataFrame with 11+ columns. Validate diversity constraints (≥3 families, ≥2 scales, ≥2 regimes, ≤30% missing).
**Files:** `code/data_assembly.py`, `code/config.py`, `requirements.txt`, `tests/test_data_assembly.py`
**Complexity:** 13/20 (Module_Size=3 + Dependencies=4 + Algorithm=2 + Integration=4)

---

### Epic E2: RI Computation (PCA + OLS)
**ID:** E2
**Title:** Compute Capability-PC1 and OLS Residual Instability
**Description:** Implement `compute_ri.py`. StandardScaler + PCA(n_components=1) on 5 capability benchmarks (assert ≥70% variance). OLS residualization of AdvGLUE_drop on [PC1, mean_confidence]. VIF check via statsmodels. Store RI column and stats dict.
**Files:** `code/compute_ri.py`, `tests/test_compute_ri.py`
**Complexity:** 12/20 (Module_Size=3 + Dependencies=3 + Algorithm=4 + Integration=2)

---

### Epic E3: Gate Evaluation + Bootstrap CIs
**ID:** E3
**Title:** Gate Condition Evaluation and Statistical Validation
**Description:** Implement `evaluate.py`. Check SD(AdvGLUE_drop) > 5% and R² < 0.80. Bootstrap CIs (10,000 samples, seed=42) for both metrics. Capability-only baseline OLS (PC1 only). Export gate_results.yaml and stats_summary.json.
**Files:** `code/evaluate.py`, `tests/test_evaluate.py`
**Complexity:** 11/20 (Module_Size=3 + Dependencies=2 + Algorithm=4 + Integration=2)

---

### Epic E4: Visualization
**ID:** E4
**Title:** Generate 5 Required Figures
**Description:** Implement `visualize.py`. Produce all 5 figures: bar chart (gate metrics vs thresholds), violin plot (RI by model family), histogram (AdvGLUE drop distribution), scatter (PC1 vs AdvGLUE drop with OLS fit line), box plot (RI by training regime). Save to `h-e1/figures/`.
**Files:** `code/visualize.py`
**Complexity:** 9/20 (Module_Size=2 + Dependencies=2 + Algorithm=2 + Integration=3)

---

### Epic E5: Entry Point + Integration
**ID:** E5
**Title:** Run Experiment Entry Point and End-to-End Integration
**Description:** Implement `run_experiment.py` orchestrating all modules sequentially. Export model_matrix.csv. Verify all 5 figures exist and results files written. Confirm `python run_experiment.py` runs without error.
**Files:** `code/run_experiment.py`, `results/` (outputs), `figures/` (outputs)
**Complexity:** 8/20 (Module_Size=2 + Dependencies=3 + Algorithm=1 + Integration=4) (wait — corrected: Module_Size=2 + Dependencies=3 + Algorithm=1 + Integration=2 = 8)

---

## Task Distribution

| ID | Task | Complexity |
|----|------|------------|
| E1 | Assemble Model × Benchmark Matrix | 13/20 |
| E2 | Compute Capability-PC1 and OLS RI | 12/20 |
| E3 | Gate Evaluation + Bootstrap CIs | 11/20 |
| E4 | Generate 5 Required Figures | 9/20 |
| E5 | Entry Point + Integration | 8/20 |

**Distribution**: High(11-14): [E1, E2, E3], Medium(7-10): [E4, E5]

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | >=2.0 | DataFrame assembly and manipulation |
| numpy | >=1.24 | Numerical operations, bootstrap sampling |
| scikit-learn | >=1.3 | PCA, StandardScaler, LinearRegression |
| statsmodels | >=0.14 | VIF computation |
| scipy | >=1.10 | Bootstrap statistics |
| pingouin | ==0.6.1 | Spearman partial correlation |
| matplotlib | >=3.7 | Figure generation |
| seaborn | >=0.12 | Violin/box plots |
| datasets | >=2.14 | TrustLLM HuggingFace loader |
| pyyaml | >=6.0 | gate_results.yaml export |

**Data Sources:**
- `TrustLLM/TrustLLM-dataset` (HuggingFace, gated — requires account agreement)
- lm-evaluation-harness CLI JSON outputs (EleutherAI/lm-evaluation-harness)
