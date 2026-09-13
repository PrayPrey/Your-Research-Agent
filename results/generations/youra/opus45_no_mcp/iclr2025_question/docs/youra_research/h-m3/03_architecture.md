# Architecture: H-M3 (MECHANISM)

**Applied**: Linear score-fusion pattern (grid-searched convex combination of two normalized uncertainty signals), reusing H-M2's `entropy`/`consistency`/`correct` fields directly — no regeneration needed.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: `h-m2/code/` exists and is fully implemented (PASS result on disk).
**Analyzed Path**: `h-m2/code/` (generate.py, entropy.py, correctness.py, consistency.py, stats.py, checkpoint.py, load_data.py, visualize.py, run_pipeline.py, config.py, results/h-m2_results.json)
**Findings**: `h-m2/code/results/h-m2_results.json` stores per-question `{qid, question, entropy, consistency, correct, majority_answer}` for all N=20 evaluated questions (PoC scale, `config.N_QUESTIONS=20`). Unlike h-m1 (which discarded raw data), **h-m2 already persists exactly the entropy and consistency scalars H-M3 needs — no regeneration, no model loading required.** H-M3 is pure post-hoc numerical analysis: load JSON -> normalize -> fuse -> grid search -> AUROC compare -> plot. `stats.py` pattern (`roc_auc_score`, t-test helpers) is directly reusable for the DeLong/bootstrap CI addition.

---

## System Components

- `h-m2/code/results/h-m2_results.json` -> `load_results.py` (NEW, tiny) -> arrays `(entropy, consistency, correct)`
- `fusion.py` (NEW) -> LinearFusionScorer (normalize + combine) + grid_search_weights
- `stats.py` (copied from h-m2, extended) -> AUROC per variant, DeLong test, bootstrap CI for improvement
- `visualize.py` (NEW, extends h-m2 pattern) -> gate bar (3 AUROCs), ROC overlay, weight heatmap, entropy-vs-consistency scatter
- `run_pipeline.py` (NEW) -> orchestrates load -> split -> grid search -> ablation eval -> stats -> figures -> results JSON

Data flow: h-m2_results.json -> load (20 rows) -> train/test split (10%/90%, seed=42) -> grid search (alpha,beta) on val split -> compute 4 ablation variants (entropy-only, consistency-only, equal, optimal) on test split -> AUROC + significance -> figures + results JSON.

**Note on sample size**: PRD requests N>=500 from full TriviaQA; actual available data is h-m2's N=20 PoC run. Architecture supports both: `load_results.py` accepts an optional `limit`/regenerate flag, but default path reuses existing h-m2 JSON (fastest, no GPU needed). If Phase 4 needs larger N, rerun h-m2's `run_pipeline.py` with higher `N_QUESTIONS` first — H-M3 code itself needs no changes for that.

---

## Modules

### ResultsLoader (`h-m3/code/load_results.py`)

**Dependencies**: none (stdlib json)

```python
def load_h_m2_results(path: str = "../../h-m2/code/results/h-m2_results.json") -> dict: ...
# returns {"entropy": np.ndarray, "consistency": np.ndarray, "correct": np.ndarray[bool], "qids": list[str]}
```

### LinearFusionScorer (`h-m3/code/fusion.py`)

**Dependencies**: numpy, sklearn.metrics

```python
class LinearFusionScorer:
    def __init__(self, alpha: float = 0.5, beta: float = 0.5): ...
    def normalize(self, values: np.ndarray) -> np.ndarray: ...
    # min-max to [0,1], zero-vector guard if max-min < 1e-8
    def compute_scores(self, entropy: np.ndarray, consistency: np.ndarray) -> np.ndarray: ...
    # alpha*(1-normalize(entropy)) + beta*normalize(consistency)

def grid_search_weights(entropy: np.ndarray, consistency: np.ndarray, labels: np.ndarray,
                         alpha_range: list[float] = None, beta_range: list[float] = None
                         ) -> tuple[float, float, float]: ...
# returns (best_alpha, best_beta, best_val_auroc); default ranges = 0.0..1.0 step 0.1 (121 combos)

def train_test_split_idx(n: int, val_frac: float = 0.1, seed: int = 42) -> tuple[np.ndarray, np.ndarray]: ...
# returns (val_idx, test_idx)
```

### StatsAnalyzer (`h-m3/code/stats.py`)

**Copied from h-m2/code/stats.py**, extended with fusion comparison

