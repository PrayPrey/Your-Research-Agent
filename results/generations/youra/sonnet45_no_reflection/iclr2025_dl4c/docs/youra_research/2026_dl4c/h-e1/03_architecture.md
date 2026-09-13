# Architecture: H-E1 Aspect-Dominant Structure Existence

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (Proof-of-Concept)  
**Generated:** 2026-05-11  
**Architect:** architecture-agent

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Findings:** First hypothesis in pipeline, no base code to reuse.

---

## Applied Patterns (Archon KB)

Applied: Statistical analysis pipeline (empirical validation structure)

---

## Design Philosophy

**EXISTENCE Architecture Principles:**
- Minimal structure to test "does spectral gap exist?"
- Single-pass pipeline: data → metrics → statistics → decision
- No model training, no ablation studies
- Focus: Statistical validation over software engineering

---

## Module Structure

### 1. DataCollector (`src/data_collection.py`)

**Dependencies:** PyGitHub, PyDriller, tree-sitter

```python
class GitHubCommitCollector:
    def __init__(self, config: CollectionConfig): ...
    def mine_repositories(self, min_stars: int, n_repos: int) -> List[RepoMetadata]: ...
    def filter_commits(self, repo: RepoMetadata, ast_max: int, time_range: Tuple) -> List[CommitData]: ...
    def compute_ast_distance(self, pre_code: str, post_code: str, language: str) -> int: ...
    def label_commit(self, commit_msg: str) -> str: ...
    def download_file_pairs(self, commit: CommitData) -> Tuple[str, str]: ...

class CommitStorage:
    def save_metadata(self, commits: List[CommitData], path: str): ...
    def save_file_pairs(self, commit_id: str, pre: str, post: str, base_dir: str): ...
    def load_commits(self, path: str) -> List[CommitData]: ...
```

---

### 2. MetricComputer (`src/metrics.py`)

**Dependencies:** pytest, SonarQube, CodeQL, pytest-benchmark

```python
class MetricComputer:
    def __init__(self, config: MetricConfig): ...
    def compute_all_metrics(self, commit: CommitData) -> Dict[str, float]: ...
    
class CorrectnessMetric:
    def compute(self, pre_file: str, post_file: str) -> float: ...
    
class QualityMetric:
    def __init__(self, sonarqube_url: str): ...
    def compute(self, pre_file: str, post_file: str) -> float: ...
    
class SecurityMetric:
    def __init__(self, codeql_path: str): ...
    def compute(self, pre_file: str, post_file: str) -> float: ...
    
class EfficiencyMetric:
    def compute(self, pre_file: str, post_file: str) -> float: ...

class OutcomeMatrixBuilder:
    def build_matrix(self, commits: List[CommitData], metrics: List[Dict]) -> np.ndarray: ...
    def save(self, matrix: np.ndarray, path: str): ...
```

---

### 3. StatisticalAnalyzer (`src/analysis.py`)

**Dependencies:** NumPy, SciPy, statsmodels

```python
class ConfoundRegressor:
    def __init__(self, confounds: List[str]): ...
    def fit_mixed_model(self, Y: np.ndarray, X: np.ndarray, groups: np.ndarray) -> np.ndarray: ...
    def compute_residuals(self, Y: np.ndarray, fitted: np.ndarray) -> np.ndarray: ...

class SpectralAnalyzer:
    def compute_covariance(self, Y_residual: np.ndarray) -> np.ndarray: ...
    def eigendecomposition(self, Sigma: np.ndarray) -> Tuple[np.ndarray, np.ndarray]: ...
    def spectral_gap(self, lambdas: np.ndarray) -> float: ...
    def cross_aspect_coupling(self, Sigma: np.ndarray) -> float: ...

class PermutationTest:
    def __init__(self, n_permutations: int): ...
    def run(self, Y_residual: np.ndarray, observed_gap: float) -> Dict: ...
    def compute_p_value(self, null_gaps: List[float], observed: float) -> float: ...

class DirectionalStability:
    def compute_on_axis_projections(self, Y_residual: np.ndarray, eigenvectors: np.ndarray, 
                                    aspect_labels: np.ndarray) -> np.ndarray: ...
    def z_scores(self, projections: np.ndarray) -> np.ndarray: ...

class CrossValidator:
    def leave_one_repo_out(self, Y_residual: np.ndarray, repo_ids: np.ndarray) -> Dict: ...
    def eigenspace_alignment(self, V_train: np.ndarray, V_test: np.ndarray) -> float: ...
```

---

### 4. ValidationPipeline (`src/validation.py`)

**Dependencies:** pandas, scikit-learn

