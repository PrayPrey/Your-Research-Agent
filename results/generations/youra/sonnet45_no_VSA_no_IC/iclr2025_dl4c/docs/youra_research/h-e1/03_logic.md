# Logic Design: h-e1 Binary Feedback Sufficiency

**Date:** 2026-08-19  
**Hypothesis:** h-e1 (EXISTENCE - Binary feedback dual-threshold sufficiency)  
**Source Documents:** 03_prd.md, 03_architecture.md, 02c_experiment_brief.md  

---

## Core Algorithms

### Algorithm 1: Binary Reward Computation

**Purpose:** Execute generated code with test suite and return binary reward (1.0 pass, 0.0 fail).

**Pseudo-code:**
```python
FUNCTION compute_binary_reward(code: str, test_cases: str, entry_point: str) -> float:
    # Construct executable program
    program = code + "\n" + test_cases + "\ncheck(" + entry_point + ")"
    
    # Initialize timeout handler
    SET timeout_handler = signal.alarm(3)  # 3 seconds
    
    TRY:
        # Execute in isolated environment
        exec_globals = {}
        exec(program, exec_globals)
        
        # All tests passed
        RETURN 1.0
        
    CATCH TimeoutError:
        # Infinite loop or excessive runtime
        RETURN 0.0
        
    CATCH SyntaxError, TypeError, NameError, ValueError, AssertionError:
        # Any execution failure
        RETURN 0.0
        
    CATCH Exception:
        # Catch-all for other errors
        RETURN 0.0
        
    FINALLY:
        # Disable timeout
        signal.alarm(0)
END FUNCTION
```

**Tensor Shapes:**
- Input: `code` (str), `test_cases` (str), `entry_point` (str)
- Output: scalar float ∈ {0.0, 1.0}

**Complexity:**
- Time: O(T) where T = execution time (≤3s timeout)
- Space: O(N) where N = code length

**Edge Cases:**
- Infinite loop → Timeout at 3s, return 0.0
- Empty code → SyntaxError, return 0.0
- Malformed test cases → RuntimeError, return 0.0
- Network access attempt → No network available in exec globals, NameError

---

### Algorithm 2: Error-Type Reward Computation

**Purpose:** Execute generated code and return graded reward based on error category.

**Pseudo-code:**
```python
FUNCTION compute_error_type_reward(code: str, test_cases: str, entry_point: str) -> float:
    # Construct executable program
    program = code + "\n" + test_cases + "\ncheck(" + entry_point + ")"
    
    # Initialize timeout handler
    SET timeout_handler = signal.alarm(3)
    
    TRY:
        # Execute in isolated environment
        exec_globals = {}
        exec(program, exec_globals)
        
        # All tests passed
        RETURN 1.0
        
    CATCH SyntaxError:
        # Code has syntax errors (most severe)
        RETURN 0.0
        
    CATCH TypeError:
        # Type mismatch (e.g., int + str)
        RETURN 0.2
        
    CATCH NameError:
        # Undefined variable
        RETURN 0.4
        
    CATCH ValueError:
        # Invalid value for operation (e.g., int("abc"))
        RETURN 0.6
        
    CATCH AssertionError:
        # Logical error (closest to correct)
        RETURN 0.8
        
    CATCH TimeoutError:
        # Infinite loop
        RETURN 0.0
        
    CATCH Exception:
        # Other errors (treat as syntax-level)
        RETURN 0.0
        
    FINALLY:
        signal.alarm(0)
END FUNCTION
```

**Tensor Shapes:**
- Input: `code` (str), `test_cases` (str), `entry_point` (str)
- Output: scalar float ∈ {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}

**Reward Rationale:**
- 0.0 (Syntax/Timeout): Code unparseable or divergent
- 0.2 (TypeError): Code parses but type system violated
- 0.4 (NameError): Type-correct but undefined symbols
- 0.6 (ValueError): Symbols defined but invalid values
- 0.8 (AssertionError): Logic runs but produces wrong answer
- 1.0 (Pass): Correct solution

**Error Category Ordering:** Syntax < Type < Name < Value < Assertion < Pass

---

### Algorithm 3: GRPO Training Loop

**Purpose:** Train policy with Group Relative Policy Optimization using execution rewards.

