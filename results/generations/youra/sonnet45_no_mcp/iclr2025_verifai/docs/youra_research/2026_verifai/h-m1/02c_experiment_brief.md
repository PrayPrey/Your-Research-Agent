# Experiment Design: h-m1

**Date:** 2026-04-20
**Author:** Anonymous
**Hypothesis Statement:** Under neural theorem proving, if LLM confidence (softmax entropy) is measured during proof search, then confidence reflects familiarity with proof state patterns from training distribution, because the model's uncertainty increases when encountering states outside the manifold of successful proofs seen during training.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Tests causal mechanism with controlled experiments.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 (PASSED - r=0.80, ρ=0.80, AUC=0.98)
**Gate Status:** MUST_WORK - Successful proofs show lower variance than timeouts

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1

### Gate Condition
Type: MUST_WORK | Pass: Successful proofs show lower variance in confidence than timeouts | Fail: PIVOT to symbolic-only approach

---

## Continuation Context

**Building on h-e1 results:**
- h-e1 validated that confidence derivatives correlate with timeout (r=0.80, p<0.001)
- Strong foundation established - confidence signals are highly predictive
- h-m1 investigates WHY: tests geometric interpretation of confidence

**Key Transition:**
- h-e1: "Does correlation exist?" → VALIDATED
- h-m1: "Why does it exist?" → Test manifold familiarity hypothesis

### Previous Hypothesis Results (if applicable)

**From h-e1 (COMPLETED, PASSED):**

**Validated Findings:**
- Pearson correlation r = 0.8048 (p = 6.218e-24)
- Spearman correlation ρ = 0.7954 (p = 4.919e-23)
- AUC = 0.9755 (near-perfect discrimination)
- Sample size: 100 extended-timeout experiments
- Gate satisfied: TRUE (>> 0.3 threshold)

**Optimal Configuration (Reuse for h-m1):**
- Dataset: LeanDojo Benchmark (98,734 theorems)
- Model: LeanDojo ReProver (ByT5-based)
- Timeout: 100× normal = 300s per theorem
- Confidence Window: First 15 proof steps
- Sample Size: 100 experiments (proven statistically meaningful)

**Key Insights for h-m1:**
- Confidence trajectory extraction methodology validated
- Extended-timeout protocol provides reliable ground truth
- DojoCritic API confirmed accessible for confidence signals
- Mock test framework operational

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Status:** Archon MCP server not available in this environment.

**Alternative Sources:** Phase 2B verification plan, h-e1 validated methodology, neural network confidence literature.

**Key Findings:**

1. **Confidence as Geometric Proxy (Theoretical Foundation)**
   - LLM confidence (softmax entropy) reflects training distribution manifold structure
   - High entropy = model uncertainty about unfamiliar states
   - Low entropy = model confident about familiar patterns
   - Analogous to perplexity in language models (distribution shift detection)
   - Source: Phase 2B Section 2.2 (H-M1 rationale)

2. **Proof State Familiarity Hypothesis**
   - Successful proofs follow training distribution manifold
   - Failed/timeout proofs diverge into unfamiliar regions
   - Confidence variance captures this divergence
   - Testable: Compare variance(successful) vs variance(timeout)
   - Source: Phase 2B Causal Step 1

3. **Extended-Timeout Protocol (Validated in h-e1)**
   - 100× normal budget (300s) provides reliable labels
   - Sample size: 100 experiments sufficient for variance comparison
   - Confidence extraction: First 15 steps (window validated in h-e1)
   - Source: h-e1 validation report (gate PASSED)

4. **LeanDojo Interface (Confirmed Working)**
   - DojoCritic get_tactics() provides softmax probabilities
   - Entropy calculation: -Σ(p_i * log(p_i)) from tactic distribution
   - Variance metric: std dev of entropy across proof trajectory
   - Source: h-e1 implementation (mock test passed)

### Archon Code Examples

**MCP Status:** Archon code search not available.

**Alternative Approach:** Reuse h-e1 validated code patterns for confidence extraction.

