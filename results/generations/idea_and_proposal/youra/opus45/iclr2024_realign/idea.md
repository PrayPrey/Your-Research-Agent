# Research Idea

## Title
Dual-Plasticity Alignment Networks: Steering Representational Alignment Through Dynamic Sparse Training

## Motivation
Understanding when and how intelligent systems learn aligned representations is a central challenge across machine learning and cognitive science. Current methods for improving alignment between artificial and biological systems rely primarily on loss function modifications, offering limited controllability. Meanwhile, dynamic sparse training techniques can reshape network topology but have never been leveraged to explicitly target representational alignment. This gap leaves researchers without principled tools to systematically increase or decrease alignment between systems—a key open question for the Re-Align workshop.

## Main Idea
We propose Dual-Plasticity Alignment Networks, which integrate alignment signals into dynamic sparse training decisions. The core mechanism operates through four steps: (1) periodically compute debiased CKA between model representations and target representations (human similarity judgments or fMRI data), (2) score connection importance using alignment-weighted formula combining task gradients and alignment correlations, (3) prune low-importance connections while growing connections between high-alignment neurons, and (4) iterate to progressively shape alignment-promoting pathways.

The key innovation is using a tunable parameter α to control the task-alignment trade-off, enabling systematic exploration of the Pareto front. We predict >10% alignment improvement over standard training while maintaining task performance. Validation uses ResNet architectures on CIFAR-10/ImageNet with THINGS human similarity data. This framework provides the first structural intervention approach for controllable representational alignment.