# Experiment Design: H-M1

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** Early attention entropy reflects task structure - entropy variance across tasks exceeds within-category variance
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests causal link between attention entropy and task structure.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 PASSED (k*=3 clusters detected)
**Gate Status:** MUST_WORK - F-test p<0.05 required

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASSED)

### Gate Condition
**Type:** MUST_WORK
**Condition:** F-test p<0.05 for entropy variance between-task vs within-category
**Fail Action:** PIVOT to alternative features (head sparsity, top-k concentration)

---

## Continuation Context

H-M1 builds on H-E1's finding that k*=3 task clusters exist in LongBench compression response profiles. This hypothesis tests whether early attention entropy (computed from first 100 tokens) can explain the observed clustering - providing a mechanism for task-conditioned routing.

### Previous Hypothesis Results (H-E1)
- **Status:** COMPLETED, PASSED
- **k*:** 3 clusters detected via gap statistic
- **Silhouette:** 0.411
- **Clusters Identified:**
  - Cluster 0: Multi-doc QA + Code (hotpotqa, 2wikimqa, musique, dureader, lcc, repobench-p)
  - Cluster 1: Single-doc QA + Few-shot (narrativeqa, qasper, multifieldqa_zh, trec, triviaqa, samsum, lsht)
  - Cluster 2: Summarization + Synthetic (multifieldqa_en, gov_report, qmsum, multi_news, vcsum, passage_retrieval_en, passage_count, passage_retrieval_zh)
- **Available Artifacts:** `h-e1/response_matrix.npy`, `h-e1/cluster_labels.json`

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Attention entropy task classification**
- Limited direct matches for attention entropy in LLM task classification
- T5 transformer documentation shows output_attentions parameter available
- Attention pattern analysis is established practice in transformer interpretability

**Query 2: Attention pattern analysis long context**
- arxiv:2405.07719 - Long context attention analysis methods
- Attend-and-Excite paper shows attention manipulation techniques
- Pattern: attention weights extractable via model forward hooks

**Key Insights:**
- Standard practice: compute Shannon entropy over attention distribution per head
- First-N tokens commonly used for probing (StreamingLLM sink tokens concept)
- F-test appropriate for comparing between-group vs within-group variance

### Archon Code Examples

- Memory-efficient attention patterns from diffusers library
- xformers FlashAttention shows attention weight access patterns
- AttnProcessor2_0 demonstrates attention hook mechanisms

### Exa GitHub Implementations

