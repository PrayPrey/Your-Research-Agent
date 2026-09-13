# Product Requirements Document: H-M2 Divergence-Confidence Link

**Date:** 2026-04-20  
**Author:** Phase 3 Orchestrator  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM (Causal)  
**Status:** Planning  
**Base Hypothesis:** h-m1 (COMPLETED, PASSED)

---

## Executive Summary

This PRD specifies implementation requirements for testing whether confidence instability specifically signals divergence in neural theorem proving. Building on h-m1's validated finding (mean_variance_success=0.095 < mean_variance_timeout=0.294), h-m2 investigates WHY timeouts have high variance by testing whether diverging searches show higher variance than difficult searches.

**Success Criteria:** Divergent timeouts show higher variance than difficult timeouts (SHOULD_WORK gate)

**Reuse Strategy:** Extend h-m1 infrastructure (dataset, model, variance analysis) with divergence classification layer.

---

## Problem Statement

### Research Question
Is high confidence variance specifically linked to divergence (cyclic, non-terminating searches) rather than general difficulty?

### Hypothesis
When proof search diverges into non-terminating regions, if proof states become unfamiliar to LLM, then confidence instability (high variance in entropy) occurs, because the model detects distribution shift similar to perplexity in language models.

### Gate Condition
- **Type:** SHOULD_WORK
- **Pass:** mean_variance(divergent) > mean_variance(difficult)
- **Fail:** Document limitation, continue to next hypothesis

### Experiment Type
MECHANISM (PoC) - Tests causal mechanism for divergence detection, direction-based validation (no p-value required for PoC)

---

## Functional Requirements

### FR-1: Reuse h-m1 Dataset and Timeout Infrastructure
**Priority:** CRITICAL  
**Reuse Level:** 100%

**Requirements:**
- Reuse same 100 theorems from h-m1 (controlled comparison)
- Same LeanDojo Benchmark source
- Same extended timeout: 300s per theorem
- Same random seed (42) for reproducibility
- Focus analysis on timeout group from h-m1

**Rationale:** Controlled experiment - subdivide h-m1's timeout group by divergence classification.

**Source:** h-m1/code/data/loader.py (REUSE AS-IS)

### FR-2: Reuse h-m1 Confidence Variance Analysis
**Priority:** CRITICAL  
**Reuse Level:** 100%

**Requirements:**
- Reuse h-m1 confidence extraction code (entropy trajectory, first 15 steps)
- Reuse h-m1 variance calculation (std dev of entropy)
- Same model: LeanDojo ReProver (pre-trained, no modifications)
- Same proof search strategy: best-first search

**Rationale:** Variance metric validated in h-m1 - proven methodology.

**Source:** h-m1/code/models/confidence_extractor.py (REUSE AS-IS)

### FR-3: Add Search Tree Tracking
**Priority:** CRITICAL  
**New Component:** YES

**Requirements:**
- Enable LeanDojo search tree tracking during proof search
- Capture: state sequences, branching points, backtrack events
- Extract: state hashes for collision detection
- Track: abandoned branches for backtrack frequency

**Implementation:**
```python
class SearchTreeTracker:
    def __init__(self):
        self.state_hashes = []
        self.backtrack_count = 0
    
    def track_state(self, proof_state):
        """Track state hash for collision detection"""
        state_hash = hash(str(proof_state))
        self.state_hashes.append(state_hash)
    
    def track_backtrack(self, search_tree_node):
        """Count backtrack events from search tree"""
        if len(search_tree_node.children) > 1:
            abandoned = sum(1 for c in search_tree_node.children if c.is_abandoned)
            self.backtrack_count += abandoned
    
    def get_divergence_markers(self):
        """Extract divergence markers from tracked data"""
        collisions = len(self.state_hashes) - len(set(self.state_hashes))
        return {
            'state_collisions': collisions,
            'backtrack_frequency': self.backtrack_count
        }
```

**Source:** NEW - Extend h-m1/code/experiment/runner.py with tracking

### FR-4: Divergence Classification
**Priority:** CRITICAL  
**New Component:** YES

