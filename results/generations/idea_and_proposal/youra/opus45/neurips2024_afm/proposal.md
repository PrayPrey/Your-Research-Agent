# Research Proposal: Compositional Primitive LoRA for Parameter-Efficient Personalization of Foundation Models

## 1. Introduction

### 1.1 Background

The proliferation of large foundation models has transformed artificial intelligence, enabling unprecedented capabilities across language understanding, generation, and multimodal reasoning. However, deploying these models for personalized user experiences presents significant challenges. Traditional personalization approaches require fine-tuning separate Low-Rank Adaptation (LoRA) modules for each user, typically involving approximately 100,000 parameters per user. At scale—serving millions of users—this approach becomes computationally prohibitive and storage-intensive. Furthermore, when user interaction data is limited (fewer than 100 samples per user), individual LoRA fine-tuning suffers from overfitting and poor generalization.

Recent advances in parameter-efficient fine-tuning have introduced methods such as PROPER, which employs routing mechanisms to assign users to group-level adapters, and VB-LoRA, which demonstrates that shared vector banks can achieve remarkable parameter efficiency. Concurrently, research in compositional learning, exemplified by Lake and Baroni's work on human-like systematic generalization, suggests that complex behaviors can emerge from combinations of simpler primitives. This insight motivates a fundamental question: can diverse user preferences be expressed as compositions of shared preference primitives, analogous to how humans achieve systematic generalization through compositional structure?

### 1.2 Research Objectives

This research proposes **Compositional Primitive LoRA (CP-LoRA)**, a novel framework that represents user personalization as learned compositions over a shared bank of primitive LoRA modules. Our primary objectives are:

1. **Develop a compositional personalization framework** that achieves comparable personalization accuracy to user-specific LoRA while using fewer than 10,000 user-specific parameters (representing a >10× efficiency improvement).

2. **Design and validate orthogonal primitive LoRA modules** that capture diverse preference patterns through contrastive pre-training on population data.

3. **Demonstrate generalization preservation** by showing that frozen primitives with learned composition networks retain >95% of base model performance on general benchmarks.

4. **Establish theoretical and empirical foundations** for compositional personalization in foundation models.

### 1.3 Significance

This research addresses a critical bottleneck in deploying personalized AI at scale. By reducing per-user parameter overhead by an order of magnitude while maintaining personalization quality, CP-LoRA enables:

- **Scalable personalization** for platforms serving millions of users
- **Effective cold-start adaptation** with limited user data (<100 interactions)
- **Preserved generalization** ensuring personalized models remain capable on general tasks
- **Reduced computational and storage costs** for model serving infrastructure

The proposed approach bridges compositional learning theory with practical foundation model adaptation, contributing both methodological innovations and theoretical insights to the adaptive foundation models research community.

---

## 2. Methodology

### 2.1 Overview

CP-LoRA consists of three main components: (1) a shared bank of $K$ primitive LoRA modules pre-trained on population data, (2) a lightweight user-specific composition network that learns to combine primitives, and (3) an inference mechanism that applies the composed adaptation to the base model. Figure 1 illustrates the overall architecture.

### 2.2 Primitive LoRA Bank Design

#### 2.2.1 Primitive Architecture

Each primitive LoRA module $\mathcal{P}_k$ for $k \in \{1, ..., K\}$ follows the standard LoRA formulation but with Minimal Semantic Unit (MSU) design principles to ensure combinability:

$$\mathcal{P}_k = B_k A_k$$

where $A_k \in \mathbb{R}^{r \times d_{in}}$ and $B_k \in \mathbb{R}^{d_{out} \times r}$ are low-rank matrices with rank $r$. Following LoRA-LEGO's MSU design, we enforce:

1. **Orthogonality constraint**: Primitives are initialized and regularized to maintain orthogonal subspaces:
$$\mathcal{L}_{orth} = \sum_{i \neq j} \|A_i^T A_j\|_F^2 + \|B_i B_j^T\|_F^2$$

2. **Permutation invariance**: The composition mechanism ensures that primitive ordering does not affect the final adaptation.

#### 2.2.2 Contrastive Pre-training

We pre-train the primitive bank on population-level data $\mathcal{D}_{pop}$ (e.g., OpenAssistant, ShareGPT) using a contrastive objective that encourages primitives to capture diverse, distinguishable preference patterns:

$$\mathcal{L}_{contrast} = -\log \frac{\exp(sim(h_i, h_j^+)/\tau)}{\sum_{k=1}^{K} \exp(sim(h_i, h_k)/\tau)}$$

