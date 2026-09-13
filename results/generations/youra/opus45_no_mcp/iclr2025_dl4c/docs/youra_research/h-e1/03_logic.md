# Logic Specification: h-e1 (Error-Type Gating)

**Type:** EXISTENCE (PoC) — minimal logic only
**Model:** CodeT5-large (770M, encoder-decoder)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - designing new APIs, no existing codebase to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## A-1: Error Classifier [Complexity: Low, Budget: 2]

**Applied:** Standard PyTorch / regex traceback parsing

### API Signatures

```python
U_LINE_ERRORS = {'SyntaxError', 'IndentationError', 'NameError',
                  'TypeError', 'AttributeError', 'KeyError', 'IndexError'}
U_IGNORE_ERRORS = {'RuntimeError', 'RecursionError', 'MemoryError',
                    'TimeoutError', 'AssertionError'}

def classify_error(traceback_str: Optional[str]) -> str:
    """Classify exception type. Returns 'U_line' or 'U_ignore'."""
    ...

def parse_traceback_line(traceback_str: str) -> Optional[int]:
    """Extract failing source line number from traceback. None if unparseable."""
    ...
```

### Pseudo-code

```
1. if traceback_str is None: return None  # (caller handles pass case)
2. for err in U_LINE_ERRORS: if err in traceback_str: return 'U_line'
3. return 'U_ignore'  # default (covers U_IGNORE_ERRORS + unknowns)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | classify_error | String match exception name against category sets |
| L-1-2 | parse_traceback_line | Regex `File ".*", line (\d+)` on last traceback frame |

---

## A-2: Gated Reward Calculator [Complexity: Medium, Budget: 3]

**Applied:** RLTF multi-granularity reward (Liu et al. 2023, Eq. 4-5) + gating extension

### API Signatures

```python
@dataclass
class Token:
    text: str
    line: int

