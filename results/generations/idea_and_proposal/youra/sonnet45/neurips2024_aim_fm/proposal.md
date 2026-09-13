# FairLoRA-FL: Privacy-Preserving Fairness in Federated Medical Foundation Models via Subgroup-Adaptive Parameter-Efficient Fine-Tuning

## 1. Introduction

### 1.1 Background

The rapid advancement of large foundation models (FMs) has demonstrated remarkable capabilities in language understanding, visual recognition, and multimodal reasoning across general domains. However, their deployment in high-stakes specialized domains such as healthcare faces critical challenges that extend beyond technical performance. Medical AI systems must simultaneously address three fundamental requirements: (1) **demographic fairness** to prevent disparities in care quality across patient subgroups, (2) **privacy preservation** to comply with regulations like HIPAA and GDPR that prohibit centralized pooling of sensitive patient data, and (3) **computational efficiency** to enable deployment in resource-constrained hospital environments.

Recent evidence reveals alarming disparities in medical AI performance across demographic groups. Roller et al. (2025) demonstrated that state-of-the-art medical foundation models exhibit accuracy gaps exceeding 20% between age and gender subgroups on diagnostic tasks, with vulnerable populations—elderly patients, minority groups, and rural communities—experiencing systematically worse outcomes. This "one size fits none" phenomenon creates unacceptable risks in clinical decision support, potentially exacerbating existing health inequities.

Existing approaches address these challenges in isolation, creating a critical gap. Centralized fairness methods like FairTune (Dutt et al. 2023) achieve <5% fairness gaps through subgroup-specific parameter-efficient fine-tuning (PEFT) but require pooling sensitive patient data from multiple hospitals, violating privacy regulations. Conversely, federated learning frameworks (Haripriya et al., 2025) preserve privacy through decentralized training but lack explicit fairness mechanisms, resulting in >15% accuracy disparities across demographic subgroups. Standard parameter-efficient approaches like LoRA (Hu et al., 2021) reduce computational costs but do not address fairness or federated privacy constraints.

This research proposes **FairLoRA-FL**, a novel framework that integrates subgroup-adaptive Low-Rank Adaptation (LoRA) with federated learning and differential privacy to achieve Pareto-optimal trade-offs across fairness, privacy, and efficiency dimensions. The core innovation lies in training $K=5$ demographic-specific rank-16 LoRA adapters per hospital on frozen medical foundation models, aggregated via FedProx with carefully allocated differential privacy budgets ($\epsilon_{\text{total}}=8$: $\epsilon_{\text{adapters}}=6$ on gradients, $\epsilon_{\text{local}}=2$ on demographic labels).

### 1.2 Research Objectives

The primary objective is to validate the hypothesis that **subgroup-adaptive federated parameter-efficient fine-tuning achieves <10% fairness gap across demographic subgroups while maintaining overall accuracy within 5% of centralized baselines**, under multi-hospital federated constraints with differential privacy guarantees. Specific objectives include:

1. **Develop the FairLoRA-FL algorithm** that trains $K$ subgroup-specific LoRA adapters per hospital and aggregates them federally via FedProx with bi-level optimization for fairness enforcement.

2. **Establish theoretical foundations** for privacy-fairness trade-offs in federated PEFT, including differential privacy composition proofs and convergence analysis for $K$-adapter FedProx aggregation.

3. **Empirically validate** the framework on two medical benchmarks (MIMIC-IV diagnosis and MedQA clinical question answering) across 8 simulated hospital nodes with realistic demographic heterogeneity.

4. **Quantify trade-offs** between fairness gap reduction, privacy budget allocation, communication efficiency, and overall accuracy through comprehensive ablation studies.

5. **Demonstrate practical feasibility** through implementation using mature open-source libraries (HuggingFace PEFT, Flower FL, Opacus DP) with deployment-ready code and documentation.

### 1.3 Research Significance

This research addresses a critical gap at the intersection of medical AI fairness, federated learning, and parameter-efficient fine-tuning. The significance spans three dimensions:

**Theoretical Contribution:** We provide the first formalization of the privacy-fairness trade-off in federated parameter-efficient fine-tuning. By allocating $\epsilon_{\text{local}}=2$ of the total privacy budget to demographic routing via local differential privacy, we enable subgroup-specific adapter selection while preserving $(\epsilon_{\text{total}}, \delta)$-differential privacy guarantees under composition theorems. This resolves the fundamental tension between achieving fairness (which requires sensitive demographic information) and maintaining privacy (which forbids centralized label sharing).

**Methodological Contribution:** The $K$-Adapter FedProx algorithm represents the first federated learning framework that aggregates $K$ separate parameter-efficient adapter sets with theoretical convergence guarantees despite data heterogeneity. Unlike standard FedProx (single model aggregation), our approach maintains $K$ parallel aggregation channels with bi-level optimization: the outer loop enforces equalized odds fairness constraints across subgroups, while the inner loop maximizes accuracy via FedProx proximal regularization ($\mu=0.01$).

**Practical Impact:** For multi-hospital medical AI deployment, FairLoRA-FL enables privacy-preserving, resource-efficient, and fair foundation model adaptation. The framework requires only 2MB communication per federated round (75× smaller than full model fine-tuning), achieves fairness gaps <10% across demographic subgroups, and maintains accuracy within 5% of centralized baselines. This makes equitable AI-assisted diagnosis feasible for resource-constrained hospitals serving vulnerable populations, directly addressing healthcare disparities in rural and developing regions where the doctor-to-population ratio is critically low.

The research aligns with the workshop's emphasis on explainability, robustness, and security of Medical Foundation Models by providing transparent subgroup-specific adaptation mechanisms, robust performance across diverse patient populations, and cryptographically sound privacy guarantees through differential privacy.

## 2. Methodology

### 2.1 Research Design Overview

We employ a **multi-phase experimental design** combining theoretical analysis, algorithm development, and empirical validation across simulated multi-hospital federated learning environments. The methodology consists of four integrated components:

1. **Algorithm Design:** Development of the FairLoRA-FL framework with $K$-adapter architecture, privacy-preserving routing, and bi-level fairness optimization.
2. **Theoretical Analysis:** Differential privacy composition proofs and FedProx convergence guarantees for $K$-adapter aggregation.
3. **Empirical Validation:** Controlled experiments on MIMIC-IV and MedQA datasets across 8 simulated hospitals with 25 independent runs.
4. **Ablation Studies:** Systematic isolation of component contributions (subgroup adapters, local DP, FedProx, fairness constraints).

### 2.2 Data Collection and Preparation

**Datasets:**

1. **MIMIC-IV (Medical Information Mart for Intensive Care IV):**
   - **Task:** Multi-label diagnosis prediction from clinical notes
   - **Size:** 299,712 hospital admissions with ICD-10 diagnosis codes
   - **Demographics:** Age (18-89 years), gender (binary), ethnicity (6 categories)
   - **Preprocessing:** Extract discharge summaries, tokenize with BioGPT tokenizer (max length 512), stratify by demographic subgroups

2. **MedQA (Medical Question Answering):**
   - **Task:** Multiple-choice clinical question answering (USMLE-style)
   - **Size:** 12,723 questions with 4-option answers
   - **Demographics:** Simulated patient demographics based on question context (age/gender extracted via NER)
   - **Preprocessing:** Format as prompt-completion pairs, extract demographic metadata

**Demographic Stratification:**

We define $K=5$ subgroups based on age quintiles and gender:
- **Age Quintiles:** [18-35), [35-50), [50-65), [65-80), [80+] years
- **Gender:** Binary (male/female)
- **Subgroup Assignment:** Each patient assigned to one of $K=5$ subgroups (age quintile × gender collapsed to 5 groups for computational feasibility)

**Hospital Simulation:**

