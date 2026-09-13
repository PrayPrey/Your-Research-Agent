# System Architecture: h-m-integrated

**Document Type**: Architecture Design
**Hypothesis ID**: h-m-integrated
**Hypothesis Type**: MECHANISM
**Created Date**: 2026-07-13
**Infrastructure Tier**: STANDARD

---

## Applied Patterns

Applied: Modular calibration pipeline (from h-e1 base implementation)
Applied: Hierarchical Bayesian updating (iterative co-calibration pattern)
Applied: Multi-baseline comparison framework (standardized evaluation)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: Reusing h-e1 data loading, consistency scoring, and conformal prediction modules. Verified import paths from actual implementation.

---

## Architecture Overview

**Purpose**: Validate hierarchical Bayesian calibration (HBC) mechanism achieving ECE < 0.05 with 30-50% computational cost reduction.

**Core Mechanism**: Three-step causal chain with mutual calibration:
1. Consistency sampling → epistemic prior C(x)
2. Conformal prediction → aleatoric intervals I(x) (weighted by C(x))
3. Bayesian co-calibration → mutual threshold updating

**Module Count**: 9 modules (4 reused from h-e1, 5 new)

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| MultiDatasetLoader | `from h_e1.src.data_loader import MultiDatasetLoader` | `h-e1/code/src/data_loader.py` |
| LlamaGenerator | `from h_e1.src.baseline_model import LlamaGenerator` | `h-e1/code/src/baseline_model.py` |
| ConsistencyScorer | `from h_e1.src.consistency_scorer import ConsistencyScorer` | `h-e1/code/src/consistency_scorer.py` |
| ConformalPredictor | `from h_e1.src.conformal_predictor import ConformalPredictor` | `h-e1/code/src/conformal_predictor.py` |

**Verified from**: `h-e1/code/src/` (actual implementation)

**Note**: Import paths assume h-e1 code is accessible. Phase 4 coder should verify relative import structure or copy modules.

---

## Module Structure

### 1. HierarchicalBayesianCalibrator (`src/hbc_calibrator.py`)

**Dependencies**: ConsistencyScorer, ConformalPredictor, LlamaGenerator

```python
class HierarchicalBayesianCalibrator:
    def __init__(
        self,
        consistency_scorer: ConsistencyScorer,
        conformal_predictor: ConformalPredictor,
        generator: LlamaGenerator,
        alpha: float = 0.1,
        max_iterations: int = 3
    ): ...
    
    def calibrate(self, calibration_data: list[dict]) -> None: ...
    
    def predict_with_uncertainty(self, query: str) -> dict: ...
    
    def _compute_weighted_nonconformity(
        self, 
        y_pred: str, 
        y_true: str, 
        consistency_score: float
    ) -> float: ...
    
    def _update_consistency_threshold(
        self, 
        coverage_results: list[float]
    ) -> float: ...
```

---

### 2. SelfCheckGPTBaseline (`src/selfcheck_baseline.py`)

**Dependencies**: ConsistencyScorer, LlamaGenerator

```python
class SelfCheckGPTBaseline:
    def __init__(
        self,
        consistency_scorer: ConsistencyScorer,
        generator: LlamaGenerator,
        threshold: float = 0.5
    ): ...
    
    def calibrate(self, calibration_data: list[dict]) -> None: ...
    
    def predict(self, query: str) -> dict: ...
    
    def optimize_threshold(
        self, 
        calibration_data: list[dict], 
        thresholds: list[float]
    ) -> float: ...
```

---

### 3. COINBaseline (`src/coin_baseline.py`)

**Dependencies**: ConformalPredictor, LlamaGenerator

```python
class COINBaseline:
    def __init__(
        self,
        conformal_predictor: ConformalPredictor,
        generator: LlamaGenerator,
        alpha: float = 0.1
    ): ...
    
    def calibrate(self, calibration_data: list[dict]) -> None: ...
    
    def predict(self, query: str) -> dict: ...
    
    def compute_coverage(self, test_data: list[dict]) -> float: ...
```

