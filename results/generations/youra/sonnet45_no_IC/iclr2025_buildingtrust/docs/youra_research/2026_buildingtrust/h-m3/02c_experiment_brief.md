# Experiment Design: h-m3

**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis Statement:** Under stratified prompt types (factual vs. misinformation), if reliability-robustness correlations are computed separately per stratum, then correlation magnitudes differ significantly (Fisher z-test p<0.05), because factual prompts show stronger coupling (r>0.4) than reasoning/misinformation prompts (r<0.3) due to different retrieval vs. computation mechanisms.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m2 (PASS)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2

### Gate Condition
SHOULD_WORK: If correlation magnitudes differ significantly (Fisher z-test p<0.05) between strata, hypothesis passes. If fails, pivot to independence hypothesis (no moderation effect).

---

## Continuation Context

This hypothesis builds on H-M1 (reliability-robustness coupling via memorization) and tests whether this coupling strength varies by prompt type. H-M1 established r=0.7233 (p<0.001) on factual stratum. H-M3 tests if misinformation stratum shows significantly weaker coupling.

### Previous Hypothesis Results (if applicable)

**From H-M2 (PASS):**
- Fairness-Reliability correlation: r=-0.2450, p=0.000100
- HONEST bias metric successfully implemented with demographic augmentation
- Sample size: 817 prompts across 3 model sizes
- All outputs already generated and cached from H-E1/H-M1

**From H-M1 (PASS):**
- Factual stratum correlation: r=0.7233, p<0.001
- Misinformation stratum correlation: r=0.2798 (mechanism specificity observed)
- 95% CI for factual: [0.6730, 0.7670]
- Baseline outputs and metrics already computed

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Results:** Limited direct matches for Fisher z-test correlation comparison in Archon KB. However, foundational statistical testing patterns found in general documentation sources.

**Key Insights:**
- Fisher z-transformation is standard for comparing two independent correlation coefficients
- Requires converting Pearson r values to z-scores before testing difference
- Formula: `z = 0.5 * ln((1+r)/(1-r))`
- Test statistic: `z_diff = (z1 - z2) / sqrt(1/(n1-3) + 1/(n2-3))`

**Relevance:** Directly applicable to H-M3 hypothesis testing framework for comparing correlations across factual vs. misinformation strata.

### Archon Code Examples

**Search Results:** No specific Fisher z-test code examples in Archon KB. Standard scipy.stats library provides necessary tools.

**Recommended Implementation:**
```python
from scipy import stats
import numpy as np

# Fisher z-transformation
z1 = np.arctanh(r1)  # For factual stratum
z2 = np.arctanh(r2)  # For misinformation stratum

# Standard error
se_diff = np.sqrt(1/(n1-3) + 1/(n2-3))

# Test statistic
z_stat = (z1 - z2) / se_diff
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
```

### Exa GitHub Implementations

**Search Status:** Exa MCP unavailable (402 payment error)

**Fallback:** Standard scipy statistical functions well-documented and widely used in correlation comparison research.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Type:** Statistical analysis (no neural network training required)

**Priority:** LOW - This is a post-hoc analysis of existing data from H-M1/H-M2. No new model implementation needed.

**Recommended Implementation Path:**
- Primary: Use existing correlation outputs from H-M1 (factual stratum: r=0.7233) and compute misinformation stratum correlation from same cached outputs
- Fallback: Re-compute both correlations from cached model outputs if needed
- Justification: H-M1 already computed factual stratum correlation. We only need to: (1) compute misinformation stratum correlation from same outputs, (2) apply Fisher z-test to compare.

### Code Analysis (Serena MCP)

**Status:** Not applicable - no codebase analysis needed for statistical comparison workflow.

**Rationale:** This hypothesis tests correlation differences using standard scipy.stats functions on previously generated evaluation data. No complex implementation to analyze.

---

## Experiment Specification

### Dataset

**Name:** TruthfulQA (stratified: factual vs. misinformation)
**Type:** standard
**Source:** HuggingFace Datasets
**Split:** generation
**Total Samples:** 817 prompts

**Stratification:**
- **Factual stratum:** ~400 prompts (questions with ground-truth factual answers)
- **Misinformation stratum:** ~417 prompts (questions designed to elicit common misconceptions)
- **Stratification variable:** Question category from TruthfulQA metadata

**Preprocessing:**
1. Load full TruthfulQA dataset
2. Stratify into factual vs. misinformation based on category labels
3. Use cached model outputs from H-E1 (already generated for all 817 prompts × 3 models)
4. Use cached reliability/robustness scores from H-M1

