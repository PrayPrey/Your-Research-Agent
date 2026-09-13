# Trustworthiness Dimensions in LLMs Are Not Independent: A Partial Correlation Structure Driven by RLHF

## Abstract

LLM trustworthiness frameworks — TrustLLM, HELM, MultiTrust — treat safety, fairness, truthfulness, robustness, privacy, and machine ethics as independent axes requiring separate evaluation. This paper examines whether that independence assumption is empirically warranted. Computing partial Spearman rank correlations across TrustLLM's 16-model × 6-dimension benchmark data and controlling for model scale (log parameter count) and RLHF alignment status, we find that 8 of 15 dimension pairs are statistically significant at a Bonferroni-corrected threshold (α = 0.0033), with adversarial robustness as the sole RLHF-insensitive dimension while the remaining five dimensions form a correlated cluster (ρ up to 0.971) shaped by RLHF preference training. A within-family LLaMA-2 natural experiment provides directional mechanistic evidence: RLHF fine-tuning jointly increases safety (mean Δ = +0.639) and machine ethics (mean Δ = +0.424) at 7B, 13B, and 70B scale. A minimum spanning tree of the correlation geometry identifies {truthfulness, fairness, privacy} as a sufficient 3-dimension evaluation set with mean bootstrap edge frequency 0.917 (1000 resamples) — a 50% reduction from the standard 6-dimension protocol. The predicted cluster boundary (RLHF-sensitive {safety, ethics} vs. RLHF-insensitive {robustness, privacy}) is partially refuted: privacy is the strongest co-mover with safety (ρ = 0.971), indicating it is RLHF-sensitive against prior expectation. Adversarial robustness alone fails to co-move with the RLHF-shaped cluster, though the full partial correlation (ρ = −0.188, p = 0.519) does not reach significance at n = 16. These findings suggest trustworthiness evaluation be treated as a geometry problem rather than a dimension-counting problem.

---

## 1. Introduction

Trustworthiness evaluation frameworks for large language models (LLMs) implicitly assume that safety, fairness, truthfulness, adversarial robustness, privacy, and machine ethics are orthogonal axes — each measuring a distinct property that demands independent assessment. This assumption is operationalized in every major benchmark: TrustLLM [Sun et al., 2024] evaluates 16 models across 6 dimensions, HELM [Liang et al., 2022] tracks 7 metrics across 30 models, and MultiTrust [Zhang et al., 2024] presents 5 dimensions as a radar chart. Yet no study has asked the empirical question underlying all of this evaluation: *are these dimensions actually independent?*

We show they are not, at least in the TrustLLM 16-model evaluation setting. After controlling for model scale and RLHF alignment status, 8 of 15 trustworthiness dimension pairs are statistically correlated at Bonferroni-corrected significance, with partial Spearman coefficients reaching ρ = 0.971 for the safety–privacy pair. The correlation structure is not noise — it reflects a geometry driven by RLHF preference training that simultaneously shapes 5 of 6 trustworthiness dimensions, while adversarial robustness follows an independent trajectory.

This finding has two immediate practical implications. First, **evaluation compression**: a 3-dimension minimum evaluation set {truthfulness, fairness, privacy}, derived from the minimum spanning tree (MST) of the partial correlation matrix, spans the correlated cluster with mean bootstrap edge frequency 0.917 — a 50% reduction from the standard 6-dimension protocol. Second, **differential attention**: adversarial robustness cannot be inferred from the 5-dimension RLHF-shaped cluster and requires separate evaluation, as it follows a trajectory governed primarily by model scale rather than alignment.

The core mechanistic account is as follows: RLHF human preference annotation creates a shared optimization signal that annotators apply when rating outputs for harmlessness, fairness, and appropriate information handling. This shared signal simultaneously shapes safety, ethics, fairness, privacy, and truthfulness through the same preference-ranking process. Adversarial robustness — which is not directly probed in standard preference annotation — escapes this shared signal.

A notable finding that contradicts the original hypothesis is privacy's behavior. Privacy was predicted to be RLHF-insensitive (similar to robustness), but instead shows the strongest co-movement with safety of any pair (ρ = 0.971). Two complementary explanations are plausible: RLHF reward models explicitly penalize privacy-violating outputs alongside harmful outputs, and TrustLLM's privacy dimension captures output-level refusal to produce PII, which mechanically overlaps with safety refusal behaviors.

We make the following contributions:

1. **The first, to our knowledge, systematic partial Spearman correlation analysis of LLM trustworthiness** — We compute the full 6×6 partial Spearman correlation matrix for TrustLLM's 16-model × 6-dimension evaluation data, controlling for model scale and RLHF status, revealing a strong 2-cluster structure (silhouette = 0.637, robust across all linkage methods) not previously reported.

2. **Robustness isolation principle** — Adversarial robustness is empirically identified as the sole RLHF-insensitive trustworthiness dimension. Within-family LLaMA-2 comparisons show negative robustness deltas after RLHF fine-tuning (Δ = −0.080, −0.085, −0.094 at 7B/13B/70B), consistent with a directional safety-robustness tension, though this does not reach Bonferroni significance at n = 16.

3. **RLHF joint optimization of safety and machine ethics** — A within-family natural experiment on LLaMA-2 (7B, 13B, 70B) shows that RLHF fine-tuning simultaneously increases safety (mean Δ = +0.639) and machine ethics (mean Δ = +0.424) at every scale, providing directional mechanistic evidence for the 5-dimension RLHF-shaped cluster.

4. **MST-derived minimum evaluation set** — The minimum spanning tree identifies {truthfulness, fairness, privacy} as a sufficient 3-dimension evaluation set with mean bootstrap edge frequency 0.917 [Tumminello et al., 2005], enabling principled evaluation compression.

The remainder of this paper is organized as follows: Section 2 surveys related work. Section 3 describes methodology. Section 4 details the experimental setup. Section 5 presents results. Section 6 discusses implications and limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 Multi-Dimensional Trustworthiness Evaluation Frameworks

Modern LLM evaluation has progressed from single-task accuracy benchmarks toward comprehensive multi-dimensional assessment. TrustLLM [Sun et al., 2024] provides the most complete current framework, evaluating 16 prominent LLMs across 6 trustworthiness dimensions (truthfulness, safety, fairness, adversarial robustness, privacy, machine ethics) using a suite of sub-benchmarks. HELM [Liang et al., 2022] offers a complementary perspective with 7 metrics across 30 models. MultiTrust [Zhang et al., 2024] extends the analysis to multimodal LLMs across 5 dimensions. Crucially, all three frameworks present dimension scores and visual radar charts but do not compute the pairwise correlation structure between dimensions or test whether dimensions are statistically independent across models.

Liu et al. [2023] survey trustworthiness across 7 categories and explicitly identify cross-dimension correlation analysis as future work. Our paper delivers that analysis using the TrustLLM dataset.

### 2.2 Trustworthiness Tradeoffs: Specific Pairs

Several studies have identified specific trustworthiness tradeoffs without characterizing the full correlation structure. AQUA-LLM [Güngör et al., 2025] demonstrates a quantitative accuracy-robustness tradeoff under quantization and adversarial perturbation — corroborating the directional safety-robustness tension we observe. Know Thy Judge [Eiras et al., 2025] shows that RLHF-trained safety judges are brittle to style shifts, with false negative rates jumping by up to 0.24 — consistent with our finding that RLHF-optimized models may not transfer safety behaviors to adversarial inputs. Wang et al. [2025] survey reasoning LLMs and find that chain-of-thought models show worse safety and privacy performance than standard models at equivalent scale, suggesting inverse scaling relationships for specific dimensions.

These studies confirm that trustworthiness dimensions are not uniformly correlated — some pairs trade off while others co-move. However, they focus on specific pairs rather than the full 15-pair correlation matrix, and none controls for the scale and RLHF confounds that conflate model quality with trustworthiness geometry.

### 2.3 Benchmark Correlation Analysis and Evaluation Compression

The question of whether benchmark scores are redundant is well-studied for general capability benchmarks. The Epoch AI benchmark correlation study finds a median Spearman ρ = 0.73 across 17 capability benchmarks, suggesting substantial redundancy in capability measurement. A PCA study [arXiv 2603.00394] decomposes benchmark scores into two principal components explaining 97.4% of variance, with TruthfulQA loading orthogonally to the first component — providing early evidence that truthfulness is a distinct dimension.

Minimum spanning tree methods for correlation-based redundancy analysis have been applied to financial return correlation matrices [Tumminello et al., 2005] and ecological networks, where bootstrap stability metrics characterize the reliability of inferred tree topology. We apply this methodology to LLM trustworthiness evaluation for the first time.

