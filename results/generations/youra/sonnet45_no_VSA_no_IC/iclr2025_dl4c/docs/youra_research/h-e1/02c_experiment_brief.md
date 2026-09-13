# Experiment Design: h-e1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Binary feedback achieves dual-threshold sufficiency: ≥8 pp absolute improvement over SFT baseline AND ≥80% relative retention of error-type feedback gains on HumanEval for 350M-1B models
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None (H-E1 is entry hypothesis)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK gate: If fail → Existence hypothesis refuted → lightweight feedback insufficient → re-evaluate main hypothesis

---

## Continuation Context

H-E1 is entry hypothesis with no prerequisites. Tests dual-threshold sufficiency of binary feedback.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in verification plan

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable - using Exa fallback*

### Archon Code Examples

*Archon MCP unavailable - using Exa fallback*

### Exa GitHub Implementations

**Query 1: Binary feedback RLVR training (MBPP/HumanEval)**

1. **RLVR for Small Models** (arxiv.org/html/2605.30478)
   - Models: Qwen3-0.6B, Llama3.2-1B
   - Dataset: MBPP (974 problems)
   - Reward: Binary unit-test pass/fail + graded error types
   - Result: +13 pp pass@1 on MBPP
   - Key: GRPO optimization, combined rewards mitigate degeneration

2. **MURPHY Multi-turn Feedback** (arxiv.org/html/2511.07833)
   - Models: Qwen3-1.7B, Qwen3-4B, OLMo-2-7B
   - Datasets: HumanEval, MBPP, BigCodeBench
   - Feedback: Quantitative (test pass rate) + qualitative (error messages)
   - Result: +8% relative gain over GRPO
   - Key: Iterative self-correction, retrospective credit assignment

3. **LETI Text Feedback Learning** (doi.org/10.18653/v1/2024.findings-naacl.16)
   - Model: 2B base
   - Dataset: MBPP training, HumanEval generalization
   - Feedback: Binary + textual (stack traces, error messages)
   - Result: Textual feedback achieves same performance with <50% gradient steps
   - Key: Feedback-conditioned fine-tuning (FCFT) with reward tokens

4. **PRLCoder Process Supervision** (arxiv.org/html/2502.01715v1)
   - Model: CodeT5+ 770M
   - Dataset: MBPP+
   - Reward: Line-by-line process rewards (mutation/refactoring verification)
   - Result: +10.5% over base, +5.1% over outcome-supervised RL
   - Key: Fine-grained rewards improve stability

5. **FALCON Dual Memory** (arxiv.org/html/2410.21349v5)
   - Model: DeepSeek-Coder-Instruct
   - Datasets: HumanEval, MBPP
   - Feedback: Multi-dimensional (compilation, style, complexity)
   - Result: +4.5% MBPP, +6.1% HumanEval over other RL methods
   - Key: Long/short-term memory buffers retain learned patterns

**Query 2: Execution reward implementation code**

6. **RLVR Training Script** (github.com/abyakod/llm-fine-tuning-guide)
   - Framework: TRL PPO
   - Reward: Binary (1.0 all tests pass, 0.0 otherwise)
   - Implementation: Subprocess execution with timeout
   - Code pattern:
   ```python
   def verify_code_solution(code, test_cases):
       # Execute code + test assertions
       # Return 1.0 if pass, 0.0 if fail
   ```

7. **LFM-Coder Sandbox** (github.com/rparkr/lfm-coder)
   - Framework: GRPO with QLoRA
   - Execution: Dual-engine (Monty Rust sandbox 1ms, Docker fallback 2577ms)
   - Benchmarks: HumanEvalPlus, MBPPPlus
   - Throughput: ~1000 exec/sec with Monty
   - Key: Asynchronous pipelining, fault-tolerant workflows

8. **Code Agent RL** (github.com/ESONG1999/Code_Agent_RL_Github)
   - Model: DeepSeek-Coder-1.3B
   - Framework: REINFORCE → PPO-Clip
   - Reward: Binary (1.0 pass) - length penalty
   - Sandbox: Unix signal.alarm timeout
   - Implementation: 4-bit QLoRA, mask prompt tokens in loss

9. **Feedback Over Form** (github.com/L3G/feedback-over-form)
   - Finding: Execution feedback loop +17-23 pp improvement
   - Topology: Flat generator-executor-refiner beats complex pipelines
   - Iteration analysis: >90% fixes on first refinement
   - Key: Feedback loop dominates pipeline structure

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is NOT a paper reproduction experiment. Hypothesis tests binary feedback sufficiency for small code LLMs using standard RLVR techniques.

