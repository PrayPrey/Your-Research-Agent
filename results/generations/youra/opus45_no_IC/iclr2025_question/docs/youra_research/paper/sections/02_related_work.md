# Related Work

We review uncertainty-based hallucination detection methods and their evaluation paradigms, highlighting the absence of systematic cross-benchmark transfer analysis that motivates our work.

## Uncertainty Quantification for LLMs

Semantic entropy (Kuhn et al., 2023) computes uncertainty over clusters of semantically equivalent generations, achieving approximately 0.85 AUROC on TriviaQA. By using bidirectional entailment to group generations by meaning rather than surface form, semantic entropy captures linguistic invariances that token-level entropy misses. However, this work—like most in the field—evaluates each benchmark independently without testing cross-benchmark transfer.

P(True) methods (Kadavath et al., 2022) prompt models to predict the probability that their own outputs are correct. Calibration improves with model scale, but the approach requires explicit self-evaluation prompting and has not been evaluated across diverse benchmark families. Our work focuses on semantic entropy, which operates during generation rather than requiring post-hoc evaluation.

Token-level uncertainty measures including entropy and predictive variance have been explored for uncertainty estimation (Xiao & Wang, 2021), but semantic entropy consistently outperforms these approaches by accounting for meaning-level rather than surface-level variation.

## Consistency-Based Detection

SelfCheckGPT (Manakul et al., 2023) detects hallucinations by measuring consistency across multiple samples, achieving strong performance on WikiBio without requiring external knowledge. While methodologically distinct from entropy-based approaches, consistency methods face similar transfer questions: calibration on one domain does not guarantee performance on another. Our clustering framework could extend to consistency-based methods in future work.

Recent work has explored black-box detection using verbalized confidence (Lin et al., 2022), but these approaches sacrifice the granular uncertainty information available when model logits are accessible. We focus on open-weight models where logit access enables semantic entropy computation.

## Benchmark Evaluation Paradigms

Existing hallucination benchmarks—TriviaQA (Joshi et al., 2017), HaluEval (Li et al., 2023), FEVER (Thorne et al., 2018), and others—have been treated as interchangeable representatives of "factual QA." HaluEval provides hallucination annotations across QA, summarization, and dialogue; FEVER tests claim verification against Wikipedia evidence. However, no prior work has examined whether benchmarks cluster into distinct families based on the error processes they probe.

Domain adaptation literature (Ben-David et al., 2010) provides theoretical grounding for our findings: distribution shift degrades transfer, and distribution similarity predicts transferability. We operationalize this theory for hallucination detection, using JS-divergence to measure uncertainty distribution similarity and hierarchical clustering to discover benchmark families.

## Positioning Our Contribution

Prior work establishes that uncertainty-based methods achieve strong in-distribution performance. What remains unknown is when this performance transfers. We address this gap by:

1. Computing pairwise JS-divergence across benchmark entropy distributions to reveal hidden structure
2. Discovering that benchmarks cluster by error-generation process, not surface features
3. Quantifying transfer boundaries (within-cluster ≤0.08, cross-cluster >0.15 degradation)
4. Providing a practical criterion (cluster membership) for predicting transfer success

This work bridges in-distribution evaluation and deployment reality by establishing when recalibration is necessary versus when existing thresholds can be reused.
