# Experiment Design: H-E1

**Date:** 2026-08-26
**Author:** PrayPrey
**Hypothesis Statement:** Under standard evaluation conditions, if we compute correlations between TruthfulQA, HHH-helpful, and HHH-harmless scores on base Llama-2-7B, then pairwise correlations will be < 0.5, because these benchmarks were designed to measure distinct alignment dimensions.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (none required)
**Gate Status:** MUST_WORK - not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
All pairwise correlations between TruthfulQA, HHH-helpful, and HHH-harmless scores must be < 0.5. If any correlation >= 0.5, benchmarks are too correlated and pipeline STOPS.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous context.

### Previous Hypothesis Results (if applicable)
N/A - Foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP unavailable in this session.** Using domain knowledge:

1. **TruthfulQA** (Lin et al., 2021): 817 questions testing model truthfulness across 38 categories. MC1/MC2 scoring.
2. **HHH-helpful** (Askell et al., 2021): Subset of Anthropic's HHH evaluation focusing on helpfulness.
3. **HHH-harmless** (Askell et al., 2021): Subset focusing on harmlessness/safety.

### Archon Code Examples

Standard evaluation approaches:
- `lm-evaluation-harness` (EleutherAI): Standard framework for LLM evaluation
- HuggingFace `evaluate` library for metric computation
- Direct logit extraction for MC tasks

### Exa GitHub Implementations

**Primary Implementation Sources:**
1. EleutherAI/lm-evaluation-harness: Standard evaluation framework
2. HuggingFace evaluate library
3. Anthropic HHH eval dataset: `Anthropic/hh-rlhf`

### 🎯 Implementation Priority Assessment

**CRITICAL: For benchmark evaluation, use established evaluation harnesses**

**Recommended Implementation Path:**
- Primary: `lm-evaluation-harness` for TruthfulQA
- Fallback: Custom evaluation script using HuggingFace datasets
- Justification: Established, reproducible evaluation infrastructure

### Code Analysis (Serena MCP)

**MCP unavailable.** Using standard evaluation patterns:
- TruthfulQA: Multiple-choice accuracy (MC1, MC2)
- HHH: Preference-based scoring (chosen vs rejected)
- Correlation: Pearson correlation on per-sample scores

---

## Experiment Specification

### Dataset

**TruthfulQA Dataset:**
- **Name:** TruthfulQA
- **Type:** standard
- **Source:** HuggingFace datasets
- **Size:** 817 questions (full test set)
- **Task:** Multiple-choice QA for truthfulness

**HHH Dataset (Helpful subset):**
- **Name:** HHH-helpful
- **Type:** standard
- **Source:** Anthropic/hh-rlhf (helpful subset)
- **Size:** Full evaluation split
- **Task:** Preference scoring

**HHH Dataset (Harmless subset):**
- **Name:** HHH-harmless
- **Type:** standard
- **Source:** Anthropic/hh-rlhf (harmless subset)
- **Size:** Full evaluation split
- **Task:** Preference scoring

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthful_qa`, `Anthropic/hh-rlhf`
- Code:
```python
from datasets import load_dataset
truthful_qa = load_dataset("truthful_qa", "multiple_choice")
hh_rlhf = load_dataset("Anthropic/hh-rlhf")
```

### Models

#### Baseline Model

**Architecture:** Llama-2-7B (base, no alignment training)
**Type:** decoder-only transformer
**Source:** meta-llama/Llama-2-7b-hf
**Parameters:** 7 billion
**Configuration:** Default pretrained weights, no fine-tuning

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

#### Proposed Model

**Architecture:** Same as baseline (evaluation-only hypothesis)

**Core Mechanism Implementation:**

This is an EXISTENCE hypothesis testing benchmark independence, not a model modification. The "mechanism" is the correlation analysis itself.

```python
# Core Mechanism: Benchmark Correlation Analysis
# Purpose: Verify alignment benchmarks measure distinct dimensions

import numpy as np
from scipy.stats import pearsonr

def compute_benchmark_correlations(scores_dict):
    """
    Compute pairwise Pearson correlations between benchmark scores.
    
    Args:
        scores_dict: {
            'truthfulqa': np.array of per-sample scores,
            'hhh_helpful': np.array of per-sample scores,
            'hhh_harmless': np.array of per-sample scores
        }
    
    Returns:
        dict of pairwise correlations
    """
    benchmarks = list(scores_dict.keys())
    correlations = {}
    
    for i, b1 in enumerate(benchmarks):
        for b2 in benchmarks[i+1:]:
            r, p = pearsonr(scores_dict[b1], scores_dict[b2])
            correlations[f"{b1}_vs_{b2}"] = {"r": r, "p": p}
    
    return correlations

