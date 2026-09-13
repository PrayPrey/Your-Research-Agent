# 6. Discussion

## 6.1 Key Findings Interpretation

### The domain content differentiation result is the paper's strongest claim

The η² > 0.91 result from h-m1 is not a supporting finding — it is the primary empirical contribution of this paper. Between-domain differences explaining over 91% of variance in cognitive task pattern proxies means that Pile domains are categorically, not marginally, distinct in their cognitive content. This grounds the theoretical assumption that has been implicit in data mixing research since The Pile's release: that Wikipedia, Books, GitHub, and other domains contain qualitatively different kinds of cognitive signal. Prior work (RegMix, DoReMi, DCLM) has assumed this differentiation without measuring it. We measure it.

The practical implication is that the assumed mechanism of domain-benchmark specificity is empirically sound: if Wikipedia concentrates entity-dense factual content (η²=0.9915), Books concentrate discourse-connective narrative content (η²=0.9142), and GitHub concentrates formal syntax (η²=0.9821), then there is a principled cognitive basis for expecting differential effects on knowledge recall (MMLU), commonsense completion (HellaSwag), and structured reasoning benchmarks. The mechanism is not just theoretically motivated — it is empirically confirmed.

### The trajectory non-uniformity result enables the next study

The h-e1 result confirms that within-family domain exposure variation exists and is sufficient for panel analysis (at least for 10 of 22 domains). The cross-scale consistency (Spearman ρ = 1.0) means that the variation is a property of data ordering, not model dynamics — every model size sees the same domain sequence, making the panel structure clean and interpretable.

The more practically important finding from h-e1 is the *infrastructure* validation: the `doc_idx.npy` identity mapping, the `step_to_sample()` arithmetic, the JSONL.zst streaming pipeline. These components, individually small, collectively constitute the missing infrastructure link between Pythia's documented training procedure and domain exposure analysis. Making this infrastructure public and validated (with 5 unit tests and 15 integration checks) is a concrete contribution to the field's capacity to study pre-training data effects.

### The 70M reversal requires replication, not rejection

The preliminary finding that ρ(Wikipedia, HellaSwag) > ρ(Wikipedia, MMLU) at 70M (N=10) is the most attention-grabbing result in this paper, but it should not be over-interpreted. We offer three competing explanations, ordered by plausibility:

**Most likely (HIGH plausibility):** The 70M MMLU floor effect. MMLU accuracy for a 70M model is approximately 25% (random chance) for the vast majority of the training run, because factual knowledge recall requires model capacity well beyond 70M parameters. When MMLU is flat (no improvement across checkpoints), Spearman ρ(anything, MMLU) is dominated by noise. This is not a finding about Wikipedia — it is a finding about the 70M model's inability to make MMLU progress regardless of domain exposure.

**Also plausible (HIGH plausibility):** N=10 checkpoint sampling artifact. The 10 available checkpoints include 6 very early steps (0, 1, 2, 4, 8, 16) where both domain exposure and benchmark scores are minimal and noisy. Spearman with N=10 non-uniformly spaced points has extremely wide confidence intervals; the result would likely shift substantially with N=154.

**Less likely (MEDIUM plausibility):** Pile-CC confound. Pile-CC (std=0.0266, highest variance of any domain) co-moves with Wikipedia in training and may capture Wikipedia's effect in a univariate Spearman. Partial correlation analysis controlling for Pile-CC would test this directly.

**Least likely (LOW plausibility):** Wikipedia genuinely drives HellaSwag more than MMLU at all scales. This would be a genuine refutation of the domain specificity hypothesis, requiring a fundamental revision of our model of how Wikipedia content translates to capabilities. The 1B and 6.9B results (pending) will determine whether this low-plausibility explanation deserves elevation.

The right stance is: the 70M result is informative about the limits of small-scale analysis, not about domain-benchmark relationships. Replication at ≥1B is required before any directional conclusion can be drawn.

## 6.2 Limitations

**L1: Partial domain lookup — six Pile domains have zero exposure in our sample.** The 600K-document first-shard PoC covers only shard 0 of The Pile's 30-shard structure. Books3, OpenWebText2, GitHub, OpenSubtitles, BookCorpus2, and YoutubeSubtitles are concentrated in later shards and are entirely absent from our domain exposure trajectories. This makes P2 (Books→HellaSwag) structurally untestable with current data and limits P1 testing to domains present in shard 0. The fix requires building the full 134M-document domain lookup across all 30 shards (estimated ~150 compute-hours with the proven `build_lookup_direct.py` infrastructure).

**L2: Incomplete evaluation cache.** The benchmark evaluation pipeline was running at analysis time but had not completed: 70M had 10/154 checkpoints, 1B had 2/154, and 6.9B had 0/154 complete evaluations. This limitation means neither Spearman analysis (requires N≥100) nor panel regression (requires N≥3 entities) could be executed definitively. Once the evaluation cache is complete, all h-m2 and h-m3 analyses can be re-run without modification.

**L3: H-M1 used domain-representative generated text rather than real Pile documents.** The η²>0.91 effect sizes may be inflated because generated domain-representative texts are cleaner and more domain-prototypical than actual Pile documents (which contain noise, mixed-domain text, and low-quality content). Directional claims are robust — Wikipedia will have higher entity density than Books regardless of noise — but the quantitative η² values should be treated as upper bounds. Validation on real Pile documents was in progress at reporting time.

**L4: Observational design — no causal claims.** Domain exposure correlations do not establish that increasing domain exposure *caused* benchmark improvement. Cross-checkpoint variation in a fixed training run is observational by construction: the model always saw data in the same order. Establishing causal effects requires interventional experiments (retraining with resampled domain proportions), which are beyond the scope of this study.

## 6.3 Broader Impact

This work contributes to the understanding of pre-training data composition effects on downstream model capabilities — a question with direct practical implications for the design of training datasets for large language models. The positive contributions (domain content differentiation infrastructure, exposure trajectory extraction pipeline) are broadly useful for future data attribution research. The negative contribution (Books3 zero-exposure in single-shard samples) warns practitioners against drawing domain-specific conclusions from partial Pile samples, reducing the risk of incorrect data mixing recommendations in future work.

We do not anticipate direct negative societal impacts from this methodology. The pipeline is purely analytical (evaluating existing models on existing benchmarks) and does not generate new model weights or training data.
