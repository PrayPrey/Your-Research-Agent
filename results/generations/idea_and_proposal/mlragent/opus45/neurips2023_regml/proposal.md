# Research Proposal: Auditing Trade-offs: A Framework for Quantifying Tensions Between Privacy, Fairness, and Explainability in Regulated ML Systems

## 1. Introduction

### Background

The proliferation of machine learning systems across high-stakes domains—including healthcare, finance, criminal justice, and hiring—has prompted governments worldwide to establish comprehensive regulatory frameworks. The European Union's General Data Protection Regulation (GDPR) enshrines rights to privacy and explanation, while the EU AI Act mandates fairness and transparency for high-risk AI systems. Similar regulatory initiatives have emerged globally, including the US Algorithmic Accountability Act and various sectoral guidelines.

However, these regulatory frameworks simultaneously impose multiple requirements that may fundamentally conflict at the algorithmic level. Differential privacy, the gold standard for privacy protection, introduces noise that can disproportionately affect underrepresented groups, thereby exacerbating fairness disparities. Detailed model explanations, while satisfying transparency requirements, can inadvertently leak sensitive training data or enable membership inference attacks. Fairness-enhancing interventions may require access to protected attributes, creating tensions with data minimization principles.

Current research has largely addressed these regulatory objectives in isolation. Yuan and Wang (2025) developed privacy-preserving fairness auditing using synthetic data, while Pentyala et al. (2022) introduced PrivFair for secure multiparty computation-based fairness evaluation. Wasif et al. (2025) explored privacy-fairness-accuracy trade-offs in federated learning, demonstrating context-dependent relationships. Sharma et al. (2024) proposed REFRESH for multi-objective feature selection. Despite these advances, practitioners lack a unified framework to systematically quantify, visualize, and navigate the inherent tensions between regulatory objectives.

### Research Objectives

This research aims to develop a comprehensive auditing framework that enables practitioners and policymakers to:

1. **Quantify pairwise and joint trade-offs** between privacy, fairness, and explainability using standardized, interpretable metrics.
2. **Map Pareto frontiers** across regulatory dimensions for specific model-dataset combinations, revealing feasible compliance regions.
3. **Compute regulatory compatibility scores** that indicate whether specific combinations of regulatory thresholds are simultaneously achievable.
4. **Provide actionable guidance** through an open-source toolkit for making informed trade-off decisions.

### Significance

This research addresses a critical gap between regulatory requirements and practical ML implementation. The absence of standardized tools for understanding regulatory trade-offs forces practitioners into ad-hoc compliance strategies, potentially leading to legal exposure or overly conservative deployments that sacrifice system utility. By providing rigorous quantification of trade-offs, our framework will enable evidence-based decisions about regulatory compliance, inform policymakers about inherent tensions in current regulations, and establish benchmarks for evaluating future multi-objective ML algorithms.

## 2. Methodology

### 2.1 Conceptual Framework

We define the regulatory trade-off space as a multi-dimensional optimization problem. Let $\mathcal{M}$ denote a model class, $\mathcal{D}$ a dataset, and $\theta$ the model parameters. We consider three regulatory dimensions:

- **Privacy** $\mathcal{P}(\theta, \mathcal{D})$: Quantified via differential privacy budget $\varepsilon$ or empirical privacy leakage measures
- **Fairness** $\mathcal{F}(\theta, \mathcal{D})$: Measured through group fairness metrics (demographic parity, equalized odds) or individual fairness measures
- **Explainability** $\mathcal{E}(\theta, \mathcal{D})$: Assessed via explanation fidelity, stability, and comprehensibility metrics

The regulatory compliance problem can be formulated as:

$$\max_{\theta} \text{Utility}(\theta, \mathcal{D}) \quad \text{s.t.} \quad \mathcal{P}(\theta, \mathcal{D}) \leq \tau_p, \quad \mathcal{F}(\theta, \mathcal{D}) \leq \tau_f, \quad \mathcal{E}(\theta, \mathcal{D}) \geq \tau_e$$

where $\tau_p$, $\tau_f$, and $\tau_e$ represent regulatory thresholds.

### 2.2 Trade-off Measurement Protocol

#### 2.2.1 Metric Definitions

**Privacy Metrics:**
- Differential privacy budget: $(\varepsilon, \delta)$-DP guarantees
- Empirical privacy leakage: Membership inference attack success rate $\text{MIA}(\theta)$
- Attribute inference vulnerability: $\text{AIA}(\theta) = \max_a P(\hat{a} = a | \theta, x)$ for sensitive attributes $a$

