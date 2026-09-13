# Experiment Design: H-M3

**Date:** 2026-08-10
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** Under conversations where AI formality delta is small, if we measure perceived attentiveness proxies, then attentiveness indicators correlate with small deltas.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests causal pathway component.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (PASS), H-M1 (PASS), H-M2 (PASS)
**Gate Status:** SHOULD_WORK - Lowest delta tercile has highest continuation rate; monotonic trend

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (AI Formality Response Varies - PASSED)

### Gate Condition
**Pass Condition:** Lowest delta tercile has highest continuation rate; monotonic trend
**Fail Action:** PIVOT to alternative proxies (response time, thumbs up/down if available)

---

## Continuation Context

### Previous Hypothesis Results (H-M2)
- **Result:** PASS
- **Key Findings:**
  - Pearson r=0.152 (p=0.00, exceeds threshold 0.1)
  - n=111,039 (human_1, AI_1) pairs analyzed
  - AI formality correlates with human formality
  - Dataset: Anthropic/hh-rlhf
  - Model: s-nlp/deberta-large-formality-ranker

**Reuse from H-M2:**
- Same dataset (Anthropic/hh-rlhf) for controlled comparison
- Same formality scorer (DeBERTa) for consistent measurement
- Formality scores already computed can be cached/reused

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No direct matches for formality accommodation analysis. Primary sources are diffusers/attention mechanisms (not applicable).

### Archon Code Examples

No directly relevant code examples found in KB for tercile/continuation analysis.

### Exa GitHub Implementations

**Highly Relevant Finds:**

1. **GoldenSimba97/Alignment_in_Chatbots** (Python)
   - Research on formality alignment effect on user satisfaction
   - Three chatbot versions: linguistic alignment, current, formality alignment
   - User test results from 60 participants
   - URL: https://github.com/GoldenSimba97/Alignment_in_Chatbots

2. **Ananthasubramaniam et al. (2023) - Linguistic Style Matching in Reddit**
   - ACL paper on LSM using function words and formality
   - Examines conversation depth, user tenure, controversiality
   - Direct relevance: formality accommodation → engagement
   - URL: https://aclanthology.org/2023.sicon-1.7.pdf

3. **GuillaumeDD/pydialign** (Python)
   - Measures verbal alignment in dyadic dialogue
   - Shared expression tracking across turns
   - URL: https://github.com/GuillaumeDD/pydialign

4. **ferdinandschessl-boop/autocorrelation-correction**
   - CRITICAL: Autocorrelation correction for turn-level metrics
   - Block bootstrap for conversations as clusters
   - Prevents inflated p-values from within-conversation correlation
   - URL: https://github.com/ferdinandschessl-boop/autocorrelation-correction

### 🎯 Implementation Priority Assessment

**CRITICAL: No author implementation exists - this is novel analysis.**

**Recommended Implementation Path:**
- Primary: Custom tercile analysis pipeline using scipy.stats
- Fallback: Adaptation of autocorrelation-correction bootstrap method
- Justification: H-M3 requires novel tercile analysis; LSM paper methodology guides approach

### Code Analysis (Serena MCP)

Not applicable - no existing codebase to analyze. Custom implementation required.

---

## Experiment Specification

### Dataset

**Name:** Anthropic/hh-rlhf (reuse from H-M2)
**Type:** standard
**Source:** HuggingFace Datasets
**Size:** ~170K conversations (train+test)

**Preprocessing (from H-M2):**
1. Parse conversation structure (Human/Assistant turns)
2. Filter: ≥2 turns per side (multi-turn requirement)
3. Extract turn pairs: (human_i, AI_i) for formality scoring

**Loading Information** (for Phase 4 download):
- Method: HuggingFace
- Identifier: `Anthropic/hh-rlhf`
- Code:
```python
from datasets import load_dataset
ds = load_dataset("Anthropic/hh-rlhf")
```

**Sample Size Guidance:**
- Use FULL train+test split (~170K conversations)
- After filtering for ≥2 turns per side: ~111K conversations (from H-M2)
- Tercile bins: ~37K conversations each
- Statistically meaningful: far exceeds 500 minimum

### Models

#### Baseline Model

