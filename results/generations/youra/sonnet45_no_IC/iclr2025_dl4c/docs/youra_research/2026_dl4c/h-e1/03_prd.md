# Product Requirements Document (PRD)
# h-e1: Tri-Modal RL Framework for Code Generation

---
metadata:
  hypothesis_id: h-e1
  hypothesis_type: EXISTENCE
  gate: MUST_WORK
  created_at: 2026-07-12
  author: Anonymous
  phase: Phase 3 - Implementation Planning
  source: Phase 2C Experiment Brief (02c_experiment_brief.md)
---

## Executive Summary

### Purpose
Implement and validate a tri-modal reinforcement learning framework that combines execution, human, and AI feedback with dynamic weight scheduling for code generation tasks.

### Hypothesis Statement
Under training conditions with access to execution, human, and AI feedback, if we apply tri-modal RL framework with dynamic weight scheduling across three phases, then we achieve ≥3% absolute improvement in harmonic mean of pass@1 and human preference scores vs. best single-feedback baseline, because sequential capability building requires phase-appropriate feedback emphasis.

### Success Criteria
- **Primary Metric**: Harmonic mean of pass@1 and human preference > 0.515 (≥3% improvement over best baseline ~0.50)
- **PoC Validation**: Code runs without error and shows positive improvement direction
- **Gate**: MUST_WORK - Implementation must demonstrate the tri-modal mechanism works

### Scope
- **In Scope**: 
  - PPO-based RL training with 1.5B parameter code LLM
  - Tri-modal reward aggregation (execution + AI + human feedback)
  - Dynamic weight scheduling across 3 training phases
  - Evaluation on HumanEval + MBPP combined dataset (664 problems)
  - Three single-feedback baselines for comparison
  
- **Out of Scope**:
  - Multi-run statistical validation (single seed=42 for PoC)
  - Hyperparameter grid search
  - Datasets beyond HumanEval + MBPP
  - Model architectures other than CodeGen-1.5B

---

## Problem Statement

### Background
Current code generation RL methods use single feedback sources (execution-only, human-only, or AI-only), each with limitations:
- **Execution feedback**: Ensures correctness but doesn't improve code quality
- **Human feedback**: Improves quality but limited by annotation cost  
- **AI feedback**: Scalable but may have systematic biases

### Research Gap
No existing work systematically integrates all three feedback modalities with dynamic weighting across training phases to balance correctness, quality, and scalability.

### Proposed Solution
Tri-modal RL framework with:
1. **Multi-signal aggregation**: Weighted combination of execution, AI, and human rewards
2. **Dynamic scheduling**: Phase-appropriate emphasis (execution → AI → human) across training
3. **Curriculum learning**: Sequential capability building over three phases

---

## Functional Requirements

### FR-1: Dataset Preparation
**Priority**: P0 (Critical)  
**Description**: Load, preprocess, and split HumanEval + MBPP datasets for training, validation, and testing.

**Acceptance Criteria**:
- Load HumanEval (164 problems) and MBPP (500 problems) from HuggingFace
- Combine into 664 total problems
- Split: 80% train (531), 10% val (66), 10% test (67)
- Tokenize with code-specific BPE tokenizer (max 512 tokens)
- Extract test case input/output pairs for execution feedback

**Dependencies**: None

---

### FR-2: Baseline Model - Execution-Only RL
**Priority**: P0 (Critical)  
**Description**: Implement PPO training with execution feedback only (test case pass/fail).

**Acceptance Criteria**:
- Load pre-trained CodeGen-1.5B or StarCoder-1.5B model
- Implement PPO with standard hyperparameters (clip=0.2, lr=5e-5)
- Reward signal: Binary pass/fail from test execution
- Train for 10,000 steps
- Evaluate on test set: pass@1, human preference, harmonic mean

**Dependencies**: FR-1

**Expected Performance**: pass@1 ≈ 0.45, preference ≈ 0.5, harmonic ≈ 0.47

---

### FR-3: Baseline Model - Human-Only RL
**Priority**: P0 (Critical)  
**Description**: Implement PPO training with human preference feedback only.

**Acceptance Criteria**:
- Same base model and PPO config as FR-2
- Reward signal: Human quality preference scores [0,1]
- Annotation: 500 samples, 3 annotators per sample, majority vote
- Blind evaluation protocol
- Train for 10,000 steps
- Evaluate on test set: pass@1, human preference, harmonic mean

**Dependencies**: FR-1

**Expected Performance**: pass@1 ≈ 0.35, preference ≈ 0.7, harmonic ≈ 0.47

