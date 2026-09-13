# Conclusion

We began with a simple observation: practitioners universally default to LoRA rank $r=16$ without principled justification. We end with an empirical scaling law: **optimal LoRA rank scales sub-linearly with model size**, following $r_{\text{opt}} \propto N^\alpha$ where $\alpha \in (0.3, 0.8)$ depending on task type.

This relationship has immediate practical value. Rather than guessing or expensive grid search, practitioners can now prescribe rank based on model scale. For a 12B model, rank=16 likely under-adapts; for a 1B model, rank=64 over-parameterizes. The scaling law provides a principled starting point.

We also uncovered mechanistic insights. Larger models exhibit a phase transition in rank sensitivity—the penalty for suboptimal rank increases super-linearly with scale. This makes principled rank selection more important, not less, as models grow. Surprisingly, attention entropy *decreases* with model size, suggesting larger models develop focused, specialized representations rather than distributed patterns.

Our scope is bounded. The scaling exponent varies by task family (single-hop vs multi-hop QA differ by $|\Delta\alpha| = 0.51$), and we tested only Pythia models. Generalization to other architectures and task types requires future work.

Moving forward, two directions are promising:
1. **Task-calibrated $\alpha$**: Develop complexity metrics predicting the scaling exponent for new tasks
2. **Attention-focus scaling**: Test whether optimal rank correlates with inverse attention entropy

The era of ad-hoc LoRA rank selection can end. With scaling laws as guides, efficient adaptation becomes predictable.
