# H-M2 Architecture: Pre-Softmax Logit Margin Inflation

Applied: N/A — no relevant patterns in KB (KB contains diffusion model content only)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1 and h-m1)
**Status**: Serena MCP requires active project selection; code read directly via file tool
**Analyzed Path**: `h-e1/code/`, `h-m1/code/`
**Findings**: h-e1/code/calibration_analysis.py contains `load_lmeval_samples()` (returns `(logprobs: (N,4), y_true: (N,))`) and `compute_ece()`, `compute_brier_decomposition()`, `compute_delta_reliability()`. h-m1/code/ follows an orchestrator pattern: `config.py` (paths/constants) + `run_experiment.py` (main pipeline) + `extract_h_e1_data.py` + `gate_and_report.py` + `plot_results.py`. H-M2 adopts the same structure.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_lmeval_samples | `from calibration_analysis import load_lmeval_samples` | `h-e1/code/calibration_analysis.py` |
| compute_ece | `from calibration_analysis import compute_ece` | `h-e1/code/calibration_analysis.py` |
| compute_brier_decomposition | `from calibration_analysis import compute_brier_decomposition` | `h-e1/code/calibration_analysis.py` |
| MODEL_REGISTRY / MODELS | `from calibration_analysis import MODEL_REGISTRY, MODELS, BASE_MODEL_IDS, ALIGNED_MODEL_IDS` | `h-e1/code/calibration_analysis.py` |

**Verified from**: `h-e1/code/calibration_analysis.py` (actual implementation)

**Key discovery**: `load_lmeval_samples(model_id, results_dir)` globs `{results_dir}/{model_id}/**/samples_mmlu*.jsonl` and returns `(logprobs: np.ndarray (N,4), y_true: np.ndarray (N,))`. This is the exact function h-m2 reuses for logprob loading on Path A.

---

## File Structure

- `h-m2/code/`
  - `config.py` — paths, constants, model registry reference
  - `margin_analysis.py` — core margin computation module
  - `load_data.py` — Path A (h-e1 cache load) + Path B (lm-eval re-run) dispatch
  - `gate_and_report.py` — gate evaluation + validation report generation
  - `visualization.py` — 5 figures
  - `run_margin_analysis.py` — entry point orchestrator
- `h-m2/figures/` — figure_01 through figure_05
- `h-m2/results/` — Path B lm-eval outputs (if needed)
- `h-m2/04_validation.md` — generated validation report

---

## Module Definitions

### config (`h-m2/code/config.py`)

**Dependencies**: pathlib, os

```python
# Path anchoring (same pattern as h-m1/code/config.py)
_CODE_DIR: Path = Path(__file__).parent.resolve()
_H_M2_DIR: Path = _CODE_DIR.parent
_H_E1_DIR: Path = _H_M2_DIR.parent / "h-e1"
_H_M1_DIR: Path = _H_M2_DIR.parent / "h-m1"

H_E1_RESULTS_DIR: str       # h-e1/code/results or h-e1/results
H_E1_CODE_DIR: str          # h-e1/code (for sys.path insert)
H_E1_VALIDATION_PATH: str   # h-e1/04_validation.md (DELTA_ECE source)
H_M2_RESULTS_DIR: str       # h-m2/results (Path B outputs)
H_M2_FIGURES_DIR: str       # h-m2/figures
H_M2_REPORT_PATH: str       # h-m2/04_validation.md
H_M2_EXPERIMENT_RESULTS_JSON: str
VERIFICATION_STATE_PATH: str

# Gate configuration
GATE_TYPE: str = "SHOULD_WORK"
MIN_PPO_SIZES_PASSING: int = 2
N_BOOTSTRAP: int = 1000
SEED: int = 42
SIZES: list[str] = ["1.4b", "2.8b", "6.9b"]
ALIGNMENTS: list[str] = ["sft", "dpo", "ppo"]
N_ITEMS_EXPECTED: int = 14042

# lm-eval Path B configuration
LMEVAL_NUM_FEWSHOT: int = 4
LMEVAL_TIMEOUT_SECONDS: int = 7200
FIGURE_DPI: int = 150
```

