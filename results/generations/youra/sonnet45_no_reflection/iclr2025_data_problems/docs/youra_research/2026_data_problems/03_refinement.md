# Phase 2A Refinement Summary

**Generated:** 2026-05-11 01:31:00  
**Workflow:** phase2a-dialogue v10.0.0  
**Gap:** Real-World Contamination-Aware Training Pipelines (gap2)  
**Discussion Exchanges:** 15 (converged)  

---

## Hypothesis Overview

**ID:** H-ContamGeometry-v1  
**Confidence:** 0.80  

### Core Statement

A multi-tier contamination-aware training architecture combining data-layer filters (temporal isolation, structural fingerprinting), manifold-layer behavioral probes (Task Signature Graphs with differential alignment metrics), and geometry-layer trajectory auditing (gradient subspace overlap, Hessian spectral concentration, information efficiency anomalies) can detect both accidental and adversarial contamination with ≥80% combined power at <5% false positive rate, even against adaptive adversaries, because contamination-induced benchmark gains (≥10% accuracy improvement) necessarily produce detectable geometric signatures in parameter-space optimization trajectories that cannot be suppressed without sacrificing the performance advantage (Pareto constraint).

---

## Three-Tier Detection Architecture

### Tier 1: Data Layer (Accidental Contamination)
- **Mechanism:** Temporal isolation + LSH-based structural fingerprinting
- **Target:** ≥95% recall @ <1% FPR on web-scraped exact matches
- **Status:** Production-ready (existing tools)

### Tier 2: Manifold Layer (Behavioral Dynamics)
- **Mechanism:** Task Signature Graph (TSG) probes with differential alignment Δ = (ΔL_invariant - ΔL_neighbor)
- **Target:** ≥80% power to detect EAL-style 1-5% injection @ <5% FPR
- **Status:** Research validation needed for TSG extraction quality

### Tier 3: Geometry Layer (Trajectory Invariants)
- **Mechanisms:**
  - Gradient subspace overlap (cosine similarity with benchmark gradients)
  - Hessian spectral concentration (anisotropic sharpening along benchmark eigendirections)
  - CKA representational alignment (internal representation similarity)
  - Information efficiency anomaly (gain-per-bit vs. null distribution)
- **Inevitability Claim:** Achieving ≥10% gains from ≤5% injection requires detectable low-dimensional parameter alignment
- **Status:** Novel contribution - requires full experimental validation

---

## Key Innovations

1. **Task Signature Graphs:** Paraphrase-invariant abstract constraint manifolds extracted via program synthesis/canonicalization
2. **Differential Alignment Metric:** Separates contamination-specific acceleration from legitimate general skill transfer
3. **Geometric Inevitability Theorem:** Contamination gains require detectable parameter-space alignment; suppressing signals collapses advantage (Pareto constraint)
4. **Multi-tier Complementary System:** Handles accidental (data), behavioral (manifold), and geometric (trajectory) signals

---

## Experimental Validation Plan

### Phase 1: Controlled EAL Replication
- Replicate Dekoninck et al.'s protocol: 1%, 5% paraphrased GSM8K injection
- Target: ~15% accuracy gain (as reported in EAL paper)
- Hyperparameters: lr=2×10⁻⁵, batch=64, epochs≤3
- Seeds: N=20 independent runs per condition

### Phase 2: Multi-Tier Detection
- Apply all three tiers to contaminated runs
- Measure detection power per tier
- Success: ≥80% combined detection @ <5% FPR

### Phase 3: Adaptive Adversary Testing
- Train adversary: max BenchmarkAcc - λ·(ProbeSignal + GeometrySignal)
- Vary λ ∈ {0, 0.1, 0.5, 1.0, 2.0}
- Measure empirical Pareto frontier
- Test inevitability: Does frontier show convex tradeoff?

---

## Testable Predictions

### P1: Tier-Specific Detection
- **Tier 1:** ≥95% accidental, <10% adversarial (expected—paraphrasing evades data-layer)
- **Tier 2:** Differential alignment Δ exceeds clean by ≥2σ for 5% injection
- **Tier 3:** ≥2 of 4 geometric metrics exceed thresholds for 5% injection

