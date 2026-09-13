# Logic Spec: H-E1 — Execution-RL vs DPO Structural Efficiency (EXISTENCE PoC)

**Version:** 1.0
**Date:** 2026-05-19
**Hypothesis Type:** EXISTENCE (LIGHT tier)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field — no existing code to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None — new implementation

---

## Applied Patterns

Applied: Standard DL Experiment Pipeline Pattern
Applied: TRL GRPOTrainer/DPOTrainer reward_funcs wiring
Applied: Monte Carlo KL divergence estimation
Applied: Zhang-Shasha tree edit distance via zss
Applied: Bootstrap CI with numpy percentile

---

## E-2: Reward Functions + AST Metric [Complexity: 12]

### API Signatures

```python
# rewards.py

import subprocess
import tempfile
import os
from typing import Optional

def run_evalplus_tests(task_id: str, completion: str) -> dict:
    """Execute completion against evalplus. Returns {passed, error_type}."""
    # Returns: {"passed": bool, "error_type": Optional[str]}
    # error_type in {None, "syntax", "runtime", "logic"}
    ...

def execution_reward_binary(
    completions: list[str],
    prompts: list[str],
    task_ids: list[str],
    **kwargs,
) -> list[float]:
    """Binary reward: +1.0 if all tests pass, 0.0 otherwise.
    Returns: list of float, len == len(completions)
    """
    ...

def execution_reward_error_type(
    completions: list[str],
    prompts: list[str],
    task_ids: list[str],
    **kwargs,
) -> list[float]:
    """Graded reward by error type.
    Returns: list of float, len == len(completions)
    """
    ...
```

```python
# ast_metric.py

import ast
from typing import Any
import zss

SEMANTIC_NODE_TYPES = frozenset([
    "If", "For", "While", "Try", "With",
    "Assign", "AugAssign", "Call", "Return",
])

class ZSSNode:
    """Wrapper making ast.AST nodes zss-compatible."""
    def __init__(self, label: str, children: list["ZSSNode"]):
        self.label = label
        self.children = children

def extract_semantic_ast(code: str) -> ZSSNode:
    """Parse code, filter to SEMANTIC_NODE_TYPES, return zss-compatible tree.
    Raises ValueError on syntax error.
    """
    ...

def compute_ast_semantic_edit_distance(code_a: str, code_b: str) -> float:
    """Zhang-Shasha edit distance between semantic ASTs.
    Returns float('inf') on parse failure of either input.
    """
    ...

def batch_ast_edit_distances(
    reference_codes: dict[str, str],
    candidate_codes: dict[str, str],
) -> dict[str, float]:
    """Per-problem edit distance. Keys: task_ids in both dicts."""
    ...
```

### Pseudo-code

```
run_evalplus_tests(task_id, completion):
1. Write completion to temp .py file
2. Invoke evalplus subprocess:
   evalplus.evaluate --dataset humaneval --samples <temp_file>
   OR use evalplus Python API: check_solution(task_id, completion)
3. Parse stdout/return dict for pass/fail status
4. On SyntaxError before exec -> error_type = "syntax"
5. On RuntimeError/Exception during exec -> error_type = "runtime"
6. On all tests NOT passing (no exception) -> error_type = "logic"
7. Return {"passed": bool, "error_type": Optional[str]}

execution_reward_binary(completions, prompts, task_ids):
1. For each (completion, task_id) in zip(completions, task_ids):
   a. result = run_evalplus_tests(task_id, completion)
   b. reward = 1.0 if result["passed"] else 0.0
2. Return list of rewards

execution_reward_error_type(completions, prompts, task_ids):
REWARD_MAP = {None: 1.0, "logic": 0.2, "runtime": -0.2, "syntax": -0.5}
1. For each (completion, task_id):
   a. result = run_evalplus_tests(task_id, completion)
   b. reward = REWARD_MAP[result["error_type"]]
2. Return list of rewards

extract_semantic_ast(code):
1. tree = ast.parse(code)  # raises SyntaxError on failure -> re-raise as ValueError
2. def _build(node):
   a. if type(node).__name__ not in SEMANTIC_NODE_TYPES: recurse into children, collect
   b. else: label = type(node).__name__
            children = [_build(c) for c in ast.iter_child_nodes(node)
                        if _build(c) is not None]
            return ZSSNode(label, children)
3. Return _build(tree) or ZSSNode("Module", [...]) as root

compute_ast_semantic_edit_distance(code_a, code_b):
1. try: tree_a = extract_semantic_ast(code_a)
   except ValueError: return float('inf')
2. try: tree_b = extract_semantic_ast(code_b)
   except ValueError: return float('inf')
3. return zss.simple_distance(tree_a, tree_b,
       get_children=lambda n: n.children,
       get_label=lambda n: n.label)
```

