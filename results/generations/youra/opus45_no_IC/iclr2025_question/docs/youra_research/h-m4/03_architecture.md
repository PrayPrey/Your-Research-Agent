# Architecture: H-M4 (MECHANISM)

**Hypothesis**: Cross-cluster benchmark pairs show failed threshold transfer (AUROC degradation > 0.15)
**Gate**: SHOULD_WORK, fail action: EXPLORE alternative distance metrics

Applied: no relevant KB pattern found (same irrelevant diffusion/LCM hits as H-M3 for "DL experiment architecture" query); reusing H-M3's validated sklearn roc_curve/roc_auc_score threshold-transfer pattern unchanged.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3 provides a fully validated within-cluster transfer pipeline; only pair selection changes)
**Status**: Patterns found from base code — `h-m3/code/` contains 8 modules (`config.py`, `data.py`, `entropy_pipeline.py`, `calibration.py`, `transfer.py`, `stats.py`, `visualize.py`, `run.py`) implementing the exact transfer protocol H-M4 needs. `calibration.py` confirmed via symbol overview: `calibrate_threshold`, `evaluate_transfer`, `compute_auroc_degradation` — signatures match spec in H-M3's `03_architecture.md`.
**Analyzed Path**: `docs/youra_research/h-m3/code/`
**Findings**:
- All data loading, entropy computation, calibration, and stats functions are benchmark-agnostic — zero changes needed.
- Only `config.py::WITHIN_CLUSTER_PAIRS` (renamed `CROSS_CLUSTER_PAIRS`) and `DEGRADATION_THRESHOLD`/`CI` gate values differ per H-M4 PRD (>0.15 vs ≤0.08).
- H-M4 adds one new capability H-M3 lacks: Mann-Whitney U comparison against H-M3's stored degradations (FR-5) — new function, not in H-M3 code.
- PopQA/HaluEval loaders not present in H-M3's `data.py` overview (H-M3 only exercised within-cluster benchmarks in its pairs) — verify these two loader branches exist before reuse; if absent, add loader stubs (H-E1's `data.py` already handles all 6 benchmarks per H-M3 findings, so branches should exist).

---

## File Structure

```
h-m4/code/
  config.py            # imports h-m3 config where unchanged; overrides CROSS_CLUSTER_PAIRS, thresholds
  transfer_runner.py    # thin wrapper: run_all_transfers over CROSS_CLUSTER_PAIRS (reuses h-m3 transfer.run_pair_transfer)
  stats.py              # aggregate_results + gate check (>0.15) + compare_to_h_m3 (Mann-Whitney U)
  visualize.py           # gate bar chart, H-M3 vs H-M4 box plot, per-pair bar, JS-divergence scatter
  run.py                 # orchestrates: reuse h-m3 data/entropy_pipeline/calibration -> transfer_runner -> stats -> visualize -> gate log
h-m4/figures/
h-m4/outputs/            # transfer_results.json, entropy caches (reuse h-m3/outputs/ for trivia_qa if present)
```

No new `data.py`, `entropy_pipeline.py`, or `calibration.py` — imported directly from H-M3.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_benchmark, split_calib_eval | `from h_m3.code.data import load_benchmark, split_calib_eval` | `h-m3/code/data.py` |
| get_or_compute_benchmark_entropy | `from h_m3.code.entropy_pipeline import get_or_compute_benchmark_entropy` | `h-m3/code/entropy_pipeline.py` |
| calibrate_threshold, evaluate_transfer, compute_auroc_degradation | `from h_m3.code.calibration import calibrate_threshold, evaluate_transfer, compute_auroc_degradation` | `h-m3/code/calibration.py` |
| run_pair_transfer | `from h_m3.code.transfer import run_pair_transfer` | `h-m3/code/transfer.py` |
| bootstrap_ci | `from h_m3.code.stats import bootstrap_ci` | `h-m3/code/stats.py` |
| H-M3 within-cluster degradations (for Mann-Whitney comparison) | hardcoded/loaded from `h-m3/outputs/transfer_results.json` | `h-m3/outputs/transfer_results.json` |

**Verified from**: `h-m3/code/` (Serena symbol overview on `calibration.py` confirms exact function names/signatures matching `h-m3/03_architecture.md`).

**Note**: No package structure exists; Phase 4 Coder resolves via `sys.path.append` to `h-m3/code/` or direct file copy — same caveat as H-M3's own external deps section.

---

## Modules

### Config (`config.py`)

**Dependencies**: h-m3/config (for SEED, CALIB_SPLIT, TARGET_FPR, GEN_MODEL, NLI_MODEL, N_GENERATIONS, TEMPERATURE, N_BOOTSTRAP — unchanged)

