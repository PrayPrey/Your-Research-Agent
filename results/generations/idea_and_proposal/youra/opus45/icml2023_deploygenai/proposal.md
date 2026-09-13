# Research Proposal: Semantic Harm Affinity Maturation (SHAM): Bridging the Generalization Gap in LLM Safety Guardrails

## 1. Introduction

### 1.1 Background

The rapid deployment of Large Language Models (LLMs) across high-stakes domains—including healthcare diagnostics, legal consultation, and financial advising—has created an urgent need for robust safety mechanisms. Current safety guardrails, designed to detect and block harmful prompts, represent a critical line of defense against adversarial misuse. However, recent evaluations have exposed a fundamental vulnerability: state-of-the-art guardrail systems exhibit dramatic performance degradation when confronted with novel adversarial attacks not represented in their training distributions.

The Young (2025) evaluation framework reveals that leading guardrail systems like Qwen3Guard-8B achieve 91.0% accuracy on benchmark attacks but plummet to 33.8% on novel attack variants—a staggering 57.2 percentage point gap. This "benchmark-to-novel gap" represents a critical deployment vulnerability that undermines the reliability of LLM safety in real-world applications. In healthcare contexts, for instance, such failures could enable adversarial actors to extract dangerous medical advice or manipulate clinical decision support systems.

The root cause of this generalization failure lies in how traditional classifier-based guardrails learn to detect harmful content. Current approaches predominantly capture surface-level patterns—specific typographical errors, cipher encodings, or syntactic structures—rather than the underlying semantic intent of harmful requests. When adversaries introduce novel surface variations (new ciphers, paraphrasing strategies, or encoding schemes), these pattern-matching classifiers fail catastrophically despite the harmful intent remaining unchanged.

### 1.2 Research Objectives

This research proposes Semantic Harm Affinity Maturation (SHAM), a novel dual-layer architecture designed to address the fundamental generalization failure of current LLM safety guardrails. Our primary objectives are:

1. **Develop a contrastive semantic harm encoder** that captures harmful intent in a surface-invariant embedding space, enabling recognition of attacks based on their semantic meaning rather than superficial patterns.

2. **Design an evolutionary affinity maturation mechanism** that dynamically expands decision boundaries using held-out attack variants as fitness signals, mimicking the adaptive immune system's ability to recognize novel pathogens.

3. **Validate the SHAM architecture** against state-of-the-art baselines, demonstrating significant reduction in the benchmark-to-novel generalization gap while maintaining acceptable false positive rates.

### 1.3 Research Significance

This research addresses a critical gap in deploying generative AI safely in high-stakes domains. The significance extends across multiple dimensions:

**Scientific Contribution:** SHAM introduces a novel theoretical framework bridging contrastive representation learning with evolutionary optimization for safety-critical NLP applications. The dual-layer architecture draws inspiration from immunological principles of innate and adaptive immunity, offering a new paradigm for robust adversarial detection.

**Practical Impact:** By reducing the benchmark-to-novel gap from >50% to <30%, SHAM enables more reliable guardrail deployment in healthcare, finance, and legal domains where adversarial robustness is paramount. This directly addresses the workshop's focus on deployment-critical features including safety, robustness, and real-world applicability.

**Methodological Advancement:** The proposed evaluation framework, incorporating both semantic clustering metrics and generalization gap measurements, provides a more comprehensive assessment methodology for guardrail systems than current benchmark-focused approaches.

## 2. Methodology

### 2.1 Overall Architecture

SHAM employs a dual-layer architecture combining fast semantic similarity detection (analogous to innate immunity) with evolved adaptive classifiers (analogous to adaptive immunity). The system processes input prompts through four sequential stages:

1. **Contrastive Semantic Encoding:** Transform input prompts into surface-invariant harm embeddings
2. **Semantic Clustering Detection:** Rapid detection via similarity to known harm clusters
3. **Evolutionary Affinity Maturation:** Adaptive boundary expansion for novel attack recognition
4. **Dual-Layer Decision Fusion:** Combined detection leveraging both layers

### 2.2 Contrastive Semantic Harm Encoder

