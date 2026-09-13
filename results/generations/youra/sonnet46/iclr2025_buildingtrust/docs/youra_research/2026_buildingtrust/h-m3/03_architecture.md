# H-M3 Architecture: Mechanism Discrimination (H1 vs H2 vs H3)

Applied: incremental-extension-with-sys-path-inheritance

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (h-m2, h-e1 — read via direct file inspection; Serena project activation failed, files read directly)
**Analyzed Path**: `docs/youra_research/20260315_buildingtrust/h-m2/code/` and `docs/youra_research/20260315_buildingtrust/h-e1/code/`
**Findings**: H-M2 uses `sys.path.insert(0, h_e1_code_dir)` + `from calibration_analysis import load_lmeval_samples`. Model key format: `pythia-{size}-{alignment}`. Config anchors via `Path(__file__).parent.resolve()`. Visualization uses `matplotlib.use("Agg")` + module-level `COLORS` dict. Gate/report in separate `gate_and_report.py`.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_lmeval_samples | `from calibration_analysis import load_lmeval_samples` | `h-e1/code/calibration_analysis.py` |
| compute_brier_decomposition | `from calibration_analysis import compute_brier_decomposition` | `h-e1/code/calibration_analysis.py` |
| compute_ece | `from calibration_analysis import compute_ece` | `h-e1/code/calibration_analysis.py` |
| compute_delta_reliability | `from calibration_analysis import compute_delta_reliability` | `h-e1/code/calibration_analysis.py` |
| load_logprob_matrices | `from load_data import load_logprob_matrices` | `h-m2/code/load_data.py` |

**sys.path pattern** (verified from h-m2/code/load_data.py line 14-17):
```python
_H_E1_CODE_DIR = str(Path(__file__).parent.parent.parent / "h-e1" / "code")
if _H_E1_CODE_DIR not in sys.path:
    sys.path.insert(0, _H_E1_CODE_DIR)
```

**Verified from**: `h-m2/code/load_data.py` and `h-e1/code/calibration_analysis.py` (actual implementation)

---

## File Organization

- `h-m3/code/`
  - `config.py` — paths, constants, gate thresholds, model registry
  - `load_data.py` — MMLU data loading (Path A/B) + TruthfulQA lm-eval runner
  - `spearman_analysis.py` — per-item Spearman ρ, mean ρ aggregation
  - `argmax_partition.py` — shared/changed-argmax partition, Brier subsets, Cohen's d
  - `truthfulqa_analysis.py` — TruthfulQA MC1 lm-eval runner + ECE computation
  - `mechanism_report.py` — H1/H2/H3 discrimination logic, 04_validation.md writer, verification_state.yaml updater
  - `visualization.py` — 5 figures per FR-6
  - `run_experiment.py` — orchestration entry point
  - `tests/`
    - `test_spearman_analysis.py`
    - `test_argmax_partition.py`
    - `test_truthfulqa_analysis.py`
    - `test_mechanism_report.py`
    - `conftest.py`
- `h-m3/figures/` — output figure directory
- `h-m3/04_validation.md` — written by mechanism_report.py
- `h-m3/experiment_results.json` — written by run_experiment.py

---

## Module Definitions

### config (`h-m3/code/config.py`)

**Dependencies**: pathlib, (none external)

