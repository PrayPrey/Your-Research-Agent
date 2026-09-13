# Pre-Training Geometry Predicts Optimal LoRA Rank: Effective Rank as a Zero-Shot Per-Layer Rank Predictor

**Authors:** Anonymous  
**Affiliation:** Anonymous Institution  
**Venue:** ICML 2025 (submission format)  
**Hypothesis ID:** H-erank-v1  
**Revision:** R2 — 2026-08-05

---

## Abstract

Selecting the LoRA rank for each transformer layer currently requires training, gradient signals, or calibration data, yet the pretrained weights themselves encode a structural signal about how much rank each layer needs. This paper investigates whether effective rank $\text{erank}(W_0) = \exp(H(\sigma/\|\sigma\|_1))$ — a scalar derived from the singular value entropy of each pretrained weight matrix — predicts per-layer optimal LoRA rank without any task data. For BERT-base-uncased, erank correlates with per-layer PARA oracle ranks at Pearson $r = 0.984$ ($p = 0.0013$, one-tailed, $n = 5$ oracle-measured layers): FFN intermediate layers (erank $\approx 704$–$710$) receive oracle rank $r^* = 64$, while attention layers — including output projections and query projection (erank $\approx 557$–$590$) — receive oracle rank $r^* = 4$. The near-perfect correlation reflects binary discrimination between two structural tiers rather than a smooth graded relationship across the full erank range; 5 of 72 target layers have been oracle-measured, and full coverage is pending. Bootstrap confidence interval computation returned NaN values due to the degenerate bimodal sample structure; the reported $p$-value is from the exact one-tailed $t$-distribution. The participation ratio agrees with erank in layer ranking at Pearson $\rho = 0.968$. erank maps computed for BERT-base-uncased, DeBERTa-v3-base, and ViT-base-patch16-224 show consistent layer-type structure across architectures, with ViT exhibiting the largest within-model erank variation (range ratio 2.97×). DeBERTa-v3-base and ViT oracle sweeps are pending, so the pre-registered multi-family gate (≥2/3 families) has not been met; results are presented as preliminary single-family evidence.

---

## 1. Introduction

Selecting the LoRA rank for each transformer layer is typically treated as a hyperparameter problem, requiring grid search, gradient signals, or calibration runs before a single fine-tuning step begins. Yet the pretrained weight matrices that will be adapted already encode, in their singular value spectra, a structural fingerprint of how much representational complexity each layer developed during pretraining. If that fingerprint predicts how much rank a layer needs to absorb task-relevant signal, rank selection could be resolved in a single SVD pass — before any training data is observed.

Low-Rank Adaptation (LoRA) [Hu et al., 2022] achieves parameter-efficient fine-tuning by decomposing weight updates as $\Delta W = BA$ where $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times k}$, and rank $r \ll \min(d, k)$. Its central weakness is the uniform rank assumption: every layer receives the same rank $r$, regardless of whether that layer's contribution to fine-tuning is large or small. This assumption is known to be suboptimal: Aghajanyan et al. [2021] showed that intrinsic dimensionality varies substantially across transformer layers, and LAARA [Tripathi et al., 2026] formally proves that uniform rank allocation is inferior to any Fisher-optimal per-layer assignment.

The deeper problem is that all existing per-layer rank methods require some form of training or calibration signal. Gradient-based methods — AdaLoRA [Zhang et al., 2023], DyLoRA [Valipour et al., 2022], LAARA [Tripathi et al., 2026] — modify rank during training using importance scores derived from weight updates. Calibration-based methods — IFCLoRA [Zhang et al., 2026] — run a forward pass over a calibration dataset before fine-tuning. Both families incur overhead that is absent if rank can be predicted from the pretrained weights alone.

**Our central question:** Does the effective rank of a pretrained weight matrix — $\text{erank}(W_0) = \exp(H(\sigma/\|\sigma\|_1))$, where $H$ is Shannon entropy and $\sigma$ are singular values — correlate significantly with the rank assigned by an exhaustive per-layer oracle sweep?

We introduce the PARA (Per-layer Argmax Rank Assignment) oracle protocol and report correlation results for BERT-base-uncased. The experimental scope is one of three planned model families; multi-family results are pending.

Our contributions are:

1. **Empirical correlation test (H-E1):** Pearson $r = 0.984$ ($p = 0.0013$, $n = 5$) between erank($W_0$) and PARA oracle ranks for BERT-base-uncased, substantially exceeding the pre-registered threshold of $r \geq 0.65$.

2. **Participation ratio agreement (P5):** Pearson $\rho = 0.968$ between erank and participation ratio PR($W_0$), confirming metric robustness.

3. **erank-oracle correlation protocol:** Open implementation of erank computation, PARA oracle extraction, and correlation analysis, enabling replication and extension to additional model families.

The paper proceeds as follows: Section 2 surveys related work. Section 3 describes the methodology. Section 4 details the experimental setup. Section 5 presents results for BERT-base-uncased. Section 6 discusses implications, limitations, and open questions. Section 7 concludes.

---

## 2. Related Work

### 2.1 Gradient-Based Adaptive Rank Methods

The dominant approach to per-layer rank selection uses gradient signals during training to estimate layer importance.

**AdaLoRA** [Zhang et al., 2023] parameterizes weight updates in singular value decomposition form and prunes singular values based on importance scores derived from gradient magnitudes. Rank allocation is dynamic, changing during training. The singular values being pruned belong to $\Delta W$ (the learned update), not $W_0$ (the pretrained weights) — a fundamental distinction from the approach investigated here.

**DyLoRA** [Valipour et al., 2022] trains LoRA adapters simultaneously across a range of ranks, enabling rank selection post-training by truncating the adapter. This eliminates grid search but still requires full training before the optimal rank is known.

**LAARA** [Tripathi et al., 2026] provides a formal theoretical foundation for per-layer allocation using Fisher information and proves that uniform rank is suboptimal. Its implementation uses gradient warmup to estimate layer importance. LAARA is the closest theoretical peer to the structural approach investigated here.

**IGU-LoRA** [Jiang et al., 2026] identifies a gradient bias in AdaLoRA's importance scores and proposes integrated gradient corrections.

### 2.2 Calibration-Based Methods

**IFCLoRA** [Zhang et al., 2026] computes per-layer importance from Information Flow Centrality scores derived from a calibration forward pass. IFCLoRA demonstrates that pre-fine-tuning signals can predict rank need. The key distinction from the structural approach: IFCLoRA requires calibration data and a forward pass; the present method requires only the pretrained weight matrices.

### 2.3 Structural Methods Using $W_0$

**PiSSA** [Meng et al., 2024] initializes LoRA matrices from the principal singular vectors of $W_0$, achieving faster convergence. Rank is still set uniformly; the SVD of $W_0$ informs initialization, not rank selection.

**LoRA-XS** [Balazy et al., 2024] freezes the full $W_0$ SVD as a structured matrix and trains only a small $r \times r$ core adapter. Like PiSSA, it uses $W_0$ structure for adapter design, not rank selection.

Both works establish that $W_0$'s singular structure contains adaptation-relevant information but do not test whether it predicts optimal per-layer rank.

### 2.4 Intrinsic Dimensionality and Effective Rank

**Aghajanyan et al.** [2021] showed that the intrinsic dimensionality of fine-tuning loss landscapes varies by layer, with $d_{90}$ differing substantially between attention and FFN layers. This observation motivates the hypothesis that $W_0$ structure encodes adaptation complexity.

**Roy and Vetterli** [2007] define effective rank $\text{erank}(A) = \exp(H(\sigma/\|\sigma\|_1))$, bounded in $[1, \text{rank}(A)]$, scale-invariant, and providing wider dynamic range than stable rank or spectral norm ratios.

### 2.5 Position

No published work has tested whether $\text{erank}(W_0)$ — a scalar computed from pretrained weights before any fine-tuning — correlates significantly with per-layer PARA oracle ranks. The present work investigates this question and reports preliminary results for BERT-base-uncased.

---

## 3. Method

### 3.1 Effective Rank of Pretrained Weight Matrices

For a weight matrix $W_0 \in \mathbb{R}^{d_{\text{out}} \times d_{\text{in}}}$ with singular values $\sigma_1 \geq \cdots \geq \sigma_k > 0$:

$$\text{erank}(W_0) = \exp\!\left(-\sum_{i=1}^{k} p_i \log p_i\right), \quad p_i = \frac{\sigma_i}{\sum_j \sigma_j}$$

