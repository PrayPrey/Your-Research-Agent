# H-E1: Per-Hypothesis Context (JIT Generated from Phase 2B)

**Generated:** 2026-08-03
**Source:** 02b_verification_plan.md
**Hypothesis ID:** H-E1

---

## Hypothesis Information

**ID:** H-E1
**Type:** EXISTENCE
**Gate:** MUST_WORK

**Statement:**
Under ContractEval's full 364 HumanEval+/MBPP+ tasks, if LLM-generated programs that pass all unit tests are evaluated via Hypothesis PBT with icontract-hypothesis strategy inference, then a non-zero contract-strength gap exists (mean fraction of test-passing programs failing ≥1 contract > 0), because Python-native execution checking is 100% tractable and h-e1 confirmed a 7.42% violation rate on the tractable subset.

**Rationale:**
h-e1 proved contracts catch test-passing failures at 7.42% on the 25.82% Z3-tractable subset. This hypothesis extends to the full 364 tasks using execution-based checking (no tractability ceiling). Foundation hypothesis — if fails, all H-M hypotheses stop.

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset Selection

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | ContractEval (HumanEval+/MBPP+ subset) | Standard benchmark with all required contract annotations; strict subset of HumanEval+/MBPP+ enabling EvalPlus integration |

**Dataset Details:**
- **Name:** ContractEval
- **Type:** standard
- **Source:** github.com/suhanmen/ContractEval (5★, ACL 2026)
- **Path:** 364 tasks with Python pre/post-condition contracts (subset of HumanEval+ and MBPP+)
- **Hypothesis Fit:** Contains icontract-annotated reference implementations across 364 coding tasks; directly enables Hypothesis PBT contract checking without Z3 tractability ceiling

### Model Selection

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Model** | Multi-model evaluation (5 LLM families, n=10 samples/task) | evalplus provides unified generation pipeline; needed to establish gap existence across models |

**Model Details:**
- **Type:** API (closed: OpenAI, Anthropic) + vLLM/HuggingFace (open: DeepSeek, CodeLlama)
- **Source:** evalplus/evalplus (1789★, NeurIPS 2023)
- **Models:** GPT-4o-mini, Claude-3-haiku, DeepSeek-Coder-V2-Lite, CodeLlama-13B, CodeLlama-34B
- **Hypothesis Fit:** evalplus supports all model backends; n=10 samples per task provides sufficient statistical power for existence check

---

## Variables

- **IV:** Verification method (Hypothesis PBT + icontract-hypothesis vs. EvalPlus differential oracle)
- **DV:** Contract-strength gap = fraction of test-passing programs failing ≥1 contract under Hypothesis PBT
- **CV:** Dataset (ContractEval 364 tasks), input budget (5k examples, seed=42, 60s), models (5 families, n=10 samples)

---

## Verification Protocol (from Phase 2B)

1. Oracle soundness pre-check: run Hypothesis (100k examples, 2h wall-clock) against ContractEval reference implementations; quarantine tasks with violations.
2. Generate n=10 code samples per (model, task) via evalplus backends; filter to test-passing programs only.
3. Run Hypothesis PBT + icontract-hypothesis (5k examples, seed=42, 60s) per (model, task, program) triple.
4. Compute contract-strength gap per task; aggregate mean across 364 quarantine-filtered tasks × 5 models.
5. Bootstrap 95% CI on mean gap; verify lower bound > 0.01.

---

## Success Criteria

- **Primary:** mean contract-strength gap > 0 across pooled results (bootstrap 95% CI lower bound > 0.01)
- **Secondary:** gap replicates h-e1's 7.42% lower bound on the tractable subset

---

## Failure Response

IF fails → STOP all H-M hypotheses; reassess whether contracts are too weak or icontract-hypothesis filter rate is prohibitively high across full 364 tasks.

---

## Dependencies

None (foundation hypothesis)

---

## Key Assumptions Relevant to H-E1

| ID | Assumption | Mitigation |
|----|------------|------------|
| A1 | ContractEval contracts are sound | Oracle soundness pre-check (100k examples, 2h per task) |
| A2 | icontract-hypothesis yields ≥100 valid samples for ≥80% tasks | Pilot test on 20 tasks before full run |

---

## Baseline & Comparison Targets

- **Baseline:** EvalPlus differential oracle (pass@1⋆ on HumanEval+/MBPP+)
- **Comparison:** ContractEval SMT-based (Lim et al. 2025) — 0% contract satisfaction for 5 open-source LLMs under Z3
- **PBT Reference:** Bose 2025 — 18-32% additional failures vs unit tests on StarCoder/CodeLlama (not ContractEval)
