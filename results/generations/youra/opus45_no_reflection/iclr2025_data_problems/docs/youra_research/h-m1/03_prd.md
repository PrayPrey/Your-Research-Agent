# Product Requirements Document: H-M1

**Hypothesis:** Attention pattern structure differs between encoder (bidirectional O(n²)) and decoder (causal O(n²/2))
**Type:** MECHANISM
**Date:** 2026-08-18
**Author:** Anonymous

---

## 1. Executive Summary

This PRD specifies the implementation requirements for validating hypothesis H-M1, which tests whether attention pattern structures fundamentally differ between encoder-only (BERT) and decoder-only (GPT-2) transformer architectures. The experiment quantifies this difference through upper-triangle sparsity metrics in attention matrices.

**Key Deliverable:** Verification that BERT produces full n×n attention matrices (bidirectional) while GPT-2 produces lower-triangular matrices (causal mask), with measurable sparsity differences >0.90.

---

## 2. Problem Statement

### 2.1 Research Question
Does the architectural choice between encoder (bidirectional) and decoder (causal) transformers create measurably different attention pattern structures?

### 2.2 Hypothesis
- **BERT (encoder-only):** Full n×n attention matrix with near-zero upper-triangle sparsity (<10%)
- **GPT-2 (decoder-only):** Lower-triangular attention matrix with near-complete upper-triangle sparsity (>99%)

### 2.3 Success Criteria
- Primary: GPT-2 upper_triangle_sparsity > 0.99, BERT upper_triangle_sparsity < 0.10
- Secondary: Measurable difference confirmed across all 12 layers

---

## 3. Functional Requirements

### FR-1: Attention Extraction Pipeline
- Load pretrained BERT-base-uncased and GPT-2 models with `output_attentions=True`
- Process SST-2 validation set (872 samples) through both models
- Extract attention weights: tuple of (batch, heads, seq_len, seq_len) per layer
- Store attention tensors for analysis

### FR-2: Sparsity Metric Computation
- Compute upper-triangle sparsity: fraction of near-zero entries (< 1e-6) in upper triangle
- Compute overall attention sparsity
- Calculate sparsity difference between architectures
- Implement causal detection: >99% upper zeros → causal

### FR-3: Layer-wise Analysis
- Calculate per-layer sparsity for all 12 layers
- Generate layer-wise comparison between BERT and GPT-2
- Identify any layer-specific patterns

### FR-4: Statistical Validation
- Process full SST-2 validation set (872 samples minimum)
- Compute mean and std of sparsity metrics across samples
- Statistical significance testing if applicable

### FR-5: Visualization
- **Required:** Bar chart comparing BERT vs GPT-2 upper triangle sparsity
- Attention heatmaps: side-by-side BERT vs GPT-2 for same input
- Layer-wise sparsity line plot across 12 layers
- Attention entropy distribution histogram

---

## 4. Data Specification

### 4.1 Primary Dataset

**SST-2 (Stanford Sentiment Treebank v2)**
- Source: GLUE benchmark via HuggingFace datasets
- Identifier: `glue`, `sst2`
- Type: Standard benchmark (auto-download)

| Split | Samples | Purpose |
|-------|---------|---------|
| Validation | 872 | Primary attention analysis |
| Test | 1,821 | Secondary validation |

**Loading:**
```python
from datasets import load_dataset
dataset = load_dataset("glue", "sst2")
val_data = dataset["validation"]  # 872 samples
```

### 4.2 Preprocessing
- Tokenize with model-specific tokenizer (BERT/GPT-2)
- Pad/truncate to max_length=128
- Use validation split for attention extraction

---

## 5. Model Specification

### 5.1 BERT-base-uncased (Encoder-only)
- Architecture: Encoder-only transformer
- Layers: 12, Hidden: 768, Heads: 12
- Parameters: ~110M
- Attention: Bidirectional (full n×n matrix)
- HuggingFace ID: `bert-base-uncased`

### 5.2 GPT-2 (Decoder-only)
- Architecture: Decoder-only transformer
- Layers: 12, Hidden: 768, Heads: 12
- Parameters: ~124M
- Attention: Causal (lower-triangular matrix)
- HuggingFace ID: `gpt2`
- Note: Set `pad_token = eos_token`

### 5.3 Loading
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

---

## 6. Evaluation Metrics

### 6.1 Primary Metrics
| Metric | Description | Expected BERT | Expected GPT-2 |
|--------|-------------|---------------|----------------|
| upper_triangle_sparsity | Fraction of near-zero in upper triangle | <0.10 | >0.99 |
| sparsity_difference | GPT-2 - BERT upper sparsity | N/A | ~1.0 |
| is_causal | Binary detection (>99% upper zeros) | False | True |

### 6.2 Secondary Metrics
- Per-layer sparsity breakdown (12 values per model)
- Per-head attention entropy
- Mean attention weight in lower vs upper triangle

### 6.3 Metric Implementation
```python
def upper_triangle_sparsity(attn_matrix, threshold=1e-6):
    seq_len = attn_matrix.shape[-1]
    mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
    upper_values = attn_matrix[..., mask]
    return (upper_values < threshold).float().mean().item()
```

---

## 7. Dependencies

### 7.1 Python Packages
| Package | Version | Purpose |
|---------|---------|---------|
| torch | >=2.0.0 | Core framework |
| transformers | >=4.30.0 | BERT/GPT-2 models |
| datasets | >=2.14.0 | SST-2 loading |
| numpy | >=1.24.0 | Array operations |
| matplotlib | >=3.7.0 | Visualization |
| seaborn | >=0.12.0 | Heatmaps |

### 7.2 Hardware
- GPU recommended for faster inference
- CPU fallback supported
- Memory: ~4GB GPU or ~8GB RAM

---

## 8. Non-Functional Requirements

### NFR-1: Performance
- Process 872 samples in <10 minutes on GPU
- Batch size 1 for per-sample attention extraction

### NFR-2: Reproducibility
- Set random seeds for any stochastic operations
- Log all model versions and configurations

### NFR-3: Output Format
- Save metrics to JSON/YAML
- Save figures to PNG format in figures/ directory
- Generate summary report in Markdown

---

## 9. Gate Condition

**Type:** MUST_WORK
**Pass Condition:** Attention pattern structure matches architectural definition
- BERT: full n×n (upper_triangle_sparsity < 0.10)
- GPT-2: lower-triangular (upper_triangle_sparsity > 0.99)

**Fail Action:** STOP - architectural error (unlikely given architectural definitions)

---

## 10. Ablation Studies

### 10.1 Layer-wise Sparsity
- Analyze sparsity pattern across all 12 layers
- Check if sparsity is consistent or varies by depth

### 10.2 Sequence Length Variation
- Test with different max_length values (64, 128, 256)
- Verify sparsity patterns hold across lengths

---

## Appendix: Reference Implementation

**BertViz (jessevig/bertviz):**
- URL: https://github.com/jessevig/bertviz
- Paper: Vig, J. (2019). "Visualizing Attention in Transformer-Based Language Representation Models"

**PyTorch Scaled Dot-Product Attention:**
- `is_causal=True` flag creates lower-triangular mask via `torch.tril()`
