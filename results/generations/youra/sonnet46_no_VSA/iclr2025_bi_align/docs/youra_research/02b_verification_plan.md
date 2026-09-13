---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-07-30"
generatedAt: "2026-07-30"
hypothesisId: "H-M1-V2"
totalHypotheses: 4
researchMode: incremental
---

# Verification Plan: Pairwise Partial Spearman Structure of Alignment Benchmarks After MMLU Scale Control

**Date:** 2026-07-30
**Hypothesis ID:** H-M1-V2
**Confidence:** 0.80
**Total Hypotheses:** 4

---

## 0. Established Facts & Scope Reduction

**Scope Reduction: 71%** (5 of 7 claims are BUILD_ON — do NOT re-verify)

### BUILD_ON (Pre-Validated — Skip in Phase 2B-4)

| Claim | Evidence |
|-------|----------|
| MMLU explains 32% of AlpacaEval-LC rank variance (R²=0.3199, N=28, p=0.0017) | h-e1 PASS snapshot |
| RLHF/SFT instruction-tuning improves TruthfulQA MC2 (+3.406 points, BCa CI [+2.589,+4.212], N=321) | h-m1 SUPERSEDED result |
| Raw cross-model Spearman rho(AlpacaEval-LC, TruthfulQA MC1) = +0.661 (N=52, CI=[0.38,0.82]) | failure_sh2-corr_run1.md |
| Fuzzy join (rapidfuzz WRatio/token_set_ratio threshold=75-80) works across open-weight leaderboards | h-e1 (match_rate=0.857), h-e2 (match_rate=0.517) |
| pingouin.partial_corr(x, y, covar=['MMLU'], method='spearman') is correct API | Phase 1 Exa verification |

### PROVE_NEW (Requires New Evidence — Phase 2B-4 Target)

| Claim | Evidence Gap |
|-------|-------------|
| Pairwise partial Spearman matrix of alignment-specific benchmarks not computed prior | clawrxiv:2603.00394 covers general benchmarks only; BenchScope uses ED scalar |
| Fisher z difference test (raw vs partial Spearman) not applied to alignment benchmark pairs | No prior work identified |

**Phase 2B-4 instruction:** Only generate hypotheses for PROVE_NEW claims. MMLU covariate validity, RLHF TruthfulQA effect, raw rho=+0.661, and fuzzy join methodology are accepted without re-testing.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under a population of N≥30 open-weight LLMs scored on {TruthfulQA MC2, BBQ accuracy, MMLU} from Open LLM Leaderboard v1 and lighteval/bbq_helm (HuggingFace), if MMLU is controlled via pingouin.partial_corr(method='spearman'), then the Fisher z difference test between raw Spearman rho and partial Spearman rho for the TruthfulQA × BBQ pair will yield a statistically detectable change (two-tailed p < 0.05 OR non-overlap of BCa 95% CIs), because MMLU captures general scale variation (R²=0.32 confirmed) that inflates the apparent co-movement of alignment benchmarks, and removing it reveals the true alignment-specific correlation structure (which may be near-zero, maintained, or sign-reversed relative to the raw correlation).

### 1.2 Alternative Hypothesis (H0)

H₀ (null): Raw Spearman rho = Partial Spearman rho (Fisher z difference test NOT significant, p ≥ 0.05) — MMLU scale control does not change the pairwise correlation structure of alignment benchmarks. Alignment co-movement is either purely scale-driven (no residual) or purely alignment-driven (scale does not contribute). Both outcomes of rejecting vs. failing-to-reject H₀ yield publishable characterizations.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Open LLM LB v1 × lighteval/bbq_helm × HarmBench Table 2 (tiered) | Provides TruthfulQA MC2+MMLU (300+ models) and BBQ accuracy; tiered design ensures Tier 1 publishable even if Tier 2+3 fail |
| **Model** | Population of open-weight LLMs (observational study) | Cross-model structural study; no training required |

**Dataset Details:**
- Source: fboulnois/llm-leaderboard-csv (GitHub) + lighteval/bbq_helm (HuggingFace) + arXiv:2402.04249 Table 2
- Path: Tier 1 (LLM LB v1 CSV + bbq_helm), Tier 2 (HarmBench hardcoded), Tier 3 (321 base/chat pairs from h-m1)

