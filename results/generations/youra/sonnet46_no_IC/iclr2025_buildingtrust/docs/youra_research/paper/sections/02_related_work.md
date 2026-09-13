# 2. Related Work

## 2.1 Multi-Dimensional Trustworthiness Evaluation Frameworks

Modern LLM evaluation has progressed from single-task accuracy benchmarks toward comprehensive multi-dimensional assessment. TrustLLM [Sun et al., 2024] provides the most complete current framework, evaluating 16 prominent LLMs across 6 trustworthiness dimensions (truthfulness, safety, fairness, adversarial robustness, privacy, machine ethics) using a suite of sub-benchmarks. HELM [Liang et al., 2022] offers a complementary perspective with 7 metrics (accuracy, calibration, robustness, fairness, bias, toxicity, efficiency) across 30 models. MultiTrust [Zhang et al., 2024] extends the analysis to multimodal LLMs across 5 dimensions. Crucially, all three frameworks present dimension scores and visual radar charts but do not compute the pairwise correlation structure between dimensions or test whether dimensions are statistically independent across models.

Liu et al. [2023] survey trustworthiness across 7 categories and explicitly identify cross-dimension correlation analysis as future work. Our paper delivers that analysis. In this sense, we do not compete with these evaluation frameworks — we analyze the data they provide.

## 2.2 Trustworthiness Tradeoffs: Specific Pairs

Several studies have identified specific trustworthiness tradeoffs without characterizing the full correlation structure. AQUA-LLM [Güngör et al., 2025] demonstrates a quantitative accuracy-robustness tradeoff under quantization and adversarial perturbation — corroborating the directional safety-robustness tension we observe. Know Thy Judge [Eiras et al., 2025] shows that RLHF-trained safety judges are brittle to style shifts, with false negative rates jumping by up to 0.24 — consistent with our finding that RLHF-optimized models may not transfer their safety behaviors to adversarial inputs. Wang et al. [2025] survey reasoning LLMs and find that chain-of-thought models show *worse* safety and privacy performance than standard models at equivalent scale, suggesting inverse scaling relationships for specific dimensions.

These studies confirm that trustworthiness dimensions are not uniformly correlated — some pairs trade off while others co-move. However, they focus on specific pairs rather than the full 15-pair correlation matrix, and none controls for the scale and RLHF confounds that conflate model quality with trustworthiness geometry.

## 2.3 Benchmark Correlation Analysis and Evaluation Compression

The question of whether benchmark scores are redundant is well-studied for general capability benchmarks. The Epoch AI benchmark correlation study finds a median Spearman ρ = 0.73 across 17 capability benchmarks, suggesting substantial redundancy in capability measurement. A PCA study (arXiv 2603.00394) decomposes benchmark scores into two principal components explaining 97.4% of variance, with TruthfulQA loading orthogonally to the first component (general capability PC1) — providing early evidence that truthfulness is a distinct dimension.

Minimum spanning tree methods for correlation-based redundancy analysis have been applied to financial return correlation matrices [Tumminello et al., 2007] and ecological networks [Millington & Niranjan, 2021], where bootstrap stability metrics characterize the reliability of inferred tree topology. We apply this methodology to the LLM trustworthiness domain for the first time, using the Tumminello (2007) mean per-edge bootstrap frequency criterion to characterize MST stability.

## 2.4 RLHF Effects on Trustworthiness

The RLHF alignment paradigm is the primary mechanism through which modern LLMs are adapted for safe and helpful behavior [Ouyang et al., 2022]. Li et al. [2025] (ICLR Oral) find that "more RLHF" does not automatically guarantee trustworthiness across all dimensions — safety can improve while other dimensions stagnate or regress. Our findings are consistent with Li et al.: we confirm that RLHF jointly optimizes safety and ethics (via LLaMA-2 within-family evidence) while robustness follows an independent path. The distinction is that we characterize the *correlation structure* of RLHF effects, not just their directional impact on individual dimensions.

## 2.5 Positioning Our Contribution

| Prior Work | Data Provided | What is Missing |
|---|---|---|
| TrustLLM [Sun et al., 2024] | 16-model × 6-dimension scores | Pairwise correlation analysis; no partial correlation controlling for confounds |
| HELM [Liang et al., 2022] | 30-model × 7-metric scores | Cross-metric correlation matrix; no statistical clustering |
| Liu et al. [2023] | 7-category survey | Explicitly lists cross-dim correlation as future work |
| AQUA-LLM [Güngör et al., 2025] | Accuracy-robustness tradeoff | Single pair; no full matrix; no confound control |
| Epoch AI study | Capability benchmark correlations (ρ=0.73) | Capability, not trustworthiness; no partial correlation |

Our work fills the gap at the intersection: we provide the first pairwise partial Spearman correlation matrix for LLM trustworthiness, the first cluster analysis of the correlation geometry, and the first MST-based minimum evaluation set — all using publicly available TrustLLM data.
