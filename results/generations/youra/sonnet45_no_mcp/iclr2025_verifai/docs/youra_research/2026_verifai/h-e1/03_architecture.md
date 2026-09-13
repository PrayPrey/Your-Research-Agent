# Architecture Specification: h-e1

**Date:** 2026-04-20  
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Architect:** Architecture Agent

Applied: DL experiment minimal structure pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Findings:** No existing code - minimal EXISTENCE architecture for correlation experiment

---

## System Overview

**Purpose:** Validate correlation between LLM confidence derivatives and proof timeout outcomes using LeanDojo ReProver on 100 extended-timeout experiments.

**Architecture Tier:** EXISTENCE (PoC) - minimal structure for "does it work?" validation

**Components:**
- Data loading (LeanDojo Benchmark sampling)
- Confidence extraction (softmax entropy monitoring)
- Experiment execution (100 × 300s timeout runs)
- Correlation analysis (Pearson r, Spearman ρ)
- Visualization (gate metrics + supporting figures)

---

## Module Specifications

### 1. DataLoader (`code/data/loader.py`)

**Dependencies:** lean_dojo, numpy

```python
class TheoremSampler:
    def __init__(self, repo_url: str, commit_hash: str, sample_size: int = 100, seed: int = 42): ...
    def load_benchmark(self) -> list: ...
    def sample_theorems(self) -> list: ...
```

### 2. ConfidenceExtractor (`code/models/confidence_extractor.py`)

**Dependencies:** numpy, scipy.stats

```python
class ConfidenceTrajectoryExtractor:
    def __init__(self, window_size: int = 15): ...
    def extract_confidence_trajectory(self, proof_search_session) -> tuple[float, list]: ...
    def compute_entropy(self, probabilities: np.ndarray) -> float: ...
    def compute_derivative(self, entropies: list) -> float: ...
```

### 3. ProofRunner (`code/experiment/runner.py`)

**Dependencies:** lean_dojo, ConfidenceExtractor

```python
class ExtendedTimeoutRunner:
    def __init__(self, timeout_seconds: int = 300, confidence_window: int = 15): ...
    def run_experiment(self, theorem) -> dict: ...
    def run_batch(self, theorems: list) -> list: ...
```

### 4. CorrelationAnalyzer (`code/analysis/analyzer.py`)

**Dependencies:** scipy.stats, sklearn.metrics, numpy

```python
class CorrelationAnalyzer:
    def compute_pearson(self, derivatives: np.ndarray, outcomes: np.ndarray) -> tuple[float, float]: ...
    def compute_spearman(self, derivatives: np.ndarray, outcomes: np.ndarray) -> tuple[float, float]: ...
    def compute_auc(self, derivatives: np.ndarray, outcomes: np.ndarray) -> float: ...
    def evaluate_gate(self, r: float, rho: float) -> bool: ...
```

### 5. Visualizer (`code/visualization/visualizer.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
class ExperimentVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics(self, r: float, rho: float, target: float = 0.3) -> None: ...
    def plot_scatter(self, derivatives: np.ndarray, outcomes: np.ndarray) -> None: ...
    def plot_distributions(self, derivatives: np.ndarray, outcomes: np.ndarray) -> None: ...
    def plot_trajectory_examples(self, trajectories: list, outcomes: list) -> None: ...
    def plot_roc_curve(self, derivatives: np.ndarray, outcomes: np.ndarray) -> None: ...
```

### 6. Configuration (`code/config.py`)

**Dependencies:** None

```python
class ExperimentConfig:
    repo_url: str = "https://github.com/leanprover-community/mathlib"
    commit_hash: str = "..."
    sample_size: int = 100
    timeout_seconds: int = 300
    confidence_window: int = 15
    random_seed: int = 42
    output_dir: str = "./results"
    figures_dir: str = "./figures"
