# Hypothesis h-c1: Expert Consensus Validation

**Status:** Experiment Design Complete (Phase 2C)  
**Type:** CONDITION  
**Gate:** MUST_WORK  
**Date:** 2026-08-28

---

## Hypothesis Statement

High-confidence expert responses (≥4/5 confidence) achieve >70% agreement within ±1 year for major benchmarks (ImageNet, GLUE, SQuAD) when surveyed about saturation timing.

---

## Phase Outputs

### Phase 2C: Experiment Design
- ✅ `02c_experiment_brief.md` - Complete experiment specification (24K, 12 sections)

### Phase 3: Implementation Planning (Pending)
- ⏳ PRD (Product Requirements Document)
- ⏳ Architecture specification
- ⏳ PRP (Phase Review Protocol)
- ⏳ Archon task breakdown

### Phase 4: Coding & Validation (Pending)
- ⏳ Implementation code
- ⏳ Validation report

---

## Quick Reference

**Dataset:** Custom expert survey (real data, NOT synthetic)  
**Sample Size:** 100-150 ML researchers → 30+ high-confidence responses per benchmark  
**Benchmarks:** ImageNet, GLUE, SQuAD saturation timing  
**Success Criteria:** >70% agreement within ±1 year, Fleiss' κ>0.60  
**Implementation Effort:** 24 tasks, ~31 hours + 2-3 weeks collection time (Tier 2)  
**Baselines:** Null hypothesis, raw agreement, Fleiss' kappa  

---

## Files in This Directory

- `README.md` - This file (hypothesis overview and phase tracking)
- `02c_experiment_brief.md` - Full experiment specification (Phase 2C output)

---

## Next Steps

**Phase 3 (Implementation Planning):**
1. Generate PRD with survey design, distribution strategy, analysis requirements
2. Design architecture: data ingestion pipeline, statistical analysis module, visualization
3. Create PRP with task breakdown (DP-01 through VAL-05)
4. Initialize Archon project with Epic-level task structure

**Phase 4 (Coding & Validation):**
1. Implement survey instrument (Google Forms)
2. Distribute survey and collect responses (2-3 weeks)
3. Implement statistical analysis pipeline (agreement rate, Fleiss' kappa, bootstrap CI)
4. Validate against success criteria (>70% agreement, n≥30, κ>0.60)
5. Generate validation report with pass/fail determination

---

## Gate Logic

**MUST_WORK Gate:**
- IF h-c1 PASSES (>70% agreement): Ground truth validated → proceed to H-M1 (score convergence detection)
- IF h-c1 FAILS (<50% agreement): PIVOT to citation-based validation (SOTA mention decay)
- IF h-c1 PARTIAL (mixed results): Use ImageNet validation for vision, citation-based for NLP

**Blocking:** h-c1 blocks all downstream hypotheses (H-M1, H-M2, H-M3) — without validated ground truth, algorithmic detection cannot be evaluated.

---

## Related Hypotheses

**Prerequisites:** None (foundation hypothesis)  
**Blocks:** H-M1 (score convergence), H-M2 (velocity decay), H-M3 (temporal lead time)  
**Parent Hypothesis:** H-E1 (data availability and expert consensus existence)

---

## Research Context

h-c1 validates Assumption A1 from the verification plan:

> **A1:** Expert consensus on saturation dates exists and is measurable (>70% high-confidence agreement within ±1 year). ImageNet saturation timing likely has community consensus around 2017-2020 window (ResNets plateau → ViT arrival).

**If Violated:** Ground truth validation collapses — must pivot to citation-based validation (SOTA mention decay in published papers).

---

**Last Updated:** 2026-08-28  
**Phase:** 2C Complete, 3 Pending
