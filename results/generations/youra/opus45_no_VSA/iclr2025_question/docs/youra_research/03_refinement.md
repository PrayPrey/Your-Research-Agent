# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-09T12:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-2
- **Gap Title**: Lightweight Probe Efficiency vs Accuracy Tradeoff
- **Execution Mode**: UNATTENDED (Recursive Entry v2)
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All convergence criteria met - SPECIFIC claim, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS addressed

### Key Insights
- Output entropy achieves ~0.64 AUROC but linear residualization destroys signal (h-e1 lesson)
- Internal trajectory dynamics may capture processing state beyond output confidence
- Normalizing trajectory variance by H_L controls for output entropy dependence
- CMI + RCI add mechanistic interpretability beyond pure detection

### Breakthrough Moments
- Exchange 5: Dr. Ally introduced Normalized Trajectory Instability (NTI)
- Exchange 9: Prof. Rex proposed Convergence Monotonicity Index (CMI) as geometry-agnostic test
- Exchange 13: Dr. Sage elevated contribution via Representational Competition Index (RCI)

---

## Final Hypothesis

### Title
Cross-Layer Trajectory Instability (CLTI) for Hallucination Detection

### Core Claim
Under single-pass inference on TruthfulQA MC1 (LLaMA-2-7B, layers 24-32), if we compute cross-layer trajectory metrics (NTI, CMI, RCI), then hallucinated responses exhibit higher instability (NTI), lower convergence monotonicity (CMI), and characteristic competition patterns (RCI), because factual retrieval follows stable attractor dynamics while fabrication requires iterative cross-layer constraint satisfaction.

### Mechanism
1. Model generates hidden representations at each layer
2. For factual retrieval: representations converge monotonically toward knowledge-grounded attractor
3. For fabrication: representations must satisfy constraints without grounded knowledge, causing cross-layer reorientation
4. Reorientation manifests as higher entropy variance, non-monotonic similarity, transient alignment with alternative (sometimes correct) answers

---

## Predictions

| ID | Prediction | Success Criterion | Gate |
|----|------------|-------------------|------|
| P1 | NTI achieves AUROC > 0.55 | ≥4/5 CV folds exceed threshold | MUST_WORK |
| P2 | Combined model improves over H_L | ΔAUROC ≥ 0.03, LRT p < 0.05 | SHOULD_WORK |
| P3 | Low-entropy subset discriminates | AUROC > 0.55, 95% CI LB > 0.50 | SHOULD_WORK |
| P4 | KL path length competes fairly | Report head-to-head winner | INFORMATIVE |
| P5 | RCI flip pattern prevalent | ≥30% hallucinations, <10% correct | SHOULD_WORK |

---

## Novelty

**What's New:** Shifts measurement paradigm from output confidence to internal processing dynamics. Unlike semantic entropy (requires sampling), SelfCheckGPT (requires consistency check), or MIND (arbitrary features), CLTI provides single-pass, interpretable trajectory metrics with mechanistic justification.

**Differentiation:**
- vs Semantic Entropy: Single-pass, no sampling
- vs SelfCheckGPT: Uses internal states, no external consistency check
- vs MIND: Interpretable trajectory metrics, not arbitrary features
- vs END: Adds CMI and RCI, normalized trajectory formalization

---

## Experimental Design

**Dataset:** TruthfulQA MC1 (817 questions, binary labels)

**Model:** LLaMA-2-7B (32 layers, 4096 hidden dim)

**Layers:** 24-32 (final 8, where logit-lens is reliable)

**Baselines:**
- Raw mean entropy (H_L): AUROC 0.6426
- P(True) probe: AUROC ~0.57

**Controls:**
- C1: Random orthogonal projection (expect ≤20% AUROC drop)
- C2: Vocabulary permutation (expect AUROC ~0.50)
- C3: Label permutation for RCI (expect flip pattern collapse)
- C4: Length partial correlation (expect p < 0.05 after Bonferroni)
- C5: Layer effect curve (expect unimodal peak layers 20-28)

---

## Limitations

- Single architecture (LLaMA-2-7B) tested initially
- TruthfulQA MC1 is multiple-choice, not free generation
- Interpretability claims (RCI flip) contingent on pattern prevalence ≥30%
- Causal intervention (layer truncation) is exploratory, not gated
- False attractor problem: hallucinations may converge smoothly

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | False attractor, RCI prevalence, KL competition |
| **Mitigation** | Pre-registered head-to-head comparison |

---

## Previous Failure Context

This is a recursive entry (v2) after h-e1 failed across 3 runs:
- Run 1: CERV approach, Cohen's d = -0.035 (needed ≥0.2)
- Run 2: R-ETF approach, AUROC 0.5582 < 0.58 target
- Run 3: Mean entropy alone, AUROC 0.519 < 0.55 threshold

**Key Lesson:** Single-scalar entropy is insufficient. CLTI uses multi-dimensional trajectory features to avoid this failure mode.
