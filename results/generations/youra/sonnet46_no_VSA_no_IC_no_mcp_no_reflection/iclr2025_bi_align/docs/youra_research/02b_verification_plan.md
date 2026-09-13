---
hypothesis_id: H-BAA-v1
hypothesis_title: "Bidirectional Alignment Asymmetry (BAA): Empirical Measurement from Existing Interaction Datasets"
date: "2026-08-31"
confidence_level: 0.75
total_hypothesis_count: 4
research_scope_mode: incremental
scope_reduction_percentage: 60
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
completedAt: "2026-08-31T00:00:00Z"
---

# Verification Plan: Bidirectional Alignment Asymmetry (BAA)

**Date:** 2026-08-31
**Hypothesis ID:** H-BAA-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 0. Established Facts & Scope Reduction

**BUILD_ON (Skip — do not re-verify):**
1. AI-to-human alignment is well-measured by existing benchmarks (HELM, TruthfulQA, BIG-Bench, lm-eval-harness)
2. WildChat-1M contains behavioral metadata (prompt text, timestamps, topic tags, turn counts) suitable for proxy extraction
3. LMSYS Chatbot Arena contains timestamped human preference votes across multiple model versions (2023-2024)
4. Human behavioral adaptation in AI interactions (deskilling, over-reliance) is documented qualitatively

**PROVE_NEW (Verify — generate hypotheses for these):**
1. Human-to-AI alignment has no existing operationalized measurement framework

**Scope Reduction:** 60% — focus verification on behavioral proxy construct validity and temporal structure suitability.

**Phase 2B-4 Instructions:** Skip re-verification of AI-to-human benchmark existence and dataset availability. Focus on: (1) behavioral proxy construct validity — distinguishing expertise gain from agency loss in WildChat metadata; (2) LMSYS Arena temporal structure suitability; (3) HH-RLHF temporal granularity (acknowledged as likely underpowered, demoted to supplementary).

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under publicly available human-AI interaction datasets (WildChat-1M, LMSYS Chatbot Arena, HH-RLHF) spanning 2022-2024, if AI-to-human alignment improves (rising HELM domain scores and LMSYS ELO ratings), then human-to-AI behavioral alignment proxies decline (decreasing prompt complexity, reduced preference vote entropy, lower correction frequency within returning user cohorts), because AI quality improvement reduces user incentive to critically probe, challenge, or correct AI outputs — creating measurable Bidirectional Alignment Asymmetry (BAA) detectable computationally without new annotation.

### 1.2 Alternative Hypothesis (H0)

There is no significant association between AI-to-human alignment metric improvement and human behavioral engagement proxies (prompt complexity, preference vote entropy, correction frequency) in existing public datasets — i.e., the two alignment directions are independent or positively correlated, not asymmetric.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | LMSYS Chatbot Arena + WildChat-1M + HH-RLHF (standard) | LMSYS Arena provides continuous timestamped preference votes for P1 temporal analysis. WildChat-1M provides behavioral metadata for P2 cohort analysis and P3 cross-domain BAA. HH-RLHF provides supplementary inter-annotator agreement test. |
| **Model** | GPT-4/GPT-3.5/Claude/Llama models (as observed in existing datasets) | Multiple model versions over time provide the AI-to-human alignment variation needed to test the negative association hypothesis |

**Dataset Details:**
- Source: HuggingFace + FastChat GitHub + anthropics/hh-rlhf GitHub
- Path: allenai/WildChat-1M (HuggingFace); lm-sys/FastChat (GitHub); anthropics/hh-rlhf (GitHub)