```python
# Directory anchoring
_CODE_DIR: Path
_H_M3_DIR: Path
_H_M2_DIR: Path
_H_E1_DIR: Path

# External paths
H_E1_RESULTS_DIR: str
H_E1_CODE_DIR: str
H_M2_RESULTS_DIR: str

# H-M3 output paths
H_M3_RESULTS_DIR: str          # h-m3/code/results/
H_M3_TRUTHFULQA_DIR: str       # h-m3/code/results/truthfulqa/
H_M3_FIGURES_DIR: str          # h-m3/figures/
H_M3_REPORT_PATH: str          # h-m3/04_validation.md
H_M3_EXPERIMENT_RESULTS_JSON: str
VERIFICATION_STATE_PATH: str

# Gate thresholds
GATE_TYPE: str                 # "SHOULD_WORK"
H1_RHO_THRESHOLD: float        # 0.9
H2_RHO_THRESHOLD: float        # 0.85
H1_COHENS_D_THRESHOLD: float   # 0.1

# Experiment constants
SIZES: list                    # ["1.4b", "2.8b", "6.9b"]
ALIGNMENTS: list               # ["sft", "dpo", "ppo"]
N_ITEMS_EXPECTED: int          # 14042
N_TRUTHFULQA_EXPECTED: int     # 817
N_BOOTSTRAP: int               # 1000
SEED: int                      # 42
N_BINS: int                    # 15

# Model registry (same as h-m2)
MODEL_REGISTRY: dict
BASE_MODEL_KEYS: list
ALIGNED_MODEL_KEYS: list
ALL_MODEL_KEYS: list
HF_MODEL_IDS: dict

# lm-eval config
LMEVAL_NUM_FEWSHOT_MMLU: int   # 4
LMEVAL_NUM_FEWSHOT_TQA: int    # 0
LMEVAL_BATCH_SIZE: str
FIGURE_DPI: int                # 150
```

---

### load_data (`h-m3/code/load_data.py`)

**Dependencies**: config, calibration_analysis (h-e1 via sys.path), load_data (h-m2 pattern adapted)

```python
def load_logprob_matrices(
    h_e1_results_dir: str,
    h_m3_results_dir: str,
    sizes: list,
    alignments: list,
    device: str = "cuda",
) -> tuple[dict, str]:
    """Dispatcher: Path A (h-e1 cache) → Path B (re-run lm-eval for MMLU).
    Returns: ({model_key: (N,4) float64}, execution_path)
    model_key format: 'pythia-{size}-{alignment}'
    """

def load_labels(
    h_e1_results_dir: str,
    sizes: list,
) -> dict[str, np.ndarray]:
    """Load y_true (N,) int64 per base model_key from h-e1 JSONL outputs.
    Returns: {'pythia-{size}-base': y_true}
    """
```

---

### spearman_analysis (`h-m3/code/spearman_analysis.py`)

**Dependencies**: numpy, scipy.stats, config

```python
def compute_spearman_rho_per_item(
    base_logprobs: np.ndarray,
    aligned_logprobs: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Per-item Spearman ρ over 4-option log-prob vectors.
    Args:
        base_logprobs: (N, 4) float64
        aligned_logprobs: (N, 4) float64
    Returns:
        rho_per_item: (N,) float64
        mean_rho: float
    """

def compute_all_spearman_results(
    logprob_matrices: dict,
    sizes: list,
    alignments: list,
) -> dict:
    """Compute Spearman ρ for all 9 base-aligned pairs.
    Returns: {
        '{size}-{alignment}': {
            'rho_per_item': np.ndarray,
            'mean_rho': float,
            'h1_pass': bool,
            'h2_flag': bool,
        }
    }
    """

def assess_h1_h2_gate(
    spearman_results: dict,
    h1_threshold: float = 0.9,
    h2_threshold: float = 0.85,
) -> dict:
    """Assess H1/H2 gate: all 9 pairs must pass H1.
    Returns: {'gate_pass': bool, 'n_h1_pass': int, 'n_h2_flag': int, 'per_pair': dict}
    """
```

---

### argmax_partition (`h-m3/code/argmax_partition.py`)

**Dependencies**: numpy, scipy.special (softmax), calibration_analysis (h-e1), config