**Repository 1:** [lena-voita/the-story-of-heads](https://github.com/lena-voita/the-story-of-heads) (⭐324)
- **Relevance:** ACL 2019 paper on attention head analysis and pruning
- **Key Method:** Analyzes specialized heads, measures head importance
- **Pattern:** Extract attention weights, compute statistics per head

**Repository 2:** [heartcored98/transformer_anatomy](https://github.com/heartcored98/transformer_anatomy) (⭐16)
- **Relevance:** ACL 2020 - Roles and Utilization of Attention Heads
- **Key Method:** Classifies attention head types by behavior pattern
- **Topics:** attention-head, interpretability, transformer-encoder

**Repository 3:** [Nandan91/entropy-guided-attention-llm](https://github.com/Nandan91/entropy-guided-attention-llm) (⭐10)
- **Relevance:** AAAI 2025 - Entropy-Guided Attention for Private LLMs
- **Key Code:** EntropyRegularization class with entropy computation
- **Pattern:**
  ```python
  def entropy(p):
      plogp = p * torch.log(p)
      plogp[p == 0] = 0
      return -plogp.sum(dim=-1)
  ```

**Repository 4:** [pouyapez/pytorch-pretrained-BERT/examples/bertology.py](https://github.com/pouyapez/pytorch-pretrained-BERT)
- **Relevance:** BERTology analysis with entropy computation
- **Key Code:** Direct entropy function for attention analysis

**Serena Analysis Needed:** false (code patterns clear from Exa search)

### 🎯 Implementation Priority Assessment

**CRITICAL:** No paper author implementation exists for this specific hypothesis (novel mechanism test).

**Recommended Implementation Path:**
- Primary: Adapt entropy computation from bertology.py / entropy-guided-attention-llm
- Fallback: Custom implementation following established pattern
- Justification: Multiple sources show identical entropy computation pattern; adapt for Llama-2 attention extraction

### Code Analysis (Serena MCP)

Not required - clear implementation pattern from GitHub search. Standard entropy computation over attention softmax outputs.

---

## Experiment Specification

### Dataset

**Name:** LongBench
**Type:** standard
**Source:** https://github.com/THUDM/LongBench
**Statistics:**
- 21 tasks across 6 categories
- ~3500 total samples
- Categories: Single-Doc QA, Multi-Doc QA, Summarization, Few-shot, Synthetic, Code

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: THUDM/LongBench
- Code:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("THUDM/LongBench", task_name, split="test")
  ```

**Preprocessing:**
- Tokenize with Llama-2 tokenizer
- Truncate to model max length (4096 tokens)
- Extract first 100 tokens for attention probing

### Models

#### Baseline Model

**Architecture:** Llama-2-7B
**Type:** decoder-only transformer
**Source:** meta-llama/Llama-2-7b-hf

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: meta-llama/Llama-2-7b-hf
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-2-7b-hf",
      torch_dtype=torch.float16,
      device_map="auto",
      output_attentions=True
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
  ```

**Configuration:**
- Layers: 32
- Heads: 32 per layer
- Hidden dim: 4096
- Total attention matrices: 32 × 32 = 1024 heads

#### Proposed Model

**Architecture:** Baseline + Attention Entropy Extraction

**Core Mechanism Implementation:**

```python
# Core Mechanism: Attention Entropy Extraction
# Based on: bertology.py, entropy-guided-attention-llm

import torch
import numpy as np
from scipy import stats

def compute_attention_entropy(attention_weights):
    """
    Compute Shannon entropy for attention distribution.
    
    Args:
        attention_weights: (batch, heads, seq_len, seq_len)
    Returns:
        entropy: (batch, heads) - entropy per head
    """
    # Attention already softmaxed, sum over attended positions
    # Add small epsilon for numerical stability
    eps = 1e-10
    p = attention_weights + eps
    log_p = torch.log(p)
    entropy = -(p * log_p).sum(dim=-1).mean(dim=-1)  # Mean over query positions
    return entropy

def extract_task_entropy(model, tokenizer, samples, n_tokens=100):
    """
    Extract attention entropy for task samples.
    
    Args:
        model: Llama-2 with output_attentions=True
        samples: list of input texts
        n_tokens: number of tokens for probing window
    Returns:
        entropy_matrix: (n_samples, n_layers, n_heads)
    """
    all_entropies = []
    for text in samples:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=n_tokens)
        with torch.no_grad():
            outputs = model(**inputs.to(model.device))
        
        # outputs.attentions is tuple of (batch, heads, seq, seq) per layer
        sample_entropy = []
        for layer_attn in outputs.attentions:
            layer_entropy = compute_attention_entropy(layer_attn)
            sample_entropy.append(layer_entropy.cpu())
        
        all_entropies.append(torch.stack(sample_entropy, dim=1))  # (1, layers, heads)
    
    return torch.cat(all_entropies, dim=0)  # (n_samples, layers, heads)

def compute_variance_ratio(entropy_by_task, task_categories):
    """
    Compute between-category vs within-category variance ratio.
    
    Args:
        entropy_by_task: dict[task_name] -> (n_samples, layers, heads)
        task_categories: dict[task_name] -> category
    Returns:
        f_statistic, p_value
    """
    # Aggregate to task-level mean entropy
    task_means = {task: ent.mean(dim=0).mean().item() 
                  for task, ent in entropy_by_task.items()}
    
    # Group by category
    categories = set(task_categories.values())
    groups = [[task_means[t] for t in task_categories if task_categories[t] == c] 
              for c in categories]
    
    # F-test (one-way ANOVA)
    f_stat, p_value = stats.f_oneway(*groups)
    return f_stat, p_value
```

### Training Protocol

**No Training Required** - This is an analysis/measurement experiment, not a training experiment.

**Execution Protocol:**
1. Load Llama-2-7B with output_attentions=True
2. Forward pass on 5-10 samples per task (21 tasks × 5 = 105 samples minimum)
3. Extract attention weights from all 32 layers × 32 heads
4. Compute entropy per head per sample
5. Aggregate to task-level statistics
6. Run F-test comparing between-task vs within-category variance

**Computational Budget:**
- Forward passes: ~105-210 (5-10 samples × 21 tasks)
- GPU memory: ~14GB (Llama-2-7B in fp16)
- Time estimate: ~30 minutes on A100

**Seeds:** 1 (deterministic forward pass, no training)

### Evaluation

**Primary Metrics:**
- F-statistic: Between-task entropy variance / Within-category entropy variance
- p-value: Statistical significance of F-test

**Success Criteria:**
- **PASS:** F-test p-value < 0.05 (between-task variance significantly exceeds within-category variance)
- **FAIL:** F-test p-value >= 0.05 (no significant difference)

**Secondary Metrics:**
- Effect size (eta-squared): Proportion of variance explained by task category
- Interpretability: Do QA tasks show different entropy than summarization tasks?

**Expected Baseline Performance** (from research):
- Attention entropy typically ranges 2-5 bits depending on context
- Task-dependent variation expected based on H-E1 cluster findings
- Source: StreamingLLM sink token analysis, transformer interpretability literature

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical_analysis
- Library: scipy.stats
- Code:
  ```python
  from scipy.stats import f_oneway
  f_stat, p_value = f_oneway(*groups)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: F-statistic and p-value visualization with threshold line

#### Additional Figures (LLM Autonomous)
- Entropy heatmap: (21 tasks × 32 layers) showing mean entropy per layer per task
- Category boxplot: Entropy distribution per LongBench category (6 categories)
- Layer-wise analysis: Which layers show most task-discriminative entropy?
- Correlation with H-E1 clusters: Do entropy-based groups match compression clusters?

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** True - Shannon entropy is well-defined mathematical operation
- **mechanism_isolatable:** True - Entropy computed independently from model predictions
- **baseline_measurable:** True - Can compute entropy across all tasks uniformly

### Architecture Compatibility
- **Compatible:** Llama-2-7B supports output_attentions=True
- **Attention Access:** Via model(**inputs, output_attentions=True).attentions
- **Format:** Tuple of (batch, heads, seq_len, seq_len) per layer

### Activation Indicators
- **mechanism_log_message:** "Extracted entropy for layer {l}, head {h}: {entropy:.4f}"
- **tensor_shape_change:** attention (B, H, S, S) → entropy (B, H)
- **metric_delta_expected:** Entropy variance between tasks should be measurable (>0)

### Mechanism Verification Code
```python
def verify_mechanism(model, sample_input):
    """Verify attention entropy extraction works correctly."""
    outputs = model(**sample_input, output_attentions=True)
    
    # Check 1: Attentions returned
    assert outputs.attentions is not None, "FAIL: output_attentions not working"
    assert len(outputs.attentions) == 32, f"FAIL: Expected 32 layers, got {len(outputs.attentions)}"
    
    # Check 2: Attention shape correct
    attn = outputs.attentions[0]
    assert len(attn.shape) == 4, f"FAIL: Expected 4D tensor, got {attn.shape}"
    assert attn.shape[1] == 32, f"FAIL: Expected 32 heads, got {attn.shape[1]}"
    
    # Check 3: Entropy computable and finite
    entropy = compute_attention_entropy(attn)
    assert torch.isfinite(entropy).all(), "FAIL: Entropy contains inf/nan"
    assert entropy.min() >= 0, "FAIL: Negative entropy (impossible)"
    
    print("✓ Mechanism verification PASSED")
    return True
```

### Failure Detection
- If p-value > 0.05: Entropy does not discriminate tasks → PIVOT to alternative features
- If entropy constant across tasks: Attention extraction may be incorrect
- If entropy contains NaN/Inf: Numerical stability issue in computation

### Success Criteria
- **hypothesis_support_metric:** p-value from F-test
- **hypothesis_support_threshold:** p < 0.05

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. F-test p-value < 0.05

---

## Appendix: Reference Implementations

### Primary References

1. **lena-voita/the-story-of-heads** (ACL 2019)
   - URL: https://github.com/lena-voita/the-story-of-heads
   - Relevance: Attention head analysis methodology
   - Stars: 324

2. **heartcored98/transformer_anatomy** (ACL 2020)
   - URL: https://github.com/heartcored98/transformer_anatomy
   - Relevance: Attention head role classification
   - Stars: 16

3. **Nandan91/entropy-guided-attention-llm** (AAAI 2025)
   - URL: https://github.com/Nandan91/entropy-guided-attention-llm
   - Relevance: Entropy computation for attention
   - Stars: 10

4. **pouyapez/pytorch-pretrained-BERT/bertology.py**
   - URL: https://github.com/pouyapez/pytorch-pretrained-BERT/blob/master/examples/bertology.py
   - Relevance: BERTology entropy function

### Code Snippets

**Entropy computation (from bertology.py):**
```python
def entropy(p):
    plogp = p * torch.log(p)
    plogp[p == 0] = 0
    return -plogp.sum(dim=-1)
```

**EntropyRegularization (from entropy-guided-attention-llm):**
```python
class EntropyRegularization:
    def __init__(self, loss_coeff=1e-5, tolerance_margin_factor=0.20, context_size=None):
        self.loss_coeff = loss_coeff
        self.tolerance_margin_factor = tolerance_margin_factor
        self.context_size = context_size
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- 2026-08-10: Hypothesis h-m1 set to IN_PROGRESS (Phase 2C started)
- Prerequisite H-E1 PASSED with k*=3 clusters

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
