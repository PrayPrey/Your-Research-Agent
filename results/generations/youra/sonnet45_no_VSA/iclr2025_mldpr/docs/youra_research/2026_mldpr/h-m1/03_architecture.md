# System Architecture: H-M1 - Community Engagement Correlation Study

**Date:** 2026-07-12  
**Hypothesis:** H-M1 (MECHANISM - INCREMENTAL)  
**Type:** Observational Correlation Study (GitHub API + Statistical Analysis)  
**Author:** Architecture Agent  
**Status:** DRAFT v1.0  

---

## Applied Patterns

**Applied:** Data Pipeline Pattern (observational correlation analysis)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from base code  
**Analyzed Path:** h-e1/src/  
**Findings:** H-E1 implements modular pipeline with data_collection, feature_engineering, analysis, and visualization modules. H-M1 will adapt this structure by replacing data_collection with GitHub API metrics collection and simplifying feature_engineering to metric merging.

---

## System Overview

H-M1 extends H-E1's observational pipeline to test community engagement correlation:
1. Load DCS_3 Scores (from H-E1 validation results)
2. Collect GitHub Activity Metrics (commits, contributors, issue response via GitHub API)
3. Data Validation and Cleaning (outlier detection, missing value handling)
4. Statistical Analysis (Spearman correlation + partial correlation)
5. Visualization (scatter plots, correlation matrix, comparison charts)

**Technology Stack:**
- Python 3.9+
- GitHub API (`PyGithub`)
- Statistical libraries (`scipy`, `pingouin`, `numpy`, `pandas`)
- Visualization (`matplotlib`, `seaborn`)

---

## Module Structure

### H-E1 Data Loader (`src/data_loading/h_e1_loader.py`)

**Dependencies:** `pandas`

```python
class HE1DataLoader:
    def __init__(self, h_e1_path: str): ...
    
    def load_dcs_scores(self) -> pd.DataFrame: ...
    
    def validate_dcs_data(self, df: pd.DataFrame) -> bool: ...
```

---

### GitHub Metrics Collector (`src/data_collection/github_collector.py`)

**Dependencies:** `PyGithub`, `pandas`, `datetime`

```python
class GitHubMetricsCollector:
    def __init__(self, github_token: str): ...
    
    def collect_commits_per_month(self, repo_id: str, t0: datetime, t90: datetime) -> float: ...
    
    def collect_unique_contributors(self, repo_id: str, commits: List) -> int: ...
    
    def collect_median_issue_response(self, repo_id: str, t0: datetime, t90: datetime) -> Optional[float]: ...
    
    def collect_repository_age(self, repo_id: str, t90: datetime) -> int: ...
    
    def collect_all_metrics(self, repo_list: pd.DataFrame) -> pd.DataFrame: ...
```

---

### Data Validator (`src/preprocessing/validator.py`)

**Dependencies:** `pandas`, `scipy`

```python
class DataValidator:
    def __init__(self, quality_threshold: float = 0.95): ...
    
    def check_completeness(self, df: pd.DataFrame) -> Tuple[int, int]: ...
    
    def detect_outliers(self, df: pd.DataFrame, z_threshold: float = 3.0) -> pd.Series: ...
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame: ...
    
    def export_cleaned_data(self, df: pd.DataFrame, output_path: str) -> None: ...
```

---

### Correlation Analyzer (`src/analysis/correlation_analyzer.py`)

**Dependencies:** `scipy`, `pingouin`, `pandas`, `numpy`

```python
class CorrelationAnalyzer:
    def __init__(self, random_seed: int = 42): ...
    
    def compute_spearman(self, x: pd.Series, y: pd.Series, one_tailed: bool = True) -> Dict: ...
    
    def compute_partial_correlation(self, df: pd.DataFrame, x: str, y: str, covar: str) -> Dict: ...
    
    def bootstrap_confidence_interval(self, x: pd.Series, y: pd.Series, n_iterations: int = 10000) -> Tuple[float, float]: ...
    
    def analyze_all_metrics(self, df: pd.DataFrame) -> Dict: ...
```

---

### Gate Checker (`src/analysis/gate_checker.py`)

**Dependencies:** `pandas`