```python
def partition_items_by_argmax(
    base_logprobs: np.ndarray,
    aligned_logprobs: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Partition N MMLU items into shared/changed-argmax subsets.
    Returns:
        shared_mask: (N,) bool
        changed_mask: (N,) bool
    """

def compute_brier_reliability_subset(
    probs: np.ndarray,
    labels: np.ndarray,
    mask: np.ndarray,
    n_bins: int = 15,
) -> float:
    """Brier reliability (Murphy 1973) for a masked subset.
    Args:
        probs: (N, 4) softmax probabilities
        labels: (N,) int64
        mask: (N,) bool
    Returns: reliability float
    """

def compute_cohens_d(
    group1: np.ndarray,
    group2: np.ndarray,
) -> float:
    """Cohen's d effect size: (mean1 - mean2) / pooled_std."""

def compute_all_partition_results(
    logprob_matrices: dict,
    labels: dict,
    sizes: list,
    alignments: list,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> dict:
    """Compute shared/changed-argmax Brier partition for all 9 pairs.
    Returns: {
        '{size}-{alignment}': {
            'shared_mask': np.ndarray,
            'changed_mask': np.ndarray,
            'n_shared': int, 'n_changed': int,
            'rel_shared_base': float, 'rel_shared_aligned': float,
            'rel_changed_base': float, 'rel_changed_aligned': float,
            'cohens_d_shared': float,
            'h1_signature': bool,
            'h2_check': bool,
        }
    }
    """
```

---

### truthfulqa_analysis (`h-m3/code/truthfulqa_analysis.py`)

**Dependencies**: config, calibration_analysis (h-e1 via sys.path), subprocess, numpy

```python
def run_lmeval_truthfulqa(
    model_key: str,
    hf_id: str,
    output_dir: str,
    device: str = "cuda",
    timeout: int = 7200,
) -> str:
    """Run lm_eval --tasks truthfulqa_mc1 --log_samples for one model.
    Returns: output directory path
    Raises: RuntimeError on failure.
    """

def load_truthfulqa_logprobs(
    model_key: str,
    results_dir: str,
) -> tuple[list, np.ndarray]:
    """Load per-item TruthfulQA MC1 log-probs (variable options).
    Returns:
        logprobs_list: list of (K_i,) arrays (variable K per item)
        y_true: (N,) int64
    """

def compute_truthfulqa_ece_all_models(
    tqa_results_dir: str,
    h_e1_results_dir: str,
    sizes: list,
    alignments: list,
    hf_model_ids: dict,
    device: str = "cuda",
    n_bins: int = 15,
) -> dict:
    """Run or load TruthfulQA MC1, compute ECE for all 12 models.
    Returns: {
        'pythia-{size}-{alignment}': {'ece': float, 'n_items': int}
    }
    """

def assess_h3_diagnostic(
    tqa_ece_results: dict,
    mmlu_ece_results: dict,
    sizes: list,
    alignments: list,
) -> dict:
    """H3 test: TruthfulQA ECE increase >> MMLU ECE increase.
    Returns: {'h3_flag': bool, 'per_alignment': dict}
    """
```

---

### mechanism_report (`h-m3/code/mechanism_report.py`)

**Dependencies**: config, spearman_analysis, argmax_partition, truthfulqa_analysis, json, yaml, pathlib

```python
def determine_dominant_mechanism(
    spearman_gate: dict,
    partition_results: dict,
    h3_diagnostic: dict,
    sizes: list,
    alignments: list,
) -> dict:
    """Apply FR-5.1 discrimination logic.
    Returns: {
        'dominant': 'H1' | 'H2' | 'H3' | 'ambiguous',
        'h1_confirmed': bool, 'h2_dominant': bool, 'h3_flag': bool,
        'per_alignment': dict,
        'gate_pass': bool,
        '6.9b_ppo_exception': str,
    }
    """

def write_validation_report(
    mechanism_result: dict,
    spearman_results: dict,
    partition_results: dict,
    tqa_ece_results: dict,
    output_path: str,
) -> None:
    """Write FR-7.1 04_validation.md with all required sections."""

def update_verification_state(
    state_path: str,
    gate_pass: bool,
    dominant_mechanism: str,
    key_metrics: dict,
) -> None:
    """Update verification_state.yaml with h-m3 gate result."""

def save_experiment_results(
    all_results: dict,
    output_path: str,
) -> None:
    """Save experiment_results.json with all computed metrics."""
```

