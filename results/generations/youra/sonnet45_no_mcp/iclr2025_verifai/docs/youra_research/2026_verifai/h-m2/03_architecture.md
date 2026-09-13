# Architecture Specification: h-m2

**Date:** 2026-04-20  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM (Causal)  
**Architect:** Phase 3 Architecture Agent  
**Base Hypothesis:** h-m1 (COMPLETED, PASSED)

Applied: Incremental extension pattern - reuse h-m1 infrastructure, add divergence analysis layer

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** h-m1 validated infrastructure reusable  
**Analyzed Path:** h-m1/code/  
**Findings:** h-m1 implements full experiment pipeline (data loading, confidence extraction, variance analysis, visualization). h-m2 extends with search tree tracking and divergence classification.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual h-m1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| TheoremSampler | `from h_m1.code.data.loader import TheoremSampler` | `h-m1/code/data/loader.py` |
| ExtendedTimeoutRunner | `from h_m1.code.experiment.runner import ExtendedTimeoutRunner` | `h-m1/code/experiment/runner.py` |
| ConfidenceTrajectoryExtractor | `from h_m1.code.models.confidence_extractor import ConfidenceTrajectoryExtractor` | `h-m1/code/models/confidence_extractor.py` |
| ExperimentVisualizer | `from h_m1.code.visualization.visualizer import ExperimentVisualizer` | `h-m1/code/visualization/visualizer.py` |

**Verified from:** h-m1/code/ (actual implementation)

---

## System Overview

**Purpose:** Test divergence-confidence link by subdividing h-m1 timeout group into divergent vs difficult proofs.

**Architecture Tier:** MECHANISM (PoC) - Extend h-m1 with divergence classification

**Components:**
- Data loading: REUSE h-m1 (100% - same theorems)
- Model execution: EXTEND h-m1 (add search tree tracking)
- Confidence extraction: REUSE h-m1 (100% - same variance calculation)
- Divergence classification: NEW (state collision + backtrack detection)
- Timeout subgroup analysis: NEW (divergent vs difficult comparison)
- Visualization: EXTEND h-m1 (add divergence plots)

---

## Module Specifications

### REUSED MODULES (No Modifications)

#### 1. DataLoader (`h-m1/code/data/loader.py`)
**Status:** REUSE AS-IS  
**Justification:** Same 100 theorems from h-m1

#### 2. ConfidenceExtractor (`h-m1/code/models/confidence_extractor.py`)
**Status:** REUSE AS-IS  
**Justification:** Same variance calculation validated in h-m1

---

### EXTENDED MODULES

#### 3. ProofRunner (`code/experiment/runner_with_tree.py`)
**Status:** EXTEND h-m1 runner  
**Dependencies:** h-m1.ExtendedTimeoutRunner, lean_dojo

```python
from h_m1.code.experiment.runner import ExtendedTimeoutRunner

class ExtendedTimeoutRunnerWithTree(ExtendedTimeoutRunner):
    """Extends h-m1 runner to capture search tree for divergence analysis."""
    
    def __init__(self, timeout_seconds: int = 300, confidence_window: int = 15):
        super().__init__(timeout_seconds, confidence_window)
    
    def run_experiment(self, theorem) -> dict:
        """
        Run experiment with search tree tracking.
        
        Returns:
            result with additional fields:
            - 'search_tree': LeanDojo search tree structure
            - 'proof_states': list of visited states
        """
        ...
    
    def _track_search_tree(self, dojo_session) -> tuple:
        """
        Capture search tree and state sequence.
        
        Returns:
            (search_tree, proof_states)
        """
        ...
```

**Complexity:** Medium (10/20) - Add tracking layer to existing runner

---

### NEW MODULES

#### 4. DivergenceClassifier (`code/analysis/divergence_classifier.py`)
**Status:** NEW for h-m2  
**Dependencies:** numpy, typing

```python
class DivergenceClassifier:
    """Classify timeout proofs as divergent vs difficult."""
    
    def __init__(self, collision_threshold: int = 2, backtrack_threshold: int = 5):
        self.collision_threshold = collision_threshold
        self.backtrack_threshold = backtrack_threshold
    
    def classify_timeout(self, proof_states: list, search_tree) -> tuple:
        """
        Classify single timeout as divergent or difficult.
        
        Args:
            proof_states: list of visited proof states
            search_tree: LeanDojo search tree structure
        
        Returns:
            (is_divergent, markers)
            markers: {'state_collisions': int, 'backtrack_frequency': int}
        """
        ...
    
    def _detect_state_collisions(self, proof_states: list) -> int:
        """Count hash collisions (cyclic behavior)."""
        ...
    
    def _count_backtracks(self, search_tree) -> int:
        """Count abandoned branches (search instability)."""
        ...
```

