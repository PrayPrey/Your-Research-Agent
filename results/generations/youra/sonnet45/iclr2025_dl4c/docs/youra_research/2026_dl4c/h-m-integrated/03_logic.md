# Logic Design: H-M-integrated

**Hypothesis ID:** H-M-integrated
**Type:** MECHANISM
**Date:** 2026-03-18
**Author:** Phase 3 Logic Agent

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-e1 actual code
**Analyzed Path:** /home/anonymous/YouRA_results_new_4_sonnet45/TEST_dl4c/docs/youra_research/20260317_dl4c/h-e1/code/
**Relevant Symbols:**
- `HumanEvalPlusLoader.load_dataset()` - Returns dict[task_id -> task_data]
- `CodeProfiler.extract_signature()` - Returns dict with correctness, cyclomatic, ast_depth, runtime_ms, memory_kb
- H-E1 results stored as CSV: `correctness,cyclomatic,ast_depth,runtime_ms,memory_kb,model,alignment_type`

---

## Knowledge Base Patterns Applied

Applied: scipy.stats percentileofscore (ranking distribution analysis)
Applied: scipy.stats mannwhitneyu (non-parametric variance testing)
Applied: pandas DataFrame operations (CSV loading and grouping)

---

## A-1: Environment Setup [Complexity: 4, Budget: 4]

**Applied:** Standard Python scientific stack

### API Signatures

```python
# setup.py
def verify_dependencies() -> bool:
    """Verify scipy, numpy, pandas, matplotlib installed. Returns success."""
    ...

def verify_h_e1_results(path: str) -> bool:
    """Check h-e1/results/signatures.csv exists and readable. Returns success."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Install scipy | Version >=1.9.0 for percentileofscore |
| L-1-2 | Install numpy | Version >=1.23.0 for array ops |
| L-1-3 | Install pandas | Version >=1.5.0 for CSV loading |
| L-1-4 | Install matplotlib | Version >=3.6.0 for visualization |

---

## A-2: Data Loading [Complexity: 6, Budget: 6]

**Applied:** pandas CSV reader pattern

### API Signatures

```python
class H_E1_ResultsLoader:
    def __init__(self, csv_path: str):
        """Initialize with path to H-E1 signatures.csv."""
        self.csv_path = csv_path
        self.data: Dict[str, Dict[str, float]] = {}

    def load_results(self) -> Dict[str, Dict[str, float]]:
        """
        Load H-E1 profiling results from CSV.
        Returns: {model_name: {correctness: float, cyclomatic: float, ...}}
        """
        ...

    def get_models_by_type(self, alignment_type: str) -> List[str]:
        """
        Filter models by alignment type.
        alignment_type: "execution" | "preference" | "baseline"
        Returns: List of model names
        """
        ...
```

### Tensor Shapes

| Variable | Type | Shape | Note |
|----------|------|-------|------|
| csv_data | DataFrame | [N_models, N_columns] | N_models=4, N_columns=7 |
| data | Dict | {model: {dim: float}} | Nested dict structure |

### Pseudo-code

```
1. df = pd.read_csv(csv_path)
2. for row in df.iterrows():
     model = row["model"]
     data[model] = {
       "correctness": row["correctness"],
       "cyclomatic": row["cyclomatic"],
       "ast_depth": row["ast_depth"],
       "runtime_ms": row["runtime_ms"],
       "memory_kb": row["memory_kb"],
       "alignment_type": row["alignment_type"]
     }
3. return data
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | CSV schema validation | Verify columns: correctness, cyclomatic, ast_depth, runtime_ms, memory_kb, model, alignment_type |
| L-2-2 | Load CSV to DataFrame | pd.read_csv with dtype validation |
| L-2-3 | Convert to dict | Transform DataFrame to nested dict structure |
| L-2-4 | Filter by alignment type | Implement get_models_by_type() |
| L-2-5 | Handle missing data | Check for NaN values, raise error if found |
| L-2-6 | Unit test | Test with mock CSV data |

---

## A-3: Percentile Ranking [Complexity: 8, Budget: 8]