#### 2.2.1 Training Data Construction

We construct attack-intent pairs $(x_i, x_j, y_{ij})$ where $y_{ij} = 1$ if attacks $x_i$ and $x_j$ share the same harmful intent category despite different surface expressions, and $y_{ij} = 0$ otherwise. Intent categories follow the 21-category taxonomy from Young (2025), including violence incitement, illegal activity facilitation, privacy violation, and others.

Positive pairs are generated through:
- **Paraphrase augmentation:** Semantically equivalent reformulations
- **Surface mutation:** Typos, character substitutions, cipher encodings
- **Structural variation:** Different syntactic structures preserving intent

#### 2.2.2 Contrastive Learning Objective

We employ the InfoNCE loss to train the semantic encoder $f_\theta$:

$$\mathcal{L}_{\text{InfoNCE}} = -\log \frac{\exp(\text{sim}(z_i, z_j^+) / \tau)}{\exp(\text{sim}(z_i, z_j^+) / \tau) + \sum_{k=1}^{K} \exp(\text{sim}(z_i, z_k^-) / \tau)}$$

where $z_i = f_\theta(x_i)$ represents the embedding of prompt $x_i$, $z_j^+$ is a positive pair (same intent), $z_k^-$ are negative pairs (different intents), $\text{sim}(\cdot, \cdot)$ denotes cosine similarity, and $\tau$ is the temperature parameter.

The encoder architecture builds upon a pre-trained transformer (e.g., RoBERTa-large) with a projection head mapping to a 256-dimensional embedding space. Training proceeds for 50 epochs with batch size 512, learning rate $2 \times 10^{-5}$, and temperature $\tau = 0.07$.

#### 2.2.3 Semantic Clustering Validation

Post-training, we validate embedding quality using:

**Clustering Purity:**
$$\text{Purity} = \frac{1}{N} \sum_{k=1}^{K} \max_j |c_k \cap t_j|$$

where $c_k$ represents cluster $k$ and $t_j$ represents true intent category $j$.

**Silhouette Score:**
$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

where $a(i)$ is the mean intra-cluster distance and $b(i)$ is the mean nearest-cluster distance.

**Success Criteria:** Clustering purity > 0.7 and silhouette score > 0.3 on held-out attack variants.

### 2.3 Evolutionary Affinity Maturation

#### 2.3.1 Motivation and Design

Inspired by the immune system's affinity maturation process—where B-cells undergo somatic hypermutation and selection to improve antibody binding—we design an evolutionary optimization procedure that expands classifier decision boundaries to recognize novel attack variants.

#### 2.3.2 Boundary Representation

We represent decision boundaries as a set of prototype vectors $\{p_1, p_2, ..., p_M\}$ in the semantic embedding space, each associated with a harm category. The detection score for an input embedding $z$ is:

$$s(z) = \max_{m=1}^{M} \left( \text{sim}(z, p_m) - \delta_m \right)$$

where $\delta_m$ is a learnable threshold for prototype $m$.

#### 2.3.3 Evolutionary Optimization via CMA-ES

We employ Covariance Matrix Adaptation Evolution Strategy (CMA-ES) to optimize prototype positions and thresholds. The optimization proceeds as follows:

**Initialization:** Sample initial population of $\lambda = 50$ candidate solutions from the current prototype distribution.

**Fitness Evaluation:** For each candidate solution $\theta_i = \{p_1^{(i)}, ..., p_M^{(i)}, \delta_1^{(i)}, ..., \delta_M^{(i)}\}$:

$$F(\theta_i) = \alpha \cdot \text{TPR}_{\text{novel}}(\theta_i) - \beta \cdot \text{FPR}(\theta_i) + \gamma \cdot \text{Coverage}(\theta_i)$$

where $\text{TPR}_{\text{novel}}$ is the true positive rate on held-out novel attacks, $\text{FPR}$ is the false positive rate on benign prompts, and $\text{Coverage}$ measures the diversity of detected attack patterns. We set $\alpha = 1.0$, $\beta = 2.0$, $\gamma = 0.5$.

