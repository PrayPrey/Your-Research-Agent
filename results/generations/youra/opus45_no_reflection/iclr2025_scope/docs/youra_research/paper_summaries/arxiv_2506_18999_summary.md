---
source_paper: "arxiv_2506_18999.md"
generated_at: "2026-08-18T13:41:54.542377"
model: "openai/gpt-5.2"
summary_chars: 12766
---

# T2MD: Diffusion Transformer-to-Mamba Distillation

## Key Metadata
- **Authors:** Yuan Yao et al.
- **Year:** 2025 (arXiv:2506.18999)
- **Venue:** arXiv
- **Core Contribution:** A multi-stage distillation pipeline (T2MD) that transfers a strong diffusion transformer (PixArt-α) into a largely Mamba2-based *hybrid* diffusion backbone, enabling efficient, high-quality text-to-image generation up to 2048×2048 (and zero-shot 4K) with improved high-resolution sampling speed.

## Section Summaries

### Abstract
The quadratic computational complexity of self-attention in
diffusion transformers (DiT) introduces substantial compu-
tational costs in high-resolution image generation. While
the linear-complexity Mamba model emerges as a poten-
tial alternative, direct Mamba training remains empirically
challenging. To address this issue, this paper introduces
diffusion transformer-to-mamba distillation (T2MD), form-
ing an efficient training pipeline that facilitates the transi-
tion from the self-attention-based transformer to the linear
complexity state-space model Mamba. We establish a diffu-
sion self-attention and Mamba hybrid model that simulta-
neously achieves efficiency and global dependencies. With
the proposed layer-level teacher forcing and feature-based
knowledge distillation, T2MD alleviates the training diffi-
culty and high cost of a state space model from scratch.
Starting from the distilled 512×512 resolution base model,
we push the generation towards 2048×2048 images via
lightweight adaptation and high-resolution fine-tuning. Ex-
periments demonstrate that our training path leads to low
overhead but high-quality text-to-image generation.
Im-
portantly, our results also justify the feasibility of using
sequential and causal Mamba models for generating non-
causal visual output, suggesting the potential for future ex-
ploration.

### Introduction & Motivation
Diffusion Transformers (DiTs) have become a standard backbone for scalable image generation, but their self-attention cost grows quadratically with the number of image tokens, making high-resolution sampling expensive. Linear-complexity sequence models such as Mamba (a selective state-space model, SSM) offer a potential efficiency alternative, yet training Mamba-based diffusion models from scratch is empirically difficult and prior Mamba diffusion work is largely capped at 512×512. The paper targets two bottlenecks: (i) avoiding the compute-heavy training of a high-quality low-res “base model” in Mamba, and (ii) resolving the architectural mismatch between *non-causal* self-attention dependencies and *sequential/causal* SSM dynamics when modeling large 2D images. T2MD is proposed as an efficient training path: distill a strong DiT teacher into a hybrid Mamba model using a teacher-forcing alignment scheme to prevent error accumulation, then adapt and fine-tune for high resolution.

### Methodology
T2MD distills a pretrained diffusion transformer teacher (PixArt-α) into a **hybrid diffusion model** where most token mixers are **Mamba2** blocks (linear complexity) and a small fraction remain **self-attention** (to preserve global interactions). The diffusion formulation is standard DDPM noise prediction: the forward process is
\[
q(x_t|x_{t-1})=\mathcal{N}\left(x_t;\sqrt{1-\beta_t}\,x_{t-1},\beta_t I\right) \tag{1}
\]
and the learned reverse process is
\[
p_\theta(x_{t-1}|x_t)=\mathcal{N}\left(x_{t-1};\mu_\theta(x_t,t),\Sigma_\theta(x_t,t)\right). \tag{2}
\]
**Architecture.** Images are encoded by a VAE \((E,D)\) into latents; noisy latents are **patchified** (patch size = 2), flattened, and added with positional encodings. The network has **28 blocks**; each block contains (i) a **token mixer** (either self-attention or Mamba2), (ii) **cross-attention** to text features from a **T5 encoder**, and (iii) an FFN. Timestep conditioning follows DiT-style **adaptive LayerNorm** with learned scale/shift \((\alpha,\beta,\gamma)\) predicted by an MLP. The student uses **4 self-attention blocks + 24 Mamba blocks** (≈86% Mamba, 14% attention), hidden size **1152**. For Mamba2, they set **SSM state dim = 256** and **expand factor = 2**.

**Tokenization for Mamba + non-causal context.** Since Mamba operates on 1D sequences, 2D tokens are raster-scanned; to better capture non-causal/global interactions they use **bidirectional scanning** with **interleaved width-first and height-first** orderings. The **same Mamba weights are shared** across the two scan directions and outputs are fused via a **linear projection**.

