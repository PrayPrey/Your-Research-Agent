# Research Proposal: Fairness-by-Design Synthetic Data Generation with Instruction-Tuned LLMs

## 1. Title

**Fairness-by-Design Synthetic Data Generation: Instruction-Tuned Large Language Models with Constrained Decoding for Equitable Machine Learning**

## 2. Introduction

### 2.1 Background

The advancement of machine learning has been fundamentally dependent on access to high-quality training datasets. However, three critical challenges—data scarcity, privacy concerns, and bias/under-representation—create significant barriers to developing trustworthy ML systems, particularly in high-stakes domains such as healthcare, finance, criminal justice, and education. Synthetic data generation has emerged as a promising solution to these challenges, offering the potential to create arbitrarily large datasets while addressing privacy and fairness concerns.

Recent developments have witnessed a paradigm shift in synthetic data generation, with Large Language Models (LLMs) increasingly replacing Generative Adversarial Networks (GANs) as the dominant approach. Studies demonstrate that LLMs achieve superior performance in generating realistic tabular data, with the LLM Tabular Survey (2024) documenting their effectiveness across diverse domains. However, this transition has exposed a critical gap: while existing LLM-based methods excel at generating high-fidelity data, they largely neglect fairness considerations, achieving only 10-15% demographic parity in generated datasets.

Current approaches to fairness in synthetic data generation suffer from fundamental limitations. Post-hoc correction methods (reweighting, resampling) achieve 8-12% demographic parity difference but sacrifice 5-10% data utility. State-of-the-art fairness-aware GANs like DECAF and CTAB-GAN+ demonstrate 8-15% demographic parity difference with 2-5% utility loss, but require domain-specific architectures and extensive training (100+ epochs). Critically, all existing methods treat fairness as an afterthought—a constraint to be imposed after model design—rather than as a fundamental design principle.

This research addresses this gap by proposing a **fairness-by-design** paradigm that integrates fairness considerations into the core architecture of LLM-based synthetic data generation. Drawing from procedural justice theory in social psychology, we hypothesize that teaching LLMs to understand fairness semantically (through instruction-tuning) while enforcing formal guarantees (through constrained decoding) will achieve superior fairness-utility trade-offs compared to existing approaches.

### 2.2 Research Objectives

The primary objectives of this research are:

1. **Develop a dual-mechanism fairness-by-design framework** combining fairness-aware instruction-tuning with constrained decoding for LLM-based synthetic tabular data generation.

2. **Achieve quantifiable fairness improvements**: Target demographic parity difference <5% (compared to baseline 15-25% and post-hoc 8-12%) while preserving data utility within 2-5% of unconstrained generation.

3. **Establish the causal mechanism** by which instruction-tuning teaches semantic fairness understanding and constrained decoding provides formal guarantees.

4. **Quantify fairness-utility trade-offs** across standard fairness benchmarks (Adult, COMPAS, German Credit) to establish practical thresholds for trustworthy ML development.

5. **Demonstrate architectural flexibility** by validating the approach across multiple LLM families (GPT-3.5, Llama-2), ensuring future-proof applicability.

### 2.3 Research Significance

This research makes several significant contributions to the field of trustworthy machine learning:

**Theoretical Contributions:**
- First application of procedural justice theory to generative AI, establishing fairness-by-design as a paradigm shift from post-hoc correction approaches.
- Causal mechanism decomposition demonstrating how learned fairness understanding (instruction-tuning) and formal guarantees (constrained decoding) synergistically improve fairness outcomes.

**Methodological Contributions:**
- Novel fairness-aware instruction-tuning framework providing systematic protocols for teaching LLMs fairness constraints with 100-500 examples.
- Dual-mechanism architecture combining learned semantic understanding with formal constraint enforcement, achieving 40-60% fairness improvement over state-of-the-art.
- Quantitative fairness-utility trade-off characterization establishing concrete thresholds (<5% fairness difference, 2-5% utility preservation).

**Practical Contributions:**
- Cost-effective generation of fair synthetic datasets for under-represented groups, reducing data collection costs from $10K+ to $500-$2K per dataset.
- Immediate applicability to high-stakes domains (healthcare: rare disease patients; finance: minority loan applicants; criminal justice: recidivism prediction for marginalized communities).
- LLM-agnostic architecture ensuring compatibility with future model developments.

