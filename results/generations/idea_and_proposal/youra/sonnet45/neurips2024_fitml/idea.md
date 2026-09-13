# Task-Adaptive LoRA Rank Selection via Gradient Spectrum Analysis

## Motivation
Fine-tuning large language models with LoRA requires expensive hyperparameter searches to determine optimal ranks, costing $150-$2000 per task. Current approaches rely on fixed heuristics (e.g., rank=64) or trial-and-error, wasting 80-90% of computational resources. Existing methods like AdaLoRA adapt ranks during training but cannot predict requirements beforehand. No principled framework exists for *a priori* rank selection based on task properties, creating a critical gap between PEFT efficiency goals and practical deployment costs.

## Main Idea
We propose that fine-tuning tasks possess intrinsic "task bandwidth"—measurable through gradient covariance eigenspectrum effective rank (r_eff)—that determines minimal sufficient LoRA ranks. Inspired by signal processing's Nyquist-Shannon theorem, we hypothesize r_opt ≥ α × r_eff, where α and β are empirically calibrated constants.

Our multi-stage analysis samples gradient spectra at steps {0, 50, 100, 200} to predict layer-specific ranks [r_Q, r_K, r_V, r_FFN] before expensive training. Testing across 60 tasks (BERT to LLaMA-70B), we predict correlation r(r_eff, r_opt) > 0.6, achieving ≥95% of optimal performance while reducing hyperparameter search costs by 5-10×. Heterogeneous layer allocation saves ≥20% parameters versus uniform ranks. This establishes the first information-theoretic foundation for PEFT hyperparameter selection, enabling resource planning and democratizing LLM fine-tuning.