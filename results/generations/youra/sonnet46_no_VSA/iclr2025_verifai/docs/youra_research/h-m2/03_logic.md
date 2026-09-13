# Logic: h-m2 — Contract Richness Stratification Analysis

**stepsCompleted:** [PRD, Architecture, Logic]
**hypothesis_id:** h-m2
**date:** 2026-08-03

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m1 code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**:
- `load_contracteval(jsonl_path: Optional[str] = None) -> dict` — returns `{task_id: task_dict}`, reads multi-object JSONL
- `CONTRACTEVAL_PATH` — `_archive/20260803T121822.../ContractEval/ContractEval.jsonl`
- `aggregate_stats(...) -> tuple` — returns `(AggregatedStats, per_task: dict)`
- `save_results(stats, per_task, results_dir, results)` — writes `oracle_isolation_results.json` + `per_task_results.csv`
- `AggregatedStats.by_model: dict` — `{model_name: {mean_gap, mean_cu_mass, n_tasks}}`
- `compute_per_task_stats(results) -> dict` — `{task_id: {mean_gap, mean_cu_mass, mean_diff_rate, mean_contract_rate, n_programs, task_type}}`

**CRITICAL finding**: H-M1 does NOT write `per_task_oracle_gap.json`. It writes:
- `oracle_isolation_results.json` (AggregatedStats dict, includes `by_model`)
- `per_task_results.csv` (per-program rows with `task_id, oracle_isolation_gap, task_type, model, ...`)

H-M2 must derive per-task mean gaps by reading `per_task_results.csv` and grouping by `task_id`, or by re-running `compute_per_task_stats` equivalent on the CSV rows.

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: docs/youra_research/h-m1/code/data_loader.py
CONTRACTEVAL_PATH = Path(__file__).parent.parent.parent / "_archive" / \
    "20260803T121822_routing_recovery" / ".data_cache" / "datasets" / \
    "ContractEval" / "data" / "ContractEval" / "ContractEval.jsonl"

def load_contracteval(jsonl_path: Optional[str] = None) -> dict:
    """Load ContractEval JSONL. Returns {task_id: task_dict}."""
    # Reads multi-object JSON stream (not standard jsonl)
    # Each task_dict has: task_id, + other fields (print keys on first load to confirm)

# From: docs/youra_research/h-m1/code/statistical_analysis.py
@dataclass
class AggregatedStats:
    mean_isolation_gap: float
    by_model: dict  # {model: {mean_gap, mean_cu_mass, n_tasks}}
    by_task_type: dict  # {task_type: {mean_gap, n_tasks}}
    # ... (full fields in actual file)

def aggregate_stats(results: list, ...) -> tuple:
    """Returns (AggregatedStats, per_task: dict)."""
    # per_task = {task_id: {mean_gap, mean_cu_mass, mean_diff_rate, mean_contract_rate, n_programs, task_type}}

def save_results(stats: AggregatedStats, per_task: dict, results_dir: str, results: list) -> None:
    """Writes oracle_isolation_results.json + per_task_results.csv to results_dir."""
    # results_dir = h-m1/code/results/   (RESULTS_DIR = str(ROOT / "code" / "results"))
```

**H-M1 output files** (actual paths):
- `h-m1/code/results/oracle_isolation_results.json` — AggregatedStats (includes `by_model`)
- `h-m1/code/results/per_task_results.csv` — per-program rows; columns include `task_id, task_type, model, oracle_isolation_gap, contract_unique_mass`

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation)

---

## A-1: Project Setup [Complexity: 5]

Applied: Standard PyTorch — no KB match needed (pure stdlib/scipy analysis)

### API Signatures

```python
# score_richness.py — top of file
from pathlib import Path

H1_RESULTS_CSV = Path(__file__).parent.parent.parent / "h-m1" / "code" / "results" / "per_task_results.csv"
H1_RESULTS_JSON = Path(__file__).parent.parent.parent / "h-m1" / "code" / "results" / "oracle_isolation_results.json"
CONTRACTEVAL_PATH = Path(__file__).parent.parent.parent / "_archive" / \
    "20260803T121822_routing_recovery" / ".data_cache" / "datasets" / \
    "ContractEval" / "data" / "ContractEval" / "ContractEval.jsonl"
