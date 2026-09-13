# Verification Plan: Interpretable Error Taxonomy for LLM Benchmarks

**Date:** 2026-04-14
**Hypothesis ID:** H-ErrorTaxonomy-v1
**Confidence:** 0.8
**Total Hypotheses:** 5

---

## 0. Established Facts & Scope Reduction

### 0.1 Build-On Claims (DO NOT RE-VERIFY)

| Claim | Status | Evidence |
|-------|--------|----------|
| Published benchmark results contain category-level error rate data | BUILD_ON | Verified by Prof. Pax - GPT-4, Claude-3, Llama-3 technical reports available |
| Previous unsupervised clustering (h-e1) failed due to API dependency | BUILD_ON | Phase 0 failure analysis - technical failure, not scientific invalidity |

**Scope Reduction:** 33% of claims already validated (2 of 3 claims are BUILD_ON)

### 0.2 Prove-New Claims (FOCUS OF VERIFICATION)

| Claim | Why Novel | Verification Approach |
|-------|-----------|----------------------|
| Category-level supervision available but item-level ground truth rare | Core challenge - must demonstrate weak supervision suffices | H-E1, H-M1-4 test weak supervision framework |

**Phase 2B-4 Instructions:** Focus on expert agreement (Cohen kappa) not prediction accuracy

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the scope of existing LLM benchmarks with published results (TruthfulQA, MMLU), if we extract interpretable features from question metadata and analyze category-level error patterns across multiple models, then we can generate an error taxonomy achieving ≥0.7 Cohen's kappa agreement with human expert categorization, because systematic failure patterns exist in question characteristics that transcend individual model implementations.

### 1.2 Alternative Hypothesis (H0)

Taxonomy category assignments are no better than random assignment, showing Cohen kappa ≤0.3, indicating patterns are artifacts not systematic error modes.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA + MMLU (standard) | Rich metadata, published results, cross-benchmark testing |
| **Model** | Published results GPT/Claude/Llama (current+baseline) | Eliminates API dependency, enables temporal comparison |

**Dataset Details:**
- Source: Public benchmarks
- Path: github.com/sylinrl/TruthfulQA + github.com/hendrycks/test

**Model Details:**
- Type: Published evaluations (no API calls)
- Source: Technical reports

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| GPT-4 Technical Report aggregate scores | ~60% TruthfulQA | TruthfulQA | No error mode categorization |
| Manual error analysis | Qualitative, small samples | Various | Not systematic, not automated |
| Category Mean Baseline | N/A | To be tested | Predict from category average only |
| Single-Feature Baseline | N/A | To be tested | Use only question length |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Published error rates are accurate and representative | Major lab technical reports undergo review and are high-stakes claims | Taxonomy built on noisy data, reduced validity |
| A2 | Metadata features capture difficulty without semantic understanding | Linguistic complexity metrics correlate with comprehension difficulty | Feature ceiling - need semantic analysis |
| A3 | Experts can reliably categorize errors (IRR ≥0.6) | Tested in pilot study | If IRR <0.5, task too subjective |
| A4 | Patterns reflect general LLM limitations not benchmark artifacts | Cross-benchmark validation tests this | Benchmark-specific, no generalization |
| A5 | Three model families provide sufficient diversity | Independent training (OpenAI, Anthropic, Meta) | Model-family artifacts |

### 1.6 Research Gap & Novelty

**Gap:** No systematic error taxonomy with quantitative expert validation using only published results exists.

**Key Innovation:** Diagnostic framing (pattern discovery) not predictive accuracy. Uses Cohen's kappa as interpretability gold standard.

**Differentiation:**
- vs Manual error analysis: Automated systematic framework
- vs Unsupervised clustering (h-e1): Supervised with expert validation, no API
- vs Aggregate benchmark scoring: Fine-grained interpretable categories

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Prerequisites | Gate |
|----|------|-------------------|---------------|------|
| H-E1 | Existence | Published category-level error rates exist for ≥3 model families | None | MUST_WORK |
| H-M1 | Mechanism | Metadata features correlate with errors (intrinsic difficulty) | H-E1 | MUST_WORK |
| H-M2 | Mechanism | Category-level rates provide signal for item clustering | H-M1 | SHOULD_WORK |
| H-M3 | Mechanism | Clustered errors are interpretable via expert recognition | H-M2 | SHOULD_WORK |
| H-M4 | Mechanism | Taxonomy generalizes across benchmarks (fundamental not artifacts) | H-M3 | SHOULD_WORK |

