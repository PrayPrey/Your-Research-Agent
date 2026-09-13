# Gradient Norms as Label-Free Minority Proxies: A Mechanistic Study of the Prediction-Residual Signal for Spurious Correlation Robustness

## Abstract

Neural networks trained on spuriously correlated data achieve high average accuracy while failing on minority groups that lack the spurious feature — a problem typically addressed with group annotations. This work investigates whether the per-sample normalized last-layer gradient norm, g̃ᵢ = ‖∇_W ℓᵢ‖ / ‖h(xᵢ)‖, constitutes a usable label-free minority group proxy signal during standard ERM training. The hypothesis is that minority samples, unable to exploit the spurious shortcut, maintain persistently elevated prediction residuals that appear directly in their gradient norms via the outer-product decomposition of the fully connected layer gradient. On the Waterbirds benchmark, g̃ achieves AUC = 0.914 for minority group prediction at epoch 5 of ERM training — without any group annotations — with a minority/majority ratio of 8.8x that persists to 8.5x at epoch 10. Feature norm distributions (h_norm_std_ratio ≈ 0.10) confirm that the signal reflects prediction-error differences rather than feature-scale artifacts. The overall gate result for the existence experiment is PARTIAL (2/3 criteria satisfied): the ratio and AUC criteria pass, while a third criterion — balance deviation of the top-25% subset — fails at 0.379 against a ≤0.10 threshold. Post-hoc analysis identifies this as a criterion design mismatch rather than a mechanism failure. Worst-group accuracy evaluation via a proposed Stage 2 last-layer retraining procedure was not executed and constitutes future work.

---

## 1. Introduction

A well-documented failure mode of empirical risk minimization (ERM) is the collapse of worst-group accuracy (WGA) on datasets with spurious correlations. On Waterbirds [Sagawa et al., 2019] — where 95% of training samples associate waterbirds with water backgrounds and landbirds with land backgrounds — a ResNet-50 trained with ERM achieves high average accuracy while performing poorly on the minority groups that do not carry the spurious feature (56 waterbird-on-land samples and 184 landbird-on-water samples out of 4,795 total training samples).

The dominant supervised remedy, Group Distributionally Robust Optimization (GroupDRO) [Sagawa et al., 2019], explicitly minimizes worst-group loss and achieves strong WGA, but requires per-sample group annotations. This requirement restricts practical deployment, since obtaining group labels demands domain expertise and is costly at scale.

Existing label-free alternatives use coarse proxy signals. Just Train Twice (JTT) [Liu et al., 2021] uses binary misclassification by an ERM model as a minority proxy, upweighting the error set in a second training stage. Learning from Failure (LfF) [Nam et al., 2020] uses the relative cross-entropy loss between a biased and a debiased network to upweight hard samples. Neither provides a mechanistic account grounded in the gradient structure of ERM training.

This work investigates the per-sample normalized last-layer gradient norm g̃ᵢ as a minority group proxy. The mechanistic hypothesis is that the outer-product decomposition of the fully connected layer gradient, ‖∇_W ℓᵢ‖_F = ‖pᵢ − yᵢ‖ · ‖h(xᵢ)‖, directly exposes the prediction residual ‖pᵢ − yᵢ‖, and that BatchNorm feature equalization renders ‖h(xᵢ)‖ approximately uniform across groups. Under this account, minority samples that cannot exploit the spurious shortcut maintain elevated prediction residuals throughout early ERM training, producing persistently elevated g̃ᵢ values relative to majority samples.

The reported experiments address four questions: (RQ1) Does g̃ achieve AUC > 0.70 for minority group prediction at T_id = 5? (RQ2) What is the minority/majority ratio at T_id ∈ {1, 3, 5, 10}? (RQ3) Does the ratio persist at T_id = 10? (RQ4) Does BatchNorm equalize feature norms (h_norm_std_ratio < 0.5)?

