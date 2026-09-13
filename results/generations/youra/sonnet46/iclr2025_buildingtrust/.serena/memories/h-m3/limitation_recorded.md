# Hypothesis Completion Snapshot: h-m3

**Date:** 2026-03-15T05:00:00Z
**Hypothesis:** h-m3
**Statement:** The dominant alignment-induced logit perturbation mechanism is H1 (monotonic scale distortion): Spearman rank correlation between base and aligned 4-option log-prob vectors is >=0.9, and Brier reliability increase is concentrated in shared-argmax items.
**Final Status:** COMPLETED (LIMITATION_RECORDED)
**Gate Result:** FAIL (SHOULD_WORK)
**Reflection Outcome:** LIMITATION_RECORDED

## Key Findings

- **H1 DEFINITIVELY RULED OUT:** 0/9 Spearman rho >= 0.90. max_rho = 0.8748 (6.9b-dpo).
- **H2 IS DOMINANT MECHANISM:** 8/9 pairs flag H2 (rho < 0.85). Boundary shift, not scale inflation.
- **PPO causes catastrophic argmax redistribution:** 1.4b-ppo rho = -0.3241, 99.7% items change argmax.
- **H3 cleanly ruled out:** TruthfulQA ECE increase < MMLU ECE increase for all alignments.
- **6.9b-DPO nearest to H1:** rho=0.875 — soft DPO at larger scale partially preserves rank order.

## Implications for Future Hypotheses

- h-m4 (ATS correction): ATS should be evaluated against H2-dominated models. Expect different correction efficiency for boundary-shift vs scale-inflation.
- Paper narrative: Alignment calibration degradation is driven by answer-switching (H2), not confidence inflation (H1).
- Research framing shift: "confidence inflation" → "decision boundary restructuring."

## Limitation Note

h-m3 SHOULD_WORK gate FAIL. No self-modification path — data quality high, experiment correct. Pipeline continues to h-m4 with H2 as confirmed dominant mechanism.
