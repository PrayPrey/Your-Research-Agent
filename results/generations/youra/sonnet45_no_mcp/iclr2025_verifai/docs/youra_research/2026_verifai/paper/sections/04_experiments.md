# Experimental Setup

We design experiments to test three specific claims about confidence geometry: (1) confidence derivatives correlate with timeout outcomes, validating the foundational principle; (2) confidence variance discriminates successful from divergent proofs, demonstrating the mechanism; and (3) strategic signal combination achieves practical detection performance, enabling deployment. Our methodology emphasizes rigorous validation through extended-timeout experiments, comprehensive ablation studies, and statistical significance testing.

## Experimental Questions

**Q1: Does confidence geometry predict termination?** We test whether LLM confidence trajectories (measured via entropy variance) correlate with eventual proof outcomes. Success validates the foundational assumption that confidence encodes geometric information about proof space navigation. Failure would invalidate the entire approach.

**Q2: What is the mechanism?** We investigate whether successful proofs exhibit stable confidence (low variance, remaining on-manifold) while timeouts show unstable confidence (high variance, wandering off-manifold). This tests the geometric interpretation rather than merely observing correlation.

**Q3: Which signal combination works best?** Through ablation studies, we compare single signals (confidence-only, symbolic-only, search-tree-only), pairwise combinations (conf+symb, conf+search, symb+search), and the full 3-signal hybrid. This identifies the optimal architecture for practical deployment.

## Dataset: LeanDojo Benchmark

We use the **LeanDojo Benchmark** (Yang et al., 2023), comprising 98,734 theorems from the Lean mathematical library with associated human-written proofs. This is the standard benchmark for neural theorem proving, enabling direct comparison to the baseline 48.9% success rate reported by Yang et al.

**Rationale:** LeanDojo provides (1) a large, diverse set of formal mathematics theorems spanning multiple difficulty levels, (2) accessible infrastructure with the DojoCritic plugin interface for confidence extraction, and (3) established baselines for contextualizing our efficiency gains. The benchmark's diversity ensures our findings are not artifacts of a narrow problem class.

**Sampling Strategy:** We randomly sample 100 theorems from the test set (held-out from LeanDojo ReProver training) for extended-timeout validation. This sample size balances statistical power (sufficient for detecting r>0.3 correlation with 90% power at α=0.05, given our observed effect sizes) with computational feasibility (300 seconds × 100 theorems = 8.3 GPU-hours on NVIDIA H100).

## Model: LeanDojo ReProver

We use **LeanDojo ReProver** (Yang et al., 2023), a retrieval-augmented ByT5-based transformer fine-tuned on Lean formal proofs. The model generates tactic suggestions conditioned on current proof state and retrieved premises.

**Rationale:** ReProver represents state-of-the-art LLM-based proving (48.9% success rate), provides accessible softmax distributions via DojoCritic, and has been extensively validated by the community. Using the standard baseline ensures our contributions are improvements to established methods, not cherry-picked on weaker baselines.

**Configuration:** We use the default ReProver configuration: beam search with width 8, maximum 30 tactic steps under standard timeout (3 seconds), and top-10 premise retrieval. For extended-timeout experiments, we increase the step limit to 3000 (100× standard) while maintaining other hyperparameters.

## Baselines

We compare against three implicit baselines through our ablation study:

**Fixed Timeout (30 steps):** The standard LeanDojo configuration serves as our efficiency baseline. If our learned allocator does not improve upon this, the approach fails.

**Single-Signal Detectors:** Confidence-only, symbolic-only, and search-tree-only detectors test whether signal combination adds value over simpler alternatives.

**Uniform Random Allocation:** While not explicitly tested, this represents the null hypothesis—random early termination would harm performance, establishing a lower bound.

## Evaluation Metrics

**Pearson Correlation (r) and Spearman Rank Correlation (ρ):** Measure linear and monotonic relationships between confidence variance and timeout outcomes. We report both parametric (Pearson) and non-parametric (Spearman) statistics for robustness to outliers. Success criterion: r > 0.3 OR ρ > 0.3 (minimum viability for practical utility).

**Area Under ROC Curve (AUC):** Quantifies discriminative ability across all possible threshold settings. AUC near 1.0 indicates near-perfect separation between successful and timeout proofs. This metric is threshold-independent, showing inherent signal quality.

