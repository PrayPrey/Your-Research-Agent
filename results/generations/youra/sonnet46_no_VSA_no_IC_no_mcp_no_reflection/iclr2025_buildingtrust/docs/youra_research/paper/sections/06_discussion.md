# Discussion

## Key Findings and Interpretation

**Finding 1: Alignment strategy is fingerprint-detectable from public benchmarks.**
The 83.3% LOO-CV accuracy (p=0.031) establishes that DPO and SFT training produce
detectably different 4D trustworthiness profiles. This is a practically useful result:
practitioners can infer a model's likely alignment strategy from four standard benchmark
evaluations available on public leaderboards, without training-data access or model
internals. The fingerprint is sufficiently strong that 10 of 12 models are correctly
identified despite the subtle differences in absolute scores (0.5–4.6pp range).

The alignment auditing implication is meaningful even at pilot scale: if a model's
reported alignment provenance is incorrect or incomplete, benchmark-based fingerprinting
provides an independent check. This is particularly relevant for the community model
ecosystem, where alignment documentation is inconsistent.

**Finding 2: Truthfulness, not fairness, carries the alignment signal.**
This is the paper's central surprising finding. The dominant theoretical narrative around
DPO predicts that preference-based training rewards bias-avoidance, producing higher
fairness scores. Our results show the opposite pattern: TruthfulQA MC2 dominates
discriminability (Fisher=0.8122), while BBQ provides essentially no signal (Fisher=0.0091).
DPO models score +4.6pp higher on truthfulness — the wrong direction for the fairness-
driven mechanism.

We propose three competing explanations for this reversal, ordered by plausibility:

1. **Implicit factual reward via annotator quality ratings (most plausible).** UltraFeedback-
   style DPO training datasets explicitly rate factual quality as a preference dimension,
   alongside helpfulness and format. If DPO models in our pool are disproportionately
   trained on datasets with factual quality ratings, preference optimization may implicitly
   improve truthfulness as a side effect. This explains why DPO models score higher on
   TruthfulQA — a calibrated log-probability metric sensitive to annotation quality.

2. **Calibration improvement from contrastive training.** TruthfulQA MC2 measures
   accuracy on normalized log-probabilities (MC2 scoring). DPO's contrastive objective
   — which increases the relative probability of preferred over rejected responses —
   may improve calibration of the model's probability distribution independently of
   factual content. This would manifest as higher MC2 scores without necessarily
   increasing the probability of factually correct answers.

3. **Sample selection bias in community model pool.** DPO models in our sample (Intel
   neural-chat, openchat, Starling) may come from curators who applied additional data
   quality filtering independent of alignment method. If the DPO community pool happens
   to include higher-quality training data, the truthfulness advantage may partially
   reflect data curation rather than alignment method per se.

These explanations are not mutually exclusive and cannot be ranked definitively from
inference-only evaluation. Distinguishing them requires training-data analysis or
controlled experiments with fixed data compositions.

**Finding 3: Preference-based methods (RLHF and DPO) may share a benchmark signature.**
Llama-2-chat's misclassification as DPO — despite RLHF training — suggests that the
alignment fingerprint captures a broader "preference-based training" cluster rather than
DPO specifically. If RLHF-PPO and DPO produce similar 4D profiles distinct from pure
SFT, the binary DPO/SFT framing understates the true structure of alignment space.
A 3-class study (DPO vs RLHF vs SFT) is the natural extension.

## Limitations

**L1: Causal mechanism is not established.** The empirical fingerprint (83.3% LOO-CV,
p=0.031) is confirmed, but the causal mechanism driving it is not. The proposed bias-
avoidance mechanism (DPO improves fairness) is falsified; the most plausible alternative
(implicit truthfulness reward via annotation criteria) is hypothesized but untested.
Mechanistic confirmation requires training-data analysis or controlled ablations of
preference data annotation criteria. The fingerprinting claim stands independently of
mechanism — alignment strategy can be detected without knowing why — but interpretation
of what the fingerprint measures remains open.

**L2: Small sample size (n=12 models, 6 pairs).** Our permutation p-value of 0.031 is
statistically significant but close to the α=0.05 threshold. Two misclassifications
shift accuracy from 100% to 83.3%; one additional error would drop it to 75%, and
two more would fall below the 67% gate. The result is confirmatory at pilot scale,
not definitive at population scale. No larger matched DPO/SFT dataset with documented
alignment provenance is publicly available without custom model training, making our
n=12 the available controlled population. Larger studies with custom-trained pairs
are needed for population-level claims.

**L3: 100-sample evaluation limit.** We use `--limit 100` per lm-evaluation-harness
task for PoC efficiency, compared to full task sizes of ~800–1200 samples. Score
estimates carry higher variance than full-task evaluation. However, the critical
null result (k_BBQ=3/6, p=0.66) is so far from the threshold (p≤0.125) that full
evaluation cannot reverse it; similarly, the 83.3% fingerprint accuracy would need
substantial degradation under full evaluation to fail the 67% threshold. Full-task
evaluation is immediate future work.

**L4: Community model confounds.** Not all pairs are perfectly matched for base model
and training data. Community DPO models have incompletely documented provenance.
The cleanest pair (zephyr-alpha/beta, alignment-handbook, same base and data) actually
produces a misclassification — which itself suggests that base architecture proximity
can dominate alignment signal under perfect matching. This is informative but limits
the strength of causal claims.

## Scope Conditions

Our results hold for 7B English-language autoregressive models evaluated on the four
benchmarks specified. Whether the fingerprint generalizes to other model scales
(13B, 70B), other languages, or other benchmark suites is unknown. The RLHF/DPO
boundary ambiguity (Llama-2-chat case) suggests that the binary DPO/SFT label may
not be the correct categorization — practitioners labeling RLHF-trained models as
"SFT" will introduce systematic classification noise.

## Broader Impact

This work contributes tools for alignment auditing — the practice of verifying how
models were trained after the fact. Positive impacts include: enabling practitioners
to cross-check alignment claims against public benchmark profiles; supporting regulatory
frameworks requiring alignment documentation; and motivating more careful annotation
of alignment provenance for public model releases.

Potential negative impacts: fingerprinting methods could be used adversarially to
identify which benchmark profile to target when attempting to misrepresent a model's
alignment strategy. However, the subtlety of the signal (0.5–4.6pp differences) and
the requirement for matched comparisons make gaming this fingerprint non-trivial.

The finding that the DPO fairness advantage is not supported by paired data is
potentially controversial but important for accuracy: practitioners should not assume
DPO alignment improves fairness without empirical verification specific to their model
and data context.
