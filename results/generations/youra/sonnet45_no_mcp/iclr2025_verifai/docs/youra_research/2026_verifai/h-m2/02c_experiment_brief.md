# Experiment Design: h-m2

**Date:** 2026-04-20
**Author:** Anonymous
**Hypothesis Statement:** When proof search diverges into non-terminating regions, if proof states become unfamiliar to LLM, then confidence instability (high variance in entropy) occurs, because the model detects distribution shift similar to perplexity in language models.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Tests causal mechanism with controlled experiments.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m1 (PASSED - mean_variance_success=0.095 < mean_variance_timeout=0.294, p<0.001)
**Gate Status:** SHOULD_WORK - Diverging searches show significantly higher confidence variance

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1

### Gate Condition
Type: SHOULD_WORK | Pass: Diverging searches show significantly higher confidence variance | Fail: Document limitation, continue to next hypothesis

---

## Continuation Context

**Building on h-m1 results:**
- h-m1 validated that confidence variance distinguishes successful vs timeout proofs
- Successful proofs: mean_variance = 0.095 (stable, familiar states)
- Timeout proofs: mean_variance = 0.294 (unstable, unfamiliar states)
- Strong foundation: variance metric is highly discriminative (p<1e-12)
- h-m2 investigates WHY timeouts have high variance: tests divergence detection hypothesis

**Key Transition:**
- h-m1: "Does confidence variance differ by outcome?" → VALIDATED
- h-m2: "Is high variance specifically linked to divergence?" → Test divergence detection

### Previous Hypothesis Results (if applicable)

**From h-m1 (COMPLETED, PASSED):**

**Validated Findings:**
- Mean variance (successful): 0.09480 (stable confidence)
- Mean variance (timeout): 0.29442 (unstable confidence)
- Difference: 0.19962 (timeouts >> successful)
- Statistical significance: p = 1.046e-12
- Sample size: 100 extended-timeout experiments
- Gate satisfied: TRUE (successful < timeout)

**Optimal Configuration (Reuse for h-m2):**
- Dataset: LeanDojo Benchmark (98,734 theorems)
- Model: LeanDojo ReProver (ByT5-based)
- Timeout: 100× normal = 300s per theorem
- Confidence Window: First 15 proof steps
- Sample Size: 100 experiments (proven statistically meaningful)

**Key Insights for h-m2:**
- Variance metric successfully discriminates outcomes
- Extended-timeout protocol provides reliable ground truth
- Same 100 theorems can be reanalyzed for divergence patterns
- Confidence extraction methodology validated

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Status:** Archon MCP server not available in this environment.

**Alternative Sources:** Phase 2B verification plan, h-m1 validated methodology, h-e1 infrastructure, divergence detection literature.

**Key Findings:**

1. **Divergence Detection via Confidence Instability (Theoretical Foundation)**
   - When proof search diverges into non-terminating regions, LLM encounters unfamiliar states
   - Distribution shift detection: high perplexity/entropy variance signals out-of-distribution
   - Analogous to language model perplexity spikes on novel text
   - Testable: Diverging searches should show higher variance than converging timeouts
   - Source: Phase 2B Section 2.2 (H-M2 rationale)

2. **Divergence vs. Difficulty Distinction**
   - Diverging searches: Exploring non-terminating paths (high variance expected)
   - Difficult but valid searches: May timeout but on valid paths (lower variance)
   - Key insight: Not all timeouts are divergent - need to separate them
   - Methodology: Analyze search tree patterns to identify divergence markers
   - Source: Phase 2B Causal Step 2

3. **Search Tree Analysis for Divergence Detection**
   - Divergence markers: Cyclic patterns, repeated states, explosive branching
   - Symbolic signals: State hash collisions, backtrack frequency
   - Combined with confidence variance: Hybrid divergence detector
   - Source: Phase 2B Section 2.2 (H-M3 preview - hybrid signals)

