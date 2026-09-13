# Research Proposal: Adaptive Closed-Loop Protein Design via Thompson Sampling and Parameter-Efficient Model Retraining

## 1. Title

**Adaptive Closed-Loop Protein Design via Thompson Sampling and Parameter-Efficient Model Retraining: Bridging Generative ML and Experimental Biology through Continuous Learning**

## 2. Introduction

### 2.1 Background

Biomolecular design through artificial engineering of proteins, molecules, and nucleic acids represents one of the most promising frontiers in addressing critical challenges across medicine, industry, and environmental sustainability. Recent advances in generative machine learning have demonstrated remarkable potential in this domain, with models like ProteinMPNN achieving 52.4% sequence recovery rates and RFdiffusion enabling de novo protein structure generation validated through X-ray crystallography. However, a fundamental disconnect persists between computational innovation and experimental reality: most ML research efforts prioritize static benchmark performance, treating generative models as fixed artifacts that generate candidates for one-shot experimental validation without learning from the expensive feedback these experiments provide.

This disconnect manifests in severe practical inefficiencies. Current protein design workflows typically require 200-300 wet-lab experiments at $250-1000 per assay to identify optimal designs, with generative models remaining static throughout the entire experimental campaign. While recent work like MAGECS has demonstrated the value of closed-loop experimental integration—achieving 35% high-activity structure generation in materials discovery—these approaches fail to update their generative models, treating them as black-box candidate generators rather than adaptive learning systems. Similarly, standard Bayesian optimization methods applied to biomolecular design use deep generative priors only as fixed feature extractors, missing opportunities to refine chemical and structural knowledge as experimental data accumulates.

The theoretical foundations for addressing this gap exist across multiple domains. Thompson Sampling provides principled probabilistic exploration-exploitation balance with proven regret bounds of $O(\sqrt{T \log T})$ for multi-armed bandit problems. Parameter-efficient fine-tuning (PEFT) methods like LoRA enable continuous model adaptation from small datasets with 99% parameter reduction, as recently demonstrated for protein language models. Multi-fidelity optimization frameworks maximize information gain per experimental cost by strategically allocating resources between fast computational oracles (AlphaFold) and expensive wet-lab validation. However, these components have never been integrated into a unified framework that addresses the unique challenges of biomolecular design: preserving learned chemical priors during adaptation, navigating non-stationary latent spaces as models retrain, and maintaining structural validity constraints throughout iterative refinement.

### 2.2 Research Objectives

This research aims to bridge the computational-experimental divide in biomolecular design through three primary objectives:

**Objective 1: Develop an integrated closed-loop framework** that combines discounted Thompson Sampling for exploration-exploitation in generative latent spaces with parameter-efficient fine-tuning (LoRA + Bayesian regularization) to enable continuous model adaptation from experimental feedback while preserving pre-trained chemical priors.

**Objective 2: Validate sample efficiency improvements** of 30-50% compared to static generative models through systematic in-silico benchmarking on diverse protein design tasks from the FLIP dataset, followed by wet-lab experimental validation on real enzyme activity and antibody affinity optimization challenges.

**Objective 3: Establish open-source implementation and experimental protocols** that enable broad adoption across protein engineering applications, including comprehensive documentation of hyperparameter selection strategies, failure modes, and domain-specific adaptations.

The central hypothesis guiding this work posits that integrating discounted Thompson Sampling ($\gamma \in [0.9, 0.99]$) for principled probabilistic exploration with parameter-efficient fine-tuning (LoRA rank $r \in \{8, 16, 32\}$, Bayesian regularization weight $\lambda \in \{0.01, 0.1, 1.0\}$) achieves 30-50% improvement in sample efficiency—defined as the number of experimental evaluations required to reach 90% of optimal performance—compared to static ProteinMPNN baselines. This improvement operates through five linked causal mechanisms: (1) Thompson Sampling maintains posteriors over latent regions enabling probabilistic exploration, (2) LoRA enables continuous adaptation from 10-50 experimental samples without catastrophic forgetting, (3) Bayesian regularization preserves chemical priors through KL-divergence penalties, (4) discount factors adapt to non-stationary latent spaces during retraining, and (5) multi-fidelity optimization maximizes information gain per cost.

### 2.3 Significance

This research addresses critical gaps at the intersection of generative ML and experimental biology with implications spanning scientific, practical, and economic dimensions.

**Scientific Significance:** This work provides the first formalization of Thompson Sampling with parameter-efficient generative model retraining for adaptive experimental design in biomolecular discovery. By extending classical Thompson Sampling theory from discrete arms with stationary rewards to continuous latent spaces with non-stationary reward distributions induced by model retraining, we establish theoretical foundations for co-evolving model-acquisition dynamics. The integration of discounted Thompson Sampling (adapting recent advances in non-stationary multi-armed bandits) with generative model fine-tuning represents a novel contribution to both machine learning theory and computational biology.