**Complexity:** Medium (11/20) - New classification logic with symbolic analysis

---

#### 5. TimeoutSubgroupAnalyzer (`code/analysis/timeout_subgroup_analyzer.py`)
**Status:** NEW for h-m2  
**Dependencies:** numpy, scipy

```python
class TimeoutSubgroupAnalyzer:
    """Analyze variance differences within timeout group (divergent vs difficult)."""
    
    def analyze_variance_by_divergence(self, timeout_results: list) -> dict:
        """
        Subdivide timeout group and compare variance.
        
        Args:
            timeout_results: list of timeout experiments with divergence classification
        
        Returns:
            analysis: {
                'divergent': {'count', 'mean_variance', 'std_variance'},
                'difficult': {'count', 'mean_variance', 'std_variance'},
                'difference': float,
                'gate_satisfied': bool
            }
        """
        ...
    
    def evaluate_gate(self, mean_divergent: float, mean_difficult: float) -> bool:
        """Test: mean_variance(divergent) > mean_variance(difficult)."""
        ...
```

**Complexity:** Medium (9/20) - Subgroup comparison logic

---

#### 6. DivergenceVisualizer (`code/visualization/divergence_visualizer.py`)
**Status:** EXTEND h-m1 visualizer  
**Dependencies:** matplotlib, seaborn, h-m1.ExperimentVisualizer

```python
from h_m1.code.visualization.visualizer import ExperimentVisualizer

class DivergenceComparisonVisualizer(ExperimentVisualizer):
    """Extends h-m1 visualizer with divergence-specific plots."""
    
    def plot_timeout_subgroup_comparison_bar(self, divergent_var: float, difficult_var: float) -> None:
        """MANDATORY: Bar chart comparing divergent vs difficult variance."""
        ...
    
    def plot_variance_by_divergence_boxplot(self, divergent_vars: list, difficult_vars: list) -> None:
        """RECOMMENDED: Box plot of variance distributions."""
        ...
    
    def plot_divergence_marker_scatter(self, collisions: list, backtracks: list, variances: list) -> None:
        """RECOMMENDED: Scatter plots (markers vs variance)."""
        ...
    
    def plot_divergence_classification_pie(self, divergent_count: int, difficult_count: int) -> None:
        """RECOMMENDED: Pie chart of timeout classification."""
        ...
```

**Complexity:** Medium (12/20) - Multiple new plot types

---

#### 7. Main Experiment Script (`code/run_h_m2.py`)
**Status:** NEW (orchestrates h-m2 experiment)  
**Dependencies:** All above modules

```python
def main():
    # REUSE h-m1 infrastructure
    sampler = TheoremSampler.load_from_h_m1()  # Same 100 theorems
    
    # EXTEND with search tree tracking
    runner = ExtendedTimeoutRunnerWithTree(timeout_seconds=300)
    
    # NEW: Divergence analysis
    classifier = DivergenceClassifier(collision_threshold=2, backtrack_threshold=5)
    subgroup_analyzer = TimeoutSubgroupAnalyzer()
    
    # Run experiments (or load h-m1 results + re-run with tree tracking)
    results = run_or_load_results()
    
    # Filter timeout group
    timeout_results = [r for r in results if r['outcome'] == 1]
    
    # NEW: Classify each timeout
    for result in timeout_results:
        is_divergent, markers = classifier.classify_timeout(
            result['proof_states'], 
            result['search_tree']
        )
        result['is_divergent'] = is_divergent
        result['divergence_markers'] = markers
    
    # NEW: Subgroup comparison
    analysis = subgroup_analyzer.analyze_variance_by_divergence(timeout_results)
    
    # EXTEND: Visualize subgroup comparison
    visualizer = DivergenceComparisonVisualizer(output_dir='h-m2/figures')
    visualizer.plot_timeout_subgroup_comparison_bar(
        analysis['divergent']['mean_variance'],
        analysis['difficult']['mean_variance']
    )
    
    # Save results
    save_results(analysis)
    
    print(f"Gate Satisfied: {analysis['gate_satisfied']}")
```

**Complexity:** Low (7/20) - Orchestration script

---

## File Organization

