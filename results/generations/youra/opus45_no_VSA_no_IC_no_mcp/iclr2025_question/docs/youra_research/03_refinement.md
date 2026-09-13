# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Self-Play Loop
- **Gap ID**: gap1-entropy-vs-consistency
- **Gap Title**: No Systematic Comparison of Entropy vs. Consistency Methods on Same Benchmark
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All 6 convergence criteria met: SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS

### Key Insights
- Entropy and consistency may capture different failure modes (epistemic uncertainty vs. generation noise)
- Discordant cases (where methods disagree) are the critical test of orthogonality
- Conditional method selection is more valuable than simple hybrid combination

### Breakthrough Moments
- Prof. Pax identifying discordant cases as the critical feasibility test
- Dr. Nova proposing conditional recommendation based on concordance patterns

---

## Final Hypothesis

### Title
Orthogonal UQ Signals: Entropy vs. Consistency for Hallucination Detection

### Core Claim
Under closed-book QA conditions (TruthfulQA), if we compute both token-level entropy and N-sample consistency for each LLM response, then a hybrid detector combining both signals will outperform either method alone by ≥3 percentage points AUROC, because the methods capture orthogonal failure modes — entropy reflects epistemic uncertainty while consistency reflects generation stability.

### Mechanism
1. Token entropy high → model uncertain about answer content (epistemic uncertainty)
2. Consistency low → model generates semantically different answers across samples (generation noise)
3. Discordant cases reveal complementary signals that improve detection when combined

---

## Predictions

| ID | Primary | Statement | Success Criterion |
|----|---------|-----------|-------------------|
| P1 | Yes | Hybrid AUROC exceeds max(entropy, consistency) by ≥3% | hybrid - max(single) ≥ 0.03 |
| P2 | No | Pearson correlation between entropy and consistency <0.3 | r < 0.3 |
| P3 | No | Discordant cases >15% with differential predictive value | proportion >0.15, AUROC >0.6 |

---

## Novelty

**Key Innovation**: First systematic head-to-head comparison of entropy vs. consistency methods on same factuality benchmark, with orthogonality hypothesis explaining why combination improves detection.

**Differentiation**:
- Kuhn et al. 2023: Evaluated semantic entropy on NLG, not factuality QA
- Manakul et al. 2023: Evaluated consistency on WikiBio, not TruthfulQA

---

## Experimental Design

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Dataset | TruthfulQA (~800 questions) | Ground truth factuality labels |
| Model | LLaMA-2-7B | Accessible logits, public weights |
| Samples | N=5 per question | Sufficient for consistency estimate |
| Entropy | Mean token entropy | Simple, interpretable aggregation |

---

## Limitations

- Single model scale (7B) — may not generalize to 13B/70B
- Single benchmark (TruthfulQA) — may not generalize to other factuality tasks
- Semantic entropy (Kuhn's method) not tested — may outperform token entropy

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

*Phase 2A Complete | 7 exchanges | UNATTENDED mode*
