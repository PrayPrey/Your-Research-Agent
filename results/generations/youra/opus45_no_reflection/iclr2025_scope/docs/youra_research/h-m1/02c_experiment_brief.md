# Experiment Design: H-M1

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Phi-1.5 attention exhibits extrapolation artifacts at 16K-32K sequence lengths
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing causal mechanism underlying main hypothesis.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 PASS (Unified framework validated)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
**MUST_WORK**: Attention entropy must increase significantly beyond 4K sequence length. If attention remains structured at 32K, the length extrapolation premise for the main hypothesis is weakened.

**Pass Condition:** Entropy increases >20% from 2K to 16K, sparsity patterns emerge at 16K+
**Fail Action:** Reduce max experiment length to 16K, or document as negative finding

---

## Continuation Context

### Previous Hypothesis Results (H-E1)
- **Gate:** PASS
- **Key Finding:** Unified Phi-Mamba framework successfully implements both MOHAWK (matrix-level) and CAB (token-level) objectives
- **Dataset Used:** allenai/c4 (streaming)
- **Tokenizer:** microsoft/phi-1_5
- **Reusable Components:** C4DataLoader, tokenizer setup, embedding layer

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct findings on Phi-1.5 attention entropy analysis. Relevant patterns from diffusion attention processors showing attention score computation via einsum operations.

### Archon Code Examples

FlashAttention references found - IO-aware attention computation. Not directly applicable but confirms attention entropy is computable from attention weights.

### Exa GitHub Implementations

**Key Findings from Research:**

1. **Information Entropy Invariance (InfoScale)** - https://github.com/HT-NEKO/InfoScale
   - Training-free entropy-invariant scaling for length extrapolation
   - Demonstrates attention entropy increases logarithmically with sequence length
   - Provides entropy computation methodology

2. **RoPE Extensions Analysis** - ACL 2025
   - "Large attention uncertainty leads to retrieval errors"
   - Attention entropy measured across lengths shows degradation
   - Code: `entropy = -sum(p * log(p))` for attention distributions

3. **Attention Alignment via Temperature Scaling** - NAACL 2024
   - T5 suffers "dispersed attention issue" at long lengths
   - Entropy alignment strategy via temperature scaling
   - Validates entropy as diagnostic metric

4. **ReAttention** - Training-free infinite context
   - "Self-attention entropy increases logarithmically with length of attention window"
   - Confirms entropy-based length extrapolation analysis approach

### 🎯 Implementation Priority Assessment

**CRITICAL: This is an analysis experiment, not training.**

**Recommended Implementation Path:**
- Primary: Extract attention patterns from Phi-1.5 at multiple lengths using HuggingFace
- Fallback: Use MOHAWK codebase attention extraction if HF access limited
- Justification: Direct measurement of teacher model behavior, no training required

### Code Analysis (Serena MCP)

Not applicable - analyzing pretrained model behavior, not modifying codebase.

---

## Experiment Specification

### Dataset

**Dataset:** C4 (allenai/c4)
**Type:** standard
**Source:** HuggingFace Datasets

**Specification:**
- Use C4 validation split for consistency
- Sample 500 documents at each length: 2K, 4K, 8K, 16K, 32K
- Filter for documents with sufficient length (>32K tokens for longest condition)
- Use same tokenizer as Phi-1.5 (microsoft/phi-1_5)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets (streaming)
- Identifier: `allenai/c4`, config `en`, split `validation`
- Code:
```python
from datasets import load_dataset
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1_5")
dataset = load_dataset("allenai/c4", "en", split="validation", streaming=True)

def filter_long_docs(example, min_tokens=32768):
    tokens = tokenizer(example["text"], truncation=False)["input_ids"]
    return len(tokens) >= min_tokens

long_docs = dataset.filter(filter_long_docs).take(500)
```

### Models

#### Baseline Model

