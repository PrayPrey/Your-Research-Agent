# Discussion

Our experiments validate that task-conditioned conversion preserves adaptation capability in sub-quadratic architectures. We discuss key findings, limitations, and implications.

## Key Findings

**The efficiency-adaptation tradeoff is not fundamental.** TC-SSM achieves 0.25% accuracy gap with 0.85× overhead—both better than thresholds set for acceptable tradeoffs. This suggests that the apparent conflict between sub-quadratic efficiency and adaptation capability stems from how conversion is performed, not from architectural constraints.

**Self-supervised task discovery works.** Cluster purity of 0.74 confirms that meaningful task structure exists in pretrained hidden states. This enables TC-SSM to condition on task identity without requiring task labels during conversion—important for practical deployment where conversion data may be unlabeled.

**Task conditioning can be computationally free.** The sub-unity overhead (0.85×) was unexpected. We hypothesize this results from improved memory bandwidth utilization: task embeddings are small (32-dimensional), cached, and reused across all sequence positions. Comprehensive modulation (all matrices) outperforms selective modulation (delta-only), suggesting that well-designed conditioning improves rather than degrades efficiency.

**The complete mechanism chain is verified.** Each stage—clustering discovers structure, embeddings encode patterns, modulation conditions dynamics, training preserves adaptation—is individually validated with margins exceeding thresholds by 2-20×. This provides confidence that TC-SSM works through the proposed mechanism rather than through confounding factors.

## Limitations

**Single model scale.** All experiments use BERT-base (110M) to Mamba-130M conversion. We cannot claim results generalize to larger scales (1B+), where different phenomena may emerge. The parameter-efficient nature of task conditioning (1.01× parameters) suggests favorable scaling, but this requires empirical validation.

**SuperGLUE classification only.** Our evaluation covers NLU classification tasks. Generation, reasoning, and multimodal tasks remain untested. The adaptation preservation mechanism is general, but task discovery quality may vary across domains.

**Sample imbalance effects.** Embedding quality correlates with training data size. Small tasks (CB: 56 samples, COPA: 100) achieve 0% individual linear probe accuracy despite contributing to overall discriminability. TC-SSM may underperform on rare or novel task types where few examples exist for contrastive learning.

**Memory bandwidth hypothesis unverified.** Our explanation for sub-unity overhead remains hypothetical. Roofline analysis and FLOPs profiling would provide stronger evidence, but fall outside our current scope.

## Broader Impact

TC-SSM enables efficient deployment of adaptable models, potentially democratizing access to capable NLP systems on resource-constrained hardware. Sub-quadratic complexity with preserved adaptation allows single models to serve diverse tasks efficiently.

However, more efficient models may accelerate deployment in contexts where careful oversight is warranted. Task conditioning without explicit task labels could enable adaptation to unintended task distributions. We recommend evaluation protocols that assess behavior across diverse task types before deployment.

The self-supervised nature of task discovery raises questions about what structures models learn to condition on. Further interpretability work could illuminate whether discovered task clusters align with human-meaningful categories or capture spurious statistical patterns.
