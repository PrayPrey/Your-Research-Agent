# Logic: H-M2 (FGO Token Masking Gradient Exclusion)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: API signatures verified from actual H-M1 code (NOT from brief's pseudo-signatures, which differ)
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**: `fgo.py::fgo_ppo_loss`, `fgo.py::create_fgo_mask`, `fgo.py::standard_ppo_loss`, `execution.py::collect_execution_trace`, `execution.py::map_tokens_to_lines`, `model.py::load_policy_model/build_ppo_config/build_ppo_trainer`, `evaluate.py::pass_at_k`, `train.py::train_condition`

**Critical divergence found**: Brief specifies `compute_fgo_masked_loss(logits, labels, execution_mask, advantages, old_log_probs, clip_epsilon)` operating on raw `logits`. Actual H-M1 code already implements this as `fgo_ppo_loss(logprobs, old_logprobs, advantages, mask, clip_eps)` taking **pre-computed logprobs**, not logits+labels. H-M2 reuses `fgo_ppo_loss` as-is — do not reimplement the brief's variant.

---

## External Dependencies (Base Hypothesis)

```python
# From: docs/youra_research/h-m1/code/fgo.py (ACTUAL CODE)
def create_fgo_mask(token_ids: torch.Tensor, token_to_line: List[int], executed_lines: Set[int]) -> torch.Tensor:
    """mask: [seq_len] binary float, 1=executed."""

def fgo_ppo_loss(logprobs: Tensor, old_logprobs: Tensor, advantages: Tensor, mask: Tensor, clip_eps: float = 0.2) -> Tensor:
    """All [B, seq_len]. Returns scalar. mask=1 (all ones) reduces to standard PPO."""

def standard_ppo_loss(logprobs: Tensor, old_logprobs: Tensor, advantages: Tensor, clip_eps: float = 0.2) -> Tensor:
    """Baseline: calls fgo_ppo_loss with mask=torch.ones_like(logprobs)."""

def verify_fgo_mechanism(mask: Tensor, logprobs: Tensor) -> None:
    """Asserts executed < total; prints masked ratio. No gradient check — H-M2 extends this."""

# From: docs/youra_research/h-m1/code/execution.py
def collect_execution_trace(code: str, test_cases: List[str]) -> Set[int]:
    """sys.settrace-based line collector, 5s timeout via SIGALRM."""

def map_tokens_to_lines(token_ids, code: str, tokenizer) -> List[int]:
    """Per-token line number via offset_mapping + bisect_right."""

# From: docs/youra_research/h-m1/code/model.py
def load_policy_model(model_id: str, torch_dtype: str) -> Tuple[AutoModelForCausalLMWithValueHead, AutoTokenizer]: ...
def build_ppo_config(lr, batch_size, mini_batch_size, gradient_accumulation_steps, seed, log_dir) -> PPOConfig: ...
def build_ppo_trainer(model, tokenizer, ppo_config) -> PPOTrainer: ...

# From: docs/youra_research/h-m1/code/evaluate.py
def pass_at_k(n: int, c: int, k: int) -> float: ...

# From: docs/youra_research/h-m1/code/config.py
class Config:
    model_id: str; lr: float; batch_size: int; per_device_batch: int
    grad_accum: int; seed: int; episodes: int; checkpoint_every: int
    torch_dtype: str; results_dir: str
```

**Verified from**: actual `docs/youra_research/h-m1/code/*.py` (not `h-m1/03_logic.md`, which used different naming for some helpers e.g. `ExecutionTraceCollector.collect_trace` vs actual `collect_execution_trace`).

---

## A-1: RandomMaskGenerator [Complexity: 4, Budget: 2+2]

**Applied**: Standard PyTorch — sample Bernoulli mask matching trace-based sparsity per sample

### API Signatures

```python
# gradmask/random_mask.py
import torch

def create_random_mask(seq_len: int, num_executed: int, device=None, generator: torch.Generator = None) -> torch.Tensor:
    """Random binary mask [seq_len] with exactly num_executed ones (sparsity-matched to trace mask)."""
    ...

def build_random_mask_like(fgo_mask: torch.Tensor, seed: int) -> torch.Tensor:
    """Given a trace-based fgo_mask [seq_len], return random mask with same #ones. Same shape/dtype."""
    ...
```

### Pseudo-code

```
build_random_mask_like(fgo_mask, seed):
    1. num_executed = int(fgo_mask.sum().item())
    2. seq_len = fgo_mask.numel()
    3. gen = torch.Generator(device=fgo_mask.device).manual_seed(seed)
    4. perm = torch.randperm(seq_len, generator=gen, device=fgo_mask.device)
    5. mask = torch.zeros_like(fgo_mask)
    6. mask[perm[:num_executed]] = 1.0
    7. return mask
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Random mask sampler | `torch.randperm`-based exact-sparsity mask |
| L-1-2 | Per-sample wrapper | Apply per batch row, preserve device/seed determinism |

---

## A-2: GradientExclusionVerifier [Complexity: 8, Budget: 3+3+2]

**Applied**: PyTorch autograd hooks on embedding layer + per-token gradient norm via `register_hook`

### API Signatures

```python
# gradmask/verify.py
import torch
import torch.nn as nn
from typing import Dict

