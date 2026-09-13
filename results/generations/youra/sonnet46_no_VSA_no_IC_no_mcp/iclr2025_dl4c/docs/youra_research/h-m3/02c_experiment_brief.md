# Experiment Design: h-m3

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** RLEF-Fraction achieves strictly higher pass@1 than RLEF-Binary at LiveCodeBench-Hard (Δ_Fraction > Δ_Binary, p < 0.05), confirming that the incremental gradient structure of fraction reward produces improvement beyond binary threshold signal at hard difficulty.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (SHOULD_WORK) Hypothesis** — Tests whether fraction vs. binary reward formulation difference materializes as a measurable pass@1 advantage at hard difficulty.

---

## Workflow Status

**Verification State:** IN_PROGRESS (h-m2 prerequisite: FAILED → LIMITATION_RECORDED, pipeline continues)
**Prerequisites Satisfied:** h-m2 SHOULD_WORK gate failed; limitation recorded; h-m3 proceeds per pipeline rules
**Gate Status:** SHOULD_WORK — failure triggers EXPLORE (document null result), not STOP

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2 (LIMITATION_RECORDED)

### Gate Condition

SHOULD_WORK: Δ(RLEF-Fraction, SFT) > Δ(RLEF-Binary, SFT) at LiveCodeBench-Hard, p < 0.05.
Failure mode: EXPLORE — binary and fraction rewards converge to similar performance; document reward null result.

---

## Continuation Context

### Previous Hypothesis Results

**h-m2 (LIMITATION_RECORDED):** Post-hoc evaluation of SFT-warm checkpoint on 180 APPS samples (60/bucket, G=2, max_new_tokens=128) yielded zero non-zero reward across all difficulty buckets. Root causes: token truncation at 128 tokens, SFT-warm has no test-correctness signal. This does NOT block h-m3 — h-m3 tests a different question (fraction vs. binary reward structure) requiring full RLEF training runs, not a reward-monitoring callback.

**Key inherited context from h-m2:**
- DeepSeek-Coder-7B base model confirmed as primary (SFT ceiling check required on HumanEval; if ≥90% switch to 1.3B)
- APPS train split (codeparrot/apps, difficulty-stratified) as training data
- bigcode-evaluation-harness correctness-only mode for all evaluations
- GRPO optimizer confirmed as training algorithm

**Critical note:** h-m3 requires an ADDITIONAL training run (RLEF-Binary) versus h-E1's RLEF-Fraction. h-E1's RLEF-Fraction checkpoint can be reused; only the binary-reward variant is new.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable in this session — replaced by web search research.*

**Finding 1: Pass-Rate vs Binary Reward (arXiv 2605.02944)**
- **Source:** "Exploring Pass-Rate Reward in Reinforcement Learning for Code Generation" (May 2025)
- **Key Result:** In rigorous controlled experiments across multiple base models and RL algorithms (GRPO, RLOO), pass-rate rewards do NOT reliably improve final pass@1 over binary rewards at convergence. Pass-rate shows early training advantage that diminishes as training progresses. At convergence, pass-rate provides slight improvement on pass@1 but underperforms binary on pass@k (k>1). 97% of tasks are solved/failed identically by both reward types.
- **Implication for h-m3:** The SHOULD_WORK assumption is challenged by existing literature. The experiment tests a hypothesis that recent work suggests may fail.
- **Used for:** Success criteria framing, expected baseline calibration, gate risk awareness

**Finding 2: VeRPO / "Beyond Binary" Dense Rewards (arXiv 2601.03525)**
- **Source:** "Beyond Binary: Turning Partial Success into Dense Verifiable Rewards for Reinforcement Learning in Code Generation" (VeRPO, Jan 2025)
- **Key Result:** Simple pass-rate (fraction) rewards suffer from *cardinality bias* — policy updates disproportionately favor gains from easy-test successes over frontier tests. VeRPO corrects this with weighted formulation. Simple fraction reward without weighting does NOT consistently outperform binary.
- **Implication for h-m3:** Naïve RLEF-Fraction (unweighted test-case fraction) may not outperform RLEF-Binary — consistent with the hypothesis being SHOULD_WORK (not MUST_WORK).
- **Used for:** Mechanism pseudo-code design, ablation motivation

