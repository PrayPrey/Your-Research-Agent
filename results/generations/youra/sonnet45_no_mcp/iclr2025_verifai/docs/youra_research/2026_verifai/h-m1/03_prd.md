# Product Requirements Document: H-M1 Confidence-Geometry Mechanism

**Date:** 2026-04-20  
**Author:** Phase 3 Orchestrator  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM (Causal)  
**Status:** Planning  
**Base Hypothesis:** h-e1 (COMPLETED, PASSED)

---

## Executive Summary

This PRD specifies implementation requirements for testing the geometric interpretation of LLM confidence in neural theorem proving. Building on h-e1's validated correlation (r=0.80), h-m1 investigates WHY confidence predicts timeouts by testing whether confidence variance reflects proof state familiarity.

**Success Criteria:** Successful proofs show lower variance than timeouts (MUST_WORK gate)

**Reuse Strategy:** Extend h-e1 infrastructure (dataset, model, timeout protocol) with new variance-based analysis.

---

## Problem Statement

### Research Question
Does LLM confidence variance reflect proof state familiarity (training distribution manifold structure)?

### Hypothesis
Under neural theorem proving, if LLM confidence (softmax entropy) is measured during proof search, then confidence reflects familiarity with proof state patterns from training distribution, because the model's uncertainty increases when encountering states outside the manifold of successful proofs seen during training.

### Gate Condition
- **Type:** MUST_WORK
- **Pass:** mean_variance(successful) < mean_variance(timeout)
- **Fail:** PIVOT to symbolic-only approach

### Experiment Type
MECHANISM (PoC) - Tests causal mechanism, direction-based validation (no p-value required for PoC)

---

## Functional Requirements

### FR-1: Reuse h-e1 Dataset Infrastructure
**Priority:** CRITICAL  
**Reuse Level:** 100%

**Requirements:**
- Reuse exact same 100 theorems from h-e1 (controlled comparison)
- Same LeanDojo Benchmark source
- Same random seed (42) for reproducibility
- No new data collection needed

**Rationale:** Controlled experiment isolating mechanism hypothesis - only analysis changes, not data.

**Source:** h-e1/code/data/loader.py (REUSE AS-IS)

### FR-2: Reuse h-e1 Model and Timeout Protocol
**Priority:** CRITICAL  
**Reuse Level:** 100%

**Requirements:**
- Reuse pre-trained LeanDojo ReProver (no modifications)
- Same extended timeout: 300s per theorem (100× normal)
- Same proof search strategy: best-first search
- Same confidence extraction: first 15 steps

**Rationale:** Infrastructure validated in h-e1 - proven methodology.

**Source:** h-e1/code/experiment/runner.py (REUSE AS-IS)

### FR-3: Extend Confidence Analysis - Variance Metric
**Priority:** CRITICAL  
**Modification:** REPLACE derivative with variance calculation

**Requirements:**
- Extract softmax entropy trajectory (reuse h-e1 extractor)
- NEW: Calculate variance (std dev) instead of derivative
- Group proofs by outcome: successful vs timeout
- Compare mean variance between groups

**Implementation:**
```python
# Reuse from h-e1
class ConfidenceTrajectoryExtractor:
    def extract_confidence_trajectory(self, proof_session):
        # EXISTING: entropy extraction
        entropies = [self.compute_entropy(step) for step in steps[:15]]
        
        # NEW FOR H-M1: variance instead of derivative
        variance = np.std(entropies)  # Changed from derivative
        return variance, entropies
```

**Source:** Extend h-e1/code/models/confidence_extractor.py

### FR-4: Group Comparison Analysis
**Priority:** CRITICAL  
**New Component:** YES

**Requirements:**
- Separate proofs into two groups: successful vs timeout
- Calculate mean variance for each group
- Test gate condition: mean_variance(successful) < mean_variance(timeout)
- No statistical test required (PoC direction check only)

**Pseudo-code:**
```python
class VarianceGroupAnalyzer:
    def analyze_variance_by_outcome(self, results):
        success_group = [r['variance'] for r in results if r['outcome'] == 'success']
        timeout_group = [r['variance'] for r in results if r['outcome'] == 'timeout']
        
        mean_success = np.mean(success_group)
        mean_timeout = np.mean(timeout_group)
        
        gate_satisfied = mean_success < mean_timeout
        return {
            'success_variance_mean': mean_success,
            'timeout_variance_mean': mean_timeout,
            'gate_satisfied': gate_satisfied
        }
```

### FR-5: Visualization - Group Comparison
**Priority:** CRITICAL  
**Modification:** EXTEND h-e1 visualizer with group plots

**Requirements:**
- MANDATORY: Bar chart comparing mean variance (successful vs timeout)
- RECOMMENDED: Histogram of variance distributions (two groups)
- RECOMMENDED: Box plot showing quartiles for each group
- RECOMMENDED: Example trajectory plots (stable vs unstable patterns)

**Source:** Extend h-e1/code/visualization/visualizer.py

---

## Non-Functional Requirements

### NFR-1: Code Reuse
**Requirement:** Minimize code duplication by extending h-e1 modules

**Approach:**
- Import h-e1 modules via Python path
- Extend classes with new variance methods
- Reuse data loading, model loading, experiment runner AS-IS

### NFR-2: Reproducibility
**Requirement:** Results must be reproducible across runs

**Approach:**
- Same random seed (42) as h-e1
- Same 100 theorems as h-e1
- Controlled comparison: only metric changes (derivative → variance)

### NFR-3: Execution Time
**Requirement:** Complete within reasonable time on single GPU

