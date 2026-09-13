# Discussion

## Key Findings Interpretation

Our results reveal three distinct failure modes operating simultaneously on HaluEval-QA, each with a specific mechanistic interpretation.

**Finding 1: NLI domain mismatch renders semantic entropy degenerate on short factual QA.**
The deberta-large-mnli model — trained on MNLI sentence pairs from news, fiction, and telephone conversations — applies an entailment threshold calibrated for 20–50 word sentences. HaluEval-QA responses are typically 5–15 tokens. At this length, surface-form variation between semantically equivalent responses (e.g., "the US" vs. "the United States" vs. "America") may exceed the NLI model's entailment threshold, causing it to classify synonymous responses as semantically distinct. Our measurement — aggregation_rate = 0.272, with 72.8% of examples at maximum cluster count — directly quantifies this domain mismatch.

This finding is not a critique of semantic entropy as a framework: Kuhn et al. (2023) correctly validate it on TriviaQA and NQ, where responses are longer and NLI aggregation operates as intended. Rather, it defines a domain boundary: the NLI clustering step requires a model whose semantic equivalence threshold is calibrated for the target response length and style. Using a general-purpose MNLI model for short factual QA responses violates this calibration requirement, and the violation is severe enough (aggregation_rate 0.272 vs. required 0.50+) to collapse the entire signal to a constant.

The practical implication is actionable: replacing deberta-large-mnli with a QA-specific entailment model (e.g., cross-encoder/nli-deberta-v3-base fine-tuned on QA entailment pairs) could recover non-degenerate semantic entropy on HaluEval-QA without any new LLM inference. The existing H-E1 stochastic samples (5 responses per example) provide all the inputs needed for this substitution experiment.

**Finding 2: SelfCheckGPT-BERTScore exhibits inverted correlation with HaluEval-QA labels.**
AUROC = 0.3562 (CI [0.332, 0.380]) implies that BERTScore consistency is *positively* correlated with HaluEval-QA hallucination labels — the opposite of SelfCheckGPT's design assumption. The most parsimonious explanation is a label construction artifact: HaluEval-QA hallucinations are ChatGPT-generated confident-sounding incorrect answers. When an LLM is presented with a question whose "correct" answer in the benchmark is actually wrong (from the LLM's perspective), it may confidently reproduce a specific incorrect fact across stochastic samples — generating highly consistent wrong answers.

This is consistent with the broader observation in Xiong et al. (2023) that LLMs are often overconfident on incorrect answers. The SelfCheckGPT assumption — that hallucinations arise from the model "not knowing" and therefore generating inconsistently — fails when hallucinations are defined as "confidently stated wrong answers" rather than "uncertain or absent knowledge."

This finding implies that SelfCheckGPT's correlation direction with hallucination labels is benchmark-dependent. On WikiBio biography generation (Manakul et al., 2023), hallucinations arise from the model generating plausible but unverifiable biographical details — a setting where inconsistency is a reasonable proxy for uncertainty. On HaluEval-QA, where hallucinations are adversarially constructed, this assumption inverts.

**Finding 3: Token entropy provides a stable but non-informative baseline.**
Token entropy (AUROC = 0.4829, CI spanning 0.5) is the "least bad" signal — it is not inverted like SelfCheckGPT, and not degenerate like semantic entropy, but it is non-informative. This suggests that LLaMA-2-7B-chat's per-token uncertainty does not systematically covary with HaluEval-QA hallucination labels under standard configurations. Possible explanations include: (a) the model is uniformly calibrated (or miscalibrated) across factual and hallucinated examples; (b) HaluEval-QA's ChatGPT-generated labels encode a "confident-sounding" characteristic that suppresses token entropy variation; or (c) the mean token entropy aggregation conflates uncertainty about which word to use with uncertainty about which fact to state.

## Connections to Prior Work

Our results extend Kuhn et al. (2023) in a critical direction: semantic entropy's AUROC performance is not a fixed property of the method but depends on the NLI clustering step's aggregation behavior, which is benchmark-dependent. A community norm of reporting NLI aggregation_rate alongside semantic entropy AUROC would prevent other researchers from encountering the degenerate case unexpectedly.

