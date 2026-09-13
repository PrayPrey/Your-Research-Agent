## Title
Prospect Theory Value Layers for Human-AI Alignment: Modeling Cognitive Biases in RLHF Reward Models

## Motivation
Current RLHF approaches assume human annotators provide rational, unbiased feedback—an assumption systematically violated in practice. Humans exhibit well-documented cognitive biases including loss aversion (weighing losses ~2.25× more than equivalent gains) and diminishing sensitivity to reward differences. These biases cause reward model misspecification, leading to suboptimal policy alignment. While behavioral economics has characterized these biases for decades, RLHF systems ignore them entirely, creating a critical gap between how humans actually evaluate AI outputs and how reward models predict preferences.

## Main Idea
We propose integrating a **Prospect Theory Value Layer (PTVL)** into RLHF reward models. The PTVL transforms raw reward outputs using prospect theory's value function—applying asymmetric transformations for gains versus losses relative to a reference point—before computing Bradley-Terry preference probabilities. Key parameters (loss aversion λ, diminishing sensitivity α,β) are learnable but initialized from established psychological estimates.

**Methodology:** Compare PTVL-enabled reward models against standard baselines on HH-RLHF, measuring preference prediction accuracy and downstream policy win rates via GPT-4 evaluation. Ablations isolate contributions of loss aversion versus diminishing sensitivity.

**Expected Outcomes:** >2% improvement in preference prediction accuracy; learned parameters converging to psychologically plausible ranges (λ∈[1.5,3.0]), validating the causal mechanism. This bridges behavioral economics and AI alignment, offering a principled approach to modeling human irrationality in feedback systems.