```python
def compute_correlation(consistencies: list[float], correctness: list[bool]) -> dict: ...  # unchanged, kept for scatter/legacy use
def pearson_entropy_consistency(entropies: list[float], consistencies: list[float]) -> float: ...  # unchanged

def evaluate_variants(entropy, consistency, labels, alpha_beta_pairs: dict[str, tuple[float,float]]
                       ) -> dict: ...
# alpha_beta_pairs e.g. {"entropy_only": (1.0,0.0), "consistency_only": (0.0,1.0),
#                        "equal": (0.5,0.5), "optimal": (best_alpha,best_beta)}
# returns {variant_name: {"auroc": float, "scores": np.ndarray}}

def bootstrap_ci_improvement(labels, scores_a: np.ndarray, scores_b: np.ndarray,
                              n_boot: int = 1000, seed: int = 42) -> dict: ...
# returns {"improvement": float, "ci_low": float, "ci_high": float}
# scores_a = combined (optimal), scores_b = best single-metric scores
```

### Visualizer (`h-m3/code/visualize.py`)

**Dependencies**: matplotlib, sklearn (roc_curve, auc)

```python
def plot_gate_metrics(auroc_entropy: float, auroc_consistency: float, auroc_combined: float, out_path: str): ...
def plot_roc_overlay(labels, entropy_scores, consistency_scores, combined_scores, out_path: str): ...
def plot_weight_heatmap(alpha_range: list[float], beta_range: list[float], auroc_grid: np.ndarray, out_path: str): ...
def plot_entropy_vs_consistency(entropies, consistencies, correctness, out_path: str): ...
# copied logic from h-m2/code/visualize.py::plot_entropy_vs_consistency
```

### Pipeline (`h-m3/code/run_pipeline.py`)

**Dependencies**: all above

```python
def run(h_m2_results_path: str = None) -> dict: ...
# load -> split(val 10%/test 90%) -> grid_search on val
# -> evaluate_variants on test (entropy_only, consistency_only, equal, optimal)
# -> bootstrap_ci_improvement(optimal vs best single) -> visualize (4 figures)
# -> write results/h-m3_results.json
```

### Config (`h-m3/code/config.py`)

```python
H_M2_RESULTS_PATH = "../../h-m2/code/results/h-m2_results.json"
VAL_FRACTION = 0.1
ALPHA_RANGE = [round(i * 0.1, 1) for i in range(11)]
BETA_RANGE = [round(i * 0.1, 1) for i in range(11)]
SEED = 42
N_BOOTSTRAP = 1000
OUTPUT_PATH = "results/h-m3_results.json"
FIGURES_DIR = "figures/"
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual h-m2 Code)

| Module | Import Path / Copy Strategy | File Location |
|--------|------------------------------|----------------|
| h-m2_results.json | read directly via `load_results.py`, no import | `h-m2/code/results/h-m2_results.json` |
| stats.py (base functions) | copy `compute_correlation`, `pearson_entropy_consistency` into `h-m3/code/stats.py`, add new functions | `h-m2/code/stats.py` |
| visualize.py (scatter pattern) | copy `plot_entropy_vs_consistency` logic into `h-m3/code/visualize.py` | `h-m2/code/visualize.py` |

**Verified from**: `h-m2/code/` (actual implementation, cross-checked against `results/h-m2_results.json`, N=20 questions).
**Note**: Cross-hypothesis imports NOT used — h-m2 is a sibling folder, not an installed package. Phase 4 must copy needed functions, not import `from h_m2...`. No generation/model code needed — H-M3 is analysis-only on existing scalar outputs.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| D-1 | Config + results loader | config.py, load_results.py reading h-m2_results.json | 3 | 1+1+1+0 |
| D-2 | LinearFusionScorer | normalize + compute_scores, min-max guard | 4 | 1+1+2+0 |
| D-3 | Train/val split + grid search | train_test_split_idx, grid_search_weights (121 combos) | 6 | 1+2+2+1 |
| D-4 | StatsAnalyzer extension | evaluate_variants, bootstrap_ci_improvement (copy base fns + new) | 7 | 2+2+2+1 |
| D-5 | Visualizer | gate bar, ROC overlay, weight heatmap, scatter (copy+extend) | 7 | 2+1+2+2 |
| D-6 | Pipeline integration | wire load->split->search->evaluate->stats->figures->JSON | 8 | 2+3+1+2 |
| D-7 | Full-run validation | run on h-m2's 20 questions, verify AUROC_combined > max(single) | 5 | 1+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [D-2, D-3, D-4, D-5, D-6, D-7], VeryLow(1-3): [D-1]

---

## Notes

- No training, no generation, no GPU — pure numerical post-processing of existing h-m2 output.
- If Phase 4 wants the PRD's full N>=500 sample, rerun `h-m2/code/run_pipeline.py` with a larger `N_QUESTIONS` first (regenerates `h-m2_results.json`); H-M3 code is agnostic to N.
- Gate is SHOULD_WORK: if fails, document as limitation and continue to H-M4.
- Out of scope (per PRD): learned/non-linear fusion, cross-dataset generalization.
