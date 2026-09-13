# Related Work

## Alignment Evaluation Benchmarks

Current alignment evaluation infrastructure focuses predominantly on AI-to-human alignment. RewardBench \citep{Lambert2024} evaluates reward models on preference prediction across chat, safety, and reasoning domains, establishing a benchmark for RLHF quality assessment. AlignBench \citep{AlignBench2024} provides Chinese-language alignment evaluation with fine-grained capability assessment. PERSONA \citep{PERSONA2024} introduces pluralistic alignment by testing whether models can serve diverse user profiles. These benchmarks share a common assumption: alignment success means the AI accurately predicts and satisfies human preferences.

What these benchmarks do not measure is whether AI responses support or undermine human agency. A response that perfectly matches stated preferences may still lead to cognitive offloading, reduced critical evaluation, or inappropriate reliance. This asymmetry motivates our investigation into whether preference data contains extractable signals orthogonal to reward prediction.

## Human Agency in AI Systems

The concept of agency-preserving AI has emerged from both AI safety and human-computer interaction research. Mitelut et al. \citep{Mitelut2023} provide a formal framework for understanding how intent-aligned AI systems can deplete human agency by removing decision-making friction that serves epistemic purposes. They argue that AI safety research must incorporate "agency foundations" — ensuring AI systems preserve human autonomy even when this conflicts with immediate helpfulness.

HumanAgencyBench \citep{HumanAgencyBench2024} operationalizes this concern with six measurable dimensions: clarifying ambiguity, presenting options, epistemic hedging, explicit deferral, supporting user reasoning, and avoiding cognitive shortcuts. Their 60,000-row dataset enables LLM-as-judge evaluation of agency preservation, though it has not been integrated with mainstream alignment benchmarks. We adapt four of these dimensions — clarifying questions, option enumeration, epistemic hedging, and explicit deferral — as computable proxies for our BAI computation.

## Bidirectional Alignment Framework

Shen et al. \citep{Shen2024} synthesize concerns about unidirectional alignment into a Bidirectional Alignment Framework. Their systematic review of 400+ papers demonstrates that the field overwhelmingly focuses on AI→Human alignment while neglecting Human→AI alignment dimensions: human agency preservation, appropriate reliance, and critical evaluation capability. They propose that complete alignment requires both directions, but acknowledge that operationalization and measurement remain open problems.

Our work directly addresses this operationalization gap. Rather than proposing new data collection, we investigate whether existing preference datasets already encode agency-related variance that can be extracted and validated independently of reward signals.

## Adversarial Probing for Representational Analysis

Gradient reversal training, introduced by Ganin and Lempitsky \citep{Ganin2015} for domain adaptation, provides a method for isolating orthogonal representational components. By training a probe to minimize predictability of one feature while preserving another, gradient reversal can disentangle entangled representations. This technique has been applied to remove protected attributes from embeddings, isolate stylistic from semantic content, and separate task-relevant from task-irrelevant variance.

We apply gradient reversal to investigate whether BAI occupies a representationally independent subspace from reward prediction. If BAI information survives gradient reversal designed to remove reward-predictive variance, this provides evidence for orthogonality beyond simple correlation analysis.

## Data Quality in RLHF

Recent work has highlighted quality issues in commonly-used preference datasets. Xu et al. \citep{Xu2024} identify systematic biases in HH-RLHF including length preferences, safety-helpfulness tradeoffs, and annotator disagreement patterns. These artifacts suggest that any signal extracted from preference data — including our BAI proxies — may reflect dataset characteristics rather than meaningful alignment constructs. Our semantic coherence analysis (H-C1) directly tests whether BAI captures interpretable content or dataset artifacts.
