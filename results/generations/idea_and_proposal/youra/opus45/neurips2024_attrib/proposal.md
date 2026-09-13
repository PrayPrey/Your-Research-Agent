# Research Proposal: AttributionBench: A Unified Benchmark for Cross-Paradigm Model Behavior Attribution with Synthetic Ground Truth

## 1. Introduction

### 1.1 Background

The rapid advancement of machine learning has produced models with remarkable capabilities across vision, language, and multimodal domains. However, our understanding of *why* these models behave as they do remains fragmented and incomplete. Model behavior attribution—the task of tracing model outputs back to controllable factors in the ML pipeline—has emerged as a critical research direction with profound implications for model safety, debugging, and scientific understanding.

Currently, three distinct paradigms address different facets of attribution. **Data attribution** methods (e.g., influence functions, TRAK) seek to identify which training examples contribute to specific model behaviors. **Mechanistic interpretability** approaches (e.g., activation patching, distributed alignment search) aim to localize behaviors within model subcomponents such as attention heads or circuits. **Concept-based interpretability** methods (e.g., TCAV, Concept Bottleneck Models) attempt to explain predictions through human-interpretable concepts. Each paradigm provides valuable but partial insights into model behavior.

A fundamental obstacle impedes progress across all three paradigms: the absence of ground truth. When analyzing real-world models trained on internet-scale data, we cannot definitively know which training examples caused a behavior, which circuits implement it, or which concepts mediate it. This ground truth gap creates three critical problems. First, we cannot objectively measure attribution method fidelity—how accurately a method identifies true causal factors. Second, we cannot compare methods across paradigms, as each uses different evaluation protocols. Third, we cannot determine when different attribution approaches should be applied or how their findings relate to each other.

Recent work has begun addressing this challenge within individual paradigms. The Mechanistic Interpretability Benchmark (MIB, ICML 2025) demonstrated that synthetic tasks with known ground truth can effectively evaluate circuit-level attribution methods. CausalGym (2024) established benchmarks for causal interpretability on linguistic tasks. DATE-LM (2025) proposed evaluation frameworks for data attribution in language models. However, no existing benchmark enables cross-paradigm comparison on shared ground truth.

### 1.2 Research Objectives

This research proposes **AttributionBench**, a unified benchmark that enables standardized evaluation of attribution methods across data, mechanistic, and concept paradigms. Our primary objectives are:

1. **Construct synthetic learning tasks** where ground truth attribution pathways are known by design at all three levels simultaneously—which training examples contribute (data), which circuits implement behaviors (mechanistic), and which concepts mediate predictions (concept).

2. **Develop a tiered validation framework** inspired by psychometric measurement theory that evaluates attribution methods at increasing levels of rigor: Tier 1 (basic identification), Tier 2 (specificity/discriminant validity), and Tier 3 (counterfactual prediction accuracy).

3. **Evaluate 6-10 representative attribution methods** spanning all three paradigms on 4-8 synthetic tasks across vision and language modalities, establishing the first cross-paradigm comparison on shared ground truth.

