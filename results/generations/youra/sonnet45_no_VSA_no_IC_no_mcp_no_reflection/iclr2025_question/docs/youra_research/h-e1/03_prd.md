# Product Requirements Document (PRD)
## Hypothesis h-e1: Token Entropy Correlation with Prediction Correctness

**Version:** 1.0  
**Date:** 2026-08-28  
**Author:** Anonymous  
**Status:** Draft

---

## Executive Summary

### Purpose
Validate whether entropy extracted from token probability distributions in frozen LLM forward passes correlates negatively with prediction correctness on factual question-answering tasks.

### Scope
Proof-of-concept (PoC) implementation to test infrastructure viability for entropy-based uncertainty quantification in frozen language models.

### Success Criteria
1. Entropy extraction succeeds for >95% of predictions
2. Statistically significant negative correlation (Spearman ρ, p < 0.05) between entropy and correctness
3. High max-prob + high entropy quadrant (Q3) population >5%

---

## Problem Statement

### Background
Uncertainty quantification in frozen LLMs requires accessible signals from single forward passes. Token probability distributions encode uncertainty through their shape, potentially measurable via entropy.

### Hypothesis
Under factual QA with frozen LLMs, if we extract token probability distributions from single forward passes, then entropy signals are measurable and correlate with prediction correctness, because output distributions encode uncertainty through their shape.

### Gate Condition
**Type:** MUST_WORK  
**Pass:** Entropy extractable >95%, significant negative correlation (p < 0.05)  
**Fail:** ABANDON entire research (infrastructure broken)

---

## Functional Requirements

### FR-1: Dataset Acquisition
**Priority:** P0  
**Description:** Load TriviaQA unfiltered dev split subset for evaluation.

**Acceptance Criteria:**
- TriviaQA unfiltered dataset loaded from HuggingFace
- First 1,000 examples from validation split extracted
- Question-answer pairs accessible in standard format
- No preprocessing applied (raw text)

**Dependencies:** HuggingFace datasets library

**Technical Details:**
```python
from datasets import load_dataset
dataset = load_dataset("trivia_qa", "unfiltered", split="validation[:1000]")
```

---

### FR-2: Model Loading
**Priority:** P0  
**Description:** Load frozen Llama-2-7B model with logits access.

**Acceptance Criteria:**
- Llama-2-7B-hf model loaded from HuggingFace transformers
- Model frozen (no gradient computation)
- Logits extractable from forward passes
- Tokenizer loaded with matching vocabulary

**Dependencies:** HuggingFace transformers, PyTorch

**Technical Details:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
model.eval()  # Frozen mode
```

---

### FR-3: Entropy Extraction
**Priority:** P0  
**Description:** Extract Shannon entropy from next-token probability distributions.

**Acceptance Criteria:**
- Logits extracted from last token position
- Softmax computed to obtain probability distribution
- Shannon entropy calculated: H(p) = -Σ p(x) log p(x)
- Numerical stability ensured (epsilon for log)
- Valid entropy value returned for each prediction

**Dependencies:** PyTorch functional

**Technical Details:**
```python
import torch.nn.functional as F

# Extract logits from forward pass
logits = model(**inputs).logits[:, -1, :]  # Next token logits

# Compute probability distribution
probs = F.softmax(logits, dim=-1)

# Shannon entropy with numerical stability
entropy = -torch.sum(probs * torch.log(probs + 1e-10), dim=-1)
```

---

### FR-4: Prediction Generation and Correctness Evaluation
**Priority:** P0  
**Description:** Generate predictions and evaluate correctness via exact match.

**Acceptance Criteria:**
- Prediction generated from argmax of logits
- Token ID decoded to text
- Exact match comparison with ground truth answer (case-insensitive)
- Binary correctness label stored

**Dependencies:** Tokenizer

**Technical Details:**
```python
# Generate prediction
pred_token_id = torch.argmax(logits, dim=-1)
pred_text = tokenizer.decode(pred_token_id)

# Check correctness
is_correct = int(pred_text.strip().lower() == answer.strip().lower())
```

---

### FR-5: Correlation Analysis
**Priority:** P0  
**Description:** Compute Spearman rank correlation between entropy and correctness.

**Acceptance Criteria:**
- Entropy values collected across all predictions
- Correctness labels (binary) collected
- Spearman rank correlation coefficient computed
- p-value computed for significance test
- Results stored with correlation coefficient and p-value

**Dependencies:** SciPy

**Technical Details:**
```python
from scipy.stats import spearmanr

correlation, p_value = spearmanr(entropies, correctness)
```

---

### FR-6: Extraction Rate Metric
**Priority:** P0  
**Description:** Measure fraction of predictions with valid entropy extraction.

**Acceptance Criteria:**
- Count of valid entropy values tracked
- Total predictions tracked
- Extraction rate computed as valid/total
- Rate compared against 95% threshold

---

### FR-7: Quadrant Analysis (Q3 Population)
**Priority:** P1  
**Description:** Identify high max-probability + high entropy population.

**Acceptance Criteria:**
- Max probability extracted for each prediction
- Median splits computed for max-prob and entropy
- Q3 (high max-prob, high entropy) population identified
- Q3 fraction computed and compared against 5% threshold

**Technical Details:**
```python
import numpy as np

# Extract max probabilities
max_probs = torch.max(probs, dim=-1).values

# Median splits
median_entropy = np.median(entropies)
median_maxprob = np.median(max_probs)