### Key Notes
- `run_evalplus_tests`: Use `evalplus.evaluate` Python API (not subprocess) where possible to avoid temp file overhead. Fall back to subprocess if API unavailable.
- GRPOTrainer calls reward_funcs with keyword args; `**kwargs` absorbs extras.
- REWARD_MAP for error_type: syntax=-0.5, runtime=-0.2, logic=+0.2, pass=+1.0 (note architecture says -0.5/-0.2/+0.2/+1.0).

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | evalplus wrapper | run_evalplus_tests with error_type classification |
| L-2-2 | binary reward | execution_reward_binary wiring |
| L-2-3 | error-type reward | execution_reward_error_type with REWARD_MAP |
| L-2-4 | ZSSNode wrapper | ast-to-zss bridge class |
| L-2-5 | AST filter traversal | extract_semantic_ast recursive filter |
| L-2-6 | edit distance | compute_ast_semantic_edit_distance + batch |

---

## E-3: GRPO Training [Complexity: 13]

### API Signatures

```python
# train_grpo.py

from config import ExperimentConfig
from trl import GRPOTrainer, GRPOConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Callable

def _get_reward_fn(reward_variant: str) -> Callable:
    """Return reward function matching variant name. reward_variant: 'binary'|'error_type'"""
    ...

def _build_grpo_config(cfg: ExperimentConfig, output_dir: str) -> GRPOConfig:
    """Construct GRPOConfig from ExperimentConfig fields."""
    ...

def train_grpo(
    cfg: ExperimentConfig,
    reward_variant: str,   # "binary" | "error_type"
    output_dir: str,
) -> str:
    """Run GRPOTrainer; save checkpoints every cfg.grpo_save_steps steps.
    Returns: path to final checkpoint directory (str).
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, seq_len] | Tokenized prompt+completion |
| logits | [B, seq_len, vocab_size] | Model output |
| log_probs | [B, seq_len] | Per-token log prob |
| rewards | [B] | One scalar per completion |

### Pseudo-code

```
_build_grpo_config(cfg, output_dir):
1. Return GRPOConfig(
     learning_rate=cfg.grpo_lr,
     per_device_train_batch_size=cfg.grpo_batch_size,
     gradient_accumulation_steps=cfg.grpo_grad_accum,
     num_generations=cfg.grpo_num_generations,
     beta=cfg.grpo_beta,
     max_steps=cfg.grpo_steps,
     save_steps=cfg.grpo_save_steps,
     output_dir=output_dir,
     seed=cfg.seed,
     bf16=(cfg.dtype == "bfloat16"),
   )

train_grpo(cfg, reward_variant, output_dir):
1. tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
2. model = AutoModelForCausalLM.from_pretrained(cfg.model_id, torch_dtype=bfloat16)
3. dataset = load_grpo_dataset(cfg)
4. reward_fn = _get_reward_fn(reward_variant)
   # reward_fn signature: (completions, prompts, task_ids, **kwargs) -> list[float]
5. grpo_config = _build_grpo_config(cfg, output_dir)
6. trainer = GRPOTrainer(
     model=model,
     args=grpo_config,
     train_dataset=dataset,
     reward_funcs=[reward_fn],
     tokenizer=tokenizer,
   )
