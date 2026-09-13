# Research Proposal: Rank-Aware Differential Privacy for Heterogeneous Federated LoRA Fine-Tuning

## 1. Title

**Rank-Aware Differential Privacy for Heterogeneous Federated LoRA Fine-Tuning: Information-Theoretic Privacy Budget Allocation for Foundation Model Adaptation**

---

## 2. Introduction

### 2.1 Background

Foundation models (FMs) have revolutionized machine learning, demonstrating remarkable capabilities across natural language processing, computer vision, and multimodal tasks. Models such as GPT-4, Llama, and their variants encode vast knowledge through pre-training on massive datasets, enabling powerful transfer learning to downstream applications. However, the deployment of these models in privacy-sensitive domains—healthcare, finance, legal services—faces fundamental challenges: the data required for domain-specific fine-tuning is often distributed across multiple organizations, subject to regulatory constraints (e.g., GDPR, HIPAA), and cannot be centralized without violating privacy requirements.

Federated Learning (FL) has emerged as a promising paradigm to address these challenges by enabling collaborative model training without centralizing raw data. In federated settings, clients train local models on their private data and share only model updates with a central server for aggregation. This approach preserves data locality while enabling collective learning across distributed sources. The intersection of FL with foundation models presents unique opportunities: organizations can collaboratively adapt powerful pre-trained models to domain-specific tasks while maintaining data sovereignty.

Parameter-efficient fine-tuning (PEFT) methods, particularly Low-Rank Adaptation (LoRA), have become essential for practical foundation model deployment. LoRA introduces trainable low-rank decomposition matrices $A \in \mathbb{R}^{r \times d}$ and $B \in \mathbb{R}^{d \times r}$ alongside frozen pre-trained weights, reducing trainable parameters by orders of magnitude while maintaining competitive performance. In federated settings, LoRA offers significant communication efficiency—clients transmit only adapter parameters rather than full model weights.

However, a critical challenge emerges when combining differential privacy (DP) with heterogeneous federated LoRA fine-tuning. Real-world federated deployments involve clients with vastly different computational resources: edge devices may support only rank-4 adapters, while server-class machines can handle rank-64 configurations. Current approaches apply uniform privacy budgets across all clients regardless of their adapter capacity, creating a fundamental mismatch. High-rank adapters, with greater expressiveness and more parameters, receive insufficient privacy protection relative to their information capacity, while low-rank adapters are over-noised, degrading their utility disproportionately.

### 2.2 Research Objectives

This research proposes **Rank-Aware Differential Privacy for Federated LoRA (RA-DP-FL)**, a novel framework that allocates privacy budgets proportionally to client LoRA ranks. Our primary objectives are:

1. **Develop a theoretically-grounded privacy budget allocation mechanism** that distributes the total privacy budget $\varepsilon_{total}$ across heterogeneous clients according to their LoRA ranks, achieving equitable information leakage per unit adapter capacity.

2. **Design rank-aware noise calibration algorithms** that adjust Gaussian mechanism parameters based on rank-specific sensitivity bounds, ensuring tighter privacy-utility tradeoffs.

3. **Implement and validate the complete RA-DP-FL framework** through comprehensive experiments on Llama-7B across standard NLP benchmarks, demonstrating accuracy improvements over uniform allocation baselines.

4. **Establish theoretical foundations** connecting rank heterogeneity, privacy budget allocation, and information-theoretic optimality in federated adapter fine-tuning.

### 2.3 Research Significance

This research addresses a critical gap at the intersection of three rapidly evolving fields: federated learning, foundation models, and differential privacy. The significance is threefold:

**Theoretical Contribution:** We provide the first information-theoretic framework for privacy budget allocation in heterogeneous federated PEFT settings, establishing connections between adapter capacity, privacy loss, and optimal noise distribution.

**Practical Impact:** By enabling efficient privacy-preserving federated fine-tuning across resource-diverse client populations, our approach unlocks foundation model deployment in privacy-sensitive domains where current methods fail to provide adequate utility under strict privacy constraints.

