# Experiment Design: H-M4

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under CoT+confidence conditions, if hedging markers are present in reasoning, then verbalized confidence correlates negatively with marker count, because the model incorporates uncertainty signals into its confidence judgment.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing hedging-confidence correlation as core mechanism.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 (PASS), h-m1 (PASS), h-m2 (PASS), h-m3 (PASS)
**Gate Status:** MUST_WORK - Spearman r < -0.2, p < 0.05

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m4
- **Type:** MECHANISM
- **Prerequisites:** h-m3

### Gate Condition
**Primary:** Spearman correlation r < -0.2 (moderate negative correlation between hedging count and confidence)
**Secondary:** Correlation significant at p < 0.05

---

## Continuation Context

H-M4 tests the core mechanism: whether the model incorporates uncertainty signals (hedging markers) into its confidence judgment. This is the critical link in the causal chain explaining super-additive calibration.

### Previous Hypothesis Results (h-m3)
- **Status:** VALIDATED (PASS)
- **CoT Order Rate:** 100.0% (hedging appears before confidence)
- **Markers Precede Rate:** 100.0%
- **Key Finding:** Prompt format inherently enforces reasoning-before-confidence structure
- **Implication:** Hedging signals are guaranteed to be in-context when confidence is verbalized

### Accumulated Evidence from Chain
- **H-E1:** Confidence extraction >95% reliable, ECE computable
- **H-M1:** CoT produces multi-step reasoning (rate: 100%, mean steps: 2.61)
- **H-M2:** Hedging markers present (rate: 80.3%, mean: 3.23 markers)
- **H-M3:** Positional ordering confirmed (100% compliance)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** MCP tools unavailable in this execution. Research grounded in Phase 2A/2B verified sources.

**Query 1: Verbalized Confidence Correlation Analysis**
- Xiong et al. 2023: Verbalized confidence extraction achieves >95% success with constrained prompts
- Tian et al. 2023: Confidence verbalization methods compared across prompting strategies
- Key insight: Spearman correlation is standard for ordinal confidence-count relationships

**Query 2: Hedging-Confidence Relationship**
- Lin et al. 2022: Uncertainty language correlates with actual model uncertainty in NLP tasks
- Kadavath et al. 2022: LLMs show meaningful self-evaluation when prompted appropriately
- Key insight: Hedging markers (might, possibly, perhaps) are reliable uncertainty indicators

### Archon Code Examples

**Spearman Correlation Implementation Pattern:**
```python
from scipy.stats import spearmanr

# Standard pattern for hedging-confidence correlation
hedging_counts = [...]  # List of marker counts per output
confidence_scores = [...]  # List of verbalized confidence (0-100)

correlation, p_value = spearmanr(hedging_counts, confidence_scores)
# Expected: r < -0.2 (negative), p < 0.05 (significant)
```

### Exa GitHub Implementations

**Note:** MCP tools unavailable. Specification based on Phase 2B research and prior hypothesis implementations.

**Key Implementation References:**
1. LLM uncertainty quantification methods (Xiong et al. 2023 codebase)
2. Verbalized confidence extraction patterns (Tian et al. 2023)
3. scipy.stats.spearmanr for correlation analysis

### 🎯 Implementation Priority Assessment

**Analysis Type:** Correlation analysis of cached data (no new API calls required)

**Recommended Implementation Path:**
- Primary: Reuse H-M2 cached outputs (817 items with hedging counts + confidence scores)
- Fallback: N/A (data already available from H-M2)
- Justification: H-M2 already extracted hedging markers and H-E1/H-M1 extracted confidence scores. Correlation analysis is purely statistical.

### Code Analysis (Serena MCP)

**Not applicable:** H-M4 performs statistical analysis on cached data, not code modification. The experiment analyzes existing outputs from previous hypotheses.

---

## Experiment Specification

### Dataset

**Dataset:** H-M2 Cached Outputs (TruthfulQA CoT+Confidence)
- **Type:** programmatic-api (cached from prior hypothesis)
- **Source:** `{hypothesis_folder}/../h-m2/code/results/h-m2_results.json`
- **Size:** 817 items (full TruthfulQA test set, processed in H-M2)

**Loading Information** (for Phase 4 download):
- Method: File read (cached data)
- Identifier: `h-m2/code/results/h-m2_results.json`
- Code:
```python
import json
with open("../h-m2/code/results/h-m2_results.json") as f:
    h_m2_data = json.load(f)
# Each item has: hedging_count, confidence_score, output_text
```

**Why Reuse H-M2 Data:**
1. Same prompting condition (CoT+confidence)
2. Already has hedging marker counts extracted
3. Already has confidence scores extracted
4. Eliminates need for new API calls (cost-efficient)
5. Ensures identical experimental conditions

### Models

#### Baseline Model

**Not Applicable for H-M4**

H-M4 is a correlation analysis hypothesis. It analyzes the statistical relationship between two variables (hedging count, confidence score) already present in H-M2 outputs.

- No model training required
- No model inference required
- Pure statistical analysis

**Loading Information** (for Phase 4 download):
- Method: N/A (no model needed)
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** Statistical Analysis Pipeline (not a neural model)

**Core Mechanism Implementation:**

