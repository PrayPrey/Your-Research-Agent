# Research Idea

## Title
Sparse Subspace PAC-Bayes for Deep Reinforcement Learning: Tractable Non-Vacuous Bounds via Fisher-Guided Compression

## Motivation
PAC-Bayesian theory offers principled generalization guarantees for probabilistic learning, but applying it to deep reinforcement learning faces two critical barriers: (1) computing KL divergence over millions of parameters yields vacuous bounds, and (2) sequential RL data violates independence assumptions. While recent work addresses these separately—subspace methods for supervised learning and mixing-time corrections for RL—no approach combines them for tractable, non-vacuous bounds in deep RL. This gap limits our theoretical understanding of when sample-efficient deep interactive learning can be guaranteed.

## Main Idea
We hypothesize that projecting policy posteriors onto Fisher information-guided low-dimensional subspaces, combined with bio-inspired gradual magnitude pruning, enables non-vacuous PAC-Bayesian bounds with O(d) complexity instead of O(D). The causal mechanism proceeds as: (1) Fisher eigenvectors identify policy-relevant directions, (2) low-d projection reduces KL computation, (3) gradual pruning further compresses without performance loss, and (4) Markov mixing-time correction validates bounds under sequential data. We will test this on MuJoCo continuous control tasks using SAC, measuring bound values (target <1.0), computational scaling, and policy performance (within 5% of dense baseline). The hypothesis is falsified if bounds remain vacuous for d≤2000 or pruning degrades performance >10%. Success would provide the first computationally tractable, theoretically grounded generalization guarantees for deep RL policies.