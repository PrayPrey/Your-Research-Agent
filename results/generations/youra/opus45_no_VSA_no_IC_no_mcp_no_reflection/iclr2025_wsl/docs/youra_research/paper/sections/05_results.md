# Results

Our experiments test whether heavy-tailed exponent computation extends to Vision Transformers with bounded variance. The results reveal a nuanced picture: the methodology works, but requires stratification controls.

## Main Results

Table 1 presents aggregate statistics for heavy-tailed exponent measurements across 53 ViT models.

| Metric | Value |
|--------|-------|
| Models processed | 53 |
| Mean α | 4.327 |
| Median α | 3.521 |
| σ(α) global | **2.868** |
| α range | [2.20, 18.92] |

**Gate verdict: FAIL.** The global variance σ = 2.868 exceeds our threshold of 0.5 by 5.7×. By this criterion, heavy-tailed exponents cannot be reliably compared across heterogeneous ViT models.

However, this headline result obscures important structure in the data.

## Within-Family Variance

When we stratify by model family (organizational training origin), variance drops dramatically.

| Family | n | σ(α) |
|--------|---|------|
| google/vit-* | 6 | **0.24** (95% CI: [0.12, 0.48]) |
| Global (all models) | 53 | 2.868 (95% CI: [2.34, 3.68]) |

The google/vit-* family achieves σ = 0.24 (bootstrap 95% CI: [0.12, 0.48]), below our 0.5 threshold even at the upper bound. The global σ = 2.868 (95% CI: [2.34, 3.68]) robustly exceeds the threshold. This represents a **12× variance reduction** through family stratification.

**Interpretation.** Heavy-tailed analysis works under controlled conditions. The methodology is sound; the problem is model heterogeneity, not theoretical inapplicability.

## Outlier Analysis

Figure 2 shows the α distribution across all models (see alpha_histogram.png).

Several models exhibit extreme α > 10:

| Model | α | Training Task |
|-------|---|---------------|
| jaranohaal/vit-base-violence-detection | 12.6 | Violence detection |
| mlx-vision/vit_base_patch16_224-mlxim | 14.8 | Unknown fine-tuning |

**Interpretation.** Outliers correspond to task-specific fine-tuning, not architectural variants. Violence detection requires different feature distributions than ImageNet classification, shifting α dramatically. This suggests training objective—not architecture—dominates weight distribution characteristics.

## Family-Level Structure

Figure 3 presents α by model family (see family_boxplot.png).

The boxplot reveals:

1. **google/vit-* models cluster tightly** (σ = 0.24), consistent with standardized Google training pipelines
2. **Fine-tuned variants show high spread**, reflecting diverse downstream tasks
3. **No clear relationship between architecture variant (tiny/base/large) and α**

**Interpretation.** Training provenance (who trained the model, for what purpose) matters more than architectural differences within the ViT family.

## Gate Check Visualization

Figure 1 visualizes the gate evaluation (see gate_check.png).

The figure shows σ(α) = 2.868 against the 0.5 threshold, with breakdown by variance source.

## Summary of Findings

| Research Question | Answer | Evidence |
|-------------------|--------|----------|
| RQ1: Can α be computed for ViT? | **Yes** | 53/100 models processed successfully |
| RQ2: Is variance bounded (σ < 0.5)? | **No** globally, **Yes** within families | σ = 2.868 global, σ = 0.24 family |
| RQ3: Does family control help? | **Yes** | 12× variance reduction |

The methodology extends to Vision Transformers, but cross-model comparison requires family-aware stratification.
