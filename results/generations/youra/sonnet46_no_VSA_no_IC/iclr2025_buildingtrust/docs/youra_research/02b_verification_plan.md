# Verification Plan: Trustworthiness Generalization Predictive Validity

**Date:** 2026-08-20
**Hypothesis ID:** H-TrustPredVal-v1
**Confidence:** 0.72
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under evaluation of 15+ publicly available LLMs on matched in-distribution/OOD trustworthiness
benchmark pairs, if we compute partial Spearman ρ between in-distribution and OOD model rankings
(controlling for general capability via MMLU), then the fairness dimension (BBQ-Disambig → BBQ-Ambig)
shows significantly positive partial ρ (ρ > 0.4, p < 0.05) while the adversarial robustness dimension
(GLUE → AdvGLUE, ANLI R1 → R3) shows lower partial ρ, because fairness failures reflect stable latent
statistical biases in model representations that manifest consistently across distribution shifts,
while adversarial robustness benchmarks are specifically designed to overcome models' current
capabilities and therefore do not track stable generalizable trustworthiness properties.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in partial Spearman ρ (MMLU-controlled) between the fairness
dimension and the robustness dimension for in-distribution to OOD model rank prediction
(Δρ = 0 across dimensions, Fisher z-test p ≥ 0.05).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Aggregated multi-model trustworthiness scores (standard) | Provides published multi-model scores on all target benchmark pairs (BBQ, ANLI, GLUE/AdvGLUE) with 15+ models, enabling Spearman ρ computation without new data collection |
| **Model** | Overlapping model set across evaluation sources | Diverse model family coverage enables Spearman ρ with sufficient range; base/instruction-tuned pairs enable P3 analysis |

**Dataset Details:**
- Source: TrustLLM (Huang et al., ICML 2024), GLUE-X (Yang et al., ACL 2023), OOD_NLP (Yuan et al., NeurIPS 2023), DecodingTrust (Wang et al., NeurIPS 2023)
- Path: Published leaderboards and paper tables; GitHub repos: HowieHwong/TrustLLM, YangLinyi/GLUE-X, lifan-yuan/OOD_NLP, AI-secure/DecodingTrust

**Model Details:**
- Type: Mixed (decoder-only transformers at various scales)
- Source: LLaMA-2 family (7B, 13B, 70B, Chat variants), Mistral (7B, Instruct), Falcon, GPT-3.5, GPT-4, Vicuna, Alpaca

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| TrustLLM multi-model evaluation (Huang et al., ICML 2024) | 16 models across 6 trustworthiness dimensions | BBQ, ANLI, TruthfulQA variants |
| DecodingTrust (Wang et al., NeurIPS 2023) | GPT-3.5 and GPT-4; GPT-4 more adversarially vulnerable despite higher standard scores | AdvGLUE++, OOD robustness, fairness |
| Gevers & Daelemans (2026) commonsense predictive validity | 23 LLMs; task-dependent predictive validity; rank correlations with leave-one-family-out CV | Commonsense benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Common model set ≥ 10 models with scores on BBQ-Disambig and BBQ-Ambig | TrustLLM evaluates 16 LLMs on BBQ variants | P1 cannot be tested (insufficient power for Spearman ρ) |
| A2 | MMLU scores available for same model set | MMLU scores widely published for LLaMA-2, GPT, Mistral, Falcon | Fall back to raw ρ (conflates trustworthiness with capability) |
| A3 | BBQ-Disambig and BBQ-Ambig use identical scoring protocols across aggregated sources | TrustLLM uses consistent evaluation protocols | Rank correlation reflects protocol differences, not genuine fairness generalization |
| A4 | Adversarial design of AdvGLUE/ANLI R3 disrupts rank stability detectably | DecodingTrust rank reversal; ANLI R3 design philosophy | Δρ < 0.2; asymmetry claim not supported (hypothesis not falsified) |
| A5 | Aggregating scores across papers yields comparable values | Standard benchmarks use fixed test sets | Must restrict to single-source datasets (reduces N) |

### 1.6 Research Gap & Novelty

