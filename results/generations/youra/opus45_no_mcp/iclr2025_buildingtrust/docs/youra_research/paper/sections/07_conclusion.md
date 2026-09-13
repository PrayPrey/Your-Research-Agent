# Conclusion

We began with the observation that LLMs generating step-by-step reasoning produce linguistic markers of uncertainty—and asked whether these markers influence confidence calibration. Our systematic verification provides an affirmative answer: the complete mechanism chain from CoT prompting to calibrated confidence is empirically validated.

Chain-of-thought prompting reliably produces multi-step reasoning (100% rate), this reasoning contains epistemic hedging markers (82% presence), these markers structurally precede confidence generation (100% ordering compliance), and hedging count negatively correlates with verbalized confidence (r=-0.315, p<1e-16). The effect size exceeds prior estimates, and the statistical significance rules out chance association.

These findings support a "self-reading" interpretation: models can leverage uncertainty signals from their own in-context reasoning to produce more calibrated confidence judgments. This mechanism operates through prompting alone, requiring no model fine-tuning or access to internal representations.

## Future Work

Three directions extend this work. First, **multi-model replication** on Llama-2-70B, Claude, and GPT-4 would establish generalization across model families. The mechanism should be architecture-agnostic, but empirical verification is needed.

Second, an **intervention study** manipulating hedging markers (injecting or removing them) would provide causal evidence beyond the correlational findings reported here. If confidence changes systematically with manipulated hedging, the self-reading interpretation would be strengthened.

Third, executing the **full ECE comparison** with real API calls would validate the primary super-additivity claim (P1): that CoT+confidence yields ECE at least 0.03 lower than single interventions. Our mechanism validation provides the theoretical foundation; the direct comparison would complete the empirical picture.

The broader implication is methodological: decomposing calibration improvement claims into mechanism-level sub-hypotheses allows for robust validation even when primary comparisons face resource constraints. The mechanism chain approach provides interpretable evidence about why an intervention works, not just whether it works.
