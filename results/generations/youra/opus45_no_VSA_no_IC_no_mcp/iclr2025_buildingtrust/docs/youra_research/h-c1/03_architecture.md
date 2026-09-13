# Architecture: h-c1 (CONDITION)

**Applied**: Stratified correlation analysis reusing h-e1 infrastructure

## File Structure

```
h-c1/code/
  config.py          # model list with type labels, reuses h-e1 paths
  data_loader.py     # loads h-e1 cache + runs new instruction-tuned evals
  stratifier.py      # splits data by model_type, labels
  correlation_analyzer.py  # within-group partial corr + bootstrap CI
  visualizer.py      # 2-panel scatter, effect size bar chart
  run.py             # orchestrates all stages
  results/           # new eval JSONs (instruction-tuned only)
  figures/           # output PNGs
```

---

## Data Flow

```
h-e1/results/*.json ─┬─> data_loader ──> stratifier ──> correlation_analyzer ──> visualizer
                     │                      │                    │                   │
new instruct evals ──┘                      v                    v                   v
                                     [base, instruct]    {r, p, CI per group}   figures/
```

---

## Modules

### config.py

```python
from h_e1.config import RESULTS_DIR as H_E1_RESULTS, TASKS, SEED, N_BOOTSTRAP

MODELS = [
    # Base (from h-e1 cache)
    {"id": "EleutherAI/pythia-70m", "type": "base", ...},
    ...
    # Instruction-tuned (new evals)
    {"id": "meta-llama/Llama-2-7b-chat-hf", "type": "instruction-tuned", ...},
    ...
]
H_E1_CACHE = "../h-e1/code/results/"
RESULTS_DIR = "results/"
FIGURES_DIR = "figures/"
```

### data_loader.py

```python
def load_h_e1_scores(cache_path: str) -> "pd.DataFrame": ...
    # reads h-e1 aggregated CSV or parses JSONs
def run_missing_evals(models: list[dict]) -> None: ...
    # runs lm-eval for instruction-tuned models not in cache
def merge_scores(h_e1_df, new_df) -> "pd.DataFrame": ...
    # concat with model_type column
```

### stratifier.py

```python
def split_by_type(df: "pd.DataFrame") -> dict[str, "pd.DataFrame"]: ...
    # returns {"base": df_base, "instruction-tuned": df_instruct}
```

### correlation_analyzer.py

```python
def partial_corr_group(df: "pd.DataFrame") -> dict: ...
    # reuse h-e1's partial_corr logic per group
def bootstrap_ci_group(df, n_bootstrap=1000) -> dict: ...
def analyze_all_groups(groups: dict) -> dict: ...
    # returns {base: {r,p,ci,...}, instruction_tuned: {...}, gate_passed: bool}
```

### visualizer.py

```python
def plot_stratified_scatter(groups: dict, results: dict, out: str) -> None: ...
    # 2-panel: base | instruction-tuned
def plot_effect_comparison(results: dict, out: str) -> None: ...
    # bar chart with CI error bars
```

### run.py

```python
def main():
    run_missing_evals(MODELS)
    df = merge_scores(load_h_e1_scores(), load_new_scores())
    groups = split_by_type(df)
    results = analyze_all_groups(groups)
    plot_stratified_scatter(groups, results, ...)
    plot_effect_comparison(results, ...)
    print_gate_result(results)  # PASS if both r > 0.2
```

---

## Reuse from h-e1

| Component | Reuse Strategy |
|-----------|---------------|
| `evaluate.py` | Import or copy `run_lm_eval()` for new models |
| `aggregate.py` | Import `parse_result_file()` for JSON parsing |
| `analysis.py` | Import `partial_corr()`, `bootstrap_ci()` |
| `results/*.json` | Read cached JSONs for all 14 base models |

---

## Epic Tasks

| ID | Task | Complexity |
|----|------|------------|
| C-1 | Config + model type labels | 3 |
| C-2 | Data loader (h-e1 cache + new evals) | 5 |
| C-3 | Run 6 instruction-tuned evaluations | 4 |
| C-4 | Stratifier module | 2 |
| C-5 | Correlation analyzer per group | 4 |
| C-6 | Visualizations (2 figures) | 4 |
| C-7 | Orchestration + gate check | 3 |

**Total**: ~25 points (LIGHT tier confirmed)

---

Skipped: formal Fisher z-test for comparing r values, add if reviewers request statistical comparison between groups.