**Practical Significance:** The proposed framework directly addresses the resource inefficiency plaguing current biomolecular design workflows. By reducing experimental budgets by 40-60% while discovering high-performers missed by static approaches, this work has immediate applications across protein engineering domains including therapeutic antibody development, enzyme optimization for industrial biocatalysis, and biomaterial design. The open-source implementation built on established frameworks (PyTorch, Hugging Face PEFT, BoTorch) ensures accessibility to researchers without extensive ML expertise, democratizing access to state-of-the-art adaptive design capabilities.

**Economic and Translational Impact:** Reducing the experimental burden from 200-300 assays to 75-120 assays translates to cost savings of $75,000-$150,000 per design campaign at typical assay costs. More critically, accelerating the design-to-validation cycle from 12-24 months to 6-9 months enables faster translation of computational innovations to real-world applications in drug discovery, sustainable manufacturing, and environmental remediation. The collaboration with Nature Biotechnology for fast-tracking exceptional submissions provides a direct pathway for high-impact dissemination to both computational and experimental communities.

**Alignment with GEM Workshop Goals:** This research directly addresses the workshop's core mission of bridging computationalists and experimentalists by: (1) advancing generative ML methodology with rigorous in-silico validation (in-silico track), (2) providing wet-lab experimental results demonstrating real-world impact (experimental track), (3) identifying biological problems (enzyme/antibody optimization) ready for ML application, and (4) establishing benchmarks and datasets for reproducible evaluation. The work exemplifies the integration of high-throughput experimentation, computational biology, and generative ML that the workshop seeks to catalyze.

## 3. Methodology

### 3.1 Overall Framework Architecture

The proposed closed-loop framework integrates five core components operating in iterative cycles:

**Component 1: Generative Model with Parameter-Efficient Fine-Tuning**
- Base architecture: Pre-trained ProteinMPNN or Chroma
- Adaptation mechanism: Low-Rank Adaptation (LoRA) with rank $r \in \{8, 16, 32\}$
- Regularization: Bayesian regularization via Laplace approximation

**Component 2: Thompson Sampling Acquisition in Latent Space**
- Posterior maintenance over latent regions
- Discounted weighting with factor $\gamma \in [0.9, 0.99]$
- Probabilistic candidate selection

**Component 3: Multi-Fidelity Oracle**
- Low-fidelity: AlphaFold structure prediction (~$1/evaluation)
- High-fidelity: Wet-lab experimental assays (~$250-1000/evaluation)
- Information gain per cost decision criterion

**Component 4: Experimental Feedback Integration**
- Batch evaluation: $B \in \{10, 20, 50\}$ candidates per round
- Data aggregation and posterior update
- Model retraining trigger

**Component 5: Chemical Validity Preservation**
- Structural constraint checking (Ramachandran plots, MolProbity scores)
- Orthogonal projection (OPLoRA) for knowledge retention
- Pre-training task performance monitoring

### 3.2 Detailed Algorithmic Design

#### 3.2.1 Generative Model with LoRA Fine-Tuning

**Base Model Initialization:**
Let $\theta_0$ denote the pre-trained ProteinMPNN parameters (approximately 500M parameters). The model defines a conditional distribution over protein sequences $s$ given backbone structure $x$:

$$P(s|x; \theta_0) = \prod_{i=1}^{L} P(s_i | s_{<i}, x; \theta_0)$$

where $L$ is sequence length and $s_i$ is the amino acid at position $i$.

**LoRA Decomposition:**
For each weight matrix $W_0 \in \mathbb{R}^{d \times k}$ in the model, we freeze $W_0$ and introduce trainable low-rank matrices:

$$W = W_0 + \Delta W = W_0 + BA$$

where $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times k}$, and rank $r \ll \min(d, k)$. This reduces trainable parameters from $dk$ to $(d+k)r$, achieving approximately 99% parameter reduction when $r=16$ for typical transformer layers.

**Bayesian Regularization via Laplace Approximation:**
The fine-tuning objective at round $t$ with experimental data $\mathcal{D}_t = \{(x_i, s_i, y_i)\}_{i=1}^{n_t}$ (structures, sequences, measured properties) is:

$$\mathcal{L}(\theta_t) = \mathcal{L}_{\text{data}}(\theta_t; \mathcal{D}_t) + \lambda \cdot \text{KL}(\theta_t || \theta_0)$$

where the data loss is:

$$\mathcal{L}_{\text{data}}(\theta_t; \mathcal{D}_t) = -\sum_{i=1}^{n_t} \log P(s_i | x_i; \theta_t) + \alpha \cdot (y_i - f(s_i))^2$$

The KL divergence term is approximated via diagonal Laplace approximation:

$$\text{KL}(\theta_t || \theta_0) \approx \frac{1}{2} (\theta_t - \theta_0)^T \text{diag}(H_0) (\theta_t - \theta_0)$$