class GradientExclusionVerifier:
    def __init__(self, model: nn.Module):
        """model: AutoModelForCausalLMWithValueHead (from H-M1 model.py)."""
        self.model = model
        self._captured_grad: torch.Tensor = None

    def _hook(self, grad: torch.Tensor) -> None:
        """register_hook callback on token embedding output. grad: [B, seq_len, hidden]."""
        self._captured_grad = grad.detach().clone()

    def verify(
        self,
        input_ids: torch.Tensor,     # [B, seq_len]
        logprobs: torch.Tensor,      # [B, seq_len] requires_grad=True (recomputed w/ grad enabled)
        old_logprobs: torch.Tensor,  # [B, seq_len]
        advantages: torch.Tensor,    # [B, seq_len]
        mask: torch.Tensor,          # [B, seq_len]
        clip_eps: float = 0.2,
    ) -> Dict[str, float]:
        """
        Returns: {
          "executed_grad_norm": float,       # mean L2 norm over masked==1 token positions, > 0 expected
          "non_executed_grad_norm": float,   # mean L2 norm over masked==0 positions, == 0 expected
          "gradient_exclusion_verified": bool,
        }
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, seq_len] | Token ids of generated response |
| embed_out | [B, seq_len, H] | Output of `model.get_input_embeddings()(input_ids)`, hook attached here |
| per_token_grad_norm | [B, seq_len] | `embed_out.grad.norm(dim=-1)` after backward |

### Pseudo-code

```
verify(input_ids, logprobs, old_logprobs, advantages, mask, clip_eps):
    1. embeds = self.model.get_input_embeddings()(input_ids)   # [B, S, H], leaf requires_grad
    2. embeds.retain_grad()
    3. loss = fgo_ppo_loss(logprobs, old_logprobs, advantages, mask, clip_eps)  # reuse H-M1 fgo.py
       # NOTE: logprobs must be recomputed from embeds through model forward pass
       # so autograd graph connects loss -> embeds. Caller responsible for wiring forward.
    4. self.model.zero_grad()
    5. loss.backward(retain_graph=False)
    6. per_token_grad_norm = embeds.grad.norm(dim=-1)          # [B, S]
    7. executed_norms = per_token_grad_norm[mask.bool()]
    8. non_executed_norms = per_token_grad_norm[~mask.bool()]
    9. exec_mean = executed_norms.mean().item() if executed_norms.numel() else 0.0
    10. non_exec_mean = non_executed_norms.mean().item() if non_executed_norms.numel() else 0.0
    11. verified = (non_exec_mean < 1e-6) and (exec_mean > 1e-6)
    12. return {"executed_grad_norm": exec_mean, "non_executed_grad_norm": non_exec_mean,
                 "gradient_exclusion_verified": verified}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Embedding-level grad capture | `retain_grad()` on embedding output, forward through model to reconnect logprobs |
| L-2-2 | Per-token norm split | `mask.bool()` boolean-index into `grad.norm(dim=-1)` |
| L-2-3 | Verification dict + assert helper | Threshold `1e-6` for zero/non-zero check, return bool |

---

## A-3: MaskedPPOTrainer (3-condition wrapper) [Complexity: 9, Budget: 3+3+3]

**Applied**: Reuse H-M1 `train_condition` loop structure; extend with mask-mode dispatch (none/random/trace)

### API Signatures

```python
# gradmask/train_masked.py
from typing import Dict, Any, List, Literal
from config import Config  # H-M1 config.py, reused as-is

MaskMode = Literal["none", "random", "trace"]

def train_masked_condition(
    condition_name: str,
    mask_mode: MaskMode,
    problems: List[Dict],
    cfg: Config,
    output_dir: str,
    seed: int,
) -> Dict[str, Any]:
    """
    Extends H-M1 train.py::train_condition. mask_mode:
      "none"   -> standard_ppo_loss (all tokens, from H-M1 fgo.py)
      "random" -> fgo_ppo_loss with build_random_mask_like() mask
      "trace"  -> fgo_ppo_loss with create_fgo_mask() from execution trace (H-M1 identical)
    Returns same dict shape as H-M1 train_condition + "grad_verification" key (list of per-episode dicts, first 5 episodes only).
    """
    ...

def run_three_condition_experiment(cfg: Config, seeds: List[int], output_dir: str = "outputs") -> Dict[str, Any]:
    """Runs {none, random, trace} x seeds, saves per-seed + aggregate results.json."""
    ...
```

### Pseudo-code

```
train_masked_condition(condition_name, mask_mode, problems, cfg, output_dir, seed):
    1. model, tokenizer = load_policy_model(cfg.model_id, cfg.torch_dtype)     # H-M1 model.py
    2. trainer = build_ppo_trainer(model, tokenizer, build_ppo_config(...))    # H-M1 model.py
    3. verifier = GradientExclusionVerifier(model)  # only if mask_mode != "none"
    4. for episode in range(cfg.episodes):
         batch = sample(problems, cfg.per_device_batch)
         generate responses via trainer (same as H-M1 train.py lines 71-89)
         for each (code, problem, response_ids):
             reward = compute_reward(code, test_cases, "combined")   # H-M1 execution.py
             if mask_mode == "none":
                 mask = torch.ones(len(response_ids))
             elif mask_mode == "trace":
                 executed = collect_execution_trace(code, test_cases)          # H-M1
                 token_to_line = map_tokens_to_lines(response_ids, code, tokenizer)  # H-M1
                 mask = create_fgo_mask(response_ids, token_to_line, executed)       # H-M1
             elif mask_mode == "random":
                 trace_mask = <same as "trace" branch, for sparsity match>
                 mask = build_random_mask_like(trace_mask, seed=seed + episode)
         ppo_step via trainer.step(...) — TRL PPOTrainer internally applies its own loss;
             custom fgo_ppo_loss/standard_ppo_loss substituted via trainer's loss_fn override
             (or manual optimizer step if TRL doesn't expose override — see Subtask L-3-2)
         if episode < 5 and mask_mode != "none":
             grad_report = verifier.verify(response_ids, logprobs, old_logprobs, advantages, mask)
             append to grad_verification log
    5. save checkpoint + results.json (mirror H-M1 train.py::train_condition output shape)

run_three_condition_experiment(cfg, seeds, output_dir):
    for seed in seeds:
        set_seed(seed)  # torch, random, numpy
        for mode in ["none", "random", "trace"]:
            train_masked_condition(f"{mode}_seed{seed}", mode, problems, cfg, output_dir, seed)
    aggregate into results.json keyed by mode -> list of per-seed dicts
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| response_ids | [seq_len] | Per-sample, ragged across batch (no padding in H-M1 loop) |
| mask | [seq_len] | Matches `create_fgo_mask` output convention (per-sample, not batched) |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Mask-mode dispatch | if/elif branch producing mask per mask_mode, reusing H-M1 fgo.py/execution.py fns |
| L-3-2 | Custom loss injection into TRL trainer.step | If TRL PPOTrainer doesn't accept custom per-token loss, fall back to manual forward/backward loop using `fgo_ppo_loss`/`standard_ppo_loss` directly (bypass `trainer.step`) |
| L-3-3 | Result aggregation across 3 modes x 3 seeds | JSON structure mirroring H-M1 `factorial_results.json` |

---

## A-4: Evaluation & Statistical Test [Complexity: 6, Budget: 2+2+2]

**Applied**: Reuse H-M1 `pass_at_k`; add scipy paired t-test

### API Signatures

```python
# gradmask/eval_stats.py
from typing import List, Dict
from scipy import stats
from evaluate import pass_at_k  # reused from H-M1

def evaluate_condition_pass1(model, tokenizer, dataset: List[Dict], num_samples: int = 1) -> float:
    """pass@1 over HumanEval+MBPP (664 problems). Uses pass_at_k(n=num_samples, c=<passed>, k=1) per problem, averaged."""
    ...

def paired_ttest_conditions(pass1_trace: List[float], pass1_random: List[float]) -> Dict[str, float]:
    """pass1_trace/random: length == len(seeds) (3). Returns {"t_stat":.., "p_value":.., "significant": p<0.05}."""
    ...
```

### Pseudo-code

```
paired_ttest_conditions(pass1_trace, pass1_random):
    1. t_stat, p_value = stats.ttest_rel(pass1_trace, pass1_random)
    2. return {"t_stat": float(t_stat), "p_value": float(p_value), "significant": p_value < 0.05}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Per-condition pass@1 loop | Generate + execute_tests per problem, reuse `pass_at_k` from H-M1 evaluate.py |
| L-4-2 | Paired t-test | `scipy.stats.ttest_rel` over 3-seed pass@1 vectors (trace vs random) |
| L-4-3 | Results JSON + gate check | Write `{condition: {seed: pass1}}`, apply MUST_WORK gate (trace>random, p<0.05; grad_exclusion_verified all True) |

---

## A-5: Visualization [Complexity: 3, Budget: 2+1]

**Applied**: matplotlib bar chart (H-M1 visualize.py pattern reused)

### API Signatures

```python
# gradmask/visualize_masking.py
def plot_gate_metrics(results: Dict[str, List[float]], save_path: str) -> None:
    """Bar chart: pass@1 mean+/-std for none/random/trace, 3 conditions."""
    ...

def plot_gradient_histogram(grad_reports: List[Dict], save_path: str) -> None:
    """Histogram: executed_grad_norm vs non_executed_grad_norm distributions."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Gate metrics bar chart | matplotlib, mean+std error bars per condition |
| L-5-2 | Gradient norm histogram | Overlaid histograms executed vs non-executed grad norms |

---

## Total Subtask Count: 13/30 used, 5 epics