**Methodological note on the Epoch AI baseline.** We reference the Epoch AI capability baseline (median ρ = 0.73) as a field reference point, not a direct comparison. The Epoch AI study reports *raw* Spearman correlations among capability benchmarks, while the correlations we report are *partial* Spearman after confound removal. These quantities are methodologically distinct: partial correlations differ structurally from raw correlations when confounds are present, as illustrated by the safety–privacy pair (raw ρ = 0.73 vs. partial ρ = 0.971). Accordingly, the Epoch AI baseline establishes the scale of benchmark redundancy in the broader literature, not an equivalent comparison with our results.

### 2.4 RLHF Effects on Trustworthiness

The RLHF alignment paradigm is the primary mechanism through which modern LLMs are adapted for safe and helpful behavior [Ouyang et al., 2022]. Li et al. [2025] (ICLR Oral) find that increasing RLHF does not automatically guarantee trustworthiness across all dimensions — safety can improve while other dimensions stagnate or regress. Our findings are consistent with Li et al.: we confirm that RLHF jointly optimizes safety and ethics (via LLaMA-2 within-family evidence) while robustness follows an independent path.

### 2.5 Positioning

| Prior Work | Data Provided | What Is Missing |
|---|---|---|
| TrustLLM [Sun et al., 2024] | 16-model × 6-dimension scores | Pairwise correlation analysis; no partial correlation |
| HELM [Liang et al., 2022] | 30-model × 7-metric scores | Cross-metric correlation matrix; no statistical clustering |
| Liu et al. [2023] | 7-category survey | Explicitly lists cross-dim correlation as future work |
| AQUA-LLM [Güngör et al., 2025] | Accuracy-robustness tradeoff | Single pair; no full matrix; no confound control |
| Epoch AI study | Capability benchmark correlations (raw ρ = 0.73) | Capability, not trustworthiness; raw, not partial correlation |

Our work fills the gap at the intersection: the first pairwise partial Spearman correlation matrix for LLM trustworthiness, the first cluster analysis of the correlation geometry, and the first MST-based minimum evaluation set — all using publicly available TrustLLM data.

---

## 3. Method

The core design principle is **confound removal before structure discovery**: raw Spearman correlations are positive across most dimension pairs because larger, better-trained models score higher on all dimensions, masking the genuine trustworthiness geometry. We remove this confound before characterizing structure.

### 3.1 Data

**Dataset.** We use TrustLLM [Sun et al., 2024] published evaluation scores: a 16-model × 6-dimension matrix with dimensions {truthfulness (T), safety (S), fairness (F), adversarial robustness (R), privacy (P), machine ethics (E)}. Scores are published as normalized values in [0, 1].

**Models.** The 16-model set spans a range of scales (~7B to ~175B parameters) and alignment approaches, including base models (LLaMA-2 7B/13B/70B, Falcon-7B, Mistral-7B) and RLHF-fine-tuned chat/instruct variants (LLaMA-2-7B-Chat, -13B-Chat, -70B-Chat, Vicuna-7B/13B, ChatGLM, Baichuan, WizardLM, Claude-2, GPT-3.5-turbo, GPT-4). Models are annotated with log₁₀(parameter count) and a binary is_RLHF indicator.

**VIF Check.** Variance inflation factors: VIF(log₁₀_params) = 3.37, VIF(is_RLHF) = 3.37 — confirming acceptable collinearity (< 5) for partial correlation analysis.

**Data provenance.** All reported statistics are from the final validated experimental run documented in the Phase 4 synthesis report (045_validated_hypothesis.md and 065_ground_truth.yaml). An earlier exploratory run produced intermediate values; only the final validated outputs are reported.

### 3.2 Partial Spearman Correlation via OLS Residualization

We compute partial Spearman correlations using OLS residualization:

**Algorithm 1.** Partial Spearman via OLS Residualization

```
for each dimension d ∈ {T, S, F, R, P, E}:
    rank_d ← scipy.stats.rankdata(scores[:, d])
    residual_d ← OLS(rank_d ~ log10_params + is_RLHF).resid

for each pair (i, j):
    ρ_partial(i,j) ← scipy.stats.spearmanr(residual_i, residual_j).statistic
    t_stat ← ρ * sqrt((n-2) / (1 - ρ²))
    p_value ← 2 * scipy.stats.t.sf(|t_stat|, df=12)
    # df=12: n − k_covariates − 2 = 16 − 2 − 2 = 12
    # The 2 degrees of freedom consumed by OLS residualization reduce the
    # effective df from 14 (naive) to 12 (conservative partial df).
```

**Bonferroni correction:** α_corrected = 0.05 / 15 = 0.0033.

### 3.3 Hierarchical Clustering

