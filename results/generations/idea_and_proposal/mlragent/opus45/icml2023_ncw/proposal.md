# Research Proposal: Compression-Aware Distillation: Learning Student Networks via Rate-Distortion Optimization

## 1. Introduction

### Background

The rapid proliferation of large-scale foundation models, including vision transformers, large language models, and multimodal architectures, has revolutionized machine learning capabilities across diverse domains. However, deploying these models on resource-constrained devices—mobile phones, edge computing platforms, and embedded systems—remains challenging due to their substantial memory footprints and computational requirements. Knowledge distillation has emerged as a prominent technique for model compression, transferring knowledge from a large "teacher" network to a compact "student" network by minimizing the divergence between their outputs or intermediate representations.

Despite significant progress, current knowledge distillation approaches suffer from a fundamental limitation: they treat compression as a separate, downstream step. Students are first trained to mimic teacher behavior, and then post-training quantization or pruning is applied for deployment. This decoupled paradigm is inherently suboptimal. As demonstrated by Dai et al. (2018) in their work on the variational information bottleneck, neural network representations contain significant redundancy that can be eliminated through information-theoretic optimization. When distilled students undergo post-hoc compression, their learned representations—optimized purely for task performance—often exhibit high entropy and lack the structural properties conducive to efficient encoding, resulting in substantial accuracy degradation.

Recent advances in neural compression, particularly learned image compression (Fu et al., 2023; Fu et al., 2025), have demonstrated that explicitly optimizing rate-distortion trade-offs during training yields representations that are simultaneously high-quality and efficiently compressible. These methods employ learnable entropy models to estimate coding costs and optimize end-to-end through differentiable quantization. Similarly, extreme compression techniques for large language models (2024) have shown that integrating quantization-aware objectives during fine-tuning significantly outperforms post-hoc quantization.

### Research Objectives

This research proposes **Compression-Aware Distillation (CAD)**, a unified framework that integrates knowledge distillation and neural compression through rate-distortion optimization. Our primary objectives are:

1. To develop a principled information-theoretic framework that jointly optimizes task distortion (knowledge transfer quality) and representation rate (compressibility) during student network training.

2. To design learnable entropy models that accurately estimate the bit-rate of intermediate layer activations, enabling explicit rate control throughout the network.

3. To establish training algorithms with progressive rate-distortion trade-off scheduling that yield students achieving superior accuracy-compression Pareto frontiers.

4. To empirically validate that compression-aware students exhibit structured properties—lower entropy, increased sparsity, and reduced intrinsic dimensionality—that enable 2-4× better compression ratios at equivalent accuracy compared to distill-then-compress baselines.

### Significance

This research bridges the historically separate fields of knowledge distillation and neural compression, contributing to the workshop's core theme of unifying machine learning and information theory. The proposed framework has significant practical implications for deploying foundation models on edge devices, reducing both storage requirements and inference costs. Furthermore, the theoretical insights into rate-distortion trade-offs in representation learning may inform future research on efficient AI systems and the information-theoretic understanding of deep learning.

## 2. Methodology

### 2.1 Problem Formulation

Consider a teacher network $T$ with parameters $\theta_T$ and a student network $S$ with parameters $\theta_S$, where $S$ has significantly fewer parameters. Let $\mathbf{x}$ denote an input sample and $\mathbf{y}$ the corresponding label. The teacher produces output logits $T(\mathbf{x}; \theta_T)$ and intermediate feature maps $\{f_T^{(l)}(\mathbf{x})\}_{l=1}^{L_T}$ at various layers. Similarly, the student produces $S(\mathbf{x}; \theta_S)$ and $\{f_S^{(l)}(\mathbf{x})\}_{l=1}^{L_S}$.

Traditional knowledge distillation minimizes:
$$\mathcal{L}_{\text{KD}} = \alpha \cdot \mathcal{L}_{\text{task}}(\mathbf{y}, S(\mathbf{x})) + (1-\alpha) \cdot D_{\text{KL}}(\sigma(T(\mathbf{x})/\tau) \| \sigma(S(\mathbf{x})/\tau))$$

where $\sigma$ is the softmax function, $\tau$ is the temperature, and $\alpha$ balances task loss and distillation loss.

### 2.2 Rate-Distortion Framework for Distillation

We reformulate knowledge distillation as a rate-distortion optimization problem. The total objective becomes:

$$\mathcal{L}_{\text{CAD}} = \underbrace{\mathcal{D}(T, S; \mathbf{x}, \mathbf{y})}_{\text{Distortion}} + \lambda \cdot \underbrace{\mathcal{R}(\{f_S^{(l)}\}_{l \in \mathcal{L}_c})}_{\text{Rate}}$$

**Distortion Term:** The distortion $\mathcal{D}$ captures both task performance and knowledge transfer quality:
$$\mathcal{D}(T, S; \mathbf{x}, \mathbf{y}) = \mathcal{L}_{\text{task}}(\mathbf{y}, S(\mathbf{x})) + \beta_1 \cdot \mathcal{L}_{\text{logit}}(T, S) + \beta_2 \cdot \mathcal{L}_{\text{feature}}(T, S)$$

where:
- $\mathcal{L}_{\text{task}}$ is the cross-entropy loss for classification or appropriate loss for other tasks
- $\mathcal{L}_{\text{logit}} = D_{\text{KL}}(\sigma(T(\mathbf{x})/\tau) \| \sigma(S(\mathbf{x})/\tau))$
- $\mathcal{L}_{\text{feature}} = \sum_{(l_T, l_S) \in \mathcal{M}} \|g_{l_S}(f_S^{(l_S)}) - f_T^{(l_T)}\|_2^2$, where $g_{l_S}$ are learnable projection layers and $\mathcal{M}$ defines layer correspondences

**Rate Term:** The rate $\mathcal{R}$ estimates the total coding cost of selected intermediate representations:
$$\mathcal{R}(\{f_S^{(l)}\}_{l \in \mathcal{L}_c}) = \sum_{l \in \mathcal{L}_c} R^{(l)}(f_S^{(l)})$$

where $\mathcal{L}_c \subseteq \{1, \ldots, L_S\}$ denotes compression-critical layers (e.g., after major blocks).

### 2.3 Learnable Entropy Models for Rate Estimation

Inspired by neural image compression, we introduce learnable entropy models at each selected layer to estimate the bit-rate of quantized activations.

**Quantization:** For each activation tensor $f_S^{(l)} \in \mathbb{R}^{B \times C \times H \times W}$ (batch × channels × height × width), we apply uniform scalar quantization:
$$\hat{f}_S^{(l)} = \text{round}(f_S^{(l)} / \Delta^{(l)}) \cdot \Delta^{(l)}$$

where $\Delta^{(l)}$ is a learnable quantization step size. During training, we employ the straight-through estimator (STE) for gradient computation through the non-differentiable rounding operation:
$$\frac{\partial \hat{f}_S^{(l)}}{\partial f_S^{(l)}} \approx 1$$

**Entropy Estimation:** We model the distribution of quantized activations using a factorized prior with learnable parameters. For each channel $c$ at layer $l$, we assume:
$$p(\hat{f}_{S,c}^{(l)} | \psi_c^{(l)}) = \prod_{i,j} p(\hat{f}_{S,c,i,j}^{(l)} | \psi_c^{(l)})$$

where $\psi_c^{(l)}$ parameterizes a flexible density model (e.g., Gaussian mixture or learned non-parametric density). The rate for layer $l$ is:
$$R^{(l)}(f_S^{(l)}) = \mathbb{E}\left[-\sum_{c,i,j} \log_2 p(\hat{f}_{S,c,i,j}^{(l)} | \psi_c^{(l)})\right]$$

In practice, we use a continuous relaxation during training by adding uniform noise $\mathcal{U}(-0.5, 0.5)$ instead of rounding, following the approach in learned image compression.

**Hyperprior for Context Modeling (Optional):** For layers with significant spatial correlations, we employ a hyperprior network $h^{(l)}$ that captures dependencies:
$$\mathbf{z}^{(l)} = h_a^{(l)}(f_S^{(l)}), \quad \hat{\mathbf{z}}^{(l)} = \text{round}(\mathbf{z}^{(l)})$$
$$\mu^{(l)}, \sigma^{(l)} = h_s^{(l)}(\hat{\mathbf{z}}^{(l)})$$

The rate then incorporates both the latent and hyperprior:
$$R^{(l)} = \mathbb{E}[-\log_2 p(\hat{f}_S^{(l)} | \mu^{(l)}, \sigma^{(l)})] + \mathbb{E}[-\log_2 p(\hat{\mathbf{z}}^{(l)})]$$

### 2.4 Progressive Training Algorithm

