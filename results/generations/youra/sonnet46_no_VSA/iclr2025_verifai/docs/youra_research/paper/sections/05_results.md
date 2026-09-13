# 5. Results

## 5.1 Oracle Isolation Gap: Contracts Are 4× Stronger Than Differential Testing (RQ1)

The central claim of this paper is that execution-based contract oracle substantially exceeds the differential oracle on contract-violating inputs. Our results confirm this with high statistical certainty and a margin far exceeding the predicted threshold.

**Table 1: Oracle Isolation Gate Metrics (Experiment A — h-m1)**

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Mean oracle-isolation gap | **0.4012** | ≥ 0.10 | ✅ PASS (4×) |
| 95% CI (oracle-isolation gap) | [0.358, 0.445] | — | — |
| Wilcoxon p-value (Holm-corrected) | **5.88e-38** | < 0.01 | ✅ PASS |
| Mean contract-unique mass | **0.4023** | ≥ 0.05 | ✅ PASS (8×) |
| 95% CI (CU mass) | [0.360, 0.447] | CI lower > 0.03 | ✅ PASS |
| Task coverage | 364/364 (100%) | ≥ 90% | ✅ PASS |

Figure 1 shows the oracle isolation gap: the mean contract failure rate (0.997) vs. the mean differential failure rate (0.596) on CVT inputs, with 95% bootstrap CIs. The gap of 0.40 is measured across all 364 tasks and 10,432 (model, task, program) triples.

The key observation is not merely that the contract oracle detects more failures — it is that 40% of evaluations constitute *contract-unique* failures: cases where the LLM program returns the same output as the ground-truth canonical (differential oracle: PASS) while the reference contract asserts that this behavior is semantically invalid (contract oracle: FAIL). This 40% CU mass — shown in Figure 2 as the breakdown by failure category — is 8× the 0.05 threshold and demonstrates that differential testing produces false negatives at a rate far exceeding what additional test quantity could address.

Figure 3 shows the per-task distribution of oracle-isolation gap as a violin plot. The distribution is concentrated above 0.20, with a median well above the 0.10 threshold, confirming that the gap is not driven by a small subset of outlier tasks.

**Stratification by task type:** The oracle-isolation gap is larger for HumanEval+ tasks (mean 0.520, n=117) than MBPP+ tasks (mean 0.345, n=247). This suggests HumanEval+ contracts are more permissive at the function-output level — the LLM program more frequently returns output equal to the canonical while still violating the relational invariant encoded in the postcondition.

**Stratification by model:** The gap is consistent across the 3 models with full coverage: Claude-3-Haiku (0.401), CodeLlama-13B (0.401), CodeLlama-34B (0.411). Model identity explains essentially none of the variance — the gap is a property of task structure and oracle design.

Figure 4 (scatter: differential vs. contract failure rate per task) shows that the contract oracle uniformly detects more failures across the task distribution, with most tasks falling substantially above the diagonal.

## 5.2 Adaptive PBT Contribution: +10pp Consistently Across All Models (RQ2)

Beyond static CVT inputs, adaptive property-based testing finds additional violations by exploring the contract-relevant input space. Our Experiment B quantifies this contribution.

**Table 2: Adaptive PBT Gate Metrics (Experiment B — h-m3)**

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Mean adaptive contribution | **0.0999** | > 0 | ✅ PASS |
| 95% CI (adaptive contribution) | [0.065, 0.133] | CI lower > 0 | ✅ PASS |
| Wilcoxon p-value (one-sided) | **2.64e-22** | < 0.05 | ✅ PASS |
| Tasks with positive contribution | 257/354 (72.6%) | — | — |
| Joined evaluation triples | 17,226 | — | — |

Figure 5 shows the most important pattern of Experiment B: the mean adaptive contribution by model family, with SEM bars. All 5 models cluster in the range 0.099–0.103 — a range of just 0.004 across models spanning 7–34B parameters and open/closed architectures.

This uniformity is striking. It means the ~10pp adaptive contribution is not a property of model quality or architecture — it is a property of the contract oracle and the input space icontract-hypothesis explores. When adaptive PBT finds an additional violation, it reflects the contract specifying behavior on inputs that the static CVT set did not cover, independent of which model generated the program.

Figure 6 (scatter: static CVT failure rate vs. adaptive PBT failure rate per triple) confirms this: the adaptive oracle consistently finds more violations than static CVT inputs, with points uniformly above the diagonal. The distribution of per-task mean adaptive contribution (Figure 7) shows most tasks cluster around the 0.10 mean, with 72.6% showing positive contribution.

**Task type stratification** (Figure 8): Both HumanEval+ and MBPP+ task types show consistent ~10pp adaptive contribution, confirming the effect is not task-type-specific.

**Interpretation:** Adaptive PBT and static oracle are two independent detection layers. Static CVT inputs reveal the semantic gap (0.40) via oracle design; adaptive PBT reveals an additional ~10pp via input exploration. Together, they provide complementary coverage of contract-violating behavior.

