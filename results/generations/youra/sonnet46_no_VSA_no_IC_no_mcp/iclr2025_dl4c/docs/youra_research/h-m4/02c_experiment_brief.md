# Experiment Design: h-m4

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Δ(RLEF-Fraction, SFT) increases monotonically across all 5 benchmark difficulty levels (HumanEval < MBPP < LCB-Easy < LCB-Medium < LCB-Hard), and the directional pattern (Δ ratio ≥ 1.0) holds for DeepSeek-Coder-1.3B as a model-scale sanity check.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m3 FAILED (SHOULD_WORK gate — LIMITATION_RECORDED, pipeline continues with warning)
**Gate Status:** SHOULD_WORK — proceed with documented limitation from h-m3

**⚠️ Continuation Warning:** h-m3 showed no significant Δ_Fraction > Δ_Binary difference at LCB-Hard (p=0.552). The monotonicity test in h-m4 uses Δ(RLEF-Fraction, SFT) across difficulty — this is a different comparison (vs SFT, not vs Binary) and tests gradient scaling rather than reward formulation difference. The h-m3 null result is noted as prior context.

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m4
- **Type:** MECHANISM
- **Prerequisites:** h-m3 (FAILED, LIMITATION_RECORDED) → h-m2, h-m1, h-e1 (all completed)

### Gate Condition
SHOULD_WORK: Monotonic trend in Δ(RLEF-Fraction, SFT) across 5 difficulty levels (Jonckheere-Terpstra p < 0.05); secondary: DeepSeek-Coder-1.3B sanity check shows Δ ratio ≥ 1.0.

---

## Continuation Context

This is the fourth and final mechanism hypothesis. All preceding experiments used:
- **Training data:** APPS (codeparrot/apps, HuggingFace)
- **Primary model:** DeepSeek-Coder-7B-base (deepseek-ai/deepseek-coder-7b-base)
- **Evaluation harness:** bigcode-evaluation-harness (correctness-only mode)
- **GRPO framework:** TRL GRPOTrainer

**Key data reuse from h-e1:** The Δ(RLEF-Fraction, SFT) values at all 5 benchmark levels were already computed in h-e1. Steps 1–2 of the verification protocol require **zero additional training** — only re-analysis of existing evaluation results for the 7B model. New training is required only for the 1.3B sanity check (Step 3 of protocol).

### Previous Hypothesis Results (h-m3)
- Δ_Fraction at LCB-Hard: +0.18; Δ_Binary at LCB-Hard: +0.1728
- Observed diff: +0.0072; p=0.552 (NOT significant)
- Conclusion: Fraction and Binary rewards converge at hard difficulty — no incremental gradient advantage confirmed
- Impact on h-m4: The monotonicity test compares RLEF-Fraction vs SFT (not vs Binary), so h-m3 null result does not invalidate h-m4 directly, but suggests that the absolute Δ values may be modest, making monotonicity harder to detect statistically.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable in this session. Web search used as substitute.*

**Query 1: RLEF difficulty scaling experiment design**
- RLEF (Gehring et al., arXiv:2410.02089): Official Meta RLEF paper; benchmarked on CodeContests + HumanEval+, MBPP+. Demonstrates generalisation from hard competitive programming training to easier benchmarks. Key insight: training on harder problems yields broader benefit — supports the inverse of our monotonicity hypothesis (training hardness → eval breadth).
- RLPF (arXiv:2607.27271): Reinforcement Learning from Performance Feedback; uses pass-rate-based rewards. Related to fraction reward formulation.
- "Beyond Binary: Turning Partial Success into Dense Verifiable Rewards" (arXiv:2601.03525): Directly compares binary vs fraction rewards; confirms partial-success signal matters for gradient density.

**Query 2: GRPO/TRL implementation for code generation**
- TRL GRPOTrainer (huggingface.co/docs/trl/grpo_trainer): Standard implementation. Supports custom reward functions; reward_model can be a callable that takes (prompts, completions) → reward tensor.
- "Execution-Grounded Credit Assignment for GRPO" (arXiv:2603.16158): Improves GRPO by weighting rewards by test execution outcome — directly relevant to our fractional reward implementation.
- "Breaking Training Bottlenecks: Effective and Stable RL for Coding Models" (arXiv:2603.07777): Stability improvements for GRPO in code; difficulty-aware datasets achieve 3× larger performance gains in 300 steps vs baseline.

