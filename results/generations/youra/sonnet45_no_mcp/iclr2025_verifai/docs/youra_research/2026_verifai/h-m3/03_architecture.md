# Architecture Specification: h-m3

**Date:** 2026-04-20  
**Hypothesis ID:** h-m3  
**Type:** MECHANISM (Hybrid Signal Combination)  
**Architect:** Phase 3 Architecture Agent  
**Base Hypothesis:** h-m2 (COMPLETED, PASSED)

Applied: Incremental extension pattern - reuse h-m2 infrastructure, add symbolic signals + hybrid voting

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** h-m2 validated infrastructure reusable  
**Analyzed Path:** h-m2/code/  
**Findings:** h-m2 implements full divergence detection pipeline (tree tracking, state capture, variance analysis). h-m3 extends with symbolic signal extraction and 7-model ablation framework.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual h-m2 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| SearchTree | `from h_m2.code.experiment.tree_tracker import SearchTree` | `h-m2/code/experiment/tree_tracker.py` |
| ExtendedTimeoutRunnerWithTree | `from h_m2.code.experiment.tree_tracker import ExtendedTimeoutRunnerWithTree` | `h-m2/code/experiment/tree_tracker.py` |
| DivergenceClassifier | `from h_m2.code.analysis.divergence_classifier import DivergenceClassifier` | `h-m2/code/analysis/divergence_classifier.py` |
| TimeoutSubgroupAnalyzer | `from h_m2.code.analysis.timeout_subgroup_analyzer import TimeoutSubgroupAnalyzer` | `h-m2/code/analysis/timeout_subgroup_analyzer.py` |
| ConfidenceTrajectoryExtractor | `from h_m2.code.models.confidence_extractor import ConfidenceTrajectoryExtractor` | `h-m2/code/models/confidence_extractor.py` |

**Verified from:** h-m2/code/ (actual implementation)

---

## System Overview

**Purpose:** Test hybrid signal combination by evaluating 7 detector variants (single-signal, pairwise, hybrid) on 100-theorem dataset.

**Architecture Tier:** MECHANISM (Full) - Extend h-m2 with symbolic signals and ablation framework

**Components:**
- Data loading: REUSE h-m2 (tree tracking + confidence extraction)
- Confidence signal: REUSE h-m1 (variance calculation)
- Search tree signal: REUSE h-m2 (backtrack frequency)
- Symbolic signal extraction: NEW (state hash collisions, exponential growth)
- Hybrid voting detector: NEW (k-of-3 voting logic)
- Ablation framework: NEW (7 model comparison)
- Visualization: EXTEND h-m2 (ablation comparison plots)

---

## Module Specifications

### REUSED MODULES (No Modifications)

#### 1. ExtendedTimeoutRunnerWithTree (`h-m2/code/experiment/tree_tracker.py`)
**Status:** REUSE AS-IS  
**Justification:** Provides tree tracking, state capture, confidence extraction (all needed for h-m3)

#### 2. ConfidenceTrajectoryExtractor (`h-m2/code/models/confidence_extractor.py`)
**Status:** REUSE AS-IS  
**Justification:** Variance calculation validated in h-m1, used in h-m2

---

### NEW MODULES

#### 3. SymbolicSignalExtractor (`code/signals/symbolic_extractor.py`)
**Status:** NEW for h-m3  
**Dependencies:** numpy, typing

```python
class SymbolicSignalExtractor:
    """Extract symbolic divergence signals from proof states."""
    
    def __init__(self, growth_window: int = 10):
        self.growth_window = growth_window
    
    def extract_signals(self, proof_states: list, search_tree) -> dict:
        """
        Extract symbolic signals from proof search trajectory.
        
        Args:
            proof_states: List of proof states from search
            search_tree: SearchTree object with state hashes
        
        Returns:
            {
                'state_collisions': int,
                'exponential_growth_rate': float
            }
        """
        ...
    
    def _count_state_collisions(self, search_tree) -> int:
        """Count hash collisions using search_tree.get_collision_count()."""
        ...
    
    def _fit_exponential_growth(self, proof_states: list) -> float:
        """Fit exponential trend to proof state sizes over time."""
        ...
```

---

#### 4. HybridTerminationDetector (`code/detectors/hybrid_detector.py`)
**Status:** NEW for h-m3  
**Dependencies:** SymbolicSignalExtractor, typing