**Model Details:**
- Type: Existing deployed models analyzed as data subjects — no new model training
- Source: Model outputs already in WildChat and LMSYS Arena logs

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| HELM (AI-to-human evaluation only) | 42-scenario holistic evaluation; domain-stratified scores per model version | Multiple LLMs at Stanford CRFM |
| lm-evaluation-harness (AI-to-human only) | Unified benchmark runner for TruthfulQA, HarmBench, BIG-Bench | Public benchmark datasets |
| reward-bench (reward model evaluation) | Evaluates RLHF reward models against human preference labels | Preference pairs from multiple datasets |
| Null hypothesis baseline | Mann-Kendall test of stationarity (H0: τ = 0) for all trend analyses | — |
| Composition drift alternative | Between-cohort decomposition: early vs. late cohort entry | WildChat-1M |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | WildChat prompt metadata reflects genuine behavioral patterns | Collected from real ChatGPT API users; Zhao et al. 2024 minimal filtering | Restrict analysis to LMSYS Arena; WildChat demoted to supplementary |
| A2 | LMSYS Arena votes represent genuine human judgment | Quality controls; multiple rounds per pair; ELO stability indicator | Temporal entropy analysis invalid; need non-Arena preference sources |
| A3 | Prompt token count decline reflects reduced critical engagement, not expertise gain | Within-cohort + topic diversity combination test distinguishes the two | Primary behavioral proxy invalid; different proxy set needed |
| A4 | HELM domain scores alignable temporally with WildChat by model version | HELM evaluation dates available; WildChat model_version field present | H3 cross-sectional BAA unreliable; demote to exploratory |
| A5 | Behavioral signals represent human-to-AI direction (not model capability confound) | Within-cohort design stratifies by model version | Results interpreted as correlational associations only |

### 1.6 Research Gap & Novelty

**First empirical quantification** of bidirectional alignment asymmetry (BAA) from existing public datasets without new annotation, new benchmarks, or synthetic data.

**Key Innovation:** Operationalizing human-to-AI alignment as a behavioral proxy composite (prompt complexity, preference entropy, correction frequency) extractable from existing interaction metadata — converting a qualitatively discussed phenomenon into a computationally measurable construct.

**Differentiation:**
- Shen et al. 2024 (survey): 400+ papers reviewed, defines both directions theoretically — no measurement methodology provided
- Dell'Acqua 2023 (deskilling): single domain field experiment — no AI-to-human alignment comparison, no scale
- Perez 2023 (sycophancy): measures AI sycophancy (AI-to-human) — no human behavioral counterpart
- HELM/lm-eval/reward-bench: AI-to-human only — human-to-AI direction entirely absent

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
**H-E1: Behavioral Proxy Signal Detectability**

**Statement:** Under WildChat-1M (2023-2024 returning user cohorts, ≥3 monthly appearances) and LMSYS Arena (2023-2024 monthly bins), if behavioral proxies (prompt token count, preference vote Shannon entropy, correction/negation frequency) are computed, then statistically significant signal is detectable (Mann-Kendall τ ≠ 0 for at least 2 of 3 proxies), because these interaction metadata fields encode behavioral engagement patterns that vary with model quality improvement.

**Rationale:** This is the existence gate: BAA can only be measured if proxy signals are statistically distinguishable from noise. Without detectable proxies, the mechanism hypotheses become untestable and the entire framework fails before Phase 3.

**Variables:**
- Independent: Time (monthly bins 2023-2024), model version
- Dependent: Mann-Kendall τ for each proxy (prompt token count, vote entropy, correction frequency)
- Controlled: Topic domain (coding/creative/medical), model version in LMSYS

**Verification Protocol:**
1. Download WildChat-1M from HuggingFace; extract prompt_tokens, timestamp, topic_category, model_version, turn_count fields.
2. Construct monthly cohorts via IP-hash clustering; filter to users appearing in ≥3 consecutive monthly bins.
3. Compute Mann-Kendall τ on prompt token count time series per cohort; aggregate across cohorts.
4. Download LMSYS Arena logs; compute Shannon entropy H(win/lose/tie) per monthly bin per top-5 model pairs.
5. Apply Mann-Kendall to LMSYS entropy time series; verify τ significantly non-zero (p < 0.05) for ≥2 of 3 proxies.

**Success Criteria (PoC):**
- Primary: Mann-Kendall τ significantly non-zero (p < 0.05) for ≥2 of 3 proxies across the 2023-2024 window
- Secondary: Effect size |τ| > 0.2 (weak to moderate trend detectable above noise)

**Failure Response:**
- IF fails (all proxies show no signal): PIVOT — investigate data quality (WildChat cohort size, LMSYS vote count per bin); if confirmed, ABANDON BAA framework

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A SH1 (phase2b_readiness.sh1_existence); Predictions P1, P2

**Gate:** MUST_WORK — failure blocks entire pipeline

---

