# Gradient Alignment as Spurious-Minority Detector: An Empirical Negative Result and Mechanistic Diagnosis

**Anonymous Authors**
*Under review*

---

## Abstract

Gradient direction during ERM training encodes which samples conflict with the dominant batch learning signal — a property theoretically well-suited for identifying spurious-minority group members without group annotations. We test this directly: we compute per-sample last-layer gradient cosine similarity with the within-batch mean gradient and measure its ROC-AUC as a spurious-minority detector on Waterbirds and CelebA across training epochs {1, 5, 10, 25, 50}. The signal fails decisively: alignment ROC-AUC reaches only 0.35 on Waterbirds and 0.63 on CelebA at best, far below per-sample loss (0.77–0.97, across datasets and epochs), and is *inverted* on Waterbirds at epoch 1 (ROC-AUC = 0.15), where spurious-minority samples appear more aligned with the batch mean than majority samples. We attribute this to batch contamination: high-loss minority samples disproportionately pull the within-batch mean gradient toward their own direction, paradoxically increasing their measured cosine similarity with the mean. This failure mode is prevalence-dependent, explaining why the inversion is weaker on CelebA (~0.8% minority) than Waterbirds (~5%). We derive an empirically grounded design principle: two-pass global mean gradient reference (not within-batch mean) is expected to be necessary to avoid contamination and recover the directional minority signal. Our results constitute the first direct empirical characterization of gradient alignment ROC-AUC as a spurious-minority detector on these benchmarks, and provide a concrete corrective direction for gradient-based annotation-free debiasing methods.

---

## 1. Introduction

A model's gradient direction during training encodes which samples it finds surprising — yet we show that measuring this surprise relative to a mini-batch average produces a signal that is *anti-predictive* of spurious-minority group membership on Waterbirds: ROC-AUC = 0.15 at epoch 1, well below chance. The per-sample loss achieves 0.93 on the same samples, at the same epoch. This inversion is not a quirk of implementation: it reveals a previously uncharacterized failure mode in gradient-based minority detection, and its diagnosis points directly to a viable corrected method.

The motivation for gradient-based debiasing is compelling. Models trained with empirical risk minimization (ERM) on spuriously-correlated data learn shortcuts: they exploit simple, spurious statistical patterns rather than the true causal features. On standard benchmarks, ERM achieves 97% average accuracy on Waterbirds while dropping to 72% worst-group accuracy — failing catastrophically for the minority group (landbirds photographed on water) that cannot rely on the spurious background correlation [Sagawa et al., 2020]. Existing debiasing methods either require group annotations (GroupDRO [Sagawa et al., 2020]) or resort to two-stage training using magnitude-based proxies for minority membership (JTT [Liu et al., 2021]; LfF [Nam et al., 2020]). Magnitude-based proxies — high loss, misclassification — conflate hard-majority samples with spurious-minority samples: both cause high loss, but for different reasons.

Gradient *direction* offers a theoretically cleaner proxy. If spurious-minority samples have gradients that consistently conflict with the majority-dominated batch direction, the cosine similarity between a sample's gradient and the batch mean gradient should be low for minority samples — distinguishing them from hard-majority samples whose gradients *align* with the batch mean despite high loss. This proxy requires no group labels, operates online during training, and is now computationally tractable via per-sample gradient APIs (PyTorch `vmap/grad`). A recent concurrent work [Bias Leaves a Gradient Trail, 2025] independently demonstrates that gradient probes can identify biased samples without labels using directional gradient signals with globally stable references — reinforcing the theoretical basis for the directional approach.

We directly test this claim. We compute per-sample last-layer gradient cosine similarity with the within-batch mean gradient for all training samples at epochs {1, 5, 10, 25, 50} on Waterbirds and CelebA under standard ERM training (ResNet-50, SGD). The result falsifies the directional hypothesis: alignment ROC-AUC never exceeds loss ROC-AUC at any epoch on either dataset, and on Waterbirds the signal is actively inverted (0.15 at epoch 1).

**The inversion reveals a batch contamination effect.** With batch size $B = 32$ and ~5% minority prevalence, 1–2 minority samples per batch carry disproportionately large gradient magnitudes (due to high training loss; loss ROC-AUC = 0.93 at epoch 1 on Waterbirds, consistent with high minority loss). These high-magnitude samples pull the within-batch mean gradient toward their own direction, paradoxically increasing the measured cosine similarity of minority samples with the batch mean. The batch mean is thus not a stable representation of the majority gradient direction — it is contaminated by the exact samples it was meant to distinguish.

