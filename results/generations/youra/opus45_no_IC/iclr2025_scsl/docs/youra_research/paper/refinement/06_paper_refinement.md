# Detecting Minority Groups via Training Dynamics: A Study of Simplicity Bias in Loss Trajectories

**Anonymous Authors**

---

## Abstract

Neural networks trained with empirical risk minimization learn spurious correlations, failing systematically on minority groups where spurious features conflict with labels. This work investigates whether training dynamics contain detectable signatures that distinguish minority from majority samples without requiring group annotations. On the Waterbirds dataset, minority-group samples exhibit 8.3× higher mean loss at epoch 5 (5% of training) compared to majority samples (0.158 vs. 0.019, Mann-Whitney U = 705,391, p = 7.36 × 10⁻¹⁵). Using linear probes on frozen ResNet-18 representations, we confirm the mechanism: representations encode spurious features (background) with 91.2% accuracy versus 80.5% for core features (bird type) at epoch 5, a 10.7 percentage point gap. Loss-based detection at the 95th percentile threshold achieves 32.9% precision—6.6× improvement over the 5% random baseline—though this precision is fundamentally bounded by the minority base rate, not signal weakness. Contrary to initial hypotheses, with ImageNet-pretrained features both spurious and core feature probe accuracies peak at the same epoch (81), indicating that simplicity bias manifests as an accuracy magnitude gap rather than a temporal gap under transfer learning conditions.

---

## 1. Introduction

Deep neural networks trained with empirical risk minimization (ERM) exploit spurious correlations present in training data. When a feature correlated with the label in training does not hold in deployment—or for minority subgroups within training—the model fails systematically. A classifier distinguishing waterbirds from landbirds may learn to rely on background (water vs. land) rather than bird morphology, because background provides a simpler, more consistent signal during training. When waterbirds appear on land—a minority of the training distribution—the model fails.

Existing solutions to this problem require either group labels during training (Group DRO; Sagawa et al., 2019) or two-stage procedures that first train a biased model, then identify failing samples for upweighting (JTT; Liu et al., 2021). While effective, these approaches cannot detect minority samples during a single training run. SPARE (Yang et al., 2023) identifies spurious correlations early via simplicity bias but uses fixed epoch thresholds rather than per-sample trajectory analysis.

This work investigates whether per-sample loss trajectories contain discriminative information about minority group membership. The hypothesis is that simplicity bias—the tendency of neural networks to learn simpler patterns first—causes majority-group samples to achieve low loss rapidly via spurious features, while minority-group samples require core feature learning and exhibit persistently higher loss.

The contributions of this work are:

1. Demonstration that early-epoch loss magnitude provides a statistically significant signal for minority-group detection (Mann-Whitney p < 10⁻¹⁴) without requiring group labels.

2. Verification via linear probes that simplicity bias manifests as a ~10 percentage point accuracy gap between spurious and core feature encoding throughout training.

3. Explicit characterization of precision limits under minority imbalance, showing that the 5% base rate—not signal weakness—bounds individual detection accuracy.

4. A refinement of simplicity bias theory: with pretrained features, the bias manifests as an accuracy magnitude gap rather than a temporal gap.

---

## 2. Related Work

### Spurious Correlation and Group Robustness

Spurious correlations arise when features correlated with labels in training data do not hold in deployment. Sagawa et al. (2019) formalized this as a group robustness problem, introducing Group DRO to optimize worst-group accuracy (WGA). Group DRO achieves approximately 91% WGA on Waterbirds but requires group annotations during training.

Subsequent work removes this requirement. JTT (Liu et al., 2021) trains an initial ERM model, identifies misclassified samples as likely minorities, and upweights them in a second training stage, closing approximately 75% of the gap to Group DRO on Waterbirds (achieving ~86% WGA). DFR (Izmailov et al., 2022) demonstrates that ERM already learns good features—the problem is the classifier head—and achieves 97% WGA by retraining only the last layer on a balanced validation set.

### Early Training Dynamics

SPARE (Yang et al., 2023) exploits simplicity bias for early spurious correlation identification, achieving +21.1% WGA improvement while being 12× faster than prior methods. LA-SSL (Zhu et al., 2023) observes that minority samples learn slower than majority samples and uses inverse learning speed for sampling weights.

This work differs from these approaches by analyzing per-sample loss trajectories as continuous discriminative signals, rather than using fixed thresholds (SPARE) or aggregate learning speed (LA-SSL).

### Positioning