**Total:** 5 hypotheses (1 Existence + 4 Mechanism)

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Published Benchmark Error Data Existence

**Type:** Existence

**Statement:** Under the scope of major LLM benchmarks (TruthfulQA, MMLU), if we examine published technical reports from multiple model families (GPT, Claude, Llama), then we can extract category-level error rates for ≥3 model families across ≥2 timepoints (baseline vs current), because major labs publish detailed benchmark results as high-stakes performance claims.

**Rationale:** Foundation hypothesis validating data availability. Without published category-level error data, the entire weak supervision approach is infeasible. This tests the BUILD_ON claim that published results contain sufficient granularity.

**Variables:**
- Independent: Model families (GPT, Claude, Llama), Timepoints (baseline: GPT-3.5/Claude-2/Llama-2, current: GPT-4/Claude-3/Llama-3)
- Dependent: Availability of category-level error rates (binary: available/not available)
- Controlled: Benchmark selection (TruthfulQA, MMLU only), Source type (technical reports only)

**Verification Protocol:**
1. Search technical reports for GPT-4, Claude-3, Llama-3 on TruthfulQA and MMLU
2. Extract category-level performance tables from each report
3. Verify baseline model data availability (GPT-3.5, Claude-2, Llama-2)
4. Confirm ≥3 model families × 2 timepoints = 6 data sources available
5. Document granularity level (confirm category-level, not just aggregate)

**Success Criteria (PoC: Direction-based):**
- Primary: ≥3 model families with category-level data for both timepoints
- Secondary: Data granularity sufficient (≥10 categories per benchmark)

**Gate:**
- Type: MUST_WORK
- If Fail: ABORT - entire approach infeasible without published data

**Dependencies:** None (foundation)

**Source:** Phase 2A Section 5 (sh1_existence), Established Facts

---

#### H-M1: Metadata-Error Correlation via Intrinsic Difficulty

**Type:** Mechanism (Step 1 of 4)

**Statement:** Under the scope of TruthfulQA questions with extracted metadata features (question type, topic, answer format, complexity, linguistic patterns), if we compute correlation with category-level error rates, then we observe significant positive correlation (Spearman ρ ≥0.4) between metadata features and errors, because metadata captures intrinsic difficulty that transcends individual model implementations (supported by Item Response Theory).

**Rationale:** Tests first causal link - whether metadata features actually correlate with errors. If metadata doesn't predict errors, downstream clustering will fail. IRT evidence suggests item characteristics predict difficulty cross-population.

**Variables:**
- Independent: Question Metadata Features (5 types: question_type, topic, answer_format, complexity, linguistic_patterns)
- Dependent: Category-level error rate (continuous, 0-100%)
- Controlled: Benchmark (TruthfulQA), Model families (3), Statistical test (Spearman correlation)

**Verification Protocol:**
1. Extract metadata features from TruthfulQA repository (817 questions)
2. Parse published category-level error rates from technical reports
3. Compute Spearman correlation between each feature and error rates
4. Test significance (p < 0.05) and effect size (ρ ≥0.4)
5. Identify top-3 predictive features for taxonomy design

**Success Criteria (PoC: Direction-based):**
- Primary: ≥2 features show ρ ≥0.4 with p < 0.05
- Secondary: Cross-model consistency (same features correlate across all 3 families)

**Gate:**
- Type: MUST_WORK
- If Fail: PIVOT to semantic features (BERT embeddings) or EXPLORE alternative feature sets

**Dependencies:** H-E1 (data must exist before correlation analysis)

**Source:** Phase 2A Causal Step 1, Evidence: Item Response Theory

---

#### H-M2: Weak Supervision via Category-Level Signal

**Type:** Mechanism (Step 2 of 4)

**Statement:** Under the scope of TruthfulQA items with correlated metadata features, if we apply weak supervision clustering using category-level error rates as noisy labels, then we achieve within-category variance <50% of between-category variance, because category-level rates propagate via shared features enabling item-level clustering despite coarse supervision.

**Rationale:** Tests weak supervision core - whether coarse category-level labels suffice for item-level clustering. This is the key tension: category supervision for item validation. Success means weak supervision framework works.

