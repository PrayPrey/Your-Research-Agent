# Introduction

Large language models frequently generate fluent but factually incorrect responses—a phenomenon known as hallucination that undermines their reliability in knowledge-intensive applications. When an LLM confidently states that "Einstein won the 1922 Nobel Prize in Chemistry" rather than Physics, users have no way of knowing the response is wrong without external verification. This problem has motivated extensive research into uncertainty quantification: if we could reliably predict *when* models are likely to hallucinate, we could warn users or abstain from responding entirely.

Two families of uncertainty signals have emerged as promising hallucination detectors. **Token-level entropy**, computed from the model's softmax distribution over next tokens, captures the model's internal uncertainty—when logit distributions are flat (high entropy), the model has low confidence in any particular continuation (Kuhn et al., 2023). **Semantic consistency**, measured by generating multiple responses and computing their pairwise similarity, captures output stability—when the model "knows" an answer, it produces consistent outputs; when hallucinating, outputs diverge (Manakul et al., 2023). A natural hypothesis follows: since these signals capture different failure modes (internal confusion versus output instability), combining them should improve detection.

We test this hypothesis systematically—and find a counterintuitive result. On TriviaQA with Llama-2-7B-chat, semantic consistency alone achieves AUROC=0.81 with a large effect size (Cohen's d=1.19), dramatically outperforming token entropy (AUROC=0.65, d=0.47). More surprisingly, linear fusion of the two signals provides *no improvement* over consistency alone at proof-of-concept scale (N=20). The signals are moderately negatively correlated (r=-0.54), suggesting partial redundancy rather than the complementarity we hypothesized.

## The Problem at Three Levels

**Surface problem:** LLM hallucinations erode trust and cause harm in high-stakes applications including medical question answering, legal document analysis, and educational tutoring. Users cannot distinguish confident-but-wrong outputs from reliable ones.

**Deeper problem:** While multiple uncertainty signals exist, they have been studied in isolation. Kuhn et al. (2023) demonstrated that semantic entropy—entropy computed after clustering responses by meaning—improves calibration. Manakul et al. (2023) showed that self-consistency checking detects factual errors. Xiong et al. (2023) found that models' verbalized confidence is poorly calibrated. Yet no work has directly compared these signals on the same benchmark with the same model, leaving practitioners without guidance on which approach to adopt.

**The gap we address:** Prior work assumes that combining uncertainty signals should help, but this assumption has not been tested. We provide the first systematic comparison of entropy and consistency signals on identical evaluation conditions, and we test whether their combination improves detection. The answer—at least at proof-of-concept scale—is no.

## Key Insight

Our central finding is that **semantic consistency alone is sufficient** for hallucination detection in factual QA, achieving strong discrimination (AUROC=0.81) without requiring entropy computation. This is practically significant: consistency requires only generated text, while entropy requires logit access—excluding API-only models like GPT-4 and Claude. More fundamentally, the failure of linear fusion to improve over consistency alone challenges the intuition that "more signals are better."

We interpret this result through the lens of signal redundancy. The moderate negative correlation (r=-0.54) between entropy and consistency means they partially overlap: questions where the model has high entropy (internal uncertainty) tend to produce low-consistency outputs (unstable responses). This correlation reduces the information gain from combining them.

However, we emphasize an important limitation: our fusion experiments used only N=20 questions due to computational constraints. The grid search for fusion weights may have overfit to this small sample, collapsing to pure consistency (optimal weights: alpha=0, beta=0.1). The complementarity hypothesis is **inconclusive**, not refuted—larger-scale validation is needed.

## Contributions

This paper makes three contributions:

1. **First direct AUROC comparison of entropy and consistency signals** on the same benchmark (TriviaQA) with the same model (Llama-2-7B-chat) under identical evaluation conditions. We find consistency outperforms entropy by 16 percentage points (0.81 versus 0.65).

2. **Quantified effect sizes** demonstrating that consistency is not merely statistically significant but practically meaningful: Cohen's d=1.19 (large effect) versus d=0.47 (moderate) for entropy. This provides actionable guidance for practitioners.

3. **An important negative result:** Linear fusion of entropy and consistency does not improve detection at proof-of-concept scale. This challenges the assumption that combining uncertainty signals provides additive benefit and identifies the entropy-consistency correlation (r=-0.54) as a limiting factor.

Our results suggest that practitioners working on hallucination detection in factual QA should prioritize consistency-based methods. The additional complexity of computing token entropy—which requires logit access and thus excludes commercial API-only models—does not appear justified by improved detection, at least in the regime we tested. Whether non-linear fusion strategies or larger sample sizes can unlock complementary benefit remains open for future work.
