# Title
Provably Robust Watermark Detection via Randomized Smoothing: A Unified Certification Framework for Generative AI

# Motivation
As generative AI proliferates, regulations like the EU AI Act and California AB 3211 mandate watermarking for synthetic content. However, existing watermark detectors lack formal robustness guarantees against adversarial attacks, limiting their reliability for high-stakes applications like deepfake detection and IP protection. Current approaches provide only empirical robustness without mathematical guarantees, creating a critical gap between regulatory requirements for auditable security and available technology. This research addresses the need for certifiable watermark detection across all generative AI modalities.

# Main Idea
We propose adapting randomized smoothing—a technique from adversarial robustness—to provide the first provable ℓ₂ robustness certificates for neural watermark detectors. The core mechanism: inject Gaussian noise during detection, use Monte Carlo sampling to estimate class probabilities, then compute a certified radius guaranteeing detection success against any perturbation within that radius. The key innovation is adaptive variance selection that optimizes the accuracy-robustness trade-off across images, text, audio, and video.

We will validate that: (1) certified radius ≥0.15 with ≥85% accuracy is achievable, (2) certification guarantees hold empirically (≥95% attack resistance within certified radius), and (3) the framework generalizes across modalities with <20% variance. This enables the first auditable, regulation-compliant watermarking system with mathematical security guarantees.