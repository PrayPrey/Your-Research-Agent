## 7. Conclusion

We opened by observing that HumanEval-style algorithm training outperforms MBPP utility-script
training on MBPP's own benchmark — consistently, across all three random seeds. After tracing
the causal mechanism through embedding-space distributional alignment, we can now explain why:
the model trained on the data most similar to the test distribution (in code-embedding space)
achieves the highest performance, regardless of whether that similarity is expected from
surface-level benchmark names.

### Summary

In this work, we addressed the question of what code SFT actually teaches by isolating the
causal effect of SFT source identity under token-budget equalization. Our key findings are:

1. **Source identity dominates HumanEval+ pass@1 by up to 29.6pp** (ANOVA F=11.37, p=0.020)
   — an effect larger than most reported architectural improvements. The choice of which
   problems to train on matters more than practitioners typically assume.

2. **Embedding alignment predicts performance rank** before any training: CodeBERT cosine
   similarity between training source and test benchmark perfectly predicts HumanEval+ pass@1
   rank across four conditions (Spearman ρ=1.0, p=0.042, dual-encoder concordant). This
   enables principled source selection from embedding measurements alone.

3. **Algorithmic training generalizes better than utility-script training**: HumanEval-only SFT
   achieves the highest MBPP+ pass@1 (~52%) across all three seeds, exceeding MBPP-only
   SFT (~50.5%). Training on the benchmark you want to target is not always the best strategy.

4. **Scale reduces source sensitivity without eliminating the mechanism**: At 7B, the absolute
   between-condition spread narrows (5.5pp vs 31.9pp at 1.3B) and equal-mix rises to match
   HumanEval-only, suggesting that richer pretraining coverage allows diversity to compete.
   Near-deterministic within-condition reproducibility at 7B motivates using absolute spread,
   not η², for cross-scale comparisons.

### Future Directions

Several directions follow directly from our experimental evidence:

**From the asymmetric generalization finding:** Classify MBPP+ tasks into algorithmic versus
utility subtypes and measure HumanEval-only and MBPP-only pass@1 per subtype. If HumanEval-only's
advantage concentrates on algorithmic MBPP+ tasks, it confirms that the generalization
mechanism is subtype-mediated, not benchmark-mediated.

**From the alignment mechanism:** Use embedding cosine similarity to the target benchmark as
an active data selection criterion — from a mixed training pool, select the top-K most aligned
problems before training. GRAPE [Zhang et al., 2025] validates this approach for general
instruction tuning; applying it with CodeBERT alignment scoring for code-specific SFT is the
natural next step.

**From incomplete MBPP+ evaluation:** Re-run MBPP+ evaluation on the existing 24 SFT
checkpoints (4 conditions × 2 scales × 3 seeds). All checkpoints are preserved; the compute
cost is evaluation-only (~4 GPU-hours). This would complete the full 2×4 transfer matrix
and enable the full mechanistic alignment test on MBPP+ at both scales.

**From the scale finding:** Apply variance-normalized effect size (Cohen's d on condition
means) for scale comparison, alongside absolute spread, in future source-identity studies at
multiple scales.

Understanding what code SFT actually teaches — which distributional properties of training
data transfer to test benchmarks, and why — is essential for reproducible benchmark evaluation
and principled data curation. We hope this work, by providing both the controlled empirical
evidence and the embedding alignment framework, accelerates that understanding.
