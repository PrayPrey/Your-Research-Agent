---
hypothesis_id: h-m2
type: MECHANISM
generated_at: 2026-08-21
author: yoon303@etri.re.kr
---

Applied: TRL GRPOTrainer reward_funcs interface pattern
Applied: subprocess sandbox execution reward pattern for code generation

# Logic: H-M2 — Variance Selection Reduces Zero-Gradient Groups in GRPO

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (INCREMENTAL from H-M1)
**Status**: API signatures verified from actual H-M1 code
**Analyzed Path**: `docs/youra_research/h-m1/code/compare_variance_selection.py`
**Relevant Symbols Found**:
- `load_profiling_output(json_path)` → `(problem_ids, p_i, variance_i)` — reuse pattern for dataset.py
- JSON key is `"top50_ids"` (verified from H-M1 logic doc cross-referencing H-E1 actual code)
- `@dataclass` config pattern — H-M2 follows same style
- matplotlib `Agg` backend set before pyplot import — required for headless
- H-M1 is single-file; H-M2 is multi-file (train loop complexity requires split)

---

## External Dependencies API (Base Hypothesis H-E1 artifact)

Signatures verified from H-M1 logic (`03_logic.md`) which cross-referenced actual H-E1 code:

```python
# H-E1 JSON output schema — key verified as "top50_ids" (not "top_ids")
# Path: docs/youra_research/h-e1/results/mbpp_variance_profile.json
{
    "gate_passed": bool,
    "top50_ids": [int, ...],          # ← "top50_ids", NOT "top_ids"
    "problems": {
        "<task_id_str>": {
            "p_i": float,
            "variance_i": float,
            "pass_count": int,
            "k": int,                  # profiling k=8 (unrelated to selection k=50)
            "rank_by_variance": int,
        }
    },
    "metrics": {
        "count_nonzero_variance": int,
        "threshold_count": int,
        "mean_p_top50": float,
        "gate_passed": bool,
        "total_problems": int,
    }
}

# NOTE: H-M2 does NOT import H-M1 code.
# It reads H-E1 JSON directly via dataset.py::load_variance_50_ids.
# H-M1 code path (reference only): docs/youra_research/h-m1/code/compare_variance_selection.py
```

---

## A-3: Reward Function [Complexity: 10, Budget: 2 subtasks]

### L-3-1: Subprocess Execution Harness

**API Signature:**
```python
def _execute_code(code: str, test_list: list[str], timeout: float = 5.0) -> bool:
    """
    Execute code string against unit test assertions in a subprocess.
    Args:
        code: Python code string (model completion)
        test_list: list of assert statements e.g. ["assert foo(1) == 2", ...]
        timeout: seconds before subprocess killed (default 5.0)
    Returns:
        True if all tests pass, False otherwise (timeout/error/fail)
    """
```

**Pseudo-code:**
```
import subprocess, sys, tempfile, textwrap

def _execute_code(code, test_list, timeout=5.0):
    # Build script: code + newline + all assert statements
    script = code + "\n" + "\n".join(test_list)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True,
            timeout=timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False
    finally:
        os.unlink(tmp_path)
```

**Subtask:**

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | subprocess_execution_harness | Write code+tests to temp file, subprocess.run with timeout, return bool |

---

### L-3-2: TRL Reward Function Interface Adapter

**API Signature:**
```python
def make_execution_reward(timeout: float = 5.0):
    """
    Factory returning a reward function compatible with TRL GRPOTrainer.
    Args:
        timeout: per-completion execution timeout in seconds
    Returns:
        reward_fn: Callable[[list[str], list[str], **kwargs], list[float]]
    """
    def reward_fn(
        completions: list[str],    # model-generated code strings, len = batch_size
        prompts: list[str],        # original prompts (used to recover test_list)
        test_lists: list[list[str]] = None,  # passed via dataset column if available
        **kwargs,                  # TRL may pass extra kwargs; ignore
    ) -> list[float]:
        """Returns reward per completion: 1.0 if all tests pass, 0.0 otherwise."""
        ...
    return reward_fn
```

**Pseudo-code:**
```
def make_execution_reward(timeout=5.0):
    def reward_fn(completions, prompts, **kwargs):
        # TRL passes test_list via dataset extras in kwargs["test_list"]
        # or via prompts context — extract from kwargs
        test_lists = kwargs.get("test_list", [[] for _ in completions])
        rewards = []
        for code, tests in zip(completions, test_lists):
            passed = _execute_code(code, tests, timeout)
            rewards.append(1.0 if passed else 0.0)
        return rewards
    return reward_fn

# TRL GRPOTrainer calls reward_funcs with:
# reward_fn(completions=list[str], prompts=list[str], **batch_row_fields)
# Dataset columns (e.g., "test_list") are passed as kwargs automatically
```