---

### margin_analysis (`h-m2/code/margin_analysis.py`)

**Dependencies**: numpy, scipy.stats

```python
import numpy as np
from scipy import stats

def compute_logit_margins(logprob_matrix: np.ndarray) -> np.ndarray:
    """
    Args:
        logprob_matrix: (N_items, 4) pre-softmax log-probs
    Returns:
        margins: (N_items,) — top1 − top2 log-prob per item
    """
    ...

def compute_delta_margin(
    base_logprobs: np.ndarray,
    aligned_logprobs: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """
    Returns: (delta_mean, ci_lower_95, ci_upper_95) in nats
    """
    ...

def compute_all_delta_margins(
    logprob_matrices: dict[str, np.ndarray],
    sizes: list[str],
    alignments: list[str],
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> dict[str, tuple[float, float, float]]:
    """
    Compute delta margins for all 9 alignment-size pairs.
    Args:
        logprob_matrices: {model_key: (N,4)} e.g. "pythia-1.4b-base"
    Returns:
        {"{alignment}_{size}": (delta_mean, ci_lower, ci_upper)}
    """
    ...

def test_gradient_ordering(
    delta_ppo: list[float],
    delta_dpo: list[float],
    delta_sft: list[float],
) -> dict[str, float]:
    """
    Wilcoxon signed-rank (one-sided) across 3 Pythia sizes.
    Returns: {'ppo_ge_dpo_stat', 'ppo_ge_dpo_p', 'dpo_gt_sft_stat', 'dpo_gt_sft_p'}
    """
    ...

def verify_mechanism_activated(results_dict: dict) -> tuple[bool, dict]:
    """
    Checks shape, positive margins, delta computed.
    Returns: (mechanism_verified: bool, indicators: dict)
    """
    ...
```

---

### load_data (`h-m2/code/load_data.py`)

**Dependencies**: config, calibration_analysis (h-e1), subprocess, sys

```python
import sys
import numpy as np

def load_logprob_matrices_path_a(
    results_dir: str,
    sizes: list[str],
    alignments: list[str],
) -> tuple[dict[str, np.ndarray], str]:
    """
    Path A: load from h-e1 cached lm-eval --log_samples JSONL outputs.
    Uses h-e1's load_lmeval_samples() directly.
    Returns: (logprob_matrices: {model_key: (N,4)}, execution_path)
    Raises: RuntimeError if any model has 0 samples loaded
    """
    ...

def run_lmeval_for_model(
    model_id: str,
    output_dir: str,
    device: str = "cuda",
    num_fewshot: int = 4,
) -> str:
    """
    Path B: subprocess lm_eval CLI call with --log_samples.
    Returns: output directory path for this model
    Raises: RuntimeError after 2 failed attempts
    """
    ...

def load_logprob_matrices_path_b(
    output_dir: str,
    sizes: list[str],
    alignments: list[str],
    device: str = "cuda",
) -> tuple[dict[str, np.ndarray], str]:
    """
    Path B: re-run lm-eval for all 12 models sequentially, then load.
    Returns: (logprob_matrices: {model_key: (N,4)}, "Path B")
    """
    ...

def load_logprob_matrices(
    h_e1_results_dir: str,
    h_m2_results_dir: str,
    sizes: list[str],
    alignments: list[str],
    device: str = "cuda",
) -> tuple[dict[str, np.ndarray], str]:
    """
    Dispatcher: try Path A, fallback to Path B.
    Returns: (logprob_matrices, execution_path)
    """
    ...
```

---

### gate_and_report (`h-m2/code/gate_and_report.py`)

**Dependencies**: config, margin_analysis, json, yaml, pathlib, datetime

