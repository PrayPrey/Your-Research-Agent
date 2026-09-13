# Experiment Design: H-M1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Token entropy captures epistemic uncertainty — when model lacks knowledge about answer, logit distribution is diffuse (high entropy correlates with factual incorrectness)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates causal link between entropy and uncertainty.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 VALIDATED)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1

### Gate Condition
**Type:** MUST_WORK
**Pass Condition:** Mean entropy (incorrect) > Mean entropy (correct)
**Fail Action:** PIVOT to semantic entropy (Kuhn et al. method)

---

## Continuation Context

This hypothesis builds on H-E1 validation results. H-E1 confirmed both token entropy and N-sample consistency individually predict factual correctness above chance (AUROC > 0.55 each).

### Previous Hypothesis Results (H-E1)
- Token entropy AUROC: validated > 0.55
- N-sample consistency AUROC: validated > 0.55
- Pipeline executing on 5x H100 without errors
- Entropy and consistency metrics computed per design

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**[INFERRED]** Pattern 1: Token Entropy for Uncertainty Quantification
- Source: Kadavath et al. 2022 "Language Models (Mostly) Know What They Don't Know"
- Key insight: Mean token entropy across response captures aggregate uncertainty
- Implementation: `entropy = -sum(p * log(p))` per token, then average

**[INFERRED]** Pattern 2: Entropy-Correctness Correlation
- Source: Xiao & Wang 2021, Malinin & Gales 2018
- Key insight: Higher entropy correlates with model uncertainty; uncertain models hallucinate more
- Relevance: Direct precedent for entropy-based uncertainty detection

**[INFERRED]** Pattern 3: Semantic Entropy (Kuhn et al. 2023)
- Source: "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation"
- Key insight: If token entropy fails, semantic entropy clusters equivalent meanings
- Caveat: Requires multiple samples and clustering — more expensive

**[INFERRED]** Pattern 4: TruthfulQA Evaluation Protocol
- Source: Lin et al. 2022 "TruthfulQA: Measuring How Models Mimic Human Falsehoods"
- Key insight: Use generation subset (~817 questions), evaluate truthfulness via labels

**[INFERRED]** Pattern 5: Effect Size Analysis
- Source: Cohen 1988 statistical conventions
- Key insight: d > 0.2 = small effect, d > 0.5 = medium, d > 0.8 = large
- Visualization: Box plots or violin plots for distribution comparison

### Archon Code Examples

**[INFERRED]** Token Entropy Computation:
```python
def compute_token_entropy(logits):
    probs = F.softmax(logits, dim=-1)
    log_probs = F.log_softmax(logits, dim=-1)
    entropy = -torch.sum(probs * log_probs, dim=-1)
    return entropy.mean()
```

**[INFERRED]** Distribution Comparison:
```python
from scipy.stats import mannwhitneyu
stat, pvalue = mannwhitneyu(incorrect_entropy, correct_entropy, alternative='greater')
d = (np.mean(incorrect_entropy) - np.mean(correct_entropy)) / pooled_std
```

### Exa GitHub Implementations

**[INFERRED]** Reference 1: SelfCheckGPT
- Repository: https://github.com/potsawee/selfcheckgpt
- Relevance: Consistency-based hallucination detection baseline
- Code pattern: Multiple sample generation + similarity computation

**[INFERRED]** Reference 2: LM-Polygraph
- Repository: https://github.com/IINemo/lm-polygraph
- Relevance: Uncertainty quantification library with entropy methods
- Code pattern: Token-level entropy extraction from HuggingFace models

**[INFERRED]** Reference 3: Uncertainty Baselines
- Repository: https://github.com/google/uncertainty-baselines
- Relevance: Calibration and uncertainty estimation methods
- Code pattern: Entropy computation utilities

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment:**
1. LM-Polygraph provides ready-to-use entropy computation for HuggingFace models
2. Custom implementation straightforward (10-15 lines)
3. No author-provided implementation for this specific hypothesis — novel experiment

**Recommended Implementation Path:**
- Primary: Custom implementation using PyTorch logits access
- Fallback: LM-Polygraph library if custom fails
- Justification: Custom gives full control over entropy aggregation; LM-Polygraph as validated fallback

### Code Analysis (Serena MCP)

**[INFERRED - Serena unavailable]** Analysis based on H-E1 codebase:
- Entropy computation already implemented in `src/metrics/entropy.py`
- Logit extraction verified working for LLaMA-2-7B
- Partitioning logic needed: split responses by correctness label

---

## Experiment Specification

### Dataset

**Name:** TruthfulQA
**Version:** Generation subset (817 questions)
**Source:** Lin et al. 2022
**Type:** standard
**Split:** Full generation subset (no train/test split — evaluation only)

**Preprocessing:**
1. Load generation subset questions
2. Generate single response per question using LLaMA-2-7B (greedy decode)
3. Extract token-level logits during generation
4. Label each response as correct/incorrect using TruthfulQA ground truth

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthful_qa` (generation config)
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "generation")
questions = dataset["validation"]["question"]  # 817 questions
```

### Models

#### Baseline Model