**Gap:** No prior study computes Spearman ρ across 15+ models between in-distribution and OOD
trustworthiness benchmark scores. DecodingTrust (N=2), TrustLLM (no cross-split ρ), GLUE-X (accuracy
gap, not rank correlation) all address adjacent questions without treating cross-split predictive validity
as the primary research question.

**Novelty:** First application of predictive validity methodology (Gevers & Daelemans 2026) to
trustworthiness benchmarks, with capability control via partial Spearman ρ to isolate
trustworthiness-specific generalization. Introduces latent-bias-stability vs. adversarial-design
distinction as the mechanistic explanation for dimension-specific predictive validity differences.

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
**H-E1: Data Availability for Cross-Split Predictive Validity Analysis**

**Statement**: Under aggregation of published LLM evaluation scores from TrustLLM, GLUE-X, OOD_NLP,
and MMLU leaderboard, if we extract per-model scores for each target benchmark pair (BBQ-Disambig/Ambig,
GLUE/AdvGLUE, ANLI R1/R3) and MMLU, then a common overlapping model set of N ≥ 10 models exists across
all required benchmarks, because TrustLLM (16 LLMs), GLUE-X (21 LLMs), and OOD_NLP collectively cover
the same major model families (LLaMA-2, GPT, Mistral, Falcon) with compatible evaluation setups.

**Rationale**: This foundational hypothesis establishes data sufficiency. Without N ≥ 10 overlapping
models, partial Spearman ρ has insufficient statistical power (Δρ = 0.3 requires N ≈ 15 for 80% power
at p < 0.05). Verifying data availability before statistical analysis prevents underpowered conclusions.

**Variables** (from Phase 2A variables_table):
- Independent: Score source (TrustLLM / GLUE-X / OOD_NLP / MMLU leaderboard)
- Dependent: N overlapping models with all required benchmark scores
- Controlled: Model name standardization protocol; evaluation protocol compatibility

**Verification Protocol** (3 steps):
1. Extract per-model score tables from each source repository and standardize model names.
2. Build model × benchmark matrix (7 columns: BBQ-Disambig, BBQ-Ambig, GLUE, AdvGLUE, ANLI-R1, ANLI-R3, MMLU); count N per cell and N_common.
3. Flag cells with N < 10 as underpowered; report N_common explicitly as the analysis basis.

**Success Criteria** (PoC: Direction-based):
- Primary: N_common ≥ 10 models with all 7 required benchmark scores
- Secondary: BBQ-Disambig/Ambig cell has N ≥ 10; GLUE/AdvGLUE cell has N ≥ 10

**Failure Response**:
- IF fails: PIVOT — restrict analysis to available dimensions; supplement from DecodingTrust or HuggingFace leaderboards

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 5 (sh1_existence), Section 1.4 (A1)

---

**H-M1: Fairness Benchmark Rank Stability via Latent Bias Mechanism**

**Statement**: Under evaluation of the overlapping model set (from H-E1), if we compute partial Spearman
ρ between BBQ-Disambig and BBQ-Ambig model rankings (controlling for MMLU rank), then partial ρ_fairness
is significantly positive (ρ > 0.4, p < 0.05, one-tailed Fisher z-test), because fairness failures are
encoded as stable latent statistical biases in model weights during pretraining that manifest consistently
whether evaluation context is informative (disambig) or underspecified (ambig).

**Rationale**: H-M1 tests Causal Step 2 — whether stable latent biases translate to preserved rank
ordering across the ID/OOD fairness split. This is the primary confirmatory prediction (P1) of the
main hypothesis and the first MUST_WORK gate: if fairness does not show positive cross-split ρ after
capability control, the core theoretical claim fails.

**Variables** (from Phase 2A variables_table):
- Independent: Evaluation split (BBQ-Disambig = ID vs. BBQ-Ambig = OOD)
- Dependent: Partial Spearman ρ (MMLU-controlled) between ID and OOD model rankings
- Controlled: MMLU rank (partialed out), overlapping model set identity, evaluation protocol consistency