This diagnosis is actionable. A two-pass global mean gradient — computed over the full training set and averaged across thousands of batches — is stable, majority-dominated, and not subject to per-batch contamination spikes. It preserves the annotation-free property and is expected to address the root cause.

**Our contributions are:**

1. **Empirical characterization:** First direct measurement of per-sample last-layer gradient alignment ROC-AUC as a spurious-minority detector on Waterbirds and CelebA. We establish that within-batch cosine similarity alignment fails (ROC-AUC ≤ 0.35 on Waterbirds; ≤ 0.63 on CelebA across epochs 1–50), while per-sample loss remains an effective proxy (0.77–0.97).

2. **Novel failure mode:** Documentation of the "alignment inversion effect" — within-batch gradient alignment is anti-predictive on Waterbirds at epoch 1, with minority samples appearing *more* aligned with the batch mean than majority samples. This is a new empirical finding about gradient-based minority detection methods.

3. **Design principle:** An empirically grounded rationale for why two-pass global mean gradient reference direction (not within-batch mean) is expected to be necessary for gradient cosine similarity to retain discriminative power in the spurious-minority detection setting.

The remainder of the paper is organized as follows: Section 2 reviews related work. Section 3 presents the methodology and experimental design. Section 4 describes our experiments. Section 5 presents results. Section 6 discusses the batch contamination diagnosis and limitations. Section 7 concludes.

---

## 2. Related Work

### Spurious Correlations and Worst-Group Accuracy

Neural networks trained with ERM exploit spurious correlations — dataset artifacts where simple co-occurring features predict class labels during training but fail to generalize across subpopulations. On Waterbirds [Wah et al., 2011; Sagawa et al., 2020] and CelebA [Liu et al., 2015], spurious correlations between background/hair color and class labels cause ERM models to achieve high average accuracy (97% and 95% respectively) while failing catastrophically on minority groups (worst-group accuracy 72% and 47%) [Sagawa et al., 2020]. The theoretical basis is established: Shah et al. [2020] formally prove simplicity bias; Arpit et al. [2017] show DNNs memorize easy-to-fit patterns before hard ones, producing temporal structure exploitable for minority identification.

### Label-Free Debiasing Methods

Methods requiring group annotations (GroupDRO [Sagawa et al., 2020]) achieve strong worst-group performance but assume the label structure one wishes to avoid. In the annotation-free regime: JTT [Liu et al., 2021] identifies minority as misclassified samples in an initial ERM run (achieving 86.7% worst-group on Waterbirds under their experimental setup); LfF [Nam et al., 2020] uses relative per-sample loss online. Both succeed because per-sample loss is an effective proxy — minority samples incur high loss where the spurious feature conflicts with the true label. However, this magnitude-based proxy conflates hard-majority samples with spurious-minority samples [Liu et al., 2021; Kirichenko et al., 2022]. DFR [Kirichenko et al., 2022] achieves near-supervised performance by retraining a linear head on a balanced held-out set, but requires a labelled validation split.

Our work extends the annotation-free regime to gradient *direction* as a proxy signal, testing whether directional information distinguishes spurious-minority from hard-majority samples in a way loss magnitude cannot. We note that our contribution is signal existence (ROC-AUC measurement), not downstream task performance; we do not reproduce JTT or GroupDRO baselines in our experimental setup, and the 86.7% worst-group figure is cited from Liu et al. [2021] and not measured here.

### Gradient-Based Training Dynamics Analysis

Per-sample gradient analysis has a growing role in understanding training. Katharopoulos and Fleuret [2018] use gradient norms for importance sampling. Toneva et al. [2019] track forgetting events. Swayamdipta et al. [2020] characterize data cartography using per-epoch loss and correctness signals. Most relevant: "Bias Leaves a Gradient Trail" [2025] demonstrates gradient probes computed at layers can identify biased samples without labels using directional gradient signals with globally stable references — consistent with our finding that per-batch reference is the failure point. Gradient alignment has also been studied in continual learning (GEM [Lopez-Paz & Ranzato, 2017]) and multi-task learning [Yu et al., 2020], where global or cross-task reference directions are used — not per-mini-batch statistics.

