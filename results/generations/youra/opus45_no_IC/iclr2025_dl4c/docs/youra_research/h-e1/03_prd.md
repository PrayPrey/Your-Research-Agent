# Product Requirements Document: H-E1

**Hypothesis:** FGO token masking improves code generation performance across ALL feedback content types  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-10  
**Author:** Anonymous

---

## 1. Executive Summary

This PRD defines requirements for validating the H-E1 hypothesis: that Fine-Grained Optimization (FGO) token masking improves code generation performance across all three feedback content types (compile-only, test-only, and combined). This is a proof-of-concept experiment using a 2×3 factorial design.

**Success Criteria:** FGO_pass@1 > Standard_pass@1 for ALL 3 content types.

---

## 2. Problem Statement

Standard PPO training for code generation applies uniform credit to all generated tokens, regardless of whether they were actually executed. This leads to:
- Gradient noise from unexecuted code paths
- Inefficient credit assignment
- Suboptimal policy learning

FGO addresses this by masking gradients for tokens in code that was never executed during test evaluation.

---

## 3. Functional Requirements

### FR-1: Data Pipeline
- **FR-1.1:** Load HumanEval dataset (164 problems, full test set)
- **FR-1.2:** Load MBPP dataset (500 test problems, indices 11-510)
- **FR-1.3:** Implement code execution sandbox for reward computation
- **FR-1.4:** Implement execution trace collection via Python sys.settrace

### FR-2: Baseline Models (2 conditions)
- **FR-2.1:** Standard PPO baseline (no masking, uniform token gradients)
- **FR-2.2:** FGO PPO (Fine-Grained Optimization with execution-based token masking)

### FR-3: Feedback Content Types (3 conditions)
- **FR-3.1:** Compile-only feedback (reward based on syntax validity)
- **FR-3.2:** Test-only feedback (reward based on test pass/fail)
- **FR-3.3:** Combined feedback (compile + test rewards)

### FR-4: Training Protocol
- **FR-4.1:** Base model: CodeLlama-7B-Instruct
- **FR-4.2:** Optimizer: AdamW (lr=3e-6, weight_decay=0.01)
- **FR-4.3:** Batch size: 64 (per-device=16, gradient_accumulation=4)
- **FR-4.4:** Training episodes: 10,000
- **FR-4.5:** Reward function per StepCoder: +1.0 pass, -0.3 fail, -0.6 runtime, -1.0 compile

### FR-5: FGO Mechanism
- **FR-5.1:** Collect executed line numbers via trace
- **FR-5.2:** Map tokens to source lines
- **FR-5.3:** Create binary mask (1=executed, 0=unexecuted)
- **FR-5.4:** Apply mask to PPO loss computation

### FR-6: Evaluation
- **FR-6.1:** Primary metric: pass@1
- **FR-6.2:** Secondary metric: pass@10
- **FR-6.3:** Evaluate on full HumanEval (164 problems) and MBPP test (500 problems)
- **FR-6.4:** Generate 2×3 factorial bar chart for gate metrics

### FR-7: Ablation Variants
- **FR-7.1:** Standard + Compile-only
- **FR-7.2:** Standard + Test-only
- **FR-7.3:** Standard + Combined
- **FR-7.4:** FGO + Compile-only
- **FR-7.5:** FGO + Test-only
- **FR-7.6:** FGO + Combined

---

## 4. Data Specification

### 4.1 HumanEval
- **Source:** OpenAI
- **Size:** 164 programming problems
- **Task:** Function completion from docstring
- **Loading:** `from human_eval.data import read_problems`
- **Download:** Auto-download via human_eval package

### 4.2 MBPP
- **Source:** Google Research / HuggingFace
- **Size:** 500 test problems (indices 11-510)
- **Task:** Program synthesis from natural language
- **Loading:** `from datasets import load_dataset; mbpp = load_dataset("mbpp", split="test")`
- **Download:** Auto-download via HuggingFace datasets

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Training should complete within 48 hours on 4×A100 GPUs
- Evaluation should complete within 2 hours per condition

### NFR-2: Reproducibility
- Fixed seed: 1 (PoC only requires single seed)
- All hyperparameters logged to config file

### NFR-3: Storage
- Checkpoint every 1000 episodes
- Final model + logs: ~50GB per condition

---

## 6. Success Criteria

### Primary Gate Condition (MUST_WORK)
FGO > Standard for ALL 3 content types:
1. FGO+Compile > Standard+Compile
2. FGO+Test > Standard+Test
3. FGO+Combined > Standard+Combined

### Expected Baseline Performance (from StepCoder paper)
- Standard PPO (test-only): ~70% pass@1 on HumanEval
- StepCoder (FGO): ~75% pass@1 on HumanEval

---

## 7. Dependencies

### 7.1 Python Packages
- torch>=2.0
- transformers>=4.35
- trl>=0.7 (PPOTrainer)
- datasets
- human_eval
- accelerate
- peft (optional, for LoRA)

### 7.2 External Repositories
- StepCoder: https://github.com/Ablustrund/APPS_Plus (reference implementation)
- human-eval: https://github.com/openai/human-eval
- bigcode-evaluation-harness: https://github.com/bigcode-project/bigcode-evaluation-harness

---

## 8. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Execution trace overhead | Training slowdown | Batch trace collection |
| Token-line mapping errors | Invalid masking | Unit test mapping logic |
| Memory constraints | OOM on 7B model | Gradient accumulation + mixed precision |

---

## 9. Out of Scope

- Multiple seeds (PoC only)
- Alternative base models
- APPS+ dataset
- Curriculum learning variants

---

*Generated from Phase 2C Experiment Brief*
