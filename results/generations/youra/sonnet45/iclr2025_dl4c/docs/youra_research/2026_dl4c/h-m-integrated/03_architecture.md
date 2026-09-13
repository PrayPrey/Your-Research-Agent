# System Architecture: H-M-integrated

**Hypothesis ID:** H-M-integrated
**Type:** MECHANISM
**Date:** 2026-03-18
**Author:** Phase 3 Architecture Agent

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns found from H-E1 base code
**Analyzed Path:** /home/anonymous/YouRA_results_new_4_sonnet45/TEST_dl4c/docs/youra_research/20260317_dl4c/h-e1/code/
**Findings:** Profiling infrastructure (correctness, cyclomatic, AST depth, runtime, memory). Results stored in CSV format with alignment_type labels. Data loader and profiler modules reusable.

---

## Knowledge Base Patterns Applied

Applied: scipy.stats percentile ranking pattern (percentileofscore, mannwhitneyu)

---

## Architecture Overview

**Scope:** Statistical analysis pipeline for mechanistic validation of alignment method signatures.
**Pattern:** Post-hoc analysis (load H-E1 results → ranking → variance testing → gate validation).
**Infrastructure:** LIGHT tier - hardcoded config, print logging, CSV output.

**File Organization:**
```
h-m-integrated/code/
├── config.py              # Hardcoded configuration
├── data_loader.py         # Load H-E1 profiling results
├── ranking_analyzer.py    # Percentile ranking computation
├── variance_analyzer.py   # Within/between-method variance
├── statistical_tests.py   # M1, M2, M3 hypothesis tests
├── visualizer.py          # 4 figures + gate metrics
└── run_analysis.py        # Entry point
```

---

## Module Specifications

### ConfigModule (`config.py`)

**Dependencies:** None

```python
class AnalysisConfig:
    H_E1_RESULTS_PATH: str = "../h-e1/results/signatures.csv"
    DIMENSIONS: list[str] = ["correctness", "cyclomatic", "ast_depth", "runtime_ms", "memory_kb"]
    M1_THRESHOLD: float = 15.0
    M2_THRESHOLD: float = 30.0
    M3_PVALUE_THRESHOLD: float = 0.05
    RANDOM_SEED: int = 42
    OUTPUT_DIR: str = "./results"
    FIGURE_DIR: str = "./figures"
```

---

### DataModule (`data_loader.py`)

**Dependencies:** pandas, config

```python
class H_E1_ResultsLoader:
    def __init__(self, csv_path: str): ...
    def load_results(self) -> dict[str, dict]: ...
    def get_models_by_type(self, alignment_type: str) -> list[str]: ...
```

---

### RankingModule (`ranking_analyzer.py`)

**Dependencies:** scipy.stats, numpy, DataModule

```python
class PercentileRankingAnalyzer:
    def __init__(self, data: dict[str, dict]): ...
    def compute_dimension_ranks(self, dimension: str) -> dict[str, float]: ...
    def compute_all_ranks(self) -> dict[str, dict[str, float]]: ...
```

---

### VarianceModule (`variance_analyzer.py`)

**Dependencies:** scipy.stats, numpy, DataModule

```python
class VarianceAnalyzer:
    def __init__(self, data: dict[str, dict]): ...
    def group_by_alignment_method(self, dimension: str) -> dict[str, list[float]]: ...
    def compute_intra_variance(self, group_scores: list[float]) -> float: ...
    def compute_inter_distance(self, group1: list[float], group2: list[float]) -> float: ...
```

---

### StatisticalTestsModule (`statistical_tests.py`)

**Dependencies:** scipy.stats, numpy, RankingModule, VarianceModule

```python
class MechanismTester:
    def __init__(self, data: dict, ranks: dict): ...
    def test_m1_execution_dominance(self) -> tuple[bool, float]: ...
    def test_m2_preference_balance(self) -> tuple[bool, float]: ...
    def test_m3_clustering_consistency(self) -> tuple[bool, float]: ...
    def run_all_tests(self) -> dict: ...
```

---

### VisualizerModule (`visualizer.py`)

**Dependencies:** matplotlib, pandas, StatisticalTestsModule

