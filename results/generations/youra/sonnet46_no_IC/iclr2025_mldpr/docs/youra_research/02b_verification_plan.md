# Verification Plan: FAIR F1 Operationalized — Binary Keyword Tag Presence Predicts OpenML Dataset Adoption (NB-2, IRR ≥ 1.1)

**Date:** 2026-08-05
**Hypothesis ID:** h-e1-v2
**Confidence:** 0.72
**Total Hypotheses:** 4
**Research Mode:** Incremental (83% scope reduction from Phase 2A)
**Workflow:** Phase 2B Planning | Status: complete
**Steps Completed:** step-00-init-environment, step-01-init-parsing, step-02-input-hypothesis, step-03-hypothesis-generation, step-04-hypothesis-inventory, step-05-risk-analysis, step-06-dependency-graph, step-07-timeline-planning, step-08-dialectical-analysis, step-09-summary, step-10-finalize
**Completed At:** 2026-08-05T04:45:00Z

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the OpenML platform context (N=5,217 datasets with N_tasks ≥ 1, cross-sectional corpus), if a dataset has keyword tags attached (has_tags=1 vs. has_tags=0), then it will have significantly more registered ML tasks (N_tasks), because keyword tags make datasets discoverable through OpenML's tag-indexed search (FAIR F1 mechanism), and discoverability drives researcher engagement and task creation.

Formally: In NB-2 regression of N_tasks on has_tags controlling for log(n_instances), log(n_features), age_years, age², C(decade), the IRR for has_tags will be ≥ 1.1 with 95% CI lower bound ≥ 1.1.

### 1.2 Alternative Hypothesis (H0)

H0-P1: There is no significant positive association between has_tags (binary) and N_tasks in NB-2 regression after controlling for dataset size, age, and decade effects (IRR 95% CI lower < 1.1 or p ≥ 0.05).

H0-P2: beta(log_tag_count_p1) ≤ 0 OR IRR 95% CI lower < 1.05 in tagged-only NB-2 [count magnitude above binary threshold does not predict additional adoption]

H0-P3: No monotonic dose-response across tag_count categories in NB-2

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | OpenML Dataset Corpus (h-e1 reuse) (standard) | N=5,217 active OpenML datasets with N_tasks≥1; contains tags field (parseable to has_tags + tag_count); same corpus as h-e1 ensuring methodological continuity and IV comparison validity |
| **Model** | Negative Binomial Type 2 (NB-2) | DV (N_tasks) is overdispersed count (CT LR=2222.68 from h-e1); NB-2 handles variance=μ+αμ² structure; BFGS optimizer achieves convergence |

**Dataset Details:**
- Source: OpenML API via openml-python (list_datasets output_format='dataframe')
- Path: h-e1/code/data/h_e1/openml_dataset_corpus.csv

**Model Details:**
- Type: count regression
- Source: statsmodels.formula.api.negativebinomial (loglike_method='nb2')

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| h-e1 composite metadata score (0-5) | IRR=1.076, 95% CI [1.060, 1.092]; below 1.1 threshold; RC-3 IRR=1.014 (p=0.19) | OpenML N=5,217 (same corpus) |
| Yang 2024 HuggingFace documentation quality | Positive correlation with popularity (Spearman ρ not reported numerically) | HuggingFace dataset cards |
| Lachmuth 2025 BonaRes FAIR metadata | 815 datasets → 62 citing papers; FAIR compliance associated with reuse | BonaRes agricultural domain repository |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | N_tasks (distinct ML task count) is a valid proxy for dataset adoption intensity | h-e1 used same proxy; N_tasks reflects deliberate researcher engagement | IRR estimates capture task-count adoption signal which may differ from run-count adoption signal |
| A2 | Tag assignment on OpenML temporally precedes task creation for most datasets | OpenML platform design: tags assigned at upload by dataset creator (Vanschoren 2014 v2 API) | Association is reverse-causal (adoption → tagging); predictive claim still valid but causal interpretation fails |
| A3 | Tag count's adoption effect is decade-invariant (has_tags effect survives C(decade) FE) | FAIR tagging conventions stable since 2016; OpenML tagging since 2012 | IRR attenuates to non-significance under decade FE (as in h-e1 RC-3); hypothesis fails |
| A4 | Zero-tag datasets in the N=5,217 sample represent valid 'untagged' observations, not missing data | OpenML allows zero-tag datasets; tags field is explicitly empty/null | Zero-tag datasets are MNAR; inclusion biases estimates downward |
| A5 | NB-2 remains appropriate with has_tags as primary IV (overdispersion structure stable under IV change) | h-e1 confirmed extreme overdispersion (CT LR stat=2222.68) | If CT test fails with new IV, fall back to Poisson or quasi-Poisson |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First empirical NB-2 count-regression quantification of FAIR F1 (keyword tagging) → ML dataset adoption effect on OpenML with decade fixed effects as primary control.

