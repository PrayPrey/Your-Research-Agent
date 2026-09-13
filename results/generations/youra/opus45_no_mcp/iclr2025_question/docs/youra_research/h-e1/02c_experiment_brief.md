# Experiment Design: H-E1

**Date:** 2026-08-19
**Author:** PrayPrey
**Hypothesis Statement:** Under QA task conditions with Llama-2-7B-chat, if we generate multiple responses per question and access token logits, then token entropy and semantic consistency can be computed for every response.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (root hypothesis)
**Gate Status:** MUST_WORK - not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
**MUST_WORK Gate:** If H-E1 fails → STOP, cannot proceed without metrics. This is foundational for all subsequent hypotheses (H-M1 through H-M4).

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - H-E1 is the root hypothesis with no dependencies.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Token Entropy Computation:**
- Standard approach: compute softmax over logits, then Shannon entropy
- Formula: H(p) = -Σ p_i log(p_i) where p = softmax(logits)
- Aggregation: mean entropy across generated tokens (excluding prompt)
- Established pattern in uncertainty quantification literature (Malinin & Gales 2018, Kuhn et al. 2023)

**Semantic Consistency Measurement:**
- Multi-sample generation with temperature > 0 for diversity
- Compute pairwise embedding similarity across N responses
- Use sentence embeddings (all-MiniLM-L6-v2 or similar)
- Consistency score = mean of pairwise cosine similarities
- Established in SelfCheckGPT (Manakul et al. 2023)

### Archon Code Examples

**Entropy computation pattern:**
```python
import torch
import torch.nn.functional as F

def compute_token_entropy(logits: torch.Tensor) -> float:
    """Compute mean entropy across tokens from logits."""
    probs = F.softmax(logits, dim=-1)
    log_probs = F.log_softmax(logits, dim=-1)
    entropy = -torch.sum(probs * log_probs, dim=-1)
    return entropy.mean().item()
```

**Consistency computation pattern:**
```python
from sentence_transformers import SentenceTransformer
import numpy as np
from itertools import combinations

def compute_semantic_consistency(responses: list[str], model) -> float:
    """Compute mean pairwise cosine similarity."""
    embeddings = model.encode(responses)
    similarities = []
    for i, j in combinations(range(len(responses)), 2):
        sim = np.dot(embeddings[i], embeddings[j]) / (
            np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
        )
        similarities.append(sim)
    return np.mean(similarities) if similarities else 1.0
```

### Exa GitHub Implementations

**Reference Repositories:**
1. **semantic-uncertainty** (Kuhn et al. 2023)
   - URL: https://github.com/jlko/semantic-uncertainty
   - Relevance: Semantic entropy computation for LLMs
   - Key files: `semantic_uncertainty/uncertainty.py`

2. **selfcheckgpt** (Manakul et al. 2023)
   - URL: https://github.com/potsawee/selfcheckgpt
   - Relevance: Multi-sample consistency checking
   - Key files: `selfcheckgpt/modeling_selfcheck.py`

3. **transformers** (HuggingFace)
   - Logit access via `model.generate(output_scores=True, return_dict_in_generate=True)`
   - Well-documented API for Llama-2 models

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is an EXISTENCE hypothesis - we are verifying that signals CAN be computed, not reproducing prior work. Use established libraries directly.

**Recommended Implementation Path:**
- Primary: HuggingFace Transformers + SentenceTransformers
- Fallback: Manual implementation following semantic-uncertainty patterns
- Justification: Standard libraries provide reliable, tested implementations. No need to reproduce paper code for existence verification.

### Code Analysis (Serena MCP)

*Serena MCP not available in this session. Using established patterns from knowledge base.*

Key implementation considerations:
- Llama-2-7B-chat requires ~14GB GPU memory (FP16)
- Use `torch.cuda.amp` for memory efficiency
- Batch generation recommended for 11K questions
- Store logits in memory-mapped files for large-scale processing

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | TriviaQA |
| **Version** | rc.nocontext |
| **Source** | HuggingFace: mandarjoshi/trivia_qa |
| **Type** | standard |
| **Split** | validation (~11,313 questions) |
| **Preprocessing** | Extract question text only (no context) |
| **Augmentation** | None |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: mandarjoshi/trivia_qa
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split="validation")
questions = [item["question"] for item in dataset]
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| **Name** | Llama-2-7B-chat |
| **Source** | HuggingFace: meta-llama/Llama-2-7b-chat-hf |
| **Type** | Instruction-tuned LLM |
| **Parameters** | 7B |
| **Precision** | FP16 |
| **Memory** | ~14GB VRAM |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: meta-llama/Llama-2-7b-chat-hf
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
```

#### Proposed Model

**Architecture:** Baseline + Entropy/Consistency computation pipeline

**Core Mechanism Implementation:**

```python
def compute_entropy_consistency(
    model,
    tokenizer,
    question: str,
    embedding_model,
    n_samples: int = 10,
    temperature: float = 0.7,
    max_new_tokens: int = 128
) -> dict:
    """
    Compute both entropy and consistency for a single question.
    
    Returns:
        dict with keys: 'entropy', 'consistency', 'responses', 'success'
    """
    # Format prompt for Llama-2-chat
    prompt = f"[INST] {question} [/INST]"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Generate N responses with logits
    responses = []
    entropies = []
    
    for _ in range(n_samples):
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            output_scores=True,
            return_dict_in_generate=True
        )
        
        # Decode response
        response_ids = outputs.sequences[0][inputs.input_ids.shape[1]:]
        response_text = tokenizer.decode(response_ids, skip_special_tokens=True)
        responses.append(response_text)
        
        # Compute entropy from scores (logits)
        if outputs.scores:
            token_entropies = []
            for score in outputs.scores:
                probs = torch.softmax(score[0], dim=-1)
                log_probs = torch.log_softmax(score[0], dim=-1)
                h = -torch.sum(probs * log_probs).item()
                token_entropies.append(h)
            entropies.append(np.mean(token_entropies))
    
    # Compute mean entropy across samples
    mean_entropy = np.mean(entropies) if entropies else float('nan')
    
    # Compute semantic consistency
    if len(responses) >= 2:
        embeddings = embedding_model.encode(responses)
        sims = []
        for i in range(len(responses)):
            for j in range(i+1, len(responses)):
                sim = np.dot(embeddings[i], embeddings[j]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
                )
                sims.append(sim)
        consistency = np.mean(sims)
    else:
        consistency = float('nan')
    
    success = not (np.isnan(mean_entropy) or np.isnan(consistency))
    
    return {
        'entropy': mean_entropy,
        'consistency': consistency,
        'responses': responses,
        'success': success
    }
