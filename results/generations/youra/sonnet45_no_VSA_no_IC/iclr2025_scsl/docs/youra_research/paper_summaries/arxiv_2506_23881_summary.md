---
paper_id: "2506.23881"
title: "Spurious-Aware Prototype Refinement for Reliable Out-of-Distribution Detection"
authors: "Zohrabi, Hasani, Baghshah, Rohrbach, Rohban"
year: 2025
arxiv_id: "2506.23881"
venue: "NeurIPS 2025"
citations: 4
---

# Paper Summary: SPROD - Spurious-Aware Prototype Refinement for OOD Detection

## Key Contributions

**Core Innovation:** SPROD refines class prototypes (feature centroids) to mitigate bias from spurious features WITHOUT requiring group annotations, hyperparameter tuning, or retraining. Post-hoc method applicable to any pretrained backbone.

**Performance on SP-OOD Benchmarks:**
- **Waterbirds:** AUROC 98.8% (vs 98.6% KNN second-best), FPR@95 2.6% (vs 5.3% second-best)
- **CelebA:** AUROC 92.7% (vs 91.8% MDS second-best)
- **UrbanCars:** AUROC 61.6% (vs 60.4% Relation second-best)
- **Animals MetaCoCo:** AUROC 78.8% (best across all methods)
- **Spurious ImageNet:** AUROC 95.2% (best across all methods)

**Average Improvement:** AUROC +4.8%, FPR@95 -9.4% vs second-best method

**Two OOD Types Defined:**
1. **SP-OOD (Spurious OOD):** Contains spurious features but lacks core features (e.g., grass background without bird)
2. **NSP-OOD (Non-Spurious OOD):** Lacks both spurious AND core features (traditional OOD)

## Methodology

**Problem Setup:**
- Models trained on data with spurious correlations learn decision boundaries biased toward majority groups (e.g., landbird+land, waterbird+water)
- SP-OOD samples share spurious features with ID (e.g., water background) → harder to detect than NSP-OOD
- Minority ID groups (e.g., waterbird+land) get misclassified as OOD due to spurious bias

**Three-Stage SPROD Pipeline:**

**Stage 1: Initial Prototype Construction**
- Compute class centroids μc = mean(features) for each class c
- Uses pretrained feature extractor fθ (ResNet-50, ViT, etc.)
- No modification to backbone weights

**Stage 2: Classification-Aware Prototype Calculation**
- For each training sample i in class c, compute "leave-one-out" prototype: μc,-i = (Nc·μc - hi) / (Nc - 1)
- Classify sample i using nearest prototype distance
- Identify correctly classified vs misclassified samples

**Stage 3: Group Prototype Refinement**
- **Key Insight:** Correctly classified samples form majority groups (rely on spurious features)
- Misclassified samples are minority groups OR samples near decision boundary
- Refine prototypes using ONLY correctly classified samples: μ'c = mean(hi | i correctly classified)
- This pushes prototypes toward core features (invariant across groups) and away from spurious bias

**OOD Scoring:**
- Compute distance to refined prototypes: d(x) = min_c ||fθ(x) - μ'c||
- Higher distance = more likely OOD

**Theoretical Justification:**
- Models trained on spurious correlations learn biased decision boundaries
- Majority groups (with spurious features) achieve higher classification accuracy
- Filtering by correct classification selects samples with core features
- Refined prototypes better represent core class semantics, less affected by spurious correlations

**Key Properties:**
- **Post-hoc:** No retraining required
- **Hyperparameter-free:** No threshold tuning needed
- **No group annotations:** Unsupervised refinement
- **Fast:** Single forward pass through training data
- **General:** Works with any backbone (ResNet, ViT, CLIP)

## Experiments & Results

**Benchmarks:**
- **SP-OOD Datasets:** Waterbirds, CelebA, UrbanCars, Animals MetaCoCo, Spurious ImageNet
- **Traditional OOD:** CIFAR-10/100, ImageNet-1K with near/far-OOD datasets
- **Backbones:** ResNet-50, ViT-B-16, CLIP

**Main SP-OOD Results (Table 2 - ResNet-50):**
| Dataset | SPROD AUROC | Second-Best | Improvement |
|---------|------------|-------------|-------------|
| Waterbirds | 98.8% | 98.6% (KNN) | +0.2pp |
| CelebA | 92.7% | 91.8% (MDS) | +0.9pp |
| UrbanCars | 61.6% | 60.4% (Relation) | +1.2pp |
| Animals MetaCoCo | 78.8% | 77.2% (KNN) | +1.6pp |
| Spurious ImageNet | 95.2% | 92.4% (MDS) | +2.8pp |

**FPR@95 Results (lower = better):**
- Waterbirds: SPROD 2.6% vs KNN 5.3% (50% reduction)
- CelebA: SPROD 22.8% vs MDS 27.8% (18% reduction)
- Average FPR@95 reduction: **9.4%** vs second-best

**Traditional OOD Results (CIFAR-10/100, ImageNet-1K):**
- SPROD maintains competitive performance with state-of-the-art on NSP-OOD datasets
- On CIFAR-10: AUROC 94.2% (vs 95.1% KNN) — small tradeoff for SP-OOD robustness
- On ImageNet-1K: AUROC 89.7% (vs 91.2% ViM)

