# Conclusion

We began by asking whether better AI makes us intellectually lazier — a question motivated by the Bidirectional Alignment Asymmetry (BAA) conjecture that improving AI quality should cause measurable behavioral disengagement in human users. Our answer is: for returning WildChat-1M users in 2023–2024, empirically, no. Prompt complexity grows significantly (τ = +0.744, p < 0.001), not declines. But the right comparison group — casual users, non-returning users, users stratified by model version — has not yet been assembled, and the measurement infrastructure to build that comparison fully is not yet publicly available.

## Summary

We contributed four things:

**First**, we established that behavioral proxy signals are computationally detectable in returning-user cohorts from public AI interaction logs. The prompt token count pipeline — WildChat-1M streaming, IP-hash cohort construction, monthly aggregation, Hamed-Rao Mann-Kendall testing — produces a strong, reproducible, autocorrelation-corrected signal (τ = +0.744, consistent with h-e1 replication τ = +0.564). The methodology works.

**Second**, we produced the first large-scale empirical test of the BAA disengagement directional prediction, and it is negative: returning users' prompt complexity does not decline. This constrains the BAA framework: the claim that AI quality improvement causes users to submit shorter, simpler prompts is not supported in publicly available general-purpose AI interaction data for 2023–2024.

**Third**, we documented a binding research infrastructure constraint: the primary LMSYS Chatbot Arena dataset is access-gated, blocking the vote entropy proxy that would provide the most direct cross-dataset BAA test. This is a first-class finding for any future study that relies on temporal LMSYS preference data.

**Fourth**, we characterized the selection bias inherent in returning-user cohort designs and specified the exact comparison experiment needed to resolve it: returning-user vs. non-returning user prompt length trends, matched by month and topic domain, in a difference-in-differences design.

## Future Directions

The most critical next steps follow directly from what the current work could not resolve:

**Disentangle selection bias from behavioral adaptation.** A two-group analysis — users with ≥3 monthly appearances vs. users with exactly 1 monthly appearance, matched by month and topic — would test whether the prompt length trend is driven by cohort self-selection or genuine within-user behavioral change. If the two groups show similar growth, the trend reflects a platform-wide shift. If only returning users grow, self-selection dominates.

**Obtain LMSYS primary access for vote entropy analysis.** The Hamed-Rao Mann-Kendall pipeline for vote Shannon entropy is implemented and validated; only the dataset access credential is missing. Once obtained, the most direct BAA cross-dataset test — declining vote discriminativeness as ELO improves — becomes straightforward to execute.

**Redesign the correction frequency proxy.** Replacing the sparse explicit-correction regex with session-level implicit correction signals — intra-session prompt similarity, session abandonment rate after single-turn interactions, follow-up question rate — would provide a more sensitive test of whether users reduce correction behavior as AI quality improves.

**Extend to post-2024 cohorts.** The GPT-4o and Claude 3.5 era (2024–2025) represents a qualitative jump in AI capability. If BAA disengagement is real, it may be more pronounced in this period than in the 2023–2024 window analyzed here. Extending the same pipeline to later WildChat-1M snapshots with sufficient cohort density would provide a stronger test.

## Closing

The question of whether AI improvement changes human behavior — and in what direction — is not merely academic. If behavioral disengagement is real and undetected, the training signals used to build future AI systems may be systematically degrading. If it is not real, or if it is real only for specific user populations under specific conditions, that is equally important to know. We have established empirically that the question is answerable from existing interaction data, that the answer for returning users in 2023–2024 is not what BAA predicts, and that resolving the remaining ambiguity requires better data access and a more careful cohort design than currently available. We hope this work motivates both.
