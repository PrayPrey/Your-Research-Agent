# Conclusion

We opened with a counterintuitive observation: a practitioner applying a standard global 30th-percentile threshold to CCNet perplexity scores in RedPajama-V2 retains 86% of Spanish documents but only 16% of English documents. This is not a quality distinction — it is a calibration artifact. CCNet's per-language KenLM models produce perplexity scores on incomparable scales across language families, and a global threshold applied to this mixture produces a retention divide that tracks language family membership rather than document quality.

We have quantified this divide precisely. Across all five threshold levels tested (k ∈ {10, 20, 30, 40, 50}), Cramér's V ranges from 0.40 to 0.57 — a consistently large effect by any conventional benchmark — with all Holm-Bonferroni-corrected p-values at machine epsilon on 208,262 documents. The retention ordering es > fr > it > en > de is perfectly consistent across all threshold levels, mapping to the Romance-vs.-Germanic language family divide. At k=40, the divide reaches an extreme: Spanish retention is 100% while German retention is 20.7%.

Three contributions emerge from this measurement:

1. **A calibrated baseline.** The V = 0.40–0.57 measurements at each k value provide a precise, reproducible baseline against which any proposed correction — per-language percentile calibration, iso-retention z-score normalization, CCNet-consistent tercile matching — can be evaluated in follow-up experiments.

2. **Structural characterization.** The perfect language-family alignment of the retention ordering, consistent across all five threshold levels, suggests the disparity is structural rather than an artifact of a particular threshold choice. Practitioners using global CCNet percentile thresholds at any common aggressiveness level will encounter this bias.

3. **Prior estimate recalibration.** Prior estimates from CCNet paper descriptions predicted V = 0.29–0.41; empirical measurement yields V = 0.40–0.57, 25–40% larger. Researchers sizing correction studies from these prior estimates will be underpowered.

The natural next step — and the directly motivated follow-on experiment — is to test whether per-language k-th percentile calibration reduces V by ≥ 0.10 across ≥ 3/5 threshold levels (the h-m1 hypothesis). The analysis infrastructure is in place; the baseline is established. The question of whether the calibration artifact can be efficiently corrected within the existing RedPajama-V2 pipeline — without requiring new LM training or corpus-level preprocessing — is immediately testable.

Practitioners who currently use `ccnet_perplexity` with global thresholds in multilingual pretraining data pipelines should be aware that they are introducing a systematic language-family bias whose magnitude (Cramér's V ≈ 0.5 at common threshold levels) is large enough to produce qualitatively unequal language representation in the filtered corpus. The simple fix — computing percentile thresholds per language rather than globally — is computationally trivial. Whether it is statistically sufficient to close the disparity is the open question this work motivates.