RESULTS_DIR = Path(__file__).parent.parent / "results"
FIGURES_DIR = Path(__file__).parent.parent / "figures"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Path constants | Define all path constants in score_richness.py; mkdir results/ figures/ in orchestrator |

---

## A-2: Data Loading [Complexity: 8]

Applied: Standard PyTorch — stdlib json + pandas CSV

### API Signatures

```python
# score_richness.py

def load_gap_dict(csv_path: Optional[Path] = None) -> dict:
    """Load per-task mean oracle-isolation gaps from H-M1 per_task_results.csv.
    Returns {task_id: float}, len == 364. Raises FileNotFoundError with 'Run H-M1 first'."""
    # Groups by task_id, takes mean of oracle_isolation_gap column
    # Shape: {str: float}, 364 entries

def load_gap_dict_by_model(csv_path: Optional[Path] = None) -> dict:
    """Load per-task gaps per model for ablation 2.
    Returns {model_name: {task_id: float}}."""

def load_contracteval_tasks(jsonl_path: Optional[Path] = None) -> dict:
    """Load ContractEval tasks. Returns {task_id: task_dict}.
    Prints available keys on first load for field verification."""
    # Wraps h-m1 load_contracteval logic; standalone (no import of h-m1 module)
    # task_dict fields: inspect on load, expect 'contract_assertions' or equivalent
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Gap loading from CSV | `load_gap_dict` reads per_task_results.csv, groups by task_id, mean of oracle_isolation_gap |

---

## A-3: AST Scoring [Complexity: 10, Budget: 2]

Applied: Standard PyTorch — Python ast stdlib

### API Signatures

```python
# score_richness.py
import ast
from dataclasses import dataclass
from typing import List, Optional, Tuple
import pandas as pd

@dataclass
class RichnessScore:
    task_id: str
    tier: int            # 1=simple, 2=structural, 3=relational, 4=compound
    score: float         # node_count + 3*has_quantifier + 2*has_relational
    has_quantifier: bool
    has_relational: bool
    node_count: int

def score_postcondition(assert_clauses: List[str]) -> Tuple[int, float, bool, bool, int]:
    """Parse assert clauses, walk AST, return (tier, score, has_quantifier, has_relational, node_count).
    Skips malformed clauses with warning; returns tier=1 defaults if all clauses fail."""

def build_richness_df(
    contracteval_tasks: dict,          # {task_id: task_dict} from load_contracteval_tasks
    contract_field: str = "contract_assertions",  # field name in task_dict; auto-detected
) -> pd.DataFrame:
    """Score all tasks. Returns DataFrame shape (364, 6):
    columns=[task_id, tier, score, has_quantifier, has_relational, node_count].
    Asserts shape==(364,6) and set(tier)=={1,2,3,4}."""

def verify_mechanism_activated(
    richness_df: pd.DataFrame,
    gap_dict: dict,
    results: dict,
) -> Tuple[bool, dict]:
    """Check all activation indicators. Returns (passed: bool, indicators: dict).
    indicators keys: richness_computed, all_tiers_present, gap_loaded,
                     gradient_direction, spearman_computed."""
```

### Pseudo-code for score_postcondition

```
for clause in assert_clauses:
    strip "assert" prefix; try ast.parse(expr, mode="eval")
    except SyntaxError: log warning, continue
    for node in ast.walk(tree):
        total_nodes += 1
        if Call node and func.id in ("any", "all"): has_quantifier = True
        if Compare node with len(ops) > 1: has_relational = True
        if BoolOp node: has_relational = True

tier = 4 if (has_quantifier and has_relational)
      else 3 if has_quantifier
      else 2 if has_relational
      else 1
score = node_count + 3*has_quantifier + 2*has_relational
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | score_postcondition | AST walk: quantifier/relational detection, tier assignment, SyntaxError skip |
| L-3-2 | build_richness_df + verify | Build DataFrame from all 364 tasks; validate shape and tier coverage |

---

## A-4: Primary Stats [Complexity: 12, Budget: 2]

Applied: Standard PyTorch — scipy.stats spearmanr + permutation_test + kruskal

### API Signatures

