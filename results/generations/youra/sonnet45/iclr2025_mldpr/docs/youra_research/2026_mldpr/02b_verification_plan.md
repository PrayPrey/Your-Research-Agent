# Verification Plan: Lifecycle-Stage Functional Separability in Cross-Repository Metadata

**Date:** 2026-03-18
**Hypothesis ID:** H-LifecycleSep-v1
**Confidence:** 0.80
**Total Hypotheses:** 3 (H-E1, H-M-integrated, H-C1)
**Mode:** Incremental (Phase 2A-based, 60% scope reduction)

---

## Executive Summary

This verification plan decomposes the main hypothesis (lifecycle-stage functional separability via semantic clustering) into 3 testable sub-hypotheses with dynamic structure based on Phase 2A analysis. Scope reduction: 60% (3 BUILD_ON claims established, 1 PROVE_NEW). Early falsification gates at Week 3 (H-E1: κ ≥ 0.60, probe ≥ 0.75) enable pivot decisions. Three-tier validation framework: baseline comparisons → stylistic controls → repository stratification. Total timeline: 6 weeks proof-of-concept.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under cross-repository metadata field conditions (HuggingFace, OpenML, UCI), if metadata fields are embedded using semantic representations (field names + example values), then unsupervised clustering will recover lifecycle-stage functional separability at 2-tier granularity (General Information vs. Responsible AI per Roman et al. 2023) that exceeds strong baselines by ≥0.15 NMI, because lifecycle categories reflect cognitively natural documentation partitions that manifest as distributional regularities (lexical, normative, value-structural) in metadata text when documentation is sufficiently structured.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in Normalized Mutual Information (NMI) between semantic clustering and baseline methods (permutation, topic model, lexical heuristic) for recovering 2-tier lifecycle structure, or NMI on unscaffolded datasets does not exceed 0.6, indicating lifecycle separability is interface-induced rather than intrinsic to metadata semantics.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Cross-Repository Metadata Sample (custom) | Heterogeneous metadata schemas across repositories test lifecycle separability under real-world schema variability |
| **Model** | Sentence Transformers (all-MiniLM-L6-v2) | Frozen embeddings enable linear separability probe and unsupervised clustering without fine-tuning artifacts |

**Dataset Details:**
- Source: HuggingFace Hub API, OpenML API, UCI repository web scraping
- Path: N=300 stratified sample (150 HF [75 scaffolded Open Datasheets, 75 unscaffolded], 100 OpenML, 50 UCI)

**Model Details:**
- Type: Semantic embedding model
- Source: Hugging Face Transformers library

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Manual cross-repository field mapping | N/A (expert annotation) | Same metadata sample | Not scalable, lacks automation |
| Lexical keyword matching | NMI ~0.45 (estimated) | Same metadata sample | Ignores distributional context and semantic nuance |
| Topic modeling (LDA) | NMI ~0.40-0.50 (estimated) | Same metadata sample | Bag-of-words approach misses sequential and normative structure |

**Best Baseline:** Lexical heuristic NMI ~0.45

### 1.5 Key Assumptions

| ID | Assumption | Supporting Evidence | If Violated |
|----|------------|---------------------|-------------|
| A1 | Lifecycle categories transfer across repositories despite contextual adaptation | Roman's 2-tier structure worked across diverse dataset producers; hypothesis scope-limited to 2-tier | If κ_across < 0.6 but κ_within ≥ 0.7 → PIVOT to scoped claims (structured repos only) |
| A2 | Distributional signatures exist in unscaffolded metadata (not solely interface-induced) | Gebru's pilots refined questions that elicited consistent responses → latent structure pre-exists scaffolding | If NMI(S) - NMI(U) > 0.2 → signal amplification interpretation, intrinsic claim weakens |
| A3 | Semantic embeddings encode lifecycle role linearly (accessible to simple probes) | Computational linguistics literature shows stance/modality features emerge in frozen embeddings | If linear probe < 0.75 → PIVOT to normative geometry hypothesis (nonlinear encoding) |
| A4 | Length/modality normalization controls for stylistic artifacts without destroying semantic signal | NLP literature shows length normalization preserves semantic content while removing surface biases | If normalized NMI collapses → amplification is stylistic not semantic, mechanism revision required |
| A5 | Cross-repository DQI variance reduction reflects improved comparability (not signal compression) | External validity anchor (correlation with citation/update frequency) validates construct validity | If mapped DQI doesn't correlate with external proxies → clustering compresses signal, failed practical utility |

