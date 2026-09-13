# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-08-05
**Hypothesis:** h-e1 (EXISTENCE, Level 0 root)
**Statement:** At least one screened intermediate layer (1-31) per model exhibits class-separable logit-lens statistics on the selection split (corrected AUROC >= 0.55 for at least one (layer, signal) pair) on both TriviaQA and TruthfulQA; LLaMA-2-7B binding case; mandatory A2 anchor (v1 final-layer references ±0.03) before the full sweep.
**Final Status:** COMPLETED (reflection outcome MODIFIED → h-e1-v2)
**Gate Result:** PARTIAL (MUST_WORK, 4/6 criteria, gate.satisfied=false)

## Results
- Validation: PARTIAL — A2 anchor halt gate fired on first cell (llama2/triviaqa: 0.5928 selection / 0.5739 full vs ref 0.5186, tol 0.03); 5/6 cells intentionally unmeasured per FR-4.1 halt semantics
- Gate Type: MUST_WORK
- Reflection: MEANINGFUL FINDINGS — anchor unsatisfiable by construction (reference provenance = 6-way different protocol: random 1000-of-7993 sample, bare prompt, substring labels, generation-time entropy, bfloat16, full-set eval). Mechanism itself fully validated; existence criterion PASSES on the binding cell (best intermediate L31 adj_kl corrected AUROC 0.6522 ≥ 0.55, depth_beats_final vs 0.5928, 20/32 layers retained).
- Lessons: (1) provenance-audit numeric anchors before adopting as halt gates — direction transfers across protocols, magnitude does not; (2) fail-fast anchor ordering saved ~2.5h GPU; (3) donor-cache reuse + 10-example label-agreement verification = 0-GPU cell; (4) adj_kl late layers (L28-31, L17) strongest signals; (5) crashed prior episodes cannot validate protocol assumptions.

## Successor
- **h-e1-v2** (READY): identical existence claim; anchor re-specified as A2-v2 protocol-internal validity (donor identity check + within-sweep final-layer baseline + descriptive v1-direction report). Enters Phase 2C. Reuses `h-e1/code/` (only `check_anchor_and_halt` needs re-spec) and finalized `results/cache_llama2_triviaqa.csv` (splits assigned, seed 42).
- Dependents h-m1/h-m2/h-m3/h-c1 BLOCKED awaiting h-e1-v2.
- Env note: conda youra-h-e1 must keep torch 2.8.0+cu128 (transformers 4.57.6 breaks on torch 2.4.x; env drifted once).

---
*Per-hypothesis snapshot for Phase 2A/2C reference. See `mem:pivot_h-e1_h-e1-v2` for the full pivot record.*
