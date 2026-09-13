# Verification Plan: RAG-Specific Corpus Curation

**Date:** 2026-07-12
**Hypothesis ID:** H-RAGCuration-v1
**Confidence:** 0.80
**Total Hypotheses:** 5 (1 Existence + 4 Mechanism)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under RAG corpus construction from Common Crawl, if a factorized ensemble of specialist retrieval-quality classifiers (trained on stratified BEIR success examples) filters documents, then the resulting corpus achieves ≥3% higher Recall@10 on factoid QA tasks compared to perplexity-based filtering (matched corpus size), because retrieval utility optimizes for factual density, entity coverage, and retrieval-specific quality dimensions orthogonal to pretraining fluency.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in Recall@10 between retrieval-quality filtered corpora and perplexity-filtered corpora when corpus size is held constant.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | BEIR Natural Questions (test set) (standard) | Natural Questions is factoid QA with extractive answers, ideal for controlled validation of retrieval utility. Test set size (~3.5K queries) sufficient for statistical power. Derived from Wikipedia, likely well-covered in Common Crawl (addresses coverage assumption). |
| **Model** | DPR (Dense Passage Retriever) | DPR is standard dense retrieval architecture widely used for RAG. Pre-trained on Natural Questions, ensuring reader model is well-calibrated for the task. Bi-encoder design allows indexing filtered corpora without retraining. |

**Dataset Details:**
- Source: BEIR benchmark (Thakur et al., 2021)
- Path: beir/nq

**Model Details:**
- Type: Dense retrieval (bi-encoder)
- Source: facebook/dpr-question_encoder-single-nq-base, facebook/dpr-ctx_encoder-single-nq-base

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Perplexity-based filtering | Not RAG-specific; serves as pretraining baseline | Common Crawl (600B tokens) | Optimizes for pretraining fluency, not retrieval utility |
| FineWeb-Edu educational filtering | +5.0pp MMLU, +4.5pp ARC for knowledge tasks | Common Crawl (15T tokens → 1.3T filtered) | Educational quality ≠ retrieval utility; may reject high-perplexity technical docs valuable for factoid retrieval |
| DataComp-LM model-based filtering | 7B model to 64% MMLU with 40% less compute than prior SOTA | 240T token pool → 3.8T DCLM-BASELINE | Optimizes for pretraining; FastText positive/negative examples selected for language modeling quality, not retrieval utility |

**Best Baseline**: FineWeb-Edu shows +5.0pp gains on knowledge-intensive tasks; if retrieval filtering achieves comparable Recall@10 gains (≥3%), demonstrates retrieval-specific quality dimension analogous to educational quality.

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | BEIR relevance annotations correlate with downstream task performance (QA answer accuracy), not just annotation agreement | BEIR is widely used benchmark, but discussion identified risk of annotation bias | Classifier trained on BEIR annotations may not improve actual retrieval utility; requires two-stage validation |
| A2 | Factual density and entity coverage are retrieval-specific quality signals orthogonal to pretraining quality (fluency, coherence) | Discussion consensus that retrieval values informativeness over narrative flow, but not empirically validated | If factual density correlates highly with educational quality, retrieval filtering is just reweighting pretraining-optimal documents |
| A3 | Common Crawl contains sufficient coverage of relevant information for Natural Questions test set (coverage failures <50% of BM25-failed queries) | Natural Questions derived from Wikipedia, likely well-covered in Common Crawl | If most query failures are coverage gaps (info absent), quality filtering cannot improve Recall measurably |
| A4 | Retrieval quality can be measured independent of reader model architecture (via controlled reader like BM25 + exact match) | Discussion identified confound: neural reader capabilities affect measured quality; proposed BM25 baseline control | Quality gains may reflect reader model bias, not document quality |
| A5 | Factorized multi-classifier approach preserves inter-document diversity needed for multi-hop reasoning | Discussion proposed diversity measurement (pairwise SBERT similarity <0.6) as validation | Single-document quality optimization may reduce diversity, harming coverage for complex queries |

### 1.6 Research Gap & Novelty

