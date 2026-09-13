# Product Requirements Document: H-M1

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis:** H-M1 - Phi-1.5 attention exhibits extrapolation artifacts at 16K-32K sequence lengths
**Type:** MECHANISM (Causal Analysis)
**Prerequisite:** H-E1 (VALIDATED - Unified framework operational)

---

## Executive Summary

Analyze Phi-1.5 attention entropy and sparsity across sequence lengths (2K, 4K, 8K, 16K, 32K) to quantify extrapolation artifacts beyond the 2048-token training length. This experiment validates the mechanistic premise that attention degrades at longer sequences, motivating the length-dependent distillation approach.

---

## Problem Statement

Phi-1.5 was trained on 2048-token sequences. When processing longer sequences, attention patterns may become diffuse (higher entropy) and less structured (lower top-k sparsity). Quantifying this degradation establishes the empirical foundation for length-dependent distillation objectives.

**Gate Condition (MUST_WORK):** Attention entropy must increase >20% from 2K to 16K. If attention remains structured at 32K, the length extrapolation premise is weakened.

---

## Functional Requirements

### FR-1: Dataset Pipeline
- **FR-1.1:** Stream C4 validation split (`allenai/c4`, `en`, `validation`)
- **FR-1.2:** Filter for documents with ≥32K tokens (minimum 32768 tokens)
- **FR-1.3:** Sample 500 documents for statistical significance
- **FR-1.4:** Truncate each document to target lengths: 2048, 4096, 8192, 16384, 32768

### FR-2: Model Loading
- **FR-2.1:** Load Phi-1.5 (`microsoft/phi-1_5`) with `output_attentions=True`
- **FR-2.2:** Use float16 precision for memory efficiency
- **FR-2.3:** Use device_map="auto" for GPU allocation
- **FR-2.4:** Enable trust_remote_code=True

### FR-3: Attention Extraction
- **FR-3.1:** Extract attention weights from middle layers (8, 12, 16 of 24)
- **FR-3.2:** Attention tensor shape: (batch, heads, seq_len, seq_len)
- **FR-3.3:** Verify attention is normalized (sum to 1.0 per query position)
- **FR-3.4:** Handle memory constraints for 32K sequences (~8GB VRAM)

### FR-4: Entropy Computation
- **FR-4.1:** Compute entropy: H = -sum(p * log(p)) with clamping at 1e-10
- **FR-4.2:** Compute per-query-position entropy, then mean per layer
- **FR-4.3:** Aggregate across heads and positions
- **FR-4.4:** Record mean and std entropy per (length, layer) combination

### FR-5: Sparsity Computation
- **FR-5.1:** Compute top-k sparsity (k=32): fraction of attention in top-32 positions
- **FR-5.2:** Higher sparsity = more focused attention
- **FR-5.3:** Record sparsity statistics per (length, layer) combination

### FR-6: Statistical Analysis
- **FR-6.1:** Calculate entropy change: (entropy_16k - entropy_2k) / entropy_2k
- **FR-6.2:** Calculate entropy trend across all 5 lengths
- **FR-6.3:** Identify inflection point (second derivative of entropy vs log(length))
- **FR-6.4:** Compute confidence intervals (95% CI from 500 samples)

### FR-7: Visualization
- **FR-7.1:** Gate metrics bar chart: entropy at 2K vs 16K vs 32K
- **FR-7.2:** Entropy vs length line plot (log-scale x-axis)
- **FR-7.3:** Layer-wise entropy heatmap (layers × lengths)
- **FR-7.4:** Sparsity distribution box plots per length
- **FR-7.5:** Save all figures to `{hypothesis_folder}/figures/`

---

## Non-Functional Requirements

### NFR-1: Performance
- Complete analysis of 500 docs × 5 lengths in <3 hours on single GPU
- Memory usage must fit in 16GB VRAM (float16, single sequence)

### NFR-2: Reproducibility
- Fixed random seed (42) for document sampling
- Deterministic document ordering

### NFR-3: Numerical Stability
- Clamp attention values at 1e-10 before log computation
- Verify no NaN/Inf in entropy outputs

---

## Success Criteria

| Criterion | Target | Validation |
|-----------|--------|------------|
| **SC-1:** Code runs without error | 0 exceptions | Analysis completes |
| **SC-2:** Entropy increase 2K→16K | >20% | Gate metric |
| **SC-3:** Entropy trend | Increasing with length | Visual inspection |
| **SC-4:** Sparsity decrease | Sparsity_32K < Sparsity_2K | Sparsity comparison |
| **SC-5:** Sufficient samples | 500 documents | Sample count |

**PASS Condition:** SC-1 AND SC-2 AND SC-3
**FAIL Action:** Reduce max experiment length to 16K, or document as negative finding

---

## Data Specification

### Dataset
- **Source:** HuggingFace Datasets - `allenai/c4`
- **Config:** `en`
- **Split:** `validation` (streaming)
- **Filter:** Documents with ≥32768 tokens
- **Sample Size:** 500 documents (statistically meaningful)
- **Tokenizer:** `microsoft/phi-1_5`

### Target Lengths
| Length | Tokens | Relative to Training |
|--------|--------|---------------------|
| 2K | 2048 | 1.0× (training length) |
| 4K | 4096 | 2.0× |
| 8K | 8192 | 4.0× |
| 16K | 16384 | 8.0× |
| 32K | 32768 | 16.0× |

---

## Dependencies

### External Packages
```
torch>=2.1.0
transformers>=4.36.0
datasets>=2.14.0
matplotlib>=3.7.0
seaborn>=0.12.0
numpy>=1.24.0
tqdm>=4.65.0
```

### Model Access
- HuggingFace: `microsoft/phi-1_5` (public, trust_remote_code required)

### External Code References
- InfoScale (HT-NEKO/InfoScale) - entropy computation methodology
- RoPE Extensions Analysis (ACL 2025) - attention entropy correlation

---

## Out of Scope

- Training or fine-tuning (analysis only)
- Early/late layer analysis (focus on middle layers 8, 12, 16)
- Cross-model comparison (Phi-1.5 only)
- Causal interventions on attention

---

## Phase 2C Completeness Check

| Item | Status |
|------|--------|
| Dataset (C4 validation) | ✅ FR-1 |
| Model (Phi-1.5) | ✅ FR-2 |
| Attention extraction | ✅ FR-3 |
| Entropy computation | ✅ FR-4 |
| Sparsity computation | ✅ FR-5 |
| Statistical analysis | ✅ FR-6 |
| Visualization | ✅ FR-7 |
| Gate condition | ✅ SC-2 (>20% entropy increase) |

---

*Generated for Phase 3 Implementation Planning*
