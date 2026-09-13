# Research Idea

## Title
Multi-Scale Perceptual Information Bottleneck for Unified Rate-Distortion-Perception Optimization in Neural Image Compression

## Motivation
Neural image compression has achieved remarkable progress, yet navigating the three-way tradeoff between rate, distortion, and perceptual quality remains challenging. Current methods either optimize pixel-wise metrics (yielding blurry reconstructions) or require complex GAN-based training for perceptual quality. A fundamental gap exists: can information-theoretic principles directly optimize for human perception? This research addresses whether computing the information bottleneck objective in perceptual feature space—rather than pixel space—enables unified R-D-P optimization through a single control parameter.

## Main Idea
We hypothesize that applying the variational information bottleneck (VIB) objective in multi-scale VGG feature space (conv1-5) causes encoders to preserve perceptually-relevant information (edges, textures, semantics) while discarding imperceptible details. The causal mechanism operates through three steps: (1) hierarchical VGG features capture human visual similarity, (2) multi-scale computation smooths the loss landscape, and (3) stable optimization enables single-parameter β to navigate the entire R-D-P surface.

We will modify CompressAI's hyperprior architecture to minimize L_PIB = R(z) + β·D_perceptual, sweeping β ∈ [0.001, 0.1]. Success requires achieving LPIPS ≤ 0.04 at 0.15 BPP on Kodak (matching HiFiC) with monotonic β-LPIPS relationship. This approach could simplify perceptual compression by eliminating adversarial training while providing theoretical grounding through information-theoretic principles.