# H-M3: Random Mathlib Tactic Sampling Baseline

**Hypothesis Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Status:** Experiment Design Completed (Phase 2C)

---

## Quick Summary

Tests whether **random tactic sampling from Mathlib corpus distribution** achieves 18-25% success on miniF2F, demonstrating 3-10 percentage point improvement over lean-auto (15.6%) attributable to human tactic frequency patterns alone.

**Predicted:** 20% success (Δ=4.4 pp above lean-auto)  
**Mechanism Tested:** Corpus pattern matching (10% contribution claim from main hypothesis)

---

## Files

### Phase 2C: Experiment Design
- **02c_experiment_brief.md** — Complete experiment specification (Level 1.5)
- **dataset_spec.yaml** — Dataset configuration (miniF2F reuse from H-E1)
- **evaluation_protocol.md** — Metrics, statistical tests, falsification criteria
- **implementation_notes.md** — Pseudo-code, tactic distribution, design rationale
- **02b_context.md** — Phase 2B context and prerequisites
- **metadata.yaml** — Hypothesis metadata and timeline

### Phase 3: Implementation Planning (Not Started)
- 03_prd.md
- 03_architecture.md
- 03_logic.md
- 03_config.md

### Phase 4: Coding & Validation (Not Started)
- code/
- 04_implementation_summary.md
- 04_validation.md

---

## Prerequisites

**H-E1 (COMPLETED):**
- lean-auto baseline: 15.6% [11.5%, 20.3%]
- Tactic count: mean=9.2±4.1
- Infrastructure validated (miniF2F + parallel workers)

---

## Key Design Decisions

### Tactic Distribution
**Weighted sampling** from empirical Mathlib distribution:
- simp (35%), rfl (15%), intro (8%), apply (7%), cases (6%), ...
- Source: LeanDojo (2023), miniF2F tidy baseline (2021), Structured Hints (2026)

### Sampling Strategy
- **Tactic budget:** 15 evaluations (from H-E1 recommendation)
- **Goal selection:** Random (when tactic creates multiple subgoals)
- **RNG seeding:** Deterministic (problem_index → seed)

### Comparison Baseline
- **H-E1 lean-auto:** 15.6% success
- **Statistical test:** One-proportion z-test (one-sided, α=0.05)
- **Target Δ:** [3%, 10%] percentage points

---

## Expected Results

**Success Rate:** 20% (49/244 problems)  
**95% CI:** [15.3%, 25.5%]  
**Δ vs lean-auto:** 4.4 percentage points  
**Statistical Significance:** p < 0.05

**Interpretation:**
- Corpus frequency patterns contribute ~5 pp (10% of main hypothesis gap)
- Supports main hypothesis 10% corpus contribution claim
- Triangulation: lean-auto (15%) < Random Mathlib (20%) < LLM (65%)

---

## Falsification

**REJECT if:**
- Random < 15% (no corpus benefit)
- Random > 30% (corpus >> predicted)
- p > 0.05 (not significant)

**PASS if:**
- Random ∈ [18%, 25%]
- Δ ∈ [3%, 10%] pp
- p < 0.05

---

## Timeline

**Phase 2C:** 4 days
- Day 1: Tactic distribution extraction (4h)
- Day 2: Random sampler implementation (6h)
- Day 3: Evaluation run (2.5h wall-clock, 8 workers)
- Day 4: Statistical analysis (4h)

**Total:** ~16 hours work

---

## Limitations

### Acknowledged
1. **Corpus bias inherent** — random sampling from human proofs encodes implicit heuristics
2. **No semantic understanding** — provides lower bound on corpus contribution
3. **Random goal selection** — human proofs prioritize strategically

### Mitigation
- Use as THIRD baseline for triangulation
- Report as lower bound, not exact measure
- Transparent caveat section in validation report

---

## References

**Primary:**
- miniF2F Benchmark (Zheng et al. 2021)
- lean-auto Prover (Qian et al. 2025)
- Tidy Baseline (Han et al. 2021 PACT)

**Tactic Distribution:**
- LeanDojo (Yang & Song 2023)
- Structured Hints (arXiv:2601.16172)
- miniF2F tidy baseline (arXiv:2109.00110)

**H-E1 Results:**
- verification_state.yaml (lean-auto 15.6%)
- h-e1/02c_experiment_brief.md

---

## Archon Integration

**Project ID:** 622e5a6a-846d-475f-bd6a-8c6080c60cbb  
**Task ID:** 85926db5-cf33-4f0b-84d0-0e66b3edc48e  
**Phase:** Phase 2C (Experiment Design)  
**Next Phase:** Phase 3 (Implementation Planning)

---

**Status:** Phase 2C Complete — Ready for Phase 3 Implementation Planning
