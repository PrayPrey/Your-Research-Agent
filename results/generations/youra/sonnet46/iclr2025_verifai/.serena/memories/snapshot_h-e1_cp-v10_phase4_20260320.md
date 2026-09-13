# Hypothesis Completion Snapshot: h-e1 (H-C_p-v10)

**Date:** 2026-03-20T10:00:00+00:00
**Hypothesis:** h-e1
**Statement:** C_p (mean pairwise normalized Levenshtein similarity across k=5 solutions) is non-degenerate on EvalPlus benchmarks: IQR(C_p) > 0.05 AND mean(C_p) in (0.05, 0.95) for ≥4/5 model-benchmark pairs
**Final Status:** COMPLETED
**Gate Result:** PASS (MUST_WORK)

## Results
- Gate Type: MUST_WORK
- n_pairs_pass: 5/5 (threshold: ≥4/5)
- IQR range: 0.0988–0.1903 (all > 0.05)
- mean range: 0.363–0.509 (all in (0.05, 0.95))

## Per-Pair Summary
- llama3-8b_humaneval: IQR=0.190, mean=0.430 PASS
- llama3-8b_mbpp: IQR=0.105, mean=0.454 PASS
- deepseek-6.7b_humaneval: IQR=0.146, mean=0.363 PASS
- deepseek-6.7b_mbpp: IQR=0.141, mean=0.509 PASS
- codellama-7b_humaneval: IQR=0.099, mean=0.462 PASS

## Unblocked Hypotheses
- h-e2: READY (Spearman correlation test)
- h-m1/m2/m3: NOT_STARTED (await h-e2)

## Archon Task
- task_id: fb0623b4-ec28-4f93-b210-66a706ed7deb
- status: done
- pipeline_project_id: 61a1fc7c-30fc-4622-a9d9-3289cad6e6a2

---
*Per-hypothesis snapshot for Phase 2A reference*
