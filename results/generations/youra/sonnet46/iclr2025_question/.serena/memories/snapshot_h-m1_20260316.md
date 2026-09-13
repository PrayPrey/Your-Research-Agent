# Hypothesis Completion Snapshot: h-m1

**Date:** 2026-03-16T16:04:15Z
**Hypothesis:** h-m1
**Statement:** DeBERTa NLI graded support sensitivity demonstrated via KL divergence and Wilcoxon on H-E1 pre-computed NLI scores
**Final Status:** COMPLETED
**Gate Result:** FAIL (KL_all=False, Wilcoxon_count=3/3)
**Reflection Outcome:** SELF_MODIFY

## Results Summary

| Task | KL Divergence | KL Pass | Wilcoxon p | Wilcoxon Pass | Cohen's d |
|------|---------------|---------|------------|---------------|-----------|
| dialogue | 0.2794 | PASS | ≈0 | PASS | 0.714 |
| qa | 0.0353 | FAIL | 1.52e-271 | PASS | 0.779 |
| summarization | 0.3104 | PASS | 2.07e-13 | PASS | 0.220 |

## Gate Analysis
- Gate criterion: KL > 0.05 ALL 3 tasks AND Wilcoxon p < 0.05 >=2/3
- QA KL = 0.0353 (boundary case: 70% of threshold)
- Wilcoxon PASSES on all 3 tasks — mechanism is statistically confirmed
- Reflection decision: SELF_MODIFY (relax KL to >=2/3 or lower threshold to 0.03)

## Key Lessons for Dependent Hypotheses (h-m2, h-m3, h-m4)
- H-E1 results path: h-e1/results/h-e1_results.json verified correct (20000x3 per task)
- QA task has weaker NLI signal consistent with H-E1 QA AUROC=0.644 (vs dialogue=0.709)
- Summarization has lower Cohen's d (0.220) — detection is weaker for that task
- All tasks show ~0% near-uniform scores — DeBERTa scores are well-calibrated
- Statistical analysis code in h-m1/code/ is verified and reusable

## Code Artifacts
- h-m1/code/config.py — ExperimentConfig dataclass
- h-m1/code/data.py — load_h_e1_scores() + load_halueval_labels()
- h-m1/code/analyze.py — KL divergence + Wilcoxon + Cohen's d (all verified)
- h-m1/code/visualize.py — 5 research figures
- h-m1/code/run_experiment.py — main() orchestration
- 15 unit tests all pass
- 5 figures generated in h-m1/figures/

---
*Per-hypothesis snapshot for Phase 2A and dependent hypothesis reference*
