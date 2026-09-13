---
source_paper: "arxiv_2312_00752.md"
generated_at: "2026-08-18T13:39:15.592756"
model: "openai/gpt-5.2"
summary_chars: 14107
---

# Mamba: Linear-Time Sequence Modeling with Selective State Spaces

## Key Metadata
- **Authors:** Albert Gu et al.
- **Year:** 2023 (arXiv:2312.00752)
- **Venue:** arXiv (preprint)
- **Core Contribution:** Introduces **selective (input-dependent) structured state space models (SSMs)** plus a **hardware-aware selective-scan algorithm**, yielding the **Mamba** architecture: an attention-free, linear-time backbone that matches/exceeds Transformer quality (notably in language) while enabling fast, cache-free inference and million-length context scaling.

## Section Summaries

### Abstract
Foundation models, now powering most of the exciting applications in deep learning, are almost universally based on the
Transformer architecture and its core attention module. Many subquadratic-time architectures such as linear attention,
gated convolution and recurrent models, and structured state space models (SSMs) have been developed to address
Transformers’ computational inefficiency on long sequences, but they have not performed as well as attention on important
modalities such as language. We identify that a key weakness of such models is their inability to perform content-based
reasoning, and make several improvements. First, simply letting the SSM parameters be functions of the input addresses
their weakness with discrete modalities, allowing the model to selectively propagate or forget information along the
sequence length dimension depending on the current token. Second, even though this change prevents the use of efficient
convolutions, we design a hardware-aware parallel algorithm in recurrent mode. We integrate these selective SSMs into a
simplified end-to-end neural network architecture without attention or even MLP blocks (Mamba). Mamba enjoys fast
inference (5× higher throughput than Transformers) and linear scaling in sequence length, and its performance improves
on real data up to million-length sequences. As a general sequence model backbone, Mamba achieves state-of-the-art
performance across several modalities such as language, audio, and genomics. On language modeling, our Mamba-3B model
outperforms Transformers of the same size and matches Transformers twice its size, both in pretraining and downstream
evaluation.

### Introduction & Motivation
Transformers dominate foundation models because **self-attention provides content-based routing**, but it scales poorly: **quadratic training cost in context length** and **linear-time inference with a KV-cache** bounded by a finite window. Prior subquadratic alternatives (linear attention, convolutions, RNNs, structured SSMs) scale better but underperform on **discrete, information-dense modalities** (notably language). The paper diagnoses a key gap: many efficient architectures are **linear time-invariant (LTI)** along the sequence axis and thus struggle with **content-based selection** (“remember this token, ignore that one”) needed for tasks like **selective copy** and **induction**. The work proposes **selective (input-dependent) SSM dynamics** plus a GPU-efficient implementation, then builds a simplified architecture (Mamba) that attains Transformer-level quality with linear-time scaling and strong long-context behavior.

### Methodology
The core primitive is a **structured state space model (SSM / S4)** with latent state \(h(t)\in\mathbb{R}^N\) mapping an input sequence \(x(t)\) to output \(y(t)\):
\[
h'(t)=Ah(t)+Bx(t),\quad y(t)=Ch(t) \tag{1}
\]
Discretized recurrence:
\[
h_t=\bar A h_{t-1}+\bar B x_t,\quad y_t=C h_t \tag{2}
\]
with ZOH discretization (one option used/illustrated):
\[
\bar A=\exp(\Delta A),\quad 
\bar B=(\Delta A)^{-1}(\exp(\Delta A)-I)\cdot \Delta B \tag{4}
\]
Prior efficient SSMs are **LTI**: \((\Delta,A,B,C)\) constant over time, enabling a convolution form \(y=x*K\) (Eq. 3) and FFT-style speedups. Mamba’s key change is **selection**: make SSM parameters **functions of the input** at each timestep (time-varying SSM, “S6”):
- \(s_B(x)=\mathrm{Linear}_N(x)\Rightarrow B_t\in\mathbb{R}^N\)
- \(s_C(x)=\mathrm{Linear}_N(x)\Rightarrow C_t\in\mathbb{R}^N\)
- \(s_\Delta(x)=\mathrm{Broadcast}_D(\mathrm{Linear}_1(x))\)
- \(\Delta_t=\tau_\Delta(\text{Parameter}+s_\Delta(x_t))\), with \(\tau_\Delta=\mathrm{softplus}\)

This yields \(\Delta,B,C\) shaped with a length dimension (e.g., \((B,L,\cdot)\)), breaking convolutional computation and requiring recurrence. The paper then introduces **hardware-aware selective scan** to compute the recurrence efficiently: (i) **kernel fusion** so discretization + recurrence happen in one GPU kernel, (ii) **parallel scan** to mitigate sequential dependence, and (iii) **recomputation** to avoid storing all intermediate states for backprop, matching the memory profile of optimized Transformer kernels (e.g., FlashAttention-style savings). Crucially, the algorithm avoids materializing the large expanded state \((B,L,D,N)\) in HBM; it loads parameters from HBM to SRAM, performs discretization/scan in SRAM, then writes only outputs \((B,L,D)\) back.

