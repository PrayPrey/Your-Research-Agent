# Experiment Design: H-E1

**Date:** 2026-08-29
**Author:** Anonymous
**Hypothesis Statement:** Higher bandwidth reward signals (categorical + continuous) provide more bits of information per gradient update than binary signals
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (none required)
**Gate Status:** MUST_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
Proposed reward signal (categorical + continuous) must demonstrate measurably higher information content per gradient update compared to binary pass/fail signals, as measured by faster convergence to pass@1 > 0.3 on MBPP.

---

## Continuation Context

This is the first hypothesis in the verification sequence. No previous results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in sequence.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Archon MCP unavailable** - Using web search results instead.

Key findings from literature:
1. **Dense Reward Signals for Code Generation** (arXiv:2601.03525): "Beyond Binary: Turning Partial Success into Dense Verifiable Rewards" - demonstrates graded reward designs with categories (passed, assertion error, runtime error, interpreter error) outperform binary rewards
2. **RLSF: Symbolic Feedback** (arXiv:2405.16661): Combines syntactic correctness, semantic structure, and functional correctness signals
3. **Execution-Grounded Credit Assignment** (arXiv:2603.16158): Token-level reward attribution for code generation

### Archon Code Examples

**Archon MCP unavailable** - Using web search results instead.

Key code patterns identified:
1. **TRL PPOTrainer**: Standard interface for PPO fine-tuning with custom reward functions
2. **Graded Reward Mapping**: `{passed: 1.0, assertion_error: 0.3, runtime_error: 0.1, syntax_error: 0.0}`
3. **Composite Reward**: `r = α * unit_test_reward + β * syntactic_reward + γ * semantic_reward`

### Exa GitHub Implementations

**Query: PPO reward shaping code generation LLM**

1. **RLHFlow/RLHF-Reward-Modeling** (GitHub)
   - Recipes for training reward models for RLHF
   - Includes PPO training scripts with TRL integration

2. **raghavc/LLM-RLHF-Tuning-with-PPO-and-DPO** (GitHub)
   - Comprehensive RLHF toolkit with PPO and DPO
   - Supports custom reward functions and datasets