**Key Innovation:** Binary tag presence (has_tags) as IV — theoretically motivated by platform search architecture and empirically motivated by h-e1 RC-2a; tests threshold behavior of FAIR F1 rather than continuous score.

**Prior Work Differentiation:**
- Yang et al. 2024 (HF platform, prose-quality metrics, no NB-2, no count regression, no decade FE)
- Chapman et al. 2019 (survey-based, no regression, no IRR estimate)
- Lachmuth et al. 2025 (domain repository agriculture, descriptive, no NB-2)
- h-e1 (composite score IV gave IRR=1.076 below 1.1 threshold; closed path)

**Scope Reduction:** 83% — 5 of 6 claims BUILD_ON (established); only 1 claim PROVE_NEW (tag_count → N_tasks via binary has_tags IV).

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Binary Tag Presence Predicts ML Dataset Adoption (Existence)**

**Type:** EXISTENCE
**Statement:** Under the OpenML platform context (N=5,217, cross-sectional), if a dataset has keyword tags (has_tags=1 vs. has_tags=0), then it will have significantly more registered ML tasks (N_tasks), because tags make datasets discoverable through OpenML's tag-indexed search (FAIR F1).

**Rationale:**
h-e1 RC-2a showed binary description presence (IRR=1.102) outperformed composite score (IRR=1.076). Binary has_tags is theoretically grounded in platform search architecture (first tag = entry into keyword search graph). Decade FE included as primary control per h-e1 lesson.

**Variables:**
- Independent: has_tags (binary 0/1)
- Dependent: N_tasks (count of distinct ML tasks, NB-2 outcome)
- Controlled: log_n_instances, log_n_features, age_years, age_sq, C(decade)

**Verification Protocol:**
1. Load corpus CSV (N=5,217); derive has_tags from tags field (non-null, non-empty = 1).
2. Verify overdispersion: re-run CT LR test with has_tags model; expect LR stat >> 3.84.
3. Fit NB-2: `smf.negativebinomial('N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq + C(decade)', data=df).fit(method='bfgs')`.
4. Compute IRR = exp(coef['has_tags']); CI_lower = exp(coef - 1.96*se); check: IRR ≥ 1.1 AND CI_lower ≥ 1.1 AND p < 0.05.
5. Report RC suite: RC-4 (top-1% winsorization), RC-5 (tag_count≥1 restriction), RC-7 (continuous age-only vs decade FE).

**Success Criteria (PoC):**
- Primary: IRR ≥ 1.1 AND 95% CI lower bound ≥ 1.1 AND p < 0.05 → PRIMARY PASS (MUST_WORK gate met)
- Secondary (partial pass): CI_lower ∈ [1.05, 1.1) → secondary criterion only

**Failure Response:**
- IF fails (CI_lower < 1.1 or p ≥ 0.05): PIVOT — check has_tags-decade correlation; if correlated, interpret as conservative estimate; route to Phase 0 if fundamental failure

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A Section 1.1 (core_statement), Section 5 (sh1_existence), Section 1.6 (P1 prediction)

---

**H-M1: Tags Enter Search Index — Platform Architecture Mechanism Step 1**

