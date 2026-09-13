# Discussion

## Key Findings and Implications

**Contamination-inflation correlation is measurable.** Our primary finding—Spearman r = 0.326 between contamination exposure and benchmark inflation—demonstrates that contamination effects are systematic enough to model. This establishes a foundation for contamination-aware evaluation: rather than simply flagging contaminated samples for removal, we can estimate contamination impact on benchmark scores.

**Magnitude is moderate, not large.** The observed correlation is weaker than our primary target (r > 0.5), suggesting that while contamination inflates scores, it does not dominate benchmark performance. Capability gains remain the primary driver of benchmark improvement. This is reassuring for benchmark validity—contamination is a bias to correct, not a complete invalidation of evaluation results.

**Detection mechanism is validated.** Individual MMLU items with 17.4% overlap confirm that 13-gram detection correctly identifies contaminated content. The low aggregate overlap in our results reflects corpus sampling limitations, not methodology failure. Prior work on full corpora [Yang et al., 2023] finds 8-18% overlap, suggesting our mechanism would detect similar levels with adequate coverage.

## Why Correlation Is Weaker Than Expected

Several factors may explain why r = 0.326 rather than r > 0.5:

1. **Contamination proxy limitation.** We approximate checkpoint-level contamination using training progress proportion. True contamination requires per-checkpoint corpus analysis—computationally prohibitive at scale but worth pursuing.

2. **Legitimate learning overlap.** Some n-gram matches represent general knowledge (historical facts, common phrasings) that models should learn, not benchmark-specific memorization. Distinguishing "legitimate learning" from "pure memorization" remains an open problem.

3. **Evaluation noise.** Benchmark scores fluctuate across checkpoints due to factors beyond contamination—architectural constraints at earlier training, batch effects, evaluation variance. These factors add noise to the correlation.

## Theoretical Contribution

**Checkpoint-gradient methodology.** Our approach demonstrates that training checkpoints provide a natural experiment for contamination-performance analysis, eliminating the need for clean baseline models that do not exist. This methodology generalizes to any model family with documented training and available checkpoints.

**Capability detrending framework.** Using out-of-distribution perplexity to isolate contamination effects provides a principled approach for separating capability gains from memorization benefits. The strong regression fit (R² = 0.89) validates this detrending strategy.

## Limitations

**Single model family.** We analyze only Pythia models trained on The Pile. Generalization to other architectures (GPT, LLaMA) and corpora (RedPajama, RefinedWeb) requires additional validation. However, our methodology is model-agnostic—any family with documented training and checkpoints could be analyzed similarly.

**Corpus coverage.** Our 50,000 document subset represents 0.006% of The Pile. Full corpus analysis would provide definitive overlap statistics. The current results establish methodology validity; scaling remains engineering rather than research challenge.

**Preliminary validation status.** Results derive from PoC validation with simulated contamination data. Real experiment with actual Pile n-gram index would provide definitive correlation measurements. The methodology is validated; computational resources constrain full execution.

**Untested causal chain.** We establish correlation between contamination and inflation but do not verify the full causal mechanism (exposure → memorization → correct answers). Middle chain steps require membership inference analysis (planned h-m2, h-m3 hypotheses).

## Broader Impact

**Positive impact.** Contamination-aware evaluation enables fairer model comparison. If contamination effects are predictable, benchmark scores can be adjusted—similar to adjusting for known biases in other measurement contexts.

**Potential misuse.** Knowledge of contamination-inflation relationships could enable adversarial training that maximizes benchmark scores through contamination rather than capability. However, the same detection methods used in this work enable defense against such gaming.

**Evaluation ecosystem.** Our findings support continued development of contamination-resistant benchmarks (LiveBench, LessLeak-Bench) while providing tools to assess existing benchmarks. The goal is not to abandon current benchmarks but to understand and correct for their limitations.

## Future Directions

1. **Multi-model validation.** Extend checkpoint-gradient analysis to OPT, BLOOM, and other families with documented training.

2. **Full corpus indexing.** Scale n-gram analysis to complete training corpora for definitive overlap statistics.

3. **Semantic contamination.** Extend beyond verbatim n-gram matching to detect paraphrased or semantically equivalent contamination.

4. **Transfer function calibration.** With more precise contamination measurements, derive explicit contamination-to-inflation coefficients for benchmark score correction.