---

### visualization (`h-m3/code/visualization.py`)

**Dependencies**: matplotlib (Agg backend), numpy, config

```python
COLORS: dict  # {"ppo": "red", "dpo": "orange", "sft": "blue", "base": "gray"}

def plot_spearman_rho_bar(
    spearman_results: dict,
    figures_dir: str,
    h1_threshold: float = 0.9,
    h2_threshold: float = 0.85,
    dpi: int = 150,
) -> str:
    """FR-6.1 Gate chart: mean ρ per alignment × size, H1/H2 thresholds.
    Returns: figure path (figure_01_spearman_rho.png)
    """

def plot_rho_distribution(
    spearman_results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """FR-6.2 Violin/histogram of per-item ρ distribution.
    Returns: figure_02_rho_distribution.png
    """

def plot_brier_partition(
    partition_results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """FR-6.3 Grouped bar: shared vs changed-argmax Brier reliability, Cohen's d.
    Returns: figure_03_brier_partition.png
    """

def plot_argmax_proportion(
    partition_results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """FR-6.4 Stacked bar: % shared vs changed-argmax per model.
    Returns: figure_04_argmax_proportion.png
    """

def plot_truthfulqa_ece(
    tqa_ece_results: dict,
    mmlu_ece_results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """FR-6.5 TruthfulQA MC1 ECE vs MMLU ECE side-by-side.
    Returns: figure_05_truthfulqa_ece.png
    """

def generate_all_figures(
    spearman_results: dict,
    partition_results: dict,
    tqa_ece_results: dict,
    mmlu_ece_results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> list[str]:
    """Generate all 5 figures; return list of saved paths."""
```

---

### run_experiment (`h-m3/code/run_experiment.py`)

**Dependencies**: all modules, config, logging, argparse

```python
def main(
    device: str = "cuda",
    smoke_test: bool = False,
) -> None:
    """Orchestrate full H-M3 experiment pipeline.
    1. Load MMLU logprob matrices (Path A → B)
    2. Compute Spearman ρ for all 9 pairs
    3. Compute shared/changed-argmax Brier partition
    4. Run/load TruthfulQA MC1 ECE
    5. Determine dominant mechanism (H1/H2/H3)
    6. Generate 5 figures
    7. Write 04_validation.md + verification_state.yaml + experiment_results.json
    """
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + Project Setup | config.py with all paths, thresholds, model registry; directory creation; logging setup | 6 | 2+1+1+2 |
| A-2 | Data Loading (MMLU) | load_data.py: Path A/B dispatcher, load_logprob_matrices, load_labels; adapt h-m2 pattern for h-m3 paths | 9 | 2+3+2+2 |
| A-3 | Spearman Analysis | spearman_analysis.py: per-item ρ via scipy.stats.spearmanr, mean ρ aggregation, H1/H2 gate assessment | 10 | 2+2+3+3 |
| A-4 | Argmax Partition + Brier Subsets | argmax_partition.py: shared/changed mask, per-subset Brier reliability, Cohen's d, H1 signature test | 12 | 3+3+3+3 |
| A-5 | TruthfulQA Analysis | truthfulqa_analysis.py: lm-eval runner (variable-option format), ECE per model, H3 diagnostic | 14 | 3+3+4+4 |
| A-6 | Mechanism Report | mechanism_report.py: H1/H2/H3 discrimination logic, 04_validation.md writer, verification_state.yaml updater, experiment_results.json | 12 | 3+2+4+3 |
| A-7 | Visualization | visualization.py: 5 figures per FR-6 (bar, violin, grouped bar, stacked bar, comparison) | 11 | 3+1+4+3 |
| A-8 | Orchestration + Tests | run_experiment.py + test suite (min 3 test methods per module, real assertions) | 10 | 2+2+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-3, A-4, A-6, A-7, A-8], Low(4-8): [A-1, A-2]