**H-M1: AI Alignment Improvement Trend (AI-to-Human Direction)**

**Statement:** Under LMSYS Chatbot Arena 2023-2024 monthly data, if model ELO ratings are tracked across time, then top-5 model ELO ratings show statistically significant monotonic increase (Mann-Kendall τ > 0, p < 0.05), because successive model versions (GPT-3.5 → GPT-4 → GPT-4o; Claude 2 → Claude 3) represent documented capability improvements reflected in preference-based rankings.

**Rationale:** This mechanism step establishes the independent variable variation needed for downstream BAA correlation. Without confirmed ELO improvement trend, the causal chain has no anchor and the negative association hypothesis becomes unfalsifiable — there is no "improving AI alignment" to correlate against.

**Variables:**
- Independent: Calendar month (2023-01 to 2024-12)
- Dependent: Mean ELO rating per monthly bin per top-5 model; Mann-Kendall τ on ELO time series
- Controlled: Model family (test GPT, Claude, Llama separately)

**Verification Protocol:**
1. Download LMSYS Arena conversation logs; extract model_a, model_b, winner, timestamp fields.
2. Compute ELO ratings per model per monthly bin using standard ELO update formula on win/lose/tie outcomes.
3. Apply Mann-Kendall trend test to ELO time series for each of top-5 models (ranked by total vote count).
4. Compute bootstrap confidence intervals (B=1000) on τ to assess stability.
5. Verify: at least 3 of top-5 models show significantly positive ELO trend (τ > 0, p < 0.05).

**Success Criteria (PoC):**
- Primary: ≥3/5 top models show Mann-Kendall τ > 0 (p < 0.05) on ELO time series
- Secondary: Mean ELO increase across observation window ≥ 50 points for best-performing model

**Failure Response:**
- IF fails: EXPLORE — check observation window length and model version labeling; if confirmed no improvement, DOCUMENT as null finding and reassess BAA framework timing assumption

**Dependencies:** H-E1

**Source:** Phase 2A causal mechanism Step 1

**Gate:** MUST_WORK — no AI-alignment improvement = no BAA to measure

---

**H-M2: AI Quality Improvement Reduces Human Critical Engagement**

**Statement:** Under WildChat-1M 2023-2024 within-cohort analysis (users in ≥3 consecutive monthly bins, stratified by model version), if model version ELO improves across the observation window, then within-cohort correction/negation frequency per session declines (negative Spearman ρ between model ELO and correction rate, ρ < -0.3, p < 0.05), because higher-quality responses reduce perceived need for users to challenge, correct, or probe AI outputs.

**Rationale:** This is the core mechanism step — the causal link from AI capability improvement to behavioral disengagement. It directly tests the proposed mechanism (reduced probing incentive) rather than observing behavioral trends in isolation, and distinguishes the hypothesized causal path from coincidental co-variation.

**Variables:**
- Independent: Model version ELO (aligned to WildChat model_version field)
- Dependent: Correction/negation frequency per session (count of negation terms, re-asks, explicit corrections normalized by turn_count)
- Controlled: Topic domain (coding/creative/medical), user cohort entry time

**Verification Protocol:**
1. Align WildChat model_version labels to LMSYS ELO values using model deployment date mapping.
2. Compute correction/negation frequency per session: count turns with negation markers ("actually", "that's wrong", "no, I meant", "please redo") normalized by turn_count.
3. Aggregate mean correction frequency per model version per monthly bin within cohorts.
4. Compute Spearman ρ between model ELO (from H-M1 results) and correction frequency across (model version × monthly bin) cells.
5. Test significance (p < 0.05); apply bootstrap CI (B=1000) to ρ estimate.

**Success Criteria (PoC):**
- Primary: Spearman ρ < -0.3 between ELO and correction frequency (p < 0.05)
- Secondary: Effect consistent across ≥2 of 3 topic domains (coding, creative, medical)

**Failure Response:**
- IF fails: PIVOT — test alternative proxy (question mark frequency, turn count per session); if all alternatives fail, DOCUMENT as A3 assumption violation (proxy construct invalidity)

**Dependencies:** H-M1

**Source:** Phase 2A causal mechanism Step 2; assumption A3

**Gate:** SHOULD_WORK — failure narrows but does not invalidate framework

---

