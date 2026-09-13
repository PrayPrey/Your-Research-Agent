# 4. Experimental Setup

We design experiments to answer three research questions:

**RQ1:** Does erank($W_0$) correlate significantly with PARA oracle ranks in at least one model family, and does the correlation satisfy the pre-registered threshold ($r \geq 0.65$, $p < 0.05$)?

**RQ2:** Is the erank-oracle correlation consistent across model families (BERT, DeBERTa, ViT), demonstrating cross-architecture generalization?

**RQ3:** Do erank($W_0$) and participation ratio PR($W_0$) agree in layer ranking ($\rho \geq 0.8$), suggesting they capture the same structural signal?

Each RQ maps directly to a testable prediction from the hypothesis: RQ1 tests the primary existence claim (P1), RQ2 tests cross-architecture generalization (implied by the ≥2/3 families criterion), and RQ3 tests the metric equivalence claim (P5).

## 4.1 Datasets

We evaluate on classification benchmarks that provide reliable per-layer oracle rank signals:

| Dataset | Task | Train Size | Eval Metric | Model |
|---------|------|-----------|-------------|-------|
| GLUE MNLI | Natural Language Inference | 392k | Accuracy (matched) | BERT-base, DeBERTa-v3-base |
| CIFAR-10 | Image Classification | 50k | Top-1 Accuracy | ViT-base-patch16-224 |

**Why MNLI?** MNLI's large training set (392k examples) ensures that oracle rank comparisons are not dominated by training set size effects — an important control given that the PARA oracle requires reliable per-rank accuracy estimates. MNLI is also the standard benchmark for BERT and DeBERTa fine-tuning [Hu et al., 2021; Zhang et al., 2023].

**Why CIFAR-10 for ViT?** CIFAR-10 provides clean image classification supervision compatible with ViT-base-patch16-224 pretraining; it is computationally lighter than ImageNet, enabling the per-rank oracle sweeps required by the PARA protocol.

## 4.2 Training Protocol

All fine-tuning uses the PEFT library [Mangrulkar et al., 2022] with LoRA adapters applied to Q, K, V, O, and FFN weight matrices.

**NLP (BERT, DeBERTa):**
- Optimizer: AdamW, lr = 2×10⁻⁵, weight decay = 0.01
- Batch size: 32, warmup ratio = 0.06
- Epochs: ≥3 (full MNLI: 392k samples)
- Baseline rank: $r_{\text{base}} = 8$ for all non-target layers

**Vision (ViT):**
- Optimizer: AdamW, lr = 1×10⁻⁴, weight decay = 0.01
- Batch size: 128, warmup ratio = 0.06
- Epochs: ≥5 (CIFAR-10: 50k samples)

**Oracle sweep:** For each target layer, we train with ranks $r \in \{4, 8, 16, 32, 64\}$ using 2 random seeds per rank, taking the mean validation accuracy for the argmax. All non-target layers remain at $r_{\text{base}} = 8$.

## 4.3 Baselines

We include two reference structural metrics to contextualize erank's correlation:

**Participation ratio PR($W_0$):** $\text{PR}(W_0) = (\sum_i \sigma_i)^2 / \sum_i \sigma_i^2$. A related structural metric that does not use the full entropy of the distribution. We test whether PR and erank agree (P5), providing a robustness check.

**Stable rank:** $\text{srank}(W_0) = \|W_0\|_F^2 / \|W_0\|_2^2$. Used in SRLoRA [Tian et al., 2026] for rank-related decisions. Included as a within-study comparison for the prior spectral entropy experiment.

## 4.4 Evaluation Metrics

**Primary metric:** Pearson $r(\text{erank}(W_0), r_l^*)$ over oracle-measured layers per model family. One-tailed $p$-value and 95% bootstrap confidence interval reported.

**Secondary metric:** Pearson $\rho(\text{erank}, \text{PR})$ for metric agreement (P5).

**Oracle quality check:** We verify that oracle ranks show meaningful variation (not all layers assigned the same rank), which is required for correlation analysis to be interpretable.

## 4.5 Implementation Details

All experiments run on NVIDIA H100 NVL GPUs. erank computation is performed in fp32 via `torch.linalg.svdvals`. PARA oracle sweeps use HuggingFace PEFT `LoraConfig` with `target_modules` set per model family (`["query", "key", "value", "dense"]` for BERT-base; `["query_proj", "key_proj", "value_proj", "dense"]` for DeBERTa-v3-base; `["query", "key", "value", "dense"]` for ViT-base). 

Figure 3 shows the distribution of PARA oracle ranks for the 5 measured BERT-base-uncased layers.

**Compute note:** Due to the per-layer sweep design, the complete oracle sweep for all 72 BERT layers requires approximately 72 × 5 ranks × 2 seeds = 720 training runs. In the current experimental run, we completed oracle measurements for 5 representative layers spanning the erank range (2 attention, 3 FFN). Full oracle coverage for BERT and multi-family expansion are in progress.
