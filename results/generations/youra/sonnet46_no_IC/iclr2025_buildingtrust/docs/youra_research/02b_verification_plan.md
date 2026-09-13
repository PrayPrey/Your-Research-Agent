---
hypothesis_id: H-CDTCS-v1
workflow: phase2b-planning
created_at: "2026-08-04"
research_mode: incremental
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
status: complete
completedAt: "2026-08-04T00:00:00Z"
---

# Verification Plan: Cross-Dimension Trustworthiness Correlation Structure (CDTCS)

**Date:** 2026-08-04
**Hypothesis ID:** H-CDTCS-v1
**Confidence:** 0.78
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the setting of existing LLM evaluation frameworks (TrustLLM 16-model × 6-dimension
scores, HELM 30-model × 7-metric scores, and Pythia-family benchmark evaluations via
lm-eval-harness), if we compute partial Spearman rank correlation matrices across
trustworthiness dimensions controlling for model scale (log parameter count) and alignment
status (RLHF fine-tuning yes/no), then we will observe a 2-cluster correlation structure
separating RLHF-sensitive dimensions (safety, ethics) from RLHF-insensitive dimensions
(adversarial robustness, calibration/privacy), with a derivable minimum spanning evaluation
set of ≤4 dimensions and replication of key cluster signs in HELM data, because RLHF
optimization creates a systematic split in how trustworthiness dimensions respond to
preference-based training: safety and ethics dimensions are directly optimized by RLHF
reward signals (making them co-move), while adversarial robustness and calibration are
orthogonal to human preference signals.

### 1.2 Alternative Hypothesis (H0)

There is no significant correlation structure (all |ρ_partial| < 0.3 across all 15 pairwise
combinations of 6 TrustLLM dimensions after controlling for model scale and alignment status);
trustworthiness dimensions are statistically independent and no 2-cluster structure exists
(silhouette score < 0.3 for all k≥2 clustering solutions).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TrustLLM Published Score Tables (standard) | Provides the exact 16-model × 6-dimension score matrix needed for the primary correlation analysis. Scores are pre-computed and publicly available, satisfying the existing-data constraint. |
| **Model** | TrustLLM 16-model evaluation set + Pythia scaling series expansion | TrustLLM 16 models provide the primary correlation analysis. Pythia 8-checkpoint series provides a controlled scale experiment where RLHF=False and only scale varies, enabling clean separation of scale effects from alignment effects. |

