# Product Requirements Document: h-e1 Binary Feedback Sufficiency

**Date:** 2026-08-19  
**Author:** Phase 3 Automated Pipeline  
**Hypothesis ID:** h-e1  
**Status:** Implementation Planning  

---

## Executive Summary

Implement RLVR training pipeline with binary execution feedback to validate dual-threshold sufficiency hypothesis for small code LLMs (350M-1B parameters). System must train three model variants (SFT baseline, Binary RLVR, Error-Type RLVR) and evaluate on HumanEval to verify:

1. Binary ≥8 pp absolute improvement over SFT
2. Binary ≥80% relative retention of error-type gains

**Gate:** MUST_WORK — failure refutes existence hypothesis and blocks all mechanistic investigations.

---

## Goals & Success Criteria

### Primary Goals

1. **Training Automation**: Reproducible RLVR training pipeline with binary/error-type reward computation
2. **Execution Sandbox**: Safe Python code execution with timeout protection and error capture
3. **Evaluation Pipeline**: HumanEval pass@1 metric computation with official evaluation harness
4. **Dual-Threshold Validation**: Automated success criteria checking for both absolute and retention thresholds

### Success Metrics

**EXISTENCE Gate Metrics:**
- Absolute improvement: `pass@1_binary - pass@1_sft ≥ 8.0 pp`
- Retention ratio: `(pass@1_binary - pass@1_sft) / (pass@1_error_type - pass@1_sft) ≥ 0.80`

**Secondary Metrics:**
- Training time per model variant (budget: <4 hours on single GPU)
- Reward convergence (binary reward mean ≥0.2 by step 500)
- Execution sandbox throughput (≥10 executions/second)

---

## User Requirements

### User Stories

**As a researcher validating H-E1, I need to:**

1. Train SFT baseline model on HumanEval prompts to establish baseline performance
2. Train RLVR model with binary rewards (1.0 all tests pass, 0.0 otherwise) to test minimal feedback sufficiency
3. Train RLVR model with error-type rewards (5-category classification) to establish upper bound
4. Execute generated code in sandboxed environment to compute rewards during training
5. Evaluate all three models on HumanEval test set with pass@1 metric
6. Generate comparison visualizations (training curves, reward distributions, gate metric bar chart)
7. Verify dual-threshold success criteria and update verification state

### Constraints

**Hardware:**
- Single GPU with 16GB VRAM (A100/V100/L4)
- LoRA + fp16 required for memory efficiency

**Time:**
- Total pipeline execution <12 hours
- Per-model training <4 hours

**Reproducibility:**
- Fixed random seed (seed=42)
- Pinned library versions (transformers, trl, datasets, torch)

**Safety:**
- Code execution must use timeout (3 seconds)
- No network access during code execution
- Isolated execution environment per sample

---

## Functional Requirements

### FR-1: Dataset Management

**Priority:** P0  
**Description:** Load and preprocess HumanEval dataset for training and evaluation

**Requirements:**
- Load from `openai/openai_humaneval` HuggingFace dataset
- Parse 164 test problems with fields: task_id, prompt, canonical_solution, test, entry_point
- Prepare training prompts (function signature + docstring)
- Prepare evaluation test suites (unit tests per problem)

**Acceptance Criteria:**
- Dataset loads without errors
- All 164 problems accessible
- Prompt format matches model input requirements (no truncation)

---

### FR-2: Baseline Model Setup

**Priority:** P0  
**Description:** Load and configure pretrained baseline model for SFT and RLVR training

**Requirements:**
- Load CodeGen-350M-mono OR StarCoderBase-1B from HuggingFace Hub
- Configure LoRA adapters (r=16, alpha=32, target_modules=[q_proj, v_proj])
- Initialize tokenizer with padding configuration
- Prepare reference model (frozen copy for KL penalty)

**Acceptance Criteria:**
- Model loads in fp16/bf16 precision
- LoRA adapters initialized correctly
- Memory footprint <14GB (fits 16GB VRAM)
- Reference model frozen (no gradient updates)

---

### FR-3: Execution Sandbox

**Priority:** P0  
**Description:** Safe Python code execution for reward computation during training

**Requirements:**
- Execute `generated_code + test_cases` in isolated environment
- Timeout protection (3 seconds per execution)
- Capture execution results: pass/fail + error types
- Return binary reward (1.0 pass, 0.0 fail)
- Return error-type reward (5-category classification: SyntaxError=0.0, TypeError=0.2, NameError=0.4, ValueError=0.6, AssertionError=0.8, Pass=1.0)

