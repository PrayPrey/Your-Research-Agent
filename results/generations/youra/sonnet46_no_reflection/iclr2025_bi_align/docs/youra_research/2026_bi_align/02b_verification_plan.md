# Verification Plan: AI-Idiomatic Feature Selection (AIFS) Adaptation Detection

**Date:** 2026-05-12
**Hypothesis ID:** H-AIFS-AdaptationDetection-v1
**Confidence:** 0.78
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under RLHF preference annotation conditions, if annotators have prior exposure to deployed RLHF-aligned AI systems (online condition) versus naive annotators (base condition), then online annotators show a statistically significant increase in conditional selection preference for AI-idiomatic stylistic features (β₄ > 0, OR ≥ 1.10 at α = 0.01 in a logit model controlling for supply, complexity, and cluster fixed effects), because repeated exposure to RLHF-optimized outputs causes annotators to internalize AI-native discourse norms — a human-to-AI stylistic adaptation effect latent in existing preference corpora.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in conditional preference for AI-idiomatic stylistic features between deployed (online) and naive (base) annotator conditions after controlling for marginal response supply, prompt complexity, and semantic cluster fixed effects. Formally: β₄ = 0 (OR = 1.0, 95% CI includes 1.0).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HH-RLHF (helpful-base + helpful-online splits) (standard) | Provides documented multi-condition collection (deployed vs. naive annotators) in a single preference corpus; 160K+ pairs; separate splits enable the core β₄ interaction test |
| **Model** | Conditional logistic regression + sentence-transformers | Logistic regression operationalizes the β₄ interaction test; frozen sentence-transformers provide stable semantic clustering without model-dependent drift |

**Dataset Details:**
- Source: HuggingFace: anthropic/hh-rlhf
- Path: https://github.com/anthropics/hh-rlhf

**Model Details:**
- Type: statistical
- Source: scikit-learn (logistic regression); sentence-transformers (all-MiniLM-L6-v2 frozen)

### 1.4 Baseline Methods (for reference comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| HH-RLHF preference modeling (AI-to-human direction only) | Standard RLHF reward modeling; no measurement of human adaptation direction | HH-RLHF (160K+ pairs) |
| Vishwarupe et al. (2026) benchmark audit | 16/16 benchmarks lack user-facing verification — qualitative finding | 16 alignment benchmarks |
| STEER-BENCH / HumanAgencyBench (2025) | Best LLMs 15+ points below human experts; 6-dimensional agency measurement | 30 community pairs / new prompts |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | HH-RLHF online annotators had substantially more prior AI interaction than base annotators | Online split from deployed Claude users; base split from naive crowdworkers — documented in Anthropic HH-RLHF dataset paper | Online/base split comparison becomes invalid as an adaptation proxy; must reframe as population heterogeneity study |
| A2 | AIFS features (structured lists, safety-prefaces, CoT markers) are specifically amplified in post-RLHF model outputs relative to pre-LLM human expert writing | Theoretical prediction based on RLHF optimization targets; requires discriminant validation against StackOverflow 2018 and FLAN baselines | β₄ interaction conflates adaptation with stable human preference for structured writing; hypothesis cannot be distinguished from null covariate shift |
| A3 | BeaverTails helpfulness and harmlessness labels were assigned with knowledge of harm category context, enabling category-stratified entropy analysis | Ji et al. (2023) annotation protocol specifies category-aware labeling; dual-label structure is a core feature of the dataset | Category-specific entropy analysis becomes invalid; fall back to aggregate entropy analysis |
| A4 | Within semantically matched prompt clusters (cosine ≥ 0.85), residual AIFS supply differences are adequately captured by the marginal AIFS covariate | Standard assumption in matched-pair preference analysis; partially validated by embedding-based cluster design | Supply confound not fully controlled; β₄ estimate biased upward; must use stricter matching or propensity score reweighting |
| A5 | PKU-SafeRLHF annotators evaluated turns sequentially within conversations (enabling within-conversation trajectory analysis) | Multi-turn structure of dataset suggests sequential evaluation; requires verification against annotation protocol documentation in Ji et al. (2024) | Within-conversation trajectory test invalid; scope PKU-SafeRLHF analysis to cross-split comparison only |

### 1.6 Research Gap & Novelty

No existing methodology quantifies the human-to-AI adaptation signal in existing preference corpora. All prior work (Shen et al. 2024, J.H. Shen et al. 2024, Vishwarupe et al. 2026) identifies the conceptual gap but provides no empirical measurement. This work introduces: (1) the AIFS construct as an automated proxy for AI-idiomatic stylistic features, (2) a conditional logit supply-control design that isolates annotator adaptation above model output supply inflation, and (3) the schema bidirectionality index as a new dataset property. Together, these transform existing preference corpora from AI-to-human evaluation archives into co-adaptation artifact repositories.