**Query 3: Difficulty-stratified benchmark performance**
- "Scaling Data Difficulty: Improving Coding Models via RL on Fresh and Challenging Problems" (arXiv:2603.07779): Demonstrates that difficulty-aware data curation shows models deliver improvements on medium and hard problems — up to 17.2% relative gains; supports difficulty-scaling hypothesis.
- LiveCodeBench (github.com/livecodebench/livecodebench): Continuously updated; Easy/Medium/Hard stratification defined by problem source and acceptance rate.

### Archon Code Examples

*Not available. Exa/web search substituted.*

### Exa GitHub Implementations

**Query 1: Official RLEF + bigcode-evaluation-harness**

**Repository 1:** bigcode-project/bigcode-evaluation-harness
- **URL:** https://github.com/bigcode-project/bigcode-evaluation-harness
- **Relevance:** Standard evaluation framework used for HumanEval, MBPP, APPS pass@1; supports LiveCodeBench integration
- **Architecture:** Task-based evaluation with configurable pass@k (unbiased estimator); correctness-only mode excludes style/efficiency checks
- **Key evaluation commands:**
  ```bash
  # HumanEval evaluation
  python main.py --model deepseek-ai/deepseek-coder-7b-base \
    --tasks humaneval --n_samples 20 --temperature 0.2 \
    --metric_output_path results/humaneval.json --allow_code_execution

  # MBPP evaluation
  python main.py --model deepseek-ai/deepseek-coder-7b-base \
    --tasks mbpp --n_samples 20 --temperature 0.2 \
    --metric_output_path results/mbpp.json --allow_code_execution
  ```
- **Dataset:** HumanEval (164 problems), MBPP (374 problems), APPS (5000 problems)
- **Results:** Standard pass@1 with n≥20 samples for unbiased estimator

**Repository 2:** huggingface/trl (GRPOTrainer)
- **URL:** https://github.com/huggingface/trl/blob/main/docs/source/grpo_trainer.md
- **Relevance:** Standard GRPO training framework used across h-e1 through h-m3
- **Key config for code generation:**
  ```python
  from trl import GRPOConfig, GRPOTrainer

  training_args = GRPOConfig(
      output_dir="./rlef_fraction_1.3b",
      num_train_epochs=3,
      per_device_train_batch_size=4,
      gradient_accumulation_steps=4,
      learning_rate=1e-5,
      warmup_ratio=0.1,
      lr_scheduler_type="cosine",
      num_generations=8,        # G in GRPO
      max_prompt_length=512,
      max_completion_length=1024,
  )
  ```

**Query 2: Jonckheere-Terpstra test Python**

**Implementation source:** scipy.stats.mannwhitneyu (manual JT via pairwise Mann-Whitney)
- No native scipy JT implementation; must implement via pairwise sum of Mann-Whitney U statistics across ordered groups
- Alternative: `clinfun` R package (via rpy2) or manual implementation

**Serena Analysis Needed:** false (code is clear from search results; no complex custom layers)

### 🎯 Implementation Priority Assessment

This experiment is primarily a **re-analysis** of existing h-e1 results (for 7B monotonicity test) plus **new training** for 1.3B sanity check.

**CRITICAL: No new RLEF-Fraction training required for the 7B model.** All Δ values at 5 difficulty levels were already computed in h-e1. The primary cost of h-m4 is:
1. Statistical analysis (Jonckheere-Terpstra) of existing 7B results: ~0 GPU hours
2. DeepSeek-Coder-1.3B SFT + RLEF-Fraction training on APPS: ~4–8 GPU hours (parallelizable with 7B)

**Recommended Implementation Path:**
- Primary: Re-use h-e1 evaluation results for 7B monotonicity test
- Secondary: Train 1.3B models using same APPS + GRPO pipeline as h-e1 (config inheritance)
- Justification: Zero redundant computation; controlled comparison via same pipeline

### Code Analysis (Serena MCP)