7. trainer.train()
8. trainer.save_model(output_dir + "/final")
9. return output_dir + "/final"
```

### Key Notes
- TRL GRPOTrainer (>=1.3.0) accepts `reward_funcs` as list of callables.
- reward_fn receives `completions: list[str]` — GRPOTrainer passes decoded completions, not token IDs.
- task_ids must be embedded in dataset column and passed via `**kwargs` through GRPOTrainer's reward_funcs calling convention.
- Save intermediate checkpoints for KL matching: `save_steps=cfg.grpo_save_steps` (every 100 steps).
- Log KL divergence to trainer state or custom callback for later `load_checkpoint_kl_log`.

### Subtasks [13/13 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | GRPOConfig builder | Map ExperimentConfig to GRPOConfig |
| L-3-2 | reward_fn dispatcher | _get_reward_fn selector |
| L-3-3 | GRPOTrainer init | Model + tokenizer + dataset wiring |
| L-3-4 | KL logging callback | Custom callback to log KL per checkpoint |
| L-3-5 | CLI entrypoint | argparse for variant selection |

---

## E-4: DPO Training [Complexity: 11]

### API Signatures

```python
# train_dpo.py

from config import ExperimentConfig
from trl import DPOTrainer, DPOConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import Dataset

def _build_dpo_config(cfg: ExperimentConfig, output_dir: str) -> DPOConfig:
    """Construct DPOConfig from ExperimentConfig fields."""
    ...

def train_dpo(
    cfg: ExperimentConfig,
    output_dir: str,
) -> str:
    """Run DPOTrainer on execution-oracle preference pairs.
    Returns: path to final checkpoint directory (str).
    """
    ...
```

### Pseudo-code

```
_build_dpo_config(cfg, output_dir):
1. Return DPOConfig(
     learning_rate=cfg.dpo_lr,
     per_device_train_batch_size=cfg.dpo_batch_size,
     gradient_accumulation_steps=cfg.dpo_grad_accum,
     beta=cfg.dpo_beta,
     max_steps=cfg.dpo_steps,
     save_steps=cfg.dpo_save_steps,
     output_dir=output_dir,
     seed=cfg.seed,
     bf16=(cfg.dtype == "bfloat16"),
   )

train_dpo(cfg, output_dir):
1. cache_path = output_dir + "/dpo_pairs_cache.json"
2. if os.path.exists(cache_path):
     dataset = Dataset.from_json(cache_path)
   else:
     dataset = generate_dpo_pairs(cfg, cfg.model_id)
     dataset.to_json(cache_path)
3. tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
4. model = AutoModelForCausalLM.from_pretrained(cfg.model_id, torch_dtype=bfloat16)
5. ref_model = AutoModelForCausalLM.from_pretrained(cfg.model_id, torch_dtype=bfloat16)
   ref_model.eval()  # frozen reference model
6. dpo_config = _build_dpo_config(cfg, output_dir)
7. trainer = DPOTrainer(
     model=model,
     ref_model=ref_model,
     args=dpo_config,
     train_dataset=dataset,
     tokenizer=tokenizer,
   )
   # dataset columns: {"prompt": str, "chosen": str, "rejected": str}
8. trainer.train()
9. trainer.save_model(output_dir + "/final")
10. return output_dir + "/final"
```

### Key Notes
- DPO dataset must have columns: `prompt`, `chosen`, `rejected`.
- Cache pairs to disk to avoid re-generation on restart.
- `ref_model` is the frozen base model (SFT-only checkpoint or base model itself).
- Save checkpoints every `cfg.dpo_save_steps` for KL matching parity with GRPO.

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | DPOConfig builder | Map ExperimentConfig to DPOConfig |
| L-4-2 | pair caching | Cache/load DPO pairs from disk |
| L-4-3 | DPOTrainer init | ref_model + dataset column format |
| L-4-4 | CLI entrypoint | argparse for standalone execution |

---

## E-5: KL Metric + Checkpoint Matching [Complexity: 12]

### API Signatures

```python
# kl_metric.py

import torch
import json
import os
from transformers import PreTrainedModel, PreTrainedTokenizer
from config import ExperimentConfig