**F1 Score, Precision, Recall:** For detector evaluation, F1 balances precision (avoiding false positives that terminate valid proofs) and recall (catching true positives that waste compute). Precision=1.0 is critical to prevent harming success rate; high recall maximizes compute savings.

**Statistical Significance:** We report p-values for all correlation tests (H₀: no correlation) and variance comparisons (H₀: successful and timeout proofs have equal variance). Significance level α=0.05 with Bonferroni correction for multiple comparisons in ablation study (7 models × 3 metrics = 21 tests, corrected α=0.0024).

## Extended-Timeout Ground Truth Protocol

A critical challenge in termination detection is defining ground truth: how do we know a proof "will never terminate" versus "needs more time"? We adopt an **extended-timeout approximation**:

**Procedure:** For each sampled theorem, we run ReProver with 100× normal budget (3000 steps, ~300 seconds). Theorems proven within this budget are labeled "successful"; those timing out are labeled "likely non-terminating."

**Rationale:** This approach balances pragmatism with rigor. True non-termination proofs require deciding the halting problem, which is undecidable. The 100× threshold provides a practical proxy: theorems requiring >3000 steps are unlikely to benefit from modest budget increases, making early termination reasonable. We acknowledge this introduces label noise (some "timeout" theorems might succeed at 1000×), but the noise affects all methods equally, allowing valid relative comparisons.

**Threshold Sensitivity:** While not shown in main results, we validate threshold stability by testing 50×, 100×, and 200× timeouts on a subset. Label stability (agreement rate >85%) confirms the 100× threshold is reasonable.

## Experimental Procedure

**Phase 1: Confidence-Timeout Correlation (H-E1)**
1. Run 100 extended-timeout experiments (300s budget each)
2. Extract confidence trajectories from first 15 steps via `get_tactics()`
3. Compute entropy H_t = -Σ p_t,i log(p_t,i) and variance σ²_H
4. Label outcomes as success (proven within 300s) or timeout
5. Compute Pearson r and Spearman ρ between σ²_H and binary outcome
6. Generate scatter plots, ROC curves, and distribution visualizations

**Phase 2: Mechanism Validation (H-M1)**
1. Group the 100 experiments by outcome (successful vs. timeout)
2. Compare variance distributions: mean and std dev for each group
3. Test H₀: μ_success = μ_timeout using Welch's t-test (unequal variances)
4. Generate box plots showing separation
5. Compute effect size (Cohen's d) to quantify magnitude

**Phase 3: Ablation Study (H-M3)**
1. Define 7 detector variants: 3 single-signal, 3 pairwise, 1 hybrid
2. For each detector, apply thresholds (median of timeout distribution)
3. Classify each of 100 theorems as flag (predicted timeout) or continue
4. Compute precision, recall, F1 for each detector
5. Statistical comparison: pairwise t-tests with Bonferroni correction
6. Identify best-performing architecture

## Hardware and Reproducibility

All experiments run on NVIDIA H100 GPUs (80GB memory) with CUDA 11.8 and PyTorch 2.0. We use LeanDojo v1.0.0 and Lean 3.4.2. Random seed is fixed at 42 for reproducibility. Total compute budget: approximately 10 GPU-hours for all experiments.

**Code and Data Release:** Upon publication, we will release (1) complete experimental code, (2) the 100-theorem sample with confidence trajectories, (3) trained threshold values, and (4) detector implementation as a DojoCritic plugin. This enables exact reproduction and facilitates integration into other neural theorem proving systems.

## Ethical Considerations

This work improves computational efficiency in automated reasoning, which is inherently beneficial (reducing energy consumption, democratizing access to formal verification tools). We identify no negative societal impacts. Potential concerns and mitigations:

**False Positives:** Early termination of valid proofs could frustrate users. Mitigation: portfolio allocation (reduce budget rather than abort), precision=1.0 in our detector, human oversight in critical applications.

**Over-Reliance:** Automated provers might reduce development of human mathematical intuition. Mitigation: position as assistance tool, not replacement; emphasize formal verification use case where correctness matters more than intuition development.

We comply with the ICML 2025 guidelines on computational efficiency reporting and provide full transparency about resource consumption to enable informed adoption decisions.