**Verification Protocol** (4 steps):
1. Compute raw Spearman ρ between BBQ-Disambig and BBQ-Ambig model rankings on N_common set.
2. Compute partial Spearman ρ removing MMLU rank as covariate using partial correlation formula.
3. Apply one-tailed Fisher z-transformation to test H0: partial ρ_fairness ≤ 0 (α = 0.05).
4. Run sensitivity analysis replacing MMLU with Winogrande as capability proxy; compare results.

**Success Criteria** (PoC: Direction-based):
- Primary: Partial ρ_fairness > 0.4 AND p < 0.05 (one-tailed Fisher z-test, N ≥ 10)
- Secondary: Raw ρ_fairness > partial ρ_fairness (confirms MMLU explains some variance)

**Failure Response**:
- IF fails: PIVOT — if ρ_fairness ≤ 0.2 or p ≥ 0.05, investigate whether N is sufficient and whether protocol aggregation introduces noise; consider single-source restriction (TrustLLM only)

**Dependencies**: H-E1 (overlapping model set must be established)

**Source**: Phase 2A Section 1.3 (Causal Step 2), Section 1.6 (P1)

---

**H-M2: Differential Predictive Validity — Fairness vs. Adversarial Robustness**

**Statement**: Under evaluation of the overlapping model set on both fairness and adversarial robustness
benchmark pairs, if we compare partial Spearman ρ_fairness (BBQ) to partial ρ_robustness
(GLUE→AdvGLUE and ANLI R1→R3), then partial ρ_fairness exceeds partial ρ_robustness by Δρ ≥ 0.2,
because the adversarial design of AdvGLUE and ANLI R3 specifically targets models that pass the
in-distribution version, disrupting the rank stability that stable latent biases would otherwise preserve.

**Rationale**: H-M2 tests the key theoretical asymmetry — not just that fairness generalizes, but that
it generalizes more than adversarial robustness. This is exploratory (P2, directional), but it is the
headline empirical claim that differentiates our work from measuring each dimension in isolation.

**Variables** (from Phase 2A variables_table):
- Independent: Trustworthiness dimension (Fairness vs. Robustness-Adversarial vs. Robustness-Difficulty)
- Dependent: Difference in partial Spearman ρ (Δρ = ρ_fairness − ρ_robustness)
- Controlled: Same overlapping model set for both dimensions; MMLU partialed from both

**Verification Protocol** (3 steps):
1. Compute partial Spearman ρ for GLUE→AdvGLUE and ANLI R1→R3 on overlapping models (same procedure as H-M1).
2. Compute Δρ = ρ_fairness − mean(ρ_AdvGLUE, ρ_ANLI); apply Fisher z-transformation for difference between two correlations (two-tailed, exploratory).
3. Report effect direction and magnitude; label P2 as exploratory/directional in all outputs.

**Success Criteria** (PoC: Direction-based):
- Primary: Δρ ≥ 0.2 (directional threshold, exploratory)
- Secondary: Both ρ_AdvGLUE < ρ_fairness AND ρ_ANLI < ρ_fairness individually

**Failure Response**:
- IF fails: EXPLORE — document limitation that dimension asymmetry not detected; does not invalidate H-M1 (fairness stability remains); refine mechanism theory

**Dependencies**: H-M1 (partial ρ_fairness must be established first)

**Source**: Phase 2A Section 1.3 (Causal Step 3), Section 1.6 (P2), Section 1.3 (key_tension)

---

**H-M3: Adversarial Design Disruption — Mechanism Confirmation**

**Statement**: Under evaluation of adversarial robustness benchmark pairs (GLUE→AdvGLUE, ANLI R1→R3),
if we examine model rank changes from ID to OOD and compute partial Spearman ρ for each adversarial pair
separately, then both ρ_AdvGLUE and ρ_ANLI are not significantly positive (ρ < 0.4 or p ≥ 0.05 after
MMLU control), confirming that adversarial benchmark construction specifically disrupts rank stability
relative to the fairness dimension.