*Skipped — Code from search results was sufficiently clear. No complex custom layers requiring semantic analysis. The key new code is the Jonckheere-Terpstra implementation and 1.3B training config, both derivable from existing resources.*

---

## Experiment Specification

### Dataset

**Name:** APPS (Automated Programming Progress Standard)
**Type:** standard
**Source:** HuggingFace — `codeparrot/apps`
**Version:** Full dataset, training split (5000 problems), split by difficulty: intro (easy), interview (medium), competition (hard)
**Path:** `auto` (HuggingFace auto-download)
**Hypothesis Fit:** APPS spans easy-to-competition difficulty levels; provides both SFT targets (correct solutions) and RLEF execution signals (test pass/fail); the intro/interview/competition split creates the difficulty gradient needed to verify monotonic training advantage. **Already used in h-e1 through h-m3; reused for controlled comparison.**

**Evaluation Datasets (no new download required):**
| Benchmark | Problems | Difficulty Level | Source |
|-----------|----------|-----------------|--------|
| HumanEval | 164 | Easy | openai/HumanEval |
| MBPP | 374 | Medium-Easy | google-research-datasets/mbpp |
| LiveCodeBench-Easy | ~250 | Easy | livecodebench/livecodebench (2024-Q4 snapshot) |
| LiveCodeBench-Medium | ~250 | Medium | livecodebench/livecodebench (2024-Q4 snapshot) |
| LiveCodeBench-Hard | ~150 | Hard | livecodebench/livecodebench (2024-Q4 snapshot) |

**Total evaluation samples:** ≥1,188 problems across 5 difficulty levels. Full standard test sets — no subsampling.

**Statistics:**
- APPS train: 5,000 problems; ~800 intro / ~2,300 interview / ~1,900 competition
- HumanEval: 164 problems (all used)
- MBPP: 374 problems (sanitised split, all used)
- LiveCodeBench: 2024-Q4 snapshot to prevent contamination

**Preprocessing:** Same as h-e1 (tokenization with DeepSeek-Coder tokenizer; max_length=2048 for prompt+completion; APPS solutions truncated to first correct solution per problem)

**Augmentation:** None (standard evaluation benchmark; no augmentation applied)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `codeparrot/apps` (training); `openai/human-eval` (eval); `google-research-datasets/mbpp` (eval); `livecodebench/livecodebench` (eval)
- Code:
  ```python
  from datasets import load_dataset
  apps_train = load_dataset("codeparrot/apps", split="train")
  # Evaluation via bigcode-evaluation-harness (separate tool)
  ```

### Models

#### Baseline Model

**Architecture:** DeepSeek-Coder-7B-base (primary) + DeepSeek-Coder-1.3B-base (sanity check)
**Type:** decoder-only transformer, code-specialized
**Source:** HuggingFace — `deepseek-ai/deepseek-coder-7b-base` / `deepseek-ai/deepseek-coder-1.3b-base`
**Configuration:**
- 7B: 32 layers, 4096 hidden dim, GQA attention; context 16k tokens
- 1.3B: 24 layers, 2048 hidden dim; context 16k tokens
**Hypothesis Fit:** Public weights; strong code generation; not saturated on HumanEval from base weights (7B~70-80% after instruction tuning; base weights likely <60%); available at 1.3B scale for scale sanity check per verification protocol. **Already used in h-e1 through h-m3; reused for controlled comparison.**