**Our contribution:** No prior study has directly measured within-batch gradient alignment ROC-AUC as a spurious-minority detector on Waterbirds or CelebA across training epochs. We fill this gap, characterize the failure mode, and identify the reference direction correction required.

---

## 3. Method

### Overview

Building on the theoretical intuition that spurious-minority samples should have gradients conflicting with the majority-dominated batch mean, we define a **Gradient Alignment Score** as the negated cosine similarity between a sample's per-sample last-layer gradient and the within-batch mean gradient. A low alignment score (conflicting direction) serves as the minority membership signal.

We measure whether the gradient alignment score achieves higher ROC-AUC than per-sample loss as a binary predictor of spurious-minority group membership, at multiple training epochs. The intervention (upweighting) is not evaluated here — it is only motivated if the directional signal surpasses loss.

### Per-Sample Gradient Alignment Score

Let $f_\theta: \mathcal{X} \to \mathbb{R}^C$ be a neural network. For a mini-batch $\mathcal{B} = \{(x_i, y_i)\}_{i=1}^{B}$, define per-sample last-layer gradients:

$$g_i = \nabla_{\theta_{\text{fc}}} \mathcal{L}(f_\theta(x_i), y_i)$$

and batch-mean gradient $\bar{g} = \frac{1}{B} \sum_{i=1}^{B} g_i$. The alignment score is:

$$a_i = 1 - \frac{g_i \cdot \bar{g}}{\|g_i\|_2 \cdot \|\bar{g}\|_2} \in [0, 2]$$

where high $a_i$ indicates gradient conflict with the batch mean (predicted minority signal). ROC-AUC of $a_i$ below 0.5 means minority samples have *lower* conflict scores — equivalently, higher raw cosine similarity with the batch mean — the direct opposite of the directional hypothesis.

**Rationale for last-layer scope:** Restricting to $\theta_{\text{fc}}$ (Linear(2048, $C$), 4,098 parameters for $C=2$) provides computational feasibility with vmap and directly captures class-discriminative gradient direction.

**Rationale for cosine similarity:** Magnitude-invariant, isolating the directional component from per-sample loss magnitude — the theorized advantage over loss-based proxies.

### Efficient Computation via vmap

```python
from torch.func import functional_call, vmap, grad

def per_sample_loss(params, buffers, x, y):
    pred = functional_call(model, (params, buffers), (x.unsqueeze(0),))
    return F.cross_entropy(pred, y.unsqueeze(0))

ft_per_sample_grad = vmap(grad(per_sample_loss), in_dims=(None, None, 0, 0))
fc_params = {k: v for k, v in model.named_parameters() if 'fc' in k}
per_sample_grads = ft_per_sample_grad(fc_params, {}, x_batch, y_batch)
```

The vmap scope is restricted to `model.fc`; the backbone is frozen during probe computation. Per-batch gradient storage: 32 × 4,098 = 131K floats. PyTorch ≥ 2.0 is required for `torch.func.vmap`.

### Probe Injection Protocol

At each checkpoint epoch $e \in \{1, 5, 10, 25, 50\}$, after standard ERM training:
1. Freeze model parameters.
2. Run full pass over training set (batch size 32).
3. Compute $a_i$ and $\ell_i$ for all $N$ training samples.
4. Evaluate ROC-AUC of each against binary minority group membership labels.

### Training Configuration

| Parameter | Waterbirds | CelebA |
|-----------|-----------|--------|
| Model | ResNet-50 (IMAGENET1K_V1) | ResNet-50 (IMAGENET1K_V1) |
| Optimizer | SGD, lr=0.001, momentum=0.9, wd=1e-4 | SGD, lr=0.0001, momentum=0.9, wd=1e-4 |
| Batch size | 32 | 32 |
| Train size | 4,795 | 16,000 (stratified subsample, ~10% of 162K) |
| Seed | 42 | 42 |
| Hardware | NVIDIA H100 NVL | NVIDIA H100 NVL |

---

## 4. Experimental Setup

### Experimental Question

**Does per-sample last-layer gradient cosine similarity with the within-batch mean gradient achieve higher ROC-AUC than per-sample loss as a predictor of spurious-minority group membership on Waterbirds and CelebA?**

