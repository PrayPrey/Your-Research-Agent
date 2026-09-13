---
source_paper: "arxiv_2408_10189.md"
generated_at: "2026-08-03T12:50:40.236480"
model: "openai/gpt-5.2"
summary_chars: 10943
---

# Transformers to SSMs: Distilling Quadratic Knowledge to Subquadratic Models

## Key Metadata
- **Authors:** Aviv Bick et al.
- **Year:** 2024 (arXiv:2408.10189)
- **Venue:** arXiv
- **Core Contribution:** Proposes **MOHAWK**, a **3-stage, progressively supervised** distillation pipeline that transfers a pretrained **Transformer (Phi-1.5)** into **Mamba-2–based SSM** models (and hybrids) using only a few billion tokens, yielding the strongest reported open-source non-Transformer results at ~1.5B scale.

## Section Summaries

### Abstract
Transformer architectures have become a dominant paradigm for domains like language modeling but suffer in many in-
ference settings due to their quadratic-time self-attention. Recently proposed subquadratic architectures, such as Mamba,
have shown promise, but have been pretrained with substantially less computational resources than the strongest Trans-
former models. In this work, we present a method that is able to distill a pretrained Transformer architecture into alterna-
tive architectures such as state space models (SSMs). The key idea to our approach is that we can view both Transformers
and SSMs as applying different forms of mixing matrices over the token sequences. We can thus progressively distill the
Transformer architecture by matching different degrees of granularity in the SSM: first matching the mixing matrices
themselves, then the hidden units at each block, and finally the end-to-end predictions. Our method, called MOHAWK, is
able to distill a Mamba-2 variant based on the Phi-1.5 architecture (Phi-Mamba) using only 3B tokens and a hybrid ver-
sion (Hybrid Phi-Mamba) using 5B tokens. Despite using less than 1% of the training data typically used to train models
from scratch, Phi-Mamba boasts substantially stronger performance compared to all past open-source non-Transformer
models. MOHAWK allows models like SSMs to leverage computational resources invested in training Transformer-based
architectures, highlighting a new avenue for building such models.

### Introduction & Motivation
Transformers dominate LLMs but incur **quadratic-time self-attention** in sequence length, which is costly at inference/finetuning. Subquadratic alternatives (SSMs like **Mamba/Mamba-2**, linear attention, RNN-like models) can be faster/cheaper, but typically lack the massive compute and curated data used for state-of-the-art Transformers. The paper asks whether we can **reuse the “quadratic knowledge”** already baked into strong pretrained Transformers to train strong subquadratic models cheaply. The key gap is **cross-architecture distillation** from attention-based teachers into SSM students of comparable scale without training from scratch.

### Methodology
MOHAWK (“**Matrix Orientation, Hidden-State Alignment, Weight-Transfer and Knowledge Distillation**”) distills a Transformer teacher into an SSM student by treating both as **sequence mixers** applying a (possibly input-dependent) **mixing matrix** over tokens. MOHAWK progresses from **fine** (matrix-level) to **coarse** (logits) supervision:

1) **Stage 1 — Matrix Orientation.** For each layer independently, set student pre-mixer components to match the teacher so the mixer input distribution aligns, then minimize Frobenius distance between the teacher attention mixing matrix and the student’s materialized SSM/SSD mixing matrix:
\[
\min_{\phi}\ \lVert \text{TeacherMixer}(u)-\text{StudentMixer}_\phi(u)\rVert_F
\tag{3}
\]
For Mamba-2, initialize convolution as **identity** so the SSD/semi-separable mixer is the primary difference.

2) **Stage 2 — Hidden-State Alignment.** Still layerwise/parallel, align the *block outputs* (attention block vs. SSM block):
\[
\min_{\phi}\ \lVert \text{AttnBlock}(u)-\text{StudentMixerBlock}_\phi(u)\rVert_2
\tag{4}
\]
For Phi-Mamba, they modify Mamba-2 to be closer to Phi’s attention block: set gate to constant **1** (open gate), remove the extra pre-output-projection norm, and distill the whole mixer block output.