**Variables:**
- Independent: Clustering algorithm (K-means, hierarchical, DBSCAN tested), Feature set (from H-M1)
- Dependent: Within/between category variance ratio (continuous, target <0.5)
- Controlled: Number of clusters (5-15 range), Distance metric (Euclidean), Sampling (stratified)

**Verification Protocol:**
1. Use top-3 features from H-M1 for clustering
2. Apply 3 clustering algorithms with category-level rates as initialization
3. Compute within-category variance / between-category variance
4. Test cluster stability via bootstrapping (100 iterations)
5. Select algorithm with lowest variance ratio

**Success Criteria (PoC: Direction-based):**
- Primary: Variance ratio <0.5 (clusters more distinct than random)
- Secondary: Cluster stability >0.7 (consistent across bootstrap samples)

**Gate:**
- Type: SHOULD_WORK
- If Fail: Document as limitation - may need more features or different clustering approach

**Dependencies:** H-M1 (correlated features required for clustering)

**Source:** Phase 2A Causal Step 2, Evidence: Weak supervision paradigm

---

#### H-M3: Expert Interpretability via Pattern Recognition

**Type:** Mechanism (Step 3 of 4)

**Statement:** Under the scope of clustered error patterns from H-M2, if we recruit 3 NLP/LLM experts with standardized annotation instructions to categorize 100 TruthfulQA items independently, then we achieve Cohen's kappa ≥0.7 between expert categories and taxonomy categories, because experts recognize interpretable systematic patterns (validated by inter-rater reliability IRR ≥0.6).

**Rationale:** Tests interpretability via expert validation - the gold standard for taxonomy quality. Cohen's kappa accounts for chance agreement. Expert IRR ≥0.6 confirms task is not too subjective. This is the primary success criterion from Phase 2A.

