# Research Proposal: Provably Robust Watermark Detection via Randomized Smoothing

## 1. Title

**Provably Robust Watermark Detection via Randomized Smoothing: A Unified Certification Framework for Generative AI**

## 2. Introduction

### 2.1 Background

The rapid proliferation of generative AI technologies has created an urgent need for reliable content authentication mechanisms. Large language models, text-to-image systems, and synthetic media generators now produce content indistinguishable from human-created works, raising critical concerns about misinformation, intellectual property theft, and deepfake manipulation. In response, regulatory frameworks worldwide are mandating watermarking for AI-generated content. The European Union's AI Act (Article 52) requires that synthetic content be clearly identifiable, while California's AB 3211 mandates provenance tracking for AI-generated media. These regulations reflect a growing consensus that watermarking is essential infrastructure for the generative AI ecosystem.

However, current watermarking technologies face a fundamental limitation: they lack formal robustness guarantees against adversarial attacks. Existing watermark detectors demonstrate empirical robustness through experimental validation, but provide no mathematical certificates that guarantee detection under adversarial perturbations. This gap between regulatory requirements for auditable security and available technology creates significant risks for high-stakes applications such as deepfake detection in legal proceedings, intellectual property protection, and content authentication for journalism.

Recent work has explored various watermarking approaches across modalities. For images, methods like Tree-Ring watermarking embed signals in diffusion model latent spaces. For text, approaches range from logit manipulation during generation to post-hoc statistical detection. Audio and video watermarking leverage perceptual models to embed imperceptible signals. While some recent work (e.g., Unigram, 2024) provides provable guarantees for specific text watermarking schemes, no general framework exists for certifying the robustness of arbitrary neural watermark detectors across all generative AI modalities.

The field of adversarial robustness has developed powerful certification techniques, most notably randomized smoothing (Cohen et al., 2019), which provides provable $\ell_2$ robustness guarantees for image classifiers. This technique transforms any base classifier into a smoothed classifier with certified robustness by injecting Gaussian noise during inference and using statistical guarantees to compute a certified radius within which predictions are guaranteed to remain constant.

### 2.2 Research Objectives

This research proposes to bridge the gap between watermark detection and certified robustness by adapting randomized smoothing to provide the first provable $\ell_2$ robustness certificates for neural watermark detectors across all generative AI modalities. Our specific objectives are:

1. **Develop a unified certification framework** that applies randomized smoothing to watermark detection, providing mathematical guarantees that watermarks remain detectable under adversarial perturbations within a certified radius.

2. **Design adaptive variance selection mechanisms** that optimize the fundamental trade-off between clean accuracy and certified robustness across different modalities and watermark strengths.

3. **Validate certification guarantees empirically** across images, text, audio, and video, demonstrating that theoretical certificates translate to practical attack resistance.

4. **Establish practical feasibility** by demonstrating that certified watermark detection achieves target performance metrics: certified radius $r \geq 0.15$, clean accuracy $\geq 85\%$, and certification success rate $\geq 90\%$.

5. **Enable regulatory compliance** by providing auditable robustness certificates suitable for high-stakes applications requiring formal security guarantees.

### 2.3 Research Significance

This research makes three fundamental contributions:

**Theoretical Contribution:** We provide the first $\ell_2$ certification framework for watermark detection that is detector-agnostic and modality-independent. Unlike Unigram (2024), which provides provable guarantees for a specific text watermarking scheme, our framework applies to any neural watermark detector with probabilistic outputs. This generality enables certification of existing watermarking systems without requiring redesign.

**Methodological Contribution:** We develop an adaptive certification protocol that combines smoothed detector construction, variance optimization, efficient Monte Carlo sampling, and cross-modality normalization. This protocol enables practical offline certification (~2 minutes per sample) while balancing the accuracy-robustness trade-off through principled optimization.

**Practical Contribution:** We enable the first certifiable watermarking system compliant with emerging regulations like the EU AI Act and California AB 3211. By providing auditable mathematical certificates, our framework supports deployment in high-stakes applications where empirical robustness is insufficient, including legal evidence authentication, intellectual property litigation, and critical infrastructure protection.