---

### 4. IndependentCascadeBaseline (`src/cascade_baseline.py`)

**Dependencies**: SelfCheckGPTBaseline, COINBaseline

```python
class IndependentCascadeBaseline:
    def __init__(
        self,
        selfcheck: SelfCheckGPTBaseline,
        coin: COINBaseline
    ): ...
    
    def calibrate(self, calibration_data: list[dict]) -> None: ...
    
    def predict(self, query: str) -> dict: ...
```

---

### 5. ECEMetric (`src/ece_metric.py`)

**Dependencies**: None

```python
class ECEMetric:
    def __init__(self, n_bins: int = 10): ...
    
    def compute(
        self, 
        predictions: np.ndarray, 
        ground_truth: np.ndarray, 
        confidences: np.ndarray
    ) -> float: ...
    
    def compute_per_bin_stats(
        self, 
        predictions: np.ndarray, 
        ground_truth: np.ndarray, 
        confidences: np.ndarray
    ) -> dict: ...
```

---

### 6. ComputationalCostTracker (`src/cost_tracker.py`)

**Dependencies**: None

```python
class ComputationalCostTracker:
    def __init__(self): ...
    
    def reset(self) -> None: ...
    
    def log_forward_pass(self, model_name: str, batch_size: int = 1) -> None: ...
    
    def get_total_cost(self) -> int: ...
    
    def get_cost_breakdown(self) -> dict: ...
    
    def compute_reduction(self, baseline_cost: int) -> float: ...
```

---

### 7. AblationStudy (`src/ablation_study.py`)

**Dependencies**: HierarchicalBayesianCalibrator, ECEMetric

```python
class AblationStudy:
    def __init__(
        self,
        hbc: HierarchicalBayesianCalibrator,
        ece_metric: ECEMetric
    ): ...
    
    def simulate_correlation_levels(
        self, 
        rho_values: list[float], 
        test_data: list[dict]
    ) -> dict: ...
    
    def perturb_consistency_scores(
        self, 
        original_scores: np.ndarray, 
        target_rho: float
    ) -> np.ndarray: ...
    
    def validate_sweet_spot(self, results: dict) -> bool: ...
```

---

### 8. MultiMethodEvaluator (`src/multi_method_evaluator.py`)

**Dependencies**: ECEMetric, ComputationalCostTracker, HierarchicalBayesianCalibrator, SelfCheckGPTBaseline, COINBaseline, IndependentCascadeBaseline

```python
class MultiMethodEvaluator:
    def __init__(
        self,
        methods: dict,
        datasets: list[str],
        ece_metric: ECEMetric,
        cost_tracker: ComputationalCostTracker
    ): ...
    
    def run_all_experiments(self) -> dict: ...
    
    def evaluate_single_method(
        self, 
        method_name: str, 
        method: object, 
        dataset_name: str
    ) -> dict: ...
    
    def compute_statistical_significance(
        self, 
        hbc_ece: np.ndarray, 
        baseline_ece: np.ndarray
    ) -> tuple[float, float]: ...
    
    def check_gate_criteria(self, results: dict) -> bool: ...
```

---

### 9. VisualizationGenerator (`src/visualization_generator.py`)

**Dependencies**: None

```python
class VisualizationGenerator:
    def __init__(self, output_dir: str = "figures/"): ...
    
    def plot_ece_comparison(self, results: dict) -> None: ...
    
    def plot_reliability_diagrams(self, results: dict) -> None: ...
    
    def plot_cost_quality_tradeoff(self, results: dict) -> None: ...
    
    def plot_coverage_comparison(self, results: dict) -> None: ...
    
    def plot_ablation_sweet_spot(self, ablation_results: dict) -> None: ...
    
    def generate_all_figures(self, results: dict, ablation_results: dict) -> None: ...
```

---

## File Organization

