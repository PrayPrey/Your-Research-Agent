# Dependency Graph (DAG) - Phase 2B

## Dependency Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 3 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
┌─────────────────────────────────────────┐
│  H-E1: Geometric-Semantic Correlation   │
│  Gate: MUST_WORK                        │
│  Test: |ρ| > 0.4, p < 0.001             │
└─────────────────────────────────────────┘
                   │
                   ▼
[Level 1 - Mechanism]
┌─────────────────────────────────────────┐
│  H-M-integrated: 4-Step Causal Chain    │
│  Gate: MUST_WORK                        │
│  Test: PR_high < PR_low, negative slope │
│  Prerequisites: H-E1                    │
└─────────────────────────────────────────┘
                   │
                   ▼
[Level 2 - Boundary Condition]
┌─────────────────────────────────────────┐
│  H-C1: Architecture Invariance          │
│  Gate: SHOULD_WORK                      │
│  Test: |Δρ| ≤ 0.15 across models        │
│  Prerequisites: H-E1, H-M-integrated    │
└─────────────────────────────────────────┘
                   │
                   ▼
           [Verification Complete]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M-integrated → H-C1
Total Levels: 3 (sequential verification)
═══════════════════════════════════════════════════════════
```

## Verification Phases with Gate Conditions

### Phase 1 - Foundation (Gate 1: MUST_WORK)

| Hypothesis | Test | Success Criterion | Gate Action |
|------------|------|-------------------|-------------|
| H-E1 | Correlation validation | Spearman \|ρ\| > 0.4, p < 0.001, 95% CI excludes 0.3 | MUST PASS - If fails, ABANDON entire hypothesis |

**Gate 1 Logic:**
- **PASS:** Geometric features correlate with SE → Proceed to mechanism validation
- **FAIL:** Correlation < 0.3 or not significant → ABANDON - geometric properties don't proxy uncertainty

### Phase 2 - Mechanism (Gate 2: MUST_WORK)

| Hypothesis | Dependencies | Test | Gate Action |
|------------|--------------|------|-------------|
| H-M-integrated | H-E1 | Mechanistic validation of 4-step chain | MUST PASS - If fails, PIVOT to black-box |

**Gate 2 Logic:**
- **PASS:** Subspace collapse validated, correlation direction correct → Proceed to generalization test
- **FAIL:** Mechanism wrong (wrong correlation direction) → PIVOT - use black-box correlation without mechanistic understanding

### Phase 2.5 - Boundary Condition (Gate 2.5: SHOULD_WORK)

| Hypothesis | Dependencies | Test | Gate Action |
|------------|--------------|------|-------------|
| H-C1 | H-E1, H-M-integrated | Cross-architecture validation | SHOULD PASS - If fails, SCOPE to Llama-3 specific |

**Gate 2.5 Logic:**
- **PASS:** \|Δρ\| ≤ 0.15 → Architecture-invariant within Llama family
- **PARTIAL:** 0.15 < \|Δρ\| ≤ 0.25 → Minor calibration needed but generalizes
- **FAIL:** \|Δρ\| > 0.25 or Llama-2 \|ρ\| < 0.25 → SCOPE to Llama-3 specific, document per-architecture calibration requirement

## Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type | Parallel Execution |
|-------|-----------|---------------|-----------|-------------------|
| 0 | H-E1 | None | MUST_WORK | - |
| 1 | H-M-integrated | H-E1 | MUST_WORK | No (sequential) |
| 2 | H-C1 | H-E1, H-M-integrated | SHOULD_WORK | No (sequential) |

**Parallelization Opportunities:** None (sequential dependency chain for PoC verification)

## Critical Path Analysis

**Critical Path:** H-E1 → H-M-integrated → H-C1 (all hypotheses on critical path)

**Bottlenecks:**
- H-E1 gates entire verification (foundation)
- H-M-integrated gates generalization testing
- H-C1 is terminal (no downstream dependencies)

**Execution Order:** Sequential only (no parallel execution in PoC mode)
1. H-E1 first (foundation)
2. H-M-integrated second (mechanism validation)
3. H-C1 third (boundary condition testing)
