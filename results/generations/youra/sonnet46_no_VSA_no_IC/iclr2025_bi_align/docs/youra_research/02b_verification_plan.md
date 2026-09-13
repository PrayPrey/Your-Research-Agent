---
title: "Verification Plan: Citation Asymmetry in Bidirectional Alignment"
hypothesis_id: H-CitAsym-v1
date: "2026-08-20"
status: complete
stepsCompleted:
  - step-00-init-environment
  - step-01-init-parsing
  - step-02-input-hypothesis
  - step-03-hypothesis-generation
  - step-04-hypothesis-inventory
  - step-05-risk-analysis
  - step-06-dependency-graph
  - step-07-timeline-planning
  - step-08-dialectical-analysis
  - step-09-summary
  - step-10-finalize
completedAt: "2026-08-20T10:00:00+00:00"
researchMode: incremental
totalHypotheses: 4
scopeReductionPercent: 57
---

# Verification Plan: Citation Asymmetry in Bidirectional Alignment

**Date:** 2026-08-20
**Hypothesis ID:** H-CitAsym-v1
**Confidence:** 0.78
**Total Hypotheses:** 4
**Research Mode:** Incremental (Phase 2A available)

---

## Section 0: Established Facts & Scope Reduction

**57% scope reduction applied — 5 of 8 claims are BUILD_ON (pre-validated).**

| Claim | Status | Evidence |
|-------|--------|----------|
| huashen218 corpus is ~400 interdisciplinary alignment papers with venue/discipline metadata | BUILD_ON | Shen et al. 2024 (arXiv:2406.09264) |
| S2AG provides directed citation edges via public API | BUILD_ON | Wade 2022 — 205M+ publications, 2.5B edges |
| HCI papers show increasing self-citation rates 2010-2020 (X-index) | BUILD_ON | Chen 2024 (CHI EA, arXiv:2303.07539) |
| NLP papers cite NLP papers at 10-30x base rate (within-field preference) | BUILD_ON | Wahle et al. 2023 EMNLP (arXiv:2310.14870) |
| Chi-squared / Fisher's exact on 2×2 contingency table is valid for cross-group citation independence | BUILD_ON | Standard method; Wahle et al. 2023 applied analogously |
| No prior directed citation graph from huashen218 corpus testing directional asymmetry | **PROVE_NEW** | Phase 1 literature review — gap 2 empirically open |
| AI→HCI citation rate significantly lower than HCI→AI within huashen218 corpus | **PROVE_NEW** | Core hypothesis — not yet tested |
| Within-group citation density (AI→AI, HCI→HCI) exceeds cross-group density | **PROVE_NEW** | Community siloing sub-hypothesis — not yet tested |

**Phase 2B focuses exclusively on 3 PROVE_NEW claims. BUILD_ON facts are treated as pre-validated.**

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the huashen218 bidirectional alignment corpus (~400 papers, 2018-2024), if papers are classified by venue group (AI-centered: NeurIPS/ICML/ICLR/ACL/EMNLP; HCI-centered: CHI/CSCW/IUI) using S2AG fieldsOfStudy with venue string fallback, then the directed citation ratio AI→HCI / HCI→AI < 1.0 (chi-squared p < 0.05 on the 2×2 citation contingency table), because ML/NLP alignment research is primarily self-referential to ML/NLP foundations (RLHF, safety, fine-tuning), while HCI alignment research — engaging with applied AI deployment in sociotechnical contexts — systematically cites ML/NLP foundational work to ground its user-facing analyses.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in the proportion of AI→HCI vs HCI→AI directed citation edges within the huashen218 alignment corpus (ratio = 1.0, chi-squared p ≥ 0.05).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | huashen218/bidirectional-alignment-reading-list + S2AG API (standard) | Corpus directly instantiates the research question — ~400 papers across ML/NLP and HCI venues. S2AG provides directed citation edges needed for 2×2 contingency table. Both public and immediately accessible. |
| **Model** | NetworkX DiGraph + scipy.stats | NetworkX DiGraph handles directed citation edge construction and betweenness centrality; scipy.stats provides chi-squared and Fisher's exact tests. ~100 lines Python, no ML models required. |

**Dataset Details:**
- Source: GitHub (huashen218/bidirectional-alignment-reading-list) + Semantic Scholar API
- Path: GitHub corpus: paper IDs (DOI/arXiv); S2AG: /paper/{id}/references and /paper/{id}/citations endpoints