**Architecture:** s-nlp/deberta-large-formality-ranker (reuse from H-M2)
**Type:** Pretrained formality classifier
**Source:** HuggingFace

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `s-nlp/deberta-large-formality-ranker`
- Code:
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
tokenizer = AutoTokenizer.from_pretrained("s-nlp/deberta-large-formality-ranker")
model = AutoModelForSequenceClassification.from_pretrained("s-nlp/deberta-large-formality-ranker")
```

#### Proposed Model

**Architecture:** Tercile Analysis Pipeline (No ML model - statistical analysis)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Tercile-Based Accommodation-Continuation Analysis
# Based on: LSM methodology (Ananthasubramaniam et al., 2023)

import numpy as np
from scipy import stats

def compute_formality_delta(human_formality: float, ai_formality: float) -> float:
    """
    Compute absolute formality delta (accommodation measure).
    Small delta = high accommodation.
    
    Args:
        human_formality: Formality score of human turn [-1, 1]
        ai_formality: Formality score of AI response [-1, 1]
    Returns:
        Absolute delta (0 = perfect accommodation)
    """
    return abs(human_formality - ai_formality)

def tercile_continuation_analysis(
    deltas: np.ndarray,           # (N,) formality deltas
    continuations: np.ndarray,    # (N,) binary: 1=continued, 0=stopped
    conversation_ids: np.ndarray  # (N,) for cluster bootstrap
) -> dict:
    """
    Core H-M3 Analysis: Test if low delta → high continuation.
    
    Returns:
        tercile_rates: Continuation rate per tercile
        monotonic: True if rate decreases with delta
        spearman_rho: Correlation between delta and continuation
        p_value: Cluster-robust p-value
    """
    # Step 1: Compute tercile thresholds
    t1, t2 = np.percentile(deltas, [33.33, 66.67])
    
    # Step 2: Assign terciles (1=low delta, 3=high delta)
    terciles = np.where(deltas <= t1, 1,
                np.where(deltas <= t2, 2, 3))
    
    # Step 3: Compute continuation rate per tercile
    tercile_rates = {}
    for t in [1, 2, 3]:
        mask = (terciles == t)
        tercile_rates[t] = continuations[mask].mean()
    
    # Step 4: Check monotonic trend (low delta → high rate)
    rates = [tercile_rates[1], tercile_rates[2], tercile_rates[3]]
    monotonic = rates[0] > rates[1] > rates[2]
    
    # Step 5: Spearman correlation (rank-based, robust)
    rho, p_naive = stats.spearmanr(deltas, continuations)
    
    # Step 6: Cluster bootstrap for robust p-value
    # (Block bootstrap: resample whole conversations)
    p_robust = cluster_bootstrap_pvalue(
        deltas, continuations, conversation_ids, n_boot=2000
    )
    
    return {
        "tercile_rates": tercile_rates,
        "monotonic": monotonic,
        "spearman_rho": rho,
        "p_naive": p_naive,
        "p_robust": p_robust,
        "n_samples": len(deltas)
    }

# Integration: After formality scoring, before results aggregation
```

### Training Protocol

**Not Applicable** - H-M3 is statistical analysis, not model training.

**Analysis Protocol:**
1. Load conversations from Anthropic/hh-rlhf
2. Filter for ≥2 turns per side
3. Score formality using DeBERTa (cached from H-M2 if available)
4. Compute formality delta per (human, AI) turn pair
5. Define continuation: 1 if user sends another message, 0 if conversation ends
6. Run tercile analysis
7. Compute cluster-robust statistics

**Computational Parameters:**
- Bootstrap iterations: 2000
- Random seed: 42
- Confidence level: 95%

### Evaluation

**Primary Metrics:**
- Tercile continuation rates (T1, T2, T3)
- Spearman rho (delta vs continuation)
- Monotonic trend flag (boolean)

**Success Criteria (Gate):**
- Lowest delta tercile (T1) has HIGHEST continuation rate
- Monotonic trend: rate(T1) > rate(T2) > rate(T3)
- p_robust < 0.05 (cluster-corrected)