3) **Stage 3 — Weight Transfer + Logit Distillation.** Copy non-mixer weights from the teacher (token embedding, MLPs, norms, LM head) and fine-tune end-to-end using teacher supervision:
\[
\min_{\phi}\ \mathcal{L}_{CE}\big(\text{TeacherModel}(x), \text{StudentModel}_\phi(x)\big)
\tag{5}
\]
They often can **freeze most weights** (e.g., MLPs) and train mainly the SSM mixers, reducing trainable parameters and mitigating catastrophic forgetting.

**Student architecture (Phi-Mamba).** Built from **Phi blocks** with **parallel** mixer + MLP structure (matching Phi-1.5), replacing attention mixers with a simplified **Mamba-2** block: removes post-convolution nonlinearity and the pre-output-projection normalization; initializes convolution and gating to identity/neutral. Two mixer changes: (i) convert to **multi-head** SSM (to distill each attention head separately), and (ii) treat dynamics as **discrete-time** by projecting \(A\) from inputs and removing \(\Delta\). The underlying time-varying SSM form is:
\[
h_{t+1}=A_t h_t + B_t x_t,\quad y_t = C_t h_t
\tag{1}
\]
and the Mamba-2/SSD view yields a causal semi-separable mixing matrix (learnable “mask”):
\[
Y = \Big(\text{(lower-triangular multiplicative mask from }\alpha_{t:i})\ \circ (C B^\top)\Big)X
\tag{2}
\]

### Experiments & Results
**Training data & budgets.** Distillation uses **C4** with **sequence length 2048**. Final **Phi-Mamba-1.5B** uses **3.0B tokens total**: Stage 1 **80M**, Stage 2 **160M**, Stage 3 **2.76B**. **Hybrid-Phi-Mamba-1.5B** uses **5B tokens**. This is contrasted with training-from-scratch baselines using far more data (e.g., Mamba/Mamba-2: **315B** tokens; RWKV variants: **1.1T**).

**Optimization.** Across experiments: **AdamW** with \(\beta=(0.9,0.95)\), **weight decay 0.1**, base **LR \(1\times 10^{-4}\)**, and **Warmup-Stable-Decay (WSD)** scheduler (10% warmup, 10% decay). Stage 3 required stabilizations (checkpointing, weight decay, gradient clipping; and reduced LR for the final run due to loss spikes).

**Evaluation tasks/metrics.** Report **accuracy** on commonsense/language understanding: **WinoGrande**, **ARC-Easy (ARC-E)**, **ARC-Challenge (ARC-C)**, **PIQA**, **HellaSwag**, plus **LAMBADA** (accuracy). They also plot/track **perplexity** during Stage 3 and **hidden-state L2 distances** during Stage 2.

**Main downstream results (Table 1; Acc %, higher is better).**

| Model | Tokens | WinoG | ARC-E | ARC-C | PIQA | HellaS | Lamb | Avg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Phi-1.5-1.3B (teacher)** | 150B | 73.4 | 75.6 | 48.0 | 76.6 | 62.6 | 53.4 | 64.9 |
| **Phi-Mamba-1.5B (MOHAWK)** | **3.0B** | **71.7** | **74.0** | **44.1** | **75.5** | **60.2** | **50.1** | **62.6** |
| Mamba-2-1.3B | 315B | 60.9 | 64.3 | 33.3 | 73.2 | 59.9 | 65.7 | 59.6 |
| Mamba-1-1.4B | 315B | 61.5 | 65.5 | 32.8 | 74.2 | 59.1 | 64.9 | 59.7 |
| Pythia-1.4B | 300B | 57.3 | 60.6 | 26.0 | 71.1 | 52.1 | 61.6 | 54.8 |

Key claimed deltas: Phi-Mamba vs pretrained Mamba-2: **+10.8** on WinoGrande (71.7 vs 60.9) and **+10.8** on ARC-C (44.1 vs 33.3), while using **~100× fewer** tokens than typical subquadratic pretraining.