**Finding 3: Rollout Pass-Rate Control (arXiv 2605.05112)**
- **Source:** "Rollout Pass-Rate Control: Steering Binary-Reward RL Toward Its Most Informative Regime" (May 2025)
- **Key Result:** Rather than changing reward formulation, controlling the rollout pass-rate (fraction of rollouts that partially solve problems) within a target range (20–80%) is more effective than switching to fraction rewards. Suggests the bottleneck is curriculum/sampling, not reward granularity.
- **Used for:** Understanding mechanism and failure modes for h-m3

### Archon Code Examples

*Archon MCP unavailable — code examples from Exa/web search below.*

### Exa GitHub Implementations

**Repository 1: bigcode-project/bigcode-evaluation-harness**
- **URL:** https://github.com/bigcode-project/bigcode-evaluation-harness
- **Relevance:** Official evaluation harness used for pass@1 on HumanEval, MBPP; used as primary evaluation tool
- **Architecture:** Autoregressive generation → sandbox execution → pass@1 computation
- **Key Code Pattern:**
  ```python
  # Evaluation invocation (correctness-only mode)
  # accelerate launch main.py \
  #   --model deepseek-ai/deepseek-coder-7b-base \
  #   --tasks humaneval,mbpp \
  #   --n_samples 1 \
  #   --batch_size 8 \
  #   --allow_code_execution \
  #   --save_generations_path generations.json
  ```
- **Used for:** Evaluation protocol specification

**Repository 2: LiveCodeBench/LiveCodeBench**
- **URL:** https://github.com/LiveCodeBench/LiveCodeBench
- **Relevance:** Official LiveCodeBench evaluation harness; supports difficulty-stratified pass@1
- **Key Features:** Release versions for contamination control (release_v4 = May 2023 – Sep 2024, 713 problems); difficulty levels: easy/medium/hard
- **Used for:** LiveCodeBench-Hard evaluation specification

**Repository 3: huggingface/trl — GRPO Trainer**
- **URL:** https://github.com/huggingface/trl/blob/main/trl/trainer/grpo_trainer.py
- **Relevance:** TRL GRPO implementation; reward_funcs parameter accepts custom reward functions including fraction-of-tests
- **Used for:** Training framework and reward function integration pattern

**Repository 4: codeparrot/apps (HuggingFace Dataset)**
- **URL:** https://huggingface.co/datasets/codeparrot/apps
- **Details:** 5000 train / 5000 test; features: problem_id, question, solutions, input_output, difficulty, url, starter_code; difficulty filter: `difficulties=["competition"]` for hard split
- **Used for:** Training dataset specification

**Serena Analysis Needed:** False — code patterns are clear from search results

### 🎯 Implementation Priority Assessment

**CRITICAL: For this experiment, there is no single "original paper" to reproduce — h-m3 is a controlled comparison experiment designed in-house.**

- **Primary:** TRL GRPOTrainer with custom reward functions (fraction vs. binary)
- **Fallback:** verl (verlproject/verl) if TRL GRPO shows instability
- **Justification:** TRL is the standard open-source GRPO implementation; most accessible for DeepSeek-Coder fine-tuning

**Recommended Implementation Path:**
- Primary: TRL GRPOTrainer (huggingface/trl)
- Fallback: verl framework (verl-project/verl)
- Justification: TRL GRPO is well-documented, supports reward_funcs API for custom fraction/binary rewards

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. TRL GRPOTrainer reward API and bigcode-harness evaluation patterns are well-documented without requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Primary Training Dataset: APPS**
- **Name:** APPS (Automated Programming Progress Standard)
- **Type:** standard (real benchmark dataset)
- **Source:** HuggingFace — codeparrot/apps
- **Split Used:** train (5000 problems)
- **Difficulty Stratification:** easy / interview / competition (maps to easy/medium/hard)
- **Hypothesis Fit:** APPS provides test-case-annotated problems with input_output field; enables execution of test cases for both fraction reward (count passing tests / total tests) and binary reward (all tests pass → 1, else 0)
- **Statistics:** 5000 train problems; difficulty distribution approx: 2500 introductory, 1500 interview, 1000 competition

