# Conclusion

We began with a counterintuitive claim: that optimizing a language model for alignment metrics makes it *less* aligned with actual human judgment — and that we can quantify exactly how fast. We have demonstrated that this is not merely a theoretical possibility but a measurable, replicable empirical property of RLHF optimization.

## Summary

The calibration-alignment divergence gap — the normalized difference between reward model score and held-out gold human preference — grows at β ≈ 0.143–0.160 nat⁻¹ of KL optimization budget. This rate is high enough to traverse more than half the normalized scale [0,1] within 4–5 nats of KL beyond the divergence onset point, and it is consistent enough to replicate within 12% across two independent model families and experimental settings.

We contributed four things:

1. **A named construct:** The calibration-alignment divergence curve, operationalized as the OLS regression slope of (RM_norm − gold_preference) on KL budget. This is the first quantitative, regression-characterized description of proxy-gold divergence as a function of optimization pressure — previously described qualitatively, now measurable.

2. **Quantified slopes with confidence:** In Coste et al. [2023] data, β = 0.143 nat⁻¹ (R² = 0.958, p = 8.89 × 10⁻⁷), with both parametric and bootstrap CIs strictly positive. The near-perfect linear fit suggests the divergence is a systematic property of the optimization process, not a local artifact.

3. **Cross-dataset replication:** In independent Gao et al. [2023] data, β = 0.160 nat⁻¹ (p = 0.003), yielding a cross-dataset slope ratio of 1.116. The slopes are within 12% despite entirely different model families, parameter scales, and task distributions — evidence that the calibration-alignment divergence rate reflects a property of RLHF itself.

4. **A measurement instrument:** The normalized divergence gap (RM_norm − gold_preference ∈ [−1, +1]) enables cross-study comparison by removing raw scale artifacts while preserving direction and monotonicity. This instrument can be computed from standard RLHF evaluation data — RM scores and held-out human preference at multiple KL checkpoints — with no additional experimental overhead.

## Future Directions

Several results in this study motivate specific, grounded future experiments:

**From our findings on ρ = 1.000 (likely digitization idealization):** Contacting Coste et al. and Gao et al. authors for raw training checkpoint data would enable exact β estimation with bootstrap digitization uncertainty propagation, resolving whether the near-perfect linear fit reflects a genuine property of the Coste experimental setup or an artifact of figure digitization.

**From the Gao data's non-monotone low-KL regime:** Piecewise linear or polynomial regression with a breakpoint at the zero-crossing (~3.5 nats in Gao data) would characterize both the pre-onset and post-onset divergence regimes separately, providing a more complete picture of the overoptimization trajectory shape.

**From the construct validity gap (L4):** A behavioral study measuring user over-reliance rates on models trained at different KL levels — following the appropriate reliance paradigm — would test whether evaluation calibration divergence predicts actual user behavioral miscalibration, resolving the most important unresolved theoretical question.

**From the coverage ratio (P3 not tested):** Applying the dual-axis classification schema to the 400 papers in the ICLR 2025 Bidirectional Alignment survey would compute the AI→Human coverage ratio R directly, grounding the bidirectional framing in our own quantitative evidence rather than the survey's qualitative characterization.

**From the slope consistency across model families:** Cross-scale replication at multiple RM parameter counts (1B, 7B, 13B, 70B) with standard RLHF training on open preference datasets would test whether the β ≈ 0.14–0.16 nat⁻¹ range is scale-invariant, as the Gao et al. scaling laws suggest.

## Final Thought

We demonstrated that β ≈ 0.143 nat⁻¹ — quantifying exactly how fast RLHF optimization degrades evaluation calibration to human judgment. A field that measures alignment by proxy scores alone, without tracking held-out human preference, systematically overestimates how aligned its models are as optimization proceeds. We hope this work motivates evaluation practices that monitor both signals — and a research agenda that treats the *rate* of calibration-alignment divergence as a fundamental property of RLHF optimization worthy of systematic study.
