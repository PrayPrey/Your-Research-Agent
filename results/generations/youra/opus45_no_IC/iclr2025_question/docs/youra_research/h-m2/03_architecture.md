# Architecture: H-M2 (MECHANISM)

**Hypothesis**: Same-family benchmarks have lower JS-divergence than cross-family (Mann-Whitney U, p<0.05)
**Gate**: SHOULD_WORK, fail action: EXPLORE

Applied: none directly relevant (KB search returned unrelated diffusion/CUDA docs); using scipy.stats.mannwhitneyu standard nonparametric test pattern per experiment brief.

---

## Codebase Analysis (Serena)

**Project Type**: green-field (statistical analysis script; no code module in H-E1 to reuse — only a data artifact)
**Status**: No `h-m2/code/` exists yet. H-E1's `code/` contains ML pipeline modules (data/generate/entropy/cluster/visualize) not applicable here — H-M2 only consumes H-E1's `results/js_divergence_matrix.npy` output file, not its code.
**Analyzed Path**: N/A (no source modules to inspect; dependency is a data artifact, not a code interface)
**Findings**: New implementation from scratch. Only reused artifact: `h-e1/results/js_divergence_matrix.npy` (6x6 matrix) plus fixed benchmark name ordering from H-E1 `config.py` (`BENCHMARKS` list).

---

## File Structure (minimal - no training)

```
h-m2/code/
  config.py         # benchmark names, family definitions, paths, thresholds
  data.py            # load js_divergence_matrix.npy (with fallback recompute stub)
  analysis.py         # pair extraction, Mann-Whitney U, Cliff's delta
  visualize.py          # box plot, heatmap, violin, forest plot
  run.py                  # orchestrates load -> analyze -> visualize -> gate log
h-m2/figures/                # output figures
```

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
BENCHMARK_NAMES = ["trivia_qa", "natural_questions", "squad", "pop_qa", "halueval_qa", "fever"]
FACTUAL_FAMILY = {"trivia_qa", "natural_questions", "squad"}
ENTITY_FAMILY = {"pop_qa", "halueval_qa", "fever"}
JS_MATRIX_PATH = "h-e1/results/js_divergence_matrix.npy"
FIGURES_DIR = "h-m2/figures"
P_VALUE_THRESHOLD = 0.05
SAME_FAMILY_MEAN_THRESHOLD = 0.15
```

### DataLoader (`data.py`)

**Dependencies**: config

```python
def load_js_matrix(path: str = JS_MATRIX_PATH) -> np.ndarray:
    """Load 6x6 symmetric JS-divergence matrix. Raises FileNotFoundError if missing."""
def recompute_js_matrix_fallback() -> np.ndarray:
    """Fallback: recompute from H-E1 entropy distributions if artifact unavailable.
    Loads h-e1/results/entropy_*.npy per benchmark, fits KDE, builds matrix (mirrors H-E1 cluster.py logic)."""
```

### FamilyAnalyzer (`analysis.py`)

**Dependencies**: config

```python
def extract_pairs(js_matrix: np.ndarray, names: list[str]) -> tuple[list[float], list[float]]:
    """Returns (same_family_js, cross_family_js) — 6 same-family, 9 cross-family values."""
def cliffs_delta(x: list[float], y: list[float]) -> float: ...
def test_error_family_hypothesis(js_matrix: np.ndarray, names: list[str]) -> dict:
    """Mann-Whitney U (one-sided, less). Returns p_value, same_family_mean,
    cross_family_mean, same_family_values, cross_family_values, effect_size_cliffs_d,
    n_same, n_cross."""
```

### Visualizer (`visualize.py`)

**Dependencies**: config

```python
def plot_family_boxplot(same: list[float], cross: list[float], out_path: str) -> None: ...
def plot_js_heatmap_with_families(js_matrix: np.ndarray, names: list[str], out_path: str) -> None: ...
def plot_family_violin(same: list[float], cross: list[float], out_path: str) -> None: ...
def plot_effect_size_forest(effect_size: float, ci: tuple[float, float], out_path: str) -> None: ...
```

### Orchestrator (`run.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    """load js_matrix -> extract pairs -> Mann-Whitney U + Cliff's delta ->
    visualize -> log gate decision (p<0.05 and same_family_mean<0.15) to 04_validation.md"""
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Config + data loading | Family definitions, load js_divergence_matrix.npy | 4 | 1+1+1+1 |
| M2-2 | Fallback recompute path | KDE-based recompute from H-E1 entropy arrays if artifact missing | 8 | 2+2+2+2 |
| M2-3 | Pair extraction | Split 15 pairs into same-family (6) / cross-family (9) via matrix indices | 5 | 1+1+2+1 |
| M2-4 | Mann-Whitney U + Cliff's delta | One-sided test, effect size computation, result dict assembly | 6 | 1+1+2+2 |
| M2-5 | Box plot + violin visualization | Family comparison plots with individual points | 5 | 2+1+1+1 |
| M2-6 | Heatmap + forest plot visualization | JS heatmap with family boundary annotations, effect size CI forest plot | 6 | 2+1+2+1 |
| M2-7 | Pipeline orchestration + gate logging | run.py wiring, gate decision (p<0.05 & mean<0.15) logged to 04_validation.md | 5 | 1+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [M2-1, M2-2, M2-3, M2-4, M2-5, M2-6, M2-7]

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Artifact)

| Artifact | Access | File Location |
|----------|--------|----------------|
| JS-divergence matrix | `np.load("h-e1/results/js_divergence_matrix.npy")` | `h-e1/results/js_divergence_matrix.npy` |
| Benchmark ordering | `BENCHMARKS` list, hardcoded matching H-E1 `config.py` | `h-e1/code/config.py` (reference only, not imported — H-M2 has no runtime dependency on H-E1 code) |
| Entropy arrays (fallback only) | `np.load(f"h-e1/results/entropy_{name}.npy")` | `h-e1/results/` (used only if `js_divergence_matrix.npy` missing) |

**Verified from**: `h-e1/03_architecture.md` (Data Flow section) — no H-E1 `code/` directory exists to inspect directly (green-field at architecture time); path/format confirmed via H-E1 spec and H-M2 experiment brief FR-1.

---

## Data Flow

`js_divergence_matrix.npy` (6x6) -> DataLoader (load or fallback recompute) -> FamilyAnalyzer (extract 6 same / 9 cross pairs -> Mann-Whitney U + Cliff's delta) -> gate decision (p<0.05 and same_family_mean<0.15) -> Visualizer (figures/)
