---
source_paper: "arxiv_2408_10189.md"
generated_at: "2026-08-18T13:40:58.663382"
model: "openai/gpt-5.2"
summary_chars: 17281
---

# Transformers to SSMs: Distilling Quadratic Knowledge to Subquadratic Models

## Key Metadata
- **Authors:** Aviv Bick et al.
- **Year:** 2024 (arXiv:2408.10189)
- **Venue:** arXiv
- **Core Contribution:** Proposes **MOHAWK**, a **three-stage** distillation pipeline that transfers a strong pretrained **Transformer** (Phi-1.5) into **subquadratic SSMs (Mamba-2)** by progressively aligning (i) mixing matrices, (ii) block hidden-states, and (iii) end-to-end logits—yielding **Phi-Mamba-1.5B** trained with only **3B tokens** yet outperforming prior open-source non-Transformer models of similar size.

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
Transformers dominate LLMs but incur **quadratic** inference cost from self-attention over sequence length \(T\) (i.e., \(O(T^2)\)), which becomes a bottleneck for long-context and latency-sensitive deployment. Subquadratic alternatives (SSMs like **Mamba/Mamba-2**, linear attention, RNN-like models) are promising, yet typically trained with far less data/compute than the best Transformers, limiting their capability. The paper asks whether we can **reuse the expensive “quadratic knowledge”** embedded in pretrained Transformers to create strong **subquadratic students** without massive pretraining. The authors’ key observation is that both attention and SSMs can be viewed as **sequence mixers** applying structured **mixing matrices** over tokens, enabling distillation objectives that directly compare mixer matrices and intermediate hidden states—before performing standard logit distillation.

### Methodology
**High-level idea (MOHAWK):** treat both Transformer attention and SSMs as instances of **sequence transformations** \(Y=f_\theta(X)\), often expressible as \(Y=MX\) with a **sequence transformation matrix** \(M\in \mathbb{R}^{T\times T}\). Distill a pretrained Transformer teacher (Phi-1.5) into an SSM student (a modified Mamba-2, “Phi-Mamba”) via three increasingly coarse/granular supervision stages: **Matrix Orientation \(\rightarrow\) Hidden-State Alignment \(\rightarrow\) Weight-Transfer & Knowledge Distillation**.

**Background equations (SSM / Mamba-2 view):** the time-varying SSM is
\[
h_{t+1}=A_t h_t + B_t x_t,\qquad y_t = C_t h_t \tag{1}
\]
with a Mamba-2 variant where \(A_t=\alpha_t I\). Using Structured State Space Duality (SSD), the mixer corresponds to a structured causal matrix:
\[
h_{t+1}=\alpha_t \cdot I h_t + B x_t,\qquad y_t = C\cdot h_t
\Rightarrow
\Big[\text{(causal mask with products } \alpha_{t:i}=\alpha_{t-1}\cdots \alpha_i)\Big]\circ (C\cdot B^\top)\cdot X \tag{2}
\]
interpretable as **causal linear attention with a learnable causal mask** (more expressive than a fixed lower-triangular all-ones mask).

#### Stage 1: **Matrix Orientation (MO-)**
Goal: make the student’s **mixer matrix** approximate the teacher’s **attention matrix** at each layer, while ensuring both mixers receive the **same pre-mixer inputs**. They set *student components preceding the mixer* to match teacher components so that differences arise primarily from the mixer itself. Optimize, per layer (parallelizable):
\[
\min_\phi \ \|\text{TeacherMixer}(u)-\text{StudentMixer}_\phi(u)\|_F \tag{3}
\]
where \(u\) is chosen as the **teacher block’s input** (output of the previous teacher layer), approximating the true in-distribution activations.

**Mamba-2-specific initialization for Stage 1:** set the Mamba convolution to **identity** (nullify its effect initially), so the only mismatch is between (materialized) **SSD/semi-separable** mixing and attention mixing. This explicitly “orients” the student mixer towards attention-like mixing.

#### Stage 2: **Hidden-State Alignment (HA-)**
Even with similar mixer matrices, block outputs can diverge due to gating/projections/convolution details. Stage 2 aligns **block outputs** (attention block vs student mixing block) by minimizing:
\[
\min_\phi\ \|\text{AttnBlock}(u)-\text{StudentMixerBlock}_\phi(u)\|_2 \tag{4}
\]
again layerwise and parallelizable.