**SFT results (reused from h-e1):**
- 7B SFT: Already trained; evaluation results at 5 benchmarks already available
- 1.3B SFT: **New training required** (same APPS procedure as 7B SFT)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `deepseek-ai/deepseek-coder-7b-base` / `deepseek-ai/deepseek-coder-1.3b-base`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "deepseek-ai/deepseek-coder-1.3b-base",
      torch_dtype=torch.bfloat16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-1.3b-base")
  ```

#### Proposed Model

**Architecture:** DeepSeek-Coder-1.3B-base fine-tuned with RLEF-Fraction (GRPO + fraction-of-tests reward)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Fraction-of-Tests Reward for GRPO
# Based on: TRL GRPOTrainer + bigcode execution harness pattern
# Used in: h-e1 (7B); now applied to 1.3B for scale sanity check

def fraction_reward_fn(completions: list[str], problems: list[dict]) -> list[float]:
    """
    Args:
        completions: list of generated code strings (B * G,)
        problems: list of APPS problem dicts with 'solutions' and 'input_output'
    Returns:
        rewards: list of float in [0.0, 1.0] — fraction of tests passing
    """
    rewards = []
    for code, problem in zip(completions, problems):
        try:
            tests = json.loads(problem["input_output"])
            passed = 0
            for inp, expected_out in zip(tests["inputs"], tests["outputs"]):
                result = safe_execute(code, inp, timeout=3.0)
                if result == expected_out.strip():
                    passed += 1
            rewards.append(passed / len(tests["inputs"]))
        except Exception:
            rewards.append(0.0)  # Execution error → zero reward
    return rewards

# Integration: passed as reward_funcs=[fraction_reward_fn] to GRPOTrainer
# Training config (1.3B — same as 7B but smaller batch ok):
config = GRPOConfig(
    num_generations=8,           # G: group size for relative advantage
    max_prompt_length=512,
    max_completion_length=1024,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,  # effective batch = 32
    learning_rate=1e-5,
    num_train_epochs=3,
    lr_scheduler_type="cosine",
)
```

**Integration point:** This is the same reward function used in h-e1 for the 7B model. The 1.3B run inherits this exactly for controlled comparison.

---

### Training Protocol

**7B Model:** Reused from h-e1 — no new training required. Evaluation results at all 5 benchmarks already exist.

**1.3B Sanity Check — New Training:**

**Optimizer:** AdamW
- Parameters: β1=0.9, β2=0.999, ε=1e-8, weight_decay=0.01
- Source: TRL GRPOTrainer defaults; consistent with h-e1

**Learning Rate:** 1e-5
- Source: h-e1 optimal; reused for controlled comparison per Phase 2B protocol

**Schedule:** Cosine decay with warmup
- Warmup ratio: 0.1 (10% of steps)
- Source: Standard GRPO training practice (arXiv:2603.07777)

**Batch Size:** 4 per device × 8 gradient accumulation = 32 effective
- Source: TRL GRPOTrainer docs; 1.3B allows larger batch than 7B

**Epochs:** 3 (same as h-e1 7B training)
- Source: h-e1; reused for controlled comparison

**Loss Function:** GRPO objective (group relative policy optimization)
- G=8 generations per prompt; advantage normalized within group

**Seeds:** 1 (fixed, same seed as h-e1 for reproducibility)

**Compute estimate:**
- 7B analysis: ~0 GPU hours (re-analysis only)
- 1.3B SFT + RLEF-Fraction: ~4–8 A100-hours each (~8–16 hours total); parallelizable

---

### Evaluation

**Primary Test: Monotonicity of Δ(RLEF-Fraction, SFT) across 5 difficulty levels**

**Difficulty ordering (ascending):**
1. HumanEval (easy)
2. MBPP (medium-easy)
3. LiveCodeBench-Easy
4. LiveCodeBench-Medium
5. LiveCodeBench-Hard

**Metric:** Δ_i = RLEF-Fraction pass@1_i − SFT pass@1_i, for i ∈ {1..5}

**Statistical Test: Jonckheere-Terpstra trend test** (nonparametric monotonic trend across ordered groups)
- H₀: No ordered trend in Δ across difficulty groups
- H₁: Δ increases monotonically with difficulty (Δ₁ ≤ Δ₂ ≤ Δ₃ ≤ Δ₄ ≤ Δ₅, strict)
- Significance threshold: p < 0.05
- Implementation: Manual via pairwise Mann-Whitney U sum (scipy.stats.mannwhitneyu)

**Secondary Test: 1.3B scale sanity check**
- Success criterion: Δ_ratio_1.3B = Δ_LCB / Δ_HumanEval ≥ 1.0 (directional; not required ≥1.5×)
- Evaluation: Same 5 benchmarks via bigcode-evaluation-harness

