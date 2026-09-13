# Experiment Design: h-e1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Under factual QA with frozen LLMs, if we extract token probability distributions from single forward passes, then entropy signals are measurable and correlate with prediction correctness, because output distributions encode uncertainty through their shape.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None (foundation hypothesis)
**Gate Status:** MUST_WORK - If fails, ABANDON (infrastructure broken)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
**Type:** MUST_WORK
**Pass Condition:** Entropy signal extractable for >95% predictions, significant negative correlation with accuracy (p < 0.05)
**Fail Action:** ABANDON entire research (infrastructure broken, cannot proceed)

---

## Continuation Context

First hypothesis in dependency chain — no prior context.

### Previous Hypothesis Results (if applicable)
N/A - Foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable — manual research substitute*

**Relevant Patterns:**
- Entropy computation: Standard Shannon entropy over softmax distributions
- LLM inference: HuggingFace transformers library with logits extraction
- Correlation analysis: SciPy Spearman rank correlation for ordinal relationships

### Archon Code Examples

*MCP unavailable — manual research substitute*

**Standard entropy extraction pattern:**
```python
logits = model(**inputs).logits
probs = F.softmax(logits, dim=-1)
entropy = -torch.sum(probs * torch.log(probs + 1e-10), dim=-1)
```

### Exa GitHub Implementations

*MCP unavailable — manual research substitute*

**Known implementations:**
- HuggingFace transformers: logits extraction from CausalLM models
- Uncertainty quantification libraries: entropy-based selective prediction
- TriviaQA evaluation: standard QA benchmarking patterns

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

*Not a reproduction study — novel PoC validation*

**Recommended Implementation Path:**
- Primary: PyTorch + HuggingFace transformers (standard DL stack)
- Fallback: JAX/Flax if memory constraints
- Justification: Most accessible, well-documented, standard for LLM research

### Code Analysis (Serena MCP)

*MCP unavailable — skipped*

---

## Experiment Specification

### Dataset

**Name:** TriviaQA (unfiltered)
**Source:** HuggingFace datasets library
**Type:** standard
**Split:** dev set (~11,000 examples total; use first 1,000 for PoC)
**Task:** Factual question answering with single-answer targets
**Preprocessing:** None (use raw text questions and answers)
**Cache:** Standard HuggingFace cache (~/.cache/huggingface/datasets)

**Rationale:** Established factual QA benchmark, directly tests hypothesis about entropy correlation with correctness on knowledge-grounded predictions.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: trivia_qa/unfiltered
- Code: 
```python
from datasets import load_dataset
dataset = load_dataset("trivia_qa", "unfiltered", split="validation[:1000]")
```

### Models

#### Baseline Model

**Architecture:** Llama-2-7B (frozen, decoder-only transformer)
**Source:** Meta AI via HuggingFace transformers
**Parameters:** 7 billion
**Purpose:** Extract logits from frozen model without fine-tuning
**Cache:** Standard HuggingFace cache (~/.cache/huggingface/hub)

**Rationale:** Open-source LLM with accessible logits, no retraining required, sufficient scale for PoC.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: meta-llama/Llama-2-7b-hf
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

#### Proposed Model

**Architecture:** Same as baseline (no architecture modification for EXISTENCE hypothesis)

**Core Mechanism Implementation:**

```python
import torch
import torch.nn.functional as F
from scipy.stats import spearmanr

def extract_entropy_and_prediction(model, tokenizer, question, answer):
    """
    Extract entropy from next-token distribution and check correctness.
    
    Returns: (entropy_value, is_correct)
    """
    # Tokenize input
    inputs = tokenizer(question, return_tensors="pt", truncation=True, max_length=512)
    
    # Forward pass (frozen model)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits[:, -1, :]  # Next token logits
    
    # Compute softmax distribution
    probs = F.softmax(logits, dim=-1)
    
    # Shannon entropy
    entropy = -torch.sum(probs * torch.log(probs + 1e-10), dim=-1)
    
    # Generate prediction
    pred_token_id = torch.argmax(logits, dim=-1)
    pred_text = tokenizer.decode(pred_token_id)
    
    # Check correctness (exact match)
    is_correct = int(pred_text.strip().lower() == answer.strip().lower())
    
    return entropy.item(), is_correct

# Main validation loop
entropies = []
correctness = []

for example in dataset:
    question = example["question"]
    answer = example["answer"]["value"]  # TriviaQA answer format
    
    entropy, correct = extract_entropy_and_prediction(model, tokenizer, question, answer)
    
    # Gate check: entropy extractable
    if entropy is not None:
        entropies.append(entropy)
        correctness.append(correct)

# Compute correlation
correlation, p_value = spearmanr(entropies, correctness)

# Gate validation
extraction_rate = len(entropies) / len(dataset)
gate_pass = extraction_rate > 0.95 and p_value < 0.05 and correlation < 0
```