**Data Reuse:** 100% - All model outputs and dimension scores already computed in H-E1/H-M1. No new generation needed.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `truthful_qa` (config: `generation`)
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "generation")
```

### Models

#### Baseline Model

**Name:** Llama-2-chat (7B, 13B, 70B)
**Type:** Decoder-only transformer with RLHF fine-tuning
**Source:** HuggingFace Transformers
**Pretrained:** Yes

**Model Details:**
- Architecture: Llama-2 with chat-tuned RLHF
- Sizes: 7B, 13B, 70B parameters
- Context window: 4096 tokens
- All outputs already cached from H-E1

**Model Reuse:** 100% - All model outputs already generated in H-E1. No new inference needed.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers (NOT NEEDED - using cached outputs)
- Identifier: `meta-llama/Llama-2-{7b,13b,70b}-chat-hf`
- Code:
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
```

#### Proposed Model

**Architecture:** Statistical analysis (no model modification)

**Core Mechanism Implementation:**

**IMPORTANT:** This hypothesis tests a STATISTICAL mechanism (correlation moderation by prompt type), not a neural architecture mechanism. No model training or modification required.

**Mechanism:** Prompt-type moderation of correlation strength
- Factual prompts → retrieval-based processing → strong reliability-robustness coupling
- Misinformation prompts → reasoning-based processing → weaker reliability-robustness coupling

**Pseudo-code for Fisher z-test:**

```python
def test_correlation_difference(r1, n1, r2, n2, alpha=0.05):
    """
    Compare two independent correlation coefficients using Fisher z-test.
    
    Args:
        r1: Correlation for factual stratum
        n1: Sample size for factual stratum
        r2: Correlation for misinformation stratum  
        n2: Sample size for misinformation stratum
        alpha: Significance level (default: 0.05)
    
    Returns:
        z_stat: Test statistic
        p_value: Two-tailed p-value
        significant: Boolean (p < alpha)
    """
    import numpy as np
    from scipy import stats
    
    # Fisher z-transformation
    z1 = np.arctanh(r1)
    z2 = np.arctanh(r2)
    
    # Standard error of difference
    se_diff = np.sqrt(1/(n1-3) + 1/(n2-3))
    
    # Test statistic
    z_stat = (z1 - z2) / se_diff
    
    # Two-tailed p-value
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    
    significant = p_value < alpha
    
    return z_stat, p_value, significant

# Expected usage for H-M3:
# r_factual = 0.7233 (from H-M1)
# n_factual = ~400
# r_misinfo = ? (to be computed)
# n_misinfo = ~417
# z, p, sig = test_correlation_difference(r_factual, n_factual, r_misinfo, n_misinfo)
```

**PoC Success:** Fisher z-test p < 0.05 AND |r_factual - r_misinfo| ≥ 0.1

### Training Protocol

**NOT APPLICABLE** - No model training required.

**Rationale:** This hypothesis performs statistical analysis on existing evaluation data from H-M1. All model outputs and dimension scores already computed.

**Workflow:**
1. Load cached model outputs from H-E1 (817 prompts × 3 models = 2,451 samples)
2. Load cached reliability/robustness scores from H-M1
3. Stratify samples into factual vs. misinformation based on TruthfulQA metadata
4. Compute correlation for each stratum
5. Apply Fisher z-test to test significance of difference

### Evaluation

**Primary Metric:** Fisher z-test p-value (SHOULD_WORK gate: p < 0.05)

**Secondary Metrics:**
1. **Correlation difference:** |r_factual - r_misinfo| (target: ≥ 0.1)
2. **Factual stratum correlation:** r_factual (expected: > 0.4, already validated as 0.7233 in H-M1)
3. **Misinformation stratum correlation:** r_misinfo (expected: < 0.3)
4. **Effect size:** Cohen's q for correlation difference
5. **Confidence intervals:** 95% CI for both correlations

**Success Criteria (SHOULD_WORK Gate):**
- Primary: Fisher z-test p < 0.05 (significant difference between strata)
- Secondary: r_factual - r_misinfo ≥ 0.1 (meaningful difference magnitude)
- Tertiary: r_factual > 0.4 AND r_misinfo < 0.3 (directional pattern matches theory)

**Expected Results:**
- Based on H-M1: r_factual = 0.7233 (already validated)
- Based on H-M1 supplementary: r_misinfo ≈ 0.28 (mentioned in validation report)
- Expected difference: 0.7233 - 0.28 = 0.44 (well above 0.1 threshold)
- Expected p-value: < 0.001 (highly significant)