**Mamba architecture** stacks homogeneous blocks with residuals + normalization, replacing attention and even explicit MLP blocks. Each block expands model width by factor \(E\) (fixed **\(E=2\)** in experiments) using linear projections (dominant parameter cost \(\approx 3ED^2\)), includes an SSM on the main branch, and uses **SiLU/Swish** so the gating resembles **SwiGLU** behavior. An optional **LayerNorm** is inserted (motivated by RetNet). SSMs use **diagonal/structured \(A\)**; default is **real-valued** for most tasks, with **complex** used for one audio setting. Initialization follows S4D variants; for real SSMs, \(A_n=-(n+1)\) is highlighted as strong.

A key interpretability link: selection generalizes **RNN gating**. For \(N=1\), \(A=-1\), \(B=1\), \(s_\Delta=\mathrm{Linear}(x)\), \(\tau_\Delta=\mathrm{softplus}\), the recurrence becomes:
\[
g_t=\sigma(\mathrm{Linear}(x_t)),\quad
h_t=(1-g_t)h_{t-1}+g_t x_t \tag{5}
\]
so \(\Delta\) acts like a learned, input-dependent **forget/overwrite gate**.

### Experiments & Results
The paper evaluates Mamba on synthetic selection tasks, plus three modalities (language, genomics, audio), emphasizing both **quality** and **efficiency/long-context scaling**.

**Synthetic tasks (selection stress tests).**
- **Selective Copying**: random spacing prevents time-only shortcuts (LTI convolutions/recurrences fail). Accuracy (Table 1) shows selectivity is decisive:

| Model Arch. | Inner Layer | Accuracy |
|---|---:|---:|
| – | S4 (no gate) | 18.3 |
| – | S6 (no gate) | 97.0 |
| H3 | S4 | 57.0 |
| Hyena | Hyena | 30.1 |
| – | S6 | 99.7 |
| Mamba | S4 | 56.4 |
| – | Hyena | 28.4 |
| – | S6 | 99.8 |

Conclusion: architectural gating alone (H3/Mamba with non-selective S4) helps but is insufficient; **input-dependent \((\Delta,B,C)\)** solves the task.
- **Induction Heads**: trained length \(2^8=256\), vocab 16; tested from \(2^6=64\) up to \(2^{20}=1{,}048{,}576\). Mamba’s selective SSM layer achieves **perfect generalization to 1M length** (>4000× extrapolation), while other methods reportedly fail beyond ~2× extrapolation; attention baselines are limited to \(2^{14}=16384\) due to memory.

**Language modeling (pretraining + zero-shot).**
- **Dataset:** The Pile (Gao et al. 2020). Training recipe follows GPT-3-style (Brown et al. 2020); a stronger baseline “Transformer++” uses PaLM/LLaMa-style upgrades (e.g., rotary embeddings, SwiGLU, RMSNorm, no linear bias, higher LR).
- **Scaling laws:** parameter range \(\approx 125\text{M}\) to \(\approx 1.3\text{B}\) under a Chinchilla-style protocol. Mamba is reported as **first attention-free** model to match strong Transformer++ perplexity trends, especially as context grows (Figure 4). Some recurrent baselines (RWKV, RetNet) lack 8k context results due to implementation/memory constraints.
- **Zero-shot evals (Table 3):** compared to Pythia and RWKV (same tokenizer/dataset/training length: **300B tokens**), plus OPT/GPT-Neo/GPT-J. Mamba is best-in-class at each size and often matches ~2× larger baselines. Key excerpts:

| Model | Pile ppl ↓ | HellaSwag acc ↑ | Arc-C acc ↑ | WinoGrande acc ↑ | Avg acc ↑ |
|---|---:|---:|---:|---:|---:|
| Pythia-160M | 10.56 | 44.3 | 24.2 | 50.6 | 40.1 |
| **Mamba-130M** | **8.14** | **55.6** | **32.8** | **61.5** | **59.7** |
| Pythia-410M | 8.28 | 62.7 | 29.4 | 54.6 | 54.3 |
| **Mamba-370M** | **6.64** | **64.9** | **36.3** | **61.5** | **59.7** |
| Pythia-2.8B | 6.73 | 71.0 | 28.5 | 57.2 | 55.2 |
| RWKV-3B | 7.00 | 72.4 | 29.4 | 54.6 | 54.3 |
| **Mamba-2.8B** | **6.22** | **75.2** | **36.3** | **61.5** | **63.3** |

(Full table includes LAMBADA ppl/acc, PIQA, Arc-E, etc.; Mamba leads consistently.)

