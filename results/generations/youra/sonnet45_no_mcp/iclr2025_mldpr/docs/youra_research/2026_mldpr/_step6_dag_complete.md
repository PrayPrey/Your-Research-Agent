# Dependency Graph and Phases

## DAG Visualization


═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1 (Existence - Copilot generates acceptable suggestions)
         │
         ▼
[Level 1 - Mechanism Step 1]
    H-M1 (Generation Assistance) ← H-E1
         │
         ▼
[Level 2 - Mechanism Step 2]
    H-M2 (Friction Reduction) ← H-M1
         │
         ▼
[Level 3 - Mechanism Step 3]
    H-M3 (Compliance Preference) ← H-M2
         │
         ▼
[Level 4 - Boundary Condition]
    H-C1 (Language Constraint) ← H-M3
         │
         ▼
    [COMPLETE]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-C1
Total Depth: 5 levels (fully sequential)
Parallelization: None (causal chain dependencies)
═══════════════════════════════════════════════════════════



═══════════════════════════════════════════════════════════
VERIFICATION PHASES WITH GATE CONDITIONS
═══════════════════════════════════════════════════════════

**Phase 1 - Foundation (Gate 1: MUST_WORK)**
| Hypothesis | Test | Gate | Consequence if Fails |
|------------|------|------|---------------------|
| H-E1 | Copilot suggestion acceptance >=70% | MUST_WORK | STOP - entire system invalid |

→ **Gate 1**: If H-E1 fails → ABANDON or major PIVOT required.

---

**Phase 2 - Core Mechanisms (Gate 2: Progressive validation)**
| Hypothesis | Dependencies | Gate | Consequence if Fails |
|------------|--------------|------|---------------------|
| H-M1 | H-E1 | MUST_WORK | Step 1 mechanism fails - explore alternatives |
| H-M2 | H-M1 | SHOULD_WORK | Document limitation - friction not reduced |
| H-M3 | H-M2 | SHOULD_WORK | Quality goal unmet - scope reduction |

→ **Gate 2**: H-M1 must pass. H-M2/H-M3 failures = narrowed scope, not full failure.

---

**Phase 3 - Boundary Conditions (Gate 3: Optional)**
| Hypothesis | Dependencies | Gate | Consequence if Fails |
|------------|--------------|------|---------------------|
| H-C1 | H-M3 | SHOULD_WORK | Confirms known limitation - expected |

→ **Gate 3**: Failure expected and acceptable - documents scope boundary.

═══════════════════════════════════════════════════════════



━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Hypothesis | Prerequisites | Gate Type | Phase |
|-------|-----------|---------------|-----------|-------|
| 0 | H-E1 | None | MUST_WORK | Phase 1 |
| 1 | H-M1 | H-E1 | MUST_WORK | Phase 2 |
| 2 | H-M2 | H-M1 | SHOULD_WORK | Phase 2 |
| 3 | H-M3 | H-M2 | SHOULD_WORK | Phase 2 |
| 4 | H-C1 | H-M3 | SHOULD_WORK | Phase 3 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Hypotheses: H-E1, H-M1 (must pass)
Progressive Hypotheses: H-M2, H-M3 (should pass, failures narrow scope)
Boundary Hypotheses: H-C1 (expected to fail, confirms limitation)