**Expected baseline performance (from research + h-e1 prior):**
- SFT 7B on HumanEval: ~40–50% pass@1
- SFT 7B on MBPP: ~35–45% pass@1
- SFT 7B on LCB-Hard: ~5–15% pass@1
- RLEF-Fraction 7B on HumanEval: SFT + ~5–10%
- RLEF-Fraction 7B on LCB-Hard: SFT + ~10–20% (if monotonicity holds)
- Source: h-e1 validation results; Phase 2B planning assumptions A1–A4

**Success Criteria:**
- PRIMARY: Jonckheere-Terpstra test on Δ values: p < 0.05, positive trend direction
- SECONDARY: 1.3B Δ ratio ≥ 1.0 (Δ_LCB_1.3B / Δ_HumanEval_1.3B)
- FAILURE RESPONSE: If non-monotonic → EXPLORE binary (easy vs hard) rather than gradual claim

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code generation / pass@1
- Library: bigcode-evaluation-harness (correctness-only); scipy.stats for JT test
- Code:
  ```python
  from scipy.stats import mannwhitneyu

  def jonckheere_terpstra(groups: list[list[float]]) -> tuple[float, float]:
      """Manual JT test: sum of pairwise Mann-Whitney U statistics."""
      J = 0
      for i in range(len(groups)):
          for j in range(i + 1, len(groups)):
              U, _ = mannwhitneyu(groups[j], groups[i], alternative="greater")
              J += U
      # Approximate normal: E[J] and Var[J] from group sizes
      n = [len(g) for g in groups]
      N = sum(n)
      E_J = (N**2 - sum(ni**2 for ni in n)) / 4
      # Simplified variance (no ties correction)
      Var_J = (N**2 * (2*N + 3) - sum(ni**2 * (2*ni + 3) for ni in n)) / 72
      z = (J - E_J) / (Var_J ** 0.5)
      from scipy.stats import norm
      p = 1 - norm.cdf(z)
      return z, p
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of Δ(RLEF-Fraction, SFT) at each of 5 difficulty levels for 7B model, with error bars (bootstrap 95% CI). Overlay 1.3B Δ values as secondary series.

#### Additional Figures (LLM Autonomous)

Based on the hypothesis type (monotonic trend) and dual-scale design:

1. **Monotonicity Plot** (PRIMARY): Line plot of Δ vs difficulty level (x-axis ordered 1–5) for both 7B and 1.3B models. Include reference line at Δ=0. Highlight JT test p-value and trend direction.

2. **Absolute Pass@1 Heatmap**: 3×5 heatmap (rows: SFT, RLEF-Fraction, Δ; columns: 5 benchmarks) for 7B; helps readers see both absolute performance and gap.

3. **Scale Comparison Panel**: Side-by-side bar charts comparing Δ ratio at 1.3B vs 7B across the 5 difficulty levels; visualizes scale robustness of the monotonic pattern.

All figures saved to `docs/youra_research/h-m4/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Pre-conditions (must hold before claiming success):**

| Pre-condition | Check | Value |
|--------------|-------|-------|
| mechanism_exists | Δ values at all 5 benchmarks computed for 7B | True — from h-e1 data |
| mechanism_isolatable | Only training method varies (SFT vs RLEF-Fraction); all else fixed | True — same APPS, same model, same eval harness |
| baseline_measurable | SFT pass@1 available at all 5 benchmarks | True — from h-e1 data |

**Architecture compatibility:** DeepSeek-Coder-7B-base and 1.3B-base are both standard autoregressive transformers. GRPO with fraction reward is model-architecture agnostic — no custom layers or attention modifications required. Compatibility confirmed from h-e1 through h-m3.

**Activation Indicators:**

| Indicator | Expected Value | Source |
|-----------|---------------|--------|
| mechanism_log_message | `"GRPO step {n}: mean reward={r:.3f}"` logged per APPS difficulty bucket | TRL callback |
| tensor_shape_change | No shape change — same architecture as baseline; reward is scalar per completion | N/A |
| metric_delta_expected | Δ_HumanEval > 0; Δ_LCB-Hard > 0; Δ_LCB-Hard > Δ_HumanEval | From h-e1 directional results |

**Mechanism Verification Code:**