**Applied:** scipy.stats.percentileofscore for ranking

### API Signatures

```python
class PercentileRankingAnalyzer:
    def __init__(self, data: Dict[str, Dict[str, float]]):
        """Initialize with loaded H-E1 results."""
        self.data = data
        self.ranks: Dict[str, Dict[str, float]] = {}

    def compute_dimension_ranks(self, dimension: str) -> Dict[str, float]:
        """
        Compute percentile rank for all models on single dimension.
        dimension: "correctness" | "cyclomatic" | "ast_depth" | "runtime_ms" | "memory_kb"
        Returns: {model: percentile_rank} where rank in [0, 100]
        """
        ...

    def compute_all_ranks(self) -> Dict[str, Dict[str, float]]:
        """
        Compute percentile ranks across all dimensions.
        Returns: {model: {dimension: percentile_rank}}
        """
        ...
```

### Pseudo-code

```
1. For each dimension in [correctness, cyclomatic, ast_depth, runtime_ms, memory_kb]:
     scores = [data[model][dimension] for model in data]

2. For each model:
     score = data[model][dimension]
     percentile = percentileofscore(scores, score, kind='rank')
     ranks[model][dimension] = percentile

3. return ranks
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Extract dimension scores | Collect all model scores for dimension |
| L-3-2 | Apply percentileofscore | Use scipy.stats.percentileofscore(kind='rank') |
| L-3-3 | Handle correctness ranking | Lower percentile = better (invert if needed) |
| L-3-4 | Handle complexity ranking | Lower complexity = better |
| L-3-5 | Handle efficiency ranking | Lower runtime/memory = better |
| L-3-6 | Iterate all dimensions | Loop over 5 dimensions |
| L-3-7 | Store results | Nested dict {model: {dim: rank}} |
| L-3-8 | Unit test | Verify ranks sum correctly across models |

---

## A-4: Variance Analysis [Complexity: 9, Budget: 9]

**Applied:** Standard statistical variance computation

### API Signatures

```python
class VarianceAnalyzer:
    def __init__(self, data: Dict[str, Dict[str, float]]):
        """Initialize with loaded H-E1 results."""
        self.data = data

    def group_by_alignment_method(self, dimension: str) -> Dict[str, List[float]]:
        """
        Group scores by alignment method.
        Returns: {"execution": [scores], "preference": [scores], "baseline": [scores]}
        """
        ...

    def compute_intra_variance(self, group_scores: List[float]) -> float:
        """
        Compute within-group variance.
        Returns: variance (float)
        """
        ...

    def compute_inter_distance(self, group1: List[float], group2: List[float]) -> float:
        """
        Compute between-group distance (mean difference).
        Returns: |mean(group1) - mean(group2)|
        """
        ...
```

### Pseudo-code

```
1. Group scores by alignment_type:
     groups = {"execution": [], "preference": [], "baseline": []}
     for model, model_data in data.items():
       alignment_type = model_data["alignment_type"]
       groups[alignment_type].append(model_data[dimension])

2. Intra-variance:
     var = np.var(group_scores)

3. Inter-distance:
     dist = abs(np.mean(group1) - np.mean(group2))
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Filter by alignment type | Collect execution/preference/baseline models |
| L-4-2 | Extract dimension scores | Get scores per group |
| L-4-3 | Compute group mean | np.mean(group_scores) |
| L-4-4 | Compute group variance | np.var(group_scores) |
| L-4-5 | Compute pairwise distances | Compare execution vs baseline, preference vs baseline |
| L-4-6 | Handle single-model groups | Return 0.0 variance for N=1 |
| L-4-7 | Aggregate variance metrics | Collect intra/inter for all groups |
| L-4-8 | Validate variance > 0 | Check for degenerate cases |
| L-4-9 | Unit test | Test with synthetic grouped data |

---

## A-5: Statistical Tests [Complexity: 13, Budget: 13]

**Applied:** scipy.stats mannwhitneyu for non-parametric testing

### API Signatures