**Scope Reduction:** 40% of Phase 2A claims are BUILD_ON (established, not re-tested). Only PROVE_NEW claims are verified in Phases 2B-4.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: AIFS Preference Shift Detection in RLHF Preference Corpora**

**Statement**: Under RLHF preference annotation with multi-condition collection (deployed vs. naive annotators), if AIFS features are measured via automated regex extraction and preference pairs are matched by semantic cluster, then deployed-condition annotators show significantly higher conditional selection preference for AI-idiomatic features (β₄ > 0, OR ≥ 1.10, p < 0.01) compared to naive-condition annotators, because prior exposure to RLHF-optimized outputs shifts annotator preference weighting toward AI-native discourse norms.

**Rationale**: This is the foundational existence test — without demonstrating the β₄ signal, subsequent mechanism steps are ungrounded. It tests whether the human-to-AI adaptation effect exists at all as a latent signal in HH-RLHF, using the documented online/base split as a natural experimental condition.

**Variables** (from Phase 2A):
- Independent: Annotator condition (helpful-base vs. helpful-online split)
- Dependent: β₄ logit interaction coefficient (ΔAIFS × split)
- Controlled: Marginal AIFS supply, prompt semantic complexity, semantic cluster FE, response length, perplexity

**Verification Protocol**:
1. Extract AIFS features (structured lists, safety-prefaces, CoT markers) via regex from all candidate responses in HH-RLHF helpful-base and helpful-online splits (full dataset, 160K+ pairs).
2. Cluster prompts using frozen all-MiniLM-L6-v2 at cosine ≥ 0.85 threshold; compute ΔAIFS per matched preference pair.
3. Fit conditional logit model: P(chosen=1) ~ β₁·ΔAIFS + β₂·Δlength + β₃·Δperplexity + β₄·(ΔAIFS×split) + cluster_FE on the full matched dataset.
4. Test H₀: β₄ = 0; extract OR, 95% CI, p-value; verify effect persists after controlling for marginal AIFS supply distribution.
5. Report β₄, OR, CI, p-value, and McFadden R² for the full model.

**Success Criteria** (PoC: Direction-based):
- Primary: β₄ > 0, OR ≥ 1.10, 95% CI excludes 1.0, p < 0.01
- Secondary: Effect persists after marginal AIFS supply control

**Failure Response**:
- IF fails: PIVOT — reframe as population heterogeneity study (A1 violation check); investigate whether AIFS construct validity is the issue (triggers A2 validation priority)

**Dependencies**: None (foundation)

**Source**: Phase 2A SH1 (sh1_existence), Prediction P1

---

---
**H-M1: RLHF Training Amplifies AI-Idiomatic Stylistic Features Above Pre-LLM Baseline**

**Statement**: Under comparison of post-RLHF model outputs against pre-LLM human expert writing baselines (StackOverflow 2018, FLAN instruction templates), if AIFS features are measured via automated regex extraction, then post-RLHF outputs show significantly higher AIFS scores than pre-LLM baselines, because RLHF optimization explicitly rewards structured responses, safety-prefaces, and CoT scaffolding that are not characteristic of pre-LLM expert human writing.

**Rationale**: This validates AIFS construct validity — a prerequisite for interpreting β₄ as annotator adaptation rather than stable human preference for structured writing (A2). Without discriminant validation, the β₄ signal cannot be attributed to AI-specific stylistic exposure. This is the critical mechanistic step that prevents confounding with pre-existing human writing style preferences.

**Variables** (from Phase 2A):
- Independent: Text source (post-RLHF model outputs vs. StackOverflow 2018 vs. FLAN templates)
- Dependent: Mean AIFS score per source
- Controlled: Text length (token count), domain (technical Q&A)

