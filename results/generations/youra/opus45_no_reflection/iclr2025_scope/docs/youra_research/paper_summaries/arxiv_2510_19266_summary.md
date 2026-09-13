---
source_paper: "arxiv_2510_19266.md"
generated_at: "2026-08-18T13:42:54.695122"
model: "openai/gpt-5.2"
summary_chars: 13364
---

# CAB: Data Efficient Any Transformer-to-Mamba Distillation via Attention Bridge

## Key Metadata
- **Authors:** Penghao Wang et al.
- **Year:** 2025 (arXiv:2510.19266)
- **Venue:** arXiv (Paper Under Review)
- **Core Contribution:** Proposes **CAB**, a **cross-architecture, data-efficient Transformer→Mamba distillation** method that aligns Transformer **(Q,K)** with Mamba’s implicit attention carriers **(C,B)** via a lightweight **MLP “Attention Bridge”**, avoiding quadratic attention-map matching.

## Section Summaries

### Abstract
State-space models (SSMs) have emerged as efficient alternatives to Transformers
for sequence modeling, offering superior scalability through recurrent structures.
However, their training remains costly and the ecosystem around them is far less
mature than that of Transformers. Moreover, the structural heterogeneity be-
tween SSMs and Transformers makes it challenging to efficiently distill knowledge
from pretrained attention models. In this work, we propose Cross-architecture
distillation via Attention Bridge(CAB), a novel data-efficient distillation frame-
work that efficiently transfers attention knowledge from Transformer teachers
to state-space student models. Unlike conventional knowledge distillation that
transfers knowledge only at the output level, CAB enables token-level supervi-
sion via a lightweight bridge and flexible layer-wise alignment, improving both
efficiency and transferability. We further introduce flexible layer-wise alignment
strategies to accommodate architectural discrepancies between teacher and stu-
dent. Extensive experiments across vision and language domains demonstrate that
our method consistently improves the performance of state-space models, even
under limited training data, outperforming both standard and cross-architecture
distillation methods. Our findings suggest that attention-based knowledge can
be efficiently transferred to recurrent models, enabling rapid utilization of Trans-
former expertise for building a stronger SSM community. Our project is available
at https://github.com/wph6/CAB.

### Introduction & Motivation
Transformers model long-range dependencies via explicit self-attention but suffer from **quadratic** cost in sequence length, whereas modern linear RNN/SSM models such as **Mamba** offer **linear-time recurrence** and strong runtime efficiency. Despite fast inference, **training SSMs remains expensive** and their tooling/ecosystem is less mature than Transformers, motivating transfer of pretrained Transformer “expertise” into Mamba. Naïve knowledge distillation (KD) from a Transformer teacher to a Mamba student is limited because it (i) transfers mostly output-level knowledge without explicitly transferring attention inductive bias, (ii) provides weak/long backprop gradients when supervision is only at outputs, and (iii) ignores heterogeneity in layer structures/depths. Prior work that aligns full attention matrices is costly; direct attention injection can even cause collapse. CAB is introduced to **transfer attention knowledge efficiently** using **token-level alignment** without constructing full \(L \times L\) attention maps, and to work well in **low-data regimes**.

### Methodology
CAB (Cross-architecture distillation via **Attention Bridge**) distills a Transformer teacher into a Mamba/SSM student by aligning *implicit* attention-like quantities inside the SSM with the teacher’s explicit attention projections, using a **lightweight MLP bridge** and **flexible layer mapping**.

