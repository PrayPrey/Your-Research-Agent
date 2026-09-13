# Conclusion

When all three LLM judges unanimously agree that code is correct, they are wrong 64% of the time. This counterintuitive finding reflects not collective wisdom but collective bias—unanimous agreement captures the intersection of over-acceptance errors shared across scales.

We presented the first scale-controlled analysis of error patterns in LLM code judges. Our findings establish that:

1. **Scale predicts error TYPE, not just rate.** Smaller models over-accept (FPR=74.8% at 7B); larger models under-accept (FNR=29.3% at proprietary). The FPR-FNR tradeoff is a fundamental scale characteristic.

2. **Ensemble voting fails.** Scale-diverse majority voting degrades accuracy by 8.05% compared to the best single judge (p=1.45×10⁻⁶). Correlated, asymmetric errors violate the IID assumption underlying ensemble benefit.

3. **Unanimous agreement is anti-informative.** Split verdicts (39.7% accuracy) outperform unanimous verdicts (35.8%). Disagreement from the most accurate judge is informative signal, not noise.

These results overturn common intuitions about scale and ensembles. Practitioners should select scale based on error-cost asymmetry rather than naive accuracy maximization, and should not combine judges across scales through majority voting.

The practical recommendation is simple: use 70B-class models for the best cost-accuracy tradeoff. The 7B→70B transition captures 95% of scale benefit (12.2pp of 12.8pp total gain). Going from 70B to proprietary adds only 0.6pp accuracy—marginal improvement at substantially higher cost.

Looking forward, our findings suggest three research directions:

**Selective ensemble strategies.** Rather than majority voting, use proprietary alone and defer to 70B only when proprietary indicates uncertainty. Disagreement-triggered abstention may outperform forced verdicts.

**Error-type-aware weighting.** Downweight 7B on "correct" verdicts (high FPR) and proprietary on "incorrect" verdicts (high FNR). Verdict-specific confidence calibration could improve ensemble accuracy.

**Scale-error characterization.** Identify specific code patterns (edge cases, subtle logic, surface features) that trigger scale-specific errors. This would enable problem-aware judge selection rather than one-size-fits-all scale choice.

Scale selection is error-type selection. Choose your judge by the error you can afford, not by the accuracy you hope for.