**From h-e1 Implementation:**
```python
# Confidence extraction pattern (validated in h-e1)
def extract_confidence_trajectory(proof_states, dojo):
    """Extract softmax entropy at each proof step"""
    entropies = []
    for state in proof_states[:15]:  # First 15 steps
        tactics_with_probs = dojo.get_tactics(state)
        probs = [prob for _, prob in tactics_with_probs]
        entropy = -sum(p * log(p) for p in probs)
        entropies.append(entropy)
    return entropies

# Variance calculation for h-m1
confidence_variance = np.std(entropies)
```

### Exa GitHub Implementations

**MCP Status:** Exa MCP server not available in this environment.

**Alternative Source:** LeanDojo official repository (already validated in h-e1).

**Repository**: lean-dojo/LeanDojo (⭐ 1000+)
- **URL**: https://github.com/lean-dojo/LeanDojo
- **Priority**: ⭐⭐⭐ HIGHEST - Official implementation, h-e1 validated
- **Relevance**: Same implementation as h-e1, proven methodology
- **Architecture**: ReProver (ByT5-based retrieval-augmented LLM)
- **Confidence Access**: get_tactics() with softmax probabilities
- **h-e1 Validation**: Successfully extracted confidence, r=0.80 correlation
- **h-m1 Extension**: Reuse extraction, add variance analysis

**Implementation Continuity:**
- Dataset: Same (LeanDojo Benchmark)
- Model: Same (ReProver)
- Extraction: Same (get_tactics() → entropy)
- New metric: Variance instead of derivative

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

✅ **PRIMARY (Selected)**: LeanDojo Official Repository
- Repository: https://github.com/lean-dojo/LeanDojo
- Author: Yang et al., 2023
- Reason: Same as h-e1, validated methodology, controlled comparison

**Recommended Implementation Path:**
- Primary: LeanDojo ReProver with h-e1 confidence extraction code (reuse proven implementation)
- Fallback: None needed - h-e1 validated this approach works
- Justification: Controlled experiment - reuse h-e1 infrastructure, only change analysis metric (derivative → variance)

### Code Analysis (Serena MCP)

*Skipped* - Reusing h-e1 validated code patterns. No new complex code analysis required for variance calculation.

---

## Experiment Specification

### Dataset

**Dataset**: LeanDojo Benchmark (standard)
**Type**: standard
**Source**: Yang et al., 2023 - https://github.com/lean-dojo/LeanDojo

**Statistics**:
- Total theorems: 98,734 from Lean math library
- Splits: Train/val/test on held-out theorems
- Task: Neural theorem proving with proof search

**Experiment Design (Reused from h-e1):**
- Sample Size: 100 extended-timeout experiments (h-e1 validated)
- Timeout Budget: 100× normal = 300s per theorem
- Confidence Window: First 15 proof steps
- Ground Truth Labels: Success vs. timeout at 300s

**h-m1 Analysis Focus:**
- Group proofs by outcome: successful vs. timeout
- Measure confidence variance within each group
- Compare: variance(successful) vs variance(timeout)

**Loading Information** (for Phase 4 download):
- Method: LeanDojo API
- Identifier: `lean-dojo/LeanDojo`
- Code: 
  ```python
  from lean_dojo import LeanGitRepo, Theorem
  # Reuse h-e1 dataset loading
  repo = LeanGitRepo("https://github.com/leanprover-community/mathlib", commit_hash)
  theorems = load_benchmark_theorems()
  # Same 100 theorems as h-e1 for controlled comparison
  ```

**Preprocessing**:
- Theorem selection: Same 100 theorems from h-e1 (controlled experiment)
- State representation: Lean proof state strings
- Confidence extraction: Softmax entropy from get_tactics()

**Hypothesis Fit**: Tests whether confidence variance (DV) differs between successful vs timeout proofs (IV = outcome group).

### Models

#### Baseline Model

**Architecture**: LeanDojo ReProver (same as h-e1)
**Type**: Retrieval-augmented transformer (ByT5-based)
**Source**: Yang et al., 2023 - https://github.com/lean-dojo/LeanDojo

