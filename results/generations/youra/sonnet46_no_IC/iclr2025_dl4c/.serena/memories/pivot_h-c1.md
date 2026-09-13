# H-C1 Phase 4 Result: PIVOT (SHOULD_WORK gate — limitation recorded)

**Hypothesis:** H-C1 — Doctest Prevalence Feasibility (CONDITION)
**Gate:** SHOULD_WORK
**Result:** PIVOT
**Gate satisfied:** false
**Completed:** 2026-08-04T18:03:00Z

## Key Finding

Pilot scan of 10,000 Python files from codeparrot/codeparrot-clean-valid (fallback; bigcode/the-stack-dedup is gated):

| Metric | Value |
|--------|-------|
| doctest_pattern_rate | 0.031 (3.1%) |
| doctest_ast_rate | 0.020 (2.0%) |
| doctest_executable_rate | 0.001 (0.1%) |
| estimated_token_pool_M | 0.004M |

PIVOT: rate < 1% scope threshold. Doctest condition infeasible at 500M token budget.

## Limitation

The doctest execution gate produces too few passing files (~12,960 of 12.96M estimated) to form a 500M-token training corpus. Primary failure mode: `import_error` — files import third-party libraries unavailable in isolated subprocess.

## Pipeline Impact

- **H-E1** proceeds with **2-condition design**: unfiltered vs compile()-filtered (doctest condition dropped)
- H-M1 through H-M4 unaffected (depend on H-E1, not doctest condition)
- Reusable from H-C1: `data_loader.py` (streaming + quality filter + reservoir sample), subprocess wrapper (`_build_wrapper`)
