---
stepsCompleted: [1, 2, 3, 4, 5]
hypothesis_id: h-e1
generated_by: Phase 3 Implementation Planning
date: 2026-03-18
---

# Product Requirements Document: Low-Rank Structure Analysis (h-e1)

**Hypothesis:** Deep Transformer layers (L≥20) exhibit operator-level low-rank structure with r_eff < 256 and monotonically decreasing operator entropy (β<0, p<0.01)

**Type:** EXISTENCE (PoC validation)
**Gate:** MUST_WORK
**Source:** Phase 2C Experiment Brief (02c_experiment_brief.md)

---

## Executive Summary

### Purpose
Validate the foundational assumption that deep Transformer layers (L≥20) in pre-trained LLaMA-7B/13B models exhibit operator-level low-rank structure, enabling bounded-state SSM conversion.

### Scope
- **In Scope:** SVD-based analysis of attention matrices from LLaMA layers 20-32, effective rank calculation, operator entropy regression
- **Out of Scope:** Model training, fine-tuning, SSM conversion implementation
- **Type:** Analysis experiment (inference-only)

### Success Criteria
1. Primary: r_eff < 256 for ALL layers L≥20
2. Secondary: β < 0 with p < 0.01 (monotonic entropy decrease)

---

## Problem Statement

### Background
The main hypothesis proposes converting deep Transformer layers to hybrid SSM-SWA architecture for efficiency. This requires validating that deep layers have compressed representations suitable for bounded-state SSM conversion (state size N ≤ 1024).

### Hypothesis Statement
Deep Transformer layers (L≥20) in pre-trained LLaMA-7B/13B models exhibit operator-level low-rank structure with effective attention rank r_eff < 256 and monotonically decreasing operator entropy (β<0, p<0.01) across layer depth.

### Gate Condition
**MUST_WORK:** If hypothesis fails, ABORT entire conversion approach (SSM state would need to scale unboundedly).

---

## Functional Requirements

### FR-1: Model Loading and Setup
**Priority:** P0 (Critical)
**Description:** Load pre-trained LLaMA-7B model with attention output hooks
**Acceptance Criteria:**
- Load model using HuggingFace Transformers (`meta-llama/Llama-2-7b-hf`)
- Configure fp16 precision for memory efficiency
- Register forward hooks to capture attention outputs for layers 20-32
- Verify model loaded successfully and hooks active

**Dependencies:**
- HuggingFace Transformers library
- HuggingFace authentication token with LLaMA access
- GPU with ≥16GB VRAM (A100/V100)

### FR-2: Dataset Preparation
**Priority:** P0 (Critical)
**Description:** Load and preprocess The Pile dataset for analysis
**Acceptance Criteria:**
- Load The Pile using HuggingFace datasets in streaming mode
- Sample 5K-10K sequences for analysis
- Tokenize sequences using LLaMA tokenizer
- Pack sequences to context lengths: 2K, 8K tokens
- Create DataLoader with batch processing

**Dependencies:**
- HuggingFace datasets library
- The Pile dataset access (EleutherAI/pile)
- LLaMA tokenizer

### FR-3: Attention Matrix Extraction
**Priority:** P0 (Critical)
**Description:** Extract attention matrices from target layers during inference
**Acceptance Criteria:**
- Run inference on prepared dataset (no gradient computation)
- Capture attention outputs from layers 20-32 via hooks
- Store attention matrices: (batch, heads, seq_len, seq_len)
- Verify all target layers captured successfully
- Handle memory efficiently (clear cache between batches)

**Dependencies:**
- FR-1 (model loaded with hooks)
- FR-2 (dataset prepared)

### FR-4: Effective Rank Computation
**Priority:** P0 (Critical)
**Description:** Compute effective rank via SVD decomposition
**Acceptance Criteria:**
- Implement SVD-based effective rank calculation
- Use 99% variance threshold (configurable)
- Compute rank for each layer independently
- Average rank across samples for each layer
- Validate r_eff < 256 for all layers L≥20