**Key Innovation**: Factorized specialist classifier ensemble that targets retrieval-specific quality dimensions (factual density, entity coverage) independent of pretraining quality, validated via stratified training on low-educational, high-BEIR examples.

**Preserved Novelty**: Demonstrates that data quality is task-specific and multi-dimensional (quality/coverage/diversity axes), not monolithic. Provides methodology for empirically characterizing filtering trade-offs for RAG, analogous to DataComp-LM's benchmark contribution for pretraining.

**Differentiation from Prior Work**:
- **DataComp-LM**: Optimizes for pretraining quality (MMLU); we optimize for retrieval utility (Recall@K) and demonstrate measurable divergence between these objectives. Methodology transfer but different quality dimension.
- **FineWeb-Edu**: Demonstrates domain-specific filtering (educational quality); we demonstrate task-specific filtering (retrieval utility). Analogous methodology applied to different inference mode (retrieval vs pretraining).
- **Perplexity-based filtering**: Perplexity is a pretraining-derived quality signal (fluency, coherence); retrieval-quality classifier learns task-specific signals (factual density, entity coverage) via supervised training on retrieval success examples.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Prerequisites | Gate | Status |
|----|------|-------------------|---------------|------|--------|
| H-E1 | Existence | Retrieval-quality filtering achieves ≥3% Recall@10 improvement vs perplexity baseline | None | MUST_WORK | Pending |
| H-M1 | Mechanism | Classifier learns factual density via stratified training | H-E1 | SHOULD_WORK | Pending |
| H-M2 | Mechanism | High-density documents improve semantic query retrieval (+4% vs +1% lexical) | H-M1 | SHOULD_WORK | Pending |
| H-M3 | Mechanism | Factorized approach preserves diversity (pairwise similarity <0.6) | H-M2 | SHOULD_WORK | Pending |
| H-M4 | Mechanism | Retrieval-optimal diverges from pretraining-optimal (<60% overlap, ≥2% gain from divergent subset) | H-M3 | SHOULD_WORK | Pending |

**Total: 5 hypotheses** (1 Existence + 4 Mechanism)

**Note**: Comparison hypotheses (H-CP*) deferred to Phase 5 Baseline Comparison.

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Retrieval-Quality Filtering Effectiveness

**Type:** EXISTENCE  
**Statement:** Under RAG corpus construction from Common Crawl, if a retrieval-quality classifier (trained on stratified BEIR success examples) filters documents, then the resulting 1M-document corpus achieves ≥3% higher Recall@10 on Natural Questions compared to perplexity-based filtering (matched corpus size), because the classifier learns to identify documents with high factual density and entity coverage.

**Rationale:**  
This existence hypothesis validates the core claim that retrieval-specific quality signals can be learned and applied to corpus curation. It establishes whether task-specific filtering (retrieval utility) measurably diverges from pretraining-optimal filtering (perplexity).

**Variables** (from Phase 2A):
- **Independent:** Filtering Strategy (Perplexity | Educational | Retrieval-Quality)
- **Dependent:** Recall@10 on BEIR Natural Questions test set (10K queries, DPR indexing)
- **Controlled:** Corpus Size (1M docs), Common Crawl source (100K sample), Retrieval Model (DPR)

**Verification Protocol:**
1. Train retrieval-quality FastText classifier on stratified BEIR examples (oversample low-educational, high-retrieval pairs)
2. Apply three filtering methods to Common Crawl 100K sample: Perplexity (GPT-2 threshold), Educational (FineWeb-style), Retrieval-Quality (FastText)
3. Index each 1M-document corpus with DPR (facebook/dpr-ctx_encoder-single-nq-base)
4. Measure Recall@10 on Natural Questions test queries (~3.5K queries from BEIR benchmark)
5. Statistical test: two-tailed t-test (3-5 replications, α=0.05, power=0.80)

**Success Criteria** (PoC: Direction-based):
- **Primary:** Recall@10_retrieval ≥ Recall@10_perplexity + 0.03 (absolute), p<0.05
- **Secondary:** Retrieval filtering also outperforms educational filtering baseline

