# Architecture: H-M2
# Post-Breakpoint Residual CoV Variance Compression Validation

**Applied**: segment-split reuse pattern (H-M1 data_loader + analyzer)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-M1)
**Status**: Patterns found from base code (Serena project listing used; files read directly)
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**: H-M1 has `data_loader.py` (load_residual_cov, load_paper_count_star_idx), `analyzer.py` (split_segments, run_brown_forsythe), `verifier.py`, `visualizer.py`, `main.py`. H-M2 reuses data_loader verbatim and extends analyzer for post/pre BF comparison instead of pre/global.

---

## File Structure

- `docs/youra_research/h-m2/code/`
  - `data_loader.py` — reused from H-M1 verbatim (symlink or copy)
  - `analyzer.py` — H-M2-specific: BF pre-vs-post + variance ratio + piecewise F-test
  - `verifier.py` — verify_mechanism_activated
  - `visualizer.py` — 5 figures
  - `main.py` — pipeline orchestrator
  - `tests/test_h_m2.py` — minimal self-check

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_residual_cov | `from data_loader import load_residual_cov` | `h-m1/code/data_loader.py` (copy to h-m2/code/) |
| load_paper_count_star_idx | `from data_loader import load_paper_count_star_idx` | `h-m1/code/data_loader.py` (copy to h-m2/code/) |

**Note**: data_loader.py is copied (not imported cross-hypothesis) to keep h-m2 self-contained. No changes needed — the loader already handles both H-E1 JSON key `breakpoint_idx` and PELT fallback.

**H-E1 JSON key**: `breakpoint_idx` (integer index into sorted array, not paper_count value)

---

## Module Definitions

### DataLoader (`data_loader.py`)

**Dependencies**: numpy, pandas, ruptures (fallback only)

```python
# Copied verbatim from h-m1/code/data_loader.py — no changes required

def load_residual_cov(csv_path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Return (paper_counts, residual_cov) sorted ascending. Raises on N!=111±.""" ...

def load_paper_count_star_idx(
    results_json_path: Path,
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
) -> int:
    """Load breakpoint_idx from H-E1 JSON or recompute via PELT. Validates (0, N).""" ...
```

---

### Analyzer (`analyzer.py`)

**Dependencies**: numpy, scipy.stats, statsmodels

```python
class VarianceCompressionResults(TypedDict):
    n_pre: int
    n_post: int
    var_pre: float
    var_post: float
    mean_pre: float
    mean_post: float
    variance_ratio: float        # var_post / var_pre; H1: < 1.0
    bf_stat: float
    bf_p_two_tailed: float
    bf_p_one_tailed: float       # bf_p_two / 2 if direction_confirmed else 1.0
    direction_confirmed: bool    # variance_ratio < 1.0
    piecewise_f_stat: float
    piecewise_f_p: float
    gate_passed: bool            # bf_p_two_tailed < 0.05 AND variance_ratio < 1.0


def split_segments(
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Return (pre, post); raises if len(pre) < 3 or len(post) < 3.""" ...


def run_brown_forsythe_pre_post(
    pre: np.ndarray,
    post: np.ndarray,
) -> Tuple[float, float, float, float]:
    """BF test (center='median') pre vs post.

    Returns: (bf_stat, bf_p_two_tailed, bf_p_one_tailed, variance_ratio)
    NOTE: center='median' mandatory — center='mean' is Levene's test, not BF.
    """
    # bf_p_one_tailed = bf_p_two / 2 if var_post < var_pre else 1.0
    ...


def run_piecewise_f_test(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
) -> Tuple[float, float]:
    """OLS baseline vs piecewise OLS with regime indicator; F-test via statsmodels.

    Returns: (f_stat, f_p)
    """
    # regime = (paper_counts >= paper_counts[paper_count_star_idx]).astype(int)
    # X_piece = [const, paper_count, regime, paper_count * regime]
    # compare nested models via anova_lm or manual F
    ...


def analyze(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
) -> VarianceCompressionResults:
    """Full analysis: split → BF → variance ratio → piecewise F → gate.""" ...
```