```python
class GateChecker:
    def __init__(self, primary_threshold: float = 0.30, secondary_threshold: float = 0.25): ...
    
    def check_primary_gate(self, rho: float, p_value: float) -> Dict[str, bool]: ...
    
    def check_secondary_gate(self, partial_rho: float, partial_p: float) -> Dict[str, bool]: ...
    
    def determine_routing(self, results: Dict) -> Dict: ...
```

---

### Visualizer (`src/visualization/plotter.py`)

**Dependencies:** `matplotlib`, `seaborn`, `pandas`

```python
class CorrelationVisualizer:
    def __init__(self, output_dir: str = "figures"): ...
    
    def plot_primary_scatter(self, df: pd.DataFrame, rho: float, p_value: float) -> None: ...
    
    def plot_correlation_matrix(self, df: pd.DataFrame) -> None: ...
    
    def plot_partial_comparison(self, raw_rho: float, partial_rho: float, ci_raw: Tuple, ci_partial: Tuple) -> None: ...
    
    def plot_component_correlations(self, df: pd.DataFrame) -> None: ...
    
    def generate_all_figures(self, df: pd.DataFrame, results: Dict) -> None: ...
```

---

### Pipeline Orchestrator (`src/pipeline.py`)

**Dependencies:** All modules above

```python
class CorrelationPipeline:
    def __init__(self, config: dict): ...
    
    def run_data_loading(self) -> pd.DataFrame: ...
    
    def run_github_collection(self, dcs_df: pd.DataFrame) -> pd.DataFrame: ...
    
    def run_validation(self, merged_df: pd.DataFrame) -> pd.DataFrame: ...
    
    def run_correlation_analysis(self, clean_df: pd.DataFrame) -> Dict: ...
    
    def run_gate_check(self, results: Dict) -> Dict: ...
    
    def run_visualization(self, clean_df: pd.DataFrame, results: Dict) -> None: ...
    
    def run_full_pipeline(self) -> Dict: ...
```

---

## File Organization

```
/workspace/TEST_mldpr/
├── docs/youra_research/h-m1/
│   ├── 02b_verification_plan.md
│   ├── 02c_experiment_brief.md
│   ├── 03_prd.md
│   ├── 03_architecture.md (this file)
│   └── figures/
│       ├── h1_primary_correlation.png
│       ├── correlation_matrix.png
│       ├── partial_correlation_comparison.png
│       └── component_level_correlation.png
├── h-m1/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── data_loading/
│   │   │   ├── __init__.py
│   │   │   └── h_e1_loader.py
│   │   ├── data_collection/
│   │   │   ├── __init__.py
│   │   │   └── github_collector.py
│   │   ├── preprocessing/
│   │   │   ├── __init__.py
│   │   │   └── validator.py
│   │   ├── analysis/
│   │   │   ├── __init__.py
│   │   │   ├── correlation_analyzer.py
│   │   │   └── gate_checker.py
│   │   └── visualization/
│   │       ├── __init__.py
│   │       └── plotter.py
│   ├── data/
│   │   ├── h_e1_dcs_scores.csv (loaded from H-E1)
│   │   ├── github_activity_metrics.csv
│   │   ├── merged_data.csv
│   │   └── activity_metrics_cleaned.csv
│   ├── results/
│   │   ├── correlation_results.csv
│   │   ├── partial_correlation_results.csv
│   │   └── bootstrap_ci.csv
│   ├── figures/
│   │   └── (generated PNG files)
│   ├── logs/
│   │   └── experiment.log
│   ├── config.yaml
│   ├── main.py
│   └── requirements.txt
```

---

## Configuration (`config.yaml`)

