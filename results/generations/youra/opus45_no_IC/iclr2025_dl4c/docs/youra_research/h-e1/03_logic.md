# Logic: H-E1 (EXISTENCE / PoC)

**Hypothesis:** FGO token masking improves code generation vs Standard PPO across 3 feedback types.
**Budget:** 0 subtasks (LIGHT tier).

Applied: No relevant KB pattern (search returned generic PyTorch docs, not FGO-specific) — signatures derived from PRD/brief StepCoder pseudo-code + TRL PPOTrainer conventions.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project — new API design, no existing code to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None — new implementation

---

## A-1: Data Pipeline [Complexity: 6]

```python
def load_humaneval() -> list[dict]:
    """164 problems. Each: {task_id, prompt, test, entry_point}."""

def load_mbpp() -> list[dict]:
    """500 problems (idx 11-510). Each: {task_id, text, code, test_list}."""

def format_prompt(problem: dict) -> str:
    """Instruction-format prompt for CodeLlama-Instruct."""
```

## A-2: Execution Sandbox + Reward [Complexity: 9]

```python
def check_compiles(code: str) -> bool:
    """compile(code, '<string>', 'exec') succeeds -> True."""

def compute_reward(code: str, test_cases: list[str], feedback_type: str) -> float:
    """
    feedback_type in {"compile", "test", "combined"}.
    compile:  +1.0 compiles else -1.0
    test:     +1.0 pass all / -0.3 fail / -0.6 runtime err / -1.0 compile err
    combined: check_compiles() first (-1.0 if fails), then test-branch reward
    """
```

Pseudo-code (reward branches, StepCoder Eq.3):
```
if feedback_type == "compile":
    return 1.0 if check_compiles(code) else -1.0
# feedback_type in {"test", "combined"}
if not check_compiles(code): return -1.0
try:
    exec(code + tests, sandbox_globals)      # sandboxed namespace, timeout-guarded
    return 1.0
except AssertionError:
    return -0.3
except Exception:
    return -0.6
```

## A-3: Trace Collection + Token-Line Mapping [Complexity: 8]

```python
def collect_execution_trace(code: str, test_cases: list[str]) -> set[int]:
    """sys.settrace line-event collector. Returns executed line numbers (1-indexed)."""

def map_tokens_to_lines(token_ids: Tensor, code: str, tokenizer) -> list[int]:
    """token_ids: [seq_len] -> list[int] len seq_len, line number per token (via offset decode)."""
```

Pseudo-code:
```
# collect_execution_trace
executed = set()
def trace_func(frame, event, arg):
    if event == "line": executed.add(frame.f_lineno)
    return trace_func
sys.settrace(trace_func)
try: exec(code + "\n" + "\n".join(test_cases), {})
except Exception: pass
finally: sys.settrace(None)
return executed

# map_tokens_to_lines
decoded = tokenizer.decode(token_ids, skip_special_tokens=False)
offsets = tokenizer(code, return_offsets_mapping=True)["offset_mapping"]  # [(start,end), ...]
line_starts = [i for i, c in enumerate(code) if i == 0 or code[i-1] == "\n"]  # cumulative char->line
token_to_line = [bisect_right(line_starts, start) for (start, end) in offsets]  # 1-indexed
return token_to_line
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| token_ids | [seq_len] | single sequence, int64 |
| token_to_line | list[int], len seq_len | line number per token position |
| executed_lines | set[int] | unordered |

## A-4: FGO Mask + Masked PPO Loss [Complexity: 10]

```python
def create_fgo_mask(token_ids: Tensor, token_to_line: list[int], executed_lines: set[int]) -> Tensor:
    """token_ids: [seq_len] -> mask: [seq_len] float, 1.0=executed, 0.0=unexecuted."""

def fgo_ppo_loss(logprobs: Tensor, old_logprobs: Tensor, advantages: Tensor,
                  mask: Tensor, clip_eps: float = 0.2) -> Tensor:
    """All args [B, seq_len] except returns scalar. Masked mean over executed tokens only."""

def standard_ppo_loss(logprobs: Tensor, old_logprobs: Tensor, advantages: Tensor,
                       clip_eps: float = 0.2) -> Tensor:
    """Same as fgo_ppo_loss with mask=ones_like(logprobs). Scalar."""

def verify_fgo_mechanism(mask: Tensor, logprobs: Tensor) -> None:
    """Asserts mask.sum() < mask.numel(); logs '[FGO] Masking {N} of {M} tokens ({P}% unexecuted)'."""
```

Pseudo-code (StepCoder Algorithm 1 / Eq. masked PPO):
```
# create_fgo_mask
mask = torch.zeros_like(token_ids, dtype=torch.float)   # [seq_len]
for i, line_num in enumerate(token_to_line):
    if line_num in executed_lines: mask[i] = 1.0
return mask

# fgo_ppo_loss / standard_ppo_loss (shared core, mask differs)
ratio = torch.exp(logprobs - old_logprobs)               # [B, seq_len]
clipped = torch.clamp(ratio, 1 - clip_eps, 1 + clip_eps) # [B, seq_len]
per_token_loss = -torch.min(ratio * advantages, clipped * advantages)  # [B, seq_len]
masked_loss = per_token_loss * mask                       # [B, seq_len]
return masked_loss.sum() / (mask.sum() + 1e-8)            # scalar
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logprobs, old_logprobs, advantages, mask | [B, seq_len] | B=per_device_batch (16) |
| loss | scalar | masked mean |

