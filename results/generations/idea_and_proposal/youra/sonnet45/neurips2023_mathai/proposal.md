# Research Proposal: Structural Invariance Testing for Measuring Compositional Abstraction in Large Language Models

## 1. Title

**Structural Invariance Testing: A Variance-Based Framework for Measuring Compositional Abstraction in Mathematical Reasoning of Large Language Models**

## 2. Introduction

### Background

Mathematical reasoning represents a cornerstone of human cognition and artificial intelligence research. Recent advances in large language models (LLMs) have demonstrated remarkable performance on mathematical reasoning benchmarks, with some models achieving over 90% accuracy on standardized datasets such as GSM8K and MATH. However, this apparent success masks a critical limitation: current evaluation methodologies cannot distinguish between genuine mathematical understanding and sophisticated pattern memorization.

Recent empirical evidence reveals this evaluation gap. Gulati et al. (2025) demonstrated that state-of-the-art models experience performance drops of up to 19.6% when presented with mathematically equivalent problems that differ only in surface features—semantic context, numerical values, or linguistic expression. Similarly, Parupudi (2025) showed that models exhibit perfect procedural fluency on certain problem types while failing catastrophically on structurally similar problems requiring combinatorial reasoning. These findings suggest that high benchmark accuracy may reflect memorization of surface patterns rather than extraction of deep mathematical structure.

This saturation-without-understanding phenomenon creates three critical problems for the research community:

1. **Benchmark Saturation**: Traditional accuracy metrics plateau while fundamental reasoning capabilities remain brittle, preventing researchers from tracking genuine progress in mathematical reasoning.

2. **Deployment Risk**: Models deployed in educational, scientific, or engineering contexts may fail unpredictably when encountering problems that deviate from training distribution surface features, despite appearing highly capable during evaluation.

3. **Research Misdirection**: Without diagnostic tools that distinguish understanding from memorization, the field risks optimizing for pattern matching rather than compositional abstraction—the ability to extract and manipulate deep mathematical structures independent of surface presentation.

The fundamental challenge is that **accuracy alone cannot distinguish these two mechanisms**. A model that has memorized solution patterns for common problem types and a model that genuinely understands mathematical structure may both achieve 90% accuracy on standard benchmarks, yet exhibit radically different behavior when surface features vary.

### Research Objectives

This research proposes **Structural Invariance Testing (SIT)**, a novel evaluation framework that measures compositional abstraction through performance variance analysis across structural equivalence classes. Our primary objectives are:

**Objective 1: Develop the Abstraction Index (AI) metric** that quantifies performance consistency across problem variants with identical deep mathematical structure but systematic surface variations. The metric is defined as:

$$AI = 1 - \frac{\sigma_{systematic} - \sigma_{stochastic}}{\max(\sigma_{possible})}$$

where $\sigma_{systematic}$ represents performance variance across structural variants, $\sigma_{stochastic}$ captures sampling variability, and $\max(\sigma_{possible})$ normalizes the metric to [0, 1].

**Objective 2: Establish domain-specific protocols** for generating structural equivalence classes across four mathematical domains: arithmetic reasoning, algebraic problem-solving, geometric reasoning, and proof-based tasks. These protocols must preserve deep mathematical structure while systematically varying surface features.

**Objective 3: Validate the framework** through expert assessment, demonstrating that (a) generated variants preserve problem difficulty within ±1 point on expert rating scales, (b) the Abstraction Index correlates with human expert judgments of "understanding," and (c) the framework successfully classifies models into interpretable diagnostic patterns.

**Objective 4: Apply the framework** to evaluate current state-of-the-art LLMs, producing a diagnostic taxonomy that identifies which models exhibit genuine compositional abstraction versus brittle memorization patterns.

### Research Hypothesis

**Core Hypothesis**: LLMs with genuine compositional abstraction capability will demonstrate performance invariance across validated structural equivalence classes (AI > 0.7 when accuracy > 70%), while models relying primarily on pattern memorization will exhibit high accuracy on original problems but low Abstraction Index scores (AI < 0.5), revealing brittleness to surface variations.

**Alternative Hypothesis (H0)**: Performance variance across structural equivalence classes is primarily driven by uncontrolled difficulty drift or stochastic variation rather than differences in compositional abstraction capability.

