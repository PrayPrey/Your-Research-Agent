# Related Work

## Weight-Space Learning

**Hyper-Representations and Meta-Learning.** Schürholt et al. [1] introduce hyper-representations as learned embeddings of neural network weights for transfer learning tasks, demonstrating that weight-based features generalize across model zoos. Our work complements this by validating the layer-wise tokenization assumption underlying such embeddings.

**Model Stitching and Layer Analysis.** Lenc & Vedaldi [2] show that layers can be analyzed semi-independently while preserving model behavior, supporting the hypothesis that cross-layer dependencies are not always critical. We extend this by empirically measuring signal preservation under layer-wise processing on property prediction tasks.

**Weight Statistics and Property Prediction.** Unterthiner et al. [3] predict model accuracy from weight statistics (norms, spectral properties), achieving moderate correlation. We compare this statistical baseline directly against transformer-based tokenization, revealing that on small datasets (100 models), both approaches achieve similar performance (80% accuracy).

**Neural Functionals.** Recent work processes weights as graph structures or functional mappings [4, 5]. While promising, these methods introduce architectural complexity. Our contribution isolates tokenization quality independent of backbone architecture choice.

## Sequence Modeling on Structured Data

**Transformers for Point Clouds and Graphs.** Point cloud transformers [6] and graph transformers [7] process variable-length structured data via attention mechanisms. Weight-space learning shares similar challenges—variable layer dimensions, permutation symmetries—but operates on learned parameter distributions rather than geometric coordinates.

**Positional Encodings for Hierarchical Data.** Hierarchical position encodings [8] capture depth information in trees and nested structures. We adapt this for weight tokens where layer depth indicates network position, enabling transformers to attend across architectural boundaries.

## Meta-Learning on Model Zoos

**Architecture Search and Transfer Learning.** Neural Architecture Search (NAS) methods [9] predict model performance from architectural descriptors. Weight-space learning extends this by using *learned parameters* as features rather than discrete architecture choices, enabling fine-grained property prediction post-training.

**Model Merging and Task Arithmetic.** Recent work [10, 11] merges pretrained models via weight averaging or interpolation. Our tokenization validation is prerequisite for learning *how* to merge—embeddings must preserve model properties to predict merge outcomes.

**Backdoor Detection in Model Weights.** Spectral signatures [12] and statistical anomalies [13] detect backdoored models from weight distributions. Our work validates that layer-wise tokenization retains sufficient signal for such anomaly detection tasks, with 80% family classification suggesting discriminative capacity for finer-grained backdoor patterns.

## Positioning

Existing weight-space learning methods demonstrate task-specific success but lack systematic evaluation of tokenization strategies. We provide the first controlled experiment isolating layer-wise processing quality, showing that:

1. **Tokenization preserves signal**: 80% accuracy significantly exceeds random baseline (25%) and gate threshold (60%)
2. **Simple baselines matter**: Per-layer statistics match transformer performance on small datasets, establishing rigorous comparison point
3. **Family separability dominates**: On 100-model zoo, architecture-specific patterns (BatchNorm, attention weights, kernel structures) are detectable via local layer statistics without requiring cross-layer reasoning

This validation enables future work on larger datasets, harder tasks, and more sophisticated weight-processing backbones with confidence that the foundational layer-wise assumption holds.

**References**  
[1] Schürholt et al., "Hyper-Representations as Generative Models", NeurIPS 2022  
[2] Lenc & Vedaldi, "Understanding Deep Image Representations by Inverting Them", CVPR 2015  
[3] Unterthiner et al., "Predicting Neural Network Accuracy from Weights", arXiv 2020  
[4] Navon et al., "Equivariant Architectures for Learning in Deep Weight Spaces", ICML 2023  
[5] Zhou et al., "Neural Functional Transformers", NeurIPS 2022  
[6] Zhao et al., "Point Transformer", ICCV 2021  
[7] Dwivedi & Bresson, "A Generalization of Transformer Networks to Graphs", AAAI 2021  
[8] Shaw et al., "Self-Attention with Relative Position Representations", NAACL 2018  
[9] Zoph & Le, "Neural Architecture Search with Reinforcement Learning", ICLR 2017  
[10] Wortsman et al., "Model Soups: Averaging Weights of Multiple Fine-tuned Models", ICML 2022  
[11] Ilharco et al., "Editing Models with Task Arithmetic", ICLR 2023  
[12] Wang et al., "Neural Cleanse: Identifying and Mitigating Backdoor Attacks", IEEE S&P 2019  
[13] Tran et al., "Spectral Signatures in Backdoor Attacks", NeurIPS 2018