```python
# analyze_correlation.py
from typing import Tuple, List
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, permutation_test, kruskal

def spearman_with_permutation(
    x: List[float],
    y: List[float],
    n_resamples: int = 9999,
    seed: int = 42,
) -> dict:
    """Returns {rho: float, p_asymptotic: float, p_exact: float}.
    Uses spearmanr(alternative='greater') + permutation_test(permutation_type='pairings')."""

def bootstrap_rho_ci(
    x: List[float],
    y: List[float],
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> Tuple[float, float]:
    """Returns (ci_lower, ci_upper) — 95% bootstrap CI on Spearman rho."""

def kruskal_wallis_tiers(
    richness_df: pd.DataFrame,  # columns include tier, task_id
    gap_dict: dict,             # {task_id: float}
) -> Tuple[float, float]:
    """Returns (kw_stat, kw_p). Groups gap_dict values by tier 1-4."""

def tier_means(
    richness_df: pd.DataFrame,
    gap_dict: dict,
) -> dict:
    """Returns {1: float, 2: float, 3: float, 4: float} — mean gap per tier."""

def run_full_analysis(
    richness_df: pd.DataFrame,
    gap_dict: dict,
    h1_results: dict,           # parsed oracle_isolation_results.json
) -> dict:
    """Run primary test + KW + bootstrap CI + ablations.
    Returns complete results dict for h_m2_results.json.
    Sets FLAT_GRADIENT=True if rho < 0.15. Raises ValueError if rho is NaN."""
```

### Data Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| x (scores) | List[float], len=364 | richness_df["score"].tolist() |
| y (gaps) | List[float], len=364 | aligned with x by task_id join |
| results dict | flat dict | rho, p_asymptotic, p_exact, ci_lower, ci_upper, kw_stat, kw_p, ablations, FLAT_GRADIENT |

### Pseudo-code for spearman_with_permutation

```
rho, p_asymptotic = spearmanr(x, y, alternative='greater')
stat_fn = lambda xs: spearmanr(xs, y).statistic
res = permutation_test((x,), stat_fn, permutation_type='pairings',
                        n_resamples=n_resamples, alternative='greater',
                        random_state=seed)
return {rho, p_asymptotic, p_exact: res.pvalue}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | spearman_with_permutation + bootstrap_rho_ci | Primary Spearman test + exact p + bootstrap CI |
| L-4-2 | kruskal_wallis_tiers + tier_means + run_full_analysis | KW test, tier means, orchestrate full results dict |

---

## A-5: Ablation Studies [Complexity: 11, Budget: 2]

Applied: Standard PyTorch — scipy.stats spearmanr on subsets

### API Signatures

```python
# analyze_correlation.py

def run_ablations(
    richness_df: pd.DataFrame,
    gap_dict: dict,
    h1_results: dict,              # oracle_isolation_results.json, for by_model and by_task_type
    gap_dict_by_model: dict,       # {model: {task_id: float}} from load_gap_dict_by_model
) -> dict:
    """Run all 4 ablations. Returns dict keyed by ablation name."""
```

### Ablation Logic

```
ablation_1 (discrete tier):
    x = richness_df["tier"].tolist()  # integer IV
    run spearman_with_permutation(x, y_gaps)

ablation_2 (per-model):
    for model, model_gaps in gap_dict_by_model.items():
        task_ids = [t for t in richness_df.task_id if t in model_gaps]
        x = richness_df.set_index("task_id").loc[task_ids, "score"].tolist()
        y = [model_gaps[t] for t in task_ids]
        results[model] = spearmanr(x, y, alternative='greater')

ablation_3 (HumanEval+ / MBPP+ subsets):
    task_type derived from: gap_dict with h1_results["by_task_type"] keys, or
    from per_task_results.csv task_type column (load alongside gap_dict)
    filter richness_df by task_type in {"humaneval", "mbpp"} (check actual field values)
    run spearman_with_permutation on each subset

ablation_4 (node_count only):
    x = richness_df["node_count"].tolist()
    run spearman_with_permutation(x, y_gaps)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | ablation_1 + ablation_4 | Discrete tier IV and node_count-only IV (both simple Spearman variants) |
| L-5-2 | ablation_2 + ablation_3 | Per-model Spearman loop; HumanEval+/MBPP+ subset splits |

---

## A-6: Mechanism Verification [Complexity: 7]

### API Signatures

(Already defined in A-3 — `verify_mechanism_activated` in `score_richness.py`)

No additional subtasks — within budget for low-complexity epic.

---

## A-7: Visualization [Complexity: 10]

### API Signatures