**Methodological Advancement:** The rank-aware allocation principle generalizes beyond LoRA to other capacity-heterogeneous federated learning scenarios, providing a template for privacy-aware resource allocation in distributed systems.

---

## 3. Methodology

### 3.1 Problem Formulation

Consider a federated learning system with $N$ clients, where client $i$ possesses private dataset $D_i$ and computational resources supporting LoRA rank $r_i$. The global objective is to fine-tune a pre-trained foundation model $\theta_0$ by learning LoRA adapters while satisfying $(\varepsilon_{total}, \delta)$-differential privacy across the federation.

**Standard LoRA Formulation:** For a pre-trained weight matrix $W_0 \in \mathbb{R}^{d \times k}$, LoRA introduces:
$$W = W_0 + BA$$
where $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times k}$, and $r \ll \min(d, k)$.

**Federated Setting:** Each client $i$ maintains local adapters $(A_i, B_i)$ with rank $r_i$ determined by device resources. The server aggregates client updates to produce global adapters.

**Privacy Constraint:** The mechanism must satisfy $(\varepsilon_{total}, \delta)$-DP, where:
$$\Pr[\mathcal{M}(D) \in S] \leq e^{\varepsilon_{total}} \Pr[\mathcal{M}(D') \in S] + \delta$$
for all neighboring datasets $D, D'$ differing in one client's data.

### 3.2 Rank-Proportional Privacy Budget Allocation

**Core Allocation Formula:** We propose allocating privacy budget to client $i$ as:
$$\varepsilon_i = \varepsilon_{total} \times \frac{r_i}{\sum_{j=1}^{N} r_j}$$

**Information-Theoretic Justification:** This allocation follows from rate-distortion theory principles. The information capacity of a rank-$r$ adapter scales as $O(r \cdot (d + k))$ parameters. To achieve equitable information leakage per unit capacity, clients with higher capacity (rank) should receive proportionally larger privacy budgets, which translates to tighter noise requirements per parameter.

**Lemma 1 (Equitable Information Leakage):** Under rank-proportional allocation, the privacy loss per trainable parameter is equalized across clients:
$$\frac{\varepsilon_i}{r_i \cdot (d + k)} = \frac{\varepsilon_{total}}{(d + k) \sum_{j=1}^{N} r_j} = \text{constant}$$

### 3.3 Rank-Aware Noise Calibration

**Sensitivity Analysis:** For LoRA adapters with rank $r_i$, the $\ell_2$-sensitivity of gradient updates depends on the adapter dimensions:
$$\Delta_i = C \cdot \sqrt{r_i \cdot (d + k)}$$
where $C$ is the gradient clipping bound.

**Gaussian Mechanism Calibration:** Given allocated budget $\varepsilon_i$ and sensitivity $\Delta_i$, the noise standard deviation for client $i$ is:
$$\sigma_i = \frac{\Delta_i \sqrt{2 \ln(1.25/\delta_i)}}{\varepsilon_i}$$

Substituting our allocation:
$$\sigma_i = \frac{C \sqrt{r_i(d+k)} \cdot \sqrt{2\ln(1.25/\delta_i)} \cdot \sum_j r_j}{\varepsilon_{total} \cdot r_i}$$

**Key Insight:** The noise-to-signal ratio $\sigma_i / \|g_i\|$ becomes balanced across clients, preventing over-noising of low-rank adapters while ensuring adequate protection for high-rank adapters.

### 3.4 Complete Algorithm

**Algorithm 1: RA-DP-FL Framework**

```
Input: Pre-trained model θ₀, clients {1,...,N} with ranks {r₁,...,rₙ},
       total privacy budget ε_total, failure probability δ, rounds T
Output: Fine-tuned global LoRA adapters (A*, B*)

1. Server Initialization:
   - Initialize global adapters (A⁰, B⁰) randomly
   - Compute rank sum: R_total = Σᵢ rᵢ
   - Allocate budgets: εᵢ = ε_total × rᵢ / R_total for each client i

2. For round t = 1 to T:
   a. Server broadcasts (Aᵗ⁻¹, Bᵗ⁻¹) to all clients
   
   b. Client i Local Training (parallel):
      - Initialize local adapters: (Aᵢ, Bᵢ) ← SVD_truncate((Aᵗ⁻¹, Bᵗ⁻¹), rᵢ)
      - For each local epoch:
        * Compute gradients: gᵢ = ∇L(θ₀ + BᵢAᵢ; Dᵢ)
        * Clip gradients: ĝᵢ = gᵢ × min(1, C/‖gᵢ‖₂)
        * Compute noise: σᵢ = Δᵢ√(2ln(1.25/δᵢ))/εᵢ
        * Add noise: g̃ᵢ = ĝᵢ + N(0, σᵢ²I)
        * Update adapters: (Aᵢ, Bᵢ) ← (Aᵢ, Bᵢ) - η·g̃ᵢ
      - Upload noised adapter updates: ΔAᵢ, ΔBᵢ
   
   c. Server Aggregation:
      - Pad updates to maximum rank: r_max = max{rᵢ}
      - Weighted aggregation: 
        ΔA = Σᵢ (|Dᵢ|/|D|) × pad(ΔAᵢ, r_max)
        ΔB = Σᵢ (|Dᵢ|/|D|) × pad(ΔBᵢ, r_max)
      - Update global: (Aᵗ, Bᵗ) = (Aᵗ⁻¹ + ΔA, Bᵗ⁻¹ + ΔB)

3. Privacy Accounting:
   - Track per-client privacy loss using moments accountant
   - Verify: Σᵢ εᵢ ≤ ε_total (by construction)
   - Compose across rounds using advanced composition

4. Return (A*, B*) = (Aᵀ, Bᵀ)
```

### 3.5 Experimental Design

**3.5.1 Datasets and Tasks**

We evaluate on standard NLP benchmarks from GLUE and SuperGLUE:
- **SST-2**: Sentiment classification (67K training samples)
- **QNLI**: Question-answering NLI (105K samples)
- **MNLI**: Multi-genre NLI (393K samples)
- **QQP**: Paraphrase detection (364K samples)

Data is partitioned across clients using Dirichlet distribution ($\alpha = 0.5$) to simulate non-IID heterogeneity.

**3.5.2 Model and Infrastructure**

- **Base Model**: Llama-7B with LoRA applied to query and value projection matrices
- **LoRA Configuration**: Ranks $r \in \{4, 8, 16, 32, 64\}$ distributed across clients
- **Client Distribution**: 50 clients with rank distribution following resource heterogeneity (40% low-rank, 40% medium-rank, 20% high-rank)
- **Hardware**: Experiments conducted on NVIDIA A100 GPUs; client simulation on single GPU with sequential processing

**3.5.3 Baselines**

1. **Uniform-DP**: Standard DP-SGD with uniform $\varepsilon_i = \varepsilon_{total}/N$ for all clients
2. **FedAvg-LoRA (Non-private)**: Upper bound without differential privacy
3. **DP-FedLoRA**: Recent approach with uniform noise across LoRA matrices
4. **FlexLoRA (Non-private)**: Heterogeneous rank aggregation without DP

**3.5.4 Hyperparameters**

| Parameter | Value |
|-----------|-------|
| Learning rate | $1 \times 10^{-4}$ |
| Batch size | 16 per client |
| Local epochs | 5 |
| Communication rounds | 100 |
| Gradient clipping $C$ | 1.0 |
| Privacy budgets $\varepsilon_{total}$ | $\{1, 3, 5, 8\}$ |
| $\delta$ | $10^{-5}$ |

**3.5.5 Evaluation Metrics**

1. **Task Accuracy**: Classification accuracy on held-out test sets
2. **Privacy-Utility Tradeoff**: Accuracy vs. $\varepsilon_{total}$ curves
3. **Per-Client Performance**: Accuracy distribution across rank groups
4. **Communication Efficiency**: Bytes transmitted per round
5. **Convergence Speed**: Rounds to reach target accuracy

**3.5.6 Statistical Analysis**

- Each experiment repeated with 5 random seeds
- Report mean ± standard deviation
- Paired t-tests for significance ($\alpha = 0.05$)
- Effect size measured via Cohen's d
- Minimum 25 experimental runs for primary claims

### 3.6 Ablation Studies

**A1. Allocation Formula Variants:**
- Linear: $\varepsilon_i \propto r_i$ (proposed)
- Square-root: $\varepsilon_i \propto \sqrt{r_i}$
- Logarithmic: $\varepsilon_i \propto \log(r_i)$
- Uniform: $\varepsilon_i = \varepsilon_{total}/N$

**A2. Rank Distribution Impact:**
- Homogeneous (all same rank)
- Mildly heterogeneous (2-3 rank values)
- Highly heterogeneous (5+ rank values)

**A3. Privacy Budget Regimes:**
- Strict: $\varepsilon_{total} \in \{1, 2\}$
- Moderate: $\varepsilon_{total} \in \{3, 5\}$
- Relaxed: $\varepsilon_{total} \in \{8, 10\}$

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Results

**Primary Outcome (P1):** We predict that RA-DP-FL will achieve **2-5% accuracy improvement** over uniform DP allocation at $\varepsilon_{total} = 3$ across all evaluated tasks. This improvement stems from the balanced noise distribution that prevents over-noising of low-rank clients while maintaining adequate protection for high-rank clients.

**Secondary Outcomes:**

- **P2 (Mechanism Validation):** Analysis will confirm that higher-rank clients receive proportionally tighter effective privacy budgets without individual performance degradation, validating the information-theoretic foundation.

- **P3 (Robustness):** Accuracy advantages will be consistent across privacy regimes, with **larger gains (3-5%) under strict budgets** ($\varepsilon \leq 3$) where noise calibration matters most, and **moderate gains (1-2%) under relaxed budgets** ($\varepsilon \geq 5$).

- **P4 (Scalability):** Benefits will persist with increasing client counts (tested up to 100 clients), demonstrating practical applicability.

**Quantitative Predictions:**

| Task | Uniform-DP Acc. | RA-DP-FL Acc. | Improvement |
|------|-----------------|---------------|-------------|
| SST-2 | 88.2% | 91.5% | +3.3% |
| QNLI | 84.7% | 87.9% | +3.2% |
| MNLI | 79.3% | 82.1% | +2.8% |
| QQP | 85.1% | 88.4% | +3.3% |

*(Predictions at $\varepsilon_{total} = 3$, averaged across 5 seeds)*

### 4.2 Theoretical Contributions

1. **Information-Theoretic Framework:** First formal connection between adapter capacity, privacy budget allocation, and optimal noise distribution in federated PEFT settings.

2. **Composition Theorem Extension:** Novel privacy accounting for heterogeneous per-client budgets under moments accountant framework.

3. **Sensitivity Bounds:** Tight rank-dependent sensitivity analysis for LoRA gradient updates.

### 4.3 Practical Impact

**Enabling Privacy-Preserving FM Deployment:** Organizations in healthcare, finance, and legal sectors can collaboratively fine-tune foundation models on sensitive distributed data while maintaining formal privacy guarantees and practical utility.

**Resource-Efficient Participation:** Clients with limited computational resources can meaningfully participate in federated fine-tuning without disproportionate accuracy penalties from over-noising.

**Regulatory Compliance:** The formal $(\varepsilon, \delta)$-DP guarantees facilitate compliance with data protection regulations (GDPR, HIPAA) while enabling collaborative AI development.

### 4.4 Broader Impact

This research contributes to the democratization of foundation model adaptation by enabling privacy-preserving collaboration across organizations with heterogeneous resources. The rank-aware allocation principle extends beyond LoRA to other capacity-heterogeneous settings, providing a general framework for equitable privacy-utility tradeoffs in distributed machine learning.

**Limitations and Future Work:** The current framework assumes resource-based rank selection independent of data characteristics. Future work will address scenarios where adaptive rank selection based on task complexity is desirable, requiring additional privacy mechanisms to prevent rank-based information leakage. Additionally, integration with secure aggregation protocols and extension to vertical federated learning settings represent important directions for continued research.

---

**Word Count:** ~2,150 words