Direct optimization with a fixed $\lambda$ can lead to training instabilities or suboptimal solutions. We propose a progressive training schedule:

**Algorithm: Compression-Aware Distillation Training**

1. **Initialization Phase** (Epochs 1 to $E_1$):
   - Train with $\lambda = 0$ (standard distillation)
   - Initialize entropy model parameters $\{\psi^{(l)}\}$

2. **Rate Introduction Phase** (Epochs $E_1$ to $E_2$):
   - Linearly anneal $\lambda$ from 0 to $\lambda_{\text{target}}$
   - Update all parameters including entropy models

3. **Joint Optimization Phase** (Epochs $E_2$ to $E_{\text{total}}$):
   - Fix $\lambda = \lambda_{\text{target}}$
   - Fine-tune with periodic entropy model recalibration

4. **Multi-Rate Training** (Optional):
   - Train with multiple $\lambda$ values simultaneously using conditional batch normalization
   - Enables a single model to operate at different rate-distortion points

### 2.5 Experimental Design

**Datasets:**
- **Image Classification:** CIFAR-100, ImageNet-1K
- **Object Detection:** MS-COCO
- **Natural Language Understanding:** GLUE benchmark

**Model Architectures:**
- Teachers: ResNet-152, ViT-Large, BERT-Large
- Students: ResNet-18/34, ViT-Tiny/Small, DistilBERT

**Baselines:**
1. Standard knowledge distillation + post-training quantization (PTQ)
2. Standard distillation + quantization-aware training (QAT)
3. FEDS (Fu et al., 2025) adapted for general networks
4. Variational Information Bottleneck compression (Dai et al., 2018)

**Evaluation Metrics:**
- **Task Performance:** Top-1/Top-5 accuracy, mAP, GLUE scores
- **Compression Metrics:** 
  - Model size (MB) after quantization
  - Bits-per-parameter (BPP)
  - Compression ratio relative to full-precision model
- **Efficiency Metrics:**
  - Inference latency on target hardware (NVIDIA Jetson, mobile CPU)
  - FLOPs reduction
- **Representation Analysis:**
  - Entropy of layer activations
  - Intrinsic dimensionality (following Konz & Mazurowski, 2024)
  - Sparsity patterns

**Experimental Protocol:**
1. Train student networks with CAD at various $\lambda$ values to construct rate-distortion curves
2. Apply final quantization (4-bit, 8-bit) to all models
3. Measure accuracy drop from quantization for CAD vs. baselines
4. Analyze learned representations for structural properties
5. Deploy on edge devices and measure end-to-end latency

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Quantitative Results:**
1. **Superior Pareto Frontiers:** CAD-trained students are expected to achieve 2-4× better compression ratios at equivalent accuracy compared to distill-then-compress baselines. For instance, on ImageNet with a ResNet-18 student, we anticipate achieving 75% top-1 accuracy at 4-bit quantization, compared to 70% for standard distillation followed by PTQ.

2. **Reduced Quantization Degradation:** The accuracy gap between full-precision and quantized models should be significantly smaller for CAD students (< 1% degradation) compared to baselines (3-5% degradation).

3. **Structured Representations:** Activation entropy measurements are expected to show 30-50% reduction in coding cost for CAD students, with increased sparsity (40-60% near-zero activations) and lower intrinsic dimensionality.

**Qualitative Insights:**
1. Visualization of learned representations will reveal structured patterns amenable to efficient coding
2. Analysis of layer-wise rate allocation will provide insights into which layers benefit most from rate constraints
3. The relationship between $\lambda$ and downstream task performance will establish practical guidelines for practitioners

### Broader Impact

**Practical Applications:**
- Enables deployment of foundation model capabilities on smartphones and IoT devices
- Reduces cloud computing costs for inference-heavy applications
- Facilitates real-time AI applications in bandwidth-constrained environments

**Theoretical Contributions:**
- Establishes formal connections between knowledge distillation and rate-distortion theory
- Provides empirical evidence for the information bottleneck hypothesis in practical settings
- Opens new research directions in information-theoretic analysis of representation learning

**Community Impact:**
- Open-source release of CAD framework and pretrained models
- Benchmark datasets for evaluating compression-aware learning methods
- Tutorial materials bridging neural compression and knowledge distillation communities

This research directly addresses the workshop's call for integrating information-theoretic principles with efficient AI techniques, contributing to the next generation of scalable, efficient information-processing systems.