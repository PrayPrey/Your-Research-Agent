# Experiment Design: H-M3

**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Hypothesis Statement:** During GRPO training on variance-50, the fraction of steps with nonzero reward variance (1 - frac_reward_zero_std) remains higher than random-50 throughout the full 50-step training budget, confirming that the frozen-model variance proxy does not degrade too quickly for problems to remain in the learning zone.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests temporal stability of proxy advantage. H-M3 is derived from H-M2 training logs (same execution, re-analysis) but requires a NEW training run with nonzero reward signal (warm-start configuration) due to H-M2 cold-start failure.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M2 FAILED (SHOULD_WORK gate — limitation recorded, non-blocking)
**Gate Status:** SHOULD_WORK — failure triggers EXPLORE (not STOP)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (FAILED — limitation recorded)

### Gate Condition
SHOULD_WORK gate: Gap (frac_zero_std(random-50) - frac_zero_std(variance-50)) must be positive at steps 10, 20, AND 50.
Failure response: EXPLORE — document proxy degradation rate.

---

## Continuation Context

### Previous Hypothesis Results (H-M2)
- **Gate:** FAILED — cold-start problem. `frac_reward_zero_std = 1.0` for both conditions across all 13 logged generation steps.
- **Root cause:** DeepSeek-Coder-7B-Instruct-v1.5 produces binary reward = 0.0 for all G=4 completions on MBPP in the first 50 training steps. No reward signal → no gradient → frac_zero_std = 1.0 for both conditions.
- **Key lesson:** H-M3 CANNOT re-use H-M2 logs for temporal analysis — all values are identically 1.0, so gap is 0.0 throughout. H-M3 requires a NEW training run with a warm-start configuration that produces nonzero rewards.
- **Proven components reused:**
  - TRL 1.9.2 `GRPOTrainer` with `processing_class`
  - Binary execution reward via subprocess + `make_execution_reward` factory
  - MBPP `full/train` split (374 problems, task_ids 601-974)
  - `frac_reward_zero_std` auto-logged by TRL when `logging_steps=1`
  - `youra-h-m1` conda env (torch 2.6.0+cu124, TRL 1.9.2)
  - H-E1 JSON key is `top_ids`; MBPP `full/train` not `sanitized/train`

### H-M3 Redesign Rationale
H-M3 tests proxy **temporal stability** — whether the frac_zero_std advantage of variance-50 over random-50 holds throughout 50 training steps, not just early on. To observe this, the model must have nonzero reward at some steps. The H-M2 reflection recommended three pivots; this experiment adopts the **warm-start (longer training)** approach: increase `max_completion_length` from 512 to 1024 and `max_steps` to 200 to allow the model time to produce some correct completions, while still keeping compute tractable on a single H100 NVL (~8 minutes per run). This is chosen over "warmer model" (requires new profiling) or "online selection" (requires architectural change beyond Phase 2C scope).

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: GRPO training step frac_reward_zero_std temporal logging**
- Results: Dominated by diffusion model training examples (Kandinsky, PixArt, ControlNet) — no direct relevance to GRPO RLEF temporal analysis.
- Key insight extracted: TRL official documentation confirms `frac_reward_zero_std` is the canonical metric. No Archon KB entries for GRPO training log analysis.

**Query 2: Curriculum selection proxy stability reinforcement learning**
- Results: Diffusion training examples — no RLVR curriculum content.
- Insight: Archon KB does not contain RLVR/GRPO-specific content. Research sourced from Exa (live web).

**Query 3: TRL GRPO reward variance training logs analysis**
- Results: Same diffusion-model-dominated KB. Insufficient for H-M3 design.

*Note: Archon KB appears to be seeded with image/diffusion content; RLEF/GRPO literature was obtained exclusively via Exa.*

### Archon Code Examples

**Query: GRPO training metrics logging pandas step analysis**
- Results: All diffusion training shell scripts (accelerate launch, LoRA fine-tuning) — not relevant.
- No reusable code patterns for GRPO log parsing found in Archon KB.

