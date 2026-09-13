# Architecture: H-M1
## RLHF Co-Optimization of Safety and Ethics — Within-Family Natural Experiment

**Date:** 2026-08-04
**Type:** MECHANISM (Incremental — extends H-E1)
**Gate:** MUST_WORK — ρ_partial(safety, ethics) > 0.5 AND ≥2/3 LLaMA-2 pairs Δ_safety > 0 AND Δ_ethics > 0

Applied: incremental-reuse pattern (statistical analysis on pre-computed h-e1 outputs)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1 extends to h-m1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 has 5 standalone modules (data_loader.py, analysis.py, clustering.py, visualization.py, main.py). Key discovery: `experiment_results_phase3.json` stores `rho_partial` (list-of-lists) and `dimensions` but does NOT store the raw 16x6 `scores_matrix` or `model_metadata`. H-M1 must load raw scores via h-e1's `load_trustllm_scores` + `add_annotations` functions (or re-read from TrustLLM/results/).

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_trustllm_scores | `sys.path.insert(0, he1_code); from data_loader import load_trustllm_scores` | `h-e1/code/data_loader.py:45` |
| add_annotations | `from data_loader import add_annotations` | `h-e1/code/data_loader.py` |
| DIMENSIONS | `from data_loader import DIMENSIONS, MODEL_ANNOTATIONS, MODEL_ORDER` | `h-e1/code/data_loader.py:14` |
| ols_residualize | `from analysis import ols_residualize` | `h-e1/code/analysis.py` |
| partial_spearman_matrix | `from analysis import partial_spearman_matrix` | `h-e1/code/analysis.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

**Critical note**: `experiment_results_phase3.json` key is `rho_partial` (not `rho_partial_matrix`). Raw scores are NOT in the JSON — must load via `load_trustllm_scores(results_dir)` pointing to `h-e1/code/TrustLLM/results/`.

---

## File Organization

- `h-m1/code/`
  - `main.py` — entrypoint, orchestrates all steps, writes outputs
  - `analysis.py` — LLaMA-2 pair extraction, delta computation, sign test
  - `visualization.py` — 4 required figures
  - `config.py` — paths and thresholds

---

## Modules

### Config (`h-m1/code/config.py`)

**Dependencies**: none

```python
HE1_CODE_DIR: str = "../../h-e1/code"          # for sys.path import
HE1_RESULTS_DIR: str = "../../h-e1/code/TrustLLM/results"
HE1_JSON: str = "../../h-e1/experiment_results_phase3.json"
OUTPUT_DIR: str = "../"                          # h-m1/
FIGURES_DIR: str = "../figures/"
RESULTS_JSON: str = "../experiment_results_phase3.json"
LOG_PATH: str = "../experiment.log"

DIMENSIONS: list = ["truthfulness","safety","fairness","robustness","privacy","machine_ethics"]
SAFETY_IDX: int = 1
ETHICS_IDX: int = 5
RHO_THRESHOLD: float = 0.5
SECONDARY_GATE_MIN: int = 2     # ≥2 of 3 pairs
N_PAIRS: int = 3

LLAMA2_SCALES: list = ["7b", "13b", "70b"]
LLAMA2_BASE_NAMES: list = ["LLaMA-2-7b-base", "LLaMA-2-13b-base", "LLaMA-2-70b-base"]
LLAMA2_CHAT_NAMES: list = ["LLaMA-2-7b-chat", "LLaMA-2-13b-chat", "LLaMA-2-70b-chat"]
```

---

### Analysis (`h-m1/code/analysis.py`)

**Dependencies**: Config, h-e1/data_loader (via sys.path), scipy, numpy, pandas

```python
def load_he1_data(he1_code_dir: str, he1_results_dir: str, he1_json: str
                  ) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    """
    Returns: (scores_df [16x6], annotated_df [16x8], rho_partial [6x6 ndarray])
    Loads scores via h-e1 data_loader; rho_partial from h-e1 JSON.
    """
    ...

def extract_llama2_pairs(scores_df: pd.DataFrame
                         ) -> list[dict]:
    """
    Returns list of 3 dicts:
    [{"scale": "7b", "base": scores_array, "chat": scores_array}, ...]
    """
    ...

def compute_deltas(pairs: list[dict]) -> list[dict]:
    """
    Returns list of 3 dicts:
    [{"scale": "7b", "delta_safety": float, "delta_ethics": float,
      "both_positive": bool, "all_deltas": np.ndarray[6]}, ...]
    """
    ...

def run_sign_test(deltas: list[dict]) -> dict:
    """
    Returns:
    {"n_both_positive": int, "secondary_gate_pass": bool, "binom_pvalue": float}
    Uses scipy.stats.binom_test(n, 3, p=0.5, alternative='greater').
    """
    ...

def verify_primary_gate(rho_partial: np.ndarray) -> dict:
    """
    Returns:
    {"rho_safety_ethics": float, "primary_gate_pass": bool}
    Reads rho_partial[SAFETY_IDX][ETHICS_IDX].
    """
    ...

def run_analysis(he1_code_dir: str, he1_results_dir: str, he1_json: str) -> dict:
    """Top-level: calls all above, returns full results dict."""
    ...
```

---

### Visualization (`h-m1/code/visualization.py`)

**Dependencies**: Config, analysis results dict, matplotlib, seaborn, numpy

```python
def plot_gate_metrics(rho_safety_ethics: float,
                      n_both_positive: int, n_pairs: int,
                      out_path: str) -> None:
    """Figure 1: Bar chart of ρ_partial vs threshold 0.5, and n_pairs vs gate 2/3."""
    ...