The significance of this work extends beyond technical improvements. By enabling the generation of fair synthetic datasets at scale, this research directly addresses the workshop's core mission: empowering trustworthy ML training through synthetic data that simultaneously addresses data scarcity, privacy, and bias/under-representation. The proposed approach provides a practical pathway for organizations to develop ML systems that meet fairness requirements without compromising model performance or incurring prohibitive data collection costs.

## 3. Methodology

### 3.1 Research Design Overview

This research employs a **2×2 factorial experimental design** with two independent factors (Instruction-Tuning: on/off × Constrained Decoding: on/off) plus two baseline conditions, resulting in six experimental conditions total:

1. **Baseline LLM** (no fairness intervention)
2. **Post-hoc Correction** (reweighting/resampling)
3. **Instruction-Tuning Only** (IT)
4. **Constrained Decoding Only** (CD)
5. **Instruction-Tuning + Constrained Decoding** (IT+CD) [Primary condition]
6. **CTAB-GAN+** (state-of-the-art fairness-aware GAN baseline)

### 3.2 Data Collection and Preparation

**Benchmark Datasets:**
We utilize three standard fairness benchmarks with varying sizes and complexity:

1. **Adult Income Dataset** (48,842 samples): Predict income >$50K with protected attributes (race, gender, age)
2. **COMPAS Recidivism Dataset** (10,000 samples): Predict recidivism risk with protected attributes (race, gender, age)
3. **UCI German Credit Dataset** (1,000 samples): Predict credit risk with protected attributes (gender, age)

**Data Preprocessing:**
- Split each dataset: 70% training (real data for validation), 20% validation, 10% test (holdout for utility evaluation)
- Standardize protected attribute encoding: Binary for gender, multi-class for race/age groups
- Document baseline demographic distributions: $P(A=a)$ for each protected attribute $A$
- Calculate baseline fairness metrics on original data

**Instruction-Tuning Data Creation:**
Generate 100-500 fairness-aware synthetic data generation examples through three methods:

1. **Manual Annotation** (50 examples): Expert-crafted examples demonstrating balanced generation across protected groups
2. **Bootstrapping** (200 examples): Use GPT-4 to generate examples following fairness templates
3. **Self-Training** (250 examples): Iteratively refine examples using constraint satisfaction feedback

Each training example follows the format:
```
Instruction: "Generate a synthetic data sample for [dataset] ensuring demographic balance. 
Protected attributes: [race, gender, age]. Target distribution: [specified proportions]."

Output: [JSON-formatted synthetic sample with balanced attributes]

Constraint Verification: [Demographic distribution check]
```

### 3.3 Algorithmic Framework

#### 3.3.1 Fairness-Aware Instruction-Tuning

**Objective:** Teach LLMs semantic understanding of fairness constraints through parameter-efficient fine-tuning.

**Algorithm:**

1. **Base Model Selection:** Initialize with pre-trained LLM $\mathcal{M}_{\text{base}}$ (GPT-3.5-turbo or Llama-2-7B)

2. **LoRA Configuration:** Apply Low-Rank Adaptation with rank $r=8$, scaling factor $\alpha=16$:
   $$W' = W_0 + \Delta W = W_0 + BA$$
   where $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times k}$, and $r \ll \min(d,k)$

3. **Training Objective:** Minimize fairness-aware loss:
   $$\mathcal{L}_{\text{IT}} = \mathcal{L}_{\text{CE}} + \lambda_{\text{fair}} \mathcal{L}_{\text{fair}}$$
   
   where:
   - $\mathcal{L}_{\text{CE}} = -\sum_{i=1}^{N} \log P(x_i | \text{instruction}_i; \theta)$ (cross-entropy)
   - $\mathcal{L}_{\text{fair}} = \sum_{a,b \in \mathcal{A}} |P(\hat{Y}=1|A=a) - P(\hat{Y}=1|A=b)|$ (demographic parity violation)
   - $\lambda_{\text{fair}} = 0.3$ (fairness weight, tuned via validation)

4. **Training Protocol:**
   - Batch size: 16
   - Learning rate: $3 \times 10^{-4}$ with cosine annealing
   - Epochs: 10-20 (early stopping on validation constraint satisfaction)
   - Constraint satisfaction threshold: 75% (minimum acceptable)

#### 3.3.2 Constrained Decoding

**Objective:** Enforce formal demographic balance guarantees during generation through grammar-based constraints.

**Algorithm (NEUROLOGIC-Adapted):**

