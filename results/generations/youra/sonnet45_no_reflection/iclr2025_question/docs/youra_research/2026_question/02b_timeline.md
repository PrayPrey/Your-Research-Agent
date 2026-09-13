# Timeline Planning - Phase 2B

## Gantt Timeline Visualization

```
═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 3 Hypotheses (Sequential Execution)
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis       │ Week 1-2  │ Week 3-4  │ Week 5    │ Week 6    │
───────────────────────┼───────────┼───────────┼───────────┼───────────┤
PHASE 1: Foundation
  H-E1 Correlation     │ ████████  │           │           │           │
  [Gate 1: MUST_WORK]  │           │ ◆         │           │           │
───────────────────────┼───────────┼───────────┼───────────┼───────────┤
PHASE 2: Mechanism
  H-M-integrated       │           │ ████████  │ ████      │           │
  [Gate 2: MUST_WORK]  │           │           │           │ ◆         │
───────────────────────┼───────────┼───────────┼───────────┼───────────┤
PHASE 2.5: Boundary
  H-C1 Architecture    │           │           │           │ ████████  │
  [Gate 2.5: SHOULD]   │           │           │           │         ◆ │
───────────────────────┼───────────┼───────────┼───────────┼───────────┤
═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks (PoC verification mode)
═══════════════════════════════════════════════════════════════════════════════
```

## Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M-integrated → H-C1

Total Duration: 6 weeks
  Formula: 2 (H-E1 foundation) + 3 (H-M mechanism) + 2 (H-C1 boundary) = 7 weeks
  Optimized: Overlap H-M and H-C1 planning reduces to 6 weeks

Slack Available: 0 weeks (all hypotheses on critical path)

Gate Points:
- Week 2: Gate 1 (H-E1) - MUST_WORK
- Week 5: Gate 2 (H-M-integrated) - MUST_WORK  
- Week 6: Gate 2.5 (H-C1) - SHOULD_WORK

Critical Path Implications:
- Any delay in H-E1 delays entire verification
- H-M-integrated gates H-C1 execution
- No parallelization opportunities (sequential dependencies)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 3
- Existence: 1 (H-E1)
- Mechanism: 1 (H-M-integrated, covers 4 causal steps)
- Condition: 1 (H-C1)

Verification Phases: 3
1. Foundation (H-E1) - Weeks 1-2
2. Mechanism (H-M-integrated) - Weeks 3-5
3. Boundary (H-C1) - Week 6

Total Duration: 6 weeks (PoC mode)
Critical Path Length: 6 weeks
Execution Mode: Sequential chain (no parallelization)

Computational Resources:
- GPU: 1x (Llama-3-8B-Instruct + Llama-2-7B for H-C1)
- Dataset: TruthfulQA (817 questions, pre-loaded)
- Ground Truth: SE computed once, reused across hypotheses
- Estimated Total GPU Hours: ~12-18 hours (full pipeline)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Execution Order

**Step 1**: Execute H-E1 (Foundation) - Weeks 1-2
- Compute geometric features (PR, eigenvalue decay, condition number) for all TruthfulQA questions
- Compute ground truth SE (K=10 sampling + DeBERTa-NLI clustering)
- Calculate Spearman correlation on test set
- Bootstrap validation (1000 resamples) for stability check

**Step 2**: Evaluate Gate 1 → MUST_WORK checkpoint
- **PASS** (|ρ| > 0.4, p < 0.001): Proceed to H-M-integrated
- **FAIL** (|ρ| < 0.3): ABANDON entire hypothesis, geometric features don't proxy uncertainty

**Step 3**: Execute H-M-integrated (Mechanism) - Weeks 3-5
- Split test set by median SE (high vs low uncertainty)
- Compare geometric features between groups (t-test)
- Validate correlation directionality (negative PR~SE, positive κ~SE)
- Ablation study: test layer ranges (16-23, 20-27, 24-31)
- Control validation: epistemic vs non-epistemic tasks

**Step 4**: Evaluate Gate 2 → MUST_WORK checkpoint
- **PASS** (mechanism validated): Proceed to H-C1
- **FAIL** (wrong mechanism): PIVOT to black-box correlation without mechanistic understanding

**Step 5**: Execute H-C1 (Architecture Boundary) - Week 6
- Replicate H-E1 on Llama-2-7B
- Compare correlation magnitudes (|Δρ| between Llama-2 and Llama-3)
- Test layer selection strategies (fixed vs proportional)

**Step 6**: Evaluate Gate 2.5 → SHOULD_WORK checkpoint
- **PASS** (|Δρ| ≤ 0.15): Architecture-invariant, generalization validated
- **PARTIAL** (0.15 < |Δρ| ≤ 0.25): Minor calibration needed
- **FAIL** (|Δρ| > 0.25): SCOPE to Llama-3 specific, document calibration requirement

**Final**: Verification complete, proceed to Phase 2C (Experiment Design) or Phase 4.5 (Synthesis) depending on all hypotheses' results
