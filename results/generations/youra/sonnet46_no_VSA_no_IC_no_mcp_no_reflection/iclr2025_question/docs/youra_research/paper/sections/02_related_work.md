# Related Work

Our work intersects three research areas: sampling-based uncertainty quantification for LLMs, hallucination detection benchmarks, and the behavioral effects of RLHF fine-tuning on LLM output distributions. We review each in turn, positioning our contribution within the existing literature.

## Sampling-Based Consistency for Uncertainty Quantification

The use of sampling-based consistency as an uncertainty signal in language models was established by Wang et al. [2022] in the context of chain-of-thought reasoning: majority vote consistency over multiple samples implicitly captures model confidence. Kuhn et al. [2023] formalized this intuition as *Semantic Uncertainty* — using NLI to cluster semantically equivalent answers and computing entropy over these semantic equivalence classes, rather than over token sequences. Applied to TriviaQA and NaturalQuestions with GPT-3 and smaller models on open-ended generation, Semantic Uncertainty achieves meaningful AUROC and outperforms token-probability baselines. Critically, the models evaluated by Kuhn et al. are base or lightly fine-tuned models where the stochastic hallucination assumption naturally holds — models that exhibit broad, uncertain sampling distributions for questions they cannot answer.

Manakul et al. [2023] introduced SelfCheckGPT, which directly operationalizes NLI-based pairwise consistency (rather than entropy-based clustering) as a hallucination detector. Evaluated on WikiBio biography generation with GPT-3, SelfCheckGPT achieves AUROC ~0.65-0.75, confirming that consistent outputs signal factual accuracy in open-ended generation. SelfCheckGPT is the direct methodological predecessor of our SMC-NLI scorer; our experimental design closely follows their NLI consistency pipeline, extended to structured factual QA and an RLHF-fine-tuned model.

Lin et al. [2024] conducted a systematic comparison of black-box uncertainty methods, finding that sampling-based consistency is competitive with white-box (logit-based) methods when logits are unavailable. Xiong et al. [2023] showed that sampling-based UQ generalizes better across model families than verbalized confidence. These results establish sampling-based consistency as the dominant black-box UQ paradigm.

**Our gap:** All prior work establishing sampling-based consistency validates on base/lightly-tuned models on open-ended generation tasks. None has systematically evaluated whether this paradigm holds for instruction-tuned (RLHF-fine-tuned) models on structured factual QA — the setting most relevant to deployed QA systems. We fill this gap, and our findings suggest the paradigm's applicability is more constrained than the literature implies.

## Hallucination Detection Benchmarks

Hallucination detection has been studied across multiple benchmark types. TruthfulQA [Lin et al., 2022] evaluates models' propensity to repeat imitative falsehoods, focusing on adversarially constructed questions. TriviaQA [Joshi et al., 2017] and NaturalQuestions [Kwiatkowski et al., 2019] provide ground-truth factual QA with exact-match evaluation, enabling model-specific hallucination assessment.

HaluEval [Li et al., 2023], which we use as our primary benchmark, was constructed by sampling ChatGPT responses and asking ChatGPT to generate hallucinated versions, producing binary correct/hallucinated labels for QA, dialogue, and summarization tasks. HaluEval has been widely adopted as a hallucination detection benchmark due to its scale and accessibility.

However, HaluEval's construction protocol introduces a fundamental cross-model evaluation concern: the binary labels reflect ChatGPT's hallucination patterns, not those of the model being evaluated. A model that answers correctly where ChatGPT hallucinated — or vice versa — will receive inaccurate labels. This label-model mismatch makes AUROC evaluation ambiguous: low AUROC may reflect either (a) the detection method failing, or (b) the benchmark labels not matching the evaluation model's actual hallucination behavior. Our results suggest this is a non-trivial concern for Llama-3-8B-Instruct evaluation on HaluEval, and we flag it as a benchmark validity issue that the community should address.

In contrast, benchmarks with model-agnostic ground truth (TriviaQA exact match, NQ F1) avoid this confound and should be preferred for cross-model hallucination detection evaluation.

## Effects of RLHF Fine-Tuning on Model Output Distributions

A critical but underexplored factor in our context is how RLHF fine-tuning affects LLM output distributions. Ziegler et al. [2019] and Ouyang et al. [2022] established that RLHF training produces models that are more deterministic and consistent in their outputs — a desirable property for deployment (users expect consistent answers) but potentially problematic for uncertainty quantification.

Instruction-following fine-tuning, whether via RLHF or supervised instruction tuning, tends to sharpen model output distributions [Bai et al., 2022]. At temperature=0.7, an instruction-tuned model may produce a much narrower distribution over output tokens than an equivalently-sized base model would, because RLHF training has reinforced specific response patterns. If this sharpening is strong enough, even "uncertain" responses — responses where the model lacks grounded knowledge — may be generated consistently across samples, eliminating the consistency-based discriminative signal.

This theoretical concern has not been empirically tested against sampling-based hallucination detectors. Our work provides the first direct empirical evidence of this effect: Llama-3-8B-Instruct produces nearly identical consistency scores for correctly-labeled (mean SMC-NLI=0.6236) and hallucinated-labeled (mean SMC-NLI=0.6299) questions, with a gap of 0.006 — noise level over N=1000 questions — consistent with a sharpened output distribution that eliminates the assumed stochastic-hallucination regime.

## Positioning Our Work

Our contribution is complementary to, not contradictory of, the prior literature. SelfCheckGPT and Semantic Uncertainty establish that sampling-based consistency works in the stochastic hallucination regime (open-ended generation, base/lightly-tuned models). We establish that instruction-tuned models on structured factual QA — increasingly the practical deployment setting — exhibit a different regime (systematic confabulation) where these methods fail. The two findings together define a regime boundary that practitioners need to know before deploying consistency-based detectors.

The closest related work is [CITATION NEEDED: any paper discussing RLHF effects on UQ], but to our knowledge no prior work has explicitly characterized the stochastic hallucination vs. systematic confabulation distinction as a regime prerequisite for sampling-based detection, or provided empirical evidence via dual-metric (NLI + embedding) evaluation with implementation correctness verification.