**Rationale**: H-M3 completes the mechanistic account by confirming Causal Step 3 for each adversarial
pair individually. If one adversarial pair shows high ρ, the theoretical asymmetry requires qualification
(partial support); if both show low ρ, the adversarial-design disruption mechanism is robustly confirmed.

**Variables** (from Phase 2A variables_table):
- Independent: Adversarial pair identity (GLUE→AdvGLUE vs. ANLI R1→R3)
- Dependent: Partial Spearman ρ per adversarial pair (MMLU-controlled)
- Controlled: Same overlapping model set; MMLU rank covariate

**Verification Protocol** (3 steps):
1. Compute partial Spearman ρ_AdvGLUE and ρ_ANLI separately (same methodology as H-M1).
2. For each: apply Fisher z-test (one-tailed, threshold ρ = 0.4, α = 0.05) to test whether adversarial ρ reaches the fairness threshold.
3. Report rank reversal instances (models that move ≥ 5 positions from ID to OOD) as qualitative evidence for adversarial disruption.

**Success Criteria** (PoC: Direction-based):
- Primary: Both ρ_AdvGLUE < 0.4 OR p ≥ 0.05 (confirming adversarial disruption prevents significant rank stability)
- Secondary: ρ_AdvGLUE < ρ_ANLI (difficulty-based shift less disruptive than adversarial attack)

**Failure Response**:
- IF fails: EXPLORE — if ρ_AdvGLUE or ρ_ANLI ≥ 0.4 (p < 0.05), the adversarial-design mechanism is weaker than hypothesized; document as limitation and explore whether capability-based robustness partially survives adversarial targeting

**Dependencies**: H-M2 (differential predictive validity context established)

**Source**: Phase 2A Section 1.3 (Causal Step 3, falsifier), Section 4 (DecodingTrust evidence)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | N_common ≥ 10 models with all required benchmark scores | PIVOT: supplement from additional sources or restrict dimensions |
| H-M1 | MUST_WORK | Partial ρ_fairness > 0.4 AND p < 0.05 (Fisher z, N ≥ 10) | PIVOT: investigate N and protocol noise; consider single-source |
| H-M2 | SHOULD_WORK | Δρ ≥ 0.2 (ρ_fairness > ρ_robustness, directional) | EXPLORE: document limitation; H-M1 result unaffected |
| H-M3 | SHOULD_WORK | Both ρ_adversarial < 0.4 or p ≥ 0.05 (per pair) | EXPLORE: qualify mechanism; report as partial adversarial disruption |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 4 weeks (1+1+1+1) |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RISK-HYPOTHESIS MAPPING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1   | A1     | H-E1, H-M1          | High     |
| R2   | A2     | H-M1, H-M2, H-M3    | Medium   |
| R3   | A3     | H-M1                | Medium   |
| R4   | A4     | H-M2, H-M3          | Medium   |
| R5   | A5     | H-M1, H-M2, H-M3    | Low      |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.2 Mitigation Strategies

**Risk R1: Insufficient Overlapping Model Set (Source: A1)**

**Description:** The intersection of models with scores across BBQ, ANLI, GLUE/AdvGLUE, and MMLU may yield N < 10, making Spearman ρ underpowered.

**Affected Hypotheses:** H-E1 (direct), H-M1 (blocked if H-E1 fails)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Cross-reference TrustLLM (16 models), GLUE-X (21 models), OOD_NLP before committing to analysis — expected overlap based on shared model families is N ≥ 12.
2. **Detection:** H-E1 data audit reveals N_common before any statistical analysis is run.
3. **Response:**
   - PIVOT: Supplement with HuggingFace Open LLM Leaderboard and DecodingTrust for missing model scores.
   - SCOPE: If N_common for full intersection is < 10, analyze each dimension pair separately (BBQ pair, GLUE pair, ANLI pair) with available models.
   - ABORT: If no dimension has N ≥ 10, the study cannot be conducted with published data alone.

**Early Warning Indicators:**
- TrustLLM and GLUE-X share fewer than 8 model names after disambiguation
- MMLU scores unavailable for more than 5 models in the TrustLLM set

---

**Risk R2: MMLU Capability Control Infeasibility (Source: A2)**

