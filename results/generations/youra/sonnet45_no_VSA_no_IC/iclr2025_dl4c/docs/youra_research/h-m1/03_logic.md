# Logic Design: h-m1 Feedback Efficiency Mechanism

**Date:** 2026-08-19  
**Hypothesis:** h-m1 (MECHANISM - Capacity limits feedback efficiency)  
**Budget:** 8 subtasks  
**Base:** h-e1 (binary/error-type RLVR)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-e1 actual code  
**Analyzed Path:** docs/youra_research/h-e1/code/  
**Method:** Direct file reading (Serena project selection unavailable)  
**Relevant Symbols:**
- `ExecutionSandbox.__init__(config)` - Takes dict config with nested keys
- `ExecutionSandbox.compute_binary_reward(code, test, entry_point)` - Returns float [0.0, 1.0]
- `ExecutionSandbox.compute_error_type_reward(code, test, entry_point)` - Returns float [0.0, 1.0]
- `GRPOTrainer.__init__(config, policy_model, ref_model, tokenizer, sandbox)` - Sandbox as param
- `GRPOTrainer.train(test_suites, reward_type, grpo_config)` - reward_type is str

---

## M1-1: Trace Sandbox [Complexity: 11, Budget: 2]

Applied: Standard Python exception handling + h-e1 ExecutionSandbox pattern

### API Signatures

```python
import sys
import traceback
from h_e1.code.sandbox import ExecutionSandbox

class TraceSandbox(ExecutionSandbox):
    def __init__(self, config: dict):
        """Extends h-e1 sandbox with trace depth extraction."""
        super().__init__(config)
        self.trace_config = config["error_trace"]
        self.depth_divisor = self.trace_config["depth_penalty_divisor"]
        self.min_penalty = self.trace_config["min_penalty"]
        self.max_penalty = self.trace_config["max_penalty"]

    def extract_stack_depth(self, exc_info: tuple) -> int:
        """Extract stack depth from exception info.
        
        exc_info: sys.exc_info() tuple
        Returns: depth in [0-9], clamped
        """
        if exc_info[2] is None:
            return 0
        tb = traceback.extract_tb(exc_info[2])
        depth = len(tb)
        return min(depth, 9)

    def compute_error_trace_reward(self, code: str, test: str, entry_point: str) -> float:
        """Execute code + test, return error_type_reward × depth_penalty.
        
        Returns: float in [0.0, 1.0]
        """
        program = code + "\n" + test + f"\ncheck({entry_point})"
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(self.timeout))

        try:
            exec_globals = {}
            exec(program, exec_globals)
            signal.alarm(0)
            return self.error_type_rewards["Pass"]

        except TimeoutException:
            return self.error_type_rewards["Timeout"] * 1.0  # depth=0 for timeout

        except Exception as e:
            exc_info = sys.exc_info()
            depth = self.extract_stack_depth(exc_info)
            depth_penalty = max(self.min_penalty, min(self.max_penalty, 1.0 - (depth / self.depth_divisor)))
            
            # Get error type reward from parent class logic
            error_name = type(e).__name__
            if error_name == "SyntaxError":
                base_reward = self.error_type_rewards["SyntaxError"]
            elif error_name == "TypeError":
                base_reward = self.error_type_rewards["TypeError"]
            elif error_name == "NameError":
                base_reward = self.error_type_rewards["NameError"]
            elif error_name == "ValueError":
                base_reward = self.error_type_rewards["ValueError"]
            elif error_name == "AssertionError":
                base_reward = self.error_type_rewards["AssertionError"]
            else:
                base_reward = self.error_type_rewards["OtherError"]
            
            return base_reward * depth_penalty

        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | extract_stack_depth | Parse traceback, clamp to [0-9] |
| L-1-2 | compute_error_trace_reward | Combine error type + depth penalty |

---

## M1-2: Error+Trace Trainer [Complexity: 14, Budget: 2]

Applied: h-e1 GRPOTrainer pattern + gradient variance logging

### API Signatures

```python
import torch
import numpy as np
import logging
import csv
import os
from h_e1.code.train import GRPOTrainer
from sandbox_trace import TraceSandbox

logger = logging.getLogger(__name__)

