# Architecture: H-M3 - LlmFix 19-Cause Fine-Grained Error Taxonomy Analysis

**Hypothesis:** DPO preference optimization concentrates failures in execution errors at fine-grained LlmFix 19-cause level (Cramér's V > 0.03)
**Type:** MECHANISM | **Gate:** SHOULD_WORK

Applied: modular-analysis-pipeline

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1 + h-m2)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260323_dl4c/h-e1/code/` and `docs/youra_research/20260323_dl4c/h-m2/code/`
**Findings**: H-E1 has `classify_error()` returning coarse 3-tier labels (syntax/runtime/assertion/other) via string matching on error_lower. `run_analysis()` accepts rl_results/dpo_results lists and returns metrics dict saved to outputs/metrics.json. H-M3 extends classification to 19-cause without changing the structural pipeline.

---

## File Organization

- `code/config.py` - ExperimentConfig dataclass
- `code/data_loader.py` - Load H-E1 outputs (no new generation)
- `code/classifier.py` - LlmFix 19-cause taxonomy classifier
- `code/analyze.py` - Dual-granularity statistical analysis
- `code/visualize.py` - 5 figures (heatmap, persistence, proportions, etc.)
- `code/run_experiment.py` - Orchestration entry point
- `code/outputs/` - metrics.json, experiment_results.json, classification_data.csv
- `code/figures/` - gate_metrics.png, error_heatmap.png, cramers_v_persistence.png, error_proportions.png, finegrained_distribution.png

---

## Module Definitions

### ExperimentConfig (`code/config.py`)

**Dependencies**: None

```python
@dataclass
class ExperimentConfig:
    # Paths to H-E1 outputs
    he1_results_path: str = "../h-e1/code/outputs/experiment_results.json"
    he1_metrics_path: str = "../h-e1/code/outputs/metrics.json"

    # Output paths
    output_dir: str = "outputs"
    figures_dir: str = "figures"

    # Statistical thresholds (H-M3 gate)
    chi2_p_threshold: float = 0.05
    cramers_v_threshold_fine: float = 0.03   # Fine-grained gate
    cramers_v_threshold_coarse: float = 0.05  # Coarse validation

    # Pseudocount for sparse cells
    pseudocount: float = 0.5

    # Reproducibility
    seed: int = 42

CONFIG = ExperimentConfig()
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: ExperimentConfig

```python
def load_he1_results(config: ExperimentConfig) -> Tuple[List[dict], List[dict]]:
    """Load H-E1 experiment_results.json, return (rl_results, dpo_results).
    Each result dict: {sample_id, model, problem_id, status, error_trace, output}
    """
    ...

def extract_failures(results: List[dict]) -> List[dict]:
    """Filter to failed samples only (status == 'fail')."""
    ...

def load_he1_metrics(config: ExperimentConfig) -> dict:
    """Load H-E1 metrics.json for validation comparison."""
    ...
```

---

### LlmFixClassifier (`code/classifier.py`)

**Dependencies**: None (pure string parsing)

```python
# LlmFix 19-cause taxonomy constants
LLMFIX_TAXONOMY: Dict[str, List[str]] = {
    "syntax": ["indentation_error", "syntax_error", "missing_import"],
    "runtime": ["name_error", "type_error", "attribute_error", "index_error",
                "key_error", "value_error", "zero_division", "recursion_error",
                "timeout", "memory_error"],
    "assertion": ["wrong_output", "partial_output", "missing_output",
                  "wrong_type", "off_by_one", "boundary_error"],
}

ALL_FINE_CAUSES: List[str] = [c for causes in LLMFIX_TAXONOMY.values() for c in causes]

def classify_error_coarse(error_trace: Optional[str]) -> str:
    """Returns: 'syntax' | 'runtime' | 'assertion' | 'other' | 'pass'"""
    ...

def classify_error_fine(error_trace: Optional[str], coarse: str) -> str:
    """Returns one of 19 LlmFix cause labels or 'unknown'."""
    ...

def classify_error_llmfix(error_trace: Optional[str], output: Optional[str] = None) -> Tuple[str, str]:
    """Returns (coarse_category, fine_cause) for dual-granularity classification."""
    ...

def classify_batch(results: List[dict]) -> List[dict]:
    """Add 'coarse_category' and 'fine_cause' keys to each result dict."""
    ...
```

---

### Analyzer (`code/analyze.py`)

**Dependencies**: ExperimentConfig, LlmFixClassifier

