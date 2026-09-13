# Architecture Specification: h-m1

**Date:** 2026-04-20  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM (Causal)  
**Architect:** Phase 3 Orchestrator  
**Base Hypothesis:** h-e1

Applied: Incremental architecture pattern - extend existing codebase with minimal modifications

---

## Codebase Analysis (Serena)

**Project Type:** Incremental (extends h-e1)  
**Status:** Reuse h-e1 validated infrastructure  
**Analyzed Path:** h-e1/code/  
**Findings:** 
- h-e1 architecture validated and operational
- All core modules reusable (DataLoader, ProofRunner, ConfidenceExtractor)
- Only analysis component needs modification (derivative → variance + group comparison)

**Reuse Strategy:**
- 100% reuse: DataLoader, ProofRunner, Configuration
- 95% reuse: ConfidenceExtractor (add variance method)
- 80% reuse: Visualizer (add group comparison plots)
- NEW: GroupAnalyzer for variance comparison

---

## External Dependencies

### From h-e1 (Verified Import Paths)
```python
# Verified from h-e1/code/ structure
from h_e1.code.data.loader import TheoremSampler
from h_e1.code.experiment.runner import ExtendedTimeoutRunner
from h_e1.code.models.confidence_extractor import ConfidenceTrajectoryExtractor
from h_e1.code.visualization.visualizer import ExperimentVisualizer
from h_e1.code.config import ExperimentConfig
```

**Import Setup:**
```python
import sys
sys.path.append('../h-e1')  # Add h-e1 to Python path
```

---

## System Overview

**Purpose:** Test geometric interpretation of confidence by comparing variance between successful and timeout proofs.

**Architecture Tier:** MECHANISM (PoC) - Extend h-e1 with group comparison analysis

**Components:**
- Data loading: REUSE h-e1 (same 100 theorems)
- Model execution: REUSE h-e1 (same timeout protocol)
- Confidence extraction: EXTEND h-e1 (add variance calculation)
- Group analysis: NEW (variance comparison)
- Visualization: EXTEND h-e1 (add group plots)

---

## Module Specifications

### REUSED MODULES (No Modifications)

#### 1. DataLoader (`h-e1/code/data/loader.py`)
**Status:** REUSE AS-IS  
**Justification:** Same 100 theorems from h-e1

#### 2. ProofRunner (`h-e1/code/experiment/runner.py`)
**Status:** REUSE AS-IS  
**Justification:** Same extended-timeout protocol (300s)

#### 3. Configuration (`h-e1/code/config.py`)
**Status:** REUSE AS-IS  
**Justification:** Same experimental settings

### EXTENDED MODULES

#### 4. ConfidenceExtractor (`code/models/variance_analyzer.py`)
**Status:** EXTEND h-e1 extractor  
**Dependencies:** h-e1.ConfidenceTrajectoryExtractor, numpy

```python
from h_e1.code.models.confidence_extractor import ConfidenceTrajectoryExtractor
import numpy as np

class VarianceAnalyzer(ConfidenceTrajectoryExtractor):
    """Extends h-e1 extractor to compute variance for h-m1."""
    
    def __init__(self, window_size: int = 15):
        super().__init__(window_size)
    
    def compute_variance(self, entropies: list) -> float:
        """
        Compute confidence variance (std dev of entropy trajectory).
        
        Args:
            entropies: Entropy values over proof steps
        
        Returns:
            variance: Standard deviation of entropies
        """
        if len(entropies) < 2:
            return 0.0
        return np.std(entropies)
```

**Complexity:** Low (5/20) - Simple extension of existing class

---

### NEW MODULES

#### 5. GroupAnalyzer (`code/analysis/group_analyzer.py`)
**Status:** NEW for h-m1  
**Dependencies:** numpy, typing

```python
class VarianceGroupAnalyzer:
    """Analyze variance differences between successful and timeout proofs."""
    
    def analyze_by_outcome(self, results: list) -> dict:
        """
        Compare mean variance between outcome groups.
        
        Args:
            results: List of experiment results with 'variance' and 'outcome' fields
        
        Returns:
            Analysis results with group statistics and gate evaluation
        """
        ...
    
    def evaluate_gate(self, mean_success: float, mean_timeout: float) -> bool:
        """
        Test gate condition: successful proofs have lower variance.
        
        Args:
            mean_success: Mean variance for successful proofs
            mean_timeout: Mean variance for timeout proofs
        
        Returns:
            True if mean_success < mean_timeout
        """
        ...
```

**Complexity:** Medium (8/20) - New analysis logic for group comparison

---

#### 6. GroupVisualizer (`code/visualization/group_visualizer.py`)
**Status:** EXTEND h-e1 visualizer  
**Dependencies:** matplotlib, seaborn, numpy, h-e1.ExperimentVisualizer