**Phi-Mamba block engineering to enable alignment/weight reuse:** The authors modify Mamba-2 blocks so non-mixer parts can be made close to the teacher attention block and later replaced by transferred weights.
- Initialize the Mamba gate to constant **1** (“open gate”) to cancel gating initially.
- Remove **normalization prior to output projection** (present in Mamba-2) because it cannot be matched to the teacher attention block.
- Remove the **post-convolution nonlinearity** (present in Mamba-1/2) to simplify alignment and facilitate weight transfer.
These choices differ from “train-from-scratch Mamba-2 best practices” but are empirically sufficient (and helpful) for distillation.

#### Stage 3: **Weight-Transfer & Knowledge Distillation (WKD)**
After per-layer alignment, residual errors compound across depth. Stage 3 transfers remaining teacher weights and performs end-to-end distillation on tokens \(x\):
\[
\min_\phi\ \mathcal{L}_{CE}\big(\text{TeacherModel}(x),\ \text{StudentModel}_\phi(x)\big) \tag{5}
\]
where \(\mathcal{L}_{CE}\) is cross-entropy between teacher and student predicted distributions (logits/soft targets).

**Transferred weights (Phi-1.5 \(\rightarrow\) Phi-Mamba):** token embeddings, final layer norm, LM head, and within each block the **MLP** and **input norm** (i.e., “swap only the sequence mixer”). This is motivated by observations that much knowledge resides in MLPs (cited: Niu et al. 2024).

**Freezing for stability/efficiency:** during Stage 3, the model can keep **MLPs/embeddings/head** frozen and train mainly the Mamba-2 mixers with minor performance drop (validated in experiments), which (i) reduces trainable parameters by >50% and (ii) mitigates catastrophic forgetting.

#### Phi-Mamba / Hybrid Phi-Mamba architectures
- **Teacher:** Phi-1.5-1.3B, 24 blocks with **parallel** mixer+MLP structure (Phi-style blocks, not strictly alternating attention/MLP as in Llama).
- **Phi-Mamba-1.5B:** replace **all 24 attention mixers** with modified **Mamba-2 (SSD) mixers** while reusing Phi MLP pathways.
- **Hybrid-Phi-Mamba-1.5B:** keep **4 attention layers** (quadratic but small constant factor) and replace remaining 20 with Mamba-2 via MOHAWK.

**Two key mixer-level changes vs vanilla Mamba-2:**
1. Convert SSM head structure from “multi-value” to **multi-head** (Transformer-like), enabling **headwise distillation** (each attention head \(\rightarrow\) one Mamba head).
2. Treat the mixer as **entirely discrete-time** by making \(A\) an input projection and **eliminating** the \(\Delta\) discretization parameter; authors claim the original Mamba-2 algorithm still applies “as a black box” (Appendix B referenced).

**Optimization hyperparameters (reported):** AdamW with \(\beta=(0.9,0.95)\), weight decay \(0.1\), learning rate \(1\times 10^{-4}\), and a Warmup-Stable-Decay schedule with 10% warmup and 10% decay. Sequence length is 2048. (Batch size, gradient accumulation, and epochs/steps are not provided in the extracted text.) Stage 3 occasionally shows loss spikes; they stabilize with checkpointing, weight decay, and gradient clipping.

### Experiments & Results
#### Setup: models, data, and evaluation
- **Teacher:** Phi-1.5-1.3B (trained on **150B tokens / unknown dataset** per table).
- **Student (main):** Phi-Mamba-1.5B distilled on **C4** with **3.0B tokens** total; sequence length 2048.
  - Token allocation across MOHAWK stages: **80M (Stage 1)**, **160M (Stage 2)**, **2.76B (Stage 3)** (total \(\approx 3.0\)B).
- **Student (hybrid):** Hybrid-Phi-Mamba-1.5B distilled on **C4** with **5B tokens** total.
- **Benchmarks/metrics:** accuracy on **WinoGrande**, **ARC-Easy (ARC-E)**, **ARC-Challenge (ARC-C)**, **PIQA**, **HellaSwag**, and **LAMBADA** (reported as “Lamb.”). They also track perplexity (C4 perplexity) for training laws/diagnostics and report “Avg.” as the mean of selected benchmark accuracies.

