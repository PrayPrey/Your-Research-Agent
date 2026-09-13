# Experiment Design: H-E1

**Date:** 2026-08-08
**Author:** Anonymous
**Hypothesis Statement:** Training×Refinement interaction > 0 on logit(pass@1), p<0.05, OR≥1.2
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (None required)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
Training×Refinement interaction > 0 on logit(pass@1), p<0.05, OR≥1.2

---

## Continuation Context

First hypothesis in verification chain. No previous results.

### Previous Hypothesis Results (if applicable)
N/A - This is the root hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: RL code generation self-refine**
- Results: Limited relevant findings (KB focused on diffusion models)
- Insight: Need external sources for code generation RL

**Query 2: Code generation execution feedback**
- Results: General ML training patterns found
- Hyperparameters: lr=2e-5 to 5e-5, AdamW optimizer common

### Archon Code Examples

- Limited code examples for CodeRL/Self-Refine pattern in KB
- Training scripts show standard HuggingFace Trainer patterns
- LoRA fine-tuning: rank=4-64, target_modules=["q_proj", "k_proj", "v_proj"]

### Exa GitHub Implementations

**Repository 1**: [salesforce/CodeRL](https://github.com/salesforce/CodeRL) (⭐ 572)
- **Relevance**: Official CodeRL implementation - RL training for code generation
- **Architecture**: CodeT5 base + REINFORCE/PPO with critic model
- **Key Insight**: Uses execution feedback as reward signal
- **Training**: Actor-critic setup, unit test pass rate as reward

**Repository 2**: [madaan/self-refine](https://github.com/madaan/self-refine) (⭐ 815)
- **Relevance**: Official Self-Refine implementation - iterative refinement
- **Architecture**: Single LLM as generator + refiner + feedback provider
- **Protocol**: FEEDBACK → REFINE → FEEDBACK loop, K iterations
- **Insight**: No RL training needed for test-time refinement

**Repository 3**: [evalplus/evalplus](https://github.com/evalplus/evalplus)
- **Relevance**: Standard evaluation framework for HumanEval+/MBPP+
- **Key**: 80x more tests than original HumanEval, rigorous evaluation
- **Usage**: `evalplus.evaluate --model X --dataset humaneval`

**Key Paper**: RLEF (ICML 2025) - RL with Execution Feedback
- Shows RL training improves iterative code refinement
- 8B and 70B models tested on competitive programming

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Status |
|----------|--------|--------|
| 1 | salesforce/CodeRL | ✅ Available - use for RL training pattern |
| 2 | salesforce/CodeT5 | ✅ Available - base model fine-tuning |
| 3 | madaan/self-refine | ✅ Available - refinement protocol |
| 4 | evalplus/evalplus | ✅ Available - evaluation framework |

**Recommended Implementation Path:**
- Primary: CodeT5+-220M from HuggingFace + custom RL training loop
- Fallback: Adapt CodeRL codebase for CodeT5+ base
- Justification: CodeT5+ has better HumanEval baseline (15.5% pass@1 for 770M), CodeRL provides RL training pattern

### Code Analysis (Serena MCP)

*Skipped - code patterns clear from Exa findings. Key patterns:*
- CodeT5+ seq2seq training: `tune_codet5p_seq2seq.py`
- RL training: Actor-critic with execution reward
- Self-Refine: Prompt-based feedback→refine loop at inference

---

## Experiment Specification

### Dataset

**Primary Dataset**: HumanEval+ (164 problems)
- **Type**: standard
- **Source**: evalplus/evalplus
- **Purpose**: Code generation benchmark with rigorous test suite (80x more tests)
- **Split**: All 164 problems for evaluation

**Secondary Dataset**: MBPP+ (378 problems)
- **Type**: standard
- **Source**: evalplus/evalplus
- **Purpose**: Additional validation on entry-level programming problems (35x more tests)
- **Split**: All 378 problems for evaluation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + evalplus
- Identifier: `evalplus/humanevalplus`, `evalplus/mbppplus`
- Code:
```python
from evalplus.data import get_human_eval_plus, get_mbpp_plus
humaneval_problems = get_human_eval_plus()
mbpp_problems = get_mbpp_plus()
```

### Models

#### Baseline Model

**Architecture**: CodeT5+-220M (Salesforce/codet5p-220m)
- **Type**: Encoder-decoder seq2seq
- **Parameters**: 220M
- **Pretrained**: CodeSearchNet (6 PLs)
- **Baseline Performance**: ~15% pass@1 on HumanEval (zero-shot)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `Salesforce/codet5p-220m`
- Code:
```python
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
model = AutoModelForSeq2SeqLM.from_pretrained("Salesforce/codet5p-220m")
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5p-220m")
```

#### Proposed Model

**Architecture:** CodeT5+-220M + RL Fine-tuning with Execution Feedback

**Core Mechanism Implementation:**

```python
# Core Mechanism: RL Training with Execution Feedback
# Based on: CodeRL (NeurIPS 2022), RLEF (ICML 2025)

class RLCodeTrainer:
    """
    RL training with structurally diverse execution feedback.
    Hypothesis: Induces feedback-conditioned edit policy.
    """
    def __init__(self, model, tokenizer, critic=None):
        self.model = model
        self.tokenizer = tokenizer
        self.optimizer = AdamW(model.parameters(), lr=2e-5)
    
    def compute_reward(self, code: str, tests: List[str]) -> Tuple[float, str]:
        """Execute code against tests, return (reward, feedback)."""
        result = execute_code_with_tests(code, tests)
        reward = result.pass_rate  # 0.0 to 1.0
        feedback = result.error_message if result.failed else "All tests passed"
        return reward, feedback
    
    def rl_step(self, prompt: str, tests: List[str]):
        """Single RL training step with REINFORCE."""
        # Generate code
        code = self.model.generate(prompt, do_sample=True, temperature=0.8)
        # Get execution feedback
        reward, feedback = self.compute_reward(code, tests)
        # Compute policy gradient loss
        log_prob = self.model.log_prob(prompt, code)
        loss = -reward * log_prob  # REINFORCE
        loss.backward()
        self.optimizer.step()
        return reward

# Test-time Self-Refine Protocol (K=3 iterations)
def self_refine(model, prompt: str, tests: List[str], K: int = 3) -> str:
    code = model.generate(prompt)
    for _ in range(K):
        reward, feedback = execute_and_get_feedback(code, tests)
        if reward == 1.0:
            break
        refine_prompt = f"{prompt}\n\nPrevious code:\n{code}\n\nFeedback:\n{feedback}\n\nRefined code:"
        code = model.generate(refine_prompt)
    return code
```

### Training Protocol

**Experimental Conditions (2×2 Factorial):**

| Condition | Training | Inference |
|-----------|----------|-----------|
| CE-Single | Cross-Entropy | Single-shot |
| CE-Refine | Cross-Entropy | Self-Refine K=3 |
| RL-Single | RL (execution feedback) | Single-shot |
| RL-Refine | RL (execution feedback) | Self-Refine K=3 |

**Training Configuration:**
- **Optimizer**: AdamW
  - lr: 2e-5
  - weight_decay: 0.05
  - warmup_steps: 200
  - **Source**: CodeT5+ fine-tuning defaults
- **Batch Size**: 8 per GPU
- **Epochs**: 10 (CE), 5 (RL phase)
- **Loss**: 
  - CE: Cross-entropy on code tokens
  - RL: REINFORCE with execution reward
- **Seeds**: 1 (PoC)

**RL-Specific:**
- Reward: Test pass rate (0.0 to 1.0)
- Feedback diversity: Error messages from execution

### Evaluation

**Primary Metric**: pass@1 on HumanEval+
- Greedy decoding (temperature=0)
- Full test suite evaluation

**Secondary Metric**: pass@1 on MBPP+

**Success Criteria (Gate):**
- Training × Refinement interaction > 0 on logit(pass@1)
- PoC: (RL-Refine - RL-Single) > (CE-Refine - CE-Single)
- Direction only, no statistical test for PoC

**Expected Baseline Performance:**
- CE-Single: ~15% pass@1 (CodeT5+ zero-shot baseline)
- Source: CodeT5+ HumanEval benchmarks

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Code generation
- Library: evalplus
- Code:
```python
from evalplus.evaluate import evaluate_functional_correctness
results = evaluate_functional_correctness(samples_file, dataset="humaneval")
pass_at_1 = results["pass@1"]
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: 2×2 factorial bar chart showing pass@1 for all 4 conditions

#### Additional Figures (LLM Autonomous)
- Interaction plot: Training method (x-axis) × Inference method (lines)
- Learning curve: pass@1 vs training steps for CE vs RL

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (all 4 conditions train/evaluate successfully)
2. Interaction effect > 0: `(RL_Refine - RL_Single) > (CE_Refine - CE_Single)`

**Mechanism Verification:**
- Pre-condition: RL training receives execution feedback (not just CE loss)
- Activation indicator: Log "RL reward: X.XX" during training
- Metric delta: RL conditions should show different pass@1 pattern than CE

---

## Appendix: Reference Implementations

### Primary References

1. **CodeRL** (NeurIPS 2022)
   - Paper: https://arxiv.org/abs/2207.01780
   - Code: https://github.com/salesforce/CodeRL
   - Key: RL training with execution feedback for code generation

2. **Self-Refine** (NeurIPS 2023)
   - Paper: https://arxiv.org/abs/2303.17651
   - Code: https://github.com/madaan/self-refine
   - Key: Iterative refinement protocol at inference time

3. **CodeT5+** (EMNLP 2023)
   - Code: https://github.com/salesforce/CodeT5
   - Model: Salesforce/codet5p-220m
   - Key: Base model for fine-tuning

4. **EvalPlus** (NeurIPS 2023)
   - Paper: https://arxiv.org/abs/2305.01210
   - Code: https://github.com/evalplus/evalplus
   - Key: Rigorous HumanEval+/MBPP+ evaluation

5. **RLEF** (ICML 2025)
   - Paper: https://proceedings.mlr.press/v267/gehring25a.html
   - Key: End-to-end RL for execution feedback grounding

6. **CYCLE** (OOPSLA 2024)
   - Paper: https://dl.acm.org/doi/10.1145/3649825
   - Key: Learning to self-refine code generation

### Code Snippets

**CodeT5+ Fine-tuning (from salesforce/CodeT5):**
```python
training_args = TrainingArguments(
    output_dir=args.save_dir,
    num_train_epochs=args.epochs,
    per_device_train_batch_size=8,
    learning_rate=2e-5,
    weight_decay=0.05,
    warmup_steps=200,
    fp16=True,
)
trainer = Trainer(model=model, args=training_args, train_dataset=train_data)
trainer.train()
```

**EvalPlus Evaluation:**
```bash
evalplus.evaluate --model <model_path> --dataset humaneval --greedy
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-08

### Workflow History for This Hypothesis
- 2026-08-08: Phase 2C experiment design started
- 2026-08-08: Research completed (Archon, Exa)
- 2026-08-08: Experiment specification synthesized

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