```python
from h_e1.code.visualization.visualizer import ExperimentVisualizer

class GroupComparisonVisualizer(ExperimentVisualizer):
    """Extends h-e1 visualizer with group comparison plots."""
    
    def plot_variance_comparison_bar(self, mean_success: float, mean_timeout: float) -> None:
        """MANDATORY: Bar chart comparing mean variance (gate metric)."""
        ...
    
    def plot_variance_distributions(self, success_vars: list, timeout_vars: list) -> None:
        """RECOMMENDED: Histogram of variance distributions by group."""
        ...
    
    def plot_variance_boxplot(self, success_vars: list, timeout_vars: list) -> None:
        """RECOMMENDED: Box plot showing quartiles for each group."""
        ...
    
    def plot_trajectory_examples(self, stable_examples: list, unstable_examples: list) -> None:
        """RECOMMENDED: Example confidence trajectories (stable vs unstable)."""
        ...
```

**Complexity:** Medium (9/20) - Multiple plot types for group comparison

---

#### 7. Main Experiment Script (`code/run_h_m1.py`)
**Status:** NEW (orchestrates h-m1 experiment)  
**Dependencies:** All above modules

```python
def main():
    # REUSE h-e1 infrastructure
    sampler = TheoremSampler.load_from_h_e1()  # Same 100 theorems
    runner = ExtendedTimeoutRunner(timeout_seconds=300)
    
    # EXTEND with variance analysis
    variance_analyzer = VarianceAnalyzer(window_size=15)
    group_analyzer = VarianceGroupAnalyzer()
    
    # Run experiments (or load h-e1 results)
    results = run_or_load_results()
    
    # NEW: Group comparison analysis
    analysis = group_analyzer.analyze_by_outcome(results)
    
    # EXTEND: Visualize group comparison
    visualizer = GroupComparisonVisualizer(output_dir='h-m1/figures')
    visualizer.plot_variance_comparison_bar(
        analysis['success_variance_mean'],
        analysis['timeout_variance_mean']
    )
    
    # Save results
    save_results(analysis)
    
    print(f"Gate Satisfied: {analysis['gate_satisfied']}")
```

**Complexity:** Low (6/20) - Orchestration script

---

## File Organization

```
h-m1/
├── code/
│   ├── models/
│   │   └── variance_analyzer.py       # EXTEND h-e1 extractor
│   ├── analysis/
│   │   └── group_analyzer.py          # NEW: Group comparison
│   ├── visualization/
│   │   └── group_visualizer.py        # EXTEND h-e1 visualizer
│   └── run_h_m1.py                    # NEW: Main experiment script
├── results/
│   ├── variance_analysis.json
│   └── group_comparison.json
├── figures/
│   ├── variance_comparison_bar.png    # MANDATORY
│   ├── variance_distributions.png     # RECOMMENDED
│   ├── variance_boxplot.png           # RECOMMENDED
│   └── trajectory_examples.png        # RECOMMENDED
└── README.md

REUSED from h-e1/ (via import):
├── code/data/loader.py
├── code/experiment/runner.py
├── code/models/confidence_extractor.py (base class)
├── code/visualization/visualizer.py (base class)
└── code/config.py
```

---

## Epic Tasks

### Epic E1: Environment Setup [Priority: 100, Complexity: 4]
**Description:** Set up h-m1 folder structure and import h-e1 dependencies

**Subtasks:**
- Create h-m1/code directory structure
- Configure Python path to import h-e1 modules
- Verify h-e1 modules are accessible
- Create output directories (results/, figures/)

**Complexity Breakdown:**
- Module Size: 1/5 (minimal setup)
- Dependencies: 1/5 (h-e1 import)
- Algorithm: 0/5 (no algorithm)
- Integration: 2/5 (Python path setup)
- **Total: 4/20**

---

### Epic E2: Extend Confidence Extraction [Priority: 90, Complexity: 8]
**Description:** Create VarianceAnalyzer extending h-e1's ConfidenceTrajectoryExtractor

**Subtasks:**
- Inherit from h-e1 ConfidenceTrajectoryExtractor
- Implement compute_variance() method
- Test variance calculation on sample trajectories
- Verify consistency with h-e1 derivative (both use np.std)

**Complexity Breakdown:**
- Module Size: 1/5 (small extension)
- Dependencies: 2/5 (h-e1 inheritance)
- Algorithm: 2/5 (variance calculation)
- Integration: 3/5 (base class integration)
- **Total: 8/20**

---

### Epic E3: Implement Group Analysis [Priority: 85, Complexity: 12]
**Description:** Create GroupAnalyzer for variance comparison between outcome groups

