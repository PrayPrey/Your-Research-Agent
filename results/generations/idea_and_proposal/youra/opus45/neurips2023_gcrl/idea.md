# Research Idea

## Title
Contrastive Molecular Goal-Conditioned RL: Bridging Representation Learning and Sample-Efficient Molecular Design via HER-Style Property Relabeling

## Motivation
Goal-conditioned RL promises intuitive molecular design by specifying desired properties rather than reward functions, yet current methods suffer from severe sample inefficiency in discrete molecular spaces. While contrastive learning has revolutionized molecular representations (UniCorn, 2024) and the contrastive-GCRL equivalence (Eysenbach, 2022) connects representations to value functions in continuous domains, this connection remains unexplored for graph-structured molecules. This gap prevents leveraging powerful techniques like Hindsight Experience Replay (HER), which achieves 10-100x efficiency gains in robotics by learning from failed attempts.

## Main Idea
We propose CM-GCRL, which trains GNN molecular encoders φ(mol) and property encoders ψ(prop) via graph-aware contrastive learning, establishing that their inner product approximates goal-conditioned value functions (φ(mol)ᵀψ(prop) ≈ V(mol,prop)). This enables HER-style relabeling: failed molecular generations are relabeled with their achieved properties as new goals, creating an implicit curriculum. Confidence-weighted relabeling (threshold τ) prevents noise from uncertain property predictions.

**Key predictions:** (1) >30% sample efficiency improvement over standard RL; (2) >85% molecular validity maintained; (3) superior multi-property Pareto coverage versus GFlowNets.

**Methodology:** Ablation studies isolating contrastive equivalence validity, HER contribution, and confidence thresholding effects on QM9/GuacaMol benchmarks.

**Impact:** Establishes theoretical foundations for GCRL in discrete molecular spaces while enabling practical multi-property drug design.