# Experiment Design: H-E1

**Date:** 2026-05-19
**Author:** Anonymous
**Hypothesis Statement:** Under controlled KL-matched conditions, if execution-feedback RL (GRPO) is applied instead of DPO on identical base model and data, then execution-RL exhibits ≥20% higher semantic-edit-per-KL than DPO, because execution reward forces probability mass toward control-flow and data-flow AST transformations.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (H-E1 has no prerequisites)
**Gate Status:** MUST_WORK — Bootstrap 95% CI for efficiency differential must exclude zero AND magnitude ≥20%. Failure triggers STOP with PIVOT option.

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK: Bootstrap 95% CI for efficiency differential (execution-RL minus DPO semantic-edit-per-KL) must exclude zero AND magnitude ≥20%. Failure triggers STOP.

---

## Continuation Context

H-E1 is the foundational hypothesis — first in the chain H-E1 → H-M1 → H-M2 → H-M3 → H-M4. No previous hypothesis results to load.

### Previous Hypothesis Results (if applicable)
N/A — H-E1 has no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: GRPO DPO execution-feedback RL code generation experiment design**
- No domain-relevant results found. Archon KB contains HuggingFace Diffusers content (image generation domain), not LLM alignment / code generation domain.
- Similarity scores: 0.39 (very low, unrelated content)

**Query 2: AST edit distance KL divergence policy movement structural efficiency**
- No domain-relevant results found. Same diffusers content returned.
- Similarity scores: 0.42 (low, unrelated)

**Query 3: GRPO reinforcement learning LLM training TRL HumanEval code benchmark**
- No domain-relevant results found. Archon KB does not contain TRL/RLHF/code-gen content.

**Assessment:** Archon KB does not contain prior cases for this research domain (execution-RL vs DPO for code generation). All implementation patterns sourced from Exa GitHub search (Step 3).

### Archon Code Examples

**Query: GRPO TRL GRPOTrainer reward function code generation**
- No relevant code examples found (returned diffusers LoRA/image generation snippets).
- All code patterns sourced from Exa GitHub (huggingface/trl official repository).

### Exa GitHub Implementations

**Query 1: TRL GRPOTrainer GRPO training LLM code generation execution reward**

**Repository 1**: huggingface/trl (⭐ 18K)
- **URL**: https://github.com/huggingface/trl
- **Relevance**: Official TRL library — GRPOTrainer and DPOTrainer implementations used directly
- **Key Code** (GRPOTrainer training loop):
  ```python
  from trl import GRPOConfig, GRPOTrainer
  from trl.rewards import accuracy_reward

  trainer = GRPOTrainer(
      model="deepseek-ai/deepseek-coder-7b-instruct-v1.5",
      reward_funcs=[execution_reward_binary, execution_reward_error_type],
      train_dataset=train_dataset,
      args=GRPOConfig(
          output_dir="grpo-deepseek-coder-7b",
          num_train_epochs=3,
          per_device_train_batch_size=4,
          gradient_accumulation_steps=4,
          learning_rate=1e-6,
          num_generations=8,  # group size G for GRPO
          logging_steps=10,
      ),
  )
  trainer.train()
  ```
- **KL tracking**: GRPOTrainer logs `kl` metric natively (KL from reference model per step)
- **Source**: https://github.com/huggingface/trl/blob/main/trl/trainer/grpo_trainer.py

**Repository 2**: huggingface/trl DPOTrainer
- **URL**: https://github.com/huggingface/trl/blob/main/trl/scripts/dpo.py
- **Key Code** (DPOTrainer):
  ```python
  from trl import DPOConfig, DPOTrainer
  from transformers import AutoModelForCausalLM

  model = AutoModelForCausalLM.from_pretrained(
      "deepseek-ai/deepseek-coder-7b-instruct-v1.5",
      dtype=torch.bfloat16
  )
  trainer = DPOTrainer(
      model=model,
      args=DPOConfig(
          output_dir="dpo-deepseek-coder-7b",
          per_device_train_batch_size=2,
          gradient_accumulation_steps=8,
          learning_rate=5e-7,
          num_train_epochs=1,
          beta=0.1,  # KL penalty coefficient
      ),
      train_dataset=preference_dataset,  # execution-oracle labeled pairs
  )
  trainer.train()
  ```