```

### Training Protocol

**No training required for H-E1.** This is an existence verification:
- Load pre-trained model (no fine-tuning)
- Run inference only
- Compute metrics from outputs

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Training | None | Existence test only |
| Inference | Full validation set (~11K) | Statistical significance |
| Samples per question | 10 | Standard for consistency metrics |
| Temperature | 0.7 | Balance diversity/quality |
| Max tokens | 128 | Sufficient for QA responses |

### Evaluation

**Task Type:** Metric Computation Verification (Existence Test)

**Primary Metric:** Success Rate
- Definition: Percentage of questions where both entropy and consistency computed without error
- Target: >99%
- Formula: `success_rate = sum(results['success']) / len(results) * 100`

**Secondary Metrics:**
1. **Entropy Variance:** `np.var([r['entropy'] for r in results if r['success']])`
   - Target: >0 (non-constant values)
2. **Consistency Variance:** `np.var([r['consistency'] for r in results if r['success']])`
   - Target: >0 (non-constant values)
3. **Entropy Range:** `[min(entropies), max(entropies)]`
   - Expected: Meaningful spread across questions
4. **Consistency Range:** `[min(consistencies), max(consistencies)]`
   - Expected: Meaningful spread across questions

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: metric_computation
- Library: numpy, scipy.stats
- Code:
```python
import numpy as np
from scipy import stats

def evaluate_existence(results: list[dict]) -> dict:
    successful = [r for r in results if r['success']]
    success_rate = len(successful) / len(results) * 100
    
    entropies = [r['entropy'] for r in successful]
    consistencies = [r['consistency'] for r in successful]
    
    return {
        'success_rate': success_rate,
        'n_successful': len(successful),
        'n_total': len(results),
        'entropy_mean': np.mean(entropies),
        'entropy_std': np.std(entropies),
        'entropy_range': [np.min(entropies), np.max(entropies)],
        'consistency_mean': np.mean(consistencies),
        'consistency_std': np.std(consistencies),
        'consistency_range': [np.min(consistencies), np.max(consistencies)],
        'pass': success_rate > 99.0
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Success rate bar chart (target 99% vs actual)

#### Additional Figures (LLM Autonomous)

1. **Entropy Distribution Histogram**
   - X: Entropy value, Y: Frequency
   - Purpose: Verify meaningful spread

2. **Consistency Distribution Histogram**
   - X: Consistency value, Y: Frequency
   - Purpose: Verify meaningful spread

3. **Entropy vs Consistency Scatter Plot**
   - X: Entropy, Y: Consistency
   - Purpose: Initial correlation check (preview for H-M3)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Success rate > 99% (both metrics computed for >99% of questions)
3. Non-zero variance in both metrics

**Gate Decision:**
- PASS → Proceed to H-M1 (entropy correlation with uncertainty)
- FAIL → STOP workflow, cannot compute required signals

---

## Appendix: Reference Implementations

### A. Semantic Uncertainty (Kuhn et al. 2023)
- **Repository:** https://github.com/jlko/semantic-uncertainty
- **Paper:** "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation"
- **Relevance:** Entropy computation from LLM outputs
- **Key insight:** Semantic clustering before entropy computation

### B. SelfCheckGPT (Manakul et al. 2023)
- **Repository:** https://github.com/potsawee/selfcheckgpt
- **Paper:** "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models"
- **Relevance:** Multi-sample consistency checking
- **Key insight:** Compare samples via BERTScore, NLI, or embeddings

### C. HuggingFace Transformers
- **Documentation:** https://huggingface.co/docs/transformers/
- **Model:** meta-llama/Llama-2-7b-chat-hf
- **Key API:** `model.generate(output_scores=True, return_dict_in_generate=True)`

### D. SentenceTransformers
- **Documentation:** https://www.sbert.net/
- **Model:** all-MiniLM-L6-v2 (fast) or all-mpnet-base-v2 (quality)
- **Key API:** `model.encode(sentences)`

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: H-E1 set to IN_PROGRESS
- 2026-08-19: Phase 2C experiment design initiated
- 2026-08-19: Experiment brief generated (02c_experiment_brief.md)

---

*MCP Tools Used: None (batch mode - used knowledge base patterns)*
*All specifications grounded in established implementations*
*Next Phase: Phase 3 - Implementation Planning*
