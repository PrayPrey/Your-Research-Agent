# Research Idea

## Title
Hierarchical Predictive Diffusion for Real-Time Audio Generation

## Motivation
Current diffusion-based audio generation achieves high quality but requires 50+ denoising steps, resulting in multi-second latencies unsuitable for interactive applications like VR/AR, gaming, and live content creation. While consistency distillation methods (e.g., SoundReactor at 26.3ms) reduce latency, they apply uniform computation regardless of content complexity. This wastes resources on predictable segments while potentially under-serving complex ones. Inspired by predictive coding in biological auditory systems—where the brain allocates processing based on prediction error magnitude—we propose adaptive computation allocation for streaming audio diffusion.

## Main Idea
We introduce Hierarchical Predictive Diffusion (HPD), combining two mechanisms: (1) **coarse-to-fine hierarchical initialization** that provides structured starting points for diffusion instead of random noise, reducing steps needed for convergence; and (2) **precision-weighted adaptive NFE scheduling** that dynamically allocates 1-2 diffusion steps for predictable segments versus 4-8 steps for complex transitions. A lightweight precision estimation network classifies segment complexity in real-time, enabling efficient computation allocation.

**Methodology:** We train on AudioCaps/VGGSound, comparing against SoundReactor, VoXtream, and offline AudioLDM baselines. Key metrics include per-frame latency (<50ms target), FAD (within 10% of offline), and MOS (≥4.0).

**Expected Impact:** 50-70% latency reduction while preserving quality, enabling high-fidelity real-time audio for interactive applications.