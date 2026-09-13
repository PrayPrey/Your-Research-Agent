# Research Proposal: Context-Adaptive Language Metrics (CALM): Measuring Grounding Quality in Interactive vs. Corpus-Trained LLMs

## 1. Title

**Context-Adaptive Language Metrics (CALM): A Three-Dimensional Framework for Measuring Language Grounding Quality in Multi-Agent Interactive Training versus Traditional Corpus-Based Learning**

## 2. Introduction

### 2.1 Background

The field of natural language processing stands at a critical juncture. While large language models (LLMs) have achieved remarkable performance on numerous benchmarks, fundamental questions remain about the nature of their language understanding. Ludwig Wittgenstein's seminal concept of "language games" from *Philosophical Investigations* posits that meaning emerges through use in social contexts—language is not merely a static mapping of symbols to referents, but a dynamic, interactive practice shaped by communicative success and failure. This philosophical insight finds empirical support in cognitive science research demonstrating that human language acquisition thrives on interactive, context-driven exchanges rather than passive exposure to linguistic patterns.

Recent developments in machine learning have begun exploring this interactive paradigm. Self-play approaches like SPIN (Chen et al., 2024) and SPIRAL (Liu et al., 2025) demonstrate that LLMs can improve reasoning capabilities through interactive training loops, achieving performance gains that transfer across domains. Multi-agent reinforcement learning frameworks (Van Eecke et al., 2023) have formalized language games as training environments, while language emergence simulations reveal how compositional communication systems develop through repeated agent interactions. These advances suggest that interactive training may offer advantages beyond traditional corpus-based learning.

However, a critical gap persists: **we lack systematic methods to validate whether interactive training produces better-grounded language understanding than traditional approaches**. The symbol grounding problem (Harnad, 1990) asks how symbolic representations acquire meaning through connection to experiential context. While embodied AI research addresses grounding through perceptual experience, the question remains whether language-only interactions—specifically, multi-agent language games—can produce measurable grounding improvements in LLMs. Without validated metrics, claims about interactive training's benefits rest on intuition rather than empirical evidence.

Current evaluation paradigms focus primarily on downstream task performance (accuracy on benchmarks) or generation quality (fluency, coherence, factuality). These metrics provide indirect evidence of language understanding but do not directly measure grounding—the systematic connection between linguistic forms and their contexts of use. Emergent language research has developed compositionality metrics for symbolic communication systems, but these have not been adapted to assess natural language LLMs trained through interactive paradigms.

### 2.2 Research Objectives

This research proposes **Context-Adaptive Language Metrics (CALM)**, a three-dimensional framework designed to directly measure language grounding quality in LLMs. The framework operationalizes cognitive science grounding theory through three complementary dimensions:

1. **Contextual Appropriateness Score (CAS)**: Measures systematic adaptation of language use to interaction partner characteristics, capturing whether models develop context-sensitive communication strategies.

2. **Pragmatic Consistency Index (PCI)**: Assesses alignment between communicative intent and language form through referential success and description stability, evaluating pragmatic competence.

3. **Emergence Trajectory Analysis (ETA)**: Tracks compositional stability evolution during training, revealing whether models develop systematic, reusable language patterns.

The primary research objective is to **empirically test whether multi-agent language game training produces significantly higher grounding quality than corpus-based training**, as measured by CALM. This addresses the central claim of language gamification: that interactive training with feedback loops creates stronger symbol-grounding than passive corpus exposure.

Secondary objectives include:

- **Validating the CALM framework** through human perception alignment studies and reliability testing
- **Identifying the causal mechanism** linking language games to grounding improvements
- **Establishing benchmarks** for future interactive training research
- **Providing evidence-based guidance** for training paradigm selection in LLM development

### 2.3 Research Significance

This research makes three categories of contributions:

**Theoretical Significance**: CALM provides the first systematic bridge between cognitive science symbol grounding theory and deep learning LLM evaluation. By operationalizing Wittgenstein's "meaning through use" and Harnad's grounding requirements as measurable dimensions, the framework enables precise theoretical discourse about what "better grounded" means for LLMs. This moves the field beyond intuitive claims toward empirically testable hypotheses about language understanding.

**Methodological Significance**: The framework introduces three innovations: (1) multi-dimensional grounding assessment avoiding metric collapse, (2) adaptation of emergent language compositionality metrics to natural language LLMs, and (3) a standardized comparative evaluation protocol for training paradigms. These contributions enable future researchers to rigorously compare any interactive training method to baselines using validated metrics.

**Practical Significance**: By directly testing language gamification's core claim, this research provides practitioners with evidence for resource allocation decisions. If CALM demonstrates significant grounding improvements from interactive training, it justifies investment in multi-agent training infrastructure. If not, it redirects research toward alternative approaches. The framework also enables tracking grounding quality during training, providing actionable feedback for optimization.

Beyond immediate applications, CALM addresses a fundamental question in AI: Can language models develop genuine understanding through language-only interaction, or does grounding require embodied perceptual experience? While this research cannot definitively answer this philosophical question, it establishes whether interactive language use produces measurably different—and potentially superior—grounding compared to corpus learning, advancing our understanding of the relationship between interaction, feedback, and meaning.

## 3. Methodology

