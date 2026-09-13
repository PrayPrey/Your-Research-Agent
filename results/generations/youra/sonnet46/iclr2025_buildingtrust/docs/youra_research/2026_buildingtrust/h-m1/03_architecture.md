# H-M1 Architecture: Base Calibration Verification

**Hypothesis:** H-M1 — Base Calibration Verification (ECE_base < 0.15 for Pythia 1.4B / 2.8B / 6.9B)
**Type:** MECHANISM
**Date:** 2026-03-15

Applied: custom pattern — Archon KB returned no relevant DL architecture patterns (diffusion-focused KB)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (Read directly — Serena required project selection)
**Analyzed Path**: `docs/youra_research/20260315_buildingtrust/h-e1/code/`
**Findings**: H-E1 has 3 core files — `calibration_analysis.py` (ECE + Brier decomp + data loading), `verify_gate.py` (gate eval + report gen), `plot_results.py` (5 figures). H-M1 reuses these directly via sys.path injection; only new file needed is `run_experiment.py`.

---

## File Structure

- `h-m1/code/run_experiment.py` — orchestrator (Path A + fallback Path B)
- `h-m1/code/extract_h_e1_data.py` — ECE_base extraction from h-e1/04_validation.md
- `h-m1/code/gate_and_report.py` — MUST_WORK gate + validation report writer
- `h-m1/code/plot_results.py` — 5 figures for H-M1
- `h-m1/code/config.py` — single fixed config (paths, thresholds, sizes)

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| compute_ece | `from calibration_analysis import compute_ece` | `h-e1/code/calibration_analysis.py` |
| compute_brier_decomposition | `from calibration_analysis import compute_brier_decomposition` | `h-e1/code/calibration_analysis.py` |
| load_lmeval_samples | `from calibration_analysis import load_lmeval_samples` | `h-e1/code/calibration_analysis.py` |
| BASE_MODEL_IDS | `from calibration_analysis import BASE_MODEL_IDS` | `h-e1/code/calibration_analysis.py` |
| CALIBRATION_CONFIG | `from calibration_analysis import CALIBRATION_CONFIG` | `h-e1/code/calibration_analysis.py` |

**Import pattern (verified from actual code):**
```python
import sys
sys.path.append("../../h-e1/code/")
from calibration_analysis import compute_ece, compute_brier_decomposition, load_lmeval_samples
```

**Verified from**: `docs/youra_research/20260315_buildingtrust/h-e1/code/` (actual implementation)

---

## Module Definitions

### Config (`h-m1/code/config.py`)

**Dependencies**: none

```python
H_E1_VALIDATION_PATH: str = "../../h-e1/04_validation.md"
H_E1_RESULTS_DIR: str = "../../h-e1/results"
H_M1_RESULTS_DIR: str = "./results"
H_M1_FIGURES_DIR: str = "./figures"
H_M1_REPORT_PATH: str = "../../04_validation.md"
GATE_THRESHOLD: float = 0.15
BASE_SIZES: list[str] = ["1.4b", "2.8b", "6.9b"]
N_BINS: int = 15
SEED: int = 42
BASE_MODEL_HF_IDS: dict[str, str] = {
    "1.4b": "EleutherAI/pythia-1.4b",
    "2.8b": "EleutherAI/pythia-2.8b",
    "6.9b": "EleutherAI/pythia-6.9b",
}
```

---

### DataExtractor (`h-m1/code/extract_h_e1_data.py`)

**Dependencies**: config, re, pathlib, calibration_analysis (h-e1)