```python
class MetricValidator:
    def test_retest_reliability(self, metrics_t1: np.ndarray, metrics_t2: np.ndarray) -> Dict: ...
    def compute_icc(self, m1: np.ndarray, m2: np.ndarray) -> float: ...
    def construct_validity(self, metric_values: np.ndarray, expert_ratings: np.ndarray) -> float: ...

class PurityValidator:
    def __init__(self, n_experts: int): ...
    def load_annotations(self, paths: List[str]) -> pd.DataFrame: ...
    def compute_purity(self, annotations: pd.DataFrame) -> float: ...
    def fleiss_kappa(self, annotations: pd.DataFrame) -> float: ...
```

---

### 5. GateDecision (`src/gate.py`)

**Dependencies:** None (pure logic)

```python
class GateEvaluator:
    def __init__(self, thresholds: Dict[str, float]): ...
    def evaluate_primary_criteria(self, results: Dict) -> bool: ...
    def evaluate_secondary_criteria(self, results: Dict) -> Dict[str, bool]: ...
    def make_decision(self, primary: bool, secondary: Dict) -> GateDecision: ...
    def save_decision(self, decision: GateDecision, path: str): ...

@dataclass
class GateDecision:
    passed: bool
    spectral_gap: float
    p_value: float
    coupling: float
    on_axis_zscore: float
    rationale: str
    timestamp: str
```

---

### 6. Visualizer (`src/visualization.py`)

**Dependencies:** matplotlib, seaborn

```python
class Visualizer:
    def eigenspectrum_plot(self, lambdas: np.ndarray, output_path: str): ...
    def permutation_distribution(self, null_gaps: List[float], observed: float, output_path: str): ...
    def directional_stability_heatmap(self, z_scores: np.ndarray, output_path: str): ...
    def covariance_heatmap(self, Sigma: np.ndarray, output_path: str): ...
```

---

### 7. ReportGenerator (`src/reporting.py`)

**Dependencies:** None (file I/O)

```python
class ReportGenerator:
    def __init__(self, results_dir: str): ...
    def generate_validation_report(self, gate_decision: GateDecision, all_results: Dict, 
                                   output_path: str): ...
    def load_all_artifacts(self) -> Dict: ...
    def format_metrics_table(self, metrics: Dict) -> str: ...
    def format_gate_summary(self, decision: GateDecision) -> str: ...
```

---

### 8. Configuration (`src/config.py`)

**Dependencies:** dataclasses, yaml

```python
@dataclass
class ExperimentConfig:
    n_commits: int = 10000
    min_stars: int = 1000
    ast_distance_max: int = 20
    time_range: Tuple[str, str] = ("2023-01-01", "2026-01-01")
    languages: List[str] = field(default_factory=lambda: ["python", "javascript", "java"])
    
    spectral_gap_threshold: float = 2.0
    p_value_threshold: float = 0.05
    coupling_threshold: float = 0.2
    on_axis_threshold: float = 2.0
    
    n_permutations: int = 1000
    n_validation_commits: int = 200
    n_purity_commits: int = 500
    n_experts: int = 3
    
    output_dir: str = "outputs"
    cache_dir: str = "cache"

def load_config(path: str) -> ExperimentConfig: ...
def save_config(config: ExperimentConfig, path: str): ...
```

---

### 9. MainPipeline (`src/main.py`)

**Dependencies:** All above modules

```python
class ExistencePipeline:
    def __init__(self, config: ExperimentConfig): ...
    
    def run_phase0_metric_validation(self) -> bool: ...
    def run_phase1a_data_collection(self) -> np.ndarray: ...
    def run_phase1b_purity_validation(self) -> float: ...
    def run_phase2_spectral_analysis(self, Y: np.ndarray) -> Dict: ...
    def run_phase3_statistical_tests(self, Y_residual: np.ndarray) -> Dict: ...
    def run_phase4_gate_decision(self, all_results: Dict) -> GateDecision: ...
    
    def execute(self) -> GateDecision: ...

def main():
    config = load_config("config.yaml")
    pipeline = ExistencePipeline(config)
    decision = pipeline.execute()
    print(f"Gate Decision: {'PASS' if decision.passed else 'FAIL'}")
```

---

## File Organization