## A-5: Model + PPOTrainer Wrapper [Complexity: 9]

```python
def load_policy_model(model_id: str = "meta-llama/CodeLlama-7b-Instruct-hf") -> tuple[nn.Module, "PreTrainedTokenizer"]:
    """fp16, device_map='auto'. Returns (model, tokenizer)."""

def build_ppo_trainer(model, tokenizer, use_fgo: bool) -> "PPOTrainer":
    """trl.PPOTrainer; use_fgo selects fgo_ppo_loss vs standard_ppo_loss in training step override."""
```

## A-6: Training Loop (Single Condition) [Complexity: 9]

```python
def train_condition(condition: str, feedback_type: str, use_fgo: bool,
                     problems: list[dict], cfg: "Config") -> dict:
    """Runs cfg.episodes PPO steps. Checkpoints every 1000 episodes. Returns {ckpt_path, log_path, metrics}."""
```

Pseudo-code (per-episode loop):
```
model, tokenizer = load_policy_model(cfg.model_id)
trainer = build_ppo_trainer(model, tokenizer, use_fgo)
for episode in range(cfg.episodes):
    batch = sample(problems, cfg.per_device_batch)
    prompts = [format_prompt(p) for p in batch]
    query_ids = tokenizer(prompts, return_tensors="pt").input_ids        # [B, prompt_len]
    response_ids = trainer.generate(query_ids)                           # [B, resp_len]
    codes = [tokenizer.decode(r) for r in response_ids]

    rewards = [compute_reward(c, p["test"], feedback_type) for c, p in zip(codes, batch)]  # [B]

    if use_fgo:
        masks = []
        for code, r_ids, p in zip(codes, response_ids, batch):
            executed = collect_execution_trace(code, p["test"])
            t2l = map_tokens_to_lines(r_ids, code, tokenizer)
            masks.append(create_fgo_mask(r_ids, t2l, executed))
        mask_batch = torch.stack(masks)                                  # [B, resp_len]
        stats = trainer.step(query_ids, response_ids, rewards, loss_fn=fgo_ppo_loss, mask=mask_batch)
    else:
        stats = trainer.step(query_ids, response_ids, rewards, loss_fn=standard_ppo_loss)

    if episode % 1000 == 0: save_checkpoint(model, cfg, episode)
return {"ckpt_path": ..., "log_path": ..., "metrics": stats}
```

## A-7: 2x3 Factorial Runner [Complexity: 7]

```python
def run_factorial_experiment(cfg: "Config") -> dict:
    """Loops FR-7.1-7.6 (use_fgo x feedback_type), calls train_condition + evaluate_condition. Returns {condition: {train, eval}}."""
```

Pseudo-code:
```
conditions = [(fgo, ft) for fgo in (False, True) for ft in ("compile", "test", "combined")]
results = {}
for use_fgo, feedback_type in conditions:
    name = f"{'fgo' if use_fgo else 'standard'}_{feedback_type}"
    train_out = train_condition(name, feedback_type, use_fgo, problems, cfg)
    eval_out = {
        "humaneval": evaluate_condition(train_out["ckpt_path"], "humaneval"),
        "mbpp": evaluate_condition(train_out["ckpt_path"], "mbpp"),
    }
    results[name] = {"train": train_out, "eval": eval_out}
return results
```

## A-8: Evaluation + Visualization [Complexity: 7]

```python
def generate_samples(model, tokenizer, problems: list[dict], n: int = 10) -> list[dict]:
    """n generations/problem. Returns [{task_id, completions: [str]*n}]."""

def pass_at_k(samples: list[dict], k: int) -> float:
    """Unbiased pass@k estimator (HumanEval formula) over samples."""

def evaluate_condition(model_path: str, dataset: str) -> dict:
    """dataset in {'humaneval','mbpp'}. Returns {'pass@1': float, 'pass@10': float}."""

def plot_gate_metrics(results: dict) -> None:
    """2x3 bar chart (Standard/FGO x compile/test/combined) -> figures/gate_metrics.png."""

def plot_training_curves(logs: dict) -> None:
    """pass@1 vs episode, 6 lines -> figures/training_curves.png."""

def plot_masking_stats(logs: dict) -> None:
    """% tokens masked per epoch (FGO conditions only) -> figures/masking_stats.png."""
```

---

## Data Flow

```
data.py (problems)
  -> train.py: format_prompt -> model.py generate -> execution.py compute_reward
  -> [use_fgo] execution.py collect_execution_trace + map_tokens_to_lines -> fgo.py create_fgo_mask
  -> fgo.py fgo_ppo_loss / standard_ppo_loss -> PPOTrainer.step -> checkpoint
train.py run_factorial_experiment loops 6x above
  -> evaluate.py generate_samples + pass_at_k -> results dict
  -> visualize.py plot_gate_metrics / plot_training_curves / plot_masking_stats -> figures/
```

No subtasks allocated (0 budget, LIGHT tier).