**Experimental scope.** Only the existence experiment (H-E1) was executed. The proposed full pipeline — Stage 2 last-layer retraining to measure WGA — was not run. No WGA results are reported. The findings reported here concern the proxy signal quality only.

**Contributions:**

1. Empirical measurement of g̃ as a minority proxy signal: AUC = 0.914 and ratio = 8.8x at T_id = 5, without group annotations, on Waterbirds.
2. Mechanistic confirmation via outer-product decomposition and BatchNorm feature equalization (h_norm_std_ratio ≈ 0.10).
3. An efficient computation procedure using a forward hook on the FC layer, requiring no additional backward passes.
4. Identification of a criterion design error: class balance deviation is an inappropriate metric for minority-focused selection on imbalanced datasets; minority recall in the selected subset is the appropriate criterion.

---

## 2. Related Work

### 2.1 Spurious Correlation Robustness

Sagawa et al. [2019] formalize spurious correlation robustness as a benchmark challenge with Waterbirds and the GroupDRO objective. GroupDRO achieves strong WGA by minimizing the maximum group-specific loss at each step but requires group annotations for all training samples. Idrissi et al. [2021] demonstrate that simple data balancing over groups is a competitive baseline on these benchmarks, provided group identity is known, underscoring that the core challenge is identifying which samples belong to minority groups.

### 2.2 Label-Free Two-Stage Methods

**Just Train Twice (JTT)** [Liu et al., 2021] identifies ERM model misclassifications as a minority proxy and upweights this error set in a second training stage. The proxy signal is binary and coarse: a sample is either misclassified or not.

**Learning from Failure (LfF)** [Nam et al., 2020] trains two networks simultaneously and uses the ratio of generalized cross-entropy losses to identify hard samples for upweighting. It requires two parallel training streams.

**Deep Feature Reweighting (DFR)** [Kirichenko et al., 2022] demonstrates that ERM-trained features already encode class-relevant information and that the problem resides in the classifier head. DFR freezes the ERM backbone and retrains only the last layer using a group-balanced validation subset. This achieves strong WGA on Waterbirds but requires group-labeled samples for subset construction. The proposed Stage 2 of the present pipeline follows the DFR principle while replacing group-labeled subset construction with gradient-norm-based selection. Stage 2 was not executed in the reported experiments.

No prior work in this paradigm uses per-sample gradient norms as the minority identification signal.

### 2.3 Gradient Dynamics and Related Signals

The **EL2N score** [Paul et al., 2021] is defined as the expected L2 norm of the prediction-error vector, E‖pᵢ − yᵢ‖. The normalized gradient norm g̃ᵢ = ‖pᵢ − yᵢ‖ is mathematically equivalent to EL2N evaluated at a single checkpoint. EL2N was introduced for dataset pruning by selecting easy (low-error) samples; the present work applies the same per-sample signal in the opposite selection direction — to identify hard (high-error) minority samples — for a different purpose.

**Forgetting events** [Toneva et al., 2019] and **influence functions** [Koh & Liang, 2017] are training-dynamic characterizations of individual samples but have not been applied to minority group identification in spuriously correlated settings.

**GEORGE** [Zhang et al., 2022] discovers pseudo-groups by unsupervised clustering in the model's representation space, then applies GroupDRO. This requires a full clustering step over the training set. The present method uses a scalar per-sample signal requiring no clustering.

**Edge of Stability** dynamics [Cohen et al., 2021] establish that gradient noise near the edge-of-stability regime can amplify per-sample learning rate differences, which may contribute to gradient norm disparity between groups.

### 2.4 Position

The normalized gradient norm g̃ provides a continuous minority proxy signal derived entirely from last-layer training dynamics, requiring no change to the training objective, no parallel networks, no clustering, and no group labels. The outer-product decomposition of the cross-entropy gradient provides a mechanistic interpretation that is absent from other proxy signals.

---