**Training pipeline (multi-stage).**  
1) **Layer-level teacher forcing (alignment pretraining).** Directly matching teacher/student layer outputs is unstable because early mismatch in causal Mamba can snowball across layers compared to non-causal attention. They inject *teacher intermediate inputs* as pseudo-ground-truth into each student Mamba token mixer. Let teacher model be \(\epsilon_{\theta'}\), student \(\epsilon_\theta\), noisy latent \(z_t\), timestep \(t\), prompt \(\tau\). Teacher token-mixer input at layer \(n\):
\[
h^{(n)}_{\theta'} = \epsilon^{(n)}_{\theta'}(z_t,t,\tau). \tag{5}
\]
Student Mamba token mixer \(MA^{(n)}_\theta\) is trained to match the teacher self-attention token mixer \(SA^{(n)}_{\theta'}\) output given the *same* \(h^{(n)}_{\theta'}\):
\[
L_{\text{forcing}}=\sum_{n=1}^N \mathbb{I}^{(n)}\left\|MA^{(n)}_{\theta}\!\left(h^{(n)}_{\theta'}\right)-SA^{(n)}_{\theta'}\!\left(h^{(n)}_{\theta'}\right)\right\|_2^2, \tag{6}
\]
and optimize under the diffusion data distribution:
\[
\bar{\theta}=\arg\min_{\bar{\theta}}\,\mathbb{E}_{q(z_t|z_0)}\,L_{\text{forcing}}. \tag{7}
\]
2) **Feature-based knowledge distillation (KD).** Initialize non-Mamba student weights by **copying** from teacher; keep only token mixers trainable (self-attn + Mamba), freeze everything else. Loss combines: diffusion noise MSE,
\[
L_{\text{mse}}=\|\epsilon-\epsilon_\theta(z_t,t,\tau)\|_2^2, \tag{8}
\]
teacher soft-label matching,
\[
L_{\text{pseudo}}=\|\epsilon_{\theta'}(z_t,t,\tau)-\epsilon_\theta(z_t,t,\tau)\|_2^2, \tag{9}
\]
and per-layer token-mixer feature matching,
\[
L_{\text{mixer}}=\frac{1}{N}\sum_{n=1}^N\left\|\epsilon^{[n]}_{\theta'}(z_t,t,\tau)-\epsilon^{[n]}_\theta(z_t,t,\tau)\right\|_2^2. \tag{10}
\]
Total distillation objective:
\[
L_{\text{distill}}=L_{\text{mse}}+\lambda_1 L_{\text{pseudo}}+\lambda_2 L_{\text{mixer}}, \quad
\theta=\arg\min_\theta \mathbb{E}_{q(z_t|z_0)}L_{\text{distill}}. \tag{11–12}
\]
(They use \(\lambda_1=0.5,\lambda_2=0.2\) in experiments.)
3) **Model adaptation (optional).** Replace components that hinder multi-resolution behavior: switch sine-cosine positional embeddings to a **centered sine-cosine** variant normalized by the long-edge length (enabling *zero-shot* higher-res), and replace PixArt-α’s SD1.5 VAE with **SDXL VAE** (noted as better for high-res). Despite these changes, the model reportedly re-converges within **100k steps**.  
4) **High-resolution fine-tuning.** Starting from distilled 512×512, fine-tune with mixed 512/1024 for **40k steps** (1024 ratio 80%), then fine-tune on 2048×2048 for **20k steps**, yielding 2K generation plus **zero-shot 4K** capability.

*(Note: optimizer, learning rate, batch size, and number of diffusion timesteps are not specified in the provided excerpt; they do specify ε-prediction, a quadratic noise schedule, and EMA decay 0.9999.)*

### Experiments & Results
**Setup / model.** The main student is a **0.7B** hybrid diffusion model (28 blocks; 4 SA + 24 Mamba2), with interleaving pattern:  
“**SA-(HM-WM)×3-SA-(HM-WM)×3-SA-(HM-WM)×3-SA-(HM-WM)×3**”, where HM/WM denote height-/width-scan Mamba blocks. They use **SDXL VAE** and **Flan-XXL T5** (both frozen). Training data: **200M image–text pairs**. Distillation uses ε-prediction, **quadratic noise schedule**, and **EMA=0.9999**.

**Metrics and datasets.**
- **GenEval score** [17] for prompt-following compositionality (subscores: position, counting, colors, attribute binding, single object, two object; plus overall).
- **FID-30K** on **MS-COCO 2014 validation** [35] (zero-shot evaluation).
- Efficiency measured on **1× NVIDIA H100**, reporting sampling **throughput (#samples/s)** and **latency** (batch size 1).

**Key ablation findings (GenEval, 512×512 base).** Training the hybrid Mamba model directly is hard; distillation components are necessary. Layer-level teacher forcing improves global/contextual tasks (notably the “two object” score), supporting the claim that forcing mitigates error propagation when distilling non-causal attention into sequential Mamba. They also test architectural choices: bidirectional vs unidirectional scan, and removing self-attention blocks.

**Main numbers (copied from provided tables).**

*Table A: GenEval (Overall ↑) ablations (selected)*

| Method | Overall |
|---|---:|
| minDALL-E | 0.227 |
| SD v1.5 | 0.427 |
| PixArt-α (teacher / upper bound) | 0.481 |
| baseline hybrid Mamba (train from scratch) | 0.301 |
| + non-Mamba weight initialization | 0.397 |
| + \(L_{\text{soft}}\) (soft label / pseudo) | 0.452 |
| + \(L_{\text{feature}}\) (mixer feature KD) | 0.462 |
| + **teacher forcing** (**T2MD**) | **0.485** |
| Causal-to-causal Mamba initialization (applied to non-causal DiT) | 0.433 |
| Bi-dir → Uni-dir | 0.448 |
| No SA (remove self-attention blocks) | 0.420 |

The paper also highlights that T2MD improves GenEval by **+0.184** over the “baseline hybrid Mamba” (0.485 vs 0.301), and is comparable to (slightly above) the teacher’s 0.481.

*Table B: FID-30K on MS-COCO 2014 val (↓ better, zero-shot)*

| Method | #Params | FID-30K ↓ |
|---|---:|---:|
| DALLE | 12.0B | 27.5 |
| GLIDE | 5.0B | 12.24 |
| LDM | 1.4B | 12.64 |
| DALLE 2 | 6.5B | 10.39 |
| StyleGAN-T | 1.0B | 13.90 |
| SD v1.5 | 0.9B | 9.62 |
| Dimba | 0.9B | 8.93 |
| LinFusion | 0.9B | 12.57 |
| PixArt-α (teacher) | 0.6B | 7.32 |
| **T2MD (ours)** | **0.7B** | **8.63** |

T2MD is worse than the teacher PixArt-α on FID (8.63 vs 7.32) but outperforms several baselines (e.g., SD1.5 at 9.62) while staying relatively small (0.7B). The authors interpret this as evidence that sequential/causal SSMs can model non-causal visual dependencies when trained appropriately.

*Table C: High-resolution efficiency (1×H100, bz=1)*

| Resolution | Throughput (samples/s) | T2MD latency | SA baseline latency | Speedup |
|---|---:|---:|---:|---:|
| 2048×2048 | 0.24 | 2.8s | 4.2s | 1.5× |
| 3840×2160 | 0.15 | 6.5s | 13.6s | 2.1× |

Baseline DiT uses **FlashAttention-2** for self-attention. The speedup grows with resolution, consistent with attention’s quadratic scaling vs Mamba’s linear complexity. Qualitatively, the paper shows 2048×2048 and 2688×1536 samples, plus **zero-shot 4K** samples after adaptation and fine-tuning.

### Discussion & Conclusion
T2MD demonstrates that distillation (especially layer-level teacher forcing + feature-based KD) can make training Mamba-based diffusion backbones practical, closing much of the quality gap to a strong DiT teacher while substantially improving high-resolution sampling efficiency. The hybrid design (small SA fraction + mostly Mamba2) appears important: removing SA or reducing bidirectionality hurts GenEval, suggesting pure sequential modeling still struggles with global visual dependencies. The approach enables beyond-2K generation (2048×2048 fine-tuned) and zero-shot 4K sampling, though the best FID still lags behind the teacher DiT.

## Key Contributions
- Introduces **T2MD**, a **Transformer-to-Mamba distillation pipeline** for diffusion models that avoids expensive from-scratch Mamba base-model training.
- Proposes **layer-level teacher forcing** to mitigate **error accumulation** when distilling **non-causal self-attention** layers into **sequential/causal Mamba** token mixers, combined with **feature-based token-mixer KD** and teacher soft labels.
- Demonstrates a **0.7B hybrid Mamba diffusion model** (≈86% Mamba2, 14% self-attention) that can generate **2048×2048** images after fine-tuning and achieves **2.1×** faster **4K** sampling latency than a comparable DiT baseline.

## Potential Relevance
This paper is directly useful if your hypothesis involves replacing attention-heavy diffusion backbones with linear-time sequence models (SSMs/Mamba) while keeping high-resolution quality. The layer-level teacher forcing idea is a concrete mechanism to stabilize *cross-architecture* distillation when teacher and student have mismatched causality/interaction patterns—potentially applicable beyond Mamba (e.g., other linear mixers). The ablations (bidirectional vs unidirectional scanning, removing SA blocks) are particularly informative for designing hybrid token mixers that retain global dependency modeling in large 2D generation.