**Subtasks:**
- Implement analyze_by_outcome() method
- Separate results into successful vs timeout groups
- Calculate mean variance for each group
- Implement evaluate_gate() method
- Unit tests for group separation and statistics

**Complexity Breakdown:**
- Module Size: 2/5 (new module)
- Dependencies: 1/5 (numpy only)
- Algorithm: 4/5 (group comparison logic)
- Integration: 5/5 (critical analysis component)
- **Total: 12/20**

---

### Epic E4: Extend Visualization [Priority: 80, Complexity: 11]
**Description:** Create GroupComparisonVisualizer with group comparison plots

**Subtasks:**
- Inherit from h-e1 ExperimentVisualizer
- Implement plot_variance_comparison_bar() (MANDATORY)
- Implement plot_variance_distributions()
- Implement plot_variance_boxplot()
- Implement plot_trajectory_examples()

**Complexity Breakdown:**
- Module Size: 2/5 (multiple plot methods)
- Dependencies: 2/5 (matplotlib, h-e1 base)
- Algorithm: 3/5 (plot logic)
- Integration: 4/5 (base class + output management)
- **Total: 11/20**

---

### Epic E5: Main Experiment Script [Priority: 75, Complexity: 10]
**Description:** Create run_h_m1.py orchestrating the experiment

**Subtasks:**
- Set up h-e1 module imports
- Implement experiment orchestration logic
- Add h-e1 result reuse option (load saved trajectories)
- Integrate all components (analyzer, visualizer)
- Save results to JSON

**Complexity Breakdown:**
- Module Size: 2/5 (orchestration script)
- Dependencies: 3/5 (all h-m1 + h-e1 modules)
- Algorithm: 1/5 (simple orchestration)
- Integration: 4/5 (coordinates all components)
- **Total: 10/20**

---

### Epic E6: Results Interpretation [Priority: 70, Complexity: 5]
**Description:** Generate README with results interpretation and gate evaluation

**Subtasks:**
- Create README.md template
- Document h-e1 reuse strategy
- Explain variance metric and gate condition
- Provide result interpretation guide (gate pass/fail)

**Complexity Breakdown:**
- Module Size: 1/5 (documentation)
- Dependencies: 0/5 (no code deps)
- Algorithm: 0/5 (no algorithm)
- Integration: 4/5 (ties to overall experiment)
- **Total: 5/20**

---

## Task Summary

| Epic ID | Name | Priority | Complexity | Type |
|---------|------|----------|------------|------|
| E1 | Environment Setup | 100 | 4 | setup |
| E2 | Extend Confidence Extraction | 90 | 8 | model |
| E3 | Implement Group Analysis | 85 | 12 | analysis |
| E4 | Extend Visualization | 80 | 11 | visualization |
| E5 | Main Experiment Script | 75 | 10 | integration |
| E6 | Results Interpretation | 70 | 5 | documentation |

**Total Epic Tasks:** 6  
**Total Complexity:** 50/120  
**Complexity Level:** Moderate (incremental experiment with code reuse)

---

## Integration Points

### h-e1 Integration
```python
# Primary integration: Import h-e1 modules
import sys
sys.path.append('../h-e1')

from h_e1.code.data.loader import TheoremSampler
from h_e1.code.experiment.runner import ExtendedTimeoutRunner
from h_e1.code.models.confidence_extractor import ConfidenceTrajectoryExtractor
from h_e1.code.visualization.visualizer import ExperimentVisualizer
```

### Data Flow
```
h-e1 Theorems → h-e1 Runner → Confidence Trajectories
                                        ↓
                              h-m1 Variance Analyzer
                                        ↓
                              Group Analysis (NEW)
                                        ↓
                        Variance Comparison Visualization
```

---

## Risk Mitigation

### Risk: h-e1 import path issues
**Mitigation:** Use relative path import with sys.path.append, verify in setup task

### Risk: h-e1 results not available
**Mitigation:** Fallback to re-running experiments if saved trajectories unavailable

### Risk: Complexity underestimated
**Mitigation:** Most complexity already validated in h-e1; h-m1 adds minimal new logic

---

## Quality Criteria

- [ ] All h-e1 modules successfully imported
- [ ] Variance calculation matches h-e1 derivative (both use np.std)
- [ ] Group comparison logic tested
- [ ] MANDATORY bar chart generated
- [ ] Gate condition evaluated correctly
- [ ] Results saved to JSON with group statistics

---

## Notes

**Key Architectural Decision:** Maximize h-e1 reuse by importing modules rather than copying code. This ensures:
- Consistency with validated h-e1 implementation
- Minimal code duplication
- Controlled comparison (only analysis metric changes)

**Optimization:** If h-e1 saved confidence trajectories, h-m1 can skip experiment execution and directly compute variance from saved entropies, reducing runtime from hours to minutes.
