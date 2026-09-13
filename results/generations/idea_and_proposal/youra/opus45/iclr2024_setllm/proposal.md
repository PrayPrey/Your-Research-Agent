# Research Proposal: ARID: Adversarial Representation-level Immune Defense for Multi-Vector LLM Attacks via Contrastive Trajectory Detection

## 1. Introduction

### 1.1 Background

Large language models (LLMs) have fundamentally transformed natural language processing, achieving remarkable performance across diverse tasks including machine translation, question-answering, dialogue systems, and code generation. Models such as GPT-4, Llama-3, and Claude have demonstrated unprecedented capabilities in understanding and generating human-like text. However, this transformative power comes with profound security vulnerabilities that threaten the trustworthy deployment of LLMs in real-world applications.

The security landscape of LLMs has evolved from simple adversarial perturbations to sophisticated multi-vector attacks that combine multiple attack strategies simultaneously. Contemporary threats include prompt injection attacks that manipulate model behavior through crafted inputs, jailbreaking techniques that bypass safety guardrails, context manipulation that exploits retrieval-augmented generation (RAG) systems, and cognitive overload attacks that overwhelm model reasoning capabilities. Recent work on JudgeDeceiver (Shi et al., 2024) demonstrates that optimization-based attacks can systematically defeat threshold-based detection mechanisms, highlighting the inadequacy of current defense paradigms.

Existing defense mechanisms predominantly rely on surface-level pattern matching, perplexity-based detection, or single-attack-type classifiers. These approaches suffer from three critical limitations: (1) they fail to generalize across attack vectors, requiring separate defenses for each attack type; (2) they are vulnerable to adaptive adversaries who can optimize attacks to evade fixed detection thresholds; and (3) they impose substantial computational overhead when deployed comprehensively. The fundamental gap in current research is the absence of a unified defense mechanism that captures the shared adversarial intent underlying diverse attack vectors at the representation level.

### 1.2 Research Objectives

This research proposes ARID (Adversarial Representation-level Immune Defense), a novel defense framework based on the hypothesis that multi-vector attacks share detectable trajectory shifts in LLM hidden state representations toward adversarial objectives. The primary objectives are:

1. **Develop a contrastive adversarial-intent projection mechanism** that maps diverse attack representations into a shared adversarial-intent subspace, enabling unified detection across attack vectors.

2. **Design trajectory-based detection** that monitors the direction of representation shifts rather than absolute values, providing robustness against optimization-based evasion attacks.

3. **Implement selective layer monitoring** at strategic transformer layers (1, L/2, L) to achieve comprehensive coverage with minimal computational overhead (<5% inference latency increase).

4. **Validate ARID's effectiveness** against multi-vector attacks using established benchmarks (AdvBench, JailbreakBench) and demonstrate significant improvement over existing defenses (>20 percentage points in TPR@FPR=0.1%).

### 1.3 Significance

This research addresses a critical gap in LLM security by providing the first unified defense framework against coordinated multi-vector attacks. The immune-inspired approach offers a principled theoretical foundation for understanding and defending against adversarial behavior in neural language models. Success in this research would: (1) establish representation-level trajectory analysis as a new paradigm for LLM defense; (2) provide practical defense mechanisms deployable in production systems; and (3) advance understanding of how adversarial intent manifests in transformer hidden states, contributing to broader interpretability research.

## 2. Methodology

### 2.1 Theoretical Framework

ARID is grounded in the hypothesis that all effective attacks against LLMs must induce specific patterns of representation change to achieve their adversarial objectives. We formalize this through the concept of **adversarial trajectory**: the directional shift in hidden state representations from benign processing toward adversarial outcomes.

**Definition 1 (Adversarial Trajectory):** For an input sequence $x$ processed by an LLM with $L$ transformer layers, let $h_l(x) \in \mathbb{R}^d$ denote the hidden state representation at layer $l$. The trajectory $\tau(x)$ is defined as:

$$\tau(x) = \{h_1(x), h_{L/2}(x), h_L(x)\}$$

**Definition 2 (Adversarial-Intent Subspace):** We hypothesize the existence of a low-dimensional subspace $\mathcal{A} \subset \mathbb{R}^d$ such that adversarial inputs induce trajectory shifts toward $\mathcal{A}$, regardless of the specific attack vector employed.

### 2.2 ARID Architecture

The ARID framework consists of four interconnected components:

#### 2.2.1 Representation Extraction Module

For each input $x$, we extract hidden state representations at three strategic layers: the first layer (capturing input-level features), the middle layer $L/2$ (capturing intermediate reasoning), and the final layer $L$ (capturing output-oriented representations). This selective extraction balances coverage with computational efficiency.

$$\mathbf{H}(x) = [h_1(x); h_{L/2}(x); h_L(x)] \in \mathbb{R}^{3d}$$

#### 2.2.2 Contrastive Adversarial-Intent Projection