- **Source**: https://github.com/huggingface/trl/blob/main/docs/source/dpo_trainer.md

**Query 2: evalplus HumanEval+ MBPP+ evaluation code generation pass@1**

**Repository 3**: evalplus/evalplus (⭐ 2K)
- **URL**: https://github.com/evalplus/evalplus
- **Relevance**: Official evaluation harness for HumanEval+ and MBPP+ — standard for code LLM benchmarking
- **Key Usage**:
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus, write_jsonl

  # Generate solutions
  samples = [
      dict(task_id=task_id, solution=model.generate(problem["prompt"]))
      for task_id, problem in get_human_eval_plus().items()
  ]
  write_jsonl("samples.jsonl", samples)

  # Evaluate
  # evalplus.evaluate --dataset humaneval --samples samples.jsonl
  ```
- **Dataset sizes**: HumanEval+ = 164 problems (v0.1.10), MBPP+ = 378 problems (v0.2.0)
- **Source**: https://github.com/evalplus/evalplus

**Query 3: AST edit distance zss Python code semantic tree diff**

**Library 1**: zss (Zhang-Shasha tree edit distance)
- **URL**: https://zhang-shasha.readthedocs.io/en/latest/
- **Installation**: `pip install zss`
- **Usage**: `zss.distance(tree1, tree2, get_children, insert_cost, remove_cost, update_cost)`
- **Relevance**: Canonical Python implementation of Zhang-Shasha tree edit distance for AST comparison

**Library 2**: codist (AST edit distance)
- **URL**: https://pypi.org/project/codist/
- **Installation**: `pip install codist`
- **Relevance**: Purpose-built Python AST edit distance library, MIT license

**Paper**: "Revisiting Code Similarity Evaluation with Abstract Syntax Tree Edit Distance" (arXiv 2404.08817)
- **Finding**: AST editing distance highly correlates with established code similarity metrics; effective for capturing structural differences

**Serena Analysis Needed**: false (TRL API is well-documented; no complex custom architecture)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This experiment does NOT reproduce a paper — it implements a novel controlled comparison using:
1. **Official TRL library** (huggingface/trl, 18K stars) for both GRPOTrainer and DPOTrainer
2. **Official evalplus** for standardized benchmark evaluation
3. **zss library** for AST edit distance computation

**Recommended Implementation Path:**
- Primary: huggingface/trl v1.3.0+ — GRPOTrainer for GRPO conditions, DPOTrainer for DPO condition
- Fallback: Custom GRPO implementation if TRL version incompatible with DeepSeek-Coder-7B tokenizer
- Justification: TRL is the canonical, actively maintained library used by TÜLU 3, DeepSeekMath, and all major RLHF papers. Single codebase reduces implementation variance between GRPO and DPO conditions.

### Code Analysis (Serena MCP)

*Skipped* — Code from TRL official repository (Exa search results) is sufficiently clear. GRPOTrainer and DPOTrainer APIs are well-documented. No complex unfamiliar architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Primary Evaluation Datasets (standard type — real, established)**

| Dataset | Problems | Tests/Problem | Purpose |
|---------|----------|---------------|---------|
| HumanEval+ | 164 | 80x augmented | Primary function-level eval |
| MBPP+ | 378 | 35x augmented | Secondary function-level eval |
| LiveCodeBench | ~400+ | Competition problems | OOD contamination-free eval (H-M4) |

**Training Data:**
- **Prompt set**: CodeAlpaca-20K / OSS-Instruct prompts (code instruction following)
- **DPO pairs**: Generated via execution oracle (run → pass/fail → preference label)
- **GRPO prompts**: Same prompt set, rewards computed via code execution

**Synthetic Data Policy Check:** PASSED — All datasets are standard real benchmarks (evalplus NeurIPS 2023, LiveCodeBench).

**Dataset Statistics:**
- HumanEval+ v0.1.10: 164 problems, Python function completion
- MBPP+ v0.2.0: 378 problems (hand-verified subset of MBPP-sanitized)
- Total evaluation: 542 problems across both benchmarks

**Preprocessing:**
- Prompts formatted with DeepSeek-Coder instruct chat template
- Code sanitization via `evalplus.sanitize` (remove markdown fences, extract function body)
- No tokenization truncation for prompts <1024 tokens

**Loading Information** (for Phase 4 download):
- Method: pip package + HuggingFace datasets
- Identifier: `evalplus/humanevalplus` (HF), `evalplus/mbppplus` (HF)
- Code:
  ```python
  # Option 1: evalplus package (recommended)
  pip install evalplus
  from evalplus.data import get_human_eval_plus, get_mbpp_plus

  # Option 2: HuggingFace datasets
  from datasets import load_dataset
  humaneval_plus = load_dataset("evalplus/humanevalplus", split="test")
  mbpp_plus = load_dataset("evalplus/mbppplus", split="test")
  ```

### Models

#### Baseline Model

**Architecture**: DeepSeek-Coder-7B-instruct-v1.5
- Decoder-only transformer, code-specialized, 7B parameters
- Trained on 2T tokens (87% code, 13% natural language)
- Supports 16K context window
- Permissive license (MIT)

**Conditions in experiment:**
1. **SFT-only** (reference): DeepSeek-Coder-7B-instruct (no further training)
2. **SFT+DPO**: Fine-tuned with DPOTrainer on execution-oracle preference pairs
3. **SFT+GRPO-binary**: Fine-tuned with GRPOTrainer, binary pass/fail reward
4. **SFT+GRPO-error-type**: Fine-tuned with GRPOTrainer, error-type reward (distinguishes syntax/runtime/logic errors)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers AutoModelForCausalLM
- Identifier: `deepseek-ai/deepseek-coder-7b-instruct-v1.5`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  import torch

  model_id = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
  tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
  model = AutoModelForCausalLM.from_pretrained(
      model_id,
      torch_dtype=torch.bfloat16,
      device_map="auto",
      trust_remote_code=True,
  )
  ```

