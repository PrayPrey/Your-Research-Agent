# Conclusion

We have presented a methodology for testing whether calibration quality mediates the correlation between LLM factuality and adversarial robustness. Our approach connects three previously isolated research communities—factuality evaluation, adversarial robustness, and calibration—through a testable hypothesis.

## Contributions

1. **Hypothesis formalization**: We articulated a testable claim that ECE-measured calibration serves as a shared internal signal enabling both factuality error detection and adversarial robustness.

2. **Evaluation pipeline**: We developed and validated a pipeline computing TruthfulQA MC1, TextFooler ASR, and ECE across diverse open-weight LLMs.

3. **Analysis framework**: We implemented correlation analysis with confound control (scale, family), mediation testing, and visualization.

## Current Status

The pipeline is validated but experimental results are incomplete. Three of twelve planned models were evaluated, and ASR values were simulated rather than measured from real attacks. No valid conclusions about the hypothesis can be drawn from current data.

## Path Forward

To complete this work:
1. Execute real TextFooler attacks on all models
2. Evaluate remaining nine models
3. Compute ECE from prediction logits
4. Run mediation analysis with real data
5. Test temperature scaling intervention

## Implications

If calibration does mediate the factuality-robustness relationship, this would provide a unified framework for LLM reliability evaluation and suggest that improving calibration—through temperature scaling or training objectives—could simultaneously improve both dimensions.

The methodology presented here provides the foundation for this investigation. We look forward to reporting complete results.