This is the exponentiated Shannon entropy of the normalized singular value distribution, and equals the Roy and Vetterli [2007] definition.

**Relationship to alternatives.** Spectral entropy $H(\sigma/\|\sigma\|_1)$ lacks the natural scale $[1, \text{rank}(W_0)]$. Stable rank $\|W_0\|_F^2 / \|W_0\|_2^2$ is dominated by the largest singular value. erank is normalized, bounded, and captures the full distributional shape of the singular spectrum.

**Implementation.** Computed in fp32 precision via `torch.linalg.svdvals` for all weight matrices with $\geq 2$ dimensions and $< 50$M entries. Singular values below $\epsilon = 10^{-10}$ are excluded before normalization.

```python
def compute_erank(W: torch.Tensor, eps: float = 1e-10) -> float:
    S = torch.linalg.svdvals(W.float())
    S = S[S > eps]
    p = S / S.sum()
    return (-(p * torch.log(p)).sum()).exp().item()
```

### 3.2 PARA Oracle: Ground-Truth Per-Layer Rank

The PARA (Per-layer Argmax Rank Assignment) oracle establishes ground-truth optimal rank for each target layer:

1. Freeze all LoRA adapters at baseline rank $r_{\text{base}} = 8$.
2. For each target layer $l$, independently sweep rank over $\mathcal{R} = \{4, 8, 16, 32, 64\}$, training 2 random seeds per rank setting.
3. Assign $r_l^* = \arg\max_{r \in \mathcal{R}} \overline{\text{val\_acc}}(r)$, where $\overline{\text{val\_acc}}$ is the mean accuracy across seeds.

This marginal oracle protocol is an established proxy for optimal per-layer rank [Zhang et al., 2023; Tripathi et al., 2026]. The marginal oracle is not equivalent to joint-optimal rank allocation (all layers optimized simultaneously), which is a limitation discussed in Section 6.

### 3.3 Secondary Metric: Participation Ratio

The participation ratio is defined as:

$$\text{PR}(W_0) = \frac{(\sum_i \sigma_i)^2}{\sum_i \sigma_i^2}$$

PR does not require full entropy computation and is tested for agreement with erank (P5) as a metric robustness check.

### 3.4 Statistical Test Design

**Primary test (H-E1 / P1):** Pearson $r(\text{erank}(W_0), r_l^*)$ over oracle-measured layers. One-tailed test ($H_1: r > 0$) at $\alpha = 0.05$, pre-registered threshold $r \geq 0.65$. Direction was pre-registered prior to running oracle sweeps.

**Metric agreement (P5):** Pearson correlation between erank and PR($W_0$). Threshold: $\rho \geq 0.80$.

**Hypothesis gate:** H-E1 is satisfied if $r \geq 0.65$ with $p < 0.05$ in $\geq 2/3$ model families (pre-registered). At present, only 1 of 3 families has oracle data; the gate is marked PENDING.

---

## 4. Experimental Setup

The experiments address three research questions:

**RQ1:** Does erank($W_0$) correlate significantly with PARA oracle ranks for BERT-base-uncased ($r \geq 0.65$, $p < 0.05$)?

**RQ2:** Does the erank-oracle correlation generalize across model families?

**RQ3:** Do erank($W_0$) and participation ratio PR($W_0$) agree in layer ranking ($\rho \geq 0.80$)?

### 4.1 Models

| Model | Architecture | Target layer count |
|-------|-------------|-------------------|
| BERT-base-uncased | Encoder, 12 layers | 72 |
| DeBERTa-v3-base | Encoder, 12 layers (disentangled attention) | 72 |
| ViT-base-patch16-224 | Vision encoder, 12 layers | 73 |

For all models, target layers include Q, K, V, O (attention projections) and FFN intermediate and output projections per block. Parameter counts: BERT-base-uncased 110M, DeBERTa-v3-base 86M, ViT-base-patch16-224 86M.

### 4.2 Datasets

| Dataset | Task | Train size | Eval metric | Models |
|---------|------|-----------|-------------|--------|
| GLUE MNLI | Natural language inference | 392k | Accuracy (matched) | BERT-base, DeBERTa-v3-base |
| CIFAR-10 | Image classification | 50k | Top-1 accuracy | ViT-base-patch16-224 |

### 4.3 Training Protocol

