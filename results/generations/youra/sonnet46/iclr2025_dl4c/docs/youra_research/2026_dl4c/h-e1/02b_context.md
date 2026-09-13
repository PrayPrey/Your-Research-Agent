# Per-Hypothesis Context: H-E1

**Generated:** JIT by Phase 2C Step 1 from 02b_verification_plan.md
**Hypothesis ID:** h-e1
**Parent Hypothesis:** H-RatioReward-v1

---

## Hypothesis

**ID:** H-E1
**Type:** EXISTENCE
**Gate:** MUST_WORK

**Statement:**
Under APPS introductory problems (difficulty=0) with Qwen2.5-Coder-7B-Instruct + SFT checkpoint (pass@8, temperature=0.8, max_new_tokens=1024), if prescreening inference is run on problems with S_term ∈ [0.3, 0.55], then (a) fraction(k_pass ≥ 1) ≥ 10% and (b) E[Var(r_ratio within group)] / E[Var(r_binary within group)] ≥ 1.5× across ≥80% of problem groups, because the Binomial(T,q) model analytically predicts E[Var(r_ratio)] = q(1-q) >> E[Var(r_binary)] = q^T(1-q^T) for T>1.

**Rationale:**
Before any GRPO training, we must confirm the variance advantage is real in practice. This hypothesis validates the fundamental prerequisite for the entire experimental design: that R_ratio actually provides different within-group information than R_binary on the prescreened problem set.

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset
- **Name:** APPS Introductory Split (prescreened S_term in [0.3, 0.55])
- **Type:** standard
- **Source:** codeparrot/apps on HuggingFace
- **Path:** ~/.cache/huggingface/datasets/codeparrot___apps
- **Hypothesis Fit:** APPS introductory problems (difficulty=0) provide sufficient test-case granularity (avg ~13 test cases) for R_ratio to differ from R_binary. Prescreened to S_term ∈ [0.3, 0.55] via empirical pass@8 inference.

### Model
- **Name:** Qwen2.5-Coder-7B-Instruct + SFT Checkpoint
- **Type:** 7B LLM fine-tuned for code generation
- **Source:** h-e1/code/sft_checkpoint/ (SFT from 3 epochs on APPS)
- **Pretrained Base:** Qwen/Qwen2.5-Coder-7B-Instruct
- **Hypothesis Fit:** 7B model with SFT checkpoint known to be in partial-tractability regime on APPS introductory at S_term ∈ [0.3, 0.55].

---

## Success Criteria

- **Primary:** fraction(k_pass ≥ 1) ≥ 10% on prescreened S_term ∈ [0.3, 0.55] subset
- **Primary:** E[Var(r_ratio)] / E[Var(r_binary)] ≥ 1.5× across ≥80% of problem groups

---

## Variables

- **Independent:** Problem subset selection (S_term ∈ [0.3, 0.55] APPS introductory)
- **Dependent:** fraction(k_pass ≥ 1), E[Var(r_ratio)]/E[Var(r_binary)] ratio
- **Controlled:** Model (Qwen2.5-Coder-7B + SFT), temperature=0.8, k=8, max_new_tokens=1024

---

## Verification Protocol (from Phase 2B)

1. Run pass@8 inference (k=8, temperature=0.8, max_new_tokens=1024) on APPS introductory problems with S_term ∈ [0.3, 0.55].
2. Compute fraction(k_pass ≥ 1) across all problem groups in the prescreened subset.
3. For each problem group, compute Var(r_ratio) and Var(r_binary) from 8 rollouts; average across groups.
4. Compute the variance ratio E[Var(r_ratio)] / E[Var(r_binary)] and check ≥1.5× across ≥80% of groups.
5. Gate decision: PASS if both fraction ≥10% AND variance ratio ≥1.5×; FAIL otherwise.

---

## Gate Condition

**Type:** MUST_WORK
**If Fail:** STOP entire experiment — R_ratio cannot provide variance advantage in this regime; return to Phase 0 for problem regime redesign

---

## Dependencies

**Prerequisites:** None (first hypothesis)
**Dependents:** H-M1 (blocked until H-E1 passes)

---

## Risk Context (from Phase 2B)

| Risk | Description | Severity |
|------|-------------|----------|
| R1 | T=1 degenerate problems (filter T≤2 in prescreening) | Medium |
| R2 | Degenerate within-group distribution | High |
| R4 | SFT checkpoint out of partial-tractability regime | Critical |
| R5 | Correlated APPS test cases | Medium |

---

## Source Reference

- **02b_verification_plan.md** Section 2.2 (H-E1 specification)
- **Phase 2A:** 03_refinement.yaml (H-RatioReward-v1, Section 1.6 P1, Section 5 SH1)