**Model Details:**
- Type: bibliometric analysis pipeline
- Source: Standard Python libraries (networkx, scipy, requests)

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| Wahle et al. 2023 (EMNLP) — "We are Who We Cite" | NLP papers heavily cite CS but cited back proportionally less by other fields | 77k NLP papers, 3.1M+ citations via S2AG | Different corpus (NLP broadly, not alignment specifically); does not test HCI vs ML alignment distinction |
| Chen 2024 (CHI EA) — X-index | HCI self-citation (X-index) increasing 2010-2020 | CHI/UIST/CSCW papers 2010-2020 | Only HCI direction; doesn't measure AI→HCI or test asymmetry on alignment corpus |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | S2AG covers ≥70% of huashen218 corpus papers with resolved paper IDs | S2AG indexes 205M+ publications; huashen218 papers are from indexed venues | Sample representativeness compromised; must characterize unresolved papers and argue for non-systematic dropout |
| A2 | huashen218 corpus has ≥30 cross-group directed edges for chi-squared analysis | Community preference effect (Wahle 2023: 10-30x base rate); prior estimate 240-720 edges | Chi-squared test under-powered; shift to descriptive statistics and bridge paper analysis only |
| A3 | Venue classification by S2AG fieldsOfStudy + venue string fallback produces valid ML_NLP/HCI separation for ≥80% of corpus papers | Wahle et al. 2023 used same S2AG approach successfully for 77k papers | Sensitivity analysis across 3 classification schemes isolates classification-dependent findings |
| A4 | Citation proportions (cross-group citations / total outgoing citations) are age-invariant within each cohort | Both numerator and denominator scale with time; proportion robust to citation age accumulation | Temporal cohort analysis confounded; must use citations-per-year normalization as fallback |
| A5 | Curated nature of huashen218 does not systematically bias citation direction | Shen et al. 2024 describes systematic review process across HCI, NLP, ML venues — not citation-graph-based selection | Findings must be explicitly scoped to corpus-level claims; field-level generalization requires matched baseline |

### 1.6 Research Gap & Novelty

**Novelty:** First directed citation graph analysis of the huashen218 bidirectional alignment corpus; first empirical test of structural asymmetry claimed qualitatively by Shen et al. 2024 and ICLR 2025 Workshop CFP.

**Key Innovation:** Citation directionality as a bias-free, objective operationalization of community asymmetry — avoids all three prior failure modes: (1) SPECTER2 centroid bias, (2) cross-corpus N=1 overlap, (3) TF-IDF keyword definitional circularity.

**Differentiation:**
- vs. Wahle et al. 2023: Different corpus (NLP broadly vs alignment specifically); different research question (field influence vs bidirectional alignment community structure)
- vs. Chen 2024: Different corpus (HCI broadly vs alignment corpus); different direction (self-citation vs cross-community asymmetry); different statistical test
- vs. Shen et al. 2024: Provides empirical bibliometric evidence for what Shen et al. 2024 argues qualitatively

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Data Infrastructure Existence — Directed Citation Graph Constructibility

**Type:** EXISTENCE
**Statement:** Under the huashen218 bidirectional alignment corpus (~400 papers, 2018-2024), if all paper IDs are resolved against S2AG and venue groups are classified via fieldsOfStudy + venue string fallback, then ≥70% of corpus papers resolve successfully AND ≥30 cross-group directed within-corpus edges are found, confirming the data infrastructure exists to support chi-squared analysis of citation directionality.

**Rationale:**
This is the foundational hypothesis. The entire study depends on S2AG coverage being sufficient and within-corpus edge density being above the pre-registered statistical power threshold. Without confirming this, all downstream tests are moot. The BUILD_ON evidence (S2AG indexes 205M+ papers, community preference effect produces elevated within-corpus density) makes this plausible but empirically unverified for this specific corpus.

**Variables:**
- Independent: None (observational)
- Dependent: S2AG coverage rate (target ≥70%); cross-group within-corpus edge count (target ≥30)
- Controlled: Venue classification scheme (3 pre-specified schemes); API rate limiting with local cache

**Verification Protocol:**
1. Extract all paper IDs (DOI/arXiv) from huashen218 GitHub reading list (~400 entries).
2. Query S2AG /paper/{id} for each; record resolution success/failure; document unresolved paper characteristics.
3. Classify resolved papers into ML_NLP vs HCI groups using S2AG fieldsOfStudy (primary) + venue string fallback (secondary), under all 3 schemes.
4. Query S2AG /paper/{id}/references for all resolved papers (rate-limited at ~40 req/min, local JSON cache); filter to within-corpus edges.
5. Count cross-group edges (AI→HCI and HCI→AI); verify ≥30 threshold; report coverage rate and edge count distribution.

**Success Criteria (PoC):**
- Primary: Coverage ≥70% AND cross-group edges ≥30 (chi-squared analysis feasible)
- Secondary: Edge count distribution across 3 classification schemes is stable (±20%)

**Failure Response:**
- Coverage 50-70%: Document unresolved papers; proceed if non-systematic dropout argued
- Coverage <50% OR edges <30: PIVOT to descriptive statistics only; bridge paper analysis still feasible
- Coverage <30%: ABANDON chi-squared analysis; study becomes feasibility report

**Dependencies:** None (foundation)
**Gate:** MUST_WORK — failure blocks all downstream hypotheses
**Source:** Phase 2A Section 5 (sh1_existence), Assumptions A1, A2

---

#### H-M1: ML/NLP Alignment Research Self-Referentiality — Low AI→HCI Outgoing Citation Proportion

**Type:** MECHANISM
**Statement:** Under the huashen218 corpus (papers with resolved S2AG IDs, ≥30 cross-group edges confirmed in H-E1), if papers are classified as ML_NLP (NeurIPS/ICML/ICLR/ACL/EMNLP), then the proportion of their outgoing within-corpus citations pointing to HCI papers (AI→HCI proportion) is significantly lower than the proportion pointing to other ML_NLP papers (AI→AI proportion), because ML/NLP alignment research (RLHF, safety, fine-tuning) is conceptually grounded in ML/NLP methodology and does not require engagement with HCI literature on user agency or sociotechnical systems.

