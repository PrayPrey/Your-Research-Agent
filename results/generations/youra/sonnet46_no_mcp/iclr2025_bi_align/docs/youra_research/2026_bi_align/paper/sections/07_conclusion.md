# 7. Conclusion

We began by observing that the verbosity preference of RLHF annotators in HH-RLHF flips sign across annotation rounds — from penalizing longer responses to rewarding them — tracking the stylistic profile of the AI text they were evaluating. Our experiments provide the first computational evidence that this pattern is not random variation but a directional shift specifically aligned with the AI-typicality axis in sentence embedding space.

## Summary

In this work, we addressed the question of whether human preference signals in RLHF annotation are temporally stationary, by proposing the Alignment Asymmetry Index (AAI) and validating its first two components on real RLHF datasets.

Our main contributions are:

1. **Verbosity preference reversal (Δβ_L = +0.080, non-overlapping 95% CI).** We demonstrate that verbosity preference weighting changes direction across annotation strata in HH-RLHF: early annotators penalize verbose responses (β_L = −0.025) while later annotators reward them (β_L = +0.056). This is the first coefficient-resolution measurement of directional stylistic drift in a real RLHF preference dataset, requiring no annotator identity metadata.

2. **Discriminant-valid AI-typicality projection (β_exposure = 0.041, p = 2.05×10⁻⁵; placebo p = 0.48).** The annotation preference gradient in WebGPT is significantly and specifically aligned with the AI-typicality direction in sentence embedding space, confirming that the drift is directional toward AI style rather than arbitrary stylistic variation.

3. **Minimum data requirements for annotation drift research.** Our null results — interaction p = 1.0 (absent disagreement labels), subthreshold effect size (absent worker IDs), and extreme topic imbalance (p = 4×10⁻²⁷⁵) — provide a concrete, actionable specification: confirming individual annotator causal adaptation requires genuine temporal metadata, within-annotator tracking, and per-prompt disagreement labels. This data standard is our most practically actionable contribution for the RLHF community.

## Future Directions

**From untested mechanism links:** Does the verbosity upweighting in later-round HH-RLHF labels propagate to reward model scoring behavior? H-M3 — training identical TRL RewardTrainer models on early vs. late round splits and comparing their style scores on a shared 500-prompt test set — is the direct test. The β_L directional shift (Δ = +0.080) provides the input signal; H-M2's validated coefficient comparison code provides the measurement infrastructure. This experiment requires approximately 4–8 GPU hours and represents the highest-priority follow-on.

**From violated assumptions:** The absence of genuine temporal metadata (A1) and within-annotator tracking (A4) are not fundamental barriers — they are data curation decisions. Purpose-built annotation experiments via Prolific or MTurk with documented multi-session worker IDs (≥ 3 sessions per worker) would enable the within-annotator causal attribution test that distinguishes individual adaptation from cohort composition effects. Similarly, collecting multi-annotator ratings (≥ 5 annotators per prompt) on a subset of HH-RLHF would enable the round × ambiguity interaction test that directly evaluates the automation bias moderation prediction.

**From scope extension:** The AAI measurement framework — coefficient comparison with shared scaler, bootstrap CI non-overlap, AI-typicality geometric projection with placebo control — is directly reusable on any English RLHF preference dataset with temporal structure. Cross-dataset replication on OpenAssistant or Chatbot Arena, where annotation metadata is richer, would establish the generalizability of the verbosity drift finding.

## Closing

RLHF pipelines are built on the assumption that human annotators provide a stable signal of what constitutes a good response. Our findings suggest this assumption deserves empirical scrutiny in any dataset with multi-round annotation structure. The alignment process that is supposed to make AI systems more human may, over annotation rounds, also make human annotators more AI-typical. Measuring this dynamic — with instruments like the AAI — is a necessary step toward annotation pipelines that remain anchored to genuine human values rather than the stylistic artifacts of the systems they are meant to evaluate.