**Model Details:**
- Type: Observational cross-section (open-weight LLMs are study subjects)
- Source: Open LLM Leaderboard v1 + BBQ + HarmBench cross-section

### 1.4 Baseline Methods (for reference)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Raw Spearman rho (uncontrolled) | rho(AlpacaEval-LC, TruthfulQA MC1) = +0.661 | 52 open-weight models |
| clawrxiv:2603.00394 PCA (6 general benchmarks) | TruthfulQA = PC2 (23.4% variance orthogonal) | 40 models |
| BenchScope ED diagnostic (22 benchmarks) | Open LLM LB effective dimensionality = 1.7 | 8400+ evaluations |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | MMLU is valid scale proxy for joint dataset (TruthfulQA+BBQ population) | MMLU R²=0.32 vs AlpacaEval-LC (h-e1); need R² check in joint dataset | Scale control invalid; raw ≈ partial; primary finding is null (publishable) |
| A2 | lighteval/bbq_helm model names compatible via fuzzy join at threshold=75 | WRatio worked in prior runs; h-e1 match_rate=0.857 | N < 30; Tier 1 gate fails; fallback to HELM Lite v1.9.0 |
| A3 | N≥30 models with complete TruthfulQA+BBQ+MMLU after join | LLM LB v1 has 300+ models; BBQ has ~79 HELM Lite models | Pre-flight gate fails; report data availability finding |
| A4 | Model family labels extractable for cluster-bootstrap | Prior runs: 39 families extracted by string prefix | Use independent bootstrap (not clustered); wider CIs |
| A5 | HarmBench Table 2 (33 models) yields N≥20 matches to Tier 1 dataset | h-e1 found only 7/21 matched — Tier 2 N≥20 may be optimistic | Tier 2 fails; complete study with Tier 1 only; report limitation |

### 1.6 Research Gap & Novelty

First study to: (1) apply Fisher z difference test comparing raw vs MMLU-partial Spearman for alignment-specific benchmark pairs, (2) characterize the partial correlation structure of {TruthfulQA MC2, BBQ accuracy, HarmBench safety rate} as a set after scale control, and (3) demonstrate whether MMLU confounds alignment benchmark co-movement empirically. clawrxiv:2603.00394 covers 6 general benchmarks with PCA but does not include BBQ/HarmBench or apply Fisher z difference test. BenchScope provides ED=1.7 scalar but no pairwise directional analysis.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | MUST_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Data Infrastructure Viability (Existence Gate)**

**Statement**: Under the constraint of fuzzy joining Open LLM Leaderboard v1 (fboulnois/llm-leaderboard-csv) with lighteval/bbq_helm at WRatio threshold=75, if the pre-flight audit executes without URL failure, then N≥30 open-weight LLMs will have complete scores on TruthfulQA MC2, BBQ accuracy, and MMLU simultaneously, because both datasets use HuggingFace-compatible model names that prior runs have successfully matched at this threshold.

**Rationale**: This is the MUST_WORK foundation gate. All downstream partial Spearman analysis is invalid without sufficient N. Prior failure (H-E2) from HarmBench infrastructure issues makes explicit pre-flight testing mandatory here.

**Variables:**
- IV: Fuzzy join threshold (WRatio=75, fixed from prior runs)
- DV: N = count of models with complete TruthfulQA MC2 + BBQ accuracy + MMLU rows
- CV: Open-weight only filter; LLM LB v1 era; proprietary model exclusion

**Verification Protocol:**
1. Execute requests.head() URL test for LLM LB v1 CSV raw URL and HuggingFace bbq_helm dataset
2. Download llm.csv; extract model_name, TruthfulQA_MC2, MMLU columns; filter open-weight only
3. Load lighteval/bbq_helm via datasets.load_dataset(); group by model name; compute mean BBQ accuracy
4. Perform rapidfuzz WRatio join at threshold=75; apply token_set_ratio fallback if match_rate < 0.55
5. Count N complete rows (non-null in all three columns); report match_rate = N_matched / N_bbq

**Success Criteria:**
- Primary: N ≥ 30 complete rows (MUST_WORK gate)
- Secondary: match_rate ≥ 0.55 (lesson from h-e2: 0.517 was marginal)