The significance extends beyond watermarking to the broader challenge of deploying AI systems with formal security guarantees. Our work demonstrates how theoretical advances in adversarial robustness can be adapted to solve pressing real-world problems in AI safety and governance.

## 3. Methodology

### 3.1 Theoretical Framework

#### 3.1.1 Randomized Smoothing for Watermark Detection

Let $D: \mathcal{Z} \rightarrow \{0, 1\}$ be a base watermark detector that classifies content $z \in \mathcal{Z}$ as watermarked (1) or clean (0). The smoothed detector $\bar{D}$ is defined as:

$$\bar{D}(z) = \arg\max_{c \in \{0,1\}} \mathbb{P}_{\delta \sim \mathcal{N}(0, \sigma^2 I)}[D(z + \delta) = c]$$

where $\sigma$ is the smoothing variance and $\delta$ represents Gaussian noise.

#### 3.1.2 Certification Guarantee

Following Cohen et al. (2019), if the smoothed detector predicts class $c_A$ with probability $p_A$ and the runner-up class $c_B$ with probability $p_B$ where $p_A > p_B$, then the certified radius is:

$$r = \frac{\sigma}{2}\left(\Phi^{-1}(p_A) - \Phi^{-1}(p_B)\right)$$

where $\Phi^{-1}$ is the inverse cumulative distribution function of the standard normal distribution. This radius guarantees that for any adversarial perturbation $\|\delta\|_2 \leq r$, the smoothed detector's prediction remains $c_A$ with probability at least $1-\alpha$ (typically $\alpha = 0.001$).

#### 3.1.3 Adaptive Variance Selection

The key innovation is adaptive variance selection that optimizes the accuracy-robustness trade-off. For a given watermark strength (measured by signal-to-noise ratio SNR), we formulate the optimization problem:

$$\sigma^* = \arg\max_{\sigma} \left\{ r(\sigma) : \text{Accuracy}(\sigma) \geq \tau_{acc} \right\}$$

where $\tau_{acc}$ is the minimum acceptable accuracy threshold (85% in our targets).

### 3.2 Data Collection and Preparation

#### 3.2.1 Multi-Modal Datasets

We will conduct experiments across four modalities at three scales:

**Phase 1 - Toy Scale (Validation):**
- **Images:** MNIST (60K training, 10K test) with synthetic watermarks
- Purpose: Validate implementation and certification guarantee

**Phase 2 - Medium Scale (Cross-Modality):**
- **Images:** CIFAR-10 (50K training, 10K test)
- **Text:** SST-2 sentiment dataset (67K training, 1.8K test)
- **Audio:** Mozilla Common Voice (100 hours, 10K samples)
- Purpose: Establish cross-modality consistency

**Phase 3 - Realistic Scale (SOTA Comparison):**
- **Images:** ImageNet subset (100K training, 10K test)
- **Text:** GPT-2 generated text (50K samples from WebText)
- **Audio:** AudioSet (100K samples, 10-second clips)
- **Video:** YouTube-VIS (2.9K videos, 131K instances)
- Purpose: Demonstrate practical feasibility

#### 3.2.2 Watermark Embedding

For each modality, we implement state-of-the-art watermarking schemes:

**Images:** Tree-Ring watermarking for diffusion models, embedding watermark signal $w$ with strength parameter $\lambda$:
$$z_{watermarked} = z_{clean} + \lambda \cdot w$$

**Text:** Logit manipulation during generation, biasing token probabilities toward a secret key-based partition.

**Audio:** Spread-spectrum watermarking in frequency domain with SNR control.

**Video:** Frame-level watermarking with temporal consistency constraints.

Watermark strength is controlled via SNR, defined as:
$$\text{SNR} = 10 \log_{10} \frac{\|z_{clean}\|^2}{\|z_{watermarked} - z_{clean}\|^2}$$

We vary SNR from 5 dB (weak) to 15 dB (strong) to evaluate robustness-strength relationships.

