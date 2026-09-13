# Research Proposal: Multi-Scale Perceptual Information Bottleneck for Unified Rate-Distortion-Perception Optimization in Neural Image Compression

## 1. Introduction

### 1.1 Background

The exponential growth of visual data across digital platforms has intensified the demand for efficient image compression techniques that preserve both fidelity and perceptual quality. Traditional codecs such as JPEG, JPEG2000, and HEVC have served as industry standards for decades, optimizing primarily for rate-distortion (R-D) performance measured through pixel-wise metrics like Peak Signal-to-Noise Ratio (PSNR) and Mean Squared Error (MSE). However, these metrics often fail to capture human perceptual preferences, leading to reconstructions that, while mathematically accurate, appear blurry or lack fine details that humans find visually important.

The emergence of neural image compression has revolutionized the field, with learned approaches now surpassing traditional codecs on standard benchmarks. Pioneering work by Ballé et al. (2018) introduced the hyperprior architecture, establishing variational autoencoders with learned entropy models as the dominant paradigm. Subsequent advances, particularly the High-Fidelity Generative Compression (HiFiC) framework by Mentzer et al. (2020), demonstrated that incorporating adversarial training could dramatically improve perceptual quality at low bitrates. However, GAN-based approaches introduce significant challenges: training instability, mode collapse, computational overhead, and the need for careful hyperparameter tuning across multiple loss terms.

A fundamental theoretical insight connects compression and machine learning: both disciplines seek to extract and preserve essential information while discarding redundancy. The Information Bottleneck (IB) principle, formalized by Tishby et al. (2000), provides an elegant framework for this tradeoff, seeking representations that maximally compress input data while preserving information relevant to a target variable. The Variational Information Bottleneck (VIB) by Alemi et al. (2017) made this principle tractable for deep learning through variational bounds.

Despite these advances, a critical gap remains: current neural compression methods either optimize pixel-wise distortion (yielding high PSNR but poor perceptual quality) or require complex multi-objective optimization with adversarial losses (achieving perceptual quality at the cost of training complexity). The three-way tradeoff between rate (R), distortion (D), and perception (P)—formalized by Blau and Michaeli (2019)—remains difficult to navigate with existing approaches.

### 1.2 Research Objectives

This research proposes a novel framework called Multi-Scale Perceptual Information Bottleneck (MS-PIB) that unifies rate-distortion-perception optimization through information-theoretic principles. Our central hypothesis posits that computing the information bottleneck objective in multi-scale perceptual feature space—rather than pixel space—enables encoders to naturally preserve perceptually-relevant information while discarding imperceptible details, all controlled through a single Lagrange multiplier β.

The specific objectives are:

1. **Develop the MS-PIB framework** that integrates variational information bottleneck optimization with multi-scale VGG-19 perceptual features (conv1-5) for neural image compression.

2. **Demonstrate unified R-D-P navigation** through a single β parameter, eliminating the need for adversarial training while achieving competitive perceptual quality.

3. **Validate the causal mechanism** linking multi-scale perceptual features to smooth loss landscapes and stable optimization dynamics.

4. **Establish theoretical connections** between perceptual-space information bottleneck and the rate-distortion-perception tradeoff surface.

### 1.3 Significance

This research addresses fundamental challenges at the intersection of information theory, perception science, and neural compression. By grounding perceptual optimization in information-theoretic principles, we provide:

- **Theoretical foundation**: A principled framework connecting IB theory to human visual perception
- **Practical simplification**: Elimination of adversarial training complexity while maintaining perceptual quality
- **Unified control**: Single-parameter navigation of the R-D-P surface
- **Reproducibility**: Stable training dynamics enabling consistent results across runs

Success would represent a significant advance in understanding how information-theoretic principles can directly optimize for human perception, with implications extending beyond image compression to video coding, generative modeling, and representation learning.

## 2. Methodology

### 2.1 Theoretical Framework

#### 2.1.1 Standard Information Bottleneck

The classical Information Bottleneck seeks a compressed representation $Z$ of input $X$ that preserves information about target $Y$:

$$\mathcal{L}_{IB} = I(X; Z) - \beta \cdot I(Z; Y)$$

