# Experiment Design: h-e1

**Date:** 2026-04-19
**Author:** Anonymous
**Hypothesis Statement:** Under the scope of HH-RLHF harmless-preference annotation, if we perform blinded human audit of rejected samples, then we will find ≥40% contain genuine safety policy violations (not marginal preferences), because annotators used explicit harmlessness criteria that distinguish violations from style differences.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** None (foundation hypothesis)
**Gate Status:** MUST_WORK gate active

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (first in chain)

### Gate Condition
Base-rate p ≥ 0.40 with binomial test p-value < 0.05
- **Failure Action:** STOP - reassess entire hypothesis or pivot framing

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous results to integrate.

### Previous Hypothesis Results (if applicable)
N/A - Foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Service Status:** Not available (no-MCP execution mode)

*Alternative research approach:* Literature-based annotation protocol design using standard inter-rater reliability methods.

### Archon Code Examples

**MCP Service Status:** Not available (no-MCP execution mode)

*Alternative approach:* Standard annotation study implementations using Cohen's κ and binomial tests.

### Exa GitHub Implementations

**MCP Service Status:** Not available (no-MCP execution mode)

*Alternative approach:* Standard statistical testing libraries (scipy, statsmodels) for binomial tests and inter-rater agreement.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Since this is a novel base-rate validation study (not reproducing prior work), we use standard annotation protocols.

**Recommended Implementation Path:**
- Primary: Custom annotation interface + standard statistical tests (scipy)
- Fallback: Manual annotation spreadsheet + R statistical tests
- Justification: EXISTENCE hypothesis requires human evaluation, not ML model implementation

### Code Analysis (Serena MCP)

**MCP Service Status:** Not available (no-MCP execution mode)

*Not applicable:* This hypothesis tests dataset properties via human annotation, not code analysis.

---

## Experiment Specification

### Dataset

**Dataset:** HH-RLHF harmless subset (Anthropic/hh-rlhf)
- **Source:** Hugging Face Datasets
- **URL:** https://huggingface.co/datasets/Anthropic/hh-rlhf
- **Subset:** harmless-base (rejected responses only for audit)
- **Sample Size:** 500 rejected responses (stratified random sampling)
- **Sampling Strategy:** Stratified by response length quartiles to avoid length bias
- **Annotation Protocol:** Blinded 3-annotator review with explicit violation criteria

**Violation Criteria (for annotators):**
1. Direct harm/violence encouragement
2. Toxic/offensive language
3. Privacy violations or personal information disclosure
4. Dangerous/illegal advice
5. Deception or misinformation
6. Other safety policy violations

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets API
- Identifier: Anthropic/hh-rlhf
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("Anthropic/hh-rlhf", "harmless-base")
rejected_samples = dataset['train']['rejected']
```

### Models

#### Baseline Model

**No ML model required** - This is a human annotation study validating dataset properties.

**Human Annotation Protocol:**
- 3 independent annotators
- Blinded to original HH-RLHF labels
- Trained on explicit harmlessness criteria
- Binary judgment per sample: "genuine violation" vs "marginal preference"

**Loading Information** (for Phase 4 download):
- Method: Annotation interface (web-based or spreadsheet)
- Identifier: Custom annotation tool
- Code: Annotation UI or Google Sheets template

#### Proposed Model

**Architecture:** Human evaluation (no ML architecture)

**Core Mechanism Implementation:**

```python
# Annotation Protocol Pseudo-code (10-30 lines)

def conduct_annotation_study(rejected_samples, n_annotators=3, sample_size=500):
    """
    Conduct blinded human audit of HH-RLHF rejected responses.
    
    Args:
        rejected_samples: List of rejected responses from HH-RLHF
        n_annotators: Number of independent annotators (default 3)
        sample_size: Number of samples to audit (default 500)
    
    Returns:
        base_rate: Proportion of genuine violations
        kappa: Inter-annotator agreement (Cohen's κ)
        p_value: Binomial test p-value for H1: p >= 0.40
    """
    
    # Step 1: Stratified sampling by response length
    sampled_responses = stratified_sample(rejected_samples, n=sample_size, 
                                          strata='length_quartile')
    
    # Step 2: Collect annotations (blinded, independent)
    annotations = []
    for annotator_id in range(n_annotators):
        annotator_labels = collect_annotations(
            samples=sampled_responses,
            annotator=annotator_id,
            criteria=VIOLATION_CRITERIA,
            blinded=True
        )
        annotations.append(annotator_labels)
    
    # Step 3: Compute inter-annotator agreement (Cohen's κ)
    kappa = compute_cohens_kappa(annotations)
    
    # Step 4: Majority vote for final labels
    final_labels = majority_vote(annotations)
    
    # Step 5: Calculate base-rate (proportion of genuine violations)
    base_rate = sum(final_labels) / len(final_labels)
    
    # Step 6: Binomial test H0: p < 0.40 vs H1: p >= 0.40
    p_value = binomial_test(n_successes=sum(final_labels), 
                            n_trials=sample_size, 
                            p_null=0.40, 
                            alternative='greater')
    
    return base_rate, kappa, p_value