def compute_kl_divergence(
    model: PreTrainedModel,
    ref_model: PreTrainedModel,
    prompts: list[str],
    tokenizer: PreTrainedTokenizer,
    n_samples: int = 100,
) -> float:
    """Monte Carlo KL(pi_theta || pi_ref) on held-out prompts.
    Returns: scalar float (mean KL across prompts).
    """
    ...

def load_checkpoint_kl_log(checkpoint_dir: str) -> dict[int, float]:
    """Load step->KL mapping from kl_log.json in checkpoint_dir.
    Returns: {step: kl_value}
    """
    ...

def match_checkpoints(
    kl_logs: dict[str, dict[int, float]],
    tolerance: float = 0.05,
) -> list[dict[str, int]]:
    """Match checkpoints across conditions within ±tolerance KL.
    Args:
        kl_logs: {condition_name: {step: kl_value}}
    Returns: list of {condition_name: matched_step} dicts
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, seq_len] | Single prompt, no batching for memory |
| logits_theta | [1, seq_len, vocab_size] | Policy model logits |
| logits_ref | [1, seq_len, vocab_size] | Reference model logits |
| log_p_theta | [1, seq_len] | Policy log probs |
| log_p_ref | [1, seq_len] | Reference log probs |
| kl_per_token | [1, seq_len] | Token-level KL contribution |

### Pseudo-code

```
compute_kl_divergence(model, ref_model, prompts, tokenizer, n_samples=100):
1. kl_values = []
2. for prompt in prompts[:n_samples]:
   a. inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
      # input_ids: [1, seq_len]
   b. with torch.no_grad():
        logits_theta = model(**inputs).logits          # [1, seq_len, vocab_size]
        logits_ref = ref_model(**inputs).logits        # [1, seq_len, vocab_size]
   c. log_p_theta = F.log_softmax(logits_theta, dim=-1)  # [1, seq_len, vocab_size]
      log_p_ref   = F.log_softmax(logits_ref,   dim=-1)  # [1, seq_len, vocab_size]
   d. p_theta = log_p_theta.exp()                         # [1, seq_len, vocab_size]
   e. kl_per_token = (p_theta * (log_p_theta - log_p_ref)).sum(-1)  # [1, seq_len]
   f. kl_prompt = kl_per_token.mean().item()
   g. kl_values.append(kl_prompt)
3. return float(np.mean(kl_values))

load_checkpoint_kl_log(checkpoint_dir):
1. log_path = os.path.join(checkpoint_dir, "kl_log.json")
2. if not os.path.exists(log_path): return {}
3. return json.load(open(log_path))  # {str(step): float} -> convert keys to int

match_checkpoints(kl_logs, tolerance=0.05):
# Strategy: for each KL value in the first condition, find steps in all
# other conditions whose KL is within ±tolerance of that value.
1. conditions = list(kl_logs.keys())
2. anchor_condition = conditions[0]
3. anchor_kl_series = kl_logs[anchor_condition]  # {step: kl}
4. matched_pairs = []
5. for anchor_step, anchor_kl in sorted(anchor_kl_series.items()):
   a. match = {anchor_condition: anchor_step}
   b. for cond in conditions[1:]:
        best_step = None
        best_diff = float('inf')
        for step, kl in kl_logs[cond].items():
          diff = abs(kl - anchor_kl)
          if diff <= tolerance and diff < best_diff:
            best_step = step
            best_diff = diff
        if best_step is None: break  # can't match all conditions
        match[cond] = best_step
   c. if len(match) == len(conditions):
        matched_pairs.append(match)
6. return matched_pairs  # list[{condition: step}]
```

### Key Notes
- KL computation runs per-prompt with no batching to avoid OOM on 7B model.
- `kl_log.json` is written by a training callback (in train_grpo.py / train_dpo.py) at each save_steps.
- `match_checkpoints` uses greedy matching; tolerance=0.05 means within 5% absolute KL.
- Deduplicate matched_pairs if anchor has multiple steps near same KL level.

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | per-prompt KL | Token-level KL computation loop |
| L-5-2 | MC aggregation | Mean over prompts |
| L-5-3 | kl_log I/O | JSON load/save for checkpoint KL logs |
| L-5-4 | greedy matching | Cross-condition ±tolerance matching |
| L-5-5 | deduplication | Remove duplicate matched pairs |

---

## E-6: Evaluation + Bootstrap CI [Complexity: 14]

### API Signatures

```python
# evaluate.py

import numpy as np
from config import ExperimentConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

def generate_solutions(
    model_path: str,
    problems: dict,                   # {task_id: problem_dict}
    tokenizer_id: str,
    cfg: ExperimentConfig,
) -> dict[str, str]:
    """Greedy-decode solutions for all problems.
    Returns: {task_id: solution_code}
    """
    ...

def run_evalplus_evaluation(
    solutions_path: str,
    dataset: str,                     # "humaneval" | "mbpp"
) -> dict[str, float]:
    """Run evalplus CLI. Returns per-task pass@1 results.
    Returns: {task_id: 1.0 or 0.0}
    """
    ...

def compute_semantic_edit_per_kl(
    ast_distances: dict[str, float],
    kl_value: float,
) -> float:
    """Mean AST edit distance / KL value (gate metric).
    Returns: float
    """
    ...

def bootstrap_ci(
    grpo_efficiencies: np.ndarray,    # shape [N_matched_checkpoints]
    dpo_efficiencies: np.ndarray,     # shape [N_matched_checkpoints]
    n_samples: int = 10000,
    ci: float = 0.95,
) -> dict:
    """Bootstrap CI for (GRPO_best - DPO_best) efficiency differential.
    Returns: {point_estimate, ci_lower, ci_upper, gate_pass: bool}
    """
    ...

def run_full_evaluation(
    condition_checkpoints: dict[str, str],  # {condition_name: checkpoint_path}
    cfg: ExperimentConfig,
) -> dict:
    """Evaluate all 4 conditions at KL-matched checkpoints.
    Returns: aggregated results dict.
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, prompt_len] | Single problem, greedy decode |
| generated_ids | [1, prompt_len + max_new_tokens] | Full sequence |