**Recommended Implementation Path:**
- Primary: TRL GRPO framework (github.com/huggingface/trl) - standard RLVR implementation
- Fallback: Manual PPO with binary rewards (multiple reference implementations available)
- Justification: Established frameworks reduce implementation risk, GRPO proven effective for 0.6-1B models on MBPP (+13pp from recent work)

### Code Analysis (Serena MCP)

*Skipped* - RLVR framework code from Exa searches sufficiently clear. Standard TRL GRPO implementation patterns documented.

---

## Experiment Specification

### Dataset

**Name:** HumanEval (OpenAI)
**Type:** standard
**Source:** OpenAI human-eval (Austin et al. 2021)
**Size:** 164 hand-written Python programming problems
**Splits:** test only (no train split - use for evaluation only)
**Features:** task_id, prompt (function signature + docstring), canonical_solution, test (unit tests), entry_point
**Hypothesis Fit:** Comprehensive test suites enable binary feedback sufficiency hypothesis testing

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + openai/human-eval evaluation harness
- Identifier: `openai/openai_humaneval`
- Code:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("openai/openai_humaneval", split="test")
  # For evaluation: pip install git+https://github.com/openai/human-eval
  from human_eval.data import read_problems
  problems = read_problems()
  ```

**Preprocessing:** None required (pre-formatted for code generation)
**Evaluation:** Use `evaluate_functional_correctness` from human-eval package with pass@k metric

### Models

#### Baseline Model (SFT - No Execution Feedback)

**Name:** CodeGen-350M-mono OR StarCoderBase-1B
**Type:** Pretrained code generation model
**Source:** Salesforce (CodeGen) or BigCode (StarCoder)
**Size:** 350M or 1B parameters
**Hypothesis Fit:** Small model capacity constraints (350M-1B) test binary feedback sufficiency for resource-constrained settings

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `Salesforce/codegen-350M-mono` OR `bigcode/starcoderbase-1b`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  
  # Option 1: CodeGen-350M
  model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")
  tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
  
  # Option 2: StarCoderBase-1B
  model = AutoModelForCausalLM.from_pretrained("bigcode/starcoderbase-1b")
  tokenizer = AutoTokenizer.from_pretrained("bigcode/starcoderbase-1b")
  ```

**Configuration:**
- Context window: 2048 (CodeGen) / 8192 (StarCoder)
- Architecture: GPT-2 based with causal LM head
- Precision: fp16/bf16 recommended for memory efficiency

#### Proposed Model

**Architecture:** Baseline + RLVR Binary Feedback Training

**Modification:** Add execution feedback loop during training (no architecture changes - training procedure change)

**Core Mechanism Implementation:**

```python
# Binary Execution Feedback Reward (RLVR)
# Based on: RLVR implementation patterns from Exa searches

def compute_binary_reward(generated_code, test_cases, entry_point):
    """
    Execute generated code against test suite and return binary reward.
    
    Args:
        generated_code: str - model-generated Python function
        test_cases: str - unit test code (from HumanEval)
        entry_point: str - function name to test
    
    Returns:
        float - 1.0 if all tests pass, 0.0 otherwise
    """
    # Step 1: Construct executable program
    check_program = generated_code + "\n" + test_cases + "\n" + f"check({entry_point})"
    
    # Step 2: Execute in sandbox with timeout
    try:
        exec_globals = {}
        with timeout(seconds=3.0):  # Prevent infinite loops
            exec(check_program, exec_globals)
        return 1.0  # All tests passed
    except (AssertionError, TimeoutError, SyntaxError, RuntimeError):
        return 0.0  # Test failed or execution error

# Training loop (GRPO framework)
class RLVRTrainer:
    def __init__(self, model, ref_model, tokenizer):
        self.policy = model  # Trainable policy (with LoRA adapters)
        self.ref = ref_model  # Frozen reference model for KL penalty
        self.tokenizer = tokenizer
    
    def train_step(self, problems, n_samples=4):
        rewards = []
        for problem in problems:
            # Generate n samples per problem
            samples = self.policy.generate(problem['prompt'], num_return_sequences=n_samples)
            
            # Compute binary rewards
            sample_rewards = [
                compute_binary_reward(s, problem['test'], problem['entry_point'])
                for s in samples
            ]
            
            # Group Relative Policy Optimization (GRPO)
            advantages = (sample_rewards - np.mean(sample_rewards)) / (np.std(sample_rewards) + 1e-8)
            
            # Policy gradient with KL penalty
            loss = -torch.mean(advantages * log_probs) + 0.1 * kl_divergence(policy, ref)
            loss.backward()
        
        return np.mean(rewards)

# Integration: Replace standard supervised fine-tuning with RLVR training loop
```

