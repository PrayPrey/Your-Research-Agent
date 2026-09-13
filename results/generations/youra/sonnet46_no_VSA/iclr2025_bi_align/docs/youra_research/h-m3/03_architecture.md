# Architecture: H-M3 — Scenario Classification of Partial Spearman

**Applied: statistical-analysis-pipeline pattern**

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**: H-M2 has `analyze.py` (flat functions, no classes), `config.py` (ExperimentConfig dataclass), `main.py` (single `main()` calling `run()`). H-M3 mirrors this structure. Key H-M2 functions consumed: `load_data()` reads CSV from cfg paths; `run()` returns results dict with keys `partial_rho`, `ci_partial`, `raw_rho`, `ci_raw`, `N`.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ExperimentConfig | `from h_m2.config import ExperimentConfig` | `h-m2/code/config.py` |
| load_data | `from h_m2.analyze import load_data` | `h-m2/code/analyze.py` |

**Verified from**: `docs/youra_research/h-m2/code/` (actual implementation)

Note: H-M3 does NOT re-import H-M2 modules at runtime. It reads `h_m2_results.json` directly. `load_data` is reused only for Tier 2/3 DataFrame construction from the same CSVs.

---

## File Structure

- `docs/youra_research/h-m3/code/`
  - `config.py` — ExperimentConfig dataclass
  - `data_loader.py` — JSON + hardcoded + CSV loading
  - `analyze.py` — scenario classification + Tier 2/3 + ablations
  - `visualize.py` — Fig1–Fig4
  - `main.py` — orchestration + serialization
  - `results/` — h_m3_results.json output
- `docs/youra_research/h-m3/figures/` — PNG outputs

---

## Modules

### Config (`code/config.py`)

**Dependencies**: stdlib only

```python
@dataclass
class ExperimentConfig:
    # Paths
    h_m2_results_path: str = "../../h-m2/code/results/h_m2_results.json"
    h_m1_pairs_csv: str = "../../h-e1/code/data/llm_leaderboard_v1/llm.csv"
    results_dir: str = "./results"
    figures_dir: str = "../../figures/h-m3"

    # Scenario boundaries (pre-specified, immutable)
    scenario_a_bound: float = 0.20   # |partial_rho| < this → scenario a
    scenario_b_bound: float = 0.40   # partial_rho > this → scenario b
    scenario_c_bound: float = -0.20  # partial_rho < this → scenario c

    # Ablation boundary variants
    tight_a: float = 0.15; tight_b: float = 0.35; tight_c: float = -0.15
    wide_a: float = 0.25;  wide_b: float = 0.45;  wide_c: float = -0.25

    # Tier 2
    n_min_harmbench: int = 20

    # Bootstrap (for Tier 2 re-analysis only)
    n_boot: int = 5000
    seed: int = 42

    # Figures
    fig_dpi: int = 300
    fig_size: tuple = (9.0, 5.0)

def load_config() -> ExperimentConfig: ...
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: config.py, json, pandas, rapidfuzz

```python
def load_h_m2_results(cfg: ExperimentConfig) -> dict:
    """Load and validate h_m2_results.json. Raises RuntimeError on missing file/keys."""
    ...

def load_harmbench_data() -> dict:
    """Return hardcoded HarmBench Table 2 (arXiv:2402.04249). No file I/O."""
    ...

def load_tier3_delta_bbq(cfg: ExperimentConfig) -> np.ndarray:
    """Load H-M1 base/chat pairs CSV, compute ΔBBQ = BBQ(chat) - BBQ(base).
    Returns array of 321 delta values."""
    ...

def load_tier1_dataframe(cfg: ExperimentConfig) -> pd.DataFrame:
    """Re-load raw LLM CSV (same path as H-M2 load_data) for Tier 2 DataFrame join.
    Replicates H-M2 load_data logic: rename cols, dropna, normalize bbq_accuracy."""
    ...

def fuzzy_join(df: pd.DataFrame, harmbench_df: pd.DataFrame,
               threshold: int = 75) -> pd.DataFrame:
    """Inner join on model_name using rapidfuzz; returns merged DataFrame."""
    ...
```

---

### Analyze (`code/analyze.py`)

**Dependencies**: data_loader.py, config.py, pingouin, scipy, numpy, pandas

```python
def assign_scenario(partial_rho: float, ci_lo: float, ci_hi: float,
                    cfg: ExperimentConfig) -> dict:
    """Classify partial_rho into scenario a/b/c/ambiguous using cfg boundaries.
    Returns: {scenario, is_ambiguous, narrative}"""
    ...

def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """Check h_m2_loaded, scenario_assigned, ci_bounds_valid, narrative_generated.
    Returns: (all_ok: bool, indicators: dict)"""
    ...

def tier2_analysis(df_tier1: pd.DataFrame, harmbench_data: dict,
                   cfg: ExperimentConfig) -> dict:
    """Fuzzy-join Tier 1 with HarmBench; skip if N < cfg.n_min_harmbench.
    If N >= 20: partial Spearman for TruthfulQA×HarmBench and BBQ×HarmBench.
    Returns: {tier2_status, N_harmbench, scenario_tqa_harm, scenario_bbq_harm, ...}"""
    ...

