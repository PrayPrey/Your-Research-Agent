# Conclusion

Paraphrasing defeats contamination detection—but does contamination leave a behavioral signature that survives? We investigated the Semantic Saturation Index, measuring confidence uniformity across paraphrases. Our findings are mixed: the underlying mechanism is validated, but the proposed metric fails.

Through controlled experiments on Mistral-7B with MMLU, we demonstrated that contamination creates measurable training exposure (31.1% accuracy gain), diverse training produces representation invariance (MPS difference 0.065, d=0.52), and invariance manifests as confidence uniformity (r=−0.517). The causal chain from contamination to behavioral signature is empirically verified.

However, SSI = 1/variance fails as a practical detector. On real MMLU inference, SSI achieves AUC=0.506—chance-level discrimination. The inverse-variance formulation amplifies noise rather than signal; within-group variance masks between-group differences entirely.

We make three contributions. First, the mechanism chain linking contamination to confidence uniformity is the first empirical demonstration of this behavioral pathway. Second, documenting the metric failure guides future work away from noise-sensitive transforms toward entropy-based or normalized alternatives. Third, identifying the simulation-reality gap—where simulated experiments passed but real inference failed—highlights the need for end-to-end validation in contamination research.

The detection problem remains open. Alternative metrics leveraging the validated mechanism offer a path forward. The signal exists; extracting it requires better engineering.
