# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-29
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Tikitaka Loop
- **Gap ID**: Gap-1
- **Gap Title**: No Systematic Head-to-Head Comparison of UQ Methods as Hallucination Detectors
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 9

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 9

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Different UQ methods may detect different hallucination types
- Semantic clustering vs. consistency checking as competing mechanisms
- Even a null result (no difference) would be valuable for practitioners

### Breakthrough Moments
- Exchange 1: Dr. Nova proposes hallucination-type specificity hypothesis
- Exchange 5: Dr. Ally synthesizes testable hypothesis with three predictions
- Exchange 6: Prof. Rex validates design and adds secondary model requirement

---

## Final Hypothesis

### Title
Controlled Comparison of UQ Methods for Hallucination Detection (H-UQ-Compare-v1)

### Core Claim
Under decoder-only LLMs (7-13B parameters), if we compare token entropy, semantic entropy, P(True), and SelfCheckGPT on identical TruthfulQA/HaluEval splits, then:
1. Semantic entropy achieves highest overall AUROC
2. Method rankings vary across hallucination categories
3. Semantic clustering produces more separable score distributions

Because semantic entropy captures meaning-level consistency while token entropy only captures surface-level confidence.

### Mechanism
Semantic entropy clusters semantically equivalent samples via NLI before computing entropy. Token entropy measures surface-level logit confidence. P(True) uses explicit probability prompting. SelfCheckGPT checks factual consistency across samples. Each captures different aspects of uncertainty, leading to category-dependent effectiveness.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|------------------|---------------|
| P1 | Semantic entropy AUROC ≥ 0.70 on TruthfulQA, outperforms token entropy by ≥3 points | AUROC ≥ 0.70 AND gap ≥ 0.03 | AUROC < 0.65 OR gap < 0.02 |
| P2 | Method rankings differ across HaluEval categories | Different #1 in ≥2 of 3 categories | Same #1 in all 3 with >3 point lead |
| P3 | Semantic entropy produces higher KL divergence | KL_semantic > KL_token | KL_token ≥ KL_semantic |

---

## Novelty

**Key Innovation**: First controlled head-to-head comparison of four UQ methods on identical benchmark conditions, testing method-hallucination-type correspondence.

**Differentiation**:
- Kuhn 2023: Compared only to token entropy on their split
- Manakul 2023: Evaluated on WikiBio, not standard benchmarks
- Kadavath 2022: Evaluated on proprietary data

---

## Experimental Design

**Models**: Llama-3-8B-Instruct (primary), Mistral-7B (secondary)

**Datasets**: TruthfulQA mc1, HaluEval (QA/dialogue/summarization)

**Methods**: Token entropy, Semantic entropy, P(True), SelfCheckGPT

**Sample Budget**: 10 generations per query for multi-sample methods

---

## Limitations

- Results may not generalize beyond 7-13B decoder-only models
- Category analysis limited to HaluEval's three subtasks
- Does not test instruction-tuned vs. base model differences
- 10-sample budget may underestimate multi-sample method potential

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

*Phase 2A Complete. Ready for Phase 2B.*