```
h-m2/
├── code/
│   ├── experiment/
│   │   └── runner_with_tree.py        # EXTEND h-m1 runner
│   ├── analysis/
│   │   ├── divergence_classifier.py   # NEW: Divergence detection
│   │   └── timeout_subgroup_analyzer.py  # NEW: Subgroup analysis
│   ├── visualization/
│   │   └── divergence_visualizer.py   # EXTEND h-m1 visualizer
│   └── run_h_m2.py                    # NEW: Main experiment script
├── results/
│   ├── divergence_classification.json
│   ├── timeout_subgroup_analysis.json
│   └── markers_data.csv
├── figures/
│   ├── timeout_subgroup_comparison_bar.png  # MANDATORY
│   ├── variance_by_divergence_boxplot.png   # RECOMMENDED
│   ├── collision_variance_scatter.png       # RECOMMENDED
│   ├── backtrack_variance_scatter.png       # RECOMMENDED
│   └── divergence_classification_pie.png    # RECOMMENDED
└── README.md

REUSED from h-m1/ (via import):
├── code/data/loader.py
├── code/models/confidence_extractor.py
├── code/visualization/visualizer.py (base class)
└── code/config.py
```

---

## Epic Tasks

### Epic E1: Environment Setup [Priority: 100, Complexity: 5]
**Description:** Set up h-m2 folder structure and configure h-m1 imports

**Subtasks:**
- Create h-m2/code directory structure
- Configure Python path to import h-m1 modules
- Verify h-m1 modules accessible
- Create output directories (results/, figures/)
- Install dependencies (lean_dojo, scipy)

**Complexity Breakdown:**
- Module Size: 1/5
- Dependencies: 2/5 (h-m1 import setup)
- Algorithm: 0/5
- Integration: 2/5
- **Total: 5/20**

---

### Epic E2: Extend Proof Runner with Search Tree Tracking [Priority: 90, Complexity: 13]
**Description:** Create ExtendedTimeoutRunnerWithTree extending h-m1 runner

**Subtasks:**
- Inherit from h-m1 ExtendedTimeoutRunner
- Implement search tree capture during proof search
- Track proof state sequences
- Store search tree structure for analysis
- Test on sample theorems

**Complexity Breakdown:**
- Module Size: 2/5 (extend existing)
- Dependencies: 3/5 (h-m1 + LeanDojo API)
- Algorithm: 3/5 (tree tracking logic)
- Integration: 5/5 (critical for divergence detection)
- **Total: 13/20**

---

### Epic E3: Implement Divergence Classifier [Priority: 85, Complexity: 14]
**Description:** Create DivergenceClassifier for timeout classification

**Subtasks:**
- Implement state collision detection (hash-based)
- Implement backtrack counting from search tree
- Define classification thresholds (collision > 2 OR backtrack > 5)
- Test classifier on mock data
- Unit tests for edge cases

**Complexity Breakdown:**
- Module Size: 3/5 (new complex module)
- Dependencies: 2/5 (numpy, lean_dojo)
- Algorithm: 5/5 (symbolic analysis logic)
- Integration: 4/5 (core mechanism)
- **Total: 14/20**

---

### Epic E4: Implement Timeout Subgroup Analysis [Priority: 80, Complexity: 10]
**Description:** Create TimeoutSubgroupAnalyzer for variance comparison

**Subtasks:**
- Implement variance grouping by divergence classification
- Calculate mean variance for divergent vs difficult subgroups
- Implement gate evaluation logic
- Compute statistics (counts, std dev)
- Unit tests for group separation

**Complexity Breakdown:**
- Module Size: 2/5
- Dependencies: 1/5 (numpy only)
- Algorithm: 3/5 (group comparison)
- Integration: 4/5 (gate evaluation)
- **Total: 10/20**

---

### Epic E5: Extend Visualization [Priority: 75, Complexity: 13]
**Description:** Create DivergenceComparisonVisualizer with new plots

**Subtasks:**
- Inherit from h-m1 ExperimentVisualizer
- Implement plot_timeout_subgroup_comparison_bar() (MANDATORY)
- Implement plot_variance_by_divergence_boxplot()
- Implement plot_divergence_marker_scatter() (collisions, backtracks)
- Implement plot_divergence_classification_pie()

**Complexity Breakdown:**
- Module Size: 3/5 (multiple plots)
- Dependencies: 2/5 (matplotlib, h-m1 base)
- Algorithm: 3/5 (plot logic)
- Integration: 5/5 (critical for results)
- **Total: 13/20**

---

