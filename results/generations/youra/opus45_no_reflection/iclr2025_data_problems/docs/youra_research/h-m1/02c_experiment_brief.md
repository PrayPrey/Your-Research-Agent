# Experiment Design: H-M1

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Attention pattern structure differs between encoder (bidirectional O(n²)) and decoder (causal O(n²/2))
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing causal mechanism (attention pattern divergence)

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (PASS)
**Gate Status:** MUST_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASS)

### Gate Condition
**Type:** MUST_WORK
**Pass Condition:** Attention pattern structure matches architectural definition (BERT full n×n, GPT-2 lower-triangular)
**Fail Action:** STOP - architectural error (unlikely given architectural definitions)

---

## Continuation Context

H-M1 builds on H-E1's validation that architecture-method interaction exists and is measurable.

### Previous Hypothesis Results (H-E1)
- **Result:** PASS
- **Best method:** TRAK (+5.1% AUC difference)
- **Methods tested:** 3 (TRAK, EK-FAC, TracIn)
- **Architectures tested:** 2 (BERT, GPT-2)
- **Implication:** Now verify the mechanistic explanation (attention pattern divergence)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**PyTorch Scaled Dot-Product Attention (torch.nn.functional.scaled_dot_product_attention):**
- Native support for `is_causal=True` flag for causal masking
- Implementation creates lower-triangular mask via `torch.ones(L, S).tril(diagonal=0)`
- Causal mask fills upper triangle with `-inf` before softmax
- This is the core mechanism differentiating BERT (no causal mask) from GPT-2 (causal mask)

**Key Code Pattern:**
```python
if is_causal:
    temp_mask = torch.ones(L, S, dtype=torch.bool).tril(diagonal=0)
    attn_bias.masked_fill_(temp_mask.logical_not(), float("-inf"))
```

### Archon Code Examples

**GPT-2 Model Initialization:**
- HuggingFace Transformers provides unified API for both BERT and GPT-2
- `output_attentions=True` returns attention weights from all layers

### Exa GitHub Implementations

**BertViz (jessevig/bertviz) - Primary Reference:**
- Interactive attention visualization for BERT, GPT-2, RoBERTa
- Simple API: `model(inputs, output_attentions=True)` → `outputs.attentions`
- Supports head view, model view, neuron view
- URL: https://github.com/jessevig/bertviz

**Key Implementation Pattern:**
```python
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained(model_name, output_attentions=True)
tokenizer = AutoTokenizer.from_pretrained(model_name)

inputs = tokenizer.encode(text, return_tensors='pt')
outputs = model(inputs)
attention = outputs.attentions  # Tuple of (batch, heads, seq_len, seq_len)
```

**IzzyViz (YiqiWang128/IzzyViz):**
- Supports encoder-only (BERT), decoder-only (GPT-2), encoder-decoder (T5)
- Static PDF output for research papers
- Comparison heatmaps for attention pattern analysis

**HuggingFace attention_visualizer.py:**
- Official utility for attention mask visualization
- Handles causal mask generation via `_update_causal_mask()`

### 🎯 Implementation Priority Assessment

**For H-M1 (attention pattern verification), use HuggingFace Transformers directly:**

1. **BERT (bert-base-uncased):** Produces full n×n attention matrices (bidirectional)
2. **GPT-2 (gpt2):** Produces lower-triangular attention matrices (causal mask)

**Recommended Implementation Path:**
- Primary: HuggingFace Transformers `output_attentions=True`
- Fallback: BertViz for visualization if needed
- Justification: Native HuggingFace API is simplest, returns raw attention tensors for quantitative analysis

### Code Analysis (Serena MCP)

*Skipped - No local codebase to analyze. H-M1 tests architectural properties of pretrained models.*

---

## Experiment Specification

### Dataset

**Name:** SST-2 (Stanford Sentiment Treebank v2)
**Source:** GLUE benchmark via HuggingFace datasets
**Type:** Standard (real dataset)

