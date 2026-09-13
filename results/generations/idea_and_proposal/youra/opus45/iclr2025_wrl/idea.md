# Research Idea

## Title
Training-Time Control Barrier Function Integration for Inherently Safe Diffusion Policies in Contact-Rich Manipulation

## Motivation
Current safe robot learning approaches apply safety constraints at inference time, filtering unsafe actions post-hoc. This creates computational overhead and fails to shape the underlying policy distribution. For contact-rich manipulation tasks requiring human-level dexterity, robots need policies that are *inherently* safe—avoiding unsafe regions by design rather than correction. Existing methods like CoBL-Diffusion achieve safety but incur 30-50% inference latency penalties, limiting real-time deployment. A fundamental gap exists: can we embed safety directly into policy learning to eliminate this trade-off?

## Main Idea
We propose integrating Control Barrier Function (CBF) constraints during diffusion policy training via Lagrangian relaxation, rather than at inference time. The core mechanism involves: (1) a CBF loss term penalizing unsafe actions during training, (2) a learned Lagrangian multiplier dynamically balancing task and safety objectives, and (3) phased training (frozen CBF → joint fine-tuning) ensuring stability. This shapes the action distribution to inherently avoid unsafe regions.

**Methodology:** Compare training-time CBF integration against inference-time filtering (CoBL-Diffusion) on CALVIN benchmark contact-rich tasks, measuring safety violation rates, task success, and inference latency.

**Expected Outcomes:** <2% safety violations (vs. 5-10% baseline) while maintaining ≥82% task success with zero inference overhead—enabling real-time deployment of safe manipulation policies.