**Verification Protocol**:
1. Sample ≥10,000 responses from HH-RLHF chosen candidates (post-RLHF) and ≥10,000 answers from StackOverflow 2018 dump (pre-LLM) and ≥5,000 FLAN instruction templates.
2. Apply identical AIFS regex feature extraction to all three corpora (same feature set: structured lists, safety-prefaces, CoT markers, hedging language).
3. Compute mean AIFS score per corpus with bootstrap 95% CI; test pairwise differences using two-sided Mann-Whitney U test.
4. Verify: AIFS(post-RLHF) > AIFS(StackOverflow) and AIFS(post-RLHF) > AIFS(FLAN) with statistical significance.
5. Report AIFS distributions and effect sizes (Cohen's d) for each pairwise comparison.

**Success Criteria** (PoC: Direction-based):
- Primary: Post-RLHF AIFS significantly exceeds both pre-LLM baselines (p < 0.05, Cohen's d > 0.3)
- Secondary: AIFS(StackOverflow 2018) and AIFS(FLAN) are not significantly different from each other (confirms pre-LLM baseline equivalence)

**Failure Response**:
- IF fails: EXPLORE — investigate which specific AIFS features fail discriminant validation; consider refining AIFS feature set before returning to H-E1 interpretation

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1, Assumption A2

---

---
**H-M2: Deployed Annotator Preference Weighting for AIFS Features Exceeds Supply Baseline**

**Statement**: Under the HH-RLHF helpful-online vs. helpful-base comparison with explicit marginal AIFS supply control, if the β₄ interaction coefficient is estimated with and without supply covariate, then β₄ remains positive and significant (OR ≥ 1.10, p < 0.01) after controlling for marginal AIFS supply distribution in the candidate pool, because the adaptation effect reflects genuine annotator preference shift — not merely increased availability of high-AIFS responses in the online collection context.

**Rationale**: This distinguishes the adaptation mechanism (H) from the supply confound (H0 alternative explanation) — the key methodological challenge identified as the hypothesis's critical tension. Confirming β₄ survives supply control is the primary causal argument for annotator adaptation vs. model selection artifact.

**Variables** (from Phase 2A):
- Independent: ΔAIFS × split interaction term (with/without supply control)
- Dependent: β₄ coefficient change when supply covariate is added/removed
- Controlled: Marginal AIFS supply proportion per split, prompt cluster FE

**Verification Protocol**:
1. Fit baseline logit without supply covariate: P(chosen=1) ~ β₁·ΔAIFS + β₄·(ΔAIFS×split) + cluster_FE.
2. Fit full logit with supply covariate: P(chosen=1) ~ β₁·ΔAIFS + β₂·Δlength + β₃·Δperplexity + β₄·(ΔAIFS×split) + β₅·supply_prop + cluster_FE.
3. Compare β₄ between baseline and full models; compute supply control attenuation ratio (β₄_full / β₄_baseline).
4. Run sensitivity analysis: vary supply covariate specification (quintiles, continuous, deciles); confirm β₄ direction and significance stability.
5. Report β₄ before/after supply control with attenuation ratio and stability across specifications.

**Success Criteria** (PoC: Direction-based):
- Primary: β₄ remains significant (p < 0.01) in full model with supply control
- Secondary: Attenuation ratio > 0.7 (supply control removes <30% of effect)

**Failure Response**:
- IF fails: PIVOT — β₄ driven by supply confound; scope analysis to within-cluster propensity score reweighting; document as limitation for A4 violation

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 2, Key Tension (supply confound), Assumption A4

---

---
**H-M3: AIFS-Preference Convergence is Strongest in RLHF-Normed Harm Categories**

**Statement**: Under BeaverTails harm category stratification, if helpfulness-harmlessness disagreement rate (D) is computed by AIFS quartile bin within each of 14 harm categories, then the AIFS-bin differential (ΔD_high-AIFS − ΔD_low-AIFS) is monotonically larger in RLHF-normed categories (violence, illegal_activities, hate_speech) than in socially ambiguous categories (sycophancy, misinformation, privacy_violation), because normative RLHF training is strongest in categories with explicit safety norms, producing greater entropy compression for high-AIFS responses in those categories.

**Rationale**: This validates the normative convergence mechanism — the third causal step. If AIFS preference convergence is category-specific (strongest where RLHF norms are clearest), it supports the hypothesis that the effect is driven by normative adaptation rather than a global style preference shift across all content types.

**Variables** (from Phase 2A):
- Independent: AIFS quartile bin (high vs. low) × harm category type (RLHF-normed vs. socially ambiguous)
- Dependent: Helpfulness-harmlessness disagreement rate D = P(helpfulness ≠ harmlessness preference) per category-bin cell
- Controlled: Prompt semantic cluster, response length, category base rate of disagreement

**Verification Protocol**:
1. Compute AIFS scores for all candidate responses in BeaverTails (333K+ QA pairs); stratify by AIFS quartile within each of 14 harm categories.
2. Compute D = P(helpfulness label ≠ harmlessness label preference) per (category × AIFS-bin) cell.
3. Calculate ΔD = D_low-AIFS − D_high-AIFS (positive ΔD = high-AIFS reduces disagreement) per category.
4. Pre-register 6 RLHF-normed categories (violence, illegal_activities, hate_speech, self_harm, weapon, drug) and 6 socially ambiguous categories; test ordinal prediction: ΔD(RLHF-normed) > ΔD(socially-ambiguous) in ≥4/6 pairs.
5. Compute rank correlation between category RLHF-norm intensity (expert-rated) and ΔD; test Spearman ρ significance.

**Success Criteria** (PoC: Direction-based):
- Primary: ΔD_high-AIFS > ΔD_low-AIFS in ≥4/6 pre-registered RLHF-normed categories
- Secondary: Rank correlation between RLHF-norm intensity and AIFS-bin differential significant at p < 0.05

**Failure Response**:
- IF fails: EXPLORE — investigate whether entropy compression is uniform (A3 violation) or driven by a different category axis; document as scope limitation

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3, Prediction P2, Assumption A3

---

---
**H-M4: Schema Bidirectionality Index Predicts β₄ Magnitude Ordinally Across Datasets**

**Statement**: Under cross-dataset comparison of HH-RLHF, BeaverTails, and PKU-SafeRLHF, if a 0–4 schema bidirectionality index is applied to each dataset's annotation schema and β₄ is estimated independently for each dataset, then the ordinal ranking β₄(HH-RLHF) < β₄(BeaverTails) < β₄(PKU-SafeRLHF) holds, because datasets with higher schema bidirectionality capture more annotator behavioral signals that enable detection of the adaptation effect.

**Rationale**: This tests whether the schema design gap (causal step 4) is mechanistically linked to adaptation detectability. A positive result would demonstrate that schema blindness (as confirmed by Vishwarupe et al. 2026) is not merely descriptive but has measurable consequences for β₄ magnitude — strengthening the policy implication for redesigning alignment dataset schemas.

**Variables** (from Phase 2A):
- Independent: Schema bidirectionality index score (0–4) per dataset
- Dependent: β₄ interaction coefficient magnitude estimated per dataset
- Controlled: Sample size per dataset, annotation protocol differences

**Verification Protocol**:
1. Apply 0–4 bidirectionality index rubric to HH-RLHF, BeaverTails, and PKU-SafeRLHF annotation schemas (score each on: output-only/static user attributes/longitudinal linkage/user belief-state change/behavioral outcome tracking).
2. Estimate β₄ independently for each dataset using the same conditional logit specification as H-E1.
3. Test ordinal prediction: β₄(HH-RLHF) < β₄(BeaverTails) < β₄(PKU-SafeRLHF) with each pairwise difference in expected direction.
4. Verify PKU-SafeRLHF annotation protocol supports sequential turn evaluation (A5 check); if not, scope to cross-split comparison only.
5. Report β₄ estimates per dataset with 95% CI; document ordinal alignment and any violations.

**Success Criteria** (PoC: Direction-based):
- Primary: All three pairwise β₄ differences in expected ordinal direction
- Secondary: Each β₄ estimate individually significant at p < 0.05 within its dataset

**Failure Response**:
- IF fails: EXPLORE — ordinal ranking fails; document bidirectionality index as insufficient predictor; scope dataset comparison to descriptive analysis of schema properties

**Dependencies**: H-M3

**Source**: Phase 2A Causal Step 4, Prediction P3, Assumption A5

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | β₄ > 0, OR ≥ 1.10, p < 0.01 | STOP — reassess entire hypothesis |
| H-M1 | MUST_WORK | AIFS(post-RLHF) > pre-LLM baselines (p < 0.05, d > 0.3) | STOP — AIFS construct invalid; H-E1 interpretation collapses |
| H-M2 | SHOULD_WORK | β₄ survives supply control (p < 0.01, attenuation < 30%) | PIVOT — document supply confound; scope analysis |
| H-M3 | SHOULD_WORK | ΔD_high > ΔD_low in ≥4/6 RLHF-normed categories | EXPLORE — document as scope limitation |
| H-M4 | SHOULD_WORK | Ordinal β₄ ranking confirmed across 3 datasets | EXPLORE — bidirectionality index as descriptive only |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1 (from A1): Annotator Condition Confound**

**Source Assumption:** A1 — HH-RLHF online annotators had substantially more prior AI interaction than base annotators.

**Description:** If online/base split differences reflect population demographics or task familiarity rather than AI exposure, the β₄ signal cannot be attributed to adaptation. The comparison becomes a population heterogeneity study rather than an adaptation study.

**Affected Hypotheses:** H-E1, H-M2

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Verify annotation protocol documentation confirms AI exposure differential; conduct literature review of Anthropic HH-RLHF dataset paper for explicit characterization.
2. **Detection:** Run demographic sensitivity checks; if β₄ collapses when controlling for task experience proxies, R1 is materializing.
3. **Response:** PIVOT to population heterogeneity framing; reframe contribution as "documenting adaptation-confounded preference signals" rather than "measuring adaptation."

**Early Warning Indicators:**
- β₄ is significant but smaller than OR ≥ 1.05 (weak signal may indicate population noise)
- Effect disappears when semantic cluster granularity increases (topic specificity eliminates signal)

---

**Risk R2 (from A2): AIFS Construct Invalidity**

**Source Assumption:** A2 — AIFS features are specifically amplified in post-RLHF outputs relative to pre-LLM human expert writing.

**Description:** If AIFS features (structured lists, safety-prefaces, CoT markers) were already prevalent in pre-LLM expert writing (e.g., StackOverflow structured answers), the construct fails discriminant validity — β₄ measures stable human preference for structured writing, not AI-specific adaptation.

**Affected Hypotheses:** H-E1, H-M1, H-M2 (all depend on AIFS validity)

**Severity:** Critical

**Mitigation Strategy:**
1. **Prevention:** H-M1 is explicitly designed as discriminant validation — run H-M1 before over-interpreting H-E1; use two pre-LLM baselines (StackOverflow + FLAN) to triangulate.
2. **Detection:** If H-M1 fails (no significant AIFS elevation in post-RLHF), R2 has materialized.
3. **Response:** EXPLORE — refine AIFS feature set to focus on features absent from pre-LLM writing (e.g., safety-prefaces specifically, not structured lists); re-run H-E1 with revised AIFS.

**Early Warning Indicators:**
- StackOverflow 2018 AIFS scores overlap substantially with HH-RLHF chosen candidates
- FLAN templates show high structured-list AIFS scores (lists were common in instruction templates)

---

**Risk R3 (from A3): BeaverTails Category Label Independence**

**Source Assumption:** A3 — BeaverTails helpfulness and harmlessness labels were assigned with knowledge of harm category context.

**Description:** If annotators were category-blind during labeling, category-stratified entropy analysis produces noise rather than meaningful normative convergence patterns. The H-M3 test becomes invalid.

**Affected Hypotheses:** H-M3

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Verify Ji et al. (2023) annotation protocol explicitly states category-aware labeling; check annotation instructions in dataset documentation.
2. **Detection:** If D rates show no systematic variation across harm categories (near-uniform), category structure is not informative.
3. **Response:** SCOPE — fall back to aggregate entropy analysis (AIFS-bin differential pooled across all 14 categories); document as limitation.

**Early Warning Indicators:**
- D rates are nearly uniform across all 14 categories in preliminary analysis
- High variance within categories suggests annotator inconsistency

---

**Risk R4 (from A4): Supply Confound Not Fully Controlled**

**Source Assumption:** A4 — Marginal AIFS supply differences are adequately captured by the supply covariate within matched clusters.

**Description:** If the supply covariate does not fully capture AIFS availability differences between online and base splits, β₄ is biased upward. The measured "adaptation" could be artifact of supply differences that were incompletely controlled.

**Affected Hypotheses:** H-M2

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** H-M2 explicitly tests supply control robustness with multiple covariate specifications (quintiles, continuous, deciles).
2. **Detection:** Large attenuation ratio (β₄_full << β₄_baseline, attenuation > 50%) signals supply confound dominance.
3. **Response:** PIVOT — use stricter matching (1:1 propensity score matching on AIFS supply) or inverse probability weighting; re-estimate β₄ with tighter supply control.

**Early Warning Indicators:**
- Attenuation ratio < 0.5 in any supply covariate specification
- β₄ loses significance when supply control is tightened

---

**Risk R5 (from A5): PKU-SafeRLHF Sequential Evaluation Unverified**

**Source Assumption:** A5 — PKU-SafeRLHF annotators evaluated turns sequentially within conversations.

**Description:** If annotation was cross-turn or non-sequential, the within-conversation trajectory test is invalid. H-M4's PKU-SafeRLHF β₄ estimate may be contaminated by non-sequential annotation artifacts.

**Affected Hypotheses:** H-M4

**Severity:** Low

**Mitigation Strategy:**
1. **Prevention:** Verify annotation protocol before running H-M4 PKU analysis; check Ji et al. (2024) dataset paper explicitly.
2. **Detection:** If PKU-SafeRLHF β₄ estimate shows unexpected patterns (e.g., very high variance across prompt clusters), sequential evaluation may be violated.
3. **Response:** SCOPE — restrict PKU-SafeRLHF analysis to cross-split comparison only (still valid for bidirectionality index); document trajectory test as pending future validation.

**Early Warning Indicators:**
- PKU-SafeRLHF annotation protocol documentation is ambiguous about sequential evaluation
- β₄ estimate for PKU has very wide CI relative to other datasets

---

### 4.2 Risk Summary Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Annotator condition confound (demographic vs. adaptation) | A1 | High | H-E1, H-M2 | Verify annotation protocol; reframe if needed |
| R2 | AIFS construct invalidity (pre-LLM baseline overlap) | A2 | Critical | H-E1, H-M1, H-M2 | H-M1 discriminant test first; refine AIFS features |
| R3 | BeaverTails category label independence | A3 | Medium | H-M3 | Verify annotation protocol; fall back to aggregate |
| R4 | Supply confound not fully controlled by covariate | A4 | High | H-M2 | Multi-specification robustness test; propensity matching |
| R5 | PKU-SafeRLHF sequential evaluation unverified | A5 | Low | H-M4 | Verify protocol; scope to cross-split if violated |

Critical Risks: 1 (R2)
High Risks: 2 (R1, R4)
Medium Risks: 1 (R3)
Low Risks: 1 (R5)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1: AIFS Preference Shift Detection
    (EXISTENCE — MUST_WORK — no dependencies)
         │
         ▼
[Level 1 - Core Mechanism: AIFS Construct Validity]
    H-M1 ← H-E1
    (MECHANISM — MUST_WORK — validates AIFS construct)
         │
         ▼
[Level 2 - Core Mechanism: Supply Control]
    H-M2 ← H-M1
    (MECHANISM — SHOULD_WORK — isolates adaptation from supply)
         │
         ▼
[Level 3 - Core Mechanism: Normative Convergence]
    H-M3 ← H-M2
    (MECHANISM — SHOULD_WORK — category-stratified validation)
         │
         ▼
[Level 4 - Core Mechanism: Schema Bidirectionality]
    H-M4 ← H-M3
    (MECHANISM — SHOULD_WORK — cross-dataset schema audit)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Critical Gates: H-E1 (MUST_WORK) and H-M1 (MUST_WORK)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │ W7      │
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │         │
  [Gate 1]       │      ◆  │         │         │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │         │
  [Gate 2]       │         │      ◆  │         │         │         │
  H-M2           │         │         │ ████    │         │         │
  H-M3           │         │         │         │ ████    │         │
  H-M4           │         │         │         │         │ ████    │
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 7 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 + 1 + 1 (H-M2, M3, M4)

Slack Available: 0 weeks (all sequential)
Critical Gates: Gate 1 (H-E1, MUST_WORK) and Gate 2 (H-M1, MUST_WORK)

Duration Breakdown:
  Phase 1 (Foundation): 2 weeks (H-E1)
  Phase 2 (Mechanisms): 5 weeks (H-M1: 2 weeks; H-M2–H-M4: 1 week each)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0 (no quantitative boundary conditions detected)

Verification Phases: 2
1. Foundation (H-E1): MUST_WORK gate
2. Mechanisms (H-M1–H-M4): MUST_WORK (H-M1) + SHOULD_WORK (H-M2–H-M4)

Total Duration: 7 weeks
Critical Path Length: 7 weeks
Execution Mode: Sequential chain
Primary Dataset: HH-RLHF (160K+ pairs, full dataset)
Secondary Datasets: BeaverTails (333K+ QA pairs), PKU-SafeRLHF
Compute: CPU-only (conditional logistic regression; no GPU required)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
  → Extract AIFS, cluster prompts, fit conditional logit on full HH-RLHF
Step 2: Evaluate Gate 1 → If β₄ > 0, OR ≥ 1.10, p < 0.01: PROCEED
Step 3: Execute H-M1 (AIFS Discriminant Validation) — Week 3-4
  → Compare AIFS across post-RLHF, StackOverflow 2018, FLAN baselines
Step 4: Evaluate Gate 2 → If AIFS discriminant validation passes: PROCEED
Step 5: Execute H-M2 (Supply Control Robustness) — Week 5
  → Test β₄ stability across supply covariate specifications
Step 6: Execute H-M3 (Normative Convergence in BeaverTails) — Week 6
  → Compute category-stratified AIFS-bin entropy differentials
Step 7: Execute H-M4 (Schema Bidirectionality Index) — Week 7
  → Apply index to 3 datasets; test ordinal β₄ ranking
Step 8: Verification complete — proceed to Phase 2C
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Existing RLHF preference corpora contain a latent human-to-AI
stylistic adaptation signal, detectable as a significant β₄ interaction
between AIFS features and annotator deployment condition, above and beyond
model output supply confounds.

Supporting Evidence:
1. RLHF optimization dynamics demonstrably amplify structured, safety-preface,
   and CoT features (Rafailov et al. 2023, 8428 citations; STEER-BENCH).
2. HH-RLHF collection context creates documented differential in annotator
   AI-exposure (deployed Claude users vs. naive crowdworkers).
3. BeaverTails 14-category structure and dual-label design enable granular
   normative convergence tests across harm categories.

Strengths:
- Uses existing public data — no new annotation needed
- Supply-control design isolates adaptation from model output confound
- Three-test empirical battery provides triangulated evidence
- Pre-registered falsification criteria established in Phase 2A

Expected Outcomes:
- P1: β₄ > 0, OR ≥ 1.10, p < 0.01 in HH-RLHF conditional logit
- P2: ΔD_high-AIFS > ΔD_low-AIFS in ≥4/6 RLHF-normed BeaverTails categories
- P3: β₄ ordinal ranking: HH-RLHF < BeaverTails < PKU-SafeRLHF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): β₄ = 0 — no significant difference in conditional
preference for AI-idiomatic stylistic features between online and base
annotator conditions after controlling for marginal AIFS supply, prompt
complexity, and semantic cluster fixed effects.

Counter-Arguments:
1. Online/base split differences may reflect population demographics (task
   experience, education, familiarity with technical writing) rather than
   AI-specific exposure — the construct is unobservable.
2. AIFS features (structured lists) were already prevalent in pre-LLM expert
   writing (StackOverflow); construct may fail discriminant validation,
   making β₄ measure stable writing style preference, not AI adaptation.
3. No annotator IDs in public HH-RLHF preclude within-annotator drift
   analysis — correlation is the strongest causal claim available.

Potential Failure Points:
- R2: AIFS construct invalidity → β₄ conflated with stable structured writing preference
- R1: Annotator condition confound → β₄ reflects demographic heterogeneity
- R4: Supply control inadequate → β₄ biased by model output availability differences

Conditions Under Which H0 Would Be Supported:
- β₄ = 0 or reverses sign after supply control
- H-M1 fails: AIFS(post-RLHF) not significantly > StackOverflow 2018 or FLAN
- Effect disappears after topic cluster fixed effects at finer granularity

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

The hypothesis H-AIFS-AdaptationDetection-v1 presents a testable claim
supported by documented collection context differences in HH-RLHF. However,
the null hypothesis raises valid concerns regarding AIFS construct validity
(R2, Critical risk) and the annotator condition confound (R1, High risk).

Resolution Path:

The verification plan addresses this dialectic through:
1. H-M1 (Foundation Gate 2): Discriminant AIFS validation against pre-LLM
   baselines — directly tests the antithesis's strongest objection first.
2. H-M2 (Supply Control): Explicit supply covariate with multi-specification
   robustness — addresses the supply confound central to H0.
3. H-E1 (Foundation Gate 1): Full-dataset β₄ estimation with pre-registered
   threshold (OR ≥ 1.10) — provides clean falsification criteria.

Conditions for Thesis Support:
- H-E1: β₄ > 0, OR ≥ 1.10, p < 0.01
- H-M1: AIFS(post-RLHF) significantly > both pre-LLM baselines
- H-M2: β₄ survives supply control (attenuation < 30%)

Conditions for Antithesis Support:
- H-E1 fails: β₄ = 0 or CI includes 1.0
- H-M1 fails: No AIFS elevation in post-RLHF vs. pre-LLM baselines
- H-M2 fails: β₄ collapses after supply control

Nuanced Outcome Possibilities:
1. Full Support: H-E1 + H-M1 + H-M2 pass → Core thesis validated; P2/P3 provide
   additional mechanistic depth.
2. Partial Support: H-E1 + H-M1 pass but H-M2 partial → Supply confound partially
   explains β₄; refined thesis: "adaptation signal exists but partially supply-driven."
3. Construct Failure: H-M1 fails → AIFS redesign needed; β₄ from H-E1 uninterpretable.
4. No Support: H-E1 fails → H0 supported; annotator condition has no detectable
   effect on AIFS preference weighting.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | β₄ signal latent in HH-RLHF splits | Split differences = demographics | H-E1 test with pre-registered OR ≥ 1.10 threshold |
| Construct | AIFS is AI-specific post-RLHF feature | AIFS pre-existed in human writing | H-M1 discriminant test vs. StackOverflow + FLAN |
| Mechanism | Adaptation above supply confound | β₄ driven by model output availability | H-M2 multi-spec supply control robustness |
| Scope | Normative convergence in harm categories | Uniform across all content types | H-M3 pre-registered category stratification |
| Generalization | Schema design predicts detectability | Only 3 datasets, ordinal test underpowered | H-M4 ordinal test (conservative, defensible) |

Overall Robustness Score: Medium-High
- Critical risk (R2) is addressed by H-M1 before full β₄ interpretation
- High risks (R1, R4) are mitigated by design (protocol verification, supply control)
- Low power for cross-dataset comparison (H-M4) is acknowledged; ordinal test is conservative

Confidence in Verification Plan: 0.78

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** β₄ > 0 (OR ≥ 1.10, p < 0.01) — deployed RLHF annotators prefer AI-idiomatic features above supply baseline.
- ID: H-AIFS-AdaptationDetection-v1 | Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (40% scope reduction from BUILD_ON claims)
- Sub-Hypotheses: 5 total (H-E1 × 1, H-M × 4)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 MUST_WORK gates (H-E1, H-M1)

**Risk Assessment:** Medium-High
- Critical concern: AIFS construct validity (R2) — addressed by H-M1 discriminant test first
- High concerns: Annotator confound (R1), supply control inadequacy (R4) — both mitigated by design

**Immediate Action:** Begin Phase 2C experiment design for H-E1 (conditional logit on full HH-RLHF)

### 7.2 Conclusions

**Key Achievements:**
- 5 hypotheses across 2 phases (7 weeks total)
- H0 addressed: β₄ = 0 (supply-controlled null, formally specified)
- 40% scope reduction: BUILD_ON claims excluded from re-verification
- Critical risk R2 mitigated by sequencing H-M1 as Gate 2 before H-E1 interpretation

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: β₄ logit interaction test on full HH-RLHF (160K+ pairs)
- Gate 1: MUST PASS (β₄ > 0, OR ≥ 1.10, p < 0.01)

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: AIFS discriminant validation vs. StackOverflow 2018 + FLAN (Week 3-4)
- H-M2: Supply control robustness — multi-spec β₄ stability (Week 5)
- H-M3: BeaverTails normative convergence — category-stratified entropy (Week 6)
- H-M4: Schema bidirectionality index — cross-dataset ordinal β₄ ranking (Week 7)
- Gate 2: H-M1 MUST PASS (AIFS construct valid)

**Critical Decision Points:**

1. **Gate 1 (H-E1 Foundation):**
   - FAIL → STOP, reassess hypothesis; investigate R1/R2 root causes
   - PASS → Proceed to H-M1

2. **Gate 2 (H-M1 MUST_WORK):**
   - FAIL → STOP, redesign AIFS construct; H-E1 β₄ uninterpretable
   - PASS → Proceed to H-M2–H-M4

3. **H-M2–H-M4 (SHOULD_WORK):**
   - Failures narrow scope but do not invalidate core thesis
   - Each failure documented as limitation for Phase 6 paper

**Open Questions (from Phase 2A):**
- Does β₄ replicate on BeaverTails and PKU-SafeRLHF, or is it HH-RLHF-specific?
- Which specific AIFS features (safety-prefaces vs. structured lists vs. CoT) drive β₄?
- Does PKU-SafeRLHF support sequential turn evaluation (A5 verification needed)?
- Can the bidirectionality index be reliably applied by a single analyst?

**Recommendations:**

1. **Immediate Actions:**
   - Start Phase 2C with H-E1 experiment design (conditional logit specification)
   - Verify HH-RLHF annotation protocol documentation for A1 confirmation
   - Pre-register falsification criteria before data access

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path; reserve 1-week buffer for H-M1 refinement
   - CPU compute sufficient — no GPU required for logistic regression pipeline

3. **Failure Management:**
   - Document all failures in Phase 4 checkpoint files
   - Execute PIVOT strategies per risk mitigation plans
   - Write Serena memory on any PARTIAL/FAIL for cross-pipeline learning

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: `03_refinement.yaml` (ID: H-AIFS-AdaptationDetection-v1)
- Schema version: 10.0.0 (Free-Parse Schema)
- Discussion exchanges: 15 (convergence: qualitative)

**B. MCP Tool Usage Summary**
- ClearThought scientificmethod: Called for H-E1 and H-M integrated chain
- Total MCP calls: 2 (incremental mode, 4-step causal chain)
- Scope reduction applied: 40% (4 BUILD_ON claims excluded)

---

*Generated by YouRA Phase 2B (v7.7.0) | 2026-05-12*