**Selection and Update:** Select the top $\mu = 25$ solutions and update the CMA-ES distribution parameters:

$$m^{(g+1)} = \sum_{i=1}^{\mu} w_i \theta_{i:\lambda}^{(g)}$$

$$C^{(g+1)} = (1 - c_1 - c_\mu) C^{(g)} + c_1 p_c^{(g+1)} (p_c^{(g+1)})^T + c_\mu \sum_{i=1}^{\mu} w_i y_{i:\lambda}^{(g)} (y_{i:\lambda}^{(g)})^T$$

where $m$ is the distribution mean, $C$ is the covariance matrix, and $c_1$, $c_\mu$ are learning rates.

**Termination:** Evolution proceeds for 100 generations or until fitness improvement < 0.001 for 10 consecutive generations.

**Computational Budget:** The entire maturation process is constrained to < 4 GPU-hours on A100-equivalent hardware.

### 2.4 Dual-Layer Decision Fusion

The final detection decision combines outputs from both layers:

$$D(x) = \sigma\left( w_1 \cdot s_{\text{semantic}}(x) + w_2 \cdot s_{\text{evolved}}(x) + b \right)$$

where $s_{\text{semantic}}(x)$ is the maximum similarity to any harm cluster centroid, $s_{\text{evolved}}(x)$ is the evolved prototype-based score, and $w_1$, $w_2$, $b$ are learned fusion parameters. The prompt is classified as harmful if $D(x) > 0.5$.

### 2.5 Experimental Design

#### 2.5.1 Datasets

**Training Data:**
- **HarmBench:** 510 harmful behaviors with multiple attack variants
- **AdvBench:** 520 adversarial prompts across harm categories
- **JailbreakBench:** 100 jailbreak attempts with surface variations
- **Synthetic Augmentation:** 10,000 additional pairs generated via paraphrasing and mutation

**Evaluation Data:**
- **Benchmark Set:** Standard evaluation prompts from Young (2025) framework
- **Novel Attack Set:** Held-out attack variants including new ciphers, encoding schemes, and paraphrasing strategies not seen during training
- **Benign Set:** 5,000 legitimate prompts for false positive evaluation

#### 2.5.2 Baseline Systems

1. **Qwen3Guard-8B:** State-of-the-art guardrail with highest overall accuracy but largest generalization gap (57.2 pp)
2. **Granite-Guardian-3.2-5B:** Best generalization performance (6.5 pp gap) but lower overall accuracy
3. **LlamaGuard-3-8B:** Widely deployed baseline
4. **SHAM-Semantic-Only:** Ablation using only contrastive encoder without affinity maturation
5. **SHAM-Evolution-Only:** Ablation using only evolutionary optimization on standard embeddings

#### 2.5.3 Evaluation Metrics

**Primary Metrics:**
- **Benchmark-to-Novel Gap:** $\text{Gap} = |\text{Acc}_{\text{benchmark}} - \text{Acc}_{\text{novel}}|$
- **Overall Accuracy:** Weighted average across all attack categories
- **Novel Attack Detection Rate:** True positive rate on unseen attack variants

**Secondary Metrics:**
- **False Positive Rate:** Percentage of benign prompts incorrectly flagged
- **Clustering Purity:** Quality of semantic harm embeddings
- **Silhouette Score:** Embedding space separability
- **Inference Latency:** Time per prompt classification

#### 2.5.4 Statistical Analysis