### Exa GitHub Implementations

**Query 1: TRL GRPO trainer frac_reward_zero_std training log parsing**

**Source 1**: HuggingFace TRL Documentation (huggingface.co/docs/trl/grpo_trainer)
- **Relevance:** Authoritative definition of `frac_reward_zero_std` metric
- **Key finding:** "The fraction of samples in the generation batch with a reward std of zero, implying there is little diversity for that prompt (all answers are correct or incorrect)."
- **Monitoring guidance:** "Persistent zero means every rollout in the group gives the same score → no advantage signal → no learning." (from OpenEnv walkthrough)
- **Log access pattern:** `trainer.state.log_history` — a list of dicts, one per logging step, each containing `frac_reward_zero_std`
- **Used for:** Temporal analysis design; log parsing code

**Source 2**: danielvanstrien.xyz — Log GRPO Completions to HuggingFace Datasets
- **Key code pattern** (Polars/Pandas per-step analysis):
  ```python
  import polars as pl
  df = pl.read_parquet("hf://datasets/.../train/**/*.parquet")
  df_sorted = df.sort("step")
  df_with_avg = df_sorted.with_columns(
      pl.col("frac_reward_zero_std")
      .rolling_mean(window_size=5, min_samples=1)
      .alias("rolling_avg")
  )
  ```
- **Used for:** Step-by-step gap trajectory computation pattern

**Source 3**: NousResearch/hermes-agent GRPO reference
- **Warning signs identified:** "`reward_std` → 0 (model collapsing to a single response)"
- **Monitoring checklist:** "Sample generations every 50–100 steps", "Check `reward_std` (>0.1)"
- **Used for:** Failure detection criteria

**Query 2: RLVR data selection proxy stability gradient signal temporal analysis**

**Source 4**: "Not only where, But when: Temporal Scheduling for RLVR" (arXiv:2605.25381)
- **URL:** https://arxiv.org/html/2605.25381v1
- **Key insight:** "Temporally scheduling the allocation criteria complements existing credit allocation methods... the scheduled credit starts from the most targeted allocation criteria to reinforce specific policy behaviors, and gradually attenuates toward general optimization."
- **Relevance to H-M3:** Confirms temporal dynamics of selection criteria are a known research dimension. Provides theoretical framing for "proxy degradation" concern in A3.
- **Used for:** Theoretical grounding for proxy stability analysis

**Source 5**: GradAlign (arXiv:2602.21492 / github.com/StigLidu/GradAlign)
- **Key insight:** "Non-stationarity of RL: rollouts are generated by an evolving policy, and learning is shaped by exploration and reward feedback... prior work often relies on manual curation or simple heuristic filters (e.g., accuracy), which can admit incorrect or low-utility problems."
- **Relevance to H-M3:** GradAlign uses validation gradient alignment as an adaptive proxy — highlights that static offline proxies (like H-M1 variance profiling) degrade as policy evolves. This is exactly what H-M3 tests.
- **Used for:** Contextualizing proxy stability concern; confirming novelty of offline frozen proxy approach

**Source 6**: Single-Rollout Hidden-State Dynamics (SHIFT, arXiv:2605.28631)
- **Key insight:** "Selection must be performed before any RL training and without labels or reward evaluation... uses RIRS magnitude as a lightweight proxy for instance utility."
- **Relevance:** Confirms frozen/offline proxy selection is an active research area; SHIFT uses one-shot hidden-state proxy. H-M3 tests temporal stability of variance-based frozen proxy.
- **Used for:** Context that offline proxy degradation is the key open question

**Source 7**: VI-CuRL (arXiv:2602.12579)
- **Key insight:** "High-confidence samples... in early stages achieves a favorable bias-variance balance... the curriculum progresses, the surrogate objective asymptotically converges to the true objective."
- **Relevance:** Confirms proxy-based curriculum should be time-bounded — matches H-M3's concern about proxy becoming stale by step 20.
- **Used for:** Success/failure threshold framing

