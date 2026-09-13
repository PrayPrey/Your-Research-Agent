# Conclusion

We began by asking a fundamental question about reward models: when they assign a score, what are they really evaluating? Our experiments reveal that the answer extends beyond content quality to include structural formatting preferences that operate independently of response substance.

## Summary

In this work, we introduced the first systematic behavioral probe for structural preferences in RLHF-trained reward models. Using controlled stimulus pairs that match content, length, correctness, and completeness while varying only format, we demonstrated that decoder-based reward models systematically prefer enumerated responses over synthesized alternatives.

Our main findings are:

1. **Enumeration preference is robust and replicable.** Three of four architecturally distinct reward models exhibit significant enumeration preference (Cohen's *d* = 0.38--1.45), with a pooled effect size of *d* = 0.70. This effect persists across different training objectives (Bradley-Terry, regression, mixture-of-experts) and training datasets (HelpSteer, UltraFeedback, Nectar).

2. **The effect is architecture-conditional.** Encoder-only PairRM shows no significant enumeration preference (*d* = 0.08, *p* = 0.35), suggesting that structural encoding depends on attention mechanism design. Causal attention in decoder-only models may accumulate structural signals differently than bidirectional attention.

3. **Structural preferences are independent of content.** The enumeration effect is orthogonal to correctness and completeness manipulations, indicating that reward models encode formatting features as separate signals from quality evaluation.

## Future Directions

Our findings open several research directions grounded in experimental evidence:

**Mechanism validation.** While we establish existence, the causal pathway remains to be validated. Testing training data log-odds could reveal whether human raters systematically prefer enumeration during annotation. Spurious enumeration controls could distinguish structural coherence from surface token bias.

**Architectural investigation.** The PairRM non-effect raises questions about attention mechanism design. Systematic comparison of encoder, decoder, and hybrid architectures could reveal which components drive structural encoding. Attention pattern visualization could show how models process enumeration markers differently.

**Extended structural probing.** Our methodology applies beyond enumeration. Other formatting features---bullet styles, paragraph organization, header formatting, emphasis markers---may also be independently encoded. A comprehensive structural sensitivity suite could become a standard component of reward model evaluation.

**Training interventions.** If structural biases are undesirable, training modifications could mitigate them. Format-standardized preference collection, structural debiasing objectives, or encoder-decoder ensemble evaluation could preserve content sensitivity while reducing format dependence.

## Closing Remarks

If reward models encode formatting preferences independently of content quality, then RLHF optimization may be steering language models toward superficial presentation patterns rather than substantive improvements in helpfulness or accuracy. Understanding these structural signals is essential for building reward models that truly evaluate what we intend.

Our work takes a first step toward this goal by demonstrating that structural preferences exist, are measurable, and vary with architecture. We hope this encourages the community to expand reward model evaluation beyond content dimensions, ensuring that alignment systems optimize for genuine quality rather than formatting heuristics.