**Testable Predictions**:
- **P1**: Models with compositional abstraction will show AI > 0.7 on problems where accuracy > 70%
- **P2**: Memorization-dependent models will show accuracy > 70% but AI < 0.5
- **P3**: Expert difficulty ratings will show variance < 1.0 point across equivalence class members
- **P4**: High-capability models will show consistent AI scores (±0.1) across different variant generation protocols for the same problem

### Significance

This research addresses a critical gap in AI evaluation methodology at a time when mathematical reasoning capabilities are increasingly central to LLM applications in education, scientific discovery, software verification, and automated theorem proving. The proposed framework offers three significant contributions:

**Theoretical Significance**: The research operationalizes "compositional abstraction" in computational systems through the structural invariance principle—understanding manifests as invariance to structure-preserving transformations. This provides a rigorous theoretical foundation for distinguishing understanding from memorization at the measurement level.

**Methodological Significance**: The Abstraction Index and structural equivalence class framework introduce a new evaluation paradigm that complements accuracy-based metrics. By systematically controlling for difficulty drift, training data contamination, and stochastic variance, the framework provides a validated diagnostic tool for reasoning capability assessment.

**Practical Significance**: The framework enables benchmark designers to create evaluation sets that resist saturation through memorization, allows model developers to diagnose specific brittleness patterns in their systems, and provides researchers with a tracking mechanism for genuine reasoning progress independent of benchmark-specific optimization.

## 3. Methodology

### Overview

The methodology consists of four integrated components: (1) structural equivalence class generation with domain-specific protocols, (2) expert validation ensuring difficulty preservation and structural fidelity, (3) contamination screening to ensure variant novelty, and (4) variance-based metric computation with statistical decomposition. We describe each component in detail.

### 3.1 Structural Equivalence Class Generation

**Definition**: A structural equivalence class $\mathcal{E}_i$ consists of a set of problems $\{p_{i,1}, p_{i,2}, ..., p_{i,k}\}$ where each problem shares identical deep mathematical structure but exhibits systematic variation in surface features.

**Domain-Specific Protocols**:

**Protocol 1: Arithmetic Word Problems (GSM8K domain)**

For each original problem $p_{i,1}$, generate variants through:

1. **Semantic Context Variation**: Replace problem context while preserving mathematical operations
   - Original: "Sarah has 24 apples and gives 1/3 to her friend..."
   - Variant: "A warehouse contains 24 boxes and ships 1/3 to a customer..."
   - Preserved structure: Division operation, fractional reasoning, subtraction

2. **Numerical Value Variation**: Modify numerical values while preserving computational complexity
   - Constraint: Maintain operation types (addition, multiplication, division)
   - Constraint: Preserve number of computational steps
   - Constraint: Keep numerical magnitudes within same order (e.g., 24 → 36, not 24 → 2400)

3. **Linguistic Expression Variation**: Rephrase problem statement while preserving logical structure
   - Active/passive voice transformation
   - Question format variation (direct vs. indirect)
   - Synonym substitution for non-mathematical terms

**Protocol 2: Algebraic Problem-Solving (MATH algebra subset)**

For algebraic problems, generate variants through:

1. **Variable Notation Variation**: 
   - Original: "Solve for $x$: $2x + 5 = 13$"
   - Variant: "Solve for $y$: $2y + 5 = 13$"
   - Variant: "Solve for $t$: $2t + 5 = 13$"

2. **Coefficient Transformation**: Apply systematic transformations preserving solution structure
   - Linear scaling: $ax + b = c$ → $kax + kb = kc$ (same solution)
   - Structural isomorphism: $2x + 5 = 13$ → $3x + 7 = 19$ (different values, same solution steps)

3. **Representation Format Variation**:
   - Standard form vs. word problem format
   - Graphical description vs. symbolic notation

**Protocol 3: Geometric Reasoning**

1. **Figure Orientation Variation**: Rotate or reflect geometric configurations
2. **Labeling Variation**: Change vertex/side labels while preserving relationships
3. **Measurement Unit Variation**: Convert between metric/imperial while preserving ratios

**Protocol 4: Proof-Based Tasks**

1. **Theorem Statement Variation**: Rephrase theorem using logically equivalent formulations
2. **Notation System Variation**: Use different but equivalent mathematical notation systems
3. **Lemma Ordering Variation**: Present supporting lemmas in different sequences