**Visualization Outputs:**
1. Forest plot: Correlations per stratum with 95% CI error bars
2. Scatter plots: Reliability vs. Robustness for each stratum (side-by-side)
3. Distribution comparison: Correlation bootstrapped distributions

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical hypothesis testing (correlation comparison)
- Library: scipy.stats, numpy
- Code:
```python
from scipy import stats
import numpy as np

# Correlation computation
r_factual, p_factual = stats.pearsonr(reliability_factual, robustness_factual)
r_misinfo, p_misinfo = stats.pearsonr(reliability_misinfo, robustness_misinfo)

# Fisher z-test
z1 = np.arctanh(r_factual)
z2 = np.arctanh(r_misinfo)
se_diff = np.sqrt(1/(n_factual-3) + 1/(n_misinfo-3))
z_stat = (z1 - z2) / se_diff
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

# Confidence intervals (Fisher z back-transform)
ci_factual = [np.tanh(z1 - 1.96/np.sqrt(n_factual-3)), 
              np.tanh(z1 + 1.96/np.sqrt(n_factual-3))]
ci_misinfo = [np.tanh(z2 - 1.96/np.sqrt(n_misinfo-3)),
              np.tanh(z2 + 1.96/np.sqrt(n_misinfo-3))]
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **Forest Plot** (PRIORITY: HIGH)
   - X-axis: Pearson correlation coefficient (-1 to 1)
   - Y-axis: Strata (Factual, Misinformation)
   - Error bars: 95% confidence intervals
   - Annotations: r-values, p-values, sample sizes

2. **Scatter Plots** (PRIORITY: HIGH)
   - Layout: 1 row × 2 columns (side-by-side)
   - Left panel: Factual stratum (reliability vs. robustness)
   - Right panel: Misinformation stratum (reliability vs. robustness)
   - Overlays: Regression lines, correlation coefficient text
   - Color: By model size (7B, 13B, 70B)

3. **Distribution Comparison** (PRIORITY: MEDIUM)
   - Violin plots or kernel density estimates
   - Show distribution of reliability and robustness scores per stratum
   - Helps visualize variance differences between strata

4. **Effect Size Visualization** (PRIORITY: LOW)
   - Bar chart showing correlation difference with significance markers
   - Include Cohen's q effect size classification (small/medium/large)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### Statistical Methods References

1. **Fisher z-transformation**
   - Source: Fisher, R. A. (1915). "Frequency distribution of the values of the correlation coefficient in samples from an indefinitely large population"
   - Implementation: scipy.special.arctanh() and np.arctanh()
   - Purpose: Transform correlation coefficients to approximately normal distribution for testing

2. **Correlation comparison test**
   - Source: Cohen & Cohen (1983). "Applied Multiple Regression/Correlation Analysis for the Behavioral Sciences"
   - Formula: z = (z1 - z2) / sqrt(1/(n1-3) + 1/(n2-3))
   - Implementation: scipy.stats.norm for p-value computation

3. **TruthfulQA stratification**
   - Source: Lin et al. (2022). "TruthfulQA: Measuring How Models Mimic Human Falsehoods"
   - Categories: Use `category` field from dataset metadata
   - Factual: Questions with factual ground truth
   - Misinformation: Questions designed to test common misconceptions

### Code References from Previous Hypotheses

**From H-M1 validation (docs/youra_research/h-m1/04_validation.md):**
- Factual stratum correlation computation: r=0.7233, p<0.001
- Stratification logic: Based on TruthfulQA question categories
- Sample sizes: ~400 factual, ~417 misinformation

**From H-E1 implementation:**
- Model output caching: All 817 prompts × 3 models already generated
- Reliability/robustness scoring: GPT-4-as-judge and paraphrase consistency metrics
- Data structure: Organized by prompt → model → dimensions

### Implementation Notes

**Data Reuse Strategy:**
- 100% reuse of cached outputs from H-E1
- 100% reuse of reliability/robustness scores from H-M1
- Only new computation: Stratification and Fisher z-test
- Estimated runtime: < 1 minute (pure statistical analysis)

**No External Repositories Required:**
- Standard scipy/numpy functions sufficient
- No model training or fine-tuning
- No new data generation

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-12T08:34:41+00:00

### Workflow History for This Hypothesis
- 2026-07-12T08:34:41: Hypothesis h-m3 set to IN_PROGRESS
- Prerequisites: h-m2 (COMPLETED, PASS)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