**Evaluation Datasets (Multi-Benchmark):**
1. **HumanEval** — 164 problems (easy difficulty reference point)
2. **MBPP** — 374 problems (medium-easy reference)
3. **LiveCodeBench Easy/Medium/Hard** — release_v4 (713 problems, May 2023–Sep 2024); difficulty-stratified via LiveCodeBench harness

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"codeparrot/apps"`
- Code: `load_dataset("codeparrot/apps", split="train")` — difficulty filter: `difficulties=["competition"]` for hard-only subsets

### Models

#### Baseline Model

**Architecture:** DeepSeek-Coder-7B (base)
- **Model ID:** `deepseek-ai/deepseek-coder-7b-base`
- **Type:** Decoder-only transformer, code-specialized
- **Parameters:** 7B
- **Pre-condition:** Run zero-shot HumanEval first; if pass@1 ≥ 90%, switch to DeepSeek-Coder-1.3B (SFT ceiling check per A4)
- **SFT Baseline:** Fine-tune on APPS train split (standard cross-entropy, full solutions) — this is the "SFT" model used to compute Δ values
- **Hypothesis Fit:** Same base model used across h-E1 (SFT + RLEF-Fraction already trained); h-m3 adds only RLEF-Binary run

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `"deepseek-ai/deepseek-coder-7b-base"`
- Code: `AutoModelForCausalLM.from_pretrained("deepseek-ai/deepseek-coder-7b-base")`

#### Proposed Model

**Architecture:** Baseline DeepSeek-Coder-7B + RLEF-Binary reward training (GRPO)

**Core Mechanism Implementation:**

```python
# Core Mechanism: RLEF-Binary vs RLEF-Fraction Reward Functions
# Based on: TRL GRPOTrainer reward_funcs API + codeparrot/apps test execution
# Reference: arXiv 2605.02944, VeRPO (arXiv 2601.03525)

def binary_reward(completions, test_cases, **kwargs):
    """
    Binary execution reward: 1 if ALL tests pass, else 0.
    Sparse signal — zero for partially correct solutions.
    Args:
        completions: List[str] — generated code solutions
        test_cases: List[dict] — {"inputs": [...], "outputs": [...]}
    Returns:
        rewards: List[float] — {0.0, 1.0}
    """
    rewards = []
    for code, tc in zip(completions, test_cases):
        passed = execute_tests(code, tc["inputs"], tc["outputs"])
        # Binary: all-or-nothing
        rewards.append(1.0 if all(passed) else 0.0)
    return rewards

def fraction_reward(completions, test_cases, **kwargs):
    """
    Fraction-of-tests reward: proportion of tests passing.
    Dense signal — non-zero for partially correct solutions.
    Args:
        completions: List[str] — generated code solutions
        test_cases: List[dict] — {"inputs": [...], "outputs": [...]}
    Returns:
        rewards: List[float] — [0.0, 1.0] continuous
    """
    rewards = []
    for code, tc in zip(completions, test_cases):
        passed = execute_tests(code, tc["inputs"], tc["outputs"])
        # Fraction: count passing / total tests
        rewards.append(sum(passed) / len(passed) if passed else 0.0)
    return rewards