**Generation Requirements**:
- Minimum $k = 5$ variants per original problem
- At least 2 variants per variation type (semantic, numerical, linguistic)
- Programmatic generation where possible (numerical, notation), manual generation for semantic context

### 3.2 Expert Validation Protocol

**Objective**: Ensure generated variants preserve difficulty and structural equivalence.

**Expert Panel Composition**:
- 3-5 mathematics experts (PhD-level or equivalent)
- Domain expertise matching problem types (arithmetic education specialists, algebra researchers, etc.)
- Inter-rater reliability target: Krippendorff's α > 0.8

**Validation Procedure**:

**Step 1: Difficulty Rating**
Each expert independently rates problem difficulty on a 10-point scale:
- 1-3: Elementary (basic operations, single-step reasoning)
- 4-6: Intermediate (multi-step reasoning, concept integration)
- 7-10: Advanced (complex reasoning, non-standard approaches)

**Step 2: Structural Equivalence Assessment**
Experts assess whether variants preserve mathematical structure:
- Binary judgment: "Does variant require identical solution strategy?" (Yes/No)
- Confidence rating: 1 (uncertain) to 5 (highly confident)

**Step 3: Difficulty Preservation Validation**
For each equivalence class $\mathcal{E}_i$:
$$\text{Difficulty Variance} = \text{Var}(\{d_{i,1}, d_{i,2}, ..., d_{i,k}\})$$

where $d_{i,j}$ is the mean expert difficulty rating for problem $p_{i,j}$.

**Acceptance Criterion**: Difficulty variance < 1.0 point; equivalence agreement > 80% across experts.

**Step 4: Iterative Refinement**
Variants failing validation are revised or replaced. Process repeats until acceptance criteria met.

### 3.3 Contamination Screening

**Motivation**: Ensure variants are not present in model training data, which would confound memorization vs. understanding distinction.

**Screening Protocol**:

**Method 1: N-gram Overlap Detection**
For each variant $p_{i,j}$, extract all n-grams (n = 8, 10, 12) and query against:
- Common Crawl snapshots
- GitHub code repositories
- Mathematics education websites (Khan Academy, AoPS, etc.)
- Known benchmark datasets

**Flagging Criterion**: 
$$\text{Contamination Risk} = \frac{\text{Matching n-grams}}{\text{Total n-grams}} > 0.3$$

**Method 2: Model Perplexity Analysis**
Compute perplexity of problem text under base language model:
$$\text{PPL}(p) = \exp\left(-\frac{1}{N}\sum_{i=1}^N \log P(w_i | w_{<i})\right)$$

Unusually low perplexity (< 10th percentile of distribution) suggests potential training data exposure.

**Method 3: Temporal Validation**
For newly generated variants, timestamp creation and verify post-dates model training cutoff.

**Minimum Requirement**: Each equivalence class must contain at least $k = 3$ variants passing all contamination screens.

### 3.4 Abstraction Index Computation

**Stochastic Variance Measurement**:

For each problem $p_{i,j}$, run model inference $n = 5$ times with temperature $T = 0.7$ to capture sampling variability:

$$\sigma_{stochastic}(p_{i,j}) = \sqrt{\frac{1}{n-1}\sum_{r=1}^n (a_{i,j,r} - \bar{a}_{i,j})^2}$$

where $a_{i,j,r} \in \{0, 1\}$ indicates correctness on run $r$, and $\bar{a}_{i,j}$ is mean accuracy.

**Systematic Variance Measurement**:

For equivalence class $\mathcal{E}_i$, compute mean accuracy per variant:

$$\bar{a}_{i,j} = \frac{1}{n}\sum_{r=1}^n a_{i,j,r}$$

Then compute systematic variance across variants:

$$\sigma_{systematic}(\mathcal{E}_i) = \sqrt{\frac{1}{k-1}\sum_{j=1}^k (\bar{a}_{i,j} - \bar{a}_i)^2}$$

where $\bar{a}_i = \frac{1}{k}\sum_{j=1}^k \bar{a}_{i,j}$ is the mean accuracy across all variants in the equivalence class.

**Abstraction Index Formula**:

$$AI(\mathcal{E}_i) = 1 - \frac{\sigma_{systematic}(\mathcal{E}_i) - \bar{\sigma}_{stochastic}(\mathcal{E}_i)}{\sigma_{max}}$$

where:
- $\bar{\sigma}_{stochastic}(\mathcal{E}_i) = \frac{1}{k}\sum_{j=1}^k \sigma_{stochastic}(p_{i,j})$ is mean stochastic variance
- $\sigma_{max} = 0.5$ is the maximum possible standard deviation for binary outcomes with mean near 0.5

**Interpretation**:
- $AI \approx 1$: Performance variance entirely explained by stochastic sampling (perfect invariance)
- $AI \approx 0$: Maximum systematic variance beyond stochastic noise (high surface sensitivity)
- $AI < 0$: Indicates measurement error or violation of assumptions (flag for review)

**Aggregate Model-Level Metrics**:

For model $M$ evaluated on $N$ equivalence classes:

$$AI_{model}(M) = \frac{1}{N}\sum_{i=1}^N AI(\mathcal{E}_i)$$

$$AI_{conditional}(M | \text{acc} > \theta) = \frac{1}{|\mathcal{S}_\theta|}\sum_{i \in \mathcal{S}_\theta} AI(\mathcal{E}_i)$$

where $\mathcal{S}_\theta = \{i : \bar{a}_i > \theta\}$ restricts to equivalence classes where model achieves accuracy above threshold $\theta$ (e.g., 0.7).

### 3.5 Diagnostic Classification Framework

Based on accuracy and AI scores, classify models into four patterns:

**Pattern 1: Strong Compositional Abstraction**
- Criteria: Accuracy > 70%, AI > 0.7
- Interpretation: Model extracts deep structure, performs consistently across surface variations

**Pattern 2: Brittle Memorization**
- Criteria: Accuracy > 70%, AI < 0.5
- Interpretation: High performance on original problems, but surface-dependent; likely memorization

**Pattern 3: Consistent Reasoning with Capability Gaps**
- Criteria: Accuracy < 70%, AI > 0.7
- Interpretation: Model lacks capability for problem type, but reasoning is structurally consistent

**Pattern 4: Inconsistent Performance**
- Criteria: Accuracy < 70%, AI < 0.5
- Interpretation: Low capability with high variance; unpredictable behavior

### 3.6 Experimental Design

**Phase 1: Protocol Development and Validation (Weeks 1-3)**

- Develop domain-specific variant generation protocols for 4 domains
- Generate pilot set: 30 equivalence classes (10 arithmetic, 10 algebra, 5 geometry, 5 proof)
- Recruit expert panel (n = 3-5 experts)
- Conduct expert validation study
- Measure inter-rater reliability (target: α > 0.8)
- Refine protocols based on validation results

**Phase 2: Benchmark Construction (Weeks 4-7)**

- Select source benchmarks: GSM8K (arithmetic), MATH (algebra, geometry), Putnam subset (proof)
- Generate variants: Target 100 equivalence classes total
  - 40 from GSM8K (arithmetic word problems)
  - 40 from MATH (20 algebra, 15 geometry, 5 proof)
  - 20 from Putnam problems (advanced proof-based)
- Apply contamination screening to all variants
- Ensure minimum k = 3 clean variants per equivalence class
- Final expert validation on full benchmark

**Phase 3: Model Evaluation (Weeks 8-11)**

Evaluate 6-8 models representing different architectures and scales:
- GPT-4, GPT-3.5-turbo (OpenAI)
- Claude 3 Opus, Claude 3 Sonnet (Anthropic)
- Gemini Pro (Google)
- Llama 3 70B, Llama 3 8B (Meta)
- Mistral Large (Mistral AI)

For each model and each problem:
- Run n = 5 inference passes (temperature = 0.7)
- Record binary correctness (exact match for numerical answers, expert grading for proofs)
- Compute stochastic variance per problem
- Compute systematic variance per equivalence class
- Calculate Abstraction Index per equivalence class
- Aggregate to model-level metrics

**Phase 4: Validation Study (Weeks 12-14)**

Correlate AI scores with expert judgments of "understanding":
- Sample 30 equivalence classes spanning AI score range
- Present model outputs to expert panel
- Experts rate "understanding" on 5-point scale:
  - 1: No understanding (random/nonsensical)
  - 2: Surface pattern matching
  - 3: Partial understanding
  - 4: Good understanding with minor gaps
  - 5: Deep understanding