**Rationale:**
This is the first causal step: ML/NLP alignment papers are self-referential. If falsified (AI→HCI proportion ≈ AI→AI proportion), the asymmetric citation dependency mechanism is broken at its source, invalidating the primary hypothesis regardless of HCI behavior. Supported by Shen et al. 2024 (qualitative divergent alignment framings) and Ghosh & Wilson 2025 (ML/ethics divergence).

**Variables:**
- Independent: Venue group classification (ML_NLP)
- Dependent: AI→HCI proportion (ML_NLP outgoing to HCI / total ML_NLP within-corpus outgoing)
- Controlled: Citation proportions (not raw counts); all 3 venue classification schemes applied

**Verification Protocol:**
1. From the 2×2 contingency table (H-E1 output), extract AI→HCI cell count and AI→AI cell count.
2. Compute AI→HCI proportion = AI→HCI / (AI→HCI + AI→AI) for each classification scheme.
3. Compare AI→HCI proportion to HCI→AI proportion using the ratio metric (< 1.0 = asymmetry).
4. Examine per-paper reference list composition for a sample of ML_NLP papers to qualitatively confirm self-referentiality.
5. Verify finding holds under ≥2 of 3 venue classification schemes.

**Success Criteria (PoC):**
- Primary: AI→HCI proportion < HCI→AI proportion (ratio < 1.0); difference is directionally consistent
- Secondary: ML_NLP reference lists show ≤10% HCI venue papers (qualitative sample, n=20)

**Failure Response:**
- ratio ≥ 1.0: PIVOT — examine whether ACL/EMNLP bridge classification is distorting results; rerun with NLP-bridge excluded scheme
- ratio = 1.0 under all 3 schemes: EXPLORE mechanism failure — check if huashen218 ML_NLP papers are unusually interdisciplinary

**Dependencies:** H-E1 (data infrastructure confirmed)
**Gate:** MUST_WORK — H-M1 is the primary causal claim; failure challenges core hypothesis
**Source:** Phase 2A Causal Mechanism Step 1, Prediction P1 (primary)

---

#### H-M2: HCI Alignment Research Asymmetric Citation Dependency — High HCI→AI Outgoing Citation Proportion

**Type:** MECHANISM
**Statement:** Under the huashen218 corpus, if papers are classified as HCI (CHI/CSCW/IUI), then the proportion of their outgoing within-corpus citations pointing to ML_NLP papers (HCI→AI proportion) is significantly higher than the proportion pointing to other HCI papers (HCI→HCI proportion), because HCI alignment research — focused on human-AI interaction, user agency, and explainability — must cite ML/NLP foundational work to characterize the AI systems it studies, creating an asymmetric epistemic dependency.

**Rationale:**
This is the second causal step: HCI alignment papers disproportionately cite ML/NLP work. If falsified (HCI→AI ≈ HCI→HCI), the asymmetric dependency claim fails, even if H-M1 is confirmed. Together H-M1 and H-M2 generate the prediction tested in H-M3. Supported by Reza et al. 2025 (HCI systematic review cites ML alignment work) and Chen 2024 X-index (HCI increasingly self-citing but also citing adjacent fields).

**Variables:**
- Independent: Venue group classification (HCI)
- Dependent: HCI→AI proportion (HCI outgoing to ML_NLP / total HCI within-corpus outgoing); within-group siloing (HCI→HCI proportion)
- Controlled: Citation proportions (not raw counts); all 3 venue classification schemes

**Verification Protocol:**
1. From the 2×2 contingency table (H-E1 output), extract HCI→AI cell count and HCI→HCI cell count.
2. Compute HCI→AI proportion = HCI→AI / (HCI→AI + HCI→HCI) for each classification scheme.
3. Compare HCI→AI proportion to AI→HCI proportion to assess the directional asymmetry.
4. Test P2 (within-group siloing): verify AI→AI proportion > AI→HCI proportion AND HCI→HCI proportion > HCI→AI proportion using proportion z-test (p < 0.05).
5. Verify findings hold under ≥2 of 3 venue classification schemes.

**Success Criteria (PoC):**
- Primary: HCI→AI proportion > AI→HCI proportion (directionally consistent with ratio < 1.0)
- Secondary: P2 confirmed — within-group proportion > cross-group for both ML_NLP and HCI (p < 0.05)

**Failure Response:**
- HCI→AI ≈ HCI→HCI: EXPLORE — check if huashen218 HCI papers are unusually self-contained; examine pre-2022 vs post-2022 cohort separately
- HCI→AI < HCI→HCI AND AI→HCI < AI→AI: PIVOT to siloing-only framing (both communities are siloed, but asymmetry claim weaker)

**Dependencies:** H-M1 (ML_NLP self-referentiality confirmed)
**Gate:** SHOULD_WORK — failure narrows thesis but does not invalidate directional asymmetry if ratio < 1.0 still holds
**Source:** Phase 2A Causal Mechanism Step 2, Prediction P2

---

#### H-M3: Measurable Directed Citation Asymmetry — 2×2 Contingency Table Test