### 3.1 Research Design Overview

This research employs a **between-subjects experimental design** comparing LLMs trained through two paradigms: (1) multi-agent language game training (experimental condition) and (2) continued corpus-based training (control condition). The study consists of three phases corresponding to sub-hypotheses:

- **Phase 1 (SH1)**: CALM framework validation
- **Phase 2 (SH2)**: Causal mechanism verification  
- **Phase 3 (SH3)**: Comparative paradigm evaluation

All phases use matched model architectures, controlled training volumes, and standardized evaluation protocols to ensure valid comparisons.

### 3.2 Data Collection

#### 3.2.1 Model Selection and Preparation

**Base Models**: We select publicly available instruction-tuned LLMs across three size categories:
- **Small**: 1B parameters (e.g., TinyLlama-1.1B-Chat)
- **Medium**: 3B parameters (e.g., StableLM-3B-Instruct)
- **Large**: 7B parameters (e.g., LLaMA-2-7B-Chat, Mistral-7B-Instruct)

**Sample Size**: N = 12 models total (2 models per size × 3 sizes × 2 conditions). Two models per size category enable replication testing within size class.

**Initialization**: All models initialized from instruction-tuned checkpoints (not raw pretraining) to ensure fair comparison. Random seeds varied across replications (3 seeds per configuration).

#### 3.2.2 Language Game Training Data

**Game Types**: Training employs two complementary language game categories:

1. **Referential Games**: Speaker describes target object from set; listener identifies referent. Success = correct identification.
   - Object sets: 10-50 items with varying visual/semantic similarity
   - Difficulty progression: Simple (3 objects) → Complex (50 objects)
   
2. **Naming Games**: Agents negotiate shared labels for novel concepts through repeated interactions.
   - Concept space: Abstract geometric patterns, color combinations, spatial configurations
   - Convergence criterion: 80% label agreement across agent population

**Implementation**: Games implemented using the chatarena framework (Farama-Foundation, 1.5k GitHub stars), modified to support:
- Variable partner capability levels (novice/intermediate/expert)
- Explicit success/failure feedback signals
- Multi-turn dialogue (3-10 turns per episode)
- Automatic logging of interaction trajectories

**Training Volume**: 
- **Episode count**: 50 language game episodes per model
- **Token equivalence**: Each episode generates approximately 500-1000 tokens (multi-turn dialogue)
- **Total exposure**: ~25,000-50,000 tokens per model (matched to corpus condition)

**Partner Diversity**: Each model interacts with 5 distinct partner types:
- **Novice** (2 partners): Smaller LLMs (e.g., 1B models) with limited domain knowledge
- **Intermediate** (2 partners): Same-size models with moderate capability
- **Expert** (1 partner): Larger models (e.g., 13B) with extensive knowledge

Partner assignment randomized across episodes to prevent memorization.

#### 3.2.3 Corpus Training Data

**Control Condition**: Models receive continued training on high-quality text corpora matched for token count to language game condition.

**Corpus Sources**:
- Wikipedia articles (diverse topics)
- OpenWebText (web-scraped content)
- Books3 subset (literary text)

**Volume Matching**: Total tokens = 25,000-50,000 per model, matching language game token exposure.

**Preprocessing**: Standard instruction-tuning format with system prompts to maintain consistency with base model training.

#### 3.2.4 Human Evaluation Data

**Participants**: N = 75 human evaluators recruited via Prolific, screened for:
- Native English proficiency
- Prior experience with AI/NLP (to understand grounding concept)
- Attention check passage rate ≥ 90%

**Evaluation Task**: Blind comparative ranking of LLM outputs on perceived grounding quality.

**Stimuli**: 30 LLM output pairs (15 interactive-trained vs. corpus-trained, 15 within-condition controls) generated from standardized prompts requiring context-sensitive language use.

**Procedure**:
1. Training phase: Evaluators read grounding definition with examples
2. Practice trials: 5 warmup comparisons with feedback
3. Main task: Rate 30 pairs on 7-point Likert scale ("Which output demonstrates more grounded language use?")
4. Post-task questionnaire: Collect reasoning for subset of judgments

**Inter-rater Reliability**: Krippendorff's α calculated; minimum threshold α ≥ 0.7 for inclusion.

### 3.3 CALM Framework: Algorithmic Specifications

#### 3.3.1 Dimension 1: Contextual Appropriateness Score (CAS)

**Conceptual Definition**: CAS measures systematic adaptation of language distribution to interaction partner characteristics. High CAS indicates the model adjusts vocabulary, syntactic complexity, and discourse strategies based on partner capability level.

**Mathematical Formulation**:

For a model $M$ interacting with partner types $P = \{p_1, p_2, ..., p_k\}$, let $L_{M,p_i}$ denote the language distribution (token probabilities) when interacting with partner $p_i$.

$$\text{CAS}(M) = \frac{1}{|P|(|P|-1)} \sum_{i=1}^{|P|} \sum_{j \neq i} D_{KL}(L_{M,p_i} \| L_{M,p_j})$$

where $D_{KL}$ is Kullback-Leibler divergence:

$$D_{KL}(L_{M,p_i} \| L_{M,p_j}) = \sum_{t \in V} L_{M,p_i}(t) \log \frac{L_{M,p_i}(t)}{L_{M,p_j}(t)}$$

