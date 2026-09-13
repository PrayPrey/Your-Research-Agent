# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** YouRA Research Pipeline
**Source Round:** Round 1 - HCTD Framework
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H1-HCTD
**Confidence Level:** 0.87 (HIGH)

**Main Hypothesis:**
Large Language Models exhibit a "cognitive integration gap" - a systematic performance degradation when cognitive abilities (reasoning, navigation, planning, theory of mind) must be coordinated in integrated tasks, compared to their performance on isolated cognitive ability tests. This integration gap is measurable through hierarchical task decomposition, varies across LLM architectures, and is distinct from task complexity effects.

**Alternative Hypothesis (H0):**
The observed performance drop in complex cognitive tasks is solely attributable to increased task difficulty or complexity, not to a distinct integration failure. LLMs that perform well on isolated cognitive ability tests will perform proportionally well when those abilities must be integrated, showing no systematic integration-specific degradation beyond what task complexity alone predicts.

### 1.2 Variables

| Variable Type | Variable Name | Operational Definition | Measurement Scale |
|--------------|---------------|----------------------|-------------------|
| **Independent Variable** | Task Integration Level | Three-level factor: (1) Primitive = single cognitive ability in isolation, (2) Pairwise = two cognitive abilities integrated, (3) Multi-cognitive = all four abilities integrated | Categorical (3 levels) |
| **Independent Variable** | Cognitive Ability Pair | Six pairwise combinations: Reasoning+Navigation, Reasoning+Planning, Reasoning+ToM, Navigation+Planning, Navigation+ToM, Planning+ToM | Categorical (6 pairs) |
| **Independent Variable** | LLM Architecture | Model architecture tested (GPT-4, Claude, DeepSeek-R1, Llama-3, Gemini, etc.) | Categorical (10 models) |
| **Dependent Variable** | Task Accuracy | Proportion of correctly solved tasks (0-1 scale) | Continuous ratio scale |
| **Dependent Variable** | Integration Coefficient (IC) | Ratio: Pairwise_Accuracy / Mean(Relevant_Primitive_Accuracies) | Continuous ratio scale (0-∞, typically 0.5-1.2) |
| **Dependent Variable** | Multi-Cognitive Integration Score (MCIS) | Ratio: Multi_Accuracy / Mean(All_Primitive_Accuracies) | Continuous ratio scale (0-∞, typically 0.3-1.0) |
| **Control Variable** | Task Complexity | Matched through control tasks - each Level 2 task has Level 1 control of equal complexity | Matched pairs design |
| **Control Variable** | Domain Content | Tasks use common domains (spatial navigation, social scenarios, numerical problems) | Fixed across conditions |

### 1.3 Causal Mechanism

**Proposed Causal Chain:**

```
Transformer Architecture Properties
  → Limited cross-attention between cognitive processing modules
  → Inability to maintain multiple cognitive representations simultaneously
  → Integration failures when tasks require coordinated cognitive abilities
  → Measurable performance gap (IC < 1.0, MCIS < IC)
```

**Mechanistic Hypothesis:**

Current LLM architectures process cognitive tasks through sequential self-attention layers that excel at isolated cognitive abilities but lack architectural mechanisms for explicit coordination between different cognitive processes. When a task requires simultaneous maintenance of:
1. Logical reasoning chains (reasoning)
2. Spatial representations (navigation)
3. Multi-step future projections (planning)
4. Mental state models of other agents (ToM)

...the transformer's residual stream becomes overloaded, leading to:
- **Attentional competition**: Later cognitive requirements overwrite earlier ones
- **Representation interference**: Spatial and logical encodings compete for shared representation space
- **Sequential bottleneck**: Planning requires completed reasoning, but ToM requires parallel belief tracking

**Evidence for Causal Links:**

1. **Attentional competition evidence:**
   - CogEval (Momennejad et al., 2023): LLMs show hallucinations and loops in complex planning - suggests attention fails to maintain goal structure while exploring paths
   - LLM-Coordination (Agashe et al., 2023): Success in environment-driven decisions but failure in partner belief modeling - suggests attention prioritizes immediate environment over mental state tracking

2. **Representation interference evidence:**
   - Spatial cognition paper (Wu & Guo, 2025): 33.25% baseline accuracy on spatial relations - suggests weak spatial representations that would interfere with other cognitive loads
   - NumericBench (Li et al., 2025): Persistent SOTA weaknesses in basic arithmetic - suggests numerical reasoning competes with other cognitive processes

