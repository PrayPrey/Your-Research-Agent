# Phase 2B: Hypothesis Verification Plan

## Document Metadata
- **Generated**: 2026-07-09
- **Workflow**: Phase 2B Planning (UNATTENDED mode)
- **Parent Hypothesis**: H-OntologyStress-v1
- **Confidence Level**: 0.8
- **Pipeline Project ID**: 4fc608d0-be7e-49ff-9add-542a8e3f6919
- **Phase 2B Task ID**: b3350b42-05b2-4b19-900f-75aa4b6ce0b4

---

## 1. Core Hypothesis Summary

### 1.1 Hypothesis Statement
**H-OntologyStress-v1**: Under creative text generation (metaphorical/speculative content), if CCP-based hallucination detection is applied with fixed thresholds calibrated for factual domains, then claim-type mass ratio (ρ_j) will degrade >0.15 AND diversity metrics will drop ≥15%, because CCP's NLI-based conditioning and product aggregation embed implicit factual-ontology assumptions that misalign with creative semantics.

### 1.2 Alternative Hypothesis (H0)
Existing hallucination detectors (CCP, AGSER) do NOT exhibit measurable performance degradation (ROC-AUC drop <0.05, ρ_j shift ≤0.05, diversity loss <5%) or increased false-positive rates on creative text compared to factual text.

### 1.3 Key Variables

**Independent Variables:**
- `task_ontology`: factual (TruthfulQA biographies) vs. creative (WritingPrompts stories)
- `detection_mechanism`: CCP vs. AGSER vs. HAD (taxonomy-trained)
- `aggregation_function`: product vs. log-sum-exp vs. mean

**Dependent Variables:**
- `claim_type_mass_ratio` (ρ_j): Median (entail+contradict mass) / (total top-K mass) [PRIMARY]
- `ROC_AUC`: ROC-AUC for hallucination detection on factual benchmarks
- `diversity_loss`: Percentage drop in Self-BLEU and embedding dispersion [PRIMARY]
- `metaphor_false_positive_ratio`: False-positive concentration on metaphor spans vs. literal spans

**Controlled Variables:**
- `base_LLM`: Same model (GPT-3.5, GPT-4, Llama3-8B, Mistral-7B) across conditions
- `decoding_temperature`: Fixed at 0.7
- `prompt_formulation`: Standardized prompts from existing benchmarks

### 1.4 Datasets and Models

**Factual Datasets:**
- TruthfulQA biographies
- HotpotQA

**Creative Datasets:**
- WritingPrompts
- OpenStoryGen

**Models:**
- GPT-3.5-turbo
- GPT-4
- Llama3-8B
- Mistral-7B

**Compute Requirements:** NVIDIA A100 40GB

### 1.5 Established Baselines (BUILD_ON)
1. CCP achieves +0.05-0.10 ROC-AUC improvement over logit baselines on biography generation [arxiv:2403.04696]
2. AGSER demonstrates F1 improvements of +0.154 to +0.368 over SelfCheckGPT on factual benchmarks [arxiv:2501.09997]
3. Product aggregation outperforms mean/min in factual domains [arxiv:2403.04696]

---

## 2. Causal Mechanism & Sub-Hypotheses

### 2.1 Causal Chain
The ontology mismatch cascade operates through four sequential steps:

```
Ontology Shift (Step 1)
    ↓
Denominator Instability (Step 2)
    ↓
Product Aggregation Amplification (Step 3)
    ↓
Detection Failure (Step 4)
```

**Moderators:** NLI context window, aggregation function choice  
**Confounds:** NLI model domain bias, claim decomposition variance  
**Link Function Requirement:** Monotonic regression of ROC-AUC degradation on ρ_j shift (R² > 0.6)

### 2.2 Sub-Hypothesis Inventory

#### H-E1: Empirical Characterization (Exploratory)
**Type:** EMPIRICAL  
**Status:** TODO  
**Gate:** 1/9 (Prerequisite for mechanistic tests)  
**Priority:** CRITICAL

**Statement:** Claim-type mass ratio ρ_j exhibits measurable degradation (Δρ_j > 0.15) when hallucination detectors trained on factual text are applied to creative text, with accompanying increases in autocorrelation (lag-1 > 0.4) and claim decomposition variance.