where $h_i$ represents the hidden representation after applying primitive $\mathcal{P}_i$, $h_j^+$ is a positive sample from the same preference cluster, and $\tau$ is a temperature parameter.

The total pre-training loss combines task performance with diversity objectives:

$$\mathcal{L}_{pretrain} = \mathcal{L}_{task} + \lambda_1 \mathcal{L}_{orth} + \lambda_2 \mathcal{L}_{contrast}$$

where $\lambda_1 = 0.1$ and $\lambda_2 = 0.05$ are hyperparameters determined through validation.

### 2.3 User Composition Network

#### 2.3.1 Architecture

For each user $u$, we learn a lightweight composition network $\mathcal{C}_u$ with approximately 5,000 parameters. The network employs cross-attention between user history embeddings and primitive representations:

**User History Encoding:**
Given user interaction history $\mathcal{H}_u = \{(x_1, y_1), ..., (x_n, y_n)\}$, we compute:

$$e_u = \text{MeanPool}(\text{Encoder}(\mathcal{H}_u)) \in \mathbb{R}^{d_h}$$

**Primitive Representation:**
Each primitive is represented by a learnable embedding $p_k \in \mathbb{R}^{d_p}$ for $k \in \{1, ..., K\}$.

**Cross-Attention Composition:**
The composition weights are computed via scaled dot-product attention:

$$\alpha_k^u = \text{softmax}\left(\frac{(W_Q e_u)(W_K p_k)^T}{\sqrt{d_k}}\right)$$

where $W_Q \in \mathbb{R}^{d_k \times d_h}$ and $W_K \in \mathbb{R}^{d_k \times d_p}$ are projection matrices shared across users, and user-specific parameters are limited to a small residual vector $r_u \in \mathbb{R}^{d_r}$ that modulates the attention:

$$\tilde{\alpha}_k^u = \alpha_k^u + \text{MLP}(r_u)_k$$

#### 2.3.2 Parameter Budget

The user-specific parameters consist of:
- Residual vector: $r_u \in \mathbb{R}^{512}$ (512 parameters)
- User-specific attention bias: $b_u \in \mathbb{R}^{K}$ (64-128 parameters)
- Optional: Small MLP layer (4,000-4,500 parameters)

**Total: ~5,000 parameters per user** (compared to ~100,000 for user-specific LoRA)

### 2.4 Composed Adaptation

The final adaptation applied to the base model combines primitives according to learned weights:

$$\Delta W_u = \sum_{k=1}^{K} \tilde{\alpha}_k^u \cdot \mathcal{P}_k = \sum_{k=1}^{K} \tilde{\alpha}_k^u \cdot B_k A_k$$

The adapted model output for user $u$ on input $x$ is:

$$y_u = f(W_0 + \Delta W_u; x)$$

where $W_0$ represents the frozen base model weights.

### 2.5 Training Procedure

**Phase 1: Primitive Pre-training (One-time)**
1. Initialize $K=64$ primitive LoRA modules with orthogonal initialization
2. Pre-train on population data $\mathcal{D}_{pop}$ for 50,000 steps
3. Apply contrastive and orthogonality losses
4. Freeze all primitive parameters

**Phase 2: User Composition Learning**
1. For each user $u$ with history $\mathcal{H}_u$:
   - Initialize composition network $\mathcal{C}_u$
   - Train on user-specific data with cross-entropy loss:
   $$\mathcal{L}_u = -\sum_{(x,y) \in \mathcal{H}_u} \log p(y|x; W_0 + \Delta W_u)$$
   - Apply early stopping based on validation performance

### 2.6 Experimental Design

#### 2.6.1 Datasets

| Dataset | Domain | Users | Samples/User | Task |
|---------|--------|-------|--------------|------|
| PersoBench | Dialogue | 500+ | 50-200 | Response generation |
| LaMP | Language | 1,000+ | 20-100 | Personalized QA |
| Amazon Reviews | E-commerce | 10,000+ | 10-500 | Sentiment/Recommendation |

#### 2.6.2 Baselines

1. **User-Specific LoRA**: Individual LoRA fine-tuning per user (~100K params)
2. **PROPER**: User-aware routing with group-level LoRAs
3. **VB-LoRA**: Shared vector bank approach
4. **Prompt Tuning**: Soft prompt personalization
5. **In-Context Learning**: Few-shot personalization without fine-tuning

#### 2.6.3 Evaluation Metrics