### 3.3 Algorithmic Steps

#### 3.3.1 Base Detector Training

For each modality, we train a neural watermark detector $D_\theta$ using standard supervised learning:

1. **Architecture Selection:**
   - Images: ResNet-50
   - Text: RoBERTa-base
   - Audio: Wav2Vec 2.0
   - Video: TimeSformer

2. **Training Procedure:**
   - Loss: Binary cross-entropy
   - Optimizer: AdamW with learning rate $10^{-4}$
   - Batch size: 64
   - Training samples: 20K per condition (10K watermarked + 10K clean)
   - Validation: 20% holdout for early stopping

3. **Output:** Probabilistic detector $D_\theta(z) \in [0,1]$ representing watermark probability

#### 3.3.2 Smoothed Detector Construction

Given base detector $D_\theta$ and smoothing variance $\sigma$, construct smoothed detector $\bar{D}_\theta$:

**Algorithm 1: Smoothed Detection**
```
Input: Content z, base detector D_θ, variance σ, samples N
Output: Smoothed prediction and certified radius r

1. Initialize counters: count_watermarked = 0, count_clean = 0
2. For i = 1 to N:
   a. Sample δ_i ~ N(0, σ²I)
   b. Compute prediction: y_i = D_θ(z + δ_i)
   c. If y_i ≥ 0.5: count_watermarked += 1
   d. Else: count_clean += 1
3. Compute probabilities:
   p̂_watermarked = count_watermarked / N
   p̂_clean = count_clean / N
4. Determine prediction: ŷ = argmax(p̂_watermarked, p̂_clean)
5. Compute certified radius:
   r = (σ/2)(Φ⁻¹(max(p̂)) - Φ⁻¹(min(p̂)))
6. Return (ŷ, r)
```

#### 3.3.3 Adaptive Variance Optimization

To optimize $\sigma$ for each application context:

**Algorithm 2: Adaptive Variance Selection**
```
Input: Validation set V, base detector D_θ, accuracy threshold τ_acc
Output: Optimal variance σ*

1. Initialize candidate variances: Σ = {0.1, 0.2, 0.3, 0.5, 0.7, 1.0}
2. For each σ ∈ Σ:
   a. Compute clean accuracy on V using smoothed detector
   b. Compute average certified radius r̄(σ) on V
   c. If accuracy(σ) ≥ τ_acc:
      Store (σ, r̄(σ))
3. Select σ* = argmax{r̄(σ) : accuracy(σ) ≥ τ_acc}
4. Return σ*
```

#### 3.3.4 Monte Carlo Sample Size Selection

We use adaptive sample sizing based on Clopper-Pearson confidence intervals:

For confidence level $1-\alpha$ and desired precision $\epsilon$, the required sample size is:
$$N \geq \frac{1}{2\epsilon^2} \log\frac{2}{\alpha}$$

For $\alpha = 0.001$ and $\epsilon = 0.01$, we obtain $N \approx 10,000$ samples.

### 3.4 Experimental Design

#### 3.4.1 Factorial Design

We employ a full factorial design with the following factors:

- **Smoothing variance ($\sigma$):** {0.1, 0.2, 0.3, 0.5, 0.7, 1.0}
- **Watermark strength (SNR):** {5, 8, 10, 12, 15} dB
- **Modality:** {Image, Text, Audio, Video}
- **Monte Carlo samples (N):** {1K, 5K, 10K, 50K, 100K}

Total conditions: $6 \times 5 \times 4 \times 5 = 600$ experimental conditions

#### 3.4.2 Evaluation Protocol

For each experimental condition:

1. **Training Phase:**
   - Train base detector on 20K samples
   - Validate on 4K holdout samples
   - Select best checkpoint by validation accuracy

2. **Certification Phase:**
   - Certify 1K test samples using Algorithm 1
   - Record: certified radius $r$, clean accuracy, certification time
   - Compute statistics: mean, median, 95th percentile of $r$

