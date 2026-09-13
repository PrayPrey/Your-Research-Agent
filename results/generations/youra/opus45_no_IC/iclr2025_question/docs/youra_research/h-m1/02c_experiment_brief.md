# Experiment Design: H-M1

**Date:** 2026-08-10
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** LLM uncertainty signals (semantic entropy) correlate with error-generation processes
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Hypothesis** - Validates that semantic entropy captures meaningful uncertainty linked to model errors.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 PASSED: silhouette=0.8245)
**Gate Status:** MUST_WORK (p < 0.05, Cohen's d > 0.3)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASS)

### Gate Condition
**Pass Criteria:**
1. Entropy significantly higher for incorrect responses (p < 0.05, Mann-Whitney U test)
2. Effect size Cohen's d > 0.3 (medium effect)

**Fail Action:** PIVOT to alternative uncertainty signal

---

## Continuation Context

H-E1 established that benchmarks cluster meaningfully (silhouette=0.8245, k=2):
- **Cluster 1 (Factual Recall):** TriviaQA, NQ, SQuAD
- **Cluster 2 (Entity/Claim):** PopQA, HaluEval-QA, FEVER

H-M1 validates the mechanism: semantic entropy should separate correct from incorrect responses, demonstrating that uncertainty reflects error-generation processes.

### Previous Hypothesis Results
| Hypothesis | Result | Key Metric |
|------------|--------|------------|
| H-E1 | PASS | Silhouette = 0.8245 > 0.5 |

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for semantic entropy in KB. Primary resources from academic literature.

### Archon Code Examples

No direct semantic entropy code examples in KB. Relying on official implementation.

### Exa GitHub Implementations

**Primary Implementation Found:**
- **Repository:** `github.com/jlko/semantic_uncertainty`
- **Paper:** Farquhar et al., Nature 2024 - "Detecting Hallucinations in Large Language Models Using Semantic Entropy"
- **Status:** Official, actively maintained, Python 3.11 + PyTorch 2.1

**Key Components:**
1. `generate_answers.py` - Sample N responses per query with logprobs
2. `compute_uncertainty_measures.py` - Compute semantic entropy via bidirectional entailment
3. `analyze_results.py` - Aggregate metrics

**Alternative Implementations:**
- `cvs-health/uqlm` - UQLM package with `SemanticEntropy` class
- `semantic-entropy-gate` - PyPI package (v0.8.0) for production use

### Implementation Priority Assessment

**CRITICAL: Use official Kuhn/Farquhar implementation for reproducibility**

| Priority | Source | Justification |
|----------|--------|---------------|
| 1 (Primary) | jlko/semantic_uncertainty | Official Nature 2024 paper code, exact methodology |
| 2 (Fallback) | cvs-health/uqlm | Clean API, HuggingFace integration |
| 3 (Reference) | semantic-entropy-gate | Production-ready, simplified interface |

**Recommended Implementation Path:**
- Primary: Adapt `jlko/semantic_uncertainty` pipeline
- Fallback: Use `uqlm.SemanticEntropy` if integration issues
- Justification: Official implementation ensures methodological fidelity to Kuhn 2023 / Farquhar 2024

### Code Analysis (Serena MCP)

*Not applicable - no existing codebase to analyze. Fresh implementation from reference.*

---

## Experiment Specification

### Dataset

**Dataset:** TriviaQA (from H-E1 Cluster 1 - Factual Recall)

| Attribute | Value |
|-----------|-------|
| **Name** | TriviaQA |
| **Version** | rc (reading comprehension subset) |
| **Source** | HuggingFace datasets |
| **Type** | standard |
| **Train Split** | Not used (inference only) |
| **Validation Split** | 11,313 samples |
| **Test Split** | Use validation (test hidden) |
| **Evaluation Samples** | 1,000 (random sample from validation) |

**Preprocessing:**
- Extract question and answer fields
- Normalize answers (lowercase, strip punctuation)
- Filter for single-answer questions

**Justification:** TriviaQA is in Cluster 1 (factual recall), has ground truth labels, and is used in Kuhn 2023/Farquhar 2024 as primary benchmark.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `trivia_qa` (subset: `rc`)
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("trivia_qa", "rc", split="validation")
dataset = dataset.shuffle(seed=42).select(range(1000))
```

### Models

#### Baseline Model

**Model:** Llama-2-7B-Chat

| Attribute | Value |
|-----------|-------|
| **Architecture** | LlamaForCausalLM |
| **Parameters** | 7B |
| **Source** | HuggingFace (meta-llama/Llama-2-7b-chat-hf) |
| **Quantization** | None (full precision for logprobs) |
| **Context Length** | 4096 tokens |

**Justification:** Same model used in Farquhar 2024; open-weight with accessible logprobs required for semantic entropy.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-chat-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
```

#### Proposed Model

**Architecture:** Baseline + Semantic Entropy Computation

This is not a model comparison experiment. H-M1 tests whether semantic entropy (computed from Llama-2-7B responses) separates correct from incorrect answers.

**Core Mechanism Implementation:**

```python
# Semantic Entropy Computation for H-M1
# Reference: Farquhar et al., Nature 2024

import numpy as np
from scipy.stats import entropy, mannwhitneyu
from transformers import pipeline

def compute_semantic_entropy(responses, logprobs, nli_model):
    """
    Compute semantic entropy over meaning clusters.
    
    Args:
        responses: List[str] - N sampled responses
        logprobs: List[float] - Log probabilities per response
        nli_model: NLI classifier for entailment detection
    
    Returns:
        float - Semantic entropy in nats
    """
    # Step 1: Cluster responses by bidirectional entailment
    clusters = cluster_by_entailment(responses, nli_model)
    
    # Step 2: Aggregate probabilities per cluster
    cluster_probs = []
    for cluster in clusters:
        cluster_prob = sum(np.exp(logprobs[i]) for i in cluster)
        cluster_probs.append(cluster_prob)
    
    # Step 3: Normalize and compute entropy
    cluster_probs = np.array(cluster_probs)
    cluster_probs = cluster_probs / cluster_probs.sum()
    semantic_entropy = entropy(cluster_probs)  # nats
    
    return semantic_entropy

def cluster_by_entailment(responses, nli_model):
    """
    Greedy clustering via bidirectional entailment.
    A and B in same cluster iff A entails B AND B entails A.
    """
    clusters = []
    for i, resp in enumerate(responses):
        assigned = False
        for cluster in clusters:
            representative = responses[cluster[0]]
            # Bidirectional entailment check
            ab = nli_model(f"{resp} [SEP] {representative}")
            ba = nli_model(f"{representative} [SEP] {resp}")
            if ab == "entailment" and ba == "entailment":
                cluster.append(i)
                assigned = True
                break
        if not assigned:
            clusters.append([i])
    return clusters

def evaluate_entropy_separation(entropy_correct, entropy_incorrect):
    """
    H-M1 Gate Evaluation: Test entropy separation.
    
    Returns:
        dict with p_value, cohens_d, gate_passed
    """
    # Mann-Whitney U test (non-parametric)
    statistic, p_value = mannwhitneyu(
        entropy_incorrect, entropy_correct,
        alternative='greater'  # incorrect should have higher entropy
    )
    
    # Cohen's d effect size
    pooled_std = np.sqrt(
        (np.var(entropy_correct) + np.var(entropy_incorrect)) / 2
    )
    cohens_d = (np.mean(entropy_incorrect) - np.mean(entropy_correct)) / pooled_std
    
    # Gate check
    gate_passed = (p_value < 0.05) and (cohens_d > 0.3)
    
    return {
        "p_value": p_value,
        "cohens_d": cohens_d,
        "mean_entropy_correct": np.mean(entropy_correct),
        "mean_entropy_incorrect": np.mean(entropy_incorrect),
        "gate_passed": gate_passed
    }
```

### Training Protocol

**No training required.** H-M1 is an inference-only experiment.

| Parameter | Value |
|-----------|-------|
| **Sampling Temperature** | 0.7 (per Kuhn 2023) |
| **Generations per Query** | N = 10 |
| **Max New Tokens** | 50 (short-phrase generation) |
| **NLI Model** | DeBERTa-v3-large (MNLI fine-tuned) |
| **Entailment Threshold** | 0.5 (softmax probability) |

### Evaluation

**Primary Metrics:**

| Metric | Description | Success Threshold |
|--------|-------------|-------------------|
| **p-value** | Mann-Whitney U test (incorrect > correct entropy) | < 0.05 |
| **Cohen's d** | Effect size for entropy separation | > 0.3 |

**Secondary Metrics:**

| Metric | Description |
|--------|-------------|
| Mean Entropy (Correct) | Average semantic entropy for correct responses |
| Mean Entropy (Incorrect) | Average semantic entropy for incorrect responses |
| AUROC | Area under ROC for entropy as correctness predictor |

**Correctness Labeling:**
- Response is "correct" if normalized answer matches any ground truth alias (exact match or F1 > 0.5)
- Response is "incorrect" otherwise

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (correct/incorrect prediction via entropy)
- Library: scipy.stats, sklearn.metrics
- Code:
```python
from scipy.stats import mannwhitneyu
from sklearn.metrics import roc_auc_score
import numpy as np

def compute_cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (np.mean(group2) - np.mean(group1)) / pooled_std

# Evaluation
_, p_value = mannwhitneyu(entropy_incorrect, entropy_correct, alternative='greater')
cohens_d = compute_cohens_d(entropy_correct, entropy_incorrect)
auroc = roc_auc_score(labels, entropies)  # 1=incorrect, higher entropy
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing mean entropy for correct vs incorrect responses with error bars, p-value annotation, and Cohen's d

#### Additional Figures (LLM Autonomous)

1. **Entropy Distribution Violin Plot**: Side-by-side violin plots of entropy distributions for correct/incorrect
2. **ROC Curve**: Entropy as predictor of incorrectness
3. **Entropy vs. Accuracy Scatter**: Per-question entropy vs. model accuracy

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. p-value < 0.05 (entropy significantly higher for incorrect responses)
3. Cohen's d > 0.3 (medium effect size)

**Expected Outcome (based on Farquhar 2024):**
- Semantic entropy achieves ~0.79-0.85 AUROC for hallucination detection
- Clear separation between correct/incorrect entropy distributions

---

## Appendix: Reference Implementations

### Primary Reference
```
Repository: github.com/jlko/semantic_uncertainty
Paper: Farquhar et al. (2024). Detecting hallucinations in large language models 
       using semantic entropy. Nature, 630, 625-630.
License: MIT
Key Files:
  - semantic_uncertainty/generate_answers.py
  - semantic_uncertainty/compute_uncertainty_measures.py
  - semantic_uncertainty/analyze_results.py
```

### Secondary References
```
1. cvs-health/uqlm (PyPI: uqlm)
   - SemanticEntropy class with generate_and_score() method
   - Clean LangChain integration

2. semantic-entropy-gate (PyPI)
   - Production-ready Gate class
   - CrossEncoderEntailment backend

3. Original deprecated repo: lorenzkuhn/semantic_uncertainty
   - ICLR 2023 version, replaced by jlko/semantic_uncertainty
```

### Key Implementation Details from Farquhar 2024

1. **Entailment Model:** DeBERTa-large fine-tuned on MNLI
2. **Bidirectional Check:** A ⊨ B AND B ⊨ A required for same cluster
3. **Context Prepending:** Question prepended to both sides for NLI
4. **Entropy Estimator:** White-box (Rao-Blackwellised) when logprobs available, discrete otherwise
5. **Normalization:** Length-normalized mean token log-probability per generation

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10T23:00:00Z

### Workflow History for This Hypothesis
| Event | Timestamp | Details |
|-------|-----------|---------|
| H-M1 set to IN_PROGRESS | 2026-08-10T21:50:19Z | External loop starting Phase 2C → 3 → 4 |
| Phase 2C experiment design | 2026-08-10T23:00:00Z | Generated 02c_experiment_brief.md |

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
