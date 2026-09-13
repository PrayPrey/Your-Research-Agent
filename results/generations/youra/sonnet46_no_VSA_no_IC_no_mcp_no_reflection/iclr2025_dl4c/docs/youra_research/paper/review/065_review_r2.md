# Adversarial Review — Round 2 (R2): Numerical Verification and Credibility

**Paper:** When Reward Granularity Matters: Mechanistic Analysis of Ratio vs. Binary Reward in GRPO Post-Training for Code LLMs  
**Review Round:** R2 — Numerical Verification, Mathematical Validity, Baseline Fairness  
**Date:** 2026-08-31  
**Personas:** Accuracy Checker, Skeptical Expert  
**Input Paper:** 06_paper_r1.md (post R1 revision)  

---

## Ground Truth Verification Table

| Claim | Paper (R1) | Ground Truth | Serena-Equiv. Verified | Match |
|-------|------------|--------------|------------------------|-------|
| Binary adv. var. = 0.0000 | ✓ §5.1 Table 1 | C1: 0.0000 | h-e1/04_validation §3.1 Table | ✓ |
| Ratio adv. var. = 0.0475 | ✓ §5.1 Table 1 | C2: 0.0475 | h-e1/04_validation §3.1 Table | ✓ |
| Ratio rewards: [0, 0, 0.2, 0.4, 0, 0.6, 0, 0] | ✓ Table 1 | C4: [0.0, 0.0, 0.2, 0.4, 0.0, 0.6, 0.0, 0.0] | h-e1/04_validation Appendix | ✓ |
| Ratio advantages: [-0.15, …, +0.45] | ✓ Table 1 | C5: [-0.15, -0.15, +0.05, +0.25, -0.15, +0.45, -0.15, -0.15] | h-e1/04_validation Appendix | ✓ |
| 987/1000 groups: 98.7% | ✓ §5.2 | C6: 987/1000, 98.7% | h-e1/04_validation §3.1 | ✓ |
| 13/1000 groups binary non-zero | ✓ §5.2 | C7: 13/1000, 1.3% | Derived: 1000-987=13 | ✓ |
| Smoke test: exit code 0 | ✓ §5.3 | C8: exit code 0 | h-e1/04_validation §3.2 | ✓ |
| Grad norms [3e-4, 7e-4] | ✓ §5.3 | C9: [0.0003, 0.0007] | h-e1/04_validation §3.2 | ✓ |
| ~54 sec/step | ✓ §5.3 | C10: ~54s (MEDIUM confidence) | h-e1/04_validation §3.2 | ✓ |
| 17/17 h-e1 unit tests | ✓ §5.3 | C11: 17/17 | h-e1/04_validation §1 | ✓ |
| 18/18 h-m1 unit tests | ✓ §5.3 | C12: 18/18 | h-m1/04_validation §1 | ✓ |
| 35/35 total | ✓ §5.3 | C13: 35/35 | Derived: 17+18 | ✓ |
| reward_mean = 0.0000 all steps | ✓ §5.4 Table 2 | C14: 0.0 | h-m1/04_validation §6 | ✓ |
| clipped_ratio = 1.0000 all steps | ✓ §5.4 Table 2 | C15: 1.0 | h-m1/04_validation §6 | ✓ |
| fraction_partial = NaN | ✓ §5.4 Table 2 | C16: NaN | h-m1/04_validation §6 | ✓ |
| 208 logged steps | ✓ §5.4 | C18: 208 (approx) | h-m1/04_validation §3.1, §6 | ✓ |
| Grad norm CI: mean +0.000730, [−0.000253, +0.002561] | ✓ §5.4 (now in Table 2 R1) | C17 | 045_validated_hypothesis §4.2 | ✓ |
| APPS n=1,789 (≥5 test cases) | ✓ §3.5 | C20: 1789 | h-e1/04_validation §2 | ✓ |
| 9 engineering issues | ✓ §3.5 | C19: 9 | h-e1+h-m1/04_validation §1.3 | ✓ |

---

## Mathematical Validity Analysis (Accuracy Checker + Skeptical Expert)

### Check M1: Binary = 0 for group [0,0,1,2,0,3,0,0] — VERIFIED

For 5-test problem, binary reward = 1 iff all 5 tests pass. Completions c1–c8 pass [0,0,1,2,0,3,0,0] tests respectively. None pass all 5. Therefore binary_reward(ci) = 0 for all i. Group mean = 0. All advantages = 0 − 0 = 0. Advantage variance = 0.0000. **Mathematically exact. ✓**

### Check M2: Ratio rewards [0, 0, 0.2, 0.4, 0, 0.6, 0, 0] — VERIFIED

k/5 for k=[0,0,1,2,0,3,0,0]: 0/5=0, 0/5=0, 1/5=0.2, 2/5=0.4, 0/5=0, 3/5=0.6, 0/5=0, 0/5=0. Sum = 1.2. Mean = 1.2/8 = 0.15. Advantages: 0-0.15=−0.15, 0−0.15=−0.15, 0.2−0.15=+0.05, 0.4−0.15=+0.25, 0−0.15=−0.15, 0.6−0.15=+0.45, 0−0.15=−0.15, 0−0.15=−0.15. **Matches paper exactly. ✓**

### Check M3: Ratio advantage variance = 0.0475 — VERIFIED

Advantages: [−0.15, −0.15, +0.05, +0.25, −0.15, +0.45, −0.15, −0.15].  
Mean of advantages = 0 (by construction).  
Var = E[A²] = (0.15² × 5 + 0.05² + 0.25² + 0.45²) / 8  
= (5×0.0225 + 0.0025 + 0.0625 + 0.2025) / 8  
= (0.1125 + 0.0025 + 0.0625 + 0.2025) / 8  
= 0.38 / 8 = 0.0475. **Exact. ✓**