```python
class HybridTerminationDetector:
    """Three-signal hybrid detector with k-of-n voting."""
    
    def __init__(self, thresholds: dict, voting_k: int = 2):
        self.thresholds = thresholds
        self.voting_k = voting_k
        self.symbolic_extractor = SymbolicSignalExtractor()
    
    def extract_all_signals(self, result: dict) -> dict:
        """
        Extract all three signal types from experiment result.
        
        Args:
            result: From ExtendedTimeoutRunnerWithTree with:
                - confidence_variance: float
                - proof_states: list
                - search_tree: SearchTree
        
        Returns:
            {
                'confidence_variance': float,
                'state_collisions': int,
                'exponential_growth': float,
                'backtrack_freq': float
            }
        """
        ...
    
    def predict(self, signals: dict) -> bool:
        """
        Voting-based termination decision.
        
        Returns:
            True if should terminate (at least k of 3 signals trigger)
        """
        ...
    
    def _check_confidence_alert(self, signals: dict) -> bool:
        """variance > threshold."""
        ...
    
    def _check_symbolic_alert(self, signals: dict) -> bool:
        """collisions > thresh OR growth > thresh."""
        ...
    
    def _check_search_alert(self, signals: dict) -> bool:
        """backtrack_freq > threshold."""
        ...
```

---

#### 5. AblationFramework (`code/evaluation/ablation_framework.py`)
**Status:** NEW for h-m3  
**Dependencies:** HybridTerminationDetector, sklearn.metrics

```python
class AblationFramework:
    """Framework for evaluating 7 detector variants."""
    
    def __init__(self, thresholds: dict):
        self.thresholds = thresholds
        self.models = self._create_models()
    
    def _create_models(self) -> dict:
        """
        Create 7 detector variants.
        
        Returns:
            {
                'confidence_only': callable,
                'symbolic_only': callable,
                'search_only': callable,
                'conf_symb': callable,
                'conf_search': callable,
                'symb_search': callable,
                'hybrid_all': callable
            }
        """
        ...
    
    def evaluate_all_models(self, signals_list: list, ground_truth: list) -> dict:
        """
        Evaluate all models on dataset.
        
        Args:
            signals_list: List of signal dicts (one per theorem)
            ground_truth: List of timeout labels (1=timeout, 0=success)
        
        Returns:
            {
                model_name: {
                    'precision': float,
                    'recall': float,
                    'f1': float,
                    'predictions': list
                }
            }
        """
        ...
    
    def compute_metrics(self, predictions: list, ground_truth: list) -> dict:
        """Compute precision, recall, F1."""
        ...
```

---

#### 6. ThresholdSelector (`code/evaluation/threshold_selector.py`)
**Status:** NEW for h-m3  
**Dependencies:** numpy

```python
class ThresholdSelector:
    """Select thresholds from timeout group using median strategy."""
    
    def select_thresholds(self, timeout_signals: list) -> dict:
        """
        Select thresholds as median of timeout group for each signal.
        
        Args:
            timeout_signals: List of signal dicts from timeout theorems
        
        Returns:
            {
                'variance': float,
                'collisions': int,
                'growth': float,
                'backtrack': float
            }
        """
        ...
```

---

#### 7. AblationVisualizer (`code/visualization/ablation_visualizer.py`)
**Status:** NEW for h-m3  
**Dependencies:** matplotlib, seaborn

```python
class AblationVisualizer:
    """Visualize ablation study results."""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
    
    def plot_ablation_comparison_bar(self, metrics_by_model: dict) -> None:
        """MANDATORY: Bar chart comparing F1 scores across 7 models."""
        ...
    
    def plot_signal_distributions(self, signals_by_outcome: dict) -> None:
        """Box plots of each signal for success vs timeout groups."""
        ...
    
    def plot_correlation_scatter(self, signals_list: list, ground_truth: list) -> None:
        """Scatter plots showing correlation of each signal with timeout."""
        ...
    
    def plot_voting_analysis(self, voting_counts: dict) -> None:
        """Bar chart showing voting patterns (0/1/2/3 signals triggered)."""
        ...
    
    def plot_confusion_matrices(self, metrics_by_model: dict) -> None:
        """Confusion matrices for all models (grid layout)."""
        ...
```

---