### Pseudo-code

```
generate_solutions(model_path, problems, tokenizer_id, cfg):
1. tokenizer = AutoTokenizer.from_pretrained(tokenizer_id)
2. model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=bfloat16)
3. model.eval()
4. solutions = {}
5. for task_id, problem in problems.items():
   a. prompt = format_problem_prompt(problem)
   b. inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
      # input_ids: [1, prompt_len]
   c. with torch.no_grad():
        outputs = model.generate(**inputs, do_sample=False, max_new_tokens=512)
        # outputs: [1, prompt_len + max_new_tokens]
   d. completion = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:],
                                    skip_special_tokens=True)
   e. solutions[task_id] = completion
6. return solutions

run_evalplus_evaluation(solutions_path, dataset):
1. cmd = ["evalplus.evaluate", "--dataset", dataset, "--samples", solutions_path]
2. result = subprocess.run(cmd, capture_output=True, text=True)
3. parse result.stdout JSON -> {task_id: pass@1}
4. return per_task_results

compute_semantic_edit_per_kl(ast_distances, kl_value):
1. if kl_value == 0.0: return float('inf')  # guard against div-by-zero
2. mean_dist = np.mean(list(ast_distances.values()))
3. return mean_dist / kl_value

bootstrap_ci(grpo_efficiencies, dpo_efficiencies, n_samples=10000, ci=0.95):
# grpo_efficiencies: [N], dpo_efficiencies: [N]
1. rng = np.random.default_rng(seed=42)
2. diffs = []
3. for _ in range(n_samples):
   a. idx = rng.integers(0, len(grpo_efficiencies), size=len(grpo_efficiencies))
   b. grpo_sample = grpo_efficiencies[idx]
   c. dpo_sample = dpo_efficiencies[idx]
   d. diff = grpo_sample.mean() - dpo_sample.mean()
   e. diffs.append(diff)
4. diffs = np.array(diffs)
5. alpha = (1 - ci) / 2
6. ci_lower = np.percentile(diffs, alpha * 100)
7. ci_upper = np.percentile(diffs, (1 - alpha) * 100)
8. point_estimate = grpo_efficiencies.mean() - dpo_efficiencies.mean()
9. gate_pass = ci_lower > cfg.gate_magnitude  # both bounds > 0.20
10. return {
      "point_estimate": point_estimate,
      "ci_lower": ci_lower,
      "ci_upper": ci_upper,
      "gate_pass": gate_pass,
    }

run_full_evaluation(condition_checkpoints, cfg):
1. kl_prompts = load_kl_prompts(cfg)
2. ref_model, ref_tokenizer = load_base_model(cfg.model_id)  # SFT-only reference
3. kl_logs = {}
4. for cond, ckpt_path in condition_checkpoints.items():
     kl_logs[cond] = load_checkpoint_kl_log(ckpt_path)
5. matched_pairs = match_checkpoints(kl_logs, tolerance=cfg.kl_tolerance)
   # matched_pairs: list[{condition: step}]
6. problems_he = load_humaneval_plus()
7. problems_mbpp = load_mbpp_plus()
8. ref_solutions = generate_solutions(cfg.model_id, problems_he, cfg.model_id, cfg)
9. grpo_efficiencies = []
10. dpo_efficiencies = []
11. for match in matched_pairs:
    a. for cond, step in match.items():
       - ckpt = condition_checkpoints[cond] + f"/checkpoint-{step}"
       - solutions = generate_solutions(ckpt, problems_he, cfg.model_id, cfg)
       - save solutions to temp JSON
       - pass1 = run_evalplus_evaluation(temp_json, "humaneval")
       - kl_val = kl_logs[cond][step]
       - ast_dists = batch_ast_edit_distances(ref_solutions, solutions)
       - eff = compute_semantic_edit_per_kl(ast_dists, kl_val)
       - if "grpo" in cond: grpo_efficiencies.append(eff)
       - if "dpo"  in cond: dpo_efficiencies.append(eff)
12. ci_result = bootstrap_ci(
      np.array(grpo_efficiencies),
      np.array(dpo_efficiencies),
      cfg.bootstrap_samples, cfg.bootstrap_ci
    )
13. return {
      "grpo_efficiencies": grpo_efficiencies,
      "dpo_efficiencies": dpo_efficiencies,
      "bootstrap_ci": ci_result,
      "kl_matched_pairs": matched_pairs,
      "pass1_results": pass1,
    }
```