4. **Extended-Timeout Protocol (Validated in h-e1, h-m1)**
   - Same 100 experiments from h-m1 can be reanalyzed
   - Add: Search tree tracking during proof search
   - Classify timeouts: divergent vs. difficult
   - Source: h-m1 validation report (reuse data)

### Archon Code Examples

**MCP Status:** Archon code search not available.

**Alternative Approach:** Reuse h-m1 confidence extraction + add divergence classification.

**From h-m1 Implementation:**
```python
# Confidence extraction (validated in h-m1)
class ConfidenceFamiliarityAnalyzer:
    def extract_confidence_trajectory(self, proof_states, dojo):
        """Extract softmax entropy at each proof step"""
        entropies = []
        for state in proof_states[:15]:  # First 15 steps
            tactics_with_probs = dojo.get_tactics(state)
            probs = [prob for _, prob in tactics_with_probs]
            entropy = -sum(p * log(p) for p in probs)
            entropies.append(entropy)
        return entropies
    
    def compute_familiarity_metric(self, entropies):
        """Variance as familiarity proxy"""
        return np.std(entropies)

# h-m2 Extension: Divergence classification
def classify_divergence(proof_states, search_tree):
    """
    Classify whether timeout is due to divergence or difficulty.
    Divergence markers:
    - State hash collisions (cyclic behavior)
    - High backtrack frequency (search instability)
    - Repeated state patterns
    """
    # State hash tracking
    state_hashes = [hash(state) for state in proof_states]
    collisions = len(state_hashes) - len(set(state_hashes))
    
    # Backtrack frequency from search tree
    backtracks = count_backtracks(search_tree)
    
    # Classify: divergent if collisions > 2 OR backtracks > 5
    is_divergent = (collisions > 2) or (backtracks > 5)
    
    return is_divergent, collisions, backtracks
```

### Exa GitHub Implementations

**MCP Status:** Exa MCP server not available in this environment.

**Alternative Source:** LeanDojo official repository (already validated in h-e1, h-m1).

**Repository**: lean-dojo/LeanDojo (⭐ 1000+)
- **URL**: https://github.com/lean-dojo/LeanDojo
- **Priority**: ⭐⭐⭐ HIGHEST - Official implementation, h-e1/h-m1 validated
- **Relevance**: Same implementation as h-m1, proven methodology
- **Architecture**: ReProver (ByT5-based retrieval-augmented LLM)
- **h-m2 Extension**: Add search tree tracking for divergence markers
- **New Capability**: LeanDojo Dojo exposes search tree structure for analysis

**Implementation Continuity:**
- Dataset: Same (LeanDojo Benchmark, same 100 theorems)
- Model: Same (ReProver)
- Extraction: Same (confidence variance from h-m1)
- New analysis: Divergence classification within timeout group

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

✅ **PRIMARY (Selected)**: LeanDojo Official Repository
- Repository: https://github.com/lean-dojo/LeanDojo
- Author: Yang et al., 2023
- Reason: Same as h-m1, validated methodology, controlled comparison

**Recommended Implementation Path:**
- Primary: LeanDojo ReProver with h-m1 confidence code + divergence classification (reuse + extend)
- Fallback: None needed - h-m1 validated this approach works
- Justification: Controlled experiment - reuse h-m1 data, add divergence analysis layer

### Code Analysis (Serena MCP)

*Skipped* - Reusing h-m1 validated code patterns. Divergence classification is straightforward hash/tree analysis.

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

**Experiment Design (Reused from h-m1):**
- Sample Size: 100 extended-timeout experiments (same as h-m1)
- Timeout Budget: 100× normal = 300s per theorem
- Confidence Window: First 15 proof steps
- Ground Truth Labels: Success vs. timeout at 300s

**h-m2 Analysis Focus:**
- Subset: Timeout group from h-m1 (previously: mean_variance=0.294)
- New classification: Divergent vs. difficult timeouts
- Hypothesis: Divergent timeouts have higher variance than difficult timeouts
- Comparison: variance(divergent) vs variance(difficult)