**Architecture:** Phi-1.5 (microsoft/phi-1_5)
**Type:** Pretrained Transformer LM
**Parameters:** 1.3B
**Max Training Length:** 2048 tokens

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `microsoft/phi-1_5`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "microsoft/phi-1_5",
    trust_remote_code=True,
    torch_dtype=torch.float16,
    device_map="auto",
    output_attentions=True  # Critical for entropy extraction
)
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1_5")
```

#### Proposed Model

**Architecture:** Same Phi-1.5 model (no modification)

This is an **analysis experiment** - we analyze the teacher model's attention behavior across lengths, not train a new model.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Attention Entropy Analysis
# Based on: InfoScale (HT-NEKO), RoPE Extensions (ACL 2025)

import torch
import torch.nn.functional as F
from typing import List, Tuple
import numpy as np

def compute_attention_entropy(attention_weights: torch.Tensor) -> torch.Tensor:
    """
    Compute entropy of attention distribution per head per position.
    
    Args:
        attention_weights: (batch, heads, seq_len, seq_len) attention probs
    Returns:
        entropy: (batch, heads, seq_len) entropy per query position
    """
    # Clamp for numerical stability (avoid log(0))
    attn = attention_weights.clamp(min=1e-10)
    # H = -sum(p * log(p))
    entropy = -torch.sum(attn * torch.log(attn), dim=-1)
    return entropy

def compute_attention_sparsity(attention_weights: torch.Tensor, top_k: int = 32) -> torch.Tensor:
    """
    Compute sparsity as fraction of attention in top-k positions.
    
    Args:
        attention_weights: (batch, heads, seq_len, seq_len)
        top_k: number of top positions to consider
    Returns:
        sparsity: (batch, heads, seq_len) fraction in top-k
    """
    topk_vals, _ = torch.topk(attention_weights, k=min(top_k, attention_weights.size(-1)), dim=-1)
    top_k_mass = topk_vals.sum(dim=-1)
    return top_k_mass

def analyze_phi15_attention(
    model,
    tokenizer,
    texts: List[str],
    target_lengths: List[int] = [2048, 4096, 8192, 16384, 32768],
    middle_layers: List[int] = [8, 12, 16]  # Layers 8-16 of 24
) -> dict:
    """
    Extract attention entropy and sparsity across sequence lengths.
    
    Returns:
        results: {length: {layer: {entropy_mean, entropy_std, sparsity_mean}}}
    """
    results = {}
    
    for length in target_lengths:
        results[length] = {}
        
        for text in texts:
            tokens = tokenizer(text, return_tensors="pt", truncation=True, max_length=length)
            
            with torch.no_grad():
                outputs = model(**tokens.to(model.device), output_attentions=True)
            
            for layer_idx in middle_layers:
                attn = outputs.attentions[layer_idx]  # (1, heads, seq, seq)
                entropy = compute_attention_entropy(attn)
                sparsity = compute_attention_sparsity(attn)
                
                # Aggregate statistics
                if layer_idx not in results[length]:
                    results[length][layer_idx] = {"entropies": [], "sparsities": []}
                
                results[length][layer_idx]["entropies"].append(entropy.mean().item())
                results[length][layer_idx]["sparsities"].append(sparsity.mean().item())
    
    return results
```

### Training Protocol

**Not Applicable** - This is an analysis experiment, not a training experiment.

**Execution Protocol:**
- Load Phi-1.5 model with `output_attentions=True`
- Sample 500 documents from C4 validation (streaming)
- For each target length [2K, 4K, 8K, 16K, 32K]:
  - Truncate documents to target length
  - Run forward pass, extract attention from middle layers (8, 12, 16)
  - Compute entropy and sparsity metrics
  - Aggregate statistics across documents

**Computational Requirements:**
- GPU Memory: ~8GB (float16, single sequence)
- Time: ~2-3 hours for 500 docs × 5 lengths
- Seeds: 1 (deterministic analysis, no training)

### Evaluation

**Primary Metrics:**

1. **Attention Entropy** (H):
   - Definition: `H = -sum(p * log(p))` over attention distribution
   - Measured: Mean entropy per layer, aggregated across heads and positions
   - Expected: Entropy increases with sequence length beyond training length (2K)

2. **Attention Sparsity** (S_k):
   - Definition: Fraction of attention mass in top-k positions (k=32)
   - Measured: Mean sparsity per layer
   - Expected: Sparsity decreases (more diffuse attention) at extrapolated lengths

3. **Entropy Inflection Point**:
   - Definition: Length at which entropy increase rate changes significantly
   - Measured: Second derivative of entropy vs log(length) curve
   - Expected: Inflection around 4K-8K (2-4x training length)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Analysis (not classification/regression)
- Library: Custom (PyTorch native)
- Code: See `compute_attention_entropy()` and `compute_attention_sparsity()` above

