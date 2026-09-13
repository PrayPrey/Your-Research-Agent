# Architecture: H-E1
# Fuzzy Join Data Infrastructure Audit

Applied: no relevant KB pattern (Archon KB contains only diffusers/image-gen content)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; single-script data pipeline

---

## Overview

EXISTENCE PoC — single Python script to test if fuzzy join yields N_complete >= 30.
No ML training. No GPU. Pandas + rapidfuzz + matplotlib only.

---

## File Organization

- `docs/youra_research/h-e1/code/run_audit.py` — single executable script (all logic)
- `docs/youra_research/h-e1/figures/` — output directory for 4 figures
- `data/llm_leaderboard_v1/llm.csv` — cached LLM LB v1 download
- `data/bbq_scores/bbq_per_model.csv` — cached HELM Lite BBQ scores

---

## Modules

### DataLoader (`run_audit.py`)

**Dependencies**: requests, pandas, datasets

```python
def load_llm_leaderboard(
    url: str = "https://github.com/fboulnois/llm-leaderboard-csv/releases/download/v1.3.0/llm.csv",
    cache_path: str = "./data/llm_leaderboard_v1/llm.csv"
) -> pd.DataFrame:
    """Returns DataFrame with columns: model_name, TruthfulQA_MC2, MMLU (open-weight only)"""
    ...

def load_bbq_scores(
    cache_path: str = "./data/bbq_scores/bbq_per_model.csv"
) -> pd.DataFrame:
    """Returns DataFrame with columns: model_name, bbq_accuracy"""
    ...
```

---

### FuzzyJoiner (`run_audit.py`)

**Dependencies**: rapidfuzz, pandas

```python
def exact_join(df_llm: pd.DataFrame, df_bbq: pd.DataFrame) -> pd.DataFrame:
    """pd.merge inner join on model_name; returns complete rows"""
    ...

def fuzzy_join(
    df_llm: pd.DataFrame,
    df_bbq: pd.DataFrame,
    threshold: int = 75
) -> tuple[pd.DataFrame, float]:
    """
    WRatio fuzzy join via process.extractOne.
    Falls back to token_set_ratio at 70 then 65 if match_rate < 0.55.
    Returns (df_complete, match_rate)
    """
    ...

def sensitivity_sweep(
    df_llm: pd.DataFrame,
    df_bbq: pd.DataFrame,
    thresholds: list[int] = [65, 70, 75, 80]
) -> pd.DataFrame:
    """Returns table: threshold -> N_complete, match_rate"""
    ...
```

---

### GateVerifier (`run_audit.py`)

**Dependencies**: pandas

```python
def verify_mechanism_activated(
    df_complete: pd.DataFrame,
    N_complete: int,
    match_rate: float,
    N_exact: int
) -> tuple[bool, dict]:
    """Returns (all_pass, indicators_dict)"""
    ...
```

---

### Visualizer (`run_audit.py`)

**Dependencies**: matplotlib, matplotlib_venn

```python
def plot_gate_metrics(N_complete: int, match_rate: float, out_dir: str) -> None:
    """Figure 1: bar chart N_complete vs 30, match_rate vs 0.55"""
    ...

def plot_score_histogram(df_matches: pd.DataFrame, out_dir: str) -> None:
    """Figure 2: histogram of WRatio scores for matched pairs"""
    ...

def plot_venn(n_llm: int, n_bbq: int, n_matched: int, out_dir: str) -> None:
    """Figure 3: Venn diagram LLM LB vs BBQ vs matched"""
    ...

def plot_sensitivity(sweep_df: pd.DataFrame, out_dir: str) -> None:
    """Figure 4: line plot N_complete vs threshold"""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Acquisition | URL preflight + download LLM LB v1 CSV + load HELM Lite BBQ scores with caching | 10 | 2+2+4+2 |
| A-2 | Exact + Fuzzy Join | Exact baseline join, WRatio join at threshold=75, token_set_ratio fallback | 12 | 3+2+5+2 |
| A-3 | Gate Verification + Sensitivity | Count N_complete, verify_mechanism_activated, sweep thresholds [65,70,75,80] | 8 | 2+1+3+2 |
| A-4 | Visualization | 4 figures (bar, histogram, Venn, line plot) saved to figures/ | 9 | 3+1+3+2 |
| A-5 | Integration + CLI | Wire all steps in main(), print summary table, end-to-end test | 7 | 1+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-2, A-4], Low(4-8): [A-3, A-5]

---

## Dependencies

```
rapidfuzz>=3.0
pandas>=1.5
datasets>=2.0
requests>=2.28
matplotlib>=3.5
matplotlib-venn>=0.11
numpy>=1.21
```

---

## Execution Flow

```
main()
  -> load_llm_leaderboard()   # preflight HEAD check, cache to data/
  -> load_bbq_scores()        # HuggingFace or CSV, cache to data/
  -> exact_join()             # N_exact baseline
  -> fuzzy_join(threshold=75) # primary mechanism + fallback
  -> verify_mechanism_activated()
  -> sensitivity_sweep()      # thresholds [65,70,75,80]
  -> plot_gate_metrics()
  -> plot_score_histogram()
  -> plot_venn()
  -> plot_sensitivity()
  -> print summary + gate pass/fail
```

---

*Generated: 2026-07-30 | Hypothesis: H-E1 | Phase: 3 - Architecture*