- Compute Spearman correlation between AI scores and expert understanding ratings
- Target: ρ > 0.6 for validation

**Phase 5: Analysis and Reporting (Weeks 15-16)**

- Classify models into diagnostic patterns
- Analyze error patterns for low-AI models (surface feature sensitivity analysis)
- Compare AI scores across domains (arithmetic vs. algebra vs. geometry vs. proof)
- Statistical significance testing (paired t-tests for model comparisons)
- Prepare comprehensive evaluation report

### 3.7 Evaluation Metrics

**Primary Metrics**:
1. **Abstraction Index (AI)**: Per equivalence class and model-level aggregates
2. **Accuracy**: Original benchmark and variant performance
3. **Performance Drop**: $\Delta_{acc} = \text{Acc}_{original} - \text{Acc}_{variants}$

**Validation Metrics**:
1. **Expert Agreement**: Krippendorff's α for difficulty ratings and structural equivalence
2. **Difficulty Preservation**: Variance of expert difficulty ratings per equivalence class
3. **Contamination Rate**: Proportion of variants flagged by screening
4. **AI-Understanding Correlation**: Spearman ρ between AI scores and expert understanding ratings

**Diagnostic Metrics**:
1. **Pattern Distribution**: Proportion of models in each of 4 diagnostic categories
2. **Domain-Specific AI**: AI scores broken down by mathematical domain
3. **Threshold Sensitivity**: AI score stability across different accuracy thresholds

**Statistical Analysis**:
- Paired t-tests comparing AI scores between models
- ANOVA testing AI differences across domains
- Regression analysis: AI ~ model_size + architecture + training_data
- Bootstrap confidence intervals (1000 iterations) for all aggregate metrics

### 3.8 Data and Resources

**Datasets**:
- GSM8K: 8,500 grade school math problems (open source)
- MATH: 12,500 competition mathematics problems (open source)
- Putnam Competition: Historical problems (publicly available)

**Computational Resources**:
- API access to commercial models (GPT-4, Claude, Gemini): ~$500 budget
- Local inference for open models (Llama, Mistral): 1x A100 GPU, ~40 hours compute
- Total compute cost estimate: ~$1,000

**Human Resources**:
- Expert panel: 3-5 experts × 20 hours @ $50-100/hr = $3,000-10,000
- Research assistant for variant generation: 100 hours @ $25/hr = $2,500
- Total human cost estimate: ~$5,500-12,500

**Total Budget Estimate**: $7,000-14,000

## 4. Expected Outcomes & Impact

### Expected Outcomes

**Outcome 1: Validated Measurement Framework**

We expect to deliver a fully validated Structural Invariance Testing framework consisting of:
- Domain-specific variant generation protocols for 4 mathematical domains
- Benchmark of 100 structural equivalence classes with expert validation
- Abstraction Index metric with demonstrated correlation (ρ > 0.6) to expert understanding judgments
- Diagnostic classification system validated on 6-8 state-of-the-art models

**Outcome 2: Empirical Findings on Current Models**

Based on preliminary evidence from Putnam-AXIOM (19.6% performance drops) and systematic diagnosis studies, we predict:

- **High-capability models (GPT-4, Claude 3 Opus)** will show Pattern 1 (strong abstraction) on arithmetic domains (AI > 0.7) but Pattern 2 (brittle memorization) on advanced proof-based tasks (AI < 0.5)
- **Medium-capability models (GPT-3.5, Llama 3 70B)** will show Pattern 2 across most domains, with accuracy > 70% on GSM8K but AI < 0.5
- **Smaller models (Llama 3 8B)** will show Pattern 3 or 4, with lower accuracy but potentially consistent AI scores within their capability range
- **Domain variation**: Arithmetic word problems will show higher AI scores than geometric or proof-based reasoning across all models

**Outcome 3: Diagnostic Insights**

Error analysis of low-AI models will reveal specific surface feature sensitivities:
- Semantic context sensitivity: Performance drops when problem context changes (e.g., apples → boxes)
- Numerical value sensitivity: Performance drops with different numerical values despite identical operations
- Notation sensitivity: Performance drops with variable name changes or alternative mathematical notation

