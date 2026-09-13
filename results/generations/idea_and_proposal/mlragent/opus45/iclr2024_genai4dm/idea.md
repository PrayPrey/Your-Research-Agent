# Research Idea

## Title
Diffusion Models as Intrinsic Motivation Generators for Sparse Reward Exploration

## Motivation
Exploration in sparse reward environments remains a fundamental challenge in reinforcement learning. Current intrinsic motivation methods (curiosity, count-based) often struggle in high-dimensional state spaces and fail to capture semantically meaningful novelty. Pre-trained diffusion models, having learned rich representations of natural data distributions, offer an untapped resource: they inherently understand "what is normal" versus "what is unusual." This knowledge can provide a principled, semantically-aware exploration signal without requiring reward labels.

## Main Idea
We propose using pre-trained image diffusion models to compute intrinsic rewards based on the reconstruction likelihood of observed states. Specifically, for each state image encountered by an agent, we compute the diffusion model's estimated log-probability (via the ELBO or denoising score matching loss). States that deviate from the pre-trained distribution—representing novel, interesting configurations—yield lower likelihoods and thus higher intrinsic rewards.

The methodology involves: (1) freezing a pre-trained diffusion model (e.g., Stable Diffusion's VAE+U-Net), (2) computing per-state novelty scores during rollouts, and (3) combining these with sparse extrinsic rewards for policy optimization.

Expected outcomes include improved exploration in visually complex environments (e.g., Minecraft, robotic manipulation) where semantic novelty matters. This approach requires zero reward-labeled data for the intrinsic signal and leverages internet-scale visual priors, potentially enabling agents to discover meaningful subgoals in open-ended tasks autonomously.