| Split | Samples | Purpose |
|-------|---------|---------|
| Train | 67,349 | Not used (pretrained models) |
| Validation | 872 | Attention pattern analysis |
| Test | 1,821 | Secondary validation |

**Preprocessing:**
- Tokenize with model-specific tokenizer (BERT/GPT-2)
- Pad/truncate to max_length=128
- Use validation split for attention extraction (872 samples)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `glue`, `sst2`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("glue", "sst2")
val_data = dataset["validation"]  # 872 samples
```

### Models

#### Baseline Model

**BERT-base-uncased:**
- Architecture: Encoder-only transformer
- Layers: 12
- Hidden: 768
- Heads: 12
- Parameters: ~110M
- Attention: Bidirectional (full n×n matrix)

**GPT-2:**
- Architecture: Decoder-only transformer
- Layers: 12
- Hidden: 768
- Heads: 12
- Parameters: ~124M
- Attention: Causal (lower-triangular matrix)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `bert-base-uncased`, `gpt2`
- Code:
```python
from transformers import AutoModel, AutoTokenizer

# BERT
bert_model = AutoModel.from_pretrained("bert-base-uncased", output_attentions=True)
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# GPT-2
gpt2_model = AutoModel.from_pretrained("gpt2", output_attentions=True)
gpt2_tokenizer = AutoTokenizer.from_pretrained("gpt2")
gpt2_tokenizer.pad_token = gpt2_tokenizer.eos_token
```

#### Proposed Model

**Architecture:** No modification needed - testing architectural property of existing models

**Core Mechanism Implementation:**

```python
def extract_attention_patterns(model, tokenizer, texts, max_length=128):
    """Extract attention weights from transformer model."""
    results = []
    
    for text in texts:
        inputs = tokenizer(text, return_tensors="pt", 
                          max_length=max_length, 
                          padding="max_length", 
                          truncation=True)
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        # attention: tuple of (batch, heads, seq_len, seq_len) per layer
        attention = outputs.attentions
        results.append(attention)
    
    return results

def compute_attention_sparsity(attention_weights):
    """Compute sparsity metrics for attention matrices."""
    # Stack all layers: (layers, batch, heads, seq, seq)
    attn_stack = torch.stack(attention_weights)
    
    # For causal models: count zeros in upper triangle
    seq_len = attn_stack.shape[-1]
    upper_triangle_mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
    
    # Effective zeros (attention < threshold or masked)
    threshold = 1e-6
    zero_mask = attn_stack < threshold
    
    # Sparsity = fraction of near-zero entries
    total_entries = attn_stack.numel()
    zero_entries = zero_mask.sum().item()
    
    # Upper triangle zeros (causal indicator)
    upper_zeros = (attn_stack[..., upper_triangle_mask] < threshold).sum().item()
    upper_total = upper_triangle_mask.sum().item() * attn_stack.shape[:-2].numel()
    
    return {
        "overall_sparsity": zero_entries / total_entries,
        "upper_triangle_sparsity": upper_zeros / upper_total,
        "is_causal": upper_zeros / upper_total > 0.99  # >99% zeros in upper triangle
    }

def verify_attention_structure(bert_attention, gpt2_attention):
    """Verify architectural attention pattern differences."""
    bert_metrics = compute_attention_sparsity(bert_attention)
    gpt2_metrics = compute_attention_sparsity(gpt2_attention)
    
    # BERT: full matrix (low upper-triangle sparsity)
    # GPT-2: causal mask (high upper-triangle sparsity ~100%)
    
    return {
        "bert_upper_sparsity": bert_metrics["upper_triangle_sparsity"],
        "gpt2_upper_sparsity": gpt2_metrics["upper_triangle_sparsity"],
        "bert_is_causal": bert_metrics["is_causal"],
        "gpt2_is_causal": gpt2_metrics["is_causal"],
        "sparsity_difference": gpt2_metrics["upper_triangle_sparsity"] - bert_metrics["upper_triangle_sparsity"]
    }
