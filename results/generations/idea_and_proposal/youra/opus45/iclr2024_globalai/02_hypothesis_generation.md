# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - FEASIBLE)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-FCEN-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under the condition of globally-deployed generative AI requiring cross-cultural evaluation, **IF** we implement a Federated Cultural Evaluation Network (FCEN) with:
1. Distributed Cultural Evaluation Nodes (CENs) operated by trained participatory mediators
2. A bottom-up Shared Cultural Ontology (SCO) extending Wikidata
3. A Federated Aggregation Protocol (FAP) with psychometric invariance testing

**THEN** we will achieve scalable cultural inclusiveness assessment with higher validity than centralized benchmarks (measured by user satisfaction correlation > 0.7)

**BECAUSE** local cultural communities possess the epistemic authority to validate AI outputs for their own contexts, while federated aggregation with Differential Item Functioning (DIF) analysis enables meaningful global comparison without imposing Western-centric evaluation criteria.

**Alternative Hypothesis (H0):**
There is no significant difference in cultural evaluation validity between FCEN's distributed architecture and centralized benchmark approaches; alternatively, centralized expert-designed benchmarks achieve equal or higher correlation with local user satisfaction than community-validated federated evaluation.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| FCEN_architecture | Independent | Presence (treatment) vs. absence (control: centralized benchmark) | Binary: 0/1 |
| Cultural_region_count (N) | Independent | Number of cultural regions with active CENs | 5-50 regions |
| Mediator_training_quality | Independent | Standardized curriculum completion rate × quality assessment score | 0-100% |
| Cultural_Inclusiveness_Score (CIS) | Dependent | Global score via federated aggregation of local CEN evaluations | 0-100 scale |
| Evaluation_coverage | Dependent | % of UNESCO cultural regions with active CENs | 0-100% |
| Inter_CEN_agreement | Dependent | Krippendorff's alpha on shared test items | 0.0-1.0 (target: α > 0.67) |
| User_satisfaction_correlation | Dependent | Pearson r between CIS and local user satisfaction surveys | -1.0 to 1.0 (target: r > 0.7) |
| AI_model_evaluated | Controlled | Fixed generative AI model version | Constant |
| Evaluation_rubric_structure | Controlled | Standardized rubric with culturally-adapted criteria | Fixed template |
| Aggregation_algorithm | Controlled | FedAvg-based weighted averaging with DIF adjustment | Fixed algorithm |

### 1.3 Causal Mechanism

**4-Step Causal Chain:**

```
Step 1: CENs with trained mediators
    ↓ (produces)
Step 2: Valid local cultural assessments
    ↓ (mapped via)
Step 3: Cross-culturally comparable data (via SCO)
    ↓ (aggregated by)
Step 4: Measurement-invariant global CIS (via FAP+DIF)
    ↓ (achieves)
OUTCOME: Valid, scalable cultural inclusiveness evaluation
```

**Detailed Mechanism:**

1. **Step 1 → Step 2 (Local Validation):** Cultural Evaluation Nodes staffed by trained participatory mediators conduct community workshops to define appropriateness criteria, then validate AI outputs against these criteria. Mediators perform crucial labor: building trust, making participation accessible, contextualizing community values.

2. **Step 2 → Step 3 (Cross-Cultural Mapping):** Local assessments are mapped to a bottom-up Shared Cultural Ontology constructed from community-defined concepts. Wikidata multilingual identifiers serve as cross-lingual anchors, enabling comparison while preserving cultural specificity.

3. **Step 3 → Step 4 (Invariant Aggregation):** The Federated Aggregation Protocol synthesizes local CEN scores using weighted averaging. Differential Item Functioning (DIF) analysis identifies culturally-biased evaluation items, adjusting scores to achieve measurement invariance.

4. **Step 4 → Outcome (Valid Global Score):** The resulting Cultural Inclusiveness Score (CIS) represents a valid global assessment because it aggregates authentic local validations while controlling for measurement non-equivalence.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Hall et al. 2025 (World Wide Dishes) | Participatory mediators successfully capture localized cultural expertise through trust-building and accessible participation | Strong |
| Step 1 → Step 2 | Qadri et al. 2025 (Thick Evaluations) | Community co-constructed metrics outperform researcher-imposed criteria for cultural representation | Strong |
| Step 2 → Step 3 | MAKIEval (Zhao et al. 2025) | Wikidata multilingual identifiers enable cross-lingual anchoring for cultural concepts | Medium |
| Step 3 → Step 4 | Mengistu et al. 2024 (FL Survey) | Federated learning handles data heterogeneity while preserving local data sovereignty | Strong |
| Step 3 → Step 4 | Nascimento et al. 2024 (Data Skew FL) | Aggregation algorithms work with non-IID distributions typical of cultural data | Medium |
| Step 4 → Outcome | Cross-cultural psychometrics literature | DIF analysis successfully identifies and adjusts for culturally-biased measurement items | Strong |

