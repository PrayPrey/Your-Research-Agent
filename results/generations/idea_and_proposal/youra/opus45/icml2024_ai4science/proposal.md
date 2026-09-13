# Research Proposal: Discovering the Scaling-Interpretability Pareto Frontier in Scientific AI via Mutual Information Alignment

## 1. Introduction

### 1.1 Background

The integration of artificial intelligence into scientific discovery has accelerated dramatically over the past decade, with transformative applications spanning molecular design, climate modeling, protein engineering, and materials science. Models such as AlphaFold have demonstrated unprecedented predictive accuracy in protein structure prediction, while large-scale foundation models are increasingly deployed across diverse scientific domains. A consistent empirical observation across these applications is that model performance improves with scale—larger architectures trained on more data with greater computational resources achieve superior predictive accuracy.

However, this scaling paradigm introduces a fundamental tension that threatens the core mission of scientific AI: the trade-off between predictive power and interpretability. Scientific discovery requires not merely accurate predictions but mechanistic understanding—scientists need to comprehend *why* a model makes particular predictions to generate testable hypotheses, validate findings against domain knowledge, and ultimately advance human understanding. As models scale from millions to billions of parameters, their internal representations become increasingly distributed and opaque, creating what is commonly termed the "black box" problem.

Current approaches to this challenge fall into two inadequate categories. The first prioritizes accuracy, accepting reduced interpretability as an unavoidable cost of performance. The second enforces interpretability constraints through techniques such as concept bottleneck models or physics-informed architectures, often sacrificing predictive performance. Neither approach provides scientists with a systematic framework to understand and navigate the fundamental trade-off between these competing objectives.

### 1.2 Research Objectives

This research proposes to characterize and navigate the scaling-interpretability trade-off in scientific AI through three primary objectives:

**Objective 1: Quantify the Pareto Frontier.** We will systematically measure the trade-off between prediction accuracy and interpretability across model scales, establishing whether a genuine Pareto frontier exists and characterizing its shape across multiple scientific domains.

**Objective 2: Operationalize Interpretability via Mutual Information.** We will develop a rigorous, domain-agnostic measure of interpretability based on mutual information (MI) between model representations and established scientific concept ontologies, enabling quantitative comparison across architectures and domains.

**Objective 3: Enable Efficient Frontier Discovery.** We will develop surrogate-accelerated multi-objective optimization methods that allow researchers to efficiently explore the accuracy-interpretability Pareto frontier without exhaustive architecture search.

### 1.3 Significance

This research addresses a critical gap in AI for Science methodology. By providing a quantitative framework for understanding the scaling-interpretability trade-off, we enable scientists to make informed decisions about model selection based on their specific requirements for accuracy versus explainability. For domains where mechanistic understanding is paramount (e.g., drug discovery requiring regulatory approval), researchers can identify architectures that maximize interpretability subject to accuracy constraints. For domains prioritizing prediction (e.g., weather forecasting), the framework reveals how much interpretability must be sacrificed for marginal accuracy gains.

Furthermore, this work contributes to the broader understanding of how scaling affects AI systems, providing empirical evidence for or against the hypothesis that increased model capacity fundamentally reduces alignment with human-interpretable concepts. This has implications beyond scientific AI, informing debates about AI safety, alignment, and the limits of scaling as a paradigm for AI development.

## 2. Methodology

### 2.1 Theoretical Framework

We formalize the scaling-interpretability trade-off as a multi-objective optimization problem. Let $\mathcal{M}$ denote the space of model architectures parameterized by scale factors (depth, width, attention patterns) ranging from 10M to 10B parameters. For a model $m \in \mathcal{M}$ trained on dataset $\mathcal{D}$, we define two objective functions:

**Prediction Accuracy $A(m)$:** Domain-specific performance metrics including AUROC for molecular property prediction (MoleculeNet), RMSE for climate variable forecasting (ClimateLearn), accuracy for protein fitness prediction (ProteinGym), and MAE for materials property prediction (MatBench).

**Interpretability Score $I(m)$:** We operationalize interpretability as the mutual information between model representations and domain concept vocabularies:

$$I(m) = I(\phi_m(x); C)$$

where $\phi_m(x)$ denotes the intermediate representation of input $x$ in model $m$, and $C$ represents the concept vocabulary from domain ontologies (ChEBI for molecules, Gene Ontology for proteins, CMIP6 variables for climate, Materials Project descriptors for materials).

The Pareto frontier $\mathcal{P}^*$ is defined as:

$$\mathcal{P}^* = \{m \in \mathcal{M} : \nexists m' \in \mathcal{M} \text{ s.t. } A(m') \geq A(m) \land I(m') \geq I(m) \text{ with at least one strict inequality}\}$$

### 2.2 Mutual Information Estimation via CLUB

Direct computation of $I(\phi_m(x); C)$ is intractable for high-dimensional representations. We employ the Contrastive Log-ratio Upper Bound (CLUB) estimator, which provides a tractable upper bound on mutual information:

$$\hat{I}_{CLUB}(\phi; C) = \mathbb{E}_{p(\phi, c)}[\log q(c|\phi)] - \mathbb{E}_{p(\phi)}\mathbb{E}_{p(c)}[\log q(c|\phi)]$$

where $q(c|\phi)$ is a variational approximation to the true conditional distribution $p(c|\phi)$. We parameterize $q(c|\phi)$ as a neural network trained to predict concept activations from representations.

For each domain, we construct concept activation vectors by:
1. Extracting intermediate representations $\phi_m(x)$ from the penultimate layer of model $m$
2. Computing concept presence indicators $c_i(x) \in \{0,1\}$ based on ontology annotations
3. Training the variational network $q_\theta(c|\phi)$ to minimize cross-entropy loss
4. Computing the CLUB estimate using held-out samples

### 2.3 Architecture Sampling Strategy

We systematically sample architectures across the scale spectrum using a structured design:

**Scale Dimensions:**
- Depth: $d \in \{6, 12, 24, 48, 96\}$ layers
- Width: $w \in \{256, 512, 1024, 2048, 4096\}$ hidden dimensions
- Attention heads: $h \in \{4, 8, 16, 32\}$ (for transformer architectures)

**Architecture Families:**
- Transformer-based (for sequence data: proteins, climate time series)
- Graph Neural Networks (for molecular and materials graphs)
- Hybrid architectures with domain-specific inductive biases

For each domain, we sample $n \geq 50$ architectures using Latin Hypercube Sampling to ensure coverage of the parameter space while maintaining computational feasibility.

### 2.4 Surrogate-Accelerated Pareto Learning

Full evaluation of each architecture requires substantial computational resources (training + MI estimation). We develop a surrogate-accelerated approach:

**Step 1: Initial Sampling.** Train and evaluate $n_0 = 20$ architectures selected via maximin Latin Hypercube design.

**Step 2: Surrogate Construction.** Train Gaussian Process (GP) surrogates for both objectives:

$$\hat{A}(m) \sim \mathcal{GP}(\mu_A(m), k_A(m, m'))$$
$$\hat{I}(m) \sim \mathcal{GP}(\mu_I(m), k_I(m, m'))$$

using architecture descriptors (parameter count, depth, width ratios) as input features.

**Step 3: Acquisition-Guided Sampling.** Select new architectures to evaluate using Expected Hypervolume Improvement (EHVI):

$$\alpha_{EHVI}(m) = \mathbb{E}[\text{HVI}(\mathcal{P} \cup \{(\hat{A}(m), \hat{I}(m))\}) - \text{HVI}(\mathcal{P})]$$

where HVI denotes the hypervolume indicator relative to a reference point.

**Step 4: Iterative Refinement.** Repeat Steps 2-3 until computational budget exhaustion or convergence (hypervolume improvement < 1% for 5 consecutive iterations).

### 2.5 Experimental Design

**Datasets and Domains:**

| Domain | Dataset | Task | Accuracy Metric | Ontology |
|--------|---------|------|-----------------|----------|
| Molecular | MoleculeNet (BBBP, Tox21) | Property prediction | AUROC | ChEBI (170k+ entities) |
| Climate | ClimateLearn | Variable forecasting | RMSE | CMIP6 variables |
| Protein | ProteinGym | Fitness prediction | Spearman ρ | Gene Ontology (44k+ terms) |
| Materials | MatBench | Property prediction | MAE | Materials Project descriptors |

**Training Protocol:**
- Optimizer: AdamW with cosine learning rate schedule
- Training epochs: Early stopping with patience=10 on validation loss
- Data splits: 80/10/10 train/validation/test (stratified where applicable)
- Reproducibility: 3 random seeds per architecture

**Evaluation Metrics:**

*Primary Metric - Hypervolume Indicator:*
$$HV(\mathcal{P}) = \text{Lebesgue measure of } \{y \in \mathbb{R}^2 : \exists m \in \mathcal{P}, y \prec (A(m), I(m)) \land r \prec y\}$$

where $r$ is a reference point set to (0, 0) after min-max normalization.

*Secondary Metrics:*
- Surrogate R²: Cross-validated prediction accuracy of GP surrogates
- Computational efficiency: Ratio of hypervolume achieved to GPU-hours expended
- Cross-domain correlation: Spearman ρ between Pareto frontier shapes across domains

### 2.6 Validation of Interpretability Measure

To validate that MI-based interpretability correlates with human-meaningful interpretability, we conduct:

**Expert Evaluation Study:**
1. Select 10 models spanning the Pareto frontier per domain
2. Generate feature attribution explanations (Integrated Gradients, SHAP)
3. Present explanations to domain experts (n=5 per domain)
4. Collect ratings on explanation quality (1-5 Likert scale)
5. Compute Spearman correlation between $I(m)$ and expert ratings

**Probing Task Validation:**
1. Train linear probes to predict concept presence from representations
2. Compute probe accuracy as alternative interpretability measure
3. Verify correlation with CLUB-based $I(m)$ (expected ρ > 0.7)

### 2.7 Statistical Analysis Plan

**Hypothesis Testing:**
- H1 (Pareto Existence): Bootstrap 95% CI for hypervolume; reject H0 if lower bound > 0.3
- H2 (Surrogate Efficiency): Paired t-test comparing hypervolume at 10% vs 100% compute
- H3 (Cross-Domain Generalizability): Permutation test for Spearman correlation significance

**Sample Size Justification:**
Power analysis indicates n=50 architectures per domain provides 80% power to detect hypervolume differences of 0.15 at α=0.05.

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome:** We expect to demonstrate the existence of a quantifiable Pareto frontier between prediction accuracy and MI-based interpretability across all four scientific domains, with hypervolume indicator > 0.5 (normalized). This would confirm our central hypothesis that scaling creates a fundamental trade-off between predictive power and concept alignment.

**Secondary Outcomes:**
1. Surrogate Pareto Learning will achieve ≥90% of full search hypervolume at ≤10% computational cost, validating the practical utility of our acceleration approach.
2. Qualitatively similar Pareto frontier shapes will emerge across domains (Spearman ρ ≥ 0.7), suggesting domain-general principles governing the scaling-interpretability trade-off.
3. CLUB-based interpretability scores will correlate significantly with expert judgments (ρ ≥ 0.5), validating MI as a meaningful proxy for human-relevant interpretability.

**Potential Negative Results:**
If hypervolume ≤ 0.3 across all domains, this would falsify our hypothesis and suggest that scaling does not systematically reduce interpretability—a finding equally valuable for the field.

### 3.2 Scientific Impact

**Methodological Contribution:** This work establishes the first systematic framework for quantifying and navigating the accuracy-interpretability trade-off in scientific AI. The MI-based interpretability metric provides a domain-agnostic, computationally tractable measure that can be adopted across scientific disciplines.

**Practical Tools:** We will release:
- Open-source implementation of CLUB-based interpretability estimation for scientific domains
- Pre-computed Pareto frontiers for standard benchmarks
- Surrogate models enabling rapid architecture selection without full training

**Theoretical Insights:** Characterizing the Pareto frontier shape provides empirical evidence for understanding how neural network representations relate to human-interpretable concepts as a function of scale, contributing to broader debates about AI alignment and interpretability.

### 3.3 Broader Impact

**For Scientific Discovery:** By enabling scientists to make informed trade-offs between accuracy and interpretability, this framework supports more effective deployment of AI in discovery pipelines. Researchers can select models appropriate to their specific needs—prioritizing interpretability for hypothesis generation or accuracy for high-throughput screening.

**For AI Safety and Alignment:** Understanding how scaling affects alignment with human concepts has implications beyond scientific AI. Our findings may inform strategies for maintaining interpretability in large language models and other scaled AI systems.

**For Resource Efficiency:** The surrogate-accelerated approach reduces computational requirements for architecture search by an order of magnitude, democratizing access to Pareto-optimal model selection for researchers with limited computational resources.

### 3.4 Limitations and Future Directions

**Limitations:**
- CLUB provides an upper bound, not exact MI; future work could explore tighter bounds
- Ontology completeness varies by domain; emerging scientific fields may lack suitable concept vocabularies
- Cross-domain transfer of surrogates remains unexplored

**Future Directions:**
- Extend framework to generative scientific AI (molecular generation, protein design)
- Investigate interventions that shift the Pareto frontier (e.g., concept regularization during training)
- Develop adaptive methods that traverse the frontier during inference based on user requirements

In conclusion, this research addresses a critical challenge in AI for Science by providing the first systematic framework for understanding and navigating the scaling-interpretability trade-off. By enabling scientists to make informed choices along this fundamental dimension, we support the ultimate goal of AI-assisted scientific discovery: not merely accurate predictions, but genuine understanding.