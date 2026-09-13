# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-03-28T09:52:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Gate Type:** MUST_WORK
**Failure Type:** MUST_WORK_FAIL

## Hypothesis Statement

PD-3 embedding dispersion achieves Spearman correlation ρ ≥ 0.30 with semantic entropy at N=20 responses on TruthfulQA, with bootstrap 95% CI lower bound > 0.15.

## Performance Gap

| Metric | Observed | Threshold | Status |
|--------|----------|-----------|--------|
| Spearman ρ | -0.0315 | ≥ 0.30 | **FAIL** |
| CI Lower Bound | -0.0974 | > 0.15 | **FAIL** |
| Shuffle Test |ρ| | 0.0386 | < 0.10 | PASS |
| p-value | 0.368 | < 0.05 | Not significant |

## Root Cause Analysis

- PD-3 measures embedding space geometry (geometric spread of response embeddings)
- Semantic Entropy measures semantic equivalence clustering via NLI (discrete grouping by meaning)
- These fundamentally different mechanisms produce uncorrelated outputs
- General-purpose embeddings (all-mpnet-base-v2) do not capture semantic equivalence
- The correlation is essentially zero (ρ = -0.0315), not just weak

## Lessons Learned

1. General-purpose sentence embeddings do NOT serve as a proxy for semantic entropy
2. Embedding dispersion and semantic clustering measure orthogonal properties
3. Need NLI-trained or task-specific embeddings if attempting SE proxy
4. The continuous embedding geometry does NOT capture what NLI-based clustering measures
5. This is a fundamental hypothesis flaw, not an implementation or parameter tuning issue

## What NOT To Do in Future Attempts

- Do NOT retry with different general-purpose embedding models (same fundamental issue)
- Do NOT assume embedding distance captures semantic meaning equivalence
- Do NOT expect parameter tuning to fix a fundamentally flawed hypothesis

## What Showed Promise

- The experiment execution was flawless (all mechanism checks passed)
- Both PD-3 and SE metrics showed valid ranges with positive variance
- The experimental framework and code can be reused for alternative approaches

## Pivot Action

PIVOT to alternative approaches:
1. Use NLI-trained embeddings instead of general-purpose embeddings
2. Consider intermediate approaches between pure embedding distance and full NLI clustering
3. Explore whether fine-tuning embeddings on NLI data improves correlation
4. Investigate alternative distance metrics beyond cosine distance

## Configuration Used

| Parameter | Value |
|-----------|-------|
| Dataset | TruthfulQA (817 questions) |
| LLM Model | Mistral-7B-v0.1 |
| Embedding Model | all-mpnet-base-v2 |
| NLI Model | DeBERTa-v3-large-mnli |
| N Responses | 20 |
| Temperature | 1.0 |
| Bootstrap Samples | 10,000 |
| Runtime | 135 minutes |

## Routing Decision

**Route to:** Phase 0 (Brainstorming)
**Reason:** MUST_WORK gate failure with essentially zero correlation indicates fundamental hypothesis flaw requiring completely new approach, not modification of existing hypothesis.

---
*For cross-phase reference*
*Written at: 2026-03-28T09:52:00Z*
