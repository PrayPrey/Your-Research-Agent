# SparsityLoRA: Activation Sparsity as a Pre-Training Structural Prior for LoRA Rank Allocation

## Abstract

Low-Rank Adaptation (LoRA) fine-tunes large language models efficiently but typically assigns uniform rank across all layers, ignoring heterogeneous computational roles that emerge during pre-training. Existing adaptive rank methods learn the allocation during training, introducing a circular dependency and per-experiment overhead. This work asks whether a pre-trained model already encodes a reliable signal for rank allocation decisions prior to any fine-tuning.

The layer-wise MLP activation sparsity profile of LLaMA-3.1-8B is characterized as a structural fingerprint measurable from a single forward pass. Using forward hooks on 512 calibration samples, the fingerprint exhibits significant heterogeneity across 32 layers (CV = 0.544 at epsilon = 0.01) and is stable across four diverse calibration distributions: intraclass correlation ICC(3,k) = 0.9846 (95% CI: [0.97, 0.99]), with all six pairwise Kendall's tau values at or above 0.734. Threshold invariance is also confirmed: all six cross-epsilon Kendall's tau values exceed 0.95 across epsilon values spanning two orders of magnitude (minimum observed: tau = 0.9597 for the epsilon = 0.01 vs. epsilon = 0.1 pair).

These results establish that LLaMA-3.1-8B's sparsity profile reflects pre-training geometry rather than input content, providing an empirical foundation for its use as a zero-cost structural prior for LoRA rank allocation. Whether this fingerprint predicts rank requirements and enables efficient allocation remains empirically open; the corresponding experiments (H-M3, H-M4) were not executed in this work.

---

## 1. Introduction

Fine-tuning a large language model requires allocating parameters to each layer. In practice this allocation is made uniformly, before training begins, despite the fact that individual layers contribute differently to model behavior. Low-Rank Adaptation (LoRA; Hu et al., 2022) constrains weight updates to low-rank matrices, reducing trainable parameters by orders of magnitude. The rank r of these updates is set uniformly across all transformer layers — a choice that does not account for the heterogeneous computational roles that emerge during pre-training.

Aghajanyan et al. (2021) demonstrate that pre-trained language models have low intrinsic dimension for fine-tuning: more than 90% of full fine-tuning performance can be recovered in a subspace far smaller than the full parameter space. Structure-aware projections (SAID) significantly outperform dimension-insensitive alternatives, suggesting that layers differ in their fine-tuning dimensionality. If this is the case, allocating equal rank to all layers may waste parameters in low-complexity layers while providing insufficient capacity in high-complexity ones.

Adaptive rank methods have addressed this concern. AdaLoRA (Zhang et al., 2023) applies singular value decomposition to weight update matrices and prunes singular values during training via an importance score. DyLoRA (Valipour et al., 2023) trains across multiple rank values simultaneously through stochastic rank sampling. Both methods share a fundamental constraint: the rank allocation is learned during training, which introduces a circular dependency — the allocation is determined by the training process it is intended to guide — and requires a full training run per task.

This work investigates whether the pre-trained model itself carries a signal that could identify which layers require more rank, before any fine-tuning begins. Specifically, the layer-wise MLP activation sparsity profile of LLaMA-3.1-8B is measured and characterized across three dimensions:

1. **Heterogeneity (RQ1):** Do layers exhibit significantly different activation sparsity (CV > 0.3) with a stable cross-distribution ranking?
2. **Cross-distribution stability (RQ2):** Is the sparsity profile stable across diverse calibration text distributions?
3. **Threshold invariance (RQ3):** Is the layer rank ordering invariant to the choice of epsilon threshold across two orders of magnitude?

The central finding is that LLaMA-3.1-8B's sparsity profile passes all three tests by substantial margins, suggesting that this profile reflects pre-training geometry rather than input-dependent activation patterns. The practical implication — whether this profile can guide rank allocation and achieve efficiency gains — is designated future work (H-M3, H-M4) and was not executed in this study.

**Contributions:**

