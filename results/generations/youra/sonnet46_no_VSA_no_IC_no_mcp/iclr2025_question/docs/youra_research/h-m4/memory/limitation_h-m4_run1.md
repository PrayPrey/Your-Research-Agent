# Limitation Record: h-m4 (Run 1)

**Date:** 2026-08-25T18:45:00+00:00
**Hypothesis:** h-m4
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

VC AUROC (0.4463) did not fall below TE AUROC (0.4381) or SE AUROC (0.2860), violating
both gate conditions. Llama-2-7B-Chat produced a degenerate overconfident distribution with
only 5 distinct confidence values (95% dominant at ~60%). Despite ECE=0.430 confirming
severe miscalibration, the near-degenerate output retained enough signal from 2 low-confidence
responses to match the near-chance TE baseline. The hypothesis that VC would underperform TE
at 7B scale is FALSIFIED — VC slightly exceeds TE but both are near-chance, not because VC
is calibrated but because TE is also uninformative on this subset.

## Failed Checks

- VC AUROC < TE AUROC (0.4463 ≮ 0.4381, delta=0.0082)
- VC AUROC < SE AUROC (0.4463 ≮ 0.2860, delta=0.1603)
- mechanism_activated: False (only 5 distinct VC values, threshold >5)

## Partial Results

| Metric | Value |
|--------|-------|
| auroc_vc | 0.4463 |
| auroc_te | 0.4381 |
| auroc_se | 0.2860 |
| delta_te | 0.0082 |
| delta_se | 0.1603 |
| ece | 0.4301 |
| distinct_scores | 5 |
| parse_rate | 1.000 |
| n_questions | 98 |

## Experiment Summary

Verbalized Confidence (VC) was tested on Llama-2-7B-Chat TriviaQA dev (N=98, seed=42).
Model produced 5 distinct confidence values (95%, 80%, 100%, 0%, scattered) with 95%
dominant. Parse rate 100% — all responses contained parseable percentage. ECE=0.430
confirms severe overconfidence (stated 80-95% vs actual ~50% accuracy). Both gate
conditions failed: VC AUROC (0.4463) marginally exceeded TE AUROC (0.4381) by 0.008
(within bootstrap CI [0.3436, 0.5433]), and far exceeded SE AUROC (0.286).

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted.

Future research attempts should consider:
1. Larger model scale (13B, 70B) — meta-cognitive calibration may emerge at higher parameter counts
2. RLHF/instruction-tuned variants may produce more diverse confidence distributions
3. Chain-of-thought confidence elicitation (ask model to reason before stating confidence)
4. The near-chance TE baseline (0.438) suggests token entropy is also uninformative on this subset

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0, this limitation informs brainstorming to avoid similar degenerate VC patterns at 7B scale
- **Phase 6 Discussion:** Limitation included in paper's Limitations section

---
*Limitation recorded at: 2026-08-25T18:45:00+00:00*
*For cross-phase reference*
*Note: Written to local file (Serena MCP unavailable in no-MCP ablation session)*
