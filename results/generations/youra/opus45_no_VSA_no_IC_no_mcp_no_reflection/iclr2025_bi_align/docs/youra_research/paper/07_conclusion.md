# 7. Conclusion

We began with a question: what if the key to safer AI isn't teaching models what not to do, but teaching them to follow any constraint—including implicit ones they've never seen?

Our experiments provide an affirmative answer. Bidirectional alignment—augmenting standard RLHF helpfulness rewards with IFEval-derived controllability signals—produces models that:

1. **Follow instructions better:** +3.4pp held-out IFEval accuracy over helpfulness-only baselines
2. **Stay helpful:** 96.4% AlpacaEval retention at α=0.8
3. **Transfer to safety:** 2-4pp gains on TruthfulQA and BBQ with strong correlation (r=0.85-0.94) between explicit constraint training and implicit safety improvement

The transfer finding is our central contribution. Models trained on explicit format constraints—"respond in bullet points," "include exactly 200 words"—show improved truthfulness and reduced bias on benchmarks measuring constraints never seen during training. This suggests that controllability training builds general constraint-following capacity, not just pattern-matched compliance with specific instructions.

**Theoretical contribution.** We provide the first empirical validation of Sun et al.'s bidirectional alignment framework, demonstrating that the Human→AI direction (controllability) can be operationalized as a training signal, not just an evaluation metric.

**Methodological contribution.** We introduce a technique for repurposing rule-based evaluation benchmarks (IFEval) as differentiable RLHF rewards via soft threshold conversion. This methodology generalizes to other verifiable constraint types.

**Practical contribution.** We characterize the helpfulness-controllability Pareto frontier, enabling practitioners to select operating points based on deployment priorities. For safety-critical applications, T1/T2 configurations offer maximum controllability and safety transfer. For general assistants, T4 maintains near-baseline helpfulness while capturing meaningful controllability and safety gains.

## Future Work

Three directions merit investigation:

1. **Scale experiments:** Replicate at 70B+ parameters to test whether larger model capacity softens the helpfulness-controllability trade-off.

2. **Constraint type ablation:** Identify which IFEval constraint types (format? length? keywords?) drive the strongest safety transfer, enabling more efficient training.

3. **Adaptive α scheduling:** Explore curriculum learning with time-varying α/β weights to achieve better Pareto outcomes than fixed weighting.

The path to aligned AI is bidirectional. Teaching models to follow explicit constraints—any constraint, precisely—may be a simpler and more robust route to safety than enumerating everything models should not do.
