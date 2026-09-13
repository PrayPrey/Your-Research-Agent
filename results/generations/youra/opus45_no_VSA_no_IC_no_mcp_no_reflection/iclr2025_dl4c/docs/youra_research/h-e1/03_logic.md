# Logic: H-E1 (EXISTENCE / PoC)

**Scope**: A-2 (Reward engine), A-3 (Model + PPO wiring), A-4 (Training loop). Budget: 7 subtasks.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, Serena skipped (no existing code)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

## KB Research (Archon)

Applied: TRL PPOTrainer custom-reward-function pattern
Applied: Dense/graded verifiable reward mapping pattern (categorical + continuous blend)

---

## A-2: Reward Engine [Complexity: 14, Budget: 3+2+5+4]

**Applied**: Sandboxed subprocess execution + graded reward pattern

### API Signatures

```python
# reward.py
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class TestResult:
    passed: bool
    error_type: str  # "passed" | "assertion_error" | "runtime_error" | "syntax_error"
    expected: Optional[Any]
    actual: Optional[Any]

def execute_tests(code: str, test_cases: list[str], timeout: float = 5.0) -> list[TestResult]:
    """Runs code+each test_case in isolated subprocess. Returns one TestResult per test case."""
    ...

def compute_reward(code: str, test_cases: list[str], condition: str) -> float:
    """condition in {'binary','categorical','high_bandwidth'}. Returns scalar in [0,1]."""
    ...
```

### Internal Helpers (not exported, used by compute_reward)

```python
def _classify_error(exc: BaseException) -> str:
    """Maps exception -> 'syntax_error'|'runtime_error'|'assertion_error'."""
    ...

def _pass_ratio(results: list[TestResult]) -> float:
    """len(passed)/len(results)."""
    ...

def _partial_credit(results: list[TestResult]) -> float:
    """Numeric closeness score in [0,1] via 1/(1+abs(expected-actual)) averaged over
    failed-but-numeric results; 0.0 if non-numeric or no expected/actual."""
    ...
```

### Pseudo-code (reward computation — non-trivial branching)

```
compute_reward(code, test_cases, condition):
    results = execute_tests(code, test_cases)
    if condition == "binary":
        return 1.0 if all(r.passed for r in results) else 0.0

    if condition == "categorical":
        # worst-case error across test cases determines score
        if all(r.passed): return 1.0
        if any(r.error_type == "assertion_error"): return 0.5
        if any(r.error_type == "runtime_error"): return 0.25
        return 0.0  # syntax_error dominates

    if condition == "high_bandwidth":
        cat_score = compute_reward(code, test_cases, "categorical")  # reuse above
        ratio = _pass_ratio(results)
        partial = _partial_credit(results)
        return 0.5 * cat_score + 0.3 * ratio + 0.2 * partial
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | Sandbox executor | `execute_tests`: subprocess isolation, timeout=5s, capture stdout/exc, expected/actual extraction from AssertionError args |
| L-A2-2 | Error classification | `_classify_error`: map SyntaxError/exec-time exc/AssertionError to error_type string |
| L-A2-3 | Reward modes | `compute_reward` binary/categorical/high_bandwidth branches + `_pass_ratio`/`_partial_credit` helpers |

---

## A-3: Model + PPO Wiring [Complexity: 9, Budget: 2+3+2+2]

**Applied**: TRL PPOTrainer custom-reward-function pattern

### API Signatures

```python
# model.py
from transformers import AutoTokenizer
from trl import AutoModelForCausalLMWithValueHead, PPOTrainer, PPOConfig
from datasets import Dataset

def load_model_and_tokenizer(
    cfg: ExperimentConfig,
) -> tuple[AutoModelForCausalLMWithValueHead, AutoTokenizer]:
    """Loads CodeLlama-7B-Instruct in bfloat16 with value head. Sets pad_token=eos_token."""
    ...