**Failure Response:**
- IF N < 30: Try HELM Lite v1.9.0 as BBQ source fallback; lower threshold to 70; if still N < 30 → STOP, report data availability finding

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 5 (sh1_existence) + established fuzzy join methodology (BUILD_ON)

---

**H-M1: Scale Confound Verification**

**Statement**: Under the joint dataset of N≥30 open-weight LLMs (after H-E1 passes), if MMLU is regressed against TruthfulQA MC2 and BBQ accuracy separately, then both Spearman rho² (MMLU×TruthfulQA) and Spearman rho² (MMLU×BBQ) will exceed 0.05 in the joint dataset, because MMLU captures general capability variation that drives all benchmark scores upward simultaneously (confirmed for AlpacaEval-LC with R²=0.32).

**Rationale**: A1 (MMLU valid scale proxy) must be verified in the *joint* dataset — not just for AlpacaEval-LC. If MMLU does not correlate with these alignment benchmarks, partial Spearman controlling MMLU is scientifically invalid. This is the Causal Step 1 pre-flight gate.

**Variables:**
- IV: MMLU score (0-100, from LLM LB v1 CSV)
- DV: Spearman rho²(MMLU, TruthfulQA MC2) and Spearman rho²(MMLU, BBQ accuracy) in joint dataset
- CV: Same N open-weight models as H-E1 joint dataset

**Verification Protocol:**
1. Compute scipy.stats.spearmanr(df['MMLU'], df['TruthfulQA_MC2']); extract rho; compute R²=rho²
2. Compute scipy.stats.spearmanr(df['MMLU'], df['BBQ_accuracy']); extract rho; compute R²=rho²
3. Assert both R² > 0.05; if either fails → document MMLU-alignment orthogonality finding (publishable null)
4. Compute raw Spearman rho(TruthfulQA_MC2, BBQ_accuracy) as baseline for Fisher z comparison

**Success Criteria:**
- Primary: MMLU R²(TruthfulQA) > 0.05 AND MMLU R²(BBQ) > 0.05 (scale confound confirmed in joint dataset)
- Secondary: raw_rho(TruthfulQA, BBQ) computed and logged

**Failure Response:**
- IF MMLU R² ≤ 0.05 for either benchmark: A1 violated; document as "MMLU does not confound alignment benchmarks" — publishable null finding; skip H-M2 Fisher z test

**Dependencies**: H-E1 (N≥30 gate must pass)

**Source**: Phase 2A Section 1.3 Causal Step 1; Assumption A1

---

**H-M2: Partial Spearman + Fisher Z Difference Test**

**Statement**: Under N≥30 open-weight LLMs with MMLU as confirmed scale covariate (H-M1 passed), if pingouin.partial_corr(method='spearman', covar=['MMLU']) is applied to the TruthfulQA MC2 × BBQ accuracy pair, then the Fisher z difference test between raw_rho and partial_rho will yield p < 0.05 OR non-overlapping BCa 95% CIs (N_bootstrap=5000, clustered by model family), because MMLU scale variation (R²=0.32 confirmed) inflates raw cross-model correlations by co-driving all benchmark scores.

**Rationale**: This is the primary scientific claim. The Fisher z test operationalizes the question "does scale control *change* the correlation structure?" rather than merely describing it. Direction-agnostic design eliminates the failure pattern from 9 prior direction-specific hypotheses.

**Variables:**
- IV: Presence/absence of MMLU scale control (raw Spearman vs partial Spearman)
- DV: Fisher z difference (z_raw - z_partial) and two-tailed p-value; BCa CI overlap status
- CV: Model family clustering (BCa bootstrap); open-weight filter; N_bootstrap=5000

**Verification Protocol:**
1. Compute partial_rho = pg.partial_corr(df, x='TruthfulQA_MC2', y='BBQ_accuracy', covar=['MMLU'], method='spearman')['r'][0]
2. Compute Fisher z: z_diff = (arctanh(raw_rho) - arctanh(partial_rho)) / sqrt(2/(N-3)); p_value = 2*(1-norm.cdf(abs(z_diff)))
3. BCa bootstrap CI (N_bootstrap=5000, clustered by model family) for both raw_rho and partial_rho
4. Family-weighted Fisher z as robustness check (handles Llama-family dominance)
5. Report: p_value, raw_rho ± CI, partial_rho ± CI, CI overlap status; assign to SIGNIFICANT or NULL outcome

