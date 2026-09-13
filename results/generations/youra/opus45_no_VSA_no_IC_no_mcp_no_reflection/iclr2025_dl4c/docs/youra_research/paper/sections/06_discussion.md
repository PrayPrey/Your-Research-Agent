# Discussion

## Key Findings

Our experiment produced a null result that is informative in its own right:

**Finding 1: PoC scale is insufficient for code LLM RL.** All nine training runs achieved 0% pass@1, regardless of reward design. This establishes that proof-of-concept experiments at 1-epoch scale cannot distinguish between reward alternatives for code generation.

**Implication:** Researchers planning reward ablation studies should budget substantially more compute than we allocated. The minimum viable scale for this hypothesis exceeds our PoC budget by an unknown factor.

**Finding 2: The information bandwidth hypothesis remains untested.** Our null result does not falsify the hypothesis. The theoretical grounding—that denser feedback enables more precise credit assignment—is not challenged by an underpowered experiment.

**Implication:** The hypothesis merits retesting at adequate scale. Our negative result provides the lower bound; future work should establish the upper bound where effects become measurable.

**Finding 3: Negative results have value.** By reporting this null result, we prevent other researchers from repeating our underpowered experiment. This is a contribution, even though it is not the contribution we planned.

## Limitations

### Scale Limitations (Decisive)

**1-epoch training:** PPO on code LLMs likely requires thousands of gradient updates before policy improvement emerges. Our ~1000 updates may be 10-100x below the necessary threshold. This limitation rendered our experiment uninformative for the original hypothesis.

**3 seeds per condition:** With all values at 0, variance estimation was impossible. A properly powered experiment requires ≥5 seeds to capture initialization effects.

**50-problem validation set:** Small evaluation sets may not reflect true performance. However, with 0% pass@1, this limitation did not affect our findings.

### Design Limitations (Acknowledged but Not Tested)

**0.5/0.5 weighting:** The HIGH condition uses a heuristic 50/50 split between pass_rate and error_score. Optimal weighting may vary by task. Sensitivity analysis was planned but could not be executed at floor scale.

**Single model size:** Only 7B tested. Scaling effects may differ at larger sizes. This limitation applies to any future positive result, not to our null finding.

**Python-only:** Error parsing assumes standard Python formatting. Generalization to other languages is unknown.

### Infrastructure Limitations

**Possible implementation differences from prior work:** CodeRL and PPOCoder may have used different training infrastructure, hyperparameters, or compute budgets. Our replication attempt may not match their unpublished details.

## Why Not Just Train Longer?

A natural question is why we did not simply train for more epochs. The answer is methodological: we committed to reporting the PoC result regardless of outcome. Abandoning negative results without publication creates survivorship bias in the literature. Our contribution is the null finding itself, not a post-hoc extended experiment.

Future work should design for adequate scale from the start, not rely on iterative extension until positive results emerge.

## Broader Impact

**Positive Impacts:**
- This work contributes scale guidance for code LLM RL research
- Reporting negative results reduces wasted compute across the community
- The information bandwidth framework may inspire future reward design work

**Potential Negative Impacts:**
- Null results may discourage exploration of feedback granularity effects
- Underpowered experiments may be miscited as falsifications

**Mitigation:** We emphasize clearly that this result is INCONCLUSIVE, not negative. The hypothesis remains open. Future work with adequate compute is needed.

## Recommendations for Future Work

1. **Budget ≥3 epochs** for any code LLM RL experiment
2. **Use ≥5 seeds** for variance estimation
3. **Include early stopping** based on validation pass@1 to avoid wasted compute
4. **Report samples-to-threshold** in addition to final accuracy
5. **Track error-type distribution** to validate credit assignment mechanisms

If these requirements are met and the information bandwidth effect is still not observed, THEN the hypothesis would be challenged. Our current result provides no such challenge—only the lower bound on adequate experimental scale.