# Integration: pass as reward_funcs to GRPOTrainer
# trainer = GRPOTrainer(model=model, reward_funcs=[binary_reward], ...)
# trainer = GRPOTrainer(model=model, reward_funcs=[fraction_reward], ...)
```

**Comparison Design:**
- Model A (h-E1 reuse): RLEF-Fraction — fine-tuned with fraction_reward (already trained in h-E1)
- Model B (new): RLEF-Binary — fine-tuned with binary_reward (same budget as RLEF-Fraction)
- Model C (baseline): SFT — fine-tuned with cross-entropy (already trained in h-E1)

### Training Protocol

**Reusing from h-E1 (controlled comparison — only reward function changes):**

**Optimizer:** AdamW via GRPO
- Parameters: lr=1e-6, weight_decay=0.01
- Source: Standard GRPO hyperparameters (TRL defaults); DeepSeek-Coder community practice

**Learning Rate:** 1e-6
- Schedule: Cosine decay with warmup (100 steps)
- Source: TRL GRPOTrainer defaults for 7B models

**Batch Size:** 4 per GPU (gradient accumulation steps=4 → effective batch 16)
- Source: h-E1 configuration (reused for controlled comparison)

**Training Budget:** Same gradient steps as RLEF-Fraction in h-E1 (match exactly for fair comparison)
- Epochs: ~1-2 epochs over APPS train split
- Estimated steps: ~1250 steps (5000 problems / effective batch 4)

**GRPO Group Size (G):** 8 completions per prompt
- Source: Standard GRPO practice; large enough for reward variance estimation

**Max New Tokens:** 512 (increased from h-m2's 128 to avoid truncation)
- Source: h-m2 post-hoc identified 128 as too short; 512 covers majority of APPS solutions

**Loss Function:** GRPO clipped policy gradient loss (built into TRL GRPOTrainer)

**Seeds:** 1 (fixed seed=42 for reproducibility; single run per reward condition)

**New Training Run Required:** RLEF-Binary only (RLEF-Fraction and SFT reused from h-E1)

### Evaluation

**Primary Metrics:**
- Δ_Fraction = RLEF-Fraction pass@1 − SFT pass@1 (at LiveCodeBench-Hard)
- Δ_Binary = RLEF-Binary pass@1 − SFT pass@1 (at LiveCodeBench-Hard)
- **Gate metric:** Δ_Fraction > Δ_Binary at LiveCodeBench-Hard (p < 0.05, bootstrap test)

**Secondary Metrics:**
- Δ_Fraction vs Δ_Binary at HumanEval (should be ≈ 0 — no difficulty effect)
- Δ_Fraction vs Δ_Binary at LiveCodeBench-Easy/Medium (intermediate difficulty)
- Absolute pass@1 for all 3 models at all benchmarks

**Expected Baseline Performance (from research):**
- SFT (DeepSeek-Coder-7B on APPS) HumanEval: ~40–55% pass@1 (Source: h-E1 / 02b_verification_plan.md)
- SFT LiveCodeBench-Hard: ~5–15% pass@1 (Source: h-M1 confirmed <60%, actual ~10–15%)
- RLEF-Fraction LiveCodeBench-Hard: Expected +2–8% over SFT (Source: h-E1 results)
- RLEF-Binary vs RLEF-Fraction: arXiv 2605.02944 suggests minimal difference at convergence

**Success Criteria:**
- PASS (SHOULD_WORK satisfied): Δ_Fraction > Δ_Binary at LiveCodeBench-Hard, p < 0.05
- FAIL (EXPLORE): Δ_Fraction ≈ Δ_Binary (null result — document reward formulation does not matter beyond binary threshold at this scale/dataset)

**Evaluation Tool:** bigcode-evaluation-harness (correctness-only) + LiveCodeBench harness (release_v4)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code generation, pass@1
- Library: bigcode-evaluation-harness + LiveCodeBench official harness
- Code:
  ```bash
  # HumanEval / MBPP
  accelerate launch main.py --model <checkpoint> --tasks humaneval,mbpp \
    --n_samples 1 --batch_size 8 --allow_code_execution
  # LiveCodeBench
  python -m lcb_runner.runner.main --model <checkpoint> \
    --release_version release_v4 --n_workers 4
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — Δ_Fraction vs Δ_Binary at each difficulty level (HumanEval, MBPP, LiveCodeBench-Easy/Medium/Hard); error bars from bootstrap 95% CI

#### Additional Figures (LLM Autonomous)

Phase 4 should generate the following figures based on experimental findings:

1. **Reward Signal Density Plot**: Training reward trajectory over steps for RLEF-Fraction vs RLEF-Binary — shows whether fraction reward provides denser non-zero signals
2. **Absolute Pass@1 Comparison Table**: All 3 models (SFT, RLEF-Binary, RLEF-Fraction) × 5 benchmarks (heatmap)
3. **Difficulty-Scaling Interaction Plot**: Line plot of Δ (RLEF-Fraction − SFT) and Δ (RLEF-Binary − SFT) across difficulty levels — visualizes whether the reward type × difficulty interaction exists
4. **Non-Zero Reward Fraction by Difficulty**: Per-difficulty histogram of non-zero reward events during training for both reward functions

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Two reward functions (binary, fraction) are implemented and produce different outputs on partially-correct solutions | TRUE — fraction reward returns continuous [0,1]; binary returns {0,1} |
| Mechanism Isolatable | Only the reward function changes between RLEF-Binary and RLEF-Fraction; all other hyperparameters identical | TRUE — same optimizer, lr, budget, G, seeds; only `reward_funcs` parameter differs |
| Baseline Measurable | SFT baseline checkpoint from h-E1 available; RLEF-Fraction checkpoint from h-E1 available | TRUE — h-E1 must have completed before h-m3 runs |

### Architecture Compatibility Check

**DeepSeek-Coder-7B with GRPO is compatible with both reward formulations.**

**Required Features:**
- Autoregressive generation (supports completion sampling for group G)
- Execution sandbox for test-case evaluation (Docker or subprocess isolation)
- TRL GRPOTrainer reward_funcs API (accepts List[Callable])