**Variables:**
- Independent: Taxonomy categories (from H-M2 clustering), Expert background (NLP/LLM evaluation experience)
- Dependent: Expert-Taxonomy Agreement (Cohen's kappa, range -1 to 1, success ≥0.7)
- Controlled: Annotation instructions (standardized), Sample size (100 items), Expert count (3)

**Verification Protocol:**
1. Sample 100 TruthfulQA items stratified by category
2. Recruit 3 experts via conference/university networks ($3000 budget)
3. Provide standardized instructions with category definitions and examples
4. Collect independent expert annotations
5. Compute Cohen's kappa (expert vs taxonomy) and IRR (expert vs expert)
6. Bootstrap confidence intervals (95% CI)

**Success Criteria (PoC: Direction-based):**
- Primary: Cohen's kappa ≥0.7 AND expert IRR ≥0.6
- Secondary: ≥80% of top-3 features per category rated interpretable by majority

**Gate:**
- Type: SHOULD_WORK
- If Fail: PIVOT to fewer categories or EXPLORE alternative annotation protocols

**Dependencies:** H-M2 (clustered taxonomy must exist before expert validation)

**Source:** Phase 2A Causal Step 3, Prediction P1 (primary)

---

#### H-M4: Cross-Benchmark Generalization Test

**Type:** Mechanism (Step 4 of 4)

**Statement:** Under the scope of the taxonomy validated on TruthfulQA (H-M3), if we apply the same taxonomy to 100 sampled MMLU items with the same expert protocol, then we achieve Cohen's kappa ≥0.6, because the taxonomy captures fundamental LLM error modes not TruthfulQA-specific artifacts (cross-benchmark transfer validates systematic patterns).

**Rationale:** Tests generalization - distinguishes systematic patterns from benchmark quirks. Lower threshold (0.6 vs 0.7) accounts for domain differences. If kappa <0.4, patterns are TruthfulQA-specific and not generalizable.

**Variables:**
- Independent: Benchmark (TruthfulQA → MMLU transfer), Taxonomy (from H-M3)
- Dependent: Cross-Benchmark Transfer Kappa (continuous, range -1 to 1, success ≥0.6)
- Controlled: Expert protocol (identical to H-M3), Sample size (100 MMLU items), Stratification (by subject)

**Verification Protocol:**
1. Sample 100 MMLU items stratified by subject area
2. Apply TruthfulQA taxonomy categories to MMLU
3. Use same 3 experts with identical annotation instructions
4. Compute Cohen's kappa (expert vs taxonomy) on MMLU sample
5. Compare MMLU kappa to TruthfulQA kappa (expected drop <0.1)

**Success Criteria (PoC: Direction-based):**
- Primary: Cross-benchmark kappa ≥0.6
- Secondary: ≥30% of categories show ≥15pp improvement baseline→current (temporal analysis)

**Gate:**
- Type: SHOULD_WORK
- If Fail: Document as TruthfulQA-specific, narrow scope claims

**Dependencies:** H-M3 (validated taxonomy required for transfer test)

**Source:** Phase 2A Causal Step 4, Prediction P2

---

## 3. Risk Analysis

### 3.1 Assumption-to-Risk Mapping

#### Risk R1: Published Error Rate Inaccuracy

**Source Assumption:** A1 - Published error rates are accurate and representative

**Description:** Technical reports may contain errors, cherry-picked results, or non-representative sampling, leading to noisy supervision signal.

**Affected Hypotheses:** H-E1, H-M1, H-M2

**Severity:** Medium (likelihood: Low, impact: Medium)

**Mitigation Strategy:**
1. **Prevention:** Cross-validate across multiple sources (compare OpenAI/Anthropic/Meta reports)
2. **Detection:** Statistical outliers in category-level rates (>3σ from mean)
3. **Response:**
   - PIVOT: Weight sources by confidence (multiple-source agreement gets higher weight)
   - SCOPE: Exclude outlier categories from analysis
   - ABORT: If <50% of data is reliable

**Early Warning Indicators:**
- Inconsistent category definitions across reports
- Error rates that don't sum correctly (>5% deviation)

---

#### Risk R2: Metadata Feature Ceiling

**Source Assumption:** A2 - Metadata features capture difficulty without semantic understanding

**Description:** Shallow metadata may miss semantic patterns requiring deeper NLU, limiting correlation strength and taxonomy richness.

**Affected Hypotheses:** H-M1, H-M2

**Severity:** High (likelihood: Medium, impact: High)

**Mitigation Strategy:**
1. **Prevention:** Test diverse feature sets early (linguistic, statistical, structural)
2. **Detection:** Correlation plateau (ρ <0.3) for all metadata features
3. **Response:**
   - PIVOT: Add semantic features (BERT embeddings, topic models)
   - SCOPE: Focus on surface patterns only (question type, format)
   - ABORT: If no features correlate (ρ <0.2)

**Early Warning Indicators:**
- Top features explain <20% variance
- Expert review finds categories non-intuitive

---

#### Risk R3: Expert Subjectivity (Low IRR)

**Source Assumption:** A3 - Experts can reliably categorize errors (IRR ≥0.6)

**Description:** Error categorization may be too subjective, preventing reliable expert agreement and invalidating kappa as interpretability measure.

**Affected Hypotheses:** H-M3

**Severity:** Critical (likelihood: Medium, impact: Critical)

**Mitigation Strategy:**
1. **Prevention:** Pilot study with 20 items to validate IRR ≥0.5 before full annotation
2. **Detection:** IRR <0.5 on pilot or full sample
3. **Response:**
   - PIVOT: Reduce categories (merge similar ones to increase agreement)
   - SCOPE: Focus on high-agreement subset only
   - ABORT: If IRR <0.4 (task too subjective for quantitative validation)

**Early Warning Indicators:**
- Pilot IRR 0.4-0.5 (borderline)
- Experts request clarification on >30% of items

---

#### Risk R4: Benchmark Specificity (No Transfer)

**Source Assumption:** A4 - Patterns reflect general LLM limitations not benchmark artifacts

**Description:** Taxonomy may be TruthfulQA-specific, failing to generalize to MMLU or other benchmarks, limiting scientific contribution.

**Affected Hypotheses:** H-M4

**Severity:** High (likelihood: Medium, impact: High)

**Mitigation Strategy:**
1. **Prevention:** Design taxonomy with cross-benchmark patterns in mind (e.g., "negation handling" vs "TruthfulQA category 7")
2. **Detection:** Cross-benchmark kappa <0.4
3. **Response:**
   - PIVOT: Identify generalizable subset (categories with kappa ≥0.5)
   - SCOPE: Frame as "TruthfulQA error taxonomy" with limited claims
   - ABORT: If <40% of categories transfer

**Early Warning Indicators:**
- Category names reference TruthfulQA-specific content
- MMLU experts struggle to apply categories

---

#### Risk R5: Insufficient Model Diversity

**Source Assumption:** A5 - Three model families provide sufficient diversity

**Description:** GPT/Claude/Llama may share architectural biases, missing errors unique to other paradigms (retrieval-augmented, smaller models).

**Affected Hypotheses:** All (generalization claim)

**Severity:** Medium (likelihood: Low, impact: Medium)

**Mitigation Strategy:**
1. **Prevention:** Document model scope clearly (autoregressive LLMs, >10B params)
2. **Detection:** Taxonomy categories cluster by model family (family-specific patterns)
3. **Response:**
   - PIVOT: Add 1-2 additional families if budget allows (e.g., Gemini, Mistral)
   - SCOPE: Narrow claims to "major frontier LLMs"
   - ABORT: Not applicable (limitation acknowledgment sufficient)

**Early Warning Indicators:**
- Categories align perfectly with known model differences (context length limits)
- Patterns disappear with model architecture changes

---

### 3.2 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Published data inaccuracy | A1 | Medium | H-E1, H-M1-2 | Cross-validate sources |
| R2 | Metadata feature ceiling | A2 | High | H-M1-2 | Pivot to semantic features |
| R3 | Expert subjectivity | A3 | Critical | H-M3 | Pilot study, reduce categories |
| R4 | Benchmark specificity | A4 | High | H-M4 | Extract generalizable subset |
| R5 | Model diversity limits | A5 | Medium | All | Scope to frontier LLMs |

**Critical Risks:** 1 (R3)
**High Risks:** 2 (R2, R4)
**Medium Risks:** 2 (R1, R5)
**Low Risks:** 0

---

## 4. Dependency Graph & Timeline

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - Published data available)
         │
         ▼