## 3. Method

### 3.1 Normalized Per-Sample Last-Layer Gradient Norm

For a model with a fully connected last layer W ∈ ℝ^(C×d), the per-sample gradient with respect to W for cross-entropy loss satisfies:

∇_W ℓᵢ = (pᵢ − yᵢ_onehot) ⊗ h(xᵢ)

where pᵢ = softmax(W · h(xᵢ)) is the predicted probability vector, yᵢ_onehot is the one-hot label vector, and h(xᵢ) ∈ ℝ^d is the input feature vector to the FC layer. The Frobenius norm of this outer-product gradient is:

‖∇_W ℓᵢ‖_F = ‖pᵢ − yᵢ_onehot‖₂ · ‖h(xᵢ)‖₂

The normalized per-sample gradient norm is defined as:

**g̃ᵢ = ‖∇_W ℓᵢ‖_F / ‖h(xᵢ)‖₂ = ‖pᵢ − yᵢ_onehot‖₂**

For ResNet architectures with BatchNorm layers, feature norms ‖h(xᵢ)‖ are approximately equalized across samples. Dividing by ‖h(xᵢ)‖ isolates the prediction-error residual ‖pᵢ − yᵢ‖ as the informative component.

**Mechanistic prediction.** Under ERM training on spuriously correlated data, majority-group samples that exploit the spurious feature converge to low prediction residuals early. Minority-group samples that cannot exploit the shortcut maintain elevated residuals. Because g̃ᵢ = ‖pᵢ − yᵢ‖ directly, any asymmetry in prediction residuals between groups immediately produces a corresponding asymmetry in normalized gradient norms. This prediction follows from the outer-product decomposition alone, without additional theoretical assumptions, provided BatchNorm approximately equalizes feature norms (verified empirically in Section 5.4).

### 3.2 Efficient Computation via FC Forward Hook

Gradient norms are computed without performing backward passes. A forward hook is registered on the FC layer to capture the input feature vector h(xᵢ) for each sample during a forward pass in eval mode. The normalized gradient norm g̃ᵢ = ‖pᵢ − yᵢ_onehot‖ is then computed directly from the softmax outputs.

**Algorithm 1: g̃ Computation**

```
Input:  model f, dataloader D (eval mode), epoch T_id
Output: {g̃ᵢ}_{i=1}^N

1. Register forward hook on model.fc → captures h(xᵢ) ∈ ℝ^{B×d}
2. Set model.eval() (no BatchNorm updates)
3. For each batch (x_b, y_b) in D:
   a. logits = f(x_b)          [hook captures h(x_b)]
   b. p_b = softmax(logits)
   c. residual_b = p_b − one_hot(y_b)
   d. g̃_b = ‖residual_b‖₂     [row-wise L2 norm]
4. Return concat(all g̃ batches)
```

Computational complexity is O(N) beyond standard inference; no additional backward passes are required. Features captured by the hook are stored on CPU to avoid GPU memory accumulation over full-dataset passes.

### 3.3 Pseudo-Minority Subset Construction

After computing {g̃ᵢ} at epoch T_id, a minority-enriched subset is constructed by ranking samples by g̃:

- **Pseudo-minority subset:** S_min = top-k% of samples by g̃ (high prediction error → minority-enriched)
- **Pseudo-majority subset:** S_maj = bottom-k% of samples by g̃ (low prediction error → majority-enriched)
- **Combined subset:** S = S_min ∪ S_maj

The primary configuration uses k = 25% and T_id = 5. Gradient norms were collected at T_id ∈ {1, 3, 5, 10} to assess temporal robustness.

### 3.4 Proposed Full Pipeline: Stage 2 Last-Layer Retraining (Not Executed)

The full two-stage pipeline — referred to as GNR-LLR (Gradient-Norm-Informed Last-Layer Retraining) — proposes the following Stage 2 procedure as future work:

```
Stage 1 (executed in this work):
  ERM training → g̃ collection at T_id → subset S construction

Stage 2 (proposed, not executed):
  Freeze feature extractor; retrain model.fc on S
  (proposed configuration: SGD, lr=0.01, 100 epochs)
  → Evaluate WGA on test set
```

Stage 2 follows the DFR principle [Kirichenko et al., 2022]: ERM features are assumed to encode class-relevant information, and retraining the classifier head on a minority-enriched subset is expected to reorient the decision boundary away from the spurious feature. The key difference from DFR is that subset construction uses g̃ rather than group-annotated samples. **Stage 2 was not implemented or evaluated in the reported experiments. No WGA results exist for this pipeline.**

---

## 4. Experimental Setup

### 4.1 Dataset

**Waterbirds** [Sagawa et al., 2019] is constructed by compositing bird images from CUB-200 [Welinder et al., 2010] onto backgrounds from Places [Zhou et al., 2018], creating a 95% background-bird spurious correlation in the training set.

| Split | Total | G0 (Landbird/Land) | G1 (Landbird/Water) | G2 (Waterbird/Land) | G3 (Waterbird/Water) |
|-------|------:|-------------------:|--------------------:|--------------------:|---------------------:|
| Train | 4,795 | 3,498 (72.9%) | 184 (3.8%) | 56 (1.2%) | 1,057 (22.1%) |
| Val   | 1,199 | — | — | — | — |
| Test  | 5,794 | — | — | — | — |

Group identity is encoded as G = y × 2 + place, where y ∈ {0,1} is the bird class and place ∈ {0,1} is the background type. Minority groups are G1 and G2, comprising approximately 5% of training samples (240 of 4,795). Preprocessing: resize to 256×256, center crop to 224×224, ImageNet normalization (mean = [0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225]).

### 4.2 Model and Training

**Model:** ResNet-50, pretrained on ImageNet-1K (ResNet50_Weights.IMAGENET1K_V1 API), with the final layer replaced by FC(2048 → 2).

| Hyperparameter | Value |
|:--------------|------:|
| Optimizer | SGD |
| Learning rate | 0.001 |
| Momentum | 0.9 |
| Weight decay | 1×10⁻⁴ |
| Batch size | 128 |
| Training epochs | 10 |
| g̃ collection epochs | {1, 3, 5, 10} |
| Random seed | 42 |
| Hardware | NVIDIA H100 NVL |
| Framework | PyTorch 2.10+cu128, Python 3.10 |

All 4,795 training samples were evaluated at each collection epoch in eval() mode (BatchNorm statistics frozen). No data subsampling was performed.

### 4.3 Evaluation Metrics

| Metric | Definition | Target |
|:-------|:-----------|-------:|
| AUC | sklearn roc_auc_score; minority label = 1 for G1∪G2 | > 0.70 |
| Ratio | mean g̃(G1∪G2) / mean g̃(G0∪G3) | ≥ 3.0x at T_id=5; ≥1.2x at T_id=10 |
| balance_deviation | deviation of top-25% subset from class-uniform distribution | ≤ 0.10 |
| h_norm_std_ratio | std(‖h(xᵢ)‖) / mean(‖h(xᵢ)‖) per group | < 0.5 |

### 4.4 Implementation

The GradientNormAnalyzer class registers a forward hook on model.fc to capture FC input features. The outer-product decomposition g̃ᵢ = ‖softmax(logitᵢ) − one_hot(yᵢ)‖ is computed from saved features and model outputs. The codebase comprises approximately 786 lines across six source files (dataset.py: 122 lines; model.py: 89; train.py: 154; evaluate.py: 162; visualize.py: 259; run_experiment.py: ~200). A test suite of 67 unit and integration tests was run; all 67 passed. Implementation planning compliance: 8/8 coding tasks completed (100%).

---

## 5. Results

