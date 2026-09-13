# Adversarial Review Report — Round 1
**Paper:** "When the Signal is Real but the Training is Not: Variance-Guided RLEF Data Selection and the Cold-Start Problem"
**Review Date:** 2026-08-21
**Reviewer:** Phase 6.5 Adversary Agent (3-Persona)

---

## Ground Truth Verification Table

| Claim | Paper States | Ground Truth | Status |
|---|---|---|---|
| MBPP nonzero-variance problems | 7.8% (29/374) | 29/374 = 7.78% | PASS |
| All-fail rate | 91.7% | 343/374 = 91.71% | PASS |
| All-pass rate | 0.5% | 2/374 = 0.53% | PASS |
| mean_var_selected | 0.1113 | 0.1113 | PASS |
| mean_var_random | 0.0262 | 0.0262 | PASS |
| Variance ratio | 4.24× | 4.24 | PASS |
| Mann-Whitney p | 2.22e−06 | 2.22e−06 | PASS |
| Profiling runtime | ~32 seconds | ~32 seconds | PASS |
| Total generation attempts | "40,000+" | 50,000 (>40,000 ✓) | PASS |
| h-m2: 10,000 attempts | 50×50×4 | 10,000 | PASS |
| frac_reward_zero_std | 1.0 all steps, both | 1.0 confirmed | PASS |
| Cold-start persists at doubled LR | confirmed | h-m3 confirmed | PASS |
| k (profiling) | k=4 (design k=8) | k=4 | PASS |
| max_new_tokens (profiling) | 128 | 128 | PASS |
| max_completion_length (training) | 512 | 512 | PASS |
| "~13 unique rollouts per 50 steps" | plausible claim | not directly measured | UNVERIFIED |
| "parameter mismatch is MOST LIKELY root cause" | stated as most likely | hypothesis only, not confirmed | WEAK |
| "~8 hours sequential HF at k=8, max_new_tokens=512" | estimated | estimated | UNVERIFIED |

---

## Executive Summary

| Severity | Count |
|---|---|
| FATAL | 0 |
| MAJOR | 3 |
| MINOR | 5 |

**Recommendation: MAJOR REVISION REQUIRED**

All numerical claims check out against ground truth. The paper has no fatal accuracy errors. However, three major weaknesses make it vulnerable to reviewer rejection: (1) the main empirical contribution is a null result with a single unconfirmed hypothesis for why it failed; (2) novelty framing is weak given the problem is well-known in RL literature; (3) the paper's scope is too narrow for a full ICML paper without the confirmed resolution of the cold-start problem.

---

## PERSONA 1: Accuracy Checker Findings

**Finding AC-1 — MINOR: "40,000+" undercounting presentation**
The paper says "40,000+ generation attempts" in the abstract. The actual total is 50,000 (h-m2: 10,000 + h-m3: 40,000). The claim is technically correct (50,000 > 40,000) but deliberately conservative. Reviewers who do the arithmetic (50 steps × 50 problems × 4 + 200 steps × 50 problems × 4 = 50,000) will notice. Recommend: state "50,000 total generation attempts" for precision, or "40,000+ (h-m3 alone)" and separate clearly.

**Finding AC-2 — MAJOR: Unverified "~13 unique rollouts" claim**
Section 5 (or Discussion) references approximately 13 unique rollouts per 50 steps. Ground truth notes this is PLAUSIBLE but not directly measured. Any reviewer who asks for the deduplication log will find it unsupported. Either provide the measurement or remove the claim.

**Finding AC-3 — MAJOR: Root cause framed as confirmed when it is a hypothesis**
The abstract and conclusion present parameter mismatch (max_new_tokens=128 vs max_completion_length=512) as "the most likely cause." Section 5 correctly hedges. However, Section 6 (Discussion) and the abstract treat this as the explanation without ruling out alternatives: wrong dataset split (ground truth notes dataset_subset="full" not "sanitized"), model degradation under training-mode temperature, or TRL sampler bugs. The paper should explicitly enumerate and rank alternative hypotheses, not just name one.