[Level 1 - Foundation]
    H-M1 (Metadata-error correlation)
         │
         ▼
[Level 2 - Clustering]
    H-M2 (Weak supervision clustering)
         │
         ▼
[Level 3 - Validation]
    H-M3 (Expert interpretability)
         │
         ▼
[Level 4 - Generalization]
    H-M4 (Cross-benchmark transfer)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 4.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3      │ W4      │ W5      │ W6      
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │         
  [Gate 1]       │         │ ◆       │         │         │         
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │         
  [Gate 2]       │         │         │ ◆       │         │         
  H-M2           │         │         │ ████    │         │         
  H-M3           │         │         │         │ ████    │         
  H-M4           │         │         │         │         │ ████    
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 4.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4

**Total Duration:** 6 weeks
- Formula: 2 (H-E1) + 1 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4) = 6 weeks

**Slack Available:** 0 weeks (all sequential dependencies)

**Gate Decision Points:**
- **Gate 1 (Week 2):** H-E1 completion → MUST PASS (data exists)
- **Gate 2 (Week 3):** H-M1 completion → MUST PASS (correlation exists)
- Subsequent H-M failures → document limitations, don't abort

### 4.5 Resource Summary

**Total Hypotheses:** 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)

**Verification Phases:** 2
1. Foundation (H-E1)
2. Mechanisms (H-M1-4)

**Execution Mode:** Sequential chain
**Critical Path Length:** 6 weeks

### 4.6 Execution Order

**Step 1:** Execute H-E1 (Foundation) - Week 1-2
- Search and extract published benchmark data

**Step 2:** Evaluate Gate 1 → If pass, proceed
- Verify ≥3 model families × 2 timepoints

**Step 3:** Execute H-M1 (First mechanism) - Week 3
- Compute metadata-error correlations

**Step 4:** Evaluate Gate 2 → If pass, proceed
- Verify ρ ≥0.4 for ≥2 features

**Step 5:** Execute H-M2 to H-M4 sequentially - Week 4-6
- H-M2: Weak supervision clustering
- H-M3: Expert validation (primary success criterion)
- H-M4: Cross-benchmark transfer

**Final:** Verification complete

---

## 5. Dialectical Analysis

### 5.1 Thesis

**Core Claim:** Systematic error patterns exist in LLM benchmarks that can be captured via metadata-based taxonomy achieving ≥0.7 Cohen's kappa expert agreement using only published results.

**Supporting Evidence:**
1. Item Response Theory shows item characteristics predict difficulty cross-population
2. Weak supervision paradigm demonstrates coarse labels can propagate via shared features
3. Expert validation via Cohen's kappa is standard for taxonomy quality assessment
4. Cross-benchmark transfer tests distinguish systematic patterns from artifacts