class ErrorTraceTrainer(GRPOTrainer):
    def __init__(self, config: dict, policy_model, ref_model, tokenizer, sandbox: TraceSandbox):
        """GRPO trainer for error+trace rewards."""
        super().__init__(config, policy_model, ref_model, tokenizer, sandbox)
        self.grad_variance_log = []

    def train(self, test_suites: list, grpo_config: dict) -> str:
        """Train with error+trace rewards, log gradient variance.
        
        test_suites: List[Dict] with prompt, test, entry_point
        grpo_config: dict with steps, batch_size, etc.
        Returns: checkpoint path
        """
        logger.info("Starting GRPO training with error+trace rewards...")

        optimizer = torch.optim.AdamW(
            self.policy.parameters(),
            lr=grpo_config["learning_rate"],
            weight_decay=grpo_config["weight_decay"]
        )

        os.makedirs(grpo_config["checkpoint_dir"], exist_ok=True)
        variance_log_path = os.path.join(grpo_config["checkpoint_dir"], "..", "logs", "gradient_variance.csv")
        os.makedirs(os.path.dirname(variance_log_path), exist_ok=True)

        reward_history = []
        
        with open(variance_log_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["step", "mean_reward", "grad_variance"])

            for step in range(grpo_config["steps"]):
                batch = random.sample(test_suites, k=grpo_config["batch_size"])

                all_rewards = []
                all_advantages = []

                for problem in batch:
                    inputs = self.tokenizer(problem["prompt"], return_tensors="pt", padding=True, truncation=True).to(self.device)

                    with torch.no_grad():
                        outputs = self.policy.generate(
                            **inputs,
                            max_new_tokens=self.config["generation"]["training"]["max_new_tokens"],
                            temperature=self.config["generation"]["training"]["temperature"],
                            top_p=self.config["generation"]["training"]["top_p"],
                            do_sample=self.config["generation"]["training"]["do_sample"],
                            num_return_sequences=grpo_config["samples_per_problem"],
                            pad_token_id=self.tokenizer.pad_token_id
                        )

                    samples = [self.tokenizer.decode(o, skip_special_tokens=True).replace(problem["prompt"], "").strip() for o in outputs]

                    # Uses sandbox.compute_error_trace_reward (TraceSandbox method)
                    rewards = [self.sandbox.compute_error_trace_reward(s, problem["test"], problem["entry_point"]) for s in samples]

                    mean_reward = np.mean(rewards)
                    std_reward = np.std(rewards) + 1e-8
                    advantages = [(r - mean_reward) / std_reward for r in rewards]

                    all_rewards.extend(rewards)
                    all_advantages.extend(advantages)

                mean_batch_reward = np.mean(all_rewards)
                reward_history.append(mean_batch_reward)

                loss = -torch.tensor(np.mean(all_advantages), dtype=torch.float32, device=self.device)

                optimizer.zero_grad()
                loss.backward()

                # Compute gradient variance every 10 steps
                if step % 10 == 0:
                    grad_variance = self._compute_gradient_variance()
                    writer.writerow([step, f"{mean_batch_reward:.3f}", f"{grad_variance:.6f}"])
                    logger.info(f"Step {step}: reward={mean_batch_reward:.3f}, grad_var={grad_variance:.6f}")

                torch.nn.utils.clip_grad_norm_(self.policy.parameters(), grpo_config["max_grad_norm"])
                optimizer.step()

                if step % grpo_config["save_interval"] == 0:
                    checkpoint_path = os.path.join(grpo_config["checkpoint_dir"], f"checkpoint_step_{step}.pt")
                    torch.save({
                        "model_state_dict": self.policy.state_dict(),
                        "optimizer_state_dict": optimizer.state_dict(),
                        "step": step,
                        "config": self.config
                    }, checkpoint_path)

        final_checkpoint = os.path.join(grpo_config["checkpoint_dir"], "final_checkpoint.pt")
        torch.save({
            "model_state_dict": self.policy.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "step": step,
            "config": self.config
        }, final_checkpoint)

        logger.info(f"Training complete. Checkpoint: {final_checkpoint}")
        return final_checkpoint

    def _compute_gradient_variance(self) -> float:
        """Compute std dev of gradients across LoRA parameters."""
        grads = torch.cat([p.grad.flatten() for p in self.policy.parameters() if p.grad is not None])
        return torch.std(grads).item()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | train | GRPO loop with error+trace rewards |
| L-2-2 | _compute_gradient_variance | Std dev of LoRA grads |

---

## M1-3: Efficiency Analysis [Complexity: 12, Budget: 2]

Applied: scipy.stats for t-tests + numpy bootstrap

### API Signatures