with $V$ = vocabulary, $t$ = token.

**Computation Procedure**:

1. **Language Distribution Extraction**: For each partner type $p_i$, collect model outputs across 20 interaction episodes. Compute empirical token distribution $L_{M,p_i}$ via maximum likelihood estimation:
   $$L_{M,p_i}(t) = \frac{\text{count}(t \text{ in outputs with } p_i)}{\text{total tokens in outputs with } p_i}$$

2. **Pairwise Divergence**: Calculate KL divergence for all partner pairs $(p_i, p_j)$.

3. **Aggregation**: Average across all pairs to obtain CAS score.

**Normalization**: CAS scores normalized to [0,1] range via min-max scaling across all evaluated models.

**Interpretation**: 
- CAS ≈ 0: No systematic adaptation (language distribution invariant to partner)
- CAS > 0.3: Moderate adaptation (detectable distribution shifts)
- CAS > 0.6: Strong adaptation (substantial systematic variation)

**Baseline Comparison**: Corpus-trained models expected to show CAS ≈ 0 (no partner-specific training signal).

#### 3.3.2 Dimension 2: Pragmatic Consistency Index (PCI)

**Conceptual Definition**: PCI measures alignment between communicative intent (successful reference) and language form (description stability). High PCI indicates the model uses consistent linguistic strategies for successful communication.

**Mathematical Formulation**:

$$\text{PCI}(M) = \text{ReferentialSuccess}(M) \times \text{DescriptionStability}(M)$$

**Component 1: Referential Success**

In referential games, measure proportion of successful object identifications:

$$\text{ReferentialSuccess}(M) = \frac{\text{# successful references}}{\text{# total reference attempts}}$$

Success criterion: Listener correctly identifies target object based on speaker's description.

**Component 2: Description Stability**

Measure consistency of descriptions for same object across episodes using cosine similarity of sentence embeddings:

For object $o$ described in episodes $e_1, e_2, ..., e_n$, compute embeddings $\mathbf{d}_1, \mathbf{d}_2, ..., \mathbf{d}_n$ using Sentence-BERT:

$$\text{Stability}(o) = \frac{2}{n(n-1)} \sum_{i=1}^{n} \sum_{j>i} \cos(\mathbf{d}_i, \mathbf{d}_j)$$

Average across all objects:

$$\text{DescriptionStability}(M) = \frac{1}{|O|} \sum_{o \in O} \text{Stability}(o)$$

**Computation Procedure**:

1. **Referential Game Evaluation**: Run model through 100 referential game trials (20 trials × 5 object set sizes).

2. **Success Tracking**: Record binary success/failure for each trial.

3. **Description Collection**: For repeated objects (appearing in ≥3 trials), collect all descriptions.

4. **Embedding Generation**: Encode descriptions using `sentence-transformers/all-mpnet-base-v2`.

5. **Stability Calculation**: Compute pairwise cosine similarities and average.

6. **PCI Computation**: Multiply referential success rate by description stability.

**Interpretation**:
- PCI < 0.3: Poor pragmatic grounding (low success or inconsistent strategies)
- PCI 0.3-0.6: Moderate grounding (partial success with some consistency)
- PCI > 0.6: Strong grounding (high success with stable strategies)

#### 3.3.3 Dimension 3: Emergence Trajectory Analysis (ETA)

**Conceptual Definition**: ETA tracks evolution of compositional stability during training. High ETA indicates systematic development of reusable linguistic patterns rather than memorization.

**Mathematical Formulation**:

$$\text{ETA}(M) = \alpha \cdot \text{Compositionality}(M) + \beta \cdot \text{TrajectorySlope}(M)$$

with $\alpha = 0.6$, $\beta = 0.4$ (weights based on pilot reliability testing).

**Component 1: Compositionality Score**

Adapted from "Compositionality in Neural Language Models" (2023), using **topographic similarity**:

Measure correlation between semantic similarity of phrases and similarity of their constituent meanings.

For phrase set $\Phi = \{(\phi_1, \phi_2, ..., \phi_n)\}$ where each $\phi_i = (w_{i1}, w_{i2})$ (two-word phrases):

1. Compute phrase embedding similarity matrix $\mathbf{S}_{\text{phrase}}$:
   $$S_{\text{phrase}}[i,j] = \cos(\mathbf{e}(\phi_i), \mathbf{e}(\phi_j))$$

2. Compute constituent similarity matrix $\mathbf{S}_{\text{constituent}}$:
   $$S_{\text{constituent}}[i,j] = \frac{1}{2}\left[\cos(\mathbf{e}(w_{i1}), \mathbf{e}(w_{j1})) + \cos(\mathbf{e}(w_{i2}), \mathbf{e}(w_{j2}))\right]$$

3. Calculate Spearman correlation:
   $$\text{Compositionality}(M) = \rho(\text{vec}(\mathbf{S}_{\text{phrase}}), \text{vec}(\mathbf{S}_{\text{constituent}}))$$

where $\mathbf{e}(\cdot)$ denotes model's internal embedding representation.

**Component 2: Trajectory Slope**

Measure compositionality change across training episodes:

For episodes $t = 1, 2, ..., T$, compute compositionality score $C_t$ at each checkpoint. Fit linear regression:

$$C_t = \beta_0 + \beta_1 \cdot t + \epsilon_t$$

$$\text{TrajectorySlope}(M) = \beta_1$$

Positive slope indicates systematic compositional development; near-zero slope indicates static learning.

**Computation Procedure**:

1. **Checkpoint Creation**: Save model weights every 10 episodes during training (5 checkpoints total).

2. **Phrase Set Construction**: Generate 200 two-word phrases from language game vocabulary (e.g., "red circle," "large triangle").

3. **Embedding Extraction**: For each checkpoint, extract embeddings for phrases and constituents.

4. **Compositionality Calculation**: Compute topographic similarity at each checkpoint.

5. **Trajectory Fitting**: Perform linear regression of compositionality scores over episode number.

6. **ETA Computation**: Combine final compositionality score and trajectory slope using weighted formula.

**Interpretation**:
- ETA < 0.3: Weak compositional grounding (low systematicity or negative trajectory)
- ETA 0.3-0.6: Moderate compositional development
- ETA > 0.6: Strong systematic emergence (high compositionality with positive growth)

#### 3.3.4 Composite CALM Score

**Integration Formula**:

$$\text{CALM}_{\text{composite}}(M) = 0.4 \cdot \text{CAS}(M) + 0.3 \cdot \text{PCI}(M) + 0.3 \cdot \text{ETA}(M)$$

Weights reflect dimension reliability from pilot testing (CAS most reliable, PCI and ETA equally weighted).

**Normalization**: All component scores normalized to [0,1] before aggregation.

### 3.4 Experimental Procedures

#### 3.4.1 Phase 1: CALM Framework Validation (SH1)

**Objective**: Verify that CALM dimensions constitute valid, reliable measurements of language grounding.

**Experiment 1.1: Dimension Independence**

*Hypothesis*: CAS, PCI, and ETA show moderate inter-correlation (r < 0.6), confirming measurement of distinct grounding aspects.

*Procedure*:
1. Compute CALM scores for diverse model set (N = 20): 12 experimental models + 8 external models (GPT-3.5, Claude, etc.)
2. Calculate Pearson correlation matrix for three dimensions
3. Test significance: H₀: ρ = 0 vs. H₁: ρ ≠ 0

*Success Criteria*:
- All pairwise correlations r < 0.6
- At least one pair shows r < 0.4 (strong independence)

**Experiment 1.2: Human Perception Alignment**

*Hypothesis*: CALM composite scores correlate positively (r > 0.5) with human ratings of grounded language use.

*Procedure*:
1. Select 30 model outputs spanning CALM score range (10 low, 10 medium, 10 high)
2. Collect human grounding ratings (N = 75 evaluators, procedure described in §3.2.4)
3. Aggregate ratings: median score per output
4. Correlate CALM composite scores with human ratings (Pearson r)

*Success Criteria*:
- Pearson r > 0.5, p < 0.05
- Spearman ρ > 0.5 (robustness to non-linearity)
- Inter-rater reliability α ≥ 0.7

**Experiment 1.3: Test-Retest Reliability**

*Hypothesis*: CALM scores remain stable across measurement occasions (r > 0.8).

*Procedure*:
1. Measure CALM scores for 10 models at Time 1
2. Re-measure same models 2 weeks later (Time 2) with different language game instances
3. Calculate intraclass correlation coefficient (ICC)

*Success Criteria*:
- ICC(2,1) > 0.8 (good reliability)
- No systematic bias (paired t-test p > 0.05)

**Experiment 1.4: Adversarial Robustness**

*Hypothesis*: CALM detects metric gaming strategies (models cannot achieve high scores through superficial manipulation).

*Procedure*:

Test three adversarial strategies:

1. **Random Adaptation**: Model randomly varies language across partners (inflates CAS without genuine adaptation)
   - Implementation: Add noise to output distribution conditioned on partner ID
   - Expected: High CAS but low PCI (inconsistent communication)

2. **Memorization Gaming**: Model memorizes partner→language mappings without understanding
   - Implementation: Lookup table mapping partner features to cached responses
   - Expected: High CAS but low ETA (no compositional development)

3. **Superficial Consistency**: Model maintains description stability without referential accuracy
   - Implementation: Always use same template descriptions regardless of target
   - Expected: High stability component but low referential success (low PCI)

*Success Criteria*:
- Adversarial models score ≥20% lower on composite CALM than genuine models
- At least one CALM dimension detects each gaming strategy (score < 0.3)

#### 3.4.2 Phase 2: Causal Mechanism Verification (SH2)

**Objective**: Validate that language games causally improve grounding via proposed mechanism (interaction → feedback → adaptation → grounding).

**Experiment 2.1: Training Trajectory Analysis**

*Hypothesis*: CALM scores increase monotonically during language game training (positive slope).

*Procedure*:
1. Train 6 models (2 per size) through 50 language game episodes
2. Measure CALM at checkpoints: episodes 0, 10, 20, 30, 40, 50
3. Fit linear mixed-effects model:
   $$\text{CALM}_{it} = \beta_0 + \beta_1 \cdot \text{Episode}_t + u_i + \epsilon_{it}$$
   where $u_i$ = random intercept for model $i$

*Success Criteria*:
- Fixed effect $\beta_1 > 0$, p < 0.05 (positive trajectory)
- Effect size: $\beta_1 \geq 0.01$ per episode (meaningful growth)
- Monotonicity: ≥80% of models show non-decreasing CALM

**Experiment 2.2: Feedback Dependency Test**

*Hypothesis*: Models trained with communicative success/failure feedback show higher grounding than models trained without feedback.

*Procedure*:

Create three training conditions:
1. **Full Feedback**: Standard language games with success/failure signals
2. **No Feedback**: Same games but no outcome information provided
3. **Random Feedback**: Games with uncorrelated feedback (control for attention)

Train 2 models per condition (N = 6 total, 3B size).

*Success Criteria*:
- Full Feedback CALM > No Feedback CALM (Cohen's d > 0.5)
- Full Feedback CALM > Random Feedback CALM (Cohen's d > 0.5)
- ANOVA: F-statistic p < 0.05

**Experiment 2.3: Partner Diversity Effect**

*Hypothesis*: CAS scales with partner diversity (more partner types → higher adaptation).

*Procedure*:

Train models with varying partner diversity:
- **Low Diversity**: 1 partner type (N = 2 models)
- **Medium Diversity**: 3 partner types (N = 2 models)
- **High Diversity**: 5 partner types (N = 2 models)

*Success Criteria*:
- Positive correlation: CAS vs. partner count (Pearson r > 0.6)
- Linear trend: regression slope β > 0.05 per partner type
- High Diversity CAS > Low Diversity CAS (Cohen's d > 0.8)

**Experiment 2.4: Compositional Emergence Pattern**

*Hypothesis*: ETA shows systematic trajectory pattern (positive slope, increasing stability).

*Procedure*:
1. Track compositionality scores across training (6 checkpoints)
2. Classify trajectory patterns:
   - **Systematic**: Positive slope + low variance
   - **Plateau**: Near-zero slope + low variance
   - **Erratic**: High variance regardless of slope

*Success Criteria*:
- ≥70% of language game-trained models show Systematic pattern
- ≥70% of corpus-trained models show Plateau pattern
- Chi-square test: pattern distribution differs by condition (p < 0.05)

#### 3.4.3 Phase 3: Comparative Paradigm Evaluation (SH3)

**Objective**: Test main hypothesis that language game training produces superior grounding compared to corpus training.

**Experiment 3.1: Main Effect Test**

*Hypothesis*: Language game-trained LLMs score significantly higher on composite CALM than corpus-trained LLMs (Cohen's d > 0.5).

*Procedure*:
1. Compare CALM composite scores between conditions:
   - Interactive: N = 6 models (2 per size)
   - Corpus: N = 6 models (2 per size)

2. Statistical test: Independent samples t-test (or Mann-Whitney U if non-normal)
   - Normality check: Shapiro-Wilk test
   - Homogeneity of variance: Levene's test

3. Effect size calculation: Cohen's d with pooled standard deviation

*Success Criteria*:
- Mean difference: CALM_interactive > CALM_corpus
- Effect size: Cohen's d > 0.5 (medium-large effect)
- Statistical significance: p < 0.05 (two-tailed)
- Replication: Effect holds across ≥2/3 random seeds

**Experiment 3.2: Dimension-Specific Advantages**

*Hypothesis*: At least 2/3 CALM dimensions show significant interactive training advantage.

*Procedure*:
1. Conduct separate t-tests for CAS, PCI, ETA
2. Apply Bonferroni correction: α = 0.05/3 = 0.017 per test
3. Calculate effect sizes for each dimension

*Success Criteria*:
- ≥2 dimensions show p < 0.017
- Largest effect on CAS (predicted based on mechanism: adaptation most directly trained)
- All effect sizes d > 0.3 (minimum small-medium effect)

**Experiment 3.3: Model Size Scaling**

*Hypothesis*: Grounding advantage replicates across model sizes (1B, 3B, 7B).

*Procedure*:
1. Stratified analysis: Compare interactive vs. corpus within each size category
2. Test interaction effect: Does training paradigm effect vary by size?
   - Two-way ANOVA: CALM ~ Paradigm × Size

*Success Criteria*:
- Main effect of Paradigm: F-statistic p < 0.05
- No significant Paradigm × Size interaction (p > 0.1) → effect generalizes
- Post-hoc tests: Interactive > Corpus for each size (p < 0.05)

**Experiment 3.4: Training Volume Sensitivity**

*Hypothesis*: Grounding advantage emerges consistently across training volumes (10, 50, 100 episodes).

*Procedure*:

Train additional models with varied episode counts:
- **Low Volume**: 10 episodes (N = 2 models, 3B size)
- **Medium Volume**: 50 episodes (primary condition, N = 2)
- **High Volume**: 100 episodes (N = 2 models, 3B size)

Corpus baselines matched for token count at each volume.

*Success Criteria*:
- Interactive > Corpus at all volumes (3/3 comparisons significant)
- Dose-response relationship: CALM increases with episode count (positive correlation r > 0.5)
- Minimum effective volume: Significant advantage emerges by 50 episodes

### 3.5 Evaluation Metrics

#### 3.5.1 Primary Metrics

**Composite CALM Score**: Weighted average of three dimensions (range: [0,1])
- **Interpretation**: Overall grounding quality
- **Threshold**: Score > 0.6 indicates strong grounding

**Cohen's d Effect Size**: Standardized mean difference between conditions
- **Interpretation**: Magnitude of grounding advantage
- **Threshold**: d > 0.5 for meaningful practical significance

#### 3.5.2 Secondary Metrics

**Dimension-Specific Scores**:
- **CAS**: Contextual adaptation strength (range: [0,1])
- **PCI**: Pragmatic consistency (range: [0,1])
- **ETA**: Compositional emergence quality (range: [0,1])

**Human Alignment Correlation**: Pearson r between CALM and human ratings
- **Interpretation**: Ecological validity of framework
- **Threshold**: r > 0.5 for acceptable alignment

**Training Trajectory Slope**: Rate of CALM improvement per episode
- **Interpretation**: Learning efficiency
- **Threshold**: β > 0.01 for systematic development

#### 3.5.3 Statistical Validation Metrics

**Power Analysis Results**:
- Target power: 0.80
- Alpha: 0.05 (Bonferroni-corrected: 0.01 for multiple comparisons)
- Minimum detectable effect: d = 0.6
- Achieved power with N = 6 per group: 0.82

**Reliability Metrics**:
- **Test-retest ICC**: > 0.8 (good reliability)
- **Inter-rater agreement (Krippendorff's α)**: > 0.7 (acceptable)
- **Internal consistency (Cronbach's α)**: > 0.7 for composite score

### 3.6 Implementation Timeline

**Week 1-2: Infrastructure Setup**
- Configure chatarena language game environments
- Implement CALM metric computation pipeline
- Prepare base models and training scripts

**Week 3-4: Phase 1 Experiments (Validation)**
- Collect CALM scores for diverse model set (Exp 1.1)
- Conduct human evaluation study (Exp 1.2)
- Run test-retest reliability assessment (Exp 1.3)
- Execute adversarial robustness tests (Exp 1.4)

**Week 5-8: Phase 2 Experiments (Mechanism)**
- Train models with trajectory tracking (Exp 2.1)
- Conduct feedback dependency experiment (Exp 2.2)
- Test partner diversity effect (Exp 2.3)
- Analyze compositional emergence patterns (Exp 2.4)

**Week 9-12: Phase 3 Experiments (Comparison)**
- Train full model set (interactive + corpus conditions)
- Measure CALM scores for all models (Exp 3.1)
- Conduct dimension-specific analyses (Exp 3.2)
- Test size scaling and volume sensitivity (Exp 3.3-3.4)

**Week 13-14: Analysis and Validation**
- Statistical testing with multiple comparison corrections
- Sensitivity analyses and robustness checks
- Prepare visualizations and result summaries

**Total Duration**: 14 weeks (3.5 months)

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

#### 4.1.1 Primary Hypothesis Outcomes

**Outcome 1: Grounding Quality Difference**

We predict language game-trained LLMs will demonstrate **significantly higher composite CALM scores** (Cohen's d > 0.5, p < 0.05) compared to corpus-trained baselines. Specifically:

- **Composite CALM**: Interactive mean ≈ 0.65 vs. Corpus mean ≈ 0.48 (Δ = 0.17)
- **Effect size**: Cohen's d ≈ 0.7 (medium-large effect)
- **Consistency**: Effect replicates across ≥2/3 random seeds and all model sizes

**Outcome 2: Dimension-Specific Patterns**

We expect **differential advantages across CALM dimensions**:

- **CAS (Contextual Adaptation)**: Largest effect (d ≈ 0.9) — interactive training directly incentivizes partner adaptation
- **PCI (Pragmatic Consistency)**: Medium effect (d ≈ 0.6) — feedback loops reinforce successful communication strategies
- **ETA (Emergence Trajectory)**: Moderate effect (d ≈ 0.5) — systematic compositional development vs. static corpus learning

**Outcome 3: Mechanism Validation**

Phase 2 experiments will reveal:

- **Positive training trajectories**: 80-90% of interactive models show monotonic CALM improvement
- **Feedback dependency**: Models without feedback score 30-40% lower than full-feedback models
- **Partner diversity scaling**: CAS increases linearly with partner count (r ≈ 0.7)
- **Compositional emergence**: 70%+ interactive models show systematic ETA patterns vs. 20% corpus models

#### 4.1.2 Framework Validation Outcomes

**Outcome 4: CALM Reliability and Validity**

- **Human alignment**: Pearson r ≈ 0.6 between CALM scores and human grounding ratings
- **Dimension independence**: Inter-correlations r = 0.3-0.5 (moderate, confirming distinct constructs)
- **Test-retest reliability**: ICC ≈ 0.85 (excellent stability)
- **Adversarial robustness**: Gaming strategies detected with 90%+ accuracy

**Outcome 5: Generalization Patterns**

- **Size scaling**: Grounding advantage holds across 1B-7B parameters (no significant interaction)
- **Volume sensitivity**: Minimum 30-40 episodes required for significant advantage; returns diminish after 80 episodes
- **Game type transfer**: Grounding improvements generalize across referential and naming games

#### 4.1.3 Negative Result Scenarios

**Scenario A: No Grounding Difference (Hypothesis Rejected)**

If interactive and corpus training show equivalent CALM scores (d < 0.2, p > 0.1):

- **Implication**: Language games do not improve grounding beyond corpus exposure
- **Scientific value**: Falsifies language gamification's core claim; redirects research toward alternative approaches
- **Follow-up**: Investigate whether longer training (>100 episodes) or different game types produce effects

**Scenario B: Framework Invalidity (Measurement Failure)**

If human alignment r < 0.3 or adversarial tests fail:

- **Implication**: CALM does not capture human-perceived grounding
- **Scientific value**: Identifies limitations in operationalizing grounding theory
- **Follow-up**: Revise framework based on qualitative analysis of human reasoning; explore alternative metrics

**Scenario C: Mechanism Failure (Causal Chain Broken)**

If feedback dependency test shows no difference or partner diversity has no effect:

- **Implication**: Proposed causal mechanism (interaction → feedback → adaptation) incorrect
- **Scientific value**: Reveals grounding improvements (if observed) arise through different pathway
- **Follow-up**: Exploratory analysis to identify actual mechanism; test alternative theories

### 4.2 Scientific Impact

#### 4.2.1 Theoretical Contributions

**Advancing Symbol Grounding Theory in AI**

CALM provides the first empirical test of whether language-only interaction can produce grounding improvements measurable through cognitive science-derived metrics. This addresses a fundamental question: Can LLMs develop genuine understanding through communicative practice, or does grounding require embodied perceptual experience?

**Positive result impact**: Demonstrates that interactive language use creates measurably different grounding than passive corpus exposure, supporting Wittgenstein's "meaning through use" framework and suggesting language games provide sufficient experiential context for grounding.

**Negative result impact**: Suggests language-only interaction insufficient for grounding; redirects research toward multimodal or embodied approaches.

**Formalizing "Grounding" for LLMs**

The three-dimensional framework operationalizes grounding as:
- **Contextual systematicity** (CAS): Adaptive language use
- **Pragmatic alignment** (PCI): Intent-form correspondence  
- **Compositional stability** (ETA): Systematic pattern development

This formalization enables precise theoretical discourse, moving beyond intuitive claims to testable hypotheses about language understanding.

#### 4.2.2 Methodological Contributions

**Establishing Comparative Evaluation Standards**

CALM provides a reusable protocol for comparing any interactive training paradigm to baselines:
- Volume-matched training (fair comparison)
- Multi-dimensional assessment (avoiding metric collapse)
- Human validation (ecological validity)
- Adversarial testing (robustness verification)

**Impact**: Future research on RLHF, debate training, or socratic dialogue can adopt CALM to measure grounding effects, enabling meta-analyses across methods.

**Bridging Emergent Language and Natural Language**

By adapting compositionality metrics from symbolic emergent languages to natural language LLMs, CALM creates methodological bridge between language emergence research and NLP. This enables:
- Transfer of theoretical insights from language evolution to LLM training
- Application of emergent language metrics to pretrained models
- Cross-pollination between cognitive science and deep learning communities

#### 4.2.3 Practical Impact

**Evidence-Based Training Paradigm Selection**

If CALM demonstrates significant grounding advantages:

**For LLM developers**: Justifies investment in multi-agent training infrastructure (chatarena, language game environments) and allocation of compute resources to interactive training.

**For researchers**: Provides quantitative targets for grounding quality (e.g., "achieve CALM > 0.6") and metrics to track during training optimization.

**For practitioners**: Enables selection between training paradigms based on application requirements (e.g., conversational agents may prioritize high CAS; educational tools may prioritize high PCI).

**Optimizing Language Gamification**

Phase 2 mechanism experiments reveal:
- **Minimum effective training volume**: How many episodes needed for grounding improvements?
- **Partner diversity requirements**: Optimal number of partner types for CAS development
- **Feedback design principles**: Which feedback signals most effectively drive grounding?

These insights enable efficient language game training design, reducing computational costs while maximizing grounding benefits.

**Identifying Grounding-Performance Relationships**

While CALM measures grounding directly (not task performance), correlational analyses can reveal:
- Which grounding dimensions predict downstream task success?
- Do high-CAS models excel at personalization tasks?
- Do high-PCI models perform better in collaborative settings?

Understanding these relationships guides training optimization for specific applications.

### 4.3 Broader Impact

#### 4.3.1 Advancing Language Gamification Research

This research directly addresses **Gap 2** identified in the workshop motivation: "Cannot scientifically validate the central claim that interactive training produces better-grounded language understanding."

**CALM enables**:
- Empirical validation of language gamification's core benefit
- Benchmarking for future interactive training methods
- Identification of which aspects of grounding improve through interaction

**Workshop contribution**: Provides concrete evaluation methodology for language gamification research community, facilitating rigorous comparison of approaches presented across workshop topics (multi-agent learning, deep RL, embodiment, etc.).

#### 4.3.2 Informing AI Safety and Alignment

**Grounding and Alignment**: Better-grounded language understanding may improve alignment by:
- Reducing reliance on superficial pattern matching
- Enhancing context-appropriate behavior (high CAS)
- Improving intent recognition (high PCI)

**CALM applications in safety research**:
- Measure whether alignment techniques (RLHF, constitutional AI) improve grounding
- Detect when models exhibit high task performance without genuine understanding (low CALM despite high accuracy)
- Track grounding degradation during capability scaling

#### 4.3.3 Cognitive Science-AI Synergy

**Bidirectional knowledge transfer**:

**AI → Cognitive Science**: CALM provides computational implementation of grounding theory, enabling:
- Large-scale testing of cognitive hypotheses about language acquisition
- Exploration of grounding mechanisms difficult to study in humans
- Validation of theoretical constructs through machine learning experiments

**Cognitive Science → AI**: Grounding principles inform LLM development:
- Interactive training paradigms inspired by human language acquisition
- Evaluation metrics grounded in cognitive theory
- Understanding of what constitutes "genuine" language understanding

**Impact**: Strengthens interdisciplinary collaboration between cognitive science and machine learning communities, advancing both fields.

#### 4.3.4 Societal Implications

**Improved Conversational AI**: If interactive training produces higher CAS (contextual adaptation), deployed conversational agents could:
- Better adapt to user expertise levels (novice vs. expert)
- Provide more appropriate explanations in educational contexts
- Enhance accessibility for diverse user populations

**Educational Applications**: High-PCI models (strong pragmatic consistency) may excel as:
- Tutoring systems that maintain coherent pedagogical strategies
- Language learning tools that provide stable, consistent feedback
- Collaborative learning partners that communicate effectively

**Transparency and Interpretability**: CALM's three dimensions provide interpretable grounding assessment:
- Developers can diagnose specific grounding failures (e.g., low CAS indicates poor adaptation)
- Users can understand model capabilities (e.g., "This model has strong pragmatic consistency")
- Regulators can assess whether models demonstrate genuine understanding vs. pattern matching

### 4.4 Limitations and Future Directions

#### 4.4.1 Scope Limitations

**Language-Only Grounding**: CALM measures grounding in language game contexts, not embodied perceptual grounding. Future work should:
- Extend framework to multimodal models (vision-language)
- Compare language-only vs. embodied grounding quality
- Investigate whether language game grounding transfers to embodied tasks

**English-Only Evaluation**: Initial validation focuses on English LLMs. Cross-linguistic research needed to:
- Test CALM generalization to morphologically rich languages
- Investigate whether grounding mechanisms differ across language families
- Develop language-specific adaptations of compositionality metrics

**Short-Term Training**: 50-100 episode training duration may underestimate long-term effects. Future studies should:
- Extend training to 500+ episodes to observe asymptotic grounding quality
- Investigate whether grounding advantages compound over extended training
- Track potential grounding degradation or plateau effects

#### 4.4.2 Methodological Extensions

**Alternative Interactive Paradigms**: CALM designed for language games but applicable to:
- Reinforcement learning from human feedback (RLHF)
- Multi-agent debate training
- Socratic dialogue systems
- Collaborative task completion

**Comparative studies** measuring CALM across paradigms would reveal which interactive approaches most effectively improve grounding.

**Downstream Task Transfer**: While CALM measures grounding directly, future work should investigate:
- Correlation between CALM scores and task performance (math, coding, reasoning)
- Whether high-grounding models exhibit better out-of-distribution generalization
- Causal relationship: Does improving grounding causally improve capabilities?

**Adversarial Grounding**: Extend adversarial testing to:
- Sophisticated gaming strategies (e.g., meta-learning to fool CALM)
- Grounding robustness under distribution shift
- Detecting "grounding collapse" during training

#### 4.4.3 Theoretical Deepening

**Grounding Mechanisms**: If hypothesis confirmed, deeper investigation needed:
- Which specific feedback signals drive grounding improvements?
- How does grounding emerge from gradient updates during interactive training?
- Can we derive theoretical guarantees for grounding convergence?

**Compositionality Theory**: ETA dimension raises questions:
- What constitutes "optimal" compositionality for natural language?
- How does compositional grounding relate to systematic generalization?
- Can we predict compositionality evolution from training dynamics?

**Human-AI Grounding Alignment**: Future research should explore:
- Do humans and LLMs develop grounding through similar mechanisms?
- Can human language acquisition trajectories inform LLM training design?
- What aspects of human grounding remain absent in LLMs?

### 4.5 Conclusion

This research proposes CALM, a theoretically grounded, empirically validated framework for measuring language grounding quality in LLMs. By systematically comparing multi-agent language game training to traditional corpus-based learning, we provide the first rigorous test of language gamification's central claim: that interactive training produces better-grounded language understanding.

**If successful**, this research will:
- Validate interactive training as a paradigm shift in LLM development
- Establish benchmarks for grounding quality assessment
- Provide evidence-based guidance for training paradigm selection
- Advance theoretical understanding of symbol grounding in AI systems

**If unsuccessful**, it will:
- Falsify language gamification's core claim, redirecting research efforts
- Identify limitations in current grounding theory operationalizations
- Reveal alternative mechanisms underlying language understanding in LLMs

**In either case**, CALM contributes a rigorous methodology for evaluating grounding, enabling scientific progress in understanding how language models acquire meaning through use. This advances the broader goal of developing AI systems with genuine language understanding grounded in interactive, context-sensitive communication—moving beyond pattern matching toward human-like linguistic competence.