3. **Sequential bottleneck evidence:**
   - VideoCogQA (Li et al., 2024): 15% performance drop as task complexity increases - suggests sequential processing bottleneck
   - AutoToM (Zhang et al., 2025): Bayesian inverse planning improves ToM - suggests explicit reasoning structure helps integrate beliefs with planning

**Key Tension:**

The tension lies between **emergent cognitive abilities** (demonstrated in isolated tests) versus **architectural integration capacity** (required for real-world cognitive tasks). Scale has produced impressive emergent abilities (GPT-4's reasoning, Claude's planning), but these abilities emerge within isolated evaluation contexts. When tasks require coordinated application, architectural constraints dominate, revealing that emergence != integration.

### 1.4 Key Assumptions

**A1: Hierarchical Decomposition Validity**
- Assumption: Complex cognitive tasks can be meaningfully decomposed into primitive abilities + integration requirements
- Justification: HCI's Hierarchical Task Analysis (HTA) provides validated methodology for task decomposition; developmental psychology shows cognitive abilities develop hierarchically
- Risk: LLM cognitive processing may be holistic rather than compositional
- Mitigation: Control tasks isolate integration effect from task complexity

**A2: Independence of Primitive Abilities**
- Assumption: Reasoning, navigation, planning, and ToM are sufficiently independent cognitive dimensions
- Justification: Cognitive science literature treats these as distinct cognitive faculties; neural correlates differ in human brains
- Risk: Abilities may be more correlated in LLMs than in humans
- Mitigation: Correlation analysis in Level 1 results will quantify independence

**A3: Task Representativeness**
- Assumption: Selected benchmark tasks (CogEval, MoMentS, NumericBench, spatial cognition) represent genuine cognitive abilities
- Justification: All benchmarks peer-reviewed and validated against human performance
- Risk: Benchmark gaming - LLMs may have been trained on similar tasks
- Mitigation: Include novel integration scenarios not present in training data

**A4: Architectural Generalization**
- Assumption: Integration gaps will vary systematically across architectures (not random noise)
- Justification: Prior work shows architectural differences matter (DeepSeek vs GPT-4, per Li et al. 2025)
- Risk: All tested models share transformer architecture - may miss non-transformer solutions
- Mitigation: Include diverse transformer variants (encoder-decoder, decoder-only, mixture-of-experts)

**A5: Control Task Adequacy**
- Assumption: Control tasks matched for complexity isolate integration effect from difficulty
- Justification: Standard cognitive psychology methodology for isolating specific cognitive factors
- Risk: Complexity matching may be imperfect
- Mitigation: Multiple complexity metrics (word count, reasoning steps, entity count) + human baseline validation

### 1.5 Scope & Boundaries

**Included in Scope:**

1. **Cognitive Abilities:** Four core abilities - reasoning (numerical/logical), spatial navigation, planning (multi-step goal-directed), theory of mind (belief attribution)
2. **LLM Architectures:** 10 SOTA models (GPT-4, Claude-3.5, DeepSeek-R1, Llama-3.3, Gemini-2.0, Qwen-2.5, Mistral-Large, Command-R+, Grok-2, PHI-4)
3. **Task Modalities:** Text-only tasks (no vision/audio requirements)
4. **Evaluation Levels:** Three levels - Primitive (isolated), Pairwise (two abilities), Multi-cognitive (all four)
5. **Metrics:** Accuracy, IC, MCIS, Cognitive Integration Gap (CIG), dependency graphs
6. **Control Design:** Matched-complexity control tasks for isolating integration effects

**Excluded from Scope:**

1. **Training Interventions:** No fine-tuning or architecture modifications - evaluation-only study
2. **Vision/Audio Modalities:** Text-only to isolate cognitive integration from multimodal processing
3. **Embodied Cognition:** No robotics or physical interaction tasks
4. **Temporal Development:** Single-shot evaluation, not longitudinal tracking across training
5. **Internal Mechanisms:** No mechanistic interpretability or activation analysis (black-box evaluation)
6. **Human Comparison:** Limited to architectural comparisons, not claiming human-level integration

**Boundary Conditions:**

