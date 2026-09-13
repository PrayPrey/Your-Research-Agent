# Product Requirements Document: h-m1

**Version:** 1.0
**Date:** 2026-08-30
**Author:** Anonymous
**Hypothesis:** h-m1 (MECHANISM)

---

## Executive Summary

This PRD defines requirements for validating the mechanism hypothesis: duality-preserving initialization provides lower initial reconstruction error than random initialization, demonstrating that Mamba-2 duality equations capture meaningful structure from attention weights.

### Key Deliverables
- Duality conversion module (reuse from h-e1)
- Random initialization baseline
- Reconstruction error measurement pipeline
- Comparative analysis and visualization

---

## Problem Statement

### Background
h-e1 validated that duality conversion produces stable SSM parameters. This hypothesis tests whether those parameters are *meaningful*—capturing attention structure rather than just being numerically valid noise.

### Goal
Demonstrate that SSM parameters derived via duality equations produce outputs closer to the original Transformer attention outputs compared to randomly initialized SSM parameters.

---

## Functional Requirements

### FR-1: BERT Weight Extraction (Reuse h-e1)
- **ID:** FR-1
- **Description:** Extract Q, K, V weight matrices from BERT-base-uncased attention layers
- **Input:** Pretrained BERT-base-uncased model from HuggingFace
- **Output:** Weight tensors W_q, W_k, W_v [768, 768] per layer
- **Reuse:** From h-e1 implementation
- **Priority:** P0 (Critical)

### FR-2: Duality Conversion Module (Reuse h-e1)
- **ID:** FR-2
- **Description:** Convert attention weights to SSM parameters using Mamba-2 SSD duality
- **Input:** BERT attention layer, d_state parameter
- **Output:** SSM parameters (A, B, C, D, dt)
- **Reuse:** From h-e1 implementation
- **Priority:** P0 (Critical)

### FR-3: Random Initialization Baseline
- **ID:** FR-3
- **Description:** Generate randomly initialized SSM parameters with matching shapes
- **Input:** d_model=768, d_state=64
- **Output:** Random SSM parameters (A, B, C, D, dt) with proper initialization scales
- **Initialization:**
  - A: Standard normal scaled by 1/sqrt(d_state)
  - B, C: Xavier uniform
  - D: Zeros
  - dt: Ones * 0.1
- **Priority:** P0 (Critical)

### FR-4: Selective Scan Forward Pass
- **ID:** FR-4
- **Description:** Forward pass through SSM with given parameters
- **Input:** Input tensor x [batch, seq_len, d_model], SSM parameters
- **Output:** Output tensor y [batch, seq_len, d_model]
- **Priority:** P0 (Critical)

### FR-5: Attention Forward Pass (Reference)
- **ID:** FR-5
- **Description:** Get reference output from original BERT attention layer
- **Input:** Input tensor x [batch, seq_len, d_model], BERT attention layer
- **Output:** Attention output tensor [batch, seq_len, d_model]
- **Priority:** P0 (Critical)

### FR-6: Reconstruction Error Computation
- **ID:** FR-6
- **Description:** Compute Frobenius norm between SSM output and attention output
- **Algorithm:** `torch.linalg.matrix_norm(ssm_output - attn_output, ord="fro").mean()`
- **Source:** MOHAWK Stage 1 alignment metric (goombalab/phi-mamba)
- **Priority:** P0 (Critical)

### FR-7: Dataset Preparation
- **ID:** FR-7
- **Description:** Load WikiText-103 validation set for evaluation
- **Dataset:** wikitext-103-raw-v1 (validation split)
- **Preprocessing:** Tokenize with BERT tokenizer, chunk to 512 tokens
- **Sample Count:** Full validation set (min 500 samples)
- **Priority:** P1 (High)

### FR-8: Comparative Evaluation
- **ID:** FR-8
- **Description:** Run both initializations on same inputs and compare errors
- **Protocol:**
  1. For each input sample:
     - Get attention layer output (reference)
     - Get duality-initialized SSM output
     - Get random-initialized SSM output
  2. Compute reconstruction error for both
  3. Store paired results
- **Priority:** P0 (Critical)

### FR-9: Statistical Analysis
- **ID:** FR-9
- **Description:** Compute statistical significance of error difference
- **Metrics:**
  - Mean reconstruction error (duality vs random)
  - Error reduction percentage
  - Paired t-test p-value
  - Effect size (Cohen's d)
- **Priority:** P1 (High)

### FR-10: Visualization
- **ID:** FR-10
- **Description:** Generate comparative visualization figures
- **Required Figures:**
  - Bar chart: mean reconstruction error (duality vs random)
  - Box plot: error distribution comparison
  - Per-layer error comparison (12 BERT layers)
  - Histogram: error distribution overlay
- **Output Path:** `h-m1/figures/`
- **Priority:** P1 (High)

---

## Non-Functional Requirements

### NFR-1: Memory Efficiency
- Batch size 16 for 512-token sequences
- GPU memory < 16GB

### NFR-2: Reproducibility
- Fixed random seed (42)
- Store all random states
- Document random init procedure

### NFR-3: Statistical Validity
- Use full validation set (not subset)
- Report confidence intervals
- Include effect size

---

## Success Criteria

### Gate Condition (MUST_WORK)
| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| Error Direction | duality_error < random_error | Mean across all samples |
| Error Reduction | > 0% | (random - duality) / random |
| Sample Coverage | 100% | All samples complete without error |

### Target Performance
| Metric | Target |
|--------|--------|
| Error Reduction | > 20% |
| P-value | < 0.05 |
| Effect Size | > 0.5 (medium) |

---

## Dependencies

### External Libraries
| Library | Version | Purpose |
|---------|---------|---------|
| torch | >= 2.0 | Core computation |
| transformers | >= 4.30 | BERT model loading |
| datasets | >= 2.0 | WikiText-103 loading |
| matplotlib | >= 3.7 | Visualization |
| scipy | >= 1.10 | Statistical tests |

### Models
| Model | Source | Purpose |
|-------|--------|---------|
| bert-base-uncased | HuggingFace | Source attention weights |

### Datasets
| Dataset | Source | Purpose |
|---------|--------|---------|
| WikiText-103 | HuggingFace Datasets | Evaluation inputs |

### Prerequisites
| Hypothesis | Status | Reused Components |
|------------|--------|-------------------|
| h-e1 | VALIDATED | Duality conversion, BERT extraction, selective scan |

---

## Out of Scope

- Training/optimization (mechanism test only)
- End-to-end perplexity evaluation
- Long-context performance
- Multi-head attention handling (use single head aggregated)

---

## Appendix: Phase 2C Traceability

| Phase 2C Item | PRD Coverage |
|---------------|--------------|
| Dataset: WikiText-103 | FR-7 |
| Model: BERT-base-uncased | FR-1, FR-5 |
| Duality conversion | FR-2 |
| Random baseline | FR-3 |
| Frobenius norm metric | FR-6 |
| Comparative evaluation | FR-8 |
| Statistical analysis | FR-9 |
| Visualization | FR-10 |

---

*Generated from Phase 2C experiment brief*
*Prerequisite: h-e1 VALIDATED*
*Next: Architecture Design (Step 3)*