```python
# H-M4: Hedging-Confidence Correlation Analysis
# Tests if model incorporates uncertainty signals into confidence

import json
from scipy.stats import spearmanr
import numpy as np

class HedgingConfidenceCorrelation:
    """
    Analyzes correlation between hedging marker count and verbalized confidence.
    Core test of the calibration mechanism hypothesis.
    """
    
    def __init__(self, h_m2_results_path: str):
        self.results_path = h_m2_results_path
        self.hedging_counts = []
        self.confidence_scores = []
        
    def load_data(self) -> int:
        """Load and extract hedging counts + confidence from H-M2 outputs."""
        with open(self.results_path) as f:
            data = json.load(f)
        
        for item in data['outputs']:
            if item.get('hedging_count') is not None and item.get('confidence') is not None:
                self.hedging_counts.append(item['hedging_count'])
                self.confidence_scores.append(item['confidence'])
        
        return len(self.hedging_counts)
    
    def compute_correlation(self) -> dict:
        """Compute Spearman correlation between hedging and confidence."""
        r, p = spearmanr(self.hedging_counts, self.confidence_scores)
        return {
            'spearman_r': float(r),
            'p_value': float(p),
            'n_samples': len(self.hedging_counts),
            'gate_pass': r < -0.2 and p < 0.05
        }
```

### Training Protocol

**Not Applicable for H-M4**

This is a statistical analysis hypothesis, not a training experiment.

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Optimizer | N/A | No training |
| Learning Rate | N/A | No training |
| Epochs | N/A | No training |
| Batch Size | N/A | No training |

**Execution Protocol:**
1. Load H-M2 cached results
2. Extract (hedging_count, confidence_score) pairs
3. Compute Spearman correlation
4. Check gate conditions (r < -0.2, p < 0.05)
5. Generate visualization

### Evaluation

**Primary Metrics:**
| Metric | Definition | Gate Threshold |
|--------|------------|----------------|
| Spearman r | Rank correlation coefficient | r < -0.2 |
| p-value | Statistical significance | p < 0.05 |
| n_samples | Valid data points | n >= 500 |

**Success Criteria (MECHANISM):**
- **Gate 1:** Spearman r < -0.2 (moderate negative correlation)
- **Gate 2:** p-value < 0.05 (statistically significant)
- **PASS:** Both gates satisfied

**Expected Values (from literature):**
- Correlation strength: -0.2 to -0.5 (moderate negative)
- Based on: Lin et al. 2022 uncertainty-language correlations

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Correlation Analysis
- Library: scipy.stats
- Code:
```python
from scipy.stats import spearmanr
r, p = spearmanr(hedging_counts, confidence_scores)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing r threshold (-0.2) vs actual r value

#### Additional Figures (LLM Autonomous)

1. **Scatter Plot with Regression Line**
   - X-axis: Hedging marker count
   - Y-axis: Verbalized confidence (0-100%)
   - Regression line showing negative slope
   - Correlation coefficient annotation

2. **Box Plot by Hedging Bucket**
   - Group samples by hedging count (0, 1-2, 3-5, 6+)
   - Show confidence distribution per bucket
   - Demonstrates monotonic decrease

3. **Histogram: Hedging Count Distribution**
   - Verify data has sufficient spread for correlation

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m4/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** True (analyzing hedging-confidence relationship)
- **mechanism_isolatable:** True (correlation is direct measurement)
- **baseline_measurable:** True (r=0 is null hypothesis baseline)

### Architecture Compatibility
- **Requirement:** H-M2 results must contain hedging_count and confidence fields
- **Check:** Load H-M2 results and verify fields exist for >500 samples

### Activation Indicators
- **mechanism_log_message:** "Computing Spearman correlation: r={r:.4f}, p={p:.4e}"
- **tensor_shape_change:** N/A (statistical analysis)
- **metric_delta_expected:** r < -0.2 vs r = 0 (null)

### Mechanism Verification Code
```python
def verify_mechanism(results: dict) -> dict:
    """Verify H-M4 mechanism is working correctly."""
    checks = {
        'data_loaded': len(results.get('hedging_counts', [])) > 500,
        'correlation_computed': 'spearman_r' in results,
        'negative_direction': results.get('spearman_r', 0) < 0,
        'significant': results.get('p_value', 1.0) < 0.05,
        'gate_pass': results.get('spearman_r', 0) < -0.2 and results.get('p_value', 1.0) < 0.05
    }
    return checks
```

### Success Thresholds
- **hypothesis_support_metric:** spearman_r
- **hypothesis_support_threshold:** r < -0.2

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Spearman r < -0.2 (moderate negative correlation)
3. p < 0.05 (statistically significant)

---

## Appendix: Reference Implementations

### Academic References
1. **Xiong et al. 2023** - "Can LLMs Express Their Uncertainty?"
   - Confidence extraction methodology
   - >95% extraction success with constrained prompts

2. **Tian et al. 2023** - "Just Ask for Calibration"
   - Verbalized confidence prompting strategies
   - Comparison across elicitation methods

3. **Lin et al. 2022** - "Teaching Models to Express Their Uncertainty"
   - Uncertainty language patterns in LLM outputs
   - Hedging-uncertainty correlation evidence

4. **Kadavath et al. 2022** - "Language Models (Mostly) Know What They Know"
   - LLM self-evaluation capabilities
   - Foundation for confidence verbalization

### Code References
1. **scipy.stats.spearmanr** - Standard implementation for rank correlation
2. **H-M2 Implementation** - Hedging marker extraction patterns

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19T02:19:55Z: h-m4 set to IN_PROGRESS (external loop)
- 2026-08-19: Phase 2C experiment design started
- Dependencies: h-m3 VALIDATED with 100% ordering compliance

---

*Research grounded in Phase 2A/2B verified sources (MCP unavailable)*
*Statistical analysis of H-M2 cached outputs - no new model inference required*
*Next Phase: Phase 3 - Implementation Planning*