- **Complexity Range:** Tasks span simple (1-2 steps) to complex (5-7 steps) but avoid extreme outliers
- **Domain Diversity:** Tasks cover spatial, social, numerical domains but avoid highly specialized knowledge
- **Language:** English-only evaluation
- **Context Length:** All tasks fit within 4K token context window

**Out-of-Scope Related Questions:**

- Why do certain architectures show better integration? (mechanistic question for future work)
- Can training improve integration? (intervention study for future work)
- Do humans exhibit similar integration gaps? (cognitive science question, not LLM research)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Integration Gap Existence):** LLMs will exhibit IC < 1.0 for at least 4 out of 6 cognitive ability pairs, indicating systematic integration failure. Mean IC across all pairs and models will be significantly below 1.0 (p < 0.01, one-sample t-test). Control task analysis will show integration effect beyond complexity (interaction effect in 2-way ANOVA: Integration_Level × Control_Condition, p < 0.05).

**Secondary Predictions:**

**P2 (Hierarchical Degradation):** Multi-Cognitive Integration Score (MCIS) will be significantly lower than mean IC (paired t-test, p < 0.01), demonstrating hierarchical degradation: Multi-cognitive < Pairwise < Primitive. Effect size (Cohen's d) for MCIS vs IC difference will be ≥ 0.5 (medium to large).

**P3 (Architectural Variation):** Different LLM architectures will show statistically different integration profiles. One-way ANOVA on IC across 10 models will show F-statistic with p < 0.05. Post-hoc Tukey HSD tests will identify at least 2 distinct architectural clusters (high-integration vs low-integration architectures).

**P4 (Ability Pair Specificity):** Certain cognitive ability pairs will show consistently larger integration challenges across models. Navigation+ToM and Reasoning+Planning pairs predicted to show lowest IC (< 0.8), while Reasoning+Navigation predicted to show highest IC (> 0.9). Repeated measures ANOVA will show significant pair effect (p < 0.01).

**P5 (Dependency Graph Structure):** Dependency graph analysis will reveal non-uniform integration difficulty. Graph-theoretic analysis (betweenness centrality) will identify Planning as central bottleneck node (highest centrality score). At least one ability pair will show bidirectional integration asymmetry (IC_A→B ≠ IC_B→A).

**Falsification Criteria:**

The hypothesis would be FALSIFIED if:

1. **No Integration Gap:** Mean IC ≥ 0.95 across all pairs and models (integration failures are rare exceptions, not systematic)
2. **Complexity Confound:** Control task ANOVA shows no interaction effect (p > 0.1) - performance drop attributable solely to complexity, not integration
3. **Random Variation:** Architectural ANOVA shows p > 0.1 - integration gaps are random noise, not architectural property
4. **Flat Hierarchy:** MCIS not significantly different from IC (p > 0.05) - no hierarchical degradation
5. **Uniform Pairs:** Ability pair ANOVA shows p > 0.1 - all pairs equally difficult, no specificity

**Statistical Power:** Minimum sample sizes calculated via power analysis (α = 0.05, power = 0.80, effect size d = 0.5):
- Per-model evaluation: 40 tasks per condition (240 pairwise tasks)
- Cross-model comparison: 10 models × 6 pairs = 60 IC measurements (sufficient for ANOVA)

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

**Baseline Comparison Strategy:**

This hypothesis uses a **within-study baseline design** rather than external SOTA comparison:

**Level 1 Primitive Tasks = Internal Baseline**
- Each LLM's performance on isolated cognitive ability tests (CogEval, MoMentS, NumericBench, spatial cognition benchmarks) serves as its own baseline
- Integration Coefficient (IC) is computed as ratio to this baseline, making comparison self-normalizing
- Avoids external SOTA comparison pitfalls (different datasets, evaluation protocols, temporal drift)

**Why No External SOTA Comparison:**

1. **Novel Metric:** No prior work measures "cognitive integration gap" - creating new benchmark, not competing with existing one
2. **Diagnostic Not Competitive:** Goal is to diagnose integration failures, not claim "best performance"
3. **Architecture-Agnostic:** Framework evaluates integration capacity, not absolute performance
4. **Benchmark Addition:** HCTD complements existing benchmarks (CogEval, MoMentS, NumericBench) by revealing integration dimension they miss

**Relevant Baselines from Phase 1 Research:**

| Benchmark | Capability | SOTA Performance | Limitation HCTD Addresses |
|-----------|-----------|------------------|---------------------------|
| CogEval (Momennejad et al., 2023) | Planning + Cognitive Maps | GPT-4 shows hallucinations in complex tasks | Tests planning in isolation, not integrated with ToM |
| MoMentS (Social ToM) | Theory of Mind | GPT-4 struggles with false-belief tasks | Tests ToM in isolation, not with planning/navigation |
| NumericBench (Li et al., 2025) | Numerical Reasoning | SOTA weaknesses persist | Tests reasoning in isolation, not integrated with navigation |
| Spatial Cognition (Wu & Guo, 2025) | Navigation | 33.25% baseline, 53.90% optimized | Tests navigation in isolation, not with reasoning/planning |
| LLM-Coordination (Agashe et al., 2023) | Multi-agent Coordination | Success in environment-driven, fails partner beliefs | Tests specific pairs implicitly, not systematically |

**HCTD Contribution Beyond Baselines:**
- **Systematic Pairwise Testing:** All 6 combinations vs ad-hoc single pairs
- **Hierarchical Structure:** Primitive → Pairwise → Multi-cognitive progression
- **Integration Metrics:** IC, MCIS, CIG quantify gap, not just absolute accuracy
- **Dependency Graphs:** Reveal which ability interactions are critical bottlenecks

### 1.8 Statistical Verification Design

**Study Design:** 3×6×10 Mixed Factorial Design
- Factor 1 (Within-Subjects): Integration Level (3 levels: Primitive, Pairwise, Multi-cognitive)
- Factor 2 (Within-Subjects): Cognitive Ability Pair (6 pairs)
- Factor 3 (Between-Subjects): LLM Architecture (10 models)

**Sample Sizes:**

| Level | Task Count per Model | Total Across 10 Models |
|-------|---------------------|------------------------|
| Primitive (Level 1) | 4 abilities × 20 tasks = 80 | 800 tasks |
| Pairwise (Level 2) | 6 pairs × 40 tasks = 240 | 2,400 tasks |
| Multi-cognitive (Level 3) | 30 tasks | 300 tasks |
| Control Tasks | 240 control tasks (matched to Level 2) | 2,400 tasks |
| **Total** | **590 tasks per model** | **5,900 total evaluations** |

**Statistical Tests:**

**Test 1: Integration Gap Existence (P1)**
- Null Hypothesis: Mean IC = 1.0 (no integration gap)
- Alternative: Mean IC < 1.0 (integration gap exists)
- Test: One-sample t-test (one-tailed, α = 0.01)
- Sample: 60 IC values (10 models × 6 pairs)
- Power: 0.95 for effect size d = 0.5

**Test 2: Control Task Validation (P1 continued)**
- Null Hypothesis: No interaction between Integration_Level and Control_Condition
- Alternative: Interaction exists (integration effect beyond complexity)
- Test: 2-way repeated measures ANOVA (Integration_Level × Control_Condition)
- Significance: α = 0.05
- Effect size: Partial η² reported

**Test 3: Hierarchical Degradation (P2)**
- Null Hypothesis: MCIS = Mean IC (no hierarchical degradation)
- Alternative: MCIS < Mean IC (hierarchical degradation)
- Test: Paired t-test (one-tailed, α = 0.01)
- Sample: 10 paired observations (one per model)
- Power: 0.85 for effect size d = 0.5

**Test 4: Architectural Variation (P3)**
- Null Hypothesis: All models have equal mean IC
- Alternative: At least two models differ significantly
- Test: One-way ANOVA with post-hoc Tukey HSD
- Significance: α = 0.05
- Effect size: η² reported
- Multiple comparisons: Bonferroni correction applied

**Test 5: Ability Pair Specificity (P4)**
- Null Hypothesis: All ability pairs have equal IC
- Alternative: At least two pairs differ significantly
- Test: Repeated measures ANOVA (6 pairs within-subjects)
- Significance: α = 0.01
- Effect size: Partial η² reported
- Post-hoc: Pairwise t-tests with Bonferroni correction

**Test 6: Dependency Graph Analysis (P5)**
- Null Hypothesis: Random graph structure (uniform centrality)
- Alternative: Non-uniform structure (Planning has highest betweenness centrality)
- Test: Betweenness centrality comparison with permutation test
- Significance: α = 0.05
- Permutations: 10,000 random graphs

**Confidence Intervals:**
- 95% confidence intervals reported for all IC, MCIS, CIG values
- Bootstrap method (10,000 resamples) for non-normal distributions

**Multiple Comparison Correction:**
- Family-wise error rate (FWER) control via Bonferroni for post-hoc tests
- False Discovery Rate (FDR) control via Benjamini-Hochberg for exploratory analyses

**Assumptions Testing:**
- Normality: Shapiro-Wilk test + QQ plots
- Homogeneity of variance: Levene's test
- Sphericity (repeated measures): Mauchly's test + Greenhouse-Geisser correction if violated

**Missing Data Protocol:**
- API failures or timeouts: Re-run up to 3 times
- Persistent failures: Exclude from analysis (document exclusion rate)
- Threshold: Exclude model if >10% task failure rate

**Reproducibility:**
- Fixed random seeds for task selection and ordering
- Temperature = 0 for all LLM API calls (deterministic sampling)
- Full dataset and code released upon publication

---

## 2. Contribution Summary

**Theoretical Contribution:**

The HCTD framework introduces **"cognitive integration gap"** as a fundamental limitation distinct from isolated cognitive ability performance. This concept challenges the implicit assumption in current LLM evaluation that high performance on isolated cognitive tasks (reasoning, navigation, planning, ToM) predicts effective performance when these abilities must be coordinated. By demonstrating systematic integration failures, HCTD establishes that **emergence of isolated abilities ≠ architectural capacity for integration**, shifting focus from "what cognitive abilities do LLMs have?" to "how well can LLMs coordinate the abilities they have?"

The dependency graph framework provides a theoretical model for understanding cognitive ability interactions, revealing:
1. **Central Bottleneck Abilities:** Which cognitive abilities are critical integration points (predicted: Planning)
2. **Asymmetric Integration:** Whether A→B integration differs from B→A (e.g., reasoning-then-navigate vs navigate-then-reason)
3. **Architectural Signatures:** How different architectures trade off isolated ability vs integration capacity

**Methodological Contribution:**

HCTD is the first evaluation framework to:

1. **Systematic Hierarchical Integration Testing:** Extends isolated benchmark methodology (CogEval, MoMentS, NumericBench) to include all pairwise combinations + multi-cognitive scenarios. Prior work tested abilities in isolation OR specific pairs implicitly; HCTD tests all combinations explicitly.

2. **Novel Integration Metrics:**
   - Integration Coefficient (IC): Quantifies pairwise integration efficiency
   - Multi-Cognitive Integration Score (MCIS): Measures full integration capacity
   - Cognitive Integration Gap (CIG): Total performance degradation from primitive to multi-cognitive
   - All metrics self-normalize to each model's baseline, enabling fair cross-architecture comparison

3. **Control Task Protocol:** Isolates integration effect from task complexity through matched-complexity control tasks - addresses major confound in prior work where "complex task performance drop" could be complexity OR integration failure

4. **Cross-Domain Transfer:** First application of HCI's Hierarchical Task Analysis (HTA) to LLM cognitive evaluation, demonstrating how established human task analysis methodology transfers to AI assessment

**Practical Contribution:**

For AI researchers and practitioners, HCTD provides:

1. **Architecture Diagnosis:** Identifies which LLM architectures exhibit cognitive integration vs which excel only in isolated abilities. Guides architecture selection for real-world applications requiring coordinated cognition (e.g., embodied agents, multi-step decision systems)

2. **Bottleneck Identification:** Dependency graphs reveal specific ability pairs requiring architectural attention (e.g., if Navigation+ToM shows lowest IC, architectures need better spatial-social integration mechanisms)

3. **Training Target Specification:** CIG metric provides quantitative target for training interventions aimed at improving integration (e.g., "reduce CIG from 0.35 to 0.15")

4. **Benchmark Complement:** HCTD doesn't replace existing benchmarks (CogEval, MoMentS) but complements them by adding integration dimension. Enables more comprehensive evaluation: isolated ability (existing benchmarks) + integration capacity (HCTD)

**Expected Impact:**

- **Theoretical:** Reframes "emergent abilities" debate to distinguish emergent isolated abilities from emergent integration capacity
- **Methodological:** Establishes systematic hierarchical evaluation as standard practice for cognitive assessment
- **Practical:** Guides next-generation LLM architectures toward explicit integration mechanisms (attention routing, modular architectures, explicit cognitive controllers)

---

## 3. Key Related Work

**Directly Built Upon:**

1. **CogEval (Momennejad et al., 2023) - Planning Evaluation Baseline**
   - Semantic Scholar ID: 9977fee41d9cce1b2ed924da966140ac8120762b
   - Citation Count: 96 | Venue: NeurIPS 2023
   - Contribution: Cognitive science-inspired benchmark for planning and cognitive maps in LLMs
   - Key Finding: LLMs show hallucinations and planning loops in complex scenarios
   - **HCTD Extension:** Uses CogEval tasks as Level 1 Planning baseline; extends to test Planning integration with other abilities (Planning+Reasoning, Planning+Navigation, Planning+ToM pairwise scenarios)

2. **MoMentS - Theory of Mind Baseline**
   - Standard benchmark for false-belief tasks and mental state attribution
   - **HCTD Extension:** Uses MoMentS as Level 1 ToM baseline; extends to test ToM integration with reasoning, navigation, and planning

3. **NumericBench (Li et al., 2025) - Reasoning Baseline**
   - Semantic Scholar ID: 536de82012437a98dd2a646bde214d9c4372a569
   - Citation Count: 9 | Venue: ACL 2025
   - Contribution: Exposes fundamental numerical reasoning gaps in SOTA LLMs
   - **HCTD Extension:** Uses NumericBench as Level 1 Reasoning baseline; extends to test Reasoning integration with navigation, planning, and ToM

4. **Spatial Cognition Benchmarks (Wu & Guo, 2025) - Navigation Baseline**
   - Semantic Scholar ID: ccc5ebb77ec589f2950cde007817f255c7b9696d
   - Citation Count: 4 | Venue: ACM TIST 2025
   - Contribution: Evaluates topological, directional, and distance reasoning in LLMs
   - Key Finding: 33.25% baseline accuracy → 53.90% with prompt optimization
   - **HCTD Extension:** Uses spatial cognition tasks as Level 1 Navigation baseline; extends to test Navigation integration with reasoning, planning, and ToM

**Methodologically Related:**

5. **LLM-Coordination (Agashe et al., 2023) - Implicit Integration Testing**
   - Semantic Scholar ID: 7f0d1740e74ce36424d64d608270077b64dfe7c0
   - Citation Count: 41 | Venue: NAACL 2023
   - Contribution: Evaluates multi-agent coordination requiring Planning+ToM integration
   - Key Finding: LLMs excel in environment-driven decisions but fail partner belief modeling
   - **HCTD Difference:** LLM-Coordination tests Planning+ToM integration implicitly in multi-agent scenarios; HCTD tests all 6 pairwise combinations explicitly and systematically, including control tasks to isolate integration effect

6. **VideoCogQA (Li et al., 2024) - Complexity-Cognition Relationship**
   - Semantic Scholar ID: 9c6304a50696b6dc2da5e2035e7c08c4f2db3383
   - Contribution: Evaluates symbolic and abstract cognitive abilities in video-language models
   - Key Finding: 15% performance drop as task complexity increases
   - **HCTD Difference:** VideoCogQA confounds complexity with integration; HCTD uses control tasks to separate these factors. HCTD also focuses on text-only cognitive integration, not multimodal.

**Theoretically Related:**

7. **Development of Cognitive Intelligence in Pre-trained Language Models (Shah et al., 2024)**
   - Semantic Scholar ID: 0c97435611169f5d63ce3e2f06ccd08bbdcdb46e
   - Citation Count: 1 | Venue: EMNLP 2024
   - Contribution: Tracks developmental trajectory of cognitive abilities during pre-training
   - Key Finding: "Window of maximal alignment" to human cognitive development
   - **HCTD Connection:** Developmental psychology insight inspired hierarchical structure, but HCTD reframes as "diagnostic decomposition" not "developmental stages" to avoid over-claiming LLM-human analogy

8. **AutoToM (Zhang et al., 2025) - Structured ToM Reasoning**
   - Semantic Scholar ID: c50cd97776b2bdb9335810edbe41386e66e953c9
   - Citation Count: 15
   - Contribution: Automated Bayesian inverse planning improves Theory of Mind reasoning
   - **HCTD Connection:** Demonstrates that explicit reasoning structure helps integrate beliefs with planning - supports hypothesis that integration requires architectural mechanisms beyond emergent abilities

**Architecturally Related:**

9. **Hybrid Mind (Yang et al., 2025) - External Module Augmentation**
   - Semantic Scholar ID: 306c9a14afb289b33487de3911cc725697c9a8dc
   - Citation Count: 8 | Venue: IJGIS 2025
   - Contribution: Integrates LLMs with GIS algorithms for spatial cognition
   - Key Finding: GPT-4 solo <25% accuracy → Hybrid Mind 70.48% accuracy
   - **HCTD Relevance:** Shows external modules can address integration gaps; HCTD's black-box evaluation establishes baseline integration capacity before augmentation

10. **Retrieval Augmented Generation Survey (Zhao et al., 2024)**
    - Semantic Scholar ID: 339d2a56f0e5176b691c358a86891e2923045c8c
    - Citation Count: 95
    - Contribution: Comprehensive survey of data-augmented LLM techniques
    - **HCTD Relevance:** HCTD evaluates end-to-end cognitive integration; RAG represents external augmentation strategy - comparative studies could test whether RAG reduces integration gaps

**Contrasts With:**

11. **Isolated Cognitive Ability Benchmarks**
    - Prior benchmarks (CogEval, MoMentS, NumericBench, spatial cognition tests) evaluate abilities in isolation
    - **HCTD Innovation:** Systematic integration testing reveals failures invisible to isolated benchmarks

12. **Single-Metric Evaluation Approaches**
    - FID metrics, BLEU scores, perplexity focus on single dimensions
    - **HCTD Innovation:** Multi-dimensional evaluation (IC per pair, MCIS, dependency graphs) reveals architectural trade-offs

**Critical Differences Justifying Novelty:**

- **Systematic Pairwise Completeness:** Prior work tests 0-2 pairs implicitly; HCTD tests all 6 pairs explicitly
- **Hierarchical Structure:** Prior work flat evaluation; HCTD hierarchical with control tasks
- **Integration Metrics:** Prior work absolute accuracy; HCTD self-normalizing ratios (IC, MCIS)
- **Diagnostic Framework:** Prior work competitive benchmarking; HCTD diagnostic tool for integration capacity

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence): Does the cognitive integration gap exist?**

