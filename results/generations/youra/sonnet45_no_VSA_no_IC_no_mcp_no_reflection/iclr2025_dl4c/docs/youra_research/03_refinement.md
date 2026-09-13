# Phase 2A Hypothesis Refinement Summary

**Hypothesis ID:** H-StrategicDebug-v1  
**Generated:** 2026-08-28T08:15:00Z  
**Workflow:** Phase 2A-Dialogue (Self-Play Ablation)  
**Exchanges:** 12 (converged)  

---

## Core Hypothesis

**Under** multi-test code generation benchmarks (Codeforces problems with 15+ test cases),  
**If** agents are evaluated on strategic debugging ability (measured via fix-impact-ratio, error clustering, and predictive fixing),  
**Then** high-performing agents will demonstrate measurable superiority in root cause identification and transfer learning compared to baseline random sampling approaches,  
**Because** strategic debugging requires conceptual understanding of code structure and error patterns rather than brute-force iteration.

---

## Key Innovation

Shifts evaluation paradigm from "did it pass the test?" to "how efficiently did it debug?" Three-metric framework (fix-impact-ratio, error clustering, predictive fixing) operationalizes "agentic capability" in measurable, execution-based terms without requiring new benchmarks or human evaluation.

---

## Three Testable Predictions

### P1: Fix-Impact-Ratio > 2.0 (PRIMARY)
High-performing agents demonstrate root cause identification by achieving fix-impact-ratio > 2.0 (one code modification resolves 2+ test failures on average), while baseline agents show ratio ~1.0.

**Test:** Run agents on 50 Codeforces problems with 15+ test cases. For each code modification, count Δpassing_tests.  
**Success:** At least one architecture shows ratio > 2.0 AND p < 0.05 vs baseline.

### P2: Error Clustering Coefficient > 0.3
Agents with conceptual understanding fix similar error types consecutively (clustering coefficient > 0.3), while baseline agents show random ordering (~0.0).

**Test:** Manually label error types for 50 problems × 15 test cases. Measure clustering vs. random baseline.  
**Success:** At least one architecture shows coefficient > 0.3 AND p < 0.05 vs random. Requires Cohen's kappa > 0.7 for labels.

### P3: Held-Out Test Slope > 1.5× Random
Agents exhibit transfer learning by passing held-out test cases (50% held out, error messages not shown) at rate > 1.5× random baseline slope.

**Test:** Reveal 50% of test failures, track held-out pass rate per iteration vs. random mutation baseline.  
**Success:** At least one architecture shows slope > 1.5× random AND p < 0.05 via permutation test.

---

## Experimental Setup

**Dataset:** Codeforces Competitive Programming Problems  
- Filter: solve_count > 1000, rating 1200-1800  
- 15-50 test cases per problem  
- Publicly available, no licensing issues  

**Agents:**  
1. GPT-4 Turbo (baseline)  
2. GPT-4 with memory module  
3. GPT-4 with error analysis prompt  

**Baselines:**  
- Random sampling (no error feedback)  
- Sequential trial-and-error (no clustering)  

**Validation:**  
- Phase 1: 50 problems with manual error labels (8h annotation, kappa > 0.7 required)  
- Phase 2: 200 problems with embedding-based proxy (if Phase 1 validates)  

---

## Persona Verdicts

| Persona | Verdict | Confidence | Key Assessment |
|---------|---------|------------|----------------|
| 🔭 Dr. Nova | STRONG | 0.90 | Paradigm shift: learning curve analysis vs. pass/fail |
| 🔬 Prof. Vera | STRONG | 0.90 | Three rigorous predictions, held-out test methodology airtight |
| 🎯 Dr. Sage | STRONG | 0.85 | Meta-framework contribution, shifts field incentives |
| ⚙️ Prof. Pax | STRONG | 0.85 | Technically feasible, Codeforces data available |
| 🛡️ Dr. Ally | STRONG | 0.85 | Concrete protocol with mitigations, ready for execution |
| 🔍 Prof. Rex | STRONG | 0.80 | Rigorous protocol, weakest link (labeling) mitigated |

**Average Confidence:** 0.86  
**Unanimous Agreement:** Yes  

---

## Remaining Risks & Mitigations

### R1: Inter-annotator agreement < 0.7 (MEDIUM)
**Mitigation:** Pilot 10 problems with 2-3 annotators. If kappa < 0.7, refine taxonomy OR skip P2 and focus on P1 & P3 (label-free).

### R2: Test suite quality variance (LOW)
**Mitigation:** Filter solve_count > 1000, manual review 10 samples before full curation.

### R3: All agents similar performance (LOW)
**Mitigation:** Include diverse architectures (GPT-4, memory, prompting, open-source). If no variance, hypothesis falsified OR framework lacks discriminative power.

### R4: Phase 1 lacks power (LOW)
**Mitigation:** Two-phase design - if p < 0.10 in Phase 1, proceed to Phase 2 (200 problems) for higher power.

---

## Phase 2B Readiness

**Status:** READY  

**Next Steps:**  
1. Curate 50 Codeforces problems (solve_count > 1000, rating 1200-1800)  
2. Pilot error taxonomy annotation (10 problems, kappa check)  
3. Implement permutation test baselines for all three metrics  
4. Run Phase 1 validation across 3 agent architectures  

**Sub-hypothesis hints for Phase 2B:**  
- H-E1: Fix-impact-ratio measurement (primary experiment)  
- H-M1: Root cause identification mechanism  
- H-M2: Error clustering mechanism  
- H-M3: Transfer learning mechanism  
- H-C1: Framework applies to 15+ test case problems only  
- H-A1: Error taxonomy annotatable (kappa > 0.7)  

---

**Discussion Log:** `/docs/youra_research/discussion_log.md` (12 exchanges)  
**Structured Output:** `03_refinement.yaml`, `02_synthesis.yaml`, `final_opinions.yaml`  