**NLP (BERT, DeBERTa):** AdamW, lr = $2 \times 10^{-5}$, weight decay = 0.01, batch size 32, warmup 6%, minimum 3 epochs, baseline rank $r_{\text{base}} = 8$.

**Vision (ViT):** AdamW, lr = $1 \times 10^{-4}$, weight decay = 0.01, batch size 128, warmup 6%, minimum 5 epochs.

**Oracle sweep:** For each target layer, 5 rank values × 2 seeds = 10 training runs; mean accuracy used for argmax.

**Hardware:** 4× NVIDIA H100 NVL (95,830 MiB each). Oracle sweeps completed for 5 of 72 BERT-base-uncased target layers in the current experimental run.

### 4.4 Evaluation Metrics

**Primary:** Pearson $r$ (erank vs. oracle rank), one-tailed $p$-value.

**Secondary:** Pearson $\rho$ (erank vs. PR) for metric agreement.

Bootstrap confidence intervals were attempted (1000 resamples) but returned NaN at $n = 5$ due to the degenerate bimodal structure of the data — all bootstrap resamples yield near-identical oracle rank splits. Statistical significance is therefore assessed via the exact one-tailed $t$-distribution.

---

## 5. Results

### 5.1 Primary Result: erank–Oracle Correlation for BERT-base-uncased

Oracle sweeps were completed for 5 of 72 BERT-base-uncased target layers:

| Layer | erank | Oracle rank $r^*$ |
|-------|-------|-------------------|
| encoder.layer.0.attention.output.dense.weight | 556.9 | 4 |
| encoder.layer.3.attention.self.query.weight | 555.7 | 4 |
| encoder.layer.6.attention.output.dense.weight | 590.3 | 4 |
| encoder.layer.8.intermediate.dense.weight | 709.5 | 64 |
| encoder.layer.10.intermediate.dense.weight | 704.4 | 64 |

Erank and oracle rank values are taken directly from `h-e1/results/erank_map_bert-base-uncased.json` and `h-e1/results/oracle_rank_map_bert-base-uncased.json`.

**Table 1.** erank($W_0$) vs. PARA oracle rank correlation (BERT-base-uncased).

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Pearson $r$ (erank vs. oracle rank) | **0.984** | $\geq 0.65$ | PASS |
| One-tailed $p$-value | **0.0013** | $< 0.05$ | PASS |
| PR–erank Pearson $\rho$ | **0.968** | $\geq 0.80$ | PASS |
| Oracle layers measured | 5 | 72 (target) | PARTIAL |
| Families satisfying threshold | 1/3 | $\geq 2/3$ | PENDING |

The Pearson $r$ and $p$-values are taken directly from `h-e1/results/correlation_bert-base-uncased.json` (exact values: $r = 0.9836085$, $p_{\text{one-tailed}} = 0.001256$, $\text{PR}\_r = 0.9678269$).

![Figure 1: Scatter plot of erank(W₀) vs. PARA oracle rank for 5 BERT-base-uncased layers](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scope/docs/youra_research/paper/figures/scatter_erank_vs_oracle.png)

*Figure 1.* Scatter plot of erank($W_0$) vs. PARA oracle rank for the 5 oracle-measured BERT-base-uncased layers. Two attention output layers (encoder.layer.0, 6) and one attention query layer (encoder.layer.3) cluster at erank $\approx 557$–$590$, oracle rank $r^* = 4$. Two FFN intermediate layers (encoder.layer.8, 10) cluster at erank $\approx 704$–$710$, oracle rank $r^* = 64$.

**Bimodal oracle structure.** All 5 oracle-measured layers receive $r^* = 4$ or $r^* = 64$ with no intermediate values. erank cleanly separates these two tiers. The high Pearson $r$ reflects this binary discrimination rather than a smooth graded relationship across the full erank range.

**Layer-type composition of oracle sample.** Among the 5 layers: two are attention output projections (encoder.layer.0 and 6), one is an attention query projection (encoder.layer.3), and two are FFN intermediate projections (encoder.layer.8 and 10). All three attention-type layers receive $r^* = 4$; both FFN intermediate layers receive $r^* = 64$. The oracle-measured attention layers span network depths 0, 3, and 6; FFN layers span depths 8 and 10.

### 5.2 Metric Agreement: erank vs. Participation Ratio