**Baselines (open-source, similar size):** Mamba-1-1.4B, Mamba-2-1.3B (both pretrained on **315B tokens / The Pile**), Finch-1.6B (1.1T / RWKV World v2), xLSTM-1.4B (300B / SlimPajama), Eagle-1.5B (1.1T / RWKV World v2), Pythia-1.4B (300B / The Pile), RWKV4-1.5B (330B / The Pile), DeltaNet-1.3B (100B / SlimPajama), GLA-1.3B (100B / SlimPajama). Hybrid baselines: **Mamba-SWA-MLP-1.6B** and **Samba-1.7B** (Ren et al. 2024). (Note: authors remark some reported numbers from Samba/Mamba-SWA-MLP are “unnormalized” on ARC-C and HellaSwag; they report normalized.)

#### Main downstream results (Phi-Mamba vs non-Transformers)
From Table 1, Phi-Mamba uses **3.0B tokens** yet substantially beats prior non-Transformers trained on hundreds of billions/trillions of tokens:

| Model | Tokens / Dataset | WinoG | ARC-E | ARC-C | PIQA | HellaS | Lamb | Avg ↑ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Phi-1.5-1.3B (teacher)** | 150B / unknown | 73.4 | 75.6 | 48.0 | 76.6 | 62.6 | 53.4 | 64.9 |
| **Phi-Mamba-1.5B** | **3.0B / C4** | **71.7** | **74.0** | **44.1** | **75.5** | **60.2** | **50.1** | **62.6** |
| Mamba-2-1.3B | 315B / The Pile | 60.9 | 64.3 | 33.3 | 73.2 | 59.9 | 65.7 | 59.6 |
| Mamba-1-1.4B | 315B / The Pile | 61.5 | 65.5 | 32.8 | 74.2 | 59.1 | 64.9 | 59.7 |
| Pythia-1.4B (Transformer) | 300B / The Pile | 57.3 | 60.6 | 26.0 | 71.1 | 52.1 | 61.6 | 54.8 |

Key deltas highlighted by the authors: on **WinoGrande**, Phi-Mamba **71.7%** vs pretrained Mamba-2 **60.9%**; on **ARC-C**, **44.1%** vs **33.3%** (Mamba-2). Despite that, Phi-Mamba still trails its teacher Phi-1.5 (e.g., ARC-C 44.1 vs 48.0).

#### Hybrid results (4 attention layers retained)
From Table 2 (commonsense average over WinoG/ARC-E/ARC-C/PIQA/HellaSwag):
- **Hybrid-Phi-Mamba-1.5B (4 attn layers)**: Avg **66.0**, close to Phi-1.5 Avg **67.2**, and better than Phi-Mamba Avg **62.6** (Table 1) while using far fewer attention layers than typical hybrids.
- Compared to **Samba-1.7B** (12 attention layers, trained on Phi-2 dataset; more params): Hybrid-Phi-Mamba is competitive and sometimes stronger, despite being distilled on **C4** (argued lower-quality than teacher’s original data).

| Model | # Attns | WinoG | ARC-E | ARC-C | PIQA | HellaS | Avg ↑ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Phi-1.5-1.3B | 24 | 73.4 | 75.6 | 48.0 | 76.6 | 62.6 | 67.2 |
| **Hybrid-Phi-Mamba-1.5B** | **4** | 72.0 | 75.3 | 45.8 | 76.5 | 60.6 | **66.0** |
| Samba-1.7B | 12 | 72.9 | 79.2 | 48.2 | 77.1 | 49.7 | 65.4 |

#### Ablations: why the 3 stages matter (MOHAWK synergy)
Table 3 varies which stages are applied (same total budget **5B tokens** across runs). General pattern: **Stage 2+3 > Stage 3 alone**, and **Stage 1-3 (full MOHAWK) is best**.
- For **Phi-Mamba**, Stage 2 only yields Avg **53.3**, Stage 3 only Avg **54.5**, Stage 2–3 Avg **62.3**, and full **1–3 Avg 62.7**.
- For **Phi-to-Phi** distillation (control), Stage 2–3 fails to recover full teacher performance; adding Stage 1 (1–3) brings Avg to **64.9**, matching the original Phi teacher Avg **64.9**—used as evidence Stage 1 is critical for attention-matrix-level matching.

