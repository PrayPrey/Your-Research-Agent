# Dependency DAG
Generated: 2026-08-19

## Visual Representation

```
PHASE 2B/2C: Hypothesis Formulation & Experiment Design
│
├─[START]
│    │
│    └──> H-E1: Coupling Exists (MUST_WORK)
│              Status: READY
│              Prerequisites: []
│              │
│              ├── SUCCESS (phi ≥ 0.3, p < 0.01) ───────> H-M1
│              │
│              └── FAIL (no significant coupling)
│                    └──> ROUTE TO PHASE 0
│                         (Research direction fails)
│
│
└──> H-M1: Difficulty-Independent Coupling (MUST_WORK)
       Status: NOT_STARTED
       Prerequisites: [h-e1]
       │
       ├── SUCCESS (partial phi ≥ 0.25) ──────────────> H-M2
       │
       └── PARTIAL/FAIL (coupling disappears)
             └──> ROUTE TO PHASE 2A-DIALOGUE
                  (Mechanism revision needed)


     H-M2: Multi-Pair Coupling (SHOULD_WORK)
       Status: NOT_STARTED
       Prerequisites: [h-e1, h-m1]
       │
       ├── SUCCESS (≥2 models, ≥3 pairs) ─────────────> H-C1
       │                                              │
       │                                              └──> Continue to Phase 5
       │
       └── FAIL (coupling rare)
             └──> Continue to Phase 5
                  (Weaker contribution, still publishable)


     H-C1: Model-Specific Fingerprints (SHOULD_WORK)
       Status: NOT_STARTED
       Prerequisites: [h-e1, h-m2]
       │
       ├── SUCCESS (Mantel r < 0.7) ──────────────────> Phase 5
       │                                              (Fingerprint claim validated)
       │
       └── FAIL (models identical)
             └──> Phase 5
                  (Universal coupling framing)


PHASE 5: Baseline Comparison (DETERMINES_SUCCESS)
│
├── SUCCESS ──────────> PHASE 6 (Paper Writing)
│
└── PARTIAL/FAIL ─────> ROUTE TO PHASE 0
                        (Approach inferior to baseline)
```

## Parallel Execution Opportunities

### Wave 1 (Phase 2C/3/4 Start)
- **H-E1** can start immediately (READY, no prerequisites)

### Wave 2 (After H-E1 Validation)
- **H-M1** can start (prerequisite: h-e1 completed)

### Wave 3 (After H-M1 Validation)
- **H-M2** can start (prerequisites: h-e1, h-m1 completed)

### Wave 4 (After H-M2 Validation)
- **H-C1** can start (prerequisites: h-e1, h-m2 completed)

**Note:** No parallel execution within this DAG - strictly sequential due to dependencies.

## Critical Path Analysis

**Longest Path (H-E1 → H-M1 → H-M2 → H-C1):**
- Total hypotheses: 4
- MUST_WORK gates: 2 (H-E1, H-M1)
- SHOULD_WORK gates: 2 (H-M2, H-C1)

**Critical Path Risk:**
- H-E1 failure: 30% likelihood → Phase 0
- H-M1 failure: 40% likelihood → Phase 2A-Dialogue or Phase 0
- Combined MUST_WORK failure: ~58%

**Phase 5 Eligibility:**
- Minimum requirement: H-E1 + H-M1 PASS
- H-M2/H-C1 failures do NOT block Phase 5

## Dependency Rules

1. **Sequential Execution:** Each hypothesis depends on prior completion
2. **Gate Enforcement:**
   - MUST_WORK FAIL → Stop pipeline, route to Phase 0 or Phase 2A-Dialogue
   - SHOULD_WORK FAIL → Continue to Phase 5 (weaker contribution)
3. **Prerequisite Validation:** Cannot start hypothesis until all prerequisites VALIDATED
4. **Cascading Modification:** If H-M1 modified, H-M2 and H-C1 must be re-evaluated for compatibility

## Routing Decision Points

| Decision Point | Condition | Route | Reason |
|----------------|-----------|-------|--------|
| After H-E1 | FAIL (no coupling) | Phase 0 | Foundational claim refuted |
| After H-M1 | FAIL (difficulty confound) | Phase 0 | Mechanism invalid |
| After H-M1 | PARTIAL (weak control) | Phase 2A-Dialogue | Mechanism needs revision |
| After H-M2 | FAIL (rare coupling) | Continue to Phase 5 | Publishable, weaker claim |
| After H-C1 | FAIL (models identical) | Continue to Phase 5 | Reframe as universal coupling |
| After Phase 5 | PARTIAL (baseline wins) | Phase 0 | Approach fundamentally inferior |

## Hypothesis Interdependencies

**H-E1 (Foundation):**
- Direct dependents: H-M1, H-M2, H-C1
- If modified: ALL downstream hypotheses must be re-assessed
- If failed: Entire research direction fails

**H-M1 (Mechanism Validation):**
- Direct dependents: H-M2
- If modified: H-M2 and H-C1 may need adjustment
- If failed: Critical mechanism invalid → Phase 0

**H-M2 (Generalization):**
- Direct dependents: H-C1
- If modified: H-C1 may need re-scoping
- If failed: Continue with single-model or few-pair coupling

**H-C1 (Differentiation):**
- Direct dependents: None
- If modified: No downstream impact
- If failed: Reframe contribution (no blocking impact)

## Workflow Execution Order

**Phase 2C (Experiment Design):**
1. H-E1 → Design coupling detection experiment
2. H-M1 → Design difficulty control experiment (awaits H-E1 design)
3. H-M2 → Design multi-pair generalization experiment (awaits H-M1 design)
4. H-C1 → Design cross-model comparison experiment (awaits H-M2 design)

**Phase 3 (Implementation Planning):**
1. H-E1 → PRD/Architecture for coupling analyzer
2. H-M1 → PRD/Architecture for difficulty controller (reuses H-E1 code)
3. H-M2 → PRD/Architecture for multi-pair validator (reuses H-E1 + H-M1 code)
4. H-C1 → PRD/Architecture for Mantel test (reuses all prior code)

**Phase 4 (PoC Validation):**
1. H-E1 → Validate basic coupling detection
2. H-M1 → Validate difficulty control (depends on H-E1 results)
3. H-M2 → Validate multi-pair generalization (depends on H-M1 results)
4. H-C1 → Validate cross-model comparison (depends on H-M2 results)

**Checkpoint:** After Phase 4, if H-E1 + H-M1 PASS, proceed to Phase 5.