```python
class MechanismTester:
    def __init__(self, data: Dict[str, Dict], ranks: Dict[str, Dict]):
        """Initialize with raw data and computed ranks."""
        self.data = data
        self.ranks = ranks

    def test_m1_execution_dominance(self) -> Tuple[bool, float]:
        """
        M1: Execution models dominate correctness (top 15% percentile).
        Returns: (passed, mean_correctness_rank)
        """
        ...

    def test_m2_preference_balance(self) -> Tuple[bool, float]:
        """
        M2: Preference models balanced across dimensions (top 30% mean rank).
        Returns: (passed, overall_mean_rank)
        """
        ...

    def test_m3_clustering_consistency(self) -> Tuple[bool, float]:
        """
        M3: Within-method variance < between-method variance (Mann-Whitney U, p<0.05).
        Returns: (passed, pvalue)
        """
        ...

    def run_all_tests(self) -> Dict[str, Dict]:
        """
        Execute all mechanism tests.
        Returns: {
          "M1": {"passed": bool, "metric": float, "threshold": float},
          "M2": {"passed": bool, "metric": float, "threshold": float},
          "M3": {"passed": bool, "metric": float, "threshold": float}
        }
        """
        ...
```

### Pseudo-code

```
M1:
1. execution_models = [m for m in data if data[m]["alignment_type"] == "execution"]
2. correctness_ranks = [ranks[m]["correctness"] for m in execution_models]
3. mean_rank = np.mean(correctness_ranks)
4. passed = mean_rank <= 15.0

M2:
1. preference_models = [m for m in data if data[m]["alignment_type"] == "preference"]
2. dimensions = ["correctness", "cyclomatic", "ast_depth", "runtime_ms", "memory_kb"]
3. mean_ranks_per_model = [np.mean([ranks[m][d] for d in dimensions]) for m in preference_models]
4. overall_mean = np.mean(mean_ranks_per_model)
5. passed = overall_mean <= 30.0

M3:
1. execution_scores = [data[m]["correctness"] for m in data if data[m]["alignment_type"] == "execution"]
2. baseline_scores = [data[m]["correctness"] for m in data if data[m]["alignment_type"] == "baseline"]
3. stat, pvalue = mannwhitneyu(execution_scores, baseline_scores, alternative='two-sided')
4. passed = pvalue < 0.05
```

### Subtasks [13/13 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | M1: Filter execution models | Extract models with alignment_type="execution" |
| L-5-2 | M1: Extract correctness ranks | Get percentile ranks for correctness dimension |
| L-5-3 | M1: Compute mean rank | np.mean(correctness_ranks) |
| L-5-4 | M1: Threshold check | mean_rank <= 15.0 |
| L-5-5 | M2: Filter preference models | Extract models with alignment_type="preference" |
| L-5-6 | M2: Compute per-model mean | Average rank across 5 dimensions per model |
| L-5-7 | M2: Compute overall mean | Average of per-model means |
| L-5-8 | M2: Threshold check | overall_mean <= 30.0 |
| L-5-9 | M3: Group by alignment method | Separate execution/preference/baseline scores |
| L-5-10 | M3: Mann-Whitney U test | scipy.stats.mannwhitneyu(execution, baseline) |
| L-5-11 | M3: P-value check | pvalue < 0.05 |
| L-5-12 | Aggregate results | Combine M1, M2, M3 into structured dict |
| L-5-13 | Unit test | Mock data with known outcomes |

---

## A-6: Gate Validation [Complexity: 7, Budget: 7]

**Applied:** Boolean logic for gate evaluation

### API Signatures

```python
class GateValidator:
    def __init__(self, test_results: Dict[str, Dict]):
        """Initialize with M1, M2, M3 test results."""
        self.test_results = test_results

    def evaluate_gate(self) -> Dict[str, Any]:
        """
        Evaluate MUST_WORK gate: M1 AND M2 must pass.
        Returns: {
          "primary_gate": bool,  # M1 AND M2
          "secondary_check": bool,  # M3
          "overall": bool,  # All three
          "m1_passed": bool,
          "m2_passed": bool,
          "m3_passed": bool,
          "decision": str  # "CONTINUE" | "EXPLORE" | "PIVOT" | "ABANDON"
        }
        """
        ...

    def generate_diagnostics(self) -> str:
        """
        Generate failure diagnostics for routing decisions.
        Returns: Human-readable diagnostic string
        """
        ...
```