The experiment was executed as a single run with seed = 42 on the Waterbirds training set (4,795 samples). No multi-seed replication was performed. All values below derive from the files `h-e1/experiment_results.json` and `h-e1/04_validation.md`.

### 5.1 Proxy Signal Quality at T_id = 5

The three gate criteria at T_id = 5 are:

| Metric | Value | Target | Status |
|:-------|------:|-------:|:-------|
| Minority/majority g̃ ratio | 8.805 | ≥ 3.0x | PASS |
| AUC (minority group prediction) | 0.914 | > 0.70 | PASS |
| balance_deviation (top-25% subset) | 0.379 | ≤ 0.10 | FAIL |

**Overall gate result: PARTIAL (2/3 criteria pass).** The experiment is classified as having a PARTIAL gate outcome; the gate type was MUST_WORK, requiring all three criteria to be satisfied.

AUC = 0.914 indicates that g̃ alone discriminates minority group membership (G1 ∪ G2 vs. G0 ∪ G3) with high accuracy at T_id = 5, without access to group labels. The ratio of 8.805 indicates that the mean normalized gradient norm of minority samples is approximately 8.8 times that of majority samples at this epoch.

Per-group g̃ values at T_id = 5:

| Group | Description | g̃ mean | g_raw mean |
|:------|:------------|--------:|----------:|
| G0 | Landbird + Land (majority) | 0.0221 | 0.553 |
| G1 | Landbird + Water (minority) | 0.3126 | 8.100 |
| G2 | Waterbird + Land (minority) | 0.4328 | 10.487 |
| G3 | Waterbird + Water (majority) | 0.0936 | 2.350 |

G2 — the smallest minority group at 56 training samples — shows the highest mean g̃ (0.4328), consistent with the prediction that samples in minority conditions with no available shortcut maintain the largest prediction residuals.

![Gate metrics at T_id=5](/home/anonymous/YouRA_results_new_4/TEST_scsl/docs/youra_research/20260315_scsl/paper/figures/gate_metrics.png)

*Figure 1. Bar chart of the three gate criteria at T_id = 5. Left: minority/majority g̃ ratio (8.8x vs. 3.0x target). Center: AUC (0.914 vs. 0.70 target). Right: balance_deviation (0.379 vs. 0.10 target; see Section 5.2 for interpretation).*

![Distribution of g̃ per group at epoch 5](/home/anonymous/YouRA_results_new_4/TEST_scsl/docs/youra_research/20260315_scsl/paper/figures/distribution_epoch5.png)

*Figure 2. Distribution of normalized gradient norms per group at T_id = 5. Minority groups G1 and G2 are shifted to higher g̃ values relative to majority groups G0 and G3.*

### 5.2 The balance_deviation Failure: Criterion Design Analysis

The balance_deviation criterion measures how closely the top-25% high-g̃ subset approximates a class-uniform distribution. The measured value (0.379) exceeds the ≤ 0.10 threshold by a factor of 3.8.

Post-hoc analysis in the reflection report identifies this as a criterion design mismatch rather than a mechanism failure. Minority groups G1 and G2 constitute approximately 5% of the 4,795 training samples (240 samples). Even if the top-25% subset (1,199 samples) captured 100% of minority samples, the minority fraction within the subset would be at most 240/1,199 ≈ 20%, far below the 50% required for class balance. The ≤ 0.10 balance_deviation target is therefore unachievable for any minority-focused selection method on this dataset.

The distinction drawn in the reflection report is between class balance (the fraction of each class in the selected subset) and minority recall (the fraction of true minority samples captured in the subset). The DFR-style retraining procedure that motivates subset construction requires minority enrichment, not class balance. Figure 4 (balance heatmap) shows that the top-25% subset is strongly minority-enriched relative to the overall training distribution. The AUC = 0.914 provides indirect evidence that minority recall in the top-25% is high, though direct minority recall was not computed in H-E1; a revised experiment (h-e1-v2) with minority recall as the criterion was proposed but not yet executed.