**Gate:**
- **Type:** MUST_WORK (Phase 4 PoC gate)
- **If Fail:** If |ΔRecall@10| < 0.01 or p>0.05, retrieval-specific filtering provides no measurable advantage → ABORT or PIVOT to different quality signals

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A Section 5 (sh1_existence), Prediction P1

---

#### H-M1: Classifier Learns Factual Density via Stratified Training

**Type:** MECHANISM (Step 1 of 4)  
**Statement:** Under stratified training (oversampling low-educational, high-BEIR examples), the retrieval-quality classifier learns to identify documents with high factual density and entity coverage, as evidenced by classifier-selected documents showing ≥15% higher named entity density than perplexity-matched controls.

**Rationale:**  
Validates that stratified training explicitly targets retrieval-pretraining divergence by forcing the classifier to learn quality signals independent of educational fluency.

**Variables:**
- **Independent:** Stratified training strategy (oversample low-educational, high-BEIR)
- **Dependent:** Named entity density (entities per 100 tokens), Type-token ratio
- **Controlled:** Corpus sample size, FastText architecture, training epochs

**Verification Protocol:**
1. Train classifier on stratified BEIR examples (explicit low-educational, high-retrieval stratification)
2. Apply classifier to Common Crawl sample and select top-50K documents
3. Compute named entity density (spaCy NER) for classifier-selected vs perplexity-matched control set
4. Measure type-token ratio and other informativeness metrics
5. Statistical test: paired t-test comparing density distributions

**Success Criteria:**
- **Primary:** Entity density_retrieval ≥ entity density_perplexity × 1.15 (15% improvement)
- **Secondary:** Type-token ratio shows similar improvement pattern

**Gate:**
- **Type:** SHOULD_WORK
- **If Fail:** Classifier did not learn retrieval-specific signals → PIVOT to different training strategy or feature engineering

**Dependencies:** H-E1 (if retrieval filtering shows no Recall improvement, this mechanism is moot)

**Source:** Phase 2A Section 1.3, Causal Step 1

---

#### H-M2: High-Density Documents Improve Semantic Query Retrieval

**Type:** MECHANISM (Step 2 of 4)  
**Statement:** Documents with high factual density and entity coverage improve retrieval performance specifically on semantic queries (BM25-failed) by +4% Recall@10, compared to +1% improvement on lexical queries (BM25-succeeded), because high-density documents contain information in multiple phrasings and higher informativeness per token.

**Rationale:**  
Demonstrates that quality improvement is semantic (meaning-based), not just lexical coverage. Differential gains validate retrieval-specific utility beyond keyword matching.

**Variables:**
- **Independent:** Document factual density (from H-M1 classifier selection)
- **Dependent:** Recall@10 improvement on semantic vs lexical query subsets
- **Controlled:** Query split methodology (BM25 top-10 baseline), corpus size

**Verification Protocol:**
1. Split Natural Questions into Lexical (answer in BM25 top-10) vs Semantic (answer not in BM25 top-10) query subsets
2. Measure Recall@10 improvement (retrieval filter - perplexity baseline) for each subset separately
3. Compare ΔRecall_semantic vs ΔRecall_lexical to validate differential gain
4. Analyze query-document match patterns (multi-phrasing evidence)

**Success Criteria:**
- **Primary:** ΔRecall_semantic ≥ 0.04 AND ΔRecall_lexical ≤ 0.01 (differential gain ≥3pp)
- **Secondary:** Evidence of multi-phrasing in high-density documents

**Gate:**
- **Type:** SHOULD_WORK
- **If Fail:** If gains are uniform (ΔRecall_semantic ≈ ΔRecall_lexical), quality is just lexical coverage → EXPLORE alternative quality metrics

**Dependencies:** H-M1 (requires factual density validation)

**Source:** Phase 2A Section 1.3, Causal Step 2, Prediction P3

---

#### H-M3: Factorized Approach Preserves Diversity

**Type:** MECHANISM (Step 3 of 4)  
**Statement:** The factorized specialist classifier approach (multiple classifiers for factoid/argument/technical modes) preserves inter-document diversity while ensuring quality, as measured by average pairwise SBERT similarity <0.6 for retrieval-filtered corpus (vs <0.6 baseline), avoiding homogenization that single-quality-dimension filtering causes.

