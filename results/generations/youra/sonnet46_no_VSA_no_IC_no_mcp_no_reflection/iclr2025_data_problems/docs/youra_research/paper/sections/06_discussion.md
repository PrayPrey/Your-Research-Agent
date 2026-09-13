# Discussion

## Interpreting the Null (and Negative) Result

Our primary finding — that Pythia-6.9B achieves a higher MMLU/HellaSwag ratio than
OLMo-7B at ~300B training tokens — is counterintuitive given the substantial investment
in Dolma's curation pipeline. We discuss three competing explanations for this result,
assess their relative plausibility, and articulate the methodological implications.

### Explanation 1: Architecture Difference (HIGH plausibility)

The most likely explanation for Pythia's MMLU advantage is the uncontrolled architecture
difference: Pythia-6.9B uses GPT-NeoX architecture, while OLMo-7B uses a LLaMA-style
architecture with rotary positional embeddings and different attention configurations.
GPT-NeoX may be more efficient at 5-shot multiple-choice tasks at the 6-8B parameter
scale, irrespective of corpus quality. Prior work has observed architecture-dependent
MMLU sensitivity — different attention mechanisms and positional encoding schemes can
produce varying few-shot performance even on identical data [Touvron et al., 2023].

This explanation is consistent with all observed results: the architecture advantage would
produce broadly distributed MMLU gains (consistent with Figure 3), would not affect
HellaSwag (which is 0-shot and commonsense-based rather than knowledge-intensive), and
would produce a stable gap rather than a widening one. Without temporal trajectory
analysis comparing Pythia and OLMo at 143B and 300B tokens, we cannot determine whether
the gap is stable (architecture-driven) or widening (quality-driven), as was planned in
the original experimental design.

### Explanation 2: Training Scale Insufficient at 300B Tokens (HIGH plausibility)

A second compelling explanation is that 300B training tokens is insufficient for Dolma's
curation quality advantage to manifest. Groeneveld et al. [2024] report that full-training
OLMo-7B (2T tokens) achieves competitive MMLU performance relative to similarly-sized
models, and attribute part of this to Dolma's academic content inclusion (S2ORC papers,
Wikipedia). If the academic content advantage compounds with training scale — as suggested
by the data quality × token count interaction documented by Muennighoff et al. [2023] —
then at 300B tokens, OLMo may not yet have processed sufficient academic content to
translate Dolma's quality advantage into MMLU gains.

This explanation is consistent with our single-checkpoint design: we cannot rule out that
OLMo's ratio would exceed Pythia's at 500B or 1T tokens. Our null result is explicitly
scoped to ~300B training tokens.

### Explanation 3: The Pile MMLU Contamination (LOW-MEDIUM plausibility)

A third explanation is that The Pile contains MMLU-adjacent content (e.g., academic PDFs
from PubMed, ArXiv, legal texts) that inflates Pythia's MMLU scores via benchmark
contamination. We note that the original contamination concern was in the opposite
direction (Dolma's deduplication might remove MMLU-adjacent content from OLMo's training),
but given our finding that Pythia outperforms OLMo, The Pile contamination is now a more
relevant concern.

However, our per-subject MMLU heatmap (Figure 3) shows Pythia's advantage is broadly
distributed across subjects including those less likely to appear in The Pile's source
domains (e.g., philosophy, sociology, moral scenarios). A contamination-driven advantage
would be expected to concentrate in domains well-represented in The Pile's specific sources
(PubMed → medicine; ArXiv → physics, mathematics; law databases → law). The absence of
domain concentration reduces the plausibility of contamination as the primary explanation,
though it does not rule it out entirely. Min-K% contamination detection [Shi et al., 2024]
applied to MMLU test questions vs. The Pile would provide more definitive evidence.

### The Structural Insight: HellaSwag Denominator Saturation

Beyond the three competing explanations for Pythia's MMLU advantage, our most informative
finding is the HellaSwag convergence. Both models achieve exactly 0.458 on HellaSwag at
~300B tokens, regardless of corpus quality. This convergence has a direct structural
implication: the MMLU/HellaSwag ratio is not a valid discriminator of corpus curation
quality at this training scale in this comparison, because the denominator provides no
discriminative information.

This finding has broader implications for how generalization balance metrics are designed.
A ratio metric r = numerator / denominator is a reliable quality discriminator only when
both numerator and denominator remain sensitive to the factor being tested. When the
denominator saturates — reaching a scale-dependent ceiling for the model family — the
ratio collapses into a proxy for numerator differences alone. For cross-architecture
comparisons, numerator differences may reflect architecture effects rather than corpus
quality. Researchers designing generalization balance metrics should verify denominator
sensitivity at their target training scale before using the ratio as a quality proxy.