**Type:** MECHANISM
**Statement:** Under the huashen218 corpus, the 2×2 directed citation contingency table (AI→HCI, AI→AI, HCI→AI, HCI→HCI) yields: ratio = (AI→HCI proportion) / (HCI→AI proportion) < 1.0 with chi-squared p < 0.05 (or Fisher's exact if any cell < 5), confirming that structural community asymmetry — ML/NLP alignment self-referentiality combined with HCI alignment's epistemic dependency on ML/NLP — is statistically detectable as a directed citation pattern.

**Rationale:**
This is the final causal step and the primary testable prediction. H-M3 synthesizes H-M1 and H-M2: if both causal mechanisms operate, they jointly produce a statistically detectable asymmetry in the 2×2 contingency table. This is the main contribution of the study. Supported by Wahle et al. 2023 (demonstrated same mechanism for NLP vs other fields) and Chen 2024 (HCI self-citation consistent with reduced outgoing cross-field citation).

**Variables:**
- Independent: Venue group assignment (ML_NLP vs HCI)
- Dependent: chi-squared statistic, p-value, ratio (AI→HCI proportion / HCI→AI proportion)
- Controlled: Pre-registered ≥30 edge threshold; 3 venue classification schemes; proportions not raw counts; Fisher's exact fallback if any cell < 5

**Verification Protocol:**
1. Assemble 2×2 contingency table from within-corpus edges (H-E1 output): rows = source venue group, columns = target venue group.
2. Run scipy.stats.chi2_contingency; if any cell < 5, use scipy.stats.fisher_exact instead.
3. Compute ratio = (AI→HCI / total_AI_outgoing) / (HCI→AI / total_HCI_outgoing).
4. Repeat under all 3 venue classification schemes; record ratio and p-value per scheme.
5. Identify bridge papers: compute nx.betweenness_centrality on directed subgraph; normalize by Kim et al. 2026 degree ratio; classify top-10 by venue group (P3 test).
6. Run pre/post-2022 cohort analysis: split corpus by publication year; compute proportions separately to detect ChatGPT-era temporal discontinuity.

**Success Criteria (PoC):**
- Primary: ratio < 1.0 AND p < 0.05 under ≥2 of 3 venue classification schemes
- Secondary (P3): ≥7 of top-10 normalized betweenness bridge papers classified as ML_NLP
- Secondary (temporal): Pre/post-2022 cohort difference detectable in citation proportion trend

**Failure Response:**
- p ≥ 0.05 under all 3 schemes: H0 supported — report null result; corpus may not exhibit structural asymmetry; shift to bridge paper and siloing analysis as primary contribution
- ratio ≥ 1.0: Directionality reversed — investigate whether HCI papers in corpus are outlier-heavy citers of ML/NLP

**Dependencies:** H-M2 (HCI asymmetric citation dependency confirmed)
**Gate:** MUST_WORK — this is the primary prediction; failure = null result (H0 supported)
**Source:** Phase 2A Causal Mechanism Step 3, Prediction P1 (primary), Section 2 (experimental setup)

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Coverage ≥70% AND cross-group edges ≥30 | STOP all downstream; pivot to descriptive study |
| H-M1 | MUST_WORK | AI→HCI proportion < HCI→AI proportion (ratio < 1.0, directional) | Challenge core hypothesis; examine classification scheme sensitivity |
| H-M2 | SHOULD_WORK | HCI→AI proportion > AI→HCI proportion | Document limitation; proceed to H-M3 if H-M1 passed |
| H-M3 | MUST_WORK | ratio < 1.0 AND p < 0.05 under ≥2/3 schemes | H0 supported; report null result as primary finding |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1 → H-M2 → H-M3 | 3 weeks |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Assumptions-to-Risk Mapping

| Risk | Source | Description | Severity | Likelihood | Affected Hypotheses |
|------|--------|-------------|----------|------------|---------------------|
| R1 | A1 | S2AG coverage < 70%: study representativeness compromised | High | Medium | H-E1 (blocker), all downstream |
| R2 | A2 | Within-corpus cross-group edge count < 30: chi-squared underpowered | Critical | Medium | H-E1 (blocker), H-M3 |
| R3 | A3 | Venue classification < 80% valid: ACL/EMNLP bridge papers distort results | Medium | Medium | H-M1, H-M2, H-M3 |
| R4 | A4 | Citation proportions not age-invariant: temporal cohort confounded | Low | Low | H-M3 (temporal analysis only) |
| R5 | A5 | Corpus curation introduces systematic citation direction bias | Medium | Low | H-M3, scope of all findings |

### 4.2 Risk Detail & Mitigation

**Risk R1: S2AG Coverage Failure**

**Source Assumption:** A1 — S2AG covers ≥70% of huashen218 corpus papers

**Description:** If S2AG cannot resolve paper IDs for >30% of corpus papers (e.g., workshop papers without DOIs, preprints before indexing lag), the remaining sample may not be representative.

**Affected Hypotheses:** H-E1 (immediate gate), H-M1, H-M2, H-M3 (downstream)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Use both DOI and arXiv ID as resolution targets; implement venue/title fuzzy search as tertiary fallback.
2. **Detection:** Track resolution success rate during H-E1 data collection; flag if coverage drops below 80% (early warning).
3. **Response:**
   - 70-90% coverage: Proceed; characterize unresolved papers (argue non-systematic dropout).
   - 50-70% coverage: Proceed with explicit sampling bias caveat; document venue distribution of unresolved vs resolved papers.
   - <50% coverage: PIVOT — study becomes S2AG coverage characterization + bridge paper case study; chi-squared analysis abandoned.

**Early Warning Indicators:** >15% resolution failures in first 50 papers; disproportionate failures in CHI or NeurIPS venue papers.

---

**Risk R2: Edge Sparsity (Critical)**

**Source Assumption:** A2 — ≥30 cross-group directed within-corpus edges

**Description:** The curated huashen218 corpus (~400 papers) may not have sufficient mutual citation density. If ML/NLP and HCI alignment papers cite each other infrequently (because they are conceptually siloed), the very hypothesis being tested may produce its own data sparsity problem.

**Affected Hypotheses:** H-E1 (gate), H-M3 (chi-squared power)

**Severity:** Critical — this is the main empirical unknown

**Mitigation Strategy:**
1. **Prevention:** Pre-register the ≥30 edge threshold; use this as an explicit study validity condition (not a post-hoc excuse).
2. **Detection:** Count cross-group edges immediately after S2AG reference retrieval; report edge count before any statistical testing.
3. **Response:**
   - ≥30 edges: Proceed with chi-squared test as planned.
   - 10-29 edges: PIVOT — use Fisher's exact test; report edge count explicitly; shift primary contribution to bridge paper analysis (P3) and descriptive siloing (P2).
   - <10 edges: SCOPE — reframe study as "measuring structural isolation via edge absence"; bridge paper analysis becomes primary.

**Early Warning Indicators:** First 50 paper reference lists yield <5 within-corpus cross-group edges.

---

**Risk R3: Venue Classification Ambiguity**

**Source Assumption:** A3 — venue classification valid for ≥80% of papers

**Description:** ACL/EMNLP papers sit at the NLP/ML boundary. Papers from these venues on alignment topics may be genuinely bridge papers, and their classification into ML_NLP vs NLP_bridge vs excluded significantly affects the 2×2 table composition.

**Affected Hypotheses:** H-M1, H-M2, H-M3

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Pre-specify all 3 classification schemes before data collection; do not inspect results before assigning schemes.
2. **Detection:** Run all 3 schemes in parallel; flag hypotheses where ratio direction or significance changes across schemes.
3. **Response:**
   - Consistent across ≥2 schemes: Report primary result under Scheme 1; sensitivity in appendix.
   - Inconsistent: EXPLORE — report all 3 results; claim finding is classification-sensitive; recommend future work with controlled vocabulary.

**Early Warning Indicators:** >20% of corpus papers are from ACL/EMNLP venues (elevated sensitivity to scheme choice).

---

**Risk R4: Age-Invariance Violation**

**Source Assumption:** A4 — citation proportions are age-invariant within cohorts

**Description:** If citation behavior changed significantly around 2022 (ChatGPT effect), pre/post-2022 cohorts have different citation norms. The proportion metric controls for accumulation time but not for behavioral regime shifts.

**Affected Hypotheses:** H-M3 (temporal cohort analysis sub-test)

**Severity:** Low

**Mitigation Strategy:**
1. **Prevention:** Run pre/post-2022 cohort analysis as a pre-specified secondary analysis; do not pool cohorts if structural break is detected.
2. **Detection:** Compute proportions separately for pre-2022 and post-2022 papers; test for proportion equality using z-test.
3. **Response:** If significant temporal break detected: SCOPE — report pre/post-2022 separately; treat ChatGPT-era citation shift as a novel finding (potentially most interesting result).

**Early Warning Indicators:** Post-2022 papers show AI→HCI proportion significantly different from pre-2022 papers (>10% absolute difference).

---

**Risk R5: Corpus Curation Bias**

**Source Assumption:** A5 — curation does not systematically bias citation direction

**Description:** If Shen et al. 2024 curated the reading list by selecting papers that cite each other bidirectionally (to demonstrate bidirectional alignment), the corpus may overestimate cross-community citation. Conversely, if they selected canonical papers from each community independently, cross-citation may be underestimated.

**Affected Hypotheses:** H-M3, scope of all findings

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Frame all findings explicitly as corpus-level (not field-level) in all reports and outputs.
2. **Detection:** Examine corpus selection methodology from Shen et al. 2024 methods section; look for evidence of citation-graph-based selection.
3. **Response:** Regardless of findings: SCOPE — matched baseline comparison (random ML/HCI papers not in corpus) deferred to Phase 5; field-level generalization explicitly excluded from Phase 4 claims.

**Early Warning Indicators:** N/A — this risk is managed by scope framing, not data-driven detection.

---

### 4.3 Baseline Failure Patterns → Risks

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| Wahle et al. 2023: broad NLP corpus (77k papers) may have sufficient edges but huashen218 is curated (~400) | R2: Edge sparsity | Pre-registered ≥30 threshold; Wahle prior estimate (10-30x base rate) provides positive evidence |
| Chen 2024: only measures self-citation (X-index), not cross-field directionality | R3: Classification sensitivity | Our 3-scheme sensitivity analysis extends Chen's approach explicitly |

### 4.4 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Primary Mitigation |
|----|------|--------|----------|----------|--------------------|
| R1 | S2AG coverage failure | A1 | High | H-E1, all | Multi-ID resolution + non-systematic dropout argument |
| R2 | Cross-group edge sparsity (Critical) | A2 | **Critical** | H-E1, H-M3 | Pre-registered ≥30 threshold; descriptive-only fallback |
| R3 | Venue classification ambiguity | A3 | Medium | H-M1-3 | 3-scheme pre-specified sensitivity analysis |
| R4 | Age-invariance violation | A4 | Low | H-M3 | Pre-2022/post-2022 cohort split as secondary analysis |
| R5 | Corpus curation bias | A5 | Medium | H-M3 | Explicit corpus-level scope framing; Phase 5 matched baseline |

Critical Risks: 1 | High Risks: 1 | Medium Risks: 2 | Low Risks: 1

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 4 Hypotheses
H-CitAsym-v1 | Incremental Mode | Sequential Chain
═══════════════════════════════════════════════════════════════

[Level 0 — Root: EXISTENCE]
    ┌─────────────────────────────────────────────────┐
    │ H-E1: Data Infrastructure Existence             │
    │ S2AG coverage ≥70% AND cross-group edges ≥30   │
    │ Gate: MUST_WORK                                 │
    └─────────────────────────────────────────────────┘
                          │
                          ▼ [GATE 1: MUST PASS]
[Level 1 — MECHANISM Step 1]
    ┌─────────────────────────────────────────────────┐
    │ H-M1: ML/NLP Self-Referentiality               │
    │ AI→HCI proportion < HCI→AI proportion          │
    │ Gate: MUST_WORK                                 │
    └─────────────────────────────────────────────────┘
                          │
                          ▼ [GATE 1.5: MUST PASS]
[Level 2 — MECHANISM Step 2]
    ┌─────────────────────────────────────────────────┐
    │ H-M2: HCI Asymmetric Citation Dependency       │
    │ HCI→AI proportion > AI→HCI proportion          │
    │ Gate: SHOULD_WORK                               │
    └─────────────────────────────────────────────────┘
                          │
                          ▼
[Level 3 — MECHANISM Step 3]
    ┌─────────────────────────────────────────────────┐
    │ H-M3: Measurable Directed Citation Asymmetry   │
    │ ratio < 1.0 AND chi-squared p < 0.05           │
    │ Gate: MUST_WORK                                 │
    └─────────────────────────────────────────────────┘
                          │
                          ▼ [GATE 2: MUST PASS]
                    ┌──────────┐
                    │ PHASE 5  │
                    │ Baseline │
                    │ Comparison│
                    └──────────┘

═══════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
No parallelization (all sequential, full chain dependency)
═══════════════════════════════════════════════════════════════
```

### 5.2 Verification Phases with Gate Conditions

**Phase 1 — Foundation** (Week 1-2)

| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | S2AG coverage ≥70% AND cross-group edges ≥30 | **MUST_WORK** |

→ **Gate 1:** H-E1 FAIL = STOP all downstream; pivot to descriptive study.

**Phase 2 — Core Mechanisms** (Week 3-5)

| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST_WORK |
| H-M2 | H-M1 | SHOULD_WORK |
| H-M3 | H-M2 | MUST_WORK |

→ **Gate 2:** H-M1 FAIL = Challenge core hypothesis. H-M2 FAIL = Document limitation, proceed. H-M3 FAIL = H0 supported; report null result.

### 5.3 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | MUST_WORK |

### 5.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 4 Hypotheses | H-CitAsym-v1
═══════════════════════════════════════════════════════════════════
Phase / Hypothesis  │ W1-2    │ W3-4    │ W5      │
────────────────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation │         │         │         │
  H-E1              │ ████████│         │         │
  [Gate 1]          │       ◆ │         │         │
────────────────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms │         │         │         │
  H-M1              │         │ ████████│         │
  H-M2              │         │   ██████│         │
  H-M3              │         │         │ ████████│
  [Gate 2]          │         │         │       ◆ │
════════════════════╪═════════╪═════════╪═════════╡
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
Critical Path: H-E1(2w) → H-M1(1.5w) → H-M2(0.5w overlap) → H-M3(1w)
═══════════════════════════════════════════════════════════════════
```

### 5.5 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Duration: 5 weeks
  Formula: 2 (H-E1) + 3 (H-M1-3 sequential) = 5 weeks
Slack Available: 0 weeks (fully sequential)
H-M1/H-M2 analysis partially overlaps (same 2×2 table)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Hypotheses: 4
  Existence: 1 (H-E1)
  Mechanism: 3 (H-M1, H-M2, H-M3)
  Condition: 0 (none — scope boundaries are non-quantitative)

Verification Phases: 2
  Phase 1: Foundation (H-E1) — 2 weeks
  Phase 2: Mechanisms (H-M1-3) — 3 weeks

Total Duration: 5 weeks
Critical Path Length: 5 weeks
Execution Mode: Sequential chain (no parallelization)
Data Infrastructure: huashen218 GitHub + S2AG API (~100 lines Python)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.7 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
  → Resolve huashen218 IDs against S2AG; classify venues; retrieve reference lists; count edges
Step 2: Evaluate Gate 1 → If coverage ≥70% AND edges ≥30: proceed; else pivot to descriptive
Step 3: Execute H-M1 (ML/NLP self-referentiality) — Week 3-4 (first half)
  → Extract AI→HCI and AI→AI cell counts from 2×2 table; compute proportion
Step 4: Execute H-M2 (HCI asymmetric dependency) — Week 3-4 (second half)
  → Extract HCI→AI and HCI→HCI cell counts; compute proportion; test P2 (siloing)
Step 5: Execute H-M3 (directed asymmetry test) — Week 5
  → Run chi-squared/Fisher's exact; compute ratio; run 3-scheme sensitivity; bridge paper analysis; temporal cohort
Step 6: Evaluate Gate 2 → If H-M3 PASS: proceed to Phase 4.5/synthesis; else report null result
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: The huashen218 bidirectional alignment corpus exhibits
directed citation asymmetry (AI→HCI / HCI→AI ratio < 1.0, p < 0.05),
reflecting structural community siloing: ML/NLP alignment research is
self-referential to ML/NLP foundations, while HCI alignment research
must cite ML/NLP work to ground its applied user-facing analyses.

Supporting Evidence:
1. Causal mechanism is parsimonious (3 steps) with a clear falsifier
   at each step; each step has supporting empirical analogues.
2. Wahle et al. 2023 (NLP cross-field asymmetry) and Chen 2024
   (HCI X-index self-citation) provide independent methodological
   validation of the mechanism in closely related corpora.
3. Shen et al. 2024 qualitatively identifies divergent alignment
   framings; this study provides the empirical operationalization.

Strengths:
- Citation directionality is bias-free (avoids all three prior failure modes)
- Pre-specified sensitivity analysis (3 venue schemes) prevents post-hoc rationalization
- Pre-registered ≥30 edge threshold ensures statistical power is confirmed before testing
- Both positive and negative results are scientifically informative

Expected Outcomes:
- P1: ratio < 1.0 AND p < 0.05 under ≥2/3 venue classification schemes
- P2: within-group density > cross-group density for both ML_NLP and HCI
- P3: ≥7 of top-10 normalized betweenness bridge papers are ML_NLP venue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): There is no significant difference in the
proportion of AI→HCI vs HCI→AI directed citation edges within the
huashen218 alignment corpus (ratio = 1.0, chi-squared p ≥ 0.05).

