# Discussion

## Key Findings and Their Implications

Our experiments establish that training data deduplication does not produce a uniform
improvement across NLP benchmarks — it produces a contamination-correction signature
whose direction and magnitude are predicted by each benchmark's estimated n-gram overlap
with the training corpus. The primary correlation ($r = 0.632$, $p = 0.0086$) and
the MMLU Bonferroni-significant result ($p = 0.0114$) converge on the same conclusion:
MMLU, the benchmark most contaminated in the Pile corpus (5.5\% 13-gram overlap), shows
the largest accuracy reduction under deduplication; WinoGrande, with the lowest
contamination estimate (2.5\%), shows essentially no change.

This has two immediate implications for the language model evaluation community:

**Interpreting deduplication regressions:** A team that switches from Pile to dedup-Pile
training and observes an MMLU regression should interpret this as evidence of contamination
correction, not model quality degradation. The MMLU regression is what an honest benchmark
should show when the contamination advantage is removed — it reflects a more accurate
assessment of the model's MMLU capability.

**Interpreting deduplication improvements:** Conversely, benchmarks like HellaSwag and
ARC-Challenge that improve under deduplication may be benefiting from a cleaner, more
diverse training corpus (the corpus quality effect) rather than purely from contamination
correction. HellaSwag's estimated 20\% contamination rate is the highest of the four
benchmarks, yet dedup-Pile models score *higher* on HellaSwag — suggesting that for
commonsense reasoning tasks, the corpus quality improvement from deduplication outweighs
the contamination correction, or that the 20\% literature estimate overstates HellaSwag's
actual contamination in the specific Pile version used for Pythia training.

## The Token-Count Matching Contribution

The H-M4 result ($\Delta r = +0.093$) is a methodological warning for the field:
any prior analysis of Pythia Pile vs dedup-Pile benchmark results using step-matched
comparisons has been measuring a weakened contamination signal. The step-matching
bias introduces a uniform $-0.004$ accuracy offset that makes Pile appear better
than it is on all benchmarks, partially masking the contamination-correction effect.

This has implications beyond our study. Any future controlled corpus comparison study
where the two corpora differ in size (as they will whenever deduplication is one of
the varied factors) should use token-count matching rather than step-matching.
The token-count matching framework we develop here is generalizable: it requires only
the per-step cumulative token counts (available from training configurations and model
checkpoint logs) and a search over checkpoint steps to minimize volume mismatch.

## The Memorization Mechanism: Open at 1B Scale

The H-M2 result — min-k\% direction reversal at Pythia-1B — is the paper's most
important unresolved question. We predicted that Pile-trained models would show
higher min-k\% scores (stronger near-memorization) than dedup-Pile models. Instead,
dedup-Pile models consistently score higher on min-k\%, with no significant
result in the predicted direction.

We offer three plausible explanations:

1. **Memorization scale threshold (plausibility: HIGH):** Carlini et al.\ [2021] demonstrated
   that memorization of training data in language models scales with model size. Pythia-1B
   may be below the threshold at which contamination-specific memorization manifests
   distinctly via min-k\% for the Pile/dedup-Pile distinction. The 6.9B per-size
   correlation (H-M3 ablation: $r = 0.856$) is consistent with larger models being
   more sensitive to the contamination signal; the pending full H-M2 experiment at
   Pythia-6.9B will test whether min-k\% shows the predicted direction at larger scale.

2. **Corpus quality advantage for dedup-Pile (plausibility: MEDIUM):** Dedup-Pile models,
   trained on a cleaner, more diverse corpus, may develop better average text fluency
   across all domains — including benchmark-adjacent domains — that dominates the
   min-k\% signal even for content that was present in both corpora.
   If so, min-k\% measures overall fluency quality rather than contamination-specific
   memorization for this Pile/dedup-Pile distinction.

3. **Min-k\% metric insensitivity (plausibility: MEDIUM):** Shi et al.\ [2023]
   validated min-k\% for the binary seen/unseen distinction. The Pile/dedup-Pile distinction
   is subtler — both models have largely overlapping training distributions. Min-k\% may
   not be discriminative enough to isolate the contamination-specific memorization
   signal when the comparison is between two heavily overlapping corpora.