```python
def build_contingency_coarse(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    pseudocount: float = 0.5,
) -> np.ndarray:
    """Build 2x3 contingency table (model × {syntax, runtime, assertion})."""
    ...

def build_contingency_fine(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    pseudocount: float = 0.5,
) -> Tuple[np.ndarray, List[str]]:
    """Build 2xK contingency table (model × fine causes). Returns (table, cause_labels)."""
    ...

def chi_square_test(contingency: np.ndarray) -> Tuple[float, float, int, np.ndarray]:
    """Returns (chi2, p_value, dof, expected)."""
    ...

def cramers_v(contingency: np.ndarray) -> float:
    """Compute Cramér's V from contingency table."""
    ...

def check_direction(rl_classified: List[dict], dpo_classified: List[dict]) -> Tuple[float, float, bool]:
    """Returns (rl_sr_prop, dpo_sr_prop, direction_satisfied).
    direction_satisfied = P(syntax+runtime|DPO) > P(syntax+runtime|RL)
    """
    ...

def compute_descriptive_stats(classified: List[dict]) -> dict:
    """Returns counts and proportions by coarse and fine category."""
    ...

def run_analysis(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    config: ExperimentConfig,
) -> dict:
    """Full dual-granularity analysis. Saves outputs/metrics.json.
    Returns metrics dict with keys: coarse, fine, direction, gate_result.
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

---

### Visualizer (`code/visualize.py`)

**Dependencies**: ExperimentConfig, Analyzer outputs

```python
def plot_gate_metrics(metrics: dict, config: ExperimentConfig) -> None:
    """Side-by-side Cramér's V bars (coarse vs fine) with threshold line.
    Saves: figures/gate_metrics.png
    """
    ...

def plot_error_heatmap(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    cause_labels: List[str],
    config: ExperimentConfig,
) -> None:
    """2x19 seaborn heatmap, proportions within model, annotated counts.
    Saves: figures/error_heatmap.png
    """
    ...

def plot_cramers_v_persistence(metrics: dict, config: ExperimentConfig) -> None:
    """Bar/line chart: V values at 3-tier and 19-cause with threshold line.
    Saves: figures/cramers_v_persistence.png
    """
    ...

def plot_error_proportions(metrics: dict, config: ExperimentConfig) -> None:
    """Grouped bar: DPO vs RL proportions by coarse category + combined syntax+runtime.
    Saves: figures/error_proportions.png
    """
    ...

def plot_finegrained_distribution(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    config: ExperimentConfig,
) -> None:
    """Stacked bar: 19-cause distribution per model, grouped by coarse category.
    Saves: figures/finegrained_distribution.png
    """
    ...

def generate_all_figures(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    metrics: dict,
    cause_labels: List[str],
    config: ExperimentConfig,
) -> None:
    """Run all plot functions."""
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: DataLoader, LlmFixClassifier, Analyzer, Visualizer, ExperimentConfig

```python
def main() -> None:
    """Orchestrate full H-M3 pipeline:
    1. Load H-E1 results
    2. Classify at coarse + fine granularity
    3. Run dual-granularity statistical analysis
    4. Generate all figures
    5. Print gate result
    """
    ...
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| H-E1 results data | File path: `../h-e1/code/outputs/experiment_results.json` | `h-e1/code/outputs/experiment_results.json` |
| H-E1 metrics | File path: `../h-e1/code/outputs/metrics.json` | `h-e1/code/outputs/metrics.json` |
| classify_error (coarse logic) | Reimplemented in `classifier.py` | `h-e1/code/analyze.py` (reference) |
| ExperimentConfig pattern | Reimplemented in `config.py` | `h-e1/code/config.py` (pattern) |

**Verified from**: `docs/youra_research/20260323_dl4c/h-e1/code/` (actual implementation)

**Note**: H-M3 does NOT import directly from h-e1 code. It reloads H-E1 output JSON files and reimplements classifier logic extended to 19 causes. The coarse `classify_error()` pattern from h-e1 (string matching on `error_lower` against SYNTAX_ERRORS/RUNTIME_ERRORS/ASSERTION_ERRORS lists) is reproduced and extended.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment & Config | Setup project structure, config.py with H-E1 paths and thresholds | 6 | 1+2+1+2 |
| A-2 | Data Loader | Load H-E1 experiment_results.json, extract RL/DPO failures, validate counts | 8 | 2+2+2+2 |
| A-3 | LlmFix Classifier (Coarse) | Reimplement 3-tier classify_error_coarse() from H-E1 pattern | 7 | 2+2+2+1 |
| A-4 | LlmFix Classifier (Fine) | Implement 19-cause classify_error_fine() and classify_error_llmfix() | 14 | 4+3+4+3 |
| A-5 | Contingency Tables | Build 2x3 and 2x19 contingency tables with pseudocount handling | 10 | 3+2+3+2 |
| A-6 | Statistical Analysis | Chi-square + Cramér's V at both levels, direction check, gate eval | 13 | 3+3+4+3 |
| A-7 | Output Saving | Save metrics.json, experiment_results.json, classification_data.csv | 7 | 2+2+1+2 |
| A-8 | Gate Metrics Figure | Plot Cramér's V coarse vs fine with threshold line (P0 required) | 8 | 2+2+2+2 |
| A-9 | Visualization Suite | error_heatmap, cramers_v_persistence, error_proportions, finegrained_distribution | 12 | 3+2+4+3 |
| A-10 | Orchestration | run_experiment.py main() integrating all modules, error handling | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-5, A-6, A-9, A-10], Low(4-8): [A-1, A-2, A-3, A-7, A-8]
