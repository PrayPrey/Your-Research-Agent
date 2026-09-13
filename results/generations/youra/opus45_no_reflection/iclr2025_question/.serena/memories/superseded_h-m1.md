# Superseded Hypothesis Record

**Date:** 2026-08-19T14:05:00Z  
**Hypothesis:** h-m1  
**Superseded By:** Phase2A-v2 (pending)  
**Status:** SUPERSEDED

## Supersede Reason

Cannot evaluate MUST_WORK gate without H-E1 prerequisite checkpoint. Code implementation complete (11/11 modules, 10/11 FR compliance verified via smoke test). The hypothesis depends on H-E1 C-LoRA embeddings as input to QPT-Net, but h-e1/checkpoints/best_model.pt does not exist in current workspace.

**Root Cause:** H-E1 prerequisite was not executed or checkpoint was not transferred to current working directory before H-M1 Phase 4 execution.

## Compatibility Assessment

| Factor | Score/Result |
|--------|--------------|
| Compatibility Score | N/A (prerequisite missing, not fundamental incompatibility) |
| Recommendation | ROUTED_TO_PHASE_2A |
| Reasoning | Hypothesis design is sound (QPT-Net Wasserstein alignment mechanism). Implementation validated via smoke test (training converges, mode collapse prevented, evaluation suite functional). Cannot proceed to full experiment without prerequisite data. Options: (1) Generate H-E1 checkpoint first, then retry H-M1, or (2) Modify H-M1 to use synthetic/alternative embeddings. |

## Implementation Details

**Code Artifacts:**
- 11 modules implemented: config, data, coin_baseline, qpt_net, train, evaluate, visualize, run_experiment, run_smoke_test, create_synthetic_data, requirements
- Total ~800 LOC
- Functional requirements: 10/11 compliance (FR-1 partial due to missing checkpoint)

**Smoke Test Results (Synthetic Data):**
- Wasserstein distances: MMLU=0.1698, GPQA=0.1794, HumanEval=0.1867 (all > 0.05 threshold)
- Mode collapse: prevented via γ=2.0 nontrivial penalty (std=0.15)
- Training convergence: early stopping at step 100
- **Note:** High W values expected for synthetic data (no real embedding-score correlation)

**Blocker:**
- H-E1 checkpoint path: `h-e1/checkpoints/best_model.pt`
- Status: File not found
- Resolution: Re-run H-E1 experiment or locate existing checkpoint from prior run

## Cascade Effects

**Prerequisite Chain:**
```
H-E1 (EXISTENCE)
  └── H-M1 (MECHANISM) ← BLOCKED HERE
      └── [Dependent hypotheses TBD]
```

No cascade targets identified yet (H-M1 dependents not yet in pipeline).

## Timeline

1. Original hypothesis: h-m1 (QPT-Net Wasserstein alignment)
2. Phase 3 implementation planning: COMPLETED (tier=FULL, 11 tasks)
3. Phase 4 code implementation: COMPLETED (11/11 modules)
4. Phase 4 validation: Smoke test PASS, full experiment BLOCKED
5. INCOMPLETE result detected: Cannot evaluate gate without prerequisite
6. Decision: ROUTE_TO_PHASE_2A (not fundamental failure, prerequisite issue)
7. New direction: Phase2A-v2 (resolve H-E1 dependency)

## Recommendations for Phase 2A

**Option 1: Sequential Execution (Recommended)**
1. Prioritize H-E1 execution in Phase 4
2. Verify H-E1 checkpoint generation (h-e1/checkpoints/best_model.pt)
3. Copy checkpoint to H-M1 workspace
4. Re-run H-M1 full experiment with real embeddings

**Option 2: Hypothesis Modification**
1. Modify H-M1 to use alternative embeddings (e.g., pre-trained uncertainty encoders)
2. Update FR-1 specification to remove H-E1 dependency
3. Re-run Phase 3 implementation planning with new requirements

**Option 3: Synthetic Baseline**
1. Use synthetic embeddings + COIN scores as baseline
2. Document limitation in paper (synthetic data only)
3. Mark as future work (requires H-E1 for full validation)

---
*Superseded at: 2026-08-19T14:05:00Z*
*For cross-phase reference*
