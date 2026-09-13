## Title: Equivariant World Models for Robust Robotic Manipulation via Learned Symmetry Discovery

## Motivation:
Current robotic manipulation systems struggle with generalization—a policy trained to grasp an object in one orientation often fails when the object is rotated or translated. While equivariant neural networks can encode known symmetries, real-world manipulation involves objects and environments with unknown or approximate symmetries. Manually specifying symmetry groups for every scenario is impractical. This gap between geometric deep learning theory and practical robotics limits deployment in unstructured environments.

## Main Idea:
We propose a framework that jointly learns world models and discovers their underlying symmetry groups directly from interaction data. The approach consists of three components: (1) a symmetry discovery module that identifies approximate Lie group structures from state-action transitions using infinitesimal generator estimation, (2) an equivariant latent dynamics model that enforces the discovered symmetries, and (3) a model-predictive control scheme operating in the symmetry-aware latent space.

The key technical innovation is a differentiable "symmetry regularizer" that encourages the world model's latent space to exhibit group-equivariant structure while remaining flexible enough to capture symmetry-breaking factors (e.g., gravity, friction). We will evaluate on simulated and real robotic manipulation benchmarks, measuring sample efficiency, out-of-distribution generalization across object poses, and robustness to perturbations.

Expected outcomes include 5-10x improvement in sample efficiency and significantly better zero-shot transfer to novel object configurations, bridging geometric deep learning principles with practical robotic learning.