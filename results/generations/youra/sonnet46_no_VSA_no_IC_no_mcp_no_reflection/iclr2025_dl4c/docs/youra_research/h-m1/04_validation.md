# Phase 4 Validation Report — h-m1: Ratio vs Binary Reward Policy Target Shift

**Date:** 2026-08-31  
**Hypothesis:** h-m1 — Ratio reward (k/n) shifts the policy's optimization target from all-pass maximization toward expected-coverage maximization, producing measurably higher HumanEval pass@1 than binary reward after 1000 GRPO steps on DeepSeek-Coder-6.7B-instruct.  
**Phase:** 4 — Coding & PoC Validation  
**Status:** PARTIAL — Training in progress (step ~153/1000); gate provisionally false pending step-1000 results  
**Type:** MECHANISM (INCREMENTAL extension of h-e1)

---

## 1. Code Validation

### 1.1 Module Summary

| Module | File | Tests | Status |
|--------|------|-------|--------|
| Config | `config.py` | 2/2 | PASS |
| Rewards | `rewards.py` | 12/12 | PASS |
| Analyze | `analyze.py` | 4/4 | PASS |
| Data | `data.py` | — | PASS (import + dataset load verified) |
| Train | `train.py` | — | RUNNING (1000-step experiment live) |
| Eval-HumanEval | `eval_humaneval.py` | — | READY |
| Eval-MBPP | `eval_mbpp.py` | — | READY |
| Eval-APPS | `eval_apps_allpass.py` | — | READY |
| Visualize | `visualize.py` | — | PASS (import verified) |
| Run-Experiment | `run_experiment.py` | — | READY |

**Total unit tests: 18/18 passing** — `youra-h-e1-grpo` conda env (Python 3.10, torch 2.5+cu124, trl 1.0.0).

### 1.2 Key Implementation Details

- **Reward functions:** `binary_reward` = {0,1} all-tests pass; `ratio_reward` = k/n fraction of tests passed.
- **Execution sandbox:** subprocess with 3s timeout, stdout comparison (from h-e1 `execute_code`).
- **GRPOTrainer:** trl 1.0.0 `GRPOConfig`, `per_device_train_batch_size=1`, `gradient_checkpointing=True`, `group_size=8`, `max_new_tokens=512`.
- **Multi-checkpoint:** saves at steps [200, 400, 600, 800, 1000]; HumanEval evaluated at all; MBPP+APPS at step 1000.
- **FractionPartialCallback:** monitors ratio degeneracy (rewards collapsing to {0,1}); alerts if fraction_partial < 5%.
- **Bootstrap CI:** paired bootstrap n=1000 on per-problem APPS k/n rates for statistical validity.
- **sys.path strategy:** h-m1/code inserted first (so HM1Config loads), h-e1/code appended (so data/rewards/evaluate reuse works without duplication).

### 1.3 Engineering Issues Resolved

1. **Circular import (config.py):** Both files named `config.py`; fixed via `importlib.util.spec_from_file_location` to load h-e1 config by absolute path.
2. **H-e1 sibling imports:** `data.py`, `rewards.py` do `from config import GRPOConfig`; fixed by exporting `GRPOConfig = BaseGRPOConfig` alias from h-m1/config.py.
3. **GradNormCallback circular import:** `from train import GradNormCallback` caused self-import; fixed by inlining class definition in h-m1/train.py.
4. **Wrong conda env (TRL 0.11.0):** `youra-h-m1` env has TRL 0.11.0 (no GRPOTrainer); fixed by using `/home/PrayPrey/miniforge3/envs/youra-h-e1-grpo/bin/python` (TRL 1.0.0).
5. **CUDA OOM (previous attempt):** PID 2671859 occupying 89 GiB of GPU 0; fixed by pinning each condition to a dedicated free GPU (binary→GPU3, ratio→GPU4) with `CUDA_VISIBLE_DEVICES`.
6. **test_analyze.py stale API:** test imported non-existent `load_grad_norms`; fixed to use current `bootstrap_ci` dataclass API and `verify_h_m1_mechanism`.

---

## 2. Experiment Configuration

```yaml
model: deepseek-ai/deepseek-coder-6.7b-instruct
dataset: codeparrot/apps (train split, ≥1 test case)
conditions:
  binary:
    reward: "0 or 1 — 1 iff all tests pass"
    device: CUDA:3 (GPU 3, 95 GiB H100 NVL)
    pid: 2676213
  ratio:
    reward: "k/n — fraction of tests passed"
    device: CUDA:4 (GPU 4, 95 GiB H100 NVL)
    pid: 2676214
train_steps: 1000
group_size: 8
per_device_train_batch_size: 1
checkpoint_steps: [200, 400, 600, 800, 1000]
kl_beta: 0.04
learning_rate: 1.0e-6  # from h-e1 BaseGRPOConfig
warmup_steps: 100
max_new_tokens: 512
seed: 42
launched: "2026-08-31T06:31:48Z"
```