**Motivating equivalence (attention ↔ recurrence).** Standard attention:
\[
\text{Attention}(Q,K,V)=\text{softmax}(QK^\top)V. \tag{1}
\]
Linear attention replaces softmax with feature maps:
\[
\text{Attention}(Q,K,V)=\phi(Q)\phi(K)^\top V, \tag{2}
\]
and under causality admits a recurrent form:
\[
y_t=\phi(q_t)h_t,\quad h_t=h_{t-1}+\phi(k_t)^\top v_t. \tag{3}
\]
Mamba’s discretized recurrence aggregates past inputs via state transitions:
\[
y_t=C_t\sum_{j=1}^{t}\Big(\prod_{k=j+1}^{t}\bar A_k\Big)\bar B_j x_j. \tag{4}
\]
When \(\bar A \approx I\), the SSM recurrence becomes structurally similar to (3):
\[
\{h_t=\bar A_t h_{t-1}+\bar B_t x_t,\ y_t=C_t h_t\}\ \Longleftrightarrow\ \{h_t=h_{t-1}+\phi(k_t)^\top v_t,\ y_t=\phi(q_t)h_t\}. \tag{5}
\]
Thus, **token-dependent** SSM projections \(B_t, C_t\) are treated as implicit carriers analogous to **Transformer \(K,Q\)**.

**Attention Bridge (token-level alignment, no \(L^2\) maps).** Because student projections \(B,C\in\mathbb{R}^{L\times d_s}\) and teacher \(K,Q\in\mathbb{R}^{L\times d_t}\) differ in dimension/semantics, CAB introduces learnable MLPs \(\varphi_B,\varphi_C\) (implemented as **2-layer MLPs with SiLU**) to map student \(B,C\) into teacher space, producing token-level supervision:
\[
\mathcal{L}_{\text{attn}}=\frac{1}{L}\sum_{l=1}^{L}\Big(\|\varphi_B(B^{(l)})-K^{(l)}\|_2^2 + \|\varphi_C(C^{(l)})-Q^{(l)}\|_2^2\Big). \tag{6}
\]
This avoids explicit attention matrices (which would require \(O(L^2)\) memory/time).

**Flexible layer-wise alignment across heterogeneous depths.** Teacher depth \(T\) and student depth \(L\) may differ. CAB uses proportional indexing:
\[
g(l)=\left\lfloor \frac{l}{L}\cdot T\right\rfloor, \tag{7}
\]
leading to the relaxed alignment loss:
\[
\mathcal{L}_{\text{attn}}=\frac{1}{L}\sum_{l=1}^{L}\Big(\|\varphi_B(B^{(l)})-K^{(g(l))}\|_2^2 + \|\varphi_C(C^{(l)})-Q^{(g(l))}\|_2^2\Big). \tag{8}
\]

**Bidirectional Vision Mamba handling.** For bidirectional ViM, compute losses per direction \(dir\in\{\text{forward},\text{backward}\}\):
\[
\mathcal{L}_{dir}=\frac{1}{L}\sum_{l=1}^{L}\Big(\|\varphi_B(B_{dir}^{(l)})-K^{(g(l))}\|_2^2 + \|\varphi_C(C_{dir}^{(l)})-Q^{(g(l))}\|_2^2\Big), \tag{9}
\]
and sum them:
\[
\mathcal{L}_{\text{attn}}=\mathcal{L}_{\text{forward}}+\mathcal{L}_{\text{backward}}. \tag{10}
\]

**Training procedure & hyperparameters (as reported).**
- **Vision (ImageNet-1k):** Teacher = **DeiT** (Tiny/Small), Student = **Vision Mamba (ViM)** (Tiny/Small/etc.). ViM distilled for **300 epochs** with **AdamW**, learning rate **\(5\times 10^{-4}\)**, **batch size 64**, **single NVIDIA A100**; standard ImageNet augmentation (random crop, horizontal flip). They note initializing \(A\approx 0\) so \(\bar A\approx I\) to better match Eq. (5) and stabilize distillation.
- **Language:** Teacher = **DistilGPT2** (OpenWebText-pretrained), Student = **Phi-Mamba-123M** (built on Mamba-2). Two stages to isolate CAB’s effect: (i) **attention alignment** on **200M tokens** using \(\mathcal{L}_{\text{attn}}\), then (ii) **soft distillation** minimizing **KL divergence** between teacher/student outputs for **2B or 4B tokens**. Both stages: learning rate **\(2\times10^{-5}\)**, **batch size 32 per device**, **8× A100 GPUs**.

