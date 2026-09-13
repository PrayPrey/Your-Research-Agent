# Logic: H-M3 - LlmFix 19-Cause Fine-Grained Error Taxonomy Analysis

Applied: string-matching taxonomy pattern (from h-e1/code/analyze.py)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1 + h-m2)
**Status**: API signatures verified from actual h-e1 code
**Analyzed Path**: `docs/youra_research/20260323_dl4c/h-e1/code/analyze.py`
**Relevant Symbols**:
- `classify_error(error_trace: Optional[str]) -> str` - single param, uses `error_lower` string matching
- `check_effect_direction(rl_results, dpo_results) -> Tuple[float, float, bool]` - returns `(rl_prop, dpo_prop, direction_matches)`; `direction_matches = rl_prop < dpo_prop`
- `run_analysis(rl_results, dpo_results, config) -> Dict` - returns flat dict with `gate_pass`, `cramers_v`, `p_value`
- `SYNTAX_ERRORS = ["syntaxerror", "indentationerror"]` (lowercase, no Python exception suffix)
- `RUNTIME_ERRORS = ["typeerror", "nameerror", "attributeerror", "indexerror", "keyerror", "valueerror", "zerodivisionerror", "recursionerror", "timeout"]`
- `ASSERTION_ERRORS = ["assertionerror", "expected"]`

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: docs/youra_research/20260323_dl4c/h-e1/code/analyze.py (ACTUAL CODE)

# Single-param classify; checks error_lower (lowercase) against list membership
def classify_error(error_trace: Optional[str]) -> str:
    """Returns: 'pass' | 'syntax' | 'runtime' | 'assertion' | 'other'"""
    ...

# Direction check: direction_matches = rl_prop < dpo_prop (NOT dpo > rl check)
def check_effect_direction(
    rl_results: List[dict],
    dpo_results: List[dict],
) -> Tuple[float, float, bool]:
    """Returns (rl_syntax_runtime, dpo_syntax_runtime, direction_matches)"""
    ...

# run_analysis returns FLAT dict (not nested coarse/fine dict)
def run_analysis(
    rl_results: List[dict],
    dpo_results: List[dict],
    config: ExperimentConfig,
) -> Dict:
    """Returns dict with: chi2, p_value, cramers_v, dof, gate_pass, ..."""
    ...
```

**Verified from**: `docs/youra_research/20260323_dl4c/h-e1/code/analyze.py` (actual code)

**Critical Notes**:
- H-E1 `classify_error` takes only `error_trace` (no `status` param)
- Error lists use lowercase Python exception names without suffix (e.g., `"syntaxerror"` not `"SyntaxError"`)
- H-M3 does NOT import from h-e1 code; loads JSON outputs and reimplements classification
- H-M3 `run_analysis` returns NESTED dict (`coarse`, `fine`, `direction`, `gate_result`) unlike H-E1 flat dict

---

## A-1: Environment & Config [Complexity: 6, Budget: 1/5]

**Applied**: Standard dataclass config pattern

### API Signatures

```python
@dataclass
class ExperimentConfig:
    he1_results_path: str = "../h-e1/code/outputs/experiment_results.json"
    he1_metrics_path: str = "../h-e1/code/outputs/metrics.json"
    output_dir: str = "outputs"
    figures_dir: str = "figures"
    chi2_p_threshold: float = 0.05
    cramers_v_threshold_fine: float = 0.03
    cramers_v_threshold_coarse: float = 0.05
    pseudocount: float = 0.5
    seed: int = 42

CONFIG = ExperimentConfig()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Config dataclass | Implement ExperimentConfig with all fields above |

---

## A-2: Data Loader [Complexity: 8, Budget: 1/5]

### API Signatures

```python
def load_he1_results(config: ExperimentConfig) -> Tuple[List[dict], List[dict]]:
    """Load experiment_results.json; return (rl_results, dpo_results).
    Each dict: {sample_id, model, problem_id, status, error_trace, output}
    """
    ...

def extract_failures(results: List[dict]) -> List[dict]:
    """Filter to status == 'fail' only."""
    ...

def load_he1_metrics(config: ExperimentConfig) -> dict:
    """Load metrics.json for validation."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Data loader | Implement load_he1_results + extract_failures with JSON parsing |

---

## A-3 + A-4: LlmFix Classifier [Complexity: 21, Budget: 1/5]

**Applied**: string-matching taxonomy pattern (extended from h-e1 SYNTAX_ERRORS/RUNTIME_ERRORS lists)

### Taxonomy Constants

```python
# LlmFix taxonomy (19 causes across 3 tiers)
# Matching strings are lowercase (consistent with h-e1 pattern: error_lower = error_trace.lower())
LLMFIX_TAXONOMY: Dict[str, List[str]] = {
    "syntax": ["indentation_error", "syntax_error", "missing_import"],
    "runtime": ["name_error", "type_error", "attribute_error", "index_error",
                "key_error", "value_error", "zero_division", "recursion_error",
                "timeout", "memory_error"],
    "assertion": ["wrong_output", "partial_output", "missing_output",
                  "wrong_type", "off_by_one", "boundary_error"],
}

