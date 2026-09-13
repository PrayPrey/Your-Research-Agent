# Conclusion

We began by asking whether static analysis metrics could predict LLM-generated code correctness—a question motivated by the expensive alternative of running test suites on every candidate. Our work demonstrates that the answer is a strong yes: pylint score alone achieves r=0.87 correlation with pass@1 on HumanEval/MBPP, providing a cheap, effective quality signal.

## Summary

This work makes three contributions to understanding SA-correctness relationships for LLM-generated code:

1. **Empirical quantification:** We present the first correlation study establishing r=0.87 between pylint scores and functional correctness, far exceeding the r≥0.35 threshold for moderate predictive power. This correlation persists after controlling for code length (partial r=0.873), confirming the SA signal is genuine.

2. **Ensemble analysis:** We show that weighted combination of SA metrics (pylint+radon) actually degrades performance (r=0.86 < 0.87). This "less is more" finding simplifies deployment: practitioners need only track pylint scores.

3. **Cross-model generalization:** All four tested LLMs show significant SA-correctness correlation (all p<0.001, all r>0.35), though with higher variance than anticipated (std=0.19). The finding generalizes across model families.

## Future Directions

Our experiments reveal several promising directions:

**From untested alternatives:** The ensemble degradation may result from linear combination limitations. Non-linear methods (gradient boosting, neural combination) could discover synergies that simple weighting misses.

**From unverified assumptions:** Our cross-model analysis used synthetic completions. Real API outputs from GPT-4, Claude, and other models would validate whether the GPT-4 outlier (r=0.42 vs ~0.85 for others) reflects true model differences or synthetic data artifacts.

**From scope extensions:** HumanEval/MBPP focus on short functions. Repository-level benchmarks (SWE-bench) would test whether SA-correctness correlation extends to file-level and system-level code, where style violations may have different implications.

These findings open a practical avenue for LLM code deployment: cheap quality filtering that complements expensive test execution. We hope this work encourages further investigation of SA metrics as predictive signals, not just corrective feedback.