**Hybrid results (Table 2; 4 attention layers kept).**

| Model | #Attn layers | WinoG | ARC-E | ARC-C | PIQA | HellaS | Avg |
|---|---:|---:|---:|---:|---:|---:|---:|
| Phi-1.5-1.3B | 24 | 73.4 | 75.6 | 48.0 | 76.6 | 62.6 | 67.2 |
| **Hybrid Phi-Mamba-1.5B** | **4** | **72.0** | **75.3** | **45.8** | **76.5** | **60.6** | **66.0** |
| Samba-1.7B | 12 | 72.9 | 79.2 | 48.2 | 77.1 | 49.7 | 65.4 |

**Ablations: necessity of stages (Table 3).** With a fixed 5B-token budget, applying **Stages 1–3** yields the best results across Phi-Mamba / Hybrid / even Phi→Phi distillation. Notably, **Stage 3 alone** (plain logit distillation + weight transfer) underperforms **Stage 2+3**, and adding **Stage 1** further improves, indicating strong complementarity rather than interference.

**Structured mixer expressivity (Tables 6–7).** They directly project/fit attention matrices from **Llama2-7B-Chat** (1000 samples, length 512, random head per layer) into structured families and compare **Frobenius distances** (lower is better): Toeplitz ≈ 12.0 (poor), low-rank ≈ 0.6, **SSD (Mamba-2 family)** improves (e.g., 0.477 @ N=16; 0.097 @ N=64 on WT-103), and general SSM ≈ 0.046 @ N=64. End-to-end, replacing attention with different mixers under MOHAWK shows SSD vastly better than Toeplitz/low-rank (e.g., Winogrande 67.2 for SSD vs ~50 for Toeplitz/low-rank; Table 7), matching the “better matrix approximation ↔ better accuracy” correlation.

**Freezing ablation (Table 8).** During MOHAWK, training only the **Mamba-2 mixers** (freezing embeddings/MLPs/head) yields only modest drops (e.g., Phi-Mamba Avg 62.7→61.4).

**Compute cost.** GPU-hours and throughput are not explicitly reported; the motivation is subquadratic inference from replacing most/all attention with Mamba-2 mixers (plus a hybrid option with only 4 attention layers).

### Discussion & Conclusion
MOHAWK shows that strong Transformer teachers can be converted into **competitive SSM-based LMs** using **orders of magnitude fewer tokens** than training SSMs from scratch, by progressively aligning **mixing matrices → block states → logits**. The authors highlight that **distillability ≠ trainability**: components useful for scratch pretraining (extra norms, post-conv activations) may be unnecessary for distillation, and freezing MLPs often works. Limitations include remaining performance gaps to the full teacher and potential need to tailor optimization/distillation specifically for hybrid architectures and stability in Stage 3.

## Key Contributions
- Introduces **MOHAWK**, a **three-stage** distillation framework: **(1) matrix mixer orientation (Eq. 3), (2) hidden-state/block alignment (Eq. 4), (3) weight transfer + logit distillation (Eq. 5)**.
- Proposes **Phi-Mamba**, a **Phi-1.5–aligned Mamba-2 variant** (multi-head SSM, discrete-time handling, simplified block) enabling direct cross-architecture weight transfer and effective distillation.
- Empirically demonstrates **state-of-the-art open-source non-Transformer performance** at ~1.5B scale with **3B tokens**, and shows **hybrid attention+SSM** models can nearly match the teacher with only **4 attention layers**.

## Potential Relevance
MOHAWK is directly useful for hypotheses about **where Transformer capability “lives”** (mixers vs MLPs) and how much can be transferred via **structured sequence-mixer alignment**. The staged objectives (matrix → states → logits) and the reported correlation between **attention-matrix approximability** (Frobenius distance) and **downstream accuracy** provide concrete knobs for testing new mixer families or distillation curricula. The freezing results suggest a practical route to **low-cost conversion** of existing Transformers into efficient architectures while preserving much of the teacher’s behavior.