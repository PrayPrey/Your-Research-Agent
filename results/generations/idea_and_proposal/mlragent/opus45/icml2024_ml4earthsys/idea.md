# Title: Uncertainty-Aware Generative Downscaling with Physics-Constrained Diffusion Models

## Motivation:
Dynamical downscaling remains a critical bottleneck in climate projections—coarse global climate models (GCMs) operate at ~100km resolution, yet impact assessments require kilometer-scale predictions. Current statistical downscaling methods either lack physical consistency or fail to capture the full uncertainty distribution, particularly for extreme events. Diffusion models excel at generating high-quality samples from complex distributions, but naive application ignores conservation laws and produces physically implausible outputs. Bridging this gap is essential for reliable regional climate adaptation planning.

## Main Idea:
I propose **Physics-Constrained Diffusion Models (PCDM)** for probabilistic climate downscaling that embeds hard physical constraints directly into the denoising process. The methodology involves: (1) training a conditional diffusion model on paired coarse-fine resolution climate data (e.g., precipitation, temperature fields), (2) incorporating differentiable physics layers that enforce mass/energy conservation and topographic consistency during sampling, and (3) using classifier-free guidance conditioned on large-scale atmospheric patterns to improve extreme event representation.

The model will output ensemble predictions capturing aleatoric uncertainty while physics constraints reduce epistemic errors. Evaluation will compare against dynamical downscaling baselines using metrics for distributional accuracy, physical consistency (e.g., water budget closure), and extreme event statistics.

**Expected Impact:** Computationally efficient (~1000× faster than dynamical methods), physically plausible probabilistic downscaling enabling robust uncertainty quantification for climate adaptation decisions.