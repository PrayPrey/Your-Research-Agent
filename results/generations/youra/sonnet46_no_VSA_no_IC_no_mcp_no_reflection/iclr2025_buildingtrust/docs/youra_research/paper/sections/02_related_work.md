# Related Work

## Alignment Strategies: DPO and SFT

Supervised Fine-Tuning (SFT) trains language models to imitate demonstration responses
via maximum likelihood on curated instruction-following data [Wei et al., 2022; Chung et al., 2022].
Reinforcement Learning from Human Feedback (RLHF) extends this by training a reward model
on human preference pairs and optimizing via PPO [Ouyang et al., 2022]. RLHF with explicit
truthfulness reward was shown to improve TruthfulQA performance in InstructGPT [Ouyang et al.,
2022], establishing that preference-based alignment can measurably affect truthfulness benchmarks.

Direct Preference Optimization (DPO) [Rafailov et al., 2023] reparameterizes the RLHF
objective to directly fine-tune from preference pairs without a separate reward model, achieving
comparable capability quality to RLHF on MT-Bench and summarization tasks. Critically, the
original DPO evaluation is restricted to capability benchmarks and does not measure fairness
or trustworthiness dimensions. This is the primary gap we fill: DPO's effect on the
multi-dimensional trustworthiness profile — truthfulness, fairness, and robustness — remains
empirically uncharacterized under matched controlled conditions.

## Trustworthiness Benchmarking

TruthfulQA [Lin et al., 2022] evaluates language models on questions where humans commonly
hold false beliefs, using MC2 accuracy over normalized log-probabilities. InstructGPT's
truthfulness improvement [Ouyang et al., 2022] on TruthfulQA motivated the expectation that
preference-based training improves calibrated truthfulness — a prior that our results support
but with DPO rather than RLHF-PPO.

BBQ [Parrish et al., 2022] tests social bias across 9 protected attribute categories using
ambiguous question answering. WinoGender [Rudinger et al., 2018] and WinoGrande [Sakaguchi
et al., 2021] measure gender-pronoun resolution accuracy. Together these benchmarks represent
the fairness-related dimensions on which DPO was theoretically expected to show advantage.

DecodingTrust [Wang et al., 2023] provides the most comprehensive multi-dimensional
trustworthiness evaluation to date, demonstrating that GPT-4 is not uniformly more
trustworthy than GPT-3.5 across 8 dimensions. This partial independence of trustworthiness
dimensions is a precondition for alignment fingerprinting to work — if all dimensions were
perfectly correlated, alignment strategy would add no independent information. However,
DecodingTrust evaluates GPT family models and does not compare alignment strategies within
matched pairs, leaving the DPO vs. SFT comparison unaddressed.

## Model Evaluation and Fingerprinting

HELM [Liang et al., 2022] introduces multi-benchmark correlation as a framework for
comprehensive capability evaluation, showing that model rankings vary substantially across
scenarios. Our work applies a classification framing to the same observation — if benchmark
profiles systematically differ by alignment category, they can serve as fingerprints.
HELM's approach addresses capability; we address alignment-strategy provenance.

Model attribution and fingerprinting have been studied in the context of copyright and
intellectual property [Zhao et al., 2023], typically targeting training data memorization.
Our approach differs fundamentally: we fingerprint alignment *strategy* (not training data
identity) from behavioral benchmarks (not memorized content). To our knowledge, no prior
work applies classification to alignment-strategy detection from standard benchmark profiles.

## Our Position

The existing literature establishes three relevant facts: (1) RLHF preference training
improves truthfulness [Ouyang et al., 2022]; (2) DPO achieves RLHF-comparable capability
[Rafailov et al., 2023]; (3) trustworthiness dimensions are partially independent [Wang et al.,
2023]. Our work combines these into a new question: can alignment strategy (DPO vs. SFT)
be detected from a 4D benchmark profile, and if so, which dimension carries the signal?
This fills the intersection of alignment evaluation and provenance verification that prior
work has not addressed. The answer — yes, from truthfulness rather than fairness — is
informative both for alignment auditing practice and for the theoretical understanding of
what DPO preference training actually optimizes.

---
*Citations requiring verification: Lin et al. (2022) TruthfulQA [arXiv:2109.07958];
Parrish et al. (2022) BBQ [arXiv:2110.08193]; Rafailov et al. (2023) DPO [arXiv:2305.18290];
Wang et al. (2023) DecodingTrust [arXiv:2306.11698]; Ouyang et al. (2022) InstructGPT
[arXiv:2203.02155]; Liang et al. (2022) HELM [arXiv:2211.09110]; Rudinger et al. (2018)
WinoGender [arXiv:1804.09301]; Sakaguchi et al. (2021) WinoGrande [arXiv:1907.10641]*
