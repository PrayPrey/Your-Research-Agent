# Research Proposal: Cross-Modal Adversarial Transferability: Exploiting Shared Representations in Large Multimodal Models

## 1. Introduction

### Background

Large Multimodal Models (LMMs) represent a transformative advancement in artificial intelligence, seamlessly integrating vision and language capabilities to enable sophisticated understanding and generation across modalities. Models such as GPT-4V, LLaVA, and MiniGPT-4 leverage shared representation spaces where visual and textual information are jointly encoded, enabling emergent cross-modal reasoning capabilities. These models are increasingly deployed in safety-critical applications, including autonomous vehicles, medical diagnosis, content moderation, and educational systems.

However, this architectural innovation—the shared embedding space connecting vision and language encoders—introduces a fundamentally new and underexplored attack surface. While adversarial attacks on single-modality systems (image classifiers and language models) are extensively studied, the cross-modal transfer of adversarial perturbations remains poorly understood. Recent surveys (Jiang et al., 2025) have highlighted critical vulnerabilities in multimodal alignment mechanisms, and emerging research (Rahmatullaev et al., 2025; Jiang et al., 2025) demonstrates that adversarial attacks can successfully exploit the intersection between modalities to bypass safety guardrails.

The cross-modal adversarial threat is particularly concerning because attackers may exploit the weakest modality to compromise the entire system. For instance, imperceptible perturbations to an image could manipulate a model into generating harmful text outputs, spreading misinformation, or revealing sensitive information. Understanding these vulnerabilities is essential for the safe deployment of LMMs in real-world applications.

### Research Objectives

This research aims to systematically investigate cross-modal adversarial transferability in Large Multimodal Models through three interconnected objectives:

1. **Theoretical Framework Development**: Establish a mathematical framework grounded in representation geometry to quantify how adversarial perturbations propagate across shared embedding spaces connecting vision and language encoders.

2. **Novel Attack Methodology**: Design and implement modality-bridging attacks that craft imperceptible image perturbations specifically optimized to induce targeted malicious text outputs.

3. **Defense Strategy Innovation**: Develop cross-modal adversarial training techniques that jointly harden both modalities by leveraging adversarial examples from each domain.

### Significance

This research addresses a critical gap at the intersection of adversarial machine learning and multimodal AI systems. By providing both theoretical understanding and practical attack/defense methodologies, this work will:

- Fundamentally advance understanding of multimodal robustness by characterizing the geometry of cross-modal adversarial transfer
- Enable proactive defense development by identifying architectural vulnerabilities in fusion mechanisms before they are exploited in the wild
- Establish standardized transferability metrics that can guide safer LMM design and deployment
- Inform policy and ethical guidelines for deploying multimodal AI in safety-critical domains

## 2. Methodology

### 2.1 Theoretical Framework: Representation Geometry of Cross-Modal Transfer

We develop a theoretical framework to characterize adversarial perturbation propagation across modalities. Let $\mathcal{V}$ denote the visual input space and $\mathcal{T}$ the textual output space, with the LMM implementing a mapping $f: \mathcal{V} \times \mathcal{T}_{prompt} \rightarrow \mathcal{T}_{output}$.

**Shared Representation Space Analysis**: We model the shared embedding space $\mathcal{Z} \subseteq \mathbb{R}^d$ where visual encoder $E_v: \mathcal{V} \rightarrow \mathcal{Z}$ and text encoder $E_t: \mathcal{T} \rightarrow \mathcal{Z}$ project their respective inputs. The cross-modal alignment objective typically minimizes:

$$\mathcal{L}_{align} = \mathbb{E}_{(v,t) \sim \mathcal{D}} \left[ \|E_v(v) - E_t(t)\|_2^2 \right]$$

**Cross-Modal Transferability Metric**: We define the Cross-Modal Adversarial Transferability (CMAT) score to quantify how perturbations in the visual domain affect textual outputs:

$$\text{CMAT}(\delta_v) = \frac{\|J_t \cdot J_v \cdot \delta_v\|_2}{\|\delta_v\|_2}$$

where $J_v = \frac{\partial E_v(v)}{\partial v}$ is the Jacobian of the visual encoder and $J_t = \frac{\partial f(z)}{\partial z}$ captures the sensitivity of the language decoder to embedding perturbations.

**Geometric Analysis of Vulnerability**: We analyze the singular value decomposition of the composed Jacobian $J = J_t \cdot J_v$ to identify principal directions of cross-modal vulnerability:

$$J = U \Sigma V^T$$

Directions corresponding to large singular values represent high-transferability subspaces where small visual perturbations cause large textual deviations.

### 2.2 Modality-Bridging Attack Design

We propose three novel attack strategies exploiting cross-modal vulnerabilities:

**Attack 1: Gradient-Based Cross-Modal Perturbation (GCMP)**

Given a target malicious output $t^*$, we optimize an imperceptible perturbation $\delta$ to the input image $v$:

$$\delta^* = \arg\min_{\|\delta\|_p \leq \epsilon} \mathcal{L}_{attack}(f(v + \delta, t_{prompt}), t^*)$$

where $\mathcal{L}_{attack}$ is the cross-entropy loss between the model's output and the target text. We employ Projected Gradient Descent (PGD) with the update rule:

$$\delta^{(k+1)} = \Pi_{\epsilon} \left( \delta^{(k)} + \alpha \cdot \text{sign}(\nabla_\delta \mathcal{L}_{attack}) \right)$$

where $\Pi_{\epsilon}$ projects onto the $\ell_p$-ball of radius $\epsilon$.

**Attack 2: Representation-Space Targeted Attack (RSTA)**

We directly manipulate the shared embedding space by finding perturbations that shift the visual embedding toward a target region associated with harmful outputs:

$$\delta^* = \arg\min_{\|\delta\|_p \leq \epsilon} \|E_v(v + \delta) - z_{target}\|_2^2 + \lambda \cdot \mathcal{R}(\delta)$$

where $z_{target}$ is computed by inverting typical embeddings of harmful text outputs, and $\mathcal{R}(\delta)$ is a regularizer promoting imperceptibility.

**Attack 3: Universal Cross-Modal Perturbation (UCMP)**

Inspired by Rahmatullaev et al. (2025), we develop universal perturbations effective across multiple input-output pairs:

$$\delta_{univ}^* = \arg\min_{\|\delta\|_p \leq \epsilon} \mathbb{E}_{(v, t_{prompt}) \sim \mathcal{D}} \left[ \mathcal{L}_{safety}(f(v + \delta, t_{prompt})) \right]$$

where $\mathcal{L}_{safety}$ measures violation of safety constraints across a distribution of queries.

### 2.3 Cross-Modal Adversarial Training Defense

We propose a novel defense strategy that jointly hardens both modalities through cross-modal adversarial training:

**Stage 1: Cross-Modal Adversarial Example Generation**

For each training sample $(v, t_{prompt}, t_{output})$, we generate adversarial examples in both modalities:

$$v_{adv} = v + \arg\max_{\|\delta\|_p \leq \epsilon_v} \mathcal{L}(f(v + \delta, t_{prompt}), t_{output})$$

$$t_{prompt}^{adv} = t_{prompt} + \arg\max_{\|\delta_t\| \leq \epsilon_t} \mathcal{L}(f(v, t_{prompt} + \delta_t), t_{output})$$

**Stage 2: Joint Adversarial Training Objective**

We optimize the model parameters $\theta$ using a composite objective:

$$\mathcal{L}_{defense}(\theta) = \mathbb{E}_{(v, t, y)} \Big[ \mathcal{L}_{clean}(f_\theta(v, t), y) + \lambda_v \mathcal{L}_{adv}(f_\theta(v_{adv}, t), y) + \lambda_t \mathcal{L}_{adv}(f_\theta(v, t^{adv}), y) + \lambda_{cross} \mathcal{L}_{adv}(f_\theta(v_{adv}, t^{adv}), y) \Big]$$

**Stage 3: Representation Regularization**

We add a geometric regularization term to reduce the magnitude of cross-modal vulnerability singular values:

$$\mathcal{L}_{reg}(\theta) = \|\Sigma(J_t \cdot J_v)\|_F$$

where $\|\cdot\|_F$ is the Frobenius norm, encouraging smoother cross-modal mappings.

### 2.4 Experimental Design

**Target Models**: We evaluate our methods on three open-source LMMs:
- LLaVA-1.5 (7B and 13B variants)
- MiniGPT-4
- InstructBLIP

**Datasets and Benchmarks**:
1. **Safety Evaluation**: MM-SafetyBench, VLGuard, and a custom cross-modal safety benchmark containing 1,000 image-text pairs spanning harmful content categories (violence, misinformation, hate speech, privacy violations)
2. **General Robustness**: VQAv2, GQA, and TextVQA for assessing clean performance retention
3. **Transferability Assessment**: Cross-model evaluation to measure attack transferability across different LMM architectures

