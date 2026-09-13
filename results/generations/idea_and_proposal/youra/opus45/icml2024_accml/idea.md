## Title
BioHomeoAL: Homeostatic Active Learning for Resource-Efficient Biological Foundation Model Adaptation

## Motivation
Foundation models like ESM-2 and DNABERT-2 hold transformative potential for biological discovery, yet most wet labs lack the computational resources and large labeled datasets required for effective fine-tuning. Current active learning approaches treat model adaptation, sample selection, and resource constraints as separate problems, leading to suboptimal experimental efficiency. This gap between ML capabilities and practical lab accessibility demands a unified framework that can reduce experimental costs while maintaining performance under realistic resource constraints.

## Main Idea
We propose BioHomeoAL, a bio-inspired framework that treats model epistemic uncertainty as a homeostatic feedback signal to coordinate foundation model adaptation. The core mechanism operates through a 5-step control loop: (1) MC Dropout quantifies model uncertainty, (2) uncertainty triggers adaptive LoRA rank selection (r∈{8,16,32}), (3) parameter-efficient updates enable rapid adaptation, (4) reduced uncertainty improves sample selection via multi-objective acquisition (uncertainty × diversity × cost⁻¹), and (5) informative sampling reduces experimental costs by 30-50%.

Key innovations include uncertainty-driven LoRA modulation and Pareto-optimized batch selection. We will validate across protein fitness, drug binding, and genomics tasks, comparing against random sampling and standard active learning baselines (BALD, BatchBALD). Success criteria: ≥30% sample efficiency improvement with ≤50% performance variance. This framework directly addresses the workshop's goal of making foundation models accessible to resource-constrained biology labs.