**Success Criteria (PoC):**
- Primary: Entropy at 16K > Entropy at 2K by >20%
- Secondary: Entropy at 32K > Entropy at 16K (continued degradation)
- Tertiary: Top-k sparsity at 32K < sparsity at 2K (attention more diffuse)

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Entropy at 2K vs 16K vs 32K bar chart

#### Additional Figures (LLM Autonomous)

1. **Entropy vs Length Curve**: Line plot of mean entropy across layers vs sequence length (log-scale x-axis)
2. **Layer-wise Entropy Heatmap**: Heatmap showing entropy per layer per length
3. **Sparsity Distribution**: Box plots of top-k sparsity at each length
4. **Attention Pattern Samples**: Example attention matrices at 2K vs 32K for qualitative comparison

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** Yes - Phi-1.5 attention is accessible via `output_attentions=True`
- **mechanism_isolatable:** Yes - Can extract attention weights per layer
- **baseline_measurable:** Yes - Entropy computable from any attention distribution

### Architecture Compatibility
- **Phi-1.5:** 24 transformer layers, standard multi-head attention
- **Attention Access:** `outputs.attentions` returns tuple of (batch, heads, seq, seq) tensors
- **Memory Constraint:** 32K sequences require ~8GB VRAM in float16

### Activation Indicators
- **mechanism_log_message:** "Extracted attention from layer {layer_idx}, shape {attn.shape}"
- **tensor_shape_change:** Attention shape scales with sequence length: (1, 32, L, L)
- **metric_delta_expected:** Entropy increase >0.5 nats from 2K to 32K

### Mechanism Verification Code
```python
def verify_mechanism_activation(outputs, expected_layers=[8, 12, 16]):
    """Verify attention extraction works correctly."""
    assert outputs.attentions is not None, "Attentions not returned"
    assert len(outputs.attentions) == 24, f"Expected 24 layers, got {len(outputs.attentions)}"
    
    for layer_idx in expected_layers:
        attn = outputs.attentions[layer_idx]
        assert attn.dim() == 4, f"Expected 4D attention, got {attn.dim()}D"
        assert torch.isfinite(attn).all(), f"Non-finite values in layer {layer_idx}"
        assert (attn >= 0).all(), f"Negative attention values in layer {layer_idx}"
        assert torch.allclose(attn.sum(dim=-1), torch.ones_like(attn.sum(dim=-1)), atol=1e-5), \
            f"Attention not normalized in layer {layer_idx}"
    
    print("✓ Mechanism verification PASSED")
    return True
```

### Success Criteria
- **hypothesis_support_threshold:** Entropy increase >20% from 2K to 16K
- **hypothesis_support_metric:** `(entropy_16k - entropy_2k) / entropy_2k > 0.20`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Entropy at 16K > Entropy at 2K by >20%
3. Entropy trend shows increase with length beyond training length

---

## Appendix: Reference Implementations

### Primary References

1. **InfoScale (Entropy Invariance)**
   - Repository: https://github.com/HT-NEKO/InfoScale
   - Key Contribution: Entropy-based analysis of length extrapolation
   - Relevance: Provides theoretical framework and entropy computation method

2. **RoPE Extensions Analysis (ACL 2025)**
   - Paper: "Understanding the RoPE Extensions of Long-Context LLMs"
   - Key Contribution: Attention entropy correlates with retrieval errors
   - Relevance: Validates entropy as diagnostic metric for length extrapolation

3. **Attention Alignment (NAACL 2024)**
   - Paper: "Attention Alignment and Flexible Positional Embeddings"
   - Key Contribution: Temperature scaling to maintain attention sharpness
   - Relevance: Entropy alignment strategy reference

4. **Phi-1.5 Technical Report**
   - Paper: "Textbooks Are All You Need II: phi-1.5"
   - Key Contribution: Model architecture and training details
   - Relevance: Training length = 2048, confirms extrapolation boundary

### Code References

```python
# From InfoScale - entropy computation
def entropy(attention_weights):
    attn = attention_weights.clamp(min=1e-10)
    return -torch.sum(attn * torch.log(attn), dim=-1)

# From RoPE Extensions - entropy vs length analysis
# "positions with errors are among the top-k in entropy"
# "attention entropy generally below 5 at length 63938" (after training)
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- H-E1 VALIDATED: Unified framework exists (2026-08-18)
- H-M1 IN_PROGRESS: Experiment design generated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web Search)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