**Evaluation Metrics**:

1. **Attack Success Rate (ASR)**: Percentage of adversarial examples that induce the target malicious behavior:
$$\text{ASR} = \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[\text{Harmful}(f(v_i + \delta_i, t_i))]$$

2. **Cross-Modal Transferability Score (CMTS)**: Our proposed metric measuring perturbation amplification across modalities

3. **Perturbation Imperceptibility**: LPIPS (Learned Perceptual Image Patch Similarity), SSIM, and $\ell_2$/$\ell_\infty$ norms

4. **Defense Effectiveness**:
   - Robust Accuracy: Performance on adversarial inputs
   - Clean Accuracy Retention: Performance degradation on benign inputs
   - Certified Robustness Bounds: Provable guarantees where applicable

5. **Efficiency Metrics**: Attack computation time, training overhead for defenses

**Experimental Protocol**:

1. **Baseline Establishment**: Evaluate undefended models against existing unimodal attacks (PGD, AutoAttack for images; TextFooler, BERT-Attack for text)

2. **Cross-Modal Attack Evaluation**: Apply our proposed GCMP, RSTA, and UCMP attacks with perturbation budgets $\epsilon \in \{4/255, 8/255, 16/255\}$ under $\ell_\infty$ norm

3. **Defense Evaluation**: Train defended models using our cross-modal adversarial training and compare against:
   - Standard adversarial training (single-modality)
   - Input preprocessing defenses (JPEG compression, feature squeezing)
   - Certified defense methods adapted from CR-UTP

4. **Ablation Studies**: Analyze the contribution of each component (representation regularization, cross-modal perturbations) to defense effectiveness

5. **Transferability Analysis**: Evaluate attacks crafted on one model against other models to assess black-box attack feasibility

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Theoretical Contributions**:
1. A rigorous mathematical framework characterizing cross-modal adversarial transferability through representation geometry
2. Identification of principal vulnerability directions in shared embedding spaces that predict attack success
3. Theoretical bounds relating architectural choices (fusion mechanisms, embedding dimensionality) to cross-modal robustness

**Methodological Contributions**:
1. Three novel attack algorithms (GCMP, RSTA, UCMP) demonstrating the feasibility of cross-modal adversarial exploitation
2. A comprehensive cross-modal adversarial training framework with geometric regularization
3. The CMAT metric for standardized assessment of cross-modal vulnerabilities

**Empirical Findings**:
1. Comprehensive vulnerability assessment across major open-source LMMs
2. Quantification of attack success rates, transferability patterns, and defense effectiveness
3. Identification of architectural components most susceptible to cross-modal attacks

### Anticipated Impact

**Scientific Impact**: This research will establish foundational understanding of adversarial robustness in the multimodal setting, opening new research directions at the intersection of representation learning, adversarial ML, and multimodal AI. The theoretical framework will enable principled analysis of future multimodal architectures.

**Practical Impact**: The attack methodologies will serve as red-teaming tools for LMM developers to proactively identify vulnerabilities. The defense strategies can be integrated into training pipelines to enhance robustness before deployment. The CMAT metric will provide a standardized benchmark for comparing multimodal model security.

**Societal Impact**: By advancing understanding of LMM vulnerabilities, this research will contribute to safer deployment of multimodal AI in healthcare, education, and content moderation. The findings will inform policy discussions on AI safety regulations and responsible AI development practices.

**Industry Applications**: The defense methodologies can be adopted by companies developing commercial LMMs (e.g., OpenAI, Google, Anthropic) to strengthen their models against adversarial exploitation. The evaluation framework provides actionable security benchmarks for pre-deployment testing.

### Timeline and Deliverables

- **Months 1-3**: Theoretical framework development and preliminary vulnerability analysis
- **Months 4-6**: Attack algorithm implementation and initial evaluation
- **Months 7-9**: Defense strategy development and comprehensive experiments
- **Months 10-12**: Analysis, paper writing, and open-source tool release

We will release our attack and defense implementations as an open-source toolkit, along with our custom evaluation benchmark, to facilitate reproducible research and adoption by the broader community. This work will be submitted to top venues including NeurIPS, ICML, and USENIX Security, contributing to both the machine learning and security research communities.