where $I(\cdot; \cdot)$ denotes mutual information and $\beta$ controls the rate-relevance tradeoff.

#### 2.1.2 Perceptual Information Bottleneck

We propose computing the IB objective in perceptual feature space. Let $\phi_l(x)$ denote the activation of a pre-trained VGG-19 network at layer $l$ for image $x$. Our Perceptual Information Bottleneck (PIB) objective becomes:

$$\mathcal{L}_{PIB} = R(z) + \beta \cdot D_{perceptual}(\hat{x}, x)$$

where $R(z)$ is the rate (bits) estimated by the entropy model, and:

$$D_{perceptual}(\hat{x}, x) = \sum_{l=1}^{L} w_l \cdot \|\phi_l(\hat{x}) - \phi_l(x)\|_2^2$$

Here, $\hat{x}$ is the reconstructed image, $L=5$ corresponds to VGG layers {conv1_2, conv2_2, conv3_4, conv4_4, conv5_4}, and $w_l$ are learnable layer weights initialized uniformly.

#### 2.1.3 Multi-Scale Formulation

The multi-scale aspect operates through hierarchical feature extraction:

- **Low-level features** (conv1-2): Capture edges, textures, local patterns
- **Mid-level features** (conv3): Encode texture statistics, local structure
- **High-level features** (conv4-5): Represent semantic content, object parts

This hierarchy ensures the encoder preserves information across perceptual scales, with the combined loss:

$$\mathcal{L}_{MS-PIB} = \mathbb{E}_{q(z|x)}[-\log p(z)] + \beta \sum_{l=1}^{5} w_l \cdot d_l(\hat{x}, x)$$

where $d_l(\hat{x}, x) = \frac{1}{H_l W_l C_l}\|\phi_l(\hat{x}) - \phi_l(x)\|_2^2$ normalizes by spatial and channel dimensions.

### 2.2 Architecture Design

#### 2.2.1 Base Architecture

We build upon the CompressAI hyperprior architecture, which consists of:

- **Encoder** $g_a$: Maps image $x \in \mathbb{R}^{H \times W \times 3}$ to latent $y \in \mathbb{R}^{h \times w \times M}$
- **Hyper-encoder** $h_a$: Extracts side information $z$ from $y$
- **Hyper-decoder** $h_s$: Reconstructs entropy parameters from quantized $\hat{z}$
- **Decoder** $g_s$: Reconstructs image $\hat{x}$ from quantized $\hat{y}$

The rate is computed as:

$$R = \mathbb{E}[-\log_2 p_{\hat{y}|\hat{z}}(\hat{y}|\hat{z})] + \mathbb{E}[-\log_2 p_{\hat{z}}(\hat{z})]$$

#### 2.2.2 MS-PIB Modifications

We introduce the following modifications:

1. **Perceptual Feature Extractor**: Frozen VGG-19 (ImageNet pretrained) extracting features at 5 layers
2. **Learnable Layer Weights**: Parameters $w_l$ (initialized to 0.2 each) optimized jointly
3. **Feature Normalization**: Instance normalization before distance computation for scale invariance

### 2.3 Training Procedure

#### 2.3.1 Data Collection and Preprocessing

- **Training Data**: 1 million images from ImageNet, randomly cropped to 256×256
- **Validation Data**: Kodak dataset (24 images, 768×512)
- **Test Data**: CLIC Professional 2020 (41 images), Tecnick (100 images)
- **Augmentation**: Random horizontal flips, no color augmentation to preserve perceptual statistics

#### 2.3.2 Optimization Algorithm

**Algorithm 1: MS-PIB Training**