**Type:** MECHANISM
**Statement:** Under OpenML platform context, if a dataset has keyword tags (has_tags=1), then it will appear in tag-indexed search results (platform search graph membership), because OpenML's search engine indexes keyword tags as primary discovery keys (Vanschoren et al. 2014), operationally verified by H-E1's significant IRR supporting the search pathway activation mechanism.

**Rationale:**
This step converts H-E1's statistical finding into a mechanistic interpretation: the IRR effect is mediated by the platform search index. Tags at upload time immediately enter the search graph. This mechanism is corroborated by platform architecture documentation and provides the theoretical link from has_tags to increased researcher encounters.

**Variables:**
- Independent: has_tags (binary 0/1) — same as H-E1
- Dependent: N_tasks (used as downstream proxy of search-driven adoption)
- Controlled: Same as H-E1

**Verification Protocol:**
1. Confirm H-E1 passes (IRR ≥ 1.1 established).
2. Check has_tags-decade correlation before fitting: `df.groupby('decade')['has_tags'].mean()` — if strongly correlated, decade FE may partially absorb has_tags.
3. Interpret H-E1 IRR as partial evidence of platform search mechanism (no direct click-through data available).
4. Check that decade FE does NOT fully eliminate the has_tags effect (IRR remains > 1.0, p < 0.05 even if below 1.1 threshold).
5. Document mechanism support level: Full support if H-E1 primary passes; partial support if secondary threshold only.

**Success Criteria (PoC):**
- Primary: H-E1 IRR passes MUST_WORK gate → mechanism step 1 verified by implication
- Secondary: has_tags effect survives decade FE (p < 0.05 regardless of IRR magnitude)

**Failure Response:**
- IF decade FE fully absorbs has_tags: EXPLORE — examine has_tags distribution by decade; check if tagging adoption is era-specific; consider decade interaction term

**Dependencies:** H-E1 (MUST_WORK gate must pass)

**Source:** Phase 2A Section 1.3 (causal_mechanism, step 1)

---

**H-M2: Search Index Membership → Discovery — Magnitude Effect (Mechanism Step 2)**

**Type:** MECHANISM
**Statement:** Under OpenML context (has_tags=1 subset), if a dataset has more keyword tags (higher log(tag_count+1)), then it will have more registered ML tasks (N_tasks), because more tags create more search pathways → more researcher discovery events → more task creation.

**Rationale:**
This tests whether tag count above the binary threshold provides additional predictive signal for adoption. If yes, it supports the discovery-probability gradient mechanism (more search pathways → more encounters). If not, binary threshold is the full signal (FAIR F1 operates as a 0/1 gate, not a dose-response relationship).

**Variables:**
- Independent: log_tag_count_plus1 = log(tag_count + 1)
- Dependent: N_tasks
- Controlled: Same as H-E1 (log size, log features, age, age_sq, C(decade))
- Sample Restriction: has_tags=1 only (avoids collinearity with has_tags)

**Verification Protocol:**
1. Restrict to df_tagged = df[df.has_tags == 1]; report N (fraction of 5,217 with tags).
2. Derive tag_count = tags.str.count(',') + 1 for tagged rows; log_tag_count_p1 = log(tag_count + 1).
3. Report has_tags / log(tag_count+1) correlation in full sample (collinearity diagnostic).
4. Fit NB-2: `smf.negativebinomial('N_tasks ~ log_tag_count_p1 + log_n_instances + log_n_features + age_years + age_sq + C(decade)', data=df_tagged).fit(method='bfgs')`.
5. Compute IRR_P2 = exp(coef['log_tag_count_p1']); CI_lower_P2; check: IRR_P2 ≥ 1.05 AND CI_lower_P2 ≥ 1.05 AND p < 0.05.

**Success Criteria (PoC):**
- Primary: IRR_P2 95% CI lower ≥ 1.05 AND p < 0.05 → dose gradient exists above binary threshold
- Null: CI_lower_P2 < 1.05 → binary threshold is the full FAIR F1 signal (scientifically informative negative)

**Failure Response:**
- IF fails: DOCUMENT as informative negative — binary has_tags captures the full FAIR F1 effect; dose-response does not extend beyond threshold