**Rationale:**  
Validates that multi-dimensional quality optimization does not reduce corpus diversity. Diversity preservation is critical for coverage of complex queries and multi-hop reasoning.

**Variables:**
- **Independent:** Classifier architecture (single vs factorized multi-specialist)
- **Dependent:** Average pairwise SBERT similarity, coverage diversity metrics
- **Controlled:** Corpus size, quality threshold, SBERT model (all-MiniLM-L6-v2)

**Verification Protocol:**
1. Compute pairwise SBERT embeddings for all documents in retrieval-filtered corpus
2. Calculate average pairwise cosine similarity across random 10K document sample
3. Compare retrieval-filtered diversity vs perplexity baseline and educational baseline
4. Analyze topic distribution (LDA clustering) to validate coverage breadth

**Success Criteria:**
- **Primary:** Average similarity_retrieval < 0.6 (maintains baseline diversity level)
- **Secondary:** Topic distribution breadth comparable to or exceeding baseline

**Gate:**
- **Type:** SHOULD_WORK
- **If Fail:** If similarity >0.7, diversity was not preserved → PIVOT to diversity-aware loss function or multi-classifier sampling

**Dependencies:** H-M2 (requires quality improvement validation)

**Source:** Phase 2A Section 1.3, Causal Step 3, Assumption A5

---

#### H-M4: Retrieval-Optimal Diverges from Pretraining-Optimal

**Type:** MECHANISM (Step 4 of 4)  
**Statement:** Retrieval-optimal and pretraining-optimal corpora diverge measurably (<60% overlap between top-50K selections), and the divergent subset (selected by retrieval, rejected by educational) contributes ≥2% absolute Recall@10 gain, because retrieval values factual density over narrative fluency (high-perplexity technical docs selected by retrieval filter, rejected by pretraining filter).

**Rationale:**  
Demonstrates performance-grounded divergence: the documents where retrieval and pretraining filters disagree are exactly the documents that drive retrieval performance gains. This validates the core meta-contribution that task-specific quality is multi-dimensional.

**Variables:**
- **Independent:** Filter selection criteria (retrieval-quality vs educational quality)
- **Dependent:** Corpus overlap percentage, Recall@10 contribution from divergent subset
- **Controlled:** Corpus size (50K for overlap analysis), quality threshold calibration

**Verification Protocol:**
1. Compute set intersection between top-50K documents from retrieval filter vs educational filter
2. Identify divergent subset: documents selected by retrieval filter but rejected by educational filter
3. Measure Recall@10 using (a) educational-filtered corpus alone, (b) educational + divergent subset
4. Calculate ΔRecall = metric(b) - metric(a) to quantify divergent subset contribution

**Success Criteria:**
- **Primary:** Overlap <60% AND ΔRecall ≥ 0.02 (divergent subset contributes ≥2pp gain)
- **Secondary:** Divergent documents show higher perplexity but higher entity density than educational baseline

**Gate:**
- **Type:** SHOULD_WORK
- **If Fail:** If overlap >80% OR ΔRecall <0.01, divergence is not performance-relevant → REFINE hypothesis scope to subset where divergence matters

**Dependencies:** H-M3 (requires diversity validation)

**Source:** Phase 2A Section 1.3, Causal Step 4, Prediction P2

---

<!--
Each hypothesis follows this format:

#### {H-ID}: {Title}

**Type:** {EXISTENCE|MECHANISM|CONDITION|COMPARISON}
**Statement:** {Full Under-If-Then-Because statement}

**Variables:**
- IV: {independent variable}
- DV: {dependent variable}
- CV: {controlled variables}

**Success Criteria:**
- {quantitative threshold 1}
- {quantitative threshold 2}

**Gate:**
- Type: {MUST_WORK|SHOULD_WORK|DETERMINES_SUCCESS}
- If Fail: {consequence}

**Prerequisites:** {list or "None"}

**Verification Protocol:** (100-150 words)
{step-by-step protocol}

