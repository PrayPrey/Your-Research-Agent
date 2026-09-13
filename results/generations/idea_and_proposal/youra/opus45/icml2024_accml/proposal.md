# Research Proposal: BioHomeoAL: Homeostatic Active Learning for Resource-Efficient Biological Foundation Model Adaptation

## 1. Introduction

### 1.1 Background

Foundation models have revolutionized machine learning across numerous domains, and their application to biological discovery holds transformative potential. Models such as ESM-2 for protein sequences and DNABERT-2 for genomic data encode rich representations of biological knowledge learned from vast unlabeled datasets. These representations can be leveraged for downstream tasks including protein fitness prediction, drug-target binding affinity estimation, and genomic variant effect prediction. However, a significant gap exists between the capabilities of these large models and their practical adoption in wet laboratory settings.

The primary barriers to adoption are threefold. First, **computational resource constraints**: most biological research laboratories operate with modest computational infrastructure—typically a single high-end GPU rather than the extensive clusters required for full fine-tuning of billion-parameter models. Second, **labeled data scarcity**: obtaining experimental labels in biology is expensive, time-consuming (days to weeks per experimental cycle), and often limited by reagent costs and throughput constraints. Third, **methodological fragmentation**: current approaches treat model adaptation, sample selection for labeling, and resource management as separate optimization problems, leading to suboptimal overall efficiency.

Active learning offers a principled framework for reducing labeling costs by iteratively selecting the most informative samples for experimental validation. Meanwhile, parameter-efficient fine-tuning methods such as Low-Rank Adaptation (LoRA) enable foundation model adaptation with orders of magnitude fewer trainable parameters. However, these techniques have not been unified within a coherent framework that addresses the unique constraints of biological discovery workflows.

### 1.2 Research Objectives

This research proposes **BioHomeoAL**, a bio-inspired framework that treats model epistemic uncertainty as a homeostatic feedback signal to coordinate foundation model adaptation for biological discovery. Drawing inspiration from biological homeostasis—where organisms maintain stable internal states through negative feedback mechanisms—we formalize a control-theoretic approach that dynamically balances model capacity allocation, sample selection, and resource utilization.

The primary objectives are:

1. **Develop a unified framework** that integrates uncertainty quantification, adaptive parameter-efficient fine-tuning, and multi-objective sample selection within a homeostatic control loop.

2. **Demonstrate sample efficiency improvements** of ≥30% compared to random sampling baselines across multiple biological modalities (protein fitness, drug binding, genomics).

3. **Validate the homeostatic stability hypothesis** by showing that the feedback-based approach achieves lower performance variance than standard active learning methods.

4. **Provide accessible implementation** suitable for resource-constrained biology laboratories with single-GPU computational setups.

### 1.3 Significance

This research directly addresses the workshop's central theme of bridging the accessibility and efficiency gap between ML research and wet lab use. By reducing experimental costs by 30-50% while maintaining task performance, BioHomeoAL can democratize access to foundation model capabilities for laboratories that cannot afford extensive computational resources or large-scale experimental campaigns. The bio-inspired control-theoretic framework provides principled guidance for the "lab in the loop" paradigm, enabling iterative refinement of ML models based on experimental results within realistic resource constraints.

---

## 2. Methodology

### 2.1 Framework Overview

BioHomeoAL operates through a 5-step homeostatic control loop that coordinates model adaptation and sample selection:

**Step 1: Uncertainty Measurement.** Quantify model epistemic uncertainty using Monte Carlo (MC) Dropout or Deep Ensembles.

**Step 2: Feedback Signal Generation.** Transform uncertainty measurements into control signals that modulate model adaptation parameters.

**Step 3: Adaptive LoRA Configuration.** Dynamically adjust LoRA rank and learning rate based on uncertainty feedback.

**Step 4: Parameter-Efficient Model Update.** Fine-tune the foundation model using the adapted LoRA configuration.

**Step 5: Multi-Objective Sample Selection.** Select the next batch of samples for experimental labeling using Pareto-optimized acquisition.

### 2.2 Uncertainty Quantification

We employ MC Dropout for computational efficiency, with Deep Ensembles as a validation alternative. For a foundation model $f_\theta$ with dropout applied during inference, we compute $n=50$ stochastic forward passes for each unlabeled sample $x$:

$$\hat{y}_i = f_\theta(x; \text{dropout}_i), \quad i = 1, \ldots, n$$