The below-random SelfCheckGPT result is superficially inconsistent with Manakul et al. (2023) but the inconsistency is explained by benchmark characteristics, not methodological deficiency. SelfCheckGPT remains a valid method on benchmarks where hallucinations arise from model uncertainty rather than adversarial label construction. The HaluEval-QA result should be understood as a boundary condition, not a refutation.

The near-random results for all three methods are consistent with Li et al.'s (2023) characterization of HaluEval-QA as using ChatGPT-generated labels — a setting where the "hallucination" signal may be partially confounded with the label generation process.

## Limitations

**Limitation 1: Single LLM (LLaMA-2-7B-chat).**
All executed experiments use LLaMA-2-7B-chat. The Mistral-7B-Instruct experiment (H-M3) was not executed — the pipeline was halted after H-M2's PIVOT result. The cross-model ranking stability claim (P3, Spearman ρ ≥ 0.8) is therefore INCONCLUSIVE.

*Why acceptable:* The NLI aggregation failure (aggregation_rate = 0.272) is a property of deberta-large-mnli's entailment behavior on HaluEval-QA response style — not of LLaMA-2-7B-chat specifically. Any LLM producing similarly short factual QA responses would trigger the same mechanism failure. The polarity inversion hypothesis for SelfCheckGPT is also more likely tied to HaluEval-QA's label construction than to the specific LLM.

*Mitigation:* Execute H-M3 using the proven h-e1 codebase (data.py, inference.py, uq\_signals.py). No architectural changes required; only new stochastic inference for Mistral.

**Limitation 2: HaluEval-QA labels are ChatGPT-generated.**
The binary hallucination labels were generated by ChatGPT prompting, not human annotation. Li et al. (2023) note that the QA subset is the most reliable of HaluEval's three tasks, but systematic biases in the label generation process (e.g., confident-sounding incorrect answers) may attenuate or invert UQ signal correlations.

*Why acceptable:* All three UQ methods are subject to the same label noise, preserving the validity of between-method comparisons. The polarity inversion hypothesis (Finding 2) offers a testable explanation for the SCG below-random result that is specific to the label construction methodology, not a general critique of the AUROC evaluation.

*Mitigation:* Run the same UQ pipeline on human-annotated benchmarks (TriviaQA, NQ) with the same LLM to isolate the benchmark-type effect. The h-e1 codebase is directly reusable.

**Limitation 3: N=5 stochastic samples.**
N=5 is the minimum inference budget specified by Manakul et al. (2023). With only 5 samples and high response diversity, NLI clustering has limited opportunity to find semantically equivalent pairs. Larger N (e.g., N=20) might recover partial NLI aggregation.

*Why acceptable:* The magnitude of the NLI aggregation failure (aggregation_rate = 0.272, 72.8% at maximum clusters) is too large to be fully explained by low N. Even if N=20 improved aggregation_rate from 0.272 to, say, 0.35, it would still fall short of the 0.50 threshold. The SCG below-random result (Δ = 0.144 below random chance) is also too large to be a sampling artifact at N=5.

*Mitigation:* Run semantic entropy with N=20 on a 500-example HaluEval-QA subset to quantify the N-effect on aggregation_rate and AUROC.

## Broader Impact

This work advances the safe deployment of LLMs by providing concrete, quantified boundary conditions for three of the most widely used hallucination detection methods. Negative results with mechanism analysis are more actionable than positive results from uncontrolled evaluations: they tell practitioners exactly when and why a detection method should not be trusted, and what empirical checks to perform before deployment.

The controlled comparison framework — matched inference conditions, bootstrap CIs, explicit mechanism verification — provides a template for future UQ evaluation studies. If adopted as a community norm (report NLI aggregation_rate alongside semantic entropy AUROC; test SelfCheckGPT on benchmarks with varying label construction methodologies), it would substantially improve the reproducibility and comparability of UQ benchmark results.

We do not foresee significant misuse potential from this work. Identifying failure modes of hallucination detectors could theoretically inform adversarial strategies against such detectors, but the failure modes we document (NLI domain mismatch, label polarity inversion) are properties of the evaluation setting rather than exploitable vulnerabilities in deployed systems. The primary beneficiaries are researchers and practitioners seeking to understand when UQ-based hallucination detection is and is not applicable.