All experiments are conducted with $n = 25$ independent runs to ensure statistical reliability. We report:
- Mean and standard deviation for all metrics
- 95% confidence intervals
- Paired t-tests comparing SHAM to each baseline ($\alpha = 0.05$, one-tailed)
- Effect size (Cohen's d) for primary comparisons

**Success Criteria:**
- Primary: Gap < 30 pp with $p < 0.05$
- Secondary: Clustering purity > 0.7, FPR within baseline + 5%

**Falsification Criteria:**
- Gap ≥ 45 pp (insufficient improvement)
- Clustering purity < 0.5 (semantic encoding failure)
- Affinity maturation improvement < 5 pp over semantic-only (evolution failure)
- FPR > baseline + 10% (selectivity failure)

#### 2.5.5 Ablation Studies

To validate the causal mechanism, we conduct systematic ablations:

1. **Semantic Encoding Ablation:** Compare SHAM embeddings vs. standard transformer embeddings
2. **Contrastive Loss Ablation:** Compare InfoNCE vs. triplet loss vs. supervised classification
3. **Evolution Strategy Ablation:** Compare CMA-ES vs. genetic algorithm vs. random search
4. **Fusion Strategy Ablation:** Compare learned fusion vs. simple averaging vs. max pooling

### 2.6 Implementation Details

**Hardware:** All experiments conducted on NVIDIA A100 GPUs (40GB)
**Software:** PyTorch 2.0, Hugging Face Transformers, pycma for CMA-ES
**Reproducibility:** All code, trained models, and evaluation scripts will be released publicly

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our theoretical analysis and preliminary evidence from related work, we anticipate the following outcomes:

**Primary Outcome:** SHAM will achieve a benchmark-to-novel gap of < 30 percentage points, representing a >45% relative reduction compared to Qwen3Guard's 57.2 pp gap. We expect overall accuracy to remain competitive at approximately 80-85%.

**Mechanism Validation:** 
- Contrastive semantic encoding will achieve clustering purity > 0.7, demonstrating that harmful intent can be captured in a surface-invariant embedding space
- Evolutionary affinity maturation will contribute >10 pp improvement over semantic encoding alone, validating the adaptive boundary expansion mechanism
- The dual-layer architecture will show synergistic benefits exceeding the sum of individual components

**Efficiency:** The complete affinity maturation process will converge within 4 GPU-hours, making SHAM practical for deployment scenarios requiring periodic model updates.

### 3.2 Scientific Impact

This research contributes to multiple scientific domains:

**Adversarial Robustness:** SHAM introduces a novel paradigm for robust adversarial detection that moves beyond pattern matching to semantic understanding. The contrastive learning approach for harm intent representation advances our understanding of how to create attack-invariant features.

**Evolutionary Computation in NLP:** The application of CMA-ES for decision boundary optimization in high-dimensional embedding spaces extends evolutionary computation methodology to safety-critical NLP applications.

**Immunology-Inspired AI:** The dual-layer architecture, inspired by innate and adaptive immunity, provides a new theoretical framework for designing robust detection systems that can both rapidly respond to known threats and adapt to novel ones.

### 3.3 Practical Impact

**Healthcare AI Safety:** Reliable guardrails enable safer deployment of LLM-based clinical decision support systems, reducing risks of adversarial manipulation that could lead to patient harm.

**Financial Services:** Robust detection of novel attack patterns protects against adversarial attempts to extract sensitive financial advice or manipulate automated trading systems.

**Legal Technology:** Improved generalization ensures that legal AI assistants maintain safety boundaries even when confronted with sophisticated adversarial prompts.

### 3.4 Limitations and Future Work

**Current Limitations:**
- SHAM cannot create new semantic harm categories; it only expands boundaries of known intent clusters
- The approach may miss attacks exploiting semantic ambiguity where harm is context-dependent
- Computational overhead of dual-layer system may impact inference latency for real-time applications

**Future Directions:**
- Extension to multimodal attacks involving images, audio, and video
- Integration with continual learning for online adaptation to emerging attack patterns
- Development of interpretability mechanisms to explain detection decisions
- Investigation of privacy-preserving training approaches for sensitive harm data

### 3.5 Broader Impact

This research directly addresses the workshop's focus on deployment-critical features for generative AI. By improving the robustness of safety guardrails, SHAM contributes to the responsible deployment of LLMs in high-stakes domains. The methodology and evaluation framework developed here can inform future research on adversarial robustness across multiple modalities and application domains.

The open release of code, models, and evaluation protocols will enable the research community to build upon this work, fostering collaborative advancement toward more reliable AI safety mechanisms. Ultimately, this research aims to bridge the gap between benchmark performance and real-world safety, enabling the beneficial deployment of generative AI while mitigating risks of adversarial misuse.