The epistemic uncertainty is quantified as the normalized predictive entropy:

$$U(x) = -\sum_{c} \bar{p}_c \log \bar{p}_c$$

where $\bar{p}_c = \frac{1}{n}\sum_{i=1}^{n} p_c^{(i)}$ is the mean predicted probability for class $c$ across MC samples. For regression tasks, we use the coefficient of variation:

$$U(x) = \frac{\sigma(\hat{y})}{\mu(\hat{y})}$$

where $\sigma(\hat{y})$ and $\mu(\hat{y})$ are the standard deviation and mean of predictions across MC samples.

### 2.3 Adaptive LoRA Configuration

LoRA introduces low-rank decomposition matrices to adapt pretrained weights. For a weight matrix $W_0 \in \mathbb{R}^{d \times k}$, LoRA parameterizes the update as:

$$W = W_0 + \Delta W = W_0 + BA$$

where $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times k}$, and $r \ll \min(d, k)$ is the rank.

**Uncertainty-Driven Rank Selection.** We introduce adaptive rank modulation based on the aggregate uncertainty of the current labeled dataset. Let $\bar{U}_t$ denote the mean uncertainty at iteration $t$:

$$r_t = \begin{cases}
8 & \text{if } \bar{U}_t < \tau_{\text{low}} \\
16 & \text{if } \tau_{\text{low}} \leq \bar{U}_t < \tau_{\text{high}} \\
32 & \text{if } \bar{U}_t \geq \tau_{\text{high}}
\end{cases}$$

where $\tau_{\text{low}} = 0.3$ and $\tau_{\text{high}} = 0.7$ are uncertainty thresholds (normalized to [0,1]). High uncertainty indicates the model requires more adaptation capacity (higher rank), while low uncertainty suggests efficient adaptation with minimal parameters.

**Learning Rate Modulation.** The learning rate is similarly adapted:

$$\eta_t = \eta_{\text{base}} \cdot (1 + \alpha \cdot \bar{U}_t)$$

where $\eta_{\text{base}}$ is the base learning rate and $\alpha = 0.5$ is a scaling factor. This allows more aggressive updates when uncertainty is high.

### 2.4 Multi-Objective Acquisition Function

Sample selection balances three objectives: informativeness (uncertainty), diversity, and experimental cost. We define the acquisition score for sample $x$ as:

$$A(x) = U(x)^\beta \cdot D(x)^\gamma \cdot C(x)^{-\delta}$$

where:
- $U(x)$ is the normalized uncertainty score
- $D(x)$ is the diversity score computed as the minimum distance to already-selected samples in embedding space
- $C(x)$ is the normalized experimental cost (e.g., synthesis difficulty, assay complexity)
- $\beta, \gamma, \delta$ are weighting exponents (default: $\beta=1, \gamma=0.5, \delta=0.3$)

**Batch Selection via Pareto Optimization.** For batch selection of size $B$, we employ a greedy Pareto-based approach:

1. Compute $(U(x), D(x), C(x)^{-1})$ for all unlabeled samples
2. Identify the Pareto frontier of non-dominated solutions
3. Select the top-$B$ samples from the frontier using the composite score $A(x)$
4. Update diversity scores after each selection to maintain batch diversity

The diversity score is computed using the foundation model's embedding space:

$$D(x) = \min_{x' \in S_{\text{selected}}} \|e(x) - e(x')\|_2$$

where $e(\cdot)$ denotes the foundation model's embedding function and $S_{\text{selected}}$ is the set of already-selected samples.

### 2.5 Homeostatic Control Loop Algorithm

The complete BioHomeoAL algorithm is presented below:

**Algorithm 1: BioHomeoAL**

**Input:** Foundation model $f_\theta$, initial labeled set $\mathcal{D}_0$, unlabeled pool $\mathcal{U}$, budget $T$ iterations, batch size $B$

**Output:** Adapted model $f_{\theta^*}$, final labeled set $\mathcal{D}_T$