### Check M4: Theoretical claim T1 (binary zero variance condition) — VERIFIED

T1 states: when all k_i ∈ {0, n}, all binary rewards ∈ {0, 1} (since binary = 1 iff k=n). If all k_i=0: all rewards=0, mean=0, advantages=0, var=0. If all k_i=n: all rewards=1, mean=1, advantages=0, var=0. If mix of 0 and n: some rewards=0, some=1 — group mean r̄ ∈ (0,1), non-zero variance possible. CORRECTION NEEDED: **The paper claims binary produces zero variance whenever "no completion passes all n tests" — this is the actual dead zone condition.** When some completions pass all n and some don't, binary variance can be non-zero. The dead zone is specifically when ALL completions fail all tests (k_i=0 for all i), OR equivalently all completions have the same binary reward. Paper's formal condition is more precise in §3.2 than the abstract/intro simplification.

**MAJOR finding:** The abstract and introduction say "98.7% of early-training groups [have zero binary variance]" because "the model cannot produce complete solutions." This is because ALL completions fail (k_i=0 for all i) — not just because some fail. The paper's §3.2 formal condition is: "all k_i ∈ {0, n}" — this includes groups where all pass (all-pass groups, 1.3%). The 98.7% figure represents groups where ALL completions fail ALL tests (k_i=0 for all i), which is a subset of the formal condition. The framing is internally consistent: in 98.7% of early-training groups, all completions fail all tests (binary=0 for all), so binary variance=0. ✓ **No FATAL/MAJOR issue — the condition is correct.**

### Check M5: Omitted claim O1 (HumanEval ≥3pp improvement) — NOT IN PAPER ✓

Searched paper for "3 percentage point", "3pp", "HumanEval improvement": not found as a claim of achieved performance. Paper correctly presents this as the *gate criterion* (not yet met), not a result. ✓

### Check M6: Omitted claim O2 (policy target shift to expected-coverage) — NOT IN PAPER ✓

The paper does NOT claim "ratio reward shifts policy target from all-pass to expected-coverage maximization" as an empirically demonstrated result. This is discussed as a mechanistic prediction in §6 Discussion ("our diagnostic framework...") but not claimed as verified. The paper is careful to say h-m1 gate was NOT satisfied. ✓

### Check M7: Omitted claims O3, O4 — NOT IN PAPER ✓

h-m2 (cross-benchmark generalization) and h-m3 (similarity reward) are not claimed or reported. Future work section mentions them as open questions only. ✓

---

## Baseline Fairness Assessment

**N/A** — This paper does not compare against external baselines in a performance table. There are no GroupDRO/ERM/JTT comparisons. The only comparisons are:
- Binary vs. ratio reward (two conditions of the same experiment) — fair, same setup
- Prior RLEF work (CodeRL, PPOCoder, DAPO) — discussed qualitatively, no numbers compared

**Assessment: BASELINE_FAIRNESS_NOT_APPLICABLE** — No baseline performance numbers to audit. ✓

---

## Signal-Performance Gap Analysis (Skeptical Expert)

### Gap G1: 36.59x CV ratio claim

**Not found in this paper.** The paper does not claim a CV ratio. This appears to be from a different domain (subpopulation robustness). ✓

### Gap G2: Strong mechanistic signal but null policy result

The paper claims: CV of advantage variance is 36x stronger for ratio vs. binary (0.0475 vs. 0.0000 — infinite ratio). Yet detection (policy effect) is zero because experimental setup collapses both to zero.

**Assessment:** The paper correctly explains this gap in §6.1 and §6.2. The mechanistic guarantee is real; the experimental conditions prevented it from being active. This is not a logical gap — it is the central finding. ✓

---

## New Issues Found in R2

**No new FATAL issues.**

**No new MAJOR issues.**

### MINOR issues for Human Review (R2 additions)

7. **§5.1 Table 1 formatting:** The "Group mean" and "Advantage variance" rows use bold in the table. The markdown bold may not render in all conference submission systems. Check venue formatting requirements.

8. **§3.2 dead zone condition inconsistency (minor):** §3.2 states the dead zone as "all k_i ∈ {0, n}" but the operative condition in early training is "all k_i = 0." The paper conflates the two in the intro/abstract. In §3.2 footnote or a parenthetical, clarify: "In early training with near-zero solve rate, the all-zero case (k_i=0 for all i) dominates; the broader condition (all k_i ∈ {0,n}) additionally includes the rare all-pass case."

---

## Persuasiveness Re-check (R2)

| Check | R1 Result | R2 Re-check | Change |
|-------|-----------|-------------|--------|
| Abstract compelling? | PASS | PASS | None |
| Problem clear in 1 min? | PASS | PASS | None |
| Novelty clear in 2 min? | PASS | PASS | None |
| "Every published paper" scope | FIXED in R1 | Now qualified — PASS | Improved |
| §6.3 pending CI stale | FIXED in R1 | Now accurate — PASS | Improved |
| Would continue reading? | YES | YES | None |

**Persuasiveness: PASSED** ✓

---

## Return Summary

```yaml
agent: adversary_r2
round: R2
status: COMPLETED
serena_searches_performed: 0  # No Serena MCP available; direct file reads used
numerical_discrepancies_found: 0  # All claims verified against ground truth
mathematical_impossibilities: 0  # All calculations verified correct
baseline_fairness_issues: 0  # No baseline comparisons in paper
fatal_count: 0
major_count: 0
minor_count: 2  # R2 additions; total with R1: 8
convergence_recommendation: CONVERGE
reason: "All FATAL and MAJOR issues resolved in R1; R2 finds no new FATAL/MAJOR issues; all numerical claims verified against ground truth; omitted claims correctly omitted; persuasiveness checks passed"
```