#### Proposed Model

**Architecture:** DeepSeek-Coder-7B-instruct-v1.5 + GRPO execution-feedback RL (binary and error-type reward variants)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Execution-Feedback Reward for GRPO
# Based on: huggingface/trl GRPOTrainer API (v1.3.0+)
# Source: https://github.com/huggingface/trl

import ast
import subprocess
from evalplus.data import get_human_eval_plus

def execution_reward_binary(completions, prompts, task_ids, **kwargs):
    """Binary execution reward: +1 if all tests pass, 0 otherwise."""
    rewards = []
    for completion, task_id in zip(completions, task_ids):
        try:
            result = run_evalplus_tests(task_id, completion)
            rewards.append(1.0 if result["passed"] else 0.0)
        except Exception:
            rewards.append(0.0)
    return rewards

def execution_reward_error_type(completions, prompts, task_ids, **kwargs):
    """Error-type reward: distinguishes syntax/runtime/logic errors."""
    rewards = []
    for completion, task_id in zip(completions, task_ids):
        result = run_evalplus_tests(task_id, completion)
        if result["passed"]:
            rewards.append(1.0)
        elif result["error_type"] == "syntax":
            rewards.append(-0.5)   # syntax errors: largest penalty
        elif result["error_type"] == "runtime":
            rewards.append(-0.2)   # runtime errors: medium penalty
        else:  # logic error (runs but fails tests)
            rewards.append(0.2)    # partial credit for executable code
    return rewards

