# Logic: H-E1 (EXISTENCE PoC)

**Applied**: Standard PyTorch REINFORCE (KB search low-relevance; HF Trainer + evalplus conventions used per architecture doc)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-4: RL training (RLCodeTrainer) [Complexity: 14, Budget: 3 subtasks]

**Applied**: Standard PyTorch (REINFORCE, no baseline — PoC minimal)

### API Signatures

```python
class RLCodeTrainer:
    def __init__(self, model: PeftModel, tokenizer: PreTrainedTokenizer, cfg: Config):
        """Holds model, tokenizer, AdamW optimizer for RL phase."""
        ...

    def compute_reward(self, code: str, tests: list[str]) -> tuple[float, str]:
        """Executes code against tests. Returns (pass_rate in [0,1], error_msg or '')."""
        ...

    def rl_step(self, prompt: str, tests: list[str]) -> float:
        """One REINFORCE update: sample, score, backprop. Returns reward (float)."""
        ...


def train_rl(model: PeftModel, tokenizer: PreTrainedTokenizer, dataset: list[dict], cfg: Config) -> PeftModel:
    """Runs cfg.rl_epochs over dataset via RLCodeTrainer.rl_step. Returns updated model."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, T_prompt] | single-sample sampling (batch_size=1 for RL) |
| generated_ids | [1, T_gen] | sampled with `do_sample=True` |
| log_probs | [T_gen] | per-token log-prob of sampled sequence |
| reward | scalar (float) | pass_rate from `compute_reward` |
| loss | scalar | `-(reward) * log_probs.sum()` |

### Pseudo-code (REINFORCE step)

```
1. tokenize prompt -> input_ids [1, T_prompt]
2. sample: outputs = model.generate(input_ids, do_sample=True, return_dict_in_generate=True, output_scores=True)
3. decode generated_ids -> code string
4. reward, err_msg = compute_reward(code, tests)   # run tests in subprocess, pass_rate = passed/total
5. log_probs = recompute via forward pass on (input_ids + generated_ids), gather token logprobs [T_gen]
6. loss = -reward * log_probs.sum()
7. loss.backward(); optimizer.step(); optimizer.zero_grad()
8. print(f"RL reward: {reward:.2f}")
9. return reward
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A4-1 | `compute_reward` | Subprocess exec of generated code vs `tests`, pass_rate + captured stderr as feedback |
| L-A4-2 | `rl_step` | Sample -> reward -> recompute logprobs -> REINFORCE loss -> optimizer step |
| L-A4-3 | `train_rl` | Loop dataset x `cfg.rl_epochs`, call `rl_step` per example, log reward, return model |

---

## A-5: Self-refine inference [Complexity: 10, Budget: within A-4's shared 3-subtask pool — no separate budget]

**Applied**: Standard PyTorch (greedy decode + iterative feedback loop)

### API Signatures

```python
def execute_and_get_feedback(code: str, tests: list[str]) -> tuple[float, str]:
    """Same exec semantics as compute_reward. Returns (pass_rate, error_msg)."""
    ...

def single_shot(model: PreTrainedModel, tokenizer: PreTrainedTokenizer, prompt: str) -> str:
    """Greedy (temperature=0) generation. Returns code string."""
    ...

def self_refine(model: PreTrainedModel, tokenizer: PreTrainedTokenizer, prompt: str, tests: list[str], k: int = 3) -> str:
    """Up to k refine iterations using execution feedback. Returns final code string."""
    ...
```

### Pseudo-code (self_refine)

```
1. code = single_shot(model, tokenizer, prompt)
2. for i in range(k):
3.     pass_rate, err_msg = execute_and_get_feedback(code, tests)
4.     if pass_rate == 1.0: return code
5.     refine_prompt = f"{prompt}\n# Previous attempt:\n{code}\n# Error:\n{err_msg}\n# Fixed code:"
6.     code = single_shot(model, tokenizer, refine_prompt)
7. return code
```

Note: `single_shot` uses `model.generate(input_ids, do_sample=False)` — greedy, no shape table needed (standard `[1, T] -> [1, T']` decode).

---

## External Dependencies

None — green-field, no base hypothesis code to call.