**Requirements:**
- Classify each timeout as divergent or difficult
- Divergence markers: state hash collisions (cyclic behavior), high backtrack frequency (search instability)
- Thresholds: collisions > 2 OR backtracks > 5 → divergent
- Apply only to timeout group from h-m1

**Pseudo-code:**
```python
class DivergenceClassifier:
    def __init__(self):
        self.collision_threshold = 2
        self.backtrack_threshold = 5
    
    def classify_timeout(self, proof_states, search_tree):
        """
        Classify timeout as divergent vs difficult.
        
        Divergent: Cyclic patterns, repeated states, high backtracks
        Difficult: Valid exploration, challenging but not cyclic
        """
        # Extract markers
        state_hashes = [hash(str(s)) for s in proof_states]
        collisions = len(state_hashes) - len(set(state_hashes))
        backtracks = self._count_backtracks(search_tree)
        
        # Classification rule
        is_divergent = (
            collisions > self.collision_threshold or
            backtracks > self.backtrack_threshold
        )
        
        return {
            'is_divergent': is_divergent,
            'markers': {
                'state_collisions': collisions,
                'backtrack_frequency': backtracks
            }
        }
    
    def _count_backtracks(self, search_tree):
        """Count abandoned branches in search tree"""
        backtrack_count = 0
        for node in search_tree.nodes:
            if len(node.children) > 1:
                abandoned = sum(1 for child in node.children if child.is_abandoned)
                backtrack_count += abandoned
        return backtrack_count
```

**Source:** NEW - h-m2/code/analysis/divergence_classifier.py

### FR-5: Timeout Group Subdivision Analysis
**Priority:** CRITICAL  
**New Component:** YES

**Requirements:**
- Take timeout group from h-m1 (previously: mean_variance=0.294)
- Subdivide into: divergent timeouts vs difficult timeouts
- Calculate mean variance for each subgroup
- Test gate condition: mean_variance(divergent) > mean_variance(difficult)
- No statistical test required (PoC direction check only)

**Pseudo-code:**
```python
class TimeoutSubgroupAnalyzer:
    def analyze_variance_by_divergence(self, timeout_results):
        """
        Subdivide h-m1 timeout group by divergence classification.
        Test if divergent timeouts have higher variance than difficult timeouts.
        """
        divergent_variances = []
        difficult_variances = []
        
        for result in timeout_results:
            # Reuse h-m1 variance calculation
            variance = result['variance']
            
            # New: divergence classification
            is_divergent = result['divergence_classification']['is_divergent']
            
            # Group by classification
            if is_divergent:
                divergent_variances.append(variance)
            else:
                difficult_variances.append(variance)
        
        # Compare groups
        mean_divergent = np.mean(divergent_variances) if divergent_variances else 0.0
        mean_difficult = np.mean(difficult_variances) if difficult_variances else 0.0
        
        # Gate condition
        gate_satisfied = mean_divergent > mean_difficult
        
        return {
            'divergent_variance_mean': mean_divergent,
            'difficult_variance_mean': mean_difficult,
            'difference': mean_divergent - mean_difficult,
            'divergent_count': len(divergent_variances),
            'difficult_count': len(difficult_variances),
            'gate_satisfied': gate_satisfied
        }
```

**Source:** NEW - h-m2/code/analysis/timeout_subgroup_analyzer.py

### FR-6: Visualization - Divergence Analysis
**Priority:** CRITICAL  
**New Component:** YES

**Requirements:**
- MANDATORY: Bar chart comparing mean variance (divergent vs difficult timeouts)
- RECOMMENDED: Box plot showing variance distributions for both timeout subgroups
- RECOMMENDED: Scatter plots: state collisions vs variance, backtrack frequency vs variance
- RECOMMENDED: Pie chart: proportion of divergent vs difficult in timeout group
- RECOMMENDED: Example trajectory plots (divergent vs difficult patterns)

**Source:** NEW - h-m2/code/visualization/divergence_visualizer.py

---

## Non-Functional Requirements

### NFR-1: Code Reuse
**Requirement:** Maximize reuse from h-m1 by extending with divergence layer