3. **Attack Evaluation Phase:**
   - Generate 5K adversarial examples using PGD attack
   - Attack budget: $\|\delta\|_2 \in \{0.5r, 0.75r, r, 1.25r, 1.5r\}$
   - Measure attack success rate at each budget
   - Validate certification guarantee: success rate $\leq 5\%$ for $\|\delta\|_2 \leq r$

#### 3.4.3 Baseline Comparisons

We compare against state-of-the-art methods:

1. **ROBIN (2024):** Empirical robustness benchmark for watermarking
2. **RAWatermark (2024):** Claims "provable" robustness (empirical only)
3. **Unigram (2024):** Provable text watermarking (modality-specific)
4. **Standard detector:** Base detector without smoothing (no certification)

Comparison metrics:
- Certified radius (ours vs. 0 for empirical methods)
- Clean accuracy
- Attack success rate under various perturbations
- Cross-modality generalization
- Computational cost

### 3.5 Evaluation Metrics

#### 3.5.1 Primary Metrics

1. **Certified Radius ($r$):**
   - Definition: Maximum $\ell_2$ perturbation with guaranteed detection
   - Unit: Normalized by content magnitude
   - Target: $r \geq 0.15$

2. **Clean Accuracy:**
   - Definition: Detection accuracy on unperturbed content
   - Target: $\geq 85\%$

3. **Certification Success Rate:**
   - Definition: Proportion of samples receiving non-zero certificate
   - Target: $\geq 90\%$

#### 3.5.2 Secondary Metrics

4. **Attack Success Rate (ASR):**
   - Definition: Proportion of successful attacks within certified radius
   - Target: $\leq 5\%$ (validates certification guarantee)

5. **Certification Time:**
   - Definition: Wall-clock time for Algorithm 1
   - Target: $\leq 2$ minutes per sample

6. **Cross-Modality Variance:**
   - Definition: Coefficient of variation of $r$ across modalities (SNR-normalized)
   - Target: $\leq 20\%$

#### 3.5.3 Statistical Tests

**Hypothesis Testing:**

**P1 (Trade-off Relationship):**
- Test: Pearson correlation between $\sigma$ and $r$ (expect $\rho > 0.8$)
- Test: Pearson correlation between $\sigma$ and accuracy (expect $\rho < -0.7$)

**P2 (Watermark Strength Scaling):**
- Test: Linear regression of $r$ on SNR
- Hypothesis: Doubling SNR increases $r$ by $\geq 30\%$

**P3 (Certification Guarantee):**
- Test: One-sample proportion test for ASR within certified radius
- Null hypothesis: ASR $\leq 5\%$ at $\alpha = 0.05$

**P4 (Monte Carlo Convergence):**
- Test: Variance ratio test comparing $N=1K$ vs. $N=100K$
- Hypothesis: 100× samples reduces variance by $\geq 5×$

**P5 (Cross-Modality Consistency):**
- Test: One-way ANOVA for certified radius across modalities
- Post-hoc: Tukey HSD for pairwise comparisons
- Hypothesis: Coefficient of variation $\leq 20\%$

**Sample Size Justification:**
- Power analysis for proportion test (P3): $n=5000$ achieves power $>0.95$ for detecting 5% deviation from null
- ANOVA (P5): $n=1000$ per modality achieves power $>0.90$ for effect size $f=0.25$

### 3.6 Implementation Details

**Software Stack:**
- Framework: PyTorch 2.0
- Certification: Custom implementation based on Cohen et al. (2019) codebase
- Watermarking: Modality-specific libraries (Stable Signature for images, etc.)

**Hardware Requirements:**
- GPU: NVIDIA A100 (40GB) for realistic-scale experiments
- CPU: 32-core for parallel Monte Carlo sampling
- Storage: 2TB for datasets and checkpoints

**Reproducibility:**
- Random seeds fixed for all experiments
- Code and checkpoints released open-source
- Detailed hyperparameter logs for all runs

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

#### 4.1.1 Technical Outcomes