def plot_within_family_deltas(deltas: list[dict], out_path: str) -> None:
    """Figure 2: Grouped bar chart — Δ_safety and Δ_ethics per scale (7B/13B/70B),
    annotated with sign test result."""
    ...

def plot_safety_ethics_scatter(annotated_df: pd.DataFrame,
                               llama2_pairs: list[dict],
                               out_path: str) -> None:
    """Figure 3: All 16 models safety vs ethics, colored by is_RLHF,
    arrows connecting LLaMA-2 base→chat pairs."""
    ...

def plot_delta_2d(deltas: list[dict], out_path: str) -> None:
    """Figure 4: (Δ_safety, Δ_ethics) scatter for 3 LLaMA-2 pairs,
    quadrant lines at (0,0), positive quadrant shaded."""
    ...

def plot_rho_heatmap_highlighted(rho_partial: np.ndarray,
                                  dimensions: list[str],
                                  out_path: str) -> None:
    """Figure 5 (bonus): ρ_partial 6×6 heatmap with safety-ethics cell highlighted."""
    ...
```

---

### Main (`h-m1/code/main.py`)

**Dependencies**: analysis, visualization, Config, json, logging

```python
def run_experiment(he1_code_dir: str = HE1_CODE_DIR,
                   he1_results_dir: str = HE1_RESULTS_DIR,
                   he1_json: str = HE1_JSON,
                   output_dir: str = OUTPUT_DIR) -> dict:
    """Orchestrates: load → analyze → visualize → serialize → log."""
    ...

def serialize_results(results: dict, out_path: str) -> None:
    """Write results to JSON (mirrors h-e1 pattern)."""
    ...

def check_gate(results: dict) -> bool:
    """Returns primary_gate_pass AND secondary_gate_pass."""
    ...

if __name__ == "__main__":
    run_experiment()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & paths | Create config.py with all paths, indices, constants | 5 | 1+1+1+2 |
| A-2 | H-E1 data loading | load_he1_data(): sys.path import of h-e1 data_loader, load scores + rho_partial from JSON | 8 | 2+2+2+2 |
| A-3 | LLaMA-2 pair extraction | extract_llama2_pairs(): filter by name pattern, validate 6 models found, form 3 pairs | 7 | 2+1+2+2 |
| A-4 | Delta computation & sign test | compute_deltas() + run_sign_test(): Δ for all 6 dims, scipy binom_test | 9 | 2+2+3+2 |
| A-5 | Primary gate verification | verify_primary_gate(): read rho_partial[1][5], compare vs threshold | 5 | 1+2+1+1 |
| A-6 | Figure 1 — Gate metrics bar | plot_gate_metrics(): dual-panel bar comparing ρ vs 0.5 and n_pairs vs 2/3 | 8 | 2+1+3+2 |
| A-7 | Figure 2 — Within-family deltas | plot_within_family_deltas(): grouped bar Δ_safety/Δ_ethics per scale, annotated | 9 | 2+1+4+2 |
| A-8 | Figure 3 — Safety-ethics scatter | plot_safety_ethics_scatter(): 16 models colored by RLHF, arrows for LLaMA-2 pairs | 10 | 2+2+4+2 |
| A-9 | Figure 4 — 2D delta space | plot_delta_2d(): scatter (Δ_safety, Δ_ethics) with quadrant shading | 8 | 2+1+3+2 |
| A-10 | Figure 5 — Heatmap highlight | plot_rho_heatmap_highlighted(): 6×6 heatmap, safety-ethics cell boxed | 7 | 2+1+2+2 |
| A-11 | Main orchestration & serialization | run_experiment(): wire all steps, serialize JSON, write log, print gate result | 9 | 2+3+2+2 |
| A-12 | Integration test | Smoke test: run full pipeline, assert 3 pairs extracted, 5 figures exist, JSON valid | 7 | 1+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-7, A-8, A-11], Low(4-8): [A-1, A-2, A-3, A-5, A-6, A-9, A-10, A-12]

**Total complexity**: 92 points across 12 tasks

---

## Data Flow

- `config.py` → paths/constants
- `main.py` calls `run_analysis()` from `analysis.py`
  - `load_he1_data()`: sys.path + h-e1 data_loader → scores_df, annotated_df; JSON → rho_partial ndarray
  - `extract_llama2_pairs(scores_df)` → 3 pairs
  - `compute_deltas(pairs)` → 3 delta dicts
  - `run_sign_test(deltas)` → secondary gate result
  - `verify_primary_gate(rho_partial)` → primary gate result
- `main.py` calls visualization functions → 5 PNGs to `h-m1/figures/`
- `main.py` → `experiment_results_phase3.json` + `experiment.log`

---

## Key Implementation Notes

1. `experiment_results_phase3.json` from h-e1 uses key `rho_partial` (list-of-lists), NOT `rho_partial_matrix`. Convert with `np.array(data["rho_partial"])`.
2. Raw scores are NOT in h-e1 JSON. Must import h-e1's `load_trustllm_scores(results_dir)` pointing to `h-e1/code/TrustLLM/results/`.
3. `MODEL_ORDER` in h-e1 data_loader is the ground-truth model ordering — use it for indexing.
4. `scipy.stats.binom_test` is deprecated in scipy ≥1.12; use `scipy.stats.binomtest` instead.