**Dependencies:** H-M1 (H-E1 must pass; H-M1 mechanism step must be supported)

**Source:** Phase 2A Section 1.3 (causal_mechanism, step 2), Section 1.6 (P2 prediction)

---

**H-M3: Discovery → Task Creation — Dose-Response Gradient (Mechanism Step 3)**

**Type:** MECHANISM
**Statement:** Under OpenML context, if datasets are grouped by tag count categories (0, 1-2, 3-5, 6+), then each higher tag count category will have significantly more N_tasks than the previous category (monotonic dose-response), because the Discovery → Task Creation pathway amplifies with additional search pathways.

**Rationale:**
P3 tests the full dose-response structure of the FAIR F1 mechanism: does the adoption effect scale monotonically with tag count? This enriches the contribution beyond the existence test (H-E1) by characterizing the functional form of the tagging-adoption relationship. Non-monotonic patterns or insignificant adjacent contrasts would indicate binary threshold is the key mechanism, not continuous dose.

**Variables:**
- Independent: tag_count_categorical (0, 1-2, 3-5, 6+) — four-level categorical
- Dependent: N_tasks
- Controlled: Same as H-E1

**Verification Protocol:**
1. Derive tag_count_cat bins: 0 → "0", 1-2 → "1-2", 3-5 → "3-5", 6+ → "6+"; report cell sizes for each bin.
2. Fit NB-2: `smf.negativebinomial('N_tasks ~ C(tag_count_cat) + log_n_instances + log_n_features + age_years + age_sq + C(decade)', data=df).fit(method='bfgs')`.
3. Extract IRR per category: exp(coef for each tag_count_cat level vs. reference category "0").
4. Test monotonic ordering: IRR(0) < IRR(1-2) < IRR(3-5) < IRR(6+).
5. Test adjacent contrasts (3 contrasts): 0 vs 1-2, 1-2 vs 3-5, 3-5 vs 6+; apply Bonferroni correction (α/3 = 0.0167).

**Success Criteria (PoC):**
- Primary: Monotonic ordering of all 4 category IRRs AND all 3 adjacent contrasts p < 0.0167 (Bonferroni) → full dose-response confirmed
- Partial: Monotonic ordering with ≥2/3 significant adjacent contrasts → partial dose-response

**Failure Response:**
- IF fails: DOCUMENT — functional form is binary threshold, not dose-response; supports simpler FAIR F1 model (tag presence = search graph membership, not graded)

**Dependencies:** H-M2 (informs interpretation of continuous vs. categorical dose-response)

**Source:** Phase 2A Section 1.3 (causal_mechanism, step 3), Section 1.6 (P3 prediction)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | IRR ≥ 1.1 AND CI_lower ≥ 1.1 AND p < 0.05 | STOP → Phase 0 (fundamental failure) |
| H-M1 | MUST_WORK | H-E1 passes AND has_tags survives decade FE (p < 0.05) | EXPLORE decade correlation; document as mechanism limitation |
| H-M2 | SHOULD_WORK | IRR_P2 CI_lower ≥ 1.05 AND p < 0.05 | DOCUMENT informative negative; binary threshold is full signal |
| H-M3 | SHOULD_WORK | Monotonic IRR ordering AND ≥2/3 adjacent contrasts p < 0.0167 | DOCUMENT; functional form is binary threshold |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 3 weeks (1 week each after first) |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Assumptions → Risk Mapping

