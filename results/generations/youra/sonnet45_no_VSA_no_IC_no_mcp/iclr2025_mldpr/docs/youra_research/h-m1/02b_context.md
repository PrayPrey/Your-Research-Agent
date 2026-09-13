# Hypothesis Context: h-m1

**Generated:** 2026-08-24
**Source:** 02b_verification_plan.md (auto-extracted)

---

## Hypothesis Information

**ID:** h-m1
**Type:** MECHANISM
**Statement:** Health metrics (usage velocity < 0.3, successor emergence > 3, issue ratio high) automatically surface deprecation candidates, reducing maintainer cognitive burden and increasing deprecation decision consistency with ≥ 60% precision and ≥ 80% recall.

**Rationale:** Validates whether computed health metrics predict actual maintainer deprecation decisions.

**Success Criteria:**
- Precision ≥ 60% (flagged datasets that maintainers actually deprecate)
- Recall ≥ 80% (proportion of actual deprecations that were flagged)
- Metrics computable from HuggingFace download logs + Papers with Code citations + GitHub issues API

---

## Experimental Setup (from Phase 2A)

### Dataset

**Selection:** HuggingFace Datasets Hub Metadata + Usage Logs
**Type:** standard
**Source:** HuggingFace Datasets Hub API, Papers with Code citation data, GitHub issue tracking
**Path:** https://huggingface.co/datasets

**Hypothesis Fit:**
- Provides real-world deprecation events, dataset cards, download logs, and programmatic loaders
- Enables computation of health metrics (usage velocity, successor emergence, issue ratio)
- Contains ground-truth maintainer deprecation decisions for precision/recall validation

### Model

**Selection:** N/A (Infrastructure Research)
**Type:** N/A
**Source:** N/A

**Hypothesis Fit:**
- This hypothesis tests dataset infrastructure mechanisms, not ML model performance
- No model training required

---

## Baseline & Comparison Targets (from Phase 2B)

### Baseline Method
- **Name:** Informal Deprecation (Status Quo)
- **Performance:** Unknown baseline successor adoption rate (to be measured)
- **Dataset:** HuggingFace Datasets Hub (current state)

### Comparison Targets
- **Method:** Datasheets for Datasets (Gebru et al. 2021)
- **Performance:** Documentation completeness but no deprecation lifecycle support
- **Dataset:** General ML datasets

---

## Dependencies and Gate Conditions

**Prerequisites:** h-e1 (Load-time instrumentation infrastructure)
**Gate Type:** MUST_WORK
**Gate Condition:** If precision <60% OR recall <80% → health metrics fail to predict deprecations → STOP

**If Gate Fails:**
- Health metrics don't capture actual deprecation drivers
- Automated detection infeasible
- Dependent hypotheses (h-m3, h-m4) blocked

---

## Variables

**Independent Variable (IV):**
- Health metric computation and deprecation candidate flagging

**Dependent Variable (DV):**
- Precision (%) in prospectively predicting maintainer deprecation decisions
- Recall (%) in prospectively predicting maintainer deprecation decisions

**Control Variables (CV):**
- Repository platform (HuggingFace)
- Observation window (6 months)
- Metric thresholds (velocity <0.3, emergence >3, issue ratio high)

---

## Verification Protocol (from Phase 2B)

**Month 0:**
- Apply health metrics to all non-deprecated HuggingFace datasets
- Flag top 30 deprecation candidates based on usage velocity, successor emergence, and issue accumulation

**Month 6:**
- Compare flagged datasets to actual maintainer deprecation decisions
- Calculate precision (true positives / all flagged) and recall (true positives / all actual deprecations)
- Validate that metrics are computable from existing APIs without requiring new data collection infrastructure

---

**Next Phase:** Phase 2C - Experiment Design