**Key Tension:**
- **Tension:** "Thick Evaluations" (Qadri et al. 2025) argues for situated, discursive evaluation that resists quantification, while FCEN proposes aggregating local evaluations into global scores.
- **Resolution:** FCEN preserves "thickness" at the local CEN level (community-defined criteria, qualitative validation) while using quantitative aggregation only for cross-cultural comparison. The meta-evaluation framework (Coverage, Agreement, Validity) captures multiple dimensions rather than reducing to a single number. Phase 2B verification will test whether this hybrid approach maintains validity.

### 1.4 Key Assumptions

| # | Assumption | Evidence | Consequence if Violated |
|---|------------|----------|------------------------|
| A1 | Cultural communities can articulate and validate appropriateness criteria for AI outputs relevant to their cultural context | World Wide Dishes, CulturalBench human annotation success | Local CEN assessments become unreliable; entire framework fails |
| A2 | Participatory mediators can be trained consistently across different cultural contexts using standardized curriculum with local adaptation | Participatory design literature; World Wide Dishes mediator roles | Quality variance across CENs; aggregation produces biased results |
| A3 | Federated aggregation produces meaningful global scores despite local variation through psychometric invariance testing | FL heterogeneity research; cross-cultural psychometrics | Global CIS becomes meaningless or systematically biased |
| A4 | Bottom-up ontology construction avoids Western-centric category imposition | Critique of existing benchmarks; decolonial AI literature | Cross-cultural comparability fails; Western bias reproduced |
| A5 | Wikidata multilingual identifiers provide sufficient cross-lingual anchoring for cultural concepts | MAKIEval methodology; Wikidata coverage statistics | Mapping layer fails; cultural concepts lost in translation |

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Generative AI systems (text, image, multimodal) deployed globally
- Cultural evaluation focused on appropriateness, representation, and inclusiveness
- Contexts where cultural communities can be engaged through participatory processes
- AI systems serving diverse cultural user bases

**Where Hypothesis Does NOT Apply:**
- Domain-specific AI requiring specialized expertise (medical, legal, scientific)
- Real-time evaluation scenarios requiring immediate results (FCEN is designed for continuous monitoring, not instant assessment)
- Cultures/communities that cannot or choose not to participate in evaluation processes
- Proprietary AI systems that cannot be evaluated externally

**Known Limitations:**
- **Coordination overhead:** Setting up CENs requires institutional partnerships, funding, and local buy-in
- **Cold start problem:** New cultural regions require bootstrapping from related cultural clusters
- **Quality variance:** Different CENs may have different quality standards despite training
- **Temporal lag:** Community-based evaluation is slower than automated benchmarks
- **Coverage gaps:** Some cultures may remain underrepresented if participation barriers persist

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Validity Advantage):** If FCEN is deployed across N ≥ 10 cultural regions, then the correlation between FCEN's Cultural Inclusiveness Score (CIS) and local user satisfaction surveys will exceed r = 0.7, significantly higher than centralized benchmarks (expected r = 0.4-0.5).

*Measurement:*
- Pearson correlation coefficient between CIS and user satisfaction
- Statistical test: Fisher's z-transformation for correlation comparison, p < 0.05
- Sample: N ≥ 10 cultural regions, ≥ 100 users per region

*Basis:*
- Centralized benchmarks achieve moderate correlation because researcher-designed criteria miss culture-specific nuances
- FCEN's community-validated criteria should better capture local user expectations

**Secondary Predictions:**
**P2 (Scalability):** If FCEN is deployed across N cultural regions, evaluation coverage will scale linearly with N (O(N)), whereas centralized benchmarks show diminishing returns (O(log N)) as cultural diversity increases.

*Measurement:*
- Plot evaluation coverage vs. number of regions
- Compare regression slopes: FCEN (linear) vs. centralized (logarithmic)