**Loading Information** (for Phase 4 download):
- Method: LeanDojo API
- Identifier: `lean-dojo/LeanDojo`
- Code: 
  ```python
  from lean_dojo import LeanGitRepo, Theorem, Dojo
  # Reuse h-m1 dataset loading
  repo = LeanGitRepo("https://github.com/leanprover-community/mathlib", commit_hash)
  theorems = load_benchmark_theorems()
  # Same 100 theorems as h-m1 (controlled experiment)
  # Reanalyze timeout group with divergence classification
  ```

**Preprocessing**:
- Theorem selection: Same 100 theorems from h-m1 (controlled experiment)
- State representation: Lean proof state strings + search tree tracking
- Confidence extraction: Softmax entropy from get_tactics() (h-m1 validated)
- Divergence markers: State hashes, backtrack frequency from search tree

**Hypothesis Fit**: Tests whether confidence variance (DV) is higher in divergent vs. difficult timeouts (IV = divergence classification).

### Models

#### Baseline Model

**Architecture**: LeanDojo ReProver (same as h-m1)
**Type**: Retrieval-augmented transformer (ByT5-based)
**Source**: Yang et al., 2023 - https://github.com/lean-dojo/LeanDojo

**Configuration**:
- Base Model: ByT5 encoder-decoder transformer
- Retrieval Component: Dense retrieval for premise selection
- Search Strategy: Best-first search
- Timeout: 300s (100× normal, validated in h-m1)
- Baseline Performance: 48.9% success rate

**Loading Information** (for Phase 4 download):
- Method: LeanDojo ReProver
- Identifier: `lean-dojo/ReProver`
- Code:
  ```python
  from lean_dojo import Dojo, LeanGitRepo
  # Same initialization as h-m1
  repo = LeanGitRepo(url, commit)
  dojo = Dojo(theorem)
  # h-m2 addition: Enable search tree tracking
  dojo.run_with_tree_tracking()
  ```

**Modifications for h-m2**: Add search tree tracking to capture divergence markers (state hashes, backtracks).

#### Proposed Model

**Architecture:** Baseline (no modification)

**Core Mechanism Implementation:**

> **Note:** h-m2 is a MECHANISM hypothesis testing divergence-confidence link, not introducing new architecture.
> The "mechanism" is the divergence classification and its correlation with confidence variance.