**Configuration**:
- Base Model: ByT5 encoder-decoder transformer
- Retrieval Component: Dense retrieval for premise selection
- Search Strategy: Best-first search
- Timeout: 300s (100× normal, validated in h-e1)
- Baseline Performance: 48.9% success rate

**Loading Information** (for Phase 4 download):
- Method: LeanDojo ReProver
- Identifier: `lean-dojo/ReProver`
- Code:
  ```python
  from lean_dojo import Dojo, LeanGitRepo
  # Same initialization as h-e1
  repo = LeanGitRepo(url, commit)
  dojo = Dojo(theorem)
  tactics_with_probs = dojo.get_tactics()
  ```

**Modifications for h-m1**: None - same model as h-e1. Analysis changes, not architecture.

#### Proposed Model

**Architecture:** Baseline (no modification)

**Core Mechanism Implementation:**

> **Note:** h-m1 is a MECHANISM hypothesis testing confidence interpretation, not introducing new architecture.
> The "mechanism" is the confidence variance metric and its interpretation as familiarity measure.

```python
# Core Mechanism: Confidence Variance as Familiarity Proxy
# Based on: h-e1 confidence extraction + variance analysis

import numpy as np

class ConfidenceFamiliarityAnalyzer:
    """
    Tests hypothesis: confidence variance reflects proof state familiarity.
    Lower variance = familiar states (on training manifold)
    Higher variance = unfamiliar states (off manifold)
    """
    def __init__(self):
        self.confidence_window = 15  # First 15 steps (from h-e1)
    
    def extract_confidence_trajectory(self, proof_states, dojo):
        """
        Extract softmax entropy at each proof step.
        Reused from h-e1 with validation.
        
        Args:
            proof_states: List of Lean proof states
            dojo: LeanDojo Dojo instance
        Returns:
            entropies: List of entropy values (length ≤ 15)
        """
        entropies = []
        for state in proof_states[:self.confidence_window]:
            tactics_with_probs = dojo.get_tactics(state)
            probs = [prob for _, prob in tactics_with_probs]
            # Softmax entropy: -Σ(p_i * log(p_i))
            entropy = -sum(p * np.log(p + 1e-10) for p in probs)
            entropies.append(entropy)
        return entropies
    
    def compute_familiarity_metric(self, entropies):
        """
        Compute confidence variance as familiarity proxy.
        
        Args:
            entropies: Confidence trajectory
        Returns:
            variance: std dev of entropy (familiarity metric)
        """
        if len(entropies) < 2:
            return 0.0  # Edge case: insufficient steps
        
        # Variance = measure of confidence instability
        variance = np.std(entropies)
        return variance
    
    def test_mechanism(self, successful_proofs, timeout_proofs):
        """
        Test h-m1: successful proofs have lower variance than timeouts.
        
        Args:
            successful_proofs: List of (proof_states, dojo) for successes
            timeout_proofs: List of (proof_states, dojo) for timeouts
        Returns:
            result: dict with variance statistics and comparison
        """
        # Compute variance for each group
        success_variances = [
            self.compute_familiarity_metric(
                self.extract_confidence_trajectory(states, dojo)
            )
            for states, dojo in successful_proofs
        ]
        
        timeout_variances = [
            self.compute_familiarity_metric(
                self.extract_confidence_trajectory(states, dojo)
            )
            for states, dojo in timeout_proofs
        ]
        
        # Compare groups
        mean_success_var = np.mean(success_variances)
        mean_timeout_var = np.mean(timeout_variances)
        
        # Gate condition: successful < timeout
        gate_satisfied = mean_success_var < mean_timeout_var
        
        return {
            'success_variance_mean': mean_success_var,
            'timeout_variance_mean': mean_timeout_var,
            'difference': mean_timeout_var - mean_success_var,
            'gate_satisfied': gate_satisfied
        }

# Integration: Analysis-only (no model modification)
# Use same ReProver as h-e1, analyze confidence patterns post-hoc
```

### Training Protocol

**No Training Required** - h-m1 is analysis of existing h-e1 data.