| ID | Risk | Source | Severity | Affected Hypotheses | Mitigation |
|----|------|--------|----------|---------------------|------------|
| R1 | N_tasks proxy captures task-count not execution-frequency adoption signal | A1 | Medium | H-E1, H-M1 | Secondary OLS on log(N_tasks) for directional consistency; explicit proxy acknowledgment in paper |
| R2 | Reverse causality: adoption drives tagging rather than tagging drives adoption | A2 | High | H-E1, H-M1 | Platform architecture argument (creator-only, upload-time tagging per Vanschoren 2014 v2 API); document as limitation |
| R3 | Decade FE absorbs has_tags signal (RC-3 failure analog to h-e1 composite) | A3 | Critical | H-E1, H-M1, H-M2, H-M3 | Pre-check has_tags-decade correlation before model fit; if correlated, interpret decade-controlled IRR as conservative; this is the primary risk |
| R4 | Zero-tag datasets are MNAR, biasing estimates downward | A4 | Medium | H-E1 | RC-5: restrict to tag_count≥1 (all-tagged subset) as sensitivity check |
| R5 | NB-2 inappropriate for has_tags model (overdispersion structure changes) | A5 | Low | All | Re-run CT LR test with has_tags model; fallback to Poisson if stat < 3.84 (unlikely given extreme overdispersion in h-e1) |

### 4.2 Detailed Risk Mitigations

**Risk R3 (Critical): Decade FE Absorbs has_tags**

*Source:* A3 — h-e1 composite score failed RC-3 (IRR=1.014, p=0.19 under decade FE)

*Prevention:*
- Check has_tags distribution by decade BEFORE fitting full model: `df.groupby('decade')['has_tags'].mean()`
- If has_tags rate rises sharply post-2015, decade FE will partially absorb the effect
- Theoretical mitigation: OpenML tagging has existed since 2012 (platform launch); FAIR conventions stable since 2016 — less decade-dependent than composite score

*Detection:*
- Fit model without C(decade) first; compare IRR; if IRR drops > 30% with decade FE, correlated confounding exists
- Run RC-7: compare age_years-only model vs. C(decade) model IRR

*Response:*
- If has_tags-decade correlation is high (Cramer's V > 0.3): report decade-controlled IRR as conservative lower bound; note theoretical argument for why correlation does not invalidate causal claim
- PIVOT only if IRR < 1.0 in ALL models (full null support)

**Risk R2 (High): Endogeneity / Reverse Causality**

*Source:* A2 — cross-sectional design cannot establish temporal ordering

*Prevention:*
- Platform architecture defense: only creator/moderator can add tags; no retroactive popularity-driven tagging possible in OpenML v2 API (Vanschoren 2014)
- Document explicitly as limitation in paper

*Detection:*
- No within-sample test available; theoretical argument only

*Response:*
- Reframe claim as predictive/associational throughout; avoid causal language unless hedged
- Future work: panel data with upload timestamps could establish temporal ordering

### 4.3 Baseline Failure Pattern → Risks

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| h-e1 composite score failed RC-3 (IRR=1.014 under decade FE) | has_tags may also fail RC-3 if tagging is era-specific | Pre-check has_tags-decade correlation; theoretical argument that binary threshold is less era-dependent |
| h-e1 composite score IRR=1.076 < 1.1 threshold | has_tags might also fall short of 1.1 (partial pass at 1.05-1.1) | Two-tier success criteria (primary 1.1, secondary 1.05) captures scientifically informative partial pass |

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence — no dependencies)
         │
         ▼  [GATE 1: MUST_WORK — if fail → STOP]
[Level 1 - Mechanism Step 1]
    H-M1 ← H-E1 (Platform Search Architecture)
         │
         ▼  [GATE 2: MUST_WORK — if fail → EXPLORE]
[Level 2 - Mechanism Step 2]
    H-M2 ← H-M1 (Magnitude Above Threshold)
         │
         ▼  [SHOULD_WORK]
[Level 3 - Mechanism Step 3]
    H-M3 ← H-M2 (Dose-Response Gradient)
         │
         ▼  [SHOULD_WORK]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Levels: 4
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │  W1-2   │  W3-4   │   W5    │
─────────────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1           │ ████████│         │         │
  [Gate 1]       │        ◆│         │         │
─────────────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │
  H-M2           │         │     ████│         │
  H-M3           │         │         │ ████████│
  [Gate 2]       │         │        ◆│         │
─────────────────┼─────────┼─────────┼─────────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3

Total Duration: 5 weeks
  Formula: 2 (H-E1) + 3 (H-M1, H-M2, H-M3)

Slack Available: 0 weeks (all sequential)