---
-->

---

## 3. Execution

### 3.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - Retrieval-quality filtering effectiveness)
         │
         ▼
[Level 1 - Mechanism Chain]
    H-M1 (Classifier learns factual density)
         │  Dependencies: H-E1
         ▼
    H-M2 (High-density improves semantic retrieval)
         │  Dependencies: H-M1
         ▼
    H-M3 (Factorized approach preserves diversity)
         │  Dependencies: H-M2
         ▼
    H-M4 (Retrieval-optimal diverges from pretraining-optimal)
         │  Dependencies: H-M3
         ▼
    [Terminal - Verification Complete]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Depth: 4 levels (sequential chain)
Parallelization: None (each step depends on previous)
═══════════════════════════════════════════════════════════
```

**Dependency Hierarchy:**
- **Level 0**: H-E1 (root, no dependencies)
- **Level 1**: H-M1 (depends on H-E1)
- **Level 2**: H-M2 (depends on H-M1)
- **Level 3**: H-M3 (depends on H-M2)
- **Level 4**: H-M4 (depends on H-M3)

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Recall@10 ≥ baseline + 0.03, p<0.05 | ABORT or PIVOT to different quality signals |
| H-M1 | SHOULD_WORK | Entity density ≥ 1.15× baseline | PIVOT to different training strategy |
| H-M2 | SHOULD_WORK | ΔRecall_semantic ≥ 0.04, ΔRecall_lexical ≤ 0.01 | EXPLORE alternative quality metrics |
| H-M3 | SHOULD_WORK | Pairwise similarity < 0.6 | PIVOT to diversity-aware loss function |
| H-M4 | SHOULD_WORK | Overlap <60%, ΔRecall ≥ 0.02 | REFINE scope to divergence-relevant subset |

**Gate Decision Logic:**
- **MUST_WORK failure** (H-E1): Full stop → reassess entire hypothesis or abandon
- **SHOULD_WORK failure** (H-M1-4): Document limitation → refine mechanism understanding or scope

### 3.3 Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses (6 weeks total)
═══════════════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ Week 1-2 │ Week 3-4 │ Week 5 │ Week 6 │ Week 7
──────────────────────┼──────────┼──────────┼────────┼────────┼────────
PHASE 1: Foundation
  H-E1 Existence      │ ████████ │          │        │        │
  [Gate 1]            │          │ ◆        │        │        │
──────────────────────┼──────────┼──────────┼────────┼────────┼────────
PHASE 2: Mechanism Chain (4 steps)
  H-M1 Factual Dens.  │          │ ████████ │        │        │
  H-M2 Semantic Retr. │          │          │ ████   │        │
  H-M3 Diversity      │          │          │        │ ████   │
  H-M4 Divergence     │          │          │        │        │ ████
  [Gate 2]            │          │          │        │        │    ◆
──────────────────────┼──────────┼──────────┼────────┼────────┼────────
═══════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work (1-2 weeks) | ◆ = Gate decision point
Total Duration: 6 weeks (2 for H-E1 + 4 for H-M1-M4)
═══════════════════════════════════════════════════════════════════════════
```

**Timeline Breakdown:**

| Phase | Hypotheses | Duration | Activities |
|-------|------------|----------|------------|
| Phase 1 (Foundation) | H-E1 | 2 weeks | Train classifiers, filter corpus, run retrieval evaluation |
| Phase 2 (Mechanisms) | H-M1 | 2 weeks | Stratified training validation, entity density analysis |
| | H-M2 | 1 week | Query split analysis (lexical vs semantic) |
| | H-M3 | 1 week | Diversity measurement (SBERT similarity) |
| | H-M4 | 1 week | Corpus overlap analysis, divergent subset evaluation |

**Total Duration: 6 weeks**

**Critical Path Analysis:**
- **Sequential execution**: No parallelization possible (each hypothesis depends on previous)
- **Slack time**: 0 weeks (critical path = total duration)
- **Early termination option**: If H-E1 fails at Week 2 (Gate 1), can stop early

---

## 4. Risk Analysis

### 4.1 Assumption-Based Risks