**Incompatible Configurations:**
- max_new_tokens < 200 (causes systematic truncation → zero rewards for both functions — same failure as h-m2 post-hoc eval)
- G < 4 (insufficient variance for GRPO advantage estimation)

> ⚠️ Phase 4 MUST verify max_new_tokens ≥ 512 and G ≥ 8 before training begins.

---

### Mechanism Activation Indicators

**How to detect if reward formulation difference is actually active:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "mean_fraction_reward=X.XX, mean_binary_reward=Y.YY" where X > Y for partially-correct prompts | training_loop.py — logging callback |
| Reward Distribution | fraction_reward mean > binary_reward mean on APPS-competition split (where partial correctness exists) | reward_monitor.py |
| Metric Delta | Δ_Fraction − Δ_Binary at LiveCodeBench-Hard; sign and magnitude | evaluate.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_reward_formulation_active(fraction_rewards, binary_rewards, threshold=0.01):
    """
    Verifies that fraction and binary rewards differ on the training batch.
    If mean(fraction) == mean(binary), the mechanism is not activating
    (all solutions are either fully correct or fully wrong — no partial credit).
    """
    import numpy as np
    mean_fraction = np.mean(fraction_rewards)
    mean_binary = np.mean(binary_rewards)
    indicators = {
        "fraction_mean": mean_fraction,
        "binary_mean": mean_binary,
        "reward_differs": abs(mean_fraction - mean_binary) > threshold,
        "fraction_denser": mean_fraction > mean_binary,  # fraction should be >= binary
    }
    activated = indicators["reward_differs"] and indicators["fraction_denser"]
    if not activated:
        print("WARNING: Fraction reward not producing denser signal than binary — "
              "possible all-or-nothing solutions in this batch")
    return activated, indicators

# Run every N steps during training; log to tensorboard
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Both rewards identical | mean_fraction == mean_binary across training | INVESTIGATE: Check if APPS problems have all-or-nothing test suites (single test) |
| No training signal difference | Loss curves identical for Binary and Fraction runs | EXPLORE: Reward formulation does not matter; document null result |
| Evaluation gap null | Δ_Fraction ≈ Δ_Binary within bootstrap CI | EXPLORE per h-m3 gate — document per arXiv 2605.02944 findings |
| Token truncation recurrence | max_new_tokens too short → near-zero rewards for both | FAIL: Increase max_new_tokens to 1024 and retry |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | fraction_reward mean > binary_reward mean (on partially-correct prompts) | Per-batch reward logging |
| Effect Measurable | Δ_Fraction ≠ Δ_Binary (any magnitude) | Post-training evaluation |
| Hypothesis Supported | Δ_Fraction > Δ_Binary at LiveCodeBench-Hard, p < 0.05 | Bootstrap hypothesis test |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. RLEF-Binary training run completes without error (same budget as RLEF-Fraction)
2. Evaluation completes on all benchmarks (HumanEval, MBPP, LiveCodeBench Easy/Medium/Hard)
3. Δ_Fraction > Δ_Binary at LiveCodeBench-Hard (p < 0.05) — OR — null result documented with mechanism analysis

**Note on null result:** Given arXiv 2605.02944 findings, a null result (Δ_Fraction ≈ Δ_Binary) is a scientifically valid and expected outcome consistent with recent literature. The SHOULD_WORK gate means failure triggers EXPLORE, not STOP.

---

## Appendix: Reference Implementations

### A. Knowledge Base Sources (Web Search)

**Source A.1:** "Exploring Pass-Rate Reward in Reinforcement Learning for Code Generation"
- **URL:** https://arxiv.org/abs/2605.02944
- **Query Used:** pass rate reward vs binary reward code generation LLM LiveCodeBench evaluation 2024 2025
- **Relevance:** Direct controlled comparison of fraction vs binary reward across GRPO/RLOO; most relevant paper to h-m3
- **Key Findings:**
  - Pass-rate reward accelerates early learning but does NOT raise final performance ceiling
  - 97% of tasks solved/failed identically by both reward types
  - Fraction rewards do not consistently move probability mass toward full-pass solutions
- **Used For:** Success criteria calibration, expected baseline, gate risk framing

**Source A.2:** "Beyond Binary: VeRPO" (arXiv 2601.03525)
- **URL:** https://arxiv.org/abs/2601.03525
- **Query Used:** RLEF binary vs fraction reward GRPO code LLM training APPS pass@1 GitHub 2024 2025
- **Relevance:** Identifies cardinality bias in naïve fraction rewards; explains mechanistically WHY fraction ≠ binary improvement
- **Key Findings:**
  - Simple fraction reward suffers cardinality bias (easy tests dominate gradient)
  - Weighted formulation (VeRPO) needed to actually outperform binary