```
h-e1/
├── src/
│   ├── data_collection.py      # FR-1: GitHub mining, commit filtering
│   ├── metrics.py               # FR-2, FR-3: Metric computation
│   ├── validation.py            # FR-2, FR-4: Reliability, purity
│   ├── analysis.py              # FR-5: Confound regression, spectral analysis
│   ├── gate.py                  # FR-9: Gate decision logic
│   ├── visualization.py         # FR-10: All plots
│   ├── reporting.py             # FR-10: Report generation
│   ├── config.py                # Configuration management
│   └── main.py                  # Pipeline orchestration
├── scripts/
│   ├── setup_environment.sh     # Install dependencies, start Docker
│   ├── run_phase0.sh            # Metric validation
│   ├── run_phase1a.sh           # Data collection
│   ├── run_phase1b.sh           # Purity validation
│   ├── run_phase2.sh            # Spectral analysis
│   ├── run_phase3.sh            # Statistical tests
│   └── run_phase4.sh            # Gate decision + report
├── config/
│   └── experiment_config.yaml   # All thresholds and parameters
├── data/
│   ├── commits_10k.jsonl        # Collected commits
│   ├── outcome_matrix.npy       # 10K×4 metrics
│   └── outcome_residual.npy     # After confound regression
├── outputs/
│   ├── eigenvalues.json
│   ├── eigenvectors.npy
│   ├── covariance_matrix.npy
│   ├── permutation_results.json
│   ├── directional_stability.json
│   ├── loro_results.json
│   └── gate1_decision.json
├── visualizations/
│   ├── eigenspectrum.png
│   ├── permutation_distribution.png
│   ├── directional_stability_heatmap.png
│   └── covariance_heatmap.png
├── reports/
│   └── h-e1_validation_report.md
└── tests/
    ├── test_data_collection.py
    ├── test_metrics.py
    └── test_analysis.py
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Data Collection Pipeline | Implement GitHub mining, commit filtering, AST distance, aspect labeling, file storage | 15 | Module(4) + Deps(3) + Algo(4) + Integration(4) |
| E2 | Metric Computation System | Implement 4 metrics (correctness, quality, security, efficiency) with SonarQube/CodeQL integration | 17 | Module(5) + Deps(4) + Algo(4) + Integration(4) |
| E3 | Validation Infrastructure | Implement test-retest reliability (ICC), construct validity, purity validation, inter-rater agreement | 14 | Module(3) + Deps(3) + Algo(4) + Integration(4) |
| E4 | Spectral Analysis Core | Implement confound regression, covariance computation, eigendecomposition, spectral gap, coupling metrics | 16 | Module(4) + Deps(3) + Algo(5) + Integration(4) |
| E5 | Statistical Testing Suite | Implement permutation test (1000 shuffles), directional stability, LORO cross-validation | 15 | Module(4) + Deps(3) + Algo(4) + Integration(4) |
| E6 | Gate Decision & Reporting | Implement gate evaluation logic, visualization suite (4 plots), comprehensive report generator | 11 | Module(3) + Deps(2) + Algo(3) + Integration(3) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [E1, E2, E4, E5], Medium(9-13): [E6], Low(4-8): [E3]

**Total Complexity:** 88 points  
**Critical Path:** E1 → E2 → E3 → E4 → E5 → E6

---

## Dependencies

### External Tools (Docker)
- **SonarQube:** `docker run -d --name sonarqube -p 9000:9000 sonarqube:latest`
- **CodeQL:** CLI from GitHub releases

### Python Libraries
```
# Core
numpy>=1.24.0
scipy>=1.10.0
pandas>=2.0.0

# Data Collection
PyGithub>=2.0.0
pydriller>=2.5.0
tree-sitter>=0.20.0

# Metrics
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-benchmark>=4.0.0

# Statistics
statsmodels>=0.14.0
scikit-learn>=1.3.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# Utils
pyyaml>=6.0
requests>=2.31.0
tqdm>=4.65.0
```

---

## Validation Checklist

### Architecture Completeness
- [x] 9 modules with interface signatures
- [x] No ASCII diagrams
- [x] File organization specified
- [x] 6 Epic tasks with complexity scores (88 total)
- [x] Codebase Analysis section included
- [x] Applied patterns noted

### EXISTENCE Compliance
- [x] Minimal structure (single-pass pipeline)
- [x] No model training modules
- [x] Focus on statistical validation
- [x] 4-6 Epic tasks (6 tasks)

### Output Requirements
- [x] Total length < 500 lines
- [x] Interface code only (no prose)
- [x] Dependencies listed
- [x] Module descriptions = signatures only

---

## Design Decisions

**Statistical Focus:** Pure empirical analysis, no deep learning infrastructure needed.

**Monolithic vs Modular:** Chose modular for clarity, but each module is single-purpose (no over-engineering).

**Docker Integration:** SonarQube/CodeQL via Docker for reproducibility.

**Checkpoint Strategy:** Save artifacts at each phase boundary (outcome_matrix, covariance, eigenvalues).

**Parallelization:** Metric computation uses multiprocessing.Pool (16 cores), but analysis remains sequential for reproducibility.

---

**End of Architecture Document**  
**Next Phase:** Phase 4 Implementation  
**Ready for:** Epic task breakdown and coding
