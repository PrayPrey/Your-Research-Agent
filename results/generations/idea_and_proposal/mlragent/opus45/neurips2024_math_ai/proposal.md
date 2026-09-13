# Research Proposal: Adaptive Difficulty Calibration for Mathematical Reasoning Benchmarks via Student-Teacher LLM Dynamics

## 1. Introduction

### Background

Mathematical reasoning represents one of the most challenging frontiers in artificial intelligence research. Unlike pattern recognition tasks where deep learning has achieved remarkable success, mathematical reasoning demands systematic logical deduction, abstract concept manipulation, and multi-step problem solving—capabilities that probe the fundamental nature of machine intelligence. Recent advances in large language models (LLMs) have demonstrated surprising mathematical capabilities, from solving competition-level problems to assisting in theorem proving. However, accurately measuring these capabilities has become increasingly problematic.

Current mathematical reasoning benchmarks face two critical and interrelated challenges. First, **benchmark saturation** occurs when static problem sets become obsolete as models improve, providing diminishing discriminative power at the frontier of model capabilities. Benchmarks like GSM8K and MATH, once considered challenging, now see near-ceiling performance from state-of-the-art models, making it difficult to distinguish genuine advances from incremental improvements. Second, **data contamination** poses existential threats to benchmark validity. With models trained on vast internet corpora, there exists substantial uncertainty about whether test problems—or closely related variants—appeared during training. This conflates memorization with reasoning, undermining our ability to assess true mathematical understanding.

Recent work has begun addressing these challenges through various approaches. RIDE (Li et al., 2025) employs Item Response Theory (IRT) to measure question difficulty and generate harder perturbations through adversarial rewriting. ScaleDiff (Pei et al., 2025) develops pipelines for scaling difficult problem generation using adaptive thinking models. Mathador-LM (Kurtic et al., 2024) introduces dynamic instance generation following target difficulty levels. While these contributions are valuable, they address the problem piecemeal—either focusing on difficulty perturbation, problem scaling, or dynamic generation—without providing a unified framework that simultaneously ensures novelty, calibrated difficulty, and discriminative validity.

### Research Objectives

This research proposes a comprehensive **student-teacher framework** for continuously generating and calibrating mathematical reasoning benchmarks. Our primary objectives are:

1. To develop a systematic methodology for generating novel mathematical problems through compositional combination of atomic concepts, ensuring resistance to contamination.
2. To establish an IRT-based calibration system using diverse "student" LLMs that accurately measures problem difficulty and discriminative power.
3. To create a self-evolving benchmark infrastructure that automatically adapts to the frontier of model capabilities.
4. To provide empirical insights into which mathematical concept combinations most effectively reveal genuine reasoning capabilities versus pattern matching.

### Significance

This research addresses the fundamental question posed by the workshop: "To what extent can machine learning models comprehend mathematics?" By developing robust measurement tools, we enable the research community to track genuine progress in mathematical reasoning. The proposed framework offers practical solutions for benchmark developers, provides diagnostic insights for model developers, and contributes theoretical understanding of the structure of mathematical reasoning difficulty. Furthermore, the methodology has implications for educational applications, where adaptive difficulty calibration could personalize mathematical instruction.

## 2. Methodology

### 2.1 System Architecture Overview

Our framework consists of four integrated components: (1) Concept Graph Construction, (2) Compositional Problem Generation, (3) Multi-Model Difficulty Calibration, and (4) Automated Solution Verification. These components operate in a continuous cycle, generating problems, collecting responses, calibrating difficulty, and filtering for discriminative power.

### 2.2 Concept Graph Construction

We construct a hierarchical mathematical concept graph $G = (V, E, R)$ where vertices $V$ represent atomic mathematical concepts, edges $E$ capture prerequisite relationships, and $R$ defines compositional rules.

