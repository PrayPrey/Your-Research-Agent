# 4. Experimental Setup

We design experiments to answer three research questions that together characterize the advantage variance collapse phenomenon:

**RQ1:** Does task granularity determine GRPO advantage variance under controlled conditions (same model, same configuration)?

**RQ2:** Is the variance difference explained by reward sparsity — specifically by the fraction of completions receiving non-zero reward?

**RQ3:** Is the effect size practically significant for training effectiveness, not just statistically significant?

Each RQ maps directly to a claim from the Introduction. RQ1 tests the primary empirical claim (76× variance gap). RQ2 tests the mechanistic claim (reward sparsity as the causal variable). RQ3 establishes whether the observed difference is large enough to matter for gradient-based learning.

## 4.1 Datasets

We evaluate on two datasets representing contrasting task granularities:

| Dataset | Source | Split | Size | Reward Type |
|---|---|---|---|---|
| APPS | `codeparrot/apps` | train | 5,000 | Binary (all tests pass) |
| CodeContests | `deepmind/code_contests` | train | 13,328 | Binary (all tests pass) |
| SWE-bench Verified | `princeton-nlp/SWE-bench_Verified` | test | 500 | Partial (file-path overlap) |

APPS and CodeContests are combined into a single function-level condition. Both require generating self-contained Python programs that pass stdin/stdout unit tests — the strictest form of binary execution reward. SWE-bench Verified represents the repo-level condition, where the reward function provides partial credit through file-path overlap, creating a non-binary reward structure that maintains non-zero positive rates even for imperfect completions.

**Why these datasets:** This pairing is the natural contrast for our RQ1. APPS+CodeContests is the canonical dataset for function-level execution-feedback RL (used by CodeRL [Le et al., 2022] and is the planned training data for the curriculum GRPO hypothesis). SWE-bench Verified is the canonical dataset for repo-level code RL. Both are widely cited, ensuring our findings are interpretable in context of the broader literature.

## 4.2 Baselines

This experiment does not have external method baselines in the traditional sense — we are not comparing our method against prior approaches on a benchmark. Instead, the two conditions (function-level, repo-level) serve as the comparison units, with the function-level condition playing the role of the "problem setting" and the repo-level condition playing the role of the "contrast condition" that demonstrates non-degenerate training is achievable with the same model and configuration.

For the curriculum GRPO infrastructure validation (H-E1), we compare four training conditions:

| Condition | Description |
|---|---|
| curriculum | APPS tiers 0–2 for steps 0–2500; tiers 3–4 for steps 2501–5000 |
| uniform | Random sampling across all tiers proportional to dataset distribution |
| easy\_only | Exclusively APPS tiers 0–2 for all 5000 steps |
| hard\_only | Exclusively APPS tiers 3–4 for all 5000 steps |

All four conditions use the same model (DeepSeek-Coder-7B-base), same TRL 1.3.0 GRPOTrainer configuration, and same 10-step smoke test protocol. The uniform condition is the standard baseline used by CodeRL, RLEF, and DeepSeek-R1.

## 4.3 Implementation Details

**Model:** CodeLlama-7b-Instruct-hf (`codellama/CodeLlama-7b-Instruct-hf`)
- No additional fine-tuning; used as-is from HuggingFace Hub
- Loaded in bf16 with gradient checkpointing enabled

**Training framework:** TRL 1.3.0 GRPOTrainer
- Key API note: `GRPOConfig` in TRL 1.3.0 requires `generation_kwargs={"max_new_tokens": 512}` rather than `max_new_tokens` directly
- CUDA\_VISIBLE\_DEVICES=0 (single NVIDIA H100 NVL)

**Dataset preprocessing:** APPS (`input_output` string format) and CodeContests (`public_tests` dict format) require schema unification. All examples are mapped to 4 uniform columns (`input_ids`, `attention_mask`, `prompt`, `test_cases_json`) via `_tokenize_and_normalize()`. APPS integers exceeding Python 3.10's string conversion limit (4300 digits) are handled via `repr()`.

**Execution reward:** Subprocess execution with 3-second timeout per test case. Binary reward (1.0 / 0.0). Each of the G=8 completions is independently executed.

## 4.4 Evaluation Metrics

**Primary metric — Advantage variance:** Per-step GRPO advantage variance, computed as the variance of all $B \times G = 32$ normalized advantages at each training step. This is the quantity that directly determines gradient signal quality in GRPO.

**Secondary metric — Positive reward rate:** Fraction of completions (across all groups in a step) receiving non-zero reward. This operationalizes the reward sparsity mechanism: if positive rate ≈ 0%, all groups are degenerate; if positive rate > 0%, some groups provide discriminative signal.

**Statistical test:** Welch's two-sample t-test on log-transformed per-step advantage variance (120 observations per condition). Two-tailed test, significance threshold $p < 0.05$. Effect size: Cohen's $d$ from log-transformed values.

**For H-E1 infrastructure validation:** Binary pass/fail per condition (all 4 conditions complete 10-step smoke test without errors, checkpoints produced, reward density CSVs written).