**Approach:**
- Import h-m1 modules via Python path
- Reuse: dataset loading, model loading, confidence extraction, variance calculation
- Add: search tree tracking, divergence classification
- Extend: analysis from 2-group (success/timeout) to 3-group (success/divergent/difficult)

### NFR-2: Reproducibility
**Requirement:** Results must be reproducible across runs

**Approach:**
- Same random seed (42) as h-m1
- Same 100 theorems as h-m1
- Controlled comparison: only add divergence classification, reuse variance

### NFR-3: Execution Time
**Requirement:** Complete within reasonable time on single GPU

**Expected Duration:**
- Search tree tracking: +10-20% overhead vs h-m1 (additional logging)
- Divergence classification: <5 minutes (post-processing)
- Variance calculation: Reuse h-m1 results
- Visualization: <10 minutes

**Optimization:** If h-m1 saved confidence trajectories + search trees, can reuse directly.

---

## Data Specifications

### Input Data
| Dataset | Source | Size | Format |
|---------|--------|------|--------|
| LeanDojo Benchmark | h-m1 reuse | 100 theorems | Same as h-m1 |
| h-m1 Results (optional) | h-m1/results/*.pkl | 100 experiments | Pickle with variance + outcomes |
| Search Trees | NEW capture | 100 trees | LeanDojo search tree structure |

### Output Data
| Artifact | Location | Format |
|----------|----------|--------|
| Divergence Classification | h-m2/results/divergence_classification.json | JSON |
| Subgroup Analysis | h-m2/results/timeout_subgroup_analysis.json | JSON |
| Figures | h-m2/figures/*.png | PNG |

---

## Success Metrics

### Gate Metric (SHOULD_WORK)
**Primary:** mean_variance(divergent) > mean_variance(difficult)

**Interpretation:**
- If TRUE: Confidence instability specifically signals divergence (mechanism validated)
- If FALSE: Confidence variance reflects general difficulty, not divergence (mechanism refuted but continue)

**No Statistical Test:** PoC validation - direction check only (not publication-level)

### Supporting Metrics
- Divergence prevalence: Proportion of timeouts classified as divergent
- Marker correlation: Scatter plots showing collision/backtrack vs variance
- Effect size: Difference magnitude (divergent_var - difficult_var)

---

## Dependencies

### External Dependencies
| Dependency | Version | Source | Purpose |
|------------|---------|--------|---------|
| lean_dojo | latest | h-m1 reuse | Theorem proving + search tree API |
| numpy | ≥1.20 | h-m1 reuse | Numerical computation |
| matplotlib | ≥3.3 | h-m1 reuse | Visualization |
| scipy | ≥1.7 | optional | Statistics (optional Mann-Whitney) |

### Internal Dependencies
| Module | Source | Reuse Level |
|--------|--------|-------------|
| DataLoader | h-m1/code/data/loader.py | 100% |
| ProofRunner | h-m1/code/experiment/runner.py | 90% (add search tree tracking) |
| ConfidenceExtractor | h-m1/code/models/confidence_extractor.py | 100% |
| VarianceAnalyzer | h-m1/code/analysis/variance_analyzer.py | 100% |
| SearchTreeTracker | NEW | 0% (new component) |
| DivergenceClassifier | NEW | 0% (new component) |
| TimeoutSubgroupAnalyzer | NEW | 0% (new component) |

### Base Hypothesis Artifacts
**h-m1 Required Files:**
- Confidence extraction: h-m1/code/models/confidence_extractor.py
- Variance calculation: h-m1/code/analysis/variance_analyzer.py
- Experiment runner: h-m1/code/experiment/runner.py (extend for search tree)
- Dataset loader: h-m1/code/data/loader.py
- (Optional) Saved results: h-m1/results/*.pkl for variance reuse

---

## Implementation Constraints

### Scope Limitations
- NO new model training
- NO new data collection
- NO new timeout experiments (reuse h-m1 data + add search tree tracking)
- ONLY add divergence classification layer to existing analysis

### Optimization Opportunities
**Reuse h-m1 Variance Results:**
If h-m1 saved variance values:
- Load h-m1 timeout group variance values
- Re-run ONLY to capture search trees for divergence classification
- OR if h-m1 saved search trees, reuse directly
- Reduces execution time significantly

**Implementation:**
```python
# Option 1: Full reuse (if h-m1 saved trees)
if os.path.exists("h-m1/results/search_trees.pkl"):
    h_m1_results = load_h_m1_results()
    # Extract timeout group
    timeout_results = [r for r in h_m1_results if r['outcome'] == 'timeout']
    # Classify divergence from saved trees
    for result in timeout_results:
        result['divergence'] = classify_divergence(result['search_tree'])

# Option 2: Partial rerun (if no trees saved)
else:
    # Rerun experiments with search tree tracking enabled
    results = run_experiments_with_tree_tracking()
```

---

## Risk Mitigation

### Risk: Search tree API not available in LeanDojo
**Mitigation:** Verify LeanDojo Dojo.get_search_tree() API; fallback to state-sequence-only analysis if needed

### Risk: Divergence thresholds too arbitrary
**Mitigation:** This is PoC with heuristic thresholds; refine in h-m3 if mechanism validates

### Risk: Insufficient divergent samples
**Mitigation:** If < 10 divergent timeouts, adjust thresholds or note as limitation

---

## Acceptance Criteria

### Code Quality
- [ ] Imports h-m1 modules successfully
- [ ] Search tree tracking tested (unit test)
- [ ] Divergence classification tested (unit test with mock trees)
- [ ] Subgroup analysis logic tested

### Experiment Execution
- [ ] Runs on same 100 theorems as h-m1
- [ ] Captures search trees for all experiments
- [ ] Classifies timeouts as divergent/difficult
- [ ] Groups variance correctly by classification

### Output Artifacts
- [ ] Bar chart: mean variance comparison (divergent vs difficult) - MANDATORY
- [ ] Divergence classification JSON with markers
- [ ] Subgroup analysis JSON with counts and statistics
- [ ] Gate condition evaluated (TRUE/FALSE)

### Documentation
- [ ] README explaining h-m1 reuse + divergence layer
- [ ] Results interpretation (gate pass/fail)
- [ ] Divergence threshold justification

---

## Appendix: Comparison with h-m1

| Aspect | h-m1 | h-m2 |
|--------|------|------|
| **Dataset** | 100 theorems | Same 100 theorems |
| **Model** | LeanDojo ReProver | Same (no changes) |
| **Timeout** | 300s extended | Same |
| **Confidence Extraction** | Entropy trajectory (15 steps) | Same (reuse) |
| **Variance Calculation** | std dev of entropy | Same (reuse) |
| **Analysis Focus** | Success vs timeout (2 groups) | Divergent vs difficult timeouts (subdivision) |
| **New Component** | N/A | Search tree tracking + divergence classification |
| **Gate** | mean_variance(success) < mean_variance(timeout) | mean_variance(divergent) > mean_variance(difficult) |

**Key Insight:** h-m2 takes h-m1's timeout group (high variance, mean=0.294) and tests whether high variance is specifically linked to divergence by subdividing timeouts into divergent vs difficult.

**Reuse Strategy:**
- h-m1 infrastructure: 100%
- h-m1 variance values: Can reuse if saved
- New analysis: Divergence classification + subgroup comparison

---

## Appendix: Divergence Detection Background

### Theoretical Foundation
Divergence in theorem proving occurs when search explores cyclic, non-terminating paths:
- **Cyclic behavior:** Revisiting same proof states (state hash collisions)
- **Search instability:** High backtrack frequency from abandoned branches
- **Distribution shift:** LLM encounters unfamiliar states outside training manifold

### Why Confidence Variance Signals Divergence
Hypothesis: When LLM enters cyclic/unfamiliar regions:
- Confidence (softmax entropy) becomes unstable (high variance)
- Analogous to language model perplexity spikes on out-of-distribution text
- Distinct from difficult proofs: challenging but valid exploration (lower variance)

### h-m2 Test
Does high variance specifically correlate with divergence markers (collisions, backtracks)?
- If YES: Variance is divergence detector (mechanism validated)
- If NO: Variance reflects general difficulty, not divergence (mechanism refuted)