### Epic E6: Main Experiment Script [Priority: 70, Complexity: 11]
**Description:** Create run_h_m2.py orchestrating the experiment

**Subtasks:**
- Set up h-m1 module imports
- Implement experiment orchestration
- Add h-m1 result reuse option (if search trees saved)
- Integrate divergence classification into pipeline
- Integrate subgroup analysis
- Save results to JSON

**Complexity Breakdown:**
- Module Size: 2/5
- Dependencies: 4/5 (all h-m2 + h-m1 modules)
- Algorithm: 1/5 (orchestration)
- Integration: 4/5 (coordinates all components)
- **Total: 11/20**

---

### Epic E7: Results Interpretation [Priority: 65, Complexity: 5]
**Description:** Generate README with divergence analysis interpretation

**Subtasks:**
- Create README.md template
- Document h-m1 reuse strategy
- Explain divergence markers and classification thresholds
- Provide result interpretation guide (gate pass/fail)
- Document divergence vs difficulty distinction

**Complexity Breakdown:**
- Module Size: 1/5
- Dependencies: 0/5
- Algorithm: 0/5
- Integration: 4/5 (ties to experiment)
- **Total: 5/20**

---

## Task Summary

| Epic ID | Name | Priority | Complexity | Type |
|---------|------|----------|------------|------|
| E1 | Environment Setup | 100 | 5 | setup |
| E2 | Extend Proof Runner with Tree Tracking | 90 | 13 | model |
| E3 | Implement Divergence Classifier | 85 | 14 | analysis |
| E4 | Implement Timeout Subgroup Analysis | 80 | 10 | analysis |
| E5 | Extend Visualization | 75 | 13 | visualization |
| E6 | Main Experiment Script | 70 | 11 | integration |
| E7 | Results Interpretation | 65 | 5 | documentation |

**Total Epic Tasks:** 7  
**Total Complexity:** 71/140  
**Average Complexity:** 10.1/20 (Moderate)

**Distribution:** VeryHigh(18-20): [], High(14-17): [E3], Medium(9-13): [E2, E4, E5, E6], Low(4-8): [E1, E7]

---

## Integration Points

### h-m1 Integration
```python
# Primary integration: Import h-m1 modules
import sys
sys.path.append('../h-m1')

from h_m1.code.data.loader import TheoremSampler
from h_m1.code.experiment.runner import ExtendedTimeoutRunner
from h_m1.code.models.confidence_extractor import ConfidenceTrajectoryExtractor
from h_m1.code.visualization.visualizer import ExperimentVisualizer
```

### Data Flow
```
h-m1 Theorems → h-m2 Runner (+ tree tracking) → Confidence + Search Trees
                                                          ↓
                                            Divergence Classification (NEW)
                                                          ↓
                                            Timeout Subgroup Analysis (NEW)
                                                          ↓
                                          Divergence Visualization
```

---

## Risk Mitigation

### Risk: Search tree API unavailable in LeanDojo
**Mitigation:** Verify Dojo search tree API; fallback to state-sequence-only if needed (collision detection works without full tree)

### Risk: Divergence thresholds too arbitrary
**Mitigation:** This is PoC - heuristic thresholds acceptable; document as limitation

### Risk: Insufficient divergent samples
**Mitigation:** If < 10 divergent timeouts, adjust thresholds or note as limitation in results

### Risk: h-m1 results missing search trees
**Mitigation:** Re-run experiments with tree tracking (adds ~10-20% overhead)

---

## Quality Criteria

- [ ] All h-m1 modules successfully imported
- [ ] Search tree tracking functional
- [ ] Divergence classification tested on mock data
- [ ] Timeout subgroups correctly separated
- [ ] MANDATORY bar chart generated
- [ ] Gate condition evaluated correctly
- [ ] Results saved to JSON with divergence markers

---

## Notes

**Key Architectural Decision:** Maximize h-m1 reuse by importing modules and extending only where needed (search tree tracking, divergence classification). This ensures:
- Consistency with validated h-m1 variance methodology
- Controlled comparison (only divergence layer added)
- Minimal code duplication

**Optimization:** If h-m1 saved search trees or can be re-run quickly, h-m2 can focus on divergence analysis. Otherwise, re-run experiments with tree tracking enabled (~10-20% overhead vs h-m1).

**Divergence Detection Rationale:** 
- State collisions (hash-based) detect cyclic patterns
- Backtrack frequency detects search instability
- Combined thresholds classify divergence vs difficulty
- PoC-level heuristics (refinement in future hypothesis if validated)