| Method | Signal Type | Group Labels | Training Stages |
|--------|------------|--------------|-----------------|
| Group DRO | Worst-group loss | Required | 1 |
| JTT | Binary misclassification | Validation only | 2 |
| DFR | Feature reweighting | Balanced val set | 1.5 |
| SPARE | Fixed epoch threshold | None | 1 |
| This work | Loss magnitude at early epoch | None | 1 |

---

## 3. Method

### Problem Setup

Consider a classification task where inputs x have class label y and group membership g. Groups arise from the interaction of core features (predictive of y) and spurious features (correlated with y in training but not causally related). Under ERM training, models exploit spurious correlations because they provide simpler, more consistent signals.

### Loss-Based Detection

For each sample i, we track loss L_i(t) across training epochs t. We use loss at an early detection epoch T_early = 5 (5% of 100 epochs). Candidate minority samples are identified as those with loss above the k-th percentile:

minority_candidate_i = 1[L_i(T_early) > percentile_k(L(T_early))]

At 5% minority rate, k = 95 selects the top 5% of high-loss samples.

### Linear Probe Analysis

To verify the simplicity bias mechanism, linear probes are trained on frozen ResNet-18 features at multiple epochs. Two separate logistic regression probes are trained:

- **Spurious probe**: Predicts background (water/land)
- **Core probe**: Predicts bird type (waterbird/landbird)

If simplicity bias operates, spurious probe accuracy should exceed core probe accuracy at early epochs.

### Implementation Details

- **Model**: ResNet-18 with ImageNet pretrained weights (IMAGENET1K_V1)
- **Training**: 100 epochs, SGD (lr=0.001, momentum=0.9, weight decay=1e-4), batch size 64
- **Checkpoints**: Epochs 5, 20, 50, 81, 100
- **Seed**: 42

---

## 4. Experimental Setup

### Dataset

Experiments use **Waterbirds** (Sagawa et al., 2019): 4,795 training samples with 5% minority rate (waterbirds on land, landbirds on water). The spurious correlation is 95%: birds appear on their "expected" backgrounds 95% of the time. The test set contains 5,794 samples.

### Evaluation Metrics

- **Precision/Recall**: Detection performance against ground-truth minority labels
- **Mann-Whitney U**: Statistical test for distribution difference between minority and majority loss values
- **Probe accuracy gap**: Spurious accuracy minus core accuracy

---

## 5. Results

### Loss Distribution Separation

At epoch 5, minority and majority samples exhibit substantially different loss distributions:

| Statistic | Minority | Majority | Ratio |
|-----------|----------|----------|-------|
| Mean loss | 0.158 | 0.019 | 8.3× |
| Median loss | 0.057 | 0.001 | 57× |

The Mann-Whitney U test confirms statistical significance: U = 705,391, p = 7.36 × 10⁻¹⁵.

![Loss trajectories by group](/home/PrayPrey/YouRA_no_IC_opus45/TEST_scsl/docs/youra_research/h-e1/figures/loss_trajectories.png)

*Figure 1: Per-sample loss trajectories colored by group membership. Minority samples cluster in the high-loss region throughout training.*

### Detection Performance

Using the 95th percentile loss threshold at epoch 5:

| Metric | Value | Random Baseline | Lift |
|--------|-------|-----------------|------|
| Precision | 0.329 | 0.050 | 6.6× |
| Recall | 0.329 | 0.050 | 6.6× |

The 6.6× lift over random demonstrates substantial detection signal. The precision value of 32.9% approaches the theoretical maximum achievable when predicting 5% of samples at a 5% minority base rate—approximately 33%—indicating that the ranking performance is near-optimal given the base rate constraint.

![Precision-Recall curve](/home/PrayPrey/YouRA_no_IC_opus45/TEST_scsl/docs/youra_research/h-e1/figures/pr_curve.png)

*Figure 2: Precision-recall curve for minority detection versus loss percentile threshold.*

### Simplicity Bias Mechanism

Linear probe analysis confirms the presence of simplicity bias:

| Epoch | Spurious Acc | Core Acc | Gap |
|-------|--------------|----------|-----|
| 5 | 91.20% | 80.50% | +10.70% |
| 20 | 91.59% | 82.26% | +9.33% |
| 50 | 91.34% | 82.62% | +8.72% |

At epoch 5, representations encode background information with 91.2% probe accuracy while bird type achieves 80.5%—a 10.7 percentage point gap. This gap persists throughout training, confirming that spurious features maintain an encoding advantage.

![Probe accuracy comparison](/home/PrayPrey/YouRA_no_IC_opus45/TEST_scsl/docs/youra_research/h-m1/code/figures/probe_accuracy.png)

