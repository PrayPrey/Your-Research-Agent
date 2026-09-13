---
hypothesis_id: h-m3
type: MECHANISM
base_hypothesis: h-m2
generated_at: 2026-08-21
author: yoon303@etri.re.kr
---

Applied: incremental-extension API pattern (extend H-M2 analyze.py with gap trajectory functions)
Applied: early-stop guard pattern (check cold-start after fixed step window before full run)

# Logic: H-M3 — Proxy Temporal Stability

## Codebase Analysis (Serena)

**Project Type**: INCREMENTAL (extends H-M2)
**Status**: API signatures verified from actual H-M2 code files
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Relevant Symbols Found**:
- `run_grpo(cfg, dataset, output_dir, condition) -> list[dict]` in `train.py` — returns log_history
- `extract_frac_zero_std(log_history) -> list[float]` in `analyze.py`
- `compute_gate_metrics(frac_var, frac_rnd, checkpoints) -> dict` in `analyze.py`
- `make_execution_reward(timeout) -> callable` in `reward.py`
- `load_mbpp_subsets(cfg) -> tuple` in `dataset.py` — uses `"top_ids"` key (verified line 13)
- `H_M2Config.max_new_tokens` field (int=512) maps to `GRPOConfig(max_new_tokens=...)` — H-M3 renames to `max_completion_length` to match TRL API directly
- Import style: flat `from config import H_M2Config` (no package); run from code/ directory

---

## External Dependencies API (Base Hypothesis H-M2)

Signatures verified from `docs/youra_research/h-m2/code/`:

```python
# dataset.py — COPY VERBATIM, no changes
def load_variance_50_ids(profiling_json: str, k: int = 50) -> list[int]:
    """Load top-k task_ids from H-E1 JSON. Key: 'top_ids' (verified line 13)."""

def load_random_50_ids(mbpp_train, k: int = 50, seed: int = 42) -> list[int]:
    """numpy.random.default_rng(seed).choice over all task_ids."""

def build_subset(mbpp_train, task_ids: list[int]) -> Dataset:
    """Filter mbpp_train by task_id membership. Validates len == k."""

def load_mbpp_subsets(cfg) -> tuple[Dataset, Dataset, list[int], list[int]]:
    """Returns (variance_50_ds, random_50_ds, variance_50_ids, random_50_ids)."""

# reward.py — COPY VERBATIM, no changes
def make_execution_reward(timeout: float = 5.0) -> callable:
    """Factory returning TRL-compatible reward_fn(completions, prompts, **kwargs) -> list[float]."""

# train.py — MODIFY: rename max_new_tokens→max_completion_length + early-stop
def run_grpo(cfg, dataset, output_dir, condition) -> tuple[list[dict], bool]:
    """H-M3 version returns (log_history, early_stopped). See L-8-2."""

# analyze.py — EXTEND: keep existing functions + add new ones below
def extract_frac_zero_std(log_history: list[dict]) -> list[float]:
    """Existing H-M2 function — REUSE AS-IS."""

def compute_gate_metrics(frac_var, frac_rnd, checkpoints=None) -> dict:
    """Existing H-M2 function — REUSE AS-IS for Fig 1 bar chart (cumulative mean)."""
```

**Critical notes from actual code:**
- H-E1 JSON key is `"top_ids"` (not `"top50_ids"` — verified from dataset.py line 13)
- `mbpp_subset="full"` (not `"sanitized"`) — verified from H-M2 config.py
- `max_new_tokens` in H-M2 GRPOConfig call must become `max_completion_length` in H-M3

---

## A-4: Extend analyze.py [Complexity: 10, Budget: 2 subtasks]

### L-4-1: verify_warm_start_succeeded

**API Signature:**
```python
def verify_warm_start_succeeded(
    log_history_var50: list[dict],
    log_history_rnd50: list[dict],
) -> tuple[bool, dict]:
    """
    Check that warm-start config produced nonzero rewards in at least one condition.
    Args:
        log_history_var50: trainer.state.log_history from variance-50 run
        log_history_rnd50: trainer.state.log_history from random-50 run
    Returns:
        (warm_start_ok, stats) where stats = {max_reward_var50, max_reward_rnd50}
    """
```