```python
def load_h_e1_ece_base(validation_file: str) -> dict[str, float]: ...
    # Parse h-e1/04_validation.md for ece_base_{size} keys via regex
    # Returns: {"pythia-1.4b-base": float, "pythia-2.8b-base": float, "pythia-6.9b-base": float}
    # Raises: FileNotFoundError if validation_file missing

def load_h_e1_ece_aligned(validation_file: str) -> dict[str, float]: ...
    # Parse h-e1/04_validation.md for ECE values of sft/dpo/ppo conditions
    # Returns: {"pythia-{size}-{align}": float, ...}

def load_h_e1_logprobs(results_dir: str, size: str) -> tuple[np.ndarray, np.ndarray]: ...
    # Load lm-eval JSONL samples for pythia-{size}-base from h-e1/results/
    # Wraps load_lmeval_samples() from calibration_analysis
    # Returns: (logprobs: (N,4), y_true: (N,))

def extract_or_recompute_ece_base(
    validation_file: str,
    h_e1_results_dir: str,
    n_bins: int = 15,
) -> dict[str, float]: ...
    # Path A: try load_h_e1_ece_base() first
    # Path A-extended: if regex fails, load logprobs + compute_ece()
    # Returns: dict of 3 base model ECE values
```

---

### GateEvaluator (`h-m1/code/gate_and_report.py`)

**Dependencies**: config, calibration_analysis (h-e1)

```python
def evaluate_must_work_gate(
    ece_base: dict[str, float],
    threshold: float = 0.15,
) -> tuple[str, list[str]]: ...
    # Returns: ("PASS"|"FAIL", failed_model_ids)
    # PASS iff all 3 sizes have ECE_base < threshold

def check_ece_ordering(
    ece_base: dict[str, float],
    ece_aligned: dict[str, float],
) -> dict[str, bool]: ...
    # Returns per-size bool: ECE_base < ECE_SFT

def verify_mechanism_activation(ece_base: dict[str, float]) -> tuple[bool, dict]: ...
    # Validate: all values non-null float in [0,1], all 3 sizes present
    # Returns: (valid, indicators_dict)

def generate_validation_report(
    ece_base: dict[str, float],
    ece_aligned: dict[str, float],
    gate_result: str,
    failed_checks: list[str],
    ordering: dict[str, bool],
    execution_path: str,
    output_path: str,
) -> None: ...
    # Write h-m1/04_validation.md with all required sections
    # Sections: metadata, gate_result, ece_table, ordering, figures, key_findings
```

---

### FigurePlotter (`h-m1/code/plot_results.py`)

**Dependencies**: config, calibration_analysis (h-e1), matplotlib, numpy

```python
def plot_ece_gate_bar(
    ece_base: dict[str, float],
    threshold: float,
    out_dir: str,
) -> None: ...
    # Figure 1 (MANDATORY): bar chart ECE_base × 3 sizes, dashed line at 0.15
    # Color: green if < 0.15, red if >= 0.15
    # Saves: figures/figure_01_ece_gate.png

def plot_base_vs_aligned_ece(
    ece_base: dict[str, float],
    ece_aligned: dict[str, float],
    out_dir: str,
) -> None: ...
    # Figure 2: 3 sizes × 4 conditions grouped bar
    # Saves: figures/figure_02_base_vs_aligned_ece.png

def plot_calibration_reliability_diagrams(
    logprobs_dict: dict[str, np.ndarray],
    y_true_dict: dict[str, np.ndarray],
    out_dir: str,
) -> None: ...
    # Figure 3: 3-panel reliability diagrams (one per size)
    # Saves: figures/figure_03_calibration_curves.png

def plot_ece_by_subject(
    logprobs_dict: dict[str, np.ndarray],
    y_true_dict: dict[str, np.ndarray],
    subject_labels: list[str],
    out_dir: str,
) -> None: ...
    # Figure 4: box plot ECE per MMLU subject × 3 base models
    # Saves: figures/figure_04_ece_by_subject.png

def plot_brier_decomposition_base(
    logprobs_dict: dict[str, np.ndarray],
    y_true_dict: dict[str, np.ndarray],
    out_dir: str,
) -> None: ...
    # Figure 5: stacked bar reliability/resolution/uncertainty for 3 base models
    # Saves: figures/figure_05_brier_decomposition.png

def generate_all_figures(
    ece_base: dict[str, float],
    ece_aligned: dict[str, float],
    logprobs_dict: dict[str, np.ndarray],
    y_true_dict: dict[str, np.ndarray],
    subject_labels: list[str],
    figures_dir: str,
) -> None: ...
    # Orchestrate all 5 figure functions
```

