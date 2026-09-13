# Hypothesis Refinement Summary

**Generated:** 2026-07-11T09:53:00Z
**Workflow:** Phase 2A-Dialogue (Self-Contained Tikitaka Loop)
**Discussion:** 15 exchanges, converged
**Hypothesis ID:** H-APIContracts-v1

---

## Core Hypothesis

**Under** ML reengineering workflows (computer vision focus),  
**If** researchers validate library behavioral assumptions via executable API contracts at environment-setup time,  
**Then** environment-stage API defects reduce by ≥30% relative to version-pinning + CI baseline (≥25% marginal reduction over CI-only), with ≥5-hour earlier detection (lifecycle shift from training-stage to environment-stage),  
**Because** contracts proactively intercept assumption violations through composition-level invariants (structural, metamorphic, cross-library) that execute in ≤10 seconds before any training begins.

---

## Key Testable Predictions

1. **P1 (Primary):** ≥40% of environment-stage API defects from Jiang et al.'s 348-defect corpus are expressible as version-stable, ≤10s executable invariants
2. **P2:** CI + Contracts uniquely detects ≥25% more environment-stage API defects than CI-only, before training begins
3. **P3:** Median time-to-first-failure reduced by ≥5 hours with CI + Contracts vs CI-only
4. **P4:** False positive rate <5% (contracts don't fail on valid library usage across adjacent versions)
5. **P5:** Same contract library applies to ≥3 distinct repos using the same library version (cross-repo reusability)

---

## Empirical Validation Plan

### Phase 1: Retrospective Contractability Coding
- Extract environment-stage API defects from Jiang et al.'s 348-defect corpus
- Blinded coding: 3 questions per defect (documented invariant exists, ≤10s executable, version-stable)
- Test H₀: contractability ≤30% vs H₁: contractability ≥40%

### Phase 2: Version-Transition Benchmark
- Sample 20 real PyTorch/HuggingFace version transitions from GitHub issues (≥10 comments, API-related)
- Test contracts on unfiltered version pairs, measure detection rate
- Success: ≥50% detection of known API breakages before training, <5% false positives

### Phase 3: Randomized PR-Level Trial
- Select active ML repos (≥1K stars, mirroring Jiang et al. sampling)
- Randomize incoming PRs to: (A) No-CI, (B) CI-only, (C) CI+Contracts
- Measure: environment defects per PR, time-to-first-failure, stage-of-first-failure
- Pre-register stratification by reporter type (58% re-users per Jiang et al.)

---

## Scope & Limitations

**Applies To:**
- ML reengineering workflows using PyTorch, HuggingFace, JAX
- Environment-stage interface/API assumption violations
- Structural, metamorphic, and composition-level binding assumptions

**Does NOT Apply To:**
- Training-stage stochasticity, convergence degradation
- Arbitrary semantic drift requiring full inference
- Performance defects without structural/metamorphic signature
- Custom user code (unless contracts written for internal interfaces)

---

## Novelty & Significance

**Novel Contributions:**
1. First systematic measurement of API defect contractability in ML
2. Library-level behavioral abstraction with cross-repo reusability
3. Auto-generation pathway from documentation (low-friction adoption)
4. Lifecycle-stage shift as measurable outcome (earlier detection, reduced debugging time)

**Field Impact:**
- Targets 46% of environment defects (API-related per Jiang et al.)
- ≥5h earlier detection per failure → thousands of researcher-hours saved annually
- Fourth reproducibility tier: fills gap between dependency pinning and integration testing

---

## Persona Consensus

- **Dr. Nova (Novelty):** STRONG - Genuinely new approach, auto-generation pathway, cross-repo abstraction
- **Prof. Vera (Falsifiability):** STRONG - Pre-registered thresholds, blinded retrospective coding, randomized trial
- **Dr. Sage (Significance):** STRONG - Field-level impact, lifecycle shift, opens future research directions
- **Prof. Pax (Feasibility):** MODERATE - Technically feasible for structural/metamorphic invariants, bounded scope is honest
- **Dr. Ally (Synthesis):** STRONG - Complete experimental design, all concerns addressed, honest about limits
- **Prof. Rex (Rigor):** STRONG (with conditions) - Rigorous validation plan, remaining risks properly identified

**Overall:** READY FOR PHASE 2B

---

## Next Steps

Proceed to **Phase 2B (Research Planning)** with:
- Primary input: `03_refinement.yaml`
- Supporting files: `02_synthesis.yaml`, `01_round_table/final_opinions.yaml`
- Expected output: Verification roadmap with experimental design details
