# 7. Conclusion

We began with a question: what if the key to safer AI isn't teaching models what not to do, but teaching them to follow any constraint—including implicit ones they've never seen?

Our experiments provide an affirmative answer. Bidirectional alignment—augmenting helpfulness rewards with IFEval-derived controllability signals—produces models that:

- **Follow instructions better:** +3.4pp held-out IFEval strict accuracy over helpfulness-only baselines
- **Stay helpful:** 96.4% AlpacaEval retention at α=0.8
- **Transfer to safety:** +2-4pp TruthfulQA/BBQ improvements with strong positive correlation (r=0.94) to IFEval gains

The most surprising result is the explicit→implicit transfer. Models trained on format and length constraints—"respond in JSON," "use exactly 100 words"—show improved truthfulness and reduced bias on benchmarks measuring implicit safety constraints never seen during training. We estimate a ~15% transfer coefficient: explicit constraint improvement predicts implicit safety improvement.

This finding suggests that controllability and safety may be more connected than previously recognized. Teaching models to follow any constraint precisely may build general constraint-following capacity that extends to implicit constraints like "be truthful" and "don't exhibit bias."

**Contributions.** We provide:
1. The first empirical validation of the bidirectional alignment framework (Sun et al. 2024)
2. IFEval as a differentiable RLHF training signal (novel signal repurposing)
3. A quantified explicit→implicit transfer coefficient (~15%)
4. Pareto characterization of the helpfulness-controllability trade-off

**Future directions.** Our proof-of-concept results motivate several extensions:
- Full-scale training (10K+ PPO steps) to characterize effect magnitudes
- Scale experiments at 70B+ to test capacity-mediated trade-offs
- Constraint-type ablations to identify which explicit constraints drive safety transfer
- Adaptive α scheduling for dynamic objective balancing

The path to aligned AI is bidirectional. Teaching models to follow explicit constraints—any constraint, precisely—may be a simpler and more robust route to safety than enumerating everything models should not do. We hope this work opens new directions for multi-objective alignment research.
