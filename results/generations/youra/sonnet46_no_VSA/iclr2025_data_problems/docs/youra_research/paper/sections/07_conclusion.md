# 7. Conclusion

We began by observing that a practitioner applying CCNet's standard perplexity filter to RedPajama-V2 would retain 86% of Spanish documents but only 16% of English documents — not from any quality difference, but from a calibration artifact introduced by applying a global threshold to locally-calibrated perplexity scores. Having characterized this phenomenon precisely, we can now say what kind of bias it is: a large, structural, language-family divide that is consistent across the full practical range of filtering aggressiveness.

In this work, we addressed the absence of a calibrated baseline for language-group retention disparity under global ccnet_perplexity thresholding by designing a CPU-only measurement methodology on pre-computed RedPajama-V2 quality signal metadata. Our contributions are:

1. **First calibrated V baseline.** Cramér's V = 0.40–0.57 for global k-th percentile thresholding on ccnet_perplexity (n = 208,262, five languages, Holm p ≈ 0 for all k ∈ {10, 20, 30, 40, 50}), establishing the reference measurement against which future correction strategies can be evaluated.

2. **Language family structure.** The retention ordering es > fr > it > en > de is consistent across all five threshold levels, providing quantitative evidence that the disparity tracks CCNet KenLM training corpus differences across language families rather than individual language characteristics.

3. **Prior estimate recalibration.** Literature-derived estimates of V ∈ [0.29, 0.41] underestimate the actual bias by 25–40% (empirical: V = 0.40–0.57). Correction studies sized from CCNet descriptions will be systematically underpowered.

## Future Directions

**From untested alternative explanations:** The Spanish saturation finding (100% retention at k=40) suggests the global threshold at permissive levels may be calibrated almost entirely by the Germanic-language mass. Testing whether this saturation reproduces on the tail partition — or disappears — would clarify whether the effect is composition-driven or structurally universal.

**From unverified assumptions:** The most urgent next step is testing whether per-language k-th percentile calibration (h-m1) reduces ΔV ≥ 0.10 for ≥3 of 5 k values — the primary correction hypothesis. If confirmed, this would establish per-language calibration as a principled default. If ΔV < 0.10, it would suggest that upstream pipeline factors (language ID asymmetries, deduplication differences) contribute to the disparity beyond threshold calibration.

**From scope extensions:** Replicating this measurement on the full 113.3B-document corpus would test whether V = 0.40–0.57 generalizes beyond the head+middle partition sample. Measuring V for other RedPajama-V2 quality signals (e.g., duplicate_line_ratio, punctuation_ratio) would determine whether the language-family bias is specific to ccnet_perplexity or a broader feature of global quality signal thresholding.

The challenge of calibrating multilingual quality filters equitably has been recognized qualitatively for years. This work provides the quantitative foundation needed to evaluate progress: a precise, reproducible V measurement that practitioners and researchers can use as the starting point — and the standard — for multilingual dataset curation going forward.