**H-M3: Reduced Engagement Manifests as Measurable Behavioral Convergence**

**Statement:** Under WildChat-1M within-cohort analysis and LMSYS Arena temporal data, if users experience within-cohort behavioral disengagement (from H-M2), then (a) Mann-Kendall τ on within-cohort prompt token count is significantly negative (p < 0.05) and early-cohort |τ| > late-cohort |τ|, AND (b) LMSYS vote entropy shows Spearman ρ < -0.4 with monthly mean ELO (p < 0.05), because reduced probing incentive produces shorter prompts and more homogeneous preference voting.

**Rationale:** This step validates that behavioral disengagement (H-M2) produces the specific measurable signals predicted by the BAA framework. It also tests the composition drift alternative explanation via the early/late cohort comparison — the most important internal validity check in the study design.

**Variables:**
- Independent: Time (user tenure in monthly bins); model ELO (monthly mean)
- Dependent: (a) Mann-Kendall τ on within-cohort prompt token count; (b) Shannon entropy of LMSYS win/lose/tie votes per monthly bin
- Controlled: User cohort entry time (early Q1 2023 vs. late Q3 2023 for composition drift test)

**Verification Protocol:**
1. Compute Mann-Kendall τ on prompt token count per WildChat cohort; aggregate across cohorts via meta-analytic weighting.
2. Perform between-cohort decomposition: compute τ separately for Q1 2023 and Q3 2023 cohorts; test if early-cohort |τ| > late-cohort |τ| via bootstrap CI overlap.
3. Compute Shannon entropy per LMSYS monthly bin per model pair; aggregate top-5 pairs.
4. Compute Spearman ρ between monthly mean ELO (from H-M1) and monthly mean vote entropy.
5. Report both sub-tests; hypothesis passes if both succeed (FULL) or one succeeds with documented limitation (PARTIAL).

**Success Criteria (PoC):**
- Primary: Within-cohort Mann-Kendall τ < 0 (p < 0.05) AND early-cohort |τ| > late-cohort |τ| (non-overlapping bootstrap CIs)
- Secondary: LMSYS vote entropy Spearman ρ < -0.4 with ELO (p < 0.05)

**Failure Response:**
- IF (a) fails but (b) succeeds: PARTIAL — LMSYS signal exists but WildChat cohort quality insufficient; document A1 assumption limitation
- IF both fail: PIVOT — recheck ELO-to-WildChat date alignment; if confirmed, DOCUMENT as null finding

**Dependencies:** H-M2

**Source:** Phase 2A causal mechanism Step 3; predictions P1, P2; assumptions A1, A4

**Gate:** SHOULD_WORK — partial results acceptable; full pass preferred for Phase 5 baseline comparison

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ≥2/3 proxies show τ ≠ 0 (p < 0.05) | STOP pipeline; investigate data quality |
| H-M1 | MUST_WORK | ≥3/5 top models ELO τ > 0 (p < 0.05) | Route to Phase 0; no BAA anchor |
| H-M2 | SHOULD_WORK | Spearman ρ < -0.3 (p < 0.05) | Document A3 violation; continue with entropy |
| H-M3 | SHOULD_WORK | Within-cohort τ < 0 + early > late; LMSYS ρ < -0.4 | Document limitation; report partial |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks (W1-W2) |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 3 weeks (W3-W6) |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: WildChat cohort quality | A1 | H-E1, H-M2, H-M3 | High |
| R2: LMSYS vote non-representativeness | A2 | H-E1, H-M3 | Medium |
| R3: Proxy construct invalidity | A3 | H-M2, H-M3 | High |
| R4: HELM-WildChat version alignment | A4 | P3 cross-section | Medium |
| R5: Model capability confound | A5 | All | Medium |

### 4.2 Mitigation Strategies

**R1: WildChat Cohort Quality Degradation**
- Prevention: Filter to IP-hashes with ≥3 monthly appearances; compute cohort stability metric
- Detection: Compare within-cohort vs. between-cohort variance ratio
- Response: PIVOT — elevate LMSYS Arena to sole primary; WildChat demoted to pilot

**R2: LMSYS Vote Non-Representativeness**
- Prevention: Filter to model pairs with ≥100 votes per monthly bin
- Detection: Check for vote distribution discontinuities; jackknife entropy stability test
- Response: PIVOT — use vote count trajectory instead of entropy if anomalies found