**Success Criteria:**
- Primary: p < 0.05 OR non-overlapping BCa 95% CIs (MUST_WORK gate — either direction confirms scale confound)
- Secondary: Family-weighted Fisher z consistent with primary result

**Failure Response:**
- IF p ≥ 0.05 AND overlapping CIs: H0 supported — MMLU does not confound alignment co-movement; this is publishable as "alignment benchmark co-movement is scale-independent"; MUST_WORK gate satisfied (result obtained, not gate failed)

**Dependencies**: H-E1 (N≥30), H-M1 (MMLU R² confirmed)

**Source**: Phase 2A Section 1.3 Causal Step 2; Section 1.6 P1 (primary prediction)

---

**H-M3: Dimensional Characterization of Scale-Free Alignment Structure**

**Statement**: Under the partial Spearman residuals from H-M2, the partial_rho value for TruthfulQA MC2 × BBQ accuracy will be assignable to one of three pre-specified scenarios: (a) |partial_rho| < 0.20 (independent constructs), (b) partial_rho > 0.40 (scale-free coherence), or (c) partial_rho < -0.20 (scale-masked tradeoff), because these three outcomes exhaustively characterize the possible dimensional relationships between factuality and bias in the alignment-specific benchmark space.

**Rationale**: Each of the three scenarios produces a distinct publishable narrative about alignment construct dimensionality. Scenario (a) supports the "multi-dimensional alignment" framing; (b) supports "coherent alignment signal"; (c) reveals a hidden tradeoff masked by scale. Tier 2 (HarmBench) extends this to the safety dimension if N≥20.

**Variables:**
- IV: partial_rho output from H-M2 (scale-free correlation)
- DV: Scenario assignment (a/b/c) based on partial_rho magnitude and sign; BCa CI range
- CV: Tier 2 (HarmBench, N≥20) as extension; Tier 3 (ΔBBQ sign test, OPTIONAL)

**Verification Protocol:**
1. Use partial_rho and BCa CI from H-M2; assign to scenario (a), (b), or (c)
2. If CI overlaps 0 AND overlaps 0.40: report "underpowered — scenario ambiguous" (not a gate failure)
3. Tier 2 (if N_harmbench ≥ 20): repeat partial Spearman for TruthfulQA×HarmBench and BBQ×HarmBench pairs; assign each to a/b/c
4. Tier 3 (OPTIONAL): sign test for ΔBBQ (chat-base) on 321 pairs from h-m1 dataset; scipy.stats.binomtest
5. Write summary table: all computed pairs × scenario assignment × CI

**Success Criteria:**
- Primary: partial_rho (TruthfulQA×BBQ) assigned to scenario with non-ambiguous BCa CI (SHOULD_WORK)
- Secondary: Tier 2 pairs characterized if N≥20; Tier 3 RLHF effect direction reported if significant

**Failure Response:**
- IF CI ambiguous (overlaps both 0 and 0.40): report "N insufficient for scenario characterization"; SHOULD_WORK gate — does not block Phase 4.5

**Dependencies**: H-M2 (partial_rho computed)

**Source**: Phase 2A Section 1.3 Causal Step 3; Section 1.6 P2, P3; Section 1.2 DV list

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | N ≥ 30 complete rows after fuzzy join | STOP; try HELM Lite fallback; if still <30 report data availability finding |
| H-M1 | MUST_WORK | MMLU R² > 0.05 for both TruthfulQA AND BBQ in joint dataset | Document MMLU orthogonality (publishable null); skip H-M2 Fisher z |
| H-M2 | MUST_WORK | Fisher z result obtained (p computed, regardless of direction) | Gate fails only if execution error; publishable in all outcome directions |
| H-M3 | SHOULD_WORK | Scenario (a/b/c) assigned with non-ambiguous CI | Report "underpowered" if ambiguous; does not block pipeline |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3 | 3 weeks (1 each after first) |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Risk Identification (from Assumptions A1-A5)

**Risk R1: MMLU not valid scale proxy in joint dataset**

