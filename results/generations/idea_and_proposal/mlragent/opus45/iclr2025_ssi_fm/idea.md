# Title: Curriculum-Aware Verifier Ensembles for Robust Self-Improvement

## Motivation
A critical bottleneck in self-improvement is the reliance on learned verifiers/reward models that can fail arbitrarily, leading to model collapse when errors compound over training iterations. Unlike RL with ground-truth rewards, self-improvement must navigate unreliable feedback signals. Current approaches treat verifier errors as noise, but verifier reliability varies systematically—easier problems are verified more accurately than harder ones. This insight remains unexploited, creating a gap between theoretical self-improvement potential and practical outcomes.

## Main Idea
I propose a **curriculum-aware ensemble verification framework** that dynamically weights multiple diverse verifiers based on estimated problem difficulty and historical verifier agreement patterns. The methodology involves:

1. **Difficulty-stratified verification**: Train verifiers on different difficulty distributions, creating specialists for easy vs. hard generations.

2. **Agreement-based confidence estimation**: Use inter-verifier disagreement as an uncertainty signal—high disagreement triggers conservative acceptance thresholds or human deferral.

3. **Adaptive curriculum**: Prioritize self-training on examples where verifier confidence is high, gradually expanding to harder problems as the model improves.

4. **Verifier co-evolution**: Periodically retrain verifiers on accepted generations, with regularization to prevent drift toward the generator's biases.

Expected outcomes include provably reduced collapse rates and sustained improvement curves beyond current methods. This bridges theoretical verification-generation gaps with practical algorithmic design.