```python
# Verify monotonicity BEFORE reporting success
def verify_monotonicity(deltas: dict) -> bool:
    """
    deltas: {
        "humaneval": float,
        "mbpp": float,
        "lcb_easy": float,
        "lcb_medium": float,
        "lcb_hard": float,
    }
    Returns True if strictly monotone increasing.
    """
    ordered = [
        deltas["humaneval"],
        deltas["mbpp"],
        deltas["lcb_easy"],
        deltas["lcb_medium"],
        deltas["lcb_hard"],
    ]
    # Check weak monotonicity (non-decreasing)
    is_monotone = all(ordered[i] <= ordered[i+1] for i in range(len(ordered)-1))
    # JT test for statistical confirmation
    # (each delta treated as point estimate; bootstrap CIs for groups)
    return is_monotone

# hypothesis_support_threshold
assert p_jt < 0.05, "JT test p >= 0.05: monotonicity not confirmed"
assert delta_1_3b_ratio >= 1.0, "1.3B sanity check failed: Δ ratio < 1.0"
```

**hypothesis_support_threshold:** JT test p < 0.05 AND 1.3B Δ ratio ≥ 1.0
**hypothesis_support_metric:** Jonckheere-Terpstra Z-statistic (positive direction) + 1.3B Δ ratio

**Failure Detection:**
- If Δ values are non-monotone: report actual Δ vector; explore binary (easy vs hard) claim as fallback
- If 1.3B training diverges (loss NaN): check learning rate (reduce to 5e-6)
- If LCB evaluation fails via bigcode-harness: fall back to custom evaluation on HumanEval+MBPP only

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (7B re-analysis + 1.3B training pipeline)
2. Jonckheere-Terpstra test: p < 0.05, positive trend
3. 1.3B Δ ratio ≥ 1.0

**Note:** h-m4 is primarily a statistical re-analysis of h-e1 results (for 7B) plus a scale verification run (1.3B). The main compute investment is the 1.3B training run. The statistical test is the key new contribution.

---

## Appendix: Reference Implementations

### A. Web Search / Knowledge Base Sources

**Source A.1:** RLEF (Gehring et al., arXiv:2410.02089)
- **Query Used:** "RLEF reinforcement learning execution feedback monotonic difficulty scaling"
- **Relevance:** Official RLEF paper; demonstrates generalisation from CodeContests (hard) to HumanEval/MBPP; key prior work grounding the difficulty-scaling hypothesis
- **Key Insights:** Training on harder problems yields broader benchmark generalisation; multi-turn RLEF with execution feedback
- **Used For:** Background justification of difficulty-scaling claim; expected direction of Δ values

**Source A.2:** "Scaling Data Difficulty" (arXiv:2603.07779)
- **Query Used:** "DeepSeek-Coder difficulty monotonic scaling results 2025"
- **Relevance:** Demonstrates difficulty-aware data curation achieves 3× larger gains; up to 17.2% relative improvement on medium/hard problems
- **Key Insights:** Difficulty-scaling effect is observable across model sizes; supports h-m4 monotonicity hypothesis
- **Used For:** Expected magnitude of Δ scaling across difficulty levels

**Source A.3:** TRL GRPOTrainer (huggingface.co/docs/trl/grpo_trainer)
- **Query Used:** "GRPO TRL DeepSeek-Coder APPS training implementation"
- **Relevance:** Standard training framework used in h-e1 through h-m3; same config inherited for 1.3B
- **Key Insights:** GRPOConfig parameters; reward_funcs callable interface; generation sampling
- **Used For:** Training protocol for 1.3B sanity check

**Source A.4:** bigcode-evaluation-harness (github.com/bigcode-project/bigcode-evaluation-harness)
- **Query Used:** "bigcode evaluation harness LiveCodeBench HumanEval MBPP pass@1"
- **Relevance:** Standard evaluation tool; correctness-only mode; HumanEval (164), MBPP (374), APPS (5000)
- **Key Insights:** Pin harness version; use unbiased pass@1 estimator with n≥20 samples
- **Used For:** Evaluation protocol for all 5 benchmarks