#### 8. Main Experiment Script (`code/run_h_m3.py`)
**Status:** NEW (orchestrates h-m3 experiment)  
**Dependencies:** All above modules + h-m2

```python
def main():
    # REUSE h-m2 infrastructure
    runner = ExtendedTimeoutRunnerWithTree(timeout_seconds=300)
    
    # Load h-m1 results for ground truth
    h_m1_results = load_h_m1_results()
    
    # Re-run with tree tracking (or load h-m2 results if available)
    experiment_results = run_or_load_experiments()
    
    # NEW: Extract all signals
    hybrid_detector = HybridTerminationDetector(thresholds={})
    signals_list = [hybrid_detector.extract_all_signals(r) for r in experiment_results]
    
    # NEW: Select thresholds from timeout group
    timeout_signals = [s for s, r in zip(signals_list, experiment_results) if r['outcome'] == 1]
    selector = ThresholdSelector()
    thresholds = selector.select_thresholds(timeout_signals)
    
    # NEW: Evaluate 7 models
    ablation = AblationFramework(thresholds)
    ground_truth = [r['outcome'] for r in experiment_results]
    metrics_by_model = ablation.evaluate_all_models(signals_list, ground_truth)
    
    # NEW: Visualize ablation study
    viz = AblationVisualizer(output_dir='h-m3/figures')
    viz.plot_ablation_comparison_bar(metrics_by_model)
    viz.plot_signal_distributions(signals_list)
    viz.plot_correlation_scatter(signals_list, ground_truth)
    
    # Gate evaluation
    hybrid_f1 = metrics_by_model['hybrid_all']['f1']
    single_f1s = [metrics_by_model[m]['f1'] for m in ['confidence_only', 'symbolic_only', 'search_only']]
    gate_satisfied = all(hybrid_f1 > f1 for f1 in single_f1s)
    
    save_results(metrics_by_model, thresholds, gate_satisfied)
```

---

## File Organization

```
h-m3/
├── code/
│   ├── signals/
│   │   ├── __init__.py
│   │   └── symbolic_extractor.py       # NEW: Symbolic signals
│   ├── detectors/
│   │   ├── __init__.py
│   │   └── hybrid_detector.py          # NEW: 3-signal voting
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── ablation_framework.py       # NEW: 7-model comparison
│   │   └── threshold_selector.py       # NEW: Data-driven thresholds
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── ablation_visualizer.py      # NEW: Ablation plots
│   └── run_h_m3.py                      # NEW: Main experiment
├── results/
│   ├── h_m3_results.json                # Metrics by model
│   ├── thresholds.txt                   # Selected thresholds
│   └── signals_data.csv                 # All signals extracted
├── figures/
│   ├── ablation_comparison_bar.png      # MANDATORY
│   ├── signal_distributions.png
│   ├── correlation_scatter.png
│   ├── voting_analysis.png
│   └── confusion_matrices_grid.png
└── README.md

REUSED from h-m2/ (via import):
├── code/experiment/tree_tracker.py      # Tree tracking, state capture
├── code/models/confidence_extractor.py  # Variance extraction
└── code/analysis/divergence_classifier.py  # (for reference only)
```

---

## Epic Tasks

### Epic E1: Environment Setup [Priority: 100, Complexity: 5]
**Description:** Set up h-m3 folder structure and configure h-m2 imports

**Subtasks:**
- Create h-m3/code directory structure (signals/, detectors/, evaluation/)
- Configure Python path to import h-m2 modules
- Verify h-m2 modules accessible (SearchTree, ExtendedTimeoutRunnerWithTree)
- Create output directories (results/, figures/)
- Install dependencies (sklearn, scipy, numpy)

**Complexity Breakdown:**
- Module Size: 1/5
- Dependencies: 2/5 (h-m2 import setup)
- Algorithm: 0/5
- Integration: 2/5
- **Total: 5/20**

---

### Epic E2: Implement Symbolic Signal Extraction [Priority: 95, Complexity: 12]
**Description:** Create SymbolicSignalExtractor for state collisions and exponential growth

**Subtasks:**
- Implement state collision counting (reuse SearchTree.get_collision_count())
- Implement exponential growth fitting (numpy polyfit on log-transformed state sizes)
- Extract proof state sizes from LeanDojo states
- Test on h-m2 results
- Unit tests for edge cases (empty states, single state)

