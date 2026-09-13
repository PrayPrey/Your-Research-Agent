# Abstract

The intuition that better pre-training data produces more generalizable language models
drives substantial investment in corpus curation — but this assumption has rarely been
tested under controlled conditions. We evaluate OLMo-7B (Dolma, multi-stage curation)
and Pythia-6.9B (The Pile, minimal curation) at matched training scale (~300B tokens),
specifically testing whether the curated-corpus model achieves a higher MMLU/HellaSwag
generalization balance ratio. Contrary to the hypothesis, Pythia achieves the higher ratio
(0.565 vs. 0.538) — a large, statistically robust reversal (95% CI entirely against
OLMo). The most informative finding is structural: both models converge to identical
HellaSwag commonsense scores at this training scale, collapsing the ratio into a proxy
for MMLU differences that are themselves architecture-confounded. This reveals that the
MMLU/HellaSwag metric loses discriminative power when its denominator saturates — a
condition that holds for 6-8B models at ~300B tokens. We characterize the minimum
requirements for future corpus quality studies: architecture-matched designs or temporal
trajectory analysis to bound architecture confounds, and denominator-sensitivity
verification before using ratio metrics as quality proxies.