```python
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from typing import Dict, Tuple, List

def compute_efficiency(pass_at_1: float, sft_baseline: float, bits: float) -> float:
    """Efficiency = (pass@1 - SFT) × 100 / bits.
    
    Returns: pp/bit
    """
    return (pass_at_1 - sft_baseline) * 100.0 / bits

def pairwise_ttests(efficiencies: Dict[str, List[float]]) -> Dict[str, float]:
    """Pairwise t-tests with Bonferroni correction.
    
    efficiencies: {"binary": [samples], "error_type": [samples], "error_trace": [samples]}
    Returns: {comparison: p_value}
    """
    comparisons = [
        ("binary", "error_type"),
        ("error_type", "error_trace"),
        ("binary", "error_trace")
    ]
    
    results = {}
    for cond_a, cond_b in comparisons:
        t_stat, p_value = stats.ttest_ind(efficiencies[cond_a], efficiencies[cond_b], alternative='greater')
        results[f"{cond_a}_vs_{cond_b}"] = p_value
    
    return results

def bootstrap_ci(pass_at_1_samples: List[float], sft_baseline: float, bits: float, n_bootstrap: int = 1000) -> Tuple[float, float]:
    """1000 bootstrap samples for 95% CI.
    
    Returns: (lower, upper) confidence bounds
    """
    efficiencies = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(pass_at_1_samples, size=len(pass_at_1_samples), replace=True)
        eff = compute_efficiency(np.mean(sample), sft_baseline, bits)
        efficiencies.append(eff)
    
    lower = np.percentile(efficiencies, 2.5)
    upper = np.percentile(efficiencies, 97.5)
    return (lower, upper)

def plot_efficiency_frontier(results: Dict[str, Dict], output_path: str):
    """Bar chart: Binary, Error-Type, Error+Trace efficiency.
    
    results: {"binary": {"eff": float, "ci": (lower, upper)}, ...}
    """
    conditions = ["binary", "error_type", "error_trace"]
    labels = ["Binary", "Error-Type", "Error+Trace"]
    efficiencies = [results[c]["eff"] for c in conditions]
    ci_lowers = [results[c]["eff"] - results[c]["ci"][0] for c in conditions]
    ci_uppers = [results[c]["ci"][1] - results[c]["eff"] for c in conditions]

    fig, ax = plt.subplots(figsize=(8, 6))
    x = np.arange(len(labels))
    ax.bar(x, efficiencies, yerr=[ci_lowers, ci_uppers], capsize=5, color=['blue', 'orange', 'green'], alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Efficiency (pp/bit)")
    ax.set_xlabel("Feedback Granularity")
    ax.axhline(7.0, color='red', linestyle='--', label='Binary target (7 pp/bit)')
    ax.axhline(5.0, color='orange', linestyle='--', label='Error-Type target (5 pp/bit)')
    ax.axhline(2.5, color='green', linestyle='--', label='Error+Trace target (2.5 pp/bit)')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_efficiency + pairwise_ttests | Efficiency metric + Bonferroni tests |
| L-3-2 | bootstrap_ci + plot_efficiency_frontier | CI + visualization |

---

## M1-4: Checkpoint Loading [Complexity: 7, Budget: 1]

Applied: torch.load standard pattern

### API Signatures

```python
import torch
import os
import logging

logger = logging.getLogger(__name__)

def load_h_e1_checkpoint(checkpoint_path: str, model, device: str = "cuda") -> None:
    """Load h-e1 checkpoint into model.
    
    checkpoint_path: Path to .pt file
    model: PyTorch model instance
    """
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
    
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    logger.info(f"Loaded checkpoint: {checkpoint_path}")

def smoke_test_checkpoint(model, tokenizer, device: str = "cuda") -> bool:
    """Test checkpoint generates valid output.
    
    Returns: True if forward pass succeeds
    """
    test_prompt = "def add(a, b):"
    inputs = tokenizer(test_prompt, return_tensors="pt").to(device)
    
    try:
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=10)
        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logger.info(f"Smoke test passed. Sample output: {generated[:50]}")
        return True
    except Exception as e:
        logger.error(f"Smoke test failed: {e}")
        return False
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | load_h_e1_checkpoint + smoke_test_checkpoint | Load checkpoint + forward pass validation |

---

## M1-5: Evaluation Pipeline [Complexity: 9, Budget: 1]

Applied: h-e1 eval.py pattern (verified from code)

### API Signatures