**Source Assumption:** A1 — MMLU valid for AlpacaEval-LC (R²=0.32) but may differ for BBQ population.

**Description:** If MMLU R²(TruthfulQA) or MMLU R²(BBQ) ≤ 0.05 in joint dataset, partial Spearman controlling MMLU is methodologically invalid. Raw and partial rho would be identical regardless of true structure.

**Affected Hypotheses:** H-M1, H-M2 (primary analysis invalidated)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Execute R² check in H-M1 as mandatory pre-flight gate before any partial Spearman code runs
2. **Detection:** If MMLU R²(alignment benchmark) < 0.05, flag immediately in Step 1 output
3. **Response:** Document as "MMLU orthogonal to alignment benchmarks in joint dataset" — this is a publishable finding. Report raw correlation structure only. PIVOT to characterizing raw pairwise correlations without partial control.

**Early Warning Indicators:** MMLU × TruthfulQA Spearman rho < 0.22 (R² < 0.05)

---

**Risk R2: Insufficient N after fuzzy join (A2+A3 combined)**

**Source Assumption:** A2 (join compatibility) + A3 (N≥30 achievable)

**Description:** lighteval/bbq_helm may use model name formats that reduce match_rate below 0.55, yielding N < 30 after join. This would trigger H-E1 MUST_WORK gate failure.

**Affected Hypotheses:** H-E1 (MUST_WORK), all downstream hypotheses (CASCADE if H-E1 fails)

**Severity:** Critical

**Mitigation Strategy:**
1. **Prevention:** Use rapidfuzz WRatio + token_set_ratio fallback; test at multiple thresholds (65, 70, 75, 80)
2. **Detection:** Report match_rate immediately after join; target ≥ 0.55
3. **Response (FALLBACK CHAIN):** (a) Lower threshold to 70; (b) Try HELM Lite v1.9.0 (79 models) as alternative BBQ source; (c) If still N < 30, report data availability finding and route to Phase 0

**Early Warning Indicators:** match_rate < 0.40 at threshold=75 → try threshold=65 or alternate BBQ source immediately

---

**Risk R3: Llama-family dominance biases Fisher z test (A4)**

**Source Assumption:** A4 — Model family labels extractable; prior run found 39 families with Llama dominance.

**Description:** Llama-2 family models (~10-15 models sharing architecture) may violate the independence assumption of standard Fisher z test, inflating effective N and producing spuriously significant p-values.

**Affected Hypotheses:** H-M2 (Fisher z result validity), H-M3 (CI calibration)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** BCa bootstrap CI clustered by model family (N_bootstrap=5000) as primary CI method
2. **Detection:** Compare clustered vs non-clustered CI widths; if clustered CI is >2x wider, Llama clustering is material
3. **Response:** Family-weighted Fisher z as primary robustness check; report both clustered and non-clustered results

**Early Warning Indicators:** Llama-family proportion > 30% of N in joint dataset

---

**Risk R4: HarmBench Tier 2 insufficient N (A5)**

**Source Assumption:** A5 — HarmBench Table 2 (33 models) may not match LLM LB v1.

**Description:** h-e1 found only 7/21 matched (33%). Even with Table 2 hardcoded fallback, N_harmbench may be < 20, rendering Tier 2 (partial Spearman with safety dimension) underpowered.

**Affected Hypotheses:** H-M3 Tier 2 (HarmBench pairs characterization)

**Severity:** Medium (SHOULD_WORK only — does not block Tier 1 finding)

**Mitigation Strategy:**
1. **Prevention:** Use hardcoded Table 2 (33 models) instead of live infrastructure (lesson from h-e2)
2. **Detection:** Count N_harmbench matches after joining HarmBench model names to Tier 1 dataset
3. **Response:** If N_harmbench < 20, report Tier 2 as "underpowered — data unavailable" and complete study with Tier 1 only

**Early Warning Indicators:** N_harmbench < 20 after hardcoded join

---

**Risk R5: URL access failure blocking data download**

**Source Assumption:** General infrastructure risk (lesson from h-e2 HarmBench inaccessibility)

**Description:** GitHub raw URL for LLM LB v1 CSV or HuggingFace API for bbq_helm may be inaccessible at execution time.