Counter-Arguments:
1. The huashen218 corpus is intentionally curated for bidirectional
   alignment — curation may have selected papers that already cite
   across communities, suppressing the asymmetry.
2. ACL/EMNLP NLP papers sit at the ML/HCI boundary; misclassifying
   them as ML_NLP may artificially inflate the AI→HCI numerator.
3. The corpus is small (~400 papers); within-corpus edge count may
   be too sparse (<30) to support chi-squared analysis at all.

Potential Failure Points:
- R2 (Edge sparsity): if <30 cross-group edges, H-M3 cannot be tested
- R3 (Classification ambiguity): ACL/EMNLP treatment changes ratio direction
- R5 (Curation bias): bidirectional selection criterion may equalize citation rates

Conditions Under Which H0 Would Be Supported:
- ratio ≥ 1.0 under all 3 venue classification schemes
- p ≥ 0.05 even with sufficient edges (genuine null)
- Edge count < 30 (underpowered — H0 neither confirmed nor rejected)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:
The hypothesis H-CitAsym-v1 presents a testable, falsifiable claim
about structural community asymmetry in a specific curated corpus.
The null hypothesis raises valid concerns about corpus edge sparsity,
classification sensitivity, and curation bias — all of which are
addressed by pre-specified design choices in the verification plan.