**Outcome 4: Methodological Contributions**

The research will produce:
- Open-source implementation of SIT framework (Python package)
- Public benchmark dataset with 100 equivalence classes
- Detailed protocol documentation for extending framework to new domains
- Validation methodology for future benchmark development

### Impact

**Immediate Impact (1-2 years)**

**For Benchmark Designers**: The framework provides a template for creating evaluation sets that resist saturation through memorization. Future benchmarks can incorporate structural equivalence classes to measure understanding alongside accuracy, extending the useful lifespan of evaluation datasets.

**For Model Developers**: The diagnostic classification system enables targeted improvement. Developers can identify whether their models suffer from brittle memorization (Pattern 2) versus capability gaps (Pattern 3), guiding different intervention strategies (e.g., training data diversification vs. architectural improvements).

**For AI Safety and Deployment**: The framework provides early warning signals for deployment risk. Models with high accuracy but low AI scores may fail unpredictably in real-world contexts where surface features vary, informing deployment decisions in high-stakes applications (education, scientific computing, automated verification).

**Medium-Term Impact (3-5 years)**

**Advancing Evaluation Methodology**: The structural invariance principle may generalize beyond mathematics to other reasoning domains (logical reasoning, causal inference, code generation). The variance-based measurement approach could inspire similar frameworks in other areas where understanding vs. memorization distinction is critical.

**Guiding Research Priorities**: By providing a validated measure of compositional abstraction, the framework enables the research community to track genuine progress in mathematical reasoning independent of benchmark-specific optimization. This may redirect research effort toward methods that improve abstraction capability rather than pattern matching.

**Educational Applications**: The framework could inform development of AI tutoring systems by identifying which problem variations students (and AI tutors) find challenging, enabling adaptive curriculum design that builds robust understanding rather than procedural fluency alone.

**Long-Term Impact (5+ years)**

**Theoretical Understanding**: Systematic application of SIT across models and domains may reveal fundamental principles about how neural networks develop compositional abstractions, informing theoretical understanding of deep learning and potentially inspiring new architectural innovations.

**Human-AI Collaboration**: As AI systems develop stronger compositional abstraction (measurable via increasing AI scores), new forms of human-machine collaboration in mathematics become possible—AI systems that can genuinely assist with mathematical discovery rather than merely pattern-matching to known solution types.

**Broader Scientific Impact**: The principle that understanding manifests as invariance to structure-preserving transformations has deep connections to physics (symmetry principles), cognitive science (transfer learning), and philosophy of science (structural realism). This research may contribute to cross-disciplinary dialogue on the nature of understanding in both biological and artificial systems.

### Limitations and Future Work

**Known Limitations**:
1. Framework requires upfront investment in protocol development and expert validation
2. Scalability to very large benchmarks may require automation vs. manual expert review
3. Framework provides diagnostic tool but cannot explain *why* models lack abstraction (complementary to mechanistic interpretability)
4. Current scope limited to structured mathematical problems; may not extend to open-ended mathematical discovery

**Future Research Directions**:
1. **Automated Variant Generation**: Develop machine learning methods to automatically generate structural equivalence classes, reducing expert labor requirements
2. **Causal Intervention Studies**: Combine SIT with mechanistic interpretability to identify which model components are responsible for abstraction vs. memorization
3. **Training-Time Integration**: Explore using structural equivalence classes during training to improve compositional abstraction
4. **Cross-Domain Extension**: Apply structural invariance principle to code generation, logical reasoning, and scientific problem-solving
5. **Longitudinal Tracking**: Apply SIT framework to track reasoning capability evolution across model generations and training paradigms

### Conclusion

This research addresses a critical gap in AI evaluation at a pivotal moment for mathematical reasoning research. As LLMs approach and exceed human performance on traditional benchmarks, the ability to distinguish genuine understanding from sophisticated pattern memorization becomes essential for scientific progress, safe deployment, and effective application. The Structural Invariance Testing framework provides a principled, validated methodology for making this distinction, with immediate practical value and long-term theoretical significance. By operationalizing compositional abstraction through performance invariance across structural equivalence classes, this work contributes both a measurement tool for current systems and a conceptual framework for understanding the nature of mathematical reasoning in artificial intelligence.