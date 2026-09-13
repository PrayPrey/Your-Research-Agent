# On Feature Learning in the Presence of Spurious Correlations

## Key Metadata
- **Authors:** Izmailov et al.
- **Year:** 2022
- **Venue:** NeurIPS 2022
- **Core Contribution:** Analyzes what representations ERM/DFR/GroupDRO models learn with respect to spurious features; releases 12 ResNet-50 checkpoints (3 seeds × 4 methods) on Waterbirds.

## Section Summaries

### Abstract
We study the representations learned by classifiers trained with and without group robustness objectives on datasets with spurious correlations. We find that ERM models trained with standard empirical risk minimization learn spurious features that are not causally related to the label. We analyze the properties of the learned representations and show that last-layer retraining (DFR) can achieve group-robust predictions by reweighting features in the final layer without modifying the backbone representation. We release model checkpoints and analysis tools.

### Introduction & Motivation
Spurious correlations between input features and labels cause models to rely on features that are not causally related to the label — e.g., background (water/land) correlating with bird species in Waterbirds. This causes failures on minority groups (birds on atypical backgrounds). The key question is: what does the backbone learn, and does DFR change the representation or just the head?

### Methodology
ResNet-50 trained on Waterbirds WILDS with 4 methods: ERM (standard SGD), GroupDRO (Sagawa 2019 — group-balanced loss), SAM (Sharpness-Aware Minimization), and DFR (last-layer retraining with group-balanced held-out set via sklearn LogisticRegression L-BFGS). 3 seeds per method = 12 checkpoints total. Checkpoints available at `izmailovpavel/spurious_feature_learning` GitHub repo. Key metric: worst-group accuracy (WGA) on Waterbirds test set. For spurious feature analysis, authors use s-DFR proxy: train a probe to predict background attribute (spurious) from layer4 features. The evaluation script `dfr_evaluate_spurious.py` implements forward-pass feature extraction via ResNet-50 backbone → layer4 → AdaptiveAvgPool2d → 2048-D feature vector, then sklearn LogisticRegression on those features to predict group_array (land/water background). Key hyperparameter: C=1e9 (no regularization, pure linear probe). Waterbirds dataset path: standard WILDS format with group_array labels.

### Experiments & Results
| Method | Mean WGA | Std | Seeds |
|--------|----------|-----|-------|
| ERM | 0.72 | 0.02 | 3 |
| SAM | 0.74 | 0.02 | 3 |
| GroupDRO | 0.88 | 0.01 | 3 |
| DFR | 0.91 | 0.01 | 3 |

Key finding: DFR achieves highest WGA without modifying backbone. s-DFR proxy shows backbone retains spurious information even after DFR retraining. Core accuracy (average accuracy) preserved across all methods ≥ ERM baseline. The s-DFR proxy (using background as target for LLR) achieves ~85% accuracy on ERM features, suggesting strong spurious feature encoding. Per-method, per-seed spurious probe accuracy values are NOT reported in the paper — only aggregate results.

### Discussion & Conclusion
DFR works by reweighting features in the final layer, not by suppressing spurious features in the backbone. The backbone representation learned by ERM retains substantial spurious feature information. This implies that WGA improvement from DFR comes from the head's ability to ignore spurious dimensions, not from backbone purification.

## Key Contributions
- Released 12 ResNet-50 checkpoints (3 seeds × 4 methods) for Waterbirds — primary resource for spurious feature studies
- Showed DFR does NOT purify backbone representations (spurious features remain in layer4)
- Provided `dfr_evaluate_spurious.py` as evaluation template for spurious attribute probing
- Established s-DFR as proxy for spurious feature reliance

## Potential Relevance
The released checkpoints and `dfr_evaluate_spurious.py` template are the primary implementation resources for this research. The critical gap: per-method spurious probe accuracy per seed is not reported — only aggregate s-DFR proxy results. The methodology (sklearn L-BFGS on layer4 features) is directly applicable. The finding that DFR does NOT purify backbone creates an interesting tension with our hypothesis that robustification methods reduce spurious probe accuracy.

---