4. **Validate benchmark properties** including ground truth reliability (>95% inter-rater agreement), tier discriminability (meaningful performance differentiation), and ranking stability (Kendall's τ > 0.7 within paradigms).

### 1.3 Significance

AttributionBench addresses a fundamental gap in the model behavior attribution literature. By providing objective ground truth across paradigms, it enables researchers to: (a) select appropriate attribution methods based on validated performance characteristics, (b) understand the relationships between different attribution paradigms, (c) develop improved methods with clear evaluation targets, and (d) build cumulative scientific knowledge about model behavior attribution. The benchmark will accelerate progress toward trustworthy, interpretable AI systems by establishing rigorous evaluation standards for the field.

## 2. Methodology

### 2.1 Synthetic Task Design

The core innovation of AttributionBench is constructing synthetic tasks where ground truth is known by design at all three attribution levels. We achieve this through careful task construction that explicitly controls causal pathways.

#### 2.1.1 Task Construction Principles

Each task follows a three-level causal structure:

**Data Level:** We construct training datasets where specific subsets $\mathcal{D}_k \subset \mathcal{D}$ are causally responsible for specific capabilities $c_k$. For example, in a multi-task image classification setting, images containing feature pattern $\phi_k$ (and only those images) teach the model to recognize concept $k$.

**Mechanistic Level:** We design tasks such that specific circuits $\mathcal{C}_k$ (sets of attention heads, MLP layers, or neurons) are necessary and sufficient for implementing capability $c_k$. This is achieved through modular task design where different capabilities require processing different input features through identifiable pathways.

**Concept Level:** We inject explicit concepts $\mathcal{V}_k$ that mediate between inputs and outputs. These concepts are human-interpretable features (e.g., "has stripes," "contains negation") that are both necessary for correct predictions and recoverable from model representations.

#### 2.1.2 Task Specifications

We propose 4-8 tasks across two modalities:

**Vision Tasks (2-4 tasks):**
- **Modular Feature Classification:** Images contain combinations of synthetic features (shapes, textures, colors). Each feature is introduced by a specific training subset, processed by identifiable circuits, and corresponds to a labeled concept.
- **Compositional Object Recognition:** Objects defined by part-whole relationships where data attribution traces to part examples, circuits implement part detection and composition, and concepts correspond to parts and relations.

**Language Tasks (2-4 tasks):**
- **Syntactic Agreement:** Subject-verb agreement across various syntactic structures. Training subsets introduce specific constructions, circuits implement agreement computation, concepts correspond to grammatical features.
- **Semantic Role Labeling:** Tasks requiring identification of agents, patients, and actions. Data subsets teach specific role patterns, circuits implement role assignment, concepts correspond to semantic roles.

#### 2.1.3 Ground Truth Specification

For each task, ground truth is formally specified as:

$$\mathcal{G} = \{(\mathcal{D}_k, \mathcal{C}_k, \mathcal{V}_k, c_k)\}_{k=1}^{K}$$

where $K$ is the number of capabilities, $\mathcal{D}_k$ is the responsible data subset, $\mathcal{C}_k$ is the implementing circuit, $\mathcal{V}_k$ is the mediating concept set, and $c_k$ is the capability. Ground truth is validated through:

1. **Construction verification:** Confirming that task design enforces intended causal structure
2. **Ablation verification:** Removing $\mathcal{D}_k$ from training eliminates $c_k$; ablating $\mathcal{C}_k$ disrupts $c_k$
3. **Expert annotation:** Three domain experts independently label ground truth; require Cohen's κ > 0.9

### 2.2 Tiered Validation Framework

Inspired by psychometric measurement theory, we evaluate attribution methods at three tiers of increasing rigor:

#### 2.2.1 Tier 1: Identification

**Objective:** Can the method identify *any* relevant attributions?

**Metrics:** 
- Precision: $P_1 = \frac{|A \cap G|}{|A|}$ where $A$ is attributed set, $G$ is ground truth
- Recall: $R_1 = \frac{|A \cap G|}{|G|}$
- F1 Score: $F_1 = \frac{2 P_1 R_1}{P_1 + R_1}$

**Evaluation:** Methods receive full input and must identify contributing factors. This tests basic attribution capability.

#### 2.2.2 Tier 2: Specificity

**Objective:** Can the method distinguish relevant from irrelevant attributions?

**Metrics:**
- Discriminant validity: Attribution scores for true factors vs. matched controls
- Specificity: $S_2 = \frac{TN}{TN + FP}$ where TN = correctly rejected non-factors
- Area Under ROC Curve (AUC) for attribution score distributions

**Evaluation:** Methods must not only identify true factors but also correctly reject plausible but incorrect alternatives (e.g., training examples similar to but not causally responsible for the behavior).

#### 2.2.3 Tier 3: Counterfactual Prediction

**Objective:** Can attribution scores predict the effects of interventions?

**Metrics:**
- Counterfactual accuracy: Correlation between predicted and actual effects of removing/modifying attributed factors
- Intervention prediction error: $E_3 = \mathbb{E}[|\hat{y}_{cf} - y_{cf}|]$ where $\hat{y}_{cf}$ is predicted counterfactual output

**Evaluation:** Given attribution scores, methods must predict how model behavior changes under interventions (data removal, circuit ablation, concept modification). This tests whether attributions capture true causal relationships.

### 2.3 Attribution Methods Under Evaluation

We evaluate 6-10 methods spanning three paradigms:

**Data Attribution (2-3 methods):**
- TRAK (Park et al., 2023): Gradient-based training data attribution
- LoRIF (Grosse et al., 2023): Low-rank influence functions
- Datamodels (Ilyas et al., 2022): Empirical data attribution via retraining

**Mechanistic Interpretability (2-4 methods):**
- Activation Patching (Meng et al., 2022): Localize behaviors via activation interventions
- Distributed Alignment Search (DAS): Supervised circuit discovery
- Sparse Autoencoders (SAE): Unsupervised feature discovery
- Attribution Patching: Gradient-based approximation to activation patching

**Concept-Based Interpretability (2-3 methods):**
- TCAV (Kim et al., 2018): Testing with Concept Activation Vectors
- Concept Bottleneck Models (Koh et al., 2020): Explicit concept layers
- Post-hoc Concept Extraction: Probe-based concept identification

### 2.4 Experimental Design

#### 2.4.1 Models

We evaluate on transformer-based models ≤10B parameters:
- **Language:** GPT-2 (124M, 774M), Pythia (410M, 1.4B, 6.9B), Llama 3.2 (1B, 8B)
- **Vision:** ViT-B/16, ViT-L/16, trained on synthetic tasks

Models are trained from scratch on synthetic tasks to ensure ground truth validity.

#### 2.4.2 Training Protocol

All models follow standardized training:
- Optimizer: AdamW with learning rate 1e-4, weight decay 0.01
- Batch size: 64 (scaled by model size)
- Training steps: Until convergence (validation loss plateau)
- Random seeds: 5 seeds per configuration for variance estimation

#### 2.4.3 Evaluation Protocol

For each (method, task, model, tier) combination:
1. Train model on synthetic task
2. Apply attribution method to test behaviors
3. Compare attributions against ground truth
4. Compute tier-specific metrics
5. Repeat with 5 random seeds

#### 2.4.4 Statistical Analysis

**Primary analyses:**
- Inter-rater reliability: Fleiss' κ for ground truth validation (threshold: κ > 0.9)
- Tier discriminability: Repeated measures ANOVA comparing F1 across tiers (α = 0.05)
- Ranking stability: Kendall's τ for method rankings across tasks (threshold: τ > 0.7)

**Sample size:** n ≥ 20 runs per method-task combination (5 seeds × 4+ model sizes)

**Reporting:** Mean ± standard deviation, 95% confidence intervals, effect sizes (Cohen's d)

### 2.5 Benchmark Validation

We validate AttributionBench itself through:

**V1: Ground Truth Reliability**
- Three expert annotators independently label ground truth for each task
- Compute Fleiss' κ; require κ > 0.9 for all attribution dimensions
- Resolve disagreements through discussion; document edge cases

**V2: Tier Discriminability**
- Test whether method performance differs significantly across tiers
- Expect monotonic decrease: Tier 1 > Tier 2 > Tier 3
- Require p < 0.05 for tier main effect in ANOVA

**V3: Ranking Stability**
- Compute within-paradigm rank correlations across tasks
- Require Kendall's τ > 0.7 for stable rankings
- Identify methods with inconsistent rankings for further analysis

**V4: Known-Result Replication**
- Verify that MIB-established findings replicate (e.g., DAS > SAE on causal localization)
- Require p < 0.05 for expected comparisons
- Discrepancies trigger benchmark review

### 2.6 Implementation Details

**Compute Requirements:**
- Model training: ~1000 GPU-hours (A100) for all models and tasks
- Attribution computation: ~500 GPU-hours for all methods
- Total: ~1500 GPU-hours

**Software:**
- PyTorch for model training
- TransformerLens for mechanistic interpretability
- Custom implementations for data attribution methods
- Scikit-learn for statistical analysis

**Data Release:**
- All synthetic tasks with ground truth labels
- Trained model checkpoints
- Attribution method outputs
- Evaluation scripts and metrics

## 3. Expected Outcomes & Impact

### 3.1 Primary Outcomes

**O1: Validated Benchmark Suite**
We expect to deliver 4-8 synthetic tasks with verified ground truth achieving >95% inter-rater agreement (κ > 0.9) across all three attribution dimensions. This provides the first evaluation framework where attribution methods can be objectively assessed against known causal structure.

**O2: Cross-Paradigm Method Comparison**
The benchmark will produce the first standardized comparison of 6-10 attribution methods across data, mechanistic, and concept paradigms. We expect to identify: (a) which methods achieve highest fidelity within each paradigm, (b) how method performance varies across validation tiers, and (c) relationships between paradigms (e.g., do methods that excel at data attribution also identify relevant circuits?).

**O3: Tiered Validation Framework**
We anticipate demonstrating that psychometric-inspired tiered validation meaningfully differentiates attribution quality. Specifically, we expect methods to show decreasing performance from Tier 1 to Tier 3, with effect sizes (Cohen's d > 0.5) indicating practical significance. This establishes evaluation standards matched to claim strength.

**O4: Method Selection Guidelines**
Based on benchmark results, we will provide practical guidelines for method selection: which methods to use for different attribution questions, at what confidence levels, and with what caveats.

### 3.2 Scientific Impact

**Advancing Attribution Science:** AttributionBench transforms model behavior attribution from a fragmented collection of methods into a unified scientific enterprise with shared evaluation standards. This enables cumulative progress where improvements can be objectively measured.

**Bridging Paradigms:** By evaluating heterogeneous methods on shared ground truth, we can begin understanding how data attribution, mechanistic interpretability, and concept-based explanations relate. This may reveal that different paradigms capture complementary aspects of the same underlying causal structure.

**Methodology Development:** Clear evaluation targets accelerate method development. Researchers can identify specific weaknesses (e.g., poor counterfactual prediction) and develop targeted improvements.

### 3.3 Practical Impact

**Model Debugging:** Validated attribution methods enable practitioners to reliably identify causes of model failures—whether problematic training data, faulty circuits, or missing concepts.

**Safety and Alignment:** Understanding which training data and internal mechanisms produce specific behaviors is essential for AI safety. AttributionBench provides tools to validate attribution methods used in safety-critical applications.

**Regulatory Compliance:** As AI regulation increasingly requires explainability, validated attribution methods provide defensible explanations of model behavior.

### 3.4 Limitations and Future Work

**Scale Transfer:** Results at ≤10B parameters may not fully transfer to frontier models. Future work should extend AttributionBench to larger scales as interpretability tools mature.

**Synthetic-Real Gap:** Synthetic tasks, while enabling ground truth, may not capture all complexities of real-world attribution. Validation studies comparing synthetic and real-world method rankings are needed.

**Task Coverage:** Initial 4-8 tasks cannot cover all attribution challenges. The benchmark should be extended to additional domains (e.g., reinforcement learning, multimodal models).

### 3.5 Timeline

- **Months 1-3:** Task design and ground truth specification
- **Months 4-6:** Model training and ground truth validation
- **Months 7-9:** Attribution method evaluation across all tiers
- **Months 10-12:** Analysis, benchmark validation, and paper preparation

### 3.6 Conclusion

AttributionBench addresses a critical gap in machine learning research by providing the first unified benchmark for evaluating attribution methods across data, mechanistic, and concept paradigms. Through carefully constructed synthetic tasks with known ground truth and rigorous tiered validation, we enable objective comparison of heterogeneous attribution approaches. This work will establish evaluation standards for the field, accelerate method development, and advance our fundamental understanding of how to attribute model behavior to controllable factors in the ML pipeline.