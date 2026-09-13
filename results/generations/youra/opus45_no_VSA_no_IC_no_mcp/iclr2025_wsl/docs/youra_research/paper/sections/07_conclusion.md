# Conclusion

We began by observing a counterintuitive finding: two architectures designed for the same purpose—processing neural network weights while respecting permutation symmetry—produce measurably different internal representations, yet this difference translates to performance advantages only for global statistics tasks, not for local anomaly detection. This partial confirmation provides the first empirical guidance for practitioners selecting weight-space architectures.

## Summary

In this work, we addressed the absence of systematic comparison between permutation-equivariant weight-space architectures by quantifying their inductive bias differences and testing task-dependent performance advantages.

Our main contributions are:

1. **First quantitative measurement of inductive bias differences:** We demonstrated that DWS produces more localized weight updates (CoV 1.44) compared to NFT's more uniform processing (CoV 1.35)—a 7% difference that operationalizes the abstract concept of "locality vs global attention."

2. **Empirical confirmation of task-dependent advantage:** NFT's global attention yields 12.3% better accuracy prediction (RMSE 82.9 vs 94.5), while the hypothesized DWS locality advantage on backdoor detection remains plausible but unverified due to experimental design limitations.

3. **Methodology for architecture comparison:** Our controlled 2×3 factorial design isolating architecture-task interactions provides a template for future weight-space architecture comparisons.

## Future Directions

This work opens several promising directions grounded in our experimental findings:

**Testing Untested Alternative Explanations:** Our experiments could not determine whether NFT's attention can learn locality given sufficient training. Future work should train NFT with constant learning rates for extended epochs on challenging tasks to test whether the inductive bias difference narrows with scale.

**Verifying Unconfirmed Assumptions:** The assumption that backdoor triggers manifest as localized weight anomalies remains unverified. Analyzing real TrojAI backdoored models for the spatial structure of weight changes would either validate DWS's locality advantage or reveal that a different mechanism is needed.

**Extending Scope:** The findings on CNN weight-spaces may extend to Transformer weight-spaces, potentially providing architecture selection guidance for analyzing fine-tuned language models. Additionally, sample efficiency curves on challenging datasets where architectures do not immediately reach ceiling performance would complete the task-dependence story.

## Closing Remarks

Our findings suggest that the right tool for the right job matters in weight-space learning: architecture selection should consider how inductive biases align with task characteristics. As the field of neural network analysis continues to evolve, understanding what different architectures capture—and what they miss—will become increasingly important for building reliable model analysis tools.
