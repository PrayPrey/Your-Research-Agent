# Title
SAE-Guided Activation Steering: Interpretable and Capability-Preserving Control of Foundation Models

# Motivation
Foundation models risk generating harmful, biased, or factually incorrect content. Existing intervention methods face a critical trade-off: heuristic approaches (like SafeSteer) achieve control but lack interpretability for debugging failures, while probe-based methods provide some interpretability but don't guarantee capability preservation. No current framework systematically integrates mechanistic interpretability into intervention design with validated multi-objective control. This creates deployment risks when interventions cause unintended capability degradation or fail unpredictably across different control objectives.

# Main Idea
We propose using sparse autoencoder (SAE) features as the foundation for designing activation steering interventions. Our three-phase framework: (1) discovers monosemantic, causally-relevant features via SAE training and activation patching validation, (2) computes steering vectors in interpretable feature space rather than raw activations, and (3) monitors feature activations during generation to detect unintended effects early. 

The core mechanism: SAE features provide interpretable control dimensions that enable systematic intervention design and transparent validation, unlike black-box alternatives. We test across safety, factuality, and style objectives on GPT-2-large/LLaMA-7B, comparing against SafeSteer and probe-only baselines.

Expected outcomes: equivalent control effectiveness (≥80% toxicity reduction) with superior capability preservation (≥98% MMLU retention vs. 97% baseline) and significantly higher expert-rated interpretability (≥4.0/5.0 vs. ≤3.0/5.0). This enables debuggable, multi-objective model control suitable for production deployment.