### Key Notes
- `generate_solutions` uses greedy decoding (`do_sample=False`) for deterministic evaluation.
- `run_evalplus_evaluation` writes solutions to JSON file first (evalplus CLI format: `{task_id: [completion]}`).
- `bootstrap_ci` gate condition: `ci_lower > cfg.gate_magnitude (0.20)` — both CI bounds above threshold.
- `run_full_evaluation` iterates matched_pairs; if few pairs, efficiency arrays may be small — still valid for bootstrap.
- For MBPP+ evaluation, repeat analogously with `problems_mbpp`.

### Subtasks [14/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | greedy decode loop | generate_solutions per problem |
| L-6-2 | evalplus CLI wrapper | run_evalplus_evaluation subprocess |
| L-6-3 | gate metric | compute_semantic_edit_per_kl |
| L-6-4 | bootstrap sampling | bootstrap_ci with numpy percentile |
| L-6-5 | gate check | ci_lower > gate_magnitude |
| L-6-6 | full eval orchestration | run_full_evaluation KL matching loop |

---

## E-1: Setup + Data Pipeline [Complexity: 10, Medium]

### API Signatures

```python
# data.py

from datasets import Dataset
from config import ExperimentConfig

def load_grpo_dataset(cfg: ExperimentConfig) -> Dataset:
    """Load CodeAlpaca-20K, apply DeepSeek-Coder chat template.
    Returns Dataset with columns: [prompt, task_id]
    """
    ...

def load_kl_prompts(cfg: ExperimentConfig) -> list[str]:
    """Fixed 100-prompt held-out set, sampled with seed=42.
    Returns: list of str, len == cfg.kl_prompt_count
    """
    ...

def generate_dpo_pairs(cfg: ExperimentConfig, model_id: str) -> Dataset:
    """Generate execution-oracle pairs.
    Returns Dataset with columns: [prompt, chosen, rejected]
    """
    ...

def load_humaneval_plus() -> dict:
    """Return HumanEval+ problem dict via evalplus API."""
    ...

def load_mbpp_plus() -> dict:
    """Return MBPP+ problem dict via evalplus API."""
    ...
```