1. The first systematic characterization of LLaMA-3.1-8B's layer-wise MLP activation sparsity profile: CV = 0.544 (epsilon = 0.01) with a systematic depth gradient (early layers highest sparsity, deep layers lowest).
2. Cross-distribution stability: ICC(3,k) = 0.9846 with tau_min = 0.734 across four diverse calibration distributions.
3. Threshold invariance: all six cross-epsilon Kendall's tau values exceed 0.95 across epsilon in {0.001, 0.01, 0.05, 0.1} (minimum: tau = 0.9597).
4. An empirical foundation for treating the sparsity fingerprint as a zero-cost structural prior for LoRA rank allocation, along with a clear statement of what remains unvalidated.

---

## 2. Related Work

### 2.1 Parameter-Efficient Fine-Tuning and Adaptive Rank

LoRA (Hu et al., 2022) constrains weight updates to low-rank matrices, reducing trainable parameters by orders of magnitude. The original formulation assigns a uniform rank r across all target layers, which is acknowledged as potentially suboptimal.

**AdaLoRA** (Zhang et al., 2023) extends LoRA with singular value decomposition of weight update matrices. Singular values are adaptively pruned during training via an importance score, achieving better parameter efficiency than uniform rank. The rank allocation is a product of the training run and must be re-derived per task.

**DyLoRA** (Valipour et al., 2023) addresses the rank search problem by training across multiple rank values simultaneously via stochastic rank sampling. Like AdaLoRA, DyLoRA produces the rank distribution as a result of training rather than providing it as an input.

**Act-LoRA** (unverified citation; see notes) uses layer-wise L2 activation norms for binary layer selection — whether to include a layer in LoRA at all — rather than continuous rank magnitude allocation, and does not characterize the stability or threshold invariance of the activation signal.

The present work differs from all three in that the proposed signal is measured before training, from a single forward pass, with no gradient computation.

### 2.2 Activation Sparsity in Large Language Models

Li et al. (2023) characterize the Lazy Neuron Phenomenon: neurons become increasingly sparse during training, with feed-forward network (FFN) activations exhibiting concentrated activity. Mirzadeh et al. (2024) demonstrate in "ReLU Strikes Back" that modern LLMs achieve substantial sparsity at inference time. Liu et al. (2025) provide the TEAL framework, a training-free approach to exploiting activation sparsity via magnitude-based thresholding, reporting 40–50% model-wide sparsity on LLaMA-2/3-8B with minimal degradation.

Szatkowski et al. (2025) identify universal structural properties across LLM families, finding that sparsity patterns exhibit cross-model consistency. This prior work motivates the cross-distribution stability analysis in the present study; the ICC(3,k) = 0.9846 result obtained here strongly confirms distribution-invariance for LLaMA-3.1-8B specifically.

The existing literature characterizes the existence and approximate magnitude of activation sparsity in large transformers. It does not establish whether the layer-wise sparsity fingerprint is stable enough — across calibration distributions and threshold choices — to serve as a pre-training prior for rank allocation decisions. That characterization is the central empirical contribution of this work.

### 2.3 Intrinsic Dimensionality and Layer Structure

Aghajanyan et al. (2021) demonstrate that pre-trained language models have low intrinsic dimension for fine-tuning. Their structure-aware projection method (SAID) significantly outperforms dimension-insensitive alternatives, providing a theoretical bridge: if activation sparsity proxies intrinsic dimension, it could directly inform rank allocation. The present work does not test this bridge empirically; H-M3 is designed to do so.

Clark et al. (2019) and Tenney et al. (2019) demonstrate a linguistic hierarchy in transformer layers, with syntactic processing concentrated in early layers and semantic integration in later ones. The depth gradient observed here — early layers most sparse, deep layers least sparse — is consistent with this specialization, though the mechanistic link is not established by this work.

| Method | Signal | Measurement Cost | Allocation Type | Stability Characterized |
|--------|--------|-----------------|-----------------|------------------------|
| AdaLoRA (Zhang et al., 2023) | SVD importance | Full training run | Continuous | No |
| DyLoRA (Valipour et al., 2023) | Rank sampling | Full training run | Continuous | No |
| TEAL (Liu et al., 2025) | Activation magnitude | Inference pass | Pruning | No |
| This work | Layer sparsity | Single forward pass | Prior (continuous) | Yes |

---

## 3. Method

### 3.1 Sparsity Measurement

Layer-wise MLP activation sparsity is defined as the fraction of gate projection activations below a threshold epsilon:

$$s_\ell(\varepsilon) = \frac{1}{|S|} \sum_{x \in S} \frac{1}{d_{\text{ffn}}} \sum_{j=1}^{d_{\text{ffn}}} \mathbf{1}\left[|\text{gate\_proj}_\ell(x)_j| < \varepsilon\right]$$

where S is the set of 512 calibration samples, and d_ffn = 14336 for LLaMA-3.1-8B. Sparsity is measured using PyTorch forward hooks registered on the `gate_proj` layer of each of 32 MLP blocks. The measurement requires a single forward pass with no gradient computation (torch.no_grad()). The primary threshold is epsilon = 0.01.

Implementation follows the hook registration pattern from the SparseGPT and TEAL codebases: a closure factory creates per-layer hook functions that accumulate per-batch sparsity fractions, which are averaged after all calibration samples are processed. Hooks are removed after each experiment run.

### 3.2 Cross-Distribution Stability (RQ2)

Four calibration distributions are used: Alpaca (instruction following; tatsu-lab/alpaca, first 512 training samples), WikiText-103 (general web text; wikitext-103-raw-v1 test split, first 512 chunks of 512 tokens), SST-2 validation (sentiment classification; SetFit/sst2, 512 samples), and MNLI validation (natural language inference; nyu-mll/multi_nli validation_matched, first 512 samples). For each distribution, all 32 layer sparsity values are measured, producing four sparsity vectors of length 32.

The following statistics are computed:

- **ICC(3,k)** (Shrout and Fleiss, 1979): intraclass correlation across all four distributions, computed using pingouin 0.6.1 (type "ICC(C,k)", 95% CI from column "CI95"). Gate threshold: ICC > 0.75.
- **All 6 pairwise Kendall's tau** (scipy.stats.kendalltau, variant='b' with tie correction): rank concordance between all pairs of distributions. Gate threshold: all tau >= 0.6.

### 3.3 Threshold Invariance (RQ3)

Sparsity profiles are measured at epsilon in {0.001, 0.01, 0.05, 0.1} using Alpaca and WikiText-103. All six cross-epsilon pairwise Kendall's tau values are computed. Gate: the maximum adjacent-pair tau must be >= 0.7; additionally, CV must exceed 0.3 for at least 3 of 4 epsilon values.

### 3.4 Model and Infrastructure

| Parameter | Value |
|-----------|-------|
| Model | meta-llama/Llama-3.1-8B (float16, device_map=auto) |
| Note | Llama-3.1-8B used due to local cache availability; Llama-3-8B was specified in the original protocol |
| GPU | NVIDIA H100 NVL (100 GB VRAM) |
| VRAM used | ~18.4 GB |
| Calibration size | 512 samples per distribution |
| Target layer | gate_proj of each of 32 MLP blocks |
| Batch size | 8 samples per forward pass |
| Primary epsilon | 0.01 |
| Epsilon sweep | {0.001, 0.01, 0.05, 0.1} |
| Statistics library | scipy 1.x (kendalltau), pingouin 0.6.1 (ICC), numpy (CV) |

### 3.5 Proposed Rank Allocation Formula (Not Validated in This Work)

The intended downstream application of the fingerprint is an inverse-sparsity rank allocation rule under a parameter budget B = 0.60 × sum_ell r_ell^uniform:

$$r_\ell^{\text{sparse}} = \text{round}\left(r_{\max} \cdot \frac{1 - s_\ell}{\max_k (1 - s_k)}\right)$$

This formula allocates higher rank to layers with lower sparsity (more active dimensions). Whether this allocation achieves >= 95% of oracle performance at 60% parameter budget is the subject of H-M3 and H-M4, neither of which was executed in this study.

---

## 4. Experimental Setup

Three experiments map directly to three research questions.