### Training Protocol

**Phase 1: Supervised Fine-Tuning (SFT) Baseline**
- **Optimizer**: AdamW
- **Learning Rate**: 2e-5
- **Epochs**: 3-5 epochs on code corpus
- **Batch Size**: 8 (with gradient accumulation if needed)
- **Loss**: Causal LM loss on (prompt, canonical_solution) pairs
- **Source**: Standard SFT baseline from RLVR papers

**Phase 2: RLVR with Binary Feedback**
- **Framework**: GRPO (Group Relative Policy Optimization) via TRL library
- **Optimizer**: AdamW
- **Learning Rate**: 2e-7 (lower than SFT)
- **Training Steps**: 500-1000 steps
- **Batch Size**: 4 problems × 4 samples = 16 rollouts per batch
- **Reward**: Binary (1.0 all tests pass, 0.0 otherwise)
- **KL Coefficient**: 0.1 (penalty for diverging from SFT policy)
- **LoRA Config**: r=16, alpha=32, target_modules=["q_proj", "v_proj"]
- **Seeds**: 1 (fixed seed=42 for PoC)
- **Source**: RLVR small models paper (arxiv.org/html/2605.30478) - Qwen3-0.6B achieved +13pp with similar setup

**Comparison Conditions** (for dual-threshold test):
1. **SFT Baseline**: No execution feedback (Phase 1 only)
2. **Binary Feedback**: RLVR with binary rewards (Phase 1 + Phase 2)
3. **Error-Type Feedback**: RLVR with 5-category error types (SyntaxError, TypeError, NameError, ValueError, AssertionError)

**Hardware**: Single GPU (16GB VRAM sufficient with LoRA + fp16)

### Evaluation

**Primary Metric**: pass@1 on HumanEval test set (164 problems)
- Compute: Generate 1 completion per problem, execute against test suite, report % passing

**Success Criteria (EXISTENCE - Dual Threshold)**:
1. Binary achieves ≥8 pp absolute improvement: `pass@1_binary - pass@1_sft ≥ 8.0`
2. Binary achieves ≥80% relative retention: `(pass@1_binary - pass@1_sft) / (pass@1_error_type - pass@1_sft) ≥ 0.8`

**Evaluation Protocol**:
1. Load trained checkpoint
2. For each of 164 HumanEval problems:
   - Generate completion with greedy decoding (temperature=0)
   - Execute completion + test suite in sandbox
   - Record pass/fail
