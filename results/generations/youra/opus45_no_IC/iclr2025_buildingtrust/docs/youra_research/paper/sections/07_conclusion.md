# Conclusion

We set out to test whether category-specific temperature scaling could exploit observed calibration variation in LLMs on truthfulness tasks. Our experiments confirmed that calibration error varies significantly across semantic categories (ANOVA p<0.001) and that confidence distributions differ substantially (17/21 cluster pairs significantly different). Yet this variation cannot be exploited: all categories require identical maximum temperature smoothing (T=10.0), revealing uniform overconfidence that dominates category-specific effects.

This negative result is itself the contribution. We provide the first systematic per-category calibration analysis on TruthfulQA, demonstrating that while category structure exists in calibration behavior, it does not translate to category-specific calibration needs. Temperature scaling — applied globally or per-category — hits the same ceiling.

Future work should explore calibration methods beyond temperature scaling: isotonic regression, learned calibrators, or training-time interventions that directly penalize miscalibration. The challenge is not identifying *which* categories are miscalibrated, but addressing the *uniform severity* of overconfidence across all categories.

Language models exhibit measurably different confidence patterns across semantic domains — yet this variation cannot be exploited for better calibration.