where $H_0$ is the Hessian of the pre-training loss at $\theta_0$, approximated using Fisher information. The regularization weight $\lambda \in \{0.01, 0.1, 1.0\}$ controls the trade-off between fitting experimental data and preserving pre-trained knowledge.

**OPLoRA Orthogonal Projection:**
To provide mathematical guarantees for knowledge preservation, we apply orthogonal projection during LoRA updates. Let $U_k$ contain the top-$k$ left singular vectors of $W_0$ (capturing critical pre-trained features). The projection operator is:

$$P_{\perp} = I - U_k U_k^T$$

LoRA updates are constrained to the orthogonal complement:

$$\Delta W = P_{\perp} BA$$

This ensures that critical pre-trained directions remain unchanged, preventing catastrophic forgetting.

#### 3.2.2 Thompson Sampling in Generative Latent Space

**Latent Space Embedding:**
The generative model maps sequences to latent embeddings via the encoder:

$$z = \text{Encoder}(s; \theta_t) \in \mathbb{R}^{d_z}$$

where $d_z$ is the latent dimension (typically 512-1024 for ProteinMPNN).

**Posterior Maintenance:**
We maintain a posterior distribution over expected property values for each latent region. Using a Gaussian Process surrogate model $\mathcal{GP}(\mu(z), k(z, z'))$ with RBF kernel:

$$k(z, z') = \sigma^2 \exp\left(-\frac{||z - z'||^2}{2\ell^2}\right)$$

The posterior mean and variance after observing data $\mathcal{D}_t = \{(z_i, y_i)\}_{i=1}^{n_t}$ are:

$$\mu_t(z) = k(z)^T (K + \sigma_n^2 I)^{-1} y$$
$$\sigma_t^2(z) = k(z, z) - k(z)^T (K + \sigma_n^2 I)^{-1} k(z)$$

where $K_{ij} = k(z_i, z_j)$ and $\sigma_n^2$ is observation noise variance.

**Discounted Thompson Sampling:**
To handle non-stationarity induced by model retraining, we apply exponential discounting to past observations. At round $t$, observation $(z_i, y_i)$ from round $\tau_i$ receives weight:

$$w_i(t) = \gamma^{t - \tau_i}$$

where $\gamma \in [0.9, 0.99]$ is the discount factor. The weighted GP posterior becomes:

$$\mu_t(z) = k(z)^T (K_w + \sigma_n^2 I)^{-1} y$$

where $K_w$ has entries $K_{w,ij} = \sqrt{w_i(t) w_j(t)} \cdot k(z_i, z_j)$.

**Candidate Selection:**
At each round $t$, we sample $B$ candidates via Thompson Sampling:

1. Sample reward function from posterior: $\tilde{f} \sim \mathcal{GP}(\mu_t, \sigma_t^2)$
2. For $b = 1, \ldots, B$:
   - Sample latent vector: $z_b = \arg\max_{z \in \mathcal{Z}} \tilde{f}(z)$ via gradient ascent
   - Decode to sequence: $s_b = \text{Decoder}(z_b; \theta_t)$
3. Return candidate set $\{s_1, \ldots, s_B\}$

#### 3.2.3 Multi-Fidelity Optimization

**Information Gain per Cost Criterion:**
For each candidate $s$, we decide between low-fidelity evaluation (AlphaFold, cost $C_L = \$1$) and high-fidelity evaluation (wet-lab, cost $C_H = \$1000$) based on expected information gain:

$$\text{fidelity}(s) = \arg\max_{f \in \{L, H\}} \frac{\text{IG}_f(s)}{C_f}$$

The information gain for fidelity $f$ is:

$$\text{IG}_f(s) = H[y_f(s)] - \mathbb{E}_{y_f}[H[y_f(s) | y_f]]$$

where $H[\cdot]$ is entropy. For Gaussian posteriors:

$$\text{IG}_f(s) = \frac{1}{2} \log(1 + \sigma_t^2(z_s) / \sigma_{f}^2)$$

where $\sigma_f^2$ is the noise variance for fidelity $f$.

**Correlation Calibration:**
We maintain a calibration model relating low-fidelity predictions $\hat{y}_L$ to high-fidelity measurements $y_H$:

$$y_H = \beta_0 + \beta_1 \hat{y}_L + \epsilon, \quad \epsilon \sim \mathcal{N}(0, \sigma_{\epsilon}^2)$$

Parameters $(\beta_0, \beta_1, \sigma_{\epsilon}^2)$ are estimated from validation data and updated as high-fidelity measurements accumulate. The correlation coefficient $\rho = \text{Corr}(\hat{y}_L, y_H)$ determines multi-fidelity effectiveness (requires $\rho \geq 0.6$).

#### 3.2.4 Complete Closed-Loop Algorithm

**Algorithm 1: Adaptive Closed-Loop Protein Design**

```
Input: Pre-trained model θ₀, experimental budget N, batch size B,
       LoRA rank r, regularization λ, discount factor γ
Output: Best sequence s* and property value y*

1. Initialize:
   - θ ← θ₀
   - D ← ∅ (experimental data)
   - s* ← null, y* ← -∞

2. For round t = 1, 2, ..., T (until budget exhausted):
   
   a. Candidate Generation:
      - Fit GP surrogate: GP(μₜ, σₜ²) using discounted data D
      - Sample B candidates via Thompson Sampling:
        For b = 1 to B:
          - Sample f̃ ~ GP(μₜ, σₜ²)
          - z_b ← argmax_z f̃(z) via gradient ascent
          - s_b ← Decoder(z_b; θ)
   
   b. Multi-Fidelity Evaluation:
      - For each candidate s_b:
        - Compute IG_L/C_L and IG_H/C_H
        - If IG_L/C_L > IG_H/C_H:
            ŷ_b ← AlphaFold(s_b)
            If ŷ_b > threshold: schedule wet-lab
        - Else:
            y_b ← WetLab(s_b)
            D ← D ∪ {(z_b, y_b, t)}
   
   c. Update Best:
      - If max(y_b) > y*:
          s* ← argmax_b y_b
          y* ← max(y_b)
   
   d. Model Retraining (every K rounds, K=5):
      - Construct LoRA loss:
        L(θ) = L_data(θ; D) + λ·KL(θ||θ₀)
      - Update LoRA parameters (B, A) via Adam optimizer
      - Apply OPLoRA projection: ΔW ← P_⊥ BA
      - θ ← θ₀ + ΔW
   
   e. Validity Check:
      - Evaluate chemical validity on held-out set
      - If validity < 95%: increase λ by 2×
   
3. Return s*, y*
```

### 3.3 Experimental Design

#### 3.3.1 Phase 1: In-Silico Validation (3 months)

**Objective:** Validate sample efficiency improvements on diverse protein design benchmarks using computational oracles.

**Tasks:** Five protein design challenges from FLIP benchmark:
1. **AAV fitness:** Adeno-associated virus capsid variants for gene therapy
2. **GB1 binding:** Protein G B1 domain binding to IgG
3. **Meltome stability:** Thermal stability across diverse protein families
4. **Beta-lactamase activity:** Antibiotic resistance enzyme catalytic efficiency
5. **Fluorescence:** GFP variants with enhanced brightness

**Methods Compared:**
1. **Proposed:** TS + LoRA PEFT + multi-fidelity (full system)
2. **Baseline 1:** Static ProteinMPNN + random sampling
3. **Baseline 2:** Static ProteinMPNN + standard Bayesian optimization (Expected Improvement)
4. **Baseline 3:** Full fine-tuning (no PEFT) + BO
5. **Baseline 4:** MAGECS-style (bird swarm algorithm, no generative model)

**Oracle Configuration:**
- Low-fidelity: AlphaFold2 structure prediction + ESM-1v property prediction
- High-fidelity: Ground-truth experimental measurements from FLIP dataset
- Cost simulation: $C_L = \$1$, $C_H = \$1000$

**Hyperparameter Settings:**
- LoRA rank: $r \in \{8, 16, 32\}$ (grid search via 5-fold CV)
- Regularization: $\lambda \in \{0.01, 0.1, 1.0\}$
- Discount factor: $\gamma \in \{0.90, 0.95, 0.99\}$
- Batch size: $B \in \{10, 20, 50\}$
- Retraining frequency: Every $K=5$ rounds

**Replication:** 10 independent runs per method per task with different random seeds (5 tasks × 5 methods × 10 runs = 250 total experiments).

**Computational Resources:**
- Hardware: NVIDIA A100 GPUs (40GB memory)
- Time per run: ~4 hours (100 rounds × 2 minutes/round)
- Total compute: 250 runs × 4 hours = 1000 GPU-hours (~$3000 at cloud pricing)

#### 3.3.2 Phase 2: Wet-Lab Validation (12 months)

**Objective:** Demonstrate real-world sample efficiency improvements on experimental protein design campaigns.

**Task 1: Enzyme Activity Optimization**
- **Target:** TEM-1 β-lactamase catalytic efficiency ($k_{\text{cat}}/K_M$) for novel cephalosporin substrate
- **Baseline:** Wild-type $k_{\text{cat}}/K_M = 10^5$ M⁻¹s⁻¹
- **Goal:** Achieve $\geq 10^6$ M⁻¹s⁻¹ (10× improvement)
- **Assay:** Michaelis-Menten kinetics via UV-Vis spectroscopy
- **Cost:** $250/variant (expression + purification + kinetics)
- **Budget:** 200 variants

**Task 2: Antibody Affinity Maturation**
- **Target:** Anti-SARS-CoV-2 spike protein single-chain variable fragment (scFv)
- **Baseline:** Wild-type $K_D = 100$ nM
- **Goal:** Achieve $K_D \leq 10$ nM (10× affinity improvement)
- **Assay:** Surface plasmon resonance (SPR) binding kinetics
- **Cost:** $500/variant (expression + purification + SPR)
- **Budget:** 200 variants

**Methods Compared:**
1. **Proposed:** Full closed-loop system
2. **Baseline:** Static ProteinMPNN + standard BO (best performer from Phase 1)

**Experimental Protocol:**

**Round Structure (repeated every 2 weeks):**
1. **Computational phase (Days 1-2):**
   - Generate $B=20$ candidates via Thompson Sampling
   - AlphaFold screening: predict structures for all candidates
   - Select top 10 by multi-fidelity criterion for wet-lab

2. **Experimental phase (Days 3-14):**
   - Gene synthesis (Days 3-5): Order synthetic genes
   - Expression (Days 6-9): Transform E. coli, culture, induce
   - Purification (Days 10-12): IMAC + SEC chromatography
   - Assay (Days 13-14): Kinetic measurements (enzyme) or SPR (antibody)

3. **Model update (Day 14):**
   - Integrate experimental data into $\mathcal{D}_t$
   - Retrain LoRA parameters
   - Update GP posterior with discounting

**Quality Control:**
- Technical replicates: 3 measurements per variant
- Positive control: Wild-type sequence in each batch
- Negative control: Known inactive mutant
- Batch randomization: Blind evaluation order

**Experimental Partners:**
- Enzyme optimization: Collaboration with industrial biocatalysis lab (equipment: HPLC, UV-Vis, fermentation)
- Antibody maturation: Academic immunology core facility (equipment: Biacore SPR, protein purification)

#### 3.3.3 Evaluation Metrics

**Primary Metric: Sample Efficiency**

$$N_{90} = \min\{n : y_{\text{best}}(n) \geq 0.9 \times y_{\text{optimal}}\}$$

where $y_{\text{best}}(n)$ is the maximum observed property value after $n$ evaluations, and $y_{\text{optimal}}$ is the known optimum (from exhaustive search in Phase 1, or expert-designed sequences in Phase 2).

**Secondary Metrics:**

1. **Cumulative Regret:**
$$R(T) = \sum_{t=1}^{T} (y_{\text{optimal}} - y_{\text{best}}(t))$$

2. **Chemical Validity Rate:**
$$V(t) = \frac{1}{B} \sum_{b=1}^{B} \mathbb{1}[\text{valid}(s_b)]$$
where validity checks include:
   - Protein: Ramachandran plot outliers < 2%, MolProbity score > 1.5
   - Synthesizability: No forbidden motifs, expressible in E. coli

3. **Cost Efficiency:**
$$C_{\text{total}} = \sum_{t=1}^{T} [n_L(t) \cdot C_L + n_H(t) \cdot C_H]$$
where $n_L(t)$, $n_H(t)$ are low/high-fidelity evaluations at round $t$.

4. **Pre-training Task Retention:**
$$\Delta_{\text{recovery}} = \frac{|\text{Recovery}_0 - \text{Recovery}_T|}{\text{Recovery}_0}$$
where Recovery is sequence recovery rate on CATH protein structures.

5. **Discovery Rate:**
$$D_{\text{unique}} = \frac{|\{s : y(s) \geq 0.9 \times y_{\text{optimal}}, s \notin \mathcal{S}_{\text{baseline}}\}|}{|\{s : y(s) \geq 0.9 \times y_{\text{optimal}}\}|}$$
measuring fraction of high-performers unique to proposed method.

#### 3.3.4 Statistical Analysis Plan

**Hypothesis Testing:**

**Primary Analysis (Sample Efficiency):**
- **Test:** Paired t-test (two-tailed) comparing $N_{90}$ between proposed method and each baseline
- **Null hypothesis:** $H_0: \mu_{\text{proposed}} - \mu_{\text{baseline}} \geq -0.1 \times \mu_{\text{baseline}}$ (less than 10% improvement)
- **Alternative:** $H_A: \mu_{\text{proposed}} - \mu_{\text{baseline}} < -0.3 \times \mu_{\text{baseline}}$ (at least 30% improvement)
- **Correction:** Bonferroni correction for 3 baseline comparisons: $\alpha = 0.05/3 = 0.017$
- **Effect size:** Cohen's $d = (\mu_{\text{proposed}} - \mu_{\text{baseline}}) / \sigma_{\text{pooled}}$, expect $d > 0.8$ (large effect)

**Secondary Analyses:**

1. **Discount Factor Effect:**
   - Paired t-test: $\gamma=0.95$ vs $\gamma=1.0$ (one-tailed, directional)
   - Prediction: $\gamma=0.95$ reduces cumulative regret by $\geq 20\%$

2. **Chemical Validity:**
   - Chi-square test: validity rate at round 10 with $\lambda \geq 0.1$ vs $\lambda=0$
   - Prediction: $V_{10}(\lambda \geq 0.1) \geq 0.95$ vs $V_{10}(\lambda=0) < 0.80$

3. **Cost Efficiency:**
   - Wilcoxon signed-rank test (non-parametric): total cost comparison
   - Prediction: 40-60% cost reduction at equivalent performance

**Power Analysis:**
- Desired power: $1-\beta = 0.80$
- Significance level: $\alpha = 0.017$ (Bonferroni-corrected)
- Expected effect size: $d = 0.8$ (large)
- Required sample size: $n \geq 20$ per group (10 runs × 2 tasks provides adequate power)

**Confound Control:**

| Confound | Control Strategy | Verification |
|----------|------------------|--------------|
| Hyperparameter tuning bias | 5-fold CV on training tasks, fixed hyperparameters on test tasks | Report train/test performance separately |
| Random seed variation | 10 independent runs with different seeds | Report mean ± std, check normality via Shapiro-Wilk |
| Task selection bias | Stratified sampling across property types (binding, stability, activity) | Subgroup analysis by task category |
| Computational resources | Fixed GPU type (A100), time budget (4h/round), memory (40GB) | Monitor resource usage, report in supplement |
| Experimental batch effects | Randomized evaluation order, positive/negative controls per batch | ANOVA for batch effects, include batch as covariate if significant |

**Stopping Rules:**

1. **Futility:** If after 50% of planned evaluations, improvement < 5% with $p > 0.20$, stop Phase 2 and report negative result
2. **Harm:** If chemical validity drops below 70% at any round, stop and redesign regularization
3. **Success:** If improvement exceeds 50% with $p < 0.01$, proceed to Phase 2 with high confidence
4. **Budget:** If experimental costs exceed $120K, stop and analyze partial data

### 3.4 Implementation Details

**Software Stack:**
- **Framework:** PyTorch 2.0+ for deep learning
- **Generative Models:** ProteinMPNN (official implementation), Chroma (Generate:Biomedicines)
- **PEFT:** Hugging Face PEFT library for LoRA implementation
- **Bayesian Optimization:** BoTorch for GP surrogate models and acquisition functions
- **Structure Prediction:** AlphaFold2 (DeepMind), ESMFold (Meta AI)
- **Property Prediction:** ESM-1v (protein language model embeddings)

**Code Organization:**
```
ClosedLoopBioDesign/
├── models/
│   ├── proteinmpnn.py      # ProteinMPNN wrapper with LoRA
│   ├── chroma.py            # Chroma wrapper
│   └── peft_utils.py        # Bayesian regularization, OPLoRA
├── acquisition/
│   ├── thompson_sampling.py # Discounted TS implementation
│   └── gp_surrogate.py      # Gaussian process posterior
├── oracles/
│   ├── alphafold.py         # AlphaFold interface
│   ├── esm.py               # ESM-1v property prediction
│   └── wetlab.py            # Experimental data interface
├── optimization/
│   ├── multifidelity.py     # Information gain per cost
│   └── closed_loop.py       # Main algorithm (Algorithm 1)
├── benchmarks/
│   ├── flip_tasks.py        # FLIP dataset loaders
│   └── baselines.py         # Baseline method implementations
└── experiments/
    ├── phase1_insilico.py   # In-silico validation scripts
    └── phase2_wetlab.py     # Wet-lab experiment tracking
```

**Reproducibility:**
- All code open-sourced under MIT license on GitHub
- Docker container with frozen dependencies
- Random seeds logged for all experiments
- Hyperparameter configurations stored in YAML files
- Pre-trained model checkpoints archived on Zenodo with DOI

**Data Management:**
- Phase 1 results: CSV files with columns [round, candidate_sequence, latent_embedding, predicted_property, true_property, method, random_seed]
- Phase 2 results: ISA-Tab format with experimental metadata (expression conditions, purification protocol, assay parameters)
- Wet-lab protocols: Detailed SOPs in Markdown format
- Model checkpoints: LoRA adapter weights saved every 5 rounds

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome: Sample Efficiency Improvement**

We expect the proposed closed-loop framework to achieve **30-50% reduction in experimental evaluations** required to reach 90% of optimal performance compared to static ProteinMPNN baselines. Specifically:

- **Phase 1 (In-Silico):** Across 5 FLIP tasks, average $N_{90}$ reduction from ~150 evaluations (static ProteinMPNN + BO) to ~75-105 evaluations (proposed method), with statistical significance $p < 0.017$ (Bonferroni-corrected) and effect size Cohen's $d > 0.8$.

- **Phase 2 (Wet-Lab):** For enzyme optimization, reduce experimental budget from ~200 variants to ~120-140 variants to achieve 10× catalytic efficiency improvement. For antibody maturation, reduce from ~200 variants to ~120-140 variants to achieve 10× affinity improvement.

**Secondary Outcomes:**

1. **Chemical Validity Preservation:** Maintain $\geq 95\%$ structural validity throughout 10 retraining rounds when using Bayesian regularization ($\lambda \geq 0.1$), compared to $< 80\%$ without regularization, validated via Ramachandran plot analysis and MolProbity scores.

2. **Cost Efficiency:** Achieve **40-60% reduction in total experimental cost** through multi-fidelity optimization, translating to savings of $60,000-$90,000 per 200-evaluation campaign (from $150K to $60-90K).

3. **Discovery of Novel High-Performers:** Identify **10-20% of top-performing designs** that are unique to the closed-loop approach (not discovered by static baselines), demonstrating exploration advantages of Thompson Sampling in generative latent spaces.

4. **Pre-Training Knowledge Retention:** Limit degradation of sequence recovery on CATH protein structures to $< 5\%$ after 10 retraining rounds (e.g., from 52% to 49.4%), demonstrating effective catastrophic forgetting prevention.

5. **Convergence Speed:** Reduce cumulative regret by $\geq 20\%$ when using discounted Thompson Sampling ($\gamma=0.95$) compared to standard Thompson Sampling ($\gamma=1.0$), validating non-stationary adaptation mechanism.

**Methodological Contributions:**

1. **Theoretical Framework:** First formalization of Thompson Sampling with parameter-efficient generative model retraining for biomolecular design, extending classical TS theory to non-stationary continuous latent spaces.

2. **Open-Source Implementation:** Production-ready Python package `ClosedLoopBioDesign` with modular architecture supporting multiple generative models (ProteinMPNN, Chroma, RFdiffusion), acquisition strategies, and experimental oracles.

3. **Benchmark Datasets:** Curated experimental validation datasets for 5 protein design tasks with wet-lab ground truth, enabling reproducible evaluation and fair comparison for future methods.

4. **Experimental Protocols:** Detailed standard operating procedures for closed-loop protein design campaigns, including gene synthesis, expression, purification, and functional assays, documented for community adoption.

### 4.2 Scientific Impact

**Advancing Machine Learning Theory:**

This research extends Thompson Sampling theory from classical settings (discrete arms, stationary rewards) to a novel regime: continuous action spaces (generative latent embeddings) with non-stationary reward distributions induced by model retraining. The theoretical analysis of convergence guarantees under discounted weighting and parameter-efficient fine-tuning provides foundations for future work on co-evolving model-acquisition dynamics in adaptive experimental design.

The integration of Bayesian regularization via Laplace approximation with low-rank adaptation establishes principled methods for preserving learned priors during continuous learning from small datasets—a critical challenge across domains beyond biomolecular design, including robotics, materials science, and drug discovery.

**Bridging Computational and Experimental Biology:**

By demonstrating that generative models can continuously improve from experimental feedback while maintaining chemical validity, this work challenges the prevailing paradigm of static pre-trained models in computational biology. The framework provides a template for integrating high-throughput experimentation with adaptive ML, addressing the GEM workshop's core mission of bridging computationalists and experimentalists.

The multi-fidelity optimization component establishes principled methods for allocating resources between computational oracles (AlphaFold) and wet-lab validation, maximizing information gain per dollar spent—a critical consideration for resource-constrained academic labs and cost-conscious industrial R&D.

### 4.3 Practical Impact

**Accelerating Protein Engineering Workflows:**

The 30-50% reduction in experimental evaluations translates directly to:
- **Time savings:** 3-6 months reduction in design-to-validation cycles (from 12-24 months to 6-18 months)
- **Cost savings:** $60,000-$90,000 per design campaign
- **Increased throughput:** Enables exploration of 2-3× more design objectives within fixed budgets

These improvements have immediate applications across:
- **Therapeutic antibody development:** Faster affinity maturation for cancer immunotherapy, infectious disease treatment
- **Industrial biocatalysis:** Rapid enzyme optimization for sustainable chemical manufacturing, biofuel production
- **Biomaterial design:** Accelerated development of protein-based materials for tissue engineering, biosensors

**Democratizing Access to Adaptive Design:**

The open-source implementation built on established frameworks (PyTorch, Hugging Face, BoTorch) lowers barriers to adoption for researchers without extensive ML expertise. The modular architecture enables plug-and-play integration with existing generative models and experimental workflows, facilitating rapid deployment across diverse protein engineering applications.

Comprehensive documentation including hyperparameter selection guidelines, failure mode analysis, and domain-specific adaptations empowers practitioners to customize the framework for their specific design challenges, from small molecule drug discovery to RNA aptamer engineering.

### 4.4 Broader Impact

**Economic and Translational Implications:**

By reducing the cost and time required for biomolecular design, this work accelerates translation of computational innovations to real-world applications with societal benefit:
- **Healthcare:** Faster development of therapeutic proteins, vaccines, diagnostics
- **Sustainability:** Accelerated design of enzymes for plastic degradation, carbon capture, green chemistry
- **Food security:** Rapid engineering of crop proteins for improved nutrition, stress tolerance

The collaboration with Nature Biotechnology for fast-tracking exceptional submissions provides a direct pathway for high-impact dissemination, ensuring visibility to both academic and industrial communities.

**Advancing Responsible AI in Science:**

The rigorous experimental validation protocol, including pre-registration of hypotheses, blinded evaluation, and comprehensive data/code sharing, establishes best practices for reproducible ML research in biology. The explicit analysis of failure modes, boundary conditions, and negative results (if observed) contributes to a more honest and cumulative scientific literature.

The multi-fidelity framework's emphasis on resource efficiency aligns with principles of sustainable research, minimizing waste of expensive reagents and animal-derived materials while maximizing scientific insight per experiment.

**Educational and Community Building:**

The open-source implementation and detailed tutorials will serve as educational resources for training the next generation of researchers at the intersection of ML and biology. Workshop presentations at GEM and related venues (NeurIPS, ICML, ISMB) will catalyze community adoption and inspire follow-on research extending the framework to new domains (small molecules, RNA, materials).

The curated benchmark datasets with wet-lab ground truth address a critical gap in biomolecular ML: the lack of standardized experimental validation benchmarks. These datasets will enable fair comparison of future methods and drive progress toward more experimentally grounded computational biology.

### 4.5 Limitations and Future Directions

**Known Limitations:**

1. **Hyperparameter Sensitivity:** The framework requires tuning of discount factor $\gamma$, LoRA rank $r$, and regularization weight $\lambda$ across 2-3 orders of magnitude, which may be challenging for practitioners without ML expertise. Future work should develop adaptive hyperparameter selection strategies based on online performance monitoring.

2. **Multi-Fidelity Assumption:** The approach assumes AlphaFold predictions correlate with wet-lab outcomes ($\rho \geq 0.6$), which may not hold for all properties (e.g., cell-level phenotypes, in vivo efficacy). Extensions to alternative low-fidelity oracles (molecular dynamics, quantum chemistry) are needed.

3. **Computational Overhead:** LoRA retraining requires 1-4 hours per round on A100 GPUs, which may bottleneck rapid experimental loops. Investigating more efficient fine-tuning methods (e.g., adapter layers, prompt tuning) could reduce this overhead.

4. **Theoretical Gaps:** Convergence guarantees for discounted Thompson Sampling in non-stationary continuous action spaces are not fully established. Rigorous regret analysis under model retraining remains an open theoretical question.

**Future Research Directions:**

1. **Extension to Multi-Objective Optimization:** Adapt the framework for simultaneous optimization of multiple properties (e.g., binding affinity + stability + expressibility) using Pareto-efficient Thompson Sampling.

2. **Transfer Learning Across Design Tasks:** Investigate meta-learning approaches to transfer knowledge from completed design campaigns to new targets, reducing cold-start sample requirements.

3. **Integration with Active Learning:** Combine Thompson Sampling acquisition with uncertainty-based active learning to balance exploration of novel regions with refinement of model predictions.

4. **Application to Small Molecules and RNA:** Extend the framework beyond proteins to small molecule drug design (using generative models like Reinvent 4) and RNA aptamer engineering (using RNA-FM).

5. **Human-in-the-Loop Design:** Incorporate expert feedback and domain constraints into the acquisition strategy, enabling collaborative human-AI protein design workflows.

**Path to Clinical and Industrial Translation:**

For therapeutic applications, the framework must be extended to optimize properties relevant to drug development (pharmacokinetics, immunogenicity, manufacturability) beyond in vitro binding/activity. Partnerships with pharmaceutical companies and biotech startups will be critical for validating the approach on real drug discovery campaigns and navigating regulatory requirements.

For industrial biocatalysis, integration with high-throughput screening platforms (e.g., droplet microfluidics, robotic liquid handling) could enable closed-loop campaigns with 1000+ evaluations, potentially discovering transformative enzyme variants for sustainable manufacturing.

---

**Conclusion:**

This research addresses a critical gap at the intersection of generative machine learning and experimental biology by developing the first integrated framework for adaptive closed-loop protein design. By combining discounted Thompson Sampling, parameter-efficient fine-tuning, and multi-fidelity optimization, we expect to achieve 30-50% improvements in sample efficiency while maintaining chemical validity and discovering novel high-performers missed by static approaches. The rigorous experimental validation spanning in-silico benchmarks and wet-lab campaigns, coupled with open-source implementation and comprehensive documentation, positions this work to catalyze broad adoption across protein engineering applications and inspire future research on adaptive experimental design in biomolecular discovery.