We train a projection network $f_\theta: \mathbb{R}^{3d} \rightarrow \mathbb{R}^k$ (where $k \ll d$) using contrastive learning to map representations into the adversarial-intent subspace. The training objective combines supervised contrastive loss with trajectory consistency regularization:

$$\mathcal{L}_{total} = \mathcal{L}_{contrast} + \lambda \mathcal{L}_{trajectory}$$

The supervised contrastive loss encourages representations of attacks to cluster together while separating from benign inputs:

$$\mathcal{L}_{contrast} = -\sum_{i \in \mathcal{B}} \frac{1}{|P(i)|} \sum_{p \in P(i)} \log \frac{\exp(f_\theta(\mathbf{H}_i) \cdot f_\theta(\mathbf{H}_p) / \tau)}{\sum_{j \neq i} \exp(f_\theta(\mathbf{H}_i) \cdot f_\theta(\mathbf{H}_j) / \tau)}$$

where $\mathcal{B}$ is the batch, $P(i)$ is the set of positive pairs (same class as $i$), and $\tau$ is the temperature parameter.

The trajectory consistency loss ensures that the projection captures directional information:

$$\mathcal{L}_{trajectory} = \sum_{i \in \mathcal{A}_{attack}} \left\| \frac{\Delta f_\theta(\mathbf{H}_i)}{\|\Delta f_\theta(\mathbf{H}_i)\|} - \mathbf{v}_{adv} \right\|^2$$

where $\Delta f_\theta(\mathbf{H}_i) = f_\theta(h_L(x_i)) - f_\theta(h_1(x_i))$ represents the trajectory direction and $\mathbf{v}_{adv}$ is a learnable adversarial direction vector.

#### 2.2.3 Trajectory-Based Detection

Unlike threshold-based detection that monitors absolute representation values, ARID detects the **direction** of representation shifts. We compute the trajectory alignment score:

$$s_{traj}(x) = \cos\left(\Delta f_\theta(\mathbf{H}(x)), \mathbf{v}_{adv}\right) = \frac{\Delta f_\theta(\mathbf{H}(x)) \cdot \mathbf{v}_{adv}}{\|\Delta f_\theta(\mathbf{H}(x))\| \|\mathbf{v}_{adv}\|}$$

This directional approach is fundamentally more robust against optimization-based evasion because adversaries cannot simultaneously: (1) maintain attack effectiveness (requiring trajectory toward adversarial objectives) and (2) evade detection (requiring trajectory away from adversarial direction).

#### 2.2.4 Lightweight Probe Classifiers

At each monitored layer $l \in \{1, L/2, L\}$, we deploy a lightweight probe classifier $g_l: \mathbb{R}^d \rightarrow [0,1]$ implemented as a two-layer MLP:

$$g_l(h_l(x)) = \sigma(W_2 \cdot \text{ReLU}(W_1 \cdot h_l(x) + b_1) + b_2)$$

The final detection decision combines trajectory alignment with probe outputs:

$$p_{attack}(x) = \alpha \cdot s_{traj}(x) + (1-\alpha) \cdot \frac{1}{3}\sum_{l \in \{1, L/2, L\}} g_l(h_l(x))$$

where $\alpha$ is a learned combination weight. An input is flagged as adversarial if $p_{attack}(x) > \theta$, with $\theta$ calibrated to achieve the target false positive rate.

### 2.3 Training Procedure

**Algorithm 1: ARID Training**

```
Input: LLM M, benign dataset D_b, attack dataset D_a (multi-vector)
Output: Trained projection network f_θ, probe classifiers {g_l}, adversarial direction v_adv

1. Initialize f_θ, {g_l}, v_adv randomly
2. For each epoch e = 1 to E:
   a. Sample batch B from D_b ∪ D_a
   b. For each x in B:
      i.   Forward pass through M, extract H(x) = [h_1(x); h_{L/2}(x); h_L(x)]
      ii.  Compute projected representation z = f_θ(H(x))
      iii. Compute trajectory Δf_θ(H(x))
   c. Compute L_contrast over batch B
   d. Compute L_trajectory over attack samples in B
   e. Compute probe losses: L_probe = Σ_l BCE(g_l(h_l(x)), y)
   f. Total loss: L = L_contrast + λ·L_trajectory + μ·L_probe
   g. Update θ, {g_l}, v_adv via Adam optimizer
3. Calibrate threshold θ on validation set to achieve FPR = 0.1%
4. Return f_θ, {g_l}, v_adv, θ
```

### 2.4 Experimental Design

#### 2.4.1 Datasets

**Training Data:**
- **Benign samples:** 10,000 samples from ShareGPT, LMSYS-Chat-1M (diverse conversational data)
- **Attack samples:** 
  - Direct injection: 2,000 samples from AdvBench
  - Jailbreaking: 2,000 samples from JailbreakBench
  - Context manipulation: 2,000 synthetic RAG poisoning samples
  - Cognitive overload: 2,000 samples with nested instructions
  - Combined multi-vector: 2,000 samples combining 2+ attack types