**Risk R1: BEIR Annotation Bias**
- **Source:** Assumption A1 - BEIR relevance annotations may not correlate with downstream QA accuracy
- **Description:** Classifier trained on BEIR annotations may optimize for annotation agreement rather than actual retrieval utility
- **Affected Hypotheses:** H-E1, H-M1
- **Severity:** HIGH
- **Mitigation Strategy:**
  - **Prevention:** Two-stage validation (train on BEIR, validate on QA exact-match accuracy)
  - **Detection:** Compare BEIR Recall@10 vs QA answer accuracy correlation
  - **Response (if occurs):** PIVOT to QA-accuracy-based training labels instead of BEIR annotations

**Risk R2: Factual Density Correlates with Educational Quality**
- **Source:** Assumption A2 - Factual density may not be orthogonal to educational quality
- **Description:** If factual density correlates highly with educational quality (r>0.7), retrieval filtering is just reweighting pretraining-optimal documents
- **Affected Hypotheses:** H-M1, H-M2, H-M4
- **Severity:** HIGH
- **Mitigation Strategy:**
  - **Prevention:** Stratified training explicitly oversamples low-educational, high-BEIR examples
  - **Detection:** Compute correlation between entity density and educational scores
  - **Response (if r>0.7):** REFINE classifier to explicitly penalize educational fluency signals

**Risk R3: Coverage Gaps Dominate Quality Effects**
- **Source:** Assumption A3 - Coverage failures may exceed 50% of BM25-failed queries
- **Description:** If most query failures are coverage gaps (information absent in corpus), quality filtering cannot improve Recall measurably
- **Affected Hypotheses:** H-E1, all H-M
- **Severity:** MEDIUM
- **Mitigation Strategy:**
  - **Prevention:** Use Natural Questions (Wikipedia-derived) which is well-covered in Common Crawl
  - **Detection:** Answer string search in corpus (coverage vs quality failure audit)
  - **Response (if coverage gaps >50%):** SCOPE to queries where coverage exists, focus on quality-coverage trade-off characterization

**Risk R4: Reader Model Confound**
- **Source:** Assumption A4 - Neural reader capabilities may affect measured quality
- **Description:** Quality gains may reflect DPR reader model bias rather than document quality
- **Affected Hypotheses:** H-E1, H-M2
- **Severity:** MEDIUM
- **Mitigation Strategy:**
  - **Prevention:** Control with BM25 baseline (lexical-only reader)
  - **Detection:** Compare gains under DPR vs BM25 retrieval
  - **Response (if DPR-only gains):** VALIDATE with multiple reader architectures (Contriever, BM25+reranker)

**Risk R5: Diversity Loss from Quality Optimization**
- **Source:** Assumption A5 - Single-document quality optimization may reduce inter-document diversity
- **Description:** Factorized approach may still homogenize corpus (pairwise similarity >0.7)
- **Affected Hypotheses:** H-M3, all hypotheses (diversity needed for coverage)
- **Severity:** MEDIUM
- **Mitigation Strategy:**
  - **Prevention:** Factorized multi-classifier approach targets multiple retrieval modes
  - **Detection:** Pairwise SBERT similarity measurement (threshold: <0.6)
  - **Response (if similarity >0.7):** PIVOT to diversity-aware loss function (add diversity term) or diversity-aware positive example sampling

### 4.2 Risk Summary Table

| ID | Risk | Severity | Likelihood | Affected | Early Warning Indicator | Mitigation |
|----|------|----------|------------|----------|------------------------|------------|
| R1 | BEIR annotation bias | HIGH | Medium | H-E1, H-M1 | BEIR-QA accuracy correlation <0.5 | Two-stage validation |
| R2 | Density-educational correlation | HIGH | Medium | H-M1, H-M2, H-M4 | Correlation r>0.7 | Stratified training |
| R3 | Coverage gaps dominate | MEDIUM | Low | All | Coverage failures >50% | Answer string audit |
| R4 | Reader model confound | MEDIUM | Low | H-E1, H-M2 | DPR gains but no BM25 gains | Multi-reader validation |
| R5 | Diversity loss | MEDIUM | Medium | H-M3, All | Pairwise similarity >0.7 | Diversity-aware loss |