**P3 (Measurement Invariance):** If bottom-up ontology with DIF adjustment is used, fewer than 15% of evaluation items will show significant Differential Item Functioning across cultural groups, compared to >30% for centralized benchmark items.

*Measurement:*
- DIF analysis using Mantel-Haenszel or IRT-based methods
- Proportion of items flagged for DIF (p < 0.05, effect size > 0.25)

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Validity Failure:** User satisfaction correlation r ≤ 0.5 (not significantly better than centralized approaches)

2. **Mechanism Failure:** Any causal link breaks:
   - Link 1: Inter-rater reliability within CENs α < 0.5 (mediator training ineffective)
   - Link 2: >50% of cultural concepts cannot be mapped to SCO (ontology fails)
   - Link 3: DIF analysis fails to achieve measurement invariance (>40% items flagged)
   - Link 4: Global CIS shows no correlation with any local satisfaction measure

3. **Scalability Failure:** Coverage does not increase with additional CENs (coordination overhead exceeds value)

4. **Comparative Failure:** Centralized benchmark achieves equal or higher validity with lower cost

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - This hypothesis proposes an architectural innovation rather than performance improvement over existing methods. Comparison is against centralized benchmark approaches (CulturalBench, WorldCuisines, ALM-Bench) on validity metrics rather than accuracy metrics.*

**Comparison Baselines:**
| Baseline | Type | Expected Validity (r) | Reference |
|----------|------|----------------------|-----------|
| CulturalBench | Centralized, human-AI teaming | ~0.45 | arxiv.org/abs/2410.02677 |
| WorldCuisines | Centralized, domain-specific | ~0.40 | Winata et al. 2024 |
| ALM-Bench | Centralized, multilingual | ~0.50 | CVPR 2025 |
| FCEN (proposed) | Federated, community-validated | >0.70 | This work |

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d) for correlation difference: d = 0.5 (medium)
- Required regions: N ≥ 10 cultural regions
- Required users per region: n ≥ 100
- Statistical power: 0.8
- Total sample: ≥ 1,000 users across ≥ 10 regions

**Test Specifications:**

| Prediction | Test | Significance | Effect Size |
|------------|------|--------------|-------------|
| P1 (Validity) | Fisher's z for correlation comparison | α = 0.05, one-tailed | Δr ≥ 0.2 |
| P2 (Scalability) | Regression slope comparison | α = 0.05 | β₁ > β₂ (linear > log) |
| P3 (Invariance) | Mantel-Haenszel DIF + IRT | α = 0.05 per item | Δ < 0.25 for ≥85% items |

