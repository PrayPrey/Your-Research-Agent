# Conclusion

We began with a striking observation: a 1.4B-parameter PPO-trained Pythia model selects a different answer than its base model counterpart for 99.7% of MMLU multiple-choice questions — with a Spearman ρ of −0.324, it has learned to systematically prefer the options its base model found least likely. This is not miscalibration in the conventional sense. It is alignment-induced answer reversal, driven by a mechanism we characterize as decision-boundary restructuring (H2).

## Summary of Contributions

Our study provides the following contributions to the understanding of RLHF-induced miscalibration:

**1. Mechanistic discrimination framework.** We pre-register three competing mechanistic hypotheses (H1 scale inflation, H2 boundary shift, H3 framing susceptibility) with falsifiable threshold-based discrimination tests (Spearman ρ ≥ 0.90 for H1; < 0.85 for H2; TruthfulQA ΔECE > MMLU ΔECE for H3). This framework is directly applicable to any model family via lm-eval-harness without modification.

**2. H2 confirmed as dominant mechanism.** Across all 9 alignment-base pairs in the Pythia 1.4B–6.9B range, we find 0/9 pairs with Spearman ρ ≥ 0.90 (H1 refuted) and 8/9 with ρ < 0.85 (H2 confirmed). The single near-threshold case (6.9B-DPO, ρ = 0.875) suggests a potential scale transition above 6.9B.

**3. Counter-intuitive alignment ordering.** DPO consistently produces larger Brier reliability degradation than PPO in all three Pythia sizes — with 1.4B DPO showing ΔReliability = 0.1048 (5.5× the base reliability) versus PPO's 0.0406. We interpret this as evidence that DPO's token-level unconstrained preference reshaping is more disruptive to answer boundaries than PPO's sequence-level reward optimization with KL penalty.

**4. Framing susceptibility definitively ruled out.** TruthfulQA ΔECE is consistently smaller than MMLU ΔECE for all alignment types (ratio 0.26–0.73). Softmax-based calibration degradation is domain-general, not framing-specific — distinguishing our finding from the verbal-confidence framing sensitivity reported by Chhikara et al.

**5. Clean causal attribution.** Pythia base models show ECE = 0.057–0.085 (all < 0.15), confirming well-calibrated pretraining and unambiguous attribution of downstream miscalibration to alignment training.

## Key Takeaways

Three takeaways stand out for practitioners:

*Aligned LLMs are not just "too confident" — they may prefer different answers entirely.* Standard calibration methods that rescale confidence magnitudes address H1-type distortions. Our finding that H2 is dominant means these methods are addressing the wrong problem for small-to-medium aligned models.

*DPO may pose a larger calibration risk than PPO.* The absence of a KL divergence penalty in DPO's training objective leaves the model's answer-preference rankings less constrained during alignment. If calibration preservation is a design goal, DPO alignment warrants additional post-hoc calibration correction or modified training objectives.

*The Spearman ρ diagnostic is a simple, cheap calibration risk indicator.* Computing per-item Spearman ρ between base and aligned log-probability vectors requires only cached lm-eval outputs and a few minutes of CPU computation. Practitioners can use this as a first-pass indicator of whether H1 or H2 is the dominant mechanism for their specific model, guiding the choice of calibration correction method.

## Future Work

Our results directly motivate three lines of future investigation:

**Cross-family replication.** Applying the Spearman ρ diagnostic to LLaMA-2-Chat 7B and 13B will test whether the H1/H2 transition occurs at larger scale for other model families, and whether the mechanism findings generalize beyond the Pythia training regime.

**ATS effectiveness for H2-type distortions.** Testing whether Adaptive Temperature Scaling \cite{xie2024ats} reduces ECE comparably for H1-type and H2-type models — or whether H2-type boundary shift requires different correction approaches — is the most immediate experiment motivated by our mechanistic finding.

**Controlled DPO vs. PPO comparison.** Training matched DPO and PPO variants from the same base checkpoint on identical HH preference data (varying only the KL penalty coefficient β) would directly test whether the DPO > PPO calibration ordering is intrinsic to the training objectives or an artifact of our checkpoint availability constraints.

The 1.4B-PPO model's near-complete answer-reversal behavior remains perhaps the most vivid illustration of the gap between alignment training objectives (helpfulness and harmlessness on conversational data) and factual calibration on knowledge benchmarks. Closing this gap requires not just better calibration correction methods, but a deeper understanding of what RLHF actually does to the representational structure of model outputs — a goal our mechanistic discrimination framework directly enables.