**Pseudo-code:**
```python
def verify_warm_start_succeeded(log_history_var50, log_history_rnd50):
    def _extract_rewards(log_history):
        return [
            e.get("rewards/reward_fn/mean", 0.0)
            for e in log_history
            if "rewards/reward_fn/mean" in e
        ]

    var_rewards = _extract_rewards(log_history_var50)
    rnd_rewards = _extract_rewards(log_history_rnd50)

    max_var = max(var_rewards, default=0.0)
    max_rnd = max(rnd_rewards, default=0.0)
    warm_start_ok = any(r > 0.0 for r in var_rewards + rnd_rewards)

    return warm_start_ok, {
        "max_reward_var50": max_var,
        "max_reward_rnd50": max_rnd,
        "warm_start_ok": warm_start_ok,
    }
```

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | verify_warm_start | Extract rewards/reward_fn/mean per step; any(r>0) across both conditions |

---

### L-4-2: compute_gap_trajectory

**API Signature:**
```python
def compute_gap_trajectory(
    frac_var: list[float],
    frac_rnd: list[float],
    log_steps: list[int],
) -> tuple[dict, float, float, float, float]:
    """
    Compute per-step gap and extract checkpoint values.
    Args:
        frac_var: frac_reward_zero_std per step for variance-50 (len = n_logged_steps)
        frac_rnd: frac_reward_zero_std per step for random-50 (len = n_logged_steps)
        log_steps: step indices corresponding to frac_var/frac_rnd entries (1-indexed)
    Returns:
        (gap_by_step, gap_at_10, gap_at_20, gap_at_50, gap_retention)
        gap_by_step: dict[int, float] — {step: frac_rnd - frac_var}
        gap_retention: gap_at_50 / gap_at_10 if gap_at_10 > 0 else 0.0
    """
```

**Pseudo-code:**
```python
def compute_gap_trajectory(frac_var, frac_rnd, log_steps):
    assert len(frac_var) == len(frac_rnd) == len(log_steps), "Lengths must match"

    gap_by_step = {
        step: rnd - var
        for step, var, rnd in zip(log_steps, frac_var, frac_rnd)
    }

    gap_at_10 = gap_by_step.get(10, 0.0)
    gap_at_20 = gap_by_step.get(20, 0.0)
    gap_at_50 = gap_by_step.get(50, 0.0)

    if gap_at_10 > 0:
        gap_retention = gap_at_50 / gap_at_10
    else:
        gap_retention = 0.0   # undefined — will be noted as N/A in results

    p1_pass = gap_at_10 > 0 and gap_at_20 > 0 and gap_at_50 > 0
    p2_pass = gap_retention >= 0.5 if gap_at_10 > 0 else False

    return gap_by_step, gap_at_10, gap_at_20, gap_at_50, gap_retention

# Helper: extract log_steps from log_history
def extract_log_steps(log_history: list[dict]) -> list[int]:
    return [int(e["step"]) for e in log_history if "step" in e and "frac_reward_zero_std" in e]
```

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-2 | compute_gap_trajectory | Per-step gap dict; checkpoint extraction at 10/20/50; gap_retention = gap_50/gap_10 |

---

## A-6: Modify run_experiment.py [Complexity: 11, Budget: 3 subtasks]

### L-6-1: Updated main() orchestration flow

**API Signature:**
```python
def main(cfg: H_M3Config = None) -> dict:
    """
    Orchestrate warm-start GRPO experiment.
    Returns gate results dict (same schema as gate_results.json).
    sys.exit(1) if warm-start fails or gate fails.
    """
```