3. **verl-project/verl** (GitHub Issue #5531)
   - Code RL Recipe: GRPO Training with Execution-Based Rewards
   - Modern implementation patterns for code generation RL

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a novel experiment (not reproduction), so we build on established frameworks:
1. TRL library (Hugging Face) - production-ready PPO implementation
2. CodeRL patterns - established reward signal design
3. MBPP/HumanEval evaluation - standard benchmarks

**Recommended Implementation Path:**
- Primary: TRL PPOTrainer with custom multi-signal reward function
- Fallback: Direct PPO implementation with PyTorch if TRL incompatible
- Justification: TRL is actively maintained, integrates with transformers, and has proven CodeLlama support

### Code Analysis (Serena MCP)

**Serena MCP unavailable** - Skipping local codebase analysis.

No existing implementation to analyze. This is a new experiment.

---

## Experiment Specification

### Dataset

**Name:** MBPP (Mostly Basic Python Programming)
**Type:** standard
**Source:** Google Research, Austin et al. 2021
**Size:** 974 problems (full), 427 problems (sanitized)
**Structure:** task_id, text (prompt), code (solution), test_list (3 test cases per problem)

**Splits:**
- Training: 374 problems (train split)
- Validation: 90 problems (validation split)
- Test: 500 problems (test split)

**Evaluation Benchmark:** HumanEval (164 problems) for generalization testing

**Loading Information** (for Phase 4 download):
- Method: Hugging Face datasets
- Identifier: google-research-datasets/mbpp
- Code:
```python
from datasets import load_dataset

# Training data
mbpp = load_dataset("google-research-datasets/mbpp", split="train")

# Evaluation data
humaneval = load_dataset("openai_humaneval", split="test")
```

### Models

#### Baseline Model

**Name:** CodeLlama-7B-Instruct
**Source:** Meta AI
**Parameters:** 7B
**Why:** Instruction-tuned for code generation, well-documented PPO fine-tuning support

**Loading Information** (for Phase 4 download):
- Method: Hugging Face transformers
- Identifier: codellama/CodeLlama-7b-Instruct-hf
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "codellama/CodeLlama-7b-Instruct-hf",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
```

#### Proposed Model

**Architecture:** CodeLlama-7B-Instruct + Multi-Signal Reward PPO

**Core Mechanism Implementation:**

```python
def compute_reward(generated_code: str, test_cases: list[str]) -> dict:
    """
    Multi-signal reward function with higher information bandwidth.
    Returns continuous + categorical signals vs binary pass/fail.
    """
    # Execute code and collect results
    results = execute_tests(generated_code, test_cases)
    
    # --- BINARY BASELINE (low bandwidth) ---
    binary_reward = 1.0 if all(r.passed for r in results) else 0.0
    
    # --- PROPOSED: HIGH BANDWIDTH SIGNAL ---
    
    # 1. Categorical signal: error type encoding (log2(4) = 2 bits)
    error_categories = {
        "passed": 1.0,
        "assertion_error": 0.5,    # Logic wrong but runs
        "runtime_error": 0.25,     # Crashes during execution
        "syntax_error": 0.0        # Won't parse
    }
    categorical_reward = error_categories.get(
        results[0].error_type, 0.0
    )
    
    # 2. Continuous signal: test pass ratio (continuous bits)
    pass_ratio = sum(1 for r in results if r.passed) / len(results)
    
    # 3. Partial credit: assertion closeness (if numeric)
    partial_scores = []
    for r in results:
        if r.error_type == "assertion_error" and r.expected and r.actual:
            # Normalized distance for numeric outputs
            if isinstance(r.expected, (int, float)):
                distance = abs(r.expected - r.actual) / (abs(r.expected) + 1e-8)
                partial_scores.append(max(0, 1 - distance))
    partial_credit = sum(partial_scores) / len(partial_scores) if partial_scores else 0.0
    
    # Composite high-bandwidth reward
    high_bandwidth_reward = (
        0.5 * categorical_reward +  # Error type signal
        0.3 * pass_ratio +          # Test pass ratio
        0.2 * partial_credit        # Numeric closeness
    )
    
    return {
        "binary": binary_reward,           # Baseline: 1 bit
        "high_bandwidth": high_bandwidth_reward,  # Proposed: ~4+ bits
        "info_breakdown": {
            "categorical": categorical_reward,
            "pass_ratio": pass_ratio,
            "partial_credit": partial_credit
        }
    }
```

### Training Protocol

**Algorithm:** PPO (Proximal Policy Optimization) via TRL
**Framework:** Hugging Face TRL library

**Hyperparameters:**
| Parameter | Value | Justification |
|-----------|-------|---------------|
| Learning rate | 1e-5 | Standard for LLM fine-tuning |
| Batch size | 4 per device | Memory constraint (7B model) |
| PPO epochs | 4 | TRL default |
| KL coefficient | 0.05 | Prevent reward hacking |
| Clip range | 0.2 | PPO standard |
| Training epochs | 3 | PoC scope |
| Seeds | 5 | Statistical validity |

**Conditions (3 total):**
1. **Binary Reward**: `reward = 1.0 if all_tests_pass else 0.0`
2. **Categorical Only**: `reward = error_category_score`
3. **Full High-Bandwidth**: `reward = composite(categorical + pass_ratio + partial_credit)`

**Training Loop:**
```python
from trl import PPOTrainer, PPOConfig

config = PPOConfig(
    learning_rate=1e-5,
    batch_size=4,
    ppo_epochs=4,
    kl_penalty="kl",
    init_kl_coef=0.05,
)

trainer = PPOTrainer(
    model=model,
    config=config,
    dataset=mbpp_train,
    tokenizer=tokenizer,
)

for epoch in range(3):
    for batch in trainer.dataloader:
        # Generate completions
        responses = trainer.generate(batch["query"])
        
        # Compute rewards (CONDITION-DEPENDENT)
        rewards = [compute_reward(r, batch["tests"]) for r in responses]
        
        # PPO update
        trainer.step(batch["query"], responses, rewards)
```

### Evaluation

**Primary Metric:** pass@1 on MBPP test split
**Secondary Metric:** pass@1 on HumanEval (generalization)
**Convergence Metric:** Training samples to reach pass@1 > 0.3

**Success Criteria (PoC):**
- High-bandwidth condition reaches pass@1 > 0.3 in fewer samples than binary condition
- Direction of effect: `samples_binary > samples_high_bandwidth`

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code_generation
- Library: evaluate (Hugging Face) + custom execution
- Code:
```python
from evaluate import load

# Code execution for pass@k
def evaluate_pass_at_k(model, dataset, k=1):
    correct = 0
    for problem in dataset:
        completions = generate_completions(model, problem["prompt"], n=k)
        if any(execute_tests(c, problem["test_list"]).all_passed for c in completions):
            correct += 1
    return correct / len(dataset)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **Learning Curves**: pass@1 vs training samples for all 3 conditions (line plot with confidence intervals)
2. **Reward Distribution**: Histogram of reward values per condition
3. **Convergence Speed**: Bar chart of samples-to-threshold for each condition
4. **Information Content**: Bits of information per gradient update estimate

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

Specifically:
- `samples_to_threshold(high_bandwidth) < samples_to_threshold(binary)`
- OR if threshold not reached: `pass_at_1(high_bandwidth, fixed_samples) > pass_at_1(binary, fixed_samples)`

---

## Appendix: Reference Implementations

### Academic Papers

1. **Beyond Binary: Turning Partial Success into Dense Verifiable Rewards** (arXiv:2601.03525)
   - Graded reward design for code generation
   - Key insight: Error category differentiation improves learning

2. **RLSF: Fine-tuning LLMs via Symbolic Feedback** (arXiv:2405.16661)
   - Composite reward: syntactic + semantic + functional
   - Proven on code generation tasks

3. **Execution-Grounded Credit Assignment for GRPO** (arXiv:2603.16158)
   - Token-level reward attribution
   - Shows dense signals improve convergence

### GitHub Repositories

1. **RLHFlow/RLHF-Reward-Modeling**: https://github.com/RLHFlow/RLHF-Reward-Modeling
   - Reward model training recipes

2. **raghavc/LLM-RLHF-Tuning-with-PPO-and-DPO**: https://github.com/raghavc/LLM-RLHF-Tuning-with-PPO-and-DPO
   - Complete RLHF pipeline with PPO

3. **meta-llama/codellama**: https://github.com/meta-llama/codellama
   - Official CodeLlama inference code

### Datasets

1. **MBPP**: https://huggingface.co/datasets/google-research-datasets/mbpp
2. **HumanEval**: https://huggingface.co/datasets/openai_humaneval

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-29

### Workflow History for This Hypothesis
- 2026-08-29: Phase 2C started, experiment design IN_PROGRESS
- 2026-08-29: Implementation research completed (web search, MCP unavailable)
- 2026-08-29: Experiment specification completed

---

*MCP Tools Used: WebSearch (Archon/Exa unavailable)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