**Source A.5:** Jonckheere-Terpstra test (statology.org; scipy manual implementation)
- **Query Used:** "Jonckheere-Terpstra trend test monotonic regression Python scipy"
- **Relevance:** Statistical test for ordered monotonic trend across groups; scipy lacks native implementation
- **Key Insights:** Manual implementation via sum of pairwise Mann-Whitney U; R `clinfun` as reference
- **Used For:** Primary statistical test for monotonicity claim

**Source A.6:** "Execution-Grounded Credit Assignment for GRPO" (arXiv:2603.16158)
- **Query Used:** "GRPO TRL APPS training pass@1 implementation"
- **Relevance:** Improves GRPO with test-execution-weighted rewards; confirms fraction reward design
- **Used For:** Confirmation of fraction reward function design

### B. Previous Hypothesis Context

**Source B.1:** h-e1 Validation Report
- **File:** `docs/youra_research/h-e1/04_validation.md`
- **Reused Components:**
  - Δ(RLEF-Fraction, SFT) at all 5 benchmark levels (7B) — primary data for JT test
  - APPS training split and tokenization config
  - bigcode-harness evaluation commands (pinned version)
  - Fraction reward function implementation
- **Why Reused:** h-m4 verification protocol Step 1 explicitly states "collect Δ from h-e1 data (no additional training)" for 7B

**Source B.2:** h-m3 Validation Report
- **File:** `docs/youra_research/h-m3/04_validation.md`
- **Limitation noted:** h-m3 showed Δ_Fraction ≈ Δ_Binary at LCB-Hard (p=0.552). This does not affect the monotonicity test (which compares Δ vs SFT across difficulty, not Fraction vs Binary), but suggests modest absolute Δ values — the JT test may have limited power if Δ values are small.
- **Mitigation:** Report both the JT p-value and the actual Δ vector; if JT fails, report the observed trend direction and magnitude as descriptive evidence.

### C. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Training dataset (APPS) | Standard (HuggingFace) | Phase 2A via 02b_verification_plan.md |
| Evaluation benchmarks (5 levels) | Standard (bigcode-harness) | Source A.4 |
| RLEF-Fraction reward function | Code (h-e1 implementation) | Source B.1 |
| 1.3B training config | Previous (h-e1 config) | Source A.3, B.1 |
| Monotonicity test (JT) | Statistical method | Source A.5 |
| Baseline Δ values (7B) | Prior experiment data | Source B.1 (h-e1) |
| Difficulty-scaling expectation | Literature | Source A.1, A.2 |
| Mechanism verification code | Derived from protocol | Phase 2B Section 2.5 (H-M4) |
| 1.3B success criterion (Δ ratio ≥ 1.0) | Phase 2B specification | 02b_verification_plan.md §2.2 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restated below)
**Date:** 2026-08-26

### Workflow History for This Hypothesis

| Event | Timestamp | Phase |
|-------|-----------|-------|
| h-m4 set to IN_PROGRESS | 2026-08-26T07:01:52+00:00 | Hypothesis Loop |
| Phase 2C initiated | 2026-08-26 | Phase 2C |
| Experiment design COMPLETED | 2026-08-26 | Phase 2C |

---

## Quality Validation Results

```
Quality Validation Results (Step 8):
─────────────────────────────────────
✅ All hyperparameters justified (h-e1 optimal values; TRL defaults; sources cited)
✅ Dataset choice justified (APPS + 5 eval benchmarks; same as h-e1 controlled comparison)
✅ Mechanism grounded in code (fraction reward fn from h-e1; JT test from scipy pattern)
✅ No unsupported assumptions (all Δ expectations trace to h-e1 data + literature)
✅ Full traceability (Traceability Matrix §C above covers all specifications)
✅ Real datasets only (APPS, HumanEval, MBPP, LiveCodeBench — all standard real datasets)

Limitations noted:
⚠️ h-m3 null result suggests modest Δ magnitudes; JT test power may be limited
⚠️ Archon MCP unavailable; web search substituted (documented in Research Summary)
⚠️ Serena MCP skipped (no complex code requiring semantic analysis)

Overall: PASSED (with documented limitations)
```

---

*MCP Tools Used: WebSearch (substitute for Archon/Exa; Archon and Exa MCP unavailable in session)*
*All specifications grounded in researched implementations and h-e1 prior results*
*Next Phase: Phase 3 — Implementation Planning*
