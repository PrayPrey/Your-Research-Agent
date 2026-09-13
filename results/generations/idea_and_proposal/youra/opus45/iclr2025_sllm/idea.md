## Title
SAE-Guided Contextual Sparsity: Interpretable Acceleration of LLM Inference via Sparse Autoencoder Feature Importance

## Motivation
LLM inference efficiency and interpretability are typically treated as separate challenges. Contextual sparsity methods (DejaVu, ShadowLLM) achieve speedups by predicting which neurons to skip, but provide no insight into *why* decisions are made. Meanwhile, Sparse Autoencoders (SAEs) decompose activations into interpretable features but haven't been leveraged for efficiency. This gap limits both debugging capabilities and trustworthy deployment. We hypothesize that SAE features, trained for interpretability, also encode task-relevance that correlates with computational importance.

## Main Idea
We propose using pre-trained SAE feature importance scores to guide contextual sparsity decisions during LLM inference. The core mechanism involves: (1) computing gradient-weighted SAE feature importance offline using Gemma Scope SAEs, (2) using these scores as soft weights to bias sparsity predictor outputs, and (3) achieving sparse computation where skipped neurons are traceable to interpretable features.

**Methodology:** We will measure SAE-sparsity correlation (target: r>0.3), accuracy retention on MMLU/HellaSwag (target: ≥98% of dense baseline), inference speedup (target: ≥1.3x), and interpretability (≥80% decisions traceable to ≤5 SAE features).

**Expected Impact:** This bridges efficiency and interpretability research, enabling faster inference with explainable sparsity decisions—critical for trustworthy LLM deployment. Falsification occurs if correlation is negligible or accuracy drops below 95%.