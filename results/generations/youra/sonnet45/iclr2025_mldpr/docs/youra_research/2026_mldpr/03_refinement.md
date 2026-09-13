# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-18T06:47:10Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: Cross-Repository Metadata Field Mapping
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: Established fully specified, falsifiable hypothesis with quantified thresholds, strong baselines, stylistic controls, stratified analyses, and external validity anchors. Reframed ontology fragility and interface effects into measurable amplification and boundary-condition phenomena.

### Key Insights

1. **Signal Amplification Framework**: Reframed interface scaffolding from threat (artifact concern) to testable phenomenon (signal amplification with quantified gap 0.1-0.2)

2. **Three-Tier Falsification**: Early gates (Week 3 baseline tests) enable pivot/proceed decisions before investing in full clustering pipeline

3. **Repository Stratification**: Transforms potential failures (context-dependence) into scoped scientific findings (lifecycle encoding varies by repository structure)

### Breakthrough Moments

- **Exchange 3**: Prof. Pax identified scaffolding-induced separability risk, leading to scaffolded vs. unscaffolded (S vs. U) comparison test design

- **Exchange 12**: Dr. Nova proposed normative geometry hypothesis (modal density encoding of lifecycle role beyond lexical features)

- **Exchange 14**: Prof. Rex formalized strong baseline requirement (≥0.15 NMI improvement), establishing falsification threshold

---

## Final Hypothesis

### Title
Lifecycle-Stage Functional Separability in Cross-Repository Metadata via Unsupervised Semantic Clustering

### Core Claim
Under cross-repository metadata field conditions (HuggingFace, OpenML, UCI), if metadata fields are embedded using semantic representations (field names + example values), then unsupervised clustering will recover lifecycle-stage functional separability at 2-tier granularity (General Information vs. Responsible AI per Roman et al. 2023) that exceeds strong baselines by ≥0.15 NMI, because lifecycle categories reflect cognitively natural documentation partitions that manifest as distributional regularities (lexical, normative, value-structural) in metadata text when documentation is sufficiently structured.

### Mechanism
**Step 1**: Lifecycle categories (Gebru's 7 stages mapped to Roman's 2 tiers) reflect cognitively natural partitions validated through iterative pilot testing—Gebru's organizational feedback and Roman's user evaluations confirmed consistent categorization behavior.

**Step 2**: Structured documentation creates distributional signatures: lexical co-occurrence (procedural verbs for Collection, licensing terms for Distribution), normative modality (deontic language for RAI), value-structural patterns (temporal markers for Maintenance).

**Step 3**: Semantic embeddings (sentence transformers) capture these signatures as geometric structure, enabling unsupervised recovery without explicit supervision.

---

## Predictions

**P1 (Primary)**: Semantic clustering of unscaffolded metadata fields will achieve NMI > 0.6 for 2-tier lifecycle separation, exceeding strong baselines (permutation, topic model, lexical heuristic) by ≥0.15
- **Test**: Unsupervised clustering on embeddings; baseline comparisons
- **Success**: NMI ≥ 0.6 AND improvement ≥ 0.15
- **Falsification**: NMI < 0.6 or improvement < 0.15

**P2**: Interface scaffolding amplifies but does not create separability: 0.1 ≤ NMI(scaffolded) - NMI(unscaffolded) ≤ 0.2 after length/modality normalization
- **Test**: HF datasets WITH vs. WITHOUT Open Datasheet markup
- **Success**: Gap in range [0.1, 0.2] after controls
- **Falsification**: Gap > 0.2 (interface-induced) or < 0.05 (no amplification)

**P3**: Cross-repository DQI variance reduction while preserving within-repository dynamic range
- **Test**: Analogous datasets DQI variance before/after clustering
- **Success**: σ²_between decreases (p<0.05), σ²_within stable (±10%), external correlation validated
- **Falsification**: Variance reduction without external correlation (signal compression)

---

## Novelty

**Key Innovation**: First automated cross-repository semantic mapping for documentation lifecycle structure—solves the inverse problem of Roman et al. 2023's single-repository scaffolding

**Differentiation from Prior Work**:
- Roman et al. 2023: Supervised scaffolding within HuggingFace using wizard interface → Our work: Unsupervised discovery across heterogeneous repositories (OpenML, UCI, legacy datasets)
- Gebru et al. 2018: Lifecycle as reflective question framework → Our work: Lifecycle as emergent computational semantic structure
- Existing FAIR tools (F-UJI, FAIRshake): Repository-specific assessment → Our work: Cross-repository semantic equivalence mapping

**Research Directions Opened**:
1. Automated datasheet scaffolding for legacy datasets lacking structured templates
2. Ecosystem-wide meta-analysis: which lifecycle stages systematically under-documented
3. Transfer learning for documentation governance (train on HF+OpenML, deploy to new repos)

---

## Experimental Design

**Dataset**: Cross-Repository Metadata Sample (N=300 stratified: 150 HF [75 scaffolded, 75 unscaffolded], 100 OpenML, 50 UCI)

**Model**: Sentence Transformers (all-MiniLM-L6-v2) frozen embeddings

**Baselines**:
- Permutation (random 2-way split)
- Topic Model (LDA 2-topic clustering)
- Lexical Heuristic (license/privacy keywords for RAI, name/source for General)

**Timeline**: 6 weeks proof-of-concept
- Week 1-2: Data collection (API calls + scraping)
- Week 3: Expert annotation (κ measurement) + linear probe (early falsification gates)
- Week 4: Clustering experiments (4 ablations: names, values, combined, +structural) + perturbation tests
- Week 5: DQI variance analysis + external correlation validation
- Week 6: Write-up

---

## Limitations

1. **Sample Size**: N=300 pilot limits generalizability; full ecosystem coverage requires larger scale
2. **Expert Annotation Bottleneck**: κ measurement requires human effort (Week 3 constraint)
3. **Causality Ambiguity**: DQI-citation correlation may reverse (popular datasets get better documentation post-hoc)—longitudinal design needed
4. **Repository Stratification**: May reveal context-dependence (lifecycle encoding stronger in structured repos like HF/OpenML vs. UCI)—transforms into scoped findings rather than universal claims

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Fully specified falsifiable hypothesis with 5 quantified thresholds and three-tier validation |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (Prof. Rex's concerns addressed via mitigation strategies) |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