**Pseudo-code:**
```python
FUNCTION grpo_train(policy: Model, ref_policy: Model, prompts: List[str], 
                    test_suites: List[Dict], reward_fn: Callable, 
                    steps: int, kl_coef: float) -> Checkpoint:
    
    # Training hyperparameters
    lr = 2e-7
    optimizer = AdamW(policy.parameters(), lr=lr)
    samples_per_problem = 4
    
    FOR step IN range(steps):
        # Sample batch of problems
        batch = random.sample(prompts, k=4)  # 4 problems per batch
        
        all_rewards = []
        all_log_probs = []
        all_ref_log_probs = []
        
        FOR problem IN batch:
            # Generate multiple samples per problem
            samples = policy.generate(
                input_ids=tokenize(problem['prompt']),
                num_return_sequences=samples_per_problem,
                max_new_tokens=512,
                do_sample=True,
                temperature=1.0
            )  # Shape: (samples_per_problem, seq_len)
            
            # Compute rewards for each sample
            problem_rewards = []
            FOR sample IN samples:
                code = decode(sample)
                reward = reward_fn(code, problem['test'], problem['entry_point'])
                problem_rewards.append(reward)
            # problem_rewards shape: (samples_per_problem,)
            
            # Compute log probabilities
            log_probs = policy.compute_log_probs(samples)  # Shape: (samples_per_problem,)
            ref_log_probs = ref_policy.compute_log_probs(samples)  # Shape: (samples_per_problem,)
            
            # Group normalization (within problem)
            mean_reward = mean(problem_rewards)
            std_reward = std(problem_rewards) + 1e-8
            advantages = (problem_rewards - mean_reward) / std_reward
            # advantages shape: (samples_per_problem,)
            
            all_rewards.extend(problem_rewards)
            all_log_probs.extend(log_probs * advantages)  # Weighted by advantages
            all_ref_log_probs.extend(ref_log_probs)
        
        # Policy gradient loss (maximize log prob of high-advantage samples)
        pg_loss = -mean(all_log_probs)  # Negative for gradient ascent
        
        # KL divergence penalty (prevent policy from diverging too far)
        kl_div = mean(exp(all_log_probs - all_ref_log_probs) - 1)
        
        # Total loss
        loss = pg_loss + kl_coef * kl_div
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Logging
        IF step % 50 == 0:
            log("Step {}: mean_reward={:.3f}, kl={:.3f}, loss={:.3f}".format(
                step, mean(all_rewards), kl_div, loss
            ))
        
        # Checkpoint saving
        IF step % 100 == 0:
            save_checkpoint(policy, "checkpoint_step_{}.pt".format(step))
    
    # Save final checkpoint
    RETURN save_checkpoint(policy, "final_checkpoint.pt")
END FUNCTION
```

**Tensor Shapes:**
```
prompts:             List of strings (164 problems)
batch:               (batch_size=4, prompt_len)
samples:             (batch_size=4, samples_per_problem=4, seq_len) → (16, seq_len)
rewards:             (16,)  # scalar per sample
log_probs:           (16,)  # scalar per sample
ref_log_probs:       (16,)  # scalar per sample
advantages:          (16,)  # normalized within each problem group
pg_loss:             scalar
kl_div:              scalar
loss:                scalar
```

**GRPO vs PPO:**
- GRPO: Group-level advantage normalization (within problem)
- PPO: Global advantage normalization (across all samples)
- GRPO benefit: More stable for sparse rewards (binary feedback)

**KL Penalty Rationale:**
- Prevents policy from collapsing to degenerate solutions
- Coefficient 0.1: Allows ~10% divergence from reference policy
- Reference policy: Frozen SFT checkpoint (not updated during GRPO)

**Convergence Criteria:**
- Target: mean_reward ≥ 0.2 (20% of samples pass tests)
- Early stop: mean_reward < 0.1 for 100 consecutive steps (degeneration)
- Max steps: 1000 (budget constraint)

---

### Algorithm 4: HumanEval Evaluation

**Purpose:** Generate completions for all 164 problems and compute pass@1 metric.

**Pseudo-code:**
```python
FUNCTION evaluate_humaneval(model: Model, test_suites: List[Dict]) -> Dict:
    results = []
    
    FOR problem IN test_suites:
        # Greedy decoding (temperature=0)
        completion = model.generate(
            input_ids=tokenize(problem['prompt']),
            max_new_tokens=512,
            temperature=0.0,  # Deterministic
            do_sample=False,
            num_return_sequences=1
        )  # Shape: (1, seq_len)
        
        code = decode(completion[0])
        
        # Execute code with test suite
        TRY:
            program = code + "\n" + problem['test'] + "\ncheck(" + problem['entry_point'] + ")"
            exec_globals = {}
            with timeout(3):
                exec(program, exec_globals)
            passed = True
        CATCH Exception:
            passed = False
        
        results.append({
            "task_id": problem['task_id'],
            "completion": code,
            "passed": passed
        })
    
    # Compute pass@1 metric
    num_passed = sum([r['passed'] for r in results])
    pass_at_1 = num_passed / len(results)  # 164 problems
    
    RETURN {
        "pass@1": pass_at_1,
        "results": results
    }
END FUNCTION
```