---

### Verifier (`verifier.py`)

**Dependencies**: analyzer.VarianceCompressionResults

```python
def verify_mechanism_activated(
    results: VarianceCompressionResults,
) -> Tuple[bool, dict]:
    """Check indicators; print log line; return (all_pass, indicators_dict).

    indicators: direction_confirmed, statistically_significant, effect_measured,
                n_pre_nonzero, n_post_nonzero
    Gate: direction_confirmed AND statistically_significant
    """
    ...
```

---

### Visualizer (`visualizer.py`)

**Dependencies**: matplotlib, numpy, analyzer.VarianceCompressionResults

```python
def plot_gate_metrics(results: VarianceCompressionResults, out_dir: Path) -> Path:
    """Bar chart: bf_p_two_tailed vs 0.05 threshold, variance_ratio vs 1.0 threshold.""" ...

def plot_boxplots(pre: np.ndarray, post: np.ndarray, out_dir: Path) -> Path:
    """Side-by-side box plots pre vs post residual CoV.""" ...

def plot_variance_bars(results: VarianceCompressionResults, out_dir: Path) -> Path:
    """Bar chart var_pre vs var_post with ratio annotation.""" ...

def plot_scatter_regime(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
    results: VarianceCompressionResults,
    out_dir: Path,
) -> Path:
    """Scatter N=111 colored by regime (pre=orange, post=blue) with ±1 SD bounds.""" ...

def plot_f_distribution(results: VarianceCompressionResults, out_dir: Path) -> Path:
    """F-distribution with BF statistic position vs critical value annotated.""" ...

def save_all_figures(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
    results: VarianceCompressionResults,
    out_dir: Path,
) -> List[Path]:
    """Run all 5 figure functions; return list of saved paths.""" ...
```

---

### Main (`main.py`)

**Dependencies**: data_loader, analyzer, verifier, visualizer, json, pathlib

```python
CSV_PATH    = _CODE_DIR / "data" / "pwc_cov_computed.csv"
H_E1_JSON   = _H_E1_DIR / "experiment_results.json"
RESULTS_PATH = _H_M2_DIR / "experiment_results.json"
FIGURES_DIR  = _H_M2_DIR / "figures"

def main() -> int:
    """Load → split → analyze → verify → visualize → save JSON.

    Returns: 0=PASS, 1=FAIL gate, 2=early-fail.
    """
    ...

if __name__ == "__main__":
    sys.exit(main())
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Copy data_loader.py from H-M1; create directory structure; symlink data/ | 4 | 1+1+1+1 |
| A-2 | Implement split_segments | Extend H-M1 version to also guard len(post) >= 3 | 5 | 1+1+1+2 |
| A-3 | Implement BF pre-vs-post test | run_brown_forsythe_pre_post with center='median', one-tailed logic | 8 | 2+2+2+2 |
| A-4 | Implement variance ratio + gate | variance_ratio = var_post/var_pre; gate = bf_p < 0.05 AND ratio < 1.0 | 6 | 2+1+2+1 |
| A-5 | Implement piecewise regression F-test | Nested OLS comparison via statsmodels anova_lm (secondary metric) | 12 | 3+2+4+3 |
| A-6 | Implement analyze() orchestrator | Tie A-2..A-5 into VarianceCompressionResults TypedDict | 7 | 2+2+2+1 |
| A-7 | Implement verifier | verify_mechanism_activated; 5 indicators; gate logic | 5 | 1+1+2+1 |
| A-8 | Implement visualizer | 5 figures: gate metrics, boxplots, variance bars, scatter regime, F-dist | 10 | 2+1+4+3 |
| A-9 | Implement main.py | Orchestrator with early-fail guards, JSON output, exit codes | 7 | 2+2+1+2 |
| A-10 | Tests | Minimal test_h_m2.py: synthetic pre/post arrays, assert gate logic | 5 | 1+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5, A-8], Low(4-8): [A-1, A-2, A-3, A-4, A-6, A-7, A-9, A-10]

**Total complexity**: 69 — well within 30-task budget (10 epics).
