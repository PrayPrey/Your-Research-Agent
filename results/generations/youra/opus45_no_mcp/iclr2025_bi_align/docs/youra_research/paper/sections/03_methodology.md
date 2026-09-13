# Methodology

We design a two-phase approach: (1) calibration clustering to identify systematic failure patterns, and (2) mechanism verification to explain why these patterns exist.

## Calibration Inversion Metric

For each task, we compute calibration inversion score from model logprobs:

$$\text{inv}(t) = P(\text{wrong}_t) - P(\text{correct}_t)$$

where $P(\text{wrong}_t)$ is the model's confidence on incorrect answers and $P(\text{correct}_t)$ is confidence on the correct answer. Tasks with inv(t) > 0.1 exhibit calibration inversion—the model is more confident in wrong answers.

We extract logprobs from open RLHF models (Llama-2-7B-Chat, Llama-2-13B-Chat, Mistral-7B-Instruct) using standard inference. Scores are averaged across models for robustness.

## Calibration Clustering

We cluster tasks by calibration inversion patterns using K-means:

1. **Feature extraction:** Each task is represented by calibration scores across models
2. **Clustering:** K-means with k ∈ {2,3,4,5}, selected by silhouette score
3. **Validation:** Silhouette > 0.3 indicates meaningful clustering

The optimal k=2 with silhouette=0.6016 reveals two behavioral clusters: high-inversion (n=693) and low-inversion (n=1519) tasks.

## Mechanism Verification Framework

We decompose the hypothesized reward conflation mechanism into four testable sub-hypotheses:

### H-E1: Existence of Systematic Patterns

**Test:** Do calibration inversion tasks cluster non-randomly?

**Metric:** Silhouette score on K-means clustering

**Threshold:** Silhouette > 0.3

**Gate:** MUST_WORK (foundation for mechanism investigation)

### H-M1: Reward Model Conflation

**Test:** Do models show similar confidence on Type A (correctness) vs Type B (user-modeling) tasks?

**Metric:** Distribution overlap using kernel density estimation; mean confidence difference

**Threshold:** Overlap > 0.7 OR mean_diff < 0.1

**Gate:** MUST_WORK (mechanism step 1)

### H-M2: Annotator Conflation

**Test:** Do annotators rate both task types with similar confidence?

**Metric:** Rate difference between task types at high-confidence threshold

**Threshold:** rate_diff < 0.15

**Gate:** SHOULD_WORK (mechanism step 2)

### H-M3: Representation Conflation

**Test:** Do model hidden states separate task types?

**Metric:** Centroid separation score; linear probe accuracy

**Threshold:** Separation < 0.1 (low separation indicates conflation); probe accuracy in 60-80% range (weak but above chance)

**Gate:** SHOULD_WORK (mechanism step 3)

### H-M4: Feature-Cluster Correlation

**Test:** Do bidirectional task features correlate with calibration inversion clusters?

**Metric:** Point-biserial correlation; Cohen's d; partial correlation after confound control

**Threshold:** r > 0.4; d > 0.3; partial_r > 0.3

**Gate:** SHOULD_WORK (mechanism step 4)

## Bidirectional Feature Detection

We operationalize bidirectionality using three keyword-based features:

1. **User-belief-reference:** Task mentions user beliefs, knowledge, or perspective
2. **Context-dependent:** Correct answer depends on context not stated in task
3. **Hedged-answer:** Correct answer requires hedging or uncertainty expression

Tasks with 1+ features are classified as Type B (bidirectional); others as Type A.

**Known limitation:** Keyword detection achieved only 2.3% feature prevalence, insufficient for correlation analysis. Semantic or embedding-based detection is needed for future work.

## Task Classification Pipeline

For each task in combined benchmark (TruthfulQA + ETHICS + HH-RLHF):

1. Extract logprobs from three models
2. Compute calibration inversion score
3. Classify task type (A/B) using keyword features
4. Cluster by calibration pattern
5. Test mechanism hypotheses

## Confound Control

We control for potential confounds:

- **Task length:** Binned into quartiles
- **Topic category:** Benchmark-provided labels
- **Format type:** Multiple choice vs open-ended
- **Estimated difficulty:** Mean accuracy across models

Partial correlation analysis removes confound effects when testing H-M4.

## Statistical Approach

- Correlations: Pearson (continuous) or point-biserial (categorical-continuous)
- Effect sizes: Cohen's d with 95% confidence intervals
- Clustering validation: Silhouette score, cluster stability across random seeds
- Cross-model consistency: Results reported for each model separately and aggregated