```

### 7. Main Experiment (`code/run_experiment.py`)

**Dependencies:** All above modules

```python
def main():
    # Load config
    # Sample theorems
    # Run experiments with confidence extraction
    # Compute correlations
    # Generate visualizations
    # Save results
    # Evaluate gate condition
    ...

if __name__ == "__main__":
    main()
```

---

## File Structure

```
h-e1/
├── code/
│   ├── config.py                          # Hardcoded configuration
│   ├── data/
│   │   ├── __init__.py
│   │   └── loader.py                      # Theorem sampling
│   ├── models/
│   │   ├── __init__.py
│   │   └── confidence_extractor.py        # Entropy calculation
│   ├── experiment/
│   │   ├── __init__.py
│   │   └── runner.py                      # Extended timeout execution
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── analyzer.py                    # Correlation computation
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── visualizer.py                  # Figure generation
│   └── run_experiment.py                  # Main entry point
├── results/
│   ├── results_raw.csv
│   ├── metrics_summary.json
│   └── experiment_metadata.json
└── figures/
    ├── gate_metrics.png                   # MANDATORY
    ├── scatter_plot.png
    ├── distributions.png
    ├── trajectory_examples.png
    └── roc_curve.png
```

---

## Data Flow

1. **Sampling:** TheoremSampler → 100 theorems from LeanDojo Benchmark
2. **Execution:** ExtendedTimeoutRunner → proof search with confidence monitoring
3. **Extraction:** ConfidenceTrajectoryExtractor → entropy trajectory + derivative
4. **Analysis:** CorrelationAnalyzer → r, ρ, p-values, AUC
5. **Visualization:** ExperimentVisualizer → 5 figures (gate metrics mandatory)
6. **Output:** CSV + JSON results files

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Install LeanDojo, dependencies, verify GPU access | 6 | 2+1+2+1 (install+verify+GPU+test) |
| A-2 | Data Loading | Implement TheoremSampler with LeanDojo API | 8 | 2+2+2+2 (API+sampling+seed+validation) |
| A-3 | Confidence Extraction | Implement ConfidenceTrajectoryExtractor with entropy calculation | 10 | 3+2+3+2 (entropy+derivative+integration+edge_cases) |
| A-4 | Experiment Execution | Implement ExtendedTimeoutRunner with 300s timeout | 12 | 3+3+3+3 (runner+timeout+batch+error_handling) |
| A-5 | Correlation Analysis | Implement CorrelationAnalyzer with gate evaluation | 9 | 2+2+3+2 (pearson+spearman+AUC+gate) |
| A-6 | Visualization | Implement ExperimentVisualizer with 5 required figures | 11 | 3+2+2+2+2 (gate_plot+scatter+dist+traj+roc) |
| A-7 | Integration & Execution | Main experiment script, run 100 experiments (~8.3 hours), save results | 14 | 3+5+4+2 (main+execution+results+validation) |

**Total Complexity:** 70  
**Distribution:** VeryHigh(18-20): [], High(14-17): [A-7], Medium(9-13): [A-3, A-4, A-5, A-6], Low(4-8): [A-1, A-2]

**Complexity Breakdown Legend:**
- Module_Size: Lines of code / complexity of implementation (1-5)
- Dependencies: Number and complexity of external dependencies (1-5)
- Algorithm: Computational/algorithmic complexity (1-5)
- Integration: Integration points and data flow complexity (1-5)

---

## Dependencies

### External Libraries

```python
# Core dependencies
lean_dojo>=1.0.0         # LeanDojo API, ReProver model
numpy>=1.21.0            # Array operations
scipy>=1.7.0             # Statistics (pearsonr, spearmanr)
scikit-learn>=1.0.0      # Metrics (roc_auc_score)
matplotlib>=3.4.0        # Visualization
seaborn>=0.11.0          # Enhanced plotting
```

### System Requirements

- Python 3.8+
- CUDA-enabled GPU (single GPU via CUDA_VISIBLE_DEVICES)
- ~1GB storage (model + results)
- ~8.3 hours execution time (100 × 300s + overhead)

---

## Configuration

### Fixed Parameters (EXISTENCE - No YAML)

```python
# Hardcoded in config.py
SAMPLE_SIZE = 100
TIMEOUT_SECONDS = 300
CONFIDENCE_WINDOW = 15
RANDOM_SEED = 42
TARGET_CORRELATION = 0.3
```

### GPU Usage

```bash
# Before running experiment
nvidia-smi  # Check available GPUs
export CUDA_VISIBLE_DEVICES=0  # Use single empty GPU
python code/run_experiment.py
```

---

## Success Criteria

### Gate Condition (MUST_WORK)

- **Primary:** Pearson r > 0.3 OR Spearman ρ > 0.3
- **Secondary:** p-value < 0.05 for statistical significance

### Output Validation

- [ ] All 100 experiments complete (success or timeout)
- [ ] results_raw.csv with 100 rows
- [ ] metrics_summary.json with r, ρ, AUC, gate_result
- [ ] All 5 figures generated (gate_metrics.png mandatory)
- [ ] Gate evaluation: PASS/FAIL recorded

---

## Implementation Notes

### Key Design Patterns

1. **Non-invasive monitoring:** Confidence extraction does not modify proof search
2. **Batch processing:** 100 theorems with progress tracking
3. **Robust error handling:** Individual theorem failures logged, batch continues
4. **Reproducibility:** Fixed seed for theorem sampling

### LeanDojo Integration Points

```python
# Theorem loading
from lean_dojo import LeanGitRepo, Theorem
repo = LeanGitRepo(url, commit)
theorems = load_benchmark_theorems()

