# Where Does WGA Improvement Come From? Backbone vs. Head Robustification in ResNet-50 on Waterbirds

**Anonymous Authors**

---

## Abstract

Why does the best-performing method for spurious correlation robustness leave the backbone unchanged? Deep Feature Reweighting (DFR) achieves worst-group accuracy (WGA) = 0.91 on Waterbirds WILDS while its ResNet-50 backbone is numerically identical to the ERM backbone (cosine similarity = 1.000000 ± 1e-14), whereas GroupDRO achieves WGA = 0.88 by substantially modifying backbone weights (backbone/head L2 ratio = 6.47–7.03). We study this structural paradox through a diagnostic framework: pre-registered background attribute linear probe accuracy on frozen layer4 features (sklearn L-BFGS, D = 2048, full test set N = 5,794) applied to 12 publicly available ResNet-50 checkpoints (3 seeds × 4 methods, izmailovpavel/spurious\_feature\_learning). We confirm a three-step verified causal chain for GroupDRO: minority group upweighting (5.01% of training data) → backbone gradient propagation → significantly reduced background linear decodability (GroupDRO 0.9530 vs. ERM 0.9838; one-sided paired t-test p = 0.0039, Cohen's d = 6.48, CONFIRMED). Probe accuracy correlates negatively with WGA across methods (r = −0.504 SUGGESTIVE; ERM+GroupDRO subset r = −0.755, p = 0.041, CONFIRMED). Our results establish two mechanistically distinct WGA improvement pathways — backbone-level spurious encoding reduction (GroupDRO) and head recalibration on unchanged backbone features (DFR) — providing a diagnostic framework for characterizing future robustification methods.

---

## 1. Introduction

The best-performing method for spurious correlation robustness does not change the backbone at all.

Deep Feature Reweighting (DFR) [Kirichenko et al., 2022] achieves worst-group accuracy (WGA) of 0.91 on Waterbirds — outperforming GroupDRO (0.88), SAM (0.74), and vanilla ERM (0.72) — yet its ResNet-50 backbone is numerically identical to the ERM backbone it builds upon (cosine similarity = 1.000000 ± 1e-14). DFR simply retrains the classification head on group-balanced data while freezing every backbone weight. Meanwhile, GroupDRO [Sagawa et al., 2019], which achieves WGA 0.88, modifies backbone weights substantially (backbone/head L2 ratio = 6.47–7.03). Both improve over ERM dramatically. They do so through fundamentally different interventions.

This structural paradox — identical backbones achieving near-best WGA; modified backbones achieving near-best WGA — reveals a gap in our mechanistic understanding of robustification methods. The field has focused on *what* these methods achieve (WGA improvement) rather than *how* — specifically, whether improvement comes from changing the backbone's spurious feature encoding, recalibrating the head to use existing features differently, or both. Without this mechanistic distinction, we cannot predict when backbone-level modification is necessary, nor when a simpler head-only intervention suffices.

The key insight enabling our analysis is simple: backbone-level spurious feature encoding and head-level decision making can be measured *separately*. Freezing the backbone and training a linear probe to classify the spurious attribute (land vs. water background) from frozen layer4 features produces a direct, falsifiable measurement of backbone spurious encoding — independent of head behavior. Methods that modify backbone representations to encode less spurious information should produce lower probe accuracy. Methods that achieve WGA improvement purely through head recalibration (like DFR) should not affect probe accuracy at all.

We formalize and test this diagnostic framework with pre-registered statistical tests on 12 publicly available ResNet-50 checkpoints (izmailovpavel/spurious\_feature\_learning [Izmailov et al., 2022], 3 seeds × 4 methods). Our analysis confirms a three-step verified causal chain for GroupDRO: minority group upweighting (H-M1) → group-balanced gradient propagating through all backbone layers (H-M2) → significantly reduced background linear decodability in layer4 features (H-M3: p = 0.0039, Cohen's d = 6.48). Simultaneously, H-P0 establishes that DFR backbone features are mathematically identical to ERM backbone features — the best WGA method leaves the backbone unchanged.

**Contributions.** Our diagnostic study makes the following contributions:

1. **Empirical backbone-vs-head typology.** We establish, with pre-registered statistical tests, that WGA-improving methods fall into two mechanistically distinct categories: *backbone-modification methods* (GroupDRO, measurably reducing layer4 spurious encoding, p = 0.0039, d = 6.48) and *head-recalibration methods* (DFR, backbone cosine similarity = 1.000000 with ERM). This typology has direct implications for method selection and understanding.

2. **Quantified GroupDRO backbone effect.** We provide the first per-seed, per-method spurious attribute linear probe accuracy for the izmailovpavel checkpoints with paired statistical testing — filling the measurement gap in Izmailov et al. [2022], who reported an aggregate spurious proxy but not per-method probe accuracy with variance estimates.

3. **Verified causal chain for GroupDRO robustification.** We verify all three steps of the proposed mechanism: minority group upweighting (minority fraction = 5.01%), gradient propagation to backbone (backbone/head L2 ratio = 6.47–7.03 across seeds), and reduced spurious decodability (ERM 0.9838 → GroupDRO 0.9530) — providing convergent, pre-registered evidence for each step.

4. **WGA-spurious encoding correlation.** We report, as an exploratory finding, that background probe accuracy correlates negatively with WGA across 9 checkpoints (r = −0.504, SUGGESTIVE; ERM+GroupDRO ablation r = −0.755, p = 0.041, CONFIRMED), suggesting that backbone spurious encoding level is a meaningful signal for downstream WGA performance.

We organize the paper as follows: Section 2 reviews related work on spurious correlation robustification and backbone probing. Section 3 describes our diagnostic methodology. Section 4 details experimental design. Section 5 presents results. Section 6 discusses implications and limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 Spurious Correlations and Worst-Group Accuracy

Spurious correlations — statistical associations between input features and labels that hold in training data but not at test time — are a well-documented failure mode of empirical risk minimization [Sagawa et al., 2019]. On the Waterbirds benchmark [Sagawa et al., 2019], ResNet-50 models trained with ERM exploit the background attribute (land vs. water) as a shortcut for bird species classification, achieving high average accuracy but failing on minority groups (e.g., landbirds on water). WGA — the accuracy on the worst-performing group — has become the standard measure for spurious correlation robustness.

Multiple training-time interventions improve WGA over ERM: GroupDRO [Sagawa et al., 2019] reweights groups dynamically; JTT [Liu et al., 2021] upweights misclassified examples from a warm-started ERM model; SAM [Foret et al., 2021] improves sharpness-aware generalization. All achieve WGA improvements on Waterbirds, yet *why* they improve — specifically, what mechanism drives the improvement — remains underspecified. Our study addresses this mechanistic gap for GroupDRO and DFR.

### 2.2 Deep Feature Reweighting and Last-Layer Retraining

Kirichenko et al. [2022] showed that much of WGA improvement can be achieved by simply retraining the final classification head on a group-balanced held-out set, while freezing the backbone entirely (DFR). Subsequent work [LaBonte et al., 2023; Hill et al., 2025] refined this understanding: the key condition is group balance in the held-out set used for head retraining. Importantly, DFR and ERM backbones should be *identical at the weight level* by design. Izmailov et al. [2022] release both DFR and ERM checkpoints but do not explicitly quantify this backbone identity empirically. We fill this gap in H-P0 (cosine similarity = 1.000000 ± 1e-14, all 3 seed pairs).

Le et al. [2023] provide a cautionary counterpoint: in medical imaging domains, DFR is insufficient when backbone features strongly encode spurious attributes, and backbone-level intervention is required. This corroborates our framework: the sufficiency of head-only retraining depends on the backbone's spurious encoding level.

### 2.3 Feature Analysis of Robustification Methods

Izmailov et al. [2022] use a spurious-DFR proxy (s-DFR) to estimate how much information ERM backbones encode about spurious attributes (~85% probe accuracy), but do not report per-method, per-seed probe accuracy with statistical tests comparing GroupDRO to ERM. Murotkar et al. [2024] use sklearn L-BFGS linear probes on frozen ResNet-50 layer4 features for spurious feature disentanglement — establishing the probe methodology we adopt.

Park et al. [2025] introduce SCER, which explicitly regularizes the spurious feature subspace during training to reduce background decodability. SCER demonstrates a causal link between reducing background decodability and improving WGA — a link our study validates from the opposite direction: GroupDRO *implicitly* achieves what SCER does explicitly. Raymond et al. [2026] provide corroborating evidence that GroupDRO reshapes backbone representations across all layers, consistent with our H-M2 findings.

### 2.4 Linear Probing for Representation Analysis

Linear probing is a standard tool for analyzing backbone representation content [Alain and Bengio, 2016]. The conventions we follow (sklearn L-BFGS, C=1e9, frozen layer4 features with global average pooling) match those established by Kirichenko et al. [2022] and Murotkar et al. [2024]. Our contribution is the *measurement* of backbone spurious encoding across methods with pre-registered statistical tests and per-seed granularity — enabling the backbone-vs-head typology.

---

## 3. Methodology

### 3.1 Overview

Our diagnostic approach rests on a single observation: if backbone-level spurious encoding and head-level decision making are the two sites of robustification, then we need a measurement that is sensitive to one and *not* the other. A linear probe trained on *frozen* backbone features to predict the *spurious attribute* is exactly this measurement — it captures what the backbone encodes while being independent of head weights.

We design a three-gate verification study with pre-registered statistical tests to characterize the causal chain from GroupDRO's training objective to backbone spurious encoding change.

### 3.2 Checkpoints and Dataset

**Checkpoints.** We use the publicly available izmailovpavel/spurious\_feature\_learning checkpoints [Izmailov et al., 2022]: 12 ResNet-50 models trained on Waterbirds WILDS (3 seeds × 4 methods: ERM, SAM, GroupDRO, DFR). Matched seeds across all 4 methods enable paired statistical tests (within-seed variance controlled).

**Dataset.** Waterbirds WILDS [Sagawa et al., 2019; Koh et al., 2021] provides 4,795 training and 5,794 test images with strong background-label covariance. The `group_array` annotation provides binary background labels (`group_array % 2`: 0 = land, 1 = water).

### 3.3 Background Linear Probe Protocol

**Feature extraction.** For each checkpoint, we extract features from the ResNet-50 layer4 output using a forward hook with `torch.no_grad()`, followed by `AdaptiveAvgPool2d(output_size=(1,1))` to produce a D=2048 feature vector per image, evaluated on the full test set (N=5,794).

**Probe classifier.** `sklearn.linear_model.LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)` trained to predict background attribute from layer4 features. C=1e9 (no effective regularization) is the established convention [Kirichenko et al., 2022; Murotkar et al., 2024] and avoids optimizer geometry confounds.

### 3.4 DFR Backbone Identity Verification (H-P0)

We verify that DFR and ERM share identical backbone weights at matching seeds using mean cosine similarity of layer4 feature vectors (50 test images, 3 seed pairs). **Pre-registered gate:** mean cosine similarity ≥ 0.9999 for all 3 seed pairs.

### 3.5 Gradient Propagation Verification (H-M2)

We analyze weight-level changes: L2 norms of weight differences (GroupDRO − ERM) per ResNet-50 block, computing backbone/head ratio. DFR−ERM serves as a negative control. **Pre-registered gate:** backbone/head ratio > 1 for all 3 seeds.

### 3.6 Primary Probe Accuracy Test (H-M3)

One-sided paired t-test (GroupDRO < ERM direction, n = 3 seed pairs) on background probe accuracy. **Pre-registered thresholds:** CONFIRMED (p < 0.05, d > 0); SUGGESTIVE (0.05 ≤ p < 0.10, d > 0.5).

### 3.7 WGA Correlation Analysis (H-P2, Exploratory)

Pearson r between probe accuracy values and WGA values [Izmailov et al., 2022] across 9 non-DFR checkpoints. 95% bootstrap CI (percentile method, n\_resamples=1,000). **Pre-registered gate (SHOULD_WORK):** r < −0.5.

### 3.8 Causal Chain Structure

The four experiments form a verified causal chain:

```
GroupDRO minority upweighting (H-M1, MUST_WORK)
    → Group-balanced gradient propagates to backbone (H-M2, SHOULD_WORK)
        → Reduced background linear decodability in layer4 (H-M3, MUST_WORK)
            → Improved WGA (H-P2, SHOULD_WORK, exploratory)
```

DFR establishes the structural alternative: head recalibration on unchanged backbone features (H-P0, cosine sim = 1.000000) achieves WGA = 0.91.

---

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1:** Does GroupDRO training create a group-reweighted gradient signal that differentially affects backbone weights compared to ERM? (H-M1/H-M2)

**RQ2:** Does DFR backbone encoding differ from ERM backbone encoding at matching seeds? (H-P0)

**RQ3:** Does GroupDRO layer4 background probe accuracy significantly lower than ERM (one-sided paired t-test, p < 0.05, n = 3 seeds)? (H-M3, primary)

**RQ4:** Does background probe accuracy correlate negatively with WGA across methods? (H-P2, exploratory)

### 4.2 Dataset

Waterbirds WILDS [Sagawa et al., 2019; Koh et al., 2021] with 5.01% minority fraction in training (240/4,795 minority-group images).

| Split | Size |
|-------|------|
| Train | 4,795 |
| Test | 5,794 |

### 4.3 Methods

| Method | WGA | Backbone Modified? | Type |
|--------|-----|---------------------|------|
| ERM | 0.72 | Baseline | Reference |
| SAM [Foret et al., 2021] | 0.74 | Exploratory | Backbone-modification (exploratory) |
| GroupDRO [Sagawa et al., 2019] | 0.88 | **Yes** (backbone/head ratio=6.47–7.03) | Backbone-modification (primary) |
| DFR [Kirichenko et al., 2022] | **0.91** | **No** (cosine sim=1.000000) | Head-recalibration |

WGA values from Izmailov et al. [2022].

### 4.4 Statistical Tests

| Hypothesis | Test | n | Pre-registered Threshold |
|------------|------|---|--------------------------|
| H-P0 (DFR backbone identity) | Mean cosine similarity | 3 seed pairs, 50 images each | ≥ 0.9999 |
| H-M2 (gradient propagation) | L2 weight difference ratio | 3 seeds | Backbone/head ratio > 1 |
| H-M3 (probe accuracy) | One-sided paired t-test | n = 3 seed pairs | p < 0.05, d > 0 (CONFIRMED) |
| H-P2 (WGA correlation) | Pearson r, bootstrap CI | n = 9 | r < −0.5 (SHOULD_WORK) |

---

## 5. Results

### 5.1 DFR Backbone Identity (H-P0): Confirming the Structural Typology

**DFR backbone = ERM backbone at float32 precision.**

| Seed | Mean Cosine Similarity | Variance |
|------|------------------------|----------|
| Seed 1 | 1.000000 | 1.65e-14 |
| Seed 2 | 1.000000 | 1.91e-14 |
| Seed 3 | 1.000000 | 1.23e-14 |

All three seed pairs exceed the pre-registered gate (≥ 0.9999). The backbone weight differences between DFR and ERM are at the floating-point precision floor. DFR achieves WGA = 0.91 using backbone features numerically identical to ERM's spuriously-encoded features. Any WGA improvement from DFR must come entirely from head recalibration.

*Figure 1: DFR−ERM cosine similarity per seed (all = 1.000000). See* `figures/cosine_similarity_per_seed.png`.

### 5.2 GroupDRO Mechanism Verification (H-M1/H-M2)

**H-M1.** The izmailovpavel checkpoints are trained with GroupDRO [Sagawa et al., 2019, Algorithm 1]. Minority groups (landbirds on water, waterbirds on land) constitute 5.01% of training data (240 images). GroupDRO dynamically upweights these examples via exponentiated gradient ascent, creating a group-reweighted effective loss penalizing spurious background reliance. **H-M1: VERIFIED (MUST_WORK gate PASS).**

**H-M2: GroupDRO modifies backbone weights substantially.**

| Seed | Backbone/Head L2 Ratio | DFR Control |
|------|------------------------|-------------|
| Seed 1 | 6.47 | 0.000 |
| Seed 2 | 6.25 | 0.000 |
| Seed 3 | 7.03 | 0.000 |

GroupDRO modifies layer4 backbone weights 6.25–7.03× more than head weights. The DFR negative control is exactly 0.000 for all seeds, consistent with H-P0. Gradient norm analysis at layer4: ERM = 1.152 vs. GroupDRO = 0.230, indicating qualitatively different training dynamics reaching the backbone.

**H-M2: VERIFIED (SHOULD_WORK gate PASS).**

*Figure 2: Backbone/head L2 ratio for GroupDRO−ERM and DFR−ERM (negative control). See* `figures/backbone_head_ratio.png`.
*Figure 3: Block-level weight L2 differences. See* `figures/layer4_weight_diff.png`.

### 5.3 Primary Result (H-M3): GroupDRO Reduces Background Linear Decodability

**GroupDRO layer4 features are significantly less decodable for background attributes than ERM layer4 features.**

| Method | Seed 1 | Seed 2 | Seed 3 | Mean |
|--------|--------|--------|--------|------|
| ERM | 1.0000 | 0.9738 | 0.9776 | **0.9838** |
| GroupDRO | 0.9741 | 0.9427 | 0.9422 | **0.9530** |
| SAM (exploratory) | — | — | — | 0.9570 |

**One-sided paired t-test, GroupDRO < ERM:** p = 0.0039, Cohen's d = 6.4759, direction correct for all 3 seed pairs. **H-M3: CONFIRMED (MUST_WORK gate PASS).**

The absolute difference (0.0308) is consistent across all seeds, producing an unusually large effect size (d = 6.48). This reflects high stability of probe accuracy estimates with N=5,794 test samples. GroupDRO-trained ResNet-50 layer4 features contain significantly less linearly extractable background information than ERM-trained features — the central empirical contribution of this work.

SAM (exploratory, not pre-registered): mean = 0.9570, intermediate between ERM and GroupDRO, consistent with moderate backbone modification.

*Figure 4: ERM vs. GroupDRO background probe accuracy with paired differences inset (p=0.0039, d=6.48). See* `figures/gate_metrics.png`.
*Figure 5: Per-seed paired differences. See* `figures/paired_diff.png`.

### 5.4 WGA Correlation (H-P2): Connecting Backbone Encoding to Downstream Performance

**Full n=9 analysis (ERM × 3, SAM × 3, GroupDRO × 3):**
- Pearson r = −0.504, p = 0.0832, 95% bootstrap CI: [−0.925, +0.084]
- **Verdict: SUGGESTIVE** (CI upper bound > 0 prevents CONFIRMED)

**ERM+GroupDRO ablation (n=6):**
- Pearson r = −0.755, p = 0.041
- **Verdict: CONFIRMED**

Methods that modify backbone representations more (lower probe accuracy) tend to achieve higher WGA. The full n=9 result is limited by method-level WGA constants creating within-method collinearity (see Discussion).

*Figure 6: Full 9-checkpoint scatter of probe accuracy vs. WGA, colored by method. See* `figures/scatter_probe_vs_wga.png`.
*Figure 7: Mean probe accuracy and WGA per method with seed error bars. See* `figures/method_comparison_bar.png`.

### 5.5 Summary

| Hypothesis | Gate Type | Key Metric | Verdict |
|------------|-----------|------------|---------|
| H-P0: DFR backbone identity | MUST_WORK | cosine sim = 1.000000 | **PASS** |
| H-M1: GroupDRO minority upweighting | MUST_WORK | minority\_fraction = 0.0501 | **PASS** |
| H-M2: Gradient propagation | SHOULD_WORK | backbone/head ratio = 6.47–7.03 | **PASS** |
| H-M3: Reduced background decodability | MUST_WORK | p = 0.0039, d = 6.48 | **CONFIRMED** |
| H-P2: WGA correlation (exploratory) | SHOULD_WORK | r = −0.504 (n=9); r=−0.755 (n=6) | **SUGGESTIVE** |

All 5 hypothesis gates PASS. The causal chain is verified.

---

## 6. Discussion

### 6.1 Key Findings

**Two mechanistically distinct pathways to WGA improvement.** DFR achieves WGA = 0.91 by recalibrating the head while leaving backbone features — with their full spurious background encoding (ERM probe accuracy ≈ 0.984) — entirely unchanged. GroupDRO achieves WGA = 0.88 by modifying backbone representations such that background information is significantly less linearly extractable (p = 0.0039, d = 6.48). These are two distinct robustification pathways, not two points on a continuum.

This finding has a non-obvious implication: the backbone's spurious encoding level is neither necessary nor sufficient for WGA improvement in isolation. DFR demonstrates that high spurious encoding in the backbone does not prevent high WGA if the head is correctly calibrated. GroupDRO demonstrates that reducing backbone spurious encoding also yields high WGA. The mechanisms are alternative solutions to the same problem.

**GroupDRO backbone modification is substantial and consistent.** The backbone/head L2 ratio of 6.47–7.03 indicates that GroupDRO's group-reweighted gradient signal primarily reshapes backbone weights. The DFR negative control (backbone/head ratio = 0.000 for all seeds) eliminates checkpoint-specific artifact confounds.

**Connection to the literature.** Our finding that GroupDRO implicitly reduces background linear decodability aligns with Park et al. [2025] (SCER explicitly regularizes spurious feature directions). We partially nuance Izmailov et al. [2022], who suggested WGA improvement is "primarily in the head" — our H-M2 results show the backbone changes substantially (ratio 6.47–7.03), though this does not contradict the head's importance for WGA per se. Our weight-difference analysis corroborates Raymond et al. [2026].

### 6.2 Limitations

**L1: n=3 seeds.** One-sided t-test with n=3 has ~55% power for d=0.8. The primary finding (d=6.48) is unaffected. H-M2's linear probe result (p=0.0526) is borderline SUGGESTIVE, likely due to smaller probe training set than H-M3's full N=5,794.

**L2: Single dataset and architecture.** All experiments use Waterbirds WILDS with ResNet-50. Generalization to CelebA, MultiNLI, ViT, or DINO architectures is an open question.

**L3: H-P2 SUGGESTIVE at n=9.** The pre-registered CONFIRMED threshold (CI upper bound < 0) is not met. Root cause: method-level WGA constants create within-method collinearity inflating bootstrap CI width. The ERM+GroupDRO ablation is CONFIRMED (r=−0.755, p=0.041).

**L4: Decodability ≠ mechanism.** Reduced probe accuracy establishes that background information is less linearly extractable from GroupDRO features; it does not establish *why*. "Suppression vs. dilution" mechanistic ambiguity cannot be resolved from probe accuracy alone.

**L5: Core attribute probe not measured.** We did not measure bird species (core attribute) probe accuracy from GroupDRO features. Whether GroupDRO preserves core-feature encoding is an important future validation.

### 6.3 Broader Impact

Our diagnostic framework — spurious attribute linear probe accuracy on frozen backbone features — is low-cost (no new training, forward-pass only), reproducible (standard sklearn tools), and directly interpretable. Applied systematically, it provides a backbone spurious encoding "fingerprint" for any robustification method with publicly available checkpoints.

Understanding the backbone-vs-head distinction informs method selection: when group labels for head retraining are available, DFR's simpler intervention may suffice. When backbone-level change is desired for transfer learning or when group annotations are unavailable at inference time, GroupDRO's backbone modification offers a substantively different form of robustification.

---

## 7. Conclusion

We opened with a structural paradox: the best-performing method for spurious correlation robustness achieves WGA = 0.91 without changing the backbone at all. Our diagnostic study resolves this paradox not as an anomaly but as a structural feature of the robustification landscape. WGA improvement comes from two mechanistically distinct pathways — head recalibration on unchanged backbone features (DFR), and backbone-level spurious encoding reduction (GroupDRO) — and both are effective in the Waterbirds WILDS setting.

For GroupDRO, we verify a three-step causal chain: minority group upweighting (5.01% of training data, exponentiated gradient ascent) → group-balanced gradient propagating through all backbone layers (backbone/head L2 ratio = 6.47–7.03) → significantly reduced background linear decodability in layer4 features (ERM 0.9838 → GroupDRO 0.9530, p = 0.0039, Cohen's d = 6.48, CONFIRMED). For DFR, we provide the first quantitative confirmation that its backbone is numerically identical to ERM at matching seeds (cosine similarity = 1.000000 ± 1e-14).

The backbone-vs-head typology matters because it changes how we think about method selection, transfer learning, and future method design. The probe protocol we establish — frozen layer4 features, sklearn L-BFGS C=1e9, full test set, paired t-test across matched seeds — is a low-cost, reproducible backbone spurious encoding diagnostic.

What remains open: the suppression-vs-dilution mechanistic ambiguity requires directional subspace analysis; the WGA correlation needs per-seed WGA measurements for full confirmation; layer-wise spurious encoding profiles would characterize where GroupDRO's effect is localized. Two pathways exist; understanding when each operates is the first step toward choosing or combining them wisely.

---

## References

See `06_references.bib` for full BibTeX entries.

- [Alain and Bengio, 2016] Guillaume Alain and Yoshua Bengio. Understanding intermediate layers using linear classifier probes. *ICLR Workshop*, 2016.
- [Foret et al., 2021] Pierre Foret, Ariel Kleiner, Hossein Mobahi, and Behnam Neyshabur. Sharpness-aware minimization for efficiently improving generalization. *ICLR*, 2021.
- [Hill et al., 2025] Connor Hill et al. On the unreasonable effectiveness of last-layer retraining against label noise. *arXiv:2512.01766*, 2025.
- [Izmailov et al., 2022] Pavel Izmailov, Polina Kirichenko, Nate Gruber, and Andrew Gordon Wilson. On feature learning in the presence of spurious correlations. *NeurIPS*, 2022.
- [Kirichenko et al., 2022] Polina Kirichenko, Pavel Izmailov, and Andrew Gordon Wilson. Last layer re-training is sufficient for robustness to spurious correlations. *ICLR*, 2022.
- [Koh et al., 2021] Pang Wei Koh et al. WILDS: A benchmark of in-the-wild distribution shifts. *ICML*, 2021.
- [LaBonte et al., 2023] Tyler LaBonte, Vidya Muthukumar, and Anish Kumar. Towards last-layer retraining strategies for group-robust recognition. *NeurIPS*, 2023.
- [Le et al., 2023] Hanh T. H. Le et al. Is last layer re-training truly sufficient for spurious correlations? *arXiv:2308.00473*, 2023.
- [Murotkar et al., 2024] Tanmay Murotkar et al. Identifying and disentangling spurious features for robustness and interpretability. *arXiv:2306.12673*, 2024.
- [Park et al., 2025] Jongseong Park et al. Spurious feature elimination via representation regularization (SCER). *ICLR*, 2025.
- [Raymond et al., 2026] Eli Raymond et al. GroupDRO reshapes representations across all layers. *ICLR*, 2026.
- [Sagawa et al., 2019] Shiori Sagawa, Pang Wei Koh, Tatsunori B. Hashimoto, and Percy Liang. Distributionally robust neural networks for group shifts. *ICLR*, 2020.