**Pseudo-code:**
```python
def main(cfg=None):
    if cfg is None:
        cfg = H_M3Config()

    # 1. Environment validation
    _validate_env(cfg)

    # 2. Load data
    variance_50_ds, random_50_ds, variance_50_ids, random_50_ids = load_mbpp_subsets(cfg)

    # 3. Run Condition A (variance-50)
    print("[H-M3] Training Condition A: variance-50 (warm-start)")
    log_var, early_stopped_var = run_grpo(cfg, variance_50_ds,
                                          f"{cfg.results_dir}/variance50", "variance50")

    # 4. Run Condition B (random-50)
    print("[H-M3] Training Condition B: random-50 (warm-start)")
    log_rnd, early_stopped_rnd = run_grpo(cfg, random_50_ds,
                                          f"{cfg.results_dir}/random50", "random50")

    # 5. Warm-start validation
    warm_start_ok, warm_stats = verify_warm_start_succeeded(log_var, log_rnd)
    if not warm_start_ok:
        _handle_cold_start_explore(cfg, log_var, log_rnd, warm_stats,
                                   variance_50_ids, random_50_ids)
        sys.exit(1)  # EXPLORE finding — non-zero exit

    # 6. Extract frac_zero_std series
    frac_var = extract_frac_zero_std(log_var)
    frac_rnd = extract_frac_zero_std(log_rnd)
    log_steps_var = extract_log_steps(log_var)
    log_steps_rnd = extract_log_steps(log_rnd)
    # Use shorter series if runs differ (early-stop case)
    n = min(len(frac_var), len(frac_rnd))
    log_steps = log_steps_var[:n]
    frac_var, frac_rnd = frac_var[:n], frac_rnd[:n]

    # 7. Gap trajectory analysis
    gap_by_step, gap_at_10, gap_at_20, gap_at_50, gap_retention = \
        compute_gap_trajectory(frac_var, frac_rnd, log_steps)

    # 8. Gate evaluation
    gate_metrics = compute_gate_metrics(frac_var, frac_rnd, cfg.gate_checkpoints)
    p1_pass = gap_at_10 > 0 and gap_at_20 > 0 and gap_at_50 > 0
    p2_pass = gap_retention >= 0.5 if gap_at_10 > 0 else False
    gate_passed = p1_pass

    # 9. Save results + figures
    save_results(cfg, warm_start_ok, gap_by_step, gap_at_10, gap_at_20, gap_at_50,
                 gap_retention, frac_var, frac_rnd, variance_50_ids, random_50_ids,
                 gate_passed, p1_pass, p2_pass, warm_stats)
    generate_all_figures(cfg, gate_metrics, gap_by_step, gap_at_10, gap_at_20,
                         gap_at_50, gap_retention, frac_var, frac_rnd, log_var, log_rnd)

    # 10. Report
    _print_gate_report(warm_start_ok, p1_pass, p2_pass, gap_at_10, gap_at_20, gap_at_50, gap_retention)

    return {"gate_passed": gate_passed, "p1_pass": p1_pass, "p2_pass": p2_pass,
            "gap_retention": gap_retention, "warm_start_ok": warm_start_ok}
```

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | main_orchestration | Full flow: env validate → load data → train × 2 → warm-start check → gap analysis → gate → save |

---

### L-6-2: Cold-start EXPLORE early-exit logic

**API Signature:**
```python
def _handle_cold_start_explore(
    cfg: H_M3Config,
    log_var: list[dict],
    log_rnd: list[dict],
    warm_stats: dict,
    variance_50_ids: list[int],
    random_50_ids: list[int],
) -> None:
    """
    Handle cold-start failure: save partial results JSON with EXPLORE finding.
    Prints EXPLORE report. Does NOT sys.exit — caller handles exit.
    """
```

**Pseudo-code:**
```python
def _handle_cold_start_explore(cfg, log_var, log_rnd, warm_stats, var_ids, rnd_ids):
    print("[H-M3] EXPLORE: Warm-start failed — cold-start persists.")
    print(f"  max_reward_var50: {warm_stats['max_reward_var50']:.4f}")
    print(f"  max_reward_rnd50: {warm_stats['max_reward_rnd50']:.4f}")
    print("  Proxy temporal stability cannot be tested in cold-start regime.")
    print("  Recommendation: try warmer model or online selection for H-M4.")

    explore_results = {
        "warm_start_succeeded": False,
        "gate_passed": False,
        "p1_pass": False,
        "p2_pass": False,
        "gap_by_checkpoint": {"10": None, "20": None, "50": None},
        "gap_retention": None,   # N/A — undefined in cold-start
        "max_rewards": warm_stats,
        "explore_finding": "cold_start_persists",
        "config": {"max_steps": cfg.max_steps, "learning_rate": cfg.learning_rate,
                   "max_completion_length": cfg.max_completion_length,
                   "num_generations": cfg.num_generations, "seed": cfg.seed},
        "variance_50_ids": var_ids,
        "random_50_ids": rnd_ids,
    }
    os.makedirs(cfg.results_dir, exist_ok=True)
    with open(f"{cfg.results_dir}/gate_results.json", "w") as f:
        json.dump(explore_results, f, indent=2)
```

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-2 | cold_start_explore_handler | Save EXPLORE JSON with gap=None fields; print diagnostic; caller does sys.exit(1) |