```
Input: Training images X, β values, learning rate η, epochs E
Output: Trained encoder g_a, decoder g_s, hyperprior h_a, h_s

1. Initialize CompressAI hyperprior weights
2. Initialize layer weights w = [0.2, 0.2, 0.2, 0.2, 0.2]
3. Load frozen VGG-19 feature extractor φ

4. For epoch = 1 to E:
5.   For batch x in DataLoader(X):
6.     # Forward pass
7.     y = g_a(x)
8.     z = h_a(y)
9.     ẑ = Quantize(z)
10.    ŷ = Quantize(y, entropy_params=h_s(ẑ))
11.    x̂ = g_s(ŷ)
12.    
13.    # Compute rate
14.    R = -log₂ p(ŷ|ẑ) - log₂ p(ẑ)
15.    
16.    # Compute multi-scale perceptual distortion
17.    D_perc = 0
18.    For l = 1 to 5:
19.      D_perc += w_l * ||φ_l(x̂) - φ_l(x)||²₂ / (H_l * W_l * C_l)
20.    
21.    # Total loss
22.    L = R + β * D_perc
23.    
24.    # Backward pass and update
25.    Backpropagate(L)
26.    Update(g_a, g_s, h_a, h_s, w; η)
27.    
28. Return trained models
```

#### 2.3.3 Hyperparameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Batch size | 256 | Stable MI estimation |
| Learning rate | 1e-4 | Standard for CompressAI |
| Optimizer | Adam (β₁=0.9, β₂=0.999) | Adaptive learning |
| Training steps | 2M | Convergence criterion |
| β sweep | {0.001, 0.003, 0.01, 0.03, 0.1} | Log-scale coverage |
| Latent channels M | 192 | CompressAI default |

### 2.4 Experimental Design

#### 2.4.1 Experiment 1: Existence Validation (SH1)

**Objective**: Verify MS-PIB achieves target perceptual quality.

**Protocol**:
1. Train MS-PIB models at β ∈ {0.001, 0.003, 0.01, 0.03, 0.1}
2. Evaluate on Kodak dataset at target 0.15 BPP
3. Measure LPIPS (AlexNet backbone), PSNR, MS-SSIM

**Success Criterion**: LPIPS ≤ 0.04 at 0.15 BPP (p < 0.05, paired t-test, n=24 images × 5 seeds)

**Falsification**: LPIPS > 0.08 triggers hypothesis rejection

#### 2.4.2 Experiment 2: Mechanism Validation (SH2)

**Objective**: Validate the three-step causal mechanism.

**Sub-experiments**:

*H-M1: Multi-scale → Smooth Loss Landscape*
- Compare loss variance during training: multi-scale (5 layers) vs single-scale (conv4 only) vs pixel-space MSE
- Metric: Coefficient of variation of gradient norms over 1000 steps
- Expected: 50% lower variance for multi-scale

*H-M2: Smooth Landscape → Stable VIB Optimization*
- Track training loss curves across 5 random seeds
- Metric: Standard deviation of final loss values
- Expected: Multi-scale achieves lower variance

*H-M3: Stable VIB → Single β Navigation*
- Sweep β and plot LPIPS vs BPP curves
- Metric: Spearman correlation ρ between β and LPIPS
- Expected: ρ > 0.9 (monotonic relationship)

#### 2.4.3 Experiment 3: Comparative Evaluation (SH3)

**Objective**: Compare MS-PIB against state-of-the-art methods.

**Baselines**:
- CompressAI Hyperprior (MSE-optimized)
- CompressAI Hyperprior (MS-SSIM-optimized)
- HiFiC (GAN-based, from published results)
- TCM (Transformer-based, 2023)
- VVC/HEVC (traditional codecs)

**Metrics**:
- Rate: Bits per pixel (BPP)
- Distortion: PSNR (dB), MS-SSIM
- Perception: LPIPS (AlexNet), FID (10K samples)
- Computational: Training time, inference FLOPs

**Evaluation Protocol**:
- Generate R-D-P curves across 0.1-0.5 BPP range
- Report BD-rate savings relative to VVC anchor
- Conduct paired statistical tests (n ≥ 25 runs)

#### 2.4.4 Ablation Studies

1. **Layer Selection**: Compare {conv4 only}, {conv1-3}, {conv3-5}, {conv1-5}
2. **Weight Learning**: Fixed uniform vs learnable weights
3. **Feature Normalization**: With/without instance normalization
4. **β Scheduling**: Fixed vs annealed during training

### 2.5 Evaluation Metrics

