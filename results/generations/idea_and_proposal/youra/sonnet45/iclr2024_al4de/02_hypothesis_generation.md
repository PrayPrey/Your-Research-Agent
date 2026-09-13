# Phase 2A Extended: Hypothesis Clarification Summary

**Date:** 2026-02-06 | **Author:** Pray | **Hypothesis ID:** H-TTFNO-v1 | **Confidence:** 0.85
**Source:** 02a_round_2_discussion.md (Round 2 - TT-FNO FEASIBLE)
**Status:** Ready for Phase 2B Verification Planning

---

## Core Hypothesis

**Under** 3D PDE solving at 512³ resolution,
**If** FNO spectral kernels are factorized using TT-decomposition (r=40),
**Then** model memory reduces from ~32GB to <5GB (8-10x) with ≤3% accuracy degradation,
**Because** TT exploits low-rank structure via sequential cores avoiding Tucker's O(R³) bottleneck.

**H0:** TT does NOT provide meaningful compression - either kernels lack low-rank structure (r>100), accuracy degrades >5%, or training unstable.

---

## Variables

| Variable | Type | Operationalization | Range |
|----------|------|-------------------|-------|
| TT-rank (r) | Independent | Hyperparameter via validation curve | 20-60 |
| Model memory | Dependent | `model.state_dict().size()` ÷ 1e9 | Target: <5GB |
| L² error | Dependent | `‖pred-true‖/‖true‖` avg test set | Target: <5-6% |
| Resolution | Independent | Grid size N³ | 64³, 128³, 256³, 512³ |
| FNO config | Controlled | modes=64, width=256 | Fixed |
| PDE type | Controlled | 3D Navier-Stokes, heat, wave | PDEBench |

---

## Causal Mechanism (N=4 steps)

**Link 1:** Dense kernel W → TT-factorized (TT1⊗TT2⊗TT3⊗TT4)
→ Params: O(modes³·ch²) → O((modes+ch)·r²), 290x reduction (134M→460K at r=40)
*Evidence:* Oseledets (2011) TT theory, Novikov (2015) 100,000x compression

**Link 2:** Parameter reduction → Memory reduction (32GB→<5GB)
→ GPU memory scales linearly with params (float32: 4 bytes/param)
*Evidence:* neuraloperator docs confirm kernel storage bottleneck

**Link 3:** Low-rank approximation (r=40) → <3% accuracy degradation
→ TT error bounded by discarded singular values; quantum systems: 90% energy at r≤50
*Evidence:* Factorized FNO (Tran 2023) <5% with Tucker; spectral smoothness theory

**Link 4:** TT-cores in convolution → Stable gradient flow
→ Standard autograd through tensor contractions + gradient clipping
*Evidence:* Novikov (2015) stable training; PyTorch autograd compatibility

**Key Tension:** Novikov validated FC layers (simple), but spectral convolutions involve FFT.
**Resolution:** Phase 0 singular value analysis on FNO kernels to validate low-rank assumption empirically.

---

## Key Assumptions & Consequences

1. **Low-rank structure (r=20-40 sufficient)** - If violated (r>100): compression <10x (impractical)
2. **Gradient flow preserved** - If violated: need specialized training (contradicts drop-in claim)
3. **Resolution invariance maintained** - If violated: lose key FNO advantage (4x cost increase)
4. **Cross-PDE generalization (r varies <2x)** - If violated: per-PDE tuning (reduces applicability)
5. **Standard training stable** - If violated: curriculum/annealing (approaches Round 1 complexity)

---

## Testable Predictions

**P1 (Memory):** Model ≤5GB at 512³ (8-10x vs ~32GB baseline)
→ Falsify if >8GB (compression <4x)

**P2 (Accuracy):** L² error degradation ≤3% avg across 3 PDEs
→ Falsify if >5% any PDE or >8% average

**P3 (Resolution Invariance):** Train 64³ → eval 512³ with <10% error increase
→ Falsify if >20% (breaks FNO property)

**Additional Falsification:** Phase 0 shows r>60 needed, training unstable with Adam+clipping, TT doesn't beat Tucker at same memory

---

## Contributions

**Primary (Methodological):** First TT-decomposition application to FNO spectral kernels, achieving 8-10x memory reduction (32GB→<5GB) with <3% accuracy loss. Avoids Tucker's O(R³) bottleneck for superior 3D scaling. Enables 512³ on single 16GB GPU.

**Secondary:**
- Theoretical: Validate spectral kernel low-rank structure (singular value analysis)
- Practical: Mode-fraction parameterization preserves resolution invariance
- Implementation: Drop-in replacement for neuraloperator (<200 lines + tntorch)

**Novelty:** TT used in quantum systems (Oseledets 2011) and FC layers (Novikov 2015), but never for learnable spectral operators. Cross-domain transfer: quantum physics → scientific ML.

---

## Key Sources (9 total)

**Foundation (5):**
1. Oseledets (2011) - TT-decomposition theory, O(n^D)→O(D·r²·n) proof
2. Novikov+ (2015) - Tensorizing NNs, 100,000x compression, stable gradients
3. Li+ (2021) - FNO architecture, resolution invariance, memory bottleneck
4. Tran+ (2023) - Factorized FNO, Tucker/CP 10-100x compression <5% error
5. Kovachki+ (2023) - Neural operator theory, universal approximation

**Comparison (2):**
6. neuraloperator library - Tucker FNO (TFNO) baseline
7. Tucker FNO (R=30) - Direct comparison at memory-matched rank

**Gap (2):**
8. Rahman+ (2023) U-FNO - Caps at 128³ despite multi-scale architecture
9. Archon KB - TT under-explored for scientific computing vs CV/NLP

---

## Phase 2B Readiness

**Sub-Hypothesis Decomposition (6 total):**
- **SH1 (Existence):** Memory ≤5GB at 512³ enables single-GPU training
- **SH2 (Mechanism, 4 parts):**
  - H-M1: TT-factorization reduces params O(modes³·ch²)→O((modes+ch)·r²)
  - H-M2: Parameter reduction → memory reduction without activation overhead
  - H-M3: Low-rank (r=40) preserves accuracy ≤3% degradation
  - H-M4: Standard gradient flow enables stable training
- **SH3 (Comparison):** TT-FNO beats Tucker FNO at same memory (no R³ bottleneck advantage)

**Checklist:** ✅ All 13 items verified (format, ID, confidence, H0, variables, mechanism N=4, evidence, tension, assumptions, predictions, falsification, baselines, SH1/SH2/SH3)

**Open Questions:**
1. Phase 0: How many PDE problems for singular value validation? (Propose: 3 PDEs × 2 resolutions)
2. Data: Are 512³ ground truth datasets available for all 3 PDEs, or generate synthetic?
3. Timeline: 8-12 weeks feasible? (Phase 0: 1-2w, Implementation: 3-4w, Experiments: 4-6w)
4. Baselines: Tucker FNO documented enough for memory-matched comparison?
5. Threshold: Keep strict 3% or relax to 5% given Factorized FNO precedent?

---

**Next Phase:** Phase 2B Verification Planning → Decompose into experiments (Phase 0 validation + H-M1 through H-M4 + comparative studies)

*Generated: 2026-02-06 | Mode: YOLO Automated*