```python
# visualize.py
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_gate_metrics(rho: float, threshold: float, p_value: float, out_dir: Path) -> None:
    """Bar: achieved rho vs threshold 0.30, p annotated. Saves figure_gate_metrics.png."""

def plot_scatter(richness_df: pd.DataFrame, gap_dict: dict, rho: float, out_dir: Path) -> None:
    """Scatter: score (x) vs gap (y), colored by tier, rho annotated. Saves figure_scatter.png."""

def plot_boxplot(richness_df: pd.DataFrame, gap_dict: dict, out_dir: Path) -> None:
    """Boxplot: gap per tier 1-4. Saves figure_boxplot.png."""

def plot_heatmap(richness_df: pd.DataFrame, gap_dict_by_model: dict, out_dir: Path) -> None:
    """Heatmap: task richness tier x model family mean gap. Saves figure_heatmap.png."""

def plot_violin(richness_df: pd.DataFrame, gap_dict: dict, cu_dict: dict, out_dir: Path) -> None:
    """Violin: contract-unique failure mass by richness tier. Saves figure_violin.png.
    cu_dict = {task_id: mean_cu_mass} derived from per_task_results.csv."""

def save_all(
    richness_df: pd.DataFrame,
    gap_dict: dict,
    gap_dict_by_model: dict,
    cu_dict: dict,
    results: dict,
    out_dir: Path,
) -> None:
    """Single entry point — calls all 5 plot functions."""
```

---

## A-8: Orchestration + Output [Complexity: 8]

### API Signatures

```python
# run_h_m2.py
from pathlib import Path
import json
import pandas as pd

RESULTS_DIR: Path  # h-m2/results/
FIGURES_DIR: Path  # h-m2/figures/

def load_h1_results(json_path: Path) -> dict:
    """Load oracle_isolation_results.json. Returns parsed dict."""

def save_results(results: dict, richness_df: pd.DataFrame, results_dir: Path) -> None:
    """Write h_m2_results.json and richness_scores.csv."""

def main() -> None:
    """Orchestrator sequence:
    1. load_gap_dict() — fail early if CSV missing
    2. load_gap_dict_by_model()
    3. load_contracteval_tasks() — print field keys
    4. build_richness_df() — validate (364,6), all 4 tiers
    5. run_full_analysis()
    6. verify_mechanism_activated()
    7. save_all() figures
    8. save_results()
    9. Print gate result: PASS / FAIL / FLAT_GRADIENT
    """
```

### Results JSON Schema

```python
# h_m2_results.json structure
{
    "rho": float,
    "p_asymptotic": float,
    "p_exact": float,
    "ci_lower": float,
    "ci_upper": float,
    "kw_stat": float,
    "kw_p": float,
    "tier_means": {1: float, 2: float, 3: float, 4: float},
    "FLAT_GRADIENT": bool,
    "gate_passed": bool,
    "ablations": {
        "discrete_tier": {"rho": float, "p_asymptotic": float, "p_exact": float},
        "per_model": {model: {"rho": float, "p_asymptotic": float}},
        "humaneval_plus": {"rho": float, "p_asymptotic": float, "n": int},
        "mbpp_plus": {"rho": float, "p_asymptotic": float, "n": int},
        "node_count_only": {"rho": float, "p_asymptotic": float, "p_exact": float},
    },
    "mechanism_indicators": dict,
}
```

---

## Implementation Notes for Phase 4

1. **per_task_oracle_gap.json does not exist** — load gaps from `per_task_results.csv` (group by task_id, mean oracle_isolation_gap). Also load `task_type` from same CSV for ablation 3.
2. **ContractEval field name** — print `task_dict.keys()` on first load; expected `contract_assertions` but may differ. Auto-detect: look for keys containing "assert" or "contract".
3. **CONTRACTEVAL_PATH** — use same path as H-M1 (`_archive/.../ContractEval.jsonl`). Accept override via env var or CLI arg.
4. **by_model gaps for ablation 2** — derive from `per_task_results.csv` grouping by `(task_id, model)`, then mean gap per group.
5. **cu_dict for violin plot** — derive from `per_task_results.csv` grouping by task_id, mean contract_unique_mass.
6. **scipy.stats.permutation_test** — `alternative='greater'` is passed to the `PermutationMethod` via `permutation_test(..., alternative='greater')`, not inside stat_fn.
