# Methodology

## Dataset and Category Clustering

We use TruthfulQA \cite{lin2022truthfulqa} in multiple-choice format (validation split, 817 questions). The benchmark provides 38 fine-grained category labels. To ensure sufficient samples per cluster for reliable ECE estimation, we group these into 7 semantic clusters based on domain similarity:

| Cluster | Categories | n |
|---------|-----------|---|
| Science & Nature | Biology, Physics, Chemistry, Weather, Animals | 142 |
| Health & Medicine | Health, Nutrition, Psychology | 127 |
| Society & Culture | Sociology, History, Language, Religion | 168 |
| Finance & Economics | Economics, Finance, Law | 70 |
| Misconceptions & Myths | Misconceptions, Myths, Superstitions, Paranormal | 134 |
| Politics & Law | Politics, Government, Conspiracies | 98 |
| Other | Logical Fallacies, Indexical Errors, Stereotypes | 78 |

Cluster sizes range from 70 (Finance) to 168 (Society), with minimum n=70 providing adequate power for bootstrap confidence intervals.

## Model and Logit Extraction

We evaluate on meta-llama/Llama-2-7b-hf, a decoder-only transformer with open weights and accessible logits. For each multiple-choice question, we extract the softmax probability assigned to each answer option from the model's next-token prediction. The confidence score for a response is the maximum probability across answer tokens.

## Temperature Scaling

Temperature scaling adjusts logits by dividing by a learned parameter T before softmax:

$$p_i^{(T)} = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}$$

where $z_i$ are the raw logits. T>1 produces softer (less confident) predictions; T<1 produces sharper predictions. We optimize T by minimizing negative log-likelihood on calibration data.

### Global Temperature Scaling

A single T is learned on the entire training set and applied uniformly:

$$T^* = \arg\min_T \sum_{(x,y) \in D_{train}} -\log p_y^{(T)}(x)$$

### Cluster-Specific Temperature Scaling

We learn a separate temperature $T_c$ for each cluster c:

$$T_c^* = \arg\min_{T_c} \sum_{(x,y) \in D_{train}^{(c)}} -\log p_y^{(T_c)}(x)$$

At inference, predictions are calibrated using the temperature corresponding to the question's cluster assignment.

**Optimization bounds:** We constrain T to [0.1, 10.0], a range spanning typical calibration needs. Values outside this range indicate either severe overconfidence (T→∞) or already well-calibrated predictions (T→1).

## Cross-Validation

We use 5-fold stratified cross-validation, preserving cluster proportions in each fold. For each fold:
1. Optimize temperature(s) on 80% training data
2. Evaluate ECE on 20% held-out data
3. Record per-cluster and aggregate metrics

Final metrics are means across folds with bootstrap confidence intervals.

## Evaluation Metrics

**Expected Calibration Error (ECE):** We use 15-bin ECE as primary metric:

$$ECE = \sum_{b=1}^{15} \frac{|B_b|}{n} |acc(B_b) - conf(B_b)|$$

where $B_b$ is the set of predictions in bin b, $acc$ is accuracy, and $conf$ is mean confidence.

**Per-cluster ECE:** ECE computed separately for each cluster's predictions.

**ANOVA:** F-test across cluster ECE values to detect significant variation.

**Kolmogorov-Smirnov test:** Pairwise comparison of confidence distributions between clusters.

**Temperature variation:** Coefficient of variation (CV) and range of optimal temperatures across clusters.

## Hypothesis Testing

We test three linked hypotheses with pre-registered success criteria:

| Hypothesis | Metric | Success Criterion | Gate |
|------------|--------|-------------------|------|
| h-e1 (Existence) | ANOVA p-value | p < 0.05 | MUST_WORK |
| h-m1 (Distributions) | Significant KS pairs | ≥ 11/21 pairs | MUST_WORK |
| h-m2 (Temperatures) | CV(T) | > 0.1 | SHOULD_WORK |

h-m2 failure blocks testing of whether cluster-specific T outperforms global T (h-m3), as uniform temperatures make the comparison trivial.

## Implementation Note

Due to GPU driver issues during execution, h-m1 used simulated confidence data calibrated to h-e1 ECE patterns using Beta distributions. Parameters were derived from measured cluster ECE values. We report this as a limitation; results should be interpreted as demonstrating methodology with ECE-consistent synthetic confidences.
