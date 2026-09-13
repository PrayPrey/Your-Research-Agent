# Introduction

A neural network that achieves 99% predictive accuracy can fundamentally misunderstand the structure of its input—learning the right answers through the wrong mechanism. This counterintuitive finding lies at the heart of understanding when architectural inductive biases are essential versus merely convenient.

Weight-space learning—predicting model properties directly from weight tensors—has emerged as a promising paradigm for tasks ranging from accuracy prediction to model quality assessment [Schürholt et al., 2022]. Central to this paradigm is the question of how to handle permutation symmetries: the weights of a neural network can be permuted across hidden neurons without changing the function it computes. Permutation-equivariant architectures like Neural Functional Networks (NFN) [Zhou et al., 2023] explicitly encode this symmetry, while standard MLPs must learn it from data.

The conventional wisdom holds that with sufficient data diversity, non-equivariant architectures should eventually learn to exploit these symmetries. After all, if the training distribution contains many permuted versions of similar weight configurations, an MLP should discover that permutation-related weights map to similar properties. This assumption has profound implications: if true, architectural inductive biases become a matter of convenience (improving sample efficiency) rather than necessity.

We challenge this assumption through systematic experiments across data scales from 1K to 40K models. Our key finding contradicts the "data teaches invariance" hypothesis: **MLPs trained on 40K models achieve near-perfect predictive accuracy (R²=0.99) but fail to develop permutation invariance (0.63 vs NFN's 1.0)**. This dissociates task performance from mechanism—high accuracy can coexist with fundamentally incorrect representations that exploit dataset-specific position-accuracy correlations rather than semantic weight structure.

This insight reveals that permutation invariance must be built in architecturally; it cannot be learned from data regardless of scale. The implications extend beyond weight-space learning: certain symmetries may require explicit architectural encoding, with data quantity unable to substitute for structural inductive bias.

Our contributions are threefold:

1. **Sample Efficiency of Equivariance:** We demonstrate that NFN achieves R²=0.95 at N=1K while matched-capacity MLPs achieve only R²=0.35—a 60 percentage point advantage that far exceeds expected margins, establishing the practical value of equivariant architectures in data-limited regimes.

2. **Mechanism Verification:** We develop a probe invariance test that measures whether models develop permutation-invariant representations. Using this test, we show that NFN's invariance is mathematically perfect (deviation < 1.19e-07 across permutations) while MLP invariance plateaus at 0.63 even at N=40K.

3. **Falsification of Learned Invariance:** We provide the first direct evidence that MLPs cannot learn permutation invariance from data diversity. Despite achieving R²=0.986 at large scale, MLPs learn position-sensitive statistics rather than permutation-invariant representations.

We organize the paper as follows: Section 2 reviews related work on weight-space learning and equivariant architectures. Section 3 describes our methodology including NFN architecture and the probe invariance test. Sections 4-5 present experimental setup and results. Section 6 discusses implications and limitations. Section 7 concludes with future directions.