def check_independence_gate(correlations, threshold=0.5):
    """Gate check: All correlations must be < threshold."""
    all_pass = all(abs(c["r"]) < threshold for c in correlations.values())
    return all_pass, correlations
```

### Training Protocol

**N/A - Evaluation-only hypothesis**

This hypothesis does not involve training. It evaluates benchmark correlations on the base (unaligned) model.

**Evaluation Protocol:**
1. Load base Llama-2-7B (no alignment)
2. Evaluate on TruthfulQA (817 samples, MC1 accuracy)
3. Evaluate on HHH-helpful (full eval split, preference accuracy)
4. Evaluate on HHH-harmless (full eval split, preference accuracy)
5. Extract per-sample scores for correlation analysis
6. Compute pairwise Pearson correlations
7. Check gate condition: all |r| < 0.5

**Seeds:** 1 (fixed, evaluation only)

### Evaluation

**Primary Metrics:**
- Pairwise Pearson correlation coefficients (3 pairs)
- Per-benchmark accuracy scores

**Success Criteria:**
- All pairwise |r| < 0.5 (benchmarks measure distinct dimensions)
- Clear separation in score distributions

**Expected Baseline Performance:**
- TruthfulQA MC1: ~25-35% (base models typically low)
- HHH-helpful: ~50-55% (near random for base)
- HHH-harmless: ~50-55% (near random for base)
- Expected correlations: < 0.3 (benchmarks designed to be distinct)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: multiple-choice + preference classification
- Library: scipy.stats (pearsonr), numpy
- Code:
```python
from scipy.stats import pearsonr
import numpy as np

# Compute correlation
r, p = pearsonr(scores_a, scores_b)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Correlation Matrix Heatmap**: 3x3 matrix showing pairwise correlations
- **Gate Status Bar**: Pass/fail visualization for r < 0.5 threshold

#### Additional Figures (LLM Autonomous)

- Score distribution histograms per benchmark
- Scatter plots of benchmark pairs with regression lines

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. All pairwise correlations < 0.5 (gate condition)

**Gate Type:** MUST_WORK
**Failure Action:** STOP pipeline (benchmarks too correlated for profile analysis)

---

## Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** Yes (correlation analysis)
- **mechanism_isolatable:** Yes (pure evaluation, no training confounds)
- **baseline_measurable:** Yes (base model evaluation)

### Architecture Compatibility
- Model: Llama-2-7B compatible with all benchmarks
- Tokenizer: Standard HuggingFace tokenizer
- Memory: ~14GB GPU for 7B model inference

### Activation Indicators
- **mechanism_log_message:** "Computing pairwise correlations..."
- **tensor_shape_change:** N/A (no tensor modification)
- **metric_delta_expected:** Correlations in range [-1, 1]

### Verification Code
```python
def verify_mechanism(correlations):
    """Verify correlation analysis executed correctly."""
    # Check all pairs computed
    expected_pairs = 3  # (TQ, HH-help), (TQ, HH-harm), (HH-help, HH-harm)
    assert len(correlations) == expected_pairs, "Missing correlation pairs"
    
    # Check values in valid range
    for pair, stats in correlations.items():
        assert -1 <= stats['r'] <= 1, f"Invalid correlation: {stats['r']}"
        assert 0 <= stats['p'] <= 1, f"Invalid p-value: {stats['p']}"
    
    return True
```

### Success Criteria
- **hypothesis_support_threshold:** 0.5
- **hypothesis_support_metric:** max(|r|) < 0.5

---

## Appendix: Reference Implementations

### Evaluation Framework
- **lm-evaluation-harness**: https://github.com/EleutherAI/lm-evaluation-harness
  - Standard TruthfulQA evaluation
  - Reproducible benchmarking

### Datasets
- **TruthfulQA**: https://github.com/sylinrl/TruthfulQA
  - Lin et al., 2021
  - 817 questions, 38 categories

- **HHH**: https://github.com/anthropics/hh-rlhf
  - Askell et al., 2021
  - Helpful/Harmless/Honest evaluation

### Statistical Methods
- Pearson correlation: scipy.stats.pearsonr
- Standard statistical test for linear relationship

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-26

### Workflow History for This Hypothesis
- Phase 2C experiment design started: 2026-08-26

---

*MCP Tools Used: None available (domain knowledge used)*
*All specifications grounded in established evaluation practices*
*Next Phase: Phase 3 - Implementation Planning*