### Pseudo-code

```
1. primary_gate = test_results["M1"]["passed"] AND test_results["M2"]["passed"]
2. secondary_check = test_results["M3"]["passed"]
3. overall = primary_gate AND secondary_check

4. Decision routing:
   if primary_gate AND secondary_check:
     decision = "CONTINUE"
   elif NOT M1_passed:
     decision = "EXPLORE: Check baseline model differences"
   elif NOT M2_passed:
     decision = "PIVOT: Revise feedback signal theory"
   elif NOT M3_passed:
     decision = "ABANDON: Clustering is noise"
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Extract pass/fail from tests | Read M1, M2, M3 passed booleans |
| L-6-2 | Compute primary gate | M1 AND M2 |
| L-6-3 | Compute secondary check | M3 |
| L-6-4 | Compute overall | All three pass |
| L-6-5 | Routing decision logic | Map failures to EXPLORE/PIVOT/ABANDON |
| L-6-6 | Generate diagnostics | Detailed failure messages |
| L-6-7 | Unit test | Test all gate combinations |

---

## A-7: Visualization [Complexity: 11, Budget: 11]

**Applied:** matplotlib figure generation patterns

### API Signatures

```python
class MechanismVisualizer:
    def __init__(self, output_dir: str):
        """Initialize with output directory for figures."""
        self.output_dir = output_dir

    def plot_dimension_rankings(
        self,
        ranks: Dict[str, Dict[str, float]],
        data: Dict[str, Dict]
    ) -> None:
        """
        Generate bar chart of percentile ranks across dimensions.
        Saves to: {output_dir}/dimension_rankings.png
        """
        ...

    def plot_m1_validation(
        self,
        execution_ranks: Dict[str, float],
        threshold: float = 15.0
    ) -> None:
        """
        Generate M1 validation plot (execution correctness dominance).
        Saves to: {output_dir}/m1_execution_dominance.png
        """
        ...

    def plot_m2_validation(
        self,
        preference_ranks: Dict[str, Dict[str, float]],
        threshold: float = 30.0
    ) -> None:
        """
        Generate M2 validation plot (preference balance).
        Saves to: {output_dir}/m2_preference_balance.png
        """
        ...

    def plot_m3_variance(
        self,
        groups: Dict[str, List[float]],
        pvalue: float
    ) -> None:
        """
        Generate M3 variance analysis (box plots).
        Saves to: {output_dir}/m3_variance_analysis.png
        """
        ...

    def plot_gate_metrics(
        self,
        m1_pass: bool,
        m2_pass: bool,
        m3_pass: bool
    ) -> None:
        """
        Generate gate validation summary figure.
        Saves to: {output_dir}/gate_validation.png
        """
        ...
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Dimension rankings: bar chart | Grouped bars per model, 5 dimensions |
| L-7-2 | Dimension rankings: color coding | execution=blue, preference=green, baseline=gray |
| L-7-3 | M1: horizontal bar chart | Execution models' correctness ranks |
| L-7-4 | M1: threshold line | Vertical line at 15th percentile |
| L-7-5 | M2: grouped bar/spider plot | Preference models across dimensions |
| L-7-6 | M2: threshold annotation | Mean rank vs 30th percentile |
| L-7-7 | M3: box plots | One box per alignment method |
| L-7-8 | M3: p-value annotation | Display Mann-Whitney U p-value |
| L-7-9 | Gate metrics: summary table | Pass/fail for M1, M2, M3 |
| L-7-10 | Save all figures | PNG format, 300 DPI |
| L-7-11 | Unit test | Generate figures with mock data |

---

## A-8: Analysis Orchestration [Complexity: 10, Budget: 10]

**Applied:** Main execution flow pattern