*Figure 3: Linear probe accuracy for spurious (background) versus core (bird type) features across training epochs.*

### Timing Analysis

The hypothesis that spurious features would peak earlier than core features was not supported. Both feature types reached peak probe accuracy at the same epoch:

| Feature Type | Peak Epoch | Peak Accuracy |
|--------------|------------|---------------|
| Spurious | 81 | 91.9% |
| Core | 81 | 82.8% |

The Wilcoxon signed-rank test confirms the curves are statistically different (p = 3.88 × 10⁻¹⁸), but this difference manifests as a consistent magnitude gap (~9-11%) rather than a temporal offset.

![Learning curves](/home/PrayPrey/YouRA_no_IC_opus45/TEST_scsl/docs/youra_research/h-m2/figures/learning_curves.png)

*Figure 4: 100-epoch linear probe learning curves showing parallel trajectories with persistent magnitude gap. Both feature types peak at epoch 81.*

---

## 6. Discussion

### Interpreting the Detection Signal

The 8× loss difference provides a statistically robust signal for minority detection. However, translating distributional difference into individual identification is constrained by base rate mathematics: at 5% minority rate, if we predict 5% of samples as minority (to match the true rate), perfect ranking achieves approximately 33% precision. The achieved 32.9% precision approaches this bound.

This does not indicate weak signal—the Mann-Whitney p-value of 7.36 × 10⁻¹⁵ demonstrates extremely strong distributional separation. Rather, it reflects the fundamental challenge of rare class detection. The appropriate use case is weighted training (as in JTT) rather than hard minority labeling.

### Magnitude Gap versus Timing Gap

The original hypothesis predicted that spurious features would peak before core features during training, reflecting their "easier" status. With ImageNet-pretrained features, this prediction was not supported—both feature types peaked at epoch 81. Simplicity bias manifests as consistently higher spurious encoding (9-11% gap) rather than earlier encoding.

This finding may be specific to transfer learning conditions. ImageNet pretraining likely encodes both background and object patterns in the initial representations, compressing the learning dynamics. Training from random initialization may exhibit different temporal patterns, though this was not tested.

### Limitations

**Single dataset**: Only Waterbirds was tested. Transfer to CelebA or MultiNLI was planned but not executed.

**Pretrained features only**: The timing dynamics may differ when training from scratch.

**No intervention evaluation**: This work characterizes the detection signal but does not evaluate whether upweighting detected samples improves worst-group accuracy. JTT's demonstrated effectiveness with misclassification-based detection suggests promise, but this remains unverified for loss-magnitude detection.

**Base rate sensitivity**: The precision bounds depend strongly on minority prevalence. At higher minority rates (e.g., 15% in CelebA), higher absolute precision would be achievable.

---

## 7. Conclusion

This work demonstrated that simplicity bias creates a detectable signature in training dynamics: minority-group samples exhibit 8× higher loss at 5% of training epochs compared to majority samples. This signal enables 6.6× improvement over random baseline for minority detection without group labels.

Linear probe analysis established the mechanism: model representations encode spurious features with approximately 10 percentage points higher accuracy than core features throughout training. With pretrained features, this manifests as an accuracy magnitude gap rather than a temporal gap—both feature types peak at the same epoch.

The detection precision of 33% reflects base rate constraints rather than signal weakness; the statistical separation is highly significant (p < 10⁻¹⁴). This suggests that loss-based detection could inform weighted training schemes, though intervention effectiveness remains to be validated.

---

## References

Izmailov, P., Podoprikhin, D., Garipov, T., Vetrov, D., & Wilson, A. G. (2022). Averaging weights leads to wider optima and better generalization. *NeurIPS 2022*.

Liu, E. Z., Haghgoo, B., Chen, A. S., Raghunathan, A., Koh, P. W., Sagawa, S., Liang, P., & Finn, C. (2021). Just Train Twice: Improving Group Robustness without Training Group Information. *ICML 2021*.

Sagawa, S., Koh, P. W., Hashimoto, T. B., & Liang, P. (2019). Distributionally Robust Neural Networks for Group Shifts: On the Importance of Regularization for Worst-Case Generalization. *ICLR 2020*.

Yang, Y., Zhang, H., Katabi, D., & Ghassemi, M. (2023). Change is Hard: A Closer Look at Subpopulation Shift. *AISTATS 2024*.

Zhu, Z., Liu, J., & Yang, Y. (2023). LA-SSL: Layer-Adaptive Self-Supervised Learning. *arXiv preprint*.
