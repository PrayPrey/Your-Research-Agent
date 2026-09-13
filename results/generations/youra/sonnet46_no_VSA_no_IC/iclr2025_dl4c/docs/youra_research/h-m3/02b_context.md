---
hypothesis_id: H-M3
generated_at: "2026-08-21"
source: 02b_verification_plan.md (JIT extraction by Phase 2C step-01)
---

# Per-Hypothesis Context: H-M3

## Hypothesis Information

**ID:** H-M3
**Type:** MECHANISM
**Gate Type:** SHOULD_WORK
**Prerequisites:** H-M2

**Statement:**
During GRPO training on variance-50, the fraction of steps with nonzero reward variance (1 - frac_reward_zero_std) remains higher than random-50 throughout the full 50-step training budget, confirming that the frozen-model variance proxy does not degrade too quickly for problems to remain in the learning zone.

**Rationale:**
A key concern (A3) is that the frozen-model proxy becomes stale as training progresses — a problem at p_i=0.45 at step 0 may reach p_i=0.85 by step 20. H-M3 tests whether the proxy is stable enough over 20–50 steps by examining whether the frac_reward_zero_std gap between variance-50 and random-50 is maintained (not just early in training).

**Source:** Phase 2A Section 1.3 Step 3; assumption A3; key tension statement

---

## Experimental Setup (from Phase 2A via Phase 2B)

**Dataset:**
- Name: MBPP (training split) → evaluation on HumanEval+
- Type: standard
- Source: google-research-datasets/mbpp (HuggingFace Datasets)
- Path: auto (HuggingFace); evaluation: EvalPlus HumanEval+ (164 problems)
- Hypothesis Fit: MBPP provides the pool for variance-guided selection; H-M3 analyzes temporal stability of selection advantage using step-by-step TRL training logs from H-M2

**Model:**
- Name: DeepSeek-Coder-7B-Instruct
- Type: Code LLM, instruction-tuned, 7B parameters
- Source: deepseek-ai/deepseek-coder-7b-instruct-v1.5 (HuggingFace)
- Hypothesis Fit: Same model used in H-M2; H-M3 re-analyzes H-M2 logs — no new training required

---

## Variables

- **Independent:** Training step (temporal variable, steps 1–50)
- **Dependent:** frac_reward_zero_std(variance-50) - frac_reward_zero_std(random-50) gap at each step
- **Controlled:** G=4, use_vllm=False, generation_batch_size=4, lr=5e-7, same base model checkpoint (all inherited from H-M2)

---

## Verification Protocol (from Phase 2B)

1. Use TRL training logs from H-M2 experiment (no new training needed).
2. Compute the gap: frac_zero_std(random-50) - frac_zero_std(variance-50) at each step 1–50.
3. Check if gap is positive (variance-50 better) at checkpoints 10, 20, AND 50.
4. Check gap trend: stable, increasing, or decreasing (proxy degradation = decreasing gap).
5. Report: gap trajectory as secondary finding regardless of H-M4 outcome.

---

## Success Criteria (PoC)

- **Primary:** Gap is positive at steps 10, 20, AND 50 (variance-50 consistently better)
- **Secondary:** Gap at step 50 ≥ 50% of gap at step 10 (proxy not fully degraded)

---

## Failure Response

- IF gap disappears by step 20: EXPLORE — document proxy degradation rate; scope hypothesis to ≤10 steps.
- IF gap positive at 10 but negative at 50: partial finding — short RLEF (≤20 steps) may benefit more.

---

## Gate Conditions

- H-M2 (prerequisite): SHOULD_WORK gate — FAILED (limitation recorded, continue with warning)
- H-M3 gate type: SHOULD_WORK (failure → EXPLORE, not STOP)

---

## Key Note: No New Training Required

H-M3 is derived entirely from H-M2 training logs. The experiment design must center on:
1. Log parsing/analysis of step-by-step frac_reward_zero_std from the H-M2 GRPO runs
2. Gap trajectory computation and visualization
3. Statistical characterization of proxy stability over time

This makes H-M3 a **log analysis experiment**, not a training experiment.