Resolution Path:
The verification plan addresses this dialectic through:
1. H-E1 (Foundation): Confirms data infrastructure before any
   statistical testing — prevents underpowered analyses.
2. 3-scheme sensitivity analysis: Classification ambiguity is
   converted into a robustness check rather than a confound.
3. Explicit corpus-level scope framing: Curation bias is managed
   by not making field-level claims.

Conditions for Thesis Support:
- H-E1 PASS: sufficient data confirmed
- H-M1 + H-M3 PASS: ratio < 1.0, p < 0.05 under ≥2 schemes
- Sensitivity analysis: result holds under ≥2/3 classification schemes

Conditions for Antithesis Support:
- H-E1 FAIL: study is infeasible (edges too sparse)
- H-M3: ratio ≥ 1.0 or p ≥ 0.05 under all 3 schemes
- Classification inconsistency: result direction reverses between schemes

Nuanced Outcome Possibilities:
1. Full Support: H-E1 + H-M1 + H-M2 + H-M3 all pass → Thesis validated
   (primary contribution + P2 siloing + P3 bridge papers)
2. Partial Support: H-M2 fails but H-M3 passes → Asymmetry confirmed
   but mechanism step 2 needs refinement
3. Underpowered: H-E1 fails (edges < 30) → Neither confirmed nor denied;
   reframe as structural isolation evidence
