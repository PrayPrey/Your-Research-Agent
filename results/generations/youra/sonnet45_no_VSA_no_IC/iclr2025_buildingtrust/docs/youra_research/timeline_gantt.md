# Timeline & Gantt Planning
Generated: 2026-08-19

## Time Estimates

### Phase 2C: Experiment Design (Per Hypothesis)
- **H-E1:** 4 hours
  - MCP research: 1h (coupling detection literature)
  - Experiment spec: 2h (MMTrustEval integration, statistical tests)
  - Validation: 1h (completeness check)

- **H-M1:** 3 hours
  - MCP research: 0.5h (partial correlation methods)
  - Experiment spec: 2h (difficulty proxy design)
  - Validation: 0.5h

- **H-M2:** 2 hours
  - MCP research: 0.5h (effect size benchmarks)
  - Experiment spec: 1h (multi-pair validation)
  - Validation: 0.5h

- **H-C1:** 2 hours
  - MCP research: 0.5h (Mantel test implementation)
  - Experiment spec: 1h (cross-model comparison)
  - Validation: 0.5h

**Total Phase 2C:** 11 hours (sequential, ~2 workdays)

---

### Phase 3: Implementation Planning (Per Hypothesis)
- **H-E1:** 6 hours
  - Archon research: 1h (MMTrustEval codebase)
  - PRD/Architecture: 3h (coupling analyzer design)
  - PRP creation: 2h (task breakdown)

- **H-M1:** 4 hours
  - Archon research: 0.5h (scipy.stats partial correlation)
  - PRD/Architecture: 2h (difficulty controller)
  - PRP creation: 1.5h

- **H-M2:** 3 hours
  - Archon research: 0.5h (effect size libraries)
  - PRD/Architecture: 1.5h (multi-pair validator)
  - PRP creation: 1h

- **H-C1:** 3 hours
  - Archon research: 0.5h (scikit-learn Mantel test)
  - PRD/Architecture: 1.5h (cross-model comparator)
  - PRP creation: 1h

**Total Phase 3:** 16 hours (sequential, ~2 workdays)

---

### Phase 4: PoC Validation (Per Hypothesis)
- **H-E1:** 12 hours
  - Data setup: 2h (MMTrustEval dataset)
  - Coding: 6h (coupling analyzer implementation)
  - Validation: 4h (statistical tests + smoke tests)

- **H-M1:** 8 hours
  - Data setup: 0h (reuses H-E1 dataset)
  - Coding: 4h (difficulty control layer)
  - Validation: 4h (partial correlation tests)

- **H-M2:** 6 hours
  - Data setup: 0h (reuses H-E1 dataset)
  - Coding: 3h (multi-pair validator)
  - Validation: 3h (generalization tests)

- **H-C1:** 6 hours
  - Data setup: 0h (reuses H-E1 dataset)
  - Coding: 3h (Mantel test integration)
  - Validation: 3h (cross-model comparison)

**Total Phase 4:** 32 hours (sequential, ~4 workdays)

---

### Phase 5: Baseline Comparison
- **Baseline selection:** 2 hours
- **Baseline adaptation:** 8 hours
- **Comparison experiments:** 6 hours
- **Analysis:** 4 hours

**Total Phase 5:** 20 hours (~2.5 workdays)

---

## Gantt Chart (Workdays)

```
Phase/Hypothesis  Day 1   Day 2   Day 3   Day 4   Day 5   Day 6   Day 7   Day 8   Day 9   Day 10  Day 11
───────────────────────────────────────────────────────────────────────────────────────────────────────────
Phase 2C:
  H-E1           [████]
  H-M1                  [███]
  H-M2                      [██]
  H-C1                         [██]

Phase 3:
  H-E1                            [█████]
  H-M1                                  [████]
  H-M2                                       [███]
  H-C1                                          [███]

Phase 4:
  H-E1                                             [████████████]
  H-M1                                                          [████████]
  H-M2                                                                   [██████]
  H-C1                                                                         [██████]

Phase 5           [████████████████████]
  (overlaps with Phase 4 completion)
───────────────────────────────────────────────────────────────────────────────────────────────────────────
Total Duration:   ~11 workdays (~2.2 weeks)
```

