# Phase Review Plan (PRP): H-E2

**Date:** 2026-07-11  
**Hypothesis:** Common semantic primitives exist across verifiers (Frama-C, Dafny, Why3) that can be abstracted into universal repair categories  
**Version:** 1.0  
**Phase:** 3 - Implementation Planning  

---

## Implementation Budget Allocation

### Epic Tasks Summary

| ID | Task | Complexity | Type | Priority |
|----|------|------------|------|----------|
| A-1 | Setup project structure | 8 | Setup | P0 |
| A-2 | Implement documentation extractors | 14 | High | P0 |
| A-3 | Implement empirical extractors | 16 | High | P0 |
| A-4 | Implement semantic clusterer | 12 | Medium | P0 |
| A-5 | Implement mapping engine | 15 | High | P0 |
| A-6 | Implement coverage computer | 10 | Medium | P0 |
| A-7 | Implement visualizer | 13 | Medium | P0 |
| A-8 | Implement pipeline orchestrator | 11 | Medium | P0 |
| A-9 | Run experiment + generate report | 9 | Medium | P0 |

**Total Complexity:** 108 points

### Budget Breakdown by Complexity Tier

- **VeryHigh (18-20):** 0 tasks, 0 points (0%)
- **High (14-17):** 3 tasks, 45 points (42%)
  - A-2: Documentation extractors (14)
  - A-3: Empirical extractors (16)
  - A-5: Mapping engine (15)
- **Medium (9-13):** 5 tasks, 55 points (51%)
  - A-4: Semantic clusterer (12)
  - A-6: Coverage computer (10)
  - A-7: Visualizer (13)
  - A-8: Pipeline orchestrator (11)
  - A-9: Experiment execution (9)
- **Low (4-8):** 1 task, 8 points (7%)
  - A-1: Setup (8)

### Estimated Timeline

**Total Duration:** 7 weeks (Week 5-12 of overall pipeline)

**Phase Breakdown:**
- **Week 5-6 (A-1, A-2, A-3):** Setup + error category extraction (38 points)
- **Week 7-8 (A-4, A-5):** Semantic clustering + mapping construction (27 points)
- **Week 9-10 (A-6, A-7, A-8):** Coverage computation + visualization + orchestration (34 points)
- **Week 11-12 (A-9):** Experiment execution + validation + reporting (9 points)

---

## Critical Path Analysis

### Dependency Chain

```
A-1 (Setup)
  ↓
A-2 (Doc Extractors) ──┐
  ↓                    │
A-3 (Empirical Ext.) ──┤
  ↓                    │
A-4 (Clusterer) ───────┤
  ↓                    │
A-5 (Mapping Engine) ──┤
  ↓                    │
A-6 (Coverage) ────────┤
  ↓                    │
A-7 (Visualizer) ──────┤
  ↓                    │
A-8 (Orchestrator) ────┤
  ↓                    │
A-9 (Experiment Run) ──┘
```

**Critical Path:** All tasks are sequential → Total complexity = 108 points

**Bottlenecks:**
1. **A-3 (Empirical Extractors):** Highest complexity (16) - Verifier installation and execution harness
2. **A-5 (Mapping Engine):** High complexity (15) - Confidence scoring algorithm design
3. **A-2 (Documentation Extractors):** High complexity (14) - Web scraping robustness

### Parallel Execution Opportunities

**None - Sequential pipeline:** Each stage depends on prior stage outputs
- A-2 & A-3 could theoretically run in parallel (both extract error categories)
- But A-4 (Clusterer) requires both documentation + empirical data → no parallelization benefit

---

## Success Criteria Validation

### MUST_WORK Gate Conditions

**Gate Metric:** Aggregate coverage ≥80%
- **Measurement:** (mapped_categories / total_categories) × 100%
- **Validation:** Automated in `coverage_report.json`
- **Failure consequence:** H-M3 (Semantic Normalization Transfer) cannot proceed

**Secondary Gates:**
1. **Per-verifier coverage ≥80%** (Frama-C, Dafny, Why3 individually)
2. **Abstraction layer feasibility** (Design document with API specification)
3. **Empirical validation** (≥500 total error instances across verifiers)

### Deliverable Checklist

**Phase 3 Outputs (COMPLETED):**
- ✅ 03_prd.md - Product Requirements Document
- ✅ 03_architecture.md - Technical architecture design
- ✅ 03_logic.md - Core logic and algorithms
- ✅ 03_config.md - Configuration schema
- ✅ 03_prp.md - Phase Review Plan (this document)

**Phase 4 Inputs Required:**
- All Phase 3 documents (PRD, Architecture, Logic, Config)
- Verifier installation instructions (from 03_config.md)
- Benchmark program sources (from 03_architecture.md)