**Tensor Shapes:**
```
problem['prompt']:   (prompt_len,)  # tokenized
completion:          (1, completion_len)
results:             List of 164 dicts
pass_at_1:           scalar float ∈ [0.0, 1.0]
```

**Greedy Decoding Rationale:**
- Deterministic generation (reproducible results)
- No sampling → No variance across runs
- Temperature=0 → Argmax at each step

**Timeout Enforcement:**
- Same 3-second timeout as training
- Prevents evaluation from hanging on infinite loops

---

### Algorithm 5: Gate Validation

**Purpose:** Check dual-threshold success criteria for EXISTENCE hypothesis.

**Pseudo-code:**
```python
FUNCTION validate_gate(sft_pass1: float, binary_pass1: float, error_type_pass1: float) -> Dict:
    # Threshold 1: Absolute improvement ≥8 percentage points
    absolute_improvement = (binary_pass1 - sft_pass1) * 100  # Convert to percentage points
    threshold_1_met = absolute_improvement >= 8.0
    
    # Threshold 2: Retention ratio ≥80%
    binary_gain = binary_pass1 - sft_pass1
    error_type_gain = error_type_pass1 - sft_pass1
    
    IF error_type_gain > 0:
        retention_ratio = binary_gain / error_type_gain
        threshold_2_met = retention_ratio >= 0.80
    ELSE:
        # Error-type failed to improve (degenerate case)
        retention_ratio = None
        threshold_2_met = False
    
    # Gate passes only if BOTH thresholds met
    gate_passed = threshold_1_met AND threshold_2_met
    
    RETURN {
        "gate_passed": gate_passed,
        "absolute_improvement": absolute_improvement,
        "retention_ratio": retention_ratio,
        "threshold_1_met": threshold_1_met,
        "threshold_2_met": threshold_2_met
    }
END FUNCTION
```

**Tensor Shapes:**
```
sft_pass1:              scalar float ∈ [0.0, 1.0]
binary_pass1:           scalar float ∈ [0.0, 1.0]
error_type_pass1:       scalar float ∈ [0.0, 1.0]
absolute_improvement:   scalar float (percentage points)
retention_ratio:        scalar float ∈ [0.0, ∞) or None
gate_passed:            boolean
```

**Edge Cases:**
- `error_type_gain ≤ 0`: Error-type failed to improve → Retention undefined, gate fails
- `binary_gain < 0`: Binary worse than SFT → Retention negative, gate fails
- `binary_gain = 0`: Binary same as SFT → Retention 0%, gate fails

**Success Scenarios:**
1. Binary: 18% pass@1, SFT: 10%, Error-Type: 20%
   - Absolute: 8pp ✓, Retention: 8pp / 10pp = 80% ✓ → PASS
2. Binary: 19% pass@1, SFT: 10%, Error-Type: 20%
   - Absolute: 9pp ✓, Retention: 9pp / 10pp = 90% ✓ → PASS

**Failure Scenarios:**
1. Binary: 17% pass@1, SFT: 10%, Error-Type: 20%
   - Absolute: 7pp ✗ → FAIL (threshold 1 not met)
2. Binary: 18% pass@1, SFT: 10%, Error-Type: 25%
   - Absolute: 8pp ✓, Retention: 8pp / 15pp = 53% ✗ → FAIL (threshold 2 not met)

---

## Data Structures

### Problem Representation
```python
Problem = {
    "task_id": str,           # e.g., "HumanEval/0"
    "prompt": str,            # Function signature + docstring
    "test": str,              # Unit test code (check function)
    "entry_point": str,       # Function name to test
    "canonical_solution": str # Ground truth solution (for SFT only)
}
```

### Checkpoint Structure
```python
Checkpoint = {
    "model_state_dict": OrderedDict,  # Model weights
    "optimizer_state_dict": OrderedDict,  # Optimizer state
    "step": int,  # Training step
    "config": {
        "lr": float,
        "kl_coef": float,
        "samples_per_problem": int
    }
}
```

### Evaluation Result
```python
EvaluationResult = {
    "pass@1": float,  # Overall metric
    "results": List[{
        "task_id": str,
        "completion": str,
        "passed": bool
    }]
}
```

---

## Control Flow