---

### L-6-3: build_gate_report

**API Signature:**
```python
def _print_gate_report(
    warm_start_ok: bool,
    p1_pass: bool,
    p2_pass: bool,
    gap_at_10: float,
    gap_at_20: float,
    gap_at_50: float,
    gap_retention: float,
) -> None:
    """Print structured gate report to stdout."""
```

**Pseudo-code:**
```python
def _print_gate_report(warm_start_ok, p1_pass, p2_pass, gap_at_10, gap_at_20, gap_at_50, gap_retention):
    print("=" * 60)
    print("[H-M3] GATE REPORT")
    print("=" * 60)
    print(f"  Warm-start:    {'PASS' if warm_start_ok else 'FAIL (cold-start)'}")
    print(f"  P1 (gap>0 at 10,20,50): {'PASS' if p1_pass else 'FAIL'}")
    print(f"    gap_at_10 = {gap_at_10:.4f}")
    print(f"    gap_at_20 = {gap_at_20:.4f}")
    print(f"    gap_at_50 = {gap_at_50:.4f}")
    print(f"  P2 (retention>=0.5): {'PASS' if p2_pass else 'FAIL'}")
    print(f"    gap_retention = {gap_retention:.4f} (threshold: 0.5)")
    print(f"  Gate: {'PASSED' if p1_pass else 'FAILED/EXPLORE'}")
    print("=" * 60)
```

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-3 | gate_report_printer | Structured stdout report: warm-start, P1 gap values, P2 retention, overall gate |

---

## A-8: Full Experiment Run [Complexity: 14, Budget: 4 subtasks]

### L-8-1: Environment validation

**API Signature:**
```python
def _validate_env(cfg: H_M3Config) -> None:
    """Validate TRL version, CUDA, H-E1 JSON presence. Raises on failure."""
```

**Pseudo-code:**
```python
import importlib.metadata, torch, os

def _validate_env(cfg):
    # TRL version check
    trl_version = importlib.metadata.version("trl")
    from packaging.version import Version
    if Version(trl_version) < Version(cfg.min_trl_version):
        raise RuntimeError(f"TRL {trl_version} < required {cfg.min_trl_version}")
    print(f"[H-M3] TRL version: {trl_version} ✓")

    # CUDA check
    if not torch.cuda.is_available():
        print("[H-M3] WARNING: CUDA not available — training will be very slow")
    else:
        print(f"[H-M3] CUDA: {torch.cuda.get_device_name(0)} ✓")

    # H-E1 JSON
    if not os.path.exists(cfg.profiling_json):
        raise FileNotFoundError(
            f"H-E1 profiling JSON not found: {cfg.profiling_json}\n"
            "Run H-E1 experiment first."
        )
    print(f"[H-M3] H-E1 JSON: {cfg.profiling_json} ✓")

    # Output dirs
    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
```

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | env_validation | TRL version >= 0.15.0; CUDA check (warn not fail); H-E1 JSON exists; mkdir output dirs |

---

### L-8-2: Early-stop detection in run_grpo

**API Signature:**
```python
def run_grpo(
    cfg: H_M3Config,
    dataset: Dataset,
    output_dir: str,
    condition: str,
) -> tuple[list[dict], bool]:
    """
    H-M3 version: returns (log_history, early_stopped).
    Early-stops if frac_reward_zero_std == 1.0 for ALL first early_stop_check_steps steps.
    """
```