### 1.6 Research Gap & Novelty

**Gap:** Existing repository-specific tools (F-UJI, FAIRshake) assess metadata within single repositories. No automated cross-repository semantic mapping exists for documentation lifecycle structure across heterogeneous schemas.

**Novelty:** First automated cross-repository semantic mapping (inverse of Roman et al. 2023's single-repo scaffolding). Tests whether lifecycle categories emerge as computational semantic structure without explicit templates, enabling ecosystem-wide meta-analysis.

---

## 2. Hypothesis Inventory

### 2.1 H-E1: Lifecycle Separability Existence

**Statement**: Cross-repository metadata fields exhibit measurable lifecycle-stage separability: inter-annotator agreement κ ≥ 0.60 across repositories AND linear probe accuracy ≥ 0.75 on scaffolded data, validating that lifecycle constructs are operationally stable and signals are linearly detectable.

**Rationale**: H-E1 validates the foundation for all subsequent hypotheses by establishing that (1) lifecycle constructs are reliable measurement tools with operational stability, and (2) semantic embeddings contain detectable lifecycle signals that are linearly encoded. These are necessary conditions for testing unsupervised clustering recovery.

**Variables**:
- Independent: Repository Type (HuggingFace, OpenML, UCI)
- Dependent (Primary): Inter-annotator Agreement (κ), Linear Probe Accuracy
- Controlled: Sample Size (N=300 stratified), Text Length, Annotation Protocol

**Verification Protocol**:
1. Three expert annotators independently label N=300 metadata fields with 2-tier lifecycle taxonomy (General Info vs RAI), blind to repository source
2. Compute Cohen's κ for each repository and overall κ_across to measure construct reliability
3. Train logistic regression probe on scaffolded HF embeddings (75 samples) to test linear separability
4. Test probe accuracy on held-out scaffolded data to validate signal detectability
5. Compare κ_within_repo vs κ_across to identify repository context effects

**Success Criteria**:
- Primary: κ_across ≥ 0.60 AND linear probe accuracy ≥ 0.75
- Secondary: κ_within ≥ 0.70 for structured repos (HF, OpenML)

**Failure Response**:
- IF κ < 0.60: PIVOT to repository-scoped claims (lifecycle is context-dependent)
- IF probe < 0.75: PIVOT to normative geometry hypothesis (nonlinear encoding)

**Gate Type**: MUST_WORK (pipeline continuation depends on passage)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 5 (sh1_existence), Prediction P1

---

### 2.2 H-M-integrated: Complete Mechanism Chain

**Statement**: Semantic embeddings encode lifecycle role via distributional signatures (lexical co-occurrence, normative modality, value-structural patterns), enabling unsupervised clustering to recover 2-tier lifecycle structure that exceeds baselines (permutation, LDA, lexical) by ≥0.15 NMI after controlling for stylistic artifacts through length/modality normalization and repository stratification.

**Rationale**: H-M-integrated tests the full causal mechanism through three validation tiers: (1) baseline comparisons establish semantic value, (2) stylistic controls distinguish signal from artifact, (3) repository stratification tests generalization. This addresses the key tension from Phase 2A: signal amplification vs interface-induced separability.

**Variables**:
- Independent: Embedding Method (4 levels), Repository Scaffolding (scaffolded/unscaffolded), Repository Type
- Dependent (Primary): NMI (Normalized Mutual Information), NMI Baseline Gap
- Controlled: Text Length (normalized), Modality Density (filtered), Sample Size

**Verification Protocol**:
1. Compute NMI for 3 baselines (permutation, LDA 2-topic, lexical keyword matching) on unscaffolded sample to establish comparison points
2. Run unsupervised K-means clustering (k=2) on semantic embeddings (all-MiniLM-L6-v2), measure NMI against 2-tier labels
3. Apply length normalization and modality filtering (deontic language removal), recompute NMI to test signal persistence
4. Train repository-specific linear probes (HF/OpenML/UCI separate), measure accuracy variance to test generalization
5. Compare scaffolded vs unscaffolded NMI gap to quantify interface amplification effect

**Success Criteria**:
- Primary: NMI(unsupervised) > 0.6 AND improvement over max(baselines) ≥ 0.15
- Secondary: Normalized NMI ≥ 0.6 (signal persists after controls), Probe variance < 0.1 (generalization)

**Failure Response**:
- IF NMI < 0.6 OR baseline gap < 0.15: EXPLORE - embeddings insufficient, test alternative representations
- IF normalized NMI collapses: PIVOT - amplification is stylistic not semantic
- IF probe variance > 0.15: SCOPE - lifecycle is repository-specific

**Gate Type**: SHOULD_WORK (graceful degradation: partial success yields scoped claims)

**Dependencies**: H-E1 (requires κ ≥ 0.60, probe ≥ 0.75)

**Source**: Phase 2A Section 1.3 (causal_mechanism 3 steps), Section 1.6 (Predictions P1-P2)

---

### 2.3 H-C1: Boundary Conditions

**Statement**: Lifecycle separability mechanism operates under boundary conditions: (C1) requires structured documentation (repos with metadata conventions), (C2) limited to 2-tier granularity (General vs RAI), (C3) requires example values (names-only embeddings insufficient), because distributional signatures manifest only when documentation has sufficient structure and semantic context.

**Rationale**: H-C1 transforms potential weaknesses into boundary discoveries by deliberately testing expected failure modes. Boundary failures define applicability scope rather than invalidate the hypothesis, yielding scientifically valuable scoped claims (e.g., "works for structured repos, not unstructured").

**Variables**:
- Independent: Documentation Structure (structured/unstructured), Lifecycle Granularity (2-tier/7-stage), Embedding Input (names/values/combined)
- Dependent: NMI Performance, Linear Probe Accuracy per condition
- Controlled: Sample Size per condition, Annotation Protocol

**Verification Protocol**:
1. Stratify UCI sample by documentation quality (structured vs unstructured subset) to isolate structure effect
2. Re-annotate structured sample with 7-stage Datasheets labels (vs 2-tier) to test granularity limit
3. Generate three embedding variants (names_only, values_only, combined) for same fields
4. Measure NMI and probe accuracy for each condition to identify performance drop thresholds
5. Identify boundary thresholds where mechanism performance degrades significantly

**Success Criteria**:
- Primary: Performance drop >0.2 NMI across boundaries (validates boundary exists)
- Secondary: Structured NMI ≥ 0.6 but unstructured < 0.4 (structure necessary)

**Failure Response**:
- IF no performance drop: EXPLORE - boundaries more fluid than expected, mechanism more general
- IF all conditions fail: ABANDON - mechanism scope narrower than anticipated

**Gate Type**: OPTIONAL (boundary discovery, high scientific value either outcome)

**Dependencies**: H-M-integrated (requires mechanism validation first)

**Source**: Phase 2A Section 1.5 (scope boundaries), Section 1.6 (Prediction P2 interface effects)

---

## 3. Risk Analysis

### Risk-Hypothesis Mapping

| Risk | Source | Description | Severity | Affected | Mitigation |
|------|--------|-------------|----------|----------|------------|
| R1 | A1 | Lifecycle categories don't transfer across repositories | HIGH | H-E1, H-M | **Prevention**: 2-tier scope reduction. **Detection**: Compare κ_across vs κ_within. **Response**: PIVOT to repository-scoped claims |
| R2 | A2 | Distributional signatures are interface-induced not intrinsic | HIGH | H-M | **Prevention**: Test unscaffolded first. **Detection**: Scaffolded vs unscaffolded gap. **Response**: PIVOT to signal amplification interpretation |
| R3 | A3 | Lifecycle encoding is nonlinear not linear | MEDIUM | H-E1, H-M | **Prevention**: Frozen embeddings. **Detection**: Linear probe Week 3. **Response**: PIVOT to normative geometry hypothesis |
| R4 | A4 | Normalization destroys semantic signal | MEDIUM | H-M | **Prevention**: Pre-register interpretation. **Detection**: Compare raw vs normalized NMI. **Response**: SCOPE to raw embeddings |
| R5 | A5 | DQI-citation causality reversed | LOW | H-M (P3) | **Prevention**: Correlation not causation claims. **Detection**: Compute correlations. **Response**: ACKNOWLEDGE longitudinal design needed |

### Risk Summary

- Critical: 0
- High: 2 (Repository transfer, Interface artifact)
- Medium: 2 (Nonlinear encoding, Normalization destroys signal)
- Low: 1 (Causality ambiguity)

---

## 4. Dependency Graph & Execution Order

### DAG Visualization

```
[Foundation]
    ↓
  H-E1 (MUST_WORK)
    ↓ (κ ≥ 0.60, probe ≥ 0.75)
    ↓
  H-M-integrated (SHOULD_WORK)
    ↓ (NMI > 0.6, baseline gap ≥ 0.15)
    ↓
  H-C1 (OPTIONAL)
```

### Execution Order

1. **H-E1** (Week 3): Foundation validation, early falsification gate
2. **H-M-integrated** (Week 4-5): Mechanism validation with three-tier tests
3. **H-C1** (Week 6): Boundary discovery (optional)

---

## 5. Timeline (6-Week Proof-of-Concept)

| Week | Tasks | Hypotheses | Gate |
|------|-------|------------|------|
| 1-2 | Data collection (APIs), Expert annotation protocol setup | - | - |
| 3 | H-E1 execution: κ measurement, Linear probe training/testing | H-E1 | MUST_WORK |
| 4 | Baseline tests, Unsupervised clustering, Normalization controls | H-M | - |
| 5 | Repository stratification, Probe variance, DQI variance testing | H-M | SHOULD_WORK |
| 6 | Boundary testing (structure, granularity, embeddings), Synthesis | H-C1 | OPTIONAL |

**Critical Path**: Week 3 gate determines pipeline continuation

---

## 6. Dialectical Analysis

**Thesis**: Lifecycle categories manifest as intrinsic distributional structure in metadata that semantic embeddings capture geometrically, enabling unsupervised clustering recovery.

**Antithesis** (H0): Separability is interface-induced artifact - scaffolding creates stylistic homogenization that clusters detect, not intrinsic semantic lifecycle structure.

**Synthesis**: Signal amplification framework - scaffolding enhances but does not create lifecycle separability. Test: 0.1 ≤ NMI(scaffolded) - NMI(unscaffolded) ≤ 0.2 after length/modality normalization. This range indicates measurable amplification while preserving intrinsic signal (NMI(unscaffolded) > 0.6 validates intrinsic structure).

---

## 7. Success Criteria Summary

| Hypothesis | Primary Criterion | Secondary Criterion | Gate |
|------------|-------------------|---------------------|------|
| H-E1 | κ ≥ 0.60 AND probe ≥ 0.75 | κ_within ≥ 0.70 | MUST_WORK |
| H-M-integrated | NMI > 0.6, baseline gap ≥ 0.15 | Normalized NMI ≥ 0.6, variance < 0.1 | SHOULD_WORK |
| H-C1 | Performance drop > 0.2 across boundaries | Structured ≥ 0.6, unstructured < 0.4 | OPTIONAL |

---

## 8. Next Steps

1. **Immediate**: Phase 2C Experiment Design (generate detailed experiment specifications for H-E1 first)
2. **Week 1-2**: Begin data collection and annotation protocol development
3. **Week 3**: Execute H-E1 early falsification gate
4. **Contingency**: Prepare PIVOT strategies for Week 3 gate failures

---

**Phase 2B Complete** | verification_state.yaml generated | Ready for Phase 2C