#### Mixer expressiveness: approximating attention matrices
They directly test whether structured mixers can match empirical attention matrices from **Llama2-7B-Chat**. Protocol (Table 6): 1,000 samples of 512 tokens; pick one attention head per layer; project/fit each attention matrix into different structured families; metric is Frobenius distance (lower is better). Results show **SSM/semi-separable** is best; **SSD (Mamba-2’s family)** is notably better than low-rank and Toeplitz.

Selected numbers (C4 column, Frobenius distance):
- Toeplitz: **12.3** (poor).
- Low-rank (rank 16): **0.595**
- SSD (state size 16): **0.453**
- SSD (state size 64): **0.093**
- **SSM (state size 64): 0.041** (best)

This supports the paper’s claim that Mamba-2/SSD provides an expressive, distillable subquadratic mixer.

#### Architecture ablation: different structured mixers under MOHAWK
Table 7 replaces the student mixer family and runs MOHAWK (Stages 2 & 3; 1B tokens per stage in this experiment) to show downstream impact correlates with block output distance:
- **SSD (Mamba-2-like)** has the lowest block output L2 distance (**5.5**) and best downstream (e.g., WinoG **67.2**, ARC-E **71.0**).
- Causal Toeplitz and causal low-rank are worse (WinoG **49–50**; ARC-E **21–28**).

#### Freezing study: train only mixers?
Table 8: training only Mamba-2 components (“Mamba-2 trainable”) vs “All”:
- Phi-Mamba Avg drops from **62.7** (All) to **61.4** (Mamba-2 only), suggesting much of the remaining capacity/knowledge is already in transferred weights and can be preserved/frozen.

#### Compute/cost reporting
The extracted text does not provide GPU type, GPU hours, tokens/sec, or inference latency measurements; complexity motivation is theoretical/architectural (quadratic vs subquadratic) and tied to Mamba-2’s known efficiency.

### Discussion & Conclusion
MOHAWK demonstrates that subquadratic models (specifically Mamba-2 variants) can inherit substantial capability from strong Transformers via progressive mixer/block/logit alignment, achieving state-of-the-art results among open non-Transformer models at ~1.5B parameters with only **3B** distillation tokens. The authors emphasize that **distillability** differs from **trainability**—components beneficial for scratch training (e.g., certain norms/activations) may be unnecessary when distilling. Limitations include a remaining performance gap to the Transformer teacher, occasional training instabilities in end-to-end distillation, and the need for further optimization of hybrid distillation recipes (e.g., attention placement, optimizer tweaks).

## Key Contributions
- **MOHAWK distillation framework (Matrix Orientation → Hidden-State Alignment → Weight-Transfer & KD):** Introduces a practical, stagewise procedure with explicit objectives at each granularity—mixer-matrix Frobenius matching (Eq. 3), per-block output L2 alignment (Eq. 4), and end-to-end cross-entropy distillation (Eq. 5)—and shows via ablations that these stages are complementary rather than redundant.
- **Phi-Mamba and Hybrid-Phi-Mamba architectures enabling cross-architecture weight reuse:** Designs a modified Mamba-2 block compatible with Phi-1.5’s block structure (removing post-conv activation and pre-output norm; opening gates; multi-head SSM) so that all non-mixer parameters (embeddings/MLPs/norms/LM head) can be transferred from the Transformer teacher, isolating the architectural change to the sequence mixer.
- **Empirical evidence linking mixer expressiveness to distillation success:** Provides controlled attention-matrix approximation experiments (Table 6) and end-to-end structured-mixer ablations (Table 7) showing that more expressive structured families (SSM/SSD) better match attention matrices and yield substantially higher downstream accuracy, supporting the “mixing matrix” perspective as a predictive tool for distillability/performance.

## Potential Relevance
MOHAWK is directly useful if you want to **convert a strong pretrained Transformer into an efficient long-context model** without reproducing full pretraining: it offers concrete intermediate supervision targets (matrix and hidden-state alignment) that reduce the difficulty of end-to-end KD across architectures. The paper’s results suggest a hypothesis that **the best subquadratic students are those whose mixer family can closely approximate attention matrices under realistic constraints**, making Frobenius-distance-to-attention a potential proxy metric when designing new mixers. The freezing results also motivate research directions where one distills only the **sequence mixers** while keeping MLP/embedding blocks fixed, potentially enabling low-resource adaptation of efficient architectures.