### 🎯 Implementation Priority Assessment

**For H-M3, there is no published prior implementation to reproduce.** H-M3 is a novel analysis:
1. Primary: Re-run GRPO training with warm-start config (see Section 6.4) → parse TRL logs for per-step `frac_reward_zero_std`
2. Fallback: If warm-start produces nonzero rewards, analyze temporal gap trajectory; if still cold-start, EXPLORE and document degradation rate as N/A (gap never existed)

**Recommended Implementation Path:**
- Primary: H-M2 codebase (`docs/youra_research/h-m2/code/`) + warm-start config modifications
- Fallback: Academic result — document that proxy temporal stability cannot be tested in cold-start regime
- Justification: H-M2 code infrastructure is validated and reusable; only config changes needed

### Code Analysis (Serena MCP)

*Skipped* — No complex unfamiliar code requiring Serena analysis. H-M2 codebase is known and validated. TRL GRPOTrainer API is well-documented.

---

## Experiment Specification

### Dataset

**Dataset:** MBPP (standard)
- **Source:** google-research-datasets/mbpp (HuggingFace Datasets)
- **Type:** standard (programmatic-api)
- **Split:** full/train (374 problems, task_ids 601-974) — SAME as H-M2
- **Subset construction:**
  - variance-50: top-50 problems by variance_i from H-E1 profiling JSON (`top_ids` key)
  - random-50: numpy default_rng(42).choice over 374 train task_ids (50 unique) — SAME as H-M2 for controlled comparison
- **Evaluation:** HumanEval+ (EvalPlus, 164 problems) — NOT needed for H-M3 (H-M3 tests frac_reward_zero_std, not pass@1)
- **Preprocessing:** None (raw MBPP task descriptions, as in H-M2)
- **Hypothesis fit:** MBPP provides the training pool; H-M3 analyzes per-step reward variance dynamics from training logs

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `"google-research-datasets/mbpp"`, `subset="full"`, `split="train"`
- Code: `load_dataset("google-research-datasets/mbpp", "full", split="train")`

### Models

#### Baseline Model

**Architecture:** DeepSeek-Coder-7B-Instruct-v1.5
- **Source:** deepseek-ai/deepseek-coder-7b-instruct-v1.5 (HuggingFace)
- **Configuration:** Frozen at initialization; same checkpoint as H-E1 profiling and H-M2
- **Purpose:** Provide GRPO training subjects; NOT fine-tuned prior to experiment
- **Hypothesis fit:** Same model as H-M2 ensures direct comparability; warm-start config modification (not model change)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers AutoModelForCausalLM
- Identifier: `"deepseek-ai/deepseek-coder-7b-instruct-v1.5"`
- Code: `AutoModelForCausalLM.from_pretrained("deepseek-ai/deepseek-coder-7b-instruct-v1.5", torch_dtype=torch.bfloat16)`

#### Proposed Model

**Architecture:** DeepSeek-Coder-7B-Instruct-v1.5 + warm-start GRPO training on variance-50 subset

**Core Mechanism Implementation:**