def build_ppo_trainer(
    cfg: ExperimentConfig,
    model: AutoModelForCausalLMWithValueHead,
    tokenizer: AutoTokenizer,
    dataset: Dataset,
) -> PPOTrainer:
    """Wraps model/tokenizer/dataset into PPOTrainer using cfg fields
    (learning_rate, batch_size, ppo_epochs, init_kl_coef)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids (prompt) | [B, L_prompt] | tokenized MBPP prompt, B=cfg.batch_size |
| response_ids | [B, L_resp] | generated code tokens, variable length per sample |
| rewards | list[Tensor([1])] | one scalar tensor per sample, from `compute_reward` |
| value | [B, L_prompt+L_resp] | value head output per token |
| logprobs | [B, L_resp] | policy logprob per generated token |

### Pseudo-code (PPOConfig construction)

```
build_ppo_trainer(cfg, model, tokenizer, dataset):
    ppo_config = PPOConfig(
        learning_rate=cfg.learning_rate,
        batch_size=cfg.batch_size,
        ppo_epochs=cfg.ppo_epochs,
        init_kl_coef=cfg.init_kl_coef,
    )
    return PPOTrainer(config=ppo_config, model=model, tokenizer=tokenizer, dataset=dataset)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A3-1 | Model loading | `load_model_and_tokenizer`: from_pretrained bfloat16, value-head wrap, tokenizer pad token setup |
| L-A3-2 | PPOTrainer wiring | `build_ppo_trainer`: PPOConfig from cfg fields, instantiate PPOTrainer |

---

## A-4: Training Loop [Complexity: 12, Budget: 3+3+3+3]

**Applied**: PPO generate -> score -> step loop pattern (TRL RLHF recipe)

### API Signatures

```python
# train.py
def run_condition(condition: str, seed: int, cfg: ExperimentConfig) -> dict:
    """Trains one (condition, seed) run for cfg.train_epochs over MBPP train set.
    Saves checkpoint to checkpoints/{condition}_{seed}/.
    Returns: {'condition', 'seed', 'metric_log': list[tuple[int,float]],  # (n_samples, pass@1)
              'rewards': list[float], 'kl': list[float], 'loss': list[float]}"""
    ...

def main() -> None:
    """for condition in REWARD_CONDITIONS: for seed in SEEDS: run_condition(condition, seed, cfg)"""
    ...
```

### Pseudo-code (PPO step loop, non-trivial)

```
run_condition(condition, seed, cfg):
    set_seed(seed)
    dataset = load_mbpp_train()
    model, tokenizer = load_model_and_tokenizer(cfg)
    ppo_trainer = build_ppo_trainer(cfg, model, tokenizer, dataset)
    metric_log = []
    n_samples = 0

    for epoch in range(cfg.train_epochs):
        for batch in ppo_trainer.dataloader:
            prompt_ids = [tokenizer(p, return_tensors="pt").input_ids[0] for p in batch["prompt"]]
            response_ids = ppo_trainer.generate(prompt_ids, max_new_tokens=256)  # [B, L_resp]
            responses = tokenizer.batch_decode(response_ids, skip_special_tokens=True)

            rewards = [
                torch.tensor(compute_reward(code, tc, condition))
                for code, tc in zip(responses, batch["test_list"])
            ]  # list of scalar tensors, len B

            stats = ppo_trainer.step(prompt_ids, response_ids, rewards)
            n_samples += cfg.batch_size

            if n_samples % EVAL_INTERVAL == 0:
                p1 = evaluate_pass_at_1(model, tokenizer, load_mbpp_val_subset())
                metric_log.append((n_samples, p1))

    save_checkpoint(model, f"checkpoints/{condition}_{seed}/")
    return {"condition": condition, "seed": seed, "metric_log": metric_log, ...}
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| prompt_ids | list[Tensor([L_i])] | ragged, per-sample token ids |
| response_ids | list[Tensor([L_resp_i])] | ragged, PPOTrainer.generate output |
| rewards | list[Tensor([])] | 0-d scalar tensor per sample |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A4-1 | run_condition core loop | seed set, dataset/model/trainer init, generate->reward->step loop, checkpoint save |
| L-A4-2 | Metric logging + main | periodic pass@1 eval into metric_log, `main()` condition x seed sweep |

---

## Total Subtasks: 7/7 used (A-2: 3, A-3: 2, A-4: 2)