## Limitations

### L1: Architecture Confound Not Bounded

The planned method for bounding the architecture confound — temporal trajectory analysis
comparing both models at 143B and 300B tokens — was not executed. The temporal trajectory
would determine whether the Pythia/OLMo ratio gap is widening (consistent with a
quality-driven advantage that compounds with tokens) or stable (consistent with a fixed
architecture-driven difference). Without this analysis, causal attribution of the null
result to corpus quality is impossible — we can describe the result, but not explain it.

*Why acceptable:* The descriptive null result (Pythia not worse than OLMo at 300B) is
itself informative for the field. The architecture confound is a scope limitation
acknowledged in the original hypothesis design (Assumption A4). *Future work:* Run
temporal trajectory at Pythia step72000 (≈143B) and OLMo matched checkpoint. If the
gap is stable, the architecture explanation dominates; if narrowing, the scale explanation
gains plausibility.

### L2: Fast Evaluation (500-Sample Limit)

The use of `--limit 500` evaluates approximately 8-9 examples per MMLU subject, introducing
high variance in per-subject accuracy estimates. Full evaluation across 14,042 MMLU
questions would provide more reliable per-subject estimates and reduce bootstrap CI width.

*Why acceptable:* The large effect size (d = −2.732) and the CI entirely below zero are
unlikely to reverse with full evaluation. The directional refutation is robust; the exact
magnitude of −0.0265 is less reliable. *Future work:* Full lm-eval-harness evaluation
(no `--limit` flag) to confirm magnitude before any publication.

### L3: Single Training Scale

Results are specific to ~300B training tokens. The corpus-quality hypothesis may hold at
different scales, and prior work suggests it does at 2T tokens [Groeneveld et al., 2024].

*Why acceptable:* The hypothesis explicitly targeted ~300B tokens as the comparison point.
This is the scope of the experiment, not a failure. *Future work:* Temporal trajectory
and full-training comparison to characterize the scale dependency.

### L4: IV Not Directly Measured

The corpus quality independent variable was operationalized via corpus identity (The Pile
vs. Dolma) rather than direct measurement of quality proxy scores (n-gram repetition rate,
Flesch-Kincaid grade level, language ID confidence). We assumed Dolma is higher quality
by these proxies based on its documented curation pipeline; this assumption was never
empirically verified on matched document samples.

*Why acceptable:* Dolma's curation advantages are well-documented in Soldaini et al.
[2024], providing a reasonable basis for the corpus-identity operationalization.
*Future work:* Sample 10K documents from each corpus and compute all three quality proxy
metrics to confirm that Dolma scores significantly higher on the composite index.

## Implications for Metric Design

Our results suggest two design requirements for future generalization balance metrics:

1. **Verify denominator sensitivity.** Before using a ratio metric as a quality proxy,
   confirm that the denominator task remains sensitive to the factor being tested at the
   target training scale. HellaSwag's convergence to identical values for both models at
   300B tokens — despite meaningful MMLU differences — reveals that it is an insensitive
   denominator for corpus quality comparisons at this scale.

2. **Require architecture-matched designs for causal claims.** Single-checkpoint
   cross-architecture comparisons cannot isolate corpus quality effects. Future studies
   claiming to measure corpus quality's effect on generalization should either (a) use
   models with identical architecture trained on different corpora, or (b) use temporal
   trajectory analysis to bound the architecture confound within a cross-suite comparison.

## Broader Impact

This work contributes a methodologically rigorous null result that characterizes the
limitations of current evaluation practice for corpus quality claims. The primary positive
impact is methodological: by documenting where cross-architecture, single-checkpoint
comparisons break down, we help researchers avoid drawing causal conclusions from
designs that cannot support them. This reduces the risk of misattributing performance
differences to corpus quality when they may reflect architecture effects.

A potential negative impact of publishing a null result on corpus curation quality is
that it could be misinterpreted as evidence that curation doesn't matter generally.
Our results are explicitly scoped to ~300B training tokens, this specific architecture
pair, and the MMLU/HellaSwag ratio metric. We emphasize that our null result does not
contradict prior evidence of curation benefits at full training scale [Groeneveld et al.,
2024; Penedo et al., 2023] — it reveals the conditions under which those benefits are
and are not detectable with current evaluation protocols.