```python
# Core Mechanism: Frozen-model variance proxy temporal stability analysis
# Based on: TRL GRPOTrainer log_history + H-M2 codebase

def run_warm_start_grpo(subset_ids, condition_name, config):
    """
    Run GRPO training with warm-start config to produce nonzero rewards.
    Args:
        subset_ids: list[int] — 50 MBPP task_ids (variance-50 or random-50)
        condition_name: str — "variance50" or "random50"
        config: H_M3Config — warm-start parameters
    Returns:
        log_history: list[dict] — per-generation-step TRL metrics
    """
    dataset = build_subset(subset_ids)  # from H-M2 dataset.py
    reward_fn = make_execution_reward()  # from H-M2 reward.py

    trainer = GRPOTrainer(
        model=load_model(config.model_id),
        processing_class=load_tokenizer(config.model_id),
        reward_funcs=[reward_fn],
        args=GRPOConfig(
            num_generations=config.G,               # 4
            generation_batch_size=config.G,          # 4
            max_steps=config.max_steps,              # 200 (warm-start)
            learning_rate=config.lr,                 # 1e-6 (warmer)
            max_completion_length=config.max_len,    # 1024 (longer)
            logging_steps=1,
            beta=0.0,
            use_vllm=False,
            save_strategy="no",
            output_dir=f"results/{condition_name}",
        ),
        train_dataset=dataset,
    )
    trainer.train()
    return trainer.state.log_history  # per-step metrics dict list


def analyze_proxy_stability(log_var50, log_rnd50):
    """
    Compute gap trajectory from TRL log_history.
    Args:
        log_var50, log_rnd50: list[dict] from trainer.state.log_history
    Returns:
        gap_by_step: dict[int, float] — step → gap (rnd - var)
        steps_with_nonzero_gap: list[int]
        gap_at_10, gap_at_20, gap_at_50: float
        gap_retention: float — gap_at_50 / gap_at_10 (proxy stability)
    """
    var_series = extract_metric(log_var50, "frac_reward_zero_std")
    rnd_series = extract_metric(log_rnd50, "frac_reward_zero_std")
    gap_by_step = {step: rnd - var
                   for step, var, rnd in zip(steps, var_series, rnd_series)}
    gap_at_10 = gap_by_step.get(10, 0.0)
    gap_at_20 = gap_by_step.get(20, 0.0)
    gap_at_50 = gap_by_step.get(50, 0.0)
    gap_retention = gap_at_50 / gap_at_10 if gap_at_10 > 0 else 0.0
    return gap_by_step, gap_at_10, gap_at_20, gap_at_50, gap_retention
```

### Training Protocol

**Warm-Start Configuration (derived from H-M2 reflection + TRL documentation):**

| Parameter | H-M2 Value | H-M3 Warm-Start Value | Rationale |
|-----------|------------|----------------------|-----------|
| max_steps | 50 | 200 | Allow time for model to produce nonzero rewards |
| learning_rate | 5e-7 | 1e-6 | Higher LR → faster reward signal emergence |
| max_completion_length | 512 | 1024 | Longer completions → higher chance of passing MBPP tests |
| num_generations (G) | 4 | 4 | Same (controlled comparison) |
| generation_batch_size | 4 | 4 | Same |
| beta | 0.0 | 0.0 | Same |
| use_vllm | False | False | Same |
| logging_steps | 1 | 1 | Per-step logging required for temporal analysis |
| save_strategy | "no" | "no" | Same |
| seed | 42 | 42 | Same |

**Optimizer:** AdamW (TRL/HF Trainer default)
- Source: TRL GRPOTrainer default; NousResearch hermes-agent GRPO reference

**LR Schedule:** Constant (no warmup)
- Source: TRL GRPOConfig default; consistent with H-M2 for controlled comparison

**Seeds:** 1 (fixed, seed=42)

**Estimated runtime:** ~8 minutes per condition on H100 NVL (2× H-M2 due to 200 steps); ~16 minutes total.

**Early stopping criterion:** If `frac_reward_zero_std = 1.0` persists for first 50 steps (as in H-M2), terminate and log as cold-start — EXPLORE finding.

**Source:** TRL docs (huggingface.co/docs/trl/grpo_trainer); H-M2 04_validation.md Section 7; reflection_report.md

### Evaluation

**Primary metric:** `frac_reward_zero_std` per generation step (logged automatically by TRL when `logging_steps=1`)

**Derived metric:** Gap trajectory = `frac_zero_std(random-50) - frac_zero_std(variance-50)` at each logged step