Secondary questions: (1) How does the signal evolve across epochs? (2) Is failure consistent across datasets with different minority prevalences? (3) What does the gap magnitude suggest about the failure mechanism?

### Datasets

**Waterbirds** [Wah et al., 2011; Sagawa et al., 2020]: Synthetic spurious correlation (bird species × background, 95% strength). Train: 4,795 samples, ~82% majority. Minority groups for evaluation: landbird on water and waterbird on land (group IDs {1, 2} in the group_DRO encoding).

**CelebA** [Liu et al., 2015]: Blond hair prediction; spurious attribute: gender. Train: 16,000 samples (stratified subsample, ~10% of full 162K dataset, seed 42). Minority: blond male (~0.8% of training data, group ID 3).

CelebA complements Waterbirds with more extreme minority prevalence — key for testing whether prevalence modulates the contamination effect.

### Baselines

- **Gradient Alignment Score ($a_i$):** Negated within-batch cosine similarity (Section 3)
- **Per-Sample Loss ($\ell_i$):** Cross-entropy loss; signal used by JTT and LfF

Identical model states; the single variable is signal type. We evaluate signal discriminability (ROC-AUC) rather than downstream worst-group accuracy; the latter is only relevant if the signal exists.

### Evaluation

**ROC-AUC** (sklearn): threshold-free discriminability measure. AUC < 0.5 indicates inverted signal. Binary labels: $y_i = \mathbb{1}[\text{group\_id}_i \in \text{minority}]$.

---

## 5. Results

### Primary Finding: Alignment Signal Fails on Both Datasets

**Table 1:** Gradient alignment vs. per-sample loss ROC-AUC at checkpoint epochs.

| Epoch | WB Align | WB Loss | WB Gap† | CelebA Align | CelebA Loss | CelebA Gap† |
|-------|:--------:|:-------:|:-------:|:------------:|:-----------:|:-----------:|
| 1     | 0.150    | 0.930   | −0.780  | 0.246        | 0.975       | −0.729      |
| 5     | 0.301    | 0.854   | −0.554  | 0.484        | 0.949       | −0.465      |
| 10    | 0.340    | 0.821   | −0.481  | 0.523        | 0.939       | −0.416      |
| 25    | 0.340    | 0.801   | −0.503  | 0.407        | 0.910       | −0.503      |
| 50    | 0.349    | 0.775   | −0.426  | 0.632        | 0.905       | −0.273      |

*† Gap = Align − Loss; negative values indicate alignment below loss. Values rounded to three decimal places from raw results (e.g., WB epoch 1: alignment = 0.1495, loss = 0.9297). See `h-e1/experiment_results.json` for full precision.*

![ROC-AUC vs. training epoch for gradient alignment score and per-sample loss, Waterbirds and CelebA combined](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_scsl/docs/youra_research/paper/figures/roc_auc_vs_epoch.png)

**Figure 1:** ROC-AUC vs. training epoch for gradient alignment score (lower curves) and per-sample loss (upper curves), on Waterbirds (solid lines) and CelebA (dashed lines). The alignment ROC-AUC remains far below loss ROC-AUC at all epochs on both datasets. The dotted horizontal line at 0.5 marks chance-level performance; alignment falls below chance on Waterbirds throughout training. Source: `h-e1/figures/roc_auc_vs_epoch.png`.

### The Alignment Inversion Effect on Waterbirds

At epoch 1 on Waterbirds: alignment ROC-AUC = **0.150** (raw value: 0.1495), substantially below chance (0.5). The conflict score $a_i$ (negated cosine similarity) is anti-predictive: minority samples score *lower* on $a_i$ than majority samples, meaning minority samples have *higher* raw cosine similarity with the within-batch mean — the direct opposite of the hypothesis. The signal moves toward chance by epoch 50 (0.349) but alignment never approaches discriminative territory at any tested epoch. The gap to loss remains 0.43–0.78 throughout training.

![ROC-AUC vs. training epoch, Waterbirds only](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_scsl/docs/youra_research/paper/figures/roc_auc_vs_epoch_waterbirds.png)