def compute_kl_divergence(model, ref_model, prompts, tokenizer, n_samples=100):
    """Monte Carlo KL estimate: KL(π_θ || π_ref) on held-out prompt set."""
    log_ratios = []
    for prompt in prompts[:n_samples]:
        with torch.no_grad():
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            logp_model = model(**inputs).logits.log_softmax(-1)
            logp_ref = ref_model(**inputs).logits.log_softmax(-1)
            log_ratios.append((logp_model - logp_ref).mean().item())
    return float(torch.tensor(log_ratios).mean())

def compute_ast_semantic_edit_distance(code_a, code_b):
    """Semantic AST edit distance: control-flow + data-flow nodes only."""
    import zss
    tree_a = extract_semantic_ast(code_a)  # filter to CF+DF nodes
    tree_b = extract_semantic_ast(code_b)
    return zss.simple_distance(tree_a, tree_b)
```

### Training Protocol

**Optimizer**: AdamW
- Parameters: lr=1e-6, weight_decay=0.01, betas=(0.9, 0.999)
- **Source**: TRL GRPOConfig defaults; consistent with TÜLU 3 RLVR training

**Learning Rate**: 1e-6 (GRPO), 5e-7 (DPO)
- GRPO: 1e-6 (from TRL example scripts for 7B models)
- DPO: 5e-7 (from TRL DPO documentation for instruct models)
- **Source**: huggingface/trl documentation

**Schedule**: Cosine decay with warmup
- Warmup: 10% of total steps
- **Source**: TRL GRPOConfig defaults

**Batch Size**:
- GRPO: per_device_train_batch_size=4, gradient_accumulation_steps=4 → effective batch=16
- DPO: per_device_train_batch_size=2, gradient_accumulation_steps=8 → effective batch=16
- num_generations (GRPO group size G): 8
- **Source**: TRL example scripts; memory-constrained for 7B model on single GPU

**Training Steps**: 1000 steps (dense checkpoint every 100 steps for KL matching)

**Loss Function**:
- GRPO: Group Relative Policy Optimization objective with KL penalty (β=0.04)
- DPO: Direct Preference Optimization with β=0.1 (KL penalty coefficient)
- **Source**: TRL defaults; β values from TÜLU 3 and DeepSeekMath papers

**Checkpoint Strategy**: Save every 100 steps → 10 checkpoints per run for KL-matched comparison

**Seeds**: 1 (fixed seed=42)

> ⚠️ **EXISTENCE (PoC)**: Single run sufficient. No multi-seed specification.

**GPU**: Single GPU (select lowest-memory GPU via `nvidia-smi`), `CUDA_VISIBLE_DEVICES=<id>`

### Evaluation

**Primary Metrics:**

| Metric | Definition | Gate |
|--------|-----------|------|
| Semantic-edit-per-KL | AST semantic edit distance (CF+DF nodes) ÷ KL divergence, at KL-matched checkpoints (±5%) | ≥20% differential, 95% CI excludes zero |
| pass@1 (HumanEval+) | Fraction of 164 problems solved with greedy decoding | Secondary |
| pass@1 (MBPP+) | Fraction of 378 problems solved with greedy decoding | Secondary |

**KL Matching Protocol:**
1. Compute KL divergence at each checkpoint via Monte Carlo (100 held-out prompts, fixed set)
2. Match checkpoints across conditions within ±5% KL tolerance
3. Compute semantic-edit-per-KL at matched checkpoints

**AST Semantic Edit Distance Protocol:**
1. Parse model outputs at matched checkpoints with Python `ast` module
2. Filter AST to control-flow nodes (If, For, While, Try, With) and data-flow nodes (Assign, AugAssign, Call, Return)
3. Compute pairwise edit distance vs SFT-only baseline using `zss.simple_distance()`
4. Average across all 164 HumanEval+ problems

**Bootstrap CI:**
- Draw 10,000 bootstrap samples of (GRPO_efficiency - DPO_efficiency) across problems
- Report 95% CI; gate passes if CI excludes zero AND point estimate ≥20%

**Success Criteria:**
- proposed_metric > baseline_metric (execution-RL semantic-edit-per-KL > DPO semantic-edit-per-KL)
- Bootstrap 95% CI excludes zero
- Magnitude ≥20% (PoC threshold)

**Expected Baseline Performance** (from Phase 2B research):
- DeepSeek-Coder-7B-instruct SFT-only: ~45-50% HumanEval+ pass@1
- TÜLU 3 RLVR at 7B scale: ~60-65% HumanEval+ pass@1
- **Source**: Phase 2B roadmap Section 1.4; TÜLU 3 paper

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code_generation / pass@k
- Library: evalplus (primary), zss (AST edit distance), scipy.stats (bootstrap CI)
- Code:
  ```python
  # pass@1 evaluation
  # evalplus.evaluate --dataset humaneval --samples samples.jsonl --greedy

  # Bootstrap CI
  from scipy import stats
  import numpy as np
  diffs = grpo_efficiencies - dpo_efficiencies  # per-problem
  boot_ci = np.percentile(
      [np.mean(np.random.choice(diffs, len(diffs))) for _ in range(10000)],
      [2.5, 97.5]
  )
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — semantic-edit-per-KL for SFT-only, DPO, GRPO-binary, GRPO-error-type at matched KL checkpoints, with 95% bootstrap CI error bars