**Acceptance Criteria:**
- Timeout enforced (no infinite loops)
- Error types correctly classified
- Throughput ≥10 executions/second
- No sandbox escapes or network access

**Implementation Note:**
```python
def compute_binary_reward(code, test_cases, entry_point):
    program = code + "\n" + test_cases + f"\ncheck({entry_point})"
    try:
        with timeout(3.0):
            exec(program, {})
        return 1.0
    except:
        return 0.0

def compute_error_type_reward(code, test_cases, entry_point):
    program = code + "\n" + test_cases + f"\ncheck({entry_point})"
    try:
        with timeout(3.0):
            exec(program, {})
        return 1.0  # Pass
    except SyntaxError:
        return 0.0
    except TypeError:
        return 0.2
    except NameError:
        return 0.4
    except ValueError:
        return 0.6
    except AssertionError:
        return 0.8
    except:
        return 0.0  # Other errors
```

---

### FR-4: SFT Baseline Training

**Priority:** P0  
**Description:** Supervised fine-tuning on HumanEval canonical solutions as baseline

**Requirements:**
- Train on (prompt, canonical_solution) pairs from HumanEval
- Use causal LM loss (teacher forcing)
- AdamW optimizer, lr=2e-5
- 3-5 epochs or until convergence
- Batch size 8 with gradient accumulation
- Save checkpoint for evaluation

**Acceptance Criteria:**
- Training completes without errors
- Loss decreases monotonically
- Checkpoint saved with tokenizer config
- Training time <2 hours on single GPU

---

### FR-5: RLVR Binary Training

**Priority:** P0  
**Description:** Group Relative Policy Optimization with binary execution rewards

**Requirements:**
- Initialize from SFT checkpoint
- GRPO framework (TRL library)
- Binary reward function (FR-3)
- Sample 4 completions per problem
- Compute group advantages: (rewards - mean) / std
- Policy gradient loss + KL penalty (coef=0.1)
- AdamW optimizer, lr=2e-7
- Train for 500-1000 steps
- Save checkpoint for evaluation

**Acceptance Criteria:**
- Mean binary reward ≥0.2 by step 500
- KL divergence <1.0 (not too far from SFT)
- Checkpoint saved with LoRA weights
- Training time <4 hours on single GPU

---

### FR-6: RLVR Error-Type Training

**Priority:** P0  
**Description:** GRPO training with 5-category error-type rewards (upper bound condition)

**Requirements:**
- Initialize from SFT checkpoint (same as FR-5)
- GRPO framework with error-type reward function
- 5-category rewards: SyntaxError=0.0, TypeError=0.2, NameError=0.4, ValueError=0.6, AssertionError=0.8, Pass=1.0
- Same GRPO hyperparameters as FR-5
- Train for 500-1000 steps
- Save checkpoint for evaluation

**Acceptance Criteria:**
- Mean error-type reward ≥0.25 by step 500
- Reward distribution spans all 5 categories
- Checkpoint saved with LoRA weights
- Training time <4 hours on single GPU

---

### FR-7: HumanEval Evaluation

**Priority:** P0  
**Description:** Compute pass@1 metric for all three model variants using official harness

**Requirements:**
- Load checkpoints (SFT, Binary, Error-Type)
- Generate 1 completion per problem (greedy decoding, temp=0)
- Execute completions with test suites
- Use `evaluate_functional_correctness` from openai/human-eval
- Output pass@1 for each model variant

