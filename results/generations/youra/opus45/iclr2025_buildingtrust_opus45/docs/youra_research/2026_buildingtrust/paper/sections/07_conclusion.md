# Conclusion

We began by observing that models achieving state-of-the-art accuracy can simultaneously produce confidence scores that are fundamentally unreliable for distinguishing correct from incorrect predictions. Our work demonstrates why: RLHF instruction tuning corrupts the discriminative relationship between confidence and correctness through geometric distortion—a reshaping of the probability landscape that cannot be repaired by temperature scaling.

## Summary

In this paper, we addressed the question of whether RLHF-induced miscalibration is scalar (fixable by temperature scaling) or geometric (requiring training-time intervention). Our key insight was that RLHF's preference optimization mechanism inflates logit margins disproportionately for incorrect predictions, creating distortion that persists even after scale normalization.

Our main contributions are:

1. **Discriminative degradation demonstration:** We showed that AUROC for margin-based correctness prediction drops 2-4 percentage points in instruction-tuned models across Qwen and Mistral families—a statistically significant effect with direct implications for confidence-based decision making.

2. **Mechanism identification:** We identified margin inflation for incorrect predictions (3-17x) as the mechanism underlying discriminative degradation, explaining why high confidence no longer reliably indicates correctness.

3. **Geometric distortion characterization:** Using percentile-normalized monotonicity (30-40% β attenuation) and Brier decomposition (2-5 percentage point refinement degradation), we demonstrated that the distortion is geometric—affecting probability landscape shape, not just scale.

4. **Cross-family validation:** Consistent effects across two independently-developed model families support RLHF as the causal factor rather than vendor-specific implementation details.

## Future Directions

This work opens several promising directions grounded in our experimental findings:

**Calibration-aware RLHF.** The margin inflation mechanism suggests a direct intervention: modify RLHF reward functions to penalize margin inflation for incorrect predictions. Such an approach could preserve helpfulness while maintaining confidence discrimination.

**Scale and architecture generalization.** Our experiments focused on 7B models. The surprising magnitude asymmetry between Qwen (3.06x inflation) and Mistral (16.79x inflation) raises questions about how architectural differences and RLHF training strength interact. Systematic study across model sizes (1B-70B) and architectures could reveal design choices that minimize geometric distortion.

**Alternative preference optimization.** Direct Preference Optimization (DPO) implicitly optimizes the same objective as RLHF without explicit reward modeling. Comparing distortion patterns between DPO and PPO-based training could identify whether geometric distortion arises from the objective itself or from specific training dynamics.

**Domain-specific calibration.** While we tested on MMLU aggregate, our findings suggest domain-specific effects may exist. Understanding whether certain knowledge domains are more resistant to discriminative degradation could inform selective deployment strategies.

## Closing Thoughts

Temperature scaling cannot straighten a bent ruler. For applications where discrimination matters—selective prediction, uncertainty quantification, human-AI collaboration—we need RLHF that optimizes confidence quality alongside response helpfulness. Our findings provide both the diagnostic framework (geometric vs. scalar distortion) and the mechanistic understanding (margin inflation) needed to develop such approaches. As instruction-tuned models become the default deployment target, ensuring their confidence signals remain trustworthy is not just a technical challenge but a prerequisite for safe AI deployment.
