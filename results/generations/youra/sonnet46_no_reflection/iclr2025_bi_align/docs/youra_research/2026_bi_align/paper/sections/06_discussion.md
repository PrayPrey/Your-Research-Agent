# 6. Discussion

## 6.1 Interpreting β₄ ≈ 0: Three Competing Explanations

The null result for β₄ admits at least three distinct explanations that are not mutually exclusive.
We assess each in turn, ordered by our judgment of plausibility.

**Explanation 1: Split invalidity (most plausible).** The helpful-base and helpful-online splits
are defined by data collection period, not by annotator identity or verified AI exposure history.
We have no ground-truth knowledge of whether individual annotators in the online split had actually
internalized AI formatting preferences at the time of annotation. If both splits contain a mixture
of AI-familiar and AI-naive annotators — as is likely given the gradual and uneven diffusion of
LLM use across the population — then the split variable is a noisy and possibly uncorrelated proxy
for the theoretical exposure construct. A null β₄ is precisely what we should expect from a
measurement instrument that has low validity, regardless of the true underlying effect. This
explanation does not falsify the bidirectional alignment hypothesis; it falsifies our operationalization
of it.

**Explanation 2: Societal saturation.** An alternative is that AIFS norms have become so
widespread — through LLM-generated content permeating the internet, social media, and everyday
communication — that the distinction between "AI-familiar" and "AI-naive" annotators has collapsed
at the population level [Vishwarupe et al., 2026; CITE: AI cultural saturation literature]. Under
this account, β₄ ≈ 0 reflects a genuine equalization of preferences across conditions rather than
a measurement failure. This explanation would imply that the bidirectional alignment effect, if it
ever existed as a between-annotator phenomenon, may now operate uniformly across all annotators.
Distinguishing Explanation 1 from Explanation 2 requires longitudinal annotator-level data that is
not available in HH-RLHF.

**Explanation 3: True null.** The most parsimonious account is that the bidirectional alignment
hypothesis is simply false at the AIFS feature level: annotator AI-familiarity does not modulate
AIFS preference, because AIFS features are preferred by all annotators for reasons unrelated to AI
exposure (e.g., formatting aids readability independent of AI connotations). The positive β₁ is
consistent with this: AIFS features may just be universally useful formatting signals, not
culturally loaded markers of AI behavior. We consider this explanation plausible but insufficient
on its own, because it does not account for why the split proxy should be expected to work even
under the null.

## 6.2 What β₁ = 0.025 Tells Us About AIFS

The positive and significant β₁ = +0.0246 is the principal affirmative finding of this paper. It
establishes that the AIFS construct — four regex patterns for structured lists, safety prefaces,
chain-of-thought markers, and hedging — captures preference-relevant variation in human judgment
that survives controls for length, fluency, and prompt-level fixed effects. This validates AIFS as
a construct for future research, even though the present hypothesis about its modulation by AI
familiarity was not confirmed.

The effect size is modest (OR ≈ 1.025 per unit of ΔAIFS), which is consistent with AIFS being one
signal among many in preference formation rather than a dominant driver. Future work should examine
whether AIFS effects are heterogeneous across prompt types (e.g., factual vs. creative), whether
individual patterns contribute differentially, and whether the construct replicates in non-RLHF
preference datasets.

## 6.3 Limitations

**Single dataset.** All analyses use HH-RLHF, a single dataset from a single organization
collected under a specific annotation protocol. Generalization to other preference datasets (e.g.,
OpenAssistant, ShareGPT-based datasets) is untested. Dataset-specific factors — annotator
recruitment, compensation, interface design — may all influence AIFS preferences in ways that are
confounded with the split variable [Shen et al., 2024].

**No annotator identity records.** The HH-RLHF dataset does not include annotator IDs or
demographic information. We cannot verify whether any individual annotator appears in both splits,
whether annotator pools overlap, or whether individual-level AI exposure varies within splits.
This is the primary constraint on our ability to test the bidirectional alignment hypothesis
cleanly.

**AIFS not validated against pre-LLM baselines.** The four AIFS patterns were defined based on
known properties of LLM-generated text, but we have not verified that they are differentially
present in LLM-generated versus human-written text from the same time period. Without this
validation, the construct operationalizes "formatting features associated with AI" rather than
"formatting features empirically distinctive of AI."

**Societal saturation is untestable in this dataset.** The equalization hypothesis (Explanation 2
above) cannot be distinguished from the proxy invalidity hypothesis (Explanation 1) without
temporal or individual-level data. Both predict β₄ ≈ 0, and HH-RLHF provides no leverage to
separate them.

## 6.4 Broader Impact

This paper makes a methodological contribution as much as an empirical one. We demonstrate that
testing bidirectional alignment hypotheses — specifically, whether AI system behavior has reshaped
human evaluator preferences — requires data infrastructure that current public RLHF datasets do
not provide: annotator identity records, longitudinal annotation, and verified AI exposure
histories. The null result in this paper is, in part, a consequence of working with the best
available public data rather than the right data.

We do not view this as a negative result in the pejorative sense. The precision null (CI width
0.025, ruling out OR ≥ 1.015) is a genuine contribution: it narrows the hypothesis space and
defines the minimum data requirements for a credible positive test. Future work that collects
annotator-level AI exposure data — even via simple surveys — would be in a position to test the
same hypothesis cleanly.

On the safety side, if the bidirectional alignment effect does exist (under Explanation 1 or 2),
its implications are significant: RLHF-trained systems may be drifting toward self-reinforcing
stylistic norms rather than toward ground-truth human preferences. Detecting and measuring this
drift is a prerequisite for correcting it. The present paper lays the groundwork for that
detection infrastructure.
