# Discussion

## Key Findings

Our experiments reveal a surprising inversion of the hypothesized relationship between spectral estimator variance and model quality.

**Finding 1: CV\_PR positively correlates with accuracy (r = +0.61).**

The original mechanism — flat spectra lead to stable SVD estimates, which indicate smooth loss landscapes enabling generalization — is contradicted. If anything, the relationship runs in the opposite direction: models with higher accuracy exhibit *more* variance in participation ratio across random projections. This suggests either confounding by model complexity or that spectral diversity (not stability) accompanies quality.

**Finding 2: The extraction methodology is reliable.**

100% completion across 100 diverse models, with CV\_PR values consistently finite and in a narrow range [0.001, 0.033], validates that randomized SVD with 20 seeds produces meaningful variance estimates. The methodology is sound; the theoretical interpretation was wrong.

**Finding 3: Negative results have value.**

The decisive falsification (r = +0.61 vs predicted r < -0.3) redirects research away from the stability-as-quality assumption. Rather than pursuing mechanism hypotheses predicated on negative correlation, future work should investigate *why* higher variance accompanies better models.

## Limitations

**Limitation 1: Confounding by model size not controlled.**

Larger models tend to have higher accuracy *and* potentially more spectral diversity. Without partial correlation controlling for parameter count, we cannot determine whether CV\_PR has independent predictive value or merely proxies model size.

*Why acceptable:* This was designed as an existence test (MUST\_WORK gate). The purpose was to establish whether the correlation exists and in which direction, not to fully characterize causal mechanisms.

*Future mitigation:* Compute partial\_corr(CV\_PR, accuracy | param\_count). If r drops to ~0, confounding is confirmed. If r remains significant, CV\_PR captures something beyond size.

**Limitation 2: Mechanism hypotheses blocked.**

The MUST\_WORK failure on h-e2 blocked dependent hypotheses (h-m1: partial correlation after controlling condition number; h-m2: within-family correlation). The mechanism for why CV\_PR relates to accuracy remains unknown.

*Why acceptable:* Proper gate enforcement prevents wasted effort on mechanism validation when the existence claim fails in its original form.

*Future mitigation:* Reformulate hypothesis with positive correlation, then run mechanism tests.

**Limitation 3: Limited architecture stratification.**

While we included multiple families (ResNet, ViT, EfficientNet, ConvNeXt, etc.), we did not analyze within-family vs cross-family correlation patterns. The relationship may differ by architecture type.

*Why acceptable:* The 94-model sample was designed for aggregate correlation, not fine-grained stratification.

*Future mitigation:* Architecture-specific analysis with larger per-family samples (≥20 models each).

## Broader Impact

**Positive impacts:** This work contributes to rigorous hypothesis testing in machine learning research. Negative results that reveal unexpected phenomena guide the field away from unproductive assumptions. The falsification provides a concrete starting point for reformulated hypotheses.

**Potential concerns:** Misinterpretation of our results could lead practitioners to believe "higher CV\_PR is good" as a selection criterion. We caution that the observed correlation may be spurious (driven by confounding) and should not be used for model selection without controlling for model size.

**Mitigation:** We explicitly state the confounding concern and recommend partial correlation analysis before any practical application.