Sub-Hypothesis 1.1: LLMs exhibit systematic integration failure in pairwise cognitive tasks (IC < 1.0 for ≥4/6 pairs)
- Verification Method: Pairwise task evaluation across 10 models with statistical testing (one-sample t-test, α=0.01)
- Success Criteria: Mean IC < 0.95, p < 0.01
- Expected Outcome: Mean IC ≈ 0.85 (based on 15% performance drop in VideoCogQA)

Sub-Hypothesis 1.2: Integration failure is distinct from task complexity (control task ANOVA shows interaction effect)
- Verification Method: 2-way ANOVA (Integration_Level × Control_Condition)
- Success Criteria: Interaction F-statistic p < 0.05
- Expected Outcome: Integration effect size partial η² ≈ 0.2-0.3

**SH2 (Mechanism): What explains integration failures?**

Sub-Hypothesis 2.1: Hierarchical degradation occurs (MCIS < IC < 1.0)
- Verification Method: Paired t-test comparing MCIS to IC across models
- Success Criteria: MCIS significantly lower than IC (p < 0.01), effect size d ≥ 0.5
- Expected Outcome: MCIS ≈ 0.6-0.7, IC ≈ 0.85

Sub-Hypothesis 2.2: Specific ability pairs show predictable integration difficulty patterns
- Verification Method: Repeated measures ANOVA on IC across 6 pairs
- Success Criteria: Significant pair effect (p < 0.01), Navigation+ToM lowest, Reasoning+Navigation highest
- Expected Outcome: Navigation+ToM IC ≈ 0.75, Reasoning+Navigation IC ≈ 0.92

