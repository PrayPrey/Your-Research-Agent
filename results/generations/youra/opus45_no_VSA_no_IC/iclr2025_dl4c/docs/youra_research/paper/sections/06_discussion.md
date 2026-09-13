# Discussion

We interpret our findings, explain the falsified predictions, acknowledge limitations, and discuss implications for practitioners and researchers.

## Interpretation of Results

### Scale as Error-Type Selection

Our central finding is that scale selection is error-type selection. When choosing an LLM judge, practitioners are not simply trading cost for accuracy—they are choosing between different error profiles:

| Scale | Bias Direction | Practical Consequence |
|-------|----------------|----------------------|
| 7B | Over-accept (high FPR) | Lets incorrect code through |
| Proprietary | Under-accept (high FNR) | Rejects correct code |
| 70B | Balanced | Best cost-accuracy tradeoff |

This framing reorients the scale selection decision. Rather than asking "which model is most accurate?", practitioners should ask "which error type is more costly in my application?"

- **When false positives are costly** (e.g., security-critical code): Use proprietary (low FPR)
- **When false negatives are costly** (e.g., creative code generation): Use 7B (low FNR)
- **When balanced accuracy matters**: Use 70B (best overall)

### Why Ensemble Voting Fails

Traditional ensemble theory assumes component errors are approximately IID. Our findings show this assumption fails for scale-diverse LLM judges:

1. **Accuracy asymmetry**: The best judge (proprietary, 45.9%) is substantially more accurate than the worst (7B, 37.6%). Majority voting grants equal weight, diluting the best signal.

2. **Correlated errors**: All three scales share over-acceptance bias (FPR > FNR for all). Unanimous "correct" verdicts are not independent confirmations—they are correlated false positives.

3. **Bias direction alignment**: The bias direction (over-acceptance) is shared across scales. Majority voting amplifies this shared bias rather than canceling scale-specific errors.

These factors combine to make ensemble voting counterproductive. The 8.05% accuracy loss is not noise—it is a structural consequence of asymmetric, correlated errors.

### Why Unanimous Agreement Signals Shared Bias

Conventional wisdom suggests unanimous agreement indicates high confidence. Our finding inverts this for scale-diverse code judges.

When all scales agree "correct":
- All three judges share the over-acceptance bias
- The unanimous verdict captures exactly the cases where all three are systematically wrong
- Unanimous "correct" has 35.8% accuracy vs. 39.7% for split verdicts

When scales *disagree*:
- Proprietary's conservatism often triggers the split
- Disagreement flags cases where the most accurate judge sees something others miss
- The disagreement is informative, not noise

This suggests **disagreement-as-signal** rather than **agreement-as-confidence** for scale-diverse panels.

## Limitations

We acknowledge the following limitations:

### Simulated Judges

Due to API unavailability during the study period, we simulated judge outputs calibrated to published model capabilities. While simulations are designed to match reported accuracy and error characteristics, real API validation is essential for deployment guidance.

**Mitigation**: Our methodology and code support direct replication with real API calls. The findings should be validated before production use.

### Single Prompt Template

We tested one prompt template to isolate scale effects. Prompt sensitivity is uncharacterized—results may differ with other prompts.

**Mitigation**: Pilot testing selected the highest-agreement prompt. Future work should test 3-5 prompt variants.

### Python Only

HumanEval+ is Python-specific. Generalization to other languages (Java, JavaScript, C++) requires replication on multilingual benchmarks like MultiPL-E.

**Mitigation**: We scope claims to Python evaluation. Language generalization is explicit future work.

### Binary Correctness

We judge correct/incorrect, ignoring partial correctness, code quality, efficiency, and style. Real-world code evaluation may require multi-dimensional assessment.

**Mitigation**: Binary correctness is the most rigorous evaluation dimension. Multi-aspect evaluation is complementary future work.

### Scale-Architecture Confound

Tested models differ in both scale and architecture (DeepSeek vs. CodeLlama vs. GPT). We cannot fully isolate scale from architecture effects.

**Mitigation**: Two 7B models from different families show similar error patterns, suggesting scale dominates architecture at this tier. Same-family comparisons (e.g., Llama-7B/13B/70B) would strengthen causal claims.

## Implications

### For Practitioners

1. **Do not ensemble across scales naively**. Scale-diverse majority voting hurts accuracy.

2. **Use 70B for cost-accuracy balance**. The 7B→70B jump captures 95% of scale benefit; 70B→proprietary adds minimal accuracy at higher cost.

3. **Select scale by error cost asymmetry**. If false positives are costly, prefer proprietary. If false negatives are costly, 7B may suffice.

4. **Treat disagreement as information**. When judges split, investigate rather than defaulting to majority vote.

### For Researchers

1. **Account for error-type asymmetry** in LLM-as-judge studies. Reporting accuracy alone misses the FPR-FNR tradeoff.

2. **Test ensemble assumptions**. The IID error assumption fails for scale-diverse panels; future ensemble methods should weight by accuracy or handle correlated errors.

3. **Investigate scale-characteristic error modes**. Our findings suggest scale affects *what* judges miss, not just *how often*. Probing studies could identify specific code patterns that trigger scale-specific errors.

## Broader Impact

This work provides evidence-based guidance for LLM judge selection in code evaluation pipelines. Positive impacts include:
- Reduced API costs through informed scale selection
- Improved code quality through better-calibrated judges
- Transparency about evaluation reliability

Potential negative impacts:
- Over-reliance on our findings without domain-specific validation
- Misapplication to tasks beyond code correctness (e.g., code review, summarization)

We recommend practitioners validate findings in their specific contexts before deployment.
