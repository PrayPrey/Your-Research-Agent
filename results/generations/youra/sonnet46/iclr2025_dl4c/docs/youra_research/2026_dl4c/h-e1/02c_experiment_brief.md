# Experiment Design: h-e1

**Date:** 2026-03-15
**Author:** Anonymous
**Hypothesis Statement:** Under APPS introductory problems (difficulty=0) with Qwen2.5-Coder-7B-Instruct + SFT checkpoint (pass@8, temperature=0.8, max_new_tokens=1024), if prescreening inference is run on problems with S_term ∈ [0.3, 0.55], then (a) fraction(k_pass ≥ 1) ≥ 10% and (b) E[Var(r_ratio within group)] / E[Var(r_binary within group)] ≥ 1.5× across ≥80% of problem groups, because the Binomial(T,q) model analytically predicts E[Var(r_ratio)] = q(1-q) >> E[Var(r_binary)] = q^T(1-q^T) for T>1.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (no prerequisites — h-e1 is first hypothesis)
**Gate Status:** MUST_WORK (gate satisfaction: null — not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition

**Type:** MUST_WORK

If **FAIL**: STOP entire experiment — R_ratio cannot provide variance advantage in this regime; return to Phase 0 for problem regime redesign.

If **PASS**: Proceed to h-m1 (Graded Advantage Diversity verification).

**Pass Conditions:**
1. fraction(k_pass ≥ 1) ≥ 10% on prescreened S_term ∈ [0.3, 0.55] subset
2. E[Var(r_ratio)] / E[Var(r_binary)] ≥ 1.5× across ≥80% of problem groups

---

## Continuation Context

This is the **first hypothesis** in the verification chain. No previous hypothesis context exists.

### Previous Hypothesis Results (if applicable)
None — h-e1 is the root hypothesis (Level 0 in dependency DAG).

> **Historical context from verification_state.yaml:** 5 prior Phase 4 failures at S_term > 0.85 (APPS competition/interview split) confirmed as completely intractable. Current design targets empirically calibrated S_term ∈ [0.3, 0.55] on introductory split.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Status:** No relevant content found in Archon KB for this domain.

The indexed knowledge base (source_id: 8b1c7f40739544a6) contains primarily image generation / diffusion model content (Stable Diffusion, LoRA, diffusers). No GRPO, RLEF, APPS, or code generation reinforcement learning content was indexed. All similarity scores were low (0.34–0.57) with no semantic match.

**Queries executed (3 KB + 2 code):**
- "GRPO reward function code generation experiment design" → 0 relevant results
- "R_ratio R_binary reward variance RLEF implementation" → 0 relevant results
- "APPS dataset code generation benchmark evaluation" → 0 relevant results
- "GRPO reward function PyTorch TRL" → 0 relevant results
- "pass@k inference code generation evaluation" → 0 relevant results

**Implication:** Archon KB does not constrain this experiment design. Primary research sources are Semantic Scholar papers and well-established TRL/HuggingFace documentation.

### Archon Code Examples

No relevant code examples found. (See Archon KB findings above.)

### Exa GitHub Implementations

**Status:** UNAVAILABLE — HTTP 402 (Payment Required) on all 3 retry attempts.

Exa MCP API quota exhausted. Per workflow protocol: documenting limitation and proceeding with Semantic Scholar academic paper findings as implementation reference.

**Exa queries attempted (3 retries each):**
- "TRL GRPOTrainer reward function pass fraction code generation GitHub"
- "GRPO reward ratio binary execution feedback Qwen2.5-Coder APPS training"
- "APPS dataset pass@k prescreening variance reward signal GRPO RL"

**Fallback:** Implementation patterns derived from academic papers found via Semantic Scholar (below).

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This experiment is **NOT a paper reproduction** — it is an original empirical comparison of R_ratio vs R_binary reward functions under GRPO. No single "official implementation" to reproduce.

**Implementation strategy:**
- Primary: HuggingFace TRL `GRPOTrainer` as GRPO training backbone (established library, no custom GRPO needed)
- Secondary reference: Afterburner (ArXiv 2505.23387) for GRPO + APPS execution feedback patterns
- Tertiary reference: PKPO (ArXiv 2505.15201) for pass@k reward theory and variance analysis

**Recommended Implementation Path:**
- Primary: TRL GRPOTrainer with custom `reward_fn` hook implementing R_ratio = tests_passed_i / total_tests_i
- Fallback: Custom GRPO loop based on DeepSeekMath / open-source GRPO implementations
- Justification: TRL v0.29.0 GRPOTrainer is the controlled baseline specified in verification_state.yaml; custom reward_fn injection is the standard extension point

### Code Analysis (Serena MCP)

*Skipped* — Exa MCP unavailable (HTTP 402); no GitHub code retrieved to analyze. Code patterns derived from Semantic Scholar paper findings and TRL documentation knowledge.

---

## Experiment Specification

### Dataset

**Dataset:** APPS — Automated Programming Progress Standard (Hendrycks et al., 2021)
**Subset:** Introductory split only (difficulty=0)
**Prescreening Filter:** S_term ∈ [0.3, 0.55] — problems where pass@8 score (fraction of 8 rollouts with ≥1 test case passed) falls in partial-tractability regime
**Dataset Type:** standard (real, established benchmark)
**Source:** codeparrot/apps on HuggingFace

**Statistics:**
- Full APPS dataset: 10,000 problems total (5,000 train, 5,000 test)
- Introductory split (difficulty=0): ~2,342 problems in train, ~1,237 in test
- Average test cases per problem: ~13 (range: 1–100+)
- Prescreened subset (S_term ∈ [0.3, 0.55]): estimated 200–600 problems (exact count determined at prescreening runtime)

**Preprocessing:**
- Filter: `difficulty == 0` (introductory only)
- Filter: `len(test_cases) >= 3` (exclude T≤2 degenerate problems per Risk R1 mitigation)
- Prescreening: run pass@8 inference (temperature=0.8, k=8, max_new_tokens=1024); compute S_term = fraction of rollouts passing ≥1 test case; retain problems with S_term ∈ [0.3, 0.55]
- Format: problem statement + function signature as prompt; solutions evaluated against test cases via execution

**Augmentation:** None (evaluation-only; no training augmentation needed for h-e1 prescreening experiment)

**Synthetic Data Check:** ✅ PASSED — codeparrot/apps is a real, standard benchmark dataset (not synthetic)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets` library
- Identifier: `"codeparrot/apps"`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("codeparrot/apps", split="train")
intro_problems = dataset.filter(lambda x: x["difficulty"] == "introductory")
# Further filter T>=3 test cases and apply S_term prescreening
```

### Models

#### Baseline Model

**Architecture:** Qwen2.5-Coder-7B-Instruct + SFT Checkpoint
**Type:** 7B parameter causal language model, instruction-tuned for code generation
**Pretrained Base:** `Qwen/Qwen2.5-Coder-7B-Instruct`
**SFT Source:** `h-e1/code/sft_checkpoint/` — 3 epochs SFT on APPS introductory problems

**Key Properties (from Qwen2.5-Coder Technical Report, ArXiv 2409.12186):**
- Architecture: Qwen2.5 transformer backbone, 7B parameters
- Pretrained on 5.5 trillion tokens of code and general text
- SOTA on 10+ code benchmarks at 7B scale
- Instruction-tuned variant supports chat format for code generation prompts

**Configuration for h-e1:**
- Inference: temperature=0.8, max_new_tokens=1024, do_sample=True
- Group size: k=8 rollouts per problem
- No GRPO training in h-e1 (prescreening experiment only)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers` + local SFT checkpoint
- Identifier: `"Qwen/Qwen2.5-Coder-7B-Instruct"` (base) + local path
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
# Load SFT checkpoint (if exists) or base model
import os
sft_path = "h-e1/code/sft_checkpoint/"
model_id = sft_path if os.path.exists(sft_path) else "Qwen/Qwen2.5-Coder-7B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```

#### Proposed Model

**Architecture:** Baseline (Qwen2.5-Coder-7B-Instruct + SFT) — **no architectural change**

> For h-e1 (EXISTENCE), the "proposed model" is the **same model** used to compute R_ratio instead of R_binary. The experiment compares two reward computation functions applied to the same model's outputs, not two model architectures.

**Core Mechanism Implementation:**

```python
# Core Mechanism: R_ratio vs R_binary Reward Functions
# Based on: Phase 2B hypothesis specification + PKPO (ArXiv 2505.15201)
# For h-e1: PRESCREENING ONLY (no GRPO training)

def compute_rewards(rollouts: list[str], test_cases: list[dict],
                    reward_type: str = "ratio") -> list[float]:
    """
    Args:
        rollouts: list of k=8 generated code strings for one problem
        test_cases: list of {input, output} test case dicts
        reward_type: "ratio" (R_ratio) or "binary" (R_binary)
    Returns:
        rewards: list of k per-rollout reward scalars
    """
    T = len(test_cases)  # total test cases for this problem
    rewards = []

    for code in rollouts:
        # Execute code against all T test cases
        tests_passed = 0
        for tc in test_cases:
            passed = execute_and_check(code, tc["input"], tc["output"])
            tests_passed += int(passed)

        if reward_type == "ratio":
            r_i = tests_passed / T          # R_ratio: continuous [0, 1]
        else:  # "binary"
            r_i = float(tests_passed == T)  # R_binary: {0, 1}

        rewards.append(r_i)

    return rewards  # shape: [k=8]


def compute_variance_ratio(problems: list, model, tokenizer) -> dict:
    """
    H-E1 Gate Check: Compute E[Var(r_ratio)] / E[Var(r_binary)] per group.
    Returns gate metrics for MUST_WORK evaluation.
    """
    import numpy as np

    var_ratios = []
    k_pass_any = []

    for prob in problems:
        rollouts = generate_k_rollouts(model, tokenizer, prob["prompt"], k=8)
        r_ratio = compute_rewards(rollouts, prob["test_cases"], "ratio")
        r_binary = compute_rewards(rollouts, prob["test_cases"], "binary")

        var_ratio_group = np.var(r_ratio)
        var_binary_group = np.var(r_binary)

        # Avoid division by zero
        if var_binary_group > 1e-8:
            var_ratios.append(var_ratio_group / var_binary_group)

        k_pass_any.append(float(any(r > 0 for r in r_binary)))

    fraction_k_pass = np.mean(k_pass_any)          # Gate check (a)
    mean_var_ratio = np.mean(var_ratios)             # Gate check (b)
    pct_above_threshold = np.mean([v >= 1.5 for v in var_ratios])

    return {
        "fraction_k_pass_ge1": fraction_k_pass,    # Must be >= 0.10
        "mean_var_ratio": mean_var_ratio,
        "pct_groups_above_1_5x": pct_above_threshold,  # Must be >= 0.80
        "gate_pass": fraction_k_pass >= 0.10 and pct_above_threshold >= 0.80
    }
```

### Training Protocol

> ⚠️ **EXISTENCE (PoC) — h-e1 is a PRESCREENING experiment, NOT a training experiment.**
> No GRPO training is performed in h-e1. The experiment runs inference only.

**Inference Configuration:**
- Model: Qwen2.5-Coder-7B-Instruct + SFT checkpoint
- Temperature: 0.8 (controlled variable from Phase 2A)
- max_new_tokens: 1024 (controlled variable from Phase 2A)
- Rollouts per problem (k): 8 (group size G=8 per Phase 2A)
- Seed: 42 (single seed for PoC)
- Batch size: determined by GPU memory (H100 NVL ~40GB → suggest batch=4-8 problems per inference batch)
- dtype: bfloat16 (standard for Qwen2.5 models per technical report)

**Execution Environment:**
- Single GPU: H100 NVL (select empty GPU via `CUDA_VISIBLE_DEVICES`)
- Execution sandbox: subprocess-based Python execution with timeout (5 seconds per test case)
- Library versions: transformers ≥ 4.45.0, datasets ≥ 2.20.0, trl == 0.29.0

**Seeds:** 1 (single seed — PoC sufficient)

**Source:** Controlled variables from Phase 2B Section 1.3 (identical to Phase 2A specification)

### Evaluation

**Primary Metrics (Gate Conditions):**

| Metric | Definition | Gate Threshold | Gate Type |
|--------|------------|----------------|-----------|
| fraction_k_pass_ge1 | fraction of problem groups where ≥1 rollout passes all test cases | ≥ 0.10 | MUST_WORK (a) |
| pct_groups_above_1.5x | % of problem groups with E[Var(r_ratio)] / E[Var(r_binary)] ≥ 1.5 | ≥ 0.80 | MUST_WORK (b) |

**Secondary Diagnostics:**
- T-distribution: histogram of number of test cases per problem (validate T≥3 filter effectiveness)
- S_term distribution: histogram of pass@8 scores on prescreened vs non-prescreened problems
- Per-problem variance ratio: scatter plot of Var(r_ratio) vs Var(r_binary)
- Empirical vs theoretical Binomial prediction: compare empirical variance ratio to Binomial(T,q) prediction (Risk R5 check)

**Success Criteria (EXISTENCE PoC):**
- Gate PASS: both (a) fraction_k_pass_ge1 ≥ 0.10 AND (b) pct_groups_above_1.5x ≥ 0.80
- Gate FAIL: either condition not met → STOP, return to Phase 0

**Expected Performance (from Phase 2B established facts):**
- EF-3: ~15% test case average for comparable models on APPS introductory → S_term ∈ [0.3, 0.55] should yield sufficient partial-pass problems
- Analytical prediction: Binomial(T=13, q=0.3) → E[Var(r_ratio)] = 0.3×0.7 = 0.21 >> E[Var(r_binary)] = 0.3^13 × (1-0.3^13) ≈ 0 → ratio >> 1.5×

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code generation evaluation (execution-based)
- Library: custom execution harness (subprocess) + numpy for statistics
- Code:
```python
import numpy as np
# Gate check implementation
gate_pass = (results["fraction_k_pass_ge1"] >= 0.10 and
             results["pct_groups_above_1_5x"] >= 0.80)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing fraction_k_pass_ge1 (target: 0.10) and pct_groups_above_1.5x (target: 0.80) vs achieved values

#### Additional Figures (LLM Autonomous)

The Phase 4 Coder should autonomously decide appropriate additional figures. Recommended based on hypothesis type:

1. **S_term Distribution Histogram**: Distribution of pass@8 scores on APPS introductory (pre- and post-prescreening filter), showing the [0.3, 0.55] selection window
2. **Variance Ratio Scatter Plot**: Per-problem E[Var(r_ratio)] vs E[Var(r_binary)], with 1.5× threshold line marked
3. **T Distribution**: Histogram of test case counts per problem in prescreened subset (validate T≥3 filter)
4. **Empirical vs Theoretical Variance Ratio**: Binomial(T,q) prediction vs empirical per problem, scatter plot colored by T

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

> **Purpose:** Define HOW Phase 4 should verify that the mechanism actually works, not just that code runs.

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | R_ratio reward function can be computed from execution output (tests_passed_i / total_tests_i) | TRUE — requires only test case execution harness |
| Mechanism Isolatable | R_ratio and R_binary are two separate reward functions applied to the same model outputs; can be switched by parameter | TRUE — `reward_type="ratio"` vs `reward_type="binary"` |
| Baseline Measurable | R_binary baseline (fraction of groups with k_pass≥1; Var(r_binary)) can be measured independently | TRUE — computed from same rollouts |

### Architecture Compatibility Check

**Mechanism:** Reward function comparison (R_ratio vs R_binary) — this is a **reward computation** change, NOT a model architecture change.

**Required Infrastructure:**
- Code execution sandbox (subprocess with timeout, stdin/stdout capture)
- Test case harness for APPS format (list of {input, output} pairs)
- k=8 rollout generation capability (batched sampling with temperature=0.8)
- Qwen2.5-Coder-7B SFT checkpoint accessible at `h-e1/code/sft_checkpoint/`

**Incompatible Scenarios:**
- SFT checkpoint missing (fallback: use base `Qwen/Qwen2.5-Coder-7B-Instruct`)
- All T=1 problems (filtered by T≥3 filter — prevents degenerate R_ratio=R_binary)
- Execution sandbox unavailable (Phase 4 MUST set up sandbox before running)

> ⚠️ If SFT checkpoint is missing, Phase 4 downloads base model. If T-filter produces <50 problems, FAIL early — insufficient sample size.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "R_ratio computed: mean=X.XX, var=Y.YY (group {i})" | reward_fn.py, per-group computation |
| Metric Delta | var_ratio > var_binary for ≥80% of groups | evaluate.py: compute_variance_ratio() |
| Distribution Check | fraction_k_pass_ge1 between 0.10 and 0.90 (not degenerate) | prescreening.py: gate_check() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """Verify R_ratio mechanism provides distinct information vs R_binary."""
    indicators = {
        "fraction_above_zero": results["fraction_k_pass_ge1"] > 0.0,
        "fraction_below_one": results["fraction_k_pass_ge1"] < 1.0,
        "variance_ratio_computed": results["mean_var_ratio"] > 0.0,
        "r_ratio_differs_r_binary": results["mean_var_ratio"] > 1.0,
    }
    mechanism_active = all(indicators.values())
    gate_pass = (
        results["fraction_k_pass_ge1"] >= 0.10 and
        results["pct_groups_above_1_5x"] >= 0.80
    )
    return mechanism_active and gate_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| All k_pass=0 (intractable) | fraction_k_pass_ge1 < 0.10 | FAIL Gate (a): S_term ∈ [0.3, 0.55] still intractable for SFT checkpoint |
| All k_pass=1 (trivial) | fraction_k_pass_ge1 > 0.95 | FAIL: Problems too easy; R_ratio = R_binary = 1.0 degenerate |
| Variance ratio < 1.5× | pct_groups_above_1.5x < 0.80 | FAIL Gate (b): R_ratio provides no variance advantage |
| Execution sandbox failure | OSError / TimeoutError in harness | FAIL EARLY: Fix execution environment before proceeding |
| T=1 problems dominating | mean T < 3 after T≥3 filter | FAIL EARLY: Dataset filtering error |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | fraction_k_pass_ge1 > 0 AND mean_var_ratio > 1.0 | Log/computation check |
| Effect Measurable | mean_var_ratio > 0.0 | Before/after reward computation |
| Hypothesis Supported | fraction_k_pass_ge1 ≥ 0.10 AND pct_groups_above_1.5x ≥ 0.80 | Both gate conditions |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (prescreening inference completes)
2. fraction_k_pass_ge1 ≥ 0.10 (R_ratio not degenerate — partial pass exists)
3. pct_groups_above_1.5x ≥ 0.80 (variance advantage confirmed)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant content found in Archon KB for this domain. The KB is populated with image generation / diffusion model content only. All 5 queries returned low-similarity irrelevant results (similarity 0.34–0.57).

**Impact:** No hyperparameters or implementation patterns sourced from Archon. All specifications derived from Phase 2B controlled variables and Semantic Scholar papers.

### B. GitHub Implementations (Exa)

**Status: UNAVAILABLE** — Exa MCP returned HTTP 402 (payment/quota exhausted) on all 3 retry attempts (15-second intervals between retries).

**Impact:** No direct GitHub code snippets available. Implementation patterns derived from academic paper descriptions (Section C below).

### C. Semantic Scholar Academic Paper Sources

**Source C.1: Afterburner (GRPO + APPS)**
- **Title:** "Afterburner: Reinforcement Learning Facilitates Self-Improving Code Efficiency Optimization"
- **ArXiv:** 2505.23387 | **Citations:** 8
- **URL:** https://www.semanticscholar.org/paper/2d3b5a90976b89ebd16efda15801df999f0a6599
- **Relevance:** ⭐⭐⭐ HIGHEST — GRPO with execution feedback on APPS benchmark; pass@1 from 47%→62%; confirms continuous/ratio-style rewards via RL outperform binary SFT/DPO
- **Key Insight:** GRPO training with execution feedback continuously improves after SFT saturates; execution-based reward signals are effective on APPS
- **Used For:** Confirming APPS+GRPO is a viable setup; informed prescreening rationale

**Source C.2: PKPO (pass@k optimization theory)**
- **Title:** "Pass@K Policy Optimization: Solving Harder Reinforcement Learning Problems"
- **ArXiv:** 2505.15201 | **Citations:** 31
- **URL:** https://www.semanticscholar.org/paper/f7bda1b5ffcd601a09e72f0d089a0fcdcc64de5c
- **Relevance:** ⭐⭐⭐ HIGHEST — Formal treatment of binary vs continuous reward in pass@k; derives low-variance unbiased estimators for both settings; annealing k achieves both pass@1 and pass@k
- **Key Insight:** Binary reward (pass@k=1) and continuous ratio reward (fractional test pass) have different variance properties in group-based optimization — directly validates h-e1 theoretical basis
- **Used For:** Theoretical grounding for R_ratio vs R_binary variance comparison; variance ratio pseudocode design

**Source C.3: Execution-Guided RL for Competitive Programming**
- **Title:** "Reasoning Through Complexity: An Execution-Guided Reinforcement Learning Approach for Competitive Programming Problems"
- **DOI:** 10.1109/ICoSEIT67010.2025.11290944
- **URL:** https://www.semanticscholar.org/paper/c79736dd9ac4fd8ae940d52badde97d4750d95da
- **Relevance:** ⭐⭐ HIGH — Uses multi-faceted (non-binary) reward with efficiency penalties on competitive programming using GRPO
- **Key Insight:** Fine-grained reward signals beyond binary execution verdict improve GRPO training for code; partial-credit style rewards are viable
- **Used For:** Confirming non-binary reward design for competitive programming

**Source C.4: Qwen2.5-Coder Technical Report**
- **ArXiv:** 2409.12186 | **Citations:** 1006
- **URL:** https://www.semanticscholar.org/paper/11dd2fc88747d20629f5aafab72ba649d93e969c
- **Relevance:** ⭐⭐⭐ HIGHEST — Official technical report for the base model used in this experiment
- **Key Insight:** 7B model, bfloat16, 5.5T token pretraining, SOTA on code benchmarks; instruction-tuned variant supports code generation prompts
- **Used For:** Model loading configuration, dtype choice (bfloat16), performance expectations

**Source C.5: Mitigating LLM Hallucination via Calibrated RL**
- **ArXiv:** 2512.19920 | **Citations:** 3
- **Relevance:** ⭐ MEDIUM — Critiques binary reward (RLVR) as incentivizing guessing; calibrated rewards with proper scoring rules outperform binary; supports R_ratio rationale
- **Used For:** Additional theoretical motivation for why R_ratio > R_binary

### D. Previous Hypothesis Context

**Previous Context:** None — h-e1 is the first hypothesis in the verification chain (no prerequisites).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (APPS introductory) | Phase 2B + Phase 2A | 02b_verification_plan.md Section 1.3 |
| Dataset filter (S_term ∈ [0.3, 0.55]) | Phase 2B | 02b_verification_plan.md H-E1 spec |
| T≥3 filter | Phase 2B Risk R1 | 02b_verification_plan.md Section 3.2.1 |
| Model (Qwen2.5-Coder-7B + SFT) | Phase 2B + Phase 2A | 02b_verification_plan.md Section 1.3 |
| Model loading (bfloat16, transformers) | Semantic Scholar | Source C.4 (Qwen2.5-Coder Tech Report) |
| R_ratio definition | Phase 2A | 02b_verification_plan.md H-M1 mechanism |
| R_binary definition | Phase 2B EF-4 | Established fact: universal baseline |
| Variance ratio computation | Phase 2B PN-1 | Binomial(T,q) analytic prediction |
| k=8 rollouts | Phase 2A | 02b_verification_plan.md Section 1.3 controlled vars |
| temperature=0.8 | Phase 2A | 02b_verification_plan.md Section 1.3 controlled vars |
| max_new_tokens=1024 | Phase 2A | 02b_verification_plan.md Section 1.3 controlled vars |
| fraction_k_pass ≥ 10% gate | Phase 2B H-E1 | 02b_verification_plan.md Section 2.2 success criteria |
| variance ratio ≥ 1.5× gate | Phase 2B H-E1 | 02b_verification_plan.md Section 2.2 success criteria |
| GRPO feasibility on APPS | Semantic Scholar | Source C.1 (Afterburner) |
| R_ratio vs R_binary theory | Semantic Scholar | Source C.2 (PKPO) |
| Non-binary reward effectiveness | Semantic Scholar | Source C.3 (Execution-guided RL) |
| Core mechanism pseudocode | Phase 2B spec + C.2 | Sources C.2 + 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-15T17:30:00

### Workflow History for This Hypothesis

- 2026-03-15T17:00:00 — Phase 2B completed; h-e1 marked READY
- 2026-03-15T15:51:11 — h-e1 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- 2026-03-15T17:30:00 — Phase 2C experiment_design.status = IN_PROGRESS (this run)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (5 queries — no relevant content), Semantic Scholar (5 queries — 4 relevant papers found), Exa (UNAVAILABLE — HTTP 402)*
*Serena: Skipped (no GitHub code to analyze)*
*All specifications grounded in Phase 2B verification plan + academic literature*
*Next Phase: Phase 3 - Implementation Planning*