**Pseudo-code:**
```python
from trl import GRPOTrainer, GRPOConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def run_grpo(cfg, dataset, output_dir, condition):
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_id, torch_dtype=torch.bfloat16, device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dataset = dataset.map(format_prompt)

    grpo_config = GRPOConfig(
        output_dir=output_dir,
        num_generations=cfg.num_generations,
        generation_batch_size=cfg.generation_batch_size,
        max_steps=cfg.max_steps,                    # 200 (warm-start)
        learning_rate=cfg.learning_rate,            # 1e-6 (warm-start)
        max_completion_length=cfg.max_completion_length,  # 1024 (warm-start)
        beta=cfg.beta,                              # 0.0
        logging_steps=cfg.logging_steps,            # 1
        use_vllm=cfg.use_vllm,                      # False
        seed=cfg.seed,                              # 42
        save_strategy="no",
        per_device_train_batch_size=1,
        report_to="none",
    )
    reward_fn = make_execution_reward(timeout=cfg.exec_timeout)

    trainer = GRPOTrainer(
        model=model,
        processing_class=tokenizer,   # TRL 1.9.2+ uses processing_class not tokenizer
        args=grpo_config,
        train_dataset=dataset,
        reward_funcs=[reward_fn],
    )
    trainer.train()

    log_history = trainer.state.log_history

    # Early-stop detection (post-hoc — TRL trains all max_steps)
    # Check if first early_stop_check_steps logged steps ALL have frac=1.0
    frac_values = [e.get("frac_reward_zero_std", 1.0) for e in log_history
                   if "frac_reward_zero_std" in e]
    early_check = frac_values[:cfg.early_stop_check_steps]
    early_stopped = len(early_check) > 0 and all(v >= 1.0 for v in early_check)

    if early_stopped:
        print(f"[H-M3] WARNING: {condition} — frac=1.0 for first {cfg.early_stop_check_steps} steps (cold-start)")

    return log_history, early_stopped
```

**Note:** True early-stop during training requires a custom callback. For PoC scope, we run all max_steps and detect cold-start post-hoc. If future runs need wall-clock savings, add `EarlyStopCallback`.

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-2 | warm_start_run_grpo | H-M3 run_grpo: max_completion_length (not max_new_tokens); processing_class; post-hoc cold-start flag |

---

### L-8-3: Per-step gap extraction and checkpoint gate

**API Signature:**
```python
def extract_log_steps(log_history: list[dict]) -> list[int]:
    """Extract step indices from log_history entries that have frac_reward_zero_std."""
```

**Pseudo-code:**
```python
def extract_log_steps(log_history):
    return [
        int(e["step"])
        for e in log_history
        if "step" in e and "frac_reward_zero_std" in e
    ]

# Gate evaluation sequence in main():
frac_var = extract_frac_zero_std(log_var)
frac_rnd = extract_frac_zero_std(log_rnd)
log_steps = extract_log_steps(log_var)  # use var steps (both should match)
gap_by_step, gap_at_10, gap_at_20, gap_at_50, gap_retention = \
    compute_gap_trajectory(frac_var, frac_rnd, log_steps)
p1_pass = gap_at_10 > 0 and gap_at_20 > 0 and gap_at_50 > 0
```

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-3 | gap_extraction_gate | extract_log_steps(); compute_gap_trajectory(); p1/p2 gate booleans |

---

### L-8-4: Gate report and sys.exit logic

**Pseudo-code:**
```python
# In main():
_print_gate_report(warm_start_ok, p1_pass, p2_pass, gap_at_10, gap_at_20, gap_at_50, gap_retention)

# sys.exit logic
if __name__ == "__main__":
    result = main()
    # Exit 0 if P1 gate passed (warm-start + gap > 0 at all checkpoints)
    # Exit 1 if failed or EXPLORE
    sys.exit(0 if result.get("gate_passed") else 1)
```

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-4 | gate_exit_logic | Print gate report; sys.exit(0) on P1 pass, sys.exit(1) on fail/EXPLORE |

---

## Subtask Summary

| Task | Subtask ID | Description | Count |
|------|-----------|-------------|-------|
| A-4 | L-4-1 | verify_warm_start_succeeded | 1 |
| A-4 | L-4-2 | compute_gap_trajectory | 1 |
| A-6 | L-6-1 | main() orchestration | 1 |
| A-6 | L-6-2 | cold_start_explore_handler | 1 |
| A-6 | L-6-3 | gate_report_printer | 1 |
| A-8 | L-8-1 | env_validation | 1 |
| A-8 | L-8-2 | warm_start_run_grpo | 1 |
| A-8 | L-8-3 | gap_extraction_gate | 1 |
| A-8 | L-8-4 | gate_exit_logic | 1 |
| **Total** | | | **9** |