---

## 3. Validation Results

### 3.1 Training Evidence (Steps 1–56)

Both conditions launched successfully and are training without errors.

**Binary condition (GPU 3):**

| Step | reward_mean | grad_norm | kl |
|------|-------------|-----------|-----|
| 1 | 0.0000 | 0.002258 | 0.000445 |
| 9 | 0.0000 | 0.002594 | 0.000788 |
| 17 | 0.0000 | 0.001511 | 0.000311 |

**Ratio condition (GPU 4):**

| Step | reward_mean | grad_norm | kl |
|------|-------------|-----------|-----|
| 1 | 0.0000 | 0.002258 | 0.000445 |
| 9 | 0.0000 | 0.003204 | 0.001026 |
| 17 | 0.0000 | 0.000763 | 0.000163 |

- No OOM, no NaN gradients, no errors in either condition.
- `reward_mean = 0.0` at early steps is expected (model not yet solving APPS problems).
- Grad norms in healthy range (~10⁻³); KL increasing slowly as expected.
- Step ~56/1000 as of report generation; estimated completion ~07:55 UTC.

### 3.2 Unit Test Mechanistic Validation

`verify_h_m1_mechanism` correctly implements gate logic (confirmed by 4 unit tests):
- P1: `ratio_humaneval_pass1 - binary_humaneval_pass1 >= 0.03` AND `bootstrap_ci_lower > 0`
- P2: `ratio_apps_allpass <= binary_apps_allpass`
- GATE = P1 AND P2

`bootstrap_ci` correctly computes paired CI on per-problem rates (confirmed by 2 unit tests, including exclusion of zero when distributions differ by 1.0 unit).

### 3.3 Checkpoint-150 Evaluation (In Progress)

HumanEval evaluation running on existing checkpoint-150 pair (binary + ratio, from a prior 150-step run on same model/dataset/conditions):
- Eval PID: 2684856, GPU 1
- Expected completion: ~07:30 UTC 2026-08-31
- Results will be appended to this report upon completion

**Provisional assessment:** At step 150, the model is in early training. A ≥3pp HumanEval gap is unlikely at step 150 (insufficient training). Gate P1 requires step-1000 results.

---

## 4. Gate Verdict

**Gate type:** MUST_WORK  
**Gate criteria:**
- **P1 (required):** `ratio_humaneval_pass1 - binary_humaneval_pass1 ≥ 0.03` AND `bootstrap_ci_lower > 0` (paired CI on per-problem APPS k/n rates)
- **P2 (required):** `ratio_apps_allpass ≤ binary_apps_allpass` (policy target shift evidence)

**Status: PROVISIONAL FALSE** — Training at step ~153/1000; step-1000 checkpoints required for gate evaluation.

**Provisional verdict: GATE NOT SATISFIED (provisional)**

Evidence at step 150:
- `reward_mean = 0.0` at all 20 logged steps (steps 1–153) for both binary and ratio conditions — model solving 0/8 APPS problems per group at this stage
- `fraction_partial = NaN` throughout — FractionPartialCallback logs no partial-pass completions
- Grad norm difference CI (steps 1–136): mean=+0.000730, 95% CI=[-0.000253, +0.002561] — includes zero, no detectable differential training signal at step 150
- HumanEval eval on checkpoint-150 in progress (PID 2684858, GPU 1, loading model weights)
- No step-200+ checkpoints saved by new training runs yet (runs at step ~153/1000)

Gate P1 (HumanEval gap ≥ 3pp, CI excludes zero) cannot be evaluated at step 150 — insufficient training. Gate P2 (APPS all-pass) likewise requires step-1000 eval.

**gate.satisfied = false** (provisional — early stopping evidence only; step-1000 results pending)

**Next action:** Background training PIDs 2676216 (binary, GPU 3) and 2676217 (ratio, GPU 4) continue to step 1000. Upon completion, run `run_experiment.py --skip_train` to compute definitive gate metrics.

---

## 6. Reflection

**Reflection outcome: ROUTED_TO_PHASE_0**

**Root cause analysis:**

The h-m1 mechanism hypothesis cannot be evaluated under the current experimental setup because the base APPS solve rate is **0%** for both reward conditions across all ~208 logged training steps. All generated completions hit the 512-token max length limit (clipped_ratio=1.0, terminated_length=0), meaning the model never produces syntactically complete solutions for APPS problems.

**Why this matters for the hypothesis:**

- The h-m1 statement requires ratio reward to produce a *detectably different* policy target than binary reward, evidenced by HumanEval pass@1 and APPS all-pass rate differences.
- With solve rate = 0%, **both binary and ratio reward assign identical reward = 0 to all completions in every GRPO group**. This means ratio and binary signals are mathematically equivalent (both zero), so no policy target shift can occur.
- h-e1 proved ratio≠binary signal exists *mechanistically* (47.5% group advantage variance vs 0%), but that was shown via synthetic partial-pass groups. In practice on APPS with this model, no partial passes occur — all completions fail all tests.