**Affected Hypotheses:** H-E1 (blocks all downstream)

**Severity:** Critical (blocks pipeline entirely)

**Mitigation Strategy:**
1. **Prevention:** Execute requests.head() URL test FIRST before any computation code runs
2. **Detection:** Non-200 HTTP status code for any required URL
3. **Response:** For LLM LB v1 — try GitHub API alternative or clone repo; for bbq_helm — try HELM Lite v1.9.0 on HuggingFace; document any URL failure in report

**Early Warning Indicators:** requests.head() returns non-200 status

---

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: MMLU not valid covariate | A1 | H-M1, H-M2 | High |
| R2: N < 30 after join | A2+A3 | H-E1 (→ CASCADE) | Critical |
| R3: Llama clustering bias | A4 | H-M2, H-M3 | Medium |
| R4: HarmBench N < 20 | A5 | H-M3 Tier 2 | Medium |
| R5: URL access failure | Infrastructure | H-E1 (→ CASCADE) | Critical |

**Risk Summary:**
- Critical: 2 (R2, R5)
- High: 1 (R1)
- Medium: 2 (R3, R4)
- Low: 0

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 — Root]
    H-E1 (EXISTENCE — no dependencies)
    GATE: MUST_WORK → N≥30
         │
         ▼
[Level 1 — Mechanism: Scale Confound]
    H-M1 ← H-E1
    GATE: MUST_WORK → MMLU R²>0.05
         │
         ▼
[Level 2 — Mechanism: Fisher Z Test]
    H-M2 ← H-M1
    GATE: MUST_WORK → Fisher z result obtained
         │
         ▼
[Level 3 — Mechanism: Dimensional Characterization]
    H-M3 ← H-M2
    GATE: SHOULD_WORK → Scenario assigned

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | MUST_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2     │ W3-4     │ W5       │ W6-7
─────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 1: Foundation
  H-E1           │ ████████ │          │          │
  [Gate 1]       │       ◆  │          │          │
─────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 2: Core Mechanisms
  H-M1           │          │ ████████ │          │
  H-M2           │          │          │ ████     │
  H-M3           │          │          │          │ ████████
  [Gate 2]       │          │       ◆  │          │
─────────────────┼──────────┼──────────┼──────────┼──────────
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
  Formula: 2 (H-E1) + 1 (H-M1) + 1 (H-M2) + 1 (H-M3)
Slack Available: 0 weeks (all sequential)
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
- Condition: 0

Verification Phases: 2
1. Foundation (H-E1) — 2 weeks
2. Mechanisms (H-M1, H-M2, H-M3) — 3 weeks

