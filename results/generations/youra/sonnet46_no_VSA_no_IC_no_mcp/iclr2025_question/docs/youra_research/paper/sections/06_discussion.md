# Discussion

## Why SE Wins on TriviaQA

The +0.155 AUROC gap between SE and TE on TriviaQA, confirmed with non-overlapping confidence intervals, is explained directly by the mechanism we measure in RQ2. Token entropy aggregates the model's token-level distribution across all output tokens — including tokens from semantically equivalent but surface-distinct responses. When a model generates K=10 samples for a question it doesn't know, the incorrect answers often take diverse surface forms ("Paris", "Lyon", "Marseille" for a question about French geography). Token entropy treats the spread across these as genuine uncertainty signal. Semantic entropy's NLI clustering assigns all semantically equivalent samples to one cluster, removing this surface variation before computing entropy.

The scale of the mechanism (intra-cluster TE variance = 7.152 nats², 71× the gate threshold) makes the explanation unambiguous: paraphrase noise is not a subtle correction but the dominant component of TE's within-cluster signal. The mean cluster count of 7.31 out of K=10 confirms that Llama-2-7B produces semantically diverse outputs — the mechanism's prerequisite is satisfied for the vast majority of TriviaQA questions (76/98 with multi-member clusters).

This mechanistic explanation extends Huang et al. [2023]'s observation that single-pass entropy underperforms sampling-based methods: we provide the feature-level evidence showing *why* — TE's paraphrase noise, not any general superiority of sampling.

## Why SE Loses on TruthfulQA

The cross-benchmark reversal (TE = 0.511 > SE = 0.445) follows directly from the mechanism's failure mode. TruthfulQA's adversarial misconceptions are designed to test whether models repeat false beliefs — statements like "Napoleon won at Waterloo" that models have absorbed from training. These misconceptions produce low-diversity model outputs: across K=10 samples, the model consistently generates the same wrong answer with high confidence. All K samples fall into one NLI cluster, yielding near-zero SE for incorrect answers — making them indistinguishable from correct answers in SE's feature space.

Token entropy succeeds precisely here: a model that repeatedly generates the same wrong answer does so with a narrow, peaked token distribution (low entropy). TE's low-entropy signal for this deterministic wrong output is a reliable correctness indicator. SE's clustering cannot distinguish "confidently wrong about one thing" from "confidently right about one thing."

Three competing explanations exist for the TruthfulQA reversal:

1. **Task-structure dependence (PRIMARY):** The deterministic-wrong output structure of TruthfulQA's adversarial misconceptions makes SE's paraphrase-filtering advantage irrelevant and TE's entropy signal effective. (Plausibility: HIGH — mechanistically consistent with H-M1 findings)

2. **NLI model size confound (SECONDARY):** H-C1 used nli-deberta-v3-small vs. H-E1's nli-deberta-v3-large. The smaller NLI model may cluster incorrectly on TruthfulQA's longer answers, inflating SE entropy artificially. (Plausibility: MEDIUM — requires direct test)

3. **EM label quality (TERTIARY):** TruthfulQA's yes/no prefix matching for correctness may be noisier than TriviaQA's alias normalization. (Plausibility: LOW — noise would deflate all AUROCs equally, not cause reversal)

We cannot cleanly attribute the reversal to (1) vs. (2) from the current data, because H-C1 changed both the benchmark and NLI model size simultaneously. The task-structure explanation is most parsimonious — it explains both the TriviaQA result (diversity mechanism active) and the TruthfulQA result (mechanism absent) with the same principle — but the NLI model size confound is a genuine limitation requiring a follow-up experiment.

## SCG BERTScore as a Short-QA Failure Mode

The |SCG − SE| gap of 0.336 (corrected) exceeds the equivalence gate by 11×, establishing that BERTScore-based consistency is not an SE substitute on short factual QA. The failure mode is specific: BERTScore measures lexical overlap via contextual embeddings, which captures surface similarity rather than semantic entailment. For 1-3 word TriviaQA answers, two wrong answers may share high BERTScore (same vocabulary, e.g., "Paris" vs. "Pairs") while being semantically distinct, or two equivalent answers may share low BERTScore (different surface forms, e.g., "Paris" vs. "the city of light"). NLI entailment correctly handles both cases.

