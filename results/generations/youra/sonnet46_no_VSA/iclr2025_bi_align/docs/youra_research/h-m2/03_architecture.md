# Architecture: H-M2 — Partial Spearman + Fisher Z Difference Test

Applied: flat-script statistical pipeline (same pattern as H-M1)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: Patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**: H-M1 uses flat 4-file layout (`config.py`, `analyze.py`, `main.py`, `tests/test_analyze.py`). `load_data(cfg)` handles the H-E1 CSV reuse, BBQ column rename (`BBQ_accuracy` → `bbq_accuracy`), fraction normalization, and `n_min` guard. `run(cfg)` orchestrates load → compute → verify → plot → save. H-M2 reuses this exact pattern; `load_data` signature is compatible but column name casing must be preserved (`bbq_accuracy` internally, `BBQ_accuracy` in CSV).

---

## File Structure

```
docs/youra_research/h-m2/code/
├── config.py          # ExperimentConfig dataclass
├── analyze.py         # all computation + plotting functions + run()
├── main.py            # entry point
├── results/
│   ├── h_m2_results.json
│   └── h_m2_summary.txt
└── tests/
    └── test_analyze.py

docs/youra_research/h-m2/figures/
    fig1_rho_comparison.png
    fig2_scatter_mmlu_gradient.png
    fig3_bootstrap_distributions.png
    fig4_family_rho_bar.png
    fig5_fisher_z_numberline.png
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_data | `from h_m1.analyze import load_data` | NOT reused — reimplemented (column name differences; H-M2 keeps `family` column) |
| AnalysisConfig pattern | reference only | `docs/youra_research/h-m1/code/config.py` |

**Note**: H-M1 `load_data` uses `bbq_accuracy` (lowercase) internally but H-M2 PRD references `BBQ_accuracy`. H-M2 reimplements `load_data` with identical logic plus `family` label extraction. No direct import from H-M1 to avoid cross-hypothesis coupling.

---

## Module Definitions

### ExperimentConfig (`config.py`)

**Dependencies**: none

```python
@dataclass
class ExperimentConfig:
    # Data
    data_path: str = "../../h-e1/code/data/llm_leaderboard_v1/llm.csv"
    required_cols: tuple = ("model_name", "TruthfulQA_MC2", "BBQ_accuracy", "MMLU")
    n_min: int = 30

    # Bootstrap
    n_boot: int = 5000
    seed: int = 42
    min_family_size: int = 3

    # Output
    figures_dir: str = "../../figures"
    results_dir: str = "./results"

    # Visualization
    fig_size: tuple = (8.0, 5.0)
    fig_dpi: int = 150
    color_significant: str = "#2ca02c"
    color_null: str = "#ff7f0e"

def load_config() -> ExperimentConfig: ...
```

---

### analyze (`analyze.py`)

**Dependencies**: ExperimentConfig, pandas, numpy, scipy.stats, pingouin, matplotlib, seaborn

```python
logger: logging.Logger

def load_data(cfg: ExperimentConfig) -> pd.DataFrame:
    """Load H-E1 CSV, dropna on required cols, normalize BBQ_accuracy, add family col.
    Raises RuntimeError if N < cfg.n_min."""
    ...

def compute_raw_spearman(df: pd.DataFrame) -> dict:
    """Returns {raw_rho, raw_p}. Asserts abs(raw_rho) < 1.0."""
    ...

def compute_partial_spearman(df: pd.DataFrame) -> dict:
    """pingouin.partial_corr(covar=['MMLU'], method='spearman').
    Returns {partial_rho, partial_p}. Asserts abs(partial_rho) < 1.0
    and abs(partial_rho - raw_rho) > 1e-6."""
    ...

def fisher_z_difference_test(raw_rho: float, partial_rho: float, N: int) -> dict:
    """Same-sample formula: SE=sqrt(2/(N-3)).
    Returns {z_raw, z_partial, z_diff, p_value, outcome}."""
    ...

def compute_bca_cis(df: pd.DataFrame, cfg: ExperimentConfig) -> dict:
    """BCa CI for raw_rho via pingouin.compute_bootci (n_boot=5000, seed=42).
    BCa CI for partial_rho via custom bootstrap loop with pg.partial_corr.
    Returns {ci_raw, ci_partial, ci_overlap_status}."""
    ...

def compute_family_robustness(df: pd.DataFrame, cfg: ExperimentConfig) -> dict:
    """Per-family Spearman rho for families with >= cfg.min_family_size members.
    Returns {family_rhos: Series, weighted_rho: float}."""
    ...

def evaluate_gate(results: dict) -> dict:
    """Gate PASS if p_value is float in [0,1]. Assigns outcome SIGNIFICANT/NULL.
    Returns results dict with gate_pass, outcome added."""
    ...

# --- Figures (5 total) ---

def plot_rho_comparison(results: dict, cfg: ExperimentConfig) -> str:
    """Fig1: Grouped bar chart raw_rho vs partial_rho with BCa CI error bars.
    Annotated with Fisher z p-value. Color by outcome. Returns file path."""
    ...

