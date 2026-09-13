# Verification Plan: Context-Aware Formal Dataset Deprecation

**Date:** 2026-08-24
**Hypothesis ID:** H-DepGraph-v1
**Confidence:** 0.8
**Total Hypotheses:** 5 sub-hypotheses

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under ML repository settings with existing deprecation metadata (HuggingFace Datasets Hub), if we deploy a three-component formal deprecation system (automated health metrics + context-aware successor graphs + instrumented executable policies), then successor adoption rates will increase by ≥ 50% relative to baseline informal mechanisms over 6 months, because the system addresses three distinct failure modes in current practice: (1) lack of automated deprecation candidate detection, (2) missing task-specific successor mappings, and (3) absence of point-of-use recommendations with adoption tracking.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in dataset successor adoption rates between users exposed to formal deprecation mechanisms (health metrics + context graphs + executable policies) and users relying on informal deprecation signals (GitHub READMEs, community discussion, manual search), measured as adoption lift < 10% over 6 months.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HuggingFace Datasets Hub Metadata + Usage Logs (standard) | Real-world repository with existing deprecation events, dataset cards (for edge inference), download logs (for health metrics), and programmatic loaders (for instrumentation) |
| **Model** | N/A (Infrastructure Research) | This hypothesis tests dataset infrastructure mechanisms, not ML model performance |

**Dataset Details:**
- Source: HuggingFace Datasets Hub API, Papers with Code citation data, GitHub issue tracking
- Path: https://huggingface.co/datasets

**Model Details:**
- Type: N/A
- Source: N/A

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Informal Deprecation (Status Quo) | Unknown baseline successor adoption rate (to be measured in Phase 1) | HuggingFace Datasets Hub (current state) |
| Datasheets for Datasets (Gebru et al. 2021) | Documentation completeness but no deprecation lifecycle support | General ML datasets |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | HuggingFace download logs and Papers with Code citation data provide sufficient signals for health metric computation | Prof. Vera confirmed usage velocity, successor emergence, and issue ratios are computable from existing APIs | If download data is too coarse-grained or citation data is incomplete, health metrics lose predictive power |
| A2 | Python import history introspection can infer user task context with ≥ 70% accuracy | Prof. Pax confirmed Python introspection technically feasible. Dr. Nova proposed hybrid approach with explicit fallback for ambiguous cases | If context inference accuracy < 70%, users receive irrelevant successor recommendations, reducing adoption |
| A3 | Users will adopt instrumented dataset loaders (opt-in wrappers) rather than bypassing them for standard loaders | Prof. Pax recommended opt-in approach to avoid maintainer buy-in dependency. Assumes value proposition outweighs adoption friction | If bypass rate > 60% or instrumentation overhead > 10%, measurement infrastructure and policy delivery fail |
| A4 | Automated edge inference from dataset card citations produces useful successor graphs rather than noisy tangles | Prof. Pax identified automated inference as feasibility requirement. Curator validation layer provides quality control | If inferred edges have low precision (many false successors), graphs become unusable clutter |
| A5 | Current informal deprecation mechanisms have low baseline successor discovery rates (< 30%), creating room for improvement | Prof. Rex flagged this as critical unknown. Paullada et al. survey documents deprecation gaps, but quantitative baseline unestablished | If baseline is already ≥ 60%, a 50% lift is mathematically impossible or approaching ceiling effects |

### 1.6 Research Gap & Novelty

**Novelty:** Context-aware successor graphs model multi-path, task-conditional succession (ImageNet → ImageNet-v2 vs. ImageNet-21k depending on use case) rather than single-path linear versioning. Usage-pattern-based context inference (Python import history introspection) eliminates explicit user tagging friction while maintaining low-friction UX. Two-tiered hypothesis treats measurement infrastructure (load-time telemetry) as research contribution.

**Gap:** Current ML repositories (HuggingFace, OpenML, UCI) use informal versioning without standardized deprecation protocols. Lack of automated detection, formal successor mappings, point-of-use recommendations, and adoption tracking.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M1, H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Instrumentation Infrastructure Validation