**Description:** MMLU scores unavailable for the overlapping model set, preventing partial Spearman ρ computation.

**Affected Hypotheses:** H-M1, H-M2, H-M3

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Check MMLU availability on Open LLM Leaderboard and HuggingFace Hub for all models in the overlapping set during H-E1 audit.
2. **Detection:** Model × benchmark matrix with MMLU column reveals gaps.
3. **Response:**
   - PIVOT: Use Winogrande or ARC as alternative capability proxy for models missing MMLU.
   - SCOPE: If MMLU unavailable for > 30% of models, report raw Spearman ρ alongside partial ρ and note the limitation.

**Early Warning Indicators:**
- Instruction-tuned chat models (e.g., LLaMA-2-Chat-70B) lack MMLU scores on standard leaderboards
- MMLU evaluation protocol (few-shot count) varies across sources for the same model

---

**Risk R3: BBQ Scoring Protocol Inconsistency (Source: A3)**

**Description:** BBQ-Disambig and BBQ-Ambig evaluations from different papers use different metrics or few-shot setups, making rank correlation reflect protocol artifacts rather than genuine fairness generalization.

**Affected Hypotheses:** H-M1

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Use only TrustLLM as the single source for both BBQ-Disambig and BBQ-Ambig scores (consistent protocol guaranteed within one paper).
2. **Detection:** Compare per-model scores from TrustLLM vs. other sources for the same model on the same benchmark; flag deviations > 5pp as protocol mismatch.
3. **Response:**
   - SCOPE: Restrict BBQ analysis to TrustLLM-only model set (may reduce N); report protocol consistency as strength.

**Early Warning Indicators:**
- Significant score discrepancy (>10pp) for the same model-benchmark pair across two sources
- TrustLLM uses accuracy while another source uses bias score (different metric families)

---

**Risk R4: Adversarial Disruption Effect Too Small to Detect (Source: A4)**

**Description:** Δρ between fairness and robustness dimensions is < 0.2, preventing confirmation of the key asymmetry (P2).

**Affected Hypotheses:** H-M2, H-M3

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Pre-register P2 as exploratory/directional — failure to detect Δρ ≥ 0.2 does not falsify the main hypothesis (P1 is the primary confirmatory test).
2. **Detection:** After computing both partial ρ values, immediately assess whether Δρ < 0.2.
3. **Response:**
   - EXPLORE: Report the observed Δρ and interpret the magnitude; partial support if direction is correct even when Δρ < 0.2.
   - SCOPE: Analyze GLUE→AdvGLUE and ANLI R1→R3 separately — one may show lower ρ than the other.

**Early Warning Indicators:**
- DecodingTrust GPT-4/GPT-3.5 comparison showing ρ not reversal for GLUE/AdvGLUE
- General capability (MMLU) explains most of robustness ρ after partial correlation

---

**Risk R5: Cross-Paper Score Aggregation Bias (Source: A5)**

**Description:** Systematic evaluation protocol differences across papers (TrustLLM, GLUE-X, OOD_NLP) introduce noise into the model × benchmark score matrix.

**Affected Hypotheses:** H-M1, H-M2, H-M3

**Severity:** Low

**Mitigation Strategy:**
1. **Prevention:** Document evaluation protocol details (few-shot count, prompt template, metric) for each source-benchmark combination; flag incompatible combinations.
2. **Detection:** For models scored in multiple sources on the same benchmark, compare scores; flag > 5pp deviation.
3. **Response:**
   - SCOPE: Restrict to single-source subsets for sensitivity analysis; compare full-aggregation vs. single-source ρ values.

**Early Warning Indicators:**
- Same model (e.g., LLaMA-2-7B) has > 5pp score difference on ANLI R1 across OOD_NLP vs. another source

---