**Genomics (DNA foundation modeling).**
- **Pretraining dataset:** **HG38** human genome; training split \(\approx 4.5\) **billion** DNA tokens/base pairs (HyenaDNA setup).
- **Scaling with model size (context 1024):** batch size 1024, \(\approx 2^{20}\approx 1\)M tokens/batch; trained **10k steps = 10B tokens**. Mamba scales smoothly and matches Transformer++ and HyenaDNA with **~3–4× fewer parameters** at \(\approx 40\)M parameter scale (Figure 5 left).
- **Scaling with context length:** models of 6 layers × width 128 (\(\approx 1.3\)–1.4M params) trained across lengths \(2^{10}=1024\) up to \(2^{20}=1{,}048{,}576\), with **20k steps \(\approx 330B\) tokens** total and sequence-length warmup. Mamba perplexity **improves monotonically** with longer context up to 1M, while HyenaDNA **degrades** as length grows (Figure 5 right), supporting the claim that selectivity helps filter irrelevant long-range noise.
- **Downstream:** “great apes” species classification (human/chimp/gorilla/orangutan/bonobo; ~99% DNA shared). Fine-tuning accuracy improves with longer sequences when using pretrained models at matching context lengths (Figure 6; numbers referenced to Table 13 in paper).

**Audio waveform modeling and generation.**
- **Pretraining:** YouTubeMix (4 hours solo piano, 16kHz). Metric: **BPB** (bits/byte), a constant-factor transform of NLL. With compute controlled, both SaShiMi (S4+MLP) and Mamba improve as sequence length grows from \(2^{13}=8192\) to \(\sim 10^6\) samples (minute-scale), but **Mamba is better throughout and widens the gap** at longer context (Figure 7). This is the main setting where the paper uses **complex-valued** SSMs.
- **Speech generation:** SC09 (1-second clips, 16kHz digits). Mamba beats autoregressive, GAN, and diffusion baselines on fidelity:

| Model | Params | NLL ↓ | FID ↓ | IS ↑ | mIS ↑ | AM ↓ |
|---|---:|---:|---:|---:|---:|---:|
| SaShiMi | 5.8M | 1.873 | 1.99 | 5.13 | 42.57 | 0.74 |
| **Mamba** | 6.1M | **1.852** | **0.94** | **6.26** | **88.54** | **0.52** |
| **Mamba (larger)** | 24.3M | 1.860 | 0.67 | 7.33 | 144.9 | 0.36 |

Ablations inside the U-Net show Mamba blocks are strongest in the “outer” long-sequence parts, and in the center blocks Mamba > S4+MLP > MHA+MLP (Table 5).

**Efficiency benchmarks.**
- **Selective scan kernel** (example \(N=16\)) is **20–40× faster** than a standard PyTorch scan; faster than FlashAttention-2 beyond sequence length ~2k (training benchmark).
- **Inference throughput:** Mamba achieves **~4–5× higher** throughput than similarly-sized Transformers, largely because it avoids the **KV cache** and thus can run much larger batches; claim: an untrained Mamba-6.9B can out-throughput a ~5× smaller Transformer-1.3B (Figure 8).

**Ablations (LM, ~350M params).**
- Selectivity matters far more than specific LTI SSM parameterization; switching S4→S6 drops perplexity from ~10.5→~8.7 in Mamba (Table 6).
- Selective parameters: \(\Delta\) is most important, but \((\Delta,B,C)\) together are best (Table 7):
  - none selective: ppl 10.93
  - only \(C\): 10.15
  - only \(B\): 9.98
  - only \(\Delta\): 9.81
  - \(\Delta,B,C\): **8.71**
- State size \(N\): increasing \(N\) yields large gains **only when \(B,C\) are also selective** (Table 10). With selective \(B,C\), ppl improves from 9.73 (N=1) → **8.71 (N=16)** at near-negligible parameter increase.

### Discussion & Conclusion
The paper argues there is “no free lunch” across modalities: classical LTI SSM inductive biases help continuous signals, while selectivity is crucial for discrete, dense data (text/DNA) and may trade off in some audio settings. It highlights open questions about whether SSM backbones support the same downstream “ecosystem” as Transformers (prompting, instruction tuning, RLHF, quantization) and whether advantages persist at larger-than-studied scales. The conclusion: **selective SSMs + selective scan** make a compelling, linear-time alternative backbone that matches Transformer quality and improves with extremely long context.

## Key Contributions
- **Selective SSMs (S6):** make key SSM parameters \(\Delta,B,C\) input-dependent to enable **content-based selection** (filter/remember/reset) while retaining structured SSM benefits; link \(\Delta\) selectivity to RNN gating (Eq. 5).
- **Hardware-aware selective scan:** a fused, parallel, recompute-based scan kernel that avoids materializing \((B,L,D,N)\) in HBM, achieving large real-world speedups and linear scaling.
- **Mamba architecture:** a simplified, homogeneous, attention-free block (no explicit MHA/MLP blocks) that attains **Transformer-level or better** results on language and strong scaling to **million-length sequences** in genomics/audio.

## Potential Relevance
Mamba provides a concrete recipe for building **long-context foundation model backbones** without attention: the selection mechanism offers a principled way to add **content-dependent routing** to otherwise linear recurrent/SSM systems, and the selective-scan kernel design is directly relevant for any attempt to make **time-varying recurrences** GPU-efficient. For hypothesis development, the strongest levers appear to be (i) **\(\Delta\)-based gating/selectivity** as a general “state reset / persist” control, and (ii) the finding that **increasing SSM state dimension \(N\)** becomes highly effective only once **input-dependent selection** is present.