**Fairness Metrics:**
- Demographic Parity Gap: $\text{DPG} = |P(\hat{Y}=1|A=0) - P(\hat{Y}=1|A=1)|$
- Equalized Odds Difference: $\text{EOD} = \max_{y \in \{0,1\}} |P(\hat{Y}=1|A=0,Y=y) - P(\hat{Y}=1|A=1,Y=y)|$
- Individual Fairness Violation: $\text{IFV} = \mathbb{E}_{x,x'}[d_{\hat{Y}}(\theta(x), \theta(x')) - d_X(x, x')]^+$

**Explainability Metrics:**
- Explanation Fidelity: $\text{EF} = 1 - \frac{1}{n}\sum_{i=1}^n |\theta(x_i) - g_i(e_i)|$ where $e_i$ is the explanation and $g_i$ a surrogate model
- Explanation Stability: $\text{ES} = 1 - \mathbb{E}_{x,\delta}[\|e(x) - e(x+\delta)\| / \|\delta\|]$
- Information Leakage through Explanations: $\text{ILE} = I(E; D_{\text{train}})$, estimated via membership inference on explanations

#### 2.2.2 Pairwise Trade-off Functions

We define trade-off functions that capture the degradation in one objective when optimizing another:

**Privacy-Fairness Trade-off:**
$$T_{PF}(\varepsilon) = \mathbb{E}_{\theta \sim \mathcal{M}_\varepsilon}[\mathcal{F}(\theta, \mathcal{D})] - \mathcal{F}(\theta^*, \mathcal{D})$$

where $\mathcal{M}_\varepsilon$ denotes models trained with privacy budget $\varepsilon$ and $\theta^*$ is the non-private optimal model.

**Privacy-Explainability Trade-off:**
$$T_{PE}(\varepsilon) = \mathcal{E}(\theta^*, \mathcal{D}) - \mathbb{E}_{\theta \sim \mathcal{M}_\varepsilon}[\mathcal{E}(\theta, \mathcal{D})]$$

**Fairness-Explainability Trade-off:**
$$T_{FE}(\lambda) = \mathcal{E}(\theta^*, \mathcal{D}) - \mathcal{E}(\theta_\lambda, \mathcal{D})$$

where $\theta_\lambda$ incorporates fairness constraints with strength $\lambda$.

### 2.3 Pareto Frontier Mapping Algorithm

We develop an algorithm to compute the achievable Pareto frontier across regulatory dimensions:

**Algorithm 1: Multi-Objective Regulatory Pareto Frontier**

```
Input: Dataset D, Model class M, Privacy budgets E = {ε₁,...,εₖ}, 
       Fairness constraints Λ = {λ₁,...,λₘ}, Explanation methods X
Output: Pareto frontier P, Dominated solutions S

1. Initialize P ← ∅, S ← ∅
2. For each ε ∈ E:
3.     For each λ ∈ Λ:
4.         For each explanation method x ∈ X:
5.             θ ← Train(M, D, ε, λ)
6.             e ← GenerateExplanations(θ, D, x)
7.             p ← (Privacy(θ, ε), Fairness(θ, D), Explainability(e, θ, D))
8.             S ← S ∪ {(θ, p)}
9. P ← ExtractParetoFrontier(S)
10. Return P, S
```

The Pareto frontier extraction identifies all non-dominated solutions:

$$P = \{p \in S : \nexists p' \in S \text{ s.t. } p' \succ p\}$$

where $p' \succ p$ denotes Pareto dominance across all three dimensions.

### 2.4 Regulatory Compatibility Scoring

We introduce a Regulatory Compatibility Score (RCS) that quantifies the feasibility of simultaneously meeting multiple regulatory thresholds:

$$\text{RCS}(\tau_p, \tau_f, \tau_e) = \begin{cases} 1 & \text{if } \exists \theta : \mathcal{P}(\theta) \leq \tau_p \land \mathcal{F}(\theta) \leq \tau_f \land \mathcal{E}(\theta) \geq \tau_e \\ \min_{\theta \in P} d(\theta, \tau) & \text{otherwise} \end{cases}$$

where $d(\theta, \tau) = \sqrt{[\mathcal{P}(\theta) - \tau_p]_+^2 + [\mathcal{F}(\theta) - \tau_f]_+^2 + [\tau_e - \mathcal{E}(\theta)]_+^2}$ measures the distance to the feasibility region.

We also compute the **Regulatory Tension Index (RTI)**:

$$\text{RTI}(\mathcal{D}, \mathcal{M}) = 1 - \frac{\text{Vol}(\text{FeasibleRegion})}{\text{Vol}(\text{TotalRegion})}$$

where volumes are computed over the normalized metric space.

### 2.5 Experimental Design

#### 2.5.1 Datasets

We will conduct experiments across three high-stakes domains:

1. **Lending**: German Credit Dataset, HELOC Dataset, LendingClub Dataset
2. **Healthcare**: MIMIC-III (mortality prediction), Diabetes 130-US Hospitals
3. **Hiring**: Adult Income Dataset, synthetic hiring datasets with known ground truth

Additionally, we will create synthetic datasets with controlled properties to validate framework behavior under known trade-off structures.

#### 2.5.2 Model Classes

- Logistic Regression (baseline, interpretable)
- Gradient Boosted Trees (XGBoost, LightGBM)
- Neural Networks (MLPs, varying depths)
- Pre-trained Language Models (for text-based applications)

#### 2.5.3 Privacy Mechanisms

- DP-SGD with varying $\varepsilon \in \{0.1, 0.5, 1.0, 2.0, 5.0, 10.0, \infty\}$
- PATE (Private Aggregation of Teacher Ensembles)
- Federated Learning with Secure Aggregation

#### 2.5.4 Fairness Interventions

- Pre-processing: Reweighting, disparate impact remover
- In-processing: Adversarial debiasing, constraint-based training
- Post-processing: Threshold optimization, calibrated equalized odds

#### 2.5.5 Explanation Methods

- SHAP values (global and local)
- LIME explanations
- Integrated Gradients
- Counterfactual explanations

#### 2.5.6 Evaluation Metrics

| Dimension | Primary Metrics | Secondary Metrics |
|-----------|-----------------|-------------------|
| Privacy | $\varepsilon$-DP, MIA success rate | AIA success, reconstruction error |
| Fairness | DPG, EOD | Individual fairness, calibration gap |
| Explainability | Fidelity, Stability | Sparsity, human evaluation scores |
| Utility | Accuracy, AUC-ROC | F1-score, calibration |

#### 2.5.7 Statistical Validation

- Bootstrap confidence intervals (95%) for all trade-off measurements
- Wilcoxon signed-rank tests for pairwise method comparisons
- Multiple hypothesis correction using Benjamini-Hochberg procedure
- Cross-validation (5-fold) for generalization assessment

### 2.6 Implementation Architecture

The open-source toolkit will be implemented in Python with the following components:

1. **Auditor Module**: Computes all privacy, fairness, and explainability metrics
2. **Trade-off Analyzer**: Generates trade-off functions and Pareto frontiers
3. **Visualization Engine**: Interactive plots for exploring trade-off landscapes
4. **Compliance Checker**: Evaluates RCS against user-specified thresholds
5. **Report Generator**: Produces audit reports aligned with regulatory requirements

## 3. Expected Outcomes & Impact

### 3.1 Scientific Contributions

1. **Standardized Trade-off Metrics**: The first comprehensive suite of metrics for quantifying pairwise and joint tensions between privacy, fairness, and explainability, enabling reproducible comparisons across studies.

2. **Empirical Trade-off Characterization**: Detailed empirical analysis revealing how trade-offs vary across domains (lending, healthcare, hiring), model classes, and data characteristics. We expect to identify conditions under which trade-offs are severe versus manageable.

3. **Pareto Frontier Methodology**: A rigorous algorithmic approach for mapping achievable regulatory compliance regions, providing theoretical and practical bounds on simultaneous optimization.

4. **Regulatory Compatibility Framework**: Novel scoring mechanisms (RCS, RTI) that translate complex trade-off landscapes into actionable compliance assessments.

### 3.2 Practical Deliverables

1. **Open-Source Toolkit**: A production-ready Python library enabling practitioners to audit their ML systems for regulatory trade-offs, with comprehensive documentation and tutorials.

2. **Benchmark Datasets**: Curated datasets with pre-computed trade-off characterizations, serving as reference points for future research.

3. **Compliance Templates**: Report templates aligned with GDPR, EU AI Act, and other regulatory frameworks, facilitating documentation requirements.

### 3.3 Policy Impact

Our findings will provide empirical evidence for policymakers about inherent tensions in current regulatory frameworks. Specifically:

- Identifying combinations of regulatory thresholds that are mathematically infeasible, informing more realistic policy design
- Quantifying the "cost of regulation" in terms of utility degradation for specific compliance requirements
- Highlighting domain-specific variations that may warrant differentiated regulatory approaches

### 3.4 Broader Impact

This research directly addresses the critical gap between regulatory aspirations and technical reality. By providing tools for systematic trade-off analysis, we enable:

- **Industry**: Evidence-based compliance decisions, reduced legal uncertainty, and optimized resource allocation for regulatory adherence
- **Regulators**: Data-driven policy refinement based on demonstrated feasibility constraints
- **Research Community**: A unified framework and benchmarks for advancing multi-objective ML optimization

The framework will be particularly valuable as regulations continue to evolve, providing a methodology for rapidly assessing the implications of new requirements. By making trade-offs transparent and quantifiable, we contribute to the broader goal of deploying ML systems that are simultaneously trustworthy across multiple dimensions, supporting the development of truly regulatable machine learning.