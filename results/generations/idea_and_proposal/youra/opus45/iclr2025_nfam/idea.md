## Title
Inference-Time Noise Modulation for Controllable Memory-Generation Trade-off in Diffusion Models

## Motivation
Diffusion models trained on discrete patterns exhibit dual behavior—sometimes retrieving memorized training samples, other times generating novel outputs—but lack principled control over this trade-off. Recent theoretical work establishes equivalence between diffusion energy landscapes and Hopfield associative memory attractors, suggesting noise variance controls attractor basin exploration. This connection remains unexploited for practical control, leaving users unable to specify whether they want faithful retrieval or creative generation without retraining.

## Main Idea
We hypothesize that scaling the inference-time noise schedule by parameter λ∈[0,1] predictably shifts diffusion outputs between memory retrieval (low λ) and novel generation (high λ). The causal mechanism: λ directly scales noise variance σ(t), which controls trajectory exploration depth in the energy landscape—low noise confines trajectories to single attractor basins (memorized patterns), while high noise enables cross-basin exploration (novel interpolations).

We test this on MNIST discrete patterns using standard DDPM, measuring retrieval accuracy (cosine similarity >0.95 to training data) at λ≤0.2 and generation novelty (L2 distance threshold) at λ≥0.8. We predict monotonic trade-off (Pearson r>0.9) across λ values.

Expected impact: A training-free, single-parameter control mechanism enabling users to dial between exact recall and creative synthesis, bridging associative memory theory with practical diffusion model deployment.