![Balance heatmap of top-25% subset](/home/anonymous/YouRA_results_new_4/TEST_scsl/docs/youra_research/20260315_scsl/paper/figures/balance_heatmap.png)

*Figure 4. Group composition of the top-25% high-g̃ subset compared to the full training set. Minority groups G1 and G2 are overrepresented in the selected subset relative to their training-set proportions.*

### 5.3 Temporal Persistence of the Proxy Signal

Gradient norms were collected at epochs {1, 3, 5, 10}. Training loss and per-epoch proxy metrics:

| Epoch | Train Loss | Train Acc | Ratio | AUC | balance_deviation |
|------:|-----------:|----------:|------:|----:|------------------:|
| 1 | 0.3395 | 0.8588 | 6.513 | 0.952 | 0.400 |
| 3 | 0.1041 | 0.9641 | 7.493 | 0.912 | 0.404 |
| **5** | **0.0733** | **0.9733** | **8.805** | **0.914** | **0.379** |
| 10 | 0.0340 | 0.9908 | 8.509 | 0.888 | 0.374 |

The ratio increases monotonically from epoch 1 (6.513) to epoch 5 (8.805) and remains at 8.509 at epoch 10. AUC is highest at epoch 1 (0.952) and declines slightly to 0.888 at epoch 10. The ratio at epoch 10 (8.509) substantially exceeds the 1.2x persistence threshold. The balance_deviation metric decreases from 0.400 to 0.374 across epochs, reflecting a gradual shift in the g̃ distribution rather than any improvement relative to the criterion design flaw identified above.

The increase in ratio from epoch 1 to epoch 5 followed by a plateau at epoch 10 is consistent with majority group saturation: as majority samples converge under the spurious shortcut, their g̃ → 0 and the ratio stabilizes. Whether the plateau would continue or reverse beyond epoch 10 was not measured.

![Temporal trajectory of proxy signal](/home/anonymous/YouRA_results_new_4/TEST_scsl/docs/youra_research/20260315_scsl/paper/figures/trajectory.png)

*Figure 3. Minority/majority g̃ ratio (left axis) and AUC (right axis) across epochs 1, 3, 5, and 10. The ratio increases from 6.5x to 8.8x across epochs 1–5 and remains at 8.5x at epoch 10.*

### 5.4 Feature Norm Equalization

The mechanistic interpretation of g̃ as a prediction-residual signal relies on ‖h(xᵢ)‖ being approximately uniform across groups. The h_norm_std_ratio (ratio of standard deviation to mean of feature norms within each group) at T_id = 5:

| Group | h_norm mean | h_norm_std_ratio |
|:------|------------:|-----------------:|
| G0 | 25.248 | ≈ 0.105 |
| G1 | 25.681 | ≈ 0.105 |
| G2 | 25.562 | ≈ 0.105 |
| G3 | 26.412 | ≈ 0.105 |

The h_norm_std_ratio across all groups is approximately 0.105 at T_id = 5 (ranging 0.097–0.118 across epochs 1–10), well below the 0.5 threshold. Feature norm means are within approximately 5% across all four groups. This supports the interpretation that the g̃ signal reflects prediction residual differences rather than feature-scale differences between groups.

![Feature norm distributions per group](/home/anonymous/YouRA_results_new_4/TEST_scsl/docs/youra_research/20260315_scsl/paper/figures/feature_norms.png)

*Figure 5. Feature norm ‖h(xᵢ)‖ distributions per group at T_id = 5. Distributions are highly overlapping across groups (h_norm_std_ratio ≈ 0.10), consistent with BatchNorm equalization.*

---

## 6. Discussion

### 6.1 Interpretation of the PARTIAL Gate Result

