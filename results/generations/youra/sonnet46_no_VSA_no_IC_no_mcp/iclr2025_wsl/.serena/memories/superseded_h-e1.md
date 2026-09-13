# Superseded Hypothesis Record

**Date:** 2026-08-26T00:00:00Z
**Hypothesis:** h-e1
**Superseded By:** Phase2A redesign (new hypothesis TBD)
**Status:** SUPERSEDED (route_to: phase2a-dialogue)

## Supersede Reason

Gate FAIL: DWSNets (Navon et al. 2023) has a hard architectural constraint (`assert len(weight_shapes) > 2`). The Schürholt MNIST model zoo uses 2-layer MLPs (784→64→10), which produces only 2 weight matrices — incompatible with DWSNets. The gate criterion (DWSNets reproduces published Spearman ρ within ±5%) cannot be satisfied without changing either the encoder or the model zoo. This is a fundamental incompatibility, not a training or hyperparameter issue.

## Compatibility Assessment

| Factor | Score/Result |
|--------|--------------|
| Compatibility Score | 0.0 (hard constraint) |
| Recommendation | SUPERSEDE |
| Reasoning | DWSNets source code enforces M>2 layers; Schürholt zoo is M=2; no parameter tuning can fix this... |

## What Was Learned

1. DWSNets requires M>2 layer target networks — check zoo architecture before selecting encoders
2. `dataset_clf` is degenerate on single-dataset zoos (no class variance)
3. NFT is viable: ρ=0.113 (lr_recovery), ρ=0.110 (gen_gap), ρ=0.104 (accuracy) — best performer
4. 4/5 encoders (flat_mlp, flat_mlp_canon, hyper_repr, NFT) confirmed working with unified data loader

## Cascade Effects

No dependent hypotheses at this stage (h-e1 is a FOUNDATION hypothesis; h-m1/h-m2/h-m3 are NOT_STARTED).

## Recommendations for Phase 2A

1. **Option A:** Drop DWSNets from the benchmark entirely; use NFT as the equivariant encoder
2. **Option B:** Switch to a zoo with 3+ layer networks (e.g., ResNets, VGGs from Schürholt)
3. **Option C:** Revise gate to "NFT produces valid Spearman ρ on 3/4 tasks" — already satisfied

## Timeline

1. Original hypothesis: h-e1 (EXISTENCE gate for DWSNets + NFT compatibility)
2. FAIL result detected: DWSNets hard constraint incompatible with 2-layer MNIST zoo
3. Reflection: Fundamental incompatibility → cannot self-modify
4. Decision: SUPERSEDE → route to /phase2a-dialogue
5. New direction: TBD in Phase 2A

---
*Superseded at: 2026-08-26T00:00:00Z*
*Written by: phase4-coding step-06b (no-MCP ablation — direct file write)*
*For cross-phase reference*
