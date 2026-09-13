# Title
Adaptive State Compression for Length-Robust Sequence Models via Information Bottleneck Training

# Motivation
State space models (SSMs) like Mamba show promise for efficient sequence modeling but struggle with length generalization—models trained on short sequences fail dramatically on longer ones. Current solutions require expensive post-training interventions or training on maximum-length sequences. This research addresses a fundamental gap: can we train SSMs to inherently generalize across sequence lengths by systematically expanding their state distribution coverage during training, rather than relying on post-hoc fixes?

# Main Idea
We hypothesize that training SSMs with learnable information bottleneck layers—progressively varying compression rates from α=0.9 to α=0.3—forces models to learn compact, length-robust state representations. The causal mechanism operates through compression-induced state distribution expansion: tight bottlenecks simulate the state budget constraints of longer sequences, while progressive schedules expose models to diverse compression regimes during training. This creates minimal sufficient statistics that transfer across lengths.

We will test this on Mamba architectures across language and vision tasks, measuring length extrapolation accuracy (2k→128k tokens) against vanilla training and existing post-training methods. Key predictions: ≥5% accuracy improvement at 4× length extrapolation with <10% training overhead. Cross-domain validation on vision tasks (64×64→256×256 resolution) will verify the mechanism's generality. This training-time solution offers a principled, efficient alternative to current length generalization approaches.