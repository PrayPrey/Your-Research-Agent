# Conclusion

We began with an apparent tradeoff: converting transformers to sub-quadratic architectures discards few-shot adaptation capability. This paper shows the tradeoff is not fundamental—it stems from how conversion is performed, not from architectural constraints.

TC-SSM integrates task conditioning directly into the conversion process, preserving the adaptation manifold rather than attempting to recover it post-hoc. Our approach makes three contributions. First, we demonstrate that self-supervised clustering discovers meaningful task structure in pretrained hidden states (purity 0.74 versus 0.20 random), enabling task conditioning without labeled data. Second, we show that low-rank modulation of SSM parameters adds negligible overhead—counterintuitively, TC-SSM runs at 0.85× vanilla Mamba inference time. Third, we validate that integrated task conditioning preserves adaptation: TC-SSM achieves 0.25% accuracy gap versus transformer baseline while adapting in just 14 gradient steps, exceeding both thresholds by substantial margins.

## Future Directions

Our results open several promising research directions, each grounded in specific experimental findings.

**Understanding the efficiency gain.** The sub-unity overhead (0.85×) was unexpected. We hypothesize memory bandwidth efficiency from batched task conditioning, but roofline analysis would provide definitive evidence. If confirmed, this mechanism could guide design of other efficient conditioning methods.

**Addressing sample imbalance.** Small tasks (CB, COPA, WSC) achieved 0% individual probe accuracy despite contributing to overall embedding discriminability. Balanced sampling or few-shot augmentation during contrastive training could improve task embedding quality for rare task types.

**Scaling validation.** Our experiments use BERT-base (110M) to Mamba-130M conversion. The parameter-efficient nature of task conditioning (1.01× overhead) suggests favorable scaling, but 1B+ scale experiments would confirm whether the mechanism transfers.

**Beyond classification.** SuperGLUE focuses on NLU classification. Extending TC-SSM to generation tasks (summarization, translation) and reasoning benchmarks would establish broader applicability.

The efficiency-adaptation tradeoff has shaped how practitioners think about model deployment. Our work suggests this constraint can be engineered away through co-design of conversion and adaptation. We hope TC-SSM encourages further research into what other capabilities can be preserved—not despite sub-quadratic efficiency, but alongside it.
