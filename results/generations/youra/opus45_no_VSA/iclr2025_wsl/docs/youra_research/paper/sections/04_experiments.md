# Experimental Setup

We design experiments to answer two research questions:

**RQ1 (Feasibility):** Can CV\_PR be reliably extracted from 100+ pretrained models?

**RQ2 (Correlation):** Does CV\_PR correlate negatively with ImageNet accuracy?

These map directly to our claims: RQ1 validates the methodology; RQ2 tests the core hypothesis.

## Dataset

We evaluate on models from the timm library (PyTorch Image Models), which provides a unified interface to 1,000+ pretrained architectures with documented ImageNet-1K validation accuracy.

**Model selection criteria:**
- Pretrained on ImageNet-1K
- Top-1 accuracy available in timm metadata
- Architecture families: ResNet, ViT, EfficientNet, ConvNeXt, DenseNet, RegNet, MobileNet

| Statistic | Value |
|-----------|-------|
| Models processed | 100 |
| Models with matched accuracy | 94 |
| Architecture families | 7+ |
| Accuracy range | ~72% – ~88% |

**Rationale:** timm provides sufficient diversity in architecture type and accuracy range to test whether CV\_PR generalizes across model families. The 100-model target ensures adequate statistical power for correlation testing.

## Baselines

For the correlation test (RQ2), we compare against random baseline (null hypothesis: no correlation). For the metric itself, we position against:

**Condition Number:** κ = σ\_max / σ\_min captures spectral extremes but not shape. If CV\_PR reduces to condition number, our metric adds nothing.

**Direct Spectral Features:** Unterthiner et al. [2020] used direct weight statistics. We test whether *variance* of spectral estimates adds signal beyond the estimates themselves.

## Implementation Details

**Framework:** PyTorch 2.0+, timm library for model loading

**Extraction Pipeline:**
1. Load pretrained model via `timm.create_model(name, pretrained=True)`
2. Iterate all Conv2d and Linear layers (≥100 elements)
3. For each weight matrix, compute CV\_PR with 20 seeds
4. Aggregate via mean across layers

**Hyperparameters:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| n\_seeds | 20 | Balance variance estimation vs compute |
| SVD rank | 50 | Sufficient for PR stability |
| Oversampling | 10 | Standard for randomized SVD |
| Seed base | 0 | Reproducibility |

**Compute:** Single NVIDIA GPU, ~2–5 seconds per model for extraction.

**Reproducibility:** Random seeds are fixed (0–19) and torch manual seed is set before each projection. Code available in supplementary materials.

## Evaluation Metrics

**RQ1 (Feasibility):**
- Completion rate: fraction of models successfully processed
- Success criterion: ≥95% completion
- CV\_PR finite range: all values in (0, 10)

**RQ2 (Correlation):**
- Pearson correlation coefficient (r)
- Spearman rank correlation (ρ) — robust to outliers
- 95% confidence interval via bootstrap
- p-value for significance

**Success criterion (original hypothesis):** r < -0.3, p < 0.05
**Falsification criterion:** r ≥ 0 or p ≥ 0.05
