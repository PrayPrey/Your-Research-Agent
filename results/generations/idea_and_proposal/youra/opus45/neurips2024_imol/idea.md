# Research Idea

## Title
Learning-Progress-Gated Adaptive Reward Integration for Open-Ended Skill Discovery

## Motivation
Current intrinsically motivated agents face a fundamental trade-off: prediction-based methods (RND) excel at state coverage but ignore skill structure, while competence-based methods (DIAYN) discover diverse skills but may miss novel states. Fixed combinations fail because optimal exploration-exploitation balance shifts during learning—early training benefits from novelty-seeking, while later stages require skill refinement. This limits agents' ability to develop broad, flexible skill repertoires essential for open-ended learning.

## Main Idea
We propose Learning-Progress-Gated Adaptive Reward Integration (LP-GARI), which dynamically combines RND and DIAYN intrinsic rewards using a learned gating mechanism. A small MLP receives learning progress signals (world model improvement, skill discriminator accuracy change, state coverage rate) and outputs an adaptive weight α(t) that balances exploration versus skill discovery rewards throughout training.

**Core mechanism:** When world model prediction error decreases rapidly (high learning progress), the system favors RND for continued exploration; when coverage saturates, it shifts toward DIAYN for skill refinement.

**Methodology:** We test in MuJoCo continuous-control environments under reward-free pre-training, measuring state coverage (k-means discretization), skill diversity (mutual information), and downstream fine-tuning efficiency against RND, DIAYN, fixed-weight, and CIM baselines.

**Expected outcomes:** ≥15% improvement in combined exploration-skill metrics over single-paradigm methods, with 1.5x faster downstream task adaptation, advancing autonomous open-ended learning systems.