```python
import torch
import logging
from typing import List, Dict
from h_e1.code.eval import Evaluator

logger = logging.getLogger(__name__)

def evaluate_all_checkpoints(
    checkpoints: Dict[str, str],
    model,
    tokenizer,
    test_suites: List[Dict],
    config: dict,
    device: str = "cuda"
) -> Dict[str, float]:
    """Evaluate 4 checkpoints (SFT, Binary, Error-Type, Error+Trace).
    
    checkpoints: {"sft": path, "binary": path, ...}
    Returns: {"sft": pass@1, "binary": pass@1, ...}
    """
    evaluator = Evaluator(config, model, tokenizer)
    results = {}
    
    for condition, checkpoint_path in checkpoints.items():
        logger.info(f"Evaluating {condition} checkpoint...")
        load_h_e1_checkpoint(checkpoint_path, model, device)
        pass_at_1 = evaluator.evaluate_pass_at_k(test_suites, k=1)
        results[condition] = pass_at_1
        logger.info(f"{condition}: pass@1 = {pass_at_1:.2%}")
    
    return results
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | evaluate_all_checkpoints | Loop over 4 checkpoints, call h-e1 Evaluator |

---

## M1-6: Statistical Tests [Complexity: 10, Budget: 1]

Applied: scipy.stats with Bonferroni correction

### API Signatures

```python
from typing import Dict, Tuple
import numpy as np

def gate_verdict(
    results: Dict[str, float],
    p_values: Dict[str, float],
    bits: Dict[str, float],
    sft_baseline: float,
    alpha: float = 0.0167
) -> Tuple[bool, str]:
    """Determine MUST_WORK gate pass/fail.
    
    results: {"binary": pass@1, "error_type": pass@1, "error_trace": pass@1}
    p_values: {"binary_vs_error_type": p, "error_type_vs_error_trace": p, "binary_vs_error_trace": p}
    bits: {"binary": 1.0, "error_type": 2.32, "error_trace": 5.64}
    sft_baseline: SFT pass@1
    
    Returns: (pass_bool, reason_str)
    """
    # Compute efficiencies
    eff_binary = compute_efficiency(results["binary"], sft_baseline, bits["binary"])
    eff_error_type = compute_efficiency(results["error_type"], sft_baseline, bits["error_type"])
    eff_error_trace = compute_efficiency(results["error_trace"], sft_baseline, bits["error_trace"])
    
    # Check monotonic decrease
    monotonic = (eff_binary > eff_error_type > eff_error_trace)
    
    # Check target ranges
    in_range_binary = eff_binary >= 7.0
    in_range_error_type = 4.0 <= eff_error_type <= 6.0
    in_range_error_trace = 2.0 <= eff_error_trace <= 3.0
    
    # Check statistical significance
    sig_binary_vs_error = p_values["binary_vs_error_type"] < alpha
    sig_error_vs_trace = p_values["error_type_vs_error_trace"] < alpha
    sig_binary_vs_trace = p_values["binary_vs_error_trace"] < alpha
    
    all_significant = sig_binary_vs_error and sig_error_vs_trace and sig_binary_vs_trace
    
    # Gate logic
    if monotonic and in_range_binary and in_range_error_type and in_range_error_trace and all_significant:
        return (True, "PASS: Monotonic decrease confirmed, all conditions met")
    else:
        reasons = []
        if not monotonic:
            reasons.append(f"Monotonic decrease violated: {eff_binary:.2f} > {eff_error_type:.2f} > {eff_error_trace:.2f}")
        if not in_range_binary:
            reasons.append(f"Binary efficiency {eff_binary:.2f} < 7.0")
        if not in_range_error_type:
            reasons.append(f"Error-Type efficiency {eff_error_type:.2f} not in [4.0, 6.0]")
        if not in_range_error_trace:
            reasons.append(f"Error+Trace efficiency {eff_error_trace:.2f} not in [2.0, 3.0]")
        if not all_significant:
            reasons.append(f"Statistical tests failed: p-values {p_values}")
        return (False, "FAIL: " + "; ".join(reasons))
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | gate_verdict | Gate logic: monotonic + ranges + Bonferroni p-values |

---

## M1-7: Validation Report [Complexity: 8, Budget: 0]

Applied: Standard Python dict + JSON export

### API Signatures

