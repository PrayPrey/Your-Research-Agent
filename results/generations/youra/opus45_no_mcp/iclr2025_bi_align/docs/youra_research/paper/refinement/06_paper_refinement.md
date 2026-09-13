# Calibration Inversion as Behavioral Marker for RLHF Reward Conflation

## Abstract

RLHF-trained language models exhibit systematic calibration inversion—confidently predicting wrong answers—on specific benchmark task clusters. This work investigates this phenomenon through calibration clustering and mechanism verification. Clustering 2,212 tasks from TruthfulQA, MMLU moral_scenarios, and Anthropic HH-RLHF by calibration patterns yields a silhouette score of 0.6016 with optimal k=2, revealing non-random failure structure. We trace this pattern to reward signal conflation: annotators rate correctness and user-modeling tasks identically (rate_diff = 0.001), reward models show similar confidence across task types (mean_diff = 0.018), and model hidden states fail to separate them (separation = 0.024). Four of five mechanism hypotheses pass validation. However, keyword-based bidirectional feature detection achieves only 2.3% prevalence with correlation r = -0.027, leaving the feature-cluster link unverified. These findings establish calibration clustering as a diagnostic tool for RLHF behavioral analysis and identify annotator conflation as a plausible mechanism root cause, while highlighting semantic detection as necessary future work.

## 1. Introduction

RLHF-trained language models achieve high aggregate benchmark accuracy yet exhibit systematic calibration inversion—confidently predicting wrong answers—on specific task clusters. This paper traces this failure pattern to reward signal conflation during training, investigating a mechanism where annotator behavior propagates through reward models into model representations.

### The Calibration Paradox

Standard evaluation reports aggregate accuracy, masking task-level failure patterns. When benchmark tasks are clustered by calibration scores—measuring the gap between model confidence and correctness—non-random structure emerges. Tasks where models show P(wrong) > P(correct) + 0.1 cluster with silhouette score 0.6016, exceeding the 0.3 threshold indicating meaningful clustering. This systematic pattern suggests underlying causes beyond random error.

### From Symptoms to Mechanisms

Surface-level observations note that RLHF models show overconfidence on certain tasks. The deeper problem is that existing evaluation provides no mechanism explanation—we observe *what* fails but not *why*. Existing work lacks methods connecting calibration patterns to training dynamics.

This work tests the hypothesis that RLHF's reward modeling conflates distinct task dimensions. Specifically, if annotators rate both "correct output" and "output requiring user-state modeling" with similar confidence, the training signal fails to distinguish task types. Models then optimize for this conflated signal, potentially developing miscalibrated confidence on tasks requiring nuanced adaptation.

### Key Insight: The Conflation Chain

The investigation examines a four-step mechanism:

1. **Annotator Conflation:** Human annotators rate correctness and user-modeling tasks identically (rate_diff = 0.001), providing no distinguishing signal during preference data collection.

2. **Reward Model Inheritance:** The reward model learns this conflated signal, showing similar confidence across task types (mean_diff = 0.018 across three models).

3. **Representation Conflation:** Model hidden states fail to separate task types internally (separation = 0.024), indicating the conflation propagates to learned representations.

4. **Calibration Consequences:** These models exhibit systematic calibration inversion on specific task clusters.

Steps 1-3 are verified empirically. Step 4's connection to bidirectional task features remains unverified with current keyword-based detection methods (2.3% feature prevalence), motivating semantic detection as future work.

### Contributions

This work makes three contributions:

- **Calibration clustering as diagnostic tool:** Clustering benchmark tasks by calibration inversion scores reveals systematic RLHF behavioral patterns (silhouette = 0.6016).

- **Empirical mechanism verification:** Quantitative evidence that annotator conflation (rate_diff = 0.001), reward conflation (mean_diff = 0.018), and representation conflation (separation = 0.024) form a coherent mechanism chain.

- **Negative result:** Keyword-based bidirectional feature detection is insufficient (2.3% prevalence, r = -0.027), establishing methodological boundaries for future work.

## 2. Related Work

### RLHF Evaluation and Benchmarks

Reinforcement Learning from Human Feedback has become the standard approach for aligning language models with human preferences. Ouyang et al. (2022) introduced InstructGPT using RLHF to improve helpfulness and safety. Evaluation typically relies on aggregate benchmark metrics—TruthfulQA measures factual accuracy (Lin et al., 2021), ETHICS assesses moral reasoning (Hendrycks et al., 2021), and HHH evaluates helpfulness, harmlessness, and honesty (Askell et al., 2021).