# Lowercase error strings for matching (mirrors h-e1 SYNTAX_ERRORS pattern)
COARSE_SYNTAX_ERRORS = ["syntaxerror", "indentationerror", "importerror", "modulenotfounderror"]
COARSE_RUNTIME_ERRORS = [
    "typeerror", "nameerror", "attributeerror", "indexerror", "keyerror",
    "valueerror", "zerodivisionerror", "recursionerror", "timeout", "memoryerror"
]
COARSE_ASSERTION_ERRORS = ["assertionerror", "expected"]

# Fine-cause match strings: (substring_to_match -> fine_cause_label)
FINE_SYNTAX_MAP = [
    ("indentationerror", "indentation_error"),
    ("syntaxerror", "syntax_error"),
    ("importerror", "missing_import"),
    ("modulenotfounderror", "missing_import"),
]
FINE_RUNTIME_MAP = [
    ("nameerror", "name_error"),
    ("typeerror", "type_error"),
    ("attributeerror", "attribute_error"),
    ("indexerror", "index_error"),
    ("keyerror", "key_error"),
    ("valueerror", "value_error"),
    ("zerodivisionerror", "zero_division"),
    ("recursionerror", "recursion_error"),
    ("timeout", "timeout"),
    ("memoryerror", "memory_error"),
]
# Assertion fine-cause: use output pattern analysis
ALL_FINE_CAUSES: List[str] = [c for causes in LLMFIX_TAXONOMY.values() for c in causes]
```

### API Signatures

```python
def classify_error_coarse(error_trace: Optional[str]) -> str:
    """Returns: 'syntax' | 'runtime' | 'assertion' | 'other' | 'pass'
    Uses error_lower string matching; order: syntax → assertion → runtime → other
    """
    ...

def classify_error_fine(error_trace: Optional[str], coarse: str) -> str:
    """Returns one of 19 LlmFix cause labels or 'unknown'.
    Dispatches to FINE_SYNTAX_MAP / FINE_RUNTIME_MAP / assertion heuristic based on coarse.
    """
    ...

def classify_error_llmfix(
    error_trace: Optional[str],
    output: Optional[str] = None,
) -> Tuple[str, str]:
    """Returns (coarse_category, fine_cause) for dual-granularity classification."""
    ...

def classify_batch(results: List[dict]) -> List[dict]:
    """Add 'coarse_category' and 'fine_cause' keys to each result dict in-place."""
    ...
```

### Pseudo-code for assertion fine-cause

```
def _classify_assertion_fine(error_trace, output):
    # output comparison heuristics
    if "wrong type" or isinstance mismatch → "wrong_type"
    if partial match or truncated → "partial_output"
    if empty or None output → "missing_output"
    if off-by-one pattern (±1 numeric diff) → "off_by_one"
    if boundary condition keywords → "boundary_error"
    default → "wrong_output"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Classifier | Implement all 4 functions + taxonomy constants in classifier.py |

---

## A-5 + A-6: Statistical Analysis [Complexity: 23, Budget: 1/5]

**Applied**: Standard scipy chi-square contingency pattern

### API Signatures