**R3: Proxy Construct Invalidity (Expertise Gain vs. Agency Loss)**
- Prevention: Multi-signal composite (token count + topic diversity + correction frequency)
- Detection: Token count declines but topic diversity/correction frequency stable = expertise gain
- Response: SCOPE — rely on entropy + correction frequency as primary; document token count as ambiguous

**R4: HELM-WildChat Version Alignment Failure**
- Prevention: Pre-register HELM-WildChat version mapping table before any analysis
- Detection: Test sensitivity under 2-3 alternative version mapping assumptions
- Response: SCOPE — demote P3 to exploratory if uncertainty exceeds ±1 month

**R5: Model Capability Confound**
- Prevention: Within-cohort design stratifies by model version; residual trends within-version = behavioral adaptation
- Detection: Compare trends within single model version windows vs. across version transitions
- Response: SCOPE — present as "behavioral correlates of AI alignment improvement" (correlational claim) if causal claim unsupported

### 4.3 Risk Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical: 0 | High: 2 (R1, R3) | Medium: 3 (R2, R4, R5) | Low: 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 DAG

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses (H-BAA-v1)
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    ┌─────────────────────────────────────────────┐
    │  H-E1 (EXISTENCE)                           │
    │  Behavioral proxy signal detectability      │
    │  Gate: MUST_WORK                            │
    └─────────────────────────────────────────────┘
                          │
                          ▼ Gate 1: MUST PASS
[Level 1 - Mechanism: AI Alignment Trend]
    ┌─────────────────────────────────────────────┐
    │  H-M1 (MECHANISM)                           │
    │  AI ELO improvement trend confirmed         │
    │  Gate: MUST_WORK                            │
    └─────────────────────────────────────────────┘
                          │
                          ▼ Gate 2: MUST PASS
[Level 2 - Mechanism: Quality → Disengagement]
    ┌─────────────────────────────────────────────┐
    │  H-M2 (MECHANISM)                           │
    │  ELO improvement → correction freq decline  │
    │  Gate: SHOULD_WORK                          │
    └─────────────────────────────────────────────┘
                          │
                          ▼ Gate 2a: Should Pass
[Level 3 - Mechanism: Behavioral Convergence]
    ┌─────────────────────────────────────────────┐
    │  H-M3 (MECHANISM)                           │
    │  Behavioral convergence measurable          │
    │  (prompts + entropy; composition drift test)│
    │  Gate: SHOULD_WORK                          │
    └─────────────────────────────────────────────┘
                          │
                          ▼
               ┌──────────────────┐
               │ Phase 5 Deferred │
               │ (skip_baseline=  │
               │  true in config) │
               └──────────────────┘

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Phase |
|-------|-----------|---------------|-----------|-------|
| 0 | H-E1 | None | MUST_WORK | Phase 1 |
| 1 | H-M1 | H-E1 | MUST_WORK | Phase 2 |
| 2 | H-M2 | H-M1 | SHOULD_WORK | Phase 2 |
| 3 | H-M3 | H-M2 | SHOULD_WORK | Phase 2 |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses (H-BAA-v1)
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis       │ W1-2     │ W3-4     │ W5       │ W6
───────────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 1: Foundation    │          │          │          │
  H-E1 (Proxy detect.) │ ████████ │          │          │
  [Gate 1: MUST PASS]  │        ◆ │          │          │
───────────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 2: Mechanisms    │          │          │          │
  H-M1 (ELO trend)     │          │ ████████ │          │
  [Gate 2: MUST PASS]  │          │        ◆ │          │
  H-M2 (Quality→Dis.)  │          │          │ ████████ │
  [Gate 2a: should]    │          │          │        ◆ │
  H-M3 (Convergence)   │          │          │          │ ████████
  [Gate 2b: should]    │          │          │          │        ◆
═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Duration: 5 weeks (2 + 1 + 1 + 1)
Slack: 0 weeks (all sequential)
Execution Mode: Sequential chain
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** H-BAA-v1 — Under publicly available human-AI interaction datasets, AI-to-human alignment improvement is negatively associated with human-to-AI behavioral engagement proxies, creating measurable Bidirectional Alignment Asymmetry (BAA) detectable computationally without new annotation.