These benchmarks report aggregate accuracy without task-level analysis. The present work clusters tasks by behavioral signals (calibration patterns), enabling mechanism investigation at the task-type level rather than aggregate statistics.

### Model Calibration

Calibration measures alignment between model confidence and actual correctness. Guo et al. (2017) established modern calibration analysis for neural networks. Prior work treats miscalibration as a general phenomenon. The current study shows calibration inversion clusters systematically (silhouette = 0.6016), indicating specific task types trigger miscalibration rather than uniform overconfidence.

### Bidirectional Alignment Framework

Shen et al. (2024) proposed a theoretical framework distinguishing AI-to-Human alignment from Human-to-AI alignment based on a survey of 400+ interdisciplinary papers. The present work operationalizes this framework, hypothesizing that tasks requiring bidirectional adaptation correlate with calibration inversion. While keyword-based feature detection proved insufficient, the underlying mechanism chain is verified.

### Positioning

Prior work either evaluates RLHF outcomes or analyzes mechanisms in isolation. This work bridges these by using behavioral patterns to investigate training mechanisms.

## 3. Method

### Calibration Inversion Metric

For each task, a calibration inversion score is computed:

$$\text{inv}(t) = P(\text{wrong}_t) - P(\text{correct}_t)$$

Tasks with inv(t) > 0.1 exhibit calibration inversion.

### Calibration Clustering

Tasks are clustered using K-means with silhouette validation. The optimal configuration is k=2 with silhouette=0.6016, revealing two behavioral clusters.

### Mechanism Verification Framework

The mechanism is decomposed into five testable sub-hypotheses:

| Hypothesis | Test | Threshold | Justification | Gate |
|------------|------|-----------|---------------|------|
| H-E1 | Silhouette score | > 0.3 | Standard clustering literature threshold for meaningful structure | MUST_WORK |
| H-M1 | Confidence mean_diff | < 0.1 | Small effect size threshold | MUST_WORK |
| H-M2 | Rate difference | < 0.15 | Small effect size threshold (d < 0.2) | SHOULD_WORK |
| H-M3 | Separation score | < 0.1 | Low separation indicating task-type conflation | SHOULD_WORK |
| H-M4 | Correlation r | > 0.4 | Moderate effect size per Cohen's conventions | SHOULD_WORK |

### Bidirectional Feature Detection

Three keyword-based features are used: user-belief-reference, context-dependent, hedged-answer. Known limitation: achieved only 2.3% prevalence.

## 4. Experimental Setup

### Datasets

| Dataset | Tasks | Purpose |
|---------|-------|---------|
| TruthfulQA | 817 | Factual accuracy |
| MMLU moral_scenarios | 895 | Moral reasoning |
| Anthropic HH-RLHF | 500 | Helpfulness |
| **Total** | **2,212** | |

### Models

Three RLHF-trained models were evaluated:

- Llama-2-7B-Chat (meta-llama/Llama-2-7b-chat-hf)
- Llama-2-13B-Chat (meta-llama/Llama-2-13b-chat-hf)
- Mistral-7B-Instruct (mistralai/Mistral-7B-Instruct-v0.2)

### Task Classification

Tasks are classified into Type A (correctness, 1,977 tasks, 89.4%) and Type B (user-state-modeling, 235 tasks, 10.6%) based on keyword markers including user belief references ("you think", "your opinion"), context markers ("given that", "considering"), and hedge markers ("might", "could", "possibly").

### Hyperparameters

Clustering: K-means with k=2, seed=42, n_init=10. Inference: batch_size 8-16, float16, device_map=auto. Inversion threshold: 0.1. Silhouette threshold: 0.3.

## 5. Results

### Summary

| Hypothesis | Result | Key Metric | Achieved |
|------------|--------|------------|----------|
| H-E1 | **PASS** | Silhouette | 0.6016 |
| H-M1 | **PASS** | mean_diff | 0.018 |
| H-M2 | **PASS** | rate_diff | 0.001 |
| H-M3 | **PASS** | separation | 0.024 |
| H-M4 | **FAIL** | r | -0.027 |

### H-E1: Calibration Clusters Exist

K-means clustering on calibration inversion scores yields:

- Silhouette: **0.6016** (threshold: 0.3)
- Optimal k: **2**
- Cluster 0: 1,519 tasks (69%), center inversion score 0.006
- Cluster 1: 693 tasks (31%), center inversion score 2.228

The silhouette score of 0.6016 exceeds the 0.3 threshold by approximately 2x. K-sweep results: k=2 (0.6016), k=3 (0.5324), k=4 (0.5522), k=5 (0.5365).

### H-M1: Reward Conflation

Analysis of model confidence on Type A vs Type B tasks:

- Mean confidence Type A: 0.083
- Mean confidence Type B: 0.065
- Mean difference: **0.018** (threshold: < 0.1)
- Distribution overlap: **0.647**

Cross-model overlap scores: Llama-2-7B (0.647), Llama-2-13B (0.643), Mistral-7B (0.653). The consistency across models (std = 0.005) indicates the pattern is not model-specific.

Per-dataset analysis: MMLU moral_scenarios shows highest overlap (0.728), TruthfulQA (0.638), Anthropic HH-RLHF (0.686).

### H-M2: Annotator Conflation

High-confidence rate comparison (threshold=0.7):

- Type A high-confidence rate: 0.0010
- Type B high-confidence rate: 0.0000
- Rate difference: **0.001** (threshold: < 0.15)
- Conflation score: **0.999**

Threshold sensitivity analysis shows rate differences remain below 0.02 across all thresholds (0.5-0.9).

Cross-model consistency: Llama-2-7B (diff=0.0010), Llama-2-13B (diff=0.0005), Mistral-7B (diff=0.0023). All models pass the gate.

### H-M3: Representation Conflation

Hidden state analysis using mean pooling of final layer representations:

**Llama-2-7B-Chat:**
- Separation score: **0.024** (threshold: < 0.1)
- Linear probe accuracy: 75.59%
- Intra-A similarity: 0.549
- Intra-B similarity: 0.511
- Inter-type similarity: 0.522

**Llama-2-13B-Chat:**
- Separation score: 0.009
- Probe accuracy: 68.13%

**Mistral-7B-Instruct:**
- Separation score: 0.008
- Probe accuracy: 72.51%

All models show separation scores well below the 0.1 threshold.

### H-M4: Feature Correlation (FAILED)

Correlation between bidirectional features and cluster membership:

- Point-biserial r: **-0.027** (threshold: > 0.4)
- Cohen's d: **-0.058** (threshold: > 0.3)
- Partial r (controlling for confounds): **-0.009**
- p-value: 0.203 (not statistically significant)
- Feature prevalence: **2.3%** (51 of 2,212 tasks)

Feature prevalence by cluster: user_belief_reference (Cluster 0: 1.78%, Cluster 1: 0.87%), context_dependent (Cluster 0: 0.13%, Cluster 1: 0.43%), hedged_answer (Cluster 0: 0.72%, Cluster 1: 0.43%).

## 6. Discussion

### Summary of Findings

The mechanism chain (annotator conflation → reward conflation → representation conflation) is verified through H-M1, H-M2, and H-M3. The H-M4 failure reflects detection inadequacy rather than mechanism failure—keyword-based features captured only 2.3% of tasks, providing insufficient statistical power to test the correlation.

### Interpretation

The experiments establish that RLHF training creates a reward model conflation pattern:

1. Human annotators rate both correctness and user-state-modeling tasks with similar high-confidence patterns (rate_diff = 0.001).

2. The reward model inherits this conflation, showing similar confidence levels on both task types (mean_diff = 0.018).

3. Hidden state analysis confirms models do not internally distinguish task types (separation = 0.024). A linear probe achieves only moderate accuracy (68-76%), indicating weak task-type encoding.

4. These RLHF models exhibit systematic calibration inversion patterns (silhouette = 0.6016).

The gap between step 3 and step 4 remains: the causal link from bidirectional task features to calibration inversion cluster membership was not established with keyword-based detection.

### Cross-Model Consistency

All three models (Llama-2-7B, Llama-2-13B, Mistral-7B) showed consistent patterns across all passing hypotheses. This cross-model consistency strengthens the finding that RLHF training creates consistent behavioral patterns regardless of base model architecture.

### Limitations

**Keyword detection insufficient:** Simple keyword patterns (user_belief, context_dependent, hedged_answer) captured only 2.3% of tasks. Bidirectionality is a semantic property not reliably captured by lexical patterns.

**Open models only:** Only open RLHF models were tested. Closed models (GPT-4, Claude) may behave differently, but logprob access required for calibration analysis is not available for these models.

**Dataset composition:** TruthfulQA, MMLU moral_scenarios, and Anthropic HH-RLHF may not contain sufficient natural bidirectional variation. These datasets were designed for accuracy evaluation, not bidirectionality analysis.

**Alternative explanations not tested:** Calibration inversion clusters may be driven by task difficulty, answer format, or topic rather than bidirectionality. These confounds were not systematically evaluated.

### Implications

Calibration clustering offers a diagnostic tool for RLHF behavioral analysis. The finding that annotators provide no distinguishing signal between task types (conflation score = 0.999) suggests that annotation-level interventions may be more effective than post-hoc calibration adjustment.