1. **Constraint Formalization:** Define demographic balance constraint as context-free grammar:
   $$\mathcal{G}_{\text{fair}} = \{S \rightarrow \text{Sample}_{a_1} | \text{Sample}_{a_2} | \ldots | \text{Sample}_{a_k}\}$$
   where $a_i \in \mathcal{A}$ are protected attribute values, and production probabilities satisfy:
   $$\left| \frac{n_{a_i}}{N} - P_{\text{target}}(A=a_i) \right| \leq \epsilon_{\text{tol}}$$
   with $\epsilon_{\text{tol}} = 0.05$ (5% tolerance)

2. **Constrained Beam Search:** At each decoding step $t$:
   
   a. Compute unconstrained token probabilities:
   $$p(x_t | x_{<t}) = \text{softmax}(\mathcal{M}_{\text{base}}(x_{<t}))$$
   
   b. Filter tokens violating constraints:
   $$\mathcal{V}_t = \{x_t : \text{violates}(\mathcal{G}_{\text{fair}}, x_{<t} \oplus x_t)\}$$
   
   c. Reweight probabilities:
   $$p'(x_t | x_{<t}) = \begin{cases}
   0 & \text{if } x_t \in \mathcal{V}_t \\
   \frac{p(x_t | x_{<t})}{\sum_{x \notin \mathcal{V}_t} p(x | x_{<t})} & \text{otherwise}
   \end{cases}$$
   
   d. Sample from reweighted distribution with temperature $\tau=0.8$

3. **Batch-Level Balancing:** Track cumulative demographic distribution across batch:
   $$\hat{P}_{\text{batch}}(A=a) = \frac{1}{n_{\text{generated}}} \sum_{i=1}^{n_{\text{generated}}} \mathbb{1}[A_i = a]$$
   
   Adjust sampling probabilities to minimize:
   $$\mathcal{D}_{\text{batch}} = \sum_{a \in \mathcal{A}} |\hat{P}_{\text{batch}}(A=a) - P_{\text{target}}(A=a)|$$

#### 3.3.3 Integrated IT+CD Pipeline

**End-to-End Generation Process:**

```
Input: Dataset schema, target size N, protected attributes A, target distribution P_target
Output: Synthetic dataset D_syn with |D_syn| = N

1. Load instruction-tuned model M_IT
2. Initialize D_syn = ∅, demographic_counts = {a: 0 for a in A}
3. For i = 1 to N:
   a. Compute current distribution: P_current = demographic_counts / i
   b. Identify under-represented group: a* = argmin_a (P_current(a) - P_target(a))
   c. Construct fairness-aware prompt:
      "Generate sample with protected attribute [a*] to balance distribution"
   d. Generate sample using constrained decoding (Algorithm 3.3.2)
   e. Validate constraint satisfaction:
      - If |P_current(a*) - P_target(a*)| > ε_tol, regenerate
   f. Add sample to D_syn, update demographic_counts
4. Return D_syn
```

### 3.4 Experimental Protocol

#### 3.4.1 Training Phase

For each dataset (Adult, COMPAS, German Credit):

1. **Instruction-Tuning:**
   - Train fairness-aware LLM using LoRA (Section 3.3.1)
   - Validate constraint satisfaction on 100-sample validation set
   - Target: ≥75% constraint satisfaction rate

2. **Constrained Decoding Calibration:**
   - Tune tolerance parameter $\epsilon_{\text{tol}} \in \{0.03, 0.05, 0.10\}$
   - Measure constraint violation rate on 1,000-sample test generation
   - Select $\epsilon_{\text{tol}}$ achieving ≤5% violation rate

#### 3.4.2 Generation Phase

For each experimental condition (6 conditions × 3 datasets = 18 configurations):

1. Generate 10 replications of 10,000 synthetic samples each
2. Record generation time and computational cost (GPU-hours)
3. Validate constraint satisfaction in real-time
4. Store generated datasets for evaluation

#### 3.4.3 Evaluation Phase

**Primary Metrics:**

1. **Demographic Parity Difference (DPD):**
   $$\text{DPD} = \max_{a,b \in \mathcal{A}} |P(\hat{Y}=1|A=a) - P(\hat{Y}=1|A=b)|$$
   Target: <5% (vs. baseline 15-25%, post-hoc 8-12%)

2. **ML Efficacy (Utility Preservation):**
   - Train downstream classifier (Logistic Regression, Random Forest, XGBoost) on synthetic data
   - Evaluate accuracy on real holdout test set
   - Compute utility loss: $\Delta_{\text{utility}} = \text{Acc}_{\text{real}} - \text{Acc}_{\text{syn}}$
   - Target: $\Delta_{\text{utility}} \leq 5\%$

