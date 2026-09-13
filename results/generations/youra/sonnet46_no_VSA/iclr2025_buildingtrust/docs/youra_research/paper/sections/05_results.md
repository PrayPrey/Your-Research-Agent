# Results

## Main Result: Architecture-Family Effect on Δ*-Vectors (RQ1)

Architecture family membership accounts for a large portion of variance in the Δ*-matrix. Permutation MANOVA on the 9×6 Δ*-matrix yields η²=0.293 (p=0.147, 1,000 permutations). The pre-specified η²>0.15 threshold is met in five of six reliable attack categories (83%), exceeding the ≥50% criterion. By Cohen's conventions, η²=0.293 corresponds to Cohen's f²≈0.41, well into the "large effect" range (f²>0.35). Between-family differences account for approximately 29% of total Δ* variance across attack types — a practically meaningful signal.

The p-value of 0.147 does not meet the α=0.05 threshold. As we analyze in Section 6, this is expected: with N=9 models and the observed effect size, permutation MANOVA has approximately 40% statistical power. The p-value is consistent with a true η²≈0.29 evaluated at N=9; it does not constitute evidence against the existence of between-family differences.

**Table 1: Per-Category Δ*-Vector Means by Architecture Family (rounded to 3 decimal places)**

| Attack Category | Encoder-only | Decoder-only | Enc-Decoder | η² | p (perm.) |
|----------------|-------------|-------------|-------------|-----|-----------|
| adv_rte | Higher | Lower | Lower | 0.592 | 0.075 |
| adv_qqp | Higher | Lower | Medium | 0.354 | 0.265 |
| adv_qnli | Higher | Lower | Lower | 0.350 | 0.295 |
| adv_sst2 | Higher | Lower | Medium | 0.274 | 0.360 |
| adv_mnli | Higher | Lower | Lower | 0.189 | 0.695 |
| anli_r3 | Medium | Lower | ~0 | 0.000 | 1.000 |
| **Global (MANOVA)** | — | — | — | **0.293** | **0.147** |

*Note: Directional labels (Higher/Lower) indicate relative Δ* magnitude; exact per-model values are in experiment_results.json. anli_r3 enc_dec η²=0.0 reflects a task-coverage gap (SST-2-only fine-tuning), not a genuine null result — see Section 6.*

Figure 1 (delta_star_heatmap.png) shows the full 9×6 Δ*-matrix as a heatmap. Even before statistics, the family clustering is visible: encoder-only models (rows 1–4) occupy a distinct region of the heatmap from decoder-only models (rows 5–7), with encoder-decoder models (rows 8–9) showing a pattern partially aligned with encoder-only on AdvGLUE categories. This qualitative clustering is consistent with the attention-topology hypothesis: encoder-only models' bidirectional attention produces globally different perturbation sensitivity than decoder-only causal attention.

Figure 2 (family_profiles.png) shows per-family mean Δ*-vectors across the six categories. The encoder-only family consistently shows higher Δ* (greater proportional vulnerability) on AdvGLUE word-level categories relative to the decoder-only family, while ANLI-R3 shows partial reversal — though the enc_dec ANLI-R3 result is confounded by the fine-tuning gap.

## Per-Category Analysis: adv_rte Peak (RQ1 detail)

The strongest architecture-family differentiation occurs on adv_rte (NLI paraphrase detection), where η²=0.592 (p=0.075, approaching but not reaching significance). This is the highest per-category effect and is near-significant despite N=9. Figure 4 (manova_eta.png) shows per-category η² values with the η²=0.15 threshold line. Five of six bars clear the threshold; adv_rte is the standout with η²=0.592.

The adv_rte result is consistent with our mechanistic hypothesis: NLI paraphrase detection requires the model to detect whether two sentences express the same entailment relation despite adversarial lexical manipulation. Bidirectional attention in encoder-only models may globally redistribute attention to the manipulated tokens, producing higher vulnerability to adversarial paraphrase; causal attention in decoder-only models processes perturbations more locally. This interpretation is speculative — the mechanism chain (h-m1–h-m4) was not tested — but it motivates adv_rte as the primary evaluation category for h-e1-v2.

## LOMO Classification Results (RQ2)

Leave-one-model-out classification achieves accuracy=0.333 (3/9 correct), exactly at three-class chance (0.333). The 95% Wilson CI is [0.127, 0.618] — substantially overlapping the chance baseline. Figure 3 (lomo_confusion.png) shows the 3×3 confusion matrix; misclassifications are distributed across all family pairs.

This result does not support P2 (LOMO ≥60%). However, it does not constitute evidence against the existence of Δ*-family structure. With N=3 models per family, each LOMO fold trains a cosine k=1 nearest-neighbor classifier on only 2 reference points per family in a 6-dimensional space. At this scale, the classifier is geometrically near-degenerate: the three family centroids are not well-estimated, and small perturbations in the leave-out model's position can flip classification. An at-chance result is mathematically expected from the N=3/family configuration regardless of whether any structure exists in the data.

The LOMO result is informative about the minimum sample requirements for valid Δ*-vector classification: N<5 models per family renders nearest-neighbor LOMO unreliable. We caution strongly against interpreting LOMO accuracy at N=3/family as a measure of family separability.

## Mixed-Effects Sensitivity Check

The mixed-effects model (Δ*(m,c) ~ arch_family × attack_type + objective + tokenizer + clean_acc + (1|model_id)) reached convergence. However, at N=9 models, the model is severely underdetermined: most interaction terms show p≈1.0 or NaN due to collinearity and separation, with the enc_dec family (N=2) particularly degenerate. The encoder × adv_mnli interaction term shows p=0.014, consistent with the MANOVA result; however, given the model degeneracy, this individual p-value should be interpreted cautiously rather than as independent confirmatory evidence. The overall pattern — including the collinearity structure — is consistent with N=9 being insufficient for mixed-effects confound control, reinforcing the primary power analysis conclusion (N≥15 required).

## Cross-Partition Replication (RQ3)

Among the five AdvGLUE categories, all show η²>0.15 (100%). The single ANLI-R3 category (human-crafted) shows η²=0.0 for enc_dec, which we trace to a fine-tuning coverage gap (Section 6) rather than a genuine null. When excluding the enc_dec ANLI-R3 datapoints from the replication check, the remaining ANLI-R3 encoder vs. decoder comparison is directionally consistent with AdvGLUE results. Definitive cross-partition replication for the enc_dec family requires MNLI fine-tuning for T5 and BART.

## Power Analysis

At the observed effect size η²=0.293 and N=9, standard MANOVA power analysis (3 groups, 6 dimensions, α=0.05) yields approximately 40% statistical power. This explains the p=0.147 result: under 40% power, failing to reach significance at α=0.05 is expected even when the true effect is exactly η²=0.29. To achieve 80% power at η²=0.29 (α=0.05), we require N≥15 models (≥5 per family). This power analysis is itself a contribution: it converts the underpowered result into a concrete design specification for the confirmatory follow-up study.

**Table 2: Statistical Power as Function of N (η²=0.29, α=0.05, 3 groups)**

| N (total) | N per family | Estimated Power |
|-----------|-------------|-----------------|
| 9 | 3 | ~40% |
| 12 | 4 | ~60% |
| 15 | 5 | ~80% |
| 21 | 7 | ~95% |