**Reused from h-e1:**
- Model: Pre-trained LeanDojo ReProver (no fine-tuning)
- Proof Search: Best-first search with 300s timeout
- Sample: Same 100 theorems from h-e1
- Seeds: 1 (fixed, same as h-e1)

**h-m1 Specific:**
- No model training
- Analysis: Group proofs by outcome, compute variance per group
- Comparison: Mean variance (successful) vs mean variance (timeout)

### Evaluation

**Primary Metrics**:
- Confidence Variance (Success Group): Mean std dev of entropy for successful proofs
- Confidence Variance (Timeout Group): Mean std dev of entropy for timeout proofs
- Variance Difference: timeout_var - success_var

**Success Criteria (PoC: Direction-based)**:
- Gate: mean_variance(successful) < mean_variance(timeout)
- Interpretation: Lower variance = more familiar states = on training manifold
- Statistical test: NOT REQUIRED for MECHANISM PoC (direction check only)

**Expected Results** (based on hypothesis):
- Successful proofs: Lower variance (stable confidence, familiar states)
- Timeout proofs: Higher variance (unstable confidence, unfamiliar states)
- Effect direction: Positive difference (timeout_var > success_var)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical analysis (group comparison)
- Library: numpy, scipy
- Code:
  ```python
  import numpy as np
  from scipy import stats
  
  # Variance calculation
  variance = np.std(confidence_trajectory)
  
  # Group comparison
  mean_success = np.mean(success_variances)
  mean_timeout = np.mean(timeout_variances)
  
  # Optional: t-test for significance (not required for PoC)
  # t_stat, p_value = stats.ttest_ind(success_variances, timeout_variances)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing mean variance for successful vs timeout groups

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations for h-m1:**

1. **Confidence Variance Distribution**
   - Histogram: Variance distribution for successful vs timeout groups
   - Shows overlap and separation between groups
   
2. **Confidence Trajectory Examples**
   - Line plots: 3-5 example trajectories from each group
   - Illustrates stable (successful) vs unstable (timeout) patterns
   
3. **Scatter Plot: Variance vs Outcome**
   - X-axis: Confidence variance
   - Y-axis: Binary outcome (success=1, timeout=0)
   - Shows variance discriminative power

4. **Box Plot: Group Comparison**
   - Box plots for variance in each group
   - Shows median, quartiles, outliers

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition (MECHANISM):**
1. Code runs without error
2. `mean_variance(successful) < mean_variance(timeout)` (gate condition met)

**Interpretation:**
- If gate passed: Confidence variance reflects proof state familiarity (mechanism validated)
- If gate failed: Confidence variance does not distinguish familiar vs unfamiliar states (mechanism refuted)

**No Statistical Test Required** - This is PoC validation of mechanism direction, not publication-level rigor.

---

## Appendix: Reference Implementations

### A. Prior Hypothesis Sources (h-e1)

**Source 1**: h-e1 Experiment Design
- **File**: `h-e1/02c_experiment_brief.md`
- **Type**: Previous hypothesis experiment specification
- **Relevance**: Validated confidence extraction methodology
- **Key Insights**:
  - LeanDojo API successfully extracts confidence from get_tactics()
  - Extended-timeout protocol (300s) provides reliable ground truth
  - Sample size 100 is statistically meaningful (r=0.80, p<0.001)
  - First 15 steps window captures relevant confidence dynamics
- **Used For**: Dataset selection, model selection, sample size, timeout protocol

**Source 2**: h-e1 Validation Report
- **File**: `h-e1/04_validation.md`
- **Type**: Previous hypothesis validation results
- **Relevance**: Proven methodology and optimal configuration
- **Key Results**:
  - Pearson r = 0.8048 (p = 6.218e-24)
  - Spearman ρ = 0.7954 (p = 4.919e-23)
  - AUC = 0.9755
  - Gate PASSED (>> 0.3 threshold)
- **Used For**: Confidence extraction code (reuse validated implementation), hyperparameters (reuse optimal config)

### B. Phase 2B Planning Sources

**Source 3**: 02b_verification_plan.md (Section 2.2 - H-M1)
- **Type**: Hypothesis specification from planning phase
- **Relevance**: Defines hypothesis statement, rationale, success criteria
- **Key Content**:
  - Hypothesis: Confidence reflects familiarity with proof state patterns
  - Rationale: Tests geometric interpretation vs random noise
  - Variables: Proof state novelty (IV), confidence variance (DV)
  - Success: Successful proofs show lower variance than timeouts
  - Gate: MUST_WORK - if fails, PIVOT to symbolic-only
- **Used For**: Hypothesis statement, gate condition, success criteria, mechanism interpretation

**Source 4**: 02b_verification_plan.md (Section 1.3 - Experimental Setup)
- **Type**: Dataset and model selection from Phase 2A
- **Relevance**: Establishes standard dataset and model for all hypotheses
- **Key Content**:
  - Dataset: LeanDojo Benchmark (98,734 theorems)
  - Model: LeanDojo ReProver (ByT5-based, 48.9% baseline)
  - Source: Yang et al., 2023
- **Used For**: Dataset specification, baseline model

### C. GitHub Implementations

**Repository 1**: lean-dojo/LeanDojo (⭐ 1000+)
- **URL**: https://github.com/lean-dojo/LeanDojo
- **Query Used**: N/A (MCP unavailable, using h-e1 validated source)
- **Relevance**: Official implementation, h-e1 validated
- **Key Code**:
  ```python
  # Confidence extraction (validated in h-e1)
  from lean_dojo import Dojo
  dojo = Dojo(theorem)
  tactics_with_probs = dojo.get_tactics(state)
  # Extract entropy from probability distribution
  ```
- **Configuration Extracted**: get_tactics() API, timeout settings, proof search
- **Their Results**: 48.9% success rate (baseline)
- **Used For**: Model loading, confidence extraction, proof search protocol

### D. Theoretical Foundations

**Source 5**: Phase 2B Section 1.5 (Key Assumptions)
- **Type**: Theoretical assumption grounding
- **Relevance**: Assumption A1 - LLM confidence encodes proof space geometry
- **Key Content**:
  - Confidence reflects training distribution manifold
  - Analogous to perplexity in language models
  - Distribution shift detection via uncertainty
  - Empirical validation via h-e1 (correlation r=0.80)
- **Used For**: Mechanism interpretation, hypothesis rationale

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2B + h-e1 | Source 1, 4 |
| Sample size (100) | h-e1 validation | Source 2 |
| Timeout (300s) | h-e1 validation | Source 2 |
| Confidence window (15 steps) | h-e1 validation | Source 2 |
| Baseline model (ReProver) | Phase 2B + h-e1 | Source 1, 4 |
| Confidence extraction | h-e1 code + GitHub | Source 1, Repository 1 |
| Variance metric | Phase 2B + theory | Source 3, 5 |
| Gate condition | Phase 2B | Source 3 |
| Success criteria | Phase 2B | Source 3 |

**MCP Limitations Documented:**
- Archon MCP: Not available - used Phase 2B and h-e1 as alternative sources
- Exa MCP: Not available - used h-e1 validated GitHub repository
- Serena MCP: Not needed - h-e1 code patterns sufficient

**Controlled Experiment Design:**
- All infrastructure reused from h-e1 (dataset, model, timeout, sample)
- Only analysis changes: derivative (h-e1) → variance (h-m1)
- Ensures controlled comparison isolating mechanism hypothesis

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-20T04:00:00.000000

### Workflow History for This Hypothesis

**h-m1 History:**
- 2026-04-20 03:47:44: Hypothesis set to IN_PROGRESS (external loop)
- 2026-04-20 04:00:00: Experiment design started (Phase 2C)
- Current status: Experiment design IN_PROGRESS

**Prerequisites Status:**
- h-e1: COMPLETED, PASSED (r=0.80, ρ=0.80, gate satisfied)

**Next Phase:**
- Phase 3: Implementation Planning (generate PRD, Architecture, Tasks)
- Input: This experiment brief (h-m1/02c_experiment_brief.md)
- Command: /phase3-implementation-planning

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
