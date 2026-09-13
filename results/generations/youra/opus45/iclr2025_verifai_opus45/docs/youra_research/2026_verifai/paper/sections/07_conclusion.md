# Conclusion

We began by observing a counterintuitive phenomenon: when LLM-generated code fails, providing detailed error information—the exception type, message, and line number—does not help the model fix it. In fact, it makes repair significantly worse. Our controlled study quantifies this effect and challenges the "more information is better" assumption underlying current LLM debugging tools.

## Summary

This work presents the first systematic comparison of error feedback granularity for LLM code repair. Our key findings are:

1. **Granularity significantly affects repair success.** ANOVA across five granularity levels (G0-G4) reveals a highly significant effect (F=23.89, p < 10⁻¹⁸), establishing that feedback design is not merely an implementation detail but a critical choice with 25+ percentage point impact.

2. **Simpler feedback dramatically outperforms detailed feedback.** For CodeLlama-7B-Instruct on MBPP, pass/fail only (G0) achieves 41.8% repair success, while error+line (G3) achieves only 16.8%. This inverse relationship contradicts the intuition that localization information helps repair.

3. **A two-cluster pattern emerges.** Repair success clusters into minimal feedback (G0, G1: ~41%) and detailed feedback (G2-G4: ~17-23%), with a sharp threshold at the G1→G2 boundary. Including the error message causes a ~22 percentage point performance drop.

4. **The "attention window hypothesis" is not supported.** We hypothesized that intermediate granularity would focus model attention optimally. The data refutes this: at the 7B scale, detailed localization appears to cause cognitive interference rather than helpful guidance.

## Future Directions

Our findings open several promising research directions grounded in our experimental observations:

**Scaling Studies.** Our results are specific to the 7B parameter scale. If simpler feedback wins due to capacity limitations, larger models (13B, 34B, 70B) may recover the expected benefit of detailed feedback. Determining the scale threshold where optimal granularity shifts would inform tool design across model sizes.

**Template Ablation.** We used the Self-Debug template throughout. Template-granularity interactions are plausible—prompts optimized for detailed feedback might recover some performance. A systematic template × granularity study would clarify whether our findings generalize beyond Self-Debug.

**Error Type Stratification.** Different error types (IndexError, TypeError, AttributeError) may respond differently to localization. Stratified analysis of our existing data could reveal error-type-specific optimal granularity, enabling adaptive feedback selection.

**Adaptive Strategies.** Rather than fixed granularity, tools might start with minimal feedback and escalate to detailed feedback only on repeated failure. Multi-turn repair with dynamic granularity adjustment remains unexplored.

**Attention Analysis.** Our prompt length hypothesis suggests that detailed feedback dilutes attention to the actual code. Analyzing attention patterns across granularity levels would provide mechanistic evidence for or against this explanation.

## Closing Remarks

The surprising effectiveness of minimal feedback challenges assumptions embedded in current LLM debugging tools. As the field develops increasingly sophisticated repair systems with detailed execution traces and runtime state, our results suggest a need for caution: more information is not always better, and the optimal feedback strategy may depend on model scale.

We hope this work encourages the community to treat feedback granularity as a first-class design variable worthy of careful ablation, rather than an implementation detail to be fixed arbitrarily. For smaller models deployed in resource-constrained settings, the simple message "the test failed" may be the most effective feedback of all.
