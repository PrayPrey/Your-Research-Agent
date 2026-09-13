---
title: "Logic: H-M2 — Pre-Softmax Logit Margin Inflation"
hypothesis_id: h-m2
hypothesis_type: MECHANISM
phase: Phase 3
date: 2026-03-15
tier: FULL
---

Applied: N/A — Archon KB contains only diffusion model content; no applicable patterns for logit margin analysis, bootstrap CI, or Wilcoxon signed-rank testing.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1 and h-m1)
**Status**: Serena project selection unavailable; code read directly via Read tool — all signatures verified from actual implementation files.
**Analyzed Path**: `h-e1/code/calibration_analysis.py`, `h-m1/code/config.py`, `h-m1/code/gate_and_report.py`, `h-m1/code/run_experiment.py`

**Relevant Symbols Found**:

| Symbol | File | Actual Signature |
|--------|------|-----------------|
| `load_lmeval_samples` | h-e1/code/calibration_analysis.py | `(model_id: str, results_dir: str = RESULTS_DIR) -> tuple[np.ndarray, np.ndarray]` |
| `compute_ece` | h-e1/code/calibration_analysis.py | `(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = N_BINS) -> float` |
| `compute_brier_decomposition` | h-e1/code/calibration_analysis.py | `(y_true, y_prob, n_bins=N_BINS) -> tuple[float, float, float]` |
| `compute_delta_reliability` | h-e1/code/calibration_analysis.py | `(base_logprobs, aligned_logprobs, y_true, n_bins, n_bootstrap, seed) -> tuple[float, float, float]` |
| `MODEL_REGISTRY` | h-e1/code/calibration_analysis.py | `dict` — keys like `"1.4b-base"`, values are HuggingFace IDs |
| `MODELS` | h-e1/code/calibration_analysis.py | `list[str]` — 12 entries: `"pythia-{size}-{base|sft|dpo|ppo}"` |
| `ALIGNED_MODEL_IDS` | h-e1/code/calibration_analysis.py | `dict[str, dict[str, str]]` — `{size: {alignment: hf_id}}` |
| `run_analysis` | h-e1/code/calibration_analysis.py | `(results_dir: str, smoke_test: bool = False) -> dict` |
| config path pattern | h-m1/code/config.py | `Path(__file__).parent.resolve()` anchored; `H_E1_CODE_DIR = str(_H_E1_DIR / "code")` |
| `write_gate_to_verification_state` | h-m1/code/run_experiment.py | atomic `.tmp` rename pattern; updates `hypotheses.h-m1` dict in yaml |