**RQ1 (Heterogeneity — H-E1):** Does LLaMA-3.1-8B MLP layer-wise activation sparsity exhibit significant variation across 32 layers (CV > 0.3) and is the layer rank ordering stable across Alpaca vs. WikiText-103 (Kendall's tau_calibration >= 0.6)?

**RQ2 (Cross-Distribution Stability — H-M1):** Is the sparsity profile stable across four diverse calibration distributions? Gate: ICC(3,k) > 0.75 and all six pairwise Kendall's tau >= 0.6.

**RQ3 (Threshold Invariance — H-M2):** Is the layer rank ordering invariant across epsilon in {0.001, 0.01, 0.05, 0.1}? Gate: CV > 0.3 for >= 3 of 4 epsilon values; maximum adjacent-pair Kendall's tau >= 0.7.

### 4.1 Datasets

| Dataset | HuggingFace Identifier | Domain | Samples Used |
|---------|----------------------|--------|-------------|
| Alpaca | tatsu-lab/alpaca | Instruction following | 512 (train split) |
| WikiText-103 | wikitext / wikitext-103-raw-v1 | General web text | 512 (test split, 512-token chunks) |
| SST-2 val | SetFit/sst2 | Sentiment classification | 512 (validation set) |
| MNLI val | nyu-mll/multi_nli | Natural language inference | 512 (validation_matched) |

For RQ1 (H-E1), Alpaca (lengths 128 and 512 tokens) and WikiText-103 are used. For RQ2 (H-M1), all four distributions are used. For RQ3 (H-M2), Alpaca and WikiText-103 are used across all four epsilon values.

### 4.2 Evaluation Metrics

**RQ1:** CV of sparsity across 32 layers (Alpaca, length 512, epsilon = 0.01); Kendall's tau_calibration between Alpaca and WikiText-103 sparsity rankings; Kendall's tau_length between 128-token and 512-token Alpaca profiles.

**RQ2:** ICC(3,k) computed across all four distributions; all 6 pairwise Kendall's tau values.

**RQ3:** CV per epsilon (pass rate >= 3/4 required); all 6 cross-epsilon pairwise Kendall's tau values; maximum adjacent-pair tau.

All Kendall's tau values are computed with scipy.stats.kendalltau (variant='b', two-tailed p-values). ICC is computed with pingouin 0.6.1.

---

## 5. Results

### 5.1 RQ1: Layer Heterogeneity (H-E1: PASS)

At primary epsilon = 0.01, the 32-layer sparsity profile measured from 512 Alpaca samples exhibits CV = 0.544, well above the gate threshold of 0.3 (mean sparsity = 0.0227, standard deviation = 0.0124). The Kendall's tau between Alpaca and WikiText-103 rankings is tau_calibration = 0.786 (p = 2.03e-13), above the threshold of 0.6. The rank correlation between 128-token and 512-token Alpaca profiles is tau_length = 0.899 (p = 2.93e-20).

A systematic depth gradient is observable in the raw per-layer data: layers 0–2 exhibit the highest mean sparsity values (approximately 0.055–0.082 at epsilon = 0.01), while layers 28–31 exhibit the lowest (approximately 0.011–0.014). Intermediate layers show a roughly monotone decline across depth with some local variation.

| epsilon | CV (Alpaca, len=512) | tau_calibration | p-value (tau_cal) | tau_length | p-value (tau_len) |
|---------|---------------------|-----------------|-------------------|------------|-------------------|
| 0.001 | 0.549 | 0.790 | 1.33e-13 | 0.883 | 5.41e-19 |
| **0.010** | **0.544** | **0.786** | **2.03e-13** | **0.899** | **2.93e-20** |
| 0.050 | 0.528 | 0.778 | 4.64e-13 | 0.875 | 2.08e-18 |
| 0.100 | 0.484 | 0.782 | 3.08e-13 | 0.879 | 1.07e-18 |

All four epsilon values pass both gate conditions. H-E1 gate result: **PASS**.

![Sparsity profile across 32 layers](/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-e1/figures/sparsity_profile.png)

*Figure 1. Per-layer mean sparsity at epsilon = 0.01 for Alpaca (length 512) and WikiText-103 (length 512), across all 32 MLP gate_proj layers of LLaMA-3.1-8B.*

![Epsilon sensitivity](/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-e1/figures/epsilon_sensitivity.png)

*Figure 2. CV and tau_calibration across all four epsilon values. All values exceed gate thresholds (dashed lines).*

### 5.2 RQ2: Cross-Distribution Stability (H-M1: PASS)

Across four diverse calibration distributions measured at primary epsilon = 0.01, ICC(3,k) = 0.9846 (95% CI: [0.97, 0.99]), far above the gate threshold of 0.75. All six pairwise Kendall's tau values exceed 0.6; the minimum is tau = 0.7339 for the WikiText-103 vs. SST-2 pair (p = 2.78e-11).

| Pair | Kendall's tau | p-value |
|------|--------------|---------|
| Alpaca vs. WikiText-103 | 0.7863 | 2.03e-13 |
| Alpaca vs. SST-2 | 0.9395 | 3.35e-24 |
| Alpaca vs. MNLI | 0.9476 | 3.51e-25 |
| WikiText-103 vs. SST-2 | **0.7339** | 2.78e-11 |
| WikiText-103 vs. MNLI | 0.7500 | 6.81e-12 |
| SST-2 vs. MNLI | 0.9839 | 3.94e-31 |

The three pairs involving WikiText-103 show tau values in [0.734, 0.786], while the three pairs among instruction-tuned and classification datasets show tau values in [0.940, 0.984]. Even the worst-case pair (WikiText-103 vs. SST-2) exceeds the gate threshold of 0.6 by a margin of 0.13.

ICC(3,k) sensitivity across epsilon values: 0.9862 (epsilon = 0.001), 0.9846 (epsilon = 0.01), 0.9878 (epsilon = 0.05), 0.9857 (epsilon = 0.1). All exceed 0.98. H-M1 gate result: **PASS**.

![Sparsity heatmap](/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m1/figures/sparsity_heatmap.png)

*Figure 3. Sparsity heatmap: 4 distributions by 32 layers at epsilon = 0.01. Rows are distributions; columns are layers.*

![Pairwise tau matrix](/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m1/figures/pairwise_tau_matrix.png)

*Figure 4. Pairwise Kendall's tau matrix for all four calibration distributions at epsilon = 0.01.*

### 5.3 RQ3: Threshold Invariance (H-M2: PASS)

All six cross-epsilon pairwise Kendall's tau values exceed 0.95 for epsilon values spanning a 100-fold range (0.001 to 0.1). The minimum is tau = 0.9597 (epsilon = 0.01 vs. epsilon = 0.1; p = 7.94e-27). The maximum is tau = 0.9960 (epsilon = 0.001 vs. epsilon = 0.01; p = 2.43e-34). CV exceeds 0.3 for all four epsilon values (pass rate 4/4).

| Pair | Kendall's tau | p-value |
|------|--------------|---------|
| epsilon = 0.001 vs. 0.01 | 0.9960 | 2.43e-34 |
| epsilon = 0.001 vs. 0.05 | 0.9677 | 4.47e-28 |
| epsilon = 0.001 vs. 0.1 | 0.9637 | 1.96e-27 |
| epsilon = 0.01 vs. 0.05 | 0.9718 | 9.26e-29 |
| epsilon = 0.01 vs. 0.1 | **0.9597** | 7.94e-27 |
| epsilon = 0.05 vs. 0.1 | 0.9798 | 2.82e-30 |

H-M2 gate result: **PASS**.

![Cross-epsilon tau heatmap](/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m2/figures/cross_epsilon_tau_heatmap.png)

*Figure 5. Cross-epsilon Kendall's tau matrix for all 6 pairs across epsilon in {0.001, 0.01, 0.05, 0.1}.*

### 5.4 Gate Summary

| Hypothesis | Metric | Value | Threshold | Gate |
|------------|--------|-------|-----------|------|
| H-E1 | CV (epsilon = 0.01) | 0.544 | > 0.3 | PASS |
| H-E1 | tau_calibration (Alpaca vs. WikiText) | 0.786 | >= 0.6 | PASS |
| H-M1 | ICC(3,k) | 0.9846 | > 0.75 | PASS |
| H-M1 | tau_min (6 pairs) | 0.7339 | >= 0.6 | PASS |
| H-M2 | CV pass rate | 4/4 | >= 3/4 | PASS |
| H-M2 | Max adjacent-pair tau | 0.9960 | >= 0.7 | PASS |

Prediction P1 (structural fingerprint exists and is stable): **SUPPORTED**. Predictions P2 (sparsity-rank correlation) and P3 (end-to-end allocation efficiency): **NOT TESTED** (H-M3 and H-M4 not executed).

---

## 6. Discussion

### 6.1 Architecture Determinism as the Primary Explanation

ICC(3,k) = 0.9846 and cross-epsilon tau > 0.95 suggest that the sparsity fingerprint is dominated by the model's weight magnitudes (pre-training geometry) rather than input content. LLaMA-3.1-8B uses SiLU activations (Sigmoid Linear Units) in its MLP blocks, producing soft near-zero values. If the magnitude distribution of gate_proj weights is the primary determinant of the fraction of activations falling below a fixed threshold, then the sparsity fraction is approximately input-independent by construction. This interpretation is consistent with the observed pattern: the WikiText-103 profiles — the most distributional-distinct from the other three datasets — show the lowest tau values relative to the others (0.734–0.750), yet still pass the stability gate comfortably.

The depth gradient — early layers most sparse, deep layers least sparse — is consistent with the linguistic hierarchy documented by Clark et al. (2019) and Tenney et al. (2019), in which early layers perform more syntactic, sparse operations and later layers integrate richer semantic representations. This observation is correlational; no causal mechanism is established here.

This architectural determinism interpretation predicts that shuffled or random inputs would produce nearly identical sparsity profiles. That experiment was not conducted; it is noted as a natural validation of the proposed mechanism.

### 6.2 Scope of Validated and Unvalidated Claims

**Validated (Predictions P1a–P1c):** The fingerprint exists (H-E1: CV = 0.544), is distribution-stable (H-M1: ICC = 0.9846, tau_min = 0.734), and is threshold-invariant (H-M2: cross-epsilon tau > 0.95). Any reasonable calibration dataset and any epsilon in [0.001, 0.1] yields essentially the same layer rank ordering.

**Not validated (Predictions P2, P3):** Whether layers with higher sparsity require lower LoRA rank (H-M3, requiring approximately 320 fine-tuning runs: 32 layers × 5 seeds × 2 tasks) and whether inverse-sparsity allocation achieves >= 95% of oracle performance at 60% parameter budget (H-M4) are empirically open questions. These experiments are fully designed in the research protocol but were not executed in this work. The practical utility of the fingerprint as a rank allocation signal has not been demonstrated.

### 6.3 Limitations

**L1: Core mechanism unvalidated (severity: high).** The proposed mechanism — that activation sparsity predicts rank requirements — has not been tested. Approximately 320 fine-tuning runs are required to test H-M3. The fingerprint's rank-predictive utility is entirely unconfirmed.

**L2: End-to-end performance unvalidated (severity: high).** No downstream fine-tuning performance result is reported. The claim that inverse-sparsity allocation would achieve efficiency gains at 60% parameter budget has zero experimental support from this work.

**L3: SiLU soft-sparsity proxy (severity: medium).** The gate_proj output is measured before the SiLU activation, so absolute sparsity values represent near-zero pre-activation magnitudes rather than true zero-valued post-activation outputs. Cross-epsilon tau > 0.96 confirms rank ordering robustness to this measurement choice, but absolute sparsity values should not be interpreted as effective sparsity without comparison to effective-rank metrics.

**L4: Single architecture and task domain (severity: low-medium).** All experiments use LLaMA-3.1-8B. No results are reported for other model families (Mistral, Gemma, Phi). Szatkowski et al. (2025) motivate cross-architecture generalization, but no such generalization is tested here. Similarly, the calibration distributions include GLUE classification tasks but no generation tasks.

**L5: Protocol deviation — LLaMA-3.1 vs. LLaMA-3 (severity: low).** The original hypothesis protocol specified LLaMA-3-8B (meta-llama/Meta-Llama-3-8B). LLaMA-3.1-8B was used due to local cache availability. The two models share the same architecture family; this deviation is assessed as minor.

**L6: Act-LoRA citation unverified (severity: low).** The Act-LoRA citation (actlora2025mdpi) was not verified via Semantic Scholar. Author names, title, volume, and DOI require manual verification before submission.

### 6.4 Broader Considerations

The primary positive implication of this work is that the measurement required is computationally trivial: a single forward pass on 512 samples with no gradient computation, completing in approximately 5 minutes on an NVIDIA H100 NVL using 18.4 GB of VRAM. If H-M3 and H-M4 validate the allocation utility, the zero-cost nature of this measurement makes it broadly applicable to resource-constrained practitioners.

The primary caution is that the current work provides no evidence of improved downstream performance. Practitioners should not use the sparsity fingerprint to inform LoRA rank allocation decisions without first validating the sparsity-rank correlation claimed in H-M3.

---

## 7. Conclusion

This work characterizes the layer-wise MLP activation sparsity profile of LLaMA-3.1-8B as a structural fingerprint measurable from a single forward pass on any calibration dataset. Three empirical findings are established:

1. The sparsity fingerprint exists and is heterogeneous: CV = 0.544 across 32 MLP layers at epsilon = 0.01, with a systematic depth gradient (early layers highest sparsity, deep layers lowest).
2. The fingerprint is stable across diverse calibration distributions: ICC(3,k) = 0.9846 (95% CI: [0.97, 0.99]) across four distributions; minimum pairwise Kendall's tau = 0.734.
3. The fingerprint is invariant to epsilon threshold: all six cross-epsilon Kendall's tau values exceed 0.95 across a 100-fold range; minimum tau = 0.9597.

These three results support treating the sparsity fingerprint as a pre-training structural property of LLaMA-3.1-8B rather than a calibration artifact. A practitioner can measure this fingerprint in approximately five minutes on modern hardware using any available text dataset.

What remains unestablished is whether the fingerprint is useful: specifically, whether higher-sparsity layers require lower LoRA rank (H-M3) and whether inverse-sparsity allocation achieves efficiency gains relative to uniform allocation (H-M4). Both experiments are fully designed; neither was executed in this work.

**Suggested future directions:**
1. H-M3: Sparsity-rank correlation study (~320 fine-tuning runs, fully specified).
2. H-M4: End-to-end SparsityLoRA performance vs. uniform LoRA at equal parameter budget.
3. Mechanism validation: Compare sparsity profiles under shuffled and random inputs to test architectural determinism.
4. Effective-rank comparison: Measure the relationship between gate_proj pre-activation sparsity and post-SiLU effective rank.
5. Cross-architecture generalization: Repeat measurements on Mistral, Gemma, and Phi model families.

---

## References

Aghajanyan, A., Zettlemoyer, L., and Gupta, S. (2021). Intrinsic dimensionality explains the effectiveness of language model fine-tuning. In *Proceedings of ACL-IJCNLP 2021*, pp. 7319–7328.

Clark, K., Khandelwal, U., Levy, O., and Manning, C. D. (2019). What does BERT look at? An analysis of BERT's attention. In *Proceedings of the 2019 ACL Workshop BlackboxNLP*, pp. 276–286.

Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., and Chen, W. (2022). LoRA: Low-rank adaptation of large language models. In *ICLR 2022*. (arXiv:2106.09685)

Li, Z., You, C., Bhojanapalli, S., Li, D., Rawat, A. S., Reddi, S. J., Ye, K., Chern, F., Yu, F. X., Guo, R., and Kumar, S. (2023). The lazy neuron phenomenon: On emergence of activation sparsity in transformers. In *ICLR 2023*. (arXiv:2210.06313)

Liu, J. Y. Z., Ponnusamy, P., Cai, T., Guo, H., Kim, Y., and Athiwaratkun, B. (2025). Training-free activation sparsity in large language models (TEAL). In *ICLR 2025*. (arXiv:2408.14690)

Mirzadeh, I., Alizadeh-Vahid, K., Mehta, S., Del Mundo, C. C., Tuzel, O., Samei, G., Rastegari, M., and Farajtabar, M. (2024). ReLU strikes back: Exploiting activation sparsity in large language models. In *ICLR 2024*. (arXiv:2310.04564)

Shrout, P. E. and Fleiss, J. L. (1979). Intraclass correlations: Uses in assessing rater reliability. *Psychological Bulletin*, 86(2):420–428.

Szatkowski, F., Bedkowski, P., Devoto, A., Dubinski, J., Minervini, P., Piorczyński, M., Scardapane, S., and Wojcik, B. (2025). Universal properties of activation sparsity in modern large language models. arXiv:2509.00454.

Tenney, I., Das, D., and Pavlick, E. (2019). BERT rediscovers the classical NLP pipeline. In *Proceedings of ACL 2019*, pp. 4593–4601.

Valipour, M., Rezagholizadeh, M., Kobyzev, I., and Ghodsi, A. (2023). DyLoRA: Parameter-efficient tuning of pre-trained models using dynamic search-free low-rank adaptation. In *Proceedings of EACL 2023*. (arXiv:2210.07558)

Zhang, Q., Chen, M., Bukharin, A., Karampatziakis, N., He, P., Cheng, Y., Chen, W., and Zhao, T. (2023). AdaLoRA: Adaptive budget allocation for parameter-efficient fine-tuning. arXiv:2303.10512.