| Metric | Formula/Tool | Interpretation |
|--------|--------------|----------------|
| BPP | $\frac{\text{bits}}{H \times W}$ | Lower is better |
| PSNR | $10 \log_{10}\frac{255^2}{\text{MSE}}$ | Higher is better |
| MS-SSIM | Multi-scale structural similarity | Higher is better |
| LPIPS | AlexNet-based perceptual distance | Lower is better |
| FID | Fréchet distance in Inception space | Lower is better |

### 2.6 Statistical Analysis

- **Effect size**: Cohen's d ≥ 0.5 for practical significance
- **Sample size**: n ≥ 25 independent runs (5 seeds × 5 β values)
- **Tests**: Paired t-tests for matched comparisons, Wilcoxon signed-rank for non-normal distributions
- **Reporting**: Mean ± standard deviation, 95% confidence intervals, p-values with Bonferroni correction

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1)**: We expect MS-PIB to achieve LPIPS ≤ 0.04 at 0.15 BPP on the Kodak dataset, matching HiFiC's perceptual quality without adversarial training. This would validate that information-theoretic principles can directly optimize for human perception.

**Secondary Outcomes**:
- **P2**: The β sweep from 0.001 to 0.1 will produce a monotonic LPIPS-BPP relationship (Spearman ρ > 0.9), demonstrating unified R-D-P navigation through a single parameter.
- **P3**: Multi-scale training will exhibit 50% lower loss variance compared to single-scale alternatives, confirming the smoothing effect of hierarchical features.

**Quantitative Targets**:

| Metric | Target | Baseline (Hyperprior) |
|--------|--------|----------------------|
| LPIPS @ 0.15 BPP | ≤ 0.04 | 0.10-0.15 |
| FID @ 0.15 BPP | ≤ 15 | 30-50 |
| Training stability | CV < 0.1 | CV ~ 0.2 |

### 3.2 Scientific Contributions

1. **Theoretical Contribution**: First demonstration that the information bottleneck principle, when computed in perceptual feature space, provides a principled foundation for rate-distortion-perception optimization. This bridges information theory and perceptual science.

2. **Methodological Contribution**: A novel training framework that eliminates adversarial losses while achieving competitive perceptual quality, significantly simplifying the neural compression pipeline.

3. **Empirical Contribution**: Comprehensive evaluation establishing the relationship between β, perceptual quality, and bitrate, providing practitioners with clear guidelines for deployment.

### 3.3 Broader Impact

**For Neural Compression Research**: MS-PIB provides a simpler, more stable alternative to GAN-based perceptual compression. The single-parameter control enables easier hyperparameter tuning and more reproducible results.

**For Information Theory**: This work demonstrates practical applications of IB principles beyond classification, extending to perceptual tasks where the "relevant information" is defined by human visual processing.

**For Applications**: Simplified training could accelerate deployment of neural codecs in bandwidth-constrained scenarios (mobile networks, satellite communication, archival storage) where perceptual quality matters.

**Limitations and Future Work**: 
- The reliance on VGG-19 features may not generalize to all image types (e.g., medical imaging, satellite imagery)
- Extension to video compression requires temporal modeling
- Theoretical analysis of the perceptual-space IB bounds remains for future work

### 3.4 Risk Mitigation

| Risk | Probability | Mitigation |
|------|-------------|------------|
| LPIPS target not met | Medium | Explore alternative perceptual networks (DINO, CLIP) |
| Training instability | Low | Gradient clipping, learning rate warmup |
| Non-monotonic β behavior | Low | Finer β grid, adaptive scheduling |
| Computational constraints | Low | Mixed precision training, gradient checkpointing |

### 3.5 Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Implementation | 2 weeks | MS-PIB codebase integrated with CompressAI |
| Experiment 1 (SH1) | 2 weeks | Existence validation results |
| Experiment 2 (SH2) | 2 weeks | Mechanism validation results |
| Experiment 3 (SH3) | 2 weeks | Comparative evaluation |
| Analysis & Writing | 2 weeks | Paper manuscript |

This research proposal presents a principled approach to unifying rate-distortion-perception optimization through information-theoretic foundations, with potential to simplify neural compression while maintaining state-of-the-art perceptual quality.