```python
CROSS_CLUSTER_PAIRS = [("trivia_qa", "pop_qa"), ("trivia_qa", "halueval_qa")]
JS_DIVERGENCE = {("trivia_qa", "pop_qa"): 0.422, ("trivia_qa", "halueval_qa"): 0.526}
DEGRADATION_THRESHOLD = 0.15
H_M3_DEGRADATIONS_PATH = "h-m3/outputs/transfer_results.json"
OUTPUTS_DIR = "h-m4/outputs"
FIGURES_DIR = "h-m4/figures"
```

### TransferRunner (`transfer_runner.py`)

**Dependencies**: config, h-m3 (data, entropy_pipeline, calibration, transfer)

```python
def run_cross_cluster_transfers(pairs: list[tuple[str, str]] = CROSS_CLUSTER_PAIRS) -> list[dict]:
    """For each (source, target): get_or_compute_benchmark_entropy both,
    run_pair_transfer(source, target) via h-m3 code. Directional only (source->target)."""
```

### Stats (`stats.py`)

**Dependencies**: config, h-m3.stats (bootstrap_ci)

```python
def aggregate_results(transfer_results: list[dict]) -> dict:
    """Returns {"mean_degradation": float, "ci_lower": float, "ci_upper": float}."""
def check_gate(agg: dict) -> bool:
    """mean_degradation > 0.15."""
def compare_to_h_m3(cross_degradations: list[float], h_m3_path: str = H_M3_DEGRADATIONS_PATH) -> dict:
    """Load H-M3 within-cluster degradations from json, scipy.stats.mannwhitneyu
    (alternative='greater'). Returns {"statistic": float, "p_value": float}."""
```

### Visualizer (`visualize.py`)

**Dependencies**: config

```python
def plot_gate_bar(mean_degradation: float, threshold: float, out_path: str) -> None: ...
def plot_within_vs_cross_box(within: list[float], cross: list[float], out_path: str) -> None: ...
def plot_per_pair_degradation(transfer_results: list[dict], out_path: str) -> None: ...
def plot_js_divergence_scatter(transfer_results: list[dict], js_map: dict, out_path: str) -> None: ...
```

### Orchestrator (`run.py`)

**Dependencies**: all modules above + h-m3 imports

```python
def main() -> None:
    """load trivia_qa/pop_qa/halueval_qa (h-m3.data) -> split calib/eval ->
    compute entropy (h-m3.entropy_pipeline, cache to h-m4/outputs) ->
    run_cross_cluster_transfers -> aggregate_results -> check_gate ->
    compare_to_h_m3 -> visualize -> log gate decision to 04_validation.md"""
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M4-1 | Config override + PopQA/HaluEval loader verification | New config.py with CROSS_CLUSTER_PAIRS; verify h-m3 data.py loads pop_qa/halueval_qa correctly | 6 | 1+2+1+2 |
| M4-2 | Cross-cluster entropy computation | Run/cache entropy+labels for trivia_qa (reuse if cached), pop_qa, halueval_qa | 8 | 2+2+2+2 |
| M4-3 | Cross-cluster transfer wrapper | transfer_runner.py: directional source->target transfers via h-m3.transfer.run_pair_transfer | 6 | 1+3+1+1 |
| M4-4 | Statistical aggregation + gate check | mean degradation, bootstrap CI, gate (>0.15) via h-m3.stats.bootstrap_ci | 5 | 1+1+1+2 |
| M4-5 | Mann-Whitney comparison vs H-M3 | Load h-m3 transfer_results.json, mannwhitneyu cross vs within degradations | 6 | 1+2+2+1 |
| M4-6 | Visualization suite | Gate bar (required), within-vs-cross box plot, per-pair bar, JS-divergence scatter | 7 | 2+1+2+2 |
| M4-7 | Pipeline orchestration + gate logging | run.py wiring end-to-end across h-m3 imports + h-m4 modules, gate decision logged | 6 | 1+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [M4-1, M4-2, M4-3, M4-4, M4-5, M4-6, M4-7]

---

## Data Flow

trivia_qa (Cluster 1, source) + pop_qa, halueval_qa (Cluster 2, targets) -> h-m3.DataLoader (unified schema, 70/30 split) -> h-m3.EntropyPipeline (cached to h-m4/outputs/) -> h-m3.Calibration (threshold @ FPR=0.1 on source calib split) -> TransferRunner (2 directional cross-cluster transfers: trivia_qa->pop_qa, trivia_qa->halueval_qa) -> Stats (mean degradation, bootstrap CI, gate check vs 0.15, Mann-Whitney vs H-M3's 0.032 baseline) -> Visualizer (figures/) -> gate decision logged to 04_validation.md