### 4.3 Risk Summary Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Risk                          | Source | Severity | Affected     | Mitigation           |
|----|-------------------------------|--------|----------|--------------|----------------------|
| R1 | Insufficient N overlapping    | A1     | High     | H-E1, H-M1   | Supplement sources   |
| R2 | MMLU unavailable for models   | A2     | Medium   | H-M1-3       | Alt proxy (Winogrde) |
| R3 | BBQ protocol inconsistency    | A3     | Medium   | H-M1         | Single-source (TrustLLM)|
| R4 | Adversarial Δρ < 0.2         | A4     | Medium   | H-M2-3       | Pre-register exploratory|
| R5 | Cross-paper score aggregation | A5     | Low      | H-M1-3       | Single-source sensitivity|

Critical Risks: 0
High Risks: 1 (R1)
Medium Risks: 3 (R2, R3, R4)
Low Risks: 1 (R5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence — data availability, no dependencies)
         │
         ▼  Gate 1: MUST PASS (N_common ≥ 10)
[Level 1 - Mechanism Core]
    H-M1 ← H-E1
    (Fairness ρ significance — confirmatory P1)
         │
         ▼  Gate 2: MUST PASS (ρ_fairness > 0.4, p < 0.05)
[Level 2 - Mechanism Comparison]
    H-M2 ← H-M1
    (Δρ asymmetry — exploratory P2)
         │
         ▼
[Level 3 - Mechanism Confirmation]
    H-M3 ← H-M2
    (Adversarial disruption per-pair confirmation)
         │
         ▼

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Hypothesis | Prerequisites | Gate Type    |
|-------|-----------|---------------|--------------|
| 0     | H-E1      | None          | MUST_WORK    |
| 1     | H-M1      | H-E1          | MUST_WORK    |
| 2     | H-M2      | H-M1          | SHOULD_WORK  |
| 3     | H-M3      | H-M2          | SHOULD_WORK  |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2    │ W3-4    │ W5      │ W6      │
──────────────────┼─────────┼─────────┼─────────┼─────────┼
PHASE 1: Foundation
  H-E1            │ ████████│         │         │         │
  [Gate 1]        │       ◆ │         │         │         │
──────────────────┼─────────┼─────────┼─────────┼─────────┼
PHASE 2: Mechanisms
  H-M1            │         │ ████████│         │         │
  H-M2            │         │         │ ████    │         │
  H-M3            │         │         │         │ ████    │
  [Gate 2]        │         │       ◆ │         │         │
──────────────────┼─────────┼─────────┼─────────┼─────────┼
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3

Total Duration: 6 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) = 6 weeks

Slack Available: 0 weeks (all sequential)
Phases: 2 (Foundation + Mechanisms)
Gates: 2 decision points
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1 to H-M3)
- Condition: 0

Verification Phases: 2
1. Foundation (H-E1) — 2 weeks
2. Mechanisms (H-M1, H-M2, H-M3) — 4 weeks

Total Duration: 6 weeks
Critical Path Length: 6 weeks
Execution Mode: Sequential chain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

**Step 1**: Execute H-E1 (Foundation) — Weeks 1-2
**Step 2**: Evaluate Gate 1 → If N_common ≥ 10, proceed; else PIVOT
**Step 3**: Execute H-M1 (Fairness ρ significance) — Weeks 3-4
**Step 4**: Evaluate Gate 2 → If partial ρ_fairness > 0.4 AND p < 0.05, proceed; else PIVOT
**Step 5**: Execute H-M2 (Δρ asymmetry) — Week 5
**Step 6**: Execute H-M3 (Per-pair adversarial confirmation) — Week 6
**Final**: Verification complete → proceed to Phase 4.5 Synthesis

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Core Claim:** Fairness benchmark scores predict OOD fairness performance (high partial ρ)
while adversarial robustness benchmark scores do not (low partial ρ), revealing that
trustworthiness dimensions differ fundamentally in their cross-split predictive validity.

**Supporting Evidence:**
1. BBQ study (Parrish et al., 2021): 3.4pp accuracy advantage when answers align with social
   bias persists across context framing — latent bias is context-independent.
2. TrustLLM (Huang et al., 2024): Consistent ordering of model families on fairness metrics
   across evaluation conditions — supports stable rank ordering hypothesis.