**Finding AC-4 — MINOR: k design vs execution inconsistency unexplained**
The paper states "design was k=8, max_new_tokens=512 — reduced due to hardware constraints and vLLM-TRL incompatibility." The implications of k=4 vs k=8 for variance estimates are not discussed. At k=4, observable variance states are {0, 0.25, 0.5, 0.75, 1.0}×(1−p), giving coarser resolution. This could affect which problems are selected. A one-paragraph analysis is needed.

**Finding AC-5 — MINOR: Variance formula labeling**
Ground truth shows 29 problems at variance=0.1875 (p_i=0.25, so p(1−p)=0.1875). The paper rounds/describes this as "p_i=0.25" and "v_i>0.1". The threshold 0.1 is below the minimum nonzero variance (0.1875 at k=4, p=0.25). This is consistent but should be stated explicitly — the threshold is effectively selecting any problem with at least one success out of four.

---

## PERSONA 2: Bored Reviewer Assessment

**Engagement Scores**

| Dimension | Score |
|---|---|
| abstract_compelling | true |
| problem_clear_in_1_minute | true |
| novelty_clear_in_2_minutes | false |
| would_continue_reading | marginal |
| attention_lost_at | Section 4 (Experimental Setup) |

**Bored Reviewer Notes**

The abstract hook is genuinely good: "a method that works analytically but fails empirically for a precise, diagnosable reason." A bored reviewer will read through the abstract.

The problem is clear: gradient starvation in GRPO with binary rewards is a real pain point. One minute reads fine.

Novelty fades fast. By Section 2 (Related Work), the reviewer sees that gradient starvation is already identified (Nie et al. 2026), variance-guided curriculum learning is not new, and the paper's unique contribution is (a) applying it to binary rewards offline, and (b) running it on MBPP with one model. That is a thin novelty claim.

Attention drops at Section 4. The experimental setup describes RQ1/RQ2/RQ3, but RQ3 fails completely and its failure is not due to the proposed method — it is due to a precondition the authors did not check beforehand. The bored reviewer now sees: "the method works analytically, we ran training, training gave nothing, we don't know why for certain." That feels like a workshop paper, not an ICML submission.

**Key BR Issues**

- BR-1 (MAJOR): The paper's framing as a full ICML paper is at risk. A negative result paper needs either (a) the confirmed resolution showing the method works when the precondition is met, or (b) a broader claim about methodology (cold-start verification should be a standard checklist item). Currently it has (b) weakly but not convincingly.
- BR-2 (MINOR): Section 3 (Methodology) describes a design that was not executed. This is confusing. The reader has to track "what was designed" vs "what was run" simultaneously.

---

## PERSONA 3: Skeptical Expert Assessment

**Novelty**

The core analytical contribution — selecting training problems by binary reward variance p(1−p) — is an application of a known principle. Curriculum learning by difficulty/variance is established (Bengio et al. 2009, Graves et al. 2017). The specific instantiation for binary execution rewards in GRPO is new in combination, but the combination is straightforward. The paper's actual novel contribution is the empirical finding that 91.7% of MBPP problems are useless for RLEF with a 7B model at current capability, and the cold-start diagnosis as a required precondition. That is a useful community finding but not a methods advance.

**Baseline Fairness**

No training baselines are compared because training produced zero signal for all conditions. This is appropriate — you cannot compare methods when both produce frac_reward_zero_std=1.0. However, the paper should be explicit: "baseline comparison is impossible under cold-start; the selection method comparison reduces to the profiling-stage statistics (RQ1/RQ2)."

**Overclaims**

