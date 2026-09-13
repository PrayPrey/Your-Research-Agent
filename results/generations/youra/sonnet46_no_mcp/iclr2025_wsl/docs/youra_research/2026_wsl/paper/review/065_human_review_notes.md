# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by AI.

**Generated**: 2026-05-05T20:30:00Z
**Rounds Completed**: 2 (R1 + R2)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 2 |
| Style | 4 |
| Clarity | 6 |
| Formatting | 2 |
| **Total** | **14** |

---

## Round 1 Issues

### Grammar
1. Section 5.4, Discussion: "Deep Sets ($\rho = 0.447$) confirms" — LaTeX math mode inconsistency; most of the paper uses plain text notation (ρ = 0.447) but this one instance uses display math. Standardize throughout.
2. Section 6.2: "The negative ρ for high-accuracy models likely reflects a capacity-regime mismatch" — "likely reflects" is correct but the sentence continues with definitive language. Consider "may reflect" for consistency.

### Style
1. Introduction §1 opening: "When a flat MLP encoder is trained to predict neural network accuracy from weights, it faces a problem that grows factorially with network depth" — strong opening but "grows factorially" is a complexity characterization, not strictly true of the problem faced at inference. Reviewers may object. Consider: "it faces a combinatorial challenge."
2. Section 6.4 Broader Impact: "No negative societal impacts are anticipated" — standard boilerplate. ICML 2025 requires genuine consideration, not a dismissal. Suggest 1-2 sentences acknowledging potential dual-use (e.g., model zoos for surveillance models).
3. Abstract: "ten times the minimum meaningful threshold" — "meaningful" is subjective. Consider "ten times the minimum pre-registered threshold" (which it was, per verification_state.yaml).
4. Section 1: "more than atoms in the observable universe" — the 10⁸³ estimate for a 2-hidden-layer width-32 network is an astronomical number but the comparison to atoms (~10⁸⁰) may invite pedantic pushback. Verify the calculation or soften to "an astronomically large number."

### Clarity
1. Section 3.4 sensitivity formula: `sensitivity_score = E[‖f(w) − f(σ(w))‖₂] / E[‖f(w) − f(w')‖₂]` — notation for σ(w) (a permuted weight) is introduced here but σ was previously used as a function in the Deep Sets decomposition in §2.2 (ρ(Σᵢφ(xᵢ))). Use different notation to avoid collision; suggest π(w) for the permuted weight.
2. Section 5.1: "We sample 500 model pairs stratified across 10 accuracy deciles" — this sentence appears in Results but the sampling methodology is described in §3.4. Forward-reference would help: "as described in §3.4."
3. Section 5.4: The disclosure paragraph before Table 2 about the untrained flat MLP is important but quite long. Consider breaking into a shorter inline disclosure + a footnote for the technical detail.
4. Section 6.3 Limitations list: L1–L6 are not numbered in order of severity — L1 is HIGH, L2 is HIGH, L3 is LOW, L4 is MEDIUM, L5 is MEDIUM, L6 is MEDIUM. Consider reordering HIGH → MEDIUM → LOW for reader clarity.
5. Section 5.2: The cross-reference to the trained flat MLP result (ρ=0.1041 from H-M1) vs. the untrained result used in H-M3 (ρ=0.1688) could be made more explicit. A one-sentence note here would help readers not read the disclosure paragraph in §5.4 first.
6. Section 7 Conclusion: "chain of evidence" (replacing "causal chain") — this is an improvement but "chain of evidence" is unusual phrasing in ML papers. Consider "mechanistic evidence chain" or "sequence of supporting evidence."

### Formatting
1. References section: Kofinas et al. citation year — listed as (2024) in the reference list but the paper is actually ICLR 2024 (proceedings from work done in 2023). Verify the correct publication year and venue against the actual paper.
2. Figure captions: Figures 3–8 are described in the Figure Captions section at the end of the paper, which is non-standard for ICML format. ICML expects figure captions to appear inline with figures. When converting to LaTeX/Overleaf (Phase 6.5.1), move captions inline.

---

## Round 2 Issues

### Clarity
1. "885,000×" — actual computed value from paper's own numbers: 0.6490 / 7.34×10⁻⁷ = 884,196. The paper rounds to 885,000 (a ~0.09% overstatement). This is within reasonable rounding but a careful reviewer may check. Options: (a) keep 885,000× with "approximately"; (b) change to ~884,000×; (c) state "over 880,000×" conservatively. Recommend option (a) — add "approximately" before 885,000×.
2. "6.489" (flat MLP mean_random_L2 in Results §5.2) — the exact value from H-M1 is 6.4895, which rounds to 6.490, not 6.489. Consider correcting to 6.490 for consistency with 3-decimal precision used elsewhere.
3. "exceeded by 19×" (orbit proportion threshold) — ratio interpretation: 1.000/0.05 = 20×; margin interpretation (used in H-E1 report): (1.000−0.05)/0.05 = 19×. The paper uses "19×" following H-E1's phrasing, but readers will compute 20×. Suggest changing to "20×" (ratio) for reader clarity, or adding "(i.e., the margin above threshold is 19× the threshold)" to clarify.
4. Bootstrap CI construction method not specified — paper states "bootstrap 95% CI (1,000 resamples)" but does not specify percentile, BCa, or other method. Suggest: "bootstrap 95% CI using the percentile method (1,000 resamples, seed=42)" if percentile method was used.

### Style
1. L3 severity: The paper rates single-seed training as [LOW] severity. The R2 Skeptical Expert notes that ICML community norms typically treat single-seed results as MEDIUM concern for empirical papers. Consider upgrading to [MEDIUM] for realism, or adding a sentence noting why [LOW] is appropriate here (e.g., "the sensitivity probe uses 500 pairs with stratified sampling, providing robustness beyond a single model training run").

### Formatting
1. NFN best checkpoint at epoch 114 of 150 — the paper does not discuss what happens in epochs 114–150 (did validation loss increase? plateau?). Training curve (Figure 2) would show this, but the figure is not yet generated. When generating figures in Phase 6.5.1, ensure Figure 2 clearly marks epoch 114 as the best checkpoint and shows the post-114 behavior.

---

## Recommended Priority

1. **Fix First**: Symbol collision (σ vs. σ in §3.4) — could confuse readers
2. **Fix Second**: 6.489 → 6.490 rounding correction (factual precision)
3. **Consider**: "19×" → "20×" (clarity for readers computing the ratio)
4. **Consider**: "approximately" before 885,000× (precision qualifier)
5. **Optional**: Kofinas citation year verification
6. **Optional**: Broader Impact section expansion for ICML 2025 requirements

---

*Note: These issues do not block paper acceptance but improve overall quality.*
*All FATAL and MAJOR issues have been resolved in 06_paper_r2.md (= 06_paper_final.md).*
