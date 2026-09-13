# Research Proposal: Cross-Modal Adversarial Transferability Detection via Representation Alignment Monitoring

## 1. Introduction

### Background

Multi-modal Foundation Models (MFMs) have emerged as transformative technologies that integrate information across diverse modalities—text, images, audio, and video—to perform complex reasoning and generation tasks. Models such as LLaVA, QwenVL, and GPT-4V represent the state-of-the-art in multi-modal large language models (MLLMs), while systems like Stable Diffusion and Sora exemplify advances in multi-modal generative models (MMGMs). These architectures typically employ shared embedding spaces where representations from different modalities are aligned and fused, enabling seamless cross-modal understanding and reasoning.

However, this architectural paradigm introduces a critical yet underexplored vulnerability: adversarial perturbations crafted in one modality can propagate through shared representation spaces and corrupt reasoning in other modalities. Unlike traditional single-modality adversarial attacks, these cross-modal adversarial transfers exploit the fundamental alignment mechanisms that make MFMs powerful. For instance, an imperceptible perturbation in an image input can cascade through fusion layers and induce erroneous, potentially harmful text outputs, bypassing safety guardrails designed for individual modalities.

Recent research has begun addressing multi-modal adversarial vulnerabilities. Wang et al. (2024) introduced MMCert, the first certified defense against adversarial attacks on multi-modal models, providing theoretical guarantees but with computational overhead unsuitable for real-time deployment. Shayegani et al. (2023) demonstrated compositional attacks that pair adversarial images with textual prompts to jailbreak vision-language models, achieving alarming success rates. Akbarian et al. (2025) proposed consensus-based generative mitigation but focused primarily on reconstruction rather than detection. These works highlight the urgency of developing efficient detection mechanisms that can identify cross-modal adversarial transfers before they compromise model outputs.

### Research Objectives

This research proposes **CrossGuard**, a real-time monitoring framework designed to detect cross-modal adversarial transferability by analyzing representation alignment dynamics during inference. Our specific objectives are:

1. To develop lightweight alignment probe networks that can be inserted at fusion layers of existing MFMs to monitor consistency between modality-specific and fused representations.

2. To establish robust detection baselines through contrastive learning on clean multi-modal pairs, enabling accurate identification of anomalous divergence patterns.

3. To design a cascading alert system that triggers enhanced scrutiny when adversarial signatures are detected in any modality.

4. To validate CrossGuard across multiple MFM architectures and attack types, demonstrating practical applicability without model retraining.

### Significance

This research addresses a fundamental gap in MFM safety: the absence of systematic defenses against cross-modal adversarial leakage. CrossGuard's significance lies in its (1) proactive detection capability that identifies attacks before they corrupt downstream reasoning, (2) model-agnostic design applicable to diverse MFM architectures, (3) computational efficiency suitable for real-time deployment, and (4) contribution to comprehensive safety mechanisms aligned with emerging AI governance frameworks. By providing the first systematic defense against cross-modal adversarial transfers, this work advances the trustworthy deployment of MFMs in high-stakes applications.

## 2. Methodology

### 2.1 Overview

CrossGuard operates as a monitoring layer integrated into MFM inference pipelines. The framework comprises three core components: Alignment Probes for measuring representation consistency, Contrastive Baseline Learning for establishing normal behavior distributions, and a Cascading Alert System for coordinated threat response. Figure 1 illustrates the overall architecture.

### 2.2 Alignment Probe Networks

#### Architecture Design

We design lightweight probe networks $\mathcal{P}_i$ for each modality-fusion interface in the target MFM. For a model with $K$ modalities and $L$ fusion layers, we deploy probes at each fusion point $(k, l)$ where modality $k$ interfaces with layer $l$.

Each probe $\mathcal{P}_{k,l}$ consists of a small multi-layer perceptron that takes as input the modality-specific representation $\mathbf{h}_k^{(l)}$ and the fused representation $\mathbf{f}^{(l)}$, computing an alignment score:

$$\mathcal{A}_{k,l} = \sigma\left(\mathbf{W}_2 \cdot \text{ReLU}\left(\mathbf{W}_1 \cdot [\mathbf{h}_k^{(l)} \| \mathbf{f}^{(l)} \| \mathbf{h}_k^{(l)} \odot \mathbf{f}^{(l)}] + \mathbf{b}_1\right) + \mathbf{b}_2\right)$$