- **Used For:** Mechanism understanding, pseudo-code design, failure mode analysis

**Source A.3:** "Rollout Pass-Rate Control" (arXiv 2605.05112)
- **URL:** https://arxiv.org/abs/2605.05112
- **Relevance:** Shows reward formulation may matter less than rollout curriculum
- **Used For:** Failure mode context, alternative interpretation if null result

### B. GitHub Implementations (Web Search)

**Repository B.1: bigcode-project/bigcode-evaluation-harness**
- **URL:** https://github.com/bigcode-project/bigcode-evaluation-harness
- **Query Used:** bigcode evaluation harness LiveCodeBench pass@1 evaluation script GitHub
- **Architecture:** Accelerate-based evaluation; sandbox execution; pass@1 computation
- **Used For:** Evaluation protocol specification (HumanEval, MBPP)

**Repository B.2: LiveCodeBench/LiveCodeBench**
- **URL:** https://github.com/LiveCodeBench/LiveCodeBench
- **Query Used:** LiveCodeBench GitHub evaluation harness 2024 Q4 snapshot pass@1
- **Details:** release_v4 = May 2023 – Sep 2024 (713 problems); difficulty-stratified
- **Used For:** LiveCodeBench-Hard evaluation specification

**Repository B.3: huggingface/trl — GRPOTrainer**
- **URL:** https://github.com/huggingface/trl/blob/main/trl/trainer/grpo_trainer.py
- **Query Used:** DeepSeek-Coder GRPO reinforcement learning fraction reward implementation GitHub trl
- **Used For:** Training framework — reward_funcs API for binary/fraction reward integration

**Repository B.4: codeparrot/apps (HuggingFace)**
- **URL:** https://huggingface.co/datasets/codeparrot/apps
- **Query Used:** APPS dataset huggingface codeparrot/apps training split pytorch loading
- **Details:** 5000 train / 5000 test; difficulty filter available
- **Used For:** Training dataset loading specification

### C. Code Analysis (Serena)

*Serena analysis not performed — not needed. Code patterns from B.3 and B.4 were sufficiently clear.*

### D. Previous Hypothesis Context

**Source:** h-m2 validation results (LIMITATION_RECORDED) + h-m1 and h-E1 context from 02b_verification_plan.md
- **Inherited Components:**
  - SFT checkpoint (DeepSeek-Coder-7B on APPS) — already trained in h-E1
  - RLEF-Fraction checkpoint — already trained in h-E1
  - Evaluation harness configuration (bigcode-harness + LiveCodeBench)
  - max_new_tokens corrected to 512 (h-m2 identified 128 as insufficient)
- **Why Reused:** Enables controlled comparison — only reward function changes between RLEF-Fraction and RLEF-Binary; all other variables held constant

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Training dataset (APPS) | Standard benchmark | B.4, 02b_verification_plan.md |
| APPS loading code | HuggingFace | B.4 |
| RLEF-Fraction checkpoint reuse | Previous hypothesis | h-E1, 02b_verification_plan.md |
| GRPO framework | GitHub | B.3 |
| Binary reward function design | Research paper | A.1, A.2 |
| Fraction reward function design | Research paper | A.1, A.2 |
| Cardinality bias (mechanism failure mode) | Research paper | A.2 |
| Expected null result calibration | Research paper | A.1 |
| HumanEval/MBPP evaluation | GitHub | B.1 |
| LiveCodeBench-Hard evaluation | GitHub | B.2 |
| GRPO hyperparameters | Previous hypothesis + TRL docs | h-E1, B.3 |
| Success criteria (p < 0.05 bootstrap) | 02b_verification_plan.md | Phase 2B planning |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated in ```state block)
**Date:** 2026-08-26T08:30:00+00:00

### Workflow History for This Hypothesis

- h-m3 set to IN_PROGRESS (external loop, 2026-08-26T06:27:14)
- Phase 2C experiment design started (2026-08-26)
- Phase 2C experiment design completed (2026-08-26)

---

*MCP Tools Used: Exa (web search fallback — Archon unavailable); Serena (skipped — not needed)*
*All specifications grounded in researched implementations and 02b_verification_plan.md*
*Next Phase: Phase 3 - Implementation Planning*
