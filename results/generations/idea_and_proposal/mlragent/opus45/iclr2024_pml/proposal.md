# Research Proposal: Adaptive Privacy Budget Allocation for Differentially Private Fine-tuning of Large Language Models

## 1. Introduction

### Background

The rapid proliferation of large language models (LLMs) has revolutionized natural language processing, enabling unprecedented capabilities in text generation, reasoning, and task completion. However, deploying these models in real-world applications often necessitates fine-tuning on domain-specific or user data, which frequently contains sensitive personal information. Privacy regulations such as the General Data Protection Regulation (GDPR) and the Digital Markets Act (DMA) impose strict requirements on how organizations handle personal data, creating a fundamental tension between model utility and regulatory compliance.

Differential privacy (DP) has emerged as the gold standard for providing mathematically rigorous privacy guarantees in machine learning. The DP-SGD algorithm, which clips gradients and adds calibrated noise during training, enables models to learn from sensitive data while bounding the information leakage about any individual data point. However, applying DP-SGD to LLM fine-tuning presents significant challenges. Current implementations treat all model parameters uniformly, injecting identical noise levels across all layers regardless of their varying contributions to privacy risk and model performance. This one-size-fits-all approach leads to substantial utility degradation—often 20-40% performance drops on downstream tasks—rendering privacy-preserving LLM deployment impractical for many applications.

Recent research has begun addressing this challenge through parameter-efficient fine-tuning methods and subspace-based approaches. Huang et al. (2025) demonstrated that freezing backbone parameters and updating through low-dimensional projection subspaces can reduce privacy budget consumption. Similarly, Zheng et al. (2026) proposed DP-SFT, which injects noise only into task-specific subspaces identified through principal gradient directions. While these methods show promise, they rely on static privacy allocation strategies that do not adapt to the varying privacy risks across different layers and training phases.

### Research Objectives

This research proposes a dynamic privacy budget allocation framework (DPA-DP) that intelligently distributes the privacy budget across model layers and training iterations. Our specific objectives are:

1. To develop a lightweight privacy risk estimator that quantifies per-layer memorization potential using gradient norms, attention patterns, and information-theoretic measures.

2. To design an adaptive noise calibration mechanism that allocates privacy budget proportionally to layer-specific privacy risks while maintaining rigorous overall privacy guarantees through advanced composition theorems.

3. To implement a temporal budget scheduling algorithm that optimally distributes privacy budget across training iterations based on gradient informativeness.

4. To validate the framework through comprehensive experiments on instruction-tuning benchmarks, demonstrating improved utility-privacy trade-offs.

### Significance

This research addresses a critical gap in privacy-preserving machine learning by enabling organizations to fine-tune LLMs on sensitive data while maintaining GDPR compliance and acceptable model quality. The proposed framework has direct implications for healthcare, finance, and legal domains where privacy regulations are stringent but domain-specific fine-tuning is essential for practical deployment.

## 2. Methodology

### 2.1 Problem Formulation

Consider a pre-trained LLM with $L$ layers, parameterized by $\theta = \{\theta_1, \theta_2, ..., \theta_L\}$. Given a sensitive fine-tuning dataset $\mathcal{D} = \{(x_i, y_i)\}_{i=1}^{n}$, our goal is to minimize the empirical loss while satisfying $(\epsilon, \delta)$-differential privacy:

$$\min_{\theta} \mathcal{L}(\theta; \mathcal{D}) = \frac{1}{n}\sum_{i=1}^{n}\ell(f_\theta(x_i), y_i)$$

subject to the constraint that the training mechanism $\mathcal{M}$ satisfies $(\epsilon, \delta)$-DP, meaning for any two adjacent datasets $\mathcal{D}$ and $\mathcal{D}'$ differing in one sample:

$$\Pr[\mathcal{M}(\mathcal{D}) \in S] \leq e^\epsilon \Pr[\mathcal{M}(\mathcal{D}') \in S] + \delta$$

### 2.2 Per-Layer Privacy Risk Estimation

We introduce a privacy risk score $\rho_l$ for each layer $l$ that captures its memorization potential. This score combines three components:

**Gradient Norm Analysis:** Layers with larger gradient norms during training are more susceptible to membership inference attacks. We compute the normalized gradient norm:

$$g_l^{(t)} = \frac{\|\nabla_{\theta_l}\mathcal{L}\|_2}{\sum_{l'=1}^{L}\|\nabla_{\theta_{l'}}\mathcal{L}\|_2}$$

**Attention Pattern Entropy:** For transformer layers, we measure the entropy of attention distributions, as concentrated attention patterns indicate potential memorization of specific training examples:

$$H_l^{(t)} = -\sum_{h=1}^{H}\sum_{i,j}A_{h,i,j}^{(l)}\log A_{h,i,j}^{(l)}$$

where $A_{h,i,j}^{(l)}$ represents the attention weight from position $i$ to $j$ in head $h$ of layer $l$.

**Fisher Information Approximation:** We estimate the Fisher information to quantify how much each layer contributes to distinguishing between adjacent datasets:

$$\mathcal{I}_l^{(t)} = \mathbb{E}\left[\left(\nabla_{\theta_l}\log p(y|x;\theta)\right)^2\right]$$

The composite privacy risk score is computed as:

$$\rho_l^{(t)} = \alpha \cdot g_l^{(t)} + \beta \cdot (1 - \hat{H}_l^{(t)}) + \gamma \cdot \hat{\mathcal{I}}_l^{(t)}$$

where $\hat{H}_l^{(t)}$ and $\hat{\mathcal{I}}_l^{(t)}$ are normalized values, and $\alpha + \beta + \gamma = 1$ are hyperparameters.

### 2.3 Adaptive Noise Calibration Mechanism

Given the privacy risk scores, we allocate the per-step privacy budget $\epsilon^{(t)}$ across layers. Let $\epsilon_l^{(t)}$ denote the privacy budget for layer $l$ at iteration $t$. We require:

$$\sum_{l=1}^{L}\epsilon_l^{(t)} = \epsilon^{(t)}$$

We allocate budget inversely proportional to privacy risk:

$$\epsilon_l^{(t)} = \epsilon^{(t)} \cdot \frac{(1/\rho_l^{(t)})}{\sum_{l'=1}^{L}(1/\rho_{l'}^{(t)})}$$

The noise standard deviation for layer $l$ is then calibrated as:

$$\sigma_l^{(t)} = \frac{C_l \cdot \sqrt{2\log(1.25/\delta)}}{\epsilon_l^{(t)}}$$

where $C_l$ is the gradient clipping bound for layer $l$, set proportionally to the layer's typical gradient magnitude.

**Privacy Guarantee via Composition:** We leverage the Rényi Differential Privacy (RDP) framework for tight composition. For each layer, the per-step RDP guarantee at order $\alpha$ is:

$$\epsilon_l^{(\alpha)} = \frac{\alpha C_l^2}{2(\sigma_l^{(t)})^2}$$

The total privacy loss after $T$ iterations is computed through RDP composition and converted to $(\epsilon, \delta)$-DP:

$$\epsilon_{total} = \min_{\alpha > 1}\left(\sum_{t=1}^{T}\max_l \epsilon_l^{(\alpha)} + \frac{\log(1/\delta)}{\alpha - 1}\right)$$

### 2.4 Temporal Budget Scheduling

We implement a non-uniform temporal allocation strategy based on the observation that early training iterations capture more generalizable patterns while later iterations tend toward memorization. We model the per-iteration budget as:

$$\epsilon^{(t)} = \epsilon_{base} \cdot \left(1 + \lambda \cdot e^{-t/\tau}\right)$$

where $\epsilon_{base}$ ensures minimum privacy per step, $\lambda$ controls the initial budget boost, and $\tau$ is a decay constant. The total budget constraint is:

$$\sum_{t=1}^{T}\epsilon^{(t)} \leq \epsilon_{total}$$

We solve for $\epsilon_{base}$ to satisfy this constraint while maximizing early-stage learning.

### 2.5 Algorithm Summary

The complete DPA-DP algorithm proceeds as follows:

**Algorithm: DPA-DP Fine-tuning**

**Input:** Pre-trained model $\theta$, dataset $\mathcal{D}$, privacy parameters $(\epsilon, \delta)$, iterations $T$

**Output:** Fine-tuned model $\theta^*$