```
h-m-integrated/
├── code/
│   └── src/
│       ├── hbc_calibrator.py           # FR5: Core HBC mechanism
│       ├── selfcheck_baseline.py       # FR6.1: SelfCheckGPT-only
│       ├── coin_baseline.py            # FR6.2: COIN-only
│       ├── cascade_baseline.py         # FR6.3: Independent cascade
│       ├── ece_metric.py               # FR7: ECE computation
│       ├── cost_tracker.py             # FR8: Computational cost
│       ├── ablation_study.py           # FR9: Sweet spot validation
│       ├── multi_method_evaluator.py   # FR6+FR10: Multi-method eval
│       ├── visualization_generator.py  # Visualization suite
│       ├── train.py                    # Main execution script
│       └── config.py                   # Configuration
├── figures/                            # Generated visualizations
├── 03_prd.md
├── 02c_experiment_brief.md
├── 03_architecture.md                  # This document
└── 04_validation.md                    # Generated by evaluator
```

---

## Data Flow

1. **Calibration Phase**:
   - DataLoader → calibration set (500 samples/dataset)
   - HBC: C(x) → weighted conformal scores → quantile + threshold
   - Baselines: Independent calibration (SelfCheck, COIN, Cascade)

2. **Test Phase**:
   - Query → 4 methods (HBC, SelfCheck, COIN, Cascade)
   - Each method → prediction + uncertainty estimates
   - CostTracker → forward pass counts

3. **Evaluation**:
   - ECEMetric → calibration quality per method
   - Statistical tests → pairwise comparisons
   - AblationStudy → sweet spot validation
   - VisualizationGenerator → 5 required figures

4. **Gate Validation**:
   - Check: ECE_HBC < 0.05 AND p < 0.05 vs all baselines
   - Check: Cost reduction 30-50% vs COIN
   - Check: Coverage ≥ 90%
   - Check: Ablation peak at ρ ~ 0.5

---

## Configuration

