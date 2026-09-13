# Title: Goal-Conditioned RL via Contrastive World Models for Molecular Discovery

## Motivation
Molecular discovery presents a unique challenge for GCRL: the goal space (desired molecular properties) is continuous, high-dimensional, and often only partially observable through expensive simulations or experiments. Current GCRL methods struggle in this domain because they assume dense goal observations and rely on distance metrics that don't capture meaningful chemical similarity. By connecting GCRL with self-supervised representation learning, we can learn latent spaces where goal-reaching becomes more tractable, enabling precise and customizable molecular generation without hand-crafted reward functions.

## Main Idea
We propose **MolGCRL**, a framework that learns a contrastive world model jointly with a goal-conditioned policy for molecular optimization. The key insight is to use temporal contrastive learning on molecular transformation trajectories to learn representations where Euclidean distance corresponds to synthesizability and property similarity.

**Methodology:**
1. Train a contrastive encoder that maps molecular graphs and target properties into a shared latent space, where positive pairs are molecules reachable within k transformation steps
2. Learn a latent dynamics model predicting next-state representations given actions (chemical reactions)
3. Train a goal-conditioned policy using hindsight relabeling in the learned latent space

**Expected Outcomes:** Improved sample efficiency in molecular optimization tasks, better generalization to novel target properties, and interpretable goal representations. We will evaluate on multi-objective drug design benchmarks (QED, synthesizability, binding affinity), demonstrating that learned representations enable effective goal-reaching where property-based reward shaping fails.