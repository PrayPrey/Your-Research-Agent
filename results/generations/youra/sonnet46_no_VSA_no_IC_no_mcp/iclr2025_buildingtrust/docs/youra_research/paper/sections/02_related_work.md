# Related Work

Our work sits at the intersection of three research threads: calibration measurement for language models, adversarial NLP benchmarks, and RLHF alignment's effect on model behavior. Each thread is mature in isolation, but no prior work addresses their combination under controlled adversarial conditions with open-weight models.

## Calibration of Neural Networks and LLMs

Expected Calibration Error (ECE) was formalized by Guo et al. [2017] as the weighted average gap between predicted confidence and empirical accuracy across equal-width confidence bins. They demonstrated that modern neural networks (ResNets, DenseNets) are systematically overconfident and that temperature scaling — rescaling logits by a single learned scalar — reliably reduces ECE without affecting accuracy. ECE has since become the standard calibration metric across NLP and computer vision.

Minderer et al. [2021] extended this analysis to distribution shift in vision models, showing that ECE *increases* under standard corruptions (ImageNet-C) and out-of-distribution benchmarks (ObjectNet) even for models with good clean-data calibration. Their key finding — that distribution shift degrades calibration — is widely cited as motivation for adversarial calibration concern. Our results complicate this picture: adversarial distribution shift in NLP does not uniformly degrade calibration, and the construction method of the adversarial benchmark determines whether calibration improves or worsens.

Kadavath et al. [2022] measured calibration of large language models using verbal probability elicitation on factual QA tasks, finding that RLHF-aligned models show better self-knowledge calibration than base models on clean benchmarks. This finding motivates our comparison of base and chat variants — but we test it in the adversarial setting that Kadavath et al. did not examine. Our finding of an alignment tax on AdvGLUE (chat worse than base) is not anticipated by clean-benchmark results and represents a genuinely new behavioral observation.

Xiong et al. [2023] studied LLM confidence elicitation through verbal uncertainty expressions, showing that models can express calibrated uncertainty when directly asked. Zhao et al. [2023] measured generation-based ECE (using sampling probabilities rather than logit-based ECE) for instruction-tuned LLMs. Neither work measures logit-based ECE on adversarial benchmark splits, which is our focus. Logit-based ECE is methodologically distinct from generation-based calibration: it is computed directly from answer-token probability distributions, does not require verbalization, and is available for any model with logit access.

**Gap:** No prior work measures logit-based ECE on adversarial NLP benchmark splits for open-weight LLMs.

## Adversarial NLP Benchmarks

Wang et al. [2021] introduced AdvGLUE, a multi-task adversarial benchmark constructed by applying human-designed perturbation methods (synonym substitution, word insertion, contextual perturbation) to GLUE examples to create inputs that preserve labels but cause model errors. AdvGLUE includes NLI (MNLI), paraphrase (QQP), and sentiment (SST-2) tasks, with accuracy drops of 15–30% for state-of-the-art models. AdvGLUE measures accuracy robustness only; calibration is not measured.

Nie et al. [2020] introduced ANLI (Adversarial NLI), constructed using a human-and-model-in-the-loop protocol: human annotators write NLI hypotheses that fool the current model, which is then retrained on the collected data for the next round. This produces three rounds of increasing difficulty (R1 < R2 < R3 in adversarial challenge). ANLI is a model-in-the-loop benchmark — the adversarial examples are specifically selected to be difficult for *the training model at each round* — which makes it fundamentally different from AdvGLUE's human-only construction.

The distinction between human-adversarial (AdvGLUE) and model-in-the-loop adversarial (ANLI) construction is not typically highlighted in papers that use both benchmarks for accuracy evaluation. We elevate it to a primary independent variable, because we observe that this distinction determines whether calibration degrades or improves under adversarial conditions. This is our main methodological observation about adversarial benchmark design.

BIG-Bench Hard [Suzgun et al., 2022] provides multi-step reasoning tasks with adversarial variants; while we originally planned to include BBH-MC in our analysis, scope constraints limited us to NLI and binary classification. We leave BBH-MC adversarial calibration to future work.

**Gap:** Adversarial benchmarks are used exclusively for accuracy evaluation; no prior work treats adversarial construction method as a variable in calibration analysis.

## RLHF Alignment and Calibration

Reinforcement Learning from Human Feedback (RLHF) [Christiano et al., 2017; Ouyang et al., 2022] fine-tunes language models to align with human preferences, producing "chat" or "instruct" model variants. The effect of RLHF on model calibration has been studied primarily on clean benchmarks. Kadavath et al. [2022] found that RLHF models show better self-reported calibration; Openai's GPT-4 technical report [OpenAI, 2023] notes calibration improvements from RLHF training. The conventional expectation is that RLHF uniformly improves or maintains calibration.

We test this expectation in the adversarial setting for the first time. Our finding — that RLHF moderation of adversarial calibration degradation is benchmark-type conditional — is not predicted by clean-benchmark RLHF calibration findings. On model-in-loop adversarial benchmarks (ANLI), RLHF consistently moderates calibration degradation (100% of rounds). On static human-adversarial benchmarks (AdvGLUE), RLHF exacerbates calibration degradation (alignment tax: ΔΔECE = −0.026). This interaction is a new empirical contribution that refines the understanding of when RLHF helps calibration robustness.

The alignment tax we document is consistent with concerns raised by Askell et al. [2021] and others that RLHF training can produce models that are confidently helpful — potentially at the cost of uncertainty calibration in adversarial settings designed to exploit instruction-following behavior.

**Gap:** RLHF's effect on calibration has been studied only on clean benchmarks; adversarial calibration moderation by RLHF is untested.

## Positioning

Our work occupies the intersection of these three threads: we apply calibration measurement (ECE, logit-based) to adversarial NLP benchmarks (AdvGLUE, ANLI) for open-weight LLMs with and without RLHF alignment. We find that the intuitions from each individual thread — distribution shift degrades calibration, adversarial benchmarks expose model failures, RLHF improves calibration — interact in non-obvious ways when combined. The conditional pattern we document (construction method × task type × RLHF) cannot be derived from any single thread and motivates adversarial calibration measurement as a distinct research problem.