**Expected Duration:**
- Confidence extraction: ~0 additional time (reuse h-e1 results)
- Variance calculation: <1 minute (post-processing)
- Visualization: <5 minutes

**Note:** Can potentially reuse h-e1's saved confidence trajectories to avoid re-running experiments.

---

## Data Specifications

### Input Data
| Dataset | Source | Size | Format |
|---------|--------|------|--------|
| LeanDojo Benchmark | h-e1 reuse | 100 theorems | Same as h-e1 |
| h-e1 Results (optional) | h-e1/results/*.pkl | 100 experiments | Pickle files with trajectories |

### Output Data
| Artifact | Location | Format |
|----------|----------|--------|
| Variance Results | h-m1/results/variance_analysis.json | JSON |
| Group Statistics | h-m1/results/group_comparison.json | JSON |
| Figures | h-m1/figures/*.png | PNG |

---

## Success Metrics

### Gate Metric (MUST_WORK)
**Primary:** mean_variance(successful) < mean_variance(timeout)

**Interpretation:**
- If TRUE: Confidence variance reflects familiarity (mechanism validated)
- If FALSE: Confidence variance does not distinguish familiar vs unfamiliar states (mechanism refuted)

**No Statistical Test:** PoC validation - direction check only (not publication-level)

### Supporting Metrics
- Distribution overlap: Visual inspection of variance histograms
- Effect size: Difference magnitude (timeout_var - success_var)

---

## Dependencies

### External Dependencies
| Dependency | Version | Source | Purpose |
|------------|---------|--------|---------|
| lean_dojo | latest | h-e1 reuse | Theorem proving interface |
| numpy | ≥1.20 | h-e1 reuse | Numerical computation |
| scipy | ≥1.7 | h-e1 reuse | Statistics (optional) |
| matplotlib | ≥3.3 | h-e1 reuse | Visualization |

### Internal Dependencies
| Module | Source | Reuse Level |
|--------|--------|-------------|
| DataLoader | h-e1/code/data/loader.py | 100% |
| ProofRunner | h-e1/code/experiment/runner.py | 100% |
| ConfidenceExtractor | h-e1/code/models/confidence_extractor.py | 95% (add variance) |
| Visualizer | h-e1/code/visualization/visualizer.py | 80% (add group plots) |

### Base Hypothesis Artifacts
**h-e1 Required Files:**
- Confidence extraction code: h-e1/code/models/confidence_extractor.py
- Experiment runner: h-e1/code/experiment/runner.py
- Dataset loader: h-e1/code/data/loader.py
- (Optional) Saved results: h-e1/results/*.pkl for trajectory reuse

---

## Implementation Constraints

### Scope Limitations
- NO new model training
- NO new data collection
- NO new timeout experiments (reuse h-e1 if possible)
- ONLY analysis metric changes (derivative → variance)

### Optimization Opportunities
**Reuse h-e1 Confidence Trajectories:**
If h-e1 saved confidence trajectories to disk:
- Load h-e1 results instead of re-running experiments
- Calculate variance from saved entropies
- Reduces execution time from hours to minutes

**Implementation:**
```python
# Option 1: Reuse h-e1 saved trajectories (fast)
if os.path.exists("h-e1/results/confidence_trajectories.pkl"):
    trajectories = load_h-e1_results()
    variances = [np.std(t['entropies']) for t in trajectories]

# Option 2: Re-run experiments (slower, but validated)
else:
    variances = run_experiments_from_scratch()
```

---

## Risk Mitigation

### Risk: h-e1 code not reusable
**Mitigation:** Verify h-e1 modules are importable; refactor if needed

### Risk: Different results from h-e1
**Mitigation:** Use exact same theorems and random seed; validate consistency

### Risk: Variance metric too simple
**Mitigation:** This is PoC - complexity added in later hypotheses if mechanism validates

---

## Acceptance Criteria

### Code Quality
- [ ] Imports h-e1 modules successfully
- [ ] Variance calculation tested (unit test)
- [ ] Group comparison logic tested

### Experiment Execution
- [ ] Runs on same 100 theorems as h-e1
- [ ] Produces variance for each experiment
- [ ] Groups results correctly by outcome

### Output Artifacts
- [ ] Bar chart: mean variance comparison (MANDATORY)
- [ ] Variance distributions histogram (RECOMMENDED)
- [ ] Results JSON with group statistics
- [ ] Gate condition evaluated (TRUE/FALSE)

### Documentation
- [ ] README explaining h-e1 reuse strategy
- [ ] Results interpretation (gate pass/fail)

---

## Appendix: Comparison with h-e1

| Aspect | h-e1 | h-m1 |
|--------|------|------|
| **Dataset** | 100 theorems | Same 100 theorems |
| **Model** | LeanDojo ReProver | Same (no changes) |
| **Timeout** | 300s extended | Same |
| **Confidence Extraction** | Entropy trajectory (15 steps) | Same |
| **Metric** | Derivative (std dev) | Variance (std dev) - SAME CALCULATION |
| **Analysis** | Correlation with timeout | Group comparison (success vs timeout) |
| **Gate** | r > 0.3 OR ρ > 0.3 | mean_variance(success) < mean_variance(timeout) |

**Key Insight:** h-e1 and h-m1 both calculate std dev of entropy. The difference is:
- h-e1: Tests correlation between std dev and binary outcome
- h-m1: Tests group difference in std dev between outcomes

**Reuse Opportunity:** If h-e1 saved std dev values, h-m1 can directly reuse them for group comparison without re-running experiments.