```

### Training Protocol

**No training required** - Human annotation study

**Annotation Collection:**
- **Annotators:** 3 independent raters
- **Training:** 1-hour session on HH-RLHF harmlessness criteria
- **Calibration:** 50-sample pilot annotation with discussion
- **Production:** 500-sample blinded annotation (no inter-annotator communication)
- **Duration:** ~2-3 hours per annotator for 500 samples
- **Quality Control:** Monitor κ on calibration set; require κ ≥ 0.60 to proceed

### Evaluation

**Primary Metrics:**
1. **Base-rate (p):** Proportion of genuine violations in sampled rejected responses
   - **Success Criterion:** p ≥ 0.40
   - **Test:** Binomial test with α = 0.05 (one-tailed, H1: p ≥ 0.40)

2. **Inter-annotator Agreement (κ):** Cohen's κ across 3 annotators
   - **Success Criterion:** κ ≥ 0.75 (substantial agreement)
   - **Interpretation:** κ < 0.60 (poor), 0.60-0.75 (moderate), ≥ 0.75 (substantial)

**Secondary Analysis:**
- Agreement with original HH-RLHF labels (proportion)
- Violation type distribution (which criteria most common)
- Length bias analysis (violation rate vs response length)

**PoC Success Condition:**
- Primary: p ≥ 0.40 AND binomial test p-value < 0.05
- Secondary: κ ≥ 0.75

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Inter-rater reliability + binomial test
- Library: statsmodels (Cohen's κ), scipy.stats (binomial_test)
- Code:
```python
from statsmodels.stats.inter_rater import cohens_kappa
from scipy.stats import binomtest

kappa = cohens_kappa(ratings_matrix)
result = binomtest(k=n_violations, n=sample_size, p=0.40, alternative='greater')
p_value = result.pvalue
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing base-rate p vs threshold (0.40), with binomial test p-value annotation

#### Additional Figures (LLM Autonomous)

1. **Inter-annotator Agreement Matrix:** Heatmap showing pairwise agreement rates between 3 annotators
2. **Violation Type Distribution:** Bar chart of violation criteria frequency (which safety violations most common)
3. **Length Bias Analysis:** Scatter plot of violation rate vs response length quartile
4. **Agreement with HH-RLHF:** Confusion matrix comparing majority-vote labels vs original HH-RLHF rejected labels

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (annotation interface functional, statistical tests execute)
2. `base_rate >= 0.40` AND `binomial_p_value < 0.05`

**MUST_WORK Gate:**
- **PASS:** If p ≥ 0.40 and p-value < 0.05 → Proceed to H-M1
- **FAIL:** If p < 0.40 → **STOP WORKFLOW** → Reassess hypothesis or pivot framing

---

## Appendix: Reference Implementations

### Statistical Testing References
1. **Cohen's κ calculation:**
   - Library: statsmodels.stats.inter_rater.cohens_kappa
   - Paper: Cohen, J. (1960). "A coefficient of agreement for nominal scales"
   
2. **Binomial Test:**
   - Library: scipy.stats.binomtest
   - Documentation: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html

### Annotation Protocol References
1. **HH-RLHF Paper:** Bai et al. (2022). "Training a Helpful and Harmless Assistant with RLHF"
   - Appendix: Annotation guidelines for harmlessness criteria
   
2. **Inter-Rater Reliability:** Landis & Koch (1977). "The measurement of observer agreement"
   - κ interpretation: < 0.00 (poor), 0.00-0.20 (slight), 0.21-0.40 (fair), 0.41-0.60 (moderate), 0.61-0.80 (substantial), 0.81-1.00 (almost perfect)

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-19T13:56:37+00:00

### Workflow History for This Hypothesis
- 2026-04-19T13:56:37: Hypothesis h-e1 set to IN_PROGRESS (Phase 2C start)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: None (no-MCP execution mode)*
*All specifications grounded in standard annotation study methodology*
*Next Phase: Phase 3 - Implementation Planning*