```yaml
experiment:
  id: h-m1
  name: Community Engagement Correlation Study
  hypothesis_type: MECHANISM

data_sources:
  h_e1_path: ../h-e1/validation_results.csv
  github_token_env: GITHUB_ACCESS_TOKEN

data_collection:
  target_n: 100
  t0_to_t90_days: 90
  min_issues_for_response_time: 5

validation:
  quality_threshold: 0.95
  outlier_z_threshold: 3.0

analysis:
  random_seed: 42
  primary_gate:
    min_rho: 0.30
    max_p: 0.05
    one_tailed: true
  secondary_gate:
    min_partial_rho: 0.25
    max_p: 0.05
  bootstrap:
    n_iterations: 10000
    confidence_level: 0.95

visualization:
  style: seaborn
  figures_dir: figures/
  dpi: 300
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| DataCollector | `from h_e1.src.data_collection.collector import DataCollector` | `h-e1/src/data_collection/collector.py` |
| FeatureExtractor | `from h_e1.src.feature_engineering.extractor import FeatureExtractor` | `h-e1/src/feature_engineering/extractor.py` |
| DocumentationScorer | `from h_e1.src.feature_engineering.doc_scorer import DocumentationScorer` | `h-e1/src/feature_engineering/doc_scorer.py` |

**Verified from**: h-e1/src/ (actual implementation)

**Note:** H-M1 reuses H-E1's validation results CSV but does NOT import code modules. Only data dependency exists.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | H-E1 Data Integration | Load DCS_3 scores from H-E1 validation results | 6 | Module:2, Deps:1, Algo:1, Integ:2 |
| M-2 | GitHub Metrics Collection | Implement GitHub API data collection (4 metrics) | 14 | Module:4, Deps:3, Algo:3, Integ:4 |
| M-3 | Data Validation Pipeline | Outlier detection, missing value handling, quality gates | 10 | Module:3, Deps:2, Algo:3, Integ:2 |
| M-4 | Correlation Analysis Engine | Spearman, partial correlation, bootstrap CI | 12 | Module:3, Deps:3, Algo:4, Integ:2 |
| M-5 | Gate Check System | Primary/secondary gate validation, routing logic | 8 | Module:2, Deps:1, Algo:3, Integ:2 |
| M-6 | Visualization Suite | 4 required figures (scatter, matrix, comparison, components) | 9 | Module:2, Deps:2, Algo:2, Integ:3 |
| M-7 | Pipeline Orchestration | Integrate all modules with error handling | 11 | Module:3, Deps:2, Algo:2, Integ:4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [M-2], Medium(9-13): [M-3, M-4, M-6, M-7], Low(4-8): [M-1, M-5]

**Total Complexity**: 70 points (MECHANISM/LIGHT tier: target 50-100)

---

## Epic Task Breakdown

### M-1: H-E1 Data Integration (Complexity: 6)

**Modules:**
- `h_e1_loader.py` (HE1DataLoader class)

**Deliverables:**
- Loaded DCS_3 scores CSV (N=100 with repo_id, dcs_3_score, t0_date)
- Validation check (all scores in [0,3] range, no missing values)

**Acceptance Criteria:**
- Successfully load ../h-e1/validation_results.csv
- Verify N=100 repositories present
- All DCS_3 scores valid (0 ≤ score ≤ 3)

**Complexity Breakdown:**
- Module_Size: 2 (1 class, ~100 LOC)
- Dependencies: 1 (pandas only)
- Algorithm: 1 (simple CSV load and validation)
- Integration: 2 (file I/O + path resolution)

---

### M-2: GitHub Metrics Collection (Complexity: 14)

**Modules:**
- `github_collector.py` (GitHubMetricsCollector class)

**Deliverables:**
- GitHub activity metrics CSV with columns:
  - commits_per_month
  - unique_contributors
  - median_issue_response_time (nullable)
  - repo_age_days
- Data collection success rate ≥95%

**Acceptance Criteria:**
- Authenticate with GitHub API (token from env)
- Collect metrics for T0-T90 window
- Handle API rate limits gracefully (exponential backoff)
- Missing data allowed only for median_issue_response_time (<5 issues)

**Complexity Breakdown:**
- Module_Size: 4 (1 class with 5 collection methods, ~400 LOC)
- Dependencies: 3 (PyGithub, pandas, datetime)
- Algorithm: 3 (temporal windowing, median calculation, rate limit handling)
- Integration: 4 (GitHub API + H-E1 data + error handling)

---

### M-3: Data Validation Pipeline (Complexity: 10)

**Modules:**
- `validator.py` (DataValidator class)

**Deliverables:**
- Data quality report (completeness, outlier count)
- Cleaned dataset CSV (≥95 repositories with complete data)
- Outlier flags (z-score > 3) reported but not removed

**Acceptance Criteria:**
- Quality gate: ≥95/100 repositories with complete data
- Z-score outlier detection for all continuous metrics
- CSV export with quality metadata

**Complexity Breakdown:**
- Module_Size: 3 (1 class with 4 validation methods, ~250 LOC)
- Dependencies: 2 (pandas, scipy.stats)
- Algorithm: 3 (completeness check, z-score calculation, missing value logic)
- Integration: 2 (reads merged data, exports cleaned CSV)

---

### M-4: Correlation Analysis Engine (Complexity: 12)

**Modules:**
- `correlation_analyzer.py` (CorrelationAnalyzer class)

**Deliverables:**
- Spearman correlation results (rho, p-value for each metric vs DCS_3)
- Partial correlation results (age-controlled)
- Bootstrap 95% CI for primary correlation
- All results exported to CSV

**Acceptance Criteria:**
- Primary test: commits_per_month vs DCS_3 (one-tailed p-value)
- Secondary test: partial correlation controlling for repo_age_days
- Bootstrap CI with 10,000 iterations

**Complexity Breakdown:**
- Module_Size: 3 (1 class with 4 analysis methods, ~300 LOC)
- Dependencies: 3 (scipy, pingouin, numpy)
- Algorithm: 4 (Spearman, partial corr, bootstrap resampling, CI calculation)
- Integration: 2 (reads cleaned data, outputs results dict)

---

### M-5: Gate Check System (Complexity: 8)

**Modules:**
- `gate_checker.py` (GateChecker class)

**Deliverables:**
- Primary gate status (PASS/FAIL based on ρ ≥ 0.30, p < 0.05)
- Secondary gate status (partial ρ ≥ 0.25, p < 0.05)
- Routing decision (PASS → Phase 5, FAIL → Phase 2A-Dialogue)

**Acceptance Criteria:**
- Correctly identify gate PASS/FAIL conditions
- Generate routing decision based on combined gates
- Export gate status to JSON

**Complexity Breakdown:**
- Module_Size: 2 (1 class with 3 gate check methods, ~150 LOC)
- Dependencies: 1 (pandas for data structures)
- Algorithm: 3 (threshold comparison, one-tailed p-value adjustment, routing logic)
- Integration: 2 (reads correlation results, outputs gate decision)

---

### M-6: Visualization Suite (Complexity: 9)

**Modules:**
- `plotter.py` (CorrelationVisualizer class)

**Deliverables:**
- 4 required figures:
  1. Primary scatter plot (commits vs DCS_3 with regression line)
  2. Correlation matrix heatmap (all metrics vs DCS_3)
  3. Partial correlation comparison (raw vs age-controlled)
  4. Component-level correlations (optional, if H-E1 component scores available)

**Acceptance Criteria:**
- All figures saved to figures/ directory
- Primary scatter includes annotated ρ and p-value
- Correlation matrix shows significance stars
- Partial comparison includes 95% CI error bars

**Complexity Breakdown:**
- Module_Size: 2 (1 class with 4 plot methods, ~300 LOC)
- Dependencies: 2 (matplotlib, seaborn)
- Algorithm: 2 (data aggregation, chart formatting)
- Integration: 3 (reads multiple CSVs, saves PNG files, handles optional data)

---

### M-7: Pipeline Orchestration (Complexity: 11)

**Modules:**
- `pipeline.py` (CorrelationPipeline class)
- `config.yaml` (configuration)
- `main.py` (entry point)

**Deliverables:**
- Full pipeline runner (6 phases: load H-E1 → collect GitHub → validate → analyze → gate check → visualize)
- Error handling and logging
- Results summary JSON

**Acceptance Criteria:**
- Pipeline executes all phases sequentially
- Intermediate CSVs saved for reproducibility
- Error logs capture GitHub API failures
- Final results JSON includes gate decision

**Complexity Breakdown:**
- Module_Size: 3 (orchestrator + config + main, ~350 LOC)
- Dependencies: 2 (all module imports + logging)
- Algorithm: 2 (sequential execution, checkpoint logic)
- Integration: 4 (coordinates 6 modules + file I/O + error handling)

---

## Data Flow

**Phase 1: Load H-E1 Data**
```
../h-e1/validation_results.csv → HE1DataLoader → h_e1_dcs_scores.csv
```

**Phase 2: Collect GitHub Metrics**
```
h_e1_dcs_scores.csv → GitHubMetricsCollector (GitHub API) → github_activity_metrics.csv
```

**Phase 3: Merge and Validate**
```
h_e1_dcs_scores.csv + github_activity_metrics.csv → DataValidator → activity_metrics_cleaned.csv
```

**Phase 4: Statistical Analysis**
```
activity_metrics_cleaned.csv → CorrelationAnalyzer → correlation_results.csv + partial_correlation_results.csv + bootstrap_ci.csv
```

**Phase 5: Gate Check**
```
correlation_results.csv + partial_correlation_results.csv → GateChecker → gate_status.json
```

**Phase 6: Visualization**
```
activity_metrics_cleaned.csv + correlation_results.csv → CorrelationVisualizer → figures/*.png
```

---

## Risk Mitigation in Architecture

### R1: GitHub API Rate Limit
- **Mitigation**: Exponential backoff in `GitHubMetricsCollector`
- **Monitoring**: Log API call counts and rate limit status
- **Fallback**: Authenticated token provides 5000 requests/hour (sufficient for N=100)

### R2: H-E1 Dependency
- **Mitigation**: Early validation in `HE1DataLoader.validate_dcs_data()`
- **Fail-fast**: Pipeline exits immediately if H-E1 data missing or invalid

### R3: Null Result (ρ ≈ 0)
- **Mitigation**: This is a valid scientific result (mechanism hypothesis rejected)
- **Routing**: GateChecker routes to Phase 2A-Dialogue to explore alternative mechanisms

### R6: Data Collection Failure
- **Mitigation**: Target N=100, accept ≥95 for quality gate
- **Monitoring**: Track collection success rate per repository
- **Logging**: Capture API errors for manual investigation

---

## Quality Gates

### Pre-Analysis Gates
1. **H-E1 Data Loaded**: N=100 with valid DCS_3 scores (M-1 validation)
2. **GitHub Collection Success**: ≥95% data collection rate (M-2 validation)
3. **Data Quality**: ≥95 repositories with complete metrics (M-3 validation)

### Analysis Gates
4. **Primary Gate (SHOULD_WORK)**: ρ ≥ 0.30 AND p < 0.05 (M-4 + M-5)
5. **Secondary Gate**: Partial ρ ≥ 0.25 AND p < 0.05 (M-4 + M-5)

---

## Success Metrics

### Pipeline Metrics
- Total runtime: ≤2 hours (GitHub API collection dominates)
- Data completeness: ≥95% (≥95/100 repositories)
- Error rate: <5% for GitHub API calls

### Research Metrics
- Primary: Spearman ρ ≥ 0.30, p < 0.05 (one-tailed)
- Secondary: Partial ρ ≥ 0.25, p < 0.05 (age-controlled)
- Bootstrap CI width: <0.40 (precision requirement)

---

## Architecture Validation

### Brevity Checks
- [x] No ASCII diagrams (used bullet lists)
- [x] No KB search logs (only "Applied: X" in header)
- [x] Module descriptions = interface signatures only
- [x] Total length < 500 lines
- [x] 6-12 Epic tasks with complexity scores

### Serena MCP Validation
- [x] Base hypothesis exists → Serena analysis included
- [x] "Codebase Analysis (Serena)" section included
- [x] Import paths verified from actual h-e1/src/ code

### Content Completeness
- [x] 7 Epic tasks with complexity scores (70 total)
- [x] Module structure (7 modules, interfaces only)
- [x] File organization
- [x] Configuration structure (YAML)
- [x] External dependencies from H-E1 listed
- [x] Data flow documented

---

**Document Version:** 1.0  
**Next Phase:** Phase 4 - Implementation (Coder Agent)  
**Total Complexity:** 70 points (within MECHANISM/LIGHT tier budget)  
**Gate Status:** SHOULD_WORK gate pending (validation in Phase 4)