#### Additional Figures (LLM Autonomous)
- **KL trajectory plot**: KL divergence vs training steps for all 4 conditions (to show matching quality)
- **AST edit distance vs KL scatter**: Sanity check plot — positive correlation validates KL as proxy (per Phase 2B Assumption A1)
- **pass@1 vs training steps**: Learning curves for all conditions on HumanEval+

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (all 4 conditions complete training and evaluation)
2. `GRPO_semantic_edit_per_KL > DPO_semantic_edit_per_KL` (direction check)
3. Bootstrap 95% CI for (GRPO - DPO) excludes zero AND magnitude ≥20%

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Status**: No domain-relevant sources found in Archon KB (KB contains HuggingFace Diffusers content, not LLM alignment/code-gen domain).

**Queries executed:**
1. "GRPO DPO execution-feedback RL code generation experiment design" → 0 relevant results (similarity 0.39)
2. "AST edit distance KL divergence policy movement structural efficiency" → 0 relevant results (similarity 0.42)
3. "GRPO reinforcement learning LLM training TRL HumanEval code benchmark" → 0 relevant results (similarity 0.43)
4. Code examples: "GRPO TRL GRPOTrainer reward function code generation" → 0 relevant results

### B. GitHub Implementations (Exa)

**Repository 1**: huggingface/trl (⭐ 18,000)
- **URL**: https://github.com/huggingface/trl
- **Query Used**: "TRL GRPOTrainer GRPO training LLM code generation execution reward HuggingFace"
- **Relevance**: Official TRL library — authoritative implementation of both GRPO and DPO trainers
- **Key Findings**:
  - GRPOTrainer natively logs `kl` metric (KL from reference model)
  - Supports custom async reward functions (useful for code execution)
  - `num_generations` parameter controls group size G for GRPO
  - DPOTrainer with `beta` controls KL penalty strength
- **Used For**: Training protocol, pseudo-code design, hyperparameter selection

**Repository 2**: huggingface/trl GRPOConfig documentation
- **URL**: https://huggingface.co/docs/trl/main/en/grpo_trainer
- **Key Configs Extracted**:
  - `num_generations=8` (group size)
  - `learning_rate=1e-6`
  - `per_device_train_batch_size=4`
  - `gradient_accumulation_steps=4`
- **Used For**: Training protocol specification

**Repository 3**: evalplus/evalplus (⭐ 2,000)
- **URL**: https://github.com/evalplus/evalplus
- **Query Used**: "evalplus HumanEval+ MBPP+ evaluation code generation pass@1"
- **Relevance**: Official evaluation harness — standard for all code LLM papers
- **Key Findings**:
  - HumanEval+ v0.1.10: 164 problems
  - MBPP+ v0.2.0: 378 problems
  - Datasets on HuggingFace: `evalplus/humanevalplus`, `evalplus/mbppplus`
  - Docker-safe execution environment available