**Primary Outcome 1: Certification Framework Validation**
We expect to demonstrate that randomized smoothing successfully provides provable robustness certificates for watermark detection with:
- Certified radius $r \geq 0.15$ for strong watermarks (SNR $\geq 12$ dB)
- Clean accuracy $\geq 85\%$ with optimized variance selection
- Certification success rate $\geq 90\%$ across all modalities

**Primary Outcome 2: Empirical Guarantee Validation**
Attack evaluation will confirm that theoretical certificates translate to practical robustness:
- Attack success rate $\leq 5\%$ for perturbations $\|\delta\|_2 \leq r$
- Attack success rate $\geq 95\%$ for perturbations $\|\delta\|_2 > 1.5r$
- Clear phase transition at certified radius boundary

**Primary Outcome 3: Cross-Modality Generalization**
The framework will demonstrate consistent performance across modalities:
- Certified radius variance $\leq 20\%$ (SNR-normalized)
- Similar accuracy-robustness trade-off curves
- Unified variance selection strategy applicable to all modalities

#### 4.1.2 Methodological Outcomes

**Adaptive Variance Selection Protocol:**
We will deliver an optimization procedure that:
- Identifies Pareto-optimal $\sigma$ for given accuracy constraints
- Improves certified radius by $\geq 20\%$ vs. fixed variance
- Generalizes across watermark strengths and modalities

**Efficiency Optimizations:**
We expect to achieve practical certification times through:
- Adaptive Monte Carlo sampling (early stopping when confidence reached)
- Batch processing for parallel certification
- Target: $\leq 2$ minutes per sample with $N=10K$

**Benchmark Suite:**
We will release a comprehensive benchmark including:
- Certified detectors for 4 modalities
- Standardized evaluation protocol
- Attack suite for validation
- Baseline comparisons with ROBIN, RAWatermark, Unigram

#### 4.1.3 Theoretical Outcomes

**Robustness-Accuracy Trade-off Characterization:**
We will provide empirical characterization of the fundamental trade-off:
- Pareto frontier mapping for each modality
- Scaling laws relating watermark strength, variance, and certified radius
- Theoretical analysis of trade-off bounds

**Failure Mode Analysis:**
We will identify conditions under which certification fails:
- Minimum watermark strength for $r > 0$
- Maximum variance before accuracy collapse
- Modality-specific challenges and solutions

### 4.2 Scientific Impact

#### 4.2.1 Advancing Watermarking Research

This work establishes a new paradigm for watermark evaluation, shifting from empirical robustness testing to formal certification. Key impacts include:

1. **Standardization:** Providing a rigorous evaluation methodology that enables fair comparison across watermarking schemes
2. **Security Guarantees:** Enabling watermark designers to provide mathematical security claims rather than empirical demonstrations
3. **Attack Resistance:** Identifying the fundamental limits of adversarial robustness for watermark detection

#### 4.2.2 Bridging Adversarial Robustness and Watermarking

Our work demonstrates how theoretical advances in adversarial machine learning can solve practical problems in AI safety:

1. **Cross-Domain Transfer:** Showing that randomized smoothing generalizes beyond image classification to multi-modal detection tasks
2. **Practical Certification:** Demonstrating that provable robustness can achieve practical performance metrics
3. **Framework Generalization:** Establishing principles for adapting certification techniques to new domains

#### 4.2.3 Contributions to AI Safety

This research addresses critical AI safety challenges:

1. **Deepfake Detection:** Providing certified detectors for synthetic media identification
2. **Content Authentication:** Enabling verifiable provenance tracking for AI-generated content
3. **Adversarial Robustness:** Advancing understanding of certified defenses in realistic settings

### 4.3 Practical Impact

#### 4.3.1 Regulatory Compliance

Our framework directly addresses regulatory requirements:

**EU AI Act (Article 52):** Provides auditable certificates demonstrating that synthetic content detection meets robustness standards

**California AB 3211:** Enables provenance tracking with formal guarantees against adversarial manipulation

**Industry Standards:** Supports development of watermarking standards (e.g., C2PA) with security certifications

#### 4.3.2 High-Stakes Applications

The framework enables deployment in critical applications:

**Legal Evidence:** Watermark detection with mathematical guarantees suitable for court proceedings

**Intellectual Property:** Certified ownership verification resistant to adversarial removal attempts

**Journalism:** Authenticated content verification for combating misinformation

**Platform Moderation:** Scalable synthetic content detection with formal robustness

#### 4.3.3 Industry Adoption

We anticipate industry impact through:

1. **Open-Source Release:** Reference implementation enabling immediate adoption
2. **API Design:** Standardized certification interface for integration into existing systems
3. **Performance Benchmarks:** Demonstrating practical feasibility for production deployment
4. **Cost Analysis:** Quantifying computational requirements for budget planning

### 4.4 Broader Impact

#### 4.4.1 Policy and Governance

This research informs AI governance by:

1. **Evidence-Based Regulation:** Providing technical foundation for watermarking mandates
2. **Auditing Standards:** Establishing certification protocols for regulatory compliance
3. **Risk Assessment:** Quantifying security guarantees for policy decision-making

#### 4.4.2 Societal Benefits

Successful deployment of certified watermarking contributes to:

1. **Trust in Digital Media:** Enabling reliable authentication of content provenance
2. **Misinformation Combat:** Providing tools for identifying synthetic misinformation
3. **Creative Rights Protection:** Protecting artists and creators from unauthorized AI reproduction
4. **Democratic Discourse:** Preserving information integrity in public communication

#### 4.4.3 Limitations and Future Work

We acknowledge important limitations:

**Scope Limitations:**
- Certification limited to $\ell_2$ perturbations (not spatial transformations, compression, or regeneration attacks)
- Offline certification only (real-time certification requires further optimization)
- Requires trained detector (not applicable to zero-shot detection)

**Future Research Directions:**
1. **Extended Threat Models:** Adapting certification to non-$\ell_2$ attacks via alternative smoothing distributions
2. **Real-Time Certification:** Developing efficient approximations for online deployment
3. **Adaptive Attacks:** Investigating attacks specifically designed against certified detectors
4. **Multi-Watermark Systems:** Extending framework to scenarios with multiple watermarking schemes

### 4.5 Success Criteria

The research will be considered successful if:

1. **Technical Targets Met:** Achieve $r \geq 0.15$, accuracy $\geq 85\%$, certification success $\geq 90\%$
2. **Guarantees Validated:** Empirical attack success rate $\leq 5\%$ within certified radius
3. **Generalization Demonstrated:** Framework works across all four modalities with variance $\leq 20\%$
4. **Practical Feasibility:** Certification time $\leq 2$ minutes per sample
5. **Community Adoption:** Open-source release receives industry/academic uptake

**Falsification Criteria:**
The hypothesis will be rejected if:
- Certified radius $r < 0.05$ for strong watermarks with $\sigma = 0.5$
- Clean accuracy $< 80\%$ for any $\sigma \geq 0.1$
- Empirical attack success $> 10\%$ within certified radius
- Framework fails for any modality
- Certification time $> 10$ minutes per sample

### 4.6 Timeline and Deliverables

**Month 1-2:** Phase 1 (Toy Scale)
- Deliverable: Validated implementation on MNIST
- Milestone: Certification guarantee holds (P3 validated)

**Month 3-4:** Phase 2 (Medium Scale)
- Deliverable: Cross-modality results on CIFAR-10, SST-2, Common Voice
- Milestone: Adaptive variance optimization working

**Month 5-6:** Phase 3 (Realistic Scale)
- Deliverable: Full benchmark on ImageNet, GPT-2, AudioSet, YouTube-VIS
- Milestone: All targets achieved, SOTA comparison complete

**Month 7-8:** Analysis and Dissemination
- Deliverable: Research paper, open-source code, benchmark suite
- Milestone: Submission to top-tier venue (NeurIPS, ICLR, CVPR)

This research proposal presents a comprehensive plan to develop the first provably robust watermark detection framework for generative AI, addressing critical needs in AI safety, regulatory compliance, and content authentication through rigorous methodology and ambitious yet achievable targets.