**Critical:** TRL GRPOTrainer passes extra dataset columns as kwargs to reward_funcs. `test_list` must be a column in the dataset (not just a field on the example) for TRL to forward it. Dataset must have columns: `["prompt", "test_list"]` minimum.

**Subtask:**

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-2 | trl_reward_interface_adapter | make_execution_reward factory; handle TRL kwargs; extract test_list from kwargs |

---

## A-4: GRPO Training Runner [Complexity: 14, Budget: 4 subtasks]

### L-4-1: Prompt Formatting for GRPOTrainer

**API Signature:**
```python
def format_prompt(example: dict) -> dict:
    """
    Add "prompt" field to dataset example for TRL GRPOTrainer.
    Args:
        example: MBPP dataset row with keys: task_id, text, code, test_list
    Returns:
        dict with added "prompt" key (DeepSeek-Coder instruction format)
    """
```

**Pseudo-code:**
```
INSTRUCTION_TEMPLATE = (
    "Write a Python function to solve the following problem.\n\n"
    "Problem: {problem}\n\n"
    "Provide only the function implementation, no explanations.\n"
)

def format_prompt(example):
    return {
        **example,
        "prompt": INSTRUCTION_TEMPLATE.format(problem=example["text"])
    }

# Applied to dataset: dataset.map(format_prompt)
# Result dataset columns: task_id, text, code, test_list, prompt
```

**Subtask:**

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | prompt_formatter | DeepSeek-Coder instruction template; dataset.map(format_prompt); preserve test_list column |

---

### L-4-2: GRPOConfig Construction

**API Signature:**
```python
def build_grpo_config(cfg: H_M2Config, output_dir: str, condition: str) -> GRPOConfig:
    """
    Build TRL GRPOConfig from H_M2Config dataclass.
    Args:
        cfg: experiment configuration
        output_dir: path for trainer checkpoints
        condition: "variance50" | "random50" (for output_dir suffixing)
    Returns:
        GRPOConfig instance
    """
```

**Pseudo-code:**
```python
from trl import GRPOConfig

def build_grpo_config(cfg, output_dir, condition):
    return GRPOConfig(
        output_dir=output_dir,
        num_generations=cfg.num_generations,            # 4
        generation_batch_size=cfg.generation_batch_size, # 4
        max_steps=cfg.max_steps,                        # 50
        learning_rate=cfg.learning_rate,                # 5e-7
        beta=cfg.beta,                                  # 0.0 — no KL
        logging_steps=cfg.logging_steps,                # 1 — per-step frac_zero_std
        save_steps=cfg.save_steps,                      # [10, 20, 50]
        use_vllm=cfg.use_vllm,                          # False
        seed=cfg.seed,                                  # 42
        max_new_tokens=cfg.max_new_tokens,              # 512
        per_device_train_batch_size=1,                  # one problem per fwd pass
        report_to="none",                               # no wandb by default
    )
```

**Subtask:**

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-2 | grpo_config_builder | Map H_M2Config → GRPOConfig; set per_device_train_batch_size=1; report_to="none" |

---

### L-4-3: GRPOTrainer Initialization and Training

**API Signature:**
```python
def run_grpo(
    cfg: H_M2Config,
    dataset: Dataset,
    output_dir: str,
    condition: str,     # "variance50" | "random50"
) -> list[dict]:
    """
    Load model, build trainer, run training for one condition.
    Args:
        cfg: experiment config
        dataset: 50-problem HuggingFace Dataset with columns [prompt, test_list, ...]
        output_dir: checkpoint save path
        condition: label for logging
    Returns:
        trainer.state.log_history (list of dicts, one per logging step)
    """
```

**Pseudo-code:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOTrainer

def run_grpo(cfg, dataset, output_dir, condition):
    print(f"[H-M2] Starting GRPO training: {condition}")

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Format dataset: add "prompt" column
    dataset = dataset.map(format_prompt)

    # Build config + reward
    grpo_config = build_grpo_config(cfg, output_dir, condition)
    reward_fn = make_execution_reward(timeout=cfg.exec_timeout)

    # Train
    trainer = GRPOTrainer(
        model=model,
        args=grpo_config,
        train_dataset=dataset,
        reward_funcs=[reward_fn],
        tokenizer=tokenizer,
    )
    trainer.train()

    return trainer.state.log_history

# Tensor shapes during training:
# Input tokens: (batch=1, seq_len) — one problem per step
# Generated completions: (num_generations=4, max_new_tokens=512) per group
# Rewards tensor: (batch=1, num_generations=4) — binary 0/1
# Grouped reward std: scalar per group → frac with std==0 over batch
```

**Subtask:**

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-3 | grpo_trainer_runner | Load model/tokenizer (bfloat16, device_map=auto); set pad_token; GRPOTrainer.train(); return log_history |

---

### L-4-4: Log History Extraction and Validation

**API Signature:**
```python
def extract_frac_zero_std(log_history: list[dict]) -> list[float]:
    """
    Extract frac_reward_zero_std values from TRL log_history.
    Args:
        log_history: trainer.state.log_history (list of dicts per logging step)
    Returns:
        list of float, one per training step (len should == max_steps)
    Raises:
        ValueError if frac_reward_zero_std not found in any log entry
    """