---

### FR-4: Baseline Model - AI-Only RL
**Priority**: P0 (Critical)  
**Description**: Implement PPO training with learned AI reward model feedback only.

**Acceptance Criteria**:
- Train reward model on combined execution + human annotation data
- Use reward model predictions as PPO reward signal
- Same base model and PPO config as FR-2, FR-3
- Train for 10,000 steps
- Evaluate on test set: pass@1, human preference, harmonic mean

**Dependencies**: FR-1, FR-3 (requires human annotations for reward model training)

**Expected Performance**: pass@1 ≈ 0.40, preference ≈ 0.65, harmonic ≈ 0.50

---

### FR-5: Tri-Modal Reward Aggregator
**Priority**: P0 (Critical)  
**Description**: Implement dynamic reward aggregation module combining execution, AI, and human feedback.

**Acceptance Criteria**:
- PyTorch nn.Module with learnable weight schedule parameters
- Input: execution_reward (B,), ai_reward (B,), human_reward (B,), training_progress [0,1]
- Output: aggregated_reward (B,)
- Dynamic phase-based weighting:
  - Phase 1 (0-30%): execution dominant
  - Phase 2 (30-70%): AI dominant
  - Phase 3 (70-100%): human dominant
- Gaussian-like weight curves centered at peak_timesteps
- Percentile normalization for reward alignment
- Weights sum to 1 at each timestep

**Dependencies**: None (core mechanism)

**Implementation Reference**: See 02c_experiment_brief.md Section "Proposed Model" for pseudo-code

---

### FR-6: Tri-Modal PPO Training
**Priority**: P0 (Critical)  
**Description**: Integrate tri-modal aggregator into PPO training loop.

**Acceptance Criteria**:
- Replace single reward signal with tri-modal aggregator output
- Collect all three feedback signals per generated code sample:
  - Execution: Run test cases, compute pass rate
  - AI: Query learned reward model
  - Human: Use cached annotations or request new ones
- Track per-signal rewards for analysis
- Train for 10,000 steps with same PPO config as baselines
- Log weight schedule trajectory

**Dependencies**: FR-2, FR-3, FR-4, FR-5

---

### FR-7: Evaluation Protocol
**Priority**: P0 (Critical)  
**Description**: Implement standardized evaluation on held-out test set.

**Acceptance Criteria**:
- Test set: 67 problems (10% of combined dataset)
- Metrics:
  - **Pass@1**: Percentage of code passing all test cases on first attempt
  - **Human Preference**: Average quality rating [0,1] from 3 annotators
  - **Harmonic Mean**: 2 * (pass@1 * pref) / (pass@1 + pref)
- Blind evaluation: Annotators don't know model identity
- Run evaluation for all 5 models (3 baselines + tri-modal + ablation if applicable)

**Dependencies**: All training FRs (FR-2, FR-3, FR-4, FR-6)

---

### FR-8: Visualization Generation
**Priority**: P1 (High)  
**Description**: Generate experiment analysis figures.

**Acceptance Criteria**:
- **Figure 1**: Weight trajectory plot (3 lines: execution, AI, human weights over training progress)
- **Figure 2**: Per-signal reward trends (exec_reward, ai_reward, human_reward over steps)
- **Figure 3**: Baseline comparison bar chart (pass@1, preference, harmonic for 5 models)
- **Figure 4**: Training curves (loss, reward, KL divergence over steps)
- **Figure 5**: Gate metrics comparison (target vs actual harmonic mean)
- All figures saved to `{hypothesis_folder}/figures/` directory
- Publication-quality formatting (readable labels, legend, axes)

**Dependencies**: FR-7 (requires evaluation results)

---

### FR-9: Human Annotation Interface
**Priority**: P1 (High)  
**Description**: Collect human preference annotations for generated code.

**Acceptance Criteria**:
- Web-based annotation interface (simple Flask app or Jupyter widget)
- Display: Problem description + Generated code
- Input: Quality rating [0-5] scale → normalized to [0,1]
- Support: 3 annotators per sample
- Export: JSON file with {sample_id, code, annotator_id, rating, timestamp}
- Target: 500 training samples annotated

**Dependencies**: FR-1 (requires generated code samples)

---

## Non-Functional Requirements

### NFR-1: Performance
- **Training Time**: ≤48 hours on single A100 GPU for 10,000 steps
- **Inference Latency**: ≤2 seconds per code generation sample
- **Memory**: Fit 1.5B model + PPO buffers in 40GB GPU memory with gradient checkpointing