**Success Criteria (PoC):**
- **P1 (primary):** Gap is positive at steps 10, 20, AND 50 (variance-50 consistently produces fewer zero-gradient groups)
- **P2 (secondary):** Gap at step 50 ≥ 50% of gap at step 10 (proxy not fully degraded; retention ≥ 0.5)

**Expected baseline performance (from literature):**
- With nonzero rewards: frac_reward_zero_std for random-50 expected ~0.69 (mathematical identity: ~69% of G=4 groups have all-same rewards at random difficulty; Gradient Starvation arXiv:2605.07689)
- Variance-50 expected lower: ~0.30-0.50 (problems selected for intermediate p_i → lower probability of all-same groups)
- Expected gap at step 0 (if warm-start succeeds): ~0.20-0.40

**PoC Pass Condition:**
1. Code runs without error
2. At least one step has nonzero reward (warm-start validation)
3. Gap > 0 at steps 10, 20, AND 50

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Training log analysis (no external metric library needed)
- Library: Python built-ins + pandas/numpy
- Code: `pd.DataFrame(trainer.state.log_history)[['step', 'frac_reward_zero_std']]`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing frac_reward_zero_std at checkpoints 10, 20, 50 for variance-50 vs random-50

#### Additional Figures (LLM Autonomous)
1. **Gap Trajectory Plot:** Line plot of gap = frac_zero_std(random-50) - frac_zero_std(variance-50) across all 200 steps. Horizontal reference line at gap=0. Red region if gap goes negative (proxy degradation). Title: "Proxy Stability: Gap Trajectory Over Training Steps"
2. **per-condition frac_reward_zero_std curves:** Two lines (variance-50, random-50) over all steps. Visually shows whether they diverge, converge, or remain parallel.
3. **Gap retention bar:** Bar at step 10, 20, 50 showing gap value and P2 retention threshold.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | TRL GRPOTrainer logs `frac_reward_zero_std` per generation step | TRUE — confirmed in H-M2 execution |
| Mechanism Isolatable | variance-50 vs random-50 training runs are independent; metric logged per condition | TRUE — H-M2 codebase supports two independent runs |
| Baseline Measurable | random-50 run provides baseline frac_reward_zero_std trajectory | TRUE — same config as H-M2 random-50 run |

### Architecture Compatibility Check

**Mechanism:** Temporal analysis of frozen-model variance proxy via TRL GRPO training logs.

**Required features:**
- TRL 1.9.2+ `GRPOTrainer` with `logging_steps=1` (confirmed in H-M2)
- Binary execution reward function that returns 0 or 1 (confirmed in H-M2)
- MBPP `full/train` split with 374 problems (confirmed in H-M2)
- H-E1 profiling JSON with `top_ids` key (confirmed in H-M2)

**Incompatible configurations:**
- `logging_steps > 1` (would miss intermediate steps)
- `use_vllm=True` (changes generation dynamics)
- `mbpp_subset="sanitized"` (only 120 problems, mismatches H-E1 profiling)