Total Duration: 5 weeks
Critical Path Length: 5 weeks
Execution Mode: Sequential chain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
Step 2: Evaluate Gate 1 → N≥30? If YES proceed; if NO attempt fallbacks, then STOP
Step 3: Execute H-M1 (Scale confound R² pre-flight) — Week 3-4
Step 4: Evaluate Gate 2 → MMLU R²>0.05? If NO document null; if YES proceed to H-M2
Step 5: Execute H-M2 (Partial Spearman + Fisher z) — Week 5
Step 6: Execute H-M3 (Dimensional characterization + Tier 2+3) — Week 6-7
Step 7: Evaluate Gate 3 (SHOULD_WORK) → Scenario assigned or report underpowered
Final: Verification complete → Phase 4.5 Synthesis
```

---

## 6. Dialectical Analysis

### 6.1 Thesis Statement

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: MMLU scale variation confounds raw cross-model correlations
between alignment benchmarks (TruthfulQA, BBQ, HarmBench), and partial
Spearman with Fisher z difference test will reveal this confounding.

Supporting Evidence:
1. MMLU R²=0.32 confirmed vs AlpacaEval-LC (h-e1 snapshot) — scale drives benchmarks
2. raw rho(AlpacaEval-LC, TruthfulQA) = +0.661 (sh2-corr) — inflated raw correlation
3. clawrxiv:2603.00394 PC2 = TruthfulQA orthogonal (23.4% variance) — partial structure exists

Strengths:
- Direction-agnostic design: any of 3 partial_rho outcomes (a/b/c) is publishable
- Fisher z difference test is inferential (not just descriptive) — more precise than prior work
- Tiered design: Tier 1 result publishable even if HarmBench Tier 2 fails

Expected Outcomes:
- Primary: Fisher z test significant (p<0.05) OR non-overlapping BCa CIs
- Secondary: partial_rho assigned to scenario (a), (b), or (c)
- Tertiary (optional): RLHF ΔBBQ sign test result
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis Development (H0-Based)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): Raw Spearman rho = Partial Spearman rho for
TruthfulQA × BBQ (Fisher z difference NOT significant, p ≥ 0.05).
MMLU scale control does not change alignment benchmark correlation structure.

Counter-Arguments:
1. A1 violation risk: MMLU R² for AlpacaEval-LC does not imply R² for
   BBQ (different benchmark type — helpfulness vs. social bias)
2. A3 risk: actual N after join may be insufficient for reliable
   Fisher z or BCa CI, producing wide CIs that overlap
3. BenchScope ED=1.7 suggests ~2 axes, which could mean alignment benchmarks
   ARE somewhat co-moving even after scale control (antithesis scenario b)

Potential Failure Points:
- H-E1 fails (N<30): entire pipeline blocked by data unavailability
- H-M1 fails (MMLU R²≤0.05): MMLU orthogonal to BBQ — no confound to detect
- H-M2 Fisher z not significant AND CIs overlap: scale does not confound
  alignment benchmark co-movement (H0 supported — still publishable)

Conditions Under Which H0 Would Be Supported:
- p ≥ 0.05 AND BCa CIs overlap for raw vs partial rho (TruthfulQA × BBQ)
- MMLU R²(BBQ) ≤ 0.05 in joint dataset (A1 violated)
- N < 30 after all fallback attempts (data availability failure)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:
H-M1-V2 presents a direction-agnostic, inferential claim that MMLU
confounds alignment benchmark correlations. The antithesis raises valid
concerns about MMLU's validity as a scale proxy specifically for BBQ
(social bias) and about achievable N after fuzzy join. The tiered
design resolves this tension: Tier 1 (TruthfulQA×BBQ) is the primary
gate, and ALL outcomes (reject/fail-to-reject H0) produce publishable
findings about alignment benchmark dimensionality.

Resolution Path:
1. Foundation (H-E1): Establishes data viability before any claim made
2. Pre-flight R² check (H-M1): Validates MMLU covariate assumption in
   the specific joint dataset — prevents methodologically invalid analysis
3. Fisher z test (H-M2): Inferential gate that resolves thesis/antithesis
   with specific p-value and CI evidence
4. Scenario assignment (H-M3): Converts binary test outcome into
   interpretable finding about alignment construct dimensionality

Conditions for Thesis Support:
- H-E1 PASS (N≥30) + H-M1 PASS (MMLU R²>0.05) + H-M2 PASS (p<0.05 or non-overlapping CIs)

Conditions for Antithesis Support:
- H-M2: p ≥ 0.05 AND overlapping CIs → "scale does not confound alignment co-movement"
- OR H-M1: MMLU R² ≤ 0.05 → "MMLU orthogonal to alignment benchmarks"

Nuanced Outcome Possibilities:
1. Full Support: p<0.05, partial_rho distinct from raw — MMLU confounds confirmed
2. H0 Supported (publishable): p≥0.05, alignment co-movement is scale-independent
3. Underpowered: CIs ambiguous — report N limitation, still publishable
4. Data failure: H-E1 fails — route to Phase 0

Overall Robustness: HIGH
- Direction-agnostic design eliminates prior failure pattern (9 direction-specific failures)
- Pre-specified scenarios (a/b/c) prevent post-hoc interpretation
- Tiered design (Tier 1/2/3) provides fallback publishability at each level
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | N≥30 achievable (LLM LB v1 × bbq_helm) | lighteval/bbq_helm model names may not match at threshold=75 | H-E1 explicit pre-flight gate + fallback chain |
| Scale Confound | MMLU R²>0.05 for alignment benchmarks | MMLU valid for helpfulness, may not extend to bias (BBQ) | H-M1 R² check in joint dataset before any analysis |
| Fisher Z | Scale control changes correlation structure | N insufficient for reliable Fisher z; CIs may overlap | BCa clustered bootstrap + family-weighted robustness check |
| Scope | 3 pre-specified scenarios cover all outcomes | CI ambiguity may leave scenario unassigned | "Underpowered" is a valid reportable outcome |
| Safety | HarmBench Tier 2 extends to safety dimension | N_harmbench < 20 (h-e1 found only 7/21 matches) | Tier 2 SHOULD_WORK only; Tier 1 publishable independently |

**Overall Robustness Score:** High

**Confidence in Verification Plan:** 0.80

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-M1-V2 — Partial Spearman structure of alignment benchmarks after MMLU scale control
- ID: H-M1-V2, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A data loaded; 71% scope reduction from BUILD_ON claims)
- Sub-Hypotheses: 4 total (H-E1, H-M1, H-M2, H-M3)
- Phases: 2 phases over 5 weeks
- Critical Gates: 3 decision points (Gate 1: N≥30, Gate 2: MMLU R²>0.05, Gate 3: SHOULD_WORK)

**Risk Assessment:** Critical risks on data availability (R2: N<30, R5: URL failure); mitigated by explicit pre-flight protocols and fallback chains.

**Immediate Action:** Begin Phase 1 with H-E1 pre-flight data audit (URL test → download → join → N count)

### 7.2 Conclusions

**Key Achievements:**
- 4 hypotheses across 2 phases
- H0 addressed: MMLU scale control does not change alignment co-movement (direction-agnostic)
- 71% scope reduction: 5 of 7 claims are BUILD_ON (prior validated)
- PROVE_NEW claims: pairwise partial Spearman matrix + Fisher z difference test

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: N≥30 complete rows (TruthfulQA MC2, BBQ accuracy, MMLU) after fuzzy join
- Gate 1: MUST PASS (N<30 → fallback chain → STOP if all fail)

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: MMLU R²>0.05 for TruthfulQA and BBQ in joint dataset (pre-flight scale confound check)
- H-M2: partial Spearman + Fisher z difference test (primary scientific claim)
- H-M3: dimensional characterization (scenario a/b/c assignment + Tier 2+3)
- Gate 2: H-M1 must pass (MMLU valid covariate); H-M2 result obtained regardless of direction

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 N≥30 gate
   - PASS → Proceed to Phase 2
   - FAIL → Try HELM Lite fallback; if N still <30 → STOP, report data availability finding

2. **Gate 2 (Scale Covariate):** H-M1 MMLU R² check
   - PASS → Proceed to Fisher z analysis (H-M2)
   - FAIL → Document "MMLU orthogonal to alignment benchmarks" (publishable null); skip H-M2

3. **Gate 3 (SHOULD_WORK):** H-M3 scenario assignment
   - Failures narrow scope but do not invalidate Tier 1 finding

**Open Questions:**
- What is actual N after TruthfulQA × BBQ × MMLU fuzzy join? (pre-flight required)
- Does MMLU R² also hold for BBQ in the joint dataset (not just AlpacaEval-LC)?
- Can HarmBench Table 2 (33 models) yield N≥20 matches to Tier 1 dataset?
- Do lighteval/bbq_helm model names use HuggingFace format matching LLM LB v1?

**Recommendations:**

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 pre-flight URL test and data audit
   - Test rapidfuzz join at multiple thresholds (65, 70, 75) before committing

2. **Resource Allocation:**
   - Allocate 5 weeks for critical path
   - Keep HELM Lite v1.9.0 as fallback BBQ source ready

3. **Failure Management:**
   - Document all URL and join failures with HTTP status codes
   - Execute family-weighted Fisher z as robustness check regardless of primary p-value

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: docs/youra_research/03_refinement.yaml (ID: H-M1-V2)
- Prior failures informing design: h-e1, h-e2, sh2-corr, sh-p1, h-m1 (9 failures in prior hypotheses)

**B. MCP Tool Usage Summary**
- Total MCP calls: 4 (scientificmethod × 4: H-E1 hypothesis+experiment, H-M1 hypothesis+experiment)
- Mode: Incremental (4-6 call budget)

**C. Scope Reduction Detail**
- Total claims: 7 (5 BUILD_ON + 2 PROVE_NEW)
- Scope reduction: 71% — only PROVE_NEW claims require experimental evidence

---