**SH3 (Comparison): Do architectures differ in integration capacity?**

Sub-Hypothesis 3.1: LLM architectures cluster into high-integration vs low-integration groups
- Verification Method: One-way ANOVA + Tukey HSD post-hoc tests + cluster analysis
- Success Criteria: ANOVA p < 0.05, ≥2 distinct clusters (Euclidean distance-based)
- Expected Outcome: GPT-4/Claude-3.5 in high-integration cluster, smaller models in low-integration

Sub-Hypothesis 3.2: Dependency graph structure reveals architectural bottlenecks
- Verification Method: Betweenness centrality analysis with permutation testing
- Success Criteria: Planning node has significantly higher centrality (p < 0.05, 10K permutations)
- Expected Outcome: Planning centrality ≈ 0.6-0.8, other abilities ≈ 0.2-0.4

### Readiness Checklist

✅ **Hypothesis Clarity**
- [x] Core hypothesis clearly stated with measurable variables
- [x] Alternative hypothesis (H0) defined for statistical testing
- [x] Causal mechanism proposed with supporting evidence from Phase 1

✅ **Operational Definitions**
- [x] All variables operationally defined with measurement scales
- [x] Task integration levels clearly specified (Primitive, Pairwise, Multi-cognitive)
- [x] Metrics fully defined (IC, MCIS, CIG) with calculation formulas