4. Null Result: H-M3 fails (p ≥ 0.05) → H0 supported; publish null result
   with descriptive statistics as primary contribution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Data Existence | S2AG covers ≥70%; ≥30 cross-group edges expected | Curated corpus may be too sparse | H-E1 pre-gate; ≥30 threshold pre-registered |
| Mechanism Step 1 | ML/NLP alignment is self-referential | ML/NLP papers may cite HCI at comparable rates | H-M1 test; qualitative sample check |
| Mechanism Step 2 | HCI alignment disproportionately cites ML/NLP | HCI papers may be equally self-citing | H-M2 test; P2 siloing analysis |
| Statistical Test | ratio < 1.0, p < 0.05 | ACL/EMNLP classification changes results | 3-scheme sensitivity analysis |
| Scope | Corpus-level finding is valid contribution | Curation bias may limit generalizability | Explicit corpus-level framing; Phase 5 for field-level |

**Overall Robustness Score:** Medium-High (well-designed with known ceiling: edge sparsity remains empirically unresolved until H-E1 runs)

**Confidence in Verification Plan:** 0.78

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-CitAsym-v1 — Citation Asymmetry in huashen218 Bidirectional Alignment Corpus
- ID: H-CitAsym-v1 | Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (Phase 2A output available; 57% scope reduction — 5 BUILD_ON claims skipped)
- Sub-Hypotheses: 4 total (H-E1 existence + H-M1/2/3 mechanism)
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (Gate 1 post-H-E1; Gate 2 post-H-M3)

