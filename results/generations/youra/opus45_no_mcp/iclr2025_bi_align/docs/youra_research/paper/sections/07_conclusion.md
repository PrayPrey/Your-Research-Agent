# Conclusion

RLHF-trained language models exhibit systematic calibration inversion on specific task clusters—a paradox where high benchmark accuracy coexists with confident wrong predictions. We traced this failure to reward signal conflation, establishing a mechanism chain from annotator behavior through reward models to internal representations.

## Summary

Our investigation yielded three findings:

1. **Calibration inversion clusters systematically.** K-means clustering achieves silhouette = 0.6016, far exceeding the 0.3 threshold, revealing non-random failure patterns that enable mechanism investigation.

2. **Reward conflation has empirical support.** Annotators rate correctness and user-modeling tasks identically (rate_diff = 0.001), reward models inherit this conflation (overlap = 0.647), and model representations fail to separate task types (separation = 0.024). This three-step mechanism is robustly verified across three models.

3. **Keyword-based detection is insufficient.** Our feature extraction achieved only 2.3% prevalence, rendering the final causal link (features → clusters) uninformative. This establishes methodological boundaries for future work.

## The Calibration Paradox Revisited

We opened with a puzzle: why do RLHF models confidently predict wrong answers on specific tasks? The mechanism answer is clear—annotator conflation propagates through training to create blind spots in model confidence. The open question is whether bidirectional task features specifically drive this pattern, which requires semantic detection beyond our keyword approach.

## Future Work

Three directions extend this research:

**Semantic feature detection.** LLM-based or embedding-based classification could achieve higher prevalence than the 2.3% achieved by keywords, enabling correlation analysis.

**Annotation intervention.** If annotator conflation causes the problem, guidelines distinguishing correctness from user-modeling could provide cleaner training signals.

**Calibration-aware RLHF.** Training objectives that penalize calibration inversion on identified task clusters could directly address the failure mode.

## Closing

The calibration paradox has a mechanism explanation: what annotators don't distinguish, models can't learn to distinguish. Fixing detection is the next frontier toward calibration-aware RLHF training.
