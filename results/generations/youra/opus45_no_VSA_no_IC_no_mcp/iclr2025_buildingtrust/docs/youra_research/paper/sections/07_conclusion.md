# Conclusion

We began by asking whether two capabilities often studied in isolation—truthfulness and adversarial robustness—might share an underlying connection. Our work provides a clear answer: they do.

## Summary

We conducted the first systematic correlation analysis between TruthfulQA MC1 and AdvGLUE accuracy across 14 decoder-only LLMs from four families. After controlling for model size, we found a strong positive correlation (r=0.80, p<0.001) with a confidence interval that excludes zero. This establishes that models resistant to generating misinformation also tend to resist adversarial attacks.

We then tested the most intuitive explanation—that well-calibrated models enable both capabilities through accurate uncertainty estimation. Our experiments falsified this hypothesis: ECE shows no significant correlation with either metric, and poorly-calibrated models paradoxically exhibited stronger truthfulness-robustness correlation than well-calibrated ones.

## Future Directions

Our mechanism falsification opens several research avenues:

**Alternative mechanisms:** The correlation's existence suggests a common cause, but calibration is not it. Future work should investigate training data quality, representation alignment, and task-specific calibration measures as candidate mechanisms.

**Larger model samples:** Our tertile analysis (4-5 models per group) lacked statistical power. Studies with 30+ models across comparable scales would enable robust mechanism testing.

**Instruction-tuned models:** Our instruction-tuned sample (N=6) was too small for reliable conclusions. Understanding whether instruction tuning preserves or disrupts the correlation has practical implications for model deployment.

We hope this work encourages the research community to study trust dimensions jointly rather than in isolation, and to rigorously test mechanistic hypotheses rather than assuming them.
