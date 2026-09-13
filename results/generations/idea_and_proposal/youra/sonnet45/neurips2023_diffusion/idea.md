# Title
Curriculum Noise Scheduling: Accelerating Diffusion Model Training Through Easy-to-Hard Timestep Ordering

# Motivation
Diffusion models require massive computational resources and large datasets (10k-1M images) for training, limiting accessibility for academic labs and small-dataset domains like medical imaging. Current training uses uniform timestep sampling, treating all denoising tasks equally despite varying difficulty. This ignores curriculum learning principles proven effective across machine learning: easy-to-hard ordering accelerates convergence by 20-40%. No prior work applies curriculum learning to diffusion's noise dimension, presenting an unexplored opportunity to dramatically improve training efficiency.

# Main Idea
We propose **Curriculum Noise Scheduling (CNS)**: reordering diffusion timestep sampling from empirically-easy (low noise) to hard (high noise) denoising tasks during training. After warmup epochs, we measure per-timestep loss L(t) to rank difficulty, then progressively expand the training timestep range with adaptive experience replay to prevent catastrophic forgetting. 

**Core mechanism**: Easy tasks establish stable gradient foundations → progressive complexity builds on learned features → replay maintains breadth while curriculum focuses learning.

**Methodology**: 3×3 factorial experiments (curriculum/uniform/inverted × full-data/1k/500 images) on ImageNet and medical datasets, measuring FID convergence speed and sample efficiency.

**Expected impact**: 2-5× faster convergence in full-data regimes and 10-100× sample efficiency in few-shot settings (500-1k images), enabling diffusion models for small-dataset scientific/medical applications while reducing training costs and carbon footprint.