### P2: Pareto Frontier Shape
- Suppressing detection signals by 50% costs ≥30% of benchmark gains
- No flat region (high gain + low signal) exists

### P3: Domain Specificity
- Code/math (HumanEval, GSM8K, MATH): ≥80% detection
- Open-ended NLP (TruthfulQA): 50-60% detection (TSG extraction less reliable)

### P4: Differential Alignment Validity
- EAL contamination: Δ > 2σ above clean
- Legitimate broad math training: |Δ| < 0.5σ (both probe types improve equally)

---

## Comparison to State-of-the-Art

| Method | Detection Signal | Paraphrase-Robust? | Performance |
|--------|------------------|-------------------|-------------|
| MIA (Fu et al.) | Instance memorization | ❌ | AUC≈50% pretrain |
| Similarity search | Text/embedding match | ❌ | TPR<2% @ 1%FPR vs. EAL |
| LiveCodeBench | Temporal freshness (eval-side) | ✅ | 100% (by construction) |
| **Our Tier 1** | Temporal + structural | Partial | ≥95% accidental, <10% adversarial |
| **Our Tier 2** | Task-manifold dynamics | ✅ | ≥65% (predicted) |
| **Our Tier 3** | Gradient geometry | ✅ | ≥80% combined (predicted) |

---

## Established Facts (Build On)

1. MIA fails during pretraining (AUC≈50%) because models learn distributions, not instances [Fu et al. 2024]
2. MIA succeeds during finetuning (up to 99.4% AUC) due to structured memorization [Fu et al. 2024]
3. EAL-style paraphrasing evades semantic detection (TPR<2% @ 1%FPR) while achieving ~15% gains [Dekoninck et al. 2024]
4. Continuous temporal monitoring is computationally feasible at scale [LiveCodeBench 2024]

---

## Scope & Boundaries

### In Scope
- Finetuning-phase contamination (where detection signals are strongest)
- Structured domains: code (HumanEval), math (GSM8K, MATH)
- 1-70B parameter models (controlled experiments feasible)
- 1-5% contamination rates (where EAL demonstrates gains)

### Out of Scope
- Pretraining contamination (MIA AUC≈50%, below detection threshold)
- Open-ended creative tasks (TSG extraction unreliable)
- Extremely diffuse contamination (<0.1% injection)
- Models >100B parameters (Hessian computation prohibitive)

---

## Remaining Concerns (Prof. Rex)

1. **TSG Quality for Open-NLP:** Manifold extraction may fail for creative/narrative tasks
   - *Mitigation:* Scope initial validation to code/math where TSG reliable

2. **Smooth Evasion Attacks:** Adversaries could diffuse contamination to blur signals
   - *Mitigation:* Explicitly test in Phase 3 adaptive adversary experiments

3. **Ecosystem Adoption:** Coordination problem across stakeholders
   - *Mitigation:* Target high-stakes benchmarks (coding competitions) where incentives exist

---

## Persona Verdicts

- 🔭 **Dr. Nova (Novelty):** STRONG - Paradigm shift from instance to geometry
- 🔬 **Prof. Vera (Falsifiability):** STRONG - Multiple falsifiable predictions with explicit thresholds
- 🎯 **Dr. Sage (Significance):** STRONG - Addresses field-level problem, enables stable benchmarks
- ⚙️ **Prof. Pax (Feasibility):** STRONG - Tier 1 production-ready, Tier 2-3 computationally feasible

---

## Next Steps (Phase 2B)

Phase 2B will decompose this main hypothesis into detailed sub-hypotheses and verification protocols:
- Sub-H1: Data-layer efficacy (accidental vs. adversarial detection rates)
- Sub-H2: TSG paraphrase-invariance (structural similarity under GPT-4 rephrasing)
- Sub-H3: Differential alignment validity (contamination vs. general training discrimination)
- Sub-H4: Geometric inevitability (Pareto frontier convexity)
- Sub-H5: Domain generalization (structured vs. open-ended detection power)
- Sub-H6: Ecosystem feasibility (computational overhead, audit infrastructure)

---

**Phase 2A Status:** ✅ COMPLETE  
**Phase 2B Readiness:** ✅ READY (all required files generated)