3. DecodingTrust (Wang et al., 2023): GPT-4 has higher standard scores but MORE adversarial
   vulnerability than GPT-3.5 — direct N=2 evidence for rank disruption under adversarial shift.

**Strengths:**
- Clear causal mechanism with distinct signatures (latent stability vs. adversarial disruption)
- Falsifiable primary prediction (P1: ρ > 0.4, p < 0.05) with exact thresholds
- Policy-relevant: informs which benchmark dimensions are reliable deployment proxies

**Expected Outcomes:**
- Primary (P1): Partial ρ_fairness > 0.4 AND p < 0.05 after MMLU control
- Secondary (P2): Δρ ≥ 0.2 (fairness ρ exceeds robustness ρ, exploratory)
- Tertiary (P3): Instruction-tuned models show smaller fairness TGG than base (directional)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Null Hypothesis (H0):** No significant difference in partial Spearman ρ (MMLU-controlled)
between the fairness dimension and the robustness dimension (Δρ = 0, Fisher z-test p ≥ 0.05).

**Counter-Arguments:**
1. General NLU capability may explain most cross-split rank correlation for all dimensions —
   partial ρ after MMLU control may be near-zero for fairness too (capability confound stronger
   than expected). Baseline from Gevers & Daelemans (2026) for commonsense benchmarks sets
   reference point.
2. Adversarial robustness may also reflect stable model properties (general reasoning quality)
   that survive adversarial targeting — some models may systematically outperform even on
   adversarially-constructed benchmarks, maintaining rank order.
3. Small common model set (N < 15 for some cells) means observed ρ values have wide confidence
   intervals — a "significant" result may not replicate with a different model set.

**Potential Failure Points:**
- R1: N_common < 10 prevents any ρ computation with sufficient power
- R3: BBQ protocol inconsistency makes ρ_fairness reflect evaluation artifact, not genuine bias stability
- R4: Adversarial disruption effect is too small (Δρ < 0.2) to confirm the key asymmetry

**Conditions Under Which H0 Would Be Supported:**
- Partial ρ_fairness ≤ 0.2 or p ≥ 0.05 after MMLU control (H-M1 fails)
- Partial ρ_robustness ≥ partial ρ_fairness (no dimension asymmetry; H-M2 fails)
- Both adversarial pairs show positive ρ (adversarial design does not disrupt rank stability; H-M3 fails)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Balanced Assessment:**

The hypothesis H-TrustPredVal-v1 presents a theoretically well-grounded claim that fairness
benchmarks have higher cross-split predictive validity than adversarial robustness benchmarks,
due to the stable-latent-bias vs. adversarial-design-disruption distinction. However, the null
hypothesis raises valid concerns: capability confounds may dominate after MMLU control, adversarial
robustness may also reflect partially-stable model properties, and small N limits statistical power.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes data sufficiency before any statistical claims
2. **Sequential mechanism testing (H-M1→M3):** Tests each step of the causal chain independently
3. **Gate conditions:** Allow early detection of H0 support (if H-M1 fails at Gate 2, H0 is supported)
4. **Exploratory labeling (P2, P3):** Prevents confirmatory bias in secondary analyses

**Conditions for Thesis Support:**
- MUST_WORK gates (H-E1, H-M1) both pass
- Partial ρ_fairness > 0.4 AND p < 0.05 (P1 confirmed)
- Δρ ≥ 0.2 in the predicted direction (P2 directionally supported)

