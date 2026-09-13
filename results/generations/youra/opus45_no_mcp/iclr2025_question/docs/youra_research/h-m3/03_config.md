# Configuration: H-M3 (MECHANISM — linear fusion)

**Applied**: Hardcoded module-level config dict pattern (matches h-m2/code/config.py style)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code (`h-m2/code/config.py`, read directly)
**Config Files Found**: `h-m2/code/config.py`
**Pattern Used**: hardcoded module-level constants (no dataclass, no dict wrapper)

---

## D-1: Config + Results Loader [Complexity: 3, Budget: 3]

**Applied**: Module-level constants (KB pattern: flat config for PoC/analysis-only pipelines, no env vars needed since no external API calls)

### Configuration (Hardcoded constants — `h-m3/code/config.py`)
```python
"""H-M3 Configuration: Linear Fusion of Entropy + Consistency"""

H_M2_RESULTS_PATH = "../../h-m2/code/results/h-m2_results.json"

VAL_FRACTION = 0.1  # 10% val (weight tuning) / 90% test, per PRD FR4.2
ALPHA_RANGE = [round(i * 0.1, 1) for i in range(11)]  # 0.0..1.0 step 0.1
BETA_RANGE = [round(i * 0.1, 1) for i in range(11)]   # 0.0..1.0 step 0.1

N_BOOTSTRAP = 1000
CI_LEVEL = 0.95

SEED = 42

OUTPUT_PATH = "results/h-m3_results.json"
FIGURES_DIR = "figures/"
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | config.py + load_results.py | Constants above; loader reads `H_M2_RESULTS_PATH` -> dict of np arrays (entropy, consistency, correct, qids) |

---

## D-3: Train/Val Split + Grid Search [Complexity: 6, Budget: 1 relevant subtask]

**Applied**: Fixed-seed index split (KB pattern: reproducible small-N split via `np.random.RandomState(seed).permutation`)

Uses `VAL_FRACTION`, `SEED`, `ALPHA_RANGE`, `BETA_RANGE` from config above — no new fields.

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | grid_search_weights | 11x11=121 combos scored on val split; select argmax AUROC |

---

## D-4: Stats — Bootstrap CI [Complexity: 7, Budget: 1 relevant subtask]

Uses `N_BOOTSTRAP=1000`, `CI_LEVEL=0.95`, `SEED=42` from config above.

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-4-1 | bootstrap_ci_improvement | Resample test set `N_BOOTSTRAP` times, seed=`SEED`, report improvement + 95% CI |

---

## D-5: Visualization [Complexity: 7, Budget: 1 relevant subtask]

**Applied**: Fixed output-path constants (`FIGURES_DIR`), no per-plot config needed — sizes/styles hardcoded in visualize.py per h-m2 pattern.

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-5-1 | 4 plot functions | Write PNGs to `FIGURES_DIR`: gate bar, ROC overlay, weight heatmap, entropy-vs-consistency scatter |

---

## Inherited Configuration (Base Hypothesis)

### Config Fields (Verified from `h-m2/code/config.py`, actual code)

```python
# From: h-m2/code/config.py (ACTUAL CODE — read directly)
SEED = 42                              # reused as-is in H-M3
OUTPUT_PATH = "results/h-m2_results.json"  # referenced (not written) by H_M2_RESULTS_PATH
FIGURES_DIR = "figures/"               # same field name/pattern reused in H-M3
```

**No dataclass inheritance** — h-m2 uses flat module constants, not a class. H-M3 follows the same flat pattern; only `SEED` and the `FIGURES_DIR` naming convention are carried over. Generation-related fields (`MODEL_NAME`, `NUM_RESPONSES`, `EMBEDDING_MODEL`, etc.) are **not needed** — H-M3 is post-hoc analysis on existing `h-m2_results.json`, no model loading.

**Verified from**: `h-m2/code/config.py` (actual implementation, lines 1-30).

---

## Notes

- All 6 D-tasks (D-1 through D-6) share the single `h-m3/code/config.py` above — no per-task config duplication.
- No hyperparameter tuning/grid variation beyond `ALPHA_RANGE`/`BETA_RANGE` (already exhaustive per PRD FR2.1-FR2.2, not a "PoC omit" case — grid search IS the mechanism under test).
- N_QUESTIONS not redefined here: H-M3 consumes whatever N exists in `h-m2_results.json` (currently N=20; PRD wants >=500, deferred to rerunning h-m2 pipeline per architecture note).