def plot_scatter_mmlu_gradient(df: pd.DataFrame, cfg: ExperimentConfig) -> str:
    """Fig2: TruthfulQA_MC2 vs BBQ_accuracy scatter, MMLU as color gradient.
    Returns file path."""
    ...

def plot_bootstrap_distributions(results: dict, cfg: ExperimentConfig) -> str:
    """Fig3: Overlaid bootstrap distribution histograms for raw_rho and partial_rho.
    Returns file path."""
    ...

def plot_family_rho_bar(results: dict, cfg: ExperimentConfig) -> str:
    """Fig4: Per-family Spearman rho bar chart (families >= min_family_size).
    Returns file path."""
    ...

def plot_fisher_z_numberline(results: dict, cfg: ExperimentConfig) -> str:
    """Fig5: Number-line CI comparison: z_raw and z_partial with 95% CIs.
    Returns file path."""
    ...

def save_results(results: dict, cfg: ExperimentConfig) -> None:
    """Save results dict to h_m2_results.json and h_m2_summary.txt."""
    ...

def run(cfg: ExperimentConfig) -> dict:
    """Orchestrate: load → raw_spearman → partial_spearman → fisher_z
    → bca_cis → family_robustness → gate_eval → plot×5 → save → return results."""
    ...
```

---

### main (`main.py`)

**Dependencies**: ExperimentConfig, load_config, run

```python
def main() -> None:
    """Load config, call run(cfg), exit 0 on gate PASS, exit 1 on gate FAIL."""
    ...

if __name__ == "__main__":
    main()
```

---

### test_analyze (`tests/test_analyze.py`)

**Dependencies**: analyze, ExperimentConfig

```python
def test_fisher_z_known_values() -> None:
    """Verify fisher_z_difference_test against hand-computed values for known rho pair."""
    ...

def test_load_data_normalizes_bbq() -> None:
    """Synthetic df with BBQ in [0,1] → after load_data normalization max > 1."""
    ...

def test_gate_pass_both_outcomes() -> None:
    """Gate PASS for p=0.01 (SIGNIFICANT) and p=0.10 (NULL)."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create file structure, config.py, requirements, output dirs | 5 | 1+1+1+2 |
| A-2 | Data Loading | load_data() reusing H-E1 CSV: dropna, BBQ normalize, family label, N guard | 7 | 2+2+1+2 |
| A-3 | Raw Spearman | compute_raw_spearman(): scipy.stats.spearmanr + arctanh domain guard | 5 | 1+2+1+1 |
| A-4 | Partial Spearman | compute_partial_spearman(): pingouin.partial_corr(covar=['MMLU'], method='spearman') + mechanism activation assert | 9 | 2+3+2+2 |
| A-5 | Fisher Z Test | fisher_z_difference_test(): same-sample SE=sqrt(2/(N-3)), z_diff, two-tailed p, outcome | 8 | 2+2+2+2 |
| A-6 | BCa Bootstrap CIs | compute_bca_cis(): pingouin.compute_bootci for raw_rho; custom pg.partial_corr bootstrap loop for partial_rho; ci_overlap_status | 13 | 3+3+4+3 |
| A-7 | Family Robustness | compute_family_robustness(): per-family Spearman rho (min_family_size≥3), weighted mean | 8 | 2+2+2+2 |
| A-8 | Gate Evaluation | evaluate_gate(): validate p_value float, assign SIGNIFICANT/NULL, log all metrics | 5 | 1+2+1+1 |
| A-9 | Figures (Fig1+2) | plot_rho_comparison (grouped bar + CI error bars) + plot_scatter_mmlu_gradient | 10 | 3+2+3+2 |
| A-10 | Figures (Fig3-5) | plot_bootstrap_distributions + plot_family_rho_bar + plot_fisher_z_numberline | 10 | 3+2+3+2 |
| A-11 | Results Persistence | save_results(): JSON + TXT; run() orchestration wiring all steps | 7 | 2+2+1+2 |
| A-12 | Tests | test_analyze.py: Fisher z known values, BBQ normalization, gate pass/fail | 6 | 1+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-6, A-9, A-10], Low(4-8): [A-1, A-2, A-3, A-5, A-7, A-8, A-11, A-12]

---

## Implementation Notes

- H-M1 `load_data` uses `bbq_accuracy` (lowercase). H-M2 CSV has `BBQ_accuracy` (mixed case). The H-M1 rename logic (`BBQ_accuracy` → `bbq_accuracy`) is reused verbatim in H-M2's `load_data`; internally H-M2 uses `BBQ_accuracy` per PRD column names to avoid confusion.
- `pingouin.compute_bootci` does not support clustered resampling. `ci_partial` uses a manual bootstrap loop (5000 iterations, seed=42) calling `pg.partial_corr` on bootstrap samples. This is the slowest step — expected ~30-50s for N_boot=5000.
- `# ponytail: non-clustered BCa via pg.compute_bootci for raw_rho; clustered family bootstrap in manual loop for partial_rho — upgrade to full scipy clustered bootstrap if CI width comparison vs non-clustered matters`
- Fixed seed via `np.random.seed(cfg.seed)` at top of `run()`, matching H-M1 pattern.