```python
class MechanismVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_dimension_rankings(self, ranks: dict, data: dict) -> None: ...
    def plot_m1_validation(self, execution_ranks: dict, threshold: float) -> None: ...
    def plot_m2_validation(self, preference_ranks: dict, threshold: float) -> None: ...
    def plot_m3_variance(self, groups: dict, pvalue: float) -> None: ...
    def plot_gate_metrics(self, m1_pass: bool, m2_pass: bool, m3_pass: bool) -> None: ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| CodeProfiler | `from h_e1.code.profiler import CodeProfiler` | h-e1/code/profiler.py |
| HumanEvalPlusLoader | `from h_e1.code.data_loader import HumanEvalPlusLoader` | h-e1/code/data_loader.py |

**Note:** These modules are NOT directly imported. H-M-integrated loads pre-computed results from `h-e1/results/signatures.csv`.

**Verified from:** h-e1/code/ (actual implementation)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Install scipy, numpy, pandas, matplotlib. Verify H-E1 results accessible. | 4 | 1+1+1+1 |
| A-2 | Data Loading | Implement H_E1_ResultsLoader. Load signatures.csv. Parse alignment types. | 6 | 2+2+1+1 |
| A-3 | Percentile Ranking | Implement PercentileRankingAnalyzer. Compute ranks for all dimensions. | 8 | 3+2+2+1 |
| A-4 | Variance Analysis | Implement VarianceAnalyzer. Group by alignment method. Compute intra/inter variance. | 9 | 3+3+2+1 |
| A-5 | Statistical Tests | Implement M1, M2, M3 hypothesis tests. Mann-Whitney U for M3. | 13 | 4+4+3+2 |
| A-6 | Gate Validation | Evaluate M1 AND M2 gate condition. Log detailed failure diagnostics. | 7 | 2+2+2+1 |
| A-7 | Visualization | Generate 4 mechanism plots + gate metrics figure. | 11 | 3+3+2+3 |
| A-8 | Analysis Orchestration | Implement run_analysis.py. Execute tests, generate report, save results. | 10 | 3+3+2+2 |

**Total Complexity:** 68
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5, A-7, A-8], Low(4-8): [A-1, A-2, A-3, A-6]

---

## Data Flow

```
1. DataModule loads H-E1 signatures.csv
   - 4 models × 5 dimensions
   - Each row: {model, alignment_type, correctness, cyclomatic, ast_depth, runtime_ms, memory_kb}

2. RankingModule computes percentile ranks
   - For each dimension: percentileofscore(all_scores, model_score)
   - Output: {model: {correctness: rank, cyclomatic: rank, ...}}

3. VarianceModule groups by alignment method
   - Execution models: [phi-2]
   - Preference models: [codegen-350M-mono]
   - Baseline models: [codegen-350M-nl, CodeGPT-small-py]

4. StatisticalTestsModule runs M1, M2, M3
   - M1: mean(execution_correctness_ranks) ≤ 15.0
   - M2: mean(preference_all_dimension_ranks) ≤ 30.0
   - M3: mannwhitneyu(execution_scores, baseline_scores) → p < 0.05

5. VisualizerModule generates 5 figures
   - Dimension rankings, M1 plot, M2 plot, M3 variance, gate metrics

6. Save results: {M1: pass/fail, M2: pass/fail, M3: pass/fail, gate: pass/fail}
```

---

## Integration Points

**Input:**
- `h-e1/results/signatures.csv` (profiling results from H-E1)
- `02c_experiment_brief.md` (experiment specification)
- `03_prd.md` (functional requirements)

**Output:**
- `04_validation.md` (Phase 4 validation report)
- `h-m-integrated/code/*.py` (implementation files)
- `h-m-integrated/figures/*.png` (5 visualizations)
- `h-m-integrated/results/mechanism_tests.csv` (M1, M2, M3 results)
- `h-m-integrated/results/gate_validation.json` (gate pass/fail)

**State:**
- `verification_state.yaml` (gate evaluation: M1 AND M2 must pass)

---

## Non-Functional Requirements

### Performance
- No GPU required (statistical analysis only)
- Expected runtime: < 5 minutes (post-hoc analysis)
- Single-threaded execution (small dataset)

### Reproducibility
- Fixed seed: `random.seed(42)`, `np.random.seed(42)`
- Deterministic scipy.stats functions

### Error Handling
- H-E1 results missing: Exit with error message
- Insufficient models per alignment type: Log warning, continue
- Statistical test failures: Log detailed diagnostics

### Logging
- Print statements for progress tracking
- CSV/JSON output for results storage
- No WandB, no structured logging (LIGHT tier)

---

## Validation Checklist

**Pre-execution:**
- [ ] H-E1 validation completed (status = COMPLETED)
- [ ] `h-e1/results/signatures.csv` exists and readable
- [ ] Python packages installed (scipy, numpy, pandas, matplotlib)

**Post-execution:**
- [ ] All 4 models loaded successfully
- [ ] M1, M2, M3 tests computed without error
- [ ] 5 figures saved to `h-m-integrated/figures/`
- [ ] Gate evaluation: M1 AND M2 pass → CONTINUE, either fails → HALT

---

**End of Architecture Document**

*Ready for Phase 3 Logic Design (03b_logic.md)*