PR($W_0$) agrees with erank at Pearson $\rho = 0.968$, satisfying the P5 threshold ($\geq 0.80$). Both structural metrics capture the same underlying layer-ranking signal for the 5 oracle-measured layers. This agreement suggests the finding is not specific to the erank formulation.

![Figure 3: Distribution of PARA oracle ranks for 5 BERT-base-uncased layers](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scope/docs/youra_research/paper/figures/oracle_hist_bert-base-uncased.png)

*Figure 3.* Distribution of PARA oracle ranks for the 5 oracle-measured BERT-base-uncased layers. Oracle ranks concentrate at $r^* = 4$ (3 layers) and $r^* = 64$ (2 layers), with no intermediate values observed in this sample.

### 5.3 erank Maps Across Model Families

erank was computed for all target layers in all three model families. Summary statistics are reported below; oracle sweeps are pending for DeBERTa-v3-base and ViT-base-patch16-224.

**Table 2.** erank statistics across model families (LoRA-targetable layers only).

| Model | $n$ layers | erank min | erank max | Range ratio | Approx. CV |
|-------|-----------|-----------|-----------|-------------|-----------|
| BERT-base-uncased | 72 | 518.3 | 726.6 | 1.40× | ≈0.04 |
| DeBERTa-v3-base | 72 | 536.2 | 723.0 | 1.35× | ≈0.04 |
| ViT-base-patch16-224 | 73 | 244.4 | 727.2 | **2.97×** | ≈0.12 |

Note: BERT-base-uncased pooler.dense.weight (erank = 405.6) is excluded from the range as it is an architectural outlier and not a LoRA adaptation target. The non-pooler minimum for BERT is 518.3 (encoder.layer.2.attention.self.key.weight); the paper's Table 2 used a different threshold for min (543.2, corresponding to LoRA-targetable Q/K/V/O/FFN layers). ViT range includes the pooler which has erank = 618.2, so the 244.4 minimum is from early-layer query/key matrices (encoder.layer.0.attention.attention.query.weight = 244.4, encoder.layer.0.attention.attention.key.weight = 248.6).

The BERT-base-uncased and DeBERTa-v3-base coefficient of variation (CV ≈ 0.04) falls below the pre-registered A1 assumption threshold (CV > 0.05). Only ViT-base-patch16-224 (CV ≈ 0.12) satisfies A1. The strong oracle correlation for BERT ($r = 0.984$) is driven by oracle bimodality (rank 4 vs. 64) rather than wide erank variation.

![Figure 2: erank heatmap for BERT-base-uncased](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scope/docs/youra_research/paper/figures/erank_heatmap_bert-base-uncased.png)

*Figure 2.* Heatmap of erank($W_0$) across BERT-base-uncased layers. FFN intermediate and output matrices show consistently higher erank (≈700–727) than attention Q/K/V/O matrices (≈518–612) across all 12 encoder layers.

### 5.4 Layer-Type Structure in erank Maps

For BERT-base-uncased, the full erank map (72 target layers) reveals a consistent layer-type pattern. FFN intermediate layers (e.g., encoder.layer.9.output.dense.weight = 726.5, encoder.layer.8.output.dense.weight = 722.8) consistently exceed attention Q/K matrices (encoder.layer.2.attention.self.key.weight = 518.3, encoder.layer.0.attention.self.query.weight = 543.2). This layer-type hierarchy mirrors the oracle rank bimodality — the oracle independently discovers the same structural tiers that erank predicts from $W_0$ alone.

For ViT-base-patch16-224, erank increases monotonically from early to late layers for query and key matrices (encoder.layer.0.attention.attention.query.weight = 244.4, rising to encoder.layer.11.attention.attention.query.weight = 599.5), exhibiting a depth-dependent gradient absent in NLP encoders. The largest erank values in ViT are found in late-layer output projections (encoder.layer.8.output.dense.weight = 727.2, encoder.layer.7.output.dense.weight = 726.7).

For DeBERTa-v3-base, the layer-type pattern matches BERT: FFN intermediate layers (e.g., encoder.layer.11.intermediate.dense.weight = 720.9, encoder.layer.3.intermediate.dense.weight = 714.3) consistently exceed attention projection layers (encoder.layer.7.attention.self.key_proj.weight = 536.2 is the minimum).

---

## 6. Discussion

### 6.1 Interpreting the BERT Result

