---
hypothesis_id: h-m1
generated_at: "2026-08-05"
source: "JIT generated from 02b_verification_plan.md by Phase 2C step-01"
---

# Per-Hypothesis Context: H-M1

## Hypothesis Information

- **ID:** H-M1
- **Type:** MECHANISM (Step 1 of 3-step causal chain)
- **Gate:** MUST_WORK
- **Prerequisites:** H-P0 (COMPLETED, PASS)

## Statement

Under GroupDRO training on Waterbirds WILDS, the worst-group loss objective upweights minority groups (land-bird on land background, water-bird on water background — background-atypical examples), creating a group-balanced effective loss signal during backbone training that differs from ERM's uniform sample weighting.

## Rationale

This is the initiating mechanism: GroupDRO's training distribution fundamentally differs from ERM by upweighting background-atypical examples. Without this differential signal, no backbone-level change would be expected. Supported by Sagawa 2019 GroupDRO paper and Exchange 3 (Dr. Sage), Exchange 6 (Prof. Vera).

## Variables

- **Independent:** Training objective (GroupDRO worst-group loss vs ERM cross-entropy)
- **Dependent:** Effective loss weighting on minority groups (land-bird-land, water-bird-water)
- **Controlled:** Architecture (ResNet-50), dataset (Waterbirds WILDS), checkpoint source (izmailovpavel)

## Experimental Setup

### Dataset
- **Name:** Waterbirds WILDS
- **Type:** standard
- **Source:** WILDS benchmark (Koh et al. 2021)
- **Path:** `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`
- **Background extraction:** `background_label = group_array % 2` (0=land, 1=water)
- **Groups:** group_array(0=landbird-land, 1=landbird-water, 2=waterbird-land, 3=waterbird-water)
- **Hypothesis Fit:** Dataset contains group labels enabling background minority group identification

### Model
- **Name:** ResNet-50 (12 checkpoints, 3 seeds × 4 methods: ERM, GroupDRO, SAM, DFR)
- **Type:** CNN feature extractor
- **Source:** izmailovpavel/spurious_feature_learning (GitHub / HuggingFace)
- **Cache path:** See H-P0 validation report for checkpoint location
- **Hypothesis Fit:** GroupDRO checkpoints encode the training objective effect; ERM provides control

## Verification Protocol

H-M1 is a **theoretical mechanism confirmation** (BUILD_ON established facts):

1. Confirm via Sagawa 2019 GroupDRO formulation: worst-group loss explicitly upweights worst-performing groups.
2. Identify minority groups in Waterbirds: group_array indices where bird species and background are non-correlated (land-bird on water [group 1], water-bird on land [group 2]).
3. Verify from existing literature that GroupDRO's WGA improvement (0.88 vs ERM 0.72) implies successful minority group performance improvement — consistent with upweighting mechanism.
4. Treat as established theoretical mechanism with empirical consequence measured in H-M2/H-M3.

**Key insight:** H-M1 does NOT require a new experiment — it confirms the theoretical foundation (Sagawa 2019) and empirical evidence (WGA 0.88 vs 0.72) that GroupDRO creates group-balanced gradient signal. The experiment designed here verifies the mechanism via literature search + weight analysis code rather than training from scratch.

## Success Criteria

- **Primary:** Confirmed by Sagawa 2019 theoretical derivation (no new experiment needed — BUILD_ON theoretical foundation)
- **Secondary:** GroupDRO WGA improvement (0.88 vs ERM 0.72 from Izmailov 2022) consistent with mechanism
- **Gate pass:** MUST_WORK — if GroupDRO mechanism doesn't create differential gradient signal, backbone change (H-M2) is unmotivated

## Dependencies and Gate

- **Prerequisites:** H-P0 PASS (confirmed — DFR ≡ ERM backbone, establishes backbone-changing vs preserving distinction)
- **Gate type:** MUST_WORK
- **Fail action:** STOP — mechanism unmotivated; reassess hypothesis

## Previous Context (H-P0)

H-P0 PASSED: DFR and ERM backbones confirmed numerically identical (mean cosine sim ≥ 0.9999, all 3 seeds). ERM background probe accuracy = 0.900 (>0.6 threshold). This confirms:
- DFR is backbone-preserving (head-only retraining)
- GroupDRO/SAM are backbone-changing methods
- Downstream causal chain H-M1→H-M2→H-M3 is valid to pursue