- OC-1 (MAJOR): "first empirical characterization of binary execution reward variance distribution on MBPP for a 7B code LLM" — likely overclaimed. Any team that has run GRPO on MBPP has implicitly characterized this distribution. The paper lacks a literature check for published reward statistics in MBPP GRPO papers (e.g., DeepSeek-Coder GRPO ablations). This claim needs "to our knowledge" hedging and a citation search.
- OC-2 (MINOR): "cold-start verification as a necessary precondition" — this is presented as a contribution, but it is essentially "check that your model can solve some training problems before training." This is basic experimental hygiene, not a novel precondition that the community was unaware of. Framing it as a contribution risks reviewer ridicule. Better framing: "we provide a simple, cheap verification protocol (profile at training-aligned parameters) and show it would have prevented 40,000 wasted compute attempts."
- OC-3 (MINOR): The paper implies the variance selection method is validated by RQ1/RQ2 alone. But RQ1/RQ2 are profiling statistics; the actual RLEF benefit (faster learning) is completely unvalidated. The method is analytically motivated and profiling-stage validated but has no training-stage validation.

**Missing Limitations**

- ML-1 (MAJOR): Single model, single dataset, single seed for training runs. All training experiments are single-run. With reward=0 throughout, this is acceptable for the negative result, but the profiling statistics (RQ1/RQ2) should report variance across seeds or note that profiling is deterministic under greedy/fixed seed.
- ML-2 (MAJOR): The paper does not test the resolution protocol it proposes. The "concrete resolution protocol" in the abstract is described but not executed. A reader cannot verify that re-profiling with aligned parameters actually fixes the cold-start. Without this, the paper contributes a diagnosis but not a cure.
- ML-3 (MINOR): Dataset: ground truth shows dataset_subset="full" not "sanitized". MBPP's test/train split and contamination issues are not discussed. Using the full 374-problem set for profiling and training may include test-split problems.
- ML-4 (MINOR): The vLLM-TRL incompatibility that forced k=4 and max_new_tokens=128 is mentioned but not characterized. Other practitioners facing the same stack (TRL 1.9.2 + vLLM) would benefit from knowing exactly what the incompatibility is.

**Accept/Reject Verdict**

**REJECT (borderline, revise-and-resubmit)**

Reasoning: The paper is honest, numerically correct, and identifies a real and useful failure mode. But it is incomplete: the proposed resolution is untested, the main method has no training-stage validation, novelty claims need hedging, and the scope feels like a technical report rather than a full paper. With the resolution protocol executed and the cold-start shown to be fixable, this becomes a strong workshop or short-paper contribution. As a full ICML paper it currently lacks a complete story arc.

---

## Summary for Revision Agent

Priority order (fix highest first):

1. **[MAJOR] Execute the resolution protocol** — Re-profile with max_new_tokens=512 (aligned to training), re-run GRPO, report whether cold-start is resolved. Without this, the paper proposes a fix it never validates. This is the single change that would most strengthen acceptance prospects.

2. **[MAJOR] Enumerate and rank alternative root causes** — Parameter mismatch is the most likely cause, but the paper must explicitly rule out or rank: (a) full vs. sanitized dataset split, (b) model temperature behavior under TRL training mode, (c) TRL sampler/tokenizer bugs. A brief table of hypotheses + evidence-for/against is sufficient.

3. **[MAJOR] Hedge "first empirical characterization" claim** — Add "to our knowledge" and cite at least two GRPO-on-MBPP papers to confirm no prior published reward statistics. If prior work exists, reframe as "detailed characterization" or "systematic characterization."

4. **[MAJOR] Clarify that training-stage validation is absent** — Add an explicit statement that RQ1/RQ2 validate profiling-stage properties only, and that training-stage benefit (faster convergence) requires cold-start resolution before it can be measured.

5. **[MINOR] Report "50,000 total attempts"** — Replace "40,000+" with "50,000 (10,000 in h-m2 + 40,000 in h-m3)" for precision.

6. **[MINOR] Remove or measure "~13 unique rollouts"** — Either instrument and report deduplication count or delete this claim.

7. **[MINOR] Discuss k=4 vs k=8 variance resolution implications** — One paragraph on how coarser k affects which problems are selected and whether k=8 would change the 7.8% figure.

8. **[MINOR] Reframe cold-start as verification protocol, not novel precondition** — Soften contribution framing to avoid reviewer pushback on "this is obvious."

9. **[MINOR] Clarify dataset split** — Note whether "full" MBPP (374 problems) overlaps with standard test splits and whether this affects profiling validity.