**Supporting Evidence:**
1. Dell'Acqua et al. 2023: deskilling in consulting professionals as AI quality improved — analogous mechanism in ChatGPT use expected in WildChat
2. Perez et al. 2023: AI sycophancy reduces user challenge incentive; counterpart human-to-AI direction predicts similar behavioral disengagement
3. WildChat-1M + LMSYS Arena provide behavioral metadata covering 2023-2024 with sufficient temporal resolution for trend analysis

**Strengths:**
- First empirical BAA operationalization from existing public data — no annotation required
- Multi-signal proxy composite (complexity + entropy + correction) guards against single-proxy failure
- Three independent falsifiable test designs (P1, P2, P3)
- Within-cohort + between-cohort decomposition addresses composition drift alternative

**Expected Outcomes:**
- P1: LMSYS vote entropy τ < 0 (p < 0.05) as ELO rises; Spearman ρ < -0.4
- P2: WildChat within-cohort prompt complexity declines; early-cohort |τ| > late-cohort |τ|
- P3: Cross-domain Spearman ρ < -0.3 (p < 0.05)

### 6.2 Antithesis

**Null Hypothesis (H0):** No significant negative association between AI-to-human alignment metric improvement and human behavioral engagement proxies — the two directions are statistically independent or positively correlated.

**Counter-Arguments:**
1. All existing measurement frameworks (HELM, lm-eval, reward-bench) measure AI-to-human only — human-to-AI direction has never been operationalized empirically; prior claims are entirely anecdotal
2. Proxy invalidity (A3): Prompt complexity decline may reflect expertise gain (efficient prompting) rather than agency loss — these produce identical token-count signals and require additional signals to distinguish
3. WildChat IP-hash cohort noise (A1): Approximate cohort tracking may conflate individual behavioral adaptation with cohort composition change

**Potential Failure Points:**
- R3 (proxy construct invalidity): Cannot distinguish expertise gain from agency loss on token count alone
- R1 (WildChat cohort quality): IP-hash precision limits within-cohort tracking fidelity
- R5 (model capability confound): Optimal prompt strategy changes with model capability (not purely behavioral disengagement)

**Conditions Under Which H0 Would Be Supported:**
- All 3 proxies show non-significant Mann-Kendall τ (p > 0.05)
- Early-cohort and late-cohort τ not significantly different (composition drift cannot be ruled out)
- Proxy signals are positive (users engage MORE as AI improves)

### 6.3 Synthesis

**Balanced Assessment:** H-BAA-v1 presents a falsifiable claim grounded in an internally consistent causal mechanism, supported by indirect evidence from deskilling and sycophancy literature. The null hypothesis raises valid methodological concerns — particularly around proxy construct validity and cohort precision — that cannot be fully resolved without executing the proposed analysis.

**Resolution Path:**
1. Foundation (H-E1): Establishes whether proxy signals are detectable at all — direct empirical test of proxy viability
2. AI trend verification (H-M1): Confirms the independent variable varies as assumed — rules out flat-ELO null scenario
3. Mechanism test (H-M2): Directly tests the causal link via correction frequency × ELO Spearman correlation
4. Convergence test (H-M3): Tests behavioral convergence AND composition drift alternative via early/late cohort comparison

**Conditions for Thesis Support:**
- H-E1 and H-M1 pass (MUST_WORK gates)
- H-M2 confirms negative Spearman ρ (p < 0.05)
- H-M3 early-cohort > late-cohort |τ| (composition drift ruled out)

**Nuanced Outcome Possibilities:**
1. Full Support: All 4 pass → BAA confirmed, causal chain supported
2. Partial (LMSYS only): H-E1/H-M1/H-M3b pass, WildChat weak → "LMSYS Arena evidence sufficient for BAA claim"
3. Partial (signal not causal): H-E1/H-M1/H-M3 pass, H-M2 weak → "Behavioral convergence correlates with AI improvement"
4. No Support: H-E1 or H-M1 fail → Antithesis supported; redirect to Phase 0

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Proxies detectable in metadata | Signals may be noise only | H-E1 test |
| Mechanism | AI quality → reduced probing | Expertise gain alternative | H-M2 + H-M3 together |
| Confounds | Within-cohort design controls | Composition drift possible | Early/late cohort test (H-M3) |
| Data quality | Large-scale public datasets | WildChat cohort imprecision | LMSYS as primary |
| Scope | Cross-domain 3 areas, multi-model | ChatGPT-specific effect | LMSYS multi-model coverage |