**Ablation Studies:**
1. **Prototype Refinement Impact:** Refined prototypes (Stage 3) improve Waterbirds AUROC from 90.2% (Stage 1) → 98.8% (+8.6pp)
2. **Backbone Fine-tuning:** Fine-tuning on spurious data helps SP-OOD detection (Waterbirds AUROC 98.8% fine-tuned vs 95.2% frozen)
3. **Low-data Regime:** SPROD maintains 96.5% AUROC on Waterbirds with only 20% training data
4. **Scoring Mechanism:** Distance-based scoring outperforms softmax-based on SP-OOD datasets

## Theoretical Framework

**Why Prototype Refinement Works:**

**Lemma 1 (Classification Accuracy by Group):** Models trained on spurious data achieve higher accuracy on majority groups (core + spurious aligned) than minority groups (core + spurious misaligned).

**Corollary:** Filtering training samples by classification correctness selects majority groups disproportionately.

**Proposition:** Refined prototypes μ'c computed from correctly classified samples are:
1. Closer to core feature representations (invariant across groups)
2. Less biased by spurious feature correlations
3. Better aligned with minority group features

**Intuition:** Majority groups dominate refined prototypes → averaging across majority groups from different classes yields prototypes that capture core features (common to all groups) while canceling out class-specific spurious features (which vary across classes).

**Connection to Spurious Correlation Theory:**
- Core features: causally related to label
- Spurious features: correlated but not causal
- SP-OOD: contains spurious but lacks core → high distance to refined prototypes (correct OOD detection)
- Minority ID: contains core but lacks spurious → moderate distance to refined prototypes (borderline, but improved vs initial prototypes)

## Related Work & Baselines

**19 Post-hoc Methods Compared:**
- **Output-based (5):** MSP, Energy, MLS, KLM, GEN
- **Feature-based (9):** MDS, RMDS, KNN, SHE, NECO, NNGuide, Relation, SCALE, fDBD, NCI
- **Gradient-based (1):** GradNorm
- **Hybrid (3):** ReAct, ViM, ASH

**SPROD vs Feature-based Methods:**
- MDS/RMDS: Use Gaussian class-conditional models, not robust to spurious bias
- KNN: Nearest-neighbor distance, no explicit spurious mitigation
- SPROD: Explicit prototype refinement to remove spurious bias

**SPROD vs Vision-Language (CLIP-based):**
- Zero-shot CLIP methods use text prompts for OOD detection
- SPROD uses visual prototypes only (no text dependency)
- SPROD designed specifically for SP-OOD challenge (CLIP not)

## Implications for Research

**For Spurious Correlation Detection:**
- SPROD detects SP-OOD (contains spurious, lacks core) vs ID (contains core + spurious)
- Directly applicable to spurious correlation scenario: minority groups (lack spurious) may be flagged as OOD-like
- Potential adaptation: Use prototype distances as spurious reliance measure

**For Worst-Group Robustness:**
- Refined prototypes reduce bias toward majority groups
- Could improve worst-group accuracy if used for classification (not just OOD detection)
- Connection to SCER 2025 (embedding regularization): SPROD refinement is a post-hoc form of embedding space correction

**Limitations:**
- Requires training data access for prototype computation (not test-time only)
- Assumes spurious correlations manifest as group structure (majority/minority)
- Performance on UrbanCars (61.6% AUROC) shows method not perfect for multi-spurious scenarios

**Feasibility Advantages:**
- Post-hoc (no retraining)
- Hyperparameter-free (no threshold tuning)
- Fast (single forward pass)
- Works on existing benchmarks (Waterbirds, CelebA)

## Relevance to Selected Research Gap

**Gap 3 (P0): Attribution effectiveness for unknown spurious features**

SPROD is NOT an attribution method, but offers alternative detection approach via prototype refinement. Key takeaways:

1. **Prototype-based detection > attribution-based:** Adebayo 2022 shows attribution fails, SPROD shows prototype refinement succeeds (98.8% AUROC Waterbirds)

2. **Unsupervised spurious mitigation:** No group annotations required — refinement automatically selects majority groups via classification correctness

3. **Post-hoc intervention:** Can be applied after training without modification to model weights

4. **Complementary to GAIA:** GAIA detects OOD via gradient abnormality, SPROD detects via prototype distance. Both post-hoc, both unsupervised.

**Potential Integration with Gradient Methods:**
- GAIA detects abnormality in gradient patterns
- SPROD detects bias in prototype representations
- Combined approach: Use GAIA for gradient-based detection + SPROD for prototype-based detection → ensemble scoring

**Action Items for Hypothesis Design:**
- ⚠️ SPROD targets OOD detection, not direct spurious mitigation (no WGA improvement shown)
- ✅ Prototype refinement idea applicable: refine class representations to reduce spurious bias
- ✅ Classification-based filtering selects majority groups — could be used to identify spurious-reliant samples
- ✅ No group annotations required (aligns with feasibility constraints)
- ❌ Does not provide gradient-based regularization (our core approach), but offers complementary detection method

**Key Insight:** SPROD shows spurious bias CAN be mitigated post-hoc via prototype refinement. Question: Can we combine with gradient regularization for training-time intervention?