**Type:** EXISTENCE
**Statement:** Load-time instrumentation successfully tracks successor adoption events with < 10% performance overhead and privacy-preserving telemetry, enabling quantitative measurement of adoption rates for ≥ 100 deprecation events over 6 months.

**Variables:**
- IV: Instrumented dataset loader deployment
- DV: Performance overhead (%), telemetry capture rate (%), tracked deprecation events count
- CV: Repository platform (HuggingFace), observation period (6 months), dataset access method (Python-based loaders)

**Success Criteria:**
- Latency overhead < 10% per dataset load operation
- Telemetry transmission success rate ≥ 95%
- ≥ 100 deprecation events logged with successor outcomes tracked
- User opt-in rate ≥ 40%

**Gate:**
- Type: MUST_WORK
- If Fail: Infrastructure cannot support measurement or policy delivery → entire methodology fails

**Prerequisites:** None

**Verification Protocol:**
Deploy instrumented dataset loader wrapper on HuggingFace. Measure latency overhead per load operation using benchmark suite across representative datasets (small/medium/large). Track telemetry transmission success rate over 6-month period. Monitor user opt-in/bypass rates. Validate privacy-preserving telemetry design through security audit. Confirm ≥ 100 deprecation events captured with complete successor outcome data.

---

#### H-M1: Health Metrics Predictive Power

**Type:** MECHANISM
**Statement:** Health metrics (usage velocity < 0.3, successor emergence > 3, issue ratio high) automatically surface deprecation candidates, reducing maintainer cognitive burden and increasing deprecation decision consistency with ≥ 60% precision and ≥ 80% recall.

**Variables:**
- IV: Health metric computation and deprecation candidate flagging
- DV: Precision (%), Recall (%) in prospectively predicting maintainer deprecation decisions
- CV: Repository platform (HuggingFace), observation window (6 months), metric thresholds

**Success Criteria:**
- Precision ≥ 60% (flagged datasets that maintainers actually deprecate)
- Recall ≥ 80% (proportion of actual deprecations that were flagged)
- Metrics computable from HuggingFace download logs + Papers with Code citations + GitHub issues API

**Gate:**
- Type: MUST_WORK
- If Fail: Health metrics don't capture actual deprecation drivers → automated detection fails

**Prerequisites:** H-E1 (requires instrumentation for metric collection)

**Verification Protocol:**
Month 0: Apply health metrics to all non-deprecated HuggingFace datasets, flag top 30 deprecation candidates based on usage velocity, successor emergence, and issue accumulation. Month 6: Compare flagged datasets to actual maintainer deprecation decisions. Calculate precision (true positives / all flagged) and recall (true positives / all actual deprecations). Validate that metrics are computable from existing APIs without requiring new data collection infrastructure.

---

#### H-M2: Context-Aware Successor Graph Accuracy

**Type:** MECHANISM
**Statement:** Context-aware successor graphs capture task-specific replacement paths via usage-pattern inference, providing more relevant recommendations than linear version-based succession with ≥ 70% context inference accuracy.

**Variables:**
- IV: Context-aware successor graph construction + usage-pattern-based context inference
- DV: Context inference accuracy (%) on labeled validation set
- CV: Dataset card citation data quality, user task diversity, Python import history availability

**Success Criteria:**
- Context inference accuracy ≥ 70% (inferred user context matches ground-truth task labels)
- User override rate < 50% (users accept inferred context without manual correction)
- Automated edge inference from dataset card citations produces precision ≥ 60%

**Gate:**
- Type: MUST_WORK
- If Fail: Context inference fails → users receive irrelevant successor recommendations → adoption doesn't improve

**Prerequisites:** H-E1 (requires instrumentation for usage pattern tracking)

**Verification Protocol:**
Build validation dataset with labeled user task contexts (classification, robustness eval, pretraining, etc.). Implement Python import history introspection + dataset card citation parsing. Test context inference on validation set, measure accuracy against ground-truth labels. Track user override rate (explicit context specification vs. accepting inferred context). Evaluate automated edge inference precision by sampling inferred successor edges and validating with domain experts or dataset maintainers.

---

#### H-M3: Executable Policy Delivery Effectiveness