**Phase 4 Expected Outputs:**
- `taxonomy_builder.py` - Main pipeline
- `extractors/` - Documentation + empirical extractors
- `clustering/` - Semantic primitive identification
- `mapping/` - Mapping engine + confidence scoring
- `evaluation/` - Coverage computation + visualization
- `data/` - error_categories.json, semantic_primitives.yaml, taxonomy_mapping.json
- `results/` - coverage_report.json
- `figures/` - Heatmap, coverage bars, frequency plots, gate comparison
- `04_validation.md` - Experimental results + gate validation

---

## Risk Mitigation Plan

### High-Priority Risks

**R1: Coverage Below 80% Threshold (MUST_WORK gate failure)**
- **Likelihood:** Medium
- **Impact:** Critical - Blocks H-M3, invalidates cross-verifier portability
- **Mitigation:**
  - Expand semantic primitive set during A-4 if initial coverage <60%
  - Allow multi-primitive assignments in A-5 (one error → multiple primitives)
  - Document tool-specific edge cases as acceptable unmapped categories
  - Fallback: Iterate on taxonomy refinement until coverage passes
- **Monitoring:** Track coverage after A-6 completion (mid-Week 10)

**R2: Verifier Installation Failures**
- **Likelihood:** High (Frama-C/Why3 have complex dependencies)
- **Impact:** Medium - Delays A-3, blocks empirical extraction
- **Mitigation:**
  - Use Docker containers with pre-installed verifiers (Dockerfile in 03_config.md)
  - Pin exact verifier versions: Frama-C 28.1, Dafny 4.9.0, Why3 1.7.2
  - Provide installation scripts for Ubuntu/Debian
  - Fallback: Use documentation-only extraction (skip empirical validation)
- **Monitoring:** Validate installations during A-1 setup

**R3: Documentation Parsing Failures**
- **Likelihood:** Low (stable documentation sources)
- **Impact:** Medium - Incomplete error catalog from A-2
- **Mitigation:**
  - Maintain local snapshots of documentation (fallback if web scraping fails)
  - Supplement with empirical error collection (A-3 compensates)
  - Manual curation of critical error categories
- **Monitoring:** Track extraction success rate during A-2 execution

### Contingency Plans

**If Coverage <80% After Initial Run:**
1. **Week 11:** Analyze unmapped categories (A-6 output)
2. **Week 11:** Refine semantic primitives (iterate A-4)
3. **Week 12:** Re-run mapping construction (A-5) with updated taxonomy
4. **Week 12:** Re-compute coverage (A-6) and validate gate

**If Verifier Installation Fails:**
1. **Fallback to documentation-only mode:** Skip A-3 (empirical extraction)
2. **Rely on A-2 output:** Use documentation error catalogs only
3. **Acknowledge limitation:** Document in 04_validation.md
4. **Adjust success criteria:** Lower total error instance target (500 → 100+)

---

## Phase 4 Handoff Checklist

### Prerequisites Verified
- ✅ Phase 2C experiment design completed (02c_experiment_brief.md)
- ✅ PRD specifies functional requirements (FR-1 to FR-4)
- ✅ Architecture defines 9 Epic tasks with complexity scores
- ✅ Logic provides API specifications and pseudo-code
- ✅ Configuration specifies verifier versions and benchmark sources

### Implementation-Ready Artifacts
- ✅ Epic task breakdown with complexity scores (108 total points)
- ✅ Technology stack specified (Python 3.10+, pandas, matplotlib, BeautifulSoup)
- ✅ Verifier integration commands (Frama-C, Dafny, Why3)
- ✅ Benchmark program sources (git clone URLs, download instructions)
- ✅ Coverage computation formula and threshold validation logic
- ✅ Visualization requirements (heatmap, coverage bars, frequency plots)

### Phase 4 Acceptance Criteria
**Coder Agent MUST produce:**
1. Working code for all 9 Epic tasks (A-1 to A-9)
2. All deliverables from PRD (code artifacts, documentation, outputs)
3. Coverage report with gate validation (coverage_report.json)
4. All required visualizations (figures/ directory)
5. 04_validation.md with experimental results and gate status

**Validator Agent MUST verify:**
1. Code runs without errors on clean environment
2. Coverage metric ≥80% (MUST_WORK gate passes)
3. Per-verifier coverage ≥80% (all three verifiers)
4. All output files generated (data/, results/, figures/)
5. Visualizations match specification (heatmap, bars, gate comparison)

---

## Approval & Sign-off

**Phase 3 Status:** COMPLETED  
**Ready for Phase 4:** YES  
**Gate Status:** Prerequisites satisfied (Phase 2C completed)  

**Next Phase:** Phase 4 - Coding & Validation  
**Estimated Start:** Immediate (unattended mode)  
**Estimated Completion:** Week 12 (7 weeks from start)  

**Archon Integration:** Epic tasks will be converted to Archon project tasks in Phase 4 initialization

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-11  
**Author:** Phase 3 Implementation Planning Agent  