### Main Pipeline
```
START
  ↓
[Load HumanEval Dataset]
  ↓
[Initialize Model (CodeGen-350M / StarCoder-1B)]
  ↓
[Apply LoRA Adapters]
  ↓
[Freeze Reference Model]
  ↓
[SFT Training]
  ├─ FOR epoch IN 1..5:
  │    ├─ FOR batch IN dataset:
  │    │    ├─ Forward pass (prompt → solution)
  │    │    ├─ Compute causal LM loss
  │    │    └─ Backward pass
  │    └─ Save checkpoint
  ↓
[GRPO Binary Training]
  ├─ FOR step IN 1..500:
  │    ├─ Sample 4 problems
  │    ├─ Generate 4 completions per problem
  │    ├─ Compute binary rewards (via sandbox)
  │    ├─ Compute group advantages
  │    ├─ Policy gradient + KL penalty
  │    └─ Update policy
  ↓
[GRPO Error-Type Training]
  ├─ FOR step IN 1..500:
  │    ├─ Sample 4 problems
  │    ├─ Generate 4 completions per problem
  │    ├─ Compute error-type rewards (via sandbox)
  │    ├─ Compute group advantages
  │    ├─ Policy gradient + KL penalty
  │    └─ Update policy
  ↓
[Evaluation]
  ├─ Load SFT checkpoint → Evaluate → sft_pass1
  ├─ Load Binary checkpoint → Evaluate → binary_pass1
  └─ Load Error-Type checkpoint → Evaluate → error_type_pass1
  ↓
[Gate Validation]
  ├─ Compute absolute improvement
  ├─ Compute retention ratio
  └─ Check both thresholds
  ↓
[Report Results]
  ├─ Generate visualizations
  └─ Update verification_state.yaml
  ↓
END
```

---

## Error Handling Logic

### Sandbox Timeout
```python
FUNCTION safe_execute(code: str, timeout_sec: float) -> Tuple[bool, Any]:
    SET signal_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_sec)
    
    TRY:
        result = exec(code, {})
        signal.alarm(0)  # Disable timeout
        RETURN (True, result)
    CATCH TimeoutError:
        RETURN (False, "TIMEOUT")
    CATCH Exception as e:
        signal.alarm(0)
        RETURN (False, str(e))
END FUNCTION
```

### Memory Overflow Recovery
```python
FUNCTION train_with_fallback(model, data, batch_size):
    TRY:
        train(model, data, batch_size)
    CATCH RuntimeError as e:
        IF "out of memory" IN str(e):
            # Reduce batch size and retry
            log("CUDA OOM detected, reducing batch size")
            batch_size = batch_size // 2
            IF batch_size >= 1:
                train_with_fallback(model, data, batch_size)
            ELSE:
                RAISE Exception("Batch size too small, cannot proceed")
        ELSE:
            RAISE e
END FUNCTION
```

### Reward Degeneration Detection
```python
FUNCTION detect_degeneration(reward_history: List[float], window: int) -> bool:
    IF len(reward_history) < window:
        RETURN False
    
    recent_rewards = reward_history[-window:]
    mean_recent = mean(recent_rewards)
    
    # Degeneration: mean reward < 0.1 for 100 steps
    IF mean_recent < 0.1:
        log("WARNING: Reward degeneration detected (mean={:.3f})".format(mean_recent))
        RETURN True
    
    RETURN False
END FUNCTION
```

---

## Optimization Strategies

### Gradient Accumulation
```python
# Effective batch size = physical_batch_size × accumulation_steps
accumulation_steps = 4
physical_batch_size = 2  # Fits in 16GB VRAM

FOR step IN range(total_steps):
    optimizer.zero_grad()
    
    FOR micro_step IN range(accumulation_steps):
        batch = get_batch(physical_batch_size)
        loss = compute_loss(batch) / accumulation_steps  # Normalize
        loss.backward()  # Accumulate gradients
    
    optimizer.step()  # Update with accumulated gradients
```

**Benefit:** Effective batch size 8 with only 2 samples in memory at once.

### Mixed Precision Training
```python
# Use fp16 for forward/backward, fp32 for optimizer
scaler = torch.cuda.amp.GradScaler()

FOR batch IN dataloader:
    optimizer.zero_grad()
    
    with torch.cuda.amp.autocast():
        loss = model(batch)
    
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

**Benefit:** Halves memory footprint and speeds up training by ~2x.

---

## Pseudo-code Summary

**5 Core Algorithms:**
1. Binary reward: Execute code, return {0.0, 1.0}
2. Error-type reward: Execute code, return {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}
3. GRPO training: Group advantage normalization + policy gradient + KL penalty
4. HumanEval evaluation: Greedy generation + pass@1 metric
5. Gate validation: Dual-threshold checking (absolute ≥8pp, retention ≥80%)

**Key Innovations:**
- Group-relative advantages (GRPO) for stable sparse reward learning
- 5-category error-type rewards (gradient between syntax error and correct)
- Dual-threshold success criteria (both absolute improvement AND retention)

**Complexity Analysis:**
- Training: O(S × P × K × T) where S=steps, P=problems/batch, K=samples/problem, T=execution time
- Evaluation: O(N × T) where N=164 problems
- Gate validation: O(1)

---

**Logic Version:** 1.0  
**Next Steps:** Configuration schema (03_config.md), Task breakdown (03_tasks.yaml)