**Pseudo-code:**
```python
def compute_effective_rank(attention_matrix, threshold=0.99):
    # attention_matrix: (batch*heads, seq_len, seq_len)
    U, S, V = torch.linalg.svd(attention_matrix)
    variance = S ** 2
    cumsum_variance = torch.cumsum(variance, dim=-1)
    total_variance = cumsum_variance[:, -1:]
    explained_ratio = cumsum_variance / total_variance
    eff_rank = (explained_ratio < threshold).sum(dim=-1) + 1
    return eff_rank.float().mean().item()
```

**Dependencies:**
- FR-3 (attention matrices extracted)
- PyTorch (`torch.linalg.svd`)

### FR-5: Operator Entropy Calculation
**Priority:** P0 (Critical)
**Description:** Compute operator entropy for each target layer
**Acceptance Criteria:**
- Extract Q, K, V projection matrices from each layer
- Compute QK covariance matrix
- Calculate log-determinant (operator entropy)
- Store entropy values for all layers 20-32

**Pseudo-code:**
```python
def compute_operator_entropy(layer):
    Q = layer.self_attn.q_proj.weight
    K = layer.self_attn.k_proj.weight
    QK = torch.matmul(Q, K.T)
    cov = torch.cov(QK)
    entropy = torch.logdet(cov + 1e-6)  # Numerical stability
    return entropy.item()
```

**Dependencies:**
- FR-1 (model loaded)
- PyTorch

### FR-6: Entropy Regression Analysis
**Priority:** P0 (Critical)
**Description:** Fit linear regression of entropy vs layer depth
**Acceptance Criteria:**
- Perform linear regression: entropy ~ layer_index
- Extract slope (β) and p-value
- Validate β < 0 with p < 0.01 (monotonic decrease)
- Report regression statistics (R², p-value, slope)

**Dependencies:**
- FR-5 (entropy values computed)
- SciPy (`scipy.stats.linregress`)

### FR-7: Visualization Generation
**Priority:** P1 (High)
**Description:** Generate analysis figures
**Acceptance Criteria:**
- Figure 1: Effective rank vs layer depth (line plot, all 32 layers, highlight L≥20)
- Figure 2: Operator entropy vs layer depth (scatter + regression line)
- Figure 3: Singular value distribution heatmap (layers 20-32)
- Figure 4: Rank threshold sensitivity (90%, 95%, 99%, 99.9%)
- All figures saved to `{hypothesis_folder}/figures/`

**Dependencies:**
- FR-4 (effective rank data)
- FR-5 (entropy data)
- matplotlib/seaborn

### FR-8: Results Validation and Reporting
**Priority:** P0 (Critical)
**Description:** Validate success criteria and generate validation report
**Acceptance Criteria:**
- Check r_eff < 256 for ALL layers 20-32
- Check β < 0 and p < 0.01
- Generate validation report (04_validation.md format)
- Report pass/fail status with supporting data
- Include gate decision (MUST_WORK satisfied or not)

**Dependencies:**
- FR-4 (effective rank results)
- FR-6 (regression results)

---

## Non-Functional Requirements

### NFR-1: Performance
- **Requirement:** Complete analysis within 3-4 hours on single GPU
- **Rationale:** Inference-only, no training required
- **Measurement:** Wall-clock time from start to results

### NFR-2: Memory Efficiency
- **Requirement:** Fit on single A100 (40GB) or V100 (16GB) GPU
- **Rationale:** LLaMA-7B fp16 + attention matrices for analysis
- **Measurement:** Peak GPU memory usage via nvidia-smi

### NFR-3: Reproducibility
- **Requirement:** Fixed random seed (42) for consistent results
- **Rationale:** Scientific reproducibility
- **Measurement:** Identical results across runs with same seed

### NFR-4: Code Quality
- **Requirement:** Modular analyzer class, clear separation of concerns
- **Rationale:** Maintainability, reusability for LLaMA-13B validation
- **Measurement:** Code review, class structure

---

## Data Requirements

### Input Data
1. **Pre-trained Model:**
   - Source: HuggingFace Hub
   - Identifier: `meta-llama/Llama-2-7b-hf`
   - Size: ~13GB (fp16)
   - Access: Requires HuggingFace auth token

2. **Dataset:**
   - Source: The Pile (EleutherAI)
   - Identifier: `EleutherAI/pile`
   - Split: train (streaming)
   - Samples: 5K-10K sequences
   - Context lengths: 2K, 8K tokens

