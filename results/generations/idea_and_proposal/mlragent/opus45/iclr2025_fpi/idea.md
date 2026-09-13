# Title: Curriculum-Guided Diffusion Samplers for Multi-Modal Boltzmann Distributions

## Motivation
Sampling from high-dimensional Boltzmann distributions with multiple isolated modes remains a fundamental challenge. Current learning-based samplers (e.g., diffusion-based methods, flow matching) often suffer from mode collapse or fail to capture the correct relative weights between modes. Classical MCMC methods mix poorly between modes, while learned samplers trained end-to-end frequently get stuck in local optima during training. This gap severely limits applications in molecular dynamics and statistical physics where accurate multi-modal sampling is crucial for computing thermodynamic properties.

## Main Idea
We propose a curriculum learning framework for training diffusion-based samplers on multi-modal unnormalized densities. The key insight is to decompose the learning problem into progressive stages: (1) First train on a "tempered" version of the target distribution with reduced barriers between modes, (2) Gradually anneal toward the true target while using the previous sampler to initialize training. 

Specifically, we parameterize a family of interpolating distributions between a tractable prior and the target Boltzmann density, using learned temperature schedules. The diffusion sampler is trained sequentially along this curriculum, with importance-weighted objectives ensuring correct mode weights at each stage.

**Expected outcomes**: Improved mode coverage and accurate relative mode weights on challenging benchmarks (alanine dipeptide, Lennard-Jones clusters). **Impact**: Enables reliable free energy estimation and rare event sampling in molecular systems where current methods fail.