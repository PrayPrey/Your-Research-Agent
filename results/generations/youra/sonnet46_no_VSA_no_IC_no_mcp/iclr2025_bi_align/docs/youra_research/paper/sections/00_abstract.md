# Abstract

Reinforcement Learning from Human Feedback (RLHF) trains language models against a reward model proxy rather than direct human judgment. As optimization pressure increases, this proxy diverges from held-out human preference — a phenomenon known qualitatively as reward hacking. We ask: how fast does this divergence grow, and does the growth rate replicate across independent experimental settings?

We define the *calibration-alignment divergence curve* as the regression slope of the normalized proxy-gold gap (RM score minus held-out human preference, both on [0,1] scale) on KL divergence budget. Analyzing published RLHF experimental data from two independent sources, we find this slope is β = 0.143 nat⁻¹ in Coste et al. [2023] (R² = 0.958, p < 10⁻⁶) and β = 0.160 nat⁻¹ in Gao et al. [2023] (p = 0.003) — a cross-dataset slope ratio of 1.116, indicating near-identical divergence rates despite different model families and scales.

These results provide the first quantitative, replicated regression characterization of how RLHF optimization degrades evaluation calibration to human judgment, framing reward hacking as an empirical instance of bidirectional alignment tension. We propose the normalized divergence gap as a standard cross-study comparison instrument computable from existing RLHF evaluation infrastructure.