**Expected Baseline Performance:**
- From LSM literature (Niederhoffer & Pennebaker): accommodation r ~ 0.1-0.3
- If no accommodation effect: tercile rates should be equal (~33% each)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: correlation_analysis
- Library: scipy.stats
- Code:
```python
from scipy.stats import spearmanr, pearsonr
import numpy as np
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Tercile continuation rates bar chart (T1 vs T2 vs T3)

#### Additional Figures (LLM Autonomous)
1. **Delta Distribution Histogram**: Show formality delta distribution with tercile boundaries
2. **Scatter Plot**: Delta vs continuation (jittered binary) with trend line
3. **Bootstrap Distribution**: Histogram of bootstrap rho values with observed rho marked

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: True - tercile binning and rate computation are standard stats
- `mechanism_isolatable`: True - delta computation is independent operation
- `baseline_measurable`: True - null hypothesis = equal tercile rates

### Architecture Compatibility
- No neural architecture - pure statistical analysis
- Dependencies: numpy, scipy, pandas
- Formality scorer: DeBERTa (pretrained, no training)

### Activation Indicators
- `mechanism_log_message`: "Tercile boundaries: T1<={t1:.3f}, T2<={t2:.3f}"
- `tensor_shape_change`: N/A (no tensors)
- `metric_delta_expected`: T1 rate - T3 rate > 0.05 (5% difference)

### Mechanism Verification Code
```python
def verify_mechanism(tercile_rates: dict) -> dict:
    """Verify H-M3 mechanism activation."""
    t1_rate = tercile_rates[1]
    t2_rate = tercile_rates[2]
    t3_rate = tercile_rates[3]
    
    mechanism_active = (t1_rate > t3_rate)  # Basic direction check
    monotonic = (t1_rate > t2_rate > t3_rate)  # Full trend
    effect_size = t1_rate - t3_rate  # Rate difference
    
    return {
        "mechanism_active": mechanism_active,
        "monotonic_trend": monotonic,
        "effect_size": effect_size,
        "passes_gate": monotonic and (effect_size > 0)
    }
```

### Success Criteria
- `hypothesis_support_threshold`: Monotonic trend with p_robust < 0.05
- `hypothesis_support_metric`: Spearman rho (negative = low delta → high continuation)

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Tercile analysis completes on full dataset
3. T1 continuation rate > T3 continuation rate (direction check)
4. Monotonic trend observed: T1 > T2 > T3

**Gate Pass Condition (Full):**
- Monotonic trend confirmed
- p_robust < 0.05 (cluster-corrected)

---

## Appendix: Reference Implementations

### Primary References

1. **LSM Methodology**
   - Ananthasubramaniam et al. (2023). "Exploring Linguistic Style Matching in Online Communities"
   - ACL SiCon Workshop
   - URL: https://aclanthology.org/2023.sicon-1.7.pdf
   - Relevance: Formality-based LSM, conversation engagement metrics

2. **Autocorrelation Correction**
   - ferdinandschessl-boop/autocorrelation-correction (GitHub)
   - Block bootstrap for turn-level metrics
   - URL: https://github.com/ferdinandschessl-boop/autocorrelation-correction
   - Relevance: Cluster-robust p-values for conversation data

3. **Formality Alignment in Chatbots**
   - GoldenSimba97/Alignment_in_Chatbots
   - User satisfaction study with formality-aligned chatbot
   - URL: https://github.com/GoldenSimba97/Alignment_in_Chatbots

4. **Verbal Alignment Measures**
   - GuillaumeDD/pydialign
   - Shared expression tracking in dialogue
   - URL: https://github.com/GuillaumeDD/pydialign

### Statistical Methods

5. **scipy.stats.spearmanr**
   - SciPy Documentation
   - URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html

6. **Bootstrap Methods**
   - Efron & Tibshirani (1993). "An Introduction to the Bootstrap"
   - Block bootstrap for dependent data

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10T08:45:00+00:00

### Workflow History for This Hypothesis
- H-E1 COMPLETED: BCS SD=0.569 (PASS)
- H-M1 COMPLETED: Lag-1 r=0.0134 (PASS)
- H-M2 COMPLETED: Pearson r=0.152 (PASS)
- H-M3 IN_PROGRESS: Experiment design generated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
