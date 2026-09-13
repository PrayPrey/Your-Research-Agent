# Product Requirements Document: h-c1

**Hypothesis:** DNSI-gap correlation holds across domains: R > 0.3 in vision (ImageNet, CIFAR, ObjectNet) AND R > 0.3 in NLP (HANS/GLUE)
**Type:** CONDITION
**Date:** 2026-08-28
**Gate:** SHOULD_WORK

---

## Executive Summary

This PRD defines requirements for validating that the DNSI-generalization gap correlation (established in h-m1) holds independently within both vision and NLP domains. Success requires |R| > 0.3 with negative correlation in each domain separately.

---

## Problem Statement

h-m1 established aggregate correlation R=-0.950 across 4 benchmarks, but n=4 may be driven by domain differences rather than within-domain mechanism. This experiment stratifies by domain to verify the correlation is not a confounding artifact.

**Key Challenge:** Original NLP domain has n=1 (HANS only). Must expand to n=3 for valid correlation.

---

## Functional Requirements

### FR-1: Data Collection
- **FR-1.1:** Load vision domain data (ImageNet, CIFAR-10, ObjectNet) with DNSI values from h-e1
- **FR-1.2:** Compute DNSI for expanded NLP benchmarks (HANS, PAWS, ANLI)
- **FR-1.3:** Load generalization gap values from published sources

### FR-2: Domain-Stratified Analysis
- **FR-2.1:** Calculate Pearson correlation within vision domain (n=3)
- **FR-2.2:** Calculate Pearson correlation within NLP domain (n=3)
- **FR-2.3:** Calculate Spearman rank correlation for both domains
- **FR-2.4:** Bootstrap CI (10,000 samples) per domain

### FR-3: Cross-Domain Comparison
- **FR-3.1:** Fisher z-transformation for comparing R_vision vs R_nlp
- **FR-3.2:** Test if correlation difference is significant (p < 0.05)
- **FR-3.3:** Verify direction consistency (both negative)

### FR-4: Visualization
- **FR-4.1:** Two-panel scatter plot (Vision | NLP) with regression lines
- **FR-4.2:** Domain comparison bar chart with 95% CI error bars
- **FR-4.3:** Bootstrap distribution comparison (overlaid histograms)

---

## Non-Functional Requirements

- **NFR-1:** Reproducibility via fixed seed (42)
- **NFR-2:** Bootstrap computation under 60 seconds
- **NFR-3:** Clear separation of domain-specific vs cross-domain analysis

---

## Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| Vision correlation | \|R\| > 0.3, negative | MUST |
| NLP correlation | \|R\| > 0.3, negative | MUST |
| Direction consistency | Both negative | MUST |
| Fisher z p-value | p > 0.05 (not significantly different) | SHOULD |

---

## Dependencies

- **h-m1:** DNSI values for ImageNet, CIFAR-10, ObjectNet, HANS
- **h-e1:** DNSI computation methodology
- **External:** Published gap values (Recht 2019, Barbu 2019, McCoy 2019, Zhang 2019, Nie 2020)

---

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| NLP n=3 still minimal | HIGH | Use Spearman + bootstrap, frame as pilot |
| DNSI computation failure for PAWS/ANLI | MODERATE | Fall back to 2 NLP if 1 fails |
| Domain confounding | MODERATE | Report within-domain separately |

---

## Out of Scope

- Model training or fine-tuning
- New benchmark creation
- Per-model analysis within benchmarks