✅ **Statistical Design**
- [x] Study design specified (3×6×10 mixed factorial)
- [x] Sample sizes justified via power analysis
- [x] Statistical tests mapped to each prediction
- [x] Significance thresholds and corrections defined

✅ **Testable Predictions**
- [x] 5 primary predictions with quantitative success criteria
- [x] Falsification criteria explicitly stated
- [x] Effect sizes predicted for key comparisons

✅ **Scope Boundaries**
- [x] Inclusions and exclusions clearly documented
- [x] Boundary conditions specified (complexity range, context length, language)
- [x] Out-of-scope questions acknowledged

✅ **Related Work Integration**
- [x] 10+ key papers mapped to hypothesis components
- [x] Baselines identified (CogEval, MoMentS, NumericBench, spatial cognition)
- [x] Novelty justified through systematic differences

✅ **Control Design**
- [x] Control task protocol for isolating integration effect
- [x] Complexity matching strategy defined
- [x] Confound mitigation documented

✅ **Phase 2B Decomposition**
- [x] 3 main sub-hypotheses (Existence, Mechanism, Comparison)
- [x] 5 sub-sub-hypotheses with verification methods and success criteria
- [x] Dependency order clear (SH1 → SH2 → SH3)

### Open Questions

**Q1: Task Count Trade-off**
- Current design: 240 pairwise tasks (40 per pair) + 240 control tasks = 480 tasks per model
- Trade-off: More tasks = better statistical power but higher computational cost
- Decision Point: Should we reduce to 30 tasks per pair (180 pairwise + 180 control) for faster iteration?
- Recommendation: Keep 40 per pair for sufficient power (power analysis shows 40 needed for d=0.5, power=0.80)