# Q3 population
q3_mask = (max_probs > median_maxprob) & (entropies > median_entropy)
q3_fraction = np.sum(q3_mask) / len(entropies)
```

---

### FR-8: Visualization Generation
**Priority:** P1  
**Description:** Generate figures for validation report.

**Acceptance Criteria:**
- **Figure 1 (Mandatory):** Gate metrics comparison bar chart
  - Metrics: extraction_rate, correlation_significance, q3_population
  - Threshold lines at target values (0.95, 0.05, 0.05)
- **Figure 2:** Scatter plot of entropy vs correctness (jittered binary)
  - Regression line with 95% confidence interval
- **Figure 3:** Histogram of entropy distributions (correct vs incorrect)
  - Overlaid distributions
- **Figure 4:** Quadrant plot (max-prob vs entropy)
  - Four quadrants with median splits
  - Color-coded by correctness
  - Q3 population annotated

**Dependencies:** matplotlib or seaborn

**Output:** Figures saved to `{hypothesis_folder}/figures/`

---

### FR-9: Validation Report Generation
**Priority:** P0  
**Description:** Generate 04_validation.md report with results.

**Acceptance Criteria:**
- Gate pass/fail status documented
- All three success criteria results reported
- Figures embedded or referenced
- Conclusion on infrastructure viability

---

## Non-Functional Requirements

### NFR-1: Performance
- Single forward pass per prediction (no multi-pass uncertainty)
- Sequential processing acceptable for PoC (batch_size=1)
- GPU utilization if available, CPU fallback

### NFR-2: Reproducibility
- Fixed random seed for deterministic results
- Exact dataset split specification (validation[:1000])
- Library versions documented

### NFR-3: Resource Constraints
- Model cache: ~13GB for Llama-2-7B
- Dataset cache: ~600MB for TriviaQA
- GPU memory: ~15GB for inference (if available)
- Disk space: <20GB total

### NFR-4: Error Handling
- Handle tokenization failures gracefully
- Skip examples with invalid entropy (NaN/Inf)
- Report skipped examples count

---

## Data Specifications

### Input Data
**Dataset:** TriviaQA unfiltered  
**Source:** HuggingFace datasets  
**Split:** validation[:1000]  
**Format:** JSON-like with "question" and "answer" fields  
**Size:** ~1,000 examples

**Fields:**
- `question`: str (factual question)
- `answer`: dict with "value" key (correct answer text)

**Cache Location:** `~/.cache/huggingface/datasets`

---

### Model Artifacts
**Model:** Llama-2-7B-hf  
**Source:** HuggingFace transformers  
**Parameters:** 7 billion  
**Format:** PyTorch checkpoint  
**Size:** ~13GB

**Cache Location:** `~/.cache/huggingface/hub`

---

### Output Data
**Validation Report:** `04_validation.md`  
**Figures:** `figures/*.png` (4 plots)  
**Intermediate Results:** Optional pickle/json with raw predictions

---

## Dependencies

### Required Libraries
- `torch >= 2.0`
- `transformers >= 4.30`
- `datasets >= 2.10`
- `scipy >= 1.10`
- `numpy >= 1.24`
- `matplotlib >= 3.7` or `seaborn >= 0.12`

### System Requirements
- Python 3.8+
- CUDA 11.8+ (optional, for GPU)
- 20GB free disk space
- 16GB RAM (32GB recommended for GPU inference)

---

## Implementation Phases

### Phase 4: Coding & Validation
1. **Environment Setup**
   - Install dependencies
   - Verify GPU availability
   - Download dataset and model

2. **Core Implementation**
   - Implement entropy extraction pipeline
   - Implement correctness evaluation
   - Implement correlation analysis

3. **Metric Computation**
   - Extraction rate
   - Spearman correlation
   - Quadrant analysis

4. **Visualization**
   - Generate all 4 figures
   - Save to figures folder

5. **Validation Report**
   - Document results in 04_validation.md
   - Include gate pass/fail decision

---

## Success Criteria (Detailed)

### Gate Validation
1. **Extraction Rate:** >95%
   - Measure: `valid_count / total_count`
   - Pass threshold: 0.95

2. **Correlation Significance:** p < 0.05
   - Measure: Spearman p-value
   - Pass threshold: <0.05
   - Expected direction: Negative correlation (ρ < 0)

3. **Quadrant Q3 Population:** >5%
   - Measure: `q3_count / total_count`
   - Pass threshold: 0.05

### Overall Gate
**PASS:** All three criteria met  
**FAIL:** Any criterion not met → ABANDON research

---

## Risks and Mitigations

### Risk 1: Model Download Failure
**Likelihood:** Low  
**Impact:** High  
**Mitigation:** Fallback to smaller model (e.g., GPT-2) for infrastructure validation

### Risk 2: Insufficient GPU Memory
**Likelihood:** Medium  
**Impact:** Medium  
**Mitigation:** CPU inference fallback, sequential processing

### Risk 3: No Correlation Found
**Likelihood:** Medium (research uncertainty)  
**Impact:** High (gate failure)  
**Mitigation:** None (expected outcome for MUST_WORK gate)

---

## Appendix

### Reference Code Structure
```
entropy_experiment/
├── data/
│   └── triviaqa_subset.py       # Dataset loading
├── models/
│   └── llama_inference.py       # Model wrapper
├── metrics/
│   ├── entropy.py               # Entropy computation
│   ├── correlation.py           # Spearman analysis
│   └── quadrant.py              # Q3 analysis
├── visualization/
│   └── plots.py                 # Figure generation
├── main.py                      # Main experiment loop
└── requirements.txt             # Dependencies
```

### Testing Strategy
- Unit tests: Entropy computation on toy distributions
- Integration tests: End-to-end pipeline on 10 examples
- Validation: Full 1,000 examples

---

**Document Status:** Ready for Phase 3 Architecture Design