> ⚠️ If warm-start config produces cold-start (frac=1.0 throughout), Phase 4 MUST log this as cold-start failure and terminate early with EXPLORE finding.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `rewards/reward_fn/mean > 0.0` at some step | `trainer.state.log_history` |
| Metric Delta | `frac_reward_zero_std < 1.0` for at least one step in either condition | `analyze.py` |
| Gap Signal | `gap = frac_rnd - frac_var > 0` at checkpoint 10 | `analyze.py:compute_gap_trajectory()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_warm_start_succeeded(log_history_var50, log_history_rnd50):
    """Check that warm-start config produced nonzero rewards."""
    var_rewards = [e.get("rewards/reward_fn/mean", 0.0)
                   for e in log_history_var50 if "rewards/reward_fn/mean" in e]
    rnd_rewards = [e.get("rewards/reward_fn/mean", 0.0)
                   for e in log_history_rnd50 if "rewards/reward_fn/mean" in e]
    warm_start_ok = any(r > 0.0 for r in var_rewards + rnd_rewards)
    return warm_start_ok, {
        "max_reward_var50": max(var_rewards, default=0.0),
        "max_reward_rnd50": max(rnd_rewards, default=0.0),
    }

def verify_proxy_stability(gap_by_step):
    """Verify gap is positive and sustained at gate checkpoints."""
    gap_10 = gap_by_step.get(10, 0.0)
    gap_20 = gap_by_step.get(20, 0.0)
    gap_50 = gap_by_step.get(50, 0.0)
    p1_pass = gap_10 > 0 and gap_20 > 0 and gap_50 > 0
    p2_pass = (gap_50 / gap_10 >= 0.5) if gap_10 > 0 else False
    return p1_pass, p2_pass, {"gap_10": gap_10, "gap_20": gap_20, "gap_50": gap_50}
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Cold-start persists | `max(rewards/reward_fn/mean) == 0.0` after 200 steps | EXPLORE: document cold-start; record gap_retention = N/A |
| Gap never positive | All gap values ≤ 0 | EXPLORE: proxy provides no temporal advantage |
| Gap degrades (retention < 0.5) | `gap_50 / gap_10 < 0.5` | Partial finding: proxy degrades; report degradation rate |
| Gap reversal | `gap_50 < 0` | EXPLORE: random-50 outperforms variance-50 at late steps |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Warm-start succeeded | `max(reward) > 0` in either condition | `trainer.state.log_history` |
| Gap positive at all gates | gap > 0 at steps 10, 20, AND 50 | `analyze.py:verify_proxy_stability()` |
| Proxy not degraded | `gap_retention = gap_50 / gap_10 ≥ 0.5` | `analyze.py:compute_gap_trajectory()` |

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Warm-start produces nonzero reward in at least one condition (validates experimental validity)
3. `gap > 0` at steps 10, 20, AND 50 (P1 primary gate)

**Fallback if warm-start still cold:** Record gap_retention = N/A; document as scope limitation. H-M3 EXPLORE finding: proxy temporal stability cannot be tested in cold-start regime with this model+MBPP config.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB:** No relevant GRPO/RLEF content found. All results were diffusion model training examples. KB appears seeded with image generation content.
- Query 1: "GRPO training step frac_reward_zero_std temporal logging" → diffusion examples (sim < 0.45)
- Query 2: "Curriculum selection proxy stability reinforcement learning" → diffusion examples (sim < 0.45)
- Query 3: "TRL GRPO reward variance training logs analysis" → diffusion examples (sim < 0.40)

*Archon Code Examples:* No relevant GRPO code patterns found.

### B. GitHub Implementations (Exa)

**Source B.1**: HuggingFace TRL Documentation
- **URL:** https://huggingface.co/docs/trl/grpo_trainer
- **Relevance:** Official definition of `frac_reward_zero_std`; `trainer.state.log_history` access pattern
- **Key insight:** "Persistent zero [frac_reward_zero_std] means every rollout in the group gives the same score → no advantage signal → no learning."
- **Used for:** Temporal analysis design; log parsing; warm-start termination criterion

**Source B.2**: danielvanstrien.xyz — Log GRPO Completions
- **URL:** https://danielvanstrien.xyz/posts/2025/grpo/trl_log_completions_to_hf_datasets.html
- **Key code pattern:**
  ```python
  df_sorted = df.sort("step")
  df_with_avg = df_sorted.with_columns(
      pl.col("frac_reward_zero_std")
      .rolling_mean(window_size=10, min_samples=1)
      .alias("rolling_avg")
  )
  ```
- **Used for:** Gap trajectory computation + rolling average visualization

**Source B.3**: NousResearch hermes-agent GRPO reference
- **URL:** https://github.com/NousResearch/hermes-agent
- **Key insight:** Warning signs — `reward_std → 0` (collapse); monitoring `reward_std > 0.1`
- **Used for:** Failure detection criteria for warm-start validation

**Source B.4**: "Not only where, But when: Temporal Scheduling for RLVR" (arXiv:2605.25381)
- **URL:** https://arxiv.org/html/2605.25381v1
- **Key insight:** Allocation criteria scheduled temporally — "starts from most targeted, gradually attenuates." H-M3 tests whether frozen offline proxy achieves this naturally.
- **Used for:** Theoretical framing of proxy stability concern; context for gap_retention metric

**Source B.5**: GradAlign (arXiv:2602.21492)
- **URL:** https://arxiv.org/html/2602.21492; https://github.com/StigLidu/GradAlign
- **Key insight:** "Non-stationarity of RL: rollouts are generated by an evolving policy." Static offline proxies may degrade.
- **Used for:** Contextualizing proxy degradation concern; novelty argument for frozen proxy

**Source B.6**: SHIFT (arXiv:2605.28631)
- **URL:** https://arxiv.org/html/2605.28631
- **Key insight:** Single-rollout hidden-state proxy for training-free RLVR selection — confirms offline proxy stability is an open research question.
- **Used for:** Background context; H-M3 novelty argument

**Source B.7**: VI-CuRL (arXiv:2602.12579)
- **Key insight:** "As curriculum progresses, surrogate objective asymptotically converges to true objective." Curriculum proxy should become less important over time.
- **Used for:** Secondary success criterion (gap_retention ≥ 0.5); proxy degradation framing

### C. Code Analysis (Serena)

*Not performed* — H-M2 codebase is validated and familiar. TRL GRPOTrainer is well-documented. No complex unknown code structures to analyze.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-M2 (`docs/youra_research/h-m2/04_validation.md`)
- **Reused components:**
  - Dataset: MBPP full/train (374 problems) — stable and validated
  - Code: `docs/youra_research/h-m2/code/` — all modules reused with config changes only
  - Config parameters: G=4, beta=0.0, use_vllm=False, seed=42, logging_steps=1, save_strategy="no"
  - Environment: `youra-h-m1` conda (torch 2.6.0+cu124, TRL 1.9.2)
- **Changes from H-M2:**
  - max_steps: 50 → 200
  - learning_rate: 5e-7 → 1e-6
  - max_completion_length: 512 → 1024
- **Why reused:** Enables controlled comparison — only warm-start config changes; all other conditions identical

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (MBPP full/train) | Previous hypothesis | H-M2 04_validation.md |
| Dataset loading code | Previous hypothesis | H-M2 code/dataset.py |
| Model (DeepSeek-Coder-7B) | Previous hypothesis | H-M2 04_validation.md |
| Model loading | Previous hypothesis | H-M2 code/train.py |
| Warm-start config (max_steps=200, lr=1e-6, max_len=1024) | Previous hypothesis | H-M2 reflection_report.md §5 |
| frac_reward_zero_std metric | GitHub/Exa | TRL docs (B.1) |
| Gap trajectory computation | GitHub/Exa | danielvanstrien.xyz (B.2) |
| Gap retention threshold (≥0.5) | Paper | VI-CuRL arXiv:2602.12579 (B.7) |
| Failure detection (reward_std → 0) | GitHub/Exa | hermes-agent (B.3) |
| Proxy degradation framing | Paper | GradAlign arXiv:2602.21492 (B.5) |
| Temporal scheduling context | Paper | arXiv:2605.25381 (B.4) |
| Mechanism verification code | Derived | H-M2 code/analyze.py pattern |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated in conversation)
**Date:** 2026-08-21

### Workflow History for This Hypothesis
- H-M3 set to IN_PROGRESS (2026-08-21T16:02:03Z)
- Phase 2C experiment design started (2026-08-21)
- H-M2 limitation context loaded (cold-start, gap=0.0 throughout)
- Warm-start redesign adopted per H-M2 reflection §5

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (TRL docs, RLVR papers), Serena (skipped — not needed)*
*All specifications grounded in researched implementations and H-M2 validated codebase*
*Next Phase: Phase 3 - Implementation Planning*
