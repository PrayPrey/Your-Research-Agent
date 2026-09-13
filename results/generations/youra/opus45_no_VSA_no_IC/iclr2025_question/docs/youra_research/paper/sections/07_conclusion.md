# Conclusion

We began with a counterintuitive premise: that a probe trained to detect hallucinations on one LLM family could transfer to others with minimal degradation. Our experiments confirm this intuition. Probes trained on Llama-3-8B transfer to Mistral-7B and Qwen-2-7B hidden states with a mean AUROC gap of only 0.013 — negligible compared to the performance variation we might expect from hyperparameter choices alone.

## Summary

In this work, we addressed the question of whether semantic entropy probes generalize across LLM architectures. Our key insight is that transformer hidden states encode uncertainty in an architecture-invariant geometric structure that can be extracted by simple linear probes and transferred via affine alignment.

Our main contributions are:

1. **First systematic cross-family validation.** We tested SEP transfer across three distinct LLM families (Meta, Mistral AI, Alibaba), demonstrating that all six cross-family pairs achieve transfer gaps below 0.034 — well under the 0.10 threshold that would suggest architecture-specific encoding.

2. **Affine alignment for dimension mismatch.** We showed that least-squares affine mapping enables transfer between models with different hidden dimensions (3584 to 4096), with gaps as small as 0.003 — no retraining required.

3. **Evidence for convergent uncertainty encoding.** Our transfer matrix provides empirical support for the hypothesis that uncertainty is a fundamental property of transformer computation, not an architectural accident of individual model families.

## Future Directions

This work opens several promising directions grounded in our experimental findings:

**Scale validation.** Our experiments tested 7–8B parameter models. Chen et al. [2025] suggest that small-to-large transfer often succeeds; extending our methodology to 70B+ models would determine whether the architecture-invariant encoding persists at scale.

**Cross-benchmark evaluation.** The transfer gap we observed on TruthfulQA may or may not hold for other hallucination tasks. Our cross-dataset hypothesis (h-m1) showed promising initial results on TriviaQA→TruthfulQA transfer; systematic evaluation across HaluEval and NQ-Open would establish the generality of our findings.

**Nonlinear probes.** Our experiments used linear probes following the original SEP methodology. The finding that Qwen transfers with smallest gaps despite dimension mismatch suggests the uncertainty subspace may be more structured than a linear probe can fully exploit. Lightweight nonlinear alternatives (MLPs, kernel methods) may reduce transfer gaps further.

**Real-time deployment.** Single-pass inference and linear probe application are already efficient; latency benchmarking for production systems would establish practical deployment viability.

## Closing

We hope this work encourages the community to rethink model-specific assumptions in uncertainty estimation. If transformers converge on similar uncertainty encodings despite diverse training procedures and architectures, then universal uncertainty modules — trained once, deployed everywhere — become practically viable. The probe that "should have failed" on other families turns out to work surprisingly well.