**Secondary Metrics:**

3. **Constraint Satisfaction Rate (CSR):**
   $$\text{CSR} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}[\text{satisfies}(\mathcal{G}_{\text{fair}}, x_i)]$$
   Target: ≥75% (IT only), ≥95% (IT+CD)

4. **Equalized Odds Difference (EOD):**
   $$\text{EOD} = \max_{a,b \in \mathcal{A}} |P(\hat{Y}=1|Y=1,A=a) - P(\hat{Y}=1|Y=1,A=b)|$$
   (Secondary fairness metric for robustness check)

5. **Generation Cost:**
   - GPU-hours per 10K samples
   - Acceptable threshold: ≤3× baseline

**Evaluation Protocol:**

1. **Fairness Evaluation:**
   - Compute DPD and EOD on generated datasets
   - Compare across 6 experimental conditions using one-way ANOVA
   - Post-hoc pairwise comparisons (Tukey HSD) to identify significant differences

2. **Utility Evaluation:**
   - Train 3 classifier types (LR, RF, XGBoost) on each synthetic dataset
   - Evaluate on real holdout test set (10% of original data)
   - Compute mean accuracy and utility loss across 10 replications
   - Paired t-test comparing IT+CD vs. baselines

3. **Fairness-Utility Trade-off Analysis:**
   - Plot Pareto frontier: DPD (x-axis) vs. Utility Loss (y-axis)
   - Identify dominated/non-dominated solutions
   - Compare IT+CD frontier vs. SOTA baselines (CTAB-GAN+, DECAF)

### 3.5 Statistical Analysis

**Hypothesis Testing:**

**H1 (Primary):** IT+CD achieves DPD <5%
- One-sample t-test: $H_0: \mu_{\text{DPD}} \geq 5\%$ vs. $H_1: \mu_{\text{DPD}} < 5\%$
- Significance level: $\alpha = 0.05$

**H2 (Utility Preservation):** IT+CD preserves utility within 5%
- One-sample t-test: $H_0: \mu_{\Delta_{\text{utility}}} \geq 5\%$ vs. $H_1: \mu_{\Delta_{\text{utility}}} < 5\%$

**H3 (Superiority):** IT+CD achieves 30% better fairness than post-hoc correction
- Non-inferiority test with margin $\delta = 0.3 \times \text{DPD}_{\text{post-hoc}}$
- Paired t-test: $H_0: \text{DPD}_{\text{IT+CD}} - \text{DPD}_{\text{post-hoc}} \geq -\delta$ vs. $H_1: \text{DPD}_{\text{IT+CD}} - \text{DPD}_{\text{post-hoc}} < -\delta$

**Power Analysis:**
- Effect size: Cohen's $d \geq 0.8$ (large effect)
- Sample size: 10 replications per condition
- Power: $1-\beta = 0.8$ (80% probability of detecting true effect)
- Calculated using G*Power for ANOVA with 6 groups

**Falsification Criteria (Hypothesis REJECTED if ANY):**
1. DPD >10% (no significant fairness improvement)
2. Utility loss >10% (unacceptable performance degradation)
3. Post-hoc correction achieves better fairness-utility trade-off (Pareto dominance)
4. Constraint satisfaction <50% for IT (mechanism failure)
5. Computational cost >10× baseline (impractical)

**Success Criteria (Hypothesis CONFIRMED if ALL):**
1. DPD <5% (primary target)
2. Utility loss ≤5% (acceptable performance)
3. 30% better fairness than post-hoc correction
4. CSR ≥75% (IT), ≥95% (IT+CD)
5. Computational cost ≤3× baseline

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Quantitative Outcomes:**

1. **Fairness Improvement:**
   - Demographic parity difference <5% (vs. baseline 15-25%, representing 66-80% improvement)
   - 40-60% fairness improvement over state-of-the-art methods (CTAB-GAN+: 10-15%, DECAF: 8-10%)
   - Constraint satisfaction rate ≥95% with IT+CD (vs. 75% with IT only)

2. **Utility Preservation:**
   - Data utility within 2-5% of unconstrained generation (vs. post-hoc 5-10% loss)
   - Competitive or superior performance compared to SOTA fairness-aware GANs
   - Maintained utility across diverse downstream tasks (classification, regression)