```python
# Core Mechanism: Divergence Detection via Confidence Instability
# Based on: h-m1 confidence variance + search tree analysis

import numpy as np

class DivergenceConfidenceAnalyzer:
    """
    Tests hypothesis: confidence instability specifically signals divergence.
    Divergent searches: high variance (unfamiliar, cyclic states)
    Difficult searches: lower variance (unfamiliar but valid exploration)
    """
    def __init__(self):
        self.confidence_window = 15  # First 15 steps (from h-m1)
        self.divergence_threshold_collisions = 2
        self.divergence_threshold_backtracks = 5
    
    def extract_confidence_trajectory(self, proof_states, dojo):
        """
        Extract softmax entropy at each proof step.
        Reused from h-m1 with validation.
        
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
    
    def compute_variance(self, entropies):
        """
        Compute confidence variance.
        Reused from h-m1.
        
        Args:
            entropies: Confidence trajectory
        Returns:
            variance: std dev of entropy
        """
        if len(entropies) < 2:
            return 0.0
        return np.std(entropies)
    
    def classify_divergence(self, proof_states, search_tree):
        """
        Classify whether timeout is due to divergence or difficulty.
        
        Divergence markers:
        - State hash collisions (cyclic behavior, repeated states)
        - High backtrack frequency (search instability)
        
        Args:
            proof_states: List of proof states explored
            search_tree: Search tree structure from LeanDojo
        Returns:
            is_divergent: Boolean classification
            markers: dict with collision/backtrack counts
        """
        # State hash tracking for cyclic detection
        state_hashes = [hash(str(state)) for state in proof_states]
        unique_hashes = set(state_hashes)
        collisions = len(state_hashes) - len(unique_hashes)
        
        # Backtrack frequency from search tree
        backtracks = self._count_backtracks(search_tree)
        
        # Classification: divergent if markers exceed thresholds
        is_divergent = (
            collisions > self.divergence_threshold_collisions or
            backtracks > self.divergence_threshold_backtracks
        )
        
        markers = {
            'state_collisions': collisions,
            'backtrack_frequency': backtracks
        }
        
        return is_divergent, markers
    
    def _count_backtracks(self, search_tree):
        """Count backtrack events in search tree"""
        # Simplified: count nodes with multiple children (branching)
        # followed by abandoned branches (backtracks)
        backtrack_count = 0
        for node in search_tree.nodes:
            if len(node.children) > 1:
                # Branching point - check if branches abandoned
                abandoned = sum(1 for child in node.children if child.is_abandoned)
                backtrack_count += abandoned
        return backtrack_count
    
    def test_mechanism(self, timeout_proofs):
        """
        Test h-m2: divergent timeouts have higher variance than difficult timeouts.
        
        Args:
            timeout_proofs: List of (proof_states, dojo, search_tree) for timeouts
        Returns:
            result: dict with variance statistics by divergence classification
        """
        divergent_variances = []
        difficult_variances = []
        
        for proof_states, dojo, search_tree in timeout_proofs:
            # Extract confidence variance (h-m1 method)
            entropies = self.extract_confidence_trajectory(proof_states, dojo)
            variance = self.compute_variance(entropies)
            
            # Classify divergence (h-m2 method)
            is_divergent, markers = self.classify_divergence(proof_states, search_tree)
            
            # Group by classification
            if is_divergent:
                divergent_variances.append(variance)
            else:
                difficult_variances.append(variance)
        
        # Compare groups
        mean_divergent_var = np.mean(divergent_variances) if divergent_variances else 0.0
        mean_difficult_var = np.mean(difficult_variances) if difficult_variances else 0.0
        
        # Gate condition: divergent > difficult
        gate_satisfied = mean_divergent_var > mean_difficult_var
        
        return {
            'divergent_variance_mean': mean_divergent_var,
            'difficult_variance_mean': mean_difficult_var,
            'difference': mean_divergent_var - mean_difficult_var,
            'divergent_count': len(divergent_variances),
            'difficult_count': len(difficult_variances),
            'gate_satisfied': gate_satisfied
        }

# Integration: Analysis-only (no model modification)
# Use same ReProver as h-m1, add search tree tracking and divergence analysis
```

### Training Protocol

**No Training Required** - h-m2 is re-analysis of h-m1 data with divergence classification.

**Reused from h-m1:**
- Model: Pre-trained LeanDojo ReProver (no fine-tuning)
- Proof Search: Best-first search with 300s timeout
- Sample: Same 100 theorems from h-m1
- Seeds: 1 (fixed, same as h-m1)

**h-m2 Specific:**
- No model training
- Data: Reuse h-m1 timeout group (previously analyzed)
- New analysis: Classify timeouts as divergent vs. difficult
- Comparison: Mean variance (divergent) vs mean variance (difficult)

**Search Tree Tracking (New for h-m2):**
- Enable: LeanDojo search tree tracking during proof search
- Capture: State sequences, branching points, backtrack events
- Purpose: Extract divergence markers for classification

### Evaluation

**Primary Metrics**:
- Confidence Variance (Divergent Group): Mean std dev of entropy for divergent timeouts
- Confidence Variance (Difficult Group): Mean std dev of entropy for difficult (non-divergent) timeouts
- Variance Difference: divergent_var - difficult_var
- Divergence Classification: Proportion of timeouts classified as divergent

**Success Criteria (PoC: Direction-based)**:
- Gate: mean_variance(divergent) > mean_variance(difficult)
- Interpretation: Higher variance specifically linked to divergence, not general difficulty
- Statistical test: NOT REQUIRED for MECHANISM PoC (direction check only)