**Complexity Breakdown:**
- Module Size: 2/5 (new module)
- Dependencies: 2/5 (numpy, h-m2 SearchTree)
- Algorithm: 4/5 (exponential fitting)
- Integration: 4/5 (critical signal)
- **Total: 12/20**

---

### Epic E3: Implement Hybrid Termination Detector [Priority: 90, Complexity: 14]
**Description:** Create HybridTerminationDetector with 3-signal voting logic

**Subtasks:**
- Implement extract_all_signals() (confidence + symbolic + search)
- Implement voting logic (k-of-3 threshold)
- Implement individual alert checkers (confidence, symbolic, search)
- Calculate backtrack frequency from SearchTree
- Test voting logic with mock signals
- Unit tests for voting edge cases

**Complexity Breakdown:**
- Module Size: 3/5 (core module)
- Dependencies: 3/5 (h-m2 + symbolic extractor)
- Algorithm: 4/5 (voting logic)
- Integration: 4/5 (core mechanism)
- **Total: 14/20**

---

### Epic E4: Implement Threshold Selection [Priority: 85, Complexity: 8]
**Description:** Create ThresholdSelector using median strategy

**Subtasks:**
- Implement median calculation for each signal type
- Load h-m1 variance threshold (0.25) for reference
- Handle edge cases (empty timeout group)
- Validate thresholds on h-m2 results
- Document threshold values

**Complexity Breakdown:**
- Module Size: 2/5
- Dependencies: 1/5 (numpy only)
- Algorithm: 2/5 (median calculation)
- Integration: 3/5 (feeds into ablation)
- **Total: 8/20**

---

### Epic E5: Implement Ablation Framework [Priority: 80, Complexity: 16]
**Description:** Create AblationFramework for 7-model comparison

**Subtasks:**
- Implement _create_models() (7 detector variants)
- Implement single-signal detectors (confidence, symbolic, search)
- Implement pairwise detectors (conf+symb, conf+search, symb+search)
- Implement hybrid detector (k=2 voting)
- Implement evaluate_all_models() (run all on dataset)
- Implement compute_metrics() (precision, recall, F1)
- Test each detector variant independently

**Complexity Breakdown:**
- Module Size: 4/5 (complex module)
- Dependencies: 3/5 (hybrid detector, sklearn)
- Algorithm: 4/5 (7 variants + metrics)
- Integration: 5/5 (critical for hypothesis test)
- **Total: 16/20**

---

### Epic E6: Implement Ablation Visualization [Priority: 75, Complexity: 13]
**Description:** Create AblationVisualizer with 5 plot types

**Subtasks:**
- Implement plot_ablation_comparison_bar() (MANDATORY: F1 comparison)
- Implement plot_signal_distributions() (box plots by outcome)
- Implement plot_correlation_scatter() (4 subplots, one per signal)
- Implement plot_voting_analysis() (voting pattern bars)
- Implement plot_confusion_matrices() (grid of 7 models)

**Complexity Breakdown:**
- Module Size: 3/5 (multiple plots)
- Dependencies: 2/5 (matplotlib, seaborn)
- Algorithm: 3/5 (plot logic)
- Integration: 5/5 (critical for results)
- **Total: 13/20**

---

### Epic E7: Main Experiment Script [Priority: 70, Complexity: 15]
**Description:** Create run_h_m3.py orchestrating full experiment

**Subtasks:**
- Load h-m1 results for ground truth labels
- Re-run experiments with tree tracking (or load h-m2 results)
- Extract all signals using HybridTerminationDetector
- Select thresholds from timeout group
- Run ablation framework (7 models)
- Compute correlation metrics (Pearson, Spearman)
- Generate all visualizations
- Save results to JSON
- Evaluate gate condition (hybrid F1 > all single F1s)

**Complexity Breakdown:**
- Module Size: 3/5 (orchestration)
- Dependencies: 5/5 (all h-m3 + h-m2 modules)
- Algorithm: 2/5 (orchestration logic)
- Integration: 5/5 (coordinates entire experiment)
- **Total: 15/20**

---

### Epic E8: Results Interpretation [Priority: 65, Complexity: 6]
**Description:** Generate README with ablation analysis interpretation

**Subtasks:**
- Create README.md template
- Document threshold selection strategy
- Explain 7-model ablation design
- Provide result interpretation guide (gate pass/fail)
- Document signal combination rationale
- Include usage instructions