Note: H-M1, H-M2, H-M3 can be run in a single
      Python script session; "weeks" represent
      logical phases, actual compute time ~hours
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0 (none required)

Verification Phases: 2
1. Foundation (H-E1): 2 logical weeks
2. Mechanisms (H-M1, H-M2, H-M3): 3 logical weeks

Data: Existing corpus (N=5,217; no new collection)
Compute: CPU-only (statsmodels NB-2); ~minutes per model
Total Duration: 5 logical weeks
Critical Path Length: 5 logical weeks
Execution Mode: Sequential chain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

1. Execute H-E1 (Foundation) — Weeks 1-2: Fit primary NB-2 model; evaluate Gate 1
2. Evaluate Gate 1 → If MUST_WORK passes, proceed to Phase 2; if fails → STOP, route to Phase 0
3. Execute H-M1 (Mechanism Step 1) — Week 3: Interpret H-E1 result as mechanism evidence; check has_tags-decade correlation
4. Execute H-M2 (Mechanism Step 2) — Week 4: Fit tagged-only NB-2 with log(tag_count+1)
5. Execute H-M3 (Mechanism Step 3) — Week 5: Fit categorical NB-2; test monotonicity and adjacent contrasts
6. Evaluate Gate 2 → Document all results; consolidate RC suite

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Binary keyword tag presence (has_tags=1 vs. 0) positively predicts OpenML ML task count (N_tasks) with IRR ≥ 1.1 (95% CI lower ≥ 1.1) in NB-2 with C(decade), because tags make datasets findable through platform search (FAIR F1 mechanism).

**Supporting Evidence:**
1. **Platform architecture**: OpenML search engine indexes keyword tags as primary discovery keys (Vanschoren et al. 2014); tags assigned at upload (creator-only privilege) precede adoption events
2. **h-e1 RC-2a precedent**: Binary description presence (IRR=1.102) outperformed composite score (IRR=1.076); binary threshold effect is empirically motivated
3. **FAIR F1 theory**: Wilkinson et al. 2016 (15,976 citations) grounding findability → reuse causal chain; cross-domain support from Lachmuth 2025 (BonaRes FAIR→reuse)
4. **Corpus reusability**: N=5,217 corpus with confirmed NB-2 appropriateness (CT LR=2222.68) and BFGS convergence reduces methodological risk

**Strengths:**
- Theory-grounded IV (not constructed composite) with direct platform mechanism
- Two-tier success criteria (1.1 primary, 1.05 secondary) captures partial effects
- Existing corpus eliminates data collection risk

**Expected Outcomes:**
- P1: IRR ≥ 1.1, CI_lower ≥ 1.1, p < 0.05 (MUST_WORK gate)
- P2: IRR_P2 CI_lower ≥ 1.05 in tagged-only NB-2
- P3: Monotonic dose-response across tag count categories

### 6.2 Antithesis

**Null Hypothesis (H0):** IRR 95% CI lower < 1.1 or p ≥ 0.05 in primary NB-2 model (has_tags has no material positive effect on N_tasks after decade FE control)

**Counter-Arguments:**
1. **RC-3 risk (strongest counter)**: h-e1 composite score failed decade FE (IRR=1.014, p=0.19); if tagging adoption is also era-specific (post-2015 platform updates), C(decade) will absorb has_tags signal
2. **Endogeneity**: Cross-sectional design cannot rule out reverse causality; platform architecture argument is structural but untested empirically
3. **Scope limitation**: N_tasks≥1 restriction selects already-adopted datasets; "more adoption" result does not address adoption vs. non-adoption (zero-inflated question)

**Potential Failure Points:**
- Failure at R3: decade FE absorbs has_tags (same as h-e1 composite failure mode)
- Failure at R2: reverse causality dominates; high-adoption datasets retroactively receive tags
- Failure at R4: MNAR zero-tag datasets drive spurious has_tags effect