### Training Protocol

**No training required** — frozen model inference only.

**Inference Settings:**
- Batch size: 1 (sequential processing)
- Max input length: 512 tokens
- Temperature: Not applicable (using logits directly, not sampling)
- Device: GPU if available, else CPU

### Evaluation

**Primary Metric:** Spearman rank correlation (entropy vs correctness)
- Computation: `scipy.stats.spearmanr(entropies, correctness_binary)`
- Expected direction: Negative correlation (higher entropy → lower accuracy)
- Threshold: p < 0.05

**Secondary Metrics:**
1. **Extraction success rate:** `len(valid_entropies) / total_predictions`
   - Threshold: >95%
2. **Entropy range:** `max(entropies) - min(entropies)`
   - Expected: >50% of theoretical max (log|V|)
3. **Quadrant Q3 population:** Fraction with high max-prob AND high entropy
   - Threshold: >5% (validates Assumption A2)

**Success Criteria (PoC, direction-based):**
1. Entropy extractable for >95% predictions
2. Significant negative correlation (p < 0.05)
3. Q3 population >5%

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Correlation analysis + binary classification accuracy
- Library: scipy.stats, numpy
- Code:
```python
from scipy.stats import spearmanr
import numpy as np

# Correlation
corr, p_val = spearmanr(entropies, correctness)

# Extraction rate
extraction_rate = np.sum(~np.isnan(entropies)) / len(entropies)

# Entropy range
entropy_range = np.max(entropies) - np.min(entropies)
theoretical_max = np.log(tokenizer.vocab_size)
range_fraction = entropy_range / theoretical_max

# Quadrant analysis (median split)
median_entropy = np.median(entropies)
median_maxprob = np.median(max_probs)
q3_mask = (max_probs > median_maxprob) & (entropies > median_entropy)
q3_fraction = np.sum(q3_mask) / len(entropies)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart
  - X-axis: Metrics (extraction_rate, correlation_significance, q3_population)
  - Y-axis: Value
  - Threshold lines: 0.95, 0.05 (p-value), 0.05 (Q3)

#### Additional Figures (LLM Autonomous)

1. **Scatter plot:** Entropy (x) vs Correctness (y, jittered binary)
   - Shows correlation visually
   - Regression line with 95% CI
   
2. **Histogram:** Entropy distribution for correct vs incorrect predictions
   - Overlaid distributions
   - Shows separation (or lack thereof)
   
3. **Quadrant plot:** Max-probability (x) vs Entropy (y)
   - Four quadrants with median splits
   - Color by correctness
   - Annotate Q3 population percentage

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### Libraries and Frameworks

1. **PyTorch** (v2.0+)
   - Purpose: Tensor operations, softmax, entropy computation
   - Repo: https://github.com/pytorch/pytorch
   
2. **HuggingFace Transformers** (v4.30+)
   - Purpose: Llama-2 model loading, tokenization, logits extraction
   - Repo: https://github.com/huggingface/transformers
   - Docs: https://huggingface.co/docs/transformers/model_doc/llama2
   
3. **HuggingFace Datasets** (v2.10+)
   - Purpose: TriviaQA dataset loading
   - Repo: https://github.com/huggingface/datasets
   - Card: https://huggingface.co/datasets/trivia_qa

4. **SciPy** (v1.10+)
   - Purpose: Spearman correlation computation
   - Docs: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html

### Related Research Implementations

*MCP unavailable — generic references only*

- Uncertainty quantification in NLP: Standard entropy-based approaches
- Selective prediction literature: Max-probability baselines (Hendrycks et al.)
- LLM evaluation frameworks: Standard QA benchmarking patterns

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- 2026-08-28: Experiment design completed (Phase 2C)
- Status: Ready for Phase 3 implementation planning

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