---

### Orchestrator (`h-m1/code/run_experiment.py`)

**Dependencies**: config, extract_h_e1_data, gate_and_report, plot_results

```python
def run_path_a(cfg: dict) -> dict[str, float]: ...
    # Extract ECE_base from h-e1/04_validation.md or h-e1/results/ logprobs
    # Returns ece_base dict or raises FileNotFoundError

def run_path_b(cfg: dict) -> dict[str, float]: ...
    # Fallback: execute lm-eval v0.4.11 for 3 base models sequentially
    # Calls: subprocess lm_eval CLI per size, then compute_ece
    # Returns ece_base dict

def main() -> None: ...
    # 1. Try run_path_a(); on failure → run_path_b()
    # 2. verify_mechanism_activation()
    # 3. evaluate_must_work_gate()
    # 4. check_ece_ordering()
    # 5. generate_all_figures()
    # 6. generate_validation_report()
    # 7. Write gate result to verification_state.yaml

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1-1 | Setup & Config | Create h-m1/code/ structure, config.py with all paths/thresholds, verify h-e1/code/ import path | 5 | 1+1+1+2 |
| M1-2 | H-E1 Data Extraction (Path A) | Implement extract_h_e1_data.py: regex parse h-e1/04_validation.md for ECE_base values, fallback to logprob reload via load_lmeval_samples | 10 | 3+2+3+2 |
| M1-3 | Path B Fallback (lm-eval re-run) | Implement run_path_b(): subprocess lm_eval CLI for 3 base models, sequential GPU execution, output path management | 12 | 3+2+4+3 |
| M1-4 | Gate Evaluation | Implement evaluate_must_work_gate(), verify_mechanism_activation(), check_ece_ordering() in gate_and_report.py | 9 | 2+2+3+2 |
| M1-5 | Figure Generation | Implement all 5 figures in plot_results.py: gate bar (mandatory) + 4 recommended (reliability diagrams, subject ECE, Brier decomp, base vs aligned) | 13 | 3+2+4+4 |
| M1-6 | Validation Report | Implement generate_validation_report(): write h-m1/04_validation.md with gate result, ECE table, ordering, figure paths, key findings | 9 | 2+2+3+2 |
| M1-7 | Orchestrator | Implement run_experiment.py: Path A/B dispatch, full pipeline integration, verification_state.yaml gate write | 11 | 2+3+3+3 |
| M1-8 | Integration Test | End-to-end smoke test with mock h-e1/04_validation.md, validate all outputs (report, figures, gate JSON) | 8 | 2+1+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M1-2, M1-3, M1-4, M1-5, M1-6, M1-7], Low(4-8): [M1-1, M1-8]

---

## Module Dependencies

```
run_experiment.py
  ├── config.py
  ├── extract_h_e1_data.py
  │     └── h-e1/code/calibration_analysis.py (compute_ece, load_lmeval_samples)
  ├── gate_and_report.py
  │     └── h-e1/code/calibration_analysis.py (compute_brier_decomposition)
  └── plot_results.py
        └── h-e1/code/calibration_analysis.py (compute_brier_decomposition, compute_ece)
```

## Execution Paths

- **Path A (primary)**: `run_experiment.py` reads `h-e1/04_validation.md` via regex — 0 GPU-hours
- **Path A-extended**: reads `h-e1/results/pythia-{size}-base/` logprob JSONL + recomputes ECE
- **Path B (fallback)**: spawns `lm_eval` subprocess for 3 base models sequentially on single GPU