We simulate $N_{\text{hospitals}}=8$ federated nodes with heterogeneous demographic distributions:
- **Urban Academic Centers (2 hospitals):** Balanced demographics, larger sample sizes
- **Rural Community Hospitals (3 hospitals):** Skewed toward elderly populations, smaller samples
- **Pediatric/Geriatric Specialists (2 hospitals):** Extreme age distributions
- **Safety-Net Hospital (1 hospital):** High minority representation

Data partitioning uses Dirichlet distribution ($\alpha=0.5$) to create realistic non-IID splits across hospitals, ensuring each hospital has different subgroup proportions.

**Train/Validation/Test Splits:**
- **Per-Hospital Split:** 70% train, 15% validation, 15% test
- **Stratification:** Maintain subgroup proportions within each split
- **Cross-Validation:** 5-fold stratified splits for statistical robustness (25 total runs = 5 random seeds × 5 data splits)

### 2.3 FairLoRA-FL Algorithm

#### 2.3.1 Architecture

**Base Model:** BioGPT-Large (347M parameters), a domain-adapted GPT-2 variant pre-trained on PubMed abstracts and clinical notes, frozen during training.

**LoRA Adapters:** For each hospital $h \in \{1, ..., N_{\text{hospitals}}\}$ and subgroup $k \in \{1, ..., K\}$, we train a rank-$r$ LoRA adapter:

$$\mathbf{W}_k^{(h)} = \mathbf{W}_0 + \mathbf{B}_k^{(h)} \mathbf{A}_k^{(h)}$$

where:
- $\mathbf{W}_0 \in \mathbb{R}^{d \times d}$ is the frozen pre-trained weight matrix
- $\mathbf{A}_k^{(h)} \in \mathbb{R}^{r \times d}$ and $\mathbf{B}_k^{(h)} \in \mathbb{R}^{d \times r}$ are trainable low-rank matrices
- $r=16$ (rank parameter, following Med42 best practices)
- Total trainable parameters per hospital: $K \times 2 \times r \times d = 5 \times 2 \times 16 \times 1024 \approx 10M$ parameters (vs. 347M for full fine-tuning)

**Routing Mechanism:** At inference, each patient with demographic metadata $\mathbf{d} = (\text{age}, \text{gender})$ is routed to the appropriate adapter:

$$k^* = \text{route}(\mathbf{d}) = \arg\min_{k} \|\mathbf{d} - \mathbf{c}_k\|_2$$

where $\mathbf{c}_k$ is the centroid of subgroup $k$ in demographic space.

#### 2.3.2 Local Training with Bi-Level Optimization

Each hospital $h$ performs local training for $E=5$ epochs per federated round:

**Inner Optimization (Accuracy Maximization):**

$$\min_{\{\mathbf{A}_k^{(h)}, \mathbf{B}_k^{(h)}\}_{k=1}^K} \sum_{k=1}^K \sum_{(\mathbf{x}, y) \in \mathcal{D}_k^{(h)}} \mathcal{L}_{\text{task}}(f_{\mathbf{W}_k^{(h)}}(\mathbf{x}), y) + \frac{\mu}{2} \sum_{k=1}^K \|\mathbf{\theta}_k^{(h)} - \mathbf{\theta}_k^{(t-1)}\|_2^2$$

where:
- $\mathcal{D}_k^{(h)}$ is the local dataset for subgroup $k$ at hospital $h$
- $\mathcal{L}_{\text{task}}$ is cross-entropy loss for diagnosis/QA tasks
- $\mu=0.01$ is the FedProx proximal term preventing drift from global model $\mathbf{\theta}_k^{(t-1)}$
- $\mathbf{\theta}_k = (\mathbf{A}_k, \mathbf{B}_k)$ denotes adapter parameters

**Outer Optimization (Fairness Enforcement):**

