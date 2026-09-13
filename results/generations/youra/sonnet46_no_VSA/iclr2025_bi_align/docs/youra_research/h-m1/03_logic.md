# Logic: H-M1 — MMLU Scale Covariate Pre-Test

**Applied**: standard scipy statistical API pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1)
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**:
- `AuditConfig` (dataclass) — `figures_dir: str`, `seed: int`, `n_complete_min: int`
- `main(config: AuditConfig) -> dict` — flat orchestration pattern (load → analyze → plot → save → return dict)
- `verify_mechanism_activated(df_complete, N_complete, match_rate, N_exact) -> tuple` — returns `(all_pass: bool, indicators: dict)`
- `plot_gate_metrics(N_complete, match_rate, out_dir) -> None` — saves PNG, returns None
- H-E1 CSV columns: `model_name`, `TruthfulQA_MC2`, `MMLU`, `bbq_accuracy` (note: H-E1 uses `bbq_accuracy` not `BBQ_accuracy`)

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: docs/youra_research/h-e1/code/run_audit.py (ACTUAL CODE)

def main(config: AuditConfig = None) -> dict:
    """Orchestrate audit. Returns results dict with hypothesis_id, N_complete, gate_passed, etc."""
    # H-M1 does NOT call this — reuses its output CSV only

# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class AuditConfig:
    llm_lb_cache: str = "./data/llm_leaderboard_v1/llm.csv"
    bbq_cache: str = "./data/bbq_scores/bbq_per_model.csv"
    figures_dir: str = "./docs/youra_research/h-e1/figures"
    seed: int = 42
    n_complete_min: int = 30
```

**Column name verified**: H-E1 CSV stores BBQ column as `bbq_accuracy` (lowercase).
H-M1 `load_data` must accept this and optionally rename to `BBQ_accuracy` for internal use,
OR keep as `bbq_accuracy` and reference consistently throughout.

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

---

## Data Schema

DataFrame after `load_data()`: shape `(N, 4)` where N ≈ 297

| Column | Dtype | Scale | Source |
|--------|-------|-------|--------|
| `model_name` | str | — | H-E1 CSV |
| `TruthfulQA_MC2` | float64 | 0–100 | H-E1 CSV |
| `bbq_accuracy` | float64 | 0–100 (normalized) | H-E1 CSV (may be 0–1, normalize if max ≤ 1.0) |
| `MMLU` | float64 | 0–100 | H-E1 CSV |

---

## A-3: Correlation Analysis [Complexity: 8, Budget: 1 subtask]

**Applied**: standard scipy statistical API pattern

### API Signatures

```python
def load_data(cfg: AnalysisConfig) -> pd.DataFrame:
    """Load H-E1 CSV, normalize BBQ, drop nulls. Raises RuntimeError if N < cfg.n_min."""
    # Returns: DataFrame shape (N, 4): model_name, TruthfulQA_MC2, bbq_accuracy, MMLU

def compute_correlations(df: pd.DataFrame) -> dict:
    """Compute Spearman rho and R² for 3 column pairs. Returns full results dict."""
    # df shape: (N, 4) with columns: TruthfulQA_MC2, bbq_accuracy, MMLU
    # Returns: see Return Dict Spec below

def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """Validate results dict integrity. Returns (all_valid: bool, indicators: dict)."""
    # Checks: R² non-NaN, in [0,1], N >= 30, gate_pass key present

def plot_r2_bar(results: dict, cfg: AnalysisConfig) -> str:
    """Bar chart R²(MMLU×TruthfulQA) and R²(MMLU×BBQ) with 0.05 threshold line."""
    # Returns: absolute save path str

def plot_scatter_mmlu_truthqa(df: pd.DataFrame, results: dict, cfg: AnalysisConfig) -> str:
    """Scatter MMLU vs TruthfulQA_MC2, annotated with rho value."""
    # df shape: (N, 4); Returns: absolute save path str

def plot_scatter_mmlu_bbq(df: pd.DataFrame, results: dict, cfg: AnalysisConfig) -> str:
    """Scatter MMLU vs bbq_accuracy, annotated with rho value."""
    # df shape: (N, 4); Returns: absolute save path str

def plot_correlation_heatmap(df: pd.DataFrame, cfg: AnalysisConfig) -> str:
    """Spearman correlation heatmap for {MMLU, TruthfulQA_MC2, bbq_accuracy}."""
    # df shape: (N, 4); Returns: absolute save path str

def save_results(results: dict, cfg: AnalysisConfig) -> None:
    """Write results to h_m1_results.json and h_m1_summary.txt in cfg.results_dir."""

def run(cfg: AnalysisConfig) -> dict:
    """Orchestrate: load → correlate → verify → plot×4 → save → return results."""
    # Returns: results dict from compute_correlations, augmented with figure paths
```

### Return Dict Spec for `compute_correlations`

```python
{
    "hypothesis_id": str,           # "h-m1"
    "N": int,                       # e.g. 297
    # MMLU × TruthfulQA pair
    "rho_mmlu_truthqa": float,      # Spearman rho, range [-1, 1]
    "R2_mmlu_truthqa": float,       # rho ** 2, range [0, 1]
    "p_mmlu_truthqa": float,        # two-tailed p-value
    # MMLU × BBQ pair
    "rho_mmlu_bbq": float,          # Spearman rho
    "R2_mmlu_bbq": float,           # rho ** 2
    "p_mmlu_bbq": float,            # two-tailed p-value
    # Baseline for H-M2
    "raw_rho_truth_bbq": float,     # Spearman rho(TruthfulQA, BBQ), unadjusted
    "p_raw_truth_bbq": float,       # p-value for above
    # Gate
    "gate_pass": bool,              # R2_mmlu_truthqa > 0.05 AND R2_mmlu_bbq > 0.05
}
```

### Pseudo-code for `compute_correlations`

```
def compute_correlations(df):
    N = len(df)

    # Pair 1: MMLU × TruthfulQA
    res1 = scipy.stats.spearmanr(df['MMLU'], df['TruthfulQA_MC2'])
    rho_mt = res1.statistic
    p_mt   = res1.pvalue
    R2_mt  = rho_mt ** 2

    # Pair 2: MMLU × BBQ
    res2 = scipy.stats.spearmanr(df['MMLU'], df['bbq_accuracy'])
    rho_mb = res2.statistic
    p_mb   = res2.pvalue
    R2_mb  = rho_mb ** 2

    # Pair 3: TruthfulQA × BBQ (baseline for H-M2)
    res3 = scipy.stats.spearmanr(df['TruthfulQA_MC2'], df['bbq_accuracy'])
    rho_tb = res3.statistic
    p_tb   = res3.pvalue

    gate_pass = (R2_mt > 0.05) and (R2_mb > 0.05)
    log: "H-M1 gate: MMLU R²(TruthfulQA)={R2_mt:.3f}, R²(BBQ)={R2_mb:.3f} — PASS/FAIL"

    return {
        "hypothesis_id": "h-m1", "N": N,
        "rho_mmlu_truthqa": rho_mt, "R2_mmlu_truthqa": R2_mt, "p_mmlu_truthqa": p_mt,
        "rho_mmlu_bbq": rho_mb, "R2_mmlu_bbq": R2_mb, "p_mmlu_bbq": p_mb,
        "raw_rho_truth_bbq": rho_tb, "p_raw_truth_bbq": p_tb,
        "gate_pass": gate_pass,
    }
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Correlation Core | `compute_correlations`: 3× spearmanr, R²=rho², gate eval, return dict |