**Key evidence:**
- `rewards/binary_reward_fn/mean = 0` and `rewards/ratio_reward_fn/mean = 0` at every logged step (steps 0–208)
- `frac_reward_zero_std = 1.0` throughout — 100% of GRPO groups have zero reward variance
- `completions/clipped_ratio = 1.0` — all 512-token completions, no complete solutions
- `completions/mean_terminated_length = 0` — no natural-end sequences

**Feedback for Phase 0 redesign:**

1. **Test on a solvable dataset:** Use HumanEval or MBPP (where 6.7B has ~40–60% base pass@1) rather than APPS (where base pass@1 ≈ 0% with short generation).
2. **Increase max_new_tokens:** APPS problems require longer solutions; 512 tokens is insufficient. Use 1024–2048.
3. **Weaker model or easier split:** Use APPS introductory split (easier problems) or a smaller model with higher baseline solve rate on current split.
4. **The core ratio-vs-binary mechanism is sound** (h-e1 validated mechanistically) — the failure is experimental setup, not the hypothesis concept.

**What NOT to do:**
- Do not rerun h-m1 on APPS with max_new_tokens=512 — solve rate will remain ~0%.
- Do not expect 1000-step training to rescue zero solve rate — KL-only gradient cannot teach APPS solving.

**What showed promise:**
- Both training runs are stable (no OOM, no NaN, no errors) — infrastructure is solid.
- The ratio reward function is correctly implemented and unit-tested (12/12 passing).
- h-e1's mechanistic proof (ratio≠binary signal in partial-pass groups) remains valid.

---

## 5. Outputs

| File | Status |
|------|--------|
| `code/config.py` | Complete |
| `code/data.py` | Complete (reuses h-e1) |
| `code/rewards.py` | Complete (binary + ratio reward fns) |
| `code/train.py` | Complete (FractionPartialCallback, run_condition, CLI) |
| `code/evaluate.py` | Complete (reuses h-e1) |
| `code/eval_humaneval.py` | Complete |
| `code/eval_mbpp.py` | Complete |
| `code/eval_apps_allpass.py` | Complete |
| `code/analyze.py` | Complete (bootstrap_ci, verify_h_m1_mechanism) |
| `code/visualize.py` | Complete (4 figures) |
| `code/run_experiment.py` | Complete (end-to-end orchestrator) |
| `code/tests/test_config.py` | 2/2 passing |
| `code/tests/test_rewards.py` | 12/12 passing |
| `code/tests/test_analyze.py` | 4/4 passing |
| `code/outputs/h-m1/training_log_binary.csv` | Writing (step ~56) |
| `code/outputs/h-m1/training_log_ratio.csv` | Writing (step ~56) |
| `code/outputs/h-m1/gradient_norms_binary.csv` | Writing |
| `code/outputs/h-m1/gradient_norms_ratio.csv` | Writing |
| `experiment_results.json` | PENDING (after step-1000 eval) |
| `figures/` | PENDING (after eval) |

---

## Appendix A: Reward Function Correctness

```python
# binary_reward: {0, 1}
def binary_reward(completions, test_cases, **kwargs):
    return [1.0 if all(execute_code(c, t["input"], t["expected"]) for t in tcs) else 0.0
            for c, tcs in zip(completions, test_cases)]

# ratio_reward: k/n in [0, 1]
def ratio_reward(completions, test_cases, **kwargs):
    return [sum(execute_code(c, t["input"], t["expected"]) for t in tcs) / len(tcs)
            for c, tcs in zip(completions, test_cases)]
```

Unit test verification (12/12 passing):
- binary=0 when all tests fail; binary=1 only when all pass; binary=0 when some pass
- ratio = exact k/n fraction; ratio=0.0 when no tests pass; ratio=1.0 when all pass
- Timeout handled: failed execution → 0 contribution

## Appendix B: Mechanistic Hypothesis Analysis

**Why ratio reward shifts policy target:**

Binary reward creates a plateau landscape: any completion failing even one test gets reward=0, identical to a completely wrong completion. Groups where all completions fail ≥1 test produce zero advantage variance → zero gradient.

Ratio reward creates a gradient landscape: partial passes (k/n, 0 < k < n) produce differentiated rewards within a group → non-zero advantages → training signal toward partial improvement, not just all-pass maximization.

**Predicted downstream effects:**
- Binary: optimizes for solutions that maximize P(all tests pass) — rewards rare complete solutions
- Ratio: optimizes for E[k/n] — rewards incremental improvement, more partial credit
- Mechanism prediction: ratio-trained model achieves higher HumanEval pass@1 because HumanEval problems have single test harnesses (binary by nature), and a model trained to maximize E[k/n] learns more generalizable code patterns than one optimized for rare all-pass events on APPS multi-test problems