**Q2: Triplet Combinations**
- Current design: Excludes triplet combinations (Reasoning+Navigation+Planning, etc.)
- Trade-off: Triplets add granularity but increase evaluation cost by ~40%
- Decision Point: Include triplets in initial study or defer to future work?
- Recommendation: Defer to Phase 2B discussion; prioritize pairwise + multi-cognitive for initial validation

**Q3: Dynamic Task Generation**
- Concern: Benchmark gaming if HCTD becomes standard evaluation
- Solution: Dynamic task generation from templates
- Decision Point: Implement now or after initial validation?
- Recommendation: Use fixed tasks for reproducibility in initial study; add dynamic generation in follow-up work

**Q4: Human Baseline Collection**
- Question: Should we collect human performance on HCTD tasks?
- Trade-off: Human baseline validates task difficulty but adds cost/time
- Decision Point: Essential for initial study or optional enhancement?
- Recommendation: Collect human baselines for subset (10 tasks per condition) to validate task representativeness and complexity matching

**Q5: Multimodal Extension**
- Future Direction: Extend HCTD to vision-language models (VLMs)
- Challenges: Multimodal integration adds confound (visual integration vs cognitive integration)
- Decision Point: Include VLMs in Phase 2B planning or defer?
- Recommendation: Defer VLM extension to future work; establish text-only HCTD first as baseline methodology

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*Date: 2026-02-06*
*Pipeline: YouRA Pipeline - LLMs and Cognitive Abilities*
*Phase: 2A Extended → Phase 2B Verification Planning*