def compute_gated_reward(
    code_tokens: List[Token],     # len = gen_len (<=256)
    traceback: Optional[str],     # None if execution passed
    gating: str = "fine_gated",   # 'fine_always' | 'fine_gated'
) -> Tensor:                      # [gen_len] float32
    """Per-token reward. Logs 'GATING: ...' when gate activates."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| code_tokens | list, len=gen_len | gen_len <= 256 |
| rewards | [gen_len] | float32, values in {1.0, -0.1, -1.0} |

### Pseudo-code

```
1. if traceback is None: return ones(gen_len)                  # coarse pass reward
2. category = classify_error(traceback)
3. error_line = parse_traceback_line(traceback)
4. if gating == 'fine_gated' and category == 'U_ignore':
       log("GATING: U_ignore error detected, applying coarse-only penalty")
       return full(gen_len, -0.1)
5. else:
       rewards = full(gen_len, -0.1)
       rewards[token.line == error_line] = -1.0
       return rewards
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | compute_gated_reward | Core gating branch logic above |
| L-2-2 | activation_logging | Increment counter + log line on U_ignore gate hit |
| L-2-3 | batch_wrapper | Vectorize over batch: `compute_batch_rewards(List[List[Token]], List[Optional[str]], gating) -> Tensor[B, gen_len]` |

---

## A-3: PPO Trainer [Complexity: High, Budget: 4]

**Applied:** Standard PPO clipped objective (HuggingFace TRL-style actor-critic)

### API Signatures

```python
class PPOPolicy(nn.Module):
    def __init__(self, base_model: T5ForConditionalGeneration):
        ...

    def forward(
        self,
        input_ids: Tensor,          # [B, 512]
        decoder_input_ids: Tensor,  # [B, gen_len]
    ) -> Tensor:                    # logits [B, gen_len, 32100]
        ...

    def generate(self, input_ids: Tensor, max_new_tokens: int = 256) -> Tensor:
        """Sample rollout. Returns token ids [B, gen_len]."""
        ...

class ValueHead(nn.Module):
    def forward(self, hidden_states: Tensor) -> Tensor:
        # hidden_states: [B, gen_len, 1024] -> value: [B, gen_len]
        ...

def compute_advantages(
    rewards: Tensor,   # [B, gen_len]
    values: Tensor,    # [B, gen_len]
    gamma: float = 1.0,
    lam: float = 0.95,
) -> Tuple[Tensor, Tensor]:  # (advantages [B, gen_len], returns [B, gen_len])
    ...

def ppo_step(
    policy: PPOPolicy,
    value_head: ValueHead,
    optimizer: torch.optim.AdamW,
    batch: Dict[str, Tensor],
    gating: str,
    clip_eps: float = 0.2,
    entropy_coef: float = 0.01,
) -> Dict[str, float]:  # {'policy_loss', 'value_loss', 'reward_mean'}
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, 512] | B=8, encoder input |
| gen_ids | [B, 256] | sampled generation |
| logits | [B, 256, 32100] | vocab=32100 (CodeT5 tokenizer) |
| rewards | [B, 256] | from A-2 batch_wrapper |
| advantages, returns | [B, 256] | GAE output |

### Pseudo-code

```
1. gen_ids, gen_logits = policy.generate(input_ids)
2. code_str = tokenizer.decode(gen_ids)
3. traceback = execute_and_get_traceback(code_str, test_cases)  # sandbox
4. rewards = compute_batch_rewards(tokens_with_lines(gen_ids), traceback, gating)  # [B, gen_len]
5. values = value_head(policy.encode(gen_ids))                                    # [B, gen_len]
6. advantages, returns = compute_advantages(rewards, values)
7. ratio = exp(new_logprobs - old_logprobs)
8. policy_loss = -min(ratio * advantages, clip(ratio, 1-eps, 1+eps) * advantages).mean()
9. value_loss = mse(values, returns)
10. loss = policy_loss + 0.5*value_loss - entropy_coef*entropy
11. loss.backward(); optimizer.step()
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | PPOPolicy | Wraps T5ForConditionalGeneration, forward + generate |
| L-3-2 | ValueHead | Linear(1024, 1) on decoder hidden states |
| L-3-3 | compute_advantages | GAE(gamma=1.0, lambda=0.95) |
| L-3-4 | ppo_step | Full clipped-objective update using A-2 rewards |

---

## A-4: Evaluation Module [Complexity: Low, Budget: 2]

**Applied:** Standard PyTorch inference + subprocess sandbox

### API Signatures

```python
def execute_code_safely(
    code: str,
    test_cases: List[Dict[str, str]],
    timeout_s: int = 30,
    mem_limit_mb: int = 512,
) -> Tuple[str, Optional[str]]:
    """Run code in sandboxed subprocess. Returns (result, traceback)."""
    # result: 'PASS' | 'FAIL' | 'ERROR'
    ...

def compute_pass_at_1(
    policy: PPOPolicy,
    test_problems: List[Dict],
    tokenizer: AutoTokenizer,
) -> float:
    """Greedy-decode each problem, execute, return pass rate."""
    ...

def log_checkpoint_metrics(step: int, pass_at_1: float, gating_rate: float, out_dir: str) -> None:
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | execute_code_safely | subprocess.run with timeout + resource.setrlimit for mem |
| L-4-2 | compute_pass_at_1 | Loop over test_problems, greedy generate, execute, aggregate |

---

## Visualization Hooks [Complexity: Low, Budget: 1]

```python
def plot_training_curves(history: Dict[str, List[Tuple[int, float]]], out_path: str) -> None: ...
def plot_error_distribution(u_line_count: int, u_ignore_count: int, out_path: str) -> None: ...
def plot_gate_metrics(steps_fine_always: int, steps_fine_gated: int, out_path: str) -> None: ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | figure_generation | matplotlib bar/pie/line plots saved to `h-e1/figures/` |