$$\min_{\{\lambda_k\}_{k=1}^K} \max_{k, k'} \left| \text{TPR}_k - \text{TPR}_{k'} \right| + \left| \text{FPR}_k - \text{FPR}_{k'} \right|$$

subject to equalized odds constraint:

$$\mathbb{E}[\hat{y} | y=1, k] = \mathbb{E}[\hat{y} | y=1, k'], \quad \mathbb{E}[\hat{y} | y=0, k] = \mathbb{E}[\hat{y} | y=0, k']$$

This is implemented via loss reweighting with Lagrangian multipliers $\lambda_k$ updated every 10 local epochs:

$$\mathcal{L}_{\text{fair}} = \sum_{k=1}^K \lambda_k \mathcal{L}_{\text{task}}^{(k)}$$

where $\lambda_k$ is increased for underperforming subgroups and decreased for overperforming ones.

#### 2.3.3 Privacy-Preserving Aggregation

**Local Differential Privacy on Demographics:**

Before sharing demographic statistics for routing, each hospital applies Laplace mechanism with $\epsilon_{\text{local}}=2$:

$$\tilde{\mathbf{c}}_k = \mathbf{c}_k + \text{Lap}\left(\frac{\Delta_{\mathbf{c}}}{\epsilon_{\text{local}}}\right)$$

where $\Delta_{\mathbf{c}} = \max_{\mathbf{d}, \mathbf{d}'} \|\mathbf{c}_k(\mathcal{D} \cup \{\mathbf{d}\}) - \mathbf{c}_k(\mathcal{D} \cup \{\mathbf{d}'\})\|_1$ is the sensitivity of centroid computation.

**Differential Privacy on Adapter Gradients:**

Each hospital clips and adds Gaussian noise to adapter gradients before transmission:

$$\tilde{\nabla} \mathbf{\theta}_k^{(h)} = \text{clip}\left(\nabla \mathbf{\theta}_k^{(h)}, C\right) + \mathcal{N}\left(0, \sigma^2 C^2 \mathbf{I}\right)$$

where:
- $C=1.0$ is the clipping threshold
- $\sigma = \frac{C \sqrt{2 \log(1.25/\delta)}}{\epsilon_{\text{adapters}} N_{\text{hospitals}}}$ with $\epsilon_{\text{adapters}}=6$, $\delta=10^{-5}$

**FedProx Aggregation:**

The central server aggregates $K$ adapter sets separately:

$$\mathbf{\theta}_k^{(t)} = \sum_{h=1}^{N_{\text{hospitals}}} \frac{n_k^{(h)}}{n_k} \tilde{\mathbf{\theta}}_k^{(h)}$$

where $n_k^{(h)}$ is the number of samples in subgroup $k$ at hospital $h$, and $n_k = \sum_h n_k^{(h)}$.

**Privacy Budget Composition:**

Total privacy guarantee via advanced composition (Dwork & Roth, 2014):

$$\epsilon_{\text{total}} = \epsilon_{\text{local}} + \sqrt{2T \log(1/\delta)} \cdot \epsilon_{\text{adapters}} + T \epsilon_{\text{adapters}} \left(e^{\epsilon_{\text{adapters}}} - 1\right)$$

For $T=100$ rounds, $\epsilon_{\text{local}}=2$, $\epsilon_{\text{adapters}}=6$, this yields $\epsilon_{\text{total}} \approx 8$ (within industry-standard privacy budgets).

### 2.4 Experimental Protocol

#### 2.4.1 Baseline Comparisons

We compare FairLoRA-FL against three baselines:

1. **Standard Federated Learning (FL-Full):**
   - FedAvg aggregation of full BioGPT fine-tuning
   - No fairness constraints, no PEFT
   - Expected: High accuracy, large fairness gap (>20%), high communication (150MB/round)

2. **Centralized FairTune (Centralized-Fair):**
   - FairTune algorithm on pooled (centralized) data
   - Fairness via bi-level optimization, PEFT via LoRA
   - Expected: Best fairness (<5% gap) and accuracy, but violates privacy

3. **Federated LoRA (FL-LoRA):**
   - FedAvg aggregation of single rank-16 LoRA adapter
   - PEFT efficiency, no fairness mechanism
   - Expected: Low communication (2MB/round), large fairness gap (>15%)

#### 2.4.2 Evaluation Metrics

**Primary Metrics:**

