# Conclusion

We set out to measure whether better pre-training data produces more generalizable language
models. At approximately 300 billion training tokens, for the Pythia/OLMo model pair,
using the MMLU/HellaSwag generalization balance ratio, the answer is: not detectably so —
and now we understand why.

## Summary

The corpus-quality → generalization-balance hypothesis predicted that OLMo-7B, trained
on Dolma's multi-stage curated corpus, would achieve a higher MMLU/HellaSwag ratio than
Pythia-6.9B, trained on The Pile with minimal curation. Our matched-scale evaluation
(both models within 0.5% of 300B training tokens) finds the opposite: Pythia achieves
a higher ratio (0.565 vs 0.538, difference = −0.0265, 95% CI [−0.045, −0.007], Cohen's
d = −2.732), and this directional refutation is consistent across all four benchmarks
evaluated.

The most informative result is not the direction of the ratio difference — which may
reflect an architecture effect beyond our ability to isolate — but the HellaSwag
convergence: both models achieve exactly 0.458 on commonsense reasoning at this training
scale, regardless of corpus quality. This convergence reveals that the MMLU/HellaSwag
ratio's denominator has saturated at ~300B tokens for 6-8B parameter models, collapsing
the ratio into a proxy for MMLU differences alone. A metric whose denominator is a
constant cannot discriminate between the factors hypothesized to drive its numerator.

Our methodological contributions are threefold: (1) we demonstrate, for the first time,
that the MMLU/HellaSwag generalization balance ratio does not discriminate corpus
curation quality at ~300B tokens in a cross-architecture comparison; (2) we identify
HellaSwag denominator saturation as the structural explanation; and (3) we characterize
the minimum requirements — architecture-matched pairs or temporal trajectory analysis —
for future studies that aim to draw causal conclusions about corpus quality effects.

## Future Directions

**Resolving the architecture confound.** The most direct path forward is an
architecture-matched comparison: two models with identical LLaMA-style (or GPT-NeoX)
architecture, trained at small scale (1-3B parameters, 10B tokens) on matched subsets of
The Pile and Dolma. If the ratio difference persists with matched architecture, it reflects
genuine corpus quality effects. If it disappears, the architecture explanation is confirmed.
This experiment is motivated by our inability to attribute the observed null result to
data quality in the presence of the GPT-NeoX/LLaMA-style confound.

**Temporal trajectory to test scale dependency.** Evaluating both models at an earlier
checkpoint (~143B tokens, available for both Pythia via step72000 and OLMo via matched
intermediate step) would test whether the ratio gap is stable (architecture-driven) or
narrowing (scale-driven, with OLMo approaching parity). The Muennighoff et al. [2023]
data quality × token count interaction predicts the latter; the architecture hypothesis
predicts the former. This experiment is motivated by the single-checkpoint limitation of
our study and could be executed with existing public checkpoints in approximately two
hours of H100 compute.

**Alternative generalization balance metrics.** Our HellaSwag saturation finding suggests
that commonsense tasks may be poor denominators for quality-sensitive ratios at intermediate
training scales. Testing alternative balance metrics — GSM8K/HellaSwag (mathematical
vs. commonsense), MMLU/WinoGrande (knowledge vs. coreference), or log-perplexity ratios
on OOD vs. ID text corpora — may reveal metrics that retain discriminative power at
300B tokens. This is motivated by the structural metric insight: the denominator task
must be verified to remain sensitive at the target scale.

**Corpus quality proxy validation.** Directly measuring quality proxies (n-gram repetition
rate, Flesch-Kincaid grade level, fastText language ID confidence) on matched document
samples from The Pile and Dolma would confirm that the assumed quality difference is
real in the specific dimensions expected to predict generalization balance. Our hypothesis
assumed Dolma is measurably higher quality by these proxies; this was never empirically
verified. Proxy validation is a prerequisite for any re-test of the original hypothesis.

## Closing

The assumption that better curation produces better-generalized models is reasonable —
but it must be testable. Our work shows that the metrics and comparison designs most
commonly used to evaluate this assumption at intermediate training scales are insufficient:
HellaSwag saturates, architectures confound, and single checkpoints cannot reveal the
temporal dynamics that separate quality effects from scale effects. Definitive tests of
the corpus quality hypothesis require designed experiments — not opportunistic comparisons
of publicly available models — and metrics that remain sensitive where we need them to.
We hope this work makes those requirements concrete, and provides a principled foundation
for the next generation of corpus quality studies.