### Experiments & Results
CAB is evaluated in **vision** (ImageNet-1k low-data) and **language modeling** (OpenWebText distillation + OOD evaluation), comparing against both standard KD and cross-architecture baselines.

**Datasets & splits / regimes.**
- **ImageNet-1k:** training on **1%, 5%, 10%, 20%** of training data (sampled per class to preserve balance), evaluated on the **full validation set**. Metric: **Top-1 accuracy (%)**.
- **Language modeling:** distillation on **OpenWebText** with **sequence length 1024**. Stage-1 uses **200M tokens** for attention alignment; stage-2 uses **2B or 4B tokens** for soft distillation. Evaluation metric: **perplexity (PPL ↓)** on **OpenWebText**, plus OOD **C4** and **WikiText**.

**Models (reported specs).**
- Vision (Table 1): DeiT-Tiny (12L, 192 dim, 5M), DeiT-Small (12L, 384 dim, 22M); ViM variants include Vim-Tiny (24L, 192 dim, 7.1M), Vim-Small (24L, 384 dim, 26M), etc.
- Language (Table 2): DistilGPT2 (6 layers, 88M params, 20.76 GFLOPs) → Phi-Mamba (6 layers, 123M params, 21.68 GFLOPs).

**Baselines compared (explicitly listed).**
- **Standard Soft Distillation** (Hinton et al., 2015): KL on softened logits only.
- **Attention Weight Reuse / “Mamba in Llama”** style (Wang et al., 2024), adapted to these settings.
- **MOHAWK multi-stage alignment** (Bick et al., 2024): aligns full attention matrices + hidden states (high cost).

**Main quantitative results.** (From Tables 3–4; higher is better for Acc, lower for PPL.)

**ImageNet Top-1 accuracy (%) under low-data training:**

| Teacher → Student | Method | 1% | 5% | 10% | 20% |
|---|---:|---:|---:|---:|---:|
| – → Vim-Tiny | Vanilla | 11.2 | 15.3 | 27.4 | 29.2 |
| DeiT-Tiny → Vim-Tiny | Soft distill | 20.4 | 23.3 | 37.0 | 41.1 |
|  | Attn weight reuse | 21.3 | 23.5 | 37.1 | 41.5 |
|  | Multi-stage align | 21.5 | 24.0 | 36.8 | 42.1 |
|  | **CAB** | **27.8** | **27.3** | **45.4** | **46.0** |
| – → Vim-Small | Vanilla | 32.9 | 36.2 | 41.5 | 47.0 |
| DeiT-Small → Vim-Small | Soft distill | 42.0 | 49.4 | 42.7 | 54.0 |
|  | Attn weight reuse | 41.5 | 49.3 | 42.6 | 54.3 |
|  | Multi-stage align | 45.1 | 50.1 | 44.0 | 53.9 |
|  | **CAB** | **49.2** | **54.9** | **49.4** | **60.7** |

Reported highlight: with DeiT-Tiny→Vim-Tiny at **10% data**, CAB achieves **45.4%**, a **+16.3** point gain over vanilla (27.4). They also show **faster convergence / lower test loss** throughout training (Fig. 3).

**Language modeling perplexity (PPL ↓):**

| Method | OpenWebText 2B | OpenWebText 4B | C4 2B | C4 4B | WikiText 2B | WikiText 4B |
|---|---:|---:|---:|---:|---:|---:|
| Teacher (DistilGPT2) | 28.2 | – | 39.7 | – | 52.96 | – |
| Attn weight reuse | 61.8 | 37.2 | 111.0 | 62.9 | 212.3 | 99.8 |
| Multi-stage align | 58.4 | 31.1 | 105.7 | 51.2 | 199.3 | 77.9 |
| **CAB** | **54.4** | **30.1** | **97.3** | **50.1** | **175.0** | **74.7** |