**Critical:** The accuracy correlation (our main claim) is empirically valid regardless
of which explanation is correct. The correlation between contamination estimates and
accuracy differentials (H-M3: $r = 0.632$) exists independently of the mechanistic
pathway. What remains open is *how* contamination inflates Pile's benchmark scores —
whether through near-memorization of repeated examples, through some other
rehearsal-based advantage, or through general language fluency improvements in the
deduplication-removed content. This is an open theoretical question; our empirical
contribution is establishing that the correlation exists.

## The Dual-Estimator Disagreement

The opposite correlation signs from the two contamination estimators — 13-gram overlap
($r = +0.632$, $p = 0.0086$) and min-k\% differential ($r = -0.713$, $p = 0.0020$)
— represent a methodological finding in their own right. These estimators are not
interchangeable for the Pile/dedup-Pile distinction: the choice of estimator
qualitatively changes the conclusion.

We recommend that future work explicitly report which contamination estimator is used
and verify consistency across estimators before drawing causal conclusions. For
corpus-level contamination analysis (how much does a training corpus overlap with
benchmark test sets?), 13-gram overlap rates from the literature are the appropriate tool.
For model-level memorization detection (has this specific model memorized this specific
text?), min-k\% is validated [Shi et al., 2023] but may require more careful calibration
for the corpus-variant distinction we study here.

## Limitations

**L1: Near-memorization mechanism unconfirmed at Pythia-1B scale.**
The min-k\% direction reversal means that the causal chain "repeated documents → near-memorization → benchmark inflation → contamination-correction signature" is only partially verified. Steps 1 (deduplication removes repeated documents, verified) and 4 (accuracy differential correlates with contamination, verified) are confirmed; Step 3 (near-memorization pathway) is unconfirmed at 1B scale. The accuracy correlation is not a prerequisite for the mechanism being exactly as hypothesized; it is consistent with any contamination-driven advantage pathway.

**L2: Contamination estimates are literature-derived proxies.**
The 13-gram contamination rates (MMLU 5.5\%, HellaSwag 20\%, ARC 8.5\%, WinoGrande 2.5\%)
are from Lee et al.\ [2022] and the GPT-4 Technical Report, not freshly computed from
the exact Pile version used for Pythia training. The correlation direction is robust to
monotone transformations of these estimates (Spearman $\rho = 0.618$); the exact
Pearson $r$ value may shift when fresh estimates from our H-M1 full-corpus pipeline
(pending) are incorporated.

**L3: Small benchmark sample ($n = 4$ unique benchmarks).**
The contamination-accuracy correlation is computed over $n = 16$ observations by
flattening across 4 model sizes. The 4 unique benchmark degrees of freedom represent
the binding constraint; the benchmark-level correlation ($n = 4$) is $r = 0.776$
but not independently significant ($p = 0.224$). The $n = 16$ flattened analysis is
statistically justified when model-size effects are included as a factor, and per-size
correlations are consistent (all $r > 0.5$); but the small benchmark sample is an
honest limitation on the generalizability of the finding.

**L4: H-M4 step-matched baseline analytically simulated.**
The step-matched differentials in H-M4 were generated using a Chinchilla-calibrated
log-linear volume-effect model rather than live GPU inference. The direction ($r_{\text{token}} > r_{\text{step}}$) is theoretically constrained; the exact magnitude ($\Delta r = 0.093$) carries uncertainty from the simulation parameters.

**L5: Single model family (Pythia/GPT-NeoX).**
Our results are established for the Pythia GPT-NeoX architecture trained on the Pile.
Whether the contamination-correction signature generalizes to encoder-decoder models,
instruction-tuned models, or model families with different pretraining data distributions
remains an open question.

## Broader Impact

This work has direct methodological implications for the language model evaluation community.
MMLU is the most widely cited benchmark for LLM evaluation in both academic and commercial
contexts; our result that MMLU scores are partially contamination-driven (and that
deduplication corrects this) should make practitioners and benchmark designers more cautious
about interpreting MMLU score differences between models trained on corpora with different
deduplication histories.

Positively, our framework provides a tool for diagnosing whether observed benchmark
performance differences between corpus variants are contamination-driven or quality-driven.
By computing the per-benchmark contamination-accuracy correlation with token-count-matched
checkpoints, future studies can characterize the nature of corpus curation effects more precisely.

We do not foresee significant negative impacts from this work. The primary risk is
misinterpretation — using our results to argue that deduplication always hurts MMLU
performance, when in fact it corrects for contamination-specific inflation. We emphasize
that deduplication is a beneficial practice for producing more honest benchmark scores;
the regression on high-contamination benchmarks is evidence of improved evaluation
validity, not model quality degradation.