### NFR-2: Reproducibility
- Fixed random seed (42) for deterministic PoC results
- Log all hyperparameters to config file
- Save model checkpoints every 1000 steps
- Version control all code with git

### NFR-3: Code Quality
- Type hints for all Python functions
- Docstrings for public APIs
- Unit tests for reward aggregator module
- Integration test for full training loop

### NFR-4: Monitoring
- Log training metrics every 10 steps (loss, reward, KL divergence)
- Track per-signal rewards separately
- Save weight schedule trajectory for analysis
- Real-time Tensorboard visualization

---

## Data Specifications

### Input Data

| Dataset | Source | Size | Format | Purpose |
|---------|--------|------|--------|---------|
| HumanEval | `openai/humaneval` (HF) | 164 problems | JSON | Code generation eval |
| MBPP | `google-research/mbpp` (HF) | 500 problems | JSON | Code generation training |
| Human Annotations | Manual collection | 500 samples | JSON | Preference training |

### Output Data

| Artifact | Path | Format | Description |
|----------|------|--------|-------------|
| PRD | `03_prd.md` | Markdown | This document |
| Trained Models | `models/` | PyTorch .pt | 4 checkpoints (3 baselines + tri-modal) |
| Evaluation Results | `results/eval_metrics.json` | JSON | Pass@1, preference, harmonic for all models |
| Figures | `figures/*.png` | PNG | 5 visualization figures |
| Training Logs | `logs/` | Tensorboard | Loss, reward, KL curves |

---

## Dependencies & Constraints

### Technical Dependencies
- **Python**: 3.9+
- **PyTorch**: 2.0+
- **Transformers**: 4.30+ (HuggingFace)
- **Datasets**: 2.12+ (HuggingFace)
- **TRL**: 0.4+ (Transformer RL library for PPO)
- **Hardware**: 1× A100 GPU (40GB) minimum

### External Services
- HuggingFace Hub (model and dataset downloads)
- Human annotation platform (500 samples, 3 annotators)

### Constraints
- **Budget**: LIGHT tier (≤15 tasks for EXISTENCE hypothesis)
- **Timeline**: Single PoC run (no multi-seed validation)
- **Scope**: Direction validation only (not statistical significance)

---

## Success Metrics & Validation

### Primary Success Metric
**Harmonic Mean Improvement**:
- Target: ≥ 0.515 (≥3% over best baseline ~0.50)
- Measurement: `2 * (pass@1 * human_pref) / (pass@1 + human_pref)` on test set
- Comparison: Tri-modal vs. max(execution-only, human-only, AI-only baselines)

### PoC Pass Criteria
1. ✅ Code runs without error through full training loop
2. ✅ Tri-modal model shows `harmonic_mean_trimodal > harmonic_mean_best_baseline`

### Gate Validation (MUST_WORK)
- If PoC passes → Proceed to dependent hypotheses (H-M1, H-M2, H-M3)
- If PoC fails → ABANDON approach, route to Phase 0 for new research question

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Human annotation cost/time | High | High | Start with 100 samples, expand if budget allows |
| Reward model training instability | Medium | Medium | Use standard RLHF techniques from InstructGPT |
| Weight schedule not optimal | Medium | Low | Learnable parameters allow adaptation |
| Single-seed variance | High | Low | Accept for PoC; flag in limitations |

---

## Appendix

### A. Glossary
- **PPO**: Proximal Policy Optimization (RL algorithm)
- **Pass@1**: Percentage of code passing all tests on first generation
- **Harmonic Mean**: Balanced metric combining correctness and quality
- **PoC**: Proof of Concept (direction validation, not statistical)

### B. References
- Phase 2C Experiment Brief: `02c_experiment_brief.md`
- PPOCoder: Shojaee et al., 2023
- InstructGPT: OpenAI RLHF paradigm
- Themis: Paul et al., 2026 (multi-criteria reward models)

### C. Traceability
All functional requirements trace to specifications in Phase 2C experiment brief:
- Dataset (HumanEval + MBPP): Section "Dataset"
- Model architecture (1.5B): Section "Models - Baseline Model"
- Tri-modal mechanism: Section "Proposed Model"
- Evaluation metrics: Section "Evaluation"
- Training protocol: Section "Training Protocol"

---

**Document Status**: ✅ COMPLETED  
**Next Phase**: Step 3 - Architecture Design (Agent-based)  
**Output Path**: `/workspace/TEST_dl4c/docs/youra_research/h-e1/03_prd.md`