They emphasize that at **4B tokens**, CAB’s student PPL becomes “comparable” to the Transformer teacher, and that **relative gains are larger on OOD (C4, WikiText)** than on OpenWebText.

**Efficiency / compute cost.**
CAB avoids storing dense attention matrices. At \(L=1024\), MOHAWK requires storing \(2\cdot(H,L,L)\) tensors per layer. CAB adds only two small MLPs (\(\varphi_B,\varphi_C\)), scaling with \((d_{\text{student}}, d_{\text{teacher}})\), not \(L^2\). On DistilGPT2→Phi-Mamba-123M (200M tokens), CAB reports **10× lower memory** and **4× faster runtime** on a single A100; Fig. 5 shows **training time 0.89 h (CAB) vs 3.83 h (MOHAWK)**, and memory annotated as **~996 MB** for the heavier baseline with a 10× reduction claim for CAB.

**Ablations (Tables 5–6).**
- **Aligning both \(B\) and \(C\)** is best. On DeiT-Tiny→Vim-Tiny with 10% ImageNet:
  - Vanilla 32.9, Soft distill 42.0
  - Align \(B\) only 48.7; Align \(C\) only 48.8
  - Sharing \(\varphi_B\equiv \varphi_C\) gives 49.0 (worse than separate mappings)
  - Align \(B+C\) with default \(\bar A\): 43.1 (poor)
  - **Align \(B+C\) with \(\bar A\approx I\) (their init): 49.2** (best)
- **Student architecture robustness (Table 6):** CAB consistently improves over soft distillation across multiple ViM capacities and data ratios (e.g., Vim-Tiny at 20%: soft 45.0 vs CAB 47.2; Vim-Mini* at 1%: soft 5.1 vs CAB 6.9).

**Qualitative/diagnostic analysis.**
They measure cosine similarity between ViM and pretrained ViT attention matrices across layers (Fig. 4): similarity dips in early layers (before L3) but increases sharply in mid-to-deep layers with attention alignment, interpreted as recovery of global token interactions typically induced by Transformer attention.

### Discussion & Conclusion
CAB shows that **attention knowledge can be transferred without explicit attention maps** by aligning **token-wise internal projections** \(B,C\) to teacher \(K,Q\), yielding strong gains particularly in **low-data** training and improved distillation efficiency. The method’s effectiveness depends on architectural bridging assumptions (notably the \(\bar A\approx I\) alignment-friendly regime), and the authors note current focus on **Transformer↔Mamba**; extending to other SSM variants or more complex hybrids is left for future work.

## Key Contributions
- Introduces **CAB**, a **cross-architecture distillation** framework that performs **token-level attention supervision** from Transformer teachers to Mamba/SSM students via a lightweight **MLP Attention Bridge** (\(\varphi_B,\varphi_C\)).
- Proposes **flexible layer-wise alignment** \(g(l)=\lfloor \frac{l}{L}T\rfloor\) to handle teacher/student depth mismatches, enabling “any Transformer-to-Mamba” matching without strict 1:1 layer pairing.
- Demonstrates **dual efficiency**: (i) **resource-efficient** (no \(L^2\) attention-map alignment; 10× less memory, 4× faster than MOHAWK in a reported setting) and (ii) **data-efficient** improvements on ImageNet with **1%–20%** data and improved LM PPL under limited token budgets.

## Potential Relevance
CAB provides a practical recipe for leveraging mature Transformer checkpoints to bootstrap emerging SSM/Mamba models when **data and compute are limited**, by distilling *internal inductive biases* rather than only logits. The key hypothesis lever is the structural bridge in Eq. (5): treating specific SSM projections (\(B,C\)) as attention analogs—this can inspire new cross-paradigm distillation targets (e.g., other SSM parameterizations) and suggests that **initialization/constraints on transition dynamics (\(\bar A\approx I\))** may be critical when transferring “attention-like” behaviors into recurrent models.