1. Initialize LoRA parameters with rank $r_0 = 16$
2. **for** $t = 1$ to $T$ **do**
3. $\quad$ // Step 1: Uncertainty Measurement
4. $\quad$ Compute $U(x)$ for all $x \in \mathcal{U}$ using MC Dropout ($n=50$)
5. $\quad$ // Step 2: Feedback Signal
6. $\quad$ Compute aggregate uncertainty $\bar{U}_t = \frac{1}{|\mathcal{U}|}\sum_{x \in \mathcal{U}} U(x)$
7. $\quad$ // Step 3: Adaptive LoRA Configuration
8. $\quad$ Update rank $r_t$ based on $\bar{U}_t$ using threshold rules
9. $\quad$ Update learning rate $\eta_t = \eta_{\text{base}} \cdot (1 + \alpha \cdot \bar{U}_t)$
10. $\quad$ Reinitialize LoRA matrices if rank changed
11. $\quad$ // Step 4: Model Update
12. $\quad$ Fine-tune $f_\theta$ on $\mathcal{D}_{t-1}$ using LoRA with $(r_t, \eta_t)$
13. $\quad$ // Step 5: Sample Selection
14. $\quad$ Compute acquisition scores $A(x)$ for all $x \in \mathcal{U}$
15. $\quad$ Select batch $\mathcal{B}_t$ of size $B$ via Pareto optimization
16. $\quad$ // Experimental labeling (simulated or real)
17. $\quad$ Obtain labels $y$ for $\mathcal{B}_t$
18. $\quad$ Update $\mathcal{D}_t = \mathcal{D}_{t-1} \cup \{(\mathcal{B}_t, y)\}$
19. $\quad$ Update $\mathcal{U} = \mathcal{U} \setminus \mathcal{B}_t$
20. **end for**
21. **return** $f_{\theta^*}$, $\mathcal{D}_T$

### 2.6 Experimental Design

#### 2.6.1 Datasets and Tasks

We evaluate BioHomeoAL across three biological modalities:

**Protein Fitness Prediction:**
- Dataset: ProteinGym benchmark (deep mutational scanning datasets)
- Foundation Model: ESM-2 (650M parameters)
- Task: Predict fitness scores for protein variants
- Metric: Spearman correlation ($\rho$), target $\rho \geq 0.7$

**Drug-Target Binding Affinity:**
- Dataset: MoleculeNet (Davis, KIBA kinase binding datasets)
- Foundation Model: ChemBERTa-2 for molecules, ESM-2 for targets
- Task: Predict binding affinity (regression) or activity (classification)
- Metric: AUROC for classification, RMSE for regression, target AUROC $\geq 0.8$

**Genomic Variant Effect:**
- Dataset: Genomic Benchmarks (regulatory element prediction)
- Foundation Model: DNABERT-2
- Task: Predict variant effects on gene expression
- Metric: Mean Absolute Error (MAE), target $\leq 15\%$ of baseline

#### 2.6.2 Baselines

We compare against the following methods:

1. **Random Sampling:** Uniform random selection of samples
2. **Uncertainty Sampling:** Select samples with highest uncertainty (entropy)
3. **BALD:** Bayesian Active Learning by Disagreement
4. **BatchBALD:** Batch-mode BALD with diversity
5. **Fixed-Rank LoRA + Uncertainty:** Standard LoRA ($r=16$) with uncertainty sampling

#### 2.6.3 Evaluation Metrics

**Primary Metric - Area Under Learning Curve (AULC):**

$$\text{AULC} = \frac{1}{T} \sum_{t=1}^{T} P_t$$

where $P_t$ is the task performance at iteration $t$. Higher AULC indicates better sample efficiency.

**Secondary Metrics:**
- **Sample Efficiency Ratio:** $\text{SER} = \frac{\text{AULC}_{\text{method}}}{\text{AULC}_{\text{random}}}$
- **Convergence Speed:** Iterations to reach 90% of final performance
- **Performance Variance:** $\text{Var}(P_t)$ across iterations (stability measure)
- **Computational Cost:** GPU-hours per active learning cycle

#### 2.6.4 Experimental Protocol

1. **Data Splitting:** 10% initial labeled set, 70% unlabeled pool, 20% held-out test set
2. **Active Learning Cycles:** $T=50$ iterations with batch size $B=10$
3. **Repetitions:** 20 independent runs per condition with different random seeds
4. **Statistical Testing:** Paired t-tests with Bonferroni correction ($\alpha = 0.0125$)
5. **Effect Size:** Report Cohen's $d$ for all comparisons

#### 2.6.5 Ablation Studies

To validate the causal mechanism, we conduct ablations:

1. **A1: Fixed vs. Adaptive LoRA:** Compare adaptive rank selection against fixed ranks ($r \in \{8, 16, 32\}$)
2. **A2: Acquisition Components:** Ablate uncertainty, diversity, and cost terms individually
3. **A3: Uncertainty Methods:** Compare MC Dropout vs. Deep Ensembles
4. **A4: Feedback Sensitivity:** Vary uncertainty thresholds $\tau_{\text{low}}, \tau_{\text{high}}$

#### 2.6.6 Computational Requirements

All experiments are designed to run on a single NVIDIA RTX 4090 (24GB VRAM):
- ESM-2 (650M) with LoRA: ~8GB VRAM
- MC Dropout inference ($n=50$): ~2 hours per AL cycle
- Total experiment time: ~100 GPU-hours per task

### 2.7 Implementation Details

The framework integrates:
- **HuggingFace Transformers + PEFT:** Foundation models and LoRA implementation
- **TorchUncertainty:** MC Dropout and ensemble uncertainty quantification
- **DeepChem:** Molecular featurization and baseline active learning pipelines

Code will be released under MIT license with documentation for wet lab users.

---

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1):** We expect BioHomeoAL to achieve ≥30% improvement in sample efficiency (AULC) compared to random sampling across all three biological modalities. Based on prior work showing 79% improvement in out-of-distribution settings with uncertainty-guided active learning, a 30% improvement represents a conservative estimate accounting for task-dependent variation.

**Secondary Outcomes:**
- **P2 (Adaptive LoRA Value):** Adaptive rank selection will provide ≥10% AULC improvement over fixed-rank LoRA, demonstrating the value of uncertainty-driven capacity modulation.
- **P3 (Homeostatic Stability):** Performance variance will be ≤50% of standard active learning methods, validating the stabilizing effect of the feedback control mechanism.
- **P4 (Task Generalization):** Meaningful improvements (>20% AULC gain) on at least 2 of 3 biological modalities, establishing BioHomeoAL as a general framework rather than task-specific solution.

### 3.2 Potential Challenges and Mitigations

**Challenge 1: Uncertainty Calibration.** MC Dropout may produce poorly calibrated uncertainties for certain foundation models.
*Mitigation:* Validate calibration using reliability diagrams; fall back to Deep Ensembles if calibration is poor.

**Challenge 2: Computational Overhead.** MC Dropout with $n=50$ samples increases inference time.
*Mitigation:* Implement batched inference; explore reducing $n$ with minimal accuracy loss.

**Challenge 3: Hyperparameter Sensitivity.** Uncertainty thresholds and acquisition weights may require task-specific tuning.
*Mitigation:* Conduct sensitivity analysis; develop automated threshold selection based on initial data statistics.

### 3.3 Broader Impact

**Scientific Impact:** BioHomeoAL provides a principled framework for integrating foundation models into experimental biology workflows. The control-theoretic formalization offers theoretical grounding for the "lab in the loop" paradigm and may inspire similar approaches in other scientific domains.

**Practical Impact:** By reducing experimental costs by 30-50%, BioHomeoAL can democratize access to foundation model capabilities for resource-constrained laboratories. A graduate student with a single GPU can now leverage billion-parameter models for their research.

**Methodological Impact:** The adaptive LoRA mechanism and multi-objective acquisition function represent novel contributions that may be applicable beyond biological contexts. The bio-inspired homeostatic framework demonstrates the value of drawing analogies from biological systems for ML algorithm design.

### 3.4 Future Directions

1. **Extension to Generative Models:** Adapt the framework for generative biological models (protein design, molecule generation)
2. **Multi-Fidelity Active Learning:** Incorporate experiments with varying costs and accuracies
3. **Federated BioHomeoAL:** Enable collaborative learning across multiple laboratories while preserving data privacy
4. **Real-World Validation:** Partner with wet laboratories for prospective experimental validation

---

## 4. Conclusion

BioHomeoAL addresses a critical gap in making foundation models accessible for biological discovery. By formalizing epistemic uncertainty as a homeostatic feedback signal, we provide a unified framework that coordinates model adaptation, sample selection, and resource management within realistic laboratory constraints. The proposed methodology is grounded in both theoretical principles and practical considerations, with comprehensive experimental validation planned across multiple biological modalities. Success of this research will directly contribute to the workshop's mission of bridging the accessibility and efficiency gap between ML research and wet lab use, enabling broader adoption of foundation models for biomedical discovery.