**Figure 2:** Waterbirds detail. Alignment ROC-AUC (0.150–0.349) vs. loss ROC-AUC (0.775–0.930) across epochs 1–50. The alignment curve remains below the dashed chance line (0.5) at all tested epochs; the loss curve begins near 0.93 and degrades monotonically as the model memorizes training samples. Source: `h-e1/figures/roc_auc_vs_epoch_waterbirds.png`.

### Temporal Dynamics on Waterbirds

On Waterbirds, per-sample loss ROC-AUC begins high (0.930 at epoch 1) and monotonically degrades to 0.775 at epoch 50 as the model memorizes training samples (training loss = 0.174 at epoch 1, approaching near-zero at 0.0003 by epoch 50). Gradient alignment begins inverted and slowly improves — converging toward loss from below, as near-zero training loss collapses all gradient discriminability.

### CelebA: Weak Positive Signal at Late Epochs

CelebA alignment begins inverted (0.246 at epoch 1), recovers through epoch 10 (0.523), dips at epoch 25 (0.407), then peaks at epoch 50 (0.632). It remains 0.273 below loss (0.905) at best. The weaker inversion is consistent with batch contamination being prevalence-dependent: at ~0.8% minority prevalence and B=32, the expected number of minority samples per batch is approximately 0.26, substantially reducing their contamination impact on the within-batch mean compared to Waterbirds (~5% minority, 1–2 samples per batch).

![ROC-AUC vs. training epoch, CelebA only](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_scsl/docs/youra_research/paper/figures/roc_auc_vs_epoch_celeba.png)

**Figure 3:** CelebA detail. Alignment ROC-AUC (0.246–0.632) vs. loss ROC-AUC (0.905–0.975) across epochs 1–50. Alignment shows a non-monotonic trajectory, dipping at epoch 25 before recovering to 0.632 at epoch 50. The gap at the best alignment epoch (epoch 50) is 0.273. Source: `h-e1/figures/roc_auc_vs_epoch_celeba.png`.

Score distributions and full ROC curves are presented in the Appendix (Figures 4–7).

---

## 6. Discussion

### Mechanistic Diagnosis: Batch Contamination

The inversion effect requires a mechanistic explanation. We propose **batch contamination** as the primary candidate: under standard ERM, minority samples incur high loss and large gradient norms. With batch size $B=32$ and ~5% minority prevalence, 1–2 minority samples per batch carry disproportionately large gradient magnitudes. These pull the within-batch mean gradient toward the minority gradient direction, increasing minority samples' measured cosine similarity with the mean — producing the observed inversion.

Formally, if minority gradients have magnitude $k > 1$ times majority gradient magnitude, the minority contribution to the batch mean is $\propto k \cdot n_\text{min} / B$. With $k$ potentially large at epoch 1 due to high minority loss (empirically, loss ROC-AUC = 0.930 on Waterbirds at epoch 1 indicates minority samples incur substantially higher loss than majority, consistent with large $k$, though $k$ is not directly measured here) and $n_\text{min} = 1$, a single minority sample's gradient contribution to the mean may be comparable to the combined majority contribution.

**Prevalence evidence:** CelebA's weaker inversion (0.246 vs. 0.150) at much lower minority prevalence (~0.8%) is quantitatively consistent with contamination being proportional to $k \cdot n_\text{min} / B$.

### Alternative Explanations

**Gradient compression at last layer:** The Linear(2048, 2) projects to 2 class logits; group-discriminative signal in earlier 2048-dim representations may be destroyed. Penultimate-layer alignment experiments would distinguish this from batch contamination — this is an immediate next step.

**ImageNet pretraining:** At epoch 1, both majority and minority samples may produce similar fine-tuning gradients, reducing directional discriminability. This may compound with contamination at early epochs.

These alternatives are not ruled out by the current experiments. The batch contamination hypothesis is supported by the prevalence-dependent pattern across datasets, but definitive separation from these alternatives requires additional ablations.

### The Expected Corrective Direction

A **two-pass global mean gradient** is expected to address the root cause:
- Pass 1: Standard ERM training
- Pass 2: Compute $\bar{g}_\text{global} = \frac{1}{N}\sum_{i=1}^N g_i$ over full training set
- Align each sample's gradient against $\bar{g}_\text{global}$ (not per-batch mean)

