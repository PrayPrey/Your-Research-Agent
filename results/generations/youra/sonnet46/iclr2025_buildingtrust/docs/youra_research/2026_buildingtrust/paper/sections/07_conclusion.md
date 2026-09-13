# 7. Conclusion

We began with the observation that aligning a language model to be helpful and harmless causes it to change its answers — not just its confidence. For 99.7% of MMLU questions, a 1.4B-PPO-trained model selects a different answer than its base counterpart; the Spearman correlation between their log-probability distributions is ρ = −0.324. Our mechanistic investigation confirms this is not exceptional behavior — it is the dominant pattern across the Pythia alignment ladder.

### Summary

In this work, we addressed the open question of *which mechanism* drives alignment-induced miscalibration in LLMs, providing the first pre-registered mechanistic discrimination between scale inflation (H1), decision-boundary restructuring (H2), and framing susceptibility (H3). Our main contributions are:

1. **H2 is the dominant mechanism** in Pythia 1.4B–6.9B: all 9 Spearman ρ values fall below the H1 threshold of 0.90; 8/9 fall below 0.85. Alignment changes answer preferences, not just confidence magnitudes. This definitively refutes the implicit H1 assumption in prior work on post-hoc calibration correction.

2. **DPO produces larger calibration degradation than PPO** (ΔReliability_DPO > ΔReliability_PPO in all 3 Pythia sizes), consistent with DPO's unconstrained token-level objective causing more aggressive boundary restructuring than PPO's KL-penalized optimization.

3. **H3 (framing susceptibility) is definitively excluded** in softmax-based ECE: ΔECE_TruthfulQA < ΔECE_MMLU for all alignment types, showing domain-general miscalibration that is not driven by adversarial framing.

4. **A reusable mechanistic framework** — Spearman ρ threshold test, argmax partition, cross-benchmark H3 diagnostic — applicable to any model family via lm-eval without modification.

### Future Directions

Our results open three categories of motivated follow-up work:

**From untested alternative explanations:** The DPO ≥ PPO ordering could be verified with matched-training DPO versus PPO experiments using identical data, duration, and reward model. If DPO > PPO persists when KL coefficient is varied in PPO training, the token-level objective interpretation is supported; if higher KL reduces the H2 effect in PPO, the KL-constraint explanation is supported.

**From unverified assumptions:** ATS [Xie et al., 2024] may correct H2-type boundary shifts by learning per-input hidden-state temperatures that track boundary redistribution patterns. H-M4 — testing whether ATS effectiveness correlates with the degree of H2 (lower ρ → greater expected improvement) — is the immediate next experiment. If ATS fails for extreme H2 cases (1.4B-PPO, ρ = −0.324), this motivates fundamentally different correction approaches.

**From scope extensions:** The 6.9B-DPO model (ρ = 0.875) suggests a potential H1/H2 mechanism transition at larger scales. Applying the Spearman ρ diagnostic to LLaMA-2-13B-Chat or Mistral-7B-Instruct — families with sufficient scale for practical deployment — would determine whether H2 dominance is specific to the 1.4B–6.9B range or persists to production-scale models.

### Closing

As RLHF alignment continues to shape how language models are deployed in consequential settings, understanding the mechanism of miscalibration becomes as important as measuring its magnitude. The question is not simply "how confident is the aligned model?" — it is "what has it learned to prefer, and can we correct it?" Our framework makes that question answerable.