# Proof search with confidence extraction
from lean_dojo import Dojo
dojo = Dojo(theorem)
tactics_with_probs = dojo.get_tactics()  # Returns [(tactic, logprob), ...]

# Softmax probability extraction
probs = np.array([np.exp(logprob) for _, logprob in tactics_with_probs])
probs = probs / probs.sum()  # Normalize
entropy_val = scipy.stats.entropy(probs)
```

### Edge Cases

- **Early termination:** Proof completes before 15 steps → use available entropy values
- **No tactics:** get_tactics() returns empty → skip theorem, log warning
- **Timeout handling:** 300s timeout enforcement via threading/async
- **Memory management:** Clear proof session after each theorem

---

## Validation

### Smoke Test

```python
# test_experiment.py
def test_smoke():
    # Load 3 theorems
    # Run with 10s timeout
    # Verify entropy extraction works
    # Verify correlation computation runs
    assert len(results) == 3
    assert all('confidence_derivative' in r for r in results)
```

### Output Validation

```python
# After experiment completion
assert os.path.exists('results/results_raw.csv')
assert os.path.exists('results/metrics_summary.json')
assert os.path.exists('figures/gate_metrics.png')

with open('results/metrics_summary.json') as f:
    metrics = json.load(f)
    assert 'correlation_pearson' in metrics
    assert 'gate_result' in metrics
```

---

## Traceability

| Requirement | Module | Implementation |
|-------------|--------|----------------|
| FR-1: Dataset sampling | DataLoader | TheoremSampler with seed=42 |
| FR-2: Baseline evaluation | ProofRunner | LeanDojo ReProver with 300s timeout |
| FR-3: Confidence extraction | ConfidenceExtractor | Entropy std dev over 15 steps |
| FR-4: Experiment execution | ProofRunner | Batch runner for 100 theorems |
| FR-5: Correlation analysis | CorrelationAnalyzer | Pearson r, Spearman ρ, AUC |
| FR-6: Visualization | Visualizer | 5 figures including gate metrics |
| FR-7: Results logging | run_experiment.py | CSV + JSON outputs |
| NFR-2: Reproducibility | config.py | Fixed seed, version pinning |

---

*Architecture optimized for EXISTENCE (PoC) tier - minimal structure for correlation validation*
*Next Phase: Phase 4 - Implementation*