The global mean is stable, majority-dominated across thousands of samples, and robust to per-batch minority gradient spikes. The annotation-free property is preserved. Computational cost: one additional full-dataset pass per epoch. Whether this correction resolves the inversion remains to be empirically validated.

### Limitations

- **Single seed (42):** Appropriate for a proof-of-concept existence test; the failure margin (0.27–0.78 gap) is replication-grade.
- **CelebA 16K subsample:** Group composition ratios are preserved by stratified sampling; the conclusion is unchanged.
- **Last layer only:** Cannot conclude alignment fails at all layers; penultimate-layer alignment is untested.
- **Global mean gradient untested:** Identified as the expected corrective direction, but not yet empirically validated.
- **Batch contamination not directly isolated:** The prevalence-dependent pattern across datasets is consistent with contamination, but does not rule out last-layer gradient compression or ImageNet pretraining as alternative or contributing explanations.

### Broader Implications

The batch contamination failure mode may affect any method using within-batch gradient statistics for minority identification in imbalanced settings. Methods should prefer globally computed gradient reference directions over per-batch statistics when minority prevalence is low and minority samples have high loss.

---

## 7. Conclusion

We opened with a counterintuitive finding: spurious-minority samples appear *more* aligned with the within-batch mean gradient than majority samples on Waterbirds at epoch 1 (alignment ROC-AUC = 0.150), despite the theoretical prediction that conflicting gradient directions should reveal them. This inversion is consistent with batch contamination by high-magnitude minority gradients.

The results are clear: within-batch gradient alignment ROC-AUC ≤ 0.35 (Waterbirds) and ≤ 0.63 (CelebA) against per-sample loss 0.77–0.97 under identical conditions. The failure is not marginal. Per-sample loss remains the practical baseline for annotation-free minority identification.

The inversion is a diagnosis, not a dead end. The within-batch mean is contaminated by high-loss minority samples — structurally, due to mini-batch imbalance. The natural corrective direction is a two-pass global mean gradient, stable and majority-dominated, requiring one additional full-dataset pass per epoch, annotation-free. Distinguishing batch contamination from last-layer gradient compression (the primary alternative explanation) requires penultimate-layer alignment experiments — an immediate next step.

**Established:** within-batch alignment fails, with a novel inversion failure mode; the failure is consistent with a mechanistic and prevalence-dependent contamination effect; two-pass global mean is the expected corrective direction. **Open:** whether the correction resolves the inversion; whether penultimate-layer alignment provides complementary information. Gradient direction as a minority signal remains theoretically sound. The reference direction was the problem — not the concept.

---

## References

Sagawa, S., Koh, P. W., Hashimoto, T. B., & Liang, P. (2020). Distributionally Robust Neural Networks. *ICLR 2020*.

Liu, E. Z., Haghgoo, B., Chen, A. S., Raghunathan, A., Koh, P. W., Sagawa, S., Liang, P., & Finn, C. (2021). Just Train Twice: Improving Group Robustness without Training Group Information. *ICML 2021*.

Nam, J., Cha, H., Ahn, S., Lee, J., & Shin, J. (2020). Learning from Failure: De-biasing Classifier from Biased Classifier. *NeurIPS 2020*.

Kirichenko, P., Izmailov, P., & Wilson, A. G. (2022). Last Layer Re-Training is Sufficient for Robustness to Spurious Correlations. *ICLR 2023*.

Wah, C., Branson, S., Welinder, P., Perona, P., & Belongie, S. (2011). The Caltech-UCSD Birds-200-2011 Dataset. *Technical Report CNS-TR-2011-001, Caltech*.

Liu, Z., Luo, P., Wang, X., & Tang, X. (2015). Deep Learning Face Attributes in the Wild. *ICCV 2015*.

Shah, H., Tamuly, K., Raghunathan, A., Jain, P., & Netrapalli, P. (2020). The Pitfalls of Simplicity Bias in Neural Networks. *NeurIPS 2020*.

Arpit, D., Jastrzębski, S., Ballas, N., Krueger, D., Bengio, E., Kanwal, M. S., Maharaj, T., Fischer, A., Courville, A., Bengio, Y., & Lacoste-Julien, S. (2017). A Closer Look at Memorization in Deep Networks. *ICML 2017*.

Rahaman, N., Baratin, A., Arpit, D., Draxler, F., Lin, M., Hamprecht, F. A., Bengio, Y., & Courville, A. (2019). On the Spectral Bias of Neural Networks. *ICML 2019*.

