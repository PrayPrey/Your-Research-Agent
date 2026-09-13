# Human Review Notes — Phase 6.5 Adversarial Review

**Date:** 2026-08-22  
**Round:** 1  
**Paper:** "Specification-Aligned Repair for EvalPlus Semantic Failures: Data Infrastructure and Pre-Registered Design"  
**Status:** MINOR issues collected for human review; NOT auto-fixed

---

## Collected MINOR Issues

### Clarity

**M-minor-1 [clarity]:** Abstract states "4/4 conditions, 5/5 tests pass" — the relationship between "4 conditions" (C1-C4, existence verification conditions) and "5 tests" (pytest test suite) is not explained in the abstract. A reader unfamiliar with the paper's two-layer verification structure cannot parse why these are different numbers. Recommend a brief parenthetical or reordering so each number's referent is clear on first read.

**M-minor-4 [clarity]:** Section 5.5 states "expected scenario (25% fix rate under C, 10% under B): ~24 discordant pairs, McNemar power ~80%." The derivation of ~24 discordant pairs from these fix rates is not shown. At n=128, discordant pairs depend on the overlap between which tasks C fixes and which B fixes, not just the marginal rates. Recommend adding a brief power analysis note or citation (e.g., G*Power reference) showing the derivation.

**M-minor-5 [clarity]:** Section 4.1 states "Figure 1 shows the failure distribution" but Figure 1 is never described inline. Readers of a text-only version (common in reviewing) receive no information about what the figure shows. Recommend one sentence describing the key takeaway from Figure 1 immediately after the reference.

### Style

**M-minor-2 [style]:** Introduction paragraph 5 uses "convergent motivation" — slightly jargon-heavy for a general ML audience. Consider replacing with "converging results" or "converging empirical support."

**M-minor-7 [style/formatting]:** The Appendix statistics block (YAML format) is unconventional for ICML format and contains pipeline metadata rather than scientific content. Consider removing from the paper body and moving to supplementary materials or an internal pipeline document.

### Grammar

**M-minor-6 [grammar]:** Introduction: "asking it to 'please try again' without explaining *what* went wrong changes almost nothing" — Note: this was revised in Round 1 to "provides almost no repair signal." If the revised phrasing is accepted, this issue is resolved. If the original phrasing is preferred, consider "yields almost no improvement" for active voice.

### Formatting

**M-minor-3 [formatting]:** Section 3.3 Table column "API Calls" shows value "0" for Condition A. This is potentially confusing — it could mean zero total calls or zero new calls. Recommend clarifying to "0 new API calls (existing data)" to distinguish from the 128 new calls in Conditions B and C.

---

## Action Required

These issues are collected for human judgment. None were auto-fixed in Round 1. The revision agent recommends human review before any venue submission.

---

## Round 2 Issues

**Date:** 2026-08-22
**Round:** 2

### Clarity

**R2-minor-1 [clarity]:** Section 5.5 — "~24 discordant pairs" derivation not shown; overlap assumption unstated. The number of discordant pairs depends on which tasks C fixes vs. which B fixes, not just the marginal fix rates (25% under C, 10% under B). Suggest adding: "assuming ~50% overlap in fixed tasks between B and C." A brief power analysis note or G*Power citation showing the derivation would strengthen the claim.

**R2-minor-2 [clarity]:** Section 6.2 — single seed (seed=42) not listed as an explicit limitation under the "Single model, single temperature" bullet. Seed choice affects stochasticity and reproducibility claims. Suggest adding "single random seed (seed=42)" to that bullet so the limitation is fully stated.

**R2-minor-3 [clarity]:** Pre-registration caveat missing — the paper states predictions are pre-registered but no third-party registry (OSF, AsPredicted, or equivalent) is cited. The current framing relies entirely on the paper's own claim of pre-registration. A footnote acknowledging that no external registry was used (or citing one if registration was completed) would strengthen credibility and align with open-science norms.