```

**Pseudo-code:**
```python
def extract_frac_zero_std(log_history):
    values = [
        entry["frac_reward_zero_std"]
        for entry in log_history
        if "frac_reward_zero_std" in entry
    ]

    if not values:
        raise ValueError(
            "frac_reward_zero_std not found in log_history. "
            "Check TRL version >= 0.15.0. "
            f"Available keys in first entry: {list(log_history[0].keys()) if log_history else []}"
        )

    if len(values) < 50:
        print(f"WARNING: Expected 50 steps, got {len(values)} frac_zero_std entries")

    return values
```

**Subtask:**

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-4 | log_history_extractor | Filter log_history for frac_reward_zero_std; raise ValueError if missing; warn if <50 entries |

---

## A-5: Analysis & Gate [Complexity: 9, Budget: No subtask — integrated into analyze.py]

### API Signatures (Low Complexity — No Subtask Budget Used)

```python
def compute_gate_metrics(
    frac_var: list[float],          # frac_reward_zero_std per step, condition A (variance-50)
    frac_rnd: list[float],          # frac_reward_zero_std per step, condition B (random-50)
    checkpoints: list[int] = None,  # default [10, 20, 50]
) -> dict:
    """
    Compute mean frac_zero_std at each checkpoint, gate booleans, secondary gap.
    Returns gate_metrics dict matching gate_results.json schema.
    """
    # checkpoints default: [10, 20, 50]
    # mean_frac_N = mean(values[0:N])  — 0-indexed, steps 1..N
    # gate_N = mean_frac_N_var < mean_frac_N_rnd
    # gap_at_10_pp = mean_frac_10_rnd - mean_frac_10_var
    # gate_passed = all(gate_10, gate_20, gate_50)

def save_results(cfg, gate_metrics, frac_var, frac_rnd, var_ids, rnd_ids) -> None:
    """Write gate_results.json to cfg.results_dir per FR-11 schema."""
```

---

## A-6: Visualization [Complexity: 8, Budget: No subtask — direct implementation]

### API Signatures

```python
def plot_gate_bar_chart(gate_metrics: dict, figures_dir: str) -> None:
    """Fig 1: Grouped bar chart of mean_frac_zero_std at checkpoints 10, 20, 50."""
    # x-axis: checkpoints [10, 20, 50]
    # two bars per checkpoint: variance-50, random-50
    # annotate gate pass/fail per checkpoint

def plot_learning_curves(frac_var: list[float], frac_rnd: list[float], figures_dir: str) -> None:
    """Fig 2: Line plot frac_reward_zero_std per step 1-50 for both conditions."""

def plot_gap_trajectory(frac_var: list[float], frac_rnd: list[float], figures_dir: str) -> None:
    """Fig 3: gap = frac_rnd - frac_var per step; hlines at 0.0 and 0.05."""

def plot_reward_std_histogram(log_var: list[dict], log_rnd: list[dict], figures_dir: str) -> None:
    """Fig 4: group reward std histogram at steps 10, 20, 50.
    Note: TRL may log reward_std (mean) but not raw per-group std.
    Fallback: use reward_std scalar from log_history if raw not available.
    """

def generate_all_figures(cfg, gate_metrics, frac_var, frac_rnd, log_var, log_rnd) -> None:
    """Call all 4 plot functions. Uses matplotlib Agg backend."""
    # matplotlib.use("Agg") — set before pyplot import (headless, matches H-M1 pattern)
```

### Tensor Shape Notes

| Stage | Shape | Notes |
|-------|-------|-------|
| Input tokens | `(1, seq_len)` | per_device_train_batch_size=1 |
| Completions | `(4, max_new_tokens)` | num_generations=4 per problem |
| Rewards | `(1, 4)` | binary 0.0/1.0 per completion |
| Reward std per group | `scalar` | std of 4 rewards → 0 or 0.5 |
| frac_reward_zero_std | `scalar` | fraction of groups with std==0 per step |

### Critical Implementation Notes

1. `matplotlib.use("Agg")` before any pyplot import — headless server (H-M1 pattern)
2. JSON key `"top50_ids"` not `"top_ids"` — verified from H-E1 actual code
3. TRL passes dataset columns as kwargs to reward_funcs — `test_list` must be a dataset column
4. `per_device_train_batch_size=1` required — generation_batch_size=4 handles the G=4 completions
5. `beta=0.0` critical — avoids spurious KL gradients on zero-std groups (TRL issue #5588)
6. `pad_token = eos_token` — DeepSeek-Coder tokenizer has no pad_token by default