---

## E-7: Orchestrator + Visualization [Complexity: 10, Medium]

### API Signatures

```python
# run_experiment.py

from config import ExperimentConfig

def run_all_conditions(cfg: ExperimentConfig) -> dict:
    """Orchestrate 4 conditions sequentially.
    Conditions: SFT-only, SFT+DPO, SFT+GRPO-binary, SFT+GRPO-error-type
    Returns: results dict with all metrics.
    """
    ...

def save_results(results: dict, output_dir: str) -> None:
    """Save results to output_dir/results.json."""
    ...
```

```python
# visualize.py

from config import ExperimentConfig

def plot_gate_metric_comparison(results: dict, cfg: ExperimentConfig) -> str:
    """Bar chart with 95% CI error bars. Returns saved path."""
    ...

def plot_kl_trajectories(kl_logs: dict[str, dict[int, float]], cfg: ExperimentConfig) -> str:
    """KL vs steps line plot for all conditions. Returns saved path."""
    ...

def plot_ast_vs_kl_scatter(results: dict, cfg: ExperimentConfig) -> str:
    """Scatter plot: AST edit vs KL per matched checkpoint. Returns saved path."""
    ...

def plot_pass1_curves(results: dict, cfg: ExperimentConfig) -> str:
    """pass@1 learning curves vs steps. Returns saved path."""
    ...

def generate_all_figures(results: dict, kl_logs: dict, cfg: ExperimentConfig) -> list[str]:
    """Run all 4 plots. Returns list of saved paths."""
    ...
```

---

## Consolidated Subtask List

| ID | Epic | Subtask | Description |
|----|------|---------|-------------|
| L-2-1 | E-2 | evalplus wrapper | run_evalplus_tests with error_type |
| L-2-2 | E-2 | binary reward | execution_reward_binary |
| L-2-3 | E-2 | error-type reward | execution_reward_error_type |
| L-2-4 | E-2 | ZSSNode wrapper | ast-to-zss bridge |
| L-2-5 | E-2 | AST filter traversal | extract_semantic_ast |
| L-2-6 | E-2 | edit distance | compute + batch AST distances |
| L-3-1 | E-3 | GRPOConfig builder | ExperimentConfig -> GRPOConfig |
| L-3-2 | E-3 | reward_fn dispatcher | _get_reward_fn |
| L-3-3 | E-3 | GRPOTrainer init | model + dataset wiring |
| L-3-4 | E-3 | KL logging callback | per-checkpoint KL to JSON |
| L-3-5 | E-3 | CLI entrypoint | argparse variant selection |
| L-4-1 | E-4 | DPOConfig builder | ExperimentConfig -> DPOConfig |
| L-4-2 | E-4 | pair caching | cache/load DPO pairs |
| L-4-3 | E-4 | DPOTrainer init | ref_model + column format |
| L-4-4 | E-4 | CLI entrypoint | standalone execution |
| L-5-1 | E-5 | per-prompt KL | token-level KL loop |
| L-5-2 | E-5 | MC aggregation | mean over prompts |
| L-5-3 | E-5 | kl_log I/O | JSON load/save |
| L-5-4 | E-5 | greedy matching | cross-condition ±tolerance |
| L-5-5 | E-5 | deduplication | remove duplicate pairs |
| L-6-1 | E-6 | greedy decode | generate_solutions |
| L-6-2 | E-6 | evalplus CLI | run_evalplus_evaluation |
| L-6-3 | E-6 | gate metric | compute_semantic_edit_per_kl |
| L-6-4 | E-6 | bootstrap sampling | bootstrap_ci numpy |
| L-6-5 | E-6 | gate check | ci_lower > gate_magnitude |
| L-6-6 | E-6 | full eval orchestration | run_full_evaluation loop |
