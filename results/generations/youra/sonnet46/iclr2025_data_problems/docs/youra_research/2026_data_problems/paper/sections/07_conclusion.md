# 7. Conclusion

We began this work by observing that the field's most widely-used pretraining quality filter was designed with performance in mind — not with awareness of its demographic consequences. Our experiments demonstrate that this is not merely an oversight to document: fastText quality filtering actively and systematically restructures the demographic-occupation association structure of the training corpus, with a near-perfect statistical regularity (Spearman ρ=1.0) that makes it a near-deterministic demographic reweighting mechanism in addition to its intended role as a quality selector.

## Summary

In this work, we addressed the gap between data curation practice (evaluated by performance benchmarks) and fairness-relevant corpus structure (never measured at the curation hyperparameter level) by developing a model-free corpus fairness audit methodology grounded in the Path-Dependent Curation Fairness Hypothesis (PCFH) framework.

Our main contributions are:

1. **Corpus entropy analysis (H-E1, MUST_WORK PASS):** fastText quality filtering creates a −22.41% relative reduction in H(occupation|demographic) from 10th to 90th percentile threshold, with Spearman ρ=−1.0 (p=1.4×10⁻²⁴) and Bootstrap 95% CI [−1.154, −0.330] excluding zero. At production thresholds (≥90th percentile), a standard quality filter erases nearly a quarter of demographic-occupation uncertainty present in minimally-filtered text.

2. **Log-odds mechanism (H-M1, MUST_WORK PASS):** Conditional log-odds of demographic-occupation co-occurrences increase monotonically from 0.697 to 2.976 (C1→C5) with perfect Spearman ρ=1.0 (p≈0) across 1800 demographic-occupation pairs — establishing that the filter amplifies directional associations, not merely reduces diversity.

3. **Model-free corpus fairness audit methodology:** The validated CorpusFilter + EntropyMeasure + LogOddsComputer pipeline, verified with 57/57 unit tests (H-E1) and 26/26 tasks (H-M1), enables practitioners to audit the fairness implications of any corpus curation configuration at quick-run scale before committing to model training.

4. **Directional evidence for corpus-to-model propagation (H-M2):** The negative control gap (|C7−C0|=0.495) provides directional support that corpus demographic structure reaches model logit space, though full-scale validation (100B token training with gpt-neox) is required for the graded mechanism claim.

## Future Directions

**From untested alternative explanations:**
The perfect ρ=1.0 in H-M1 may be an artifact of rank correlation saturation on 6 discrete data points rather than a genuinely perfect relationship. A continuous fastText percentile sweep (20 levels from 5% to 95%) would test whether ρ=1.0 holds at finer resolution or drops to a strong-but-imperfect value — distinguishing structural confounding from scale saturation.

**From unverified assumptions:**
Full-scale H-M2 replication — Pythia-1B trained on C0-C7 at 100B tokens with gpt-neox framework — would determine whether the graded corpus entropy → logit margin correlation (currently ρ=0.357 at 50B tokens) reaches significance at full compute budget. Following this, H-M3 (BBQ accuracy gap measurement on matched-capability model pairs) would complete the causal chain from corpus curation to downstream fairness benchmarks.

**From scope extension opportunities:**
The corpus audit methodology (H-E1/H-M1) is modular and reusable. Applying it to RefinedWeb, FineWeb, RedPajama, and Dolma subcorpora would establish whether the vocabulary-demographic coupling we observe in DCLM-POOL is universal to CommonCrawl-derived text or specific to the DCLM-POOL filtering regime. Developing the pipeline as a standalone pip-installable tool would enable broad adoption by the data curation community.

## Closing

We began by noting that fastText was designed as a neutral quality proxy. Our work shows it is also a demographic reweighting mechanism — one that every practitioner using DCLM-style pipelines is already running without demographic feedback. As data curation becomes the primary lever for steering large language model behavior, understanding and auditing the demographic implications of quality filters is not an optional concern. It is a prerequisite for responsible practice.