**Risk Assessment:** Medium (dominated by R2 — edge sparsity is empirically unresolved)
- Primary concerns: (1) within-corpus cross-group edge count < 30 threshold; (2) ACL/EMNLP classification sensitivity

**Immediate Action:** Begin Phase 1 with H-E1 — resolve huashen218 corpus IDs against S2AG

### 7.2 Conclusions

**Key Achievements:**
- 4 sub-hypotheses defined across 2 phases with verification protocols
- H0 addressed (chi-squared p ≥ 0.05 → null result path fully specified)
- Pre-registered sensitivity analysis and edge threshold prevent post-hoc rationalization

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Resolve corpus IDs, classify venues, retrieve reference lists, count within-corpus edges
- Gate 1: Coverage ≥70% AND cross-group edges ≥30 — MUST PASS

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: ML/NLP self-referentiality — AI→HCI proportion < HCI→AI proportion
- H-M2: HCI asymmetric citation dependency — HCI→AI proportion > AI→HCI proportion
- H-M3: 2×2 contingency table test — ratio < 1.0, chi-squared p < 0.05 under ≥2/3 schemes
- Gate 2: H-M3 MUST PASS for primary thesis support

**Critical Decision Points:**

1. **Gate 1 (Foundation — H-E1):**
   - PASS (≥70% coverage, ≥30 edges) → Proceed to Phase 2
   - FAIL (<70% OR <30 edges) → STOP chi-squared path; pivot to descriptive statistics + bridge paper analysis

2. **Gate 2 (Mechanism — H-M3):**
   - PASS (ratio < 1.0, p < 0.05, ≥2 schemes) → Phase 4.5 Synthesis; thesis supported
   - PARTIAL (H-M2 fail, H-M3 pass) → Thesis supported with mechanism Step 2 caveat
   - FAIL (p ≥ 0.05 all schemes) → H0 supported; null result as primary contribution

**Open Questions:**
- Actual within-corpus cross-group edge count (empirically unknown until H-E1 runs)
- ACL/EMNLP classification scheme sensitivity — which scheme produces most stable results?
- Post-2022 ChatGPT-era temporal discontinuity — is citation behavior regime-shifting?

**Recommendations:**

1. **Immediate Actions:**
   - Begin H-E1 data collection: clone huashen218 GitHub repo; implement S2AG retrieval with local JSON cache
   - Pre-register all 3 venue classification schemes before data inspection
   - Set up rate-limited S2AG client (~40 req/min; full corpus retrieval ~15-40 min with cache)

2. **Resource Allocation:**
   - Allocate 5 weeks for full critical path
   - H-M1/M2/M3 share the same 2×2 table — compute once, analyze three ways (efficient)
   - Reserve time for null-result writeup if H-M3 fails (publishable in either direction)

3. **Failure Management:**
   - Document all S2AG resolution failures with reason codes
   - Execute descriptive-statistics PIVOT if edge count < 30 (pre-planned, not improvised)
   - Report all 3 venue classification scheme results regardless of outcome

### 7.3 Appendices

#### A. Phase 2A Reference
- **Source:** docs/youra_research/03_refinement.yaml (ID: H-CitAsym-v1)
- **Generated:** 2026-08-20 | Schema: 10.0.0 | Convergence: Exchange 7, 6/6 criteria met
- **Supplementary:** docs/youra_research/02_synthesis.yaml (measurement plan, validation strategy)

#### B. MCP Tool Usage Summary
- **Total MCP calls:** 2 (incremental mode)
- **Tools:** mcp__clearThought__scientificmethod × 2 (H-E1 hypothesis+experiment; H-M integrated hypothesis+experiment)
- **Scope reduction applied:** 57% (5 BUILD_ON claims not re-verified)

#### C. Established Facts Not Re-Verified (BUILD_ON)
- S2AG provides directed citation edges (Wade 2022)
- HCI X-index self-citation trend (Chen 2024)
- NLP within-field citation preference 10-30x (Wahle et al. 2023)
- huashen218 corpus structure (Shen et al. 2024)
- Chi-squared validity for 2×2 contingency tables (standard statistics)

---

*Phase 2B Verification Plan Complete | Next: Phase 2C Experiment Design for H-E1*