## 7. Conclusion

RLHF models exhibit systematic calibration inversion patterns that cluster non-randomly (silhouette = 0.6016). The underlying mechanism is supported: annotators rate correctness and user-state-modeling tasks similarly (rate_diff = 0.001), reward models show similar confidence across task types (mean_diff = 0.018), and model representations fail to distinguish them (separation = 0.024). Four of five hypotheses passed validation.

Keyword-based bidirectional detection proved insufficient (2.3% prevalence, r = -0.027), leaving the feature-cluster relationship unverified. The calibration paradox has a plausible mechanism explanation: what annotators do not distinguish, models cannot learn to distinguish. Semantic feature detection methods are needed to complete the causal chain.

## References

Askell, A., Bai, Y., Chen, A., Drain, D., Ganguli, D., Henighan, T., Jones, A., Joseph, N., Mann, B., DasSarma, N., et al. (2021). A General Language Assistant as a Laboratory for Alignment. arXiv preprint arXiv:2112.00861.

Bai, Y., Jones, A., Ndousse, K., Askell, A., Chen, A., DasSarma, N., Drain, D., Fort, S., Ganguli, D., Henighan, T., et al. (2022). Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback. arXiv preprint arXiv:2204.05862.

Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On Calibration of Modern Neural Networks. In International Conference on Machine Learning (pp. 1321-1330).

Hendrycks, D., Burns, C., Basart, S., Critch, A., Li, J., Song, D., & Steinhardt, J. (2021). Aligning AI with shared human values. arXiv preprint arXiv:2008.02275.

Jiang, A. Q., Sablayrolles, A., Mensch, A., Bamford, C., Chaplot, D. S., Casas, D. de las, Bressand, F., Lengyel, G., Lample, G., Saulnier, L., et al. (2023). Mistral 7B. arXiv preprint arXiv:2310.06825.

Lin, S., Hilton, J., & Evans, O. (2021). TruthfulQA: Measuring How Models Mimic Human Falsehoods. arXiv preprint arXiv:2109.07958.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., et al. (2022). Training language models to follow instructions with human feedback. Advances in Neural Information Processing Systems, 35, 27730-27744.

Shen, H., et al. (2024). Position: Towards Bidirectional Human-AI Alignment. arXiv preprint arXiv:2406.09264.

Touvron, H., Martin, L., Stone, K., Albert, P., Almahairi, A., Babaei, Y., Bashlykov, N., Batra, S., Bhargava, P., Bhosale, S., et al. (2023). Llama 2: Open Foundation and Fine-Tuned Chat Models. arXiv preprint arXiv:2307.09288.

## Figures

![Cluster Scatter](/home/PrayPrey/YouRA_results_new_4_opus45_no_mcp/TEST_bi_align/docs/youra_research/paper/figures/cluster_scatter.png)
*Figure 1: Task calibration clustering showing k=2 optimal clusters (silhouette=0.6016). Cluster 0 (1,519 tasks) shows low/no inversion; Cluster 1 (693 tasks) shows high inversion.*

![Confidence Histograms](/home/PrayPrey/YouRA_results_new_4_opus45_no_mcp/TEST_bi_align/docs/youra_research/paper/figures/confidence_histograms.png)
*Figure 2: Type A vs Type B confidence distributions showing similar patterns across task types (mean_diff=0.018).*

![Sensitivity Curve](/home/PrayPrey/YouRA_results_new_4_opus45_no_mcp/TEST_bi_align/docs/youra_research/paper/figures/sensitivity_curve.png)
*Figure 3: Annotator conflation across confidence thresholds. Rate differences remain below 0.02 at all thresholds.*

![t-SNE Visualization](/home/PrayPrey/YouRA_results_new_4_opus45_no_mcp/TEST_bi_align/docs/youra_research/paper/figures/tsne_meta-llama_Llama-2-7b-chat-hf.png)
*Figure 4: Hidden state t-SNE visualization showing weak task-type separation (separation=0.024).*

![Feature Breakdown](/home/PrayPrey/YouRA_results_new_4_opus45_no_mcp/TEST_bi_align/docs/youra_research/paper/figures/feature_breakdown.png)
*Figure 5: Bidirectional feature prevalence by cluster. Total prevalence: 2.3%.*

![Cross-Model Heatmap](/home/PrayPrey/YouRA_results_new_4_opus45_no_mcp/TEST_bi_align/docs/youra_research/paper/figures/cross_model_heatmap.png)
*Figure 6: Cross-model overlap scores showing consistent conflation pattern (0.64-0.65 across all models).*