**Critical Risks:** 2 (R1, R2)  
**High Risks:** 2 (R1, R2)  
**Medium Risks:** 3 (R3, R4, R5)

---

## 5. Dialectical Analysis

### 5.1 Thesis Statement

**Core Claim:** Under RAG corpus construction from Common Crawl, retrieval-quality filtering (trained on stratified BEIR examples) achieves ≥3% higher Recall@10 on factoid QA compared to perplexity-based filtering, because retrieval utility optimizes for factual density and entity coverage orthogonal to pretraining fluency.

**Supporting Evidence:**
1. **Mechanism Evidence:** DataComp-LM demonstrated model-based classifiers learn quality signals from positive/negative examples; stratified training extends this to retrieval-pretraining divergence
2. **Task-Specificity:** FineWeb showed quality metrics beyond fluency (educational content) drive task-specific gains; retrieval context extends this to factual density
3. **Testable Predictions:** Three quantitative predictions with clear success/failure thresholds enable rigorous falsification

**Strengths:**
- **Established methodology:** Builds on validated DataComp-LM and FineWeb techniques
- **Clear causal mechanism:** 4-step chain from classifier training to divergence validation
- **Rigorous experimental design:** Controlled comparison with matched corpus size, statistical testing (α=0.05, power=0.80)

**Expected Outcomes:**
- **Primary:** ≥3% Recall@10 improvement (retrieval vs perplexity filtering)
- **Secondary:** <60% corpus overlap with ≥2% gain from divergent subset
- **Tertiary:** Differential semantic query gain (+4% semantic vs +1% lexical)

### 5.2 Antithesis (Null Hypothesis)

**Null Hypothesis (H0):** There is no significant difference in Recall@10 between retrieval-quality filtered and perplexity-filtered corpora when corpus size is held constant.

**Counter-Arguments:**
1. **Baseline insufficiency:** Perplexity filtering optimizes for fluency, but fluency may correlate with informativeness—no divergence expected
2. **Assumption violations:** BEIR annotations may reflect human annotation bias toward fluent documents (A1); factual density may correlate with educational quality (A2)
3. **Scope limitations:** Restricted to factoid QA with extractive answers; generalization to other retrieval modes (argumentative, multi-hop) not validated

**Potential Failure Points:**
- **R1 (BEIR bias):** Classifier optimizes for annotation agreement, not retrieval utility → no QA accuracy gains
- **R2 (Density-educational correlation):** Retrieval filtering just reweights pretraining-optimal documents → overlap >80%
- **R3 (Coverage gaps):** Quality filtering cannot improve Recall if information is absent → gains <1%

**Conditions Under Which H0 Would Be Supported:**
- If |ΔRecall@10| < 0.01 or p>0.05 (no statistically significant difference)
- If mechanism chain breaks at H-M1 (classifier fails to learn retrieval-specific signals)
- If corpus overlap >80% AND divergent subset contributes <1% gain (no performance-relevant divergence)

### 5.3 Synthesis

**Balanced Assessment:**

The hypothesis H-RAGCuration-v1 presents a testable claim that retrieval-quality filtering produces measurably better RAG corpora than perplexity-based filtering by optimizing for task-specific quality dimensions (factual density, entity coverage). However, the null hypothesis raises valid concerns regarding annotation bias (R1), potential correlation between factual density and educational quality (R2), and scope limitations to factoid QA.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes existence of ≥3% Recall@10 improvement before investigating mechanism
2. **Sequential mechanism testing (H-M1-M4):** Tests 4-step causal chain to validate *why* retrieval filtering works
3. **Risk mitigation:** Two-stage validation (R1), stratified training (R2), coverage audits (R3) address key failure modes
4. **Gate conditions:** MUST_WORK gate at H-E1 allows early termination if no effect detected

**Conditions for Thesis Support:**
- H-E1 passes (Recall@10_retrieval ≥ baseline + 0.03, p<0.05)
- H-M1 validates (entity density ≥ 1.15× baseline, proving retrieval-specific learning)
- H-M4 confirms divergence (<60% overlap, ≥2% gain from divergent subset)