```python
def evaluate_should_work_gate(
    delta_results: dict[str, tuple[float, float, float]],
) -> tuple[str, list[str], dict]:
    """
    Returns: (gate_result: "PASS"|"FAIL", failed_checks, exploration_notes)
    PASS condition: >= 2/3 PPO sizes have delta_mean > 0 AND ci_lower > 0
    """
    ...

def generate_validation_report(
    delta_results: dict[str, tuple[float, float, float]],
    ordering_stats: dict[str, float],
    gate_result: str,
    failed_checks: list[str],
    exploration_notes: dict,
    execution_path: str,
    figure_paths: list[str],
    mechanism_indicators: dict,
) -> str:
    """
    Writes h-m2/04_validation.md.
    Returns: report file path
    """
    ...

def write_gate_to_verification_state(
    gate_result: str,
    delta_results: dict[str, tuple[float, float, float]],
    gate_report_path: str,
    verification_state_path: str,
) -> None:
    """
    Update h-m2 gate and validation fields in verification_state.yaml.
    Preserves all other hypothesis entries.
    """
    ...
```

---

### visualization (`h-m2/code/visualization.py`)

**Dependencies**: matplotlib, seaborn, numpy, config

```python
def plot_delta_margin_bar(
    delta_results: dict[str, tuple[float, float, float]],
    figures_dir: str,
) -> str:
    """Figure 1: grouped bar chart PPO/DPO/SFT x size with 95% CI error bars."""
    ...

def plot_margin_violin(
    logprob_matrices: dict[str, np.ndarray],
    figures_dir: str,
    size: str = "1.4b",
) -> str:
    """Figure 2: violin plot base vs PPO margin distributions."""
    ...

def plot_delta_margin_vs_delta_ece(
    delta_results: dict[str, tuple[float, float, float]],
    delta_ece: dict[str, float],
    figures_dir: str,
) -> str:
    """Figure 3: scatter Δmargin vs ΔECE across 9 model-size pairs."""
    ...

def plot_gradient_ordering_heatmap(
    delta_results: dict[str, tuple[float, float, float]],
    figures_dir: str,
) -> str:
    """Figure 4: 3x3 heatmap alignment x model size of Δmargin."""
    ...

def plot_margin_cdf(
    logprob_matrices: dict[str, np.ndarray],
    figures_dir: str,
    size: str = "1.4b",
) -> str:
    """Figure 5: CDF of margins base vs PPO 1.4b."""
    ...

def generate_all_figures(
    delta_results: dict[str, tuple[float, float, float]],
    logprob_matrices: dict[str, np.ndarray],
    delta_ece: dict[str, float],
    figures_dir: str,
) -> list[str]:
    """Generate all 5 figures. Returns list of saved file paths."""
    ...
```

---

### run_margin_analysis (`h-m2/code/run_margin_analysis.py`)

**Dependencies**: config, load_data, margin_analysis, gate_and_report, visualization

```python
def main() -> dict:
    """
    Full H-M2 pipeline (8 steps):
    1. Load logprob matrices (Path A -> Path B fallback)
    2. Validate shapes (N_items == 14042 per model)
    3. Compute all Δmargin + bootstrap CI (9 pairs)
    4. Test gradient ordering (Wilcoxon PPO >= DPO > SFT)
    5. Evaluate SHOULD_WORK gate
    6. Generate 5 figures
    7. Write 04_validation.md report
    8. Update verification_state.yaml + save experiment_results.json
    Returns: results dict with gate_result, delta_results, figure_paths
    """
    ...

if __name__ == "__main__":
    results = main()
    sys.exit(0 if results["gate_result"] == "PASS" else 1)
```

---

## Data Flow