**Conditions for Antithesis Support:**
- H-E1 fails (N_common < 10 — study infeasible with published data)
- H-M1 fails (partial ρ_fairness ≤ 0.2 or p ≥ 0.05 — fairness not stable after capability control)
- All adversarial pairs show ρ ≥ 0.4 (adversarial design does not disrupt rank stability)

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1, H-M1 pass; Δρ ≥ 0.2 → Thesis validated, publishable main finding
2. **Partial Support:** H-E1, H-M1 pass; Δρ < 0.2 → Fairness stability confirmed but dimension asymmetry unclear; refine theory
3. **Minimal Support:** H-E1 passes; H-M1 fails → Fairness does not generalize either; all dimensions show weak cross-split ρ; revisit theoretical mechanism
4. **No Support:** H-E1 fails → Study infeasible with current published data; requires data collection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect        | Thesis Position                    | Antithesis Challenge            | Resolution            |
|---------------|------------------------------------|---------------------------------|-----------------------|
| Existence     | Published scores exist for N≥10    | Overlap may be N<10             | H-E1 audit (Gate 1)   |
| Mechanism     | Fairness = stable latent bias      | Capability explains all ρ       | Partial ρ (MMLU ctrl) |
| Asymmetry     | Fairness ρ > Robustness ρ by Δ≥0.2 | No systematic dimension diff    | H-M2 Fisher z-test    |
| Adversarial   | Adversarial design disrupts rank   | Robust models stable regardless | H-M3 per-pair ρ       |
| Scope         | 15+ English-language LLMs          | Results may not generalize      | Report N; scope limits|

**Overall Robustness Score:** Medium-High
**Confidence in Verification Plan:** 0.72

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Cross-split predictive validity differs by trustworthiness dimension — fairness shows high partial ρ (stable latent bias), adversarial robustness shows low partial ρ (adversarial design disruption).
- ID: H-TrustPredVal-v1, Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (50% scope reduction from Phase 2A established facts)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3, H-C: 0)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points (Gate 1: N_common; Gate 2: ρ_fairness significance)

**Risk Assessment:** Medium
- Primary concerns: (1) insufficient overlapping model N, (2) MMLU capability proxy limitations

**Immediate Action:** Begin Phase 2C experiment design for H-E1 (data availability audit)

### 7.2 Conclusions

**Key Achievements:**
- 4 hypotheses across 2 phases with clear MUST_WORK / SHOULD_WORK gate structure
- H0 addressed: No significant Δρ across dimensions (Fisher z-test p ≥ 0.05)
- 50% scope reduction applied: BUILD_ON claims (Spearman ρ validity, benchmark pair validity) do not need re-verification

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Verify N_common ≥ 10 models with all required benchmark scores
- Gate 1: MUST PASS — N_common < 10 blocks all subsequent analysis

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Partial ρ_fairness > 0.4, p < 0.05 after MMLU control (confirmatory P1)
- H-M2: Δρ ≥ 0.2, ρ_fairness > ρ_robustness (exploratory P2)
- H-M3: Both adversarial pairs show non-significant or low ρ (mechanism confirmation)
- Gate 2: H-M1 must pass (MUST_WORK) — H-M2/M3 failures document limitations only

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP all analysis; PIVOT to supplement data or restrict scope
   - PASS → Proceed to Phase 2 mechanisms

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → Revisit mechanism theory; route to Phase 2A-Dialogue
   - OPTIONAL FAIL (H-M2, H-M3) → Document limitation; continue to Phase 4.5

**Open Questions:**
- What is the exact overlapping model set N per dimension cell after disambiguation?
- Can TrustLLM hallucination OOD task serve as reliability dimension with consistent protocol?
- Are MMLU scores available for all models in the overlapping set across all required papers?

**Recommendations:**

1. **Immediate Actions:**
   - Begin Phase 2C experiment design starting with H-E1 (data audit is gating)
   - Set up model name standardization mapping (LLaMA-2 aliases across papers)

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path; reserve 1 week buffer for data engineering challenges
   - H-E1 audit is the highest-leverage early task — resolves R1 risk immediately

3. **Failure Management:**
   - Document all N per cell values regardless of outcome
   - Execute PIVOT strategies for R1, R2 before declaring failure

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: `/docs/youra_research/03_refinement.yaml` (ID: H-TrustPredVal-v1)
- Architecture: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- Discussion exchanges: 7; Convergence: all 6 criteria met

**B. MCP Tool Usage Summary**
- Total MCP calls: 4 (mcp__clearThought__scientificmethod × 4)
- Call sequence: H-E1 hypothesis → H-E1 experiment → H-M-integrated hypothesis → H-M-integrated experiment
- Scope reduction applied: 50% (BUILD_ON claims excluded from hypothesis generation)