**Report Format:**
- Mean ± SD for all metrics
- 95% Confidence Intervals
- Effect sizes (Cohen's d, Pearson r)
- p-values with multiple comparison correction (Bonferroni)

---

## 2. Contribution Summary

**Primary Contribution:**
- **Type:** Methodological (with Theoretical foundation)
- **Statement:** We introduce FCEN (Federated Cultural Evaluation Network), the first federated architecture for cultural AI evaluation that distributes validation authority to cultural communities while enabling global comparison through psychometric invariance testing.
- **Novelty:** Paradigm shift from "design globally, deploy locally" (centralized benchmarks) to "validate locally, aggregate globally" (federated evaluation). First application of federated learning principles to cultural AI assessment.

**Secondary Contributions:**
- **Theoretical:** Framework for distributed epistemic authority in AI evaluation, grounded in participatory design and postcolonial AI critique
- **Practical:** Scalable, continuous cultural monitoring architecture for production AI systems; empowers cultural communities in AI governance
- **Empirical:** Meta-evaluation framework (Coverage, Agreement, Validity) for assessing cultural evaluation systems

---

## 3. Key Related Work

### Foundation Sources (MUST CITE)

1. **"The Human Labour of Data Work: World Wide Dishes"** (Hall et al., 2025)
   - Authors: S. Hall, S. Dalal, R. Sefala, et al.
   - URL: arxiv.org/abs/2502.05961
   - Key Finding: Participatory mediators perform crucial labor (trust-building, accessibility, value contextualization) that enables authentic community data collection
   - **Supports:** Mechanism Link 1 (CEN mediator design)

2. **"A Survey on Heterogeneity in Federated Learning"** (Mengistu et al., 2024)
   - Authors: T.M. Mengistu, T. Kim, J.W. Lin
   - Citations: 46
   - Key Finding: FL handles data heterogeneity while preserving privacy through distributed aggregation
   - **Supports:** Mechanism Link 3 (FAP design)

3. **"The Case for Thick Evaluations of Cultural Representation"** (Qadri et al., 2025)
   - Authors: R. Qadri, M. Díaz, D. Wang, M. Madaio
   - URL: AIES 2025
   - Key Finding: Community co-constructed metrics outperform researcher-imposed criteria; "thick" evaluation respects situated meaning-making
   - **Supports:** Mechanism Link 1, Key Tension resolution

### Comparison Baselines

4. **CulturalBench** (2024)
   - URL: arxiv.org/abs/2410.02677
   - Key Feature: 1,696 human-written questions, 45 global regions, Human-AI Red-Teaming
   - **Comparison:** Centralized design limits cultural authority; FCEN comparison baseline

5. **WorldCuisines** (Winata et al., 2024)
   - Semantic Scholar ID: 58bb72cd1694
   - Key Feature: 1M+ datapoints, 30 languages, largest multicultural VQA benchmark
   - **Comparison:** Scale achieved but centralized; validates scalability is possible

### Gap Evidence

6. **"Exposing Blindspots: Cultural Bias in Generative Image Models"** (Seo et al., 2025)
   - Semantic Scholar ID: 269b141cfc7c
   - Key Finding: Cross-country evaluation reveals Global-North bias in default T2I generations
   - **Supports:** Gap existence - centralized approaches perpetuate bias

7. **Cross-Cultural Psychometrics Literature** (Various, 2021-2024)
   - Key Method: Differential Item Functioning (DIF) analysis for measurement invariance
   - **Supports:** Mechanism Link 3 (FAP invariance testing)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Can Cultural Evaluation Nodes (CENs) produce reliable cultural appropriateness assessments when operated by trained participatory mediators?"
- Maps to: Primary prediction (validity foundation)
- Verification type: Empirical (pilot CEN deployment)
- Critical: MUST PASS - if local assessment is unreliable, entire framework fails

**SH2 (Mechanism):**
"Does the 4-step causal mechanism (CEN → Local Assessment → SCO Mapping → FAP Aggregation → Global CIS) operate as proposed?"
- Maps to: Causal mechanism (N=4 steps)
- Will decompose in Phase 2B into 4 sub-hypotheses:
  - H-M1: CEN → Valid local assessments
  - H-M2: Local assessments + SCO → Comparable data
  - H-M3: Comparable data + FAP → Measurement invariance
  - H-M4: Invariant aggregation → Valid global CIS
- Verification type: Causal analysis per link
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does FCEN achieve higher validity (user satisfaction correlation) than centralized benchmarks (CulturalBench, WorldCuisines)?"
- Maps to: Secondary predictions (comparative advantage)
- Verification type: Comparative empirical
- Critical: Determines practical value and publication impact

**Total sub-hypotheses in Phase 2B:** 2 + 4 = **6 sub-hypotheses**

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-FCEN-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence (10 variables)
- [x] Causal mechanism has evidence at each step (N=4 steps, evidence table complete)
- [x] Causal chain length (N=4) determined and documented
- [x] Key tension identified (Thick vs. quantitative) and resolution proposed
- [x] Key assumptions list consequences if violated (5 assumptions)
- [x] At least 2 testable predictions exist with primary marked (3 predictions)
- [x] Falsification criteria defined (4 failure conditions)
- [x] Baselines identified for comparison (3 baselines)
- [x] SH1, SH2, SH3 are clear starting points

**Status: ALL ITEMS VERIFIED ✓**

### Open Questions

1. **Resource Requirements:** What is the minimum viable CEN deployment? (Estimate: 3-5 cultural regions, 10-20 mediators, 6-month pilot)

2. **Data Availability:** Which cultural regions have existing community partnerships or participatory AI infrastructure that could bootstrap CEN deployment?

3. **Technical Feasibility:** Can Wikidata coverage be verified for target cultural regions before ontology construction? What fallback exists for concepts without Wikidata entries?

4. **Priority Verification Order:**
   - Phase 2B recommends: SH1 (existence) → SH2-M1 (first mechanism link) → SH2-M2/M3/M4 → SH3 (comparison)
   - Rationale: Early failure detection at foundation level prevents wasted effort

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