**Operationalization:**
- Measure median ρ_j on TruthfulQA biographies vs. WritingPrompts samples
- Compute lag-1 autocorrelation of CCP scores within claims
- Measure inter-tool agreement for claim decomposition (Krippendorff's α)
- Collect baseline diversity metrics (Self-BLEU, embedding dispersion)

**Success Criteria:**
- Δρ_j > 0.15 between factual and creative domains
- Lag-1 autocorrelation > 0.4 in creative text (vs. <0.2 in factual)
- Claim decomposition reliability (α > 0.7) established

**Deliverables:**
- ρ_j degradation report with 95% confidence intervals
- Autocorrelation statistics table
- Decomposition variance analysis
- Baseline diversity metrics

**Estimated Duration:** 1 week  
**Compute Budget:** 20 A100-hours  
**Dependencies:** None (entry point)

---

#### H-M1: Ontology Shift Mechanism
**Type:** MECHANISTIC (Step 1 of causal chain)  
**Status:** TODO  
**Gate:** 2/9  
**Priority:** HIGH

**Statement:** Creative text contains metaphorical and counterfactual content where factual verifiability assumptions are semantically inappropriate, leading to systematic NLI model confusion distinct from simple uncertainty.

**Operationalization:**
- Annotate 200 creative samples for metaphor density (human raters)
- Measure NLI entropy on metaphor spans vs. literal spans
- Compare NLI label distributions (entail/contradict/neutral) across factual/creative domains
- Test correlation between metaphor density and ρ_j degradation

**Success Criteria:**
- Metaphor density ≥2× higher in creative vs. factual samples
- NLI entropy on metaphors > 1.5× literal spans
- Metaphor density correlates with ρ_j degradation (r > 0.5, p < 0.01)

**Deliverables:**
- Metaphor annotation dataset (200 samples, inter-rater reliability κ > 0.7)
- NLI confusion analysis report
- Correlation analysis between metaphor density and ρ_j

**Estimated Duration:** 1.5 weeks  
**Compute Budget:** 15 A100-hours  
**Dependencies:** H-E1 (requires baseline ρ_j measurements)

---

#### H-M2: Denominator Instability Mechanism
**Type:** MECHANISTIC (Step 2 of causal chain)  
**Status:** TODO  
**Gate:** 3/9  
**Priority:** HIGH

**Statement:** NLI models misclassify metaphoric alternatives as neutral (rather than entail/contradict), decreasing the denominator in ρ_j = (entail+contradict mass) / (total top-K mass) and destabilizing claim-level scoring.

**Operationalization:**
- Sample 100 claims with high metaphor density from H-M1 dataset
- Generate alternative claims using same procedure as CCP
- Manually label expected NLI relations (gold standard)
- Measure neutral-label inflation: P(neutral | metaphor) vs. P(neutral | literal)
- Compute ρ_j sensitivity to neutral mass via ablation

**Success Criteria:**
- P(neutral | metaphor) ≥ 1.5× P(neutral | literal)
- Neutral-label inflation accounts for ≥60% of ρ_j degradation
- Manual correction of neutral labels recovers ≥50% of ρ_j loss

**Deliverables:**
- Neutral-label inflation analysis
- Gold-standard NLI annotations for 100 creative claims
- ρ_j sensitivity ablation results

**Estimated Duration:** 1.5 weeks  
**Compute Budget:** 25 A100-hours  
**Dependencies:** H-M1 (requires metaphor-annotated dataset)

---

#### H-M3: Product Aggregation Amplification
**Type:** MECHANISTIC (Step 3 of causal chain)  
**Status:** TODO  
**Gate:** 4/9  
**Priority:** HIGH

**Statement:** Product aggregation compounds correlated low-probability creative tokens multiplicatively, causing claim scores to degrade faster than alternative aggregation functions (log-sum-exp, mean).

**Operationalization:**
- Implement CCP with three aggregation functions: product, log-sum-exp, mean
- Measure correlation between token-level scores within creative claims (lag-1, lag-2 autocorrelation)
- Simulate synthetic claims with controlled autocorrelation levels
- Compare ROC-AUC degradation across aggregation functions

**Success Criteria:**
- Product aggregation shows ≥2× greater ROC-AUC degradation vs. log-sum-exp on creative text
- Autocorrelation effect confirmed via permutation test (ΔROC-AUC > 0.03 under random permutation)
- Simulation reproduces empirical autocorrelation-aggregation interaction

**Deliverables:**
- Aggregation function comparison table (ROC-AUC, calibration error)
- Autocorrelation analysis (lag-1, lag-2 coefficients)
- Permutation test results
- Synthetic claim simulation code and results

**Estimated Duration:** 2 weeks  
**Compute Budget:** 40 A100-hours  
**Dependencies:** H-M2 (requires ρ_j degradation mechanism understanding)

---

#### H-M4: Detection Failure Mechanism
**Type:** MECHANISTIC (Step 4 of causal chain)  
**Status:** TODO  
**Gate:** 5/9  
**Priority:** HIGH

**Statement:** Aggregation fragility from H-M3 manifests as false-positive clustering on metaphor spans and diversity suppression (≥15% drop in Self-BLEU and embedding dispersion) when detectors are used to filter model outputs.

**Operationalization:**
- Apply CCP/AGSER detection with fixed thresholds (calibrated on factual text) to creative samples
- Measure false-positive concentration on metaphor spans vs. literal spans
- Simulate filtering pipeline: remove high-hallucination-score outputs, measure diversity loss
- Compare diversity metrics (Self-BLEU, embedding cosine variance) pre/post filtering

**Success Criteria:**
- Metaphor false-positive ratio ≥ 2× (false positives concentrate on metaphors)
- Diversity loss ≥ 15% under threshold-based filtering
- False-positive clustering statistically significant (χ² test, p < 0.01)

**Deliverables:**
- False-positive span analysis (metaphor vs. literal)
- Diversity loss report (Self-BLEU, embedding metrics)
- Filtering simulation results
- Statistical significance tests

**Estimated Duration:** 1.5 weeks  
**Compute Budget:** 30 A100-hours  
**Dependencies:** H-M3 (requires aggregation function analysis)

---

#### H-C: Comparative Robustness (HAD vs. CCP/AGSER)
**Type:** COMPARATIVE  
**Status:** TODO  
**Gate:** 6/9  
**Priority:** OPTIONAL (STRETCH)

**Statement:** HAD (taxonomy-trained hallucination detector) exhibits ≥15% smaller AUC degradation on creative tasks compared to AGSER, while maintaining Span F1 within ±5%, because explicit taxonomy training captures diverse epistemic intents beyond binary factuality.

**Operationalization:**
- Apply HAD, CCP, and AGSER to paired factual/creative prompts
- Measure ROC-AUC degradation (creative - factual) for each detector
- Compute Span F1 on manually annotated hallucination spans
- Analyze error patterns: does HAD avoid metaphor false positives?

**Success Criteria:**
- HAD ΔAUC ≤ AGSER ΔAUC - 0.15 (HAD more robust)
- HAD Span F1 degradation ≤ 0.05 (maintains span-level accuracy)
- HAD metaphor false-positive rate < 0.5× AGSER rate

**Deliverables:**
- Detector comparison table (ROC-AUC, Span F1, metaphor FP rate)
- Error pattern analysis
- Paired t-test for AUC degradation differences

**Estimated Duration:** 2 weeks  
**Compute Budget:** 35 A100-hours  
**Dependencies:** H-M4 (requires false-positive analysis framework)  
**Risk:** HAD may not be publicly available; mark as OPTIONAL

---

## 3. Testable Predictions

### P1: ρ_j Degradation and Link Function
**Prediction:** Median ρ_j will drop by >0.15 in creative corpora vs. biographies, with monotonic link to ROC-AUC degradation (R² > 0.6).

**Success Criterion:** Δρ_j > 0.15 AND R² > 0.6 in regression ROC-AUC ~ ρ_j  
**Failure Criterion:** Δρ_j ≤ 0.05 OR R² < 0.4  
**Measurement Approach:** Compare median ρ_j on TruthfulQA biographies vs. WritingPrompts, fit monotonic regression  
**Verified By:** H-E1, H-M2

---

### P2: Autocorrelation and Aggregation Fragility
**Prediction:** Lag-1 CCP autocorrelation will exceed 0.4 in fiction (vs. <0.2 in biography), causing product aggregation fragility with permutation ΔROC-AUC > 0.03.

**Success Criterion:** Mean lag-1 autocorr > 0.4 in fiction AND permutation ΔROC-AUC > 0.03  
**Failure Criterion:** Autocorrelation < 0.3 OR permutation effect < 0.01  
**Measurement Approach:** Measure intra-claim CCP correlation, run permutation controls on token ordering  
**Verified By:** H-M3

---

### P3: Comparative Detector Robustness
**Prediction:** AGSER shows ≥15% AUC drop on creative tasks while HAD remains within ±5% Span F1, with metaphor false-positive concentration ≥2×.

**Success Criterion:** AGSER ΔAUC ≥ 0.15 AND HAD Δ Span F1 ≤ 0.05 AND metaphor FP ratio ≥ 2×  
**Failure Criterion:** Both degrade similarly OR HAD shows no robustness advantage  
**Measurement Approach:** Apply both detectors to paired factual/creative prompts, measure span-level performance  
**Verified By:** H-C (OPTIONAL)

---

## 4. Experimental Phases and Timeline

### Phase 0: PREREQUISITE - ρ_j Validation Study
**Duration:** 1 week  
**Status:** TODO  
**Gate:** 0/9

**Objectives:**
- Establish inter-rater reliability for claim decomposition (Krippendorff's α > 0.7)
- Validate ρ_j convergent validity (correlate with independent metaphor density scores, r > 0.5)
- Run power analysis simulation to confirm detectable effect size (0.15 ρ_j shift)

**Go/No-Go Criteria:**
- Claim decomposition reliability α > 0.7
- Convergent validity r > 0.5
- Power analysis indicates ≥80% power to detect Δρ_j = 0.15 with n=4 models, n=2 domains

**Deliverables:**
- Validation report (reliability, validity, power analysis)
- Pre-registered analysis plan

---

### Phase 1: Ontology Stress Characterization (PILOT)
**Duration:** 2 weeks  
**Status:** TODO  
**Gate:** 1/9  
**Models:** GPT-3.5-turbo, Llama3-8B (pilot subset)

**Sub-Hypotheses:** H-E1, H-M1

**Objectives:**
- Measure ρ_j degradation on pilot models
- Characterize autocorrelation and decomposition stability
- Annotate metaphor density and validate ontology shift mechanism

**Go/No-Go Criteria (Pilot Phase):**
- ρ_j reliability > 0.7 (confirmed from Phase 0)
- Effect size Δρ_j > 0.1 (at least two-thirds of predicted 0.15)
- Metaphor density correlation r > 0.4

**Decision Point:** If pilot succeeds, proceed to full four-model experiment. If pilot fails go/no-go criteria, pivot to calibration-focused research question.

**Deliverables:**
- ρ_j degradation report (pilot models)
- Autocorrelation statistics
- Decomposition variance analysis
- Metaphor annotation dataset (200 samples)
- Go/no-go decision report

---

### Phase 2: Comparative Mechanism Testing (MAIN)
**Duration:** 3 weeks  
**Status:** TODO  
**Gate:** 2-6/9  
**Models:** GPT-3.5, GPT-4, Llama3-8B, Mistral-7B (full set if pilot succeeds)

**Sub-Hypotheses:** H-M2, H-M3, H-M4, H-C (optional)

**Objectives:**
- Apply CCP/AGSER/HAD to paired factual/creative tasks
- Measure performance degradation and false-positive patterns
- Validate denominator instability and aggregation amplification mechanisms
- Compare detector robustness (if HAD available)

**Deliverables:**
- ROC-AUC comparison table (all detectors × all models)
- Metaphor false-positive analysis
- Neutral-label inflation report
- Autocorrelation and aggregation ablation results
- HAD comparison (if available, else mark N/A)

---

### Phase 3: Aggregation Ablation
**Duration:** 2 weeks  
**Status:** TODO  
**Gate:** 7-9/9

**Sub-Hypotheses:** H-M3, H-M4

**Objectives:**
- Replace product aggregation with log-sum-exp and mean
- Test calibration preservation and diversity metrics
- Validate aggregation function as causal factor

**Deliverables:**
- Calibration curves (all aggregation functions)
- Diversity metrics comparison (Self-BLEU, embedding dispersion)
- Permutation test results
- Synthetic claim simulation

---

### Timeline Summary (Gantt Chart)

```
Week 1-1:   [Phase 0: ρ_j Validation]
Week 2-3:   [Phase 1: Pilot - H-E1, H-M1]
            └─ Decision Point: Go/No-Go for full experiment
Week 4-6:   [Phase 2: Main - H-M2, H-M3, H-M4, H-C]
Week 7-8:   [Phase 3: Aggregation Ablation]
Week 9:     [Analysis, Write-up, Pre-print Preparation]

Total Duration: 9 weeks
Critical Path: Phase 0 → Phase 1 → Decision → Phase 2 → Phase 3
```

---

## 5. Dependency Graph (DAG)

```
                    [Phase 0: ρ_j Validation]
                              ↓
                       [H-E1: Empirical]
                       /              \
                      /                \
              [H-M1: Ontology]    (ρ_j baseline)
                     ↓                  ↓
              [H-M2: Denominator] ← (ρ_j mechanism)
                     ↓
              [H-M3: Aggregation]
                     ↓
              [H-M4: Detection Failure]
                     ↓
              [H-C: Comparative] (OPTIONAL)

Legend:
- Solid arrows: Hard dependencies (must complete predecessor)
- Dashed arrows: Soft dependencies (informs but not blocking)
- Boxes with OPTIONAL: Can be skipped if resource constraints
```

**Critical Path:** Phase 0 → H-E1 → H-M1 → H-M2 → H-M3 → H-M4  
**Parallel Opportunities:** H-M1 metaphor annotation can run in parallel with H-E1 ρ_j computation  
**Optional Branch:** H-C depends on HAD availability (check early, mark N/A if unavailable)

---

## 6. Risk Analysis and Mitigation

### 6.1 Identified Risks

#### RISK-1: Novel ρ_j Metric Lacks Validation
**Severity:** HIGH  
**Probability:** 0.85  
**Impact:** Unvalidated metric undermines all causal claims

**Concerns:**
- Will different claim decomposition tools yield consistent ρ_j values?
- Does ρ_j actually measure what we claim (construct validity)?
- Can we detect 0.15 shift with adequate statistical power (n=4 models, n=2 domains)?

**Mitigation:**
- **Phase 0 PREREQUISITE:** Conduct inter-rater reliability study (target α > 0.7)
- Include convergent validity check: correlate ρ_j with independent metaphor density scores (target r > 0.5)
- Run power analysis simulation before main experiment
- Pre-register analysis plan to reduce researcher degrees of freedom

**Fallback:** If validation fails, pivot to exploratory research question focused on calibration rather than causal mechanism

---

#### RISK-2: HAD Unavailability Blocks H-C
**Severity:** MEDIUM  
**Probability:** 0.9  
**Impact:** Cannot test comparative robustness claim

**Concerns:**
- HAD detector not publicly available
- May require author contact or institutional access
- Timeline risk if access delayed

**Mitigation:**
- **Mark H-C as OPTIONAL/STRETCH goal** from outset
- Contact HAD authors early (Week 1) to assess availability
- If unavailable by Week 3, formally mark H-C as N/A and proceed without comparative analysis
- Null result for H-C is acceptable; focus on CCP/AGSER mechanisms

**Fallback:** Reframe contribution as mechanism discovery rather than detector comparison

---

#### RISK-3: Compute Budget Constraint
**Severity:** MEDIUM  
**Probability:** 0.7  
**Impact:** Cannot complete full four-model experiment

**Concerns:**
- 4 models × 2 datasets × 3 aggregation functions × multiple samples = ~140 A100-hours
- API costs for GPT-3.5/GPT-4
- Potential budget overrun if pilot expands

**Mitigation:**
- **Staged compute plan:** Pilot with 2 models (GPT-3.5, Llama3-8B) first (~40 A100-hours)
- Go/no-go decision point after pilot (Week 3)
- Use cached API calls where possible (store intermediate NLI results)
- Set clear budget ceiling: if pilot + main exceeds 150 A100-hours, scale back to 2 models for Phase 3

**Fallback:** Two-model paper is still publishable; emphasize mechanism over model coverage

---

#### RISK-4: Factual/Creative Boundary Conflation
**Severity:** MEDIUM  
**Probability:** 0.75  
**Impact:** Confounds genre with epistemic intent, threatens construct validity

**Concerns:**
- WritingPrompts may contain factual biographical elements
- TruthfulQA biographies may use figurative language
- False positives on metaphors could reflect legitimate uncertainty rather than detector failure
- Genre ≠ epistemic intent (philosophical concern)

**Mitigation:**
- **Multi-dimensional operationalization:** Measure genre + prompt type + human-annotated epistemic intent
- Include mixed-genre samples as robustness check (e.g., creative nonfiction, speculative biographies)
- Reframe hypothesis as "genre mismatch" rather than absolute factual/creative divide
- Add qualitative analysis of false-positive cases to understand semantic patterns beyond binary classification
- Validate epistemic intent annotations with independent raters (κ > 0.7)

**Fallback:** Acknowledge limitation in discussion; reframe as domain shift rather than ontology shift

---

#### RISK-5: Statistical Power with Small Sample
**Severity:** MEDIUM  
**Probability:** 0.6  
**Impact:** Type II error (fail to detect real effect)

**Concerns:**
- Only 4 models and 2 task types
- Between-model variance may be high
- Corrections for multiple comparisons reduce power further

**Mitigation:**
- **Phase 0 power analysis:** Simulate effect detection with n=4, Δρ_j=0.15
- If power < 80%, consider within-subjects design (same model on both domains)
- Use Bayesian estimation as supplement to NHST (report posterior intervals)
- Increase sample size per condition (more prompts per model-domain pair)

**Fallback:** Frame as exploratory study; emphasize effect size estimation over hypothesis testing

---

### 6.2 Risk Mitigation Strategy (Three-Tier)

**TIER 1 - PREREQUISITE:**
- ρ_j validation study with inter-rater reliability (α > 0.7) and convergent validity (r > 0.5)
- Power analysis simulation
- Pre-registered analysis plan

**TIER 2 - PILOT:**
- Two-model pilot (GPT-3.5, Llama3-8B) to validate ρ_j metric in practice
- Go/no-go criteria: reliability > 0.7, effect size Δρ_j > 0.1
- Decision point at Week 3

**TIER 3 - MAIN:**
- Full four-model experiment only if pilot succeeds
- H-C marked as OPTIONAL (contingent on HAD availability)
- Multi-dimensional task ontology operationalization
- Qualitative false-positive analysis

**Exit Criteria:**
- If Phase 0 validation fails (α < 0.7), STOP and redesign metric
- If pilot go/no-go fails, PIVOT to calibration-focused research
- If HAD unavailable by Week 3, mark H-C as N/A and proceed

---

## 7. Dialectical Analysis

### 7.1 Thesis
**Claim:** The hypothesis H-OntologyStress-v1 is scientifically valid and experimentally feasible despite identified risks.

**Premises:**
1. CCP and AGSER demonstrate strong performance on factual benchmarks (ROC-AUC +0.05-0.10, F1 +0.154-0.368)
2. Creative text fundamentally differs from factual text in epistemic intent and semantic structure
3. Product aggregation mathematically compounds correlated low-probability events
4. The causal chain (Ontology Shift → NLI confusion → denominator instability → aggregation amplification → detection failure) is mechanistically coherent
5. Pilot-based staged approach can validate ρ_j metric before full-scale investment

**Conclusion:** With proper risk mitigation (ρ_j validation, pilot phase, optional H-C), the hypothesis can be rigorously tested and will yield publishable insights regardless of outcome.

**Confidence:** 0.85

**Strengths:**
- Builds on established baselines with strong empirical grounding
- Mechanistic causal chain is testable at each step
- Risk mitigation plan addresses key validity threats
- Null result is publishable (calibration focus)

**Weaknesses:**
- Novel ρ_j metric lacks prior validation
- Factual/creative boundary may be theoretically problematic
- Compute requirements may limit experimental scope

---

### 7.2 Antithesis
**Claim:** The experimental design conflates genre with epistemic intent, undermining the hypothesis's theoretical foundation.

**Premises:**
1. Genre (biography vs fiction) is not equivalent to epistemic intent (factual verification vs creative expression)
2. WritingPrompts may contain verifiable factual claims within fictional narratives
3. TruthfulQA biographies may use metaphors and figurative language
4. The hypothesis assumes a clean factual/creative divide that may not exist in real text
5. False positives on metaphors could reflect legitimate uncertainty rather than detector failure

**Conclusion:** The experimental design may fail to isolate the ontology shift mechanism, leading to uninterpretable results.

**Confidence:** 0.7

**Strengths:**
- Identifies genuine confound between genre and epistemic intent
- Points to need for finer-grained operationalization
- Challenges assumption that metaphors should not be fact-checked

**Weaknesses:**
- Perfect isolation may be an unattainable standard
- Genre-level effects are still informative even if imperfect
- Mitigation strategies can address the confound

---

### 7.3 Synthesis
**Claim:** Multi-dimensional operationalization of task ontology synthesizes theoretical rigor with experimental pragmatism.

**Premises:**
1. Genre provides coarse-grained manipulation that is experimentally tractable
2. Additional dimensions (human-annotated epistemic intent, metaphor density) enable fine-grained construct validation
3. Mixed-genre robustness checks can identify boundary conditions
4. Qualitative false-positive analysis reveals semantic patterns beyond binary classification
5. Reframing as "genre mismatch" rather than "creative vs factual" acknowledges theoretical complexity while preserving testability

**Conclusion:** Enhanced operationalization preserves experimental feasibility while addressing theoretical concerns about the factual/creative boundary.

**Confidence:** 0.8

**Strengths:**
- Integrates measurement validity concerns with practical constraints
- Provides path to both confirming and disconfirming evidence
- Enables discovery of boundary conditions and moderating factors
- Maintains publishability under multiple outcome scenarios

**Weaknesses:**
- Adds complexity to experimental design and analysis plan
- Requires additional annotation effort for epistemic intent coding
- May reduce statistical power by introducing additional variables

---

### 7.4 Resolution
The synthesis position is adopted with the following commitments:

1. **Multi-dimensional operationalization:** Genre (primary manipulation) + metaphor density + epistemic intent annotations
2. **Robustness checks:** Include mixed-genre samples to test boundary conditions
3. **Qualitative analysis:** Systematic coding of false-positive cases to understand semantic patterns
4. **Reframing:** Use "genre mismatch" language in write-up to acknowledge theoretical complexity
5. **Transparent limitations:** Acknowledge genre/intent conflation in discussion section

This approach balances theoretical rigor (antithesis concerns) with experimental feasibility (thesis strengths) while preserving the core mechanistic contribution.

---

## 8. Executive Summary

### 8.1 Research Question
Do hallucination detection methods (CCP, AGSER) designed for factual text exhibit systematic performance degradation and creativity suppression when applied to creative text generation?

### 8.2 Core Hypothesis
CCP's NLI-based conditioning and product aggregation embed implicit factual-ontology assumptions. When applied to creative text (metaphors, counterfactuals), these assumptions cause: (1) claim-type mass ratio ρ_j degradation >0.15, (2) diversity loss ≥15%, and (3) false-positive clustering on metaphor spans (≥2× concentration).

### 8.3 Causal Mechanism (4-Step Chain)
1. **Ontology Shift:** Creative text semantics differ from factual assumptions
2. **Denominator Instability:** NLI misclassifies metaphoric alternatives as neutral, reducing ρ_j
3. **Product Aggregation Amplification:** Correlated low-probability creative tokens compound multiplicatively
4. **Detection Failure:** False-positive clustering and diversity suppression

### 8.4 Verification Strategy
- **6 sub-hypotheses:** H-E1 (empirical), H-M1-M4 (mechanistic chain), H-C (comparative, optional)
- **3 testable predictions:** P1 (ρ_j degradation + link function), P2 (autocorrelation + aggregation), P3 (comparative robustness)
- **3-phase experimental design:** Phase 0 (ρ_j validation), Phase 1 (pilot + ontology characterization), Phase 2 (mechanism testing), Phase 3 (aggregation ablation)
- **Staged risk mitigation:** Prerequisite validation → pilot go/no-go → main experiment

### 8.5 Key Risks and Mitigations
| Risk | Severity | Mitigation |
|------|----------|------------|
| ρ_j metric unvalidated | HIGH | Phase 0 prerequisite: reliability α > 0.7, convergent validity r > 0.5, power analysis |
| HAD unavailable | MEDIUM | Mark H-C as OPTIONAL; contact authors early; N/A if unavailable |
| Compute budget constraint | MEDIUM | Pilot with 2 models first; go/no-go at Week 3; scale back to 2 models if needed |
| Genre/intent conflation | MEDIUM | Multi-dimensional operationalization; mixed-genre robustness checks; qualitative FP analysis |
| Low statistical power | MEDIUM | Within-subjects design; Bayesian estimation; increase samples per condition |

### 8.6 Timeline and Resources
- **Total Duration:** 9 weeks
- **Compute Budget:** ~140 A100-hours (pilot: 40, main: 70, ablation: 30)
- **Critical Path:** Phase 0 (Week 1) → Phase 1 pilot (Week 2-3) → Decision → Phase 2 main (Week 4-6) → Phase 3 ablation (Week 7-8) → Write-up (Week 9)
- **Decision Points:** Phase 0 validation (Week 1), Pilot go/no-go (Week 3), HAD availability (Week 3)

### 8.7 Expected Outcomes
**If hypothesis confirmed:**
- First empirical demonstration of ontology-dependent hallucination detection failure
- Mechanistic understanding of NLI-aggregation interaction in creative domains
- Design principles for ontology-adaptive detection methods

**If hypothesis disconfirmed:**
- CCP/AGSER robustness exceeds predictions
- Pivot to calibration-focused contribution
- Still publishable: "Hallucination detectors transfer to creative text better than expected"

**Regardless of outcome:**
- Novel ρ_j metric validated (or invalidated) for future use
- Benchmark dataset (creative text + hallucination annotations)
- Open questions for ontology-adaptive detection research

---

## 9. Sub-Hypothesis Status Table

| ID | Type | Status | Gate | Priority | Duration | Compute | Dependencies |
|----|------|--------|------|----------|----------|---------|--------------|
| Phase-0 | VALIDATION | TODO | 0/9 | CRITICAL | 1 week | 5 A100-hr | None |
| H-E1 | EMPIRICAL | TODO | 1/9 | CRITICAL | 1 week | 20 A100-hr | Phase-0 |
| H-M1 | MECHANISTIC | TODO | 2/9 | HIGH | 1.5 weeks | 15 A100-hr | H-E1 |
| H-M2 | MECHANISTIC | TODO | 3/9 | HIGH | 1.5 weeks | 25 A100-hr | H-M1 |
| H-M3 | MECHANISTIC | TODO | 4/9 | HIGH | 2 weeks | 40 A100-hr | H-M2 |
| H-M4 | MECHANISTIC | TODO | 5/9 | HIGH | 1.5 weeks | 30 A100-hr | H-M3 |
| H-C | COMPARATIVE | TODO | 6/9 | OPTIONAL | 2 weeks | 35 A100-hr | H-M4 |

**Total Estimated Duration:** 9 weeks (excluding H-C if unavailable)  
**Total Compute Budget:** ~170 A100-hours (140 if H-C skipped)

---

## 10. Next Steps (Immediate Actions)

1. **Week 1 - Phase 0 Validation:**
   - Recruit 2-3 annotators for claim decomposition reliability study
   - Implement ρ_j calculation pipeline
   - Run power analysis simulation (n=4 models, Δρ_j=0.15)
   - Pre-register analysis plan on OSF or AsPredicted
   - Contact HAD authors to assess availability

2. **Week 2-3 - Pilot Phase:**
   - Run H-E1 on GPT-3.5 + Llama3-8B
   - Annotate 200 creative samples for metaphor density (H-M1)
   - Evaluate go/no-go criteria (reliability, effect size, metaphor correlation)
   - Make HAD availability decision (proceed with H-C or mark N/A)

3. **Week 3 Decision Point:**
   - If pilot succeeds: proceed to full four-model main experiment
   - If pilot fails: pivot to calibration-focused research question
   - If HAD unavailable: formally mark H-C as N/A

4. **Week 4+ - Main Experiment:**
   - Execute Phase 2 (H-M2, H-M3, H-M4) on full model set
   - Execute Phase 3 (aggregation ablation)
   - Continuous analysis and write-up

---

## Appendix A: Verification State Schema

The verification state is tracked in `verification_state.yaml` with the following structure:

```yaml
sub_hypotheses:
  H-E1:
    type: EMPIRICAL
    status: TODO
    gate: 1/9
    priority: CRITICAL
    estimated_duration_weeks: 1
    compute_budget_hours: 20
    dependencies: ["Phase-0"]
  H-M1:
    type: MECHANISTIC
    status: TODO
    gate: 2/9
    priority: HIGH
    estimated_duration_weeks: 1.5
    compute_budget_hours: 15
    dependencies: ["H-E1"]
  H-M2:
    type: MECHANISTIC
    status: TODO
    gate: 3/9
    priority: HIGH
    estimated_duration_weeks: 1.5
    compute_budget_hours: 25
    dependencies: ["H-M1"]
  H-M3:
    type: MECHANISTIC
    status: TODO
    gate: 4/9
    priority: HIGH
    estimated_duration_weeks: 2
    compute_budget_hours: 40
    dependencies: ["H-M2"]
  H-M4:
    type: MECHANISTIC
    status: TODO
    gate: 5/9
    priority: HIGH
    estimated_duration_weeks: 1.5
    compute_budget_hours: 30
    dependencies: ["H-M3"]
  H-C:
    type: COMPARATIVE
    status: TODO
    gate: 6/9
    priority: OPTIONAL
    estimated_duration_weeks: 2
    compute_budget_hours: 35
    dependencies: ["H-M4"]
    risk_notes: "HAD availability uncertain; mark N/A if unavailable by Week 3"

checkpoint:
  current_gate: 0/9
  completed_sub_hypotheses: []
  current_phase: "Phase-0-Validation"
  decision_points:
    - week: 1
      decision: "Phase 0 validation pass/fail"
      criteria: "reliability α > 0.7, convergent validity r > 0.5, power > 80%"
    - week: 3
      decision: "Pilot go/no-go"
      criteria: "ρ_j reliability > 0.7, effect size Δρ_j > 0.1"
    - week: 3
      decision: "HAD availability"
      criteria: "Author response or public access confirmed"
```

---

**END OF PHASE 2B VERIFICATION PLAN**