**Strengths:**
- Based on established IRT and weak supervision theory
- Clear 4-step causal mechanism with testable predictions
- No API dependency (avoids h-e1 failure mode)
- Quantitative interpretability measure (kappa) not qualitative

**Expected Outcomes:**
- Primary: Cohen's kappa ≥0.7 on TruthfulQA (H-M3)
- Secondary: Cross-benchmark kappa ≥0.6 on MMLU (H-M4)
- Tertiary: ≥80% features interpretable (expert survey)
- Temporal: ≥30% categories improve ≥15pp baseline→current

---

### 5.2 Antithesis

**Null Hypothesis (H0):** Taxonomy category assignments are no better than random assignment, showing Cohen kappa ≤0.3, indicating patterns are artifacts not systematic error modes.

**Counter-Arguments:**
1. Published results may be cherry-picked or non-representative (R1)
2. Metadata features may be too shallow to capture error modes (R2 - feature ceiling)
3. Expert categorization may be too subjective (R3 - IRR <0.5)
4. Patterns may be TruthfulQA-specific artifacts (R4 - no transfer)
5. Three model families may share architectural biases (R5)

**Potential Failure Points:**
- H-E1 fails: Published data lacks category-level granularity
- H-M1 fails: No metadata features correlate (ρ <0.2) → feature ceiling
- H-M3 fails: Kappa <0.5 OR expert IRR <0.5 → too subjective
- H-M4 fails: Cross-benchmark kappa <0.4 → TruthfulQA-specific

**Conditions Under Which H0 Would Be Supported:**
- If Cohen's kappa ≤0.3 (random-level agreement)
- If expert IRR <0.5 (task too subjective)
- If H-E1 or H-M1 MUST_WORK gates fail (foundation broken)

---

### 5.3 Synthesis

**Balanced Assessment:**

The hypothesis H-ErrorTaxonomy-v1 presents a testable claim that systematic error patterns can be discovered via weak supervision with expert validation. However, the null hypothesis raises valid concerns regarding metadata feature limitations (R2), expert subjectivity (R3), and benchmark specificity (R4).

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes data availability before investing in taxonomy
2. **Sequential mechanism testing (H-M1-4):** Tests each causal link independently with clear falsification criteria
3. **Gate conditions:** Allow early detection of H0 support (H-E1/H-M1 failures abort quickly)
4. **Risk mitigation:** Pilot study for R3, cross-validation for R1, semantic pivot for R2

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M1)
- Primary prediction confirmed (kappa ≥0.7, IRR ≥0.6)
- Mechanism chain validates through H-M3 minimum

**Conditions for Antithesis Support:**
- H-E1 fails (data not available at category level)
- H-M1 fails (no metadata correlation, ρ <0.2)
- H-M3 fails (kappa <0.5 OR IRR <0.5)

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 through H-M4 all pass → Thesis validated, generalizable taxonomy
2. **Partial Support:** H-M1-3 pass, H-M4 fails → TruthfulQA-specific taxonomy (still publishable at workshop)
3. **Minimal Support:** H-E1/H-M1 pass, H-M3 fails → Patterns exist but not interpretable (pivot to semantic features)
4. **No Support:** H-E1 or H-M1 fail → Antithesis supported, approach infeasible

---

### 5.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| **Existence** | Published data contains category-level rates | May lack granularity or be cherry-picked | H-E1 verifies granularity, cross-validates sources (R1 mitigation) |
| **Mechanism** | 4-step causal chain (metadata→clustering→expert→transfer) | Alternative explanations (artifacts, subjectivity) | Each H-M tests one link with falsification criteria |
| **Interpretability** | Kappa ≥0.7 demonstrates expert-recognizable patterns | Experts may disagree (IRR <0.5) | Pilot study gates H-M3, kappa accounts for chance |
| **Generalization** | Cross-benchmark transfer proves systematic patterns | TruthfulQA-specific artifacts | H-M4 tests MMLU transfer, threshold 0.6 (lower than 0.7) |

**Overall Robustness Score:** Medium-High
- Strong theoretical foundation (IRT, weak supervision)
- Clear falsification criteria at each step
- Critical risk (R3) mitigated via pilot study
- Early gates (H-E1, H-M1) prevent wasted effort