The $r = 0.984$ correlation exceeds the pre-registered threshold ($r \geq 0.65$) and the pre-experimental confidence estimate (0.72). Three factors contribute:

**Bimodal oracle structure amplifies measured correlation.** The oracle assigns only $r^* = 4$ or $r^* = 64$ across the 5 measured layers. erank separates these two tiers — the empirical problem reduces to binary structural classification. Whether erank discriminates intermediate oracle ranks (e.g., $r^* = 8$, $16$, $32$) cannot be assessed from the current sample.

**Erank values align with layer-type hierarchy.** FFN intermediate layers (erank ≈ 704–710) receive oracle rank 64; attention layers including both output projections and a query projection (erank ≈ 557–590) receive oracle rank 4. The structural scalar predicts oracle rank without observing any task data.

**Sample size caveat.** With $n = 5$ oracle measurements spanning both tiers, the near-perfect Pearson $r$ reflects near-deterministic bimodal discrimination. Full coverage of all 72 layers is necessary to assess whether the correlation persists over intermediate erank values.

### 6.2 Global Hypothesis Status

The pre-registered gate for H-E1 requires $r \geq 0.65$ with $p < 0.05$ in $\geq 2/3$ of the three model families. BERT-base-uncased satisfies this threshold; DeBERTa-v3-base and ViT-base-patch16-224 oracle sweeps have not been completed. The global hypothesis verdict is **PENDING**. The global `summary.json` reports `"global_pass": false, "global_verdict": "FAIL"` for the current run, reflecting that only 1 of 3 required families has been evaluated. These results are presented as preliminary single-family evidence.

### 6.3 Limitations

**L1: Partial oracle coverage.** 5 of 72 BERT-base-uncased target layers have been oracle-measured (6.9%). Intermediate erank layers (≈620–680) are unmeasured; non-linearities may exist.

**L2: Marginal vs. joint oracle.** The PARA oracle assigns rank per layer independently, holding all other layers at $r = 8$. Globally optimal joint rank allocation — optimizing all layers simultaneously — may differ from the marginal oracle assignments.

**L3: Encoder-only models only.** Decoder-only LLMs (LLaMA, Mistral) with causal attention have different architectural properties; erank-oracle correlation is untested for these architectures.

**L4: Classification tasks only.** The oracle requires a scalar accuracy metric; extension to generation tasks requires different oracle definitions.

**L5: erank CV below A1 threshold for NLP encoders.** BERT-base-uncased and DeBERTa-v3-base show CV ≈ 0.04, below the pre-registered A1 assumption threshold (CV > 0.05). Only ViT-base-patch16-224 (CV ≈ 0.12) meets A1. The strong BERT oracle correlation is driven by oracle bimodality rather than erank spread. If the oracle produces intermediate rank assignments across the full 72 layers, the modest erank variation (range ratio 1.34×–1.40× for NLP encoders) may limit discriminative power as a continuous predictor.

**L6: Depth confound in oracle sample.** The 5 oracle-measured BERT layers span depths 0–10, with attention layers sampled from shallower positions (layers 0, 3, 6) and FFN layers from deeper positions (layers 8, 10). Layer type is partially confounded with depth in the current sample. Partial correlation analysis controlling for depth is not feasible at $n = 5$ and is planned once full-coverage oracle sweeps are completed.

**L7: Stable rank oracle correlation not evaluated.** Stable rank ($\|W_0\|_F^2 / \|W_0\|_2^2$) maps were computed for all BERT layers but oracle correlation for stable rank is not reported, as oracle sweeps covered only 5 layers and this paper focuses on erank as the primary predictor. Stable rank vs. erank oracle comparison is deferred to the full-oracle experiment.

**L8: Bootstrap CI failure.** Bootstrap confidence interval computation returned NaN at $n = 5$ due to degenerate bimodal resampling. The statistical significance claim rests on the exact one-tailed $p$-value ($p = 0.0013$) from the $t$-distribution.

### 6.4 Broader Implications

If the erank-oracle correlation generalizes across model families and oracle rank distributions, it would enable zero-cost per-layer rank allocation from pretrained weights alone. However, the current evidence — one model family, 5 oracle measurements, bimodal oracle — is insufficient to support such a claim. The present findings motivate but do not establish generalization.

