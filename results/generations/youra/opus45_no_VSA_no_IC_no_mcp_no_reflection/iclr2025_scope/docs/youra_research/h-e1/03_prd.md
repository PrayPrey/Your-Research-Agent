# Product Requirements Document: h-e1

**Version:** 1.0
**Date:** 2026-08-29
**Author:** Anonymous
**Hypothesis:** h-e1 (EXISTENCE)

---

## Executive Summary

This PRD defines requirements for validating the existence hypothesis: closed-form SSM initialization from Transformer attention weights using Mamba-2 duality equations produces valid, non-divergent parameters enabling stable optimization. This is a Proof-of-Concept (PoC) validation requiring no training—only forward pass stability verification.

### Key Deliverables
- Duality conversion module: BERT attention → SSM parameters
- Stability validation pipeline
- Metrics collection and visualization

---

## Problem Statement

### Background
Transformer-to-SSM conversion typically requires extensive retraining. Mamba-2's structured state-space duality (SSD) theory suggests direct parameter mapping may be possible, but no implementation exists proving this approach produces numerically stable parameters.

### Goal
Demonstrate that SSM parameters derived via duality equations from BERT attention weights produce valid (non-NaN/Inf) outputs with magnitude comparable to original Transformer outputs.

---

## Functional Requirements

### FR-1: BERT Weight Extraction
- **ID:** FR-1
- **Description:** Extract Q, K, V weight matrices from BERT-base-uncased attention layers
- **Input:** Pretrained BERT-base-uncased model from HuggingFace
- **Output:** Weight tensors W_q, W_k, W_v [768, 768] per layer
- **Priority:** P0 (Critical)

### FR-2: Duality Conversion Module
- **ID:** FR-2
- **Description:** Implement `duality_init_ssm_from_attention()` function converting attention weights to SSM parameters
- **Input:** BERT attention layer, d_state parameter
- **Output:** SSM parameters (A, B, C, D, dt)
- **Algorithm:**
  - Compute QK^T, apply SVD
  - A: negative eigenvalues from singular values
  - B: derived from key structure
  - C: derived from value structure
  - D: skip connection (0.1 scaling)
  - dt: discretization step (1/sqrt(d_model))
- **Priority:** P0 (Critical)

### FR-3: Selective Scan Implementation
- **ID:** FR-3
- **Description:** Implement reference selective scan for SSM forward pass
- **Input:** Input tensor x [batch, seq_len, d_model], SSM parameters
- **Output:** Output tensor y [batch, seq_len, d_model]
- **Priority:** P0 (Critical)

### FR-4: Stability Validation
- **ID:** FR-4
- **Description:** Validate SSM outputs for numerical stability
- **Checks:**
  - NaN count in output tensor
  - Inf count in output tensor
  - Magnitude ratio vs Transformer output
- **Priority:** P0 (Critical)

### FR-5: Dataset Preparation
- **ID:** FR-5
- **Description:** Load and preprocess WikiText-103 validation samples
- **Dataset:** wikitext-103-raw-v1 (validation split)
- **Preprocessing:** Tokenize with BERT tokenizer, chunk to 512-2048 tokens
- **Sample Count:** 100 samples (sufficient for existence check)
- **Priority:** P1 (High)

### FR-6: Metrics Collection
- **ID:** FR-6
- **Description:** Compute and store stability metrics per sample
- **Metrics:**
  - nan_count
  - inf_count
  - magnitude_ratio
  - is_stable (boolean)
- **Priority:** P1 (High)

### FR-7: Visualization
- **ID:** FR-7
- **Description:** Generate figures for results
- **Required Figures:**
  - Gate metrics comparison (bar chart)
  - Output distribution histogram
  - Magnitude ratio scatter plot
  - A matrix eigenvalue visualization
- **Output Path:** `{hypothesis_folder}/figures/`
- **Priority:** P1 (High)

---

## Non-Functional Requirements

### NFR-1: Memory Efficiency
- Batch size 8 for 2048-token sequences
- GPU memory < 16GB

### NFR-2: Reproducibility
- Fixed random seed
- Deterministic operations where possible

### NFR-3: Code Quality
- Type hints throughout
- Docstrings for public functions
- Unit tests for duality conversion

---

## Success Criteria

### Gate Condition (MUST_WORK)
| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| NaN/Inf Rate | 0% | All 100 samples |
| Magnitude Ratio | < 10x | All 100 samples |
| Forward Pass Success | 100% | No exceptions |

### Pass Condition
All samples must:
1. Complete forward pass without error
2. Produce no NaN or Inf values
3. Have output magnitude within 10x of Transformer output

---

## Dependencies

### External Libraries
| Library | Version | Purpose |
|---------|---------|---------|
| torch | >= 2.0 | Core computation |
| transformers | >= 4.30 | BERT model loading |
| datasets | >= 2.0 | WikiText-103 loading |
| matplotlib | >= 3.7 | Visualization |

### Models
| Model | Source | Purpose |
|-------|--------|---------|
| bert-base-uncased | HuggingFace | Source attention weights |

### Datasets
| Dataset | Source | Purpose |
|---------|--------|---------|
| WikiText-103 | HuggingFace Datasets | Calibration sequences |

---

## Out of Scope

- Training/optimization (covered in h-m1)
- Multi-layer conversion (single layer for PoC)
- Performance benchmarking (existence only)
- Long-context evaluation (covered in later hypotheses)

---

## Appendix: Phase 2C Traceability

| Phase 2C Item | PRD Coverage |
|---------------|--------------|
| Dataset: WikiText-103 | FR-5 |
| Model: BERT-base-uncased | FR-1 |
| Duality conversion | FR-2 |
| Selective scan | FR-3 |
| Stability metrics | FR-4, FR-6 |
| Visualization | FR-7 |

---

*Generated from Phase 2C experiment brief*
*Next: Architecture Design (Step 3)*
