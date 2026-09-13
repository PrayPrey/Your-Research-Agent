# H-M1 Context: Scale Confound Verification
**Generated:** 2026-07-30 (JIT from 02b_verification_plan.md by Phase 2C step-01)
**Hypothesis ID:** H-M1
**Phase 2B Source:** docs/youra_research/02b_verification_plan.md

---

## Hypothesis Info

**Statement:** Under the joint dataset of N≥30 open-weight LLMs (after H-E1 passes), if MMLU is regressed against TruthfulQA MC2 and BBQ accuracy separately, then both Spearman rho² (MMLU×TruthfulQA) and Spearman rho²(MMLU×BBQ) will exceed 0.05 in the joint dataset, because MMLU captures general capability variation that drives all benchmark scores upward simultaneously (confirmed for AlpacaEval-LC with R²=0.32).

**Type:** MECHANISM
**Gate:** MUST_WORK
**Rationale:** A1 (MMLU valid scale proxy) must be verified in the *joint* dataset — not just for AlpacaEval-LC. If MMLU does not correlate with these alignment benchmarks, partial Spearman controlling MMLU is scientifically invalid.

---

## Variables

- **IV:** MMLU score (0-100, from LLM LB v1 CSV)
- **DV:** Spearman rho²(MMLU, TruthfulQA MC2) and Spearman rho²(MMLU, BBQ accuracy) in joint dataset
- **CV:** Same N open-weight models as H-E1 joint dataset

---

## Experimental Setup (from Phase 2A via Phase 2B)

**Dataset:**
- Name: Open LLM Leaderboard v1 × lighteval/bbq_helm (joint dataset from H-E1)
- Type: programmatic-api
- Source: fboulnois/llm-leaderboard-csv (GitHub) + lighteval/bbq_helm (HuggingFace)
- Path: docs/youra_research/h-e1/code/data/llm_leaderboard_v1/llm.csv (LLM LB v1 cache) + HuggingFace API for bbq_helm
- Hypothesis Fit: Provides MMLU, TruthfulQA MC2, and BBQ accuracy for 297 open-weight models after H-E1 fuzzy join; exactly the joint dataset needed to verify MMLU as scale covariate

**Model:**
- Name: Population of open-weight LLMs (observational cross-section study)
- Type: No ML model; statistical analysis only (scipy.stats, pingouin)
- Source: Joint dataset output from H-E1 (N=297 complete rows)
- Hypothesis Fit: Cross-model structural study; MMLU R² check is a statistical test on existing scores, no training required

---

## Verification Protocol (from Phase 2B)

1. Compute `scipy.stats.spearmanr(df['MMLU'], df['TruthfulQA_MC2'])`; extract rho; compute R²=rho²
2. Compute `scipy.stats.spearmanr(df['MMLU'], df['BBQ_accuracy'])`; extract rho; compute R²=rho²
3. Assert both R² > 0.05; if either fails → document MMLU-alignment orthogonality finding (publishable null)
4. Compute raw Spearman rho(TruthfulQA_MC2, BBQ_accuracy) as baseline for Fisher z comparison

---

## Success Criteria

- **Primary (Gate):** MMLU R²(TruthfulQA) > 0.05 AND MMLU R²(BBQ) > 0.05
- **Secondary:** raw_rho(TruthfulQA, BBQ) computed and logged

---

## Failure Response

- IF MMLU R² ≤ 0.05 for either benchmark: A1 violated; document as "MMLU does not confound alignment benchmarks" — publishable null finding; skip H-M2 Fisher z test

---

## Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Raw Spearman rho (uncontrolled) | rho(AlpacaEval-LC, TruthfulQA MC1) = +0.661 | 52 open-weight models |
| clawrxiv:2603.00394 PCA (6 general benchmarks) | TruthfulQA = PC2 (23.4% variance orthogonal) | 40 models |
| BenchScope ED diagnostic (22 benchmarks) | Open LLM LB effective dimensionality = 1.7 | 8400+ evaluations |

---

## Dependencies

- **H-E1:** PASSED (N=297, match_rate=1.000) — joint dataset available at h-e1/code/data/

---

## Key Assumptions

- A1: MMLU is valid scale proxy for joint dataset — THIS HYPOTHESIS TESTS THIS
- A2: Fuzzy join worked (VALIDATED in H-E1, match_rate=1.000)
- A3: N≥30 (VALIDATED in H-E1, N=297)