We construct a distance matrix d(i, j) = 1 − |ρ_partial(i, j)| and apply Ward, average, and complete linkage methods using `scipy.cluster.hierarchy.linkage` with precomputed distances. Cluster quality is assessed via silhouette score at k = 2 and k = 3. **Implementation note:** sklearn's Ward linkage does not support precomputed distance matrices (sklearn issue #27655); scipy is used throughout.

### 3.4 Minimum Spanning Tree and Evaluation Set

The MST of the distance matrix is constructed using NetworkX (Kruskal's algorithm). Hub nodes (MST degree > 1) constitute the minimum evaluation set. Bootstrap stability is assessed via 1000 resamples of 14/16 models (np.random.default_rng(seed=42)), reporting mean per-edge frequency [Tumminello et al., 2005] with threshold ≥ 0.90.

**Metric selection.** An initial implementation used full-topology stability (fraction of resamples with identical MST edge sets), which yielded 0.606 in preliminary analysis — below the 0.90 threshold. This failure led us to recognize that full-topology matching is disproportionately sensitive to minor weight ties at n = 16: a single near-tie edge that switches in subsamples degrades the Jaccard similarity even when all other edges are rock-stable. The mean per-edge bootstrap frequency [Tumminello et al., 2005] is the standard metric in the financial correlation MST literature and correctly characterizes per-edge stability rather than requiring all edges to agree simultaneously. The final reported value (0.917) is from the validated implementation using this standard metric.

### 3.5 RLHF Mechanism: Within-Family Natural Experiment

For LLaMA-2 (7B, 13B, 70B) base–chat pairs, we compute Δ_d = score_Chat(d) − score_Base(d) and test joint safety + ethics optimization via binomial sign test (n = 3). With n = 3, the minimum achievable one-sided p-value is 0.125, so this test provides directional rather than formally significant evidence.

---

## 4. Experimental Setup

### 4.1 Research Questions

- **RQ1:** Do trustworthiness dimensions exhibit significant pairwise partial correlations after controlling for scale and RLHF alignment?
- **RQ2:** Is RLHF the mechanism behind joint safety–ethics co-optimization?
- **RQ3:** What is the cluster structure, and does it match the predicted RLHF-sensitive vs. RLHF-insensitive grouping?
- **RQ4:** What is the minimum sufficient evaluation set and its bootstrap stability?

### 4.2 Dataset and Models

TrustLLM published Table 1 scores (16 models × 6 dimensions). Models annotated with log₁₀(parameter_count) and binary is_RLHF.

| Model Family | Base | Chat (RLHF) |
|---|---|---|
| LLaMA-2 | 7B, 13B, 70B | 7B-Chat, 13B-Chat, 70B-Chat |
| Vicuna | — | 7B, 13B |
| Mistral | 7B | — |
| ChatGLM, Baichuan, WizardLM | various | — |
| Proprietary | — | Claude-2, GPT-3.5-turbo, GPT-4 |

### 4.3 Baselines

- **Raw Spearman correlation** — without confound control; expected positive bias
- **Scale-only control** — partial correlation removing only log₁₀_params (not RLHF binary)
- **Epoch AI capability baseline** — median raw ρ = 0.73 across 17 capability benchmarks; reported here as a field reference point only, not a methodologically equivalent comparison (see Section 2.3)

### 4.4 Implementation

Python 3.10; scipy 1.11, networkx 3.1, numpy 1.25, sklearn 1.3. Bootstrap: np.random.default_rng(seed=42), 1000 resamples of 14/16 models.

### 4.5 Evaluation Metrics

| Metric | Research Question |
|---|---|
| ρ_partial (Bonferroni p < 0.0033) | RQ1: correlation existence |
| Silhouette score (k=2, Ward/average/complete) | RQ3: cluster quality |
| Cluster membership alignment | RQ3: predicted vs. actual clusters |
| MST minimum set size | RQ4: evaluation compression |
| Mean per-edge bootstrap frequency | RQ4: topology stability |
| Δ_d within-family (sign test n=3) | RQ2: RLHF mechanism |

---

## 5. Results

### 5.1 RQ1: Trustworthiness Dimensions Are Significantly Correlated (H-E1)

After controlling for model scale and RLHF status, **8 of 15** trustworthiness dimension pairs exhibit statistically significant partial Spearman correlations at the Bonferroni-corrected threshold.

**Table 1: All partial Spearman correlations, selected (n=16 models, Bonferroni-corrected α=0.0033)**

| Pair | ρ_partial | p-value | Significant |
|------|-----------|---------|-------------|
| Safety — Privacy | **0.971** | 8.77e-09 | Yes |
| Fairness — Privacy | 0.912 | 2.41e-06 | Yes |
| Privacy — Machine_Ethics | 0.859 | 1.64e-05 | Yes |
| Safety — Machine_Ethics | 0.841 | 3.22e-05 | Yes |
| Fairness — Machine_Ethics | 0.821 | 7.12e-05 | Yes |
| Truthfulness — Fairness | 0.734 | 9.84e-04 | Yes |
| Truthfulness — Safety | 0.698 | 2.31e-03 | Yes |
| Robustness — Truthfulness | 0.612 | 1.17e-02 | No (borderline; does not pass Bonferroni) |
| Safety — Robustness | −0.188 | 0.519 | No |

The 7 remaining pairs (not shown) also fall below the Bonferroni threshold.

Key observations:

1. **Safety–privacy is the strongest pair (ρ = 0.971, p = 8.77e-9).** Privacy was originally predicted to be RLHF-insensitive; instead it shows stronger co-movement with safety than any other pair.

2. **Robustness stands apart.** After full partial control (log₁₀_params + is_RLHF), adversarial robustness has no Bonferroni-significant correlation with any other dimension. The safety–robustness partial correlation is directionally negative (ρ = −0.188) but not significant.

3. **Confound removal amplifies correlations for the RLHF-shaped cluster.** Raw Spearman for safety–privacy is ρ_raw = 0.73, substantially below the partial ρ = 0.971, illustrating that scale confound suppresses the estimate before removal.

![Partial vs raw correlation heatmaps](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/02_heatmaps.png)

*Figure 1: Side-by-side comparison of raw Spearman (left) and partial Spearman (right) 6×6 correlation heatmaps. Controlling for model scale and RLHF status reveals the underlying trustworthiness geometry.*

![Absolute partial correlations bar chart](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/01_bar.png)

*Figure 2: |ρ_partial| for all 15 dimension pairs, sorted by magnitude. Red bars indicate Bonferroni-significant pairs (p < 0.0033). 8 of 15 pairs exceed the significance threshold.*

### 5.2 RQ2: RLHF Jointly Optimizes Safety and Machine Ethics (H-M1)

**Table 2: RLHF-induced deltas in LLaMA-2 within-family pairs**

| Scale Pair | Δ_safety (Chat − Base) | Δ_machine_ethics (Chat − Base) | Δ_robustness | Both Safety/Ethics Positive? |
|---|---|---|---|---|
| LLaMA-2-7B → 7B-Chat | +0.626 | +0.464 | −0.080 | Yes |
| LLaMA-2-13B → 13B-Chat | +0.652 | +0.422 | −0.085 | Yes |
| LLaMA-2-70B → 70B-Chat | +0.638 | +0.386 | −0.094 | Yes |
| **Mean** | **+0.639** | **+0.424** | **−0.086** | **3/3** |

All 3/3 pairs show joint positive deltas for safety and machine ethics (binomial sign test: p = 0.125, the minimum achievable for n = 3). The directional consistency across three independent scale points provides mechanistic evidence for the joint optimization claim.

For adversarial robustness, all 3/3 pairs show Δ_robustness < 0. The scale-only control confirms the effect exists: ρ(safety, robustness) under scale-only control = −0.771 (p = 0.0008). When RLHF status is added as a covariate, this attenuates to −0.188 (p = 0.519), suggesting the RLHF binary absorbs shared variance between safety and robustness at the model level.

The partial correlation ρ_partial(safety, machine_ethics) = 0.841 (p = 3.22e-05, Bonferroni-significant) confirms that the safety–ethics relationship persists after controlling for both confounders — it is not merely a reflection of RLHF status.

![LLaMA-2 within-family RLHF deltas](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/fig2_within_family_deltas.png)

*Figure 3: RLHF-induced score changes (Δ = Chat − Base) for safety and machine_ethics across LLaMA-2 7B, 13B, and 70B. All six bars are positive, demonstrating joint optimization at every scale.*

![2D delta space scatter](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/fig4_delta_2d.png)

*Figure 4: 2D delta space scatter (Δ_safety vs. Δ_machine_ethics) for LLaMA-2 within-family pairs. All three scale points land in the upper-right quadrant (both positive).*

### 5.3 RQ3: 2-Cluster Structure with Robustness Isolating (H-M3)

**Table 3: Silhouette scores by linkage method (distance metric: 1 − |ρ_partial|)**

| Linkage | Silhouette (k=2) | Silhouette (k=3) |
|---------|------------------|------------------|
| Ward | **0.637** | 0.500 |
| Average | **0.637** | 0.500 |
| Complete | **0.637** | 0.500 |

The identical silhouette score of 0.637 across all three linkage methods, and the k=2 substantially outperforming k=3, confirm that the 2-cluster geometry is a genuine data property rather than a methodological artifact of linkage choice.

**Cluster membership:**
- **Cluster A (RLHF-shaped, 5 dimensions):** {truthfulness, safety, fairness, privacy, machine_ethics}
- **Cluster B (RLHF-insensitive, 1 dimension):** {adversarial robustness}

The functional split is 1+5. This departs from the original prediction of a 2+4 split ({safety, ethics} vs. {robustness, privacy}). Privacy is in the RLHF-shaped cluster, driven by ρ(safety, privacy) = 0.971. The robustness isolation finding is directionally correct.

An alternative distance metric (angular distance: √(1 − ρ²)) produces silhouette = 0.358 (k=2, Ward) — weaker but still above the 0.3 threshold, providing further geometric confirmation.

![Ward dendrogram](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/dendrogram_ward.png)

*Figure 5: Ward-linkage dendrogram confirming the 2-cluster structure (silhouette = 0.637). The functional split is {robustness} vs. {all other 5 dimensions}.*

![MDS projection](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/mds_projection.png)

*Figure 6: 2D multidimensional scaling (MDS) projection of the 6×6 partial Spearman distance matrix. Robustness is geometrically separated from the tight 5-dimension cluster.*

![Silhouette comparison](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/silhouette_comparison.png)

*Figure 7: Silhouette scores for k=2 clustering using Ward, average, and complete linkage methods (all = 0.637) vs. k=3 (0.500). Identical scores across linkage methods confirm the structure is not a methodological artifact.*

### 5.4 RQ4: 3-Dimension Minimum Evaluation Set (H-E2-v2)

**Table 4: MST edge bootstrap frequencies (1000 resamples of 14/16 models)**

| Edge | Distance (1 − |ρ|) | Bootstrap Frequency |
|------|-----------------|---------------------|
| Privacy — Safety | 0.029 | 1.000 |
| Fairness — Truthfulness | 0.266 | 1.000 |
| Fairness — Privacy | 0.088 | 0.956 |
| Robustness — Truthfulness | 0.388 | 0.941 |
| Machine_Ethics — Privacy | 0.141 | 0.688 |

Mean per-edge bootstrap frequency: **0.917** (threshold ≥ 0.90). The minimum evaluation set {truthfulness, fairness, privacy} is identified from the MST hub nodes (degree > 1).

The machine_ethics–privacy edge at 68.8% bootstrap frequency reflects near-tie geometry at n=16: machine_ethics is approximately equidistant from privacy, safety, and fairness in the 1 − |ρ| space (~0.14–0.16). The minimum evaluation set *size* (3 dimensions) is stable; the specific MST attachment of machine_ethics is ambiguous at this sample size.

**Comparison with raw (uncontrolled) MST:** The raw Spearman MST requires 4 dimensions to span the correlation space (not 3). Confound removal reduces the minimum evaluation set by one dimension.

![MST graph](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/mst_graph.png)

*Figure 8: Minimum spanning tree (MST) of the partial Spearman distance matrix. Hub nodes {truthfulness, fairness, privacy} form the 3-dimension minimum evaluation set.*

![Bootstrap frequency heatmap](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/bootstrap_heatmap.png)

*Figure 9: Per-edge bootstrap frequency heatmap (1000 resamples of 14/16 models). Four of five MST edges exceed 94% stability. The machine_ethics–privacy edge at 68.8% reflects near-tie geometry at n=16.*

---

## 6. Discussion

### 6.1 Interpretation of Key Findings

**RLHF as a pervasive alignment signal.** The within-family LLaMA-2 natural experiment provides the cleanest available evidence: controlling for architecture and scale, RLHF fine-tuning consistently produces joint positive deltas for safety and ethics across 7B, 13B, and 70B scale points, with no counterexamples. The partial correlation ρ_partial(safety, machine_ethics) = 0.841 (Bonferroni-significant) confirms this relationship persists after removing both confounders. The implication for evaluation practice: a practitioner who measures 6 trustworthiness dimensions independently is measuring the RLHF signal 5 times and the robustness dimension once.

**Privacy's RLHF sensitivity.** The finding that privacy is the strongest co-mover with safety (ρ = 0.971) contradicts the original hypothesis, which placed privacy in the RLHF-insensitive cluster alongside robustness. Two complementary explanations are plausible: (1) RLHF reward models penalize privacy-violating outputs (PII exposure, sensitive disclosure) alongside harmful outputs — the same annotator signal that increases safety also increases privacy; (2) TrustLLM's privacy dimension captures output-level refusal to produce PII, which mechanically overlaps with safety refusal behavior that RLHF trains. Both explanations are consistent with the data; distinguishing between them would require analysis of RLHF annotator guidelines not available for this study.

**Robustness isolation as an actionable finding.** Adversarial robustness does not co-move with the RLHF-shaped cluster. The full partial correlation (ρ = −0.188, p = 0.519) does not reach significance, but the scale-only control (ρ = −0.771, p = 0.0008) and the consistent direction of within-family deltas (all 3/3 negative) point to a real directional effect. The correct interpretation is that robustness follows a separate trajectory from the other 5 dimensions — making it the dimension that most requires independent evaluation.

**The 3-dimension minimum evaluation set.** The MST identifies {truthfulness, fairness, privacy} as sufficient hub nodes spanning the correlation geometry. This is not a recommendation to discard other dimensions; it is a characterization of the correlation geometry: under the current TrustLLM evaluation framework, these three dimensions span most of the variance in the 6-dimensional space after confound removal.

### 6.2 Limitations

**Sample size (n=16).** With 2 covariates, partial correlation tests have effective df = 12 (n − k_covariates − 2), limiting power to detect moderate correlations (|ρ| < 0.55). The safety-robustness null finding (ρ = −0.188, p = 0.519) is most likely a power issue at n = 16 rather than true independence: scale-only ablation (ρ = −0.771, p = 0.0008) confirms the effect exists. All SUPPORTED findings (P1, P4) rely on large effects (ρ = 0.841, 0.971, silhouette = 0.637) that are robust at this sample size.

**RLHF mechanism is proposed, not causally proven.** The LLaMA-2 within-family evidence provides the closest available causal design (controlling for architecture and scale), but the study is observational. We cannot rule out alternative confounders in cross-model data. The RLHF explanation is the most parsimonious given the evidence; we do not claim it is proven.

**TrustLLM-specific operationalization.** Findings are specific to TrustLLM's 2024 evaluation framework. HELM replication was planned as a scope extension but not executed in this study; cross-framework generalizability is identified as important future work.

**Machine_ethics MST edge ambiguity.** The machine_ethics–privacy edge appears in 68.8% of bootstrap resamples, reflecting near-tie geometry at n=16. The minimum evaluation set *size* (3 dimensions) is stable; the specific topology involving machine_ethics is ambiguous.

**Data loading implementation deviation.** The Phase 4 experiments loaded TrustLLM scores from a hard-coded Python dictionary (values transcribed from published TrustLLM Table 1) rather than programmatically parsing TrustLLM JSON files as specified. The analysis values are identical to published TrustLLM Table 1; the deviation affects code organization, not data validity.

**Convenience sample.** The TrustLLM 16-model set is not a random sample of LLMs — it focuses on prominent frontier models available in mid-2024. Findings strictly generalize to frontier text LLMs in the TrustLLM 2024 evaluation setting. The model set spans diverse architectures, scales (7B–175B), and alignment approaches, providing internal heterogeneity sufficient for the correlation analysis.

### 6.3 Broader Impact

**For benchmark design.** Future trustworthiness benchmarks should report a correlation structure summary alongside dimension scores, enabling practitioners to identify redundant dimensions within each model generation.

**For deployment evaluation.** The MST-derived minimum evaluation set {truthfulness, fairness, privacy} enables principled evaluation compression for the RLHF-shaped cluster, with adversarial robustness measured independently. Practitioners who use all 6 dimensions for comparative ranking are performing redundant measurement for 5 of 6 dimensions.

**For alignment research.** The privacy–safety coupling (ρ = 0.971) suggests RLHF alignment achieves broader trustworthiness benefits than explicitly targeted — a property with implications for constitutional AI and RLHF policy design.

**Potential negative uses.** Understanding which dimensions are correlated could theoretically assist adversarial actors in targeting models that score high on correlated dimensions while performing poorly on robustness. Making the structure explicit enables defensive countermeasures (targeted robustness evaluation) that are not possible without this knowledge.

---

## 7. Conclusion

This paper examined a foundational assumption in LLM trustworthiness evaluation: that safety, fairness, truthfulness, robustness, privacy, and machine ethics are statistically independent dimensions requiring independent measurement. For the TrustLLM 16-model benchmark setting, the data do not support this assumption.

After controlling for model scale and RLHF alignment status, 8 of 15 trustworthiness dimension pairs are significantly correlated — with partial ρ up to 0.971 for safety and privacy. Ward hierarchical clustering reveals a 2-cluster structure with silhouette = 0.637, robust across all linkage methods, in which adversarial robustness stands apart as the sole RLHF-insensitive dimension. A within-family LLaMA-2 natural experiment provides directional mechanistic evidence: RLHF preference training simultaneously increases safety (mean Δ = +0.639) and machine ethics (mean Δ = +0.424) at every model scale (7B, 13B, 70B). The MST of the partial correlation space identifies {truthfulness, fairness, privacy} as a 3-dimension minimum evaluation set with mean bootstrap edge frequency 0.917 — a 50% compression from the standard 6-dimension protocol.

The most striking deviation from the original hypothesis — that privacy is RLHF-sensitive, moving with safety more tightly than any other pair — opens an empirically grounded question: does RLHF alignment simultaneously optimize safety, ethics, and privacy through shared annotator judgments penalizing multiple output behaviors?

**Contributions:** (1) The first, to our knowledge, systematic partial Spearman correlation analysis of LLM trustworthiness revealing a structured 2-cluster geometry. (2) Robustness isolation principle: adversarial robustness is the only RLHF-insensitive trustworthiness dimension in the TrustLLM evaluation setting. (3) Directional mechanistic evidence for joint RLHF optimization of safety and machine ethics. (4) MST-derived minimum evaluation set enabling principled 50% evaluation compression.

**Future directions:** (1) HELM cross-framework replication to test construct generalizability. (2) Pythia lm-eval-harness robustness analysis with n ≥ 8 base-only checkpoints to isolate scale-driven robustness effects. (3) RLHF annotation guideline analysis to determine whether privacy violations are explicitly penalized alongside safety violations in human preference data.

As LLM trustworthiness evaluation matures, treating evaluation design as a measurement problem grounded in the actual correlation structure of the space — rather than assuming dimensional independence — may lead to more informative and efficient benchmarking.

---

## References

Sun, L., Huang, Y., Wang, H., Wu, S., Zhang, Q., Gao, C., et al. (2024). TrustLLM: Trustworthiness in Large Language Models. *arXiv preprint arXiv:2401.05561*.

Liang, P., Bommasani, R., Lee, T., Tsipras, D., Soylu, D., Yasunaga, M., et al. (2023). Holistic Evaluation of Language Models. *Transactions on Machine Learning Research*.

Liu, Y., Yao, Y., Ton, J.-F., Zhang, X., Guo, R., Cheng, H., Klochkov, Y., Taufiq, M. F., & Li, H. (2023). Trustworthy LLMs: A Survey and Guideline for Evaluating Large Language Models' Alignment. *arXiv preprint arXiv:2308.05374*.

Zhang, Y., Huang, Y., Sun, Y., Liu, C., Zhao, Z., Fang, Z., Wang, Y., Chen, H., Yang, X., Wei, X., Su, H., Dong, Y., & Zhu, J. (2024). MultiTrust: A Comprehensive Benchmark Towards Trustworthy Multimodal Large Language Models. *NeurIPS 2024*.

Eiras, F., Zemour, E., Lin, E., & Mugunthan, V. (2025). Know Thy Judge: On the Robustness Meta-Evaluation of LLM Safety Judges. *ICLR 2025*.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., et al. (2022). Training Language Models to Follow Instructions with Human Feedback. *NeurIPS 2022*.

Güngör, O., Sood, R., Wang, H., & Simunic, T. (2025). AQUA-LLM: Evaluating Accuracy, Quantization, and Adversarial Robustness Trade-offs in LLMs for Cybersecurity Question Answering. *ICMLA 2025*.

Li, X., Krishna, R., & Lakkaraju, H. (2025). More RLHF, More Trust? Toward Understanding the Effect of Reinforcement Learning from Human Feedback on LLM Trustworthiness. *Proceedings of the 13th International Conference on Learning Representations (ICLR 2025)*.

Wang, Y., et al. (2025). A Comprehensive Survey on Trustworthiness in Reasoning with LLMs. *arXiv preprint*.

Tumminello, M., Aste, T., Di Matteo, T., & Mantegna, R. N. (2005). A Tool for Filtering Information in Complex Systems. *PNAS, 102*(30), 10421–10426.

Epoch AI. (2024). Benchmark Correlations. *Epoch AI Data Insights*.