**Complexity Breakdown:**
- Module Size: 1/5
- Dependencies: 0/5
- Algorithm: 0/5
- Integration: 5/5 (ties to experiment)
- **Total: 6/20**

---

## Task Summary

| Epic ID | Name | Priority | Complexity | Type |
|---------|------|----------|------------|------|
| E1 | Environment Setup | 100 | 5 | setup |
| E2 | Implement Symbolic Signal Extraction | 95 | 12 | signals |
| E3 | Implement Hybrid Termination Detector | 90 | 14 | detector |
| E4 | Implement Threshold Selection | 85 | 8 | evaluation |
| E5 | Implement Ablation Framework | 80 | 16 | evaluation |
| E6 | Implement Ablation Visualization | 75 | 13 | visualization |
| E7 | Main Experiment Script | 70 | 15 | integration |
| E8 | Results Interpretation | 65 | 6 | documentation |

**Total Epic Tasks:** 8  
**Total Complexity:** 89/160  
**Average Complexity:** 11.1/20 (Medium)

**Distribution:** VeryHigh(18-20): [], High(14-17): [E3, E5, E7], Medium(9-13): [E2, E6], Low(4-8): [E1, E4, E8]

---

## Integration Points

### h-m2 Integration
```python
# Primary integration: Import h-m2 modules
import sys
from pathlib import Path

h_m2_path = Path(__file__).parent.parent.parent / "h-m2" / "code"
sys.path.insert(0, str(h_m2_path))

from experiment.tree_tracker import ExtendedTimeoutRunnerWithTree, SearchTree
from models.confidence_extractor import ConfidenceTrajectoryExtractor
```

### Data Flow
```
h-m1 Results (ground truth) → h-m3 Experiment
                                    ↓
h-m2 Runner (tree tracking) → Extract 3 Signal Types:
                                    - Confidence (h-m1)
                                    - Symbolic (NEW)
                                    - Search Tree (h-m2)
                                    ↓
                          Select Thresholds (median)
                                    ↓
                          7-Model Ablation Framework:
                          - 3 single-signal
                          - 3 pairwise
                          - 1 hybrid (k=2 voting)
                                    ↓
                          Evaluate Metrics (F1, precision, recall)
                                    ↓
                          Gate: hybrid_f1 > all_single_f1s
```

---

## Risk Mitigation

### Risk: Exponential growth fitting unstable
**Mitigation:** Use log-linear regression with error handling; fallback to state size variance if fit fails

### Risk: Insufficient divergent samples for threshold selection
**Mitigation:** Use h-m1 timeout group (37 samples) for threshold selection; adjust if needed

### Risk: h-m2 results not saved
**Mitigation:** Re-run experiments with tree tracking (~10-20% overhead vs h-m1); reuse ExtendedTimeoutRunnerWithTree

### Risk: All models perform similarly (no ablation difference)
**Mitigation:** This is acceptable for PoC (SHOULD_WORK gate); document as finding

---

## Quality Criteria

- [ ] All h-m2 modules successfully imported
- [ ] Symbolic signal extraction functional (collisions + growth)
- [ ] Hybrid detector voting logic tested
- [ ] All 7 models implemented and tested
- [ ] Threshold selection from timeout group working
- [ ] MANDATORY ablation comparison bar chart generated
- [ ] Gate condition evaluated correctly (hybrid F1 > all single F1s)
- [ ] Results saved to JSON with all metrics

---

## Notes

**Key Architectural Decision:** Maximize h-m2 reuse by importing tree tracking and confidence extraction. Add only:
- Symbolic signal extraction (20% new code)
- Hybrid voting logic (10% new code)
- Ablation framework (70% new code - largest component)

**Optimization:** If h-m2 saved full experiment results with search trees, h-m3 can skip re-running and directly extract signals. Otherwise, re-run with ExtendedTimeoutRunnerWithTree.

**Ablation Design Rationale:**
- Single-signal baselines: Test individual signal strength
- Pairwise combinations: Test 2-signal synergy
- Hybrid (k=2): Test 3-signal voting hypothesis
- Gate: Hybrid must outperform ALL single signals (strict test)

**Threshold Strategy:** Use median of timeout group for each signal (data-driven, no hyperparameter search). This is PoC-level; future work can optimize thresholds.