This finding has practical implications: practitioners seeking a lower-compute SCG alternative to SE should use SelfCheckNLI (NLI-based consistency) rather than the BERTScore variant on short factual QA tasks. Manakul et al. [2023] evaluate SCG on long-form generation (WikiBio), where lexical overlap is a better semantic proxy. Our result characterizes the task-type boundary of BERTScore's adequacy.

## VC Degeneracy as a Meta-Cognitive Failure

The ECE = 0.430 and 5-distinct-value distribution confirm that 7B-scale instruction-tuned models lack reliable meta-cognitive access to their uncertainty. Xiong et al. [2023] document similar calibration failures at 7B scale and show improvement at 70B; our independent replication with a different elicitation prompt confirms the finding is robust to prompt variation and provides more precise characterization of the degeneracy pattern (near-constant 95% confidence regardless of actual accuracy).

The practical implication is clear: at 7B scale, VC cannot be used as an uncertainty proxy without calibration correction. Post-hoc calibration (Guo et al. [2017]) may partially address ECE, but the degenerate 5-value distribution suggests the model has learned a collapsed representation of confidence that calibration alone may not recover.

## Limitations

**L1: Task-structure scope condition (principled limitation).**
The SE > TE advantage holds on TriviaQA but not TruthfulQA. This does not invalidate the TriviaQA finding — the N=98 result is well-powered and the mechanism is confirmed. It does constrain the paper's scope claim: practitioners should not assume SE universally outperforms TE without first characterizing whether their task produces paraphrase-diverse or deterministic-wrong incorrect outputs. We frame this task-structure condition as a contribution rather than a failure: identifying *when* a method works is more valuable than false claims of universality.

**L2: N=98 pilot statistical power.**
Bootstrap 95% CI half-widths of ~0.05–0.07 provide ample power for the primary finding (gap = +0.155, 3× the gate). For TruthfulQA results (AUROC range 0.44–0.51), CIs overlap substantially, making the ranking directional evidence rather than statistically definitive. The pre-specified protocol included an N=500 extension for gaps near threshold; the primary finding does not require extension. TruthfulQA results should be interpreted as directional until replicated at larger N.

**L3: NLI model size confound in H-C1.**
H-C1 uses nli-deberta-v3-small (vs. nli-deberta-v3-large in H-E1) simultaneously with the benchmark change. We cannot attribute the TruthfulQA reversal purely to task structure without controlling for NLI model size. The follow-up experiment (re-run H-C1 with the large NLI model) is the next required step to isolate the two factors.

**L4: Sign convention inconsistency in secondary pipelines.**
H-M3 and H-M4 report SE AUROC = 0.286, the uninverted orientation. Corrected values (1 − 0.286 = 0.714) are consistent with H-E1. All P2 and P3 hypothesis evaluations use internally consistent orientations within their respective pipelines; the inconsistency affects only cross-pipeline SE comparison, not the primary findings.

**L5: H-M2 ablation design flaw.**
H-M2's planned ablation of NLI clustering was invalidated by an experiment design error (the ablated predictor is a monotone transform of SE, guaranteeing zero AUROC delta by construction). The mechanistic evidence for NLI clustering's contribution comes instead from H-M1's direct intra-cluster variance measurement, which is independent of the ablation design. The NLI contribution to SE's advantage is thus supported indirectly but not causally quantified.

## Broader Impact

This work characterizes when semantic entropy is and is not a reliable uncertainty estimator, providing empirical guidance for practitioners deploying LLMs in systems that depend on uncertainty-based safety mechanisms. The task-structure condition we identify — paraphrase-rich vs. deterministic-wrong incorrect outputs — is a benchmark property that practitioners can evaluate for their specific use case before committing to a method. By documenting where SE fails (adversarial misconception tasks) alongside where it succeeds (open-domain factual recall), we reduce the risk of over-trusting uncertainty estimates in high-stakes settings.

The VC degeneracy finding has direct safety implications: 7B-scale models expressing 95% confidence while answering incorrectly ~53% of the time should not be used as uncertainty proxies without ECE-based calibration correction. This confirms and extends Xiong et al. [2023]'s finding with more precise characterization, reinforcing the recommendation against VC-based uncertainty at sub-13B scales.

We note no foreseeable misuse of this work: uncertainty estimation methods are defensive tools (detecting when models are likely wrong), and characterizing their scope conditions improves their reliable application.
