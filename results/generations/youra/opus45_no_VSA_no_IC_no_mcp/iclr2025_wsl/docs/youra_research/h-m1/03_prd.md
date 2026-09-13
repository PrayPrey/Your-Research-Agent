# Product Requirements Document: h-m1

**Hypothesis:** Architecture encodes different inductive biases: DWS uses equivariant layers preserving weight locality; NFT flattens to tokens with full attention.

**Date:** 2026-08-28
**Type:** MECHANISM
**Prerequisites:** h-e1 (VALIDATED)

---

## Executive Summary

This experiment validates the mechanistic hypothesis that DWS and NFT architectures encode fundamentally different inductive biases during training. DWS uses equivariant layers that preserve weight locality, while NFT flattens weights to tokens with full attention. We measure these differences through gradient flow patterns and weight update distributions during training on TrojAI backdoor detection.

---

## Problem Statement

Building on h-e1 (which confirmed distinct processing patterns exist), h-m1 investigates the *mechanism* behind these differences: how gradient flow and weight updates differ between architectures during training.

---

## Functional Requirements

### FR-1: Data Preparation
- **FR-1.1:** Download TrojAI Round 10 models (1000+ training, 200 validation, 500 test)
- **FR-1.2:** Extract weight tensors from each layer
- **FR-1.3:** Normalize weight values per-layer
- **FR-1.4:** Create DWS-format (structured tensors) and NFT-format (tokenized) representations

### FR-2: Model Implementation
- **FR-2.1:** Implement MLP Baseline (flattened weights → [512, 256, 128] → binary output)
- **FR-2.2:** Implement DWS architecture with equivariant layers
- **FR-2.3:** Implement NFT architecture with transformer encoder on tokenized weights
- **FR-2.4:** Reuse h-e1 validated implementations where applicable

### FR-3: Training Dynamics Tracking
- **FR-3.1:** Track gradient norms per layer every epoch
- **FR-3.2:** Snapshot weights every 10 epochs
- **FR-3.3:** For NFT: Record attention patterns each epoch
- **FR-3.4:** For DWS: Compute locality score of weight updates

### FR-4: Evaluation Metrics
- **FR-4.1:** Compute gradient norm distribution (Wasserstein distance DWS vs NFT)
- **FR-4.2:** Compute weight update coefficient of variation across layers
- **FR-4.3:** Track DWS locality score: std(layer_updates) / mean(layer_updates)
- **FR-4.4:** Track NFT attention entropy evolution over training

### FR-5: Visualization
- **FR-5.1:** Generate gradient norm heatmap (per-layer over epochs)
- **FR-5.2:** Generate weight update pattern plot (locality score evolution)
- **FR-5.3:** Generate attention entropy curve for NFT
- **FR-5.4:** Generate layer-wise update distribution box plots

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- 3 random seeds for statistical comparison
- Fixed training protocol: AdamW, lr=1e-4, batch=32, 100 epochs

### NFR-2: Performance
- Training completes within reasonable time on single GPU
- Memory efficient weight storage for 1000+ models

### NFR-3: Code Quality
- Extend h-e1 validated codebase
- Type hints and docstrings for key functions

---

## Success Criteria

1. DWS shows different gradient flow pattern than NFT (Wasserstein distance > 0.1)
2. DWS weight updates more localized (higher CoV across layers)
3. NFT attention entropy increases over training (becomes more distributed)
4. Architecture-specific signatures detectable within first 20 epochs

**Gate:** MUST_WORK - If fails, PIVOT to alternative mechanism explanation

---

## Dependencies

- PyTorch 2.0+
- scipy.stats (Wasserstein distance)
- matplotlib/seaborn (visualization)
- h-e1 validated code (DWS/NFT implementations)
- TrojAI API access

---

## Data Specification

| Dataset | Source | Size | Format |
|---------|--------|------|--------|
| TrojAI Round 10 | trojai.nist.gov | 1700+ models | CNN weights |

---

## Evaluation Protocol

1. Train DWS, NFT, MLP on TrojAI for 100 epochs
2. Track gradient/weight metrics every epoch
3. Compare distributions using statistical tests
4. Generate figures for paper
5. Report PASS if all 4 success criteria met

---

*Generated for YouRA Phase 3 Implementation Planning*
