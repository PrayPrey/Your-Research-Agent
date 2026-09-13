# Experiment Design: H-M3

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** Dense credit assignment enables faster and more precise policy learning
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing learning efficiency hypothesis.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M2 CONDITIONAL_PASS)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (Token masking excludes non-executed code from gradients)

### Gate Condition
SHOULD_WORK: If fails, document limitation and proceed. Not a blocking gate.

**Success Criteria:**
1. FGO reaches 50% pass@1 threshold in <60% of Standard PPO's samples
2. FGO achieves higher final pass@1 than Standard PPO

---

## Continuation Context

H-M3 tests whether dense credit assignment (via FGO token masking) translates to faster learning convergence and better final performance. This is the efficiency hypothesis building on H-M1 (trace collection) and H-M2 (gradient exclusion).

### Previous Hypothesis Results

**H-M2 (Token Masking):** CONDITIONAL_PASS
- Gradient exclusion verified: masked tokens receive zero gradient
- Average 81.2% tokens masked (non-executed)
- Executed token gradient norm: ~0.0085
- Implementation ready for full training

**H-M1 (Trace Collection):** CONDITIONAL_PASS
- Token precision: 80.93%
- Token recall: 82.45%
- Token F1: 81.68%
- Trace capture rate: 100%

---

## Implementation Research Summary

### Archon Knowledge Base Findings

- PPO implementations from stable-baselines3 and custom implementations
- GAE (Generalized Advantage Estimation) standard implementation for dense rewards
- Training curve logging patterns with TensorBoard/wandb

### Archon Code Examples

- Distributed training with accelerate library
- Learning rate scheduling (cosine decay, warmup)
- Checkpoint management every N iterations

### Exa GitHub Implementations

**Key Finding:** PPO learning efficiency depends heavily on reward density.

From research:
- "PPO is an on-policy algorithm that learns best through a dense reward system"
- Sparse rewards cause PPO to optimize toward local maxima
- Dense rewards enable consistent convergence toward desired behavior

**StepCoder Paper (ACL 2024):**
- FGO (Fine-Grained Optimization) masks unexecuted code segments
- Combined with CCCS (Curriculum of Code Completion Subtasks)
- Outperforms PPOCoder, CodeRL on APPS+ dataset

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

FGO implementation from H-M2 is ready. Focus on training curve measurement.

**Recommended Implementation Path:**
- Primary: Use H-M2 validated FGO masking with training curve logging
- Fallback: Simplified efficiency proxy (gradient variance comparison)
- Justification: H-M2 infrastructure ready; add convergence tracking

### Code Analysis (Serena MCP)

Not applicable - building on existing H-M2 code.

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | HumanEval + MBPP |
| **Type** | standard |
| **Source** | OpenAI (HumanEval), Google (MBPP) |
| **Train Split** | HumanEval: 164 problems, MBPP: 374 train |
| **Test Split** | HumanEval: 164 (full), MBPP: 500 test |
| **Preprocessing** | Tokenize with CodeLlama tokenizer, max_length=512 |
| **Augmentation** | None |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `openai_humaneval`, `mbpp`
- Code:
```python
from datasets import load_dataset
humaneval = load_dataset("openai_humaneval")
mbpp = load_dataset("mbpp")
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| **Name** | CodeLlama-7B-Instruct |
| **Type** | Decoder-only transformer |
| **Source** | meta-llama/CodeLlama-7b-Instruct-hf |
| **Parameters** | 7B |
| **Justification** | Standard baseline for code generation RL |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/CodeLlama-7b-Instruct-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/CodeLlama-7b-Instruct-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/CodeLlama-7b-Instruct-hf")
```

#### Proposed Model

**Architecture:** CodeLlama-7B + FGO Token Masking (from H-M2)

**Core Mechanism Implementation:**

```python
def measure_convergence_efficiency(
    model,
    train_data,
    eval_data,
    fgo_enabled: bool,
    trace_collector,
    max_steps: int = 5000,
    eval_interval: int = 100,
    target_pass1: float = 0.5
) -> dict:
    """
    Measure training efficiency: steps to reach target pass@1.
    
    Returns:
        steps_to_target: Steps to reach 50% pass@1 (or max_steps if not reached)
        final_pass1: Final pass@1 at end of training
        learning_curve: List of (step, pass@1) tuples
    """
    optimizer = AdamW(model.parameters(), lr=1e-5)
    learning_curve = []
    steps_to_target = None
    
    for step in range(max_steps):
        batch = sample_batch(train_data)
        
        # Generate code and get reward
        generated = model.generate(batch["prompts"])
        rewards, traces = evaluate_with_traces(generated, batch["tests"])
        
        if fgo_enabled:
            # Dense credit: mask non-executed tokens
            masks = trace_collector.tokens_to_mask(traces, generated)
            loss = fgo_ppo_loss(model, generated, rewards, masks)
        else:
            # Sparse credit: standard PPO loss
            loss = standard_ppo_loss(model, generated, rewards)
        
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        
        # Evaluate periodically
        if step % eval_interval == 0:
            pass1 = evaluate_pass1(model, eval_data)
            learning_curve.append((step, pass1))
            
            if steps_to_target is None and pass1 >= target_pass1:
                steps_to_target = step
    
    return {
        "steps_to_target": steps_to_target or max_steps,
        "final_pass1": learning_curve[-1][1],
        "learning_curve": learning_curve
    }


def fgo_ppo_loss(model, generated, rewards, masks):
    """FGO-masked PPO loss (dense credit assignment)."""
    log_probs = model.log_prob(generated)
    advantages = compute_gae(rewards, model.value(generated))
    
    # Token-level loss with FGO mask
    per_token_loss = -log_probs * advantages.unsqueeze(-1)
    masked_loss = per_token_loss * masks
    
    return masked_loss.sum() / (masks.sum() + 1e-8)


def standard_ppo_loss(model, generated, rewards):
    """Standard PPO loss (sparse credit: sequence-level)."""
    log_probs = model.log_prob(generated)
    advantages = compute_gae(rewards, model.value(generated))
    
    # Sequence-level loss (all tokens weighted equally)
    per_token_loss = -log_probs * advantages.unsqueeze(-1)
    
    return per_token_loss.mean()
```