**Conditions Under Which H0 Would Be Supported:**
- CI_lower < 1.1 AND CI_lower < 1.05 in primary NB-2 (both tiers fail)
- IRR becomes non-significant (p ≥ 0.05) under decade FE
- has_tags-decade correlation is strong (Cramer's V > 0.3), suggesting era confounding

### 6.3 Synthesis

**Balanced Assessment:**

h-e1-v2 (has_tags IV) is theoretically stronger than h-e1 (composite score IV): binary threshold behavior is more compatible with the platform search architecture mechanism than a continuous composite. However, the antithesis's strongest point — RC-3 survival uncertainty — remains empirically unresolved until Phase 4 execution.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes existence with two-tier IRR criteria before claiming mechanism
2. **Sequential mechanism testing (H-M1 → H-M3):** Tests causal chain step-by-step; each step provides mechanistic evidence independent of the others
3. **Pre-check decade correlation (H-M1):** Explicitly tests the antithesis's RC-3 concern before fitting the full model

**Conditions for Thesis Support:**
- H-E1 MUST_WORK gate passes (IRR ≥ 1.1, CI_lower ≥ 1.1)
- has_tags effect survives C(decade) without full attenuation
- H-M1 decade correlation check shows low correlation

**Conditions for Antithesis Support:**
- H-E1 fails: IRR < 1.1 in BOTH primary and secondary threshold (CI_lower < 1.05)
- H-E1 secondary only (1.05 ≤ CI_lower < 1.1): partial antithesis support
- has_tags-decade Cramer's V > 0.3 AND IRR attenuates to non-significance: full antithesis on RC-3 grounds

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 primary passes, H-M1 survives FE, H-M2/H-M3 show dose-response → publish with strong FAIR F1 contribution
2. **Partial Support:** H-E1 secondary pass (CI_lower 1.05-1.1) + H-M2/H-M3 significant → publish with qualified claim; dose-response enriches secondary contribution
3. **Mechanism Positive / Existence Threshold Fail:** H-E1 directional (p < 0.05) but CI_lower < 1.05 + H-M2/H-M3 significant → publish as null primary with informative mechanism characterization
4. **No Support:** H-E1 p ≥ 0.05 under decade FE → Route to Phase 0 (RC-3 failure replicated)

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | has_tags → N_tasks IRR ≥ 1.1 (platform search mechanism) | RC-3 attenuation: decade FE may absorb signal | H-E1 test + H-M1 decade correlation pre-check |
| Mechanism | 3-step causal chain: tags → index → discovery → task creation | No direct discovery data; only proxy evidence available | H-M2 (magnitude) + H-M3 (dose-response) as convergent evidence |
| Scope | N_tasks≥1 studies adoption intensity differential | Cannot generalize to adoption vs. non-adoption | Explicitly scoped; future work: hurdle model for full adoption |
| Performance | IRR ≥ 1.1 outperforms h-e1 composite (IRR=1.076) | Same threshold failure mode possible | Two-tier criteria; h-e1 RC-2a empirical precedent for binary > composite |

**Overall Robustness:** Medium-High (strong theoretical grounding, empirical precedent from h-e1 RC-2a; primary risk is RC-3 survival)

**Confidence in Verification Plan:** 0.72

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** h-e1-v2 — Binary keyword tag presence (has_tags) predicts N_tasks ≥ 10% more in NB-2 with C(decade), grounded in FAIR F1 and OpenML platform search architecture
- ID: h-e1-v2 | Confidence: 0.72 | Scope reduction: 83% (incremental mode)

**Verification Structure:**
- Mode: Incremental (Phase 2A data fully parsed)
- Sub-Hypotheses: 4 total (H-E1: Existence, H-M1/H-M2/H-M3: Mechanism steps 1-3)
- Phases: 2 phases over 5 logical weeks
- Critical Gates: 2 decision points (Gate 1: H-E1 MUST_WORK; Gate 2: H-M1 MUST_WORK)

**Risk Assessment:** Medium-High
- Primary concern: RC-3 survival (has_tags decade FE attenuation — same failure mode as h-e1 composite)
- Secondary concern: N_tasks proxy heterogeneity (auto-generated vs. research tasks)

**Immediate Action:** Begin Phase 2C with H-E1 experiment design; corpus already available at h-e1/code/data/h_e1/openml_dataset_corpus.csv

### 7.2 Conclusions

**Key Achievements:**
- 4 hypotheses defined across 2 phases; H0 explicitly addressed for all 3 predictions
- 83% scope reduction applied (5 of 6 claims established from h-e1; only tag-specific IV is PROVE_NEW)
- MCP Scientific Method used for H-E1 and H-M-integrated (3 calls total)
- Risk R3 (Critical: RC-3 attenuation) identified, mitigation specified (decade correlation pre-check)

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Binary tag presence (has_tags) → N_tasks in NB-2 with C(decade); Gate 1: MUST PASS
- RC suite: RC-4 (winsorization), RC-5 (tag_count≥1 restriction), RC-7 (age-only vs. decade FE)

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Check has_tags-decade correlation; interpret H-E1 as mechanism evidence; Gate 2: MUST PASS
- H-M2: log(tag_count+1) NB-2 on has_tags=1 subset; IRR_P2 CI_lower ≥ 1.05
- H-M3: Categorical dose-response NB-2; monotonic ordering + Bonferroni adjacent contrasts

**Critical Decision Points:**

1. **Gate 1 (H-E1 Foundation):** IRR ≥ 1.1 AND CI_lower ≥ 1.1 AND p < 0.05
   - FAIL → STOP, route to Phase 0 (tag IV also fails threshold)
   - PARTIAL (CI_lower 1.05-1.09) → Continue with qualified claim; document as partial support
   - PASS → Proceed to Phase 2 mechanisms

2. **Gate 2 (H-M1 Mechanism):** H-E1 must have passed; has_tags survives decade FE
   - FAIL (p ≥ 0.05 under decade FE) → Document RC-3 failure; route to Phase 0
   - PASS → Continue H-M2, H-M3 for dose-response characterization

**Open Questions:**
- What fraction of N=5,217 have tag_count=0? (determines collinearity between log(tag_count+1) and has_tags)
- Does has_tags survive decade FE (RC-3 equivalent)? — the critical empirical question
- Is P2 (magnitude above threshold) significant? Or is binary threshold the full FAIR F1 signal?

**Recommendations:**

1. **Immediate Actions:**
   - Derive has_tags and tag_count in Python before running any models (one preprocessing step)
   - Check has_tags-decade correlation FIRST (before model fitting) to anticipate RC-3 outcome
   - Run all 3 predictions (P1, P2, P3) in a single session using the existing corpus

2. **Resource Allocation:**
   - Allocate 5 logical weeks; actual compute ~hours (CPU statsmodels NB-2, no GPU needed)
   - Reserve buffer: if RC-3 check shows high correlation, budget extra analysis time

3. **Failure Management:**
   - Document all results regardless of outcome (informative negatives for paper's contribution section)
   - If H-E1 partial pass: two-tier reporting structure pre-registered in Phase 2A; proceed with H-M2/H-M3 even if P1 only partially passes

### 7.3 Appendices

**Appendix A: Phase 2A Reference**
- Primary source: docs/youra_research/03_refinement.yaml (ID: h-e1-v2)
- Supplementary: docs/youra_research/02_synthesis.yaml, docs/youra_research/01_round_table/final_opinions.yaml
- Corpus: h-e1/code/data/h_e1/openml_dataset_corpus.csv (N=5,217; 24 cols)

**Appendix B: MCP Tool Usage Summary**
- Total MCP calls: 3
- Tools: mcp__clearThought__scientificmethod × 3
  - H-E1-verification (hypothesis stage)
  - H-E1-verification (experiment stage)
  - H-M-integrated (hypothesis + experiment stages)

**Appendix C: Established Facts (BUILD_ON — Not Re-Verified)**
1. NB-2 appropriate for N_tasks (CT LR=2222.68, h-e1)
2. C(decade) required as primary covariate (not optional robustness)
3. Binary metadata presence outperforms continuous composite
4. h-e1 composite score IRR=1.076 below 1.1 threshold (path closed)
5. Tags are FAIR F1 (Findability) operationalization on OpenML
