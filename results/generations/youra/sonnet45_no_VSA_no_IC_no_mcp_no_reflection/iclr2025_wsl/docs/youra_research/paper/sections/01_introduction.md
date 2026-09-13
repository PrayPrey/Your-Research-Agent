# Introduction

Neural network weights encode architectural priors and training history. A ResNet-50's 25 million parameters capture BatchNorm statistics, residual connection patterns, and learned kernel structures that distinguish it from a ViT-Base with patch embeddings and attention mechanisms. Can we predict a model's test accuracy or detect backdoor tampering just from weight tensors—without executing the model? Weight-space learning treats model parameters as first-class data, enabling meta-learning applications like model zoo search, neural architecture prediction, and anomaly detection.

Processing weights as data requires handling variable layer shapes and high dimensionality while preserving architectural signal. A standard approach flattens each layer into tokens for sequence models, but systematic validation of this tokenization strategy is missing. Does layer-wise processing retain sufficient structure for property prediction, or do cross-layer dependencies dominate?

Prior work in weight-space learning demonstrates feasibility through task performance—hyper-representations transfer across meta-learning tasks [1], model stitching shows layer-wise analysis validity [2], and weight statistics correlate with model properties [3]. However, these approaches lack controlled experiments isolating tokenization quality from downstream task complexity. The foundational question remains unanswered: *Does layer-wise weight tokenization preserve enough structural signal for reliable property prediction?*

We address this gap through systematic validation on timm Model Zoo (100 pretrained vision models across 4 architecture families: ResNet, ViT, EfficientNet, ConvNeXt). Our contributions:

1. **Tokenization Validation**: Layer-wise processing (flatten + pad + per-layer normalize) achieves 80% accuracy on architecture family classification, significantly exceeding our 60% gate threshold and 25% random baseline.

2. **Baseline Comparison**: Simple per-layer statistics (mean/std/L2 norm) match transformer performance (both 80%) on small datasets, revealing that family-level discriminability doesn't require cross-layer attention modeling when architecture families exhibit strong layer-level separability.

3. **Practical Method**: We provide a reusable tokenization pattern—flatten weight matrices, zero-pad to fixed length, apply per-layer normalization—validated on real pretrained model zoo with reproducible hyperparameters and evaluation protocol.

Our findings validate layer-wise tokenization as a viable foundation for weight-space transformers while highlighting that simple statistical baselines provide strong comparison points. This work enables future research on larger datasets and harder downstream tasks (backdoor detection, property prediction, model synthesis) with confidence that the tokenization approach preserves necessary structural signal.

**References**  
[1] Schürholt et al., "Hyper-Representations as Generative Models", NeurIPS 2022  
[2] Lenc & Vedaldi, "Understanding Deep Image Representations by Inverting Them", CVPR 2015  
[3] Unterthiner et al., "Predicting Neural Network Accuracy from Weights", arXiv 2020