**Personalization Accuracy:**
- Task completion accuracy on user-specific benchmarks
- Personalization score: $PS = \frac{Acc_{CP-LoRA}}{Acc_{UserLoRA}}$

**Generalization Retention:**
- Performance on MMLU, HellaSwag, ARC-Challenge
- Retention rate: $GR = \frac{Perf_{adapted}}{Perf_{base}}$

**Parameter Efficiency:**
- User-specific parameter count
- Efficiency ratio: $ER = \frac{Params_{UserLoRA}}{Params_{CP-LoRA}}$

#### 2.6.4 Statistical Analysis

- **Sample size**: $n \geq 25$ users per condition (power analysis: Cohen's d = 0.5, power = 0.8)
- **Primary test**: Paired t-test comparing CP-LoRA vs. user-specific LoRA
- **Significance level**: $\alpha = 0.05$
- **Reporting**: Mean ± Std Dev, 95% CI, Cohen's d, p-value

#### 2.6.5 Ablation Studies

1. **Number of primitives**: $K \in \{32, 64, 128\}$
2. **Composition network size**: 2K, 5K, 10K parameters
3. **Pre-training data scale**: 100K, 500K, 1M samples
4. **Orthogonality constraint strength**: $\lambda_1 \in \{0.01, 0.1, 1.0\}$

### 2.7 Implementation Details

- **Base models**: LLaMA-7B, LLaMA-13B, Mistral-7B
- **LoRA rank**: $r = 8$ per primitive
- **Number of primitives**: $K = 64$ (default)
- **Training**: AdamW optimizer, learning rate $1 \times 10^{-4}$, batch size 32
- **Hardware**: 8× NVIDIA A100 GPUs
- **Estimated compute**: 1-2 days for primitive pre-training, <1 hour per user adaptation

---

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and supporting evidence from related work, we anticipate the following outcomes:

**Primary Outcome (P1):** CP-LoRA will achieve personalization accuracy $\geq 90\%$ of user-specific LoRA baselines on PersoBench and LaMP benchmarks. This prediction is supported by VB-LoRA's demonstration that shared representations can match full fine-tuning performance and LoRA-LEGO's validation of MSU combinability.

**Secondary Outcomes:**
- **P2 (Generalization):** Retention of $>95\%$ base model performance on general benchmarks, as frozen primitives preserve the model's general knowledge while composition networks handle user-specific adaptation.
- **P3 (Efficiency):** Achievement of target personalization with $<10,000$ user-specific parameters, representing $>10\times$ efficiency improvement over conventional approaches.

### 3.2 Falsification Criteria

The hypothesis will be rejected if:
1. Personalization accuracy falls below 80% of user-specific LoRA baseline
2. Generalization retention drops below 85% of base model performance
3. User-specific parameters exceed 50,000 without accuracy gains
4. $K=128$ primitives fail to cover $>80\%$ of test user preferences

### 3.3 Scientific Contributions

1. **Theoretical**: Establishing compositional structure as a viable paradigm for personalization, bridging cognitive science insights with practical ML systems.

2. **Methodological**: Novel primitive pre-training objectives combining contrastive learning with orthogonality constraints for diverse, combinable adapters.

3. **Empirical**: Comprehensive evaluation demonstrating the personalization-efficiency-generalization trade-off across multiple domains and model scales.

### 3.4 Broader Impact

**Practical Applications:**
- Scalable personalized assistants for consumer applications
- Efficient recommendation systems with user-specific adaptation
- Privacy-preserving personalization (minimal user-specific storage)

**Research Directions:**
- Extension to multimodal foundation models (vision-language personalization)
- Continual primitive learning for evolving user preferences
- Federated compositional learning for privacy-sensitive domains

**Limitations and Ethical Considerations:**
- Primitive pre-training requires substantial population data, raising data governance questions
- Compositional representation may not capture extreme outlier preferences
- Personalization systems require careful consideration of filter bubbles and bias amplification

---

## 4. Conclusion

This proposal presents CP-LoRA, a compositional approach to parameter-efficient personalization that addresses the scalability challenges of adapting foundation models to individual users. By representing user preferences as learned compositions over shared primitive LoRA modules, we hypothesize that comparable personalization quality can be achieved with an order of magnitude fewer user-specific parameters. The proposed methodology combines insights from compositional learning, contrastive representation learning, and efficient fine-tuning to create a practical framework for scalable personalized AI. Through rigorous experimental validation on established benchmarks with clearly defined success and falsification criteria, this research aims to advance both the theoretical understanding and practical deployment of adaptive foundation models.