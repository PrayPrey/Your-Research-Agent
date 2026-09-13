# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-10T23:00:00
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap1-eviction-vs-compression
- **Gap Title**: Systematic Comparison of Eviction vs Compression Trade-offs
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 17

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 17

**Convergence Reason**: All 6 criteria met; all personas participated with genuine challenge/response

### Key Insights
- Eviction and quantization are not independent; interaction effects may dominate
- Task categories (LongBench 6) may not align with compression-relevant structure
- Attention patterns in early tokens encode task-relevant information
- Pareto frontier is task-dependent, not universal

### Breakthrough Moments
- Exchange 7: Flipping from assuming to discovering compression-relevant task structure via clustering
- Exchange 9: Attention probe (first 100 tokens) as router input to predict optimal compression
- Exchange 13: AUPC (Area Under Pareto Curve) as unified metric replacing single-point accuracy

---

## Final Hypothesis

### Title
Attention-Probe Router for Task-Conditioned KV Cache Compression

### Core Claim
Under the constraint of fixed memory budget and LongBench benchmark, if we characterize KV compression response profiles across eviction and quantization strategies per task, then an attention-probe-based router will select task-appropriate configurations achieving ≥5% AUPC improvement over best single strategy, because early attention patterns encode task structure that correlates with compression tolerance.

### Mechanism
1. Early attention entropy reflects task structure (broad integration vs precise retrieval)
2. High-entropy tasks tolerate eviction better (many tokens contribute equally)
3. Low-entropy tasks tolerate quantization better (few critical tokens need precision)
4. Router uses attention features to predict cluster → optimal config

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | Gap statistic identifies k* > 1 clusters | k* > 1 with gap > SE | k* = 1 |
| P2 | Router achieves ≥5% AUPC improvement | AUPC(router) > 1.05 × AUPC(best-single) | AUPC(router) ≤ AUPC(best-single) |
| P3 | Attention entropy correlates with cluster | ρ > 0.5 | ρ ≤ 0.3 |

---

## Novelty
- **First** systematic task-conditioned Pareto characterization of KV compression
- **First** attention-based compression router using early token features
- Shifts paradigm from "best method" to "best method per task"

---

## Experimental Design

| Component | Value |
|-----------|-------|
| **Dataset** | LongBench (21 tasks, 6 categories) |
| **Model** | Llama-2-7B |
| **Compression Configs** | 6 (eviction 40/80% × quantization FP16/INT8/INT4) |
| **Baselines** | Best-Single, H2O-Default, StreamingLLM-Default, Full-KV |
| **Validation** | 3-fold cross-validation (train on 14, test on 7) |
| **Compute** | ~5 GPU-hours on A100 |

---

## Limitations
- Single model architecture (Llama-2-7B); cross-model generalization is future work
- English-primary benchmark; multilingual generalization untested
- Static strategy selection at inference start; no mid-generation switching
- Attention probe assumes patterns stabilize in first 100 tokens

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | 17 exchanges, all criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | 5% threshold may be aggressive; cross-model untested |

---