**Critical Notes**:
- `load_lmeval_samples` returns raw **log-probs** (not softmax'd): `logprobs: (N, 4) float64` — these ARE the pre-softmax values H-M2 needs directly.
- H-E1 `results_dir` resolves to `h-e1/code/results/` per h-m1 config: `str(_H_E1_DIR / "code" / "results")`.
- Model keys use format `"pythia-{size}-{alignment}"` (with `pythia-` prefix).
- H-M1 uses `num_fewshot=0` for Path B; H-M2 PRD specifies `num_fewshot=4` — use 4 for H-M2 Path B.

---

## External Dependencies API (Base Hypothesis)

Signatures verified from `/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/h-e1/code/calibration_analysis.py` (actual code):

```python
# From: h-e1/code/calibration_analysis.py

def load_lmeval_samples(
    model_id: str,                    # e.g. "pythia-1.4b-base"
    results_dir: str = RESULTS_DIR,   # ← actual param name (NOT results_path)
) -> tuple[np.ndarray, np.ndarray]:
    """Glob results_dir/{model_id}/**/samples_mmlu*.jsonl.
    Returns: (logprobs: (N,4) float64, y_true: (N,) int64)
    Note: logprobs are RAW pre-softmax log-probs — use directly for margin computation.
    """

def compute_ece(
    y_true: np.ndarray,   # (N,) int64
    y_prob: np.ndarray,   # (N, 4) float64 softmax probabilities
    n_bins: int = 15,
) -> float: ...

def compute_brier_decomposition(
    y_true: np.ndarray,   # (N,) int64
    y_prob: np.ndarray,   # (N, 4) float64 softmax probabilities
    n_bins: int = 15,
) -> tuple[float, float, float]: ...  # (reliability, resolution, uncertainty)

# Importable constants (verified)
MODELS: list[str]           # 12 entries: "pythia-{size}-{base|sft|dpo|ppo}"
MODEL_REGISTRY: dict        # keys: "{size}-{alignment}", values: HuggingFace IDs
BASE_MODEL_IDS: dict        # {"1.4b": "EleutherAI/pythia-1.4b", ...}
ALIGNED_MODEL_IDS: dict     # {size: {alignment: hf_id}}
CALIBRATION_CONFIG: dict    # {"n_bins": 15, "n_bootstrap": 1000, "seed": 42, ...}
```

**Import pattern (verified from h-m1/code/run_experiment.py):**
```python
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-e1" / "code"))
from calibration_analysis import (
    load_lmeval_samples, compute_ece, MODELS, MODEL_REGISTRY,
    BASE_MODEL_IDS, ALIGNED_MODEL_IDS, CALIBRATION_CONFIG,
)
```

**Verified from**: actual `h-e1/code/calibration_analysis.py` (NOT spec)

---

## A-1: Project Setup [Complexity: 6]

### API Signatures

```python
# h-m2/code/config.py
from pathlib import Path

_CODE_DIR: Path = Path(__file__).parent.resolve()
_H_M2_DIR: Path = _CODE_DIR.parent
_H_E1_DIR: Path = _H_M2_DIR.parent / "h-e1"
_H_M1_DIR: Path = _H_M2_DIR.parent / "h-m1"

# External paths
H_E1_CODE_DIR: str = str(_H_E1_DIR / "code")
H_E1_RESULTS_DIR: str = str(_H_E1_DIR / "code" / "results")   # matches h-m1 pattern
H_E1_VALIDATION_PATH: str = str(_H_E1_DIR / "04_validation.md")

# H-M2 output paths
H_M2_RESULTS_DIR: str = str(_CODE_DIR / "results")
H_M2_FIGURES_DIR: str = str(_H_M2_DIR / "figures")
H_M2_REPORT_PATH: str = str(_H_M2_DIR / "04_validation.md")
H_M2_EXPERIMENT_RESULTS_JSON: str = str(_H_M2_DIR / "experiment_results.json")
VERIFICATION_STATE_PATH: str = str(_H_M2_DIR.parent / "verification_state.yaml")

# Gate constants
GATE_TYPE: str = "SHOULD_WORK"
MIN_PPO_SIZES_PASSING: int = 2
N_BOOTSTRAP: int = 1000
SEED: int = 42
SIZES: list[str] = ["1.4b", "2.8b", "6.9b"]
ALIGNMENTS: list[str] = ["sft", "dpo", "ppo"]
N_ITEMS_EXPECTED: int = 14042
LMEVAL_NUM_FEWSHOT: int = 4
LMEVAL_TIMEOUT_SECONDS: int = 7200
FIGURE_DPI: int = 150
```

---

## A-2: Path A Data Loader [Complexity: 10]

### API Signatures

```python
# h-m2/code/load_data.py

import sys
import numpy as np
from pathlib import Path

def load_logprob_matrices_path_a(
    results_dir: str,
    sizes: list[str],
    alignments: list[str],
) -> tuple[dict[str, np.ndarray], str]:
    """Load from h-e1 cached lm-eval JSONL via load_lmeval_samples().
    Returns: ({model_key: (N,4) float64}, "Path A")
    Raises: RuntimeError if any model returns 0 samples.
    """

def load_logprob_matrices(
    h_e1_results_dir: str,
    h_m2_results_dir: str,
    sizes: list[str],
    alignments: list[str],
    device: str = "cuda",
) -> tuple[dict[str, np.ndarray], str]:
    """Dispatcher: try Path A, fallback to Path B.
    Returns: (logprob_matrices, execution_path)  execution_path: "A" | "B"
    """
```

### Tensor Shapes

| Variable | Shape | Dtype | Note |
|----------|-------|-------|------|
| logprob_matrices[model_key] | (14042, 4) | float64 | raw pre-softmax log-probs |
| y_true (unused in h-m2 core) | (14042,) | int64 | from load_lmeval_samples, not needed for margins |

---

## A-3: Path B Fallback lm-eval [Complexity: 12, Budget: 2 subtasks]

### API Signatures

```python
# h-m2/code/load_data.py (continued)

import subprocess
import logging

logger = logging.getLogger(__name__)

# HuggingFace IDs per PRD §5 Model Registry (verified distinct from h-e1 IDs)
HF_MODEL_IDS: dict[str, dict[str, str]] = {
    "1.4b": {
        "base": "EleutherAI/pythia-1.4b",
        "sft":  "lomahony/pythia-1.4b-deduped-tldr",
        "dpo":  "Leogrin/pythia-1.4b-sft-tldr-dpo",
        "ppo":  "usvsnsp/pythia-1.4b-sft-tldr-ppo",
    },
    "2.8b": {
        "base": "EleutherAI/pythia-2.8b",
        "sft":  "lomahony/pythia-2.8b-deduped-tldr",
        "dpo":  "Leogrin/pythia-2.8b-sft-tldr-dpo",
        "ppo":  "usvsnsp/pythia-2.8b-sft-tldr-ppo",
    },
    "6.9b": {
        "base": "EleutherAI/pythia-6.9b",
        "sft":  "lomahony/pythia-6.9b-deduped-tldr",
        "dpo":  "Leogrin/pythia-6.9b-sft-tldr-dpo",
        "ppo":  "usvsnsp/pythia-6.9b-sft-tldr-ppo",
    },
}

def run_lmeval_for_model(
    model_key: str,      # e.g. "pythia-1.4b-base"
    hf_id: str,          # HuggingFace model ID
    output_dir: str,     # h-m2/results/
    device: str = "cuda",
    num_fewshot: int = 4,
    timeout: int = 7200,
) -> str:
    """Subprocess lm_eval CLI with --log_samples --num_fewshot 4.
    Retries once with batch_size=4 on CUDA OOM.
    Returns: model output directory path
    Raises: RuntimeError after 2 failed attempts.
    """

def load_logprob_matrices_path_b(
    output_dir: str,
    sizes: list[str],
    alignments: list[str],
    device: str = "cuda",
    num_fewshot: int = 4,
) -> tuple[dict[str, np.ndarray], str]:
    """Run lm-eval sequentially for all 12 models then load via load_lmeval_samples().
    Returns: ({model_key: (N,4)}, "Path B")
    """
```

### Pseudo-code (subprocess call)

```
for size in sizes:
    for alignment in ["base"] + alignments:
        model_key = f"pythia-{size}-{alignment}"
        hf_id = HF_MODEL_IDS[size][alignment]
        model_out = os.path.join(output_dir, model_key)
        cmd = ["lm_eval", "--model", "hf",
               "--model_args", f"pretrained={hf_id},dtype=float32",
               "--tasks", "mmlu",
               "--num_fewshot", str(num_fewshot),
               "--output_path", model_out + "/",
               "--log_samples",
               "--device", device]
        try:
            subprocess.run(cmd, check=True, timeout=timeout)
        except subprocess.CalledProcessError as e:
            if "CUDA out of memory" in str(e.stderr):
                # retry with batch_size=4
                cmd += ["--batch_size", "4"]
                subprocess.run(cmd, check=True, timeout=timeout)
            else:
                raise RuntimeError(f"lm_eval failed for {model_key}")
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-3-1 | run_lmeval_for_model | subprocess lm_eval CLI; OOM retry batch_size fallback; return output_dir |
| L-M2-3-2 | load_logprob_matrices_path_b | Sequential loop 12 models; call run_lmeval_for_model; load via load_lmeval_samples; validate N==14042 |

---

## A-4: Core Margin Module [Complexity: 11, Budget: 2 subtasks]

### API Signatures

```python
# h-m2/code/margin_analysis.py

import numpy as np
from scipy import stats

def compute_logit_margins(logprob_matrix: np.ndarray) -> np.ndarray:
    """Compute per-item top-1 minus top-2 log-prob margin.
    Args:  logprob_matrix: (N, 4) float64 raw pre-softmax log-probs
    Returns: margins: (N,) float64 — all values >= 0 by construction
    """

def compute_delta_margin(
    base_logprobs: np.ndarray,      # (N, 4) float64
    aligned_logprobs: np.ndarray,   # (N, 4) float64
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Bootstrap 95% CI for mean(aligned_margins) - mean(base_margins).
    Returns: (delta_mean, ci_lower_95, ci_upper_95) in nats
    Raises: ValueError if NaN present; AssertionError if margins negative.
    """

def compute_all_delta_margins(
    logprob_matrices: dict[str, np.ndarray],  # {model_key: (N,4)}
    sizes: list[str],
    alignments: list[str],
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> dict[str, tuple[float, float, float]]:
    """Compute delta margins for all 9 alignment-size pairs.
    Returns: {"{alignment}_{size}": (delta_mean, ci_lower, ci_upper)}
             e.g. "ppo_1.4b", "dpo_2.8b", "sft_6.9b"
    """

def verify_mechanism_activated(results_dict: dict) -> tuple[bool, dict]:
    """Verify shape, positive margins, delta computed for all 9 pairs.
    Returns: (mechanism_verified: bool, indicators: dict)
    indicators: {logprob_matrix_shape_ok, margins_positive, delta_computed,
                 delta_positive_ppo_count, ci_lower_positive_ppo_count}
    """
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logprob_matrix | (14042, 4) | input to compute_logit_margins |
| sorted_logprobs | (14042, 4) | np.sort descending axis=1 |
| margins | (14042,) | top1 - top2; all >= 0 |
| delta_per_item | (14042,) | aligned_margins - base_margins; may be negative |
| boot_means | (1000,) | bootstrap distribution of mean delta |

### Pseudo-code for compute_delta_margin

```
base_margins    = compute_logit_margins(base_logprobs)      # (N,)
aligned_margins = compute_logit_margins(aligned_logprobs)   # (N,)
assert np.all(base_margins >= 0) and np.all(aligned_margins >= 0)
delta_per_item  = aligned_margins - base_margins            # (N,)
delta_mean      = float(np.mean(delta_per_item))
np.random.seed(seed)
boot_means      = [np.mean(np.random.choice(delta_per_item, N, replace=True))
                   for _ in range(n_bootstrap)]
ci_lower = float(np.percentile(boot_means, 2.5))
ci_upper = float(np.percentile(boot_means, 97.5))
return delta_mean, ci_lower, ci_upper
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-4-1 | compute_logit_margins + compute_delta_margin | Sort logprobs descending; margin=col0-col1; bootstrap CI loop n=1000; assert positive margins; raise ValueError on NaN |
| L-M2-4-2 | compute_all_delta_margins + verify_mechanism_activated | Loop 9 pairs; aggregate results dict; verify shape==14042, margins positive, delta computed; return (bool, indicators) |

---

## A-5: Gradient Ordering Test [Complexity: 7]

### API Signatures

```python
# h-m2/code/margin_analysis.py (continued)

def test_gradient_ordering(
    delta_ppo: list[float],   # [Δmargin_ppo_1.4b, Δmargin_ppo_2.8b, Δmargin_ppo_6.9b]
    delta_dpo: list[float],   # same for DPO
    delta_sft: list[float],   # same for SFT
) -> dict[str, float]:
    """Wilcoxon signed-rank one-sided tests across 3 Pythia sizes.
    Falls back to sign test (NaN) if scipy raises ValueError (ties/zeros with n=3).
    Returns: {ppo_ge_dpo_stat, ppo_ge_dpo_p, dpo_gt_sft_stat, dpo_gt_sft_p}
    """
```

---

## A-6: Gate Evaluation [Complexity: 7]

### API Signatures

```python
# h-m2/code/gate_and_report.py

def evaluate_should_work_gate(
    delta_results: dict[str, tuple[float, float, float]],
) -> tuple[str, list[str], dict]:
    """SHOULD_WORK gate: >= 2/3 PPO sizes with delta_mean > 0 AND ci_lower > 0.
    Returns: (gate_result: "PASS"|"FAIL", failed_checks: list[str], exploration_notes: dict)
    exploration_notes is {} on PASS; contains {action, hypothesis, next_step} on FAIL.
    """
```

---

## A-7: Figure 1 (Gate Chart) [Complexity: 9]

### API Signatures

```python
# h-m2/code/visualization.py

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

def plot_delta_margin_bar(
    delta_results: dict[str, tuple[float, float, float]],
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """Grouped bar chart: PPO/DPO/SFT x 3 sizes with asymmetric 95% CI error bars.
    Colors: red=PPO, orange=DPO, blue=SFT. Dashed zero line.
    Returns: saved figure path (figure_01_delta_margin_gate.png)
    """
```

---

## A-8: Figures 2-5 [Complexity: 12, Budget: 2 subtasks]

### API Signatures

```python
# h-m2/code/visualization.py (continued)

import seaborn as sns

def plot_margin_violin(
    logprob_matrices: dict[str, np.ndarray],  # {model_key: (N,4)}
    figures_dir: str,
    size: str = "1.4b",
    dpi: int = 150,
) -> str:
    """Violin plot: margin distributions for base vs PPO for given size.
    Computes margins via compute_logit_margins() internally.
    Returns: figure_02_margin_violin.png path
    """

def plot_delta_margin_vs_delta_ece(
    delta_results: dict[str, tuple[float, float, float]],
    delta_ece: dict[str, float],   # {"ppo_1.4b": float, ...} — loaded from h-e1/04_validation.md
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """Scatter: Δmargin vs ΔECE across 9 model-size pairs.
    delta_ece loaded from h-e1/04_validation.md via regex (same pattern as parse_h_e1_validation_report).
    Returns: figure_03_delta_margin_vs_delta_ece.png path
    """

def plot_gradient_ordering_heatmap(
    delta_results: dict[str, tuple[float, float, float]],
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """Heatmap: 3x3 (alignment x model_size) of Δmargin values via seaborn.heatmap.
    Rows: sft/dpo/ppo. Cols: 1.4b/2.8b/6.9b.
    Returns: figure_04_gradient_ordering_heatmap.png path
    """

def plot_margin_cdf(
    logprob_matrices: dict[str, np.ndarray],  # {model_key: (N,4)}
    figures_dir: str,
    size: str = "1.4b",
    dpi: int = 150,
) -> str:
    """CDF of margins: base vs PPO for given size.
    np.sort + np.arange/N for empirical CDF.
    Returns: figure_05_margin_cdf.png path
    """

def load_delta_ece_from_validation(
    h_e1_validation_path: str,
) -> dict[str, float]:
    """Parse h-e1/04_validation.md for ΔECE values for 9 model-size pairs.
    Returns: {"ppo_1.4b": float, "dpo_1.4b": float, "sft_1.4b": float, ...}
    Returns {} on FileNotFoundError or parse failure (non-fatal for figure 3).
    """

def generate_all_figures(
    delta_results: dict[str, tuple[float, float, float]],
    logprob_matrices: dict[str, np.ndarray],
    h_e1_validation_path: str,
    figures_dir: str,
    dpi: int = 150,
) -> list[str]:
    """Generate all 5 figures. Returns list of saved paths (len 5)."""
```

### Pseudo-code for plot_delta_margin_vs_delta_ece

```
delta_ece = load_delta_ece_from_validation(h_e1_validation_path)
if not delta_ece: return early with warning

x_vals = [delta_ece.get(f"{a}_{s}", np.nan) for a in alignments for s in sizes]  # 9 values
y_vals = [delta_results.get(f"{a}_{s}", (np.nan, 0, 0))[0] for ...]              # 9 Δmargins
scatter with color by alignment (PPO=red, DPO=orange, SFT=blue)
add Pearson r annotation; save figure_03
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-8-1 | plot_margin_violin + plot_margin_cdf | Compute margins from logprob_matrices[f"pythia-{size}-base/ppo"]; violin via seaborn; CDF via np.sort empirical; save fig 2 and 5 |
| L-M2-8-2 | plot_delta_margin_vs_delta_ece + plot_gradient_ordering_heatmap + load_delta_ece_from_validation | Parse h-e1/04_validation.md ΔECE; scatter 9 points; seaborn heatmap 3x3; save fig 3 and 4 |

---

## A-9: Validation Report [Complexity: 9]

### API Signatures

```python
# h-m2/code/gate_and_report.py (continued)

def generate_validation_report(
    delta_results: dict[str, tuple[float, float, float]],
    ordering_stats: dict[str, float],
    gate_result: str,
    failed_checks: list[str],
    exploration_notes: dict,
    execution_path: str,
    figure_paths: list[str],
    mechanism_indicators: dict,
    output_path: str,
) -> str:
    """Write h-m2/04_validation.md with all required sections.
    Sections: metadata, gate_result, delta_margin_table (9 pairs),
              bootstrap_ci_table (3 PPO sizes), wilcoxon_results,
              mechanism_indicators, exploration_notes (if FAIL),
              figure_paths, key_findings (>=3).
    Returns: output_path
    """

def write_gate_to_verification_state(
    gate_result: str,
    delta_results: dict[str, tuple[float, float, float]],
    gate_report_path: str,
    verification_state_path: str,
) -> None:
    """Update h-m2 section in verification_state.yaml atomically (.tmp rename).
    Sets: hypotheses.h-m2.{gate_result, gate_type, key_metrics, updated_at}
    key_metrics: {delta_ppo_1.4b, delta_ppo_2.8b, delta_ppo_6.9b, execution_path}
    """
```

---

## A-11: Main Orchestrator [Complexity: 10]

### API Signatures

```python
# h-m2/code/run_margin_analysis.py

import sys
import argparse
import json
import logging
from pathlib import Path

# sys.path.insert(0, config.H_E1_CODE_DIR) before importing calibration_analysis
from config import *
from load_data import load_logprob_matrices
from margin_analysis import (
    compute_all_delta_margins, test_gradient_ordering, verify_mechanism_activated
)
from gate_and_report import (
    evaluate_should_work_gate, generate_validation_report,
    write_gate_to_verification_state
)
from visualization import generate_all_figures

def main(smoke_test: bool = False, device: str = "cuda") -> dict:
    """8-step H-M2 pipeline.
    1. Load logprob matrices (Path A -> Path B fallback)
    2. Validate all shapes == (14042, 4); raises ValueError on mismatch
    3. compute_all_delta_margins (9 pairs, bootstrap n=1000, seed=42)
    4. test_gradient_ordering (Wilcoxon PPO>=DPO, DPO>SFT)
    5. verify_mechanism_activated(results_dict)
    6. evaluate_should_work_gate(delta_results)
    7. generate_all_figures(...)
    8. generate_validation_report(...) + write_gate_to_verification_state(...)
       + save experiment_results.json
    Returns: {gate_result, delta_results, figure_paths, execution_path}
    """

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()
    results = main(smoke_test=args.smoke_test, device=args.device)
    sys.exit(0 if results["gate_result"] == "PASS" else 1)
```

---

## Subtask Budget Summary

| Epic | Module | Subtasks Used | Budget |
|------|--------|--------------|--------|
| A-3 | load_data.py Path B | 2 | 2 |
| A-4 | margin_analysis.py core | 2 | 2 |
| A-8 | visualization.py figures 2-5 | 2 | 2 |
| **Total** | | **6** | **6** |

---

*Generated: Phase 3 Logic Agent*
*Hypothesis: H-M2 (MECHANISM, FULL tier) | Base: H-E1, H-M1*
*Subtasks used: 6/6 (A-3: 2, A-4: 2, A-8: 2)*