### Training Protocol

| Parameter | Value |
|-----------|-------|
| **Optimizer** | AdamW |
| **Learning Rate** | 1e-5 |
| **LR Schedule** | Cosine decay with 100-step warmup |
| **Batch Size** | 4 (gradient accumulation: 4, effective: 16) |
| **Max Steps** | 5000 |
| **Eval Interval** | 100 steps |
| **Seeds** | 42, 123, 456 |
| **PPO Clip** | 0.2 |
| **GAE Lambda** | 0.95 |
| **Gamma** | 0.99 |

**Conditions:**
1. **Standard PPO:** Sequence-level rewards, no masking
2. **FGO PPO:** Token-level masking based on execution traces

### Evaluation

| Metric | Description | Success Threshold |
|--------|-------------|-------------------|
| **Steps to 50% pass@1** | Training steps to reach 50% pass@1 | FGO < 60% of Standard |
| **Final pass@1** | Pass@1 at end of training | FGO > Standard |
| **Learning curve slope** | Average improvement per 100 steps | FGO slope > Standard slope |
| **Sample efficiency** | pass@1 improvement per sample | FGO > 1.5x Standard |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Code generation evaluation
- Library: Custom + human_eval
- Code:
```python
from human_eval.evaluation import evaluate_functional_correctness

def evaluate_pass1(model, eval_data, n_samples=1):
    samples = []
    for problem in eval_data:
        code = model.generate(problem["prompt"], num_return_sequences=n_samples)
        samples.append({"task_id": problem["task_id"], "completion": code[0]})
    
    results = evaluate_functional_correctness(samples, k=[1])
    return results["pass@1"]
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Learning Curve Comparison**: FGO vs Standard PPO pass@1 over training steps

#### Additional Figures (LLM Autonomous)

1. **Steps to Target Bar Chart**: Side-by-side bars showing steps to reach 50% pass@1
2. **Sample Efficiency Plot**: pass@1 improvement per 1000 samples
3. **Training Loss Curves**: PPO loss over training for both conditions
4. **Gradient Magnitude Distribution**: Histogram of gradient norms (dense vs sparse)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. FGO condition reaches target pass@1 in fewer steps than Standard
3. Learning curves can be plotted and compared

**Gate Type:** SHOULD_WORK
- If PASS: Dense credit assignment validated
- If FAIL: Document as limitation, efficiency claim limited but mechanism still valid

---

## Appendix: Reference Implementations

### StepCoder (ACL 2024)
- **Paper:** "StepCoder: Improving Code Generation with Reinforcement Learning from Compiler Feedback"
- **Authors:** Dou et al., Fudan University
- **URL:** https://aclanthology.org/2024.acl-long.251/
- **Key Contribution:** FGO (Fine-Grained Optimization) + CCCS (Curriculum)
- **Relevance:** Source of FGO mechanism; efficiency gains reported

### PPO Reference Implementations
- **stable-baselines3:** https://github.com/DLR-RM/stable-baselines3
- **PPO from scratch:** https://github.com/DavidH2802/PPO-from-scratch
- **Key Patterns:** GAE computation, clipped objective, learning curve logging

### Dense Reward Literature
- PPO learns best with dense reward signals (Analytics Vidhya tutorial)
- Sparse rewards cause convergence to local maxima
- FGO provides token-level density from execution traces

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10T09:00:00+00:00

### Workflow History for This Hypothesis

| Event | Timestamp | Phase | Details |
|-------|-----------|-------|---------|
| H-M3 set to IN_PROGRESS | 2026-08-10T08:47:13 | Hypothesis Loop | External loop starting Phase 2C → 3 → 4 for h-m3 |
| Experiment design started | 2026-08-10T09:00:00 | Phase 2C | MCP research: Archon KB, Exa code search |
| Experiment design completed | 2026-08-10T09:00:00 | Phase 2C | Generated 02c_experiment_brief.md |

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub/Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