```
h-e1/results/{model_key}/**/samples_mmlu*.jsonl   [Path A]
    |
    v
load_data.load_logprob_matrices()
    |  uses: calibration_analysis.load_lmeval_samples()
    v
logprob_matrices: {model_key: np.ndarray (14042, 4)}
    |
    +---> margin_analysis.compute_all_delta_margins()
    |         -> delta_results: {"ppo_1.4b": (mean, lo, hi), ...}
    |
    +---> margin_analysis.test_gradient_ordering()
    |         -> ordering_stats: {wilcoxon p-values}
    |
    +---> margin_analysis.verify_mechanism_activated()
    |         -> (bool, indicators)
    |
    +---> gate_and_report.evaluate_should_work_gate()
    |         -> gate_result: "PASS"|"FAIL"
    |
    +---> visualization.generate_all_figures()
    |         -> figure_paths[0..4]
    |
    +---> gate_and_report.generate_validation_report()
    |         -> h-m2/04_validation.md
    |
    +---> gate_and_report.write_gate_to_verification_state()
              -> verification_state.yaml updated
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create h-m2/code/ structure, config.py with all paths/constants, h-m2/figures/ and h-m2/results/ dirs | 6 | 2+1+1+2 |
| A-2 | Path A Data Loader | Implement load_data.py Path A: import h-e1 calibration_analysis.load_lmeval_samples(), dispatch across all 12 model keys, validate N==14042, shape (N,4) | 10 | 2+3+2+3 |
| A-3 | Path B Fallback | Implement Path B in load_data.py: subprocess lm_eval CLI for all 12 models with --log_samples --num_fewshot 4, retry logic, load results | 12 | 3+2+4+3 |
| A-4 | Core Margin Module | Implement margin_analysis.py: compute_logit_margins, compute_delta_margin (bootstrap CI n=1000), compute_all_delta_margins for 9 pairs, verify_mechanism_activated | 11 | 3+2+4+2 |
| A-5 | Gradient Ordering Test | Implement test_gradient_ordering (Wilcoxon signed-rank, one-sided, with ValueError fallback for ties) in margin_analysis.py | 7 | 1+2+3+1 |
| A-6 | Gate Evaluation | Implement gate_and_report.evaluate_should_work_gate: >=2/3 PPO sizes pass delta_mean>0 AND ci_lower>0; exploration_notes if FAIL | 7 | 2+2+2+1 |
| A-7 | Figure 1 (Gate Chart) | plot_delta_margin_bar: grouped bar chart PPO/DPO/SFT x 3 sizes with asymmetric 95% CI error bars, zero dashed line, color coding | 9 | 2+2+3+2 |
| A-8 | Figures 2-5 | plot_margin_violin, plot_delta_margin_vs_delta_ece (load ΔECE from h-e1/04_validation.md), plot_gradient_ordering_heatmap, plot_margin_cdf | 12 | 3+2+4+3 |
| A-9 | Validation Report | generate_validation_report writing 04_validation.md with all required sections: gate result, 9 Δmargin values, 3 CI lowers, Wilcoxon p-values, exploration notes, figure paths | 9 | 2+2+3+2 |
| A-10 | verification_state.yaml Update | write_gate_to_verification_state: parse yaml, update h-m2 gate/validation fields, write Δmargin key_metrics, preserve other entries | 8 | 2+2+2+2 |
| A-11 | Main Orchestrator | run_margin_analysis.py main(): 8-step pipeline with try/except path dispatch, smoke_test CLI flag, experiment_results.json output | 10 | 2+3+2+3 |
| A-12 | Integration Test | End-to-end smoke test (--smoke-test flag, 10 items), verify gate output, verify all 5 figures generated, verify 04_validation.md written | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4, A-7, A-8, A-9, A-11, A-12], Low(4-8): [A-1, A-5, A-6, A-10]

---

## Module Dependency Graph

```
run_margin_analysis.py
  ├── config.py
  ├── load_data.py
  │     ├── config.py
  │     └── [h-e1/code] calibration_analysis.py (load_lmeval_samples)
  ├── margin_analysis.py
  │     └── (numpy, scipy.stats)
  ├── gate_and_report.py
  │     ├── config.py
  │     └── (yaml, json, datetime)
  └── visualization.py
        ├── config.py
        └── (matplotlib, seaborn, numpy)
```
