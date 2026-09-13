# Architecture: h-e1

**Applied**: minimal-pipeline pattern (flat module layout, single entry point)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis or existing codebase

---

## File Structure

```
docs/youra_research/h-e1/
├── code/
│   ├── run_experiment.py        # Entry point — orchestrates full pipeline
│   ├── data_loader.py           # CSV load + NaN drop + N>=200 assert
│   ├── statistical_analysis.py  # VIF + Spearman partial corr + bootstrap
│   ├── gate_evaluator.py        # Gate logic (r>0, p<0.05, |r|>=0.15)
│   ├── visualizer.py            # 5 figures -> figures/
│   └── report_writer.py         # Writes 04_validation.md
├── figures/                     # Output: 5 PNG files
└── 04_validation.md             # Results output
```

**Data path**: `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv`

---

## Modules

### DataLoader (`code/data_loader.py`)

**Dependencies**: pandas

```python
def load_and_validate(csv_path: str) -> pd.DataFrame:
    # loads CSV, drops NaN in {win_rate, length_controlled_winrate, avg_length},
    # asserts len >= 200, returns clean DataFrame
    ...
```

---

### StatisticalAnalysis (`code/statistical_analysis.py`)

**Dependencies**: pandas, numpy, pingouin, statsmodels

```python
def compute_vif(df: pd.DataFrame) -> dict[str, float]:
    # VIF for win_rate and avg_length; keys: 'win_rate', 'avg_length'
    ...

def spearman_partial_corr(df: pd.DataFrame) -> dict:
    # pingouin.partial_corr(x='win_rate', y='length_controlled_winrate',
    #   covar='avg_length', method='spearman', alternative='greater')
    # returns: {'r_partial': float, 'p_val': float, 'ci95': list, 'n': int}
    ...

def bootstrap_partial_corr(
    df: pd.DataFrame,
    n_bootstrap: int = 1000,
    random_state: int = 42
) -> tuple[float, float, list[float]]:
    # returns (ci_lower, ci_upper, boot_rs)
    ...
```

---

### GateEvaluator (`code/gate_evaluator.py`)

**Dependencies**: none (pure logic)

```python
def evaluate_gate(
    r_partial: float,
    p_val: float,
    boot_ci_lower: float
) -> dict:
    # passes = (r_partial > 0) and (p_val < 0.05) and (abs(r_partial) >= 0.15)
    # returns: {'passes_gate': bool, 'r_partial': float, 'p_val': float,
    #           'boot_ci_lower': float, 'r_threshold': 0.15, 'alpha': 0.05}
    ...
```

---

### Visualizer (`code/visualizer.py`)

**Dependencies**: matplotlib, seaborn, pandas, numpy, pathlib

```python
def save_all_figures(
    df: pd.DataFrame,
    boot_rs: list[float],
    vif: dict,
    corr_result: dict,
    output_dir: str
) -> list[str]:
    # Generates and saves 5 figures; returns list of file paths
    # fig1: scatter win_rate vs LC_winrate, color by avg_length quartile
    # fig2: partial regression (residualized win_rate vs residualized LC_winrate)
    # fig3: bootstrap histogram with CI bands
    # fig4: VIF bar chart
    # fig5: delta scatter (LC_winrate - win_rate) vs win_rate with trend line
    ...
```

---

### ReportWriter (`code/report_writer.py`)

**Dependencies**: pathlib

```python
def write_validation_report(
    gate_result: dict,
    corr_result: dict,
    boot_ci: tuple,
    vif: dict,
    figure_paths: list[str],
    output_path: str
) -> None:
    # Writes 04_validation.md: gate status, r_partial, p_val, CI95,
    # bootstrap CI, VIF values, figure paths, interpretation
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    # 1. load_and_validate(CSV_PATH)
    # 2. compute_vif(df)
    # 3. spearman_partial_corr(df)
    # 4. bootstrap_partial_corr(df)
    # 5. evaluate_gate(r_partial, p_val, boot_ci_lower)
    # 6. save_all_figures(df, boot_rs, vif, corr_result, FIGURES_DIR)
    # 7. write_validation_report(..., OUTPUT_PATH)
    # 8. print gate result (PASS/FAIL) and exit

if __name__ == '__main__':
    main()
```

---

## Constants (inline in run_experiment.py)

```python
CSV_PATH = 'docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv'
FIGURES_DIR = 'docs/youra_research/h-e1/figures'
OUTPUT_PATH = 'docs/youra_research/h-e1/04_validation.md'
N_BOOTSTRAP = 1000
RANDOM_STATE = 42
ALPHA = 0.05
R_THRESHOLD = 0.15
VIF_WARN = 5.0
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1-1 | Data Loading | Implement data_loader.py: CSV load, NaN drop, N>=200 assert | 5 | 1+1+1+2 |
| E1-2 | Statistical Analysis | Implement statistical_analysis.py: VIF + partial corr + bootstrap | 12 | 3+2+4+3 |
| E1-3 | Gate Evaluation | Implement gate_evaluator.py: AND-gate logic + result dict | 4 | 1+1+1+1 |
| E1-4 | Visualization | Implement visualizer.py: 5 figures saved to figures/ | 10 | 3+2+3+2 |
| E1-5 | Report Writer | Implement report_writer.py: write 04_validation.md | 6 | 2+1+1+2 |
| E1-6 | Orchestration | Implement run_experiment.py: wire all modules, CLI entry point | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E1-2, E1-4], Low(4-8): [E1-1, E1-3, E1-5, E1-6]

---

## Module Dependency Graph

```
run_experiment.py
  -> data_loader.py
  -> statistical_analysis.py
  -> gate_evaluator.py
  -> visualizer.py
  -> report_writer.py
```

All modules are leaf nodes with no cross-dependencies except through run_experiment.py.