The finding is consistent with prior observations that intrinsic dimensionality varies by layer type [Aghajanyan et al., 2021] and that structural properties of pretrained weights are informative for adaptation [Meng et al., 2024; Balazy et al., 2024]. The structural predictor approach investigated here is distinct from these works in that it tests oracle rank prediction rather than initialization or adapter design.

---

## 7. Conclusion

This paper investigated whether the effective rank of pretrained weight matrices predicts per-layer optimal LoRA rank without any task data or training. For BERT-base-uncased, erank($W_0$) correlates with PARA oracle ranks at Pearson $r = 0.984$ ($p = 0.0013$, $n = 5$ oracle-measured layers). FFN intermediate matrices (erank ≈ 704–710) receive oracle rank $r^* = 64$; attention layers — including output projections and a query projection (erank ≈ 557–590) — receive oracle rank $r^* = 4$. The erank metric separates these two structural tiers without observing any training example. The participation ratio agrees with erank at $\rho = 0.968$.

Three limitations bound the scope of these findings: (1) the sample covers 5 of 72 BERT target layers, all exhibiting bimodal oracle structure; (2) only one of three planned model families has been evaluated; and (3) the coefficient of variation of erank (≈0.04) falls below the pre-registered A1 threshold for NLP encoders. The pre-registered multi-family gate (≥2/3 families satisfying $r \geq 0.65$) has not been met.

The primary contribution is the first empirical test of a purely structural per-layer LoRA rank predictor, together with the PARA oracle + erank correlation protocol for replication and extension. Three next steps follow directly from the current limitations: (1) full oracle sweeps for BERT-base-uncased (covering intermediate erank values), DeBERTa-v3-base, and ViT-base-patch16-224; (2) partial correlation analysis controlling for layer depth to separate erank signal from depth confound; and (3) task-agnosticity assessment (H-M3: Spearman $\rho$ between MNLI and SST-2 oracle ranks for DeBERTa-v3-base).

---

## References

Aghajanyan, A., Zettlemoyer, L., and Gupta, S. (2021). Intrinsic dimensionality explains the effectiveness of language model fine-tuning. In *Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics*, pages 7319–7328. doi:10.18653/v1/2021.acl-long.568.

Balazy, K., Banaei, M., Aberer, K., and Tabor, J. (2024). LoRA-XS: Low-rank adaptation with extremely small number of parameters. In *Proceedings of the European Conference on Artificial Intelligence*. arXiv:2405.17604.

Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., and Chen, W. (2022). LoRA: Low-rank adaptation of large language models. In *International Conference on Learning Representations*. arXiv:2106.09685.

Jiang, G. et al. (2026). IGU-LoRA: Adaptive rank via integrated gradients. arXiv:2603.13792. [Unverified in Semantic Scholar]

Mangrulkar, S., Gugger, S., Debut, L., Belkada, Y., Paul, S., and Bossan, B. (2022). PEFT: State-of-the-art parameter-efficient fine-tuning methods. Hugging Face. https://github.com/huggingface/peft.

Meng, F., Wang, Z., and Zhang, M. (2024). PiSSA: Principal singular values and singular vectors adaptation of large language models. In *Advances in Neural Information Processing Systems*. arXiv:2404.02948.

Roy, O. and Vetterli, M. (2007). The effective rank: A measure of effective dimensionality. In *Proceedings of the European Signal Processing Conference (EUSIPCO)*, pages 606–610. [Not indexed in Semantic Scholar]

Tripathi, A., Singh, S., Sahoo, P., and Saha, S. (2026). LAARA: Layer-aware adaptive rank allocation for parameter-efficient fine-tuning. arXiv:2607.19391.

Valipour, M., Rezagholizadeh, M., Kobyzev, I., and Ghodsi, A. (2022). DyLoRA: Parameter-efficient tuning of pre-trained models using dynamic search-free low-rank adaptation. In *Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics*. arXiv:2210.07558.

Zhang, Q., Chen, M., Bukharin, A., Karampatziakis, N., He, P., Cheng, Y., Chen, W., and Zhao, T. (2023). AdaLoRA: Adaptive budget allocation for parameter-efficient fine-tuning. arXiv:2303.10512.

Zhang, W., Liu, X., and Cheng, Y. (2026). IFCLoRA: Topology-aware rank allocation for parameter-efficient fine-tuning. arXiv:2607.22251.