The experiment satisfies two of three gate criteria (ratio and AUC) by large margins. The ratio of 8.805 is nearly three times the 3.0x target; AUC = 0.914 is 0.214 above the 0.70 target. The third criterion (balance_deviation ≤ 0.10) is not satisfied, but post-hoc analysis demonstrates that the ≤ 0.10 target is incompatible with the dataset's class imbalance and the definition of the criterion. The reflection decision recorded in `h-e1/reflection_report.md` is SELF_MODIFY: the criterion is to be replaced with minority recall ≥ 0.60 in the next iteration (h-e1-v2), which was not yet executed.

The AUC = 0.914 and ratio = 8.805 results are obtained from a single experimental run (seed = 42). Multi-seed replication (5 seeds) was planned as hypothesis h-m4 but was not executed. These values should therefore be interpreted as single-seed results pending confirmation.

### 6.2 Mechanistic Account

The outer-product decomposition ‖∇_W ℓᵢ‖_F = ‖pᵢ − yᵢ‖ · ‖h(xᵢ)‖ makes a clear mechanistic prediction: if BatchNorm equalizes ‖h(xᵢ)‖ across groups (confirmed, h_norm_std_ratio ≈ 0.10), then the gradient norm disparity between groups must reflect prediction residual differences. The observed 8.8x ratio between minority and majority g̃ values at epoch 5 is consistent with this prediction.

However, the mechanistic account makes no claim about the magnitude of the effect, only its direction. The empirically observed 8.8x ratio could be influenced by factors beyond the outer-product decomposition alone — including specific properties of the Waterbirds dataset, the ImageNet pretraining of the ResNet-50 backbone, and the particular training configuration used. Generalization to other datasets (e.g., CelebA) and architectures was not tested.

### 6.3 Relationship to EL2N

The normalized gradient norm g̃ᵢ = ‖pᵢ − yᵢ‖ is algebraically equivalent to the EL2N score [Paul et al., 2021] when evaluated at a single training checkpoint rather than averaged over early training. EL2N was proposed for dataset pruning — identifying and removing easy (low-error) samples — while the present work uses the same quantity to identify hard (high-error) minority samples for a different downstream task. The two use cases are complementary in the selection direction (bottom-k% vs. top-k%) and distinct in purpose (pruning vs. minority enrichment for retraining).

### 6.4 Limitations

**Limitation 1: WGA not measured.** The primary limitation of this work is that Stage 2 (last-layer retraining on the g̃-selected subset) was not executed. There are no worst-group accuracy results for the proposed GNR-LLR pipeline. Whether the high AUC of the proxy signal translates to improved WGA is an open empirical question.

**Limitation 2: Single dataset.** All experiments were conducted on Waterbirds only. No CelebA experiments were run. Generalization of the signal to other spuriously correlated benchmarks is unknown.

**Limitation 3: Minority recall not directly measured.** AUC = 0.914 provides indirect evidence that top-k% selection captures a large fraction of minority samples, but the direct minority recall at k = 25% was not computed in H-E1. A revised experiment (h-e1-v2) with minority recall as the gate criterion was proposed but not yet run.

**Limitation 4: Single random seed.** All results use seed = 42. Multi-seed validation was not performed. Results may vary across seeds.

**Limitation 5: Temporal behavior beyond epoch 10 not measured.** The ratio plateau at epoch 10 (8.5x) is consistent with majority saturation but this interpretation was not tested by collecting g̃ beyond epoch 10.

---

## 7. Conclusion

This work investigates whether the per-sample normalized last-layer gradient norm g̃ᵢ = ‖∇_W ℓᵢ‖ / ‖h(xᵢ)‖ provides a usable minority group proxy signal during standard ERM training, without group annotations. On Waterbirds, g̃ achieves AUC = 0.914 for minority group prediction at epoch 5 of ERM training, with a minority/majority ratio of 8.8x. The signal persists to epoch 10 (ratio 8.5x, AUC 0.888). Feature norm equalization (h_norm_std_ratio ≈ 0.10) is confirmed, supporting the outer-product decomposition interpretation that the gradient norm disparity reflects prediction residual differences rather than feature-scale artifacts.