### Output Data
1. **Analysis Results:**
   - Effective rank per layer (layers 1-32)
   - Operator entropy per layer (layers 20-32)
   - Regression statistics (β, p-value, R²)

2. **Figures:**
   - 4 PNG files in `{hypothesis_folder}/figures/`

3. **Validation Report:**
   - `04_validation.md` with pass/fail decision

---

## Environment Requirements

### Hardware
- GPU: 1x NVIDIA A100 (40GB) or V100 (16GB)
- RAM: ≥32GB system memory
- Storage: ~20GB (model + dataset cache)

### Software
- Python 3.8+
- PyTorch 2.0+ with CUDA support
- HuggingFace Transformers 4.30+
- HuggingFace datasets 2.12+
- SciPy 1.10+
- matplotlib/seaborn for visualization

### GPU Selection
```bash
# ALWAYS set before running
export CUDA_VISIBLE_DEVICES=<empty_gpu_id>
nvidia-smi  # Check GPU availability
```

---

## Dependencies

### External Libraries
- `transformers` (HuggingFace)
- `datasets` (HuggingFace)
- `torch` (PyTorch)
- `scipy` (regression analysis)
- `matplotlib`, `seaborn` (visualization)

### Access Requirements
- HuggingFace authentication token with LLaMA model access
- Network access for model/dataset download (first run)

### Prerequisite Hypotheses
None (foundation hypothesis)

---

## Success Metrics

### Primary Metrics
1. **Effective Rank (r_eff):**
   - Target: r_eff < 256 for ALL layers L≥20
   - Method: SVD-based rank at 99% variance
   - Threshold: MUST satisfy for all 12 layers (20-32)

2. **Operator Entropy Slope (β):**
   - Target: β < 0 with p < 0.01
   - Method: Linear regression entropy ~ layer_depth
   - Statistical test: One-tailed t-test on slope

### PoC Pass Condition
**Both** primary metrics must be satisfied:
- r_eff < 256 for all L≥20 **AND**
- β < 0, p < 0.01

### Expected Baseline
Based on LoRA literature (HuggingFace PEFT):
- Expected r_eff: 8-64 for attention weight updates
- Expected range for full attention: 50-200

---

## Implementation Notes

### From Phase 2C Research

**Archon Knowledge Base Findings:**
- LoRA demonstrates ranks 8-64 for attention layers (q_proj, k_proj, v_proj)
- SVD-based rank estimation at 90-99% variance threshold is standard
- PyTorch `torch.linalg.svd` is the recommended implementation

**Code Patterns:**
```python
# Standard attention extraction (from PyTorch docs)
attn_weight = query @ key.transpose(-2, -1) * scale_factor
attn_weight = torch.softmax(attn_weight, dim=-1)
output = attn_weight @ value

# Effective rank calculation (from LoRA analysis patterns)
U, S, V = torch.linalg.svd(attention_matrix)
cumsum = torch.cumsum(S**2, dim=0) / torch.sum(S**2)
eff_rank = torch.sum(cumsum < 0.99) + 1
```

### Analysis Type
This is an **ANALYSIS experiment**, not a training experiment:
- No model training or fine-tuning
- No gradient computation required
- Inference-only with attention output capture
- Lightweight computational requirements (compared to training)

---

## Risk Mitigation

### Risk 1: High-Rank Structure (r_eff > 256)
- **Severity:** Critical (MUST_WORK gate)
- **Mitigation:** Early diagnostic in Phase 0 pilot
- **Early Warning:** r_eff > 512 at L≥20
- **Fallback:** ABORT conversion approach

### Risk 2: HuggingFace Token Issues
- **Severity:** Medium
- **Mitigation:** Document token setup in environment requirements
- **Fallback:** Use publicly available alternative model

### Risk 3: GPU Memory Overflow
- **Severity:** Medium
- **Mitigation:** Use fp16, clear cache between batches, reduce batch size
- **Fallback:** Reduce sample count to 2K-5K

---

*Generated by Phase 3 Implementation Planning | Based on Phase 2C Experiment Brief*
*Hypothesis h-e1: Low-Rank Structure Existence | Type: EXISTENCE | Gate: MUST_WORK*