def tier3_analysis(delta_bbq: np.ndarray) -> dict:
    """scipy.stats.binomtest on sign(ΔBBQ > 0) for 321 pairs.
    Returns: {k_positive, n, p_value, direction}"""
    ...

def ablation_ci_method(partial_rho: float, df: pd.DataFrame,
                       cfg: ExperimentConfig) -> dict:
    """Re-assign scenario using Fisher parametric CI from pingouin.partial_corr.
    Returns: {scenario, matches_primary: bool}"""
    ...

def ablation_boundary(partial_rho: float, ci_lo: float, ci_hi: float,
                      cfg: ExperimentConfig) -> dict:
    """Assign scenario under tight and wide boundary variants.
    Returns: {tight: {scenario}, wide: {scenario}}"""
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: analyze.py, config.py, matplotlib

```python
def plot_scenario_panel(results: dict, cfg: ExperimentConfig) -> str:
    """Fig1: Horizontal number line with partial_rho point + BCa CI band.
    Scenario boundary lines at ±0.20, +0.40. Returns saved PNG path."""
    ...

def plot_partial_corr_heatmap(results: dict, cfg: ExperimentConfig) -> str | None:
    """Fig2: Pairwise partial Spearman heatmap for Tier 1+2 pairs.
    Returns None if Tier 2 SKIPPED."""
    ...

def plot_raw_vs_partial(results: dict, cfg: ExperimentConfig) -> str:
    """Fig3: Bar chart raw_rho vs partial_rho with BCa CI error bars + scenario overlay.
    Extends H-M2 Fig1 pattern."""
    ...

def plot_delta_bbq_histogram(results: dict, cfg: ExperimentConfig) -> str | None:
    """Fig4: ΔBBQ histogram with vertical line at 0 + binomtest annotation.
    Returns None if Tier 3 not executed."""
    ...
```

---

### Main (`code/main.py`)

**Dependencies**: all modules above

```python
def run(cfg: ExperimentConfig) -> dict:
    """Orchestrate: load H-M2 results → assign_scenario → Tier2 → Tier3
    → ablations → verify → plot × 4 → save h_m3_results.json → return results."""
    ...

def main() -> None:
    """Entry point: load_config() → run() → print gate status."""
    ...
```

---

## Data Flow

- `data_loader.load_h_m2_results()` → `partial_rho`, `ci_partial`, `raw_rho`, `ci_raw`, `N`
- `analyze.assign_scenario(partial_rho, ci_partial[0], ci_partial[1])` → `scenario`, `narrative`
- `data_loader.load_tier1_dataframe()` + `load_harmbench_data()` → `analyze.tier2_analysis()`
- `data_loader.load_tier3_delta_bbq()` → `analyze.tier3_analysis()`
- All results → `visualize.*` → PNG files
- All results → `results/h_m3_results.json`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + scaffolding | ExperimentConfig dataclass, results/figures dirs | 5 | 2+1+1+1 |
| A-2 | Data loader (Tier 1) | load_h_m2_results with validation + key checks | 6 | 2+1+1+2 |
| A-3 | Data loader (Tier 2 + 3) | Hardcoded HarmBench dict + ΔBBQ CSV + fuzzy_join | 8 | 2+2+2+2 |
| A-4 | assign_scenario + verify | Core scenario classification + mechanism verification | 9 | 2+2+3+2 |
| A-5 | Tier 2 analysis | partial_corr via pingouin, N-gate, scenario assignment | 10 | 3+2+3+2 |
| A-6 | Tier 3 analysis | binomtest on 321 ΔBBQ signs | 5 | 1+1+2+1 |
| A-7 | Ablation studies | CI-method ablation + boundary-sensitivity ablation | 8 | 2+2+2+2 |
| A-8 | Fig1 scenario panel | Number line + CI band + boundary lines | 9 | 2+2+3+2 |
| A-9 | Fig2 heatmap | Pairwise partial corr heatmap (conditional on Tier 2) | 8 | 2+2+2+2 |
| A-10 | Fig3 raw vs partial | Bar chart extends H-M2 Fig1 + scenario overlay | 7 | 2+1+2+2 |
| A-11 | Fig4 ΔBBQ histogram | ΔBBQ dist + sign test annotation (conditional) | 6 | 2+1+2+1 |
| A-12 | main.py + serialization | Orchestration + h_m3_results.json with all keys | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5, A-8], Low(4-8): [A-1, A-2, A-3, A-6, A-7, A-9, A-10, A-11, A-12]

---

## h_m3_results.json Schema

```json
{
  "partial_rho": float,
  "ci_partial": [float, float],
  "raw_rho": float,
  "ci_raw": [float, float],
  "N": int,
  "scenario": "a|b|c|ambiguous",
  "is_ambiguous": bool,
  "narrative": str,
  "ablation_ci_method": {"scenario": str, "matches_primary": bool},
  "ablation_boundary_tight": {"scenario": str},
  "ablation_boundary_wide": {"scenario": str},
  "tier2": {"tier2_status": "EXECUTED|SKIPPED", "N_harmbench": int, "...": "..."},
  "tier3": {"k_positive": int, "n": int, "p_value": float, "direction": str},
  "mechanism_verified": bool,
  "gate_passed": bool
}
```