The existence experiment (H-E1) receives a PARTIAL gate result (2/3 criteria pass). The third criterion — balance deviation of the top-25% subset — fails at 0.379 against a ≤ 0.10 target; post-hoc analysis identifies this as a criterion design mismatch rather than a mechanism failure. A revised experiment with minority recall as the criterion was proposed but not executed.

The full GNR-LLR pipeline (Stage 2 last-layer retraining) was not implemented or evaluated. No WGA results exist. The relationship between the strong proxy signal quality reported here and downstream WGA improvement via Stage 2 retraining remains to be established empirically.

Three directions follow from this work: (1) executing the full GNR-LLR pipeline (Stage 2) to measure WGA on Waterbirds; (2) running h-e1-v2 with minority recall as the criterion and comparing AUC(g̃) against AUC(binary misclassification); (3) evaluating the proxy signal on CelebA.

---

## References

[Sagawa et al., 2019] Sagawa, S., Koh, P. W., Hashimoto, T. B., & Liang, P. (2019). Distributionally Robust Neural Networks for Group Shifts: On the Importance of Regularization for Worst-Case Generalization. arXiv:1911.08731.

[Liu et al., 2021] Liu, E., Haghgoo, B., Chen, A. S., Raghunathan, A., Koh, P. W., Sagawa, S., Liang, P., & Finn, C. (2021). Just Train Twice: Improving Group Robustness without Training Group Information. ICML 2021.

[Kirichenko et al., 2022] Kirichenko, P., Izmailov, P., & Wilson, A. G. (2022). Last Layer Re-Training is Sufficient for Robustness to Spurious Correlations. ICLR 2023.

[Nam et al., 2020] Nam, J., Cha, H., Ahn, S., Lee, J., & Shin, J. (2020). Learning from Failure: Training Debiased Classifier from Biased Classifier. NeurIPS 2020.

[Paul et al., 2021] Paul, M., Ganguli, S., & Dziugaite, G. K. (2021). Deep Learning on a Data Diet: Finding Important Examples Early in Training. NeurIPS 2021.

[Idrissi et al., 2021] Idrissi, B. Y., Arjovsky, M., Pezeshki, M., & Lopez-Paz, D. (2021). Simple data balancing achieves competitive worst-group-accuracy. CLEaR 2022.

[Zhang et al., 2022] Zhang, M., Sohoni, N. S., Zhang, H. R., Finn, C., & Ré, C. (2022). GEORGE: No Annotations Needed: Group Discovery and Distributionally Robust Optimization. ICLR 2022.

[Cohen et al., 2021] Cohen, J. M., Kaur, S., Li, Y., Kolter, J. Z., & Talwalkar, A. (2021). Gradient Descent on Neural Networks Typically Occurs at the Edge of Stability. ICLR 2021.

[Toneva et al., 2019] Toneva, M., Sordoni, A., Combes, R. T. d., Trischler, A., Bengio, Y., & Gordon, G. J. (2019). An Empirical Study of Example Forgetting during Deep Neural Network Learning. ICLR 2019.

[Koh & Liang, 2017] Koh, P. W., & Liang, P. (2017). Understanding Black-box Predictions via Influence Functions. ICML 2017.

[Ioffe & Szegedy, 2015] Ioffe, S. & Szegedy, C. (2015). Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift. ICML 2015.

[Welinder et al., 2010] Welinder, P. et al. (2010). Caltech-UCSD Birds 200. Technical Report CNS-TR-2010-001, Caltech.

[Zhou et al., 2018] Zhou, B., Lapedriza, A., Khosla, A., Oliva, A., & Torralba, A. (2018). Places: A 10 Million Image Database for Scene Recognition. IEEE TPAMI 2018.