where $\|$ denotes concatenation, $\odot$ represents element-wise multiplication, $\sigma$ is the sigmoid function, and $\mathbf{W}_1, \mathbf{W}_2, \mathbf{b}_1, \mathbf{b}_2$ are learnable parameters.

#### Divergence Pattern Detection

To capture anomalous alignment patterns, we compute multiple divergence metrics at each probe location:

1. **Cosine Divergence**: 
$$D_{\cos}^{(k,l)} = 1 - \frac{\mathbf{h}_k^{(l)} \cdot \mathbf{f}^{(l)}}{\|\mathbf{h}_k^{(l)}\| \|\mathbf{f}^{(l)}\|}$$

2. **KL Divergence of Attention Patterns**: For transformer-based fusion, we monitor attention weight distributions:
$$D_{KL}^{(k,l)} = \sum_{i} p_{\text{clean}}(a_i^{(k,l)}) \log \frac{p_{\text{clean}}(a_i^{(k,l)})}{p_{\text{observed}}(a_i^{(k,l)})}$$

3. **Representation Norm Ratio**:
$$D_{\text{norm}}^{(k,l)} = \left|\frac{\|\mathbf{h}_k^{(l)}\|}{\|\mathbf{f}^{(l)}\|} - \mu_{\text{norm}}^{(k,l)}\right|$$

where $\mu_{\text{norm}}^{(k,l)}$ is the expected ratio learned from clean data.

### 2.3 Contrastive Baseline Learning

#### Training Objective

We learn normal alignment distributions using a contrastive learning framework. Given a dataset of clean multi-modal pairs $\mathcal{D} = \{(\mathbf{x}_1^{(i)}, \mathbf{x}_2^{(i)}, ..., \mathbf{x}_K^{(i)})\}_{i=1}^N$, we train the alignment probes to distinguish between semantically consistent (positive) and inconsistent (negative) representation pairs.

The contrastive loss for each probe is defined as:

$$\mathcal{L}_{\text{contrast}}^{(k,l)} = -\log \frac{\exp(\text{sim}(\mathbf{h}_k^{(l)}, \mathbf{f}^{(l)})/\tau)}{\exp(\text{sim}(\mathbf{h}_k^{(l)}, \mathbf{f}^{(l)})/\tau) + \sum_{j \in \mathcal{N}} \exp(\text{sim}(\mathbf{h}_k^{(l)}, \mathbf{f}_j^{(l)})/\tau)}$$

where $\text{sim}(\cdot, \cdot)$ is cosine similarity, $\tau$ is a temperature parameter, and $\mathcal{N}$ represents negative samples from mismatched pairs.

#### Threshold Calibration

For each divergence metric, we establish detection thresholds using the learned distributions. Given the empirical distribution of divergence scores $\{D^{(k,l)}_m\}$ on clean validation data, we set thresholds at the $(1-\alpha)$ quantile for a desired false positive rate $\alpha$:

$$\theta_m^{(k,l)} = Q_{1-\alpha}\left(\{D^{(k,l)}_m\}_{\text{clean}}\right)$$

We also learn adaptive thresholds using a small validation set containing both clean and adversarial examples, optimizing for the F1-score.

### 2.4 Cascading Alert System

#### Detection Logic

The cascading alert system implements a hierarchical detection mechanism. Let $\mathbf{D}^{(k,l)} = [D_{\cos}^{(k,l)}, D_{KL}^{(k,l)}, D_{\text{norm}}^{(k,l)}]$ be the vector of divergence metrics at probe $(k,l)$.

**Level 1 (Modality-Specific Alert)**: An alert is triggered for modality $k$ if:
$$\exists l, m: D_m^{(k,l)} > \theta_m^{(k,l)}$$

**Level 2 (Cross-Modal Scrutiny)**: When Level 1 is triggered for modality $k$, we activate enhanced monitoring on all downstream fusion paths:
$$\mathcal{S}_k = \{(k', l'): l' > l, \text{fusion}(k, k') \text{ exists at } l'\}$$

For each $(k', l') \in \mathcal{S}_k$, we apply stricter thresholds $\theta'^{(k',l')}_m = \gamma \cdot \theta_m^{(k',l')}$ where $\gamma < 1$.

**Level 3 (Global Alert)**: A system-wide alert is issued if:
$$\sum_{k,l} \mathbb{1}\left[\exists m: D_m^{(k,l)} > \theta_m^{(k,l)}\right] > T_{\text{global}}$$

#### Response Actions