- **Used For**: Dataset specification, evaluation protocol

**Library 4**: zss (Zhang-Shasha tree edit distance)
- **URL**: https://zhang-shasha.readthedocs.io/en/latest/
- **Query Used**: "AST edit distance zss Python code semantic tree diff"
- **Relevance**: Canonical Python implementation of Zhang-Shasha algorithm for tree edit distance
- **Installation**: `pip install zss`
- **Used For**: AST semantic edit distance computation (core metric)

**Library 5**: codist (AST edit distance)
- **URL**: https://pypi.org/project/codist/
- **Relevance**: Purpose-built Python AST edit distance — alternative to zss
- **Used For**: Fallback if zss performance insufficient

**Paper**: "Revisiting Code Similarity Evaluation with AST Edit Distance" (arXiv:2404.08817)
- **URL**: https://huggingface.co/papers/2404.08817
- **Key Finding**: AST editing distance highly correlates with established code similarity metrics; effective for capturing structural code differences
- **Used For**: Validation of AST edit distance as meaningful proxy

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from TRL official repository (Exa search results) is sufficiently clear. GRPOTrainer and DPOTrainer APIs are well-documented with complete examples. No complex custom architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Previous Context**: None — H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (HumanEval+/MBPP+) | GitHub (Exa) | evalplus/evalplus (Repo B.3) |
| Dataset loading code | GitHub (Exa) | evalplus/evalplus README |
| Model (DeepSeek-Coder-7B) | Phase 2A/2B | 02b_verification_plan.md Section 1.3 |
| Model loading code | Web (Exa) | deepseek-ai/deepseek-coder-7b-instruct-v1.5 HF page |
| GRPO training | GitHub (Exa) | huggingface/trl (Repo B.1) |
| DPO training | GitHub (Exa) | huggingface/trl DPO docs (Repo B.2) |
| KL divergence tracking | GitHub (Exa) | TRL GRPOTrainer native logging |
| AST edit distance | Web (Exa) | zss library (Library B.4) |
| Bootstrap CI | Phase 2B | 02b_verification_plan.md Section 2.2 H-E1 |
| Training hyperparameters | GitHub (Exa) | TRL GRPOConfig docs (Repo B.2) |
| Success criteria (≥20%) | Phase 2B | 02b_verification_plan.md Section 3.2 |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md H-E1 verification protocol |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-19

### Workflow History for This Hypothesis
- Phase 2B completed: H-E1 defined as EXISTENCE hypothesis with MUST_WORK gate, no prerequisites
- Phase 2C started: experiment_design set to IN_PROGRESS
- Phase 2C completed: experiment_design set to COMPLETED (this run)

---

## Quality Validation

**Check 1: All Hyperparameters Justified?** ✅
- lr=1e-6 (GRPO): TRL example scripts for 7B instruct models
- lr=5e-7 (DPO): TRL DPO documentation
- beta=0.04 (GRPO KL): DeepSeekMath paper default
- beta=0.1 (DPO): TRL DPO documentation default
- num_generations=8: TRL GRPO example, memory-optimal for 7B

**Check 2: Dataset Choice Justified?** ✅
- HumanEval+/MBPP+: Phase 2A selection, canonical code LLM benchmarks (NeurIPS 2023)
- Standard type (not synthetic): real established datasets ✅

**Check 3: Mechanism Grounded in Code?** ✅
- Execution reward functions: based on TRL reward_funcs API (GRPOTrainer)
- KL computation: Monte Carlo estimation via log-probabilities (TRL native)
- AST edit distance: zss library (Zhang-Shasha algorithm)

**Check 4: No Unsupported Assumptions?** ✅
- All claims reference Phase 2B verification plan or Exa search findings

**Check 5: Full Traceability?** ✅
- Traceability matrix provided above

**Overall: PASSED**

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — no domain-relevant results), Exa (GitHub — primary source), Serena (skipped — TRL API sufficiently clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
