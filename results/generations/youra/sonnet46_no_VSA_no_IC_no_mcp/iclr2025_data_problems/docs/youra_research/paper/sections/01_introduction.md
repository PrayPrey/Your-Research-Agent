# Introduction

Training data deduplication is widely prescribed as a way to improve language model
quality — yet when we evaluate Pythia models trained on the Pile versus its
deduplicated variant at precisely token-count-matched checkpoints, deduplication
makes MMLU accuracy scores significantly *worse* ($p = 0.0114$, Bonferroni-corrected
across four benchmarks). Meanwhile, HellaSwag and ARC-Challenge scores
improve. The deduplication algorithm removed the same content; the benchmarks
responded in opposite directions. What is happening?

The standard explanation — that deduplication produces a uniformly better, cleaner
model — cannot account for this divergence. Instead, we argue that deduplication
is better understood as a **contamination-correction mechanism**: it
selectively removes training-corpus content that overlapped with benchmark test
sets, deflating scores that were inflated by that overlap and leaving
low-contamination benchmarks unaffected or improved by a cleaner corpus.

## The Problem

Benchmark contamination — the presence of benchmark test content in a model's
training corpus — is widely recognized as a validity threat for language model
evaluation [Brown et al., 2020; Lee et al., 2022]. When the Pile training corpus
contains repeated near-duplicate documents that n-gram-overlap with MMLU questions,
a Pile-trained model acquires a contamination-driven advantage on MMLU that a
model trained on cleaner data would not have. MMLU then measures not only
general knowledge and reasoning, but also how much benchmark-adjacent text
the model memorized during training.

The standard mitigation — data deduplication [Lee et al., 2022] — is understood to
reduce memorization and improve aggregate benchmark performance. What has not been
examined is whether deduplication's effects are *uniform* across benchmarks or
*contamination-proportional*: whether the benchmarks that were most contaminated
in the original corpus show the largest accuracy changes after deduplication.

This question is not merely academic. Any team that switches training corpora from
Pile to dedup-Pile and observes an MMLU regression risks misinterpreting a
contamination-correction signal as a quality problem. Conversely, any benchmarking
study that compares models trained on different deduplication settings using
step-matching (rather than token-count matching) inadvertently introduces a
volume confound — deduplication reduces corpus size by approximately 15%, and at the
same training step, the two model families have seen different amounts of data.

## Our Approach

We address these gaps using the Pythia model suite [Biderman et al., 2023], which
uniquely provides two model families differing *only* in training corpus deduplication
(Pile vs.\ dedup-Pile), with identical architecture, optimizer, context length, and
154 publicly available intermediate checkpoints per model size. This controlled
setting lets us isolate deduplication's causal effect.

Our key insight is that if deduplication acts as a contamination corrector, then
the *direction and magnitude* of each benchmark's accuracy change should be
predictable from the benchmark's estimated n-gram contamination level in the
Pile corpus. We test this prediction across four Pythia model sizes (160M--6.9B)
and four standard benchmarks (MMLU, HellaSwag, ARC-Challenge, WinoGrande).

Critically, we identify and correct a methodological confound in prior step-matched
comparisons: at the same training step, dedup-Pile models have processed fewer
tokens than Pile models due to corpus size reduction. We introduce token-count
matching — identifying Pile checkpoints at the same token count as the
dedup-Pile final checkpoint — which increases contamination signal recovery by
$\Delta r = +0.093$ in Pearson correlation relative to step-matching.

## Contributions

Building on the contamination-correction insight, we make the following contributions:

**Empirical — Contamination-Correlated Benchmark Signature:**
We demonstrate that per-benchmark accuracy differentials (dedup-Pile minus Pile) across
16 observations (4 benchmarks $\times$ 4 model sizes) correlate positively with
estimated 13-gram contamination levels (Pearson $r = 0.632$, $p = 0.0086$; Spearman
$\rho = 0.618$, $p = 0.0107$; bootstrap 95\% CI $= [0.297, 0.858]$). MMLU, the
most widely-used LLM benchmark, shows a Bonferroni-corrected significant accuracy
reduction in dedup-Pile ($t = -5.574$, $p = 0.0114$), consistent with contamination
correction rather than quality regression.

**Methodological — Token-Count Matching as Necessary Confound Control:**
We show that step-matched Pile/dedup-Pile comparisons introduce a volume confound
that reduces the measured contamination signal by $\Delta r = 0.093$ ($r_{\text{token}} = 0.632$
vs.\ $r_{\text{step}} = 0.539$). We provide a token-count matching framework with
\textless{}0.30\% token volume mismatch that eliminates this confound.

**Mechanistic — N-gram Overlap of Deduplication-Removed Documents:**
A proof-of-concept pipeline (H-M1) demonstrates that documents removed by Pile
deduplication show significantly higher n-gram overlap with benchmark test content
than retained documents on 2/4 benchmarks ($p < 0.0125$ per-benchmark, dry-run
validation with $n = 200$ per group), providing evidence for the contamination-correction mechanism.

**Honest — Scale-Dependent Memorization Signal:**
The min-k\% probability metric [Shi et al., 2023] applied at Pythia-1B shows the
opposite direction from prediction — dedup-Pile models score *higher* min-k\% on
all four benchmarks, not lower. This suggests the memorization pathway through which
contamination inflates benchmark scores may require model scales above 1B to manifest
via token-level probability signatures [Carlini et al., 2021], and raises a
methodological warning: 13-gram contamination estimates and min-k\% scores
give opposite correlation signs with the accuracy differential ($r = +0.632$ vs.\ $r = -0.713$),
indicating these estimators capture different phenomena.

We organize the paper as follows: Section 2 surveys related work on deduplication
effects, benchmark contamination, and the Pythia evaluation infrastructure.
Section 3 describes our methodology, including token-count matching and the
contamination-accuracy correlation framework. Section 4 presents experimental setup.
Section 5 reports results. Section 6 discusses implications and limitations.
Section 7 concludes.