Upon detection, CrossGuard can trigger configurable responses: logging for analysis, output suppression, input sanitization requests, or human-in-the-loop verification for high-stakes applications.

### 2.5 Experimental Design

#### Datasets

1. **Multi-Modal Alignment Dataset (MMAD)**: We curate a dataset combining MS-COCO, Visual Genome, and AudioCaps with verified cross-modal alignments for training alignment probes.

2. **Adversarial Evaluation Set**: We generate adversarial examples using:
   - PGD attacks on image modality with varying $\epsilon \in \{2/255, 4/255, 8/255\}$
   - Textual adversarial attacks using the RL-based method from Zang et al. (2024)
   - Compositional attacks following Shayegani et al. (2023)
   - Novel cross-modal transfer attacks targeting fusion layers

#### Target Models

We evaluate CrossGuard on:
- **LLaVA-1.5** (7B and 13B variants)
- **QwenVL** 
- **InstructBLIP**
- **CLIP** (as a baseline encoder)

#### Evaluation Metrics

1. **Detection Performance**:
   - True Positive Rate (TPR) at fixed False Positive Rates (FPR = 1%, 5%)
   - Area Under ROC Curve (AUROC)
   - Detection latency (milliseconds per sample)

2. **Cross-Modal Transfer Detection**:
   - Transfer Detection Rate (TDR): percentage of attacks where cross-modal propagation is detected
   - Early Detection Rate: detection before corruption affects output

3. **Computational Overhead**:
   - Additional inference time
   - Memory footprint
   - Parameters added (relative to base model)

#### Baseline Comparisons

- MMCert (Wang et al., 2024): certified defense approach
- CAMME-style detection (Khan et al., 2025): multi-modal cross-attention detection
- Input reconstruction defense (Akbarian et al., 2025)
- Standard single-modality adversarial detection methods

#### Ablation Studies

1. Probe placement analysis: evaluating detection accuracy vs. number and location of probes
2. Divergence metric importance: contribution of each metric type
3. Threshold calibration strategies: fixed vs. adaptive thresholds
4. Cascading mechanism effectiveness: with and without hierarchical alerting

## 3. Expected Outcomes & Impact

### Expected Results

Based on our preliminary analysis and related work performance, we anticipate CrossGuard will achieve:

1. **Detection Accuracy**: >85% true positive rate in identifying cross-modal adversarial transfers with <5% false positive rate, meeting practical deployment requirements.

2. **Early Detection**: Ability to flag adversarial inputs before 70% of cross-modal corruption occurs, enabling preemptive response.

3. **Efficiency**: <10ms additional latency per inference and <2% parameter overhead relative to base MFMs.

4. **Generalization**: Consistent performance across different MFM architectures without architecture-specific tuning.

5. **Attack Coverage**: Effective detection of both existing attack methods and novel cross-modal transfer attacks.

### Scientific Contributions

This research will deliver:

1. **Theoretical Framework**: Formalization of cross-modal adversarial transferability as a measurable phenomenon through representation alignment dynamics.

2. **Open-Source Toolkit**: Publicly available implementation of CrossGuard compatible with popular MFM frameworks (HuggingFace Transformers, PyTorch).

3. **Benchmark Dataset**: First dedicated benchmark for cross-modal adversarial transfer detection with standardized evaluation protocols.

4. **Design Guidelines**: Recommendations for incorporating alignment monitoring into MFM development pipelines.

### Broader Impact

CrossGuard addresses critical safety challenges as MFMs become deployed in high-stakes applications including healthcare diagnostics, autonomous systems, and content moderation. By providing real-time detection capabilities without requiring model retraining, our approach offers a practical path toward trustworthy MFM deployment. The framework aligns with emerging AI governance principles emphasizing proactive risk assessment and comprehensive safety mechanisms throughout the AI lifecycle.

Furthermore, CrossGuard's monitoring approach contributes to transparency and interpretability goals by exposing internal alignment dynamics, enabling auditors and researchers to understand how adversarial signals propagate through multi-modal systems. This visibility supports both technical safety evaluation and regulatory compliance efforts.

### Limitations and Future Work

We acknowledge that CrossGuard focuses on detection rather than mitigation, requiring integration with response mechanisms. Future work will explore automated mitigation strategies, extension to additional modalities (audio, video), and adaptation to agentic systems with tool use capabilities. We will also investigate adaptive attacks specifically designed to evade alignment monitoring, ensuring robust evaluation of our approach.