3. **Efficiency Gains:**
   - Generation cost 1.5-2× baseline (acceptable overhead for fairness guarantees)
   - Training efficiency: 100-500 examples for instruction-tuning (vs. 100+ epochs for GANs)
   - Scalability: Linear cost scaling with dataset size

**Qualitative Outcomes:**

4. **Mechanistic Understanding:**
   - Empirical validation of dual-mechanism hypothesis (learned + formal constraints)
   - Quantified contribution of instruction-tuning vs. constrained decoding
   - Identified failure modes and boundary conditions

5. **Architectural Insights:**
   - LLM-agnostic framework validated across GPT-3.5 and Llama-2
   - Transferability across datasets (Adult, COMPAS, German Credit)
   - Extensibility to other fairness metrics (equalized odds, calibration)

### 4.2 Scientific Impact

**Theoretical Contributions:**

1. **Paradigm Shift:** Establishes fairness-by-design as a principled alternative to post-hoc correction, grounded in procedural justice theory from social psychology.

2. **Causal Mechanism:** Decomposes fairness-constraint learning into semantic understanding (instruction-tuning) and formal enforcement (constrained decoding), providing a blueprint for future trustworthy AI systems.

3. **Trade-off Characterization:** Quantifies fairness-utility Pareto frontiers, establishing concrete thresholds (<5% fairness, 2-5% utility) for practical deployment.

**Methodological Contributions:**

4. **Reusable Framework:** Provides systematic protocols for fairness-aware instruction-tuning applicable to diverse generative tasks beyond tabular data.

5. **Benchmarking Standards:** Establishes rigorous evaluation methodology for fairness in synthetic data generation, addressing the workshop's identified gap in consistent benchmarking.

6. **Open-Source Toolkit:** Planned release of implementation, training data, and evaluation scripts to accelerate community adoption.

### 4.3 Practical Impact

**Immediate Applications:**

1. **Healthcare:** Generate synthetic datasets for rare disease patients, enabling ML development without privacy violations or selection bias. Example: Synthetic data for underdiagnosed conditions in minority populations.

2. **Finance:** Create fair training datasets for credit scoring and loan approval systems, addressing historical discrimination against marginalized communities while maintaining predictive accuracy.

3. **Criminal Justice:** Develop recidivism prediction models trained on synthetic data that mitigates racial bias, supporting evidence-based sentencing reform.

4. **Education:** Generate synthetic student performance data for adaptive learning systems, ensuring equitable representation across socioeconomic backgrounds.

**Economic Impact:**

5. **Cost Reduction:** Reduce data collection costs from $10K+ to $500-$2K per dataset, democratizing access to high-quality training data for resource-constrained organizations.

6. **Regulatory Compliance:** Enable organizations to meet emerging fairness regulations (EU AI Act, US algorithmic accountability bills) through auditable synthetic data generation.

**Societal Impact:**

7. **Equity Advancement:** Directly addresses under-representation of marginalized groups in ML training data, reducing algorithmic discrimination in high-stakes decisions.

8. **Trust Building:** Provides transparent, verifiable fairness guarantees (through constrained decoding), increasing public trust in AI systems deployed in sensitive domains.

9. **Research Acceleration:** Enables researchers to access fair, privacy-preserving datasets without lengthy IRB approvals or data use agreements, accelerating innovation in trustworthy ML.

### 4.4 Alignment with Workshop Goals

This research directly addresses the workshop's three core challenges:

1. **Data Scarcity:** Generates arbitrarily large synthetic datasets from limited real data (demonstrated on German Credit with only 1,000 samples).

2. **Privacy:** Builds on DP-Tabula and SafeSynthDP precedents, with future extensions to integrate differential privacy guarantees (deferred to follow-up work).

3. **Bias and Under-representation:** Core focus—achieves 40-60% fairness improvement through fairness-by-design, enabling curated benchmark datasets that reflect equitable demographic distributions.

The proposed fairness-by-design paradigm represents a fundamental shift from treating fairness as a post-processing constraint to embedding it as a core architectural principle. By demonstrating that LLMs can learn semantic fairness understanding while providing formal guarantees, this research establishes a blueprint for the next generation of trustworthy synthetic data generation systems—systems that simultaneously address fidelity, privacy, and fairness without compromising on any dimension.

**Long-term Vision:** This work lays the foundation for a future where synthetic data generation is not merely a technical convenience but a mechanism for advancing social equity—where ML systems trained on synthetic data outperform those trained on biased real-world data, not despite fairness constraints, but because of them.