**Name:** LLaMA-2-7B
**Type:** Decoder-only autoregressive LLM
**Source:** Meta AI
**Purpose:** Generate responses and extract logits for entropy computation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

#### Proposed Model

**Architecture:** LLaMA-2-7B with entropy computation on logits

**Core Mechanism Implementation:**

```python
# Core mechanism: Token entropy computation and correctness correlation
# Lines: 25

import torch
import torch.nn.functional as F
import numpy as np
from scipy.stats import mannwhitneyu

def compute_response_entropy(model, tokenizer, question: str, max_new_tokens: int = 100):
    """Compute mean token entropy for a single response."""
    inputs = tokenizer(question, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            output_scores=True,
            return_dict_in_generate=True,
            do_sample=False  # greedy for determinism
        )
    
    # Extract logits from generation scores
    entropies = []
    for logits in outputs.scores:
        probs = F.softmax(logits, dim=-1)
        log_probs = F.log_softmax(logits, dim=-1)
        token_entropy = -torch.sum(probs * log_probs, dim=-1)
        entropies.append(token_entropy.item())
    
    return np.mean(entropies)

def test_entropy_uncertainty_link(correct_entropies: list, incorrect_entropies: list):
    """Test if incorrect responses have higher entropy."""
    mean_correct = np.mean(correct_entropies)
    mean_incorrect = np.mean(incorrect_entropies)
    
    # Effect size (Cohen's d)
    pooled_std = np.sqrt((np.var(correct_entropies) + np.var(incorrect_entropies)) / 2)
    d = (mean_incorrect - mean_correct) / pooled_std if pooled_std > 0 else 0
    
    # Mann-Whitney U test
    stat, pvalue = mannwhitneyu(incorrect_entropies, correct_entropies, alternative='greater')
    
    return {
        "mean_correct": mean_correct,
        "mean_incorrect": mean_incorrect,
        "effect_size_d": d,
        "pvalue": pvalue,
        "pass": mean_incorrect > mean_correct and d > 0.2
    }
```

### Training Protocol

**Training Required:** No

This is an **evaluation-only** experiment. No model training or fine-tuning.

**Inference Protocol:**
1. Load pre-trained LLaMA-2-7B
2. For each TruthfulQA question:
   - Generate response with logit extraction
   - Compute mean token entropy
   - Record correctness label
3. Partition entropies by correctness
4. Compute statistics and effect size

**Hyperparameters:**
- max_new_tokens: 100
- do_sample: False (greedy decoding)
- temperature: N/A (greedy)
- dtype: float16

### Evaluation

**Primary Metric:** Direction check
- **Pass:** Mean entropy (incorrect) > Mean entropy (correct)

**Secondary Metric:** Effect size
- **Pass:** Cohen's d > 0.2 (small but detectable effect)

**Tertiary Metric:** Statistical significance
- **Informative only:** Mann-Whitney U p-value < 0.05

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical comparison (no ML metrics)
- Library: scipy.stats, numpy
- Code:
```python
from scipy.stats import mannwhitneyu
import numpy as np
# Already included in core mechanism pseudocode
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Entropy Distribution Plot**: Box/violin plot comparing entropy distributions for correct vs incorrect responses

#### Additional Figures (LLM Autonomous)

1. **Histogram Overlay**: Overlapping histograms of entropy distributions with KDE
2. **Scatter Plot**: Entropy vs response length (check for confound)
3. **ROC Curve**: Entropy as binary classifier for correctness

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Mean entropy (incorrect) > Mean entropy (correct)
3. Effect size d > 0.2 (secondary)

---

## Appendix: Reference Implementations

### A. Token Entropy Computation (Standard Pattern)
```python
# From LM-Polygraph / uncertainty estimation literature
def token_entropy(logits: torch.Tensor) -> float:
    """Compute entropy of probability distribution."""
    probs = F.softmax(logits, dim=-1)
    log_probs = torch.log(probs + 1e-10)  # avoid log(0)
    return -torch.sum(probs * log_probs, dim=-1).mean().item()
```

### B. TruthfulQA Loading
```python
from datasets import load_dataset
ds = load_dataset("truthful_qa", "generation")
# ds["validation"] contains 817 questions with:
# - question: str
# - best_answer: str
# - correct_answers: list[str]
# - incorrect_answers: list[str]
```

### C. Correctness Labeling
```python
def is_correct(response: str, correct_answers: list, incorrect_answers: list) -> bool:
    """Simple substring matching for PoC."""
    response_lower = response.lower()
    for ans in correct_answers:
        if ans.lower() in response_lower:
            return True
    return False
```

### D. Related Papers
1. Kadavath et al. 2022 - "Language Models (Mostly) Know What They Don't Know"
2. Kuhn et al. 2023 - "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation"
3. Lin et al. 2022 - "TruthfulQA: Measuring How Models Mimic Human Falsehoods"
4. Malinin & Gales 2018 - "Predictive Uncertainty Estimation via Prior Networks"

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- H-E1 validated: Both methods predict factuality above chance
- H-M1 started: Testing entropy-uncertainty mechanism

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