```

### Training Protocol

**No training required** - H-M1 analyzes pretrained model attention patterns.

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Training | None | Testing architectural property |
| Inference | Forward pass only | Extract attention weights |
| Batch size | 1 | Per-sample attention extraction |
| Device | GPU (if available) | Speed |
| Samples | 872 (full validation) | Statistical significance |

### Evaluation

**Primary Metrics:**
1. **Upper Triangle Sparsity:** Fraction of near-zero attention in upper triangle
   - BERT expected: ~0% (bidirectional)
   - GPT-2 expected: ~100% (causal mask)

2. **Sparsity Difference:** GPT-2 upper sparsity - BERT upper sparsity
   - Expected: ~1.0 (or ~50% when counting all entries)

3. **Causal Detection:** Binary classification of attention pattern type
   - Threshold: >99% upper triangle zeros → causal

**Secondary Metrics:**
- Per-layer sparsity breakdown
- Per-head attention entropy
- Mean attention weight in lower vs upper triangle

**Success Criteria:**
- Primary: GPT-2 upper_triangle_sparsity > 0.99, BERT upper_triangle_sparsity < 0.10
- Secondary: Measurable difference confirmed across all 12 layers

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Attention pattern analysis (not classification)
- Library: torch, numpy
- Code:
```python
import torch
import numpy as np

def upper_triangle_sparsity(attn_matrix, threshold=1e-6):
    """Compute fraction of near-zero entries in upper triangle."""
    seq_len = attn_matrix.shape[-1]
    mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
    upper_values = attn_matrix[..., mask]
    return (upper_values < threshold).float().mean().item()
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing BERT vs GPT-2 upper triangle sparsity

#### Additional Figures (LLM Autonomous)

1. **Attention Heatmaps:** Side-by-side BERT vs GPT-2 attention matrices for same input
   - Shows full matrix (BERT) vs lower-triangular (GPT-2)
   
2. **Layer-wise Sparsity:** Line plot of sparsity across 12 layers for both models

3. **Attention Entropy Distribution:** Histogram of per-head attention entropy

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Attention patterns match architectural definition (BERT: full matrix, GPT-2: causal mask)
3. Measurable sparsity difference quantified

---

## Appendix: Reference Implementations

### Primary References

1. **HuggingFace Transformers - Attention Output**
   - URL: https://huggingface.co/docs/transformers/index
   - Usage: `output_attentions=True` returns tuple of attention tensors
   - Format: `(batch_size, num_heads, sequence_length, sequence_length)`

2. **BertViz - Attention Visualization**
   - URL: https://github.com/jessevig/bertviz
   - Paper: Vig, J. (2019). "Visualizing Attention in Transformer-Based Language Representation Models"
   - ArXiv: https://arxiv.org/abs/1904.02679

3. **PyTorch Scaled Dot-Product Attention**
   - URL: https://pytorch.org/docs/master/generated/torch.nn.functional.scaled_dot_product_attention
   - Key: `is_causal` parameter creates lower-triangular mask

### Code Snippets from Research

**BertViz Attention Extraction:**
```python
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("bert-base-uncased", output_attentions=True)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

inputs = tokenizer.encode("The cat sat on the mat", return_tensors='pt')
outputs = model(inputs)
attention = outputs[-1]  # or outputs.attentions
tokens = tokenizer.convert_ids_to_tokens(inputs[0])
```

**PyTorch Causal Mask Generation:**
```python
def create_causal_mask(seq_len):
    """Create lower-triangular causal attention mask."""
    return torch.tril(torch.ones(seq_len, seq_len))
```

### Related Papers

- Clark et al. (2019). "What Does BERT Look At? An Analysis of BERT's Attention"
  - ArXiv: https://arxiv.org/abs/1906.04341
  
- Michel et al. (2019). "Are Sixteen Heads Really Better than One?"
  - ArXiv: https://arxiv.org/abs/1905.10650

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- H-E1 → PASS (prerequisite satisfied)
- H-M1 → IN_PROGRESS (current)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
