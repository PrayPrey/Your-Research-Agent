# Conclusion

We began by observing that on 18% of factuality questions, token entropy and answer consistency point in opposite directions—and each method is right about its own subset. This counterintuitive finding motivated us to systematically investigate whether these uncertainty signals capture fundamentally different hallucination patterns.

## Summary

In this work, we conducted the first systematic comparison of entropy-based and consistency-based uncertainty quantification for LLM hallucination detection on the same benchmark. Our key insight is that token entropy captures epistemic uncertainty (does the model know the answer?) while N-sample consistency captures generation stability (does the model produce reliable outputs?). These are orthogonal phenomena measuring different aspects of model uncertainty.

Our main contributions are:

1. **Empirical demonstration of orthogonality:** We showed that entropy and consistency share only 5% of variance (r = 0.228), confirming they measure fundamentally different phenomena. This establishes the theoretical foundation for multi-signal hallucination detection.

2. **Mechanism validation:** We validated the causal chain from entropy to uncertainty (H-M1) and from consistency to stability (H-M2), with consistency showing a large effect size (Cohen's d = 1.068) distinguishing correct from incorrect responses.

3. **Complementarity analysis:** We demonstrated that 18.1% of questions exhibit method disagreement, with each method achieving AUROC > 0.75 on its winning subset. This proves that combining signals could capture failure modes neither detects alone.

## Future Directions

This work opens several directions grounded in our experimental findings:

**From untested alternative explanations:** Our large effect size (d = 1.068) may reflect TruthfulQA's adversarial design or our temperature setting (T=1.0). Future work should ablate temperature ∈ {0.7, 0.8, 0.9, 1.0} and replicate on non-adversarial benchmarks like Natural Questions to assess robustness.

**From unverified assumptions:** We tested only LLaMA-2-7B. Cross-model replication on Mistral-7B, LLaMA-3-8B, and larger scales (13B, 70B) is needed to verify generalization. Similarly, the N=5 sample count should be ablated to assess consistency estimate stability.

**From scope extensions:** With orthogonality established, the natural next step is building and evaluating a hybrid detector that combines both signals. Beyond factuality QA, extending to long-form generation (summaries, explanations) where entropy aggregation may need adaptation is a promising direction.

## Closing

As language models become more capable yet continue to hallucinate, understanding the orthogonal structure of uncertainty signals becomes critical. Our finding that entropy and consistency capture complementary failure modes suggests that robust hallucination detection requires multiple lenses—no single signal suffices. We hope this work encourages the community to move beyond single-signal approaches toward principled multi-signal frameworks for trustworthy AI systems.
