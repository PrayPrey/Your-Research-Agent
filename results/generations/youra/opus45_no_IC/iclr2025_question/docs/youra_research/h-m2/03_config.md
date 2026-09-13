# Configuration: H-M2 (MECHANISM)

**Applied**: Standard scipy.stats hardcoded-dict config pattern (KB search returned no directly relevant results — unrelated PyTorch/InvokeAI docs).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No `h-m2/code/` exists. H-E1 has no `code/` directory to inspect either (data artifact dependency only, not a code interface) — Serena skipped per architecture's own analysis.
**Config Files Found**: None — new config design
**Pattern Used**: Hardcoded dict (module-level constants in `config.py`)

---

## M2-1: Config + Data Loading [Complexity: 4, Budget: 4]

**Applied**: Hardcoded module-level constants (no tuning needed — fixed statistical analysis, matches architecture spec exactly)

### Configuration (`h-m2/code/config.py`)

```python
# Benchmark ordering — MUST match h-e1/code/config.py BENCHMARKS list exactly
# (matrix rows/cols are indexed by this order)
BENCHMARK_NAMES = [
    "trivia_qa", "natural_questions", "squad",   # Factual Recall family
    "pop_qa", "halueval_qa", "fever",            # Entity/Claim family
]

FACTUAL_FAMILY = {"trivia_qa", "natural_questions", "squad"}
ENTITY_FAMILY = {"pop_qa", "halueval_qa", "fever"}

# Paths
JS_MATRIX_PATH = "h-e1/results/js_divergence_matrix.npy"
ENTROPY_PATH_TEMPLATE = "h-e1/results/entropy_{name}.npy"  # fallback recompute only
FIGURES_DIR = "h-m2/figures"
VALIDATION_LOG_PATH = "h-m2/04_validation.md"

# Statistical thresholds (from PRD Success Criteria)
P_VALUE_THRESHOLD = 0.05          # PRIMARY: Mann-Whitney U one-sided
SAME_FAMILY_MEAN_THRESHOLD = 0.15  # SECONDARY: mean same-family JS-div
CLIFFS_DELTA_THRESHOLD = -0.5      # TERTIARY: large effect size

SEED = 42  # unused (no stochastic steps), kept for reproducibility record
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M2-1-1 | Benchmark ordering | Define `BENCHMARK_NAMES` matching H-E1 matrix index order |
| C-M2-1-2 | Family sets | Define `FACTUAL_FAMILY` / `ENTITY_FAMILY` per PRD FR-2 |
| C-M2-1-3 | Path constants | `JS_MATRIX_PATH`, `ENTROPY_PATH_TEMPLATE`, `FIGURES_DIR`, `VALIDATION_LOG_PATH` |
| C-M2-1-4 | Thresholds | `P_VALUE_THRESHOLD`, `SAME_FAMILY_MEAN_THRESHOLD`, `CLIFFS_DELTA_THRESHOLD` |

---

## Notes

- No dataclass used — pure hardcoded dict/constants per architecture spec's own `config.py` design; this is a fixed statistical analysis (no hyperparameter sweep, no ablations).
- `BENCHMARK_NAMES` order is load-bearing: matrix row/col `i` must correspond to `BENCHMARK_NAMES[i]`. Verify against `h-e1/code/config.py` `BENCHMARKS` list if/when it exists (currently reference-only per architecture, H-E1 `code/` not yet built).
- `SEED` included for consistency with other hypotheses' configs but has no effect (no randomness in Mann-Whitney U / Cliff's delta on a fixed matrix).