```python
def build_contingency_coarse(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    pseudocount: float = 0.5,
) -> np.ndarray:
    """Build 2x3 table (model × {syntax, runtime, assertion}). Shape: [2, 3]"""
    ...

def build_contingency_fine(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    pseudocount: float = 0.5,
) -> Tuple[np.ndarray, List[str]]:
    """Build 2xK table (model × fine causes with counts > 0). Returns (table [2, K], cause_labels)."""
    ...

def chi_square_test(contingency: np.ndarray) -> Tuple[float, float, int, np.ndarray]:
    """Thin wrapper around scipy.stats.chi2_contingency.
    Returns (chi2, p_value, dof, expected).
    """
    ...

def cramers_v(contingency: np.ndarray) -> float:
    """V = sqrt(chi2 / (n * min(r-1, c-1))). n = contingency.sum()."""
    ...

def check_direction(
    rl_classified: List[dict],
    dpo_classified: List[dict],
) -> Tuple[float, float, bool]:
    """Returns (rl_sr_prop, dpo_sr_prop, direction_satisfied).
    direction_satisfied = dpo_sr_prop > rl_sr_prop
    (mirrors h-e1 check_effect_direction logic: direction_matches = rl_prop < dpo_prop)
    """
    ...

def compute_descriptive_stats(classified: List[dict]) -> dict:
    """Returns {'coarse_counts': Counter, 'fine_counts': Counter,
                'coarse_props': dict, 'fine_props': dict}"""
    ...

def run_analysis(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    config: ExperimentConfig,
) -> dict:
    """Full dual-granularity analysis. Saves outputs/metrics.json.
    Returns nested dict with keys: coarse, fine, direction, gate_result.
    """
    ...

def save_outputs(
    all_classified: List[dict],
    metrics: dict,
    config: ExperimentConfig,
) -> None:
    """Save experiment_results.json and classification_data.csv."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| coarse table | [2, 3] | rows: RL/DPO; cols: syntax/runtime/assertion |
| fine table | [2, K] | K = number of observed fine causes (up to 19) |
| expected | same as input | from chi2_contingency |

### metrics.json structure

```python
{
    "coarse": {"chi2": float, "p_value": float, "cramers_v": float, "dof": int, "contingency_table": [[int]]},
    "fine":   {"chi2": float, "p_value": float, "cramers_v": float, "dof": int, "contingency_table": [[int]]},
    "direction": {
        "dpo_syntax_runtime_prop": float,
        "rl_syntax_runtime_prop": float,
        "direction_satisfied": bool,  # dpo_sr_prop > rl_sr_prop
    },
    "gate_result": {
        "cramers_v_threshold": 0.03,
        "cramers_v_actual": float,   # from fine level
        "p_value_threshold": 0.05,
        "p_value_actual": float,     # from fine level
        "gate_pass": bool,
    }
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Analyzer | Implement all analysis functions + save_outputs in analyze.py |

---

## A-7 through A-10: Visualization & Orchestration [Complexity: 36, Budget: 1/5]

### API Signatures

```python
# visualize.py
def plot_gate_metrics(metrics: dict, config: ExperimentConfig) -> None:
    """Side-by-side Cramér's V (coarse vs fine) with threshold line. → figures/gate_metrics.png"""
    ...

def plot_error_heatmap(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    cause_labels: List[str],
    config: ExperimentConfig,
) -> None:
    """2xK seaborn heatmap, proportion within model, annotated counts. → figures/error_heatmap.png"""
    ...

def plot_cramers_v_persistence(metrics: dict, config: ExperimentConfig) -> None:
    """V values at 3-tier and 19-cause with threshold line. → figures/cramers_v_persistence.png"""
    ...

def plot_error_proportions(metrics: dict, config: ExperimentConfig) -> None:
    """Grouped bar: DPO vs RL proportions by coarse category. → figures/error_proportions.png"""
    ...

def plot_finegrained_distribution(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    config: ExperimentConfig,
) -> None:
    """Stacked bar: 19-cause distribution per model grouped by coarse. → figures/finegrained_distribution.png"""
    ...

def generate_all_figures(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    metrics: dict,
    cause_labels: List[str],
    config: ExperimentConfig,
) -> None:
    """Run all 5 plot functions."""
    ...

# run_experiment.py
def main() -> None:
    """Orchestrate: load → classify → analyze → visualize → print gate."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | Visualization + main | Implement all plot functions and run_experiment.py main() |

---

## Summary: Subtask Budget

| ID | File | Description |
|----|------|-------------|
| L-1-1 | config.py | ExperimentConfig dataclass |
| L-2-1 | data_loader.py | load_he1_results, extract_failures, load_he1_metrics |
| L-3-1 | classifier.py | classify_error_coarse/fine/llmfix + classify_batch + taxonomy constants |
| L-5-1 | analyze.py | build_contingency_coarse/fine, chi_square_test, cramers_v, check_direction, run_analysis, save_outputs |
| L-10-1 | visualize.py + run_experiment.py | All 5 plot functions + main() |

**Total**: 5/5 subtasks used
