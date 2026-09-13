# Product Requirements Document: H-M2

**Hypothesis:** Token-level representations remain stable across lengths while matrix-level degrades
**Type:** MECHANISM
**Date:** 2026-08-18
**Author:** YouRA Research Pipeline

---

## 1. Executive Summary

This experiment validates that token-level distillation (CAB) produces more robust hidden state representations than matrix-level distillation (MOHAWK) as sequence length increases. We measure hidden state drift between teacher (Phi-1.5) and student (Phi-Mamba) models across multiple sequence lengths within the valid training range (512-2048 tokens).

**Success Criteria:** CAB drift slope < MOHAWK drift slope

---

## 2. Problem Statement

### 2.1 Context
H-M1 validated that Phi-1.5 has a hard 2048 token context limit due to fixed positional embeddings. This establishes the boundary conditions for comparing distillation objectives within the valid training distribution.

### 2.2 Research Question
Does token-level alignment (Q/K→B/C via CAB) produce more length-robust representations than matrix-level alignment (attention map matching via MOHAWK)?

### 2.3 Hypothesis
Token-level representations remain stable across sequence lengths while matrix-level representations degrade. This would manifest as:
- Lower drift slope for CAB vs MOHAWK
- Bounded drift growth for CAB at maximum length

---

## 3. Functional Requirements

### FR-1: Data Loading Pipeline
- Load C4 validation split via HuggingFace streaming
- Filter documents with >= 8192 characters (sufficient for 2048 tokens)
- Sample 500 documents per length condition
- Tokenize with Phi-1.5 tokenizer
- Prepare batches at lengths: 512, 1024, 1536, 2048

### FR-2: Model Loading
- **Teacher:** Load microsoft/phi-1_5 with output_hidden_states=True
- **Student (MOHAWK):** Load goombalab/phi-mamba checkpoint
- **Student (CAB):** Load wph6/CAB checkpoint OR train minimal CAB variant

### FR-3: Hidden State Extraction
- Extract hidden states at layers 8, 12, 16 (middle layers)
- Project student dimensions if different from teacher (2048)
- Compute L2 distance per position, average across batch and sequence

### FR-4: Drift Measurement
- Compute per-length drift for both MOHAWK and CAB
- Store per-layer breakdown
- Compute linear regression slope across lengths

### FR-5: Statistical Analysis
- Calculate drift slopes using scipy.stats.linregress
- Compute 95% confidence intervals
- Validate standard deviation < mean for each condition

### FR-6: Visualization
- **Required:** Drift vs Length line plot (MOHAWK orange, CAB blue)
- **Optional:** Per-layer heatmap, cosine similarity bars, drift distributions

---

## 4. Data Specification

### 4.1 Primary Dataset

| Attribute | Value |
|-----------|-------|
| Name | C4 (Colossal Clean Crawled Corpus) |
| Source | allenai/c4 (HuggingFace) |
| Split | validation |
| Language | en |
| Loading | Streaming (no full download required) |

### 4.2 Sample Configuration

| Length | Samples | Total Tokens |
|--------|---------|--------------|
| 512 | 500 | 256K |
| 1024 | 500 | 512K |
| 1536 | 500 | 768K |
| 2048 | 500 | 1.024M |

**Total:** 2000 samples, ~2.56M tokens processed

### 4.3 Preprocessing
```python
from datasets import load_dataset

dataset = load_dataset("allenai/c4", "en", split="validation", streaming=True)
filtered = dataset.filter(lambda x: len(x["text"]) >= 8192)
samples = list(filtered.take(500))
```

---

## 5. Model Specification

### 5.1 Teacher Model

| Attribute | Value |
|-----------|-------|
| Name | Phi-1.5 |
| Source | microsoft/phi-1_5 |
| Architecture | Decoder-only Transformer |
| Parameters | 1.3B |
| Hidden Dim | 2048 |
| Layers | 24 |
| Context Limit | 2048 tokens |

### 5.2 Student Models

| Variant | Distillation Type | Source | Notes |
|---------|-------------------|--------|-------|
| Phi-Mamba-MOHAWK | Matrix-level | goombalab/phi-mamba | Official, 3B token training |
| Phi-Mamba-CAB | Token-level | wph6/CAB | May need custom training |

---

## 6. Evaluation Metrics

### 6.1 Primary Metrics

| Metric | Formula | Success Threshold |
|--------|---------|-------------------|
| L2 Drift | `torch.norm(h_t - h_s, p=2, dim=-1).mean()` | CAB < MOHAWK per length |
| Drift Slope | `scipy.stats.linregress(lengths, drifts).slope` | CAB slope < MOHAWK slope |

### 6.2 Secondary Metrics

| Metric | Formula | Purpose |
|--------|---------|---------|
| Cosine Similarity | `F.cosine_similarity(h_t, h_s, dim=-1).mean()` | Alternative alignment measure |
| Per-Layer Drift | L2 at layers 8, 12, 16 | Layer-wise robustness |
| Drift Variance | `std(drifts) / mean(drifts)` | Measurement stability |

### 6.3 Gate Condition
**PASS:** `cab_slope < mohawk_slope` AND `cab_drift_max < 2 * cab_drift_min`

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| torch | >=2.0 | Core framework |
| transformers | >=4.35 | Phi-1.5 loading |
| mamba-ssm | >=1.0 | Mamba architecture |
| datasets | >=2.14 | C4 loading |
| scipy | >=1.10 | Linear regression |
| matplotlib | >=3.7 | Visualization |
| numpy | >=1.24 | Numerical ops |

### 7.2 Hardware Requirements
- GPU: 1× A100 (40GB) or equivalent
- RAM: 32GB minimum
- Storage: 10GB for model checkpoints

### 7.3 External References
- MOHAWK Paper: https://arxiv.org/abs/2408.10189
- CAB Paper: https://arxiv.org/abs/2510.19266
- Phi-Mamba Repo: https://github.com/goombalab/phi-mamba
- CAB Repo: https://github.com/wph6/CAB

---

## 8. Non-Functional Requirements

### NFR-1: Performance
- Total runtime < 4 hours on A100
- Memory usage < 35GB peak

### NFR-2: Reproducibility
- Set random seeds for sampling
- Log exact sample indices
- Save intermediate drift values

### NFR-3: Robustness
- Handle dimension mismatches via projection
- Graceful fallback if CAB checkpoint unavailable

---

## 9. Success Criteria

### 9.1 PoC Pass Conditions
1. Code executes without error for both model types
2. `cab_slope < mohawk_slope` (primary gate)
3. Drift measurements statistically meaningful (std < mean)

### 9.2 Expected Outcome
- MOHAWK drift increases more steeply with length (matrix-level captures length-specific patterns)
- CAB drift remains flatter (token-level Q/K alignment generalizes better)

---

## 10. Risk Assessment

| Risk | Mitigation |
|------|------------|
| CAB checkpoint unavailable | Train minimal 500M token variant |
| Dimension mismatch | Use learned projection layer |
| Memory overflow | Reduce batch size, use gradient checkpointing |
| Phi-1.5 extrapolation | Stay within 2048 token limit (validated by H-M1) |

---

*Generated by Phase 3 Implementation Planning*
*Source: 02c_experiment_brief.md*