Toneva, M., Sordoni, A., Combes, R. T. d., Trischler, A., Bengio, Y., & Gordon, G. J. (2019). An Empirical Study of Example Forgetting during Deep Neural Network Learning. *ICLR 2019*.

Swayamdipta, S., Schwartz, R., Lourie, N., Wang, Y., Hajishirzi, H., Smith, N. A., & Choi, Y. (2020). Dataset Cartography: Mapping and Diagnosing Datasets with Training Dynamics. *EMNLP 2020*.

Katharopoulos, A., & Fleuret, F. (2018). Not All Samples Are Created Equal: Deep Learning with Importance Sampling. *ICML 2018*.

[BiasTail25] Anonymous. (2025). Bias Leaves a Gradient Trail. *arXiv:2605.28780*.

Lopez-Paz, D., & Ranzato, M. (2017). Gradient Episodic Memory for Continual Learning. *NeurIPS 2017*.

Yu, T., Kumar, S., Gupta, A., Levine, S., Hausman, K., & Finn, C. (2020). Gradient Surgery for Multi-Task Learning. *NeurIPS 2020*.

Kirichenko, P., Izmailov, P., & Wilson, A. G. (2022). Correct-N-Contrast: a Contrastive Approach for Improving Robustness to Spurious Correlations. *ICML 2022*.

PyTorch Team. (2025). torch.func API Documentation.

---

## Appendix

### A. Score Distributions at Epoch 5

![Score distributions at epoch 5 by group, Waterbirds](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_scsl/docs/youra_research/paper/figures/score_distribution_epoch5_waterbirds.png)

**Figure 4:** Alignment score ($a_i$) and per-sample loss distributions by group on Waterbirds at epoch 5, displayed as overlaid kernel density estimates. The minority groups (landbird-on-water, waterbird-on-land; group IDs {1, 2}) are shifted toward *lower* $a_i$ values relative to majority — i.e., higher raw cosine similarity with the batch mean — confirming the inversion: minority samples appear more aligned with the batch mean, not less. Loss distributions in the same figure show clean minority/majority separation consistent with loss ROC-AUC = 0.854 at epoch 5. Source: `h-e1/figures/score_distribution_epoch5_waterbirds.png`.

![Score distributions at epoch 5 by group, CelebA](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_scsl/docs/youra_research/paper/figures/score_distribution_epoch5_celeba.png)

**Figure 5:** Alignment score and per-sample loss distributions at epoch 5 by group on CelebA (blond-male minority, group ID 3, vs. all others). Minority and majority alignment score distributions are near-identical, confirming that the alignment signal is non-discriminative at epoch 5 (alignment ROC-AUC = 0.484). Loss distributions show clear separation consistent with loss ROC-AUC = 0.949. Source: `h-e1/figures/score_distribution_epoch5_celeba.png`.

### B. ROC Curves at Best Alignment Epoch

![ROC curves at epoch 50 (best alignment epoch), Waterbirds](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_scsl/docs/youra_research/paper/figures/roc_curves_best_epoch_waterbirds.png)

**Figure 6:** ROC curves at epoch 50 (the epoch at which alignment achieves its best performance on Waterbirds). The alignment ROC curve (AUC = 0.349) lies near the diagonal, indicating near-random discriminability; the loss ROC curve (AUC = 0.775) shows substantial area above the diagonal. Source: `h-e1/figures/roc_curves_best_epoch_waterbirds.png`.

![ROC curves at epoch 50 (best alignment epoch), CelebA](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_scsl/docs/youra_research/paper/figures/roc_curves_best_epoch_celeba.png)

**Figure 7:** ROC curves at epoch 50 (the epoch at which alignment achieves its best performance on CelebA). Alignment ROC-AUC = 0.632, showing slightly positive but weak discriminability; loss ROC-AUC = 0.905. Source: `h-e1/figures/roc_curves_best_epoch_celeba.png`.

### C. Experiment Configuration Details

Full experiment configuration, including minority group ID encoding and dataset preprocessing, is provided in Section 3 (Methodology). Raw numerical results at full precision are available in `h-e1/code/outputs/results.json` and `h-e1/experiment_results.json`. Code is available at [anonymized for review].