**Concept Extraction:** We extract concepts from structured mathematical curricula (K-12 through undergraduate), mathematical ontologies (e.g., Mathematical Subject Classification), and existing benchmark problem annotations. Each concept $c_i \in V$ is represented by:
- A formal definition $d_i$
- Associated operations and procedures $O_i$
- Typical problem templates $T_i$
- Prerequisite concepts $\text{Pre}(c_i) \subset V$

**Relationship Encoding:** Edges encode multiple relationship types:
- Prerequisite edges: $e_{ij}^{pre}$ indicates $c_i$ is required to understand $c_j$
- Composition edges: $e_{ij}^{comp}$ indicates $c_i$ and $c_j$ can be meaningfully combined
- Analogy edges: $e_{ij}^{anal}$ indicates structural similarity between concepts

**Novelty Scoring:** For any concept combination $(c_i, c_j, ..., c_k)$, we compute a novelty score based on co-occurrence frequency in existing benchmarks:

$$\text{Novelty}(c_i, c_j, ..., c_k) = 1 - \frac{\text{count}(c_i \land c_j \land ... \land c_k)}{\min(\text{count}(c_i), \text{count}(c_j), ..., \text{count}(c_k))}$$

High novelty scores indicate concept combinations rarely seen together, reducing contamination risk.

### 2.3 Compositional Problem Generation

The "teacher" component generates problems through structured composition of concepts.

**Generation Algorithm:**

```
Algorithm: ComposeProblem(G, difficulty_target, novelty_threshold)
Input: Concept graph G, target difficulty d*, novelty threshold τ
Output: Novel mathematical problem P

1. Sample seed concept c_0 ~ P(V) weighted by concept centrality
2. Initialize concept set S = {c_0}
3. While |S| < k (composition depth):
   a. For each c in S, retrieve compatible concepts C_c via composition edges
   b. Score candidates by: score(c') = α·Novelty(S ∪ {c'}) + β·DifficultyEstimate(S ∪ {c'})
   c. Sample c* from top candidates, add to S
4. If Novelty(S) < τ, restart from step 1
5. Retrieve problem templates T_S compatible with concept set S
6. Instantiate template with specific values using symbolic constraints
7. Generate problem statement P via teacher LLM with prompt:
   "Create a mathematical problem requiring concepts {S} following template structure {T_S}"
8. Verify problem well-formedness via symbolic solver
9. Return P with ground truth solution
```

**Template Instantiation:** Problem templates define structural patterns (e.g., "find x such that [equation involving concepts]"). We instantiate templates using constraint-based sampling to ensure:
- Numerical values within reasonable ranges
- Unique solutions exist
- No degenerate cases (division by zero, etc.)

### 2.4 Multi-Model Difficulty Calibration via Item Response Theory

We employ a panel of $M$ "student" LLMs spanning diverse architectures and scales: $\{LLM_1, LLM_2, ..., LLM_M\}$. Each model attempts generated problems, producing response data for IRT calibration.

**IRT Model Specification:** We adopt the two-parameter logistic (2PL) IRT model:

$$P(Y_{ij} = 1 | \theta_j, a_i, b_i) = \frac{1}{1 + e^{-a_i(\theta_j - b_i)}}$$

where:
- $Y_{ij}$ indicates whether model $j$ correctly solves problem $i$
- $\theta_j$ represents the latent ability of model $j$
- $b_i$ represents the difficulty of problem $i$
- $a_i$ represents the discrimination parameter of problem $i$

**Parameter Estimation:** We estimate parameters using marginal maximum likelihood with the EM algorithm:

$$\mathcal{L}(\mathbf{a}, \mathbf{b}) = \prod_{i=1}^{N} \int \prod_{j=1}^{M} P(Y_{ij} | \theta_j, a_i, b_i)^{Y_{ij}} (1 - P(Y_{ij} | \theta_j, a_i, b_i))^{1-Y_{ij}} f(\theta_j) d\theta_j$$

**Discriminative Power Filtering:** Problems are retained in the benchmark only if they meet discriminative criteria:

$$\text{DiscriminativePower}(i) = a_i \cdot \text{Var}(\{Y_{ij}\}_{j=1}^{M}) > \delta$$

This ensures problems effectively separate models by ability rather than exhibiting uniform difficulty (too easy or too hard for all models).

### 2.5 Automated Solution Verification

To ensure benchmark integrity, all generated problems undergo automated verification:

**Symbolic Verification Pipeline:**
1. Parse problem into formal representation using semantic parsing
2. Translate to symbolic mathematics system (SymPy/Mathematica)
3. Attempt automated solving to confirm solution existence and uniqueness
4. Cross-validate teacher LLM solution against symbolic solution
5. For problems where symbolic solving fails, employ consensus verification across multiple teacher LLMs with different prompting strategies

**Quality Filtering:** Problems are rejected if:
- Symbolic solver detects inconsistencies or multiple solutions
- Problem statement contains ambiguities (detected via semantic analysis)
- Ground truth solution cannot be verified by at least two independent methods

### 2.6 Experimental Design

**Datasets and Baselines:**
- Existing benchmarks: GSM8K, MATH, MMLU-Math, Mathador-LM
- Generated benchmark: 5,000 problems across 10 mathematical domains
- Student panel: 15 LLMs including GPT-4, Claude-3, Llama-3, Gemini, and various smaller models

**Evaluation Metrics:**

1. **Discriminative Validity:** Correlation between IRT ability estimates and external measures of model capability
2. **Contamination Resistance:** Performance gap between base models and models fine-tuned on benchmark-adjacent data
3. **Saturation Resistance:** Rate at which problems maintain discriminative power as models improve (measured over 6-month period)
4. **Calibration Accuracy:** Correlation between predicted difficulty and observed solve rates on held-out model panel

**Ablation Studies:**
- Impact of concept graph depth on problem novelty
- Comparison of IRT models (1PL, 2PL, 3PL)
- Effect of student panel diversity on calibration quality
- Symbolic vs. LLM-based verification accuracy

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Living Benchmark Infrastructure:** A continuously evolving benchmark that automatically generates calibrated problems as models improve. We anticipate maintaining discriminative power for at least 12 months post-release, compared to typical 3-6 month saturation for static benchmarks.

2. **Contamination-Resistant Evaluation:** Through compositional novelty, we expect generated problems to show less than 5% performance variance between models with different training data exposure, compared to 15-30% variance observed in existing benchmarks.

3. **Diagnostic Concept Maps:** Identification of specific concept combinations that maximally separate reasoning from memorization. Preliminary analysis suggests that cross-domain compositions (e.g., combining geometric reasoning with probabilistic analysis) provide highest discriminative power.

4. **Calibrated Difficulty Scales:** IRT-based difficulty estimates with reliability coefficients exceeding 0.9, enabling precise tracking of model improvement trajectories.

### Broader Impact

**For Benchmark Developers:** Our framework provides a template for creating adaptive benchmarks in other reasoning domains (logical, scientific, commonsense reasoning).

**For Model Developers:** Diagnostic insights reveal specific reasoning gaps, guiding targeted improvements rather than undifferentiated scaling.

**For Educators:** The adaptive difficulty calibration methodology could be applied to personalized mathematics education, dynamically adjusting problem difficulty to student ability—particularly valuable in resource-limited educational contexts.

**For the Research Community:** By providing reliable measurement tools, we enable clearer assessment of whether advances represent genuine progress toward mathematical understanding or sophisticated pattern matching. This directly addresses the workshop's guiding question about machine comprehension of mathematics.

### Limitations and Future Work

We acknowledge that our framework currently focuses on problems with verifiable solutions, excluding open-ended mathematical exploration. Future work will extend to proof-based mathematics and investigate integration with formal verification systems. Additionally, while IRT provides robust psychometric foundations, incorporating more sophisticated models of reasoning processes (e.g., cognitive diagnostic models) could yield finer-grained assessments.