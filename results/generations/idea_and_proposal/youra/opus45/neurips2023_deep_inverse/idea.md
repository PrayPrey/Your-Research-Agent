# Research Idea

## Title
Geometry-Aware Modular Diffusion Priors for Cross-Modality Medical Imaging Inverse Problems

## Motivation
Deep learning solutions for medical imaging inverse problems typically require large modality-specific training datasets, limiting their applicability when target modality data is scarce. While diffusion models have emerged as powerful priors, they are trained separately for each imaging modality (MRI, CT, X-ray), ignoring shared geometric structures across modalities. This creates a critical gap: can we leverage geometric regularities common to medical imaging—edges, boundaries, anatomical structures—to enable efficient cross-modality transfer?

## Main Idea
We hypothesize that decomposing diffusion priors into a geometry-aware universal encoder (trained on multi-modal data) plus lightweight LoRA adapters (<5% parameters) enables effective cross-modality transfer. The causal mechanism operates in three stages: (1) multi-modal training forces the encoder to learn only modality-invariant geometric features, (2) diffusion learns a universal structural prior in this geometric latent space, and (3) small adapters specialize for modality-specific characteristics during transfer.

We will test this by pre-training on MRI+CT, then adapting to X-ray reconstruction. The key prediction: achieving reconstruction quality within 1dB PSNR of modality-specific baselines while using ≤50% target modality data. Falsification occurs if transfer provides <3dB improvement or cross-modality latent similarity fails to exceed standard VAE baselines. Success would significantly reduce data requirements for deploying diffusion-based reconstruction in data-limited clinical settings.