```python
# config.py
CONFIG = {
    "base_hypothesis": {
        "path": "../h-e1/code",
        "modules": ["data_loader", "baseline_model", "consistency_scorer", "conformal_predictor"]
    },
    "model": {
        "name": "meta-llama/Llama-2-7b-hf",
        "temperature": 1.0,
        "max_tokens": 256,
        "num_samples": 5,
    },
    "datasets": {
        "names": ["truthful_qa", "Anthropic/hh-rlhf", "squad_v2"],
        "max_length": 512,
        "calibration_size": 500,
        "test_size": 1000,
    },
    "hbc": {
        "alpha": 0.1,
        "max_iterations": 3,
        "initial_threshold": 0.5,
    },
    "baselines": {
        "selfcheck_thresholds": [0.3, 0.4, 0.5, 0.6, 0.7],
        "coin_alpha": 0.1,
    },
    "evaluation": {
        "ece_bins": 10,
        "gate_ece_max": 0.05,
        "gate_p_threshold": 0.05,
        "gate_coverage_min": 0.90,
        "gate_cost_reduction_min": 0.30,
        "gate_cost_reduction_max": 0.50,
    },
    "ablation": {
        "rho_values": [0.2, 0.35, 0.5, 0.65, 0.8],
        "sweet_spot_center": 0.5,
        "sweet_spot_tolerance": 0.1,
    },
    "output": {
        "figures_dir": "figures/",
        "report_path": "04_validation.md",
    },
}
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | HBC Core Implementation | Implement hierarchical Bayesian calibrator with three-step mechanism (consistency prior → weighted conformal → mutual updating) | 15 | Module(4) + Deps(3) + Algo(5) + Integration(3) |
| M-2 | Baseline Suite | Implement SelfCheckGPT-only, COIN-only, Independent Cascade baselines with calibration protocols | 14 | Module(3) + Deps(3) + Algo(5) + Integration(3) |
| M-3 | ECE Metric & Cost Tracking | Implement ECE computation with binning + forward pass tracker for all methods | 10 | Module(2) + Deps(2) + Algo(4) + Integration(2) |
| M-4 | Multi-Method Evaluator | Implement unified evaluation framework with statistical significance testing and gate validation | 12 | Module(3) + Deps(3) + Algo(3) + Integration(3) |
| M-5 | Ablation Study | Implement sweet spot validation with correlation perturbation and ECE measurement across ρ values | 11 | Module(2) + Deps(3) + Algo(4) + Integration(2) |
| M-6 | Visualization Suite | Implement 5 required figures (ECE comparison, reliability diagrams, cost-quality, coverage, ablation) | 12 | Module(3) + Deps(2) + Algo(4) + Integration(3) |
| M-7 | Integration Testing | End-to-end pipeline testing with all datasets, methods, and gate validation | 11 | Module(2) + Deps(4) + Algo(2) + Integration(3) |
| M-8 | Experiment Execution | Run full experiments on 3 datasets × 4 methods with ablation study and generate validation report | 10 | Module(2) + Deps(2) + Algo(3) + Integration(3) |

**Total Tasks**: 8
**Total Complexity**: 95
**Distribution**: VeryHigh(18-20): [], High(14-17): [M-1, M-2], Medium(9-13): [M-3, M-4, M-5, M-6, M-7, M-8], Low(4-8): []

---

## Task Execution Sequence

**Phase 1 (Core Mechanism)**: M-1 (HBC implementation)
**Phase 2 (Baselines)**: M-2 (all baseline methods)
**Phase 3 (Metrics)**: M-3 (ECE + cost tracking)
**Phase 4 (Evaluation)**: M-4 || M-5 || M-6 (parallel - evaluator, ablation, viz)
**Phase 5 (Validation)**: M-7 → M-8 (integration → execution)

---

## Success Criteria Mapping

| Gate Metric | Module | Method |
|-------------|--------|--------|
| ECE_HBC < 0.05 | ECEMetric | `compute()` |
| p < 0.05 (vs all baselines) | MultiMethodEvaluator | `compute_statistical_significance()` |
| Cost reduction 30-50% | ComputationalCostTracker | `compute_reduction()` |
| Coverage ≥ 90% | HierarchicalBayesianCalibrator | `predict_with_uncertainty()` → coverage check |
| Ablation peak at ρ ~ 0.5 | AblationStudy | `validate_sweet_spot()` |

---

## Testing Strategy

**Unit Tests**:
- `test_hbc_calibrator.py`: Weighted nonconformity, threshold updating
- `test_baselines.py`: Each baseline method (SelfCheck, COIN, Cascade)
- `test_ece_metric.py`: Binning, per-bin stats, ECE computation
- `test_cost_tracker.py`: Forward pass counting, reduction calculation
- `test_ablation.py`: Correlation perturbation, sweet spot validation

**Integration Tests**:
- `test_multi_method_pipeline.py`: Full pipeline with all methods
- `test_gate_validation.py`: Gate criteria checking

---

## Infrastructure Notes

**Logging**: CSV metric export + matplotlib figures
**Error Handling**: Graceful degradation for OOM, model loading failures
**Reproducibility**: Fixed seed=42 in all modules
**Hardware**: Single GPU (≥24GB VRAM), 8-12 hours for full experiment (3 datasets × 4 methods)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OOM with 4 methods × 3 datasets | Sequential processing, clear GPU cache between methods |
| HBC convergence failure | Max 3 iterations, fallback to iteration 1 results |
| ECE ≥ 0.05 (gate failure) | Report finding, analyze failure mode (coverage vs calibration) |
| Cost reduction < 30% | Optimize sampling strategy, reduce num_samples if needed |
| No sweet spot in ablation | Report finding, revise causal theory |

---

## Deliverables

1. **Code**: 10 Python files in `code/src/`
2. **Figures**: 5 visualizations in `figures/`
   - ECE comparison bar chart (gate validation)
   - Reliability diagrams (4 subplots)
   - Cost-quality tradeoff scatter
   - Coverage comparison bar chart
   - Ablation sweet spot curve
3. **Report**: `04_validation.md` with pass/fail determination

---

**Architecture Status**: COMPLETE
**Ready for Phase 4 Implementation**: YES
**Estimated Implementation Time**: 12-16 hours (coding) + 8-12 hours (experiment execution)