**Confidence in Verification Plan:** 0.8
- Matches Phase 2A confidence level
- Sequential gates allow adaptive response
- Risks identified with mitigation strategies

---

## 6. Executive Summary

**Main Hypothesis:** Systematic error taxonomy achievable at ≥0.7 kappa using only published results
- ID: H-ErrorTaxonomy-v1, Confidence: 0.8

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 5 total (1 Existence + 4 Mechanism)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 MUST_WORK decision points (H-E1, H-M1)

**Risk Assessment:** Medium
- Critical risk: Expert subjectivity (R3) - mitigated via pilot study
- High risks: Feature ceiling (R2), Benchmark specificity (R4)

**Scope Reduction:** 33% efficiency gain
- 2 of 3 claims BUILD_ON (already validated)
- Focus verification on weak supervision framework only

**Immediate Action:** Begin Phase 1 with H-E1 (data extraction)

---

## 7. Key Achievements & Recommendations

### 7.1 Key Achievements

- 5 hypotheses across 2 verification phases
- H0 addressed: Kappa ≤0.3 indicates random patterns (artifacts)
- Dynamic structure: 4-step mechanism matches Phase 2A causal chain
- Risk-aware: 5 risks identified with mitigation strategies

### 7.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Published category-level error rates exist for ≥3 model families
- Gate 1: MUST PASS (abort if data unavailable)

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Metadata features correlate with errors (ρ ≥0.4)
- H-M2: Category-level rates enable item clustering (variance ratio <0.5)
- H-M3: Expert validation achieves kappa ≥0.7, IRR ≥0.6 (PRIMARY)
- H-M4: Cross-benchmark transfer kappa ≥0.6 on MMLU
- Gate 2: H-M1 must pass (correlation must exist)

### 7.3 Critical Decision Points

**Gate 1 (Foundation) - Week 2:**
- PASS: ≥3 model families with category-level data → Proceed to H-M1
- FAIL: Data lacks granularity → ABORT (approach infeasible)

**Gate 2 (Mechanism) - Week 3:**
- CRITICAL PASS: ρ ≥0.4 for ≥2 features → Proceed to H-M2
- CRITICAL FAIL: ρ <0.2 for all features → PIVOT to semantic features or ABORT

**H-M3 Pilot Decision - Week 4:**
- Pilot IRR ≥0.5 → Proceed with full 100-item annotation
- Pilot IRR <0.5 → PIVOT to fewer categories or ABORT if <0.4

### 7.4 Open Questions (from Phase 2A)

- Optimal clustering algorithm? (K-means vs hierarchical vs DBSCAN)
- Ideal number of taxonomy categories? (5-15 range to test)
- Can HuggingFace leaderboard supplement technical reports? (Additional data source)

### 7.5 Recommendations

**Immediate Actions:**
1. Start Phase 1 with H-E1 (data extraction from technical reports)
2. Set up measurement infrastructure (feature extraction pipeline)
3. Recruit expert pool early (3-month lead time for conference sourcing)

**Resource Allocation:**
- Allocate 6 weeks for critical path (H-E1 through H-M4)
- Reserve 2-week buffer for failures and pivots
- Budget $3000 for expert annotation (identified in Phase 2A)

**Failure Management:**
- Document all failures with root cause analysis
- Execute PIVOT strategies per risk mitigation plans (Section 3)
- Gate 1/2 failures trigger immediate user consultation

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml
- **Hypothesis ID:** H-ErrorTaxonomy-v1
- **Causal Chain:** 4 steps validated by 6-persona round table
- **Convergence:** All objections addressed, READY status

### B. Workflow Execution Notes
- **MCP Services:** Unavailable (Archon, ClearThought, Exa not configured)
- **Analysis Method:** Manual analytical decomposition based on Phase 2A structure
- **Mode:** UNATTENDED (all steps auto-executed)
- **Duration:** Steps 0-10 completed in single session

### C. Phase 2C Integration
- **State File:** verification_state.yaml (generated in Step 10)
- **Next Phase:** Phase 2C - Experiment Design for each hypothesis
- **Invocation:** /phase2c-experiment-design or /hypothesis-next skill

---

*Generated by YouRA Phase 2B Planning Workflow v7.7.0 | 2026-04-14*
*Execution Mode: UNATTENDED | Analysis: Manual (MCP unavailable)*