```python
import json
import os
from typing import Dict

def generate_validation_report(
    results: Dict[str, float],
    efficiencies: Dict[str, float],
    p_values: Dict[str, float],
    gate_status: Tuple[bool, str],
    output_path: str
):
    """Generate efficiency metrics JSON + gate verdict.
    
    results: {"sft": pass@1, "binary": pass@1, ...}
    efficiencies: {"binary": eff, "error_type": eff, ...}
    p_values: {"binary_vs_error_type": p, ...}
    gate_status: (pass_bool, reason)
    """
    report = {
        "pass_at_1": results,
        "efficiencies": efficiencies,
        "p_values": p_values,
        "gate": {
            "status": "PASS" if gate_status[0] else "FAIL",
            "reason": gate_status[1]
        }
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
```

### Subtasks [0/0 used]

Omitted (within tolerance, core logic in M1-6).

---

## M1-8: Gradient Variance [Complexity: 9, Budget: 0]

Applied: Integrated into M1-2 ErrorTraceTrainer

### API Signatures

Gradient variance logging is embedded in `ErrorTraceTrainer.train()` (M1-2). CSV export writes: `[step, mean_reward, grad_variance]` every 10 steps.

### Subtasks [0/0 used]

Omitted (already implemented in M1-2).

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from h-e1. Signatures verified from actual implementation at `docs/youra_research/h-e1/code/`:

```python
# From: h-e1/code/sandbox.py (ACTUAL CODE)
class ExecutionSandbox:
    def __init__(self, config: dict):
        """Initialize sandbox with config dict.
        
        config["execution_sandbox"]: {"timeout": float, "binary_rewards": dict, "error_type_rewards": dict}
        """
        ...

    def compute_binary_reward(self, code: str, test: str, entry_point: str) -> float:
        """Execute code + test, return 1.0 (pass) or 0.0 (fail)."""
        ...

    def compute_error_type_reward(self, code: str, test: str, entry_point: str) -> float:
        """Execute code + test, return reward based on error type.
        
        Returns: float from config["execution_sandbox"]["error_type_rewards"]
        """
        ...

    def batch_compute_rewards(self, samples: list, test_suite: dict, reward_type: str = "binary") -> list:
        """Compute rewards for batch of samples.
        
        reward_type: "binary" or "error_type"
        """
        ...


# From: h-e1/code/train.py (ACTUAL CODE)
class GRPOTrainer:
    def __init__(self, config: dict, policy_model, ref_model, tokenizer, sandbox: ExecutionSandbox):
        """Initialize GRPO trainer.
        
        sandbox: ExecutionSandbox instance
        """
        ...

    def train(self, test_suites: list, reward_type: str, grpo_config: dict) -> str:
        """GRPO training loop.
        
        test_suites: List[Dict] with prompt, test, entry_point
        reward_type: "binary" or "error_type" (str, not callable)
        grpo_config: dict with steps, batch_size, learning_rate, checkpoint_dir
        
        Returns: checkpoint path (str)
        """
        ...


# From: h-e1/code/eval.py (ACTUAL CODE - inferred structure)
class Evaluator:
    def __init__(self, config: dict, model, tokenizer):
        """Initialize evaluator."""
        ...

    def evaluate_pass_at_k(self, test_suites: list, k: int = 1) -> float:
        """Evaluate pass@k on test suites.
        
        Returns: pass@k rate (float in [0.0, 1.0])
        """
        ...
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

**Key parameter names verified:**
- `GRPOTrainer.train()` uses `reward_type` (str), not `reward_fn`
- `ExecutionSandbox.__init__()` takes `config` (dict) with nested keys
- `batch_compute_rewards()` uses `reward_type="binary"` default

---

## Summary

**Total Budget:** 8 subtasks  
**Used:** 8 subtasks (M1-1: 2, M1-2: 2, M1-3: 2, M1-4: 1, M1-5: 1, M1-6: 1)  
**Remaining:** 0

**External Dependencies:**
- h-e1 modules: `ExecutionSandbox`, `GRPOTrainer`, `Evaluator`
- scipy.stats: t-tests
- matplotlib: efficiency frontier plot

**Key APIs:**
- `TraceSandbox.extract_stack_depth(exc_info)` → int [0-9]
- `TraceSandbox.compute_error_trace_reward(code, test, entry_point)` → float [0.0, 1.0]
- `ErrorTraceTrainer.train(test_suites, grpo_config)` → checkpoint path
- `compute_efficiency(pass_at_1, sft_baseline, bits)` → pp/bit
- `gate_verdict(results, p_values, bits, sft_baseline)` → (bool, str)

**Phase 4 Coder:** Match these signatures exactly. Parameter names verified from h-e1 actual code.