## Critical Path

**Sequential Dependencies:**
1. Phase 2C: H-E1 → H-M1 → H-M2 → H-C1
2. Phase 3: H-E1 → H-M1 → H-M2 → H-C1
3. Phase 4: H-E1 → H-M1 → H-M2 → H-C1
4. Phase 5: After Phase 4 (H-E1 + H-M1 MUST_WORK gates)

**Total Critical Path Time:** ~79 hours (11 workdays)

## Parallelization Opportunities

**None within hypothesis DAG** - strictly sequential due to dependencies.

**Potential parallelization:**
- Phase 5 can start AFTER H-E1 + H-M1 validated (don't wait for H-M2/H-C1)
  - Saves: ~6 hours if baseline comparison starts early

**Optimized Timeline:** ~10 workdays (if Phase 5 overlaps with H-M2/H-C1)

## Contingency Buffers

### API Rate Limit Buffer
- Risk: R4 (API quotas)
- Buffer: +2 hours per hypothesis in Phase 4
- Total buffer: +8 hours

### Difficulty Proxy Rework Buffer
- Risk: R2 (confidence scores invalid)
- Buffer: +4 hours (H-M1 Phase 3/4 rework)
- Trigger: If confidence-based difficulty fails validation

### MUST_WORK Failure Rerouting
- Risk: R5, R6 (H-E1/H-M1 failure)
- Impact: Pipeline stops, route to Phase 0 or Phase 2A-Dialogue
- No buffer - this is expected behavior

### Qualitative Validation Extension
- Risk: R9 (qualitative validation needed)
- Buffer: +4 hours (embedding similarity analysis)
- Trigger: If statistical coupling found but interpretation unclear

**Total Contingency Buffer:** +16 hours (~2 additional workdays)

**Worst-Case Timeline:** 13 workdays (~2.6 weeks)

## Resource Requirements

### Computational
- **Phase 2C/3:** Minimal (planning only)
- **Phase 4:** 
  - API calls: 7,500 requests (500 instances × 3 models × 5 dimensions)
  - Cost estimate: $150-200
  - GPU: Not required (API-only evaluation)

### Human Effort
- **Phase 2C:** 11 hours (autonomous)
- **Phase 3:** 16 hours (autonomous)
- **Phase 4:** 32 hours (autonomous + validation review)
- **Phase 5:** 20 hours (autonomous)

**Total autonomous time:** 79 hours

### MCP Service Dependencies
- **Archon KB:** Phase 3 (implementation research)
- **Serena:** Phase 4 (codebase navigation)
- **Exa/Scholar:** Phase 2C (experiment design literature)

## Milestone Schedule

| Milestone | Target Day | Deliverable |
|-----------|------------|-------------|
| Phase 2C Complete | Day 2 | 4 experiment design documents (02c_*.md) |
| Phase 3 Complete | Day 4 | 4 PRD/Architecture/PRP sets |
| Phase 4 H-E1 Validated | Day 6 | Basic coupling detection working |
| Phase 4 H-M1 Validated | Day 7 | Difficulty control validated |
| Phase 4 H-M2 Validated | Day 8 | Multi-pair generalization confirmed |
| Phase 4 H-C1 Validated | Day 9 | Cross-model comparison complete |
| Phase 5 Complete | Day 11 | Baseline comparison report |
| Phase 6 Ready | Day 11 | Proceed to paper writing |

## Risk-Adjusted Timeline

**Best Case (All Pass):** 10 workdays
**Expected Case (Some SHOULD_WORK Fail):** 11 workdays
**Worst Case (MUST_WORK Fail → Reroute):** 7 workdays + Phase 0 restart

**Recommendation:** Plan for 11-13 workdays (~2.5 weeks) with contingency buffer.