**Acceptance Criteria:**
- All 164 problems evaluated
- Results saved to JSON with per-problem pass/fail
- Pass@1 computed correctly (# passed / 164)
- SFT baseline pass@1 >0 (sanity check)

---

### FR-8: Gate Validation

**Priority:** P0  
**Description:** Automated dual-threshold success criteria checking

**Requirements:**
- Load evaluation results (SFT, Binary, Error-Type pass@1)
- Compute absolute improvement: `pass@1_binary - pass@1_sft`
- Compute retention ratio: `(pass@1_binary - pass@1_sft) / (pass@1_error_type - pass@1_sft)`
- Check threshold 1: absolute ≥8.0
- Check threshold 2: retention ≥0.80
- Output gate status: PASS (both met) or FAIL (one or both failed)
- Update verification_state.yaml with results

**Acceptance Criteria:**
- Correct arithmetic for both metrics
- Gate status correctly determined
- verification_state.yaml updated with final gate decision

---

### FR-9: Visualization

**Priority:** P1 (mandatory gate figure + autonomous extras)  
**Description:** Generate figures for validation report

**Mandatory Figure:**
- Gate metrics comparison bar chart (absolute improvement, retention ratio vs thresholds)

**Autonomous Recommendations:**
- Training curves (pass@1 vs steps for all three models)
- Reward distribution histograms (binary/error-type)
- Error type breakdown (proportion of each error category)
- Retention scatter plot (error-type gain vs binary gain per problem)

**Acceptance Criteria:**
- Gate figure saves to `h-e1/figures/gate_metrics.png`
- Additional figures save to `h-e1/figures/` with descriptive names
- All figures use consistent style (resolution ≥300 DPI, readable fonts)

---

### FR-10: Automation & Orchestration

**Priority:** P0  
**Description:** End-to-end pipeline execution with progress logging

**Requirements:**
- Single entry point script: `python run_experiment.py --hypothesis h-e1`
- Sequential execution: Dataset setup → SFT → Binary RLVR → Error-Type RLVR → Evaluation → Validation
- Progress logging to console and log file
- Error handling with informative messages
- Checkpoint resumption (skip completed stages)

**Acceptance Criteria:**
- Pipeline runs end-to-end without manual intervention
- Logs capture all training metrics and evaluation results
- Crashes produce actionable error messages
- Resumption works after interruption

---

## Non-Functional Requirements

### NFR-1: Performance

**Targets:**
- Total pipeline runtime <12 hours
- Per-model training <4 hours
- Execution sandbox throughput ≥10 exec/sec
- Memory footprint <14GB VRAM

### NFR-2: Reliability

**Requirements:**
- Deterministic results with fixed seed
- Crash recovery with checkpoint resumption
- Sandbox isolation prevents code escapes
- Timeout protection for infinite loops

### NFR-3: Maintainability

**Requirements:**
- Modular code structure (dataset, model, training, eval modules)
- Configuration file for hyperparameters (YAML/JSON)
- Docstrings for all public functions
- Logging at INFO level for key events

### NFR-4: Reproducibility

**Requirements:**
- Requirements.txt with pinned versions
- Fixed random seed (42) across numpy, torch, transformers
- Deterministic execution order (no async randomness)
- Save all hyperparameters to experiment config file

---

## System Architecture

### Components

1. **Dataset Loader** (`dataset.py`)
   - HuggingFace datasets integration
   - HumanEval preprocessing

2. **Model Manager** (`model.py`)
   - Pretrained model loading
   - LoRA configuration
   - Reference model freezing

3. **Execution Sandbox** (`sandbox.py`)
   - Reward computation (binary + error-type)
   - Timeout enforcement
   - Error classification

4. **Training Engine** (`train.py`)
   - SFT trainer (HuggingFace Trainer)
   - GRPO trainer (TRL PPOTrainer)
   - Checkpoint management

5. **Evaluation Pipeline** (`eval.py`)
   - Generation with greedy decoding
   - HumanEval harness integration
   - Metrics computation

6. **Validation Reporter** (`validate.py`)
   - Gate threshold checking
   - visualization generation
   - State file updates

7. **Orchestrator** (`run_experiment.py`)
   - End-to-end pipeline coordination
   - Progress logging
   - Error handling

### Data Flow

```
HumanEval Dataset
    ↓
[Dataset Loader] → Training Prompts → [SFT Trainer] → SFT Checkpoint
                                           ↓
                                      Reference Model (frozen)
                                           ↓
Training Prompts → [GRPO Binary] → Execution Sandbox (binary reward) → Binary Checkpoint
                         ↓
Training Prompts → [GRPO Error-Type] → Execution Sandbox (error-type reward) → Error-Type Checkpoint
                         ↓
[Evaluation Pipeline] ← All Checkpoints → HumanEval pass@1 results
    ↓
[Validation Reporter] → Gate status + Figures → verification_state.yaml update
```

---

## Dependencies

### Required Libraries

```
transformers>=4.45.0
trl>=0.24.0
datasets>=3.0.0
torch>=2.4.0
accelerate>=1.0.0
peft>=0.8.0  # LoRA
human-eval  # git+https://github.com/openai/human-eval
matplotlib>=3.8.0
numpy>=1.26.0
pyyaml>=6.0
```

### Hardware

- NVIDIA GPU with 16GB VRAM (A100, V100, L4)
- CUDA 11.8+
- 50GB disk space (models + checkpoints)

### External Resources

- HuggingFace Hub access (for pretrained models)
- Internet connection for initial downloads
- No external APIs required during training/evaluation

---

## Risks & Mitigations

### Risk 1: Memory Overflow

**Impact:** High (training crashes)  
**Probability:** Medium  
**Mitigation:**
- Use LoRA (reduces trainable params by 100x)
- Enable fp16/bf16 mixed precision
- Gradient checkpointing if needed
- Reduce batch size to 4 if 8 fails

### Risk 2: Sandbox Escapes

**Impact:** High (security vulnerability)  
**Probability:** Low  
**Mitigation:**
- Use `signal.alarm` timeout (not `threading.Timer`)
- No file I/O allowed in execution context
- Restrict globals to empty dict
- Catch all exception types

### Risk 3: Low Baseline Performance

**Impact:** Medium (hard to achieve 8pp improvement)  
**Probability:** Medium  
**Mitigation:**
- Use stronger SFT baseline (more epochs if pass@1 <5%)
- Increase RLVR training steps to 1000 if 500 insufficient
- Switch to StarCoderBase-1B if CodeGen-350M too weak

### Risk 4: Reward Degeneration

**Impact:** Medium (policy collapse to trivial solutions)  
**Probability:** Medium  
**Mitigation:**
- KL penalty coefficient 0.1 prevents excessive divergence
- Monitor KL divergence during training (<1.0 threshold)
- Early stopping if mean reward decreases for 100 steps

---

## Open Questions

1. **Model Selection:** CodeGen-350M vs StarCoderBase-1B?  
   → **Decision:** Start with CodeGen-350M (faster training), fallback to StarCoder if baseline <5% pass@1

2. **Training Steps:** 500 vs 1000?  
   → **Decision:** Start with 500, extend to 1000 if reward still improving

3. **Error-Type Categories:** 5 categories sufficient?  
   → **Decision:** Yes, covers 90% of HumanEval failures based on LETI paper analysis

4. **Evaluation Samples:** pass@1 only or also pass@10?  
   → **Decision:** pass@1 only (hypothesis specifies pass@1)

---

## Appendices

### Appendix A: Hyperparameters Summary

| Parameter | SFT | Binary RLVR | Error-Type RLVR |
|-----------|-----|-------------|-----------------|
| Optimizer | AdamW | AdamW | AdamW |
| Learning Rate | 2e-5 | 2e-7 | 2e-7 |
| Batch Size | 8 | 4 problems × 4 samples | 4 problems × 4 samples |
| Epochs/Steps | 3-5 epochs | 500-1000 steps | 500-1000 steps |
| KL Coefficient | N/A | 0.1 | 0.1 |
| LoRA r/alpha | 16/32 | 16/32 | 16/32 |
| Precision | fp16 | fp16 | fp16 |
| Seed | 42 | 42 | 42 |

### Appendix B: File Structure

```
h-e1/
├── 01_research_data.md
├── 02a_hypothesis.md
├── 02b_context.md
├── 02c_experiment_brief.md
├── 03_prd.md (this file)
├── 03_architecture.md (next)
├── 03_logic.md (next)
├── 03_config.md (next)
├── 03_tasks.yaml (next)
├── code/
│   ├── run_experiment.py
│   ├── dataset.py
│   ├── model.py
│   ├── sandbox.py
│   ├── train.py
│   ├── eval.py
│   ├── validate.py
│   └── config.yaml
├── figures/
│   ├── gate_metrics.png
│   ├── training_curves.png
│   ├── reward_distribution.png
│   └── error_breakdown.png
└── 04_validation.md (output)
```

### Appendix C: Experiment Brief Reference

**Source:** `02c_experiment_brief.md`  
**Key Sections Used:**
- Dataset specification (lines 143-163)
- Model selection (lines 170-197)
- Training protocol (lines 267-292)
- Evaluation metrics (lines 296-322)
- Success criteria (lines 301-302)

---

**Document Version:** 1.0  
**Next Steps:** Generate 03_architecture.md, 03_logic.md, 03_config.md via specialized agents