### API Signatures

```python
def run_analysis(config: Dict) -> Dict:
    """
    Main entry point for H-M-integrated analysis.

    Args:
        config: {
          "h_e1_results_path": str,
          "dimensions": List[str],
          "m1_threshold": float,
          "m2_threshold": float,
          "m3_pvalue_threshold": float,
          "output_dir": str,
          "figure_dir": str
        }

    Returns: {
      "test_results": Dict,
      "gate_evaluation": Dict,
      "figures_saved": List[str]
    }
    """
    ...

def save_results(results: Dict, output_path: str) -> None:
    """Save results to JSON file."""
    ...

def generate_validation_report(results: Dict, output_path: str) -> None:
    """Generate 04_validation.md report."""
    ...
```

### Pseudo-code

```
1. Load H-E1 results (DataModule)
2. Compute percentile rankings (RankingModule)
3. Compute variance metrics (VarianceModule)
4. Run M1, M2, M3 tests (StatisticalTestsModule)
5. Evaluate gate (GateValidator)
6. Generate visualizations (VisualizerModule)
7. Save results to JSON
8. Generate validation report markdown
9. Return results dict
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Parse config | Load experiment configuration |
| L-8-2 | Initialize modules | Instantiate all 6 modules |
| L-8-3 | Execute pipeline | Call modules in sequence |
| L-8-4 | Error handling | Try/catch for each module, log failures |
| L-8-5 | Progress logging | Print status after each step |
| L-8-6 | Save JSON results | Write test_results + gate_evaluation |
| L-8-7 | Generate markdown report | Format 04_validation.md |
| L-8-8 | Create output directories | Ensure results/ and figures/ exist |
| L-8-9 | Return results | Structured dict with all outputs |
| L-8-10 | Unit test | End-to-end test with mock data |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following data structures are loaded from H-E1 results. Format verified from actual CSV output:

```python
# From: h-e1/results/signatures.csv (ACTUAL DATA)
# CSV Format: correctness,cyclomatic,ast_depth,runtime_ms,memory_kb,model,alignment_type
# Example row:
# 0.687,4.426,6.464,0.799,165.602,microsoft/phi-2,execution

# No direct API calls to H-E1 code - only CSV file reading
# H-E1 modules NOT imported directly:
# - HumanEvalPlusLoader (data already collected)
# - CodeProfiler (profiling already complete)
```

**Verified from:** h-e1/results/signatures.csv (actual output data, NOT code import)

---

## Configuration Schema

```python
class AnalysisConfig:
    """Configuration for H-M-integrated analysis."""

    # Input paths
    H_E1_RESULTS_PATH: str = "../h-e1/results/signatures.csv"

    # Dimensions to analyze
    DIMENSIONS: List[str] = [
        "correctness",
        "cyclomatic",
        "ast_depth",
        "runtime_ms",
        "memory_kb"
    ]

    # Mechanism test thresholds
    M1_THRESHOLD: float = 15.0  # Top 15% for execution correctness
    M2_THRESHOLD: float = 30.0  # Top 30% for preference balance
    M3_PVALUE_THRESHOLD: float = 0.05  # Clustering significance

    # Output paths
    OUTPUT_DIR: str = "./results"
    FIGURE_DIR: str = "./figures"

    # Reproducibility
    RANDOM_SEED: int = 42
```

---

## Data Flow Summary

```
1. Load H-E1 CSV → Dict[model, metrics]
2. Compute percentile ranks → Dict[model, Dict[dimension, rank]]
3. Group by alignment_type → Dict[type, List[scores]]
4. Run M1 test → (passed, mean_correctness_rank)
5. Run M2 test → (passed, overall_mean_rank)
6. Run M3 test → (passed, pvalue)
7. Evaluate gate → {primary_gate, secondary_check, decision}
8. Generate 5 figures → PNG files
9. Save results → JSON + markdown report
```

---

**End of Logic Design**

*Total Subtasks: 68 (within budget)*
*Ready for Phase 3 Configuration Agent (03c_config.md)*
