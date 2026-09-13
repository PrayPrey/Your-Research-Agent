# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-24T12:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Self-Play)
- **Gap ID**: gap-1
- **Gap Title**: Unified Bidirectional Alignment Measurement Framework
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All 6 personas agreed on alignment mode framework with testable predictions

### Key Insights
- h-m1's negative correlation (r=-0.06) reveals orthogonality, enabling valid 2x2 mode decomposition
- Mode 3 (Misaligned-Confident: high human entropy, low RM variance) represents safety-critical overconfident failures
- Aggregate metrics (RewardBench accuracy) miss mode-specific failure patterns; distribution analysis fills this gap

### Breakthrough Moments
- Exchange 5: Dr. Ally reconciled h-m1's "failed" correlation with new hypothesis framework
- Exchange 7: Dr. Nova proposed the four-mode alignment taxonomy
- Exchange 8: Prof. Vera formalized testable predictions with clear success/falsification criteria

---

## Final Hypothesis

### Title
Alignment Mode Hypothesis (H-AMode)

### Core Claim
Under the scope of Chatbot Arena pairwise battles with standard response pairs, if we classify samples into four alignment modes based on human vote entropy (high/low, median split) crossed with RM ensemble variance (high/low, median split), then the Mode 3 population (Misaligned-Confident) will constitute >10% of samples, because reward models overfit to surface features while humans disagree on subjective criteria the RMs weren't trained on.

### Mechanism
1. Human voters evaluate responses on diverse criteria including subjective preferences
2. When responses differ substantively, some humans prefer A, others prefer B (high entropy)
3. Reward models trained on aggregate preferences collapse subjective distinctions
4. RMs become confident on samples where they lack nuanced training signal (low variance)
5. Result: Overconfident misalignment (high entropy + low variance = Mode 3)

---

## Predictions

**P1 (Primary - Existence):** Mode 3 (Misaligned-Confident) > 10% of samples
- Success: Proportion statistically > 10% (one-sided binomial test, p < 0.05)
- Falsification: Proportion < 5%

**P2 (Mechanism):** Mode 3 response pairs have lower semantic similarity than Mode 1
- Success: Cohen's d > 0.3 for similarity difference
- Falsification: No significant difference or d < 0.1

**P3 (Scope):** Mode 3 proportion higher for subjective prompts vs objective prompts
- Success: Ratio > 1.5 (subjective:objective Mode 3 rate)
- Falsification: Ratio < 1.0 (opposite direction)

---

## Novelty

**Key Innovation:** First work to characterize AI-human alignment through joint entropy-variance mode distributions.

**Differentiation:**
- RewardBench gives aggregate accuracy; we reveal mode-specific failure patterns
- h-m1 sought correlation; we use orthogonality as feature for 2x2 decomposition
- BiAlign framework is taxonomic; we provide computational measurement methodology

---

## Experimental Design

**Dataset:** Chatbot Arena battles (lmsys/chatbot_arena_conversations)

**Models:** RM ensemble (OpenAssistant RM, PairRM, ArmoRM)

**Thresholds:** Median split for entropy/variance (sensitivity analysis with terciles)

**Baselines:**
- Uniform mode distribution (25% each)
- h-m1 correlation analysis (r=-0.06)

---

## Limitations

- Median split thresholds may not generalize across datasets
- Semantic similarity as mechanism proxy may miss some failure modes
- Prompt type classification requires existing metadata or simple heuristics
- Results specific to pairwise preference evaluation settings

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 personas agreed |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

## Previous Failure Context

This hypothesis builds on h-m1 (Run 1) which FAILED with r=-0.06 (wrong direction). Key lessons:
- Human and RM uncertainty are orthogonal constructs (not correlated)
- The orthogonality is now used as a FEATURE enabling 2x2 mode decomposition
- Do NOT assume shared ambiguity; instead characterize the mismatch patterns
