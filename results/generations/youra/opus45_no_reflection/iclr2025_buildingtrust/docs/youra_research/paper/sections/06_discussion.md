# Discussion

## Summary of Current State

This work presents a methodology for testing whether calibration quality mediates the correlation between LLM factuality and adversarial robustness. The evaluation pipeline has been validated, but full experimental results are not yet available due to incomplete data collection.

**What we have demonstrated:**
- A principled experimental design connecting three research areas
- A validated pipeline for computing MC1, ASR, and ECE
- Functional analysis code for correlation, partial correlation, and visualization

**What remains to be demonstrated:**
- Whether the hypothesized correlation exists in real data
- Whether ECE mediates any observed correlation
- Whether calibration interventions improve both metrics

## Limitations

### Critical Limitations

**Mock ASR data**: The most significant limitation is that TextFooler Attack Success Rates were simulated rather than measured. The simulation formula `asr = 0.5 + random * 0.15 - mc1 * 0.3` artificially creates negative correlation between MC1 and ASR, making all reported correlation values artifacts. This limitation invalidates all correlation-based findings.

**Insufficient sample size**: Only 3 of 12 planned models were evaluated. With n=3, correlation analysis lacks statistical power. Bootstrap confidence intervals and significance tests are unreliable at this sample size.

### Acceptable Limitations

**Correlational design**: Even with complete data, this study establishes correlation, not causation. Temperature scaling provides quasi-causal evidence, but the observational correlation analysis cannot prove calibration causes the relationship.

**Word-level perturbations only**: TextFooler represents one adversarial attack type. Findings may not generalize to character-level perturbations, sentence-level attacks, or distributional robustness.

**Open-weight models only**: We require logit access for ECE computation. Proprietary models (GPT-4, Claude) with logprob APIs could extend the scope but are not included.

## Technical Issues Identified

During pipeline validation, we identified and resolved several issues:

1. **Tokenizer padding**: Llama and Mistral models lacked padding tokens, causing TextFooler to fail. Fixed by setting `pad_token = eos_token`.

2. **70B model OOM**: Large models exceed single-GPU memory. Solution: multi-GPU inference with `device_map="auto"` or model quantization.

3. **T5 architecture mismatch**: FLAN-T5 is encoder-decoder, not ideal for classification-based attacks. May need to exclude from TextFooler evaluation.

## Implications for the Field

If the calibration-mediation hypothesis is supported by future experiments, this would:

1. **Unify evaluation**: Provide a single framework connecting factuality, robustness, and calibration
2. **Suggest interventions**: Temperature scaling as a simple method to improve both metrics
3. **Guide training**: Training objectives that improve calibration may transfer to both domains

If the hypothesis is refuted (r < 0.3 or mediation < 10%), this would:

1. **Establish independence**: Factuality and robustness are distinct properties
2. **Redirect research**: Different interventions needed for each dimension
3. **Bound expectations**: No "silver bullet" for LLM reliability

## Future Work

### Immediate Next Steps

1. Run real TextFooler attacks on all evaluated models
2. Complete evaluation for remaining 9 models
3. Re-run analysis with valid ASR data

### Extended Scope

1. Include additional benchmarks (HaluEval for factuality, BERT-Attack for robustness)
2. Test on proprietary models with logprob APIs
3. Investigate attention head correlations (NL-ITI direction)

## Conclusion Preview

The methodology presented here provides a principled framework for testing the calibration-mediation hypothesis. Full validation awaits real experimental data. We have demonstrated pipeline functionality and identified the path to completion.