**Conditions for Antithesis Support:**
- H-E1 fails (|ΔRecall@10| < 0.01 or p>0.05) → no existence of effect
- H-M1 fails (entity density ≈ baseline) → classifier did not learn retrieval-specific signals
- Corpus overlap >80% OR divergent subset gain <1% → no performance-relevant divergence

**Nuanced Outcome Possibilities:**
1. **Full Thesis Support:** All 5 hypotheses pass → retrieval-optimal corpus curation validated, meta-contribution confirmed (task-specific quality is multi-dimensional)
2. **Partial Support:** H-E1 + some H-M pass → effect exists but mechanism partially understood; refine causal model
3. **Null Support:** H-E1 fails → no effect detected; PIVOT to different quality signals or ABORT hypothesis
4. **Scope-Limited Support:** Works for factoid QA but not generalizable → document as factoid-specific technique

**Robustness Assessment:**

The dialectical structure ensures robust verification:
- **If thesis is correct:** Sequential mechanism tests provide mechanistic evidence beyond correlation
- **If antithesis is correct:** Early gate (H-E1) detects null effect quickly (2 weeks), minimizing wasted effort
- **If reality is nuanced:** Gate structure allows documenting partial support with refined scope

---

## 6. Summary

### 6.1 Executive Summary

This verification plan operationalizes the hypothesis **H-RAGCuration-v1**: that retrieval-quality filtering (trained on stratified BEIR examples) produces RAG corpora with ≥3% higher Recall@10 on factoid QA compared to perplexity-based filtering, because retrieval utility optimizes for factual density and entity coverage orthogonal to pretraining fluency.

**Verification Structure:**
- **5 hypotheses** (1 Existence + 4 Mechanism)
- **6-week timeline** (2 weeks foundation + 4 weeks mechanism chain)
- **2 critical gates** (MUST_WORK at H-E1, SHOULD_WORK at H-M1)
- **5 identified risks** with mitigation strategies

**Key Innovation:** Demonstrates task-specific data quality is multi-dimensional (retrieval utility ≠ pretraining fluency), providing meta-contribution framework for RAG corpus curation analogous to DataComp-LM's benchmark role for pretraining.

### 6.2 Verification Readiness

**Ready to Proceed:**
- ✅ Clear testable predictions with quantitative thresholds
- ✅ Experimental setup validated (BEIR Natural Questions, DPR, Common Crawl)
- ✅ Risk mitigation strategies defined for all 5 critical assumptions
- ✅ Sequential dependency structure with early termination option
- ✅ Baseline comparison methods identified (perplexity, educational filtering)

**Phase 2C Experiment Design - Next Steps:**
1. Generate detailed experiment specifications for each hypothesis (Level 1.5 design)
2. Implement retrieval-quality classifier training pipeline (stratified BEIR sampling)
3. Design corpus filtering and indexing infrastructure (DPR integration)
4. Implement measurement protocols (Recall@10, entity density, diversity metrics)
5. Create statistical testing framework (bootstrap, t-tests, Fisher combined)

### 6.3 Success Criteria Summary

| Gate | Hypothesis | Metric | Threshold | Action if Fail |
|------|------------|--------|-----------|----------------|
| Gate 1 (MUST_WORK) | H-E1 | Recall@10 improvement | ≥ +0.03, p<0.05 | ABORT or PIVOT |
| Gate 2 (SHOULD_WORK) | H-M1 | Entity density ratio | ≥ 1.15× | Document limitation |
| | H-M2 | Semantic query gain | ΔRecall_sem ≥ 0.04 | Explore alternatives |
| | H-M3 | Diversity preservation | Similarity < 0.6 | Add diversity term |
| | H-M4 | Divergence validation | Overlap <60%, Δ≥0.02 | Refine scope |

**Minimum Success:** H-E1 passes → existence validated, proceed to publication even if mechanisms partially understood  
**Full Success:** All 5 hypotheses pass → complete mechanistic understanding, meta-contribution confirmed

---
