# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Tikitaka Loop
- **Gap ID**: gap-1-benchmark-comparison
- **Gap Title**: Systematic Benchmark Comparison Missing
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 8

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 8

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Reframed benchmark comparison as inductive bias study rather than architecture horse-race
- Property type determines optimal architecture choice due to differing locality requirements
- Effect sizes should be derived from baseline variance for principled thresholds

### Breakthrough Moments
- Dr. Nova's paradigm shift to inductive bias framing
- Prof. Pax's solution to use TrojAI (larger dataset) for backdoor detection task
- Dr. Ally's integration of matched-baseline to isolate equivariance contribution

---

## Final Hypothesis

### Title
Locality Inductive Bias in Permutation-Equivariant Weight Processing

### Core Claim
Under model property prediction tasks on standard benchmarks (TrojAI, ModelZoo), if different permutation-equivariant architectures (DWS, NFT) are applied, then property-type-dependent performance differences emerge, because explicit locality inductive bias (DWS) improves fine-grained pattern detection while global attention (NFT) improves holistic property aggregation.

### Mechanism
DWS encodes spatial weight structure directly in equivariant layer operations, reducing sample complexity for local pattern detection. NFT's full attention must learn locality from data, advantaging global property aggregation but requiring more data for local patterns.

---

## Predictions

| ID | Primary | Statement | Success Criterion |
|----|---------|-----------|-------------------|
| P1 | Yes | DWS outperforms NFT and baseline on TrojAI backdoor detection | DWS AUC > NFT AUC by >1.5σ |
| P2 | Yes | NFT outperforms DWS and baseline on ModelZoo accuracy prediction | NFT RMSE < DWS RMSE by >1.5σ |
| P3 | No | Both equivariant methods outperform MLP baseline on at least one task | At least one method > baseline per task |

---

## Novelty

**Key Innovation**: First systematic comparison of permutation-equivariant architectures (NFT, DWS) on model property prediction with mechanistic grounding in locality inductive bias.

**Differentiation**:
- NFT (Zhou 2024) evaluated on INR tasks; we evaluate on property prediction
- DWS (Navon 2023) evaluated on weight editing; we evaluate on classification/regression
- Prior baselines (Unterthiner 2020) use hand-crafted statistics; we compare learned methods

---

## Experimental Design

**Independent Variables**: Architecture type (MLP-Baseline, NFT, DWS) × Property type (Backdoor, Accuracy)

**Dependent Variables**: 
- Backdoor detection AUC (TrojAI)
- Accuracy prediction RMSE (ModelZoo)

**Baselines**: MLP-Baseline (flattened weights), Weight Statistics (Unterthiner)

**Design**: 3×2 mixed factorial design with matched-parameter controls

---

## Limitations

- Cross-benchmark comparison (TrojAI vs ModelZoo) may introduce model architecture confounds
- Locality mechanism is inferred from architecture design, not directly probed via attention visualization
- Results may not generalize to model architectures not present in the benchmarks

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met after 8 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (mitigations specified) |

---

*Phase 2A Complete | Ready for Phase 2B*