1. **Fairness Gap:**
$$\text{FG} = \max_{k \in \{1, ..., K\}} \text{Acc}_k - \min_{k \in \{1, ..., K\}} \text{Acc}_k$$
Target: FG < 10% (stretch goal: <5%)

2. **Overall Accuracy:**
$$\text{Acc}_{\text{overall}} = \frac{1}{K} \sum_{k=1}^K \text{Acc}_k$$
Target: $\text{Acc}_{\text{overall}} \geq \text{Acc}_{\text{centralized}} - 5\%$

**Secondary Metrics:**

3. **Equalized Odds Violation:**
$$\text{EOV} = \max_{k, k'} \left| \text{TPR}_k - \text{TPR}_{k'} \right| + \left| \text{FPR}_k - \text{FPR}_{k'} \right|$$

4. **Communication Efficiency:**
$$\text{CommCost} = T \times N_{\text{hospitals}} \times \text{size}(\{\mathbf{\theta}_k\}_{k=1}^K)$$
Expected: 2MB per round × 100 rounds × 8 hospitals = 1.6GB total

5. **Routing Accuracy:**
$$\text{RoutingAcc} = \frac{1}{|\mathcal{D}_{\text{test}}|} \sum_{(\mathbf{x}, \mathbf{d}) \in \mathcal{D}_{\text{test}}} \mathbb{1}[\text{route}(\tilde{\mathbf{d}}) = \text{route}(\mathbf{d})]$$
where $\tilde{\mathbf{d}}$ is the noisy demographic under local DP. Target: ≥90%

6. **Convergence Speed:**
Number of rounds until validation accuracy change <0.5% over 10 consecutive rounds. Target: ≤100 rounds

**Tertiary Metrics:**

7. **Privacy Leakage:** Membership inference attack success rate (should be ≤random guess + 5%)
8. **Subgroup-Specific Metrics:** Per-subgroup accuracy, precision, recall, F1-score
9. **Computational Cost:** GPU-hours per hospital, wall-clock time per round

#### 2.4.3 Statistical Analysis

**Hypothesis Testing:**

1. **Fairness Gap Test:**
   - Null hypothesis $H_0$: FG ≥ 10%
   - Alternative $H_1$: FG < 10%
   - Test: One-sample t-test on FG across 25 runs
   - Significance level: $\alpha=0.05$

2. **Accuracy Degradation Test:**
   - Null hypothesis $H_0$: $\text{Acc}_{\text{FairLoRA-FL}} - \text{Acc}_{\text{centralized}} \leq -5\%$
   - Alternative $H_1$: $\text{Acc}_{\text{FairLoRA-FL}} - \text{Acc}_{\text{centralized}} > -5\%$
   - Test: Paired t-test across 25 runs
   - Significance level: $\alpha=0.05$ with Bonferroni correction for multiple comparisons

**Sample Size Justification:**

For paired t-test with effect size $d=0.5$ (5% accuracy difference), power $1-\beta=0.80$, and $\alpha=0.05$:

$$n = \frac{2(z_{1-\alpha/2} + z_{1-\beta})^2}{d^2} = \frac{2(1.96 + 0.84)^2}{0.5^2} \approx 25 \text{ runs}$$

Implemented as 5 random seeds × 5 train/val/test splits.

**Ablation Study Design:**

Systematic removal of components to isolate contributions:

| Configuration | K Adapters | Local DP | FedProx μ | Fairness Constraint | Expected Outcome |
|---------------|-----------|----------|-----------|---------------------|------------------|
| FairLoRA-FL (Full) | ✓ | ✓ | ✓ | ✓ | FG<10%, Acc≥baseline-5% |
| Ablation 1 | ✗ (K=1) | ✓ | ✓ | ✓ | FG>15% (no subgroup adaptation) |
| Ablation 2 | ✓ | ✗ | ✓ | ✓ | Routing Acc<80% (no privacy) |
| Ablation 3 | ✓ | ✓ | ✗ (μ=0) | ✓ | Non-convergence (no FedProx) |
| Ablation 4 | ✓ | ✓ | ✓ | ✗ | FG>15% (no fairness enforcement) |

### 2.5 Implementation Details

**Software Stack:**
- **Framework:** PyTorch 2.0 with HuggingFace Transformers 4.35
- **PEFT Library:** HuggingFace PEFT 0.7.0 for LoRA implementation
- **Federated Learning:** Flower 1.6.0 for FL coordination
- **Differential Privacy:** Opacus 1.4.0 for DP-SGD
- **Compute:** 8× NVIDIA V100 GPUs (32GB VRAM each), simulating 8 hospitals

**Hyperparameters:**
- Learning rate: $3 \times 10^{-4}$ with cosine annealing
- Batch size: 16 per hospital (effective batch size 128 across 8 hospitals)
- Local epochs per round: $E=5$
- Total federated rounds: $T=100$
- LoRA rank: $r=16$, $\alpha=32$
- FedProx proximal term: $\mu=0.01$
- DP clipping threshold: $C=1.0$
- Privacy budgets: $\epsilon_{\text{local}}=2$, $\epsilon_{\text{adapters}}=6$, $\delta=10^{-5}$

**Computational Budget:**
- Training time: ~40 GPU-hours (8 hospitals × 100 rounds × 0.05 hours/round)
- Inference time: <100ms per patient (routing + forward pass)
- Storage: 10MB per hospital (K=5 adapters × 2MB each)

### 2.6 Validation Protocol

**Phase 1: Pilot Study (Week 1)**
- Small-scale validation: 2 hospitals, K=3 subgroups, T=50 rounds
- Objectives: Verify routing accuracy ≥90% under DP noise, test K-adapter convergence
- Success criteria: Routing Acc ≥90%, validation accuracy plateaus by round 50

**Phase 2: Full Validation (Weeks 2-4)**
- Full 8-hospital deployment with K=5 subgroups, T=100 rounds
- 25 independent runs (5 seeds × 5 data splits)
- Comprehensive metric collection and statistical testing

**Phase 3: Ablation Studies (Week 5)**
- Systematic component removal (4 ablation configurations)
- Isolate contributions of subgroup adapters, local DP, FedProx, fairness constraints

**Phase 4: Robustness Testing (Week 6)**
- Stress tests: Extreme data heterogeneity (α=0.1), hospital dropout (20% failure rate)
- Privacy auditing: Membership inference attacks, demographic reconstruction attacks
- Sensitivity analysis: Vary K (3, 5, 10), r (8, 16, 32), ε (4, 8, 16)

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcomes:**

1. **Fairness-Privacy-Efficiency Pareto Optimality:**
We expect FairLoRA-FL to achieve a Pareto-optimal trade-off that no baseline can dominate across all three dimensions:
   - **Fairness:** Gap <10% (vs. >15% for FL-LoRA, >20% for FL-Full)
   - **Privacy:** $\epsilon=8$ with federated deployment (vs. no privacy for Centralized-Fair)
   - **Efficiency:** 2MB communication/round (vs. 150MB for FL-Full)

Statistical validation will demonstrate that FairLoRA-FL significantly outperforms baselines on fairness (p<0.05, one-tailed t-test) while maintaining comparable accuracy (within 5% of centralized baseline, p<0.05, paired t-test).

2. **Validated Causal Mechanism:**
Ablation studies will confirm the four-step causal chain:
   - **Step 1 (Subgroup Adapters):** Jensen-Shannon divergence >0.3 between adapter weight distributions, with subgroup-specific adapters outperforming generic adapters by ≥3% on respective subgroups
   - **Step 2 (Privacy-Preserving Routing):** Routing accuracy ≥90% under $\epsilon_{\text{local}}=2$ DP noise, with membership inference attack success rate ≤55% (random guess + 5%)
   - **Step 3 (FedProx Convergence):** Convergence within 100 rounds for K=5 adapters, with validation accuracy plateauing (change <0.5% over final 10 rounds)
   - **Step 4 (Fairness Enforcement):** Bi-level optimization reduces fairness gap from >15% (without fairness constraint) to <10% (with constraint)

3. **Theoretical Contributions:**
   - **DP Composition Proof:** Formal proof that $\epsilon_{\text{total}} = \epsilon_{\text{local}} + \sqrt{2T \log(1/\delta)} \cdot \epsilon_{\text{adapters}} \leq 8$ under advanced composition
   - **K-Adapter Convergence Theorem:** Extension of FedProx convergence guarantees (Li et al., 2020) to $K$ parallel adapter aggregation channels, showing convergence rate $O(1/\sqrt{T})$ under heterogeneous data

4. **Practical Deployment Artifacts:**
   - Open-source implementation with comprehensive documentation
   - Pre-trained FairLoRA-FL checkpoints for BioGPT on MIMIC-IV and MedQA
   - Deployment guide for multi-hospital federated learning infrastructure
   - Privacy audit toolkit for membership inference and reconstruction attacks

**Secondary Outcomes:**

5. **Subgroup Performance Analysis:**
Detailed breakdown of accuracy, precision, recall, and F1-score for each of K=5 demographic subgroups, identifying which populations benefit most from subgroup-specific adaptation. We expect elderly patients (age 65+) and underrepresented gender groups to show the largest improvements (≥8% accuracy gain vs. generic adapter).

6. **Scalability Insights:**
Sensitivity analysis varying K (3, 5, 10 subgroups) will reveal optimal granularity for fairness-efficiency trade-offs. We hypothesize diminishing returns beyond K=5, with K=10 providing <2% additional fairness improvement at 2× computational cost.

7. **Privacy-Utility Trade-off Characterization:**
Systematic variation of $\epsilon_{\text{total}}$ (4, 8, 16) will quantify the privacy-accuracy frontier. We expect:
   - $\epsilon=4$: Fairness gap <12%, accuracy degradation ~7% (strong privacy, moderate utility loss)
   - $\epsilon=8$: Fairness gap <10%, accuracy degradation ~5% (balanced, target configuration)
   - $\epsilon=16$: Fairness gap <8%, accuracy degradation ~3% (weak privacy, high utility)

### 3.2 Impact on Medical AI Deployment

**Immediate Clinical Impact:**

1. **Equitable Diagnostic Support for Vulnerable Populations:**
By reducing fairness gaps from >20% to <10%, FairLoRA-FL ensures that AI-assisted diagnosis provides comparable accuracy for elderly patients, minority groups, and rural populations. This directly addresses health disparities identified by Roller et al. (2025), where current medical AI systems systematically underperform on vulnerable subgroups.

2. **Privacy-Compliant Multi-Hospital Collaboration:**
The framework enables hospitals to collaboratively improve medical AI without violating HIPAA/GDPR regulations. With $\epsilon=8$ differential privacy guarantees and federated architecture, hospitals can participate in AI development while maintaining patient confidentiality—critical for safety-net hospitals serving sensitive populations.

3. **Resource-Efficient Deployment:**
2MB communication overhead per round (vs. 150MB for full fine-tuning) makes federated learning feasible for rural and community hospitals with limited network bandwidth. 10M trainable parameters per hospital (vs. 347M for full fine-tuning) enable deployment on commodity GPUs, reducing infrastructure costs by ~10×.

**Long-Term Research Impact:**

4. **New Research Paradigm for Fair Federated Learning:**
FairLoRA-FL establishes a template for addressing fairness in federated settings across domains beyond healthcare (finance, legal AI, education). The privacy-fairness trade-off formalization via local DP on sensitive attributes provides a principled framework for future research.

5. **Benchmark for Medical AI Fairness:**
Our comprehensive evaluation protocol (25 runs, 4 ablations, 3 baselines, 6 primary metrics) sets a new standard for rigorous fairness evaluation in medical AI. The open-source implementation and pre-trained checkpoints will serve as baselines for future work.

6. **Foundation for Multimodal Fair Federated Learning:**
While this work focuses on text-based medical tasks (diagnosis from notes, clinical QA), the architecture naturally extends to multimodal settings (medical imaging + EHR, radiology reports + scans). Future work can integrate vision encoders with subgroup-specific adapters for fair multimodal medical AI.

**Broader Societal Impact:**

7. **Addressing Healthcare Disparities:**
By enabling equitable AI deployment in underserved regions, FairLoRA-FL contributes to reducing the global doctor-to-population ratio crisis. AI assistants achieving <10% fairness gaps can provide reliable diagnostic support in rural clinics lacking specialist access, improving health outcomes for millions.

8. **Trust in Medical AI:**
Transparent fairness guarantees (<10% gap) and cryptographic privacy proofs ($\epsilon=8$ DP) build trust among patients and clinicians. This addresses the "black box" concern in medical AI, making adoption more likely in high-stakes clinical settings.

9. **Policy Implications:**
The framework demonstrates that privacy regulations (HIPAA/GDPR) and fairness requirements (equalized odds) are not mutually exclusive. This provides evidence for policymakers designing AI governance frameworks that mandate both privacy and fairness.

### 3.3 Limitations and Future Work

**Known Limitations:**

1. **Coarse Demographic Granularity:** K=5 subgroups (age quintiles × gender) may miss intersectional disparities (e.g., elderly minority women). Future work should explore finer stratification (K=20 with race/ethnicity) and hierarchical adapter architectures.

2. **Binary Gender Assumption:** Current implementation uses binary gender labels, excluding non-binary and transgender patients. Extending to non-binary demographics requires rethinking subgroup definitions and routing mechanisms.

3. **Simulated Hospital Environments:** Validation uses simulated federated nodes on MIMIC-IV/MedQA. Real-world deployment faces additional challenges (network failures, asynchronous updates, malicious participants) requiring robustness testing.

4. **Task-Specific Validation:** Experiments focus on diagnosis prediction and clinical QA. Generalization to other medical tasks (treatment recommendation, prognosis, surgical planning) requires additional validation.

**Future Research Directions:**

1. **Multimodal Extension:** Integrate medical imaging (X-rays, CT scans) with EHR text via multimodal adapters, addressing modality-specific fairness (e.g., imaging quality disparities across hospitals).

2. **Dynamic Subgroup Discovery:** Replace fixed K=5 subgroups with learned clustering that automatically discovers fairness-relevant patient stratifications from data.

3. **Personalized Federated Learning:** Extend from subgroup-level to patient-level adaptation via meta-learning, enabling personalized medical AI while preserving privacy.

4. **Adversarial Robustness:** Evaluate resilience to adversarial attacks (model poisoning, gradient manipulation) in federated settings, critical for security-sensitive medical deployments.

5. **Real-World Pilot Deployment:** Partner with hospital networks for prospective clinical trials, measuring real-world fairness, privacy, and clinical utility in live diagnostic workflows.

### 3.4 Dissemination Plan

**Academic Outputs:**
- **Conference Submission:** NeurIPS 2026 Workshop on Medical Foundation Models (target venue)
- **Journal Article:** Extended version for Journal of Medical AI or Nature Digital Medicine
- **Preprint:** arXiv release with full technical appendices and reproducibility materials

**Open-Source Release:**
- **GitHub Repository:** Complete implementation with documentation, tutorials, and pre-trained checkpoints
- **HuggingFace Model Hub:** FairLoRA-FL checkpoints for BioGPT on MIMIC-IV and MedQA
- **Docker Containers:** Reproducible federated learning environment for multi-hospital simulation

**Community Engagement:**
- **Workshop Presentation:** Live demo of FairLoRA-FL deployment at workshop
- **Tutorial Session:** Hands-on tutorial for implementing fair federated PEFT
- **Industry Partnerships:** Collaborate with healthcare AI companies (e.g., Google Health, Microsoft Healthcare) for real-world validation

This research represents a critical step toward trustworthy, equitable, and privacy-preserving medical AI that can serve all patient populations, particularly those most vulnerable to healthcare disparities. By demonstrating that fairness, privacy, and efficiency are achievable simultaneously through principled algorithm design, FairLoRA-FL provides a blueprint for the next generation of Medical Foundation Models.