**Type:** MECHANISM
**Statement:** Executable policies deliver deprecation warnings + successor recommendations at dataset load time (point of use), increasing visibility compared to documentation-only approaches with user bypass rate < 40%.

**Variables:**
- IV: Load-time deprecation warnings + successor recommendations delivery
- DV: User bypass rate (%), warning visibility (measured via user surveys/telemetry)
- CV: Warning design (non-intrusive), recommendation quality (from H-M2)

**Success Criteria:**
- User bypass rate < 40% (users don't disable instrumented loaders to avoid warnings)
- Warning delivery success rate ≥ 95%
- Comparative visibility increase vs. README-only approach (measured via A/B test)

**Gate:**
- Type: SHOULD_WORK
- If Fail: Users bypass warnings → policy delivery fails, but core mechanisms (H-M1, H-M2) still validated

**Prerequisites:** H-M1 (health metrics for deprecation detection), H-M2 (successor recommendations)

**Verification Protocol:**
Implement Python decorator-based load-time warning system. A/B test: Group A receives instrumented loaders with warnings, Group B receives standard loaders with README-only deprecation info. Measure bypass rate (users switching from instrumented to standard loaders). Track warning delivery success via telemetry. Conduct user surveys on warning visibility and intrusiveness. Compare successor discovery rates between groups.

---

#### H-M4: Adoption Tracking Measurement Infrastructure

**Type:** MECHANISM
**Statement:** Load-time instrumentation tracks successor adoption events, enabling quantitative measurement of deprecation mechanism efficacy with < 10% performance overhead and ≥ 95% telemetry capture rate.

**Variables:**
- IV: Successor adoption event tracking via instrumented loaders
- DV: Performance overhead (%), telemetry capture rate (%), adoption event completeness
- CV: Privacy-preserving telemetry design, user opt-in requirements

**Success Criteria:**
- Performance overhead < 10% (same as H-E1, reinforced at scale)
- Telemetry capture rate ≥ 95%
- Adoption events tracked: user loads deprecated dataset D, then loads successor S within 30 days

**Gate:**
- Type: SHOULD_WORK
- If Fail: Cannot quantitatively measure adoption rates → efficacy claims rely on qualitative assessment

**Prerequisites:** H-M3 (executable policies must deliver recommendations for adoption tracking to be meaningful)

**Verification Protocol:**
Deploy adoption tracking instrumentation at scale. Monitor performance overhead across diverse dataset sizes and user workloads. Track telemetry capture success rate over 6-month period. Validate adoption event logic: deprecated dataset load → successor dataset load within 30-day window. Ensure privacy-preserving design (anonymized user IDs, opt-in consent, no sensitive data capture). Calculate adoption rates: percentage of users loading deprecated dataset D who subsequently load successor S.

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → [H-M1, H-M2] → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Overhead < 10%, capture ≥ 95%, ≥ 100 events tracked | STOP - Infrastructure cannot support methodology |
| H-M1 | MUST_WORK | Precision ≥ 60%, Recall ≥ 80% | STOP - Health metrics don't predict deprecations |
| H-M2 | MUST_WORK | Context accuracy ≥ 70%, override < 50% | STOP - Context inference fails, recommendations irrelevant |
| H-M3 | SHOULD_WORK | Bypass < 40%, delivery ≥ 95% | PARTIAL - Core mechanisms validated, policy delivery optional |
| H-M4 | SHOULD_WORK | Overhead < 10%, capture ≥ 95% | PARTIAL - Qualitative efficacy assessment if measurement fails |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 2C | Design all experiments | 2-3 days |
| Phase 3 | Implementation planning | 3-4 days |
| Phase 4 | PoC validation (H-E1 → H-M1 → H-M2 → H-M3 → H-M4) | 10-14 days |
| Phase 5 | Baseline comparison (skipped per module config) | 0 days (skipped) |
| Phase 6 | Paper writing | 5-7 days |

**Total Duration:** ~20-28 days (Phase 5 skipped)

---

## 4. Risk Analysis

### 4.1 Assumption Risks

| Risk ID | Source Assumption | Risk Statement | Impact | Mitigation |
|---------|------------------|----------------|--------|------------|
| R1 | A1: Data availability | HuggingFace download logs too coarse-grained or citation data incomplete | Health metrics (H-M1) fail | Early API exploration to validate metric computability before Phase 4 |
| R2 | A2: Context inference accuracy | Python import history introspection < 70% accurate | Irrelevant successor recommendations (H-M2 fails) | Hybrid approach: automated inference + explicit fallback for ambiguous cases |
| R3 | A3: User adoption friction | Bypass rate > 60% or overhead > 10% | Instrumentation fails (H-E1, H-M4 fail) | UX testing + performance benchmarking before deployment |
| R4 | A4: Graph edge quality | Automated edge inference produces noisy graphs | Successor recommendations unusable (H-M2 degrades) | Three-tier governance: automation + curator validation + community feedback |
| R5 | A5: Baseline ceiling effect | Informal baseline already ≥ 60% | 50% lift mathematically impossible (Phase 5 would fail if run) | Empirical baseline measurement in Phase 1 before setting efficacy targets |

### 4.2 Execution Risks

| Risk | Description | Probability | Impact | Mitigation |
|------|-------------|-------------|--------|------------|
| Privacy concerns block deployment | Telemetry raises user privacy objections | Medium | High (H-E1, H-M4 fail) | Privacy-preserving design from start, opt-in consent, anonymization |
| Maintainer buy-in required | HuggingFace maintainers refuse API access | Low | Critical (entire methodology fails) | Opt-in wrapper approach avoids maintainer dependency |
| Cross-domain generalization | Results specific to HuggingFace, don't generalize | Medium | Medium (limits contribution scope) | Test on OpenML as secondary validation platform |

---

## 5. Dependency Graph & Timeline

### 5.1 DAG Visualization

```
         ┌─────┐
         │H-E1 │  ← Foundation: Instrumentation Infrastructure
         └──┬──┘
            │
      ┌─────┴─────┐
      │           │
   ┌──▼──┐     ┌──▼──┐
   │H-M1 │     │H-M2 │  ← Parallel: Health Metrics & Context Graphs
   └──┬──┘     └──┬──┘
      │           │
      └─────┬─────┘
            │
         ┌──▼──┐
         │H-M3 │  ← Policies: Deliver Recommendations
         └──┬──┘
            │
         ┌──▼──┐
         │H-M4 │  ← Measurement: Track Adoption
         └─────┘
```

### 5.2 Gantt Timeline (Phase 4 PoC Validation)

```
Week 1-2: H-E1 (Instrumentation)
  ████████░░░░░░░░░░░░░░░░
Week 2-3: H-M1 (Health Metrics) & H-M2 (Context Graphs) [Parallel]
  ░░░░░░░░████████░░░░░░░░
Week 3-4: H-M3 (Executable Policies)
  ░░░░░░░░░░░░░░░░████████
Week 4-5: H-M4 (Adoption Tracking)
  ░░░░░░░░░░░░░░░░░░░░████

Critical Path: H-E1 → H-M1 → H-M3 → H-M4
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

Formal deprecation mechanisms (health metrics + context-aware graphs + executable policies) significantly improve dataset successor adoption rates over informal mechanisms because they address three distinct failure modes: (1) lack of automated detection, (2) missing task-specific mappings, (3) absence of point-of-use recommendations.

### 6.2 Antithesis (from H0)

There is no significant difference in successor adoption rates because engaged users already discover successors via informal channels (GitHub, community discussion), and formal mechanisms only help inactive users who wouldn't have adopted successors anyway. The added infrastructure complexity (instrumentation, context inference, policy delivery) introduces friction that negates any discovery benefits.

### 6.3 Synthesis

The hypothesis is falsifiable via prospective 6-month measurement comparing formal vs. informal groups. If baseline informal adoption is already high (≥ 60%), formal mechanisms provide marginal benefit. However, if baseline is low (< 30%) as assumed, the 50% lift is achievable by reducing discovery friction for the majority of users who don't actively monitor GitHub/community channels. The measurement infrastructure (H-E1, H-M4) is itself a contribution, enabling first-time quantitative tracking of dataset deprecation efficacy. Risk mitigation via hybrid context inference and opt-in instrumentation addresses adoption friction concerns.

### 6.4 Robustness Assessment

**Strengths:**
- Builds on proven software ecosystem mechanisms (package deprecation, dependency graphs)
- Incremental validation: each sub-hypothesis tests one mechanism independently
- Scope reduction from Phase 2A: 43% of work pre-validated (BUILD_ON claims)

**Weaknesses:**
- Baseline unknown (A5 risk): efficacy claims depend on empirical baseline measurement
- Context inference unvalidated (A2 risk): 70% accuracy threshold requires validation dataset
- Generalization uncertain: results may be HuggingFace-specific

**Recommendations:**
1. Early baseline measurement in Phase 1 before Phase 4 implementation
2. Context inference validation on labeled dataset before scale deployment
3. Secondary validation on OpenML to test cross-platform generalization

---

## 7. Executive Summary

### 7.1 Overview

This verification plan decomposes the main hypothesis (H-DepGraph-v1) into **5 sub-hypotheses** tested sequentially through Phases 2C-4:
- **H-E1**: Instrumentation infrastructure (foundation)
- **H-M1-M4**: Four mechanism steps (health metrics, context graphs, executable policies, adoption tracking)

**Scope reduction:** 43% of claims pre-validated from Phase 2A (BUILD_ON status), focusing verification on 3 novel PROVE_NEW claims.

### 7.2 Key Dependencies

**Critical path:** H-E1 → H-M1 → H-M3 → H-M4
**Parallel execution:** H-M1 and H-M2 can run concurrently after H-E1

### 7.3 Gate Strategy

- **MUST_WORK gates:** H-E1, H-M1, H-M2 (foundation + core mechanisms)
- **SHOULD_WORK gates:** H-M3, H-M4 (efficacy + measurement)
- **Phase 5 skipped:** Baseline comparison disabled per module config (skip_baseline_comparison: true)

### 7.4 Risk Mitigation

Top 3 risks:
1. **Baseline ceiling effect (R5):** Mitigate via early empirical baseline measurement
2. **Context inference accuracy (R2):** Mitigate via hybrid approach (automated + explicit fallback)
3. **User adoption friction (R3):** Mitigate via UX testing + performance benchmarking

### 7.5 Next Steps

1. **Phase 2C (Experiment Design):** Generate detailed experimental protocols for each hypothesis
2. **Phase 3 (Implementation Planning):** Create task breakdown, architecture documents, and resource allocation
3. **Phase 4 (PoC Validation):** Execute experiments, validate MUST_WORK gates, track adoption metrics
4. **Phase 6 (Paper Writing):** Synthesize results into publication (Phase 5 baseline comparison skipped)

---

## Appendices

### A. Established Facts Registry (BUILD_ON - Not Re-Tested)

From Phase 2A Section 0:

1. **Current ML repositories use informal versioning** (Paullada et al. 2021 survey, HuggingFace codebase analysis)
2. **Software ecosystems have proven deprecation mechanisms** (NPM, PyPI systems)
3. **DAG-based dependency graphs well-understood** (Maven Central dependency resolution)
4. **Python introspection can track import history** (sys.modules inspection documented)

These claims are **assumed true** and not re-verified in Phase 2B-4.

### B. Verification State File

Path: `verification_state.yaml` (managed via ABLATION MODE - state in prompt context)

Contains:
- Sub-hypothesis tracking (status, gates, prerequisites, validation results)
- Pipeline metadata (project ID, task mappings, phase tracking)
- Workflow state (current phase, execution mode, routing decisions)
- Statistics (hypothesis counts, gate pass/fail rates, phase completion)

### C. Glossary

- **H-E**: Existence hypothesis (validates phenomenon exists)
- **H-M**: Mechanism hypothesis (tests causal chain step)
- **H-C**: Condition hypothesis (boundary conditions) - none in this plan
- **MUST_WORK gate**: Failure blocks Phase 5 (foundation/core mechanisms)
- **SHOULD_WORK gate**: Failure allows Phase 5 with PARTIAL result (optional features)
- **DETERMINES_SUCCESS gate**: Phase 5 baseline comparison (skipped in this pipeline)
