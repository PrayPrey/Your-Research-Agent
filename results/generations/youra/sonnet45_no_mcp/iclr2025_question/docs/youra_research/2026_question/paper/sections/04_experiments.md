# Experimental Setup

We design three experiments to test our mechanistic hypotheses about uncertainty estimation. Each experiment addresses a specific question with clear success criteria.

## Experiment 1: Semantic Clustering Contribution (h-e1)

**Research Question:** Does semantic clustering add measurable value beyond multiple sampling for uncertainty estimation?

**Hypothesis:** Semantic entropy (K=10 with clustering) outperforms ensemble baseline (K=10 without clustering) by ≥0.07 AUROC on knowledge-gap errors.

**Experimental Design:** This ablation study isolates the clustering contribution by matching computational budgets. Both methods use exactly K=10 samples from Mistral-7B at temperature 0.7 on the same 100 NaturalQuestions unanswerable questions. The only difference is whether we cluster semantically equivalent answers before computing entropy.

**Rationale:** Previous work has not isolated whether semantic entropy's advantage comes from the clustering mechanism or simply from using more samples. This controlled comparison answers that question definitively.

**Procedure:**
1. Sample K=10 answers for each of 100 NaturalQuestions unanswerable questions
2. Apply semantic entropy: embed answers, cluster with threshold 0.5, compute entropy over clusters
3. Apply ensemble baseline: identify most common answer by exact string match, compute disagreement rate
4. Compute AUROC for both methods on error detection
5. Test whether AUROC difference ≥ 0.07

**Success Criteria:**
- Primary: AUROC_semantic - AUROC_ensemble ≥ 0.07
- Secondary: AUROC_semantic ≥ 0.70 (absolute performance threshold)
- Gate: MUST_WORK (core contribution requires validation)

**Expected Outcome:** If semantic clustering adds value, we should observe measurably better discrimination from grouping equivalent answers. If clustering does not add value, both methods should perform similarly since they use the same samples.

## Experiment 2: Method Independence Analysis (h-m1)

**Research Question:** Do uncertainty methods capture orthogonal versus redundant signals?

**Hypothesis:** Pairwise correlations between uncertainty methods are below 0.7, indicating distinct uncertainty dimensions.

**Experimental Design:** We apply four methods (semantic entropy, self-consistency, token variance, verbalized confidence) to identical samples and measure correlation. Using the same samples eliminates variance from different model runs.

**Rationale:** If methods capture orthogonal dimensions (semantic diversity, sampling agreement, distributional sharpness, introspection), correlations should be low. High correlations would suggest methods measure the same underlying signal with different computations.

**Procedure:**
1. Generate K=5 answers for each of 100 NaturalQuestions questions
2. Apply all four uncertainty methods to the same samples:
   - Semantic entropy: cluster and compute entropy
   - Self-consistency: compute majority vote agreement
   - Token variance: compute variance of token probabilities
   - Verbalized confidence: extract self-reported percentage
3. Compute pairwise Pearson correlations across all method pairs
4. Identify maximum correlation and compare to 0.7 threshold

**Success Criteria:**
- Primary: Maximum pairwise correlation < 0.7
- Secondary: At least three method pairs show |correlation| < 0.3 (strong independence)
- Gate: SHOULD_WORK (supporting evidence for orthogonality claim)

**Expected Outcome:** Low correlations would validate that methods measure distinct aspects of uncertainty and justify multi-method approaches. High correlations would suggest redundancy, indicating the field should consolidate rather than proliferate methods.

## Experiment 3: Error Type Signatures (h-m2)

**Research Question:** Do different error types exhibit distinct uncertainty signatures?

**Hypothesis:** Knowledge gaps show higher semantic diversity than confident misconceptions.

**Experimental Design:** We compare semantic diversity and sampling agreement distributions across two datasets: NaturalQuestions (representing knowledge gaps) and TruthfulQA (representing confident misconceptions).

**Rationale:** If error types have characteristic signatures, we should observe systematic differences in uncertainty patterns. Knowledge gaps should produce diverse wrong answers (high diversity, low agreement), while confident misconceptions should produce consistent wrong answers (low diversity, high agreement).

**Procedure:**
1. Sample K=5 answers for 100 questions each from NaturalQuestions and TruthfulQA
2. Compute semantic diversity (entropy over clusters) for both datasets
3. Compute sampling agreement (majority vote fraction) for both datasets
4. Test statistical significance of diversity difference using t-test (α = 0.05)
5. Verify direction: NaturalQuestions diversity > TruthfulQA diversity

**Success Criteria:**
- Primary: Diversity difference statistically significant (p < 0.05) in predicted direction
- Secondary: Effect size ≥ 0.5 standard deviations
- Gate: SHOULD_WORK (supporting evidence for error-type characterization)

**Expected Outcome:** If error types have distinct signatures, dataset-level analysis should reveal systematic patterns. If signatures are instance-specific rather than dataset-specific, we expect weak or null results, pointing toward instance-level features as the next research direction.

## Implementation Details

All experiments use:
- **Model:** Mistral-7B-v0.1 (7B parameters, decoder-only transformer)
- **Hardware:** Single GPU (CUDA device 0)
- **Embedding model:** sentence-transformers/all-MiniLM-L6-v2 (for semantic entropy)
- **Clustering:** Agglomerative with cosine distance threshold 0.5
- **Temperature:** 0.7 for sampling methods
- **Random seed:** 42 for reproducibility

**Data Sources:**
- NaturalQuestions: HuggingFace datasets library (natural_questions validation split, unanswerable subset)
- TruthfulQA: HuggingFace datasets library (truthful_qa generation format)

**Validation Protocol:**
Each experiment follows the three-stage protocol (data collection, method application, analysis) with pre-registered success criteria and gate conditions from the verification plan (Phase 2B). Results are compared against thresholds before gate evaluation.

## Statistical Power

With 100 samples per dataset, we have 80% power to detect:
- AUROC difference of 0.07 at α = 0.05 (Experiment 1)
- Correlation difference from 0.7 of magnitude 0.15 at α = 0.05 (Experiment 2)
- Diversity difference of 0.3 standard deviations at α = 0.05 (Experiment 3)

These effect sizes are based on pilot data and represent meaningful practical differences for the hypotheses under test.