1. Initialize temporal budget schedule $\{\epsilon^{(t)}\}_{t=1}^{T}$
2. **For** $t = 1$ to $T$ **do:**
   - Sample minibatch $B_t$ from $\mathcal{D}$
   - Compute per-sample gradients $\{g_i\}_{i \in B_t}$
   - **For** each layer $l$ **do:**
     - Compute privacy risk score $\rho_l^{(t)}$
   - Allocate layer budgets $\{\epsilon_l^{(t)}\}_{l=1}^{L}$
   - **For** each layer $l$ **do:**
     - Clip gradients: $\bar{g}_{i,l} = g_{i,l} \cdot \min(1, C_l/\|g_{i,l}\|_2)$
     - Compute noisy gradient: $\tilde{g}_l = \frac{1}{|B_t|}\sum_{i}\bar{g}_{i,l} + \mathcal{N}(0, \sigma_l^{(t)2}I)$
   - Update: $\theta \leftarrow \theta - \eta \tilde{g}$
3. **Return** $\theta^* = \theta$

### 2.6 Experimental Design

**Datasets and Tasks:** We evaluate on three instruction-tuning benchmarks:
- **Alpaca-52k:** General instruction following
- **Medical-QA:** Healthcare domain (privacy-sensitive)
- **Financial-PhraseBank:** Financial sentiment analysis

**Models:** We experiment with LLaMA-7B, LLaMA-13B, and Mistral-7B to assess scalability.

**Baselines:**
1. Vanilla DP-SGD with uniform noise
2. DP-LoRA (parameter-efficient DP fine-tuning)
3. DP-SFT (subspace-based approach)
4. Ghost Clipping (efficient DP-SGD variant)

**Privacy Budgets:** We evaluate at $\epsilon \in \{1, 3, 8\}$ with $\delta = 1/n$.

**Evaluation Metrics:**
- **Utility:** ROUGE-L, BLEU scores, task-specific accuracy
- **Privacy:** Membership inference attack success rate, extraction attack resistance
- **Efficiency:** Wall-clock training time, GPU memory usage

**Ablation Studies:**
1. Contribution of each privacy risk component ($\alpha$, $\beta$, $\gamma$)
2. Impact of temporal scheduling parameters ($\lambda$, $\tau$)
3. Sensitivity to hyperparameter choices

## 3. Expected Outcomes & Impact

### Expected Outcomes

We anticipate the following outcomes from this research:

1. **Improved Utility-Privacy Trade-off:** We expect 15-25% improvement in downstream task performance (measured by ROUGE-L and task accuracy) compared to vanilla DP-SGD under equivalent privacy budgets ($\epsilon = 3$). This improvement stems from directing more privacy budget to layers with lower memorization risk.

2. **Maintained Privacy Guarantees:** The framework will provide mathematically rigorous $(\epsilon, \delta)$-DP guarantees through proper RDP composition, validated by reduced membership inference attack success rates (targeting <55% accuracy, near random guessing).

3. **Computational Efficiency:** Despite the adaptive allocation overhead, we expect training time to remain within 1.2× of standard DP-SGD due to the lightweight nature of the privacy risk estimator, which requires only gradient statistics already computed during backpropagation.

4. **Generalizable Framework:** The methodology will generalize across model architectures (decoder-only, encoder-decoder) and fine-tuning paradigms (full fine-tuning, LoRA, prompt tuning).

### Impact

**Scientific Impact:** This research advances the theoretical understanding of privacy-utility trade-offs in deep learning by demonstrating that non-uniform privacy allocation across model components can significantly improve efficiency without compromising formal guarantees. The privacy risk estimation framework provides a principled approach to quantifying layer-wise memorization potential.

**Practical Impact:** The framework enables organizations to deploy privacy-preserving LLMs in regulated industries. Healthcare providers can fine-tune models on patient data while maintaining HIPAA compliance; financial institutions can adapt models to proprietary data while meeting regulatory requirements. This bridges the current gap between theoretical privacy guarantees and practical deployment needs.

**Regulatory Alignment:** By providing quantifiable privacy guarantees compatible with GDPR's data minimization principles, this work supports the responsible adoption of AI systems in privacy-sensitive contexts, contributing to the broader goal of trustworthy AI development.

**Open Science:** We will release our implementation as an open-source library compatible with popular frameworks (Hugging Face Transformers, PyTorch), enabling researchers and practitioners to adopt privacy-preserving fine-tuning with minimal overhead.