# Research Proposal: Curriculum Noise Scheduling for Sample-Efficient Diffusion Model Training

## 1. Title

**Curriculum Noise Scheduling: Accelerating Diffusion Model Training Through Adaptive Easy-to-Hard Timestep Ordering with Experience Replay**

## 2. Introduction

### 2.1 Background

Diffusion models have emerged as the dominant paradigm in generative modeling over the past three years, achieving unprecedented success in image synthesis, video generation, audio production, and scientific applications. These models work by gradually adding noise to data through a forward diffusion process, then learning to reverse this process through iterative denoising. The theoretical foundation, established by Ho et al. (2020) in Denoising Diffusion Probabilistic Models (DDPM) and extended by Song et al. through score-based generative modeling, has enabled remarkable generation quality surpassing GANs in many domains.

However, this success comes at a substantial computational cost. Training state-of-the-art diffusion models requires massive datasets (typically 10,000 to 1,000,000 images) and extensive computational resources (hundreds to thousands of GPU hours). This creates significant barriers for academic laboratories with limited budgets, small-dataset domains such as medical imaging where data collection is expensive and privacy-constrained, and rapid prototyping scenarios requiring quick iteration. The environmental impact is also concerning, with large-scale diffusion model training contributing substantially to the carbon footprint of machine learning research.

Current diffusion model training employs uniform timestep sampling, where denoising tasks across all noise levels $t \sim \mathcal{U}[0,T]$ are treated equally during optimization. This approach ignores a fundamental insight from educational science and machine learning: **curriculum learning**—the principle that ordering training examples from easy to hard can dramatically accelerate convergence. Bengio et al. (2009) demonstrated that curriculum learning reduces training iterations by 20-40% across computer vision and natural language processing tasks. This principle has been successfully applied to data complexity (image resolution in Stable Diffusion), sequence length (Transformer training), and task difficulty (reinforcement learning), but has never been explored for diffusion models' noise dimension.

The noise dimension presents a natural curriculum opportunity: denoising tasks at different timest