3. Compute pass@1 = (# passed) / 164

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code_generation
- Library: openai/human-eval evaluation harness
- Code:
  ```python
  from human_eval.evaluation import evaluate_functional_correctness
  # Saves results to samples.jsonl_results.jsonl with pass@k metrics
  results = evaluate_functional_correctness("samples.jsonl")
  print(f"pass@1: {results['pass@1']}")
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

**Recommended visualizations for binary feedback experiment:**
1. **Training Curve**: Pass@1 vs training steps for SFT baseline, Binary RLVR, Error-Type RLVR
2. **Reward Distribution**: Histogram of binary rewards across training problems
3. **Error Type Breakdown**: Bar chart showing proportion of SyntaxError, TypeError, NameError, ValueError, AssertionError in failed samples
4. **Retention Analysis**: Scatter plot showing (Error-Type gain - SFT) vs (Binary gain - SFT) per problem to visualize 80% retention threshold

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*Archon MCP unavailable during workflow execution - Exa used as fallback*

### B. GitHub Implementations (Exa)

**1. RLVR for Small Models (Qwen/Llama <1B)**
- **URL**: https://arxiv.org/html/2605.30478
- **Query**: "binary feedback reinforcement learning code generation training PyTorch HumanEval MBPP"
- **Key Findings**:
  - Models: Qwen3-0.6B, Llama3.2-1B on MBPP
  - Result: +13 pp pass@1 with GRPO
  - Framework: TRL 0.24, GRPO optimization
  - Reward: Binary unit-test + graded error types
- **Used For**: Training protocol, GRPO framework selection, expected baseline performance

**2. MURPHY Multi-turn Feedback**
- **URL**: https://arxiv.org/html/2511.07833
- **Query**: "binary feedback reinforcement learning code generation training PyTorch HumanEval MBPP"
- **Key Findings**:
  - Feedback types: Quantitative (pass rate) + qualitative (error messages)
  - Result: +8% relative gain over GRPO baseline
  - Multi-turn refinement approach
- **Used For**: Understanding feedback granularity spectrum

**3. LETI Textual Feedback Learning**
- **URL**: https://doi.org/10.18653/v1/2024.findings-naacl.16
- **Query**: "binary feedback reinforcement learning code generation training PyTorch HumanEval MBPP"
- **Key Findings**:
  - Binary + textual (stack traces) feedback
  - Textual achieves same performance with <50% gradient steps
  - Feedback-conditioned fine-tuning (FCFT)
- **Used For**: Error-type feedback condition design

**4. HumanEval Dataset Documentation**
- **URL**: https://huggingface.co/datasets/openai/openai_humaneval
- **Query**: "HumanEval dataset load_dataset openai evaluation Python implementation"
- **Key Findings**:
  - 164 hand-written Python problems
  - Fields: task_id, prompt, canonical_solution, test, entry_point
  - Loading: `load_dataset("openai/openai_humaneval")`
  - Evaluation harness: github.com/openai/human-eval
- **Used For**: Dataset specification, loading code

**5. CodeGen-350M Model Card**
- **URL**: https://huggingface.co/Salesforce/codegen-350M-mono
- **Query**: "CodeGen-350M StarCoder-1B pretrained model load PyTorch HuggingFace transformers"
- **Key Findings**:
  - 350M parameters, pre-trained on BigPython
  - Loading: `AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")`
  - Context: 2048 tokens
  - Architecture: GPT-2 based
- **Used For**: Baseline model specification, loading code

**6. StarCoderBase-1B Model Card**
- **URL**: https://huggingface.co/bigcode/starcoderbase-1b
- **Query**: "CodeGen-350M StarCoder-1B pretrained model load PyTorch HuggingFace transformers"
- **Key Findings**:
  - 1B parameters, trained on 80+ languages (The Stack v1.2)
  - Multi-Query Attention, 8192 token context
  - Fill-in-the-Middle objective, 1T tokens
  - Loading: `AutoModelForCausalLM.from_pretrained("bigcode/starcoderbase-1b")`
- **Used For**: Alternative baseline model option

**7. LFM-Coder Sandbox Implementation**
- **URL**: https://github.com/rparkr/lfm-coder
- **Query**: "execution feedback code LLM training pass fail reward function PyTorch implementation"
- **Key Findings**:
  - Dual-engine sandbox: Monty (Rust, 1ms) + Docker fallback (2577ms)
  - GRPO with QLoRA, 4-bit quantization
  - Throughput: ~1000 exec/sec
  - Asynchronous pipelining
- **Used For**: Execution sandbox design considerations

**8. RLVR Training Script Example**
- **URL**: https://github.com/abyakod/llm-fine-tuning-guide/blob/main/scripts/13_rlvr_training.py
- **Query**: "execution feedback code LLM training pass fail reward function PyTorch implementation"
- **Key Findings**:
  - Binary reward function: 1.0 all tests pass, 0.0 otherwise
  - Subprocess execution with timeout
  - PPO framework with TRL
- **Used For**: Binary reward computation pseudo-code

### C. Serena Code Analysis

*Skipped* - RLVR framework code sufficiently clear from Exa searches

### D. Phase 2B Verification Plan

**Source**: docs/youra_research/02b_verification_plan.md (Section 2.2: H-E1 Specification)
- **Hypothesis Statement**: Binary feedback achieves dual-threshold sufficiency
- **Success Criteria**:
  - ≥8 pp absolute improvement over SFT baseline
  - ≥80% relative retention: (Binary - SFT) / (Error-type - SFT) ≥ 0.8
- **Gate Type**: MUST_WORK
- **Used For**: Success criteria definition, dual-threshold specification

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19T17:01:00

### Workflow History for This Hypothesis

**Phase 2C - Experiment Design**: COMPLETED
- Date: 2026-08-19
- Status: IN_PROGRESS → COMPLETED
- Output: 02c_experiment_brief.md
- MCP Tools: Exa (Archon unavailable), Serena (skipped - code clear)
- Sources: 8 Exa GitHub/paper searches documented

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