**Dataset Details:**
- Source: https://github.com/HowieHwong/TrustLLM (results/ folder)
- Path: HowieHwong/TrustLLM repository / results/*.json

**Model Details:**
- Type: convenience sample + controlled natural experiment
- Source: TrustLLM: 16 models from published evaluation; Pythia: EleutherAI/pythia-70m through pythia-12b via HuggingFace

### 1.4 Baseline Methods (for comparison context)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Raw (uncontrolled) Spearman correlation | Expected mostly positive correlations due to scale confound | TrustLLM 16-model scores |
| HELM holistic evaluation | 7-metric × 30-model; qualitative tradeoff detection via radar charts only | HELM leaderboard |
| Capability benchmark correlation (Epoch AI) | Median ρ=0.73 across 17 capability benchmarks | General capability benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | TrustLLM GitHub publishes per-model per-dimension scores in results/*.json with sufficient granularity (not just aggregate rankings) | HowieHwong/TrustLLM GitHub results/ folder with per-model JSON files (Exchange 14) | Must re-run lm-eval-harness on same 16 models — significant engineering work but feasible |
| A2 | 16 TrustLLM models span sufficient variation in scale and RLHF alignment for partial correlation estimation | LLaMA-2 7B/13B/70B base+chat, Mistral-7B, Falcon-7B, GPT-3.5/4, Claude-2, Vicuna — spanning ~7B to ~175B+ (Exchange 8) | Partial correlation estimates unreliable; Pythia expansion partially mitigates via scale range coverage |
| A3 | RLHF alignment status (binary: RLHF vs base) is sufficient covariate; DPO/SFT treated as aligned | TrustLLM model set primarily uses RLHF or base; DPO was less prevalent in 2024 (Exchange 9) | DPO models could introduce noise; sensitivity analysis: rerun with DPO models excluded |
| A4 | Same construct (e.g., 'safety') measured differently in TrustLLM vs HELM is sufficiently correlated for cross-framework replication | Both measure harmful output avoidance; construct overlap substantial (Prof. Pax, Exchange 4) | HELM replication finds no structure → qualify as TrustLLM-operationalization-specific; negative replication is itself contribution |
| A5 | Spearman rank correlation is appropriate for bounded [0,1] dimension scores | Standard in benchmark correlation literature; Spearman robust to outliers and non-normality (Exchange 2) | Report both Spearman and Pearson, note divergence |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First systematic cross-dimension partial Spearman correlation analysis for LLM trustworthiness; RLHF-cluster organizing principle for trustworthiness correlation structure; MST-derived minimum sufficient evaluation set.

**Key Innovation:** Reframes trustworthiness evaluation from "measure all 6 dimensions independently" to "measure the minimum spanning set derived from correlation geometry" — prescriptive output with immediate practical value for deployment evaluation.

**Gap:** Liu et al. [2023] (575 citations) explicitly identifies cross-dimension correlation analysis as future work. TrustLLM [Sun et al., 2024] and HELM [Liang et al., 2022] both note qualitative tradeoffs but publish neither Spearman correlation matrices nor partial correlations controlling for confounds. This paper fills all three gaps simultaneously.

**Established Facts (BUILD_ON — NOT re-verified):**
1. LLM trustworthiness dimensions can be independently measured using existing benchmarks [TrustLLM, Sun et al., 2024]
2. Safety-RLHF creates safety-robustness trade-off within model families [LLaMA-2-Chat vs LLaMA-2-base, TrustLLM]
3. General capability benchmarks are highly correlated (median Spearman ρ=0.73, Epoch AI)

**Scope Reduction: 43%** — 3 of 6 claims are BUILD_ON (established). Only 3 PROVE_NEW claims require verification.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Gate | Prerequisites | Status |
|----|------|-------------------|------|---------------|--------|
| H-E1 | EXISTENCE | 2-cluster partial Spearman correlation structure exists in TrustLLM 16-model data | MUST_WORK | None | READY |
| H-E2 | EXISTENCE | MST-derived minimum evaluation set of ≤4 dimensions is stable (≥90% bootstrap stability) | MUST_WORK | H-E1 | NOT_STARTED |
| H-M1 | MECHANISM | RLHF directly co-optimizes safety and ethics (safety-ethics positive partial ρ) | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | RLHF-induced representation rigidity reduces adversarial robustness (safety-robustness negative partial ρ) | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | Combined RLHF effects produce 2-cluster structure with correct cluster membership alignment | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Trustworthiness Correlation Structure Existence**

**Statement:** Under the TrustLLM 16-model × 6-dimension evaluation setting, if we compute partial Spearman rank correlations for all 15 dimension pairs controlling for log(param_count) and RLHF status, then at least one correlation will be statistically significant (|ρ_partial| > 0.5, p < 0.0033 Bonferroni-corrected), because LLM trustworthiness dimensions are not statistically independent — RLHF optimization systematically co-moves related dimensions.

**Rationale:** This is the foundation hypothesis testing whether any correlation structure exists at all. It directly verifies PROVE_NEW claim 2 (2-cluster RLHF-driven structure). Without passing H-E1, no mechanism testing makes sense.

**Variables:**
- Independent: Trustworthiness dimension pair (15 combinations of 6 dimensions)
- Dependent: Partial Spearman ρ_partial (after OLS residualization on [log_params, is_RLHF])
- Controlled: Benchmark operationalization (TrustLLM fixed), model population (16-model set)

**Verification Protocol:**
1. Download HowieHwong/TrustLLM results/*.json and extract per-model per-dimension scores into 16×6 matrix
2. Annotate each model with log10(param_count) and is_RLHF binary flag
3. For each of 15 dimension pairs: OLS-residualize both dimensions on [log_params, is_RLHF], compute Spearman ρ on residuals, test H0: ρ=0 using t-distribution (df=13)
4. Apply Bonferroni correction (α=0.0033 for 15 tests); flag significant pairs
5. Perform Ward hierarchical clustering on 6×6 ρ_partial matrix; compute silhouette score for k=2

**Success Criteria (PoC):**
- Primary: At least 1 of 15 |ρ_partial| > 0.5 AND p < 0.0033
- Secondary: Silhouette score > 0.3 for k=2 hierarchical solution

**Failure Response:**
- IF primary fails: PIVOT — investigate whether score files have sufficient granularity (A1 check); run lm-eval-harness as fallback

**Dependencies:** None (foundation)

**Source:** Phase 2A PROVE_NEW claim 2, predictions P1-P3

---

**H-E2: MST Minimum Evaluation Set Existence**

**Statement:** Under the TrustLLM 16-model evaluation setting, if we construct the minimum spanning tree (MST) of the partial Spearman distance matrix (1-|ρ_partial|), then the MST will identify a minimum sufficient evaluation set of ≤4 dimensions with ≥90% bootstrap topology stability (1000 resamples of 14/16 models), because the correlation structure is strong enough to make some dimensions redundant for evaluation purposes.

**Rationale:** This directly verifies PROVE_NEW claim 3 (MST minimum evaluation set). It upgrades the descriptive correlation contribution to a prescriptive, actionable output — the key innovation of the paper. Bootstrap stability validates that the minimum set is not an artifact of the specific 16-model sample.

**Variables:**
- Independent: Dimension inclusion/exclusion in MST
- Dependent: MST-derived minimum evaluation set size (integer ∈ {1,2,3,4,5,6}); bootstrap topology stability (proportion [0,1])
- Controlled: Distance metric (1-|ρ_partial|); bootstrap sample size (14/16 models)

**Verification Protocol:**
1. Use ρ_partial matrix from H-E1; construct complete graph with edge weights (1-|ρ_partial|)
2. Apply networkx.minimum_spanning_tree (Kruskal's algorithm) to identify minimum spanning tree
3. Identify the minimum sufficient evaluation set: dimensions reachable from MST structure
4. Bootstrap 1000 times (resample 14 of 16 models): recompute ρ_partial → MST → topology; record edge set each time
5. Compute topology stability = proportion of bootstrap samples with identical edge set to full-sample MST

**Success Criteria (PoC):**
- Primary: MST minimum set ≤4 dimensions
- Secondary: Bootstrap topology stability ≥0.90

**Failure Response:**
- IF minimum set = 6 (no redundancy): EXPLORE — report full correlation structure as null result; publishable finding of dimension independence
- IF stability < 0.70: EXPLORE — report MST as sample-specific; increase n via Pythia expansion

**Dependencies:** H-E1 (requires ρ_partial matrix)

**Source:** Phase 2A PROVE_NEW claim 3, prediction P4

---

**H-M1: RLHF Directly Co-Optimizes Safety and Ethics**

**Statement:** Under the TrustLLM 16-model setting with partial Spearman controls, if RLHF fine-tuning directly rewards safe and ethics-aligned outputs via preference learning, then RLHF Chat/Instruct models will outscore size-matched base models on BOTH safety AND ethics simultaneously, and ρ_partial(safety, ethics) > 0.5 (p < 0.0033), because RLHF reward signals penalize harmful outputs and reward value-aligned responses — jointly optimizing both safety and ethics dimensions.

**Rationale:** Step 1 of the 3-step RLHF causal chain. Tests whether RLHF actually co-moves safety and ethics, providing the mechanistic grounding for the positive cluster correlation. Uses LLaMA-2 family (6 within-family pairs across 3 scales) as natural experiment.

**Variables:**
- Independent: RLHF alignment status (RLHF-tuned Chat vs base, within-family)
- Dependent: ρ_partial(safety, ethics); within-family safety and ethics score difference
- Controlled: Model scale (within-family comparison controls architecture and pretraining)

**Verification Protocol:**
1. Extract LLaMA-2 7B, 13B, 70B base and Chat variant scores from TrustLLM JSON
2. Compute within-family signed differences: Δ_safety = Chat_safety - Base_safety; Δ_ethics = Chat_ethics - Base_ethics for each scale
3. Test sign: all 3 Δ_safety > 0 AND all 3 Δ_ethics > 0 (both improve with RLHF)
4. Verify ρ_partial(safety, ethics) > 0.5 from H-E1 correlation matrix
5. HELM replication: compute same correlation on HELM subset to test construct robustness

**Success Criteria (PoC):**
- Primary: ρ_partial(safety, ethics) > 0.5 AND p < 0.0033
- Secondary: ≥2/3 within-family pairs show Δ_safety > 0 AND Δ_ethics > 0 simultaneously

**Failure Response:**
- IF fails: PIVOT — investigate whether RLHF binary classification is correct (DPO/SFT mis-labeling); consult TrustLLM paper for model training details

**Dependencies:** H-E1 (ρ_partial matrix)

**Source:** Phase 2A causal step 1, prediction P1

---

**H-M2: RLHF Representation Rigidity Reduces Adversarial Robustness**

**Statement:** Under the TrustLLM 16-model setting, if RLHF-induced conservative refusal patterns create representation-level rigidity that is brittle to adversarial perturbations, then ρ_partial(safety, robustness) < -0.4 (p < 0.0033), and RLHF Chat variants should score EQUAL OR LOWER on adversarial robustness compared to size-matched base models, because the same pattern-matching representations that avoid harmful outputs via conservative prediction are brittle to adversarial input perturbations.

**Rationale:** Step 2 of the RLHF causal chain. Tests the safety-robustness anti-correlation that produces the negative cross-cluster partial ρ. Grounded in AQUA-LLM accuracy-robustness tradeoff and Know Thy Judge safety judge brittleness evidence. The negative sign is the mechanistic signature of RLHF's dual effect.

**Variables:**
- Independent: RLHF alignment status (Chat vs base within-family)
- Dependent: ρ_partial(safety, robustness); Δ_robustness = Chat_robustness - Base_robustness within-family
- Controlled: Model scale (within-family comparison), benchmark operationalization

**Verification Protocol:**
1. Extract adversarial robustness dimension scores for all 16 models from TrustLLM JSON
2. Compute Δ_robustness for LLaMA-2 family (3 within-family pairs)
3. Test sign: Δ_robustness ≤ 0 in ≥2/3 pairs (RLHF does not improve robustness)
4. Verify ρ_partial(safety, robustness) < -0.4 from H-E1 correlation matrix
5. Pythia baseline: within-Pythia ρ(safety, robustness) should be near zero (RLHF=False, scale only)

**Success Criteria (PoC):**
- Primary: ρ_partial(safety, robustness) < -0.4 AND p < 0.0033
- Secondary: ≥2/3 LLaMA-2 within-family Δ_robustness ≤ 0

**Failure Response:**
- IF primary fails (ρ_partial > 0): EXPLORE — this would reject the RLHF mechanism; report as finding that safety and robustness are positively correlated
- IF Pythia shows same structure: EXPLORE — structure may be scale-driven, not RLHF-driven

**Dependencies:** H-M1 (establishes positive RLHF cluster; H-M2 establishes negative cross-cluster link)

**Source:** Phase 2A causal step 2, prediction P2

---

**H-M3: 2-Cluster Correlation Structure with Correct Cluster Membership**

**Statement:** Under the TrustLLM 16-model setting, if the RLHF-driven co-movement of safety+ethics (positive ρ) combines with the safety-robustness anti-correlation (negative ρ) from Steps 1+2, then hierarchical clustering (Ward linkage) of the 6×6 ρ_partial matrix will produce a 2-cluster solution with silhouette score > 0.3 AND cluster membership matching the predicted RLHF-sensitive {safety, ethics} vs RLHF-insensitive {adversarial robustness, calibration/privacy} grouping in ≥4/6 dimensions.

**Rationale:** Step 3 of the RLHF causal chain — the observable structural prediction that emerges from Steps 1+2. This is the primary testable claim (PROVE_NEW claim 2). The specific cluster membership prediction (which dimensions belong to which cluster) is the strongest test: it must be made BEFORE data analysis and must match in ≥4/6 dimensions to count as confirmation.

**Variables:**
- Independent: Dimension membership in RLHF-sensitive vs RLHF-insensitive cluster (pre-specified prediction)
- Dependent: Silhouette score for k=2 Ward clustering; cluster membership alignment score (matched/6 dimensions)
- Controlled: Clustering algorithm (Ward linkage fixed), distance metric (ρ_partial matrix)

**Verification Protocol:**
1. Apply sklearn AgglomerativeClustering (ward linkage) to 6×6 ρ_partial matrix for k=2
2. Compute silhouette_score for k=2 solution
3. Map cluster labels to dimension names; compare to predicted {safety,ethics} vs {robustness,calibration/privacy}
4. Count membership alignment: predicted dimension in correct cluster / 6 total dimensions
5. HELM replication: repeat clustering on HELM equivalent partial correlation matrix; check if same 2-cluster sign pattern emerges

**Success Criteria (PoC):**
- Primary: Silhouette score > 0.3 for k=2 AND ≥4/6 dimensions in predicted clusters
- Secondary: HELM replication shows same sign pattern for P1 (safety-ethics positive) and P2 (safety-robustness negative)

**Failure Response:**
- IF silhouette < 0.3: EXPLORE — report correlation structure without cluster interpretation; investigate k≠2 alternatives
- IF cluster membership misaligns (< 4/6): EXPLORE — report actual cluster membership; check whether truthfulness or fairness swap clusters

**Dependencies:** H-M1 + H-M2 (both mechanism steps must be established before Step 3 makes sense)

**Source:** Phase 2A causal step 3, prediction P3

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-E2
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ≥1 |ρ_partial|>0.5, p<0.0033 | STOP — reassess data availability (A1 check); PIVOT to lm-eval-harness |
| H-E2 | MUST_WORK | MST set ≤4 dims AND stability ≥0.90 | EXPLORE — report full structure; increase n via Pythia |
| H-M1 | MUST_WORK | ρ_partial(safety,ethics)>0.5, p<0.0033 | PIVOT — check RLHF classification; DPO labeling |
| H-M2 | SHOULD_WORK | ρ_partial(safety,robustness)<-0.4, p<0.0033 | EXPLORE — report positive correlation as null finding |
| H-M3 | SHOULD_WORK | Silhouette>0.3 AND ≥4/6 cluster alignment | EXPLORE — report without cluster interpretation |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Existence Extension | H-E2 | 1 week |
| Phase 3: Core Mechanisms | H-M1, H-M2, H-M3 | 3 weeks |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1 (from A1): Data Granularity Unavailability**
- **Source Assumption:** A1 — TrustLLM publishes per-model per-dimension scores in results/*.json
- **Description:** Published JSON files may contain only aggregate rankings, not per-model per-dimension continuous scores needed for Spearman correlation
- **Affected Hypotheses:** H-E1, H-E2, H-M1, H-M2, H-M3 (ALL hypotheses blocked if A1 fails)
- **Severity:** Critical
- **Mitigation Strategy:**
  1. Prevention: Verify data format FIRST before any other steps (one-time check taking <1 hour)
  2. Detection: Load one model JSON and check for per-dimension float scores vs rank integers
  3. Response: If unavailable → PIVOT to lm-eval-harness re-evaluation of same 16 models (24-48 GPU hours)
- **Early Warning:** JSON files contain only integer rankings or aggregate scores

**Risk R2 (from A2): Insufficient Model Variation for Partial Correlation**
- **Source Assumption:** A2 — 16 models span sufficient scale/alignment variation
- **Description:** Partial correlation estimation may be unreliable if model population lacks sufficient diversity in scale range or RLHF ratio
- **Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3 (correlation estimates unreliable)
- **Severity:** High
- **Mitigation Strategy:**
  1. Prevention: Verify that TrustLLM 16-model set includes ≥4 RLHF models and ≥4 base models spanning at least 2 orders of magnitude in parameter count
  2. Detection: Check condition number of [log_params, is_RLHF] design matrix — high collinearity signals problem
  3. Response: If multicollinearity → add Pythia expansion (8 base-only checkpoints) to increase n and scale coverage
- **Early Warning:** VIF > 5 for either covariate in the partial correlation OLS step

**Risk R3 (from A3): DPO/SFT Misclassification**
- **Source Assumption:** A3 — RLHF binary covariate is sufficient; DPO/SFT treated as aligned
- **Description:** If DPO models (e.g., Vicuna trained on GPT-4 data via distillation) are mis-classified as RLHF, the binary covariate introduces noise
- **Affected Hypotheses:** H-M1, H-M2, H-M3 (mechanism tests rely on RLHF binary)
- **Severity:** Medium
- **Mitigation Strategy:**
  1. Prevention: Carefully audit each model's training procedure; create three-way classification (RLHF / DPO-SFT / base)
  2. Detection: Sensitivity analysis — rerun partial correlations with DPO-SFT excluded
  3. Response: If signs flip when DPO-SFT excluded → refine classification; report both analyses
- **Early Warning:** Results are unstable across RLHF binary vs three-way classification

**Risk R4 (from A4): Cross-Framework Construct Mismatch**
- **Source Assumption:** A4 — TrustLLM 'safety' and HELM 'toxicity' are sufficiently correlated for replication
- **Description:** HELM replication may find no structure because dimension operationalizations differ enough to capture different latent constructs
- **Affected Hypotheses:** H-M3 (HELM replication component), H-E1 (replication validation)
- **Severity:** Medium
- **Mitigation Strategy:**
  1. Prevention: Map TrustLLM dimensions to HELM metrics a priori; document construct overlap before analysis
  2. Detection: Check correlation between TrustLLM and HELM scores for models appearing in both
  3. Response: If replication fails → qualify finding as TrustLLM-operationalization-specific; negative replication is a secondary contribution
- **Early Warning:** <5 models overlap between TrustLLM and HELM evaluation sets

**Risk R5 (from A5): Spearman Inappropriate for Score Distribution**
- **Source Assumption:** A5 — Spearman rank correlation is appropriate for bounded [0,1] scores
- **Description:** If scores have extreme distributions (many zeros, ceiling effects), rank-based correlation may behave unexpectedly
- **Affected Hypotheses:** H-E1, H-E2, H-M1, H-M2, H-M3 (all correlation analyses)
- **Severity:** Low
- **Mitigation Strategy:**
  1. Prevention: Examine score distributions for each dimension before analysis; check for floor/ceiling effects
  2. Detection: Compare Spearman vs Pearson results; if signs diverge, investigate
  3. Response: Report both Spearman and Pearson results; use Pearson as sensitivity check
- **Early Warning:** Any dimension has >20% of models scoring at floor (0) or ceiling (1)

### 4.2 Risk Summary Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| ID | Risk                          | Source | Severity | Affected      | Mitigation           |
|----|-------------------------------|--------|----------|---------------|----------------------|
| R1 | Data granularity unavailable  | A1     | Critical | ALL           | Verify first; fallback lm-eval-harness |
| R2 | Insufficient model variation  | A2     | High     | H-E1, H-M*   | Pythia expansion     |
| R3 | DPO/SFT misclassification     | A3     | Medium   | H-M1-3       | Three-way audit + sensitivity analysis |
| R4 | Cross-framework construct gap | A4     | Medium   | H-M3, H-E1  | Pre-specify mapping; qualify finding   |
| R5 | Spearman distribution issues  | A5     | Low      | ALL           | Compare Spearman + Pearson            |

Critical Risks: 1 (R1)
High Risks: 1 (R2)
Medium Risks: 2 (R3, R4)
Low Risks: 1 (R5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence: 2-cluster structure — no dependencies)
         │
         ├─────────────────────────┐
         ▼                         ▼
[Level 1 - Existence Extension]  [Level 1 - First Mechanism]
    H-E2 ← H-E1                  H-M1 ← H-E1
    (MST minimum set)                  │
                                       ▼
                             [Level 2 - Second Mechanism]
                                  H-M2 ← H-M1
                                       │
                                       ▼
                             [Level 3 - Third Mechanism]
                                  H-M3 ← H-M2

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Secondary Path: H-E1 → H-E2
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Level | Hypothesis | Prerequisites | Gate Type    |
|-------|-----------|---------------|--------------|
| 0     | H-E1      | None          | MUST_WORK    |
| 1     | H-E2      | H-E1          | MUST_WORK    |
| 1     | H-M1      | H-E1          | MUST_WORK    |
| 2     | H-M2      | H-M1          | SHOULD_WORK  |
| 3     | H-M3      | H-M2          | SHOULD_WORK  |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase / Hypothesis  │ W1-2    │ W3     │ W4     │ W5     │ W6
────────────────────┼─────────┼────────┼────────┼────────┼────────
PHASE 1: Foundation
  H-E1             │ ████████│        │        │        │
  [Gate 1]         │       ◆ │        │        │        │
────────────────────┼─────────┼────────┼────────┼────────┼────────
PHASE 2: Existence Extension (parallel with Phase 3)
  H-E2             │         │ ████   │        │        │
  [Gate E2]        │         │     ◆  │        │        │
────────────────────┼─────────┼────────┼────────┼────────┼────────
PHASE 3: Core Mechanisms (sequential)
  H-M1             │         │ ████   │        │        │
  [Gate M1]        │         │     ◆  │        │        │
  H-M2             │         │        │ ████   │        │
  [Gate M2]        │         │        │     ◆  │        │
  H-M3             │         │        │        │ ████   │
  [Gate M3]        │         │        │        │     ◆  │
────────────────────┼─────────┼────────┼────────┼────────┼────────
HELM REPLICATION   │         │        │        │        │ ████
  [Final Gate]     │         │        │        │        │     ◆
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
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 (→ HELM replication)
Total Duration: 6 weeks
  Formula: 2 (H-E1) + 1 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (HELM)

Secondary Path: H-E1 → H-E2 (3 weeks total, completes before critical path)

Note: H-E2 and H-M1 can be executed in parallel (both depend only on H-E1).
This is an opportunity for parallelization: start H-E2 and H-M1 concurrently
after H-E1 passes, saving ~1 week on the secondary path.

Slack Available:
- H-E2 path: 3 weeks slack relative to critical path
- H-M2, H-M3: 0 slack (on critical path)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Hypotheses: 5
- Existence: 2 (H-E1, H-E2)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0 (not needed)

Verification Phases: 3
1. Foundation (H-E1): 2 weeks — pure statistical analysis, no GPU
2. Existence Extension (H-E2) + Mechanism Phase 1 (H-M1): 1 week — parallel, no GPU
3. Core Mechanisms (H-M2, H-M3): 2 weeks — no GPU (TrustLLM scores only)
4. HELM Replication + Pythia expansion: 1 week — 24-48 GPU hours for Pythia lm-eval-harness

Total Compute: ~24-48 GPU hours (Pythia only)
Primary Analysis: Zero new compute (TrustLLM + HELM published scores)
Critical Path: 6 weeks (5 weeks if H-E2 + H-M1 parallelized)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
  → Download TrustLLM scores, build 16×6 matrix
  → Compute all 15 partial Spearman correlations
  → Hierarchical clustering silhouette test

Step 2: Evaluate Gate 1 (MUST_WORK)
  → PASS: Proceed to Steps 3+4 in parallel
  → FAIL: PIVOT to lm-eval-harness data collection

Step 3 (parallel): Execute H-E2 (MST minimum set) — Week 3
  → Construct MST from ρ_partial distance matrix
  → Bootstrap 1000 resamples for topology stability

Step 4 (parallel): Execute H-M1 (RLHF co-optimizes safety+ethics) — Week 3
  → Within-family LLaMA-2 comparison
  → Verify ρ_partial(safety,ethics) > 0.5

Step 5: Evaluate Gate M1 (MUST_WORK)
  → PASS: Proceed to H-M2
  → FAIL: PIVOT on RLHF classification

Step 6: Execute H-M2 (RLHF reduces robustness) — Week 4
  → Verify ρ_partial(safety,robustness) < -0.4
  → Pythia within-family control

Step 7: Execute H-M3 (2-cluster structure) — Week 5
  → Ward clustering on full ρ_partial matrix
  → Cluster membership alignment test
  → HELM replication — Week 6

Step 8: Final — Synthesis + verification_state.yaml update
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Core Claim: LLM trustworthiness dimensions exhibit a non-random 2-cluster partial
Spearman correlation structure driven by RLHF optimization pressure, detectable
in existing published evaluation data without new benchmarks or annotation.

Supporting Evidence:
1. Within-family RLHF comparisons [Sun et al., 2024] show safety gains and
   robustness costs from RLHF (LLaMA-2-Chat vs LLaMA-2-base comparison)
2. AQUA-LLM [Güngör et al., 2025] and Know Thy Judge [Eiras et al., 2025]
   provide mechanism evidence: RLHF creates accuracy-robustness tradeoff and
   safety judges are brittle to style shifts (FNR ≤0.24 jump)
3. TruthfulQA loads orthogonally to capability PC1 (PCA study 2603.00394),
   showing that trustworthiness dimensions are geometrically distinct from
   capability — consistent with structured rather than random correlation

Strengths:
- Predictions are made BEFORE data analysis (not post-hoc)
- Uses existing published data only — zero new data collection required
- Both positive and negative outcomes are publishable (null finding of independence
  is also a meaningful contribution filling Liu et al. [2023] open direction)
- Addresses explicitly stated open question from 575-citation survey

Expected Outcomes:
- P1: ρ_partial(safety, ethics) > 0.5, p < 0.0033
- P2: ρ_partial(safety, robustness) < -0.4, p < 0.0033
- P3: Silhouette > 0.3 for k=2 clustering
- P4: MST minimum set ≤4 dimensions, stability ≥0.90
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS (H0-Based)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Null Hypothesis (H0): There is no significant correlation structure across 6
TrustLLM trustworthiness dimensions after controlling for model scale and RLHF
alignment status (all |ρ_partial| < 0.3; silhouette < 0.1 for all k≥2).
Trustworthiness dimensions are statistically independent.

Counter-Arguments:
1. n=16 is severely underpowered: after Bonferroni correction (α=0.0033), only
   |ρ| > 0.55 is detectable with df=13 — the study may simply lack power to
   find moderate correlation structure even if it exists
2. Benchmark operationalization sensitivity: 'safety' in TrustLLM and 'safety'
   in HELM may measure different constructs; cross-framework replication may fail
   even if intra-framework structure is real
3. RLHF mechanism is a proposed explanatory framework, not a directly testable
   causal claim — observed correlations may reflect uncontrolled confounds
   beyond the binary RLHF covariate (pretraining data, scale, architecture)

Potential Failure Points:
- R1: Data unavailability blocks all analysis (Critical risk)
- R2: Insufficient model variation makes partial correlation estimates unreliable
- n=16 may be insufficient to detect moderate cluster structure (silhouette
  between 0.1 and 0.3 would be real but undetectable)

Conditions Under Which H0 Would Be Supported:
- All 15 |ρ_partial| < 0.3 after controlling for scale and alignment
- Silhouette < 0.1 for all k≥2 clustering solutions
- HELM replication shows no correlated sign pattern for P1/P2
- Pythia expansion shows same correlation structure (implicating scale, not RLHF)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Balanced Assessment:

The hypothesis H-CDTCS-v1 presents a theoretically motivated and methodologically
sound claim. However, the null hypothesis raises a valid statistical power concern
(n=16 after Bonferroni) that cannot be fully resolved without the Pythia expansion.

Resolution Path:

The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Establishes whether ANY structure exists
   before committing to mechanistic interpretation
2. Sequential mechanism testing (H-M1 → H-M2 → H-M3): Tests causal chain
   step-by-step with falsifiers at each stage
3. Dual gate structure: MUST_WORK gates on H-E1/H-M1 allow early exit if
   null hypothesis is supported
4. Pythia natural experiment: Within-Pythia correlations (RLHF=False) distinguish
   RLHF-mechanism signal from scale confound
5. HELM replication: Independent operationalization reduces risk that TrustLLM
   findings are construct-specific artifacts

Conditions for Thesis Support:
- H-E1 passes: ≥1 |ρ_partial| > 0.5, p < 0.0033
- H-M1 passes: ρ_partial(safety, ethics) > 0.5
- H-M3 shows correct cluster membership ≥4/6 dimensions

Conditions for Antithesis Support:
- H-E1 fails: All |ρ_partial| < 0.3 (dimensions statistically independent)
- H-M1 fails: ρ_partial(safety, ethics) not significant
- Pythia shows same 2-cluster structure (scale drives the structure, not RLHF)

Nuanced Outcome Possibilities:
1. Full Support: H-E1 + H-E2 + H-M1-3 all pass → CDTCS thesis validated, paper ready
2. Partial Support: H-E1 passes, H-M2/M3 fail → Report correlation structure
   without RLHF mechanistic interpretation; still fills Liu et al. open question
3. Scale-Confound Finding: Pythia shows same structure → RLHF mechanism rejected;
   result reframed as scale-driven geometry; publishable as null for RLHF mechanism
4. No Structure: H-E1 fails → Report dimension independence as positive null finding;
   directly answers Liu et al. open question with a negative answer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Non-random correlation structure exists | n=16 insufficient power | H-E1 test with Bonferroni; Pythia expands n |
| Mechanism | RLHF drives 2-cluster structure | Scale confound alternative | Pythia natural experiment (RLHF=False) |
| Scope | Applicable to 2024-era frontier LLMs | TrustLLM-specific artifact | HELM cross-framework replication |
| Prescriptive claim | MST provides minimum evaluation set | Sample-specific topology | Bootstrap stability test (1000 resamples) |

Overall Robustness Score: Medium-High
- Strength: Pre-specified predictions, existing data only, multiple falsification paths
- Weakness: n=16 main sample limits power for moderate effects

Confidence in Verification Plan: 0.78
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-CDTCS-v1 — LLM trustworthiness dimensions exhibit 2-cluster partial Spearman correlation structure driven by RLHF optimization.
- ID: H-CDTCS-v1, Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (Phase 2A Dialogue available)
- Sub-Hypotheses: 5 total (H-E1, H-E2, H-M1, H-M2, H-M3)
  - H-E: 2, H-M: 3, H-C: 0
- Phases: 3 phases over 6 weeks
- Critical Gates: 3 MUST_WORK gates (H-E1, H-E2, H-M1)

**Risk Assessment:** Medium
- Primary concerns: Data granularity availability (R1 — Critical), n=16 power limit (R2 — High)

**Immediate Action:** Verify TrustLLM data format (data granularity check takes <1 hour); begin Phase 1 with H-E1 only after confirming score availability

### 7.2 Conclusions

**Key Achievements:**
- 5 sub-hypotheses defined across 3 phases, all derived from Phase 2A PROVE_NEW claims
- H0 directly addressed: all 15 |ρ_partial| < 0.3 → dimensions independent → thesis rejected
- Both thesis and antithesis outcomes are publishable at NeurIPS/ICML/ICLR tier
- Zero new data collection for primary analysis (existing TrustLLM + HELM scores)
- Scope reduction of 43%: 3 BUILD_ON claims accepted without re-verification

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: 2-cluster correlation structure existence test
- Gate 1: MUST PASS — if fails, PIVOT to lm-eval-harness

**Phase 2: Parallel Existence Extension + Mechanism Step 1** (1 week)
- H-E2: MST minimum evaluation set (parallel with H-M1)
- H-M1: RLHF co-optimizes safety and ethics
- Gate M1: MUST PASS — if fails, PIVOT on RLHF classification

**Phase 3: Mechanism Steps 2-3 + Replication** (3 weeks)
- H-M2: RLHF reduces adversarial robustness
- H-M3: 2-cluster structure with correct cluster membership
- HELM replication + Pythia natural experiment

**Critical Decision Points:**
1. **Gate 1 (H-E1):** Pass → proceed; Fail → STOP, lm-eval-harness fallback
2. **Gate E2 (H-E2):** Pass → MST claim confirmed; Fail → EXPLORE scope of correlation
3. **Gate M1 (H-M1):** Pass → proceed to H-M2; Fail → PIVOT on RLHF covariate

**Open Questions (from Phase 2A):**
- Exact format and granularity of TrustLLM published score files — needs immediate verification
- Whether HELM leaderboard API provides model-level scores for all 7 metrics simultaneously
- How to handle models in TrustLLM with no HELM equivalent (model matching strategy)

**Recommendations:**
1. **Immediate Action:** Download one TrustLLM result JSON and verify per-dimension float scores exist before investing any other time
2. **Resource Allocation:** Allocate 6 weeks; reserve 24-48 GPU hours for Pythia expansion (Week 6)
3. **Failure Management:** Document all partial results; negative findings on H-M2/M3 are publishable; only H-E1 failure is a true blocker

### 7.3 Appendices

**Appendix A: Phase 2A Reference**
- Source: `docs/youra_research/03_refinement.yaml` (ID: H-CDTCS-v1)
- Schema version: 10.0.0, generated 2026-08-04
- Discussion exchanges: 16; convergence at Exchange 15; all 6 personas participated

**Appendix B: MCP Tool Usage Summary**
- Total MCP calls: 4 (scientificmethod × 2, experiment stage × 2)
- Mode: Incremental (Phase 2A pre-seeded hypothesis structure)
- Tools used: mcp__clearThought__scientificmethod (H-E1-verification, H-M-integrated)