**Test Data:** Held-out 20% from each category, plus 500 novel attack combinations not seen during training.

#### 2.4.2 Models

- **Primary:** Llama-3-8B-Instruct
- **Scale validation:** Llama-3-70B-Instruct
- **Generalization:** Mistral-7B-Instruct (architecture transfer)

#### 2.4.3 Baselines

1. **Perplexity-based detection:** Flag inputs with perplexity > threshold
2. **SPIN (Single-vector):** State-of-the-art prompt injection detector
3. **Guardrails (Llama Guard):** Content-based safety classifier
4. **Full-layer monitoring:** Probes at all layers (overhead comparison)

#### 2.4.4 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| TPR@FPR=0.1% | True positive rate when false positive rate = 0.1% | >80% |
| AUROC | Area under ROC curve | >0.95 |
| Attack Success Rate | % attacks bypassing defense | <20% |
| Inference Overhead | Additional latency vs. undefended | <5% |
| Silhouette Score | Clustering quality in projected space | >0.3 |

#### 2.4.5 Statistical Analysis

- **Sample size:** n ≥ 200 per attack category (1,000 total test samples)
- **Effect size:** Cohen's h = 0.4 (medium-large)
- **Statistical power:** 0.8 at α = 0.05
- **Primary test:** McNemar's test for paired comparison with Bonferroni correction
- **Reporting:** Detection rates with 95% confidence intervals, odds ratios, confusion matrices

### 2.5 Ablation Studies

1. **Layer selection:** Compare {1, L/2, L} vs. {1, L/4, L/2, 3L/4, L} vs. all layers
2. **Projection dimension:** k ∈ {16, 32, 64, 128}
3. **Contrastive vs. trajectory loss:** Evaluate contribution of each component
4. **Attack vector generalization:** Train on subset, test on held-out attack types

### 2.6 Adversarial Robustness Evaluation

To validate robustness against adaptive adversaries, we implement JudgeDeceiver-style optimization attacks specifically targeting ARID:

$$x^* = \arg\min_x \mathcal{L}_{attack}(x) - \beta \cdot p_{attack}(x)$$

where $\mathcal{L}_{attack}$ is the attack objective and $\beta$ controls evasion pressure. We evaluate ARID's detection rate under varying $\beta$ values to characterize the attack-defense tradeoff.

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and preliminary analysis, we anticipate the following outcomes:

**Primary Outcome (P1):** ARID will achieve TPR@FPR=0.1% exceeding 80% on combined multi-vector attacks, representing a >20 percentage point improvement over single-vector defenses. This improvement stems from the shared adversarial-intent subspace capturing cross-vector attack signatures.

**Secondary Outcomes:**
- **P2:** Against JudgeDeceiver-style optimization attacks, ARID will maintain >80% detection rate compared to <50% for threshold-based defenses, validating the trajectory-based approach's robustness.
- **P3:** Selective layer monitoring will achieve <5% inference overhead while maintaining detection performance within 3% of full-layer monitoring.

**Mechanism Validation:** We expect silhouette scores >0.3 in the projected adversarial-intent subspace, confirming that diverse attack vectors cluster together, supporting our core hypothesis about shared representation-level signatures.

### 3.2 Potential Limitations

1. **Arms race dynamics:** Sophisticated adversaries may develop attacks specifically targeting trajectory-based detection, necessitating periodic model updates.
2. **Scale constraints:** Validation on 70B+ models may reveal computational challenges not apparent at 8B scale.
3. **Distribution shift:** Novel attack vectors not represented in training may evade detection initially.

### 3.3 Scientific Impact

This research contributes to multiple areas of LLM security and trustworthiness:

1. **Theoretical contribution:** Establishes the adversarial trajectory framework as a principled approach to understanding attack behavior in transformer representations.
2. **Methodological contribution:** Introduces contrastive adversarial-intent projection as a technique for unified multi-vector defense.
3. **Empirical contribution:** Provides comprehensive evaluation of representation-level defense against state-of-the-art attacks.

### 3.4 Practical Impact

ARID addresses critical deployment challenges for LLM systems:

1. **Unified defense:** Reduces the complexity of maintaining separate defenses for each attack type.
2. **Production-ready:** <5% overhead enables deployment in latency-sensitive applications.
3. **Adaptive capability:** The immune-inspired framework supports continuous learning against emerging threats.

### 3.5 Broader Implications

Success in this research would advance the broader goal of trustworthy AI by demonstrating that representation-level analysis can provide robust security guarantees. The trajectory-based detection paradigm may generalize beyond LLMs to other deep learning systems facing adversarial threats, contributing to the emerging field of AI safety and security.