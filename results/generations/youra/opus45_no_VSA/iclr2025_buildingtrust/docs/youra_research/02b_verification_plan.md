# Phase 2B: Verification Plan
## H-GRC-v1: Generalized Representational Coherence

Generated: 2026-08-08T09:00:00Z

---

## Main Hypothesis

**ID:** H-GRC-v1  
**Statement:** High cross-benchmark correlation in LLM trustworthiness evaluation reflects a shared latent factor (Generalized Representational Coherence) arising from representation stability, detectable via residual PCA after controlling for model scale and training confounds.

---

## Sub-Hypotheses

### H-E1 (Existence) — MUST_WORK
**Statement:** λ₁,residual exceeds 95th percentile of permutation distribution after controlling for log(params) and release date.

- **Type:** EXISTENCE
- **Gate:** MUST_WORK (blocks Phase 5 if fails)
- **Prerequisites:** None
- **Status:** READY
- **Test:** PCA on residualized benchmark matrix; 1000 permutation shuffles
- **Success:** p < 0.05 (observed λ₁ > 95th percentile of permuted λ₁)

### H-M1 (Mechanism) — MUST_WORK
**Statement:** PC1,residual correlates positively with Behavioral Stability Index (BSI) computed on independent datasets (ρ > 0, p < 0.05).

- **Type:** MECHANISM
- **Gate:** MUST_WORK
- **Prerequisites:** H-E1
- **Status:** NOT_STARTED
- **Test:** Pearson correlation between PC1 scores and BSI composite (PAWS/QQP)
- **Success:** ρ > 0, p < 0.05

### H-M2 (Mechanism) — SHOULD_WORK
**Statement:** Instruction-tuning increases both BSI and PC1,residual score within matched base/instruct model pairs (paired t-test p < 0.05).

- **Type:** MECHANISM
- **Gate:** SHOULD_WORK (failure does not block Phase 5)
- **Prerequisites:** H-E1
- **Status:** NOT_STARTED
- **Test:** Paired t-test on ΔBSI and ΔPC1 for matched pairs
- **Success:** Both Δ > 0 with p < 0.05

### H-C1 (Condition) — SHOULD_WORK
**Statement:** Any new trustworthiness benchmark added after PC1 estimation shows loading ≥ 0.3 on frozen PC1 (prospective structural validity).

- **Type:** CONDITION
- **Gate:** SHOULD_WORK
- **Prerequisites:** H-E1
- **Status:** NOT_STARTED
- **Test:** Out-of-sample factor scoring on new benchmarks
- **Success:** Loading ≥ 0.3 for at least 2 independent benchmarks

---

## Dependency Graph (DAG)

```
H-E1 (Existence)
 ├── H-M1 (Mechanism: BSI correlation)
 ├── H-M2 (Mechanism: Instruction-tuning effect)
 └── H-C1 (Condition: Prospective validity)
```

H-E1 is the foundation. All other hypotheses depend on PC1,residual existing.

---

## Risk Assessment

| Hypothesis | Risk Level | Primary Risk | Mitigation |
|------------|------------|--------------|------------|
| H-E1 | LOW | Standard PCA + permutation | Well-established method |
| H-M1 | MEDIUM | BSI construct validity | Use multiple stability proxies |
| H-M2 | MEDIUM | Quasi-causal confounds | Control for release date, family |
| H-C1 | LOW | New benchmark availability | Use held-out existing benchmarks |

---

## Timeline

| Phase | Hypothesis | Duration | Notes |
|-------|------------|----------|-------|
| 2C | H-E1 | 1 week | Foundation experiment design |
| 2C | H-M1, H-M2, H-C1 | 1 week | Parallel after H-E1 |
| 3 | All | 1 week | Implementation planning |
| 4 | All | 2 weeks | PoC validation |
| 5 | Main | 1 week | Baseline comparison |

**Critical Path:** H-E1 → (H-M1 ∥ H-M2 ∥ H-C1) → Phase 5

---

## Dialectical Analysis

**Thesis:** GRC exists as a latent factor beyond scale-driven covariance. Training procedures that increase representation stability improve all trustworthiness dimensions simultaneously.

**Antithesis:** High correlation is a scale confound only. After controlling for log(parameters) and release date, no residual factor structure remains. BSI correlation is spurious.

**Synthesis:** Hierarchical residualization tests both positions. If λ₁,residual > permutation null after stepwise confound control, thesis is supported. Attenuation plot tracks how much variance is explained by each confound layer.

---

## Data Requirements

- **Models:** ~100 from HELM/Open LLM Leaderboard
- **Benchmarks:** TruthfulQA, MMLU, AdvGLUE, BBH, calibration metrics
- **BSI Datasets:** PAWS, QQP (independent from trustworthiness benchmarks)
- **Matched Pairs:** Llama-2/Chat, Mistral/Instruct, etc.

---

## Next Steps

1. Begin Phase 2C with H-E1 (READY status)
2. Generate detailed experiment design for eigenvalue dominance test
3. Progress to H-M1/H-M2/H-C1 after H-E1 validated