**Overall Robustness Score:** Medium-High
**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary & Appendices

### Executive Summary

**Main Hypothesis:** H-BAA-v1 — BAA is measurable from existing public datasets: AI-to-human alignment improvement is negatively associated with human-to-AI behavioral engagement proxies.
- ID: H-BAA-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A Dialogue available, 60% scope reduction)
- Sub-Hypotheses: 4 total (H-E1 + H-M1 + H-M2 + H-M3); H-E: 1, H-M: 3
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 MUST_WORK (H-E1, H-M1), 2 SHOULD_WORK (H-M2, H-M3)

**Risk Assessment:** Medium-High
- Primary concerns: (1) WildChat cohort quality (IP-hash precision), (2) Proxy construct validity (expertise gain vs. agency loss ambiguity)

**Immediate Action:** Begin Phase 1 with H-E1 — download WildChat-1M + LMSYS Arena, compute proxy signal statistics

### Conclusions

**Key Achievements:**
- 4 sub-hypotheses across 2 phases (5 weeks)
- H0 explicitly addressed: independence/positive correlation of alignment directions
- 60% scope reduction via established facts (BUILD_ON claims excluded)
- Three independent test designs embedded in hypothesis chain

**Verification Execution Order:**

Phase 1: Foundation (2 weeks)
- H-E1: Behavioral proxies statistically detectable (≥2/3 pass Mann-Kendall)
- Gate 1: MUST PASS → if fails, investigate data quality and STOP

Phase 2: Core Mechanisms (3 weeks)
- H-M1: LMSYS ELO improvement trend confirmed (τ > 0)
- H-M2: ELO improvement negatively correlated with correction frequency (ρ < -0.3)
- H-M3: Within-cohort prompt complexity declines; early > late cohort; LMSYS entropy ρ < -0.4
- Gate 2: H-M1 must pass; H-M2/H-M3 failures narrow scope

**Critical Decision Points:**

1. Gate 1 (Foundation): H-E1 must pass
   - FAIL → STOP, reassess data quality and hypothesis feasibility
   - PASS → Proceed to Phase 2

2. Gate 2 (Mechanisms): H-M1 must pass
   - CRITICAL FAIL → Route to Phase 0 (no ELO trend = no BAA anchor)
   - H-M2 fail → Document A3 assumption violation, rely on entropy only
   - H-M3 fail → Document WildChat limitation, LMSYS-only conclusion

**Open Questions:**
- WildChat cohort sensitivity: how much does IP-hash noise affect within-cohort estimates?
- HELM-WildChat version matching: pre-register mapping before Phase 3 implementation
- HH-RLHF: confirm number of temporal phases before including or dropping from analysis
- All [INFERRED] arXiv IDs from Phase 1 require verification before Phase 3

**Recommendations:**

1. Immediate Actions:
   - Start Phase 1 with H-E1: download datasets, compute proxy signal statistics
   - Pre-register HELM-WildChat version mapping table before any analysis

2. Resource Allocation:
   - Allocate 5 weeks for critical path
   - Reserve additional week for data download/preprocessing

3. Failure Management:
   - Document all failures with gate results
   - Execute PIVOT strategies (R1: LMSYS elevation; R3: multi-signal composite)
   - WildChat sensitivity analysis mandatory regardless of outcome

### Appendices

**A. Phase 2A Reference**
- Source: docs/youra_research/03_refinement.yaml (ID: H-BAA-v1)
- Discussion: 9 exchanges, all 6 convergence criteria met
- Agents: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**B. Analysis Tools**
- scipy.stats.kendalltau — Mann-Kendall trend tests
- scipy.stats.spearmanr — cross-sectional BAA correlations
- Bootstrap CI: B=1000 resamples for all effect size estimates

**C. MCP Tool Usage**
- Total MCP calls: 0 (ablation mode — ClearThought unavailable; reasoning applied directly from Phase 2A structure)