## 5.3 Contract Richness Does Not Predict Oracle Gap (RQ3 — Negative Result)

We hypothesized that richer contracts (higher AST complexity tier) would produce larger oracle-isolation gaps, providing a mechanistic gradient for the universal-property mechanism. The data refutes the gradient form of this hypothesis while confirming a threshold effect.

**Table 3: Richness-Gap Correlation (Experiment C — h-m2)**

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Spearman ρ | **0.136** | ≥ 0.30 | ❌ BELOW THRESHOLD |
| p-value (exact permutation) | 5.30e-03 | < 0.05 | ✅ Significant |
| 95% CI (ρ) | [0.034, 0.235] | — | — |

**Per-tier means (oracle-isolation gap):**

| Tier | Name | Mean Gap | N Tasks |
|------|------|----------|---------|
| 1 | Simple | 0.339 | 178 (48.9%) |
| 2 | Structural (BoolOp) | 0.523 | 40 (11.0%) |
| 3 | Relational (any/all) | 0.436 | 117 (32.1%) |
| 4 | Compound | 0.473 | 29 (8.0%) |

The correlation is statistically significant (p = 0.005) but weak (ρ = 0.136), falling substantially below the ρ ≥ 0.30 threshold for a mechanistically meaningful gradient. More importantly, the tier gradient is non-monotonic: Tier 2 (Structural) shows a *higher* mean gap (0.523) than Tier 3 (Relational, 0.436) or Tier 4 (Compound, 0.473).

Figure 9 (scatter: richness score vs. oracle gap per task) and Figure 10 (bar chart of per-tier mean gaps) show this pattern clearly. The gap is high across *all* tiers — the primary predictor is whether a contract exists at all (any tier vs. none), not how complex it is.

**Interpretation:** The oracle-isolation gap reflects a *threshold effect* of contract presence, not a gradient of contract complexity. ContractEval's contracts are primarily input validation (preconditions), and AST complexity of precondition constraints correlates imperfectly with oracle discriminating power. Tier 2 BoolOp contracts function primarily as strict input guards, making them highly likely to fire on CVT inputs designed to violate preconditions.

## 5.4 Cross-Model Orthogonality: Underpowered at n=5 (RQ4 — Partial/Null Result)

**Table 4: Cross-Model Analysis Gate Metrics (Experiment D — h-m4)**

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Kendall τ | **0.40** | ≤ 0.60 | ✅ PASS |
| Permutation p-value | 0.4833 | < 0.05 | ❌ FAIL |
| Partial ΔR² (model identity) | **0.0044** | ≥ 0.10 | ❌ FAIL |
| Cross-model gap (task-controlled) | **0.0069** | ≥ 0.10 | ❌ FAIL |

**Model rankings:**
- By contract-satisfaction: GPT-4o-mini > DeepSeek-Coder-V2-Lite > CodeLlama-34B > CodeLlama-13B > Claude-3-Haiku
- By pass@1*: DeepSeek-Coder-V2-Lite > GPT-4o-mini > Claude-3-Haiku > CodeLlama-34B > CodeLlama-13B

The Kendall τ = 0.40 satisfies the ≤ 0.60 threshold, showing moderate non-monotonicity between contract and pass@1* rankings. However, p = 0.48 indicates this cannot be distinguished from the null (no correlation) at n=5 models. This is a structural constraint: with n=5, the exact permutation test achieves p < 0.05 only for |τ| = 1.0 (minimum achievable p ≈ 0.017 two-sided). The τ = 0.40 finding is consistent with orthogonality but statistically unconfirmable at this sample size.

The ΔR² = 0.004 and cross-model gap = 0.007 are genuine null findings, not power artifacts. After controlling for pass@1* and log(model size), model family identity explains negligible additional variance in contract satisfaction. The between-task variance dominates the between-model variance — some ContractEval tasks are universally hard for all models, regardless of capability tier.

Figure 11 (scatter: contract rate vs. pass@1*), Figure 12 (per-model contract rate bar), and Figure 13 (variance decomposition) illustrate these patterns.

**Summary of Results**

| Hypothesis | Finding | Strength |
|------------|---------|---------|
| h-e1: Gap exists across 364 tasks | 62.6% tasks show ≥1 violation; mean max gap 0.471 | HIGH |
| h-m1: Oracle-isolation gap ≥ 0.10 | Gap = 0.40 (4× threshold); p = 5.88e-38 | HIGH |
| h-m3: Adaptive PBT adds > 0 | Contribution = 0.0999; p = 2.64e-22; uniform across models | HIGH |
| h-m2: Richness gradient ρ ≥ 0.30 | ρ = 0.136; threshold effect not gradient | NEGATIVE |
| h-m4: Cross-model orthogonality | τ = 0.40 consistent but p = 0.48; ΔR² = 0.004 null | PARTIAL/NULL |