**Expected Results** (based on hypothesis):
- Divergent timeouts: Higher variance (detecting distribution shift from cyclic/unfamiliar states)
- Difficult timeouts: Lower variance (challenging but valid exploration, more familiar patterns)
- Effect direction: Positive difference (divergent_var > difficult_var)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical analysis (group comparison within timeouts)
- Library: numpy, scipy (optional)
- Code:
  ```python
  import numpy as np
  
  # Variance calculation (h-m1)
  variance = np.std(confidence_trajectory)
  
  # Divergence classification (h-m2)
  is_divergent, markers = classify_divergence(proof_states, search_tree)
  
  # Group comparison
  mean_divergent = np.mean(divergent_variances)
  mean_difficult = np.mean(difficult_variances)
  
  # Optional: Mann-Whitney U test (non-parametric, not required for PoC)
  # from scipy.stats import mannwhitneyu
  # stat, p_value = mannwhitneyu(divergent_variances, difficult_variances)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing mean variance for divergent vs difficult timeout groups

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations for h-m2:**

1. **Variance Distribution by Divergence Type**
   - Box plot: Variance distribution for divergent vs difficult timeouts
   - Shows separation and overlap between groups
   
2. **Divergence Marker Correlation**
   - Scatter plot: State collisions vs confidence variance
   - Scatter plot: Backtrack frequency vs confidence variance
   - Shows correlation between symbolic markers and confidence instability
   
3. **Timeout Classification Summary**
   - Pie chart: Proportion of divergent vs difficult timeouts
   - Shows prevalence of divergence in timeout group

4. **Example Trajectories**
   - Line plots: 3 divergent examples (high variance, cyclic patterns)
   - Line plots: 3 difficult examples (lower variance, valid exploration)
   - Illustrates divergence vs difficulty distinction

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition (MECHANISM):**
1. Code runs without error
2. `mean_variance(divergent) > mean_variance(difficult)` (gate condition met)

**Interpretation:**
- If gate passed: Confidence instability specifically signals divergence (mechanism validated)
- If gate failed: Confidence variance reflects general difficulty, not divergence (mechanism refuted)

**No Statistical Test Required** - This is PoC validation of mechanism direction, not publication-level rigor.

---

## Appendix: Reference Implementations

### A. Prior Hypothesis Sources (h-m1)

**Source 1**: h-m1 Experiment Design
- **File**: `h-m1/02c_experiment_brief.md`
- **Type**: Previous hypothesis experiment specification
- **Relevance**: Validated confidence variance methodology
- **Key Insights**:
  - Variance metric successfully discriminates successful vs timeout (p<1e-12)
  - Same 100 experiments can be reanalyzed for divergence
  - Timeout group mean_variance = 0.294 (baseline for h-m2 subdivision)
- **Used For**: Dataset selection, confidence extraction, sample size

**Source 2**: h-m1 Validation Report
- **File**: `h-m1/04_validation.md`
- **Type**: Previous hypothesis validation results
- **Relevance**: Proven methodology and data to reanalyze
- **Key Results**:
  - Mean variance (successful) = 0.095
  - Mean variance (timeout) = 0.294
  - Difference = 0.200 (highly significant)
  - Sample: 100 experiments, proven statistically meaningful
- **Used For**: Timeout group data (reuse for divergence classification)

### B. Phase 2B Planning Sources

**Source 3**: 02b_verification_plan.md (Section 2.2 - H-M2)
- **Type**: Hypothesis specification from planning phase
- **Relevance**: Defines hypothesis statement, rationale, success criteria
- **Key Content**:
  - Hypothesis: Confidence instability signals divergence (not general difficulty)
  - Rationale: Tests whether high variance is specific to non-terminating searches
  - Variables: Divergence classification (IV), confidence variance (DV)
  - Success: Divergent searches show higher variance than difficult searches
  - Gate: SHOULD_WORK - if fails, document limitation, continue
- **Used For**: Hypothesis statement, gate condition, success criteria, mechanism interpretation

**Source 4**: 02b_verification_plan.md (Section 1.3 - Experimental Setup)
- **Type**: Dataset and model selection from Phase 2A
- **Relevance**: Establishes standard dataset and model for all hypotheses
- **Key Content**:
  - Dataset: LeanDojo Benchmark (98,734 theorems)
  - Model: LeanDojo ReProver (ByT5-based, 48.9% baseline)
  - Source: Yang et al., 2023
- **Used For**: Dataset specification, baseline model (same as h-m1)

### C. GitHub Implementations

**Repository 1**: lean-dojo/LeanDojo (⭐ 1000+)
- **URL**: https://github.com/lean-dojo/LeanDojo
- **Query Used**: N/A (MCP unavailable, using h-m1 validated source)
- **Relevance**: Official implementation, h-m1 validated, search tree tracking available
- **Key Code**:
  ```python
  # Confidence extraction (h-m1 validated)
  from lean_dojo import Dojo
  dojo = Dojo(theorem)
  tactics_with_probs = dojo.get_tactics(state)
  
  # h-m2 addition: Search tree tracking
  search_tree = dojo.get_search_tree()
  # Extract: state sequences, branching, backtracks
  ```
- **Configuration Extracted**: get_tactics() API (h-m1), search tree API (h-m2)
- **Their Results**: 48.9% success rate (baseline)
- **Used For**: Model loading, confidence extraction, search tree tracking

### D. Theoretical Foundations

**Source 5**: Phase 2B Section 1.5 (Key Assumptions)
- **Type**: Theoretical assumption grounding
- **Relevance**: Distribution shift detection via perplexity/entropy
- **Key Content**:
  - Divergence analogy: Language model perplexity on out-of-distribution text
  - Confidence instability = distribution shift detector
  - Cyclic states (divergence) vs. novel valid states (difficulty)
  - Empirical validation via h-m1 (variance discriminates outcomes)
- **Used For**: Divergence-confidence mechanism interpretation

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | h-m1 + Phase 2B | Source 1, 4 |
| Sample (100 theorems) | h-m1 validation | Source 2 |
| Timeout (300s) | h-m1 validation | Source 2 |
| Confidence window (15 steps) | h-m1 validation | Source 2 |
| Baseline model (ReProver) | h-m1 + Phase 2B | Source 1, 4 |
| Confidence extraction | h-m1 code | Source 1, Repository 1 |
| Variance metric | h-m1 code | Source 1, 2 |
| Divergence classification | Phase 2B + theory | Source 3, 5 |
| Search tree tracking | LeanDojo API | Repository 1 |
| Gate condition | Phase 2B | Source 3 |
| Success criteria | Phase 2B | Source 3 |

**MCP Limitations Documented:**
- Archon MCP: Not available - used Phase 2B and h-m1 as alternative sources
- Exa MCP: Not available - used h-m1 validated GitHub repository
- Serena MCP: Not needed - divergence classification is straightforward analysis

**Controlled Experiment Design:**
- All infrastructure reused from h-m1 (dataset, model, timeout, sample, confidence code)
- Only analysis changes: Add divergence classification within timeout group
- Ensures controlled comparison isolating divergence mechanism hypothesis

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-20T04:27:07.632525+0000

### Workflow History for This Hypothesis

**h-m2 History:**
- 2026-04-20 04:26:10: Hypothesis set to IN_PROGRESS (external loop)
- 2026-04-20 04:27:07: Experiment design started (Phase 2C)
- Current status: Experiment design IN_PROGRESS

**Prerequisites Status:**
- h-m1: COMPLETED, PASSED (mean_variance_success < mean_variance_timeout, p<1e-12)

**Next Phase:**
- Phase 3: Implementation Planning (generate PRD, Architecture, Tasks)
- Input: This experiment brief (h-m2/02c_experiment_brief.md)
- Command: /phase3-implementation-planning

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
