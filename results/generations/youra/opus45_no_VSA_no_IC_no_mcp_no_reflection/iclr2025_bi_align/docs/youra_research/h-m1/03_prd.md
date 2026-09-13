# Product Requirements Document: H-M1

**Hypothesis:** Combined reward R = α·R_AlpacaEval + β·R_IFEval_rate can be optimized via PPO without divergence or reward hacking

**Type:** MECHANISM | **Gate:** MUST_WORK | **Budget Tier:** FULL (30 tasks max)

---

## 1. Executive Summary

This PRD specifies implementation requirements for validating that PPO training with a combined multi-objective reward signal (helpfulness + controllability) converges stably without reward hacking. The experiment tests whether two potentially competing reward signals can be optimized simultaneously using standard RLHF infrastructure.

**Core Deliverable:** A working PPO training pipeline that combines AlpacaEval-based helpfulness rewards with IFEval constraint satisfaction rates, demonstrating stable convergence over 1000 training steps.

---

## 2. Problem Statement

Current RLHF approaches optimize single reward dimensions (typically helpfulness). Real-world deployment requires models that are both helpful AND controllable (follow user constraints). This experiment validates whether multi-objective reward optimization is feasible without training instability or reward hacking.

**Success = Both reward components improve without KL divergence exceeding safety thresholds.**

---

## 3. Functional Requirements

### FR-1: Combined Reward Model
- **FR-1.1:** Implement `CombinedRewardModel` wrapper integrating H-E1 `IFEvalRewardSignal`
- **FR-1.2:** Support configurable α/β weights (default: α=0.5, β=0.5)
- **FR-1.3:** Output scalar reward per sequence compatible with trl.PPOTrainer

### FR-2: PPO Training Pipeline
- **FR-2.1:** Configure trl.PPOTrainer with Meta-Llama-3-8B-Instruct base
- **FR-2.2:** Implement frozen reference model for KL divergence anchor
- **FR-2.3:** Support 1000 PPO training steps with checkpointing every 250 steps
- **FR-2.4:** Log separate reward components (R_helpfulness, R_IFEval) every 10 steps

### FR-3: Data Pipeline
- **FR-3.1:** Load UltraFeedback train split (~60k preference pairs)
- **FR-3.2:** Load IFEval with 70/30 train/test split (541 prompts)
- **FR-3.3:** Implement prompt sampling for PPO rollouts

### FR-4: Evaluation Pipeline
- **FR-4.1:** Checkpoint evaluation at steps 250, 500, 750, 1000
- **FR-4.2:** IFEval strict accuracy on held-out 30%
- **FR-4.3:** Reward hacking detection (compare training vs eval metrics)

### FR-5: Baseline Configurations
- **FR-5.1:** B1-SFT: No RL training (baseline reference)
- **FR-5.2:** B2-Helpfulness-Only: α=1.0, β=0.0 (single-objective)
- **FR-5.3:** T1-Combined: α=0.5, β=0.5 (this experiment)

### FR-6: Ablation Variants
- **FR-6.1:** α=0.7, β=0.3 (helpfulness-dominant)
- **FR-6.2:** α=0.3, β=0.7 (controllability-dominant)
- **FR-6.3:** Dynamic α/β scheduling (linear interpolation)

---

## 4. Non-Functional Requirements

### NFR-1: Training Stability
- KL divergence must stay < 5.0 throughout training
- No NaN/Inf in loss values
- Gradient norms within expected ranges

### NFR-2: Resource Constraints
- Single A100 80GB or 2× A6000 48GB
- Training time: ~4-6 hours for 1000 steps
- Disk: ~50GB for checkpoints + logs

### NFR-3: Reproducibility
- Fixed random seeds for all stochastic operations
- Complete hyperparameter logging via W&B or TensorBoard
- Checkpoint saving with full optimizer state

---

## 5. Success Criteria

### Primary (MUST_WORK Gate)
| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Convergence | Both R_helpfulness and R_IFEval show positive trend | Reward trajectory over 1000 steps |
| No Divergence | KL < 5.0 | Maximum KL observed during training |
| Stability | Zero NaN/Inf | Loss monitoring |

### Secondary (Informative)
| Criterion | Target | Notes |
|-----------|--------|-------|
| Reward Correlation | training ↔ eval r > 0.7 | Reward hacking detection |
| Both Signals Improve | Neither component degrades | Individual trajectory analysis |

---

## 6. Dependencies

### From H-E1 (Prerequisite - VALIDATED)
- `IFEvalRewardSignal` module for continuous [0,1] constraint satisfaction scores
- Verified gradient flow through sigmoid soft thresholds

### External Dependencies
- `trl>=0.8.0` (PPO Trainer)
- `transformers>=4.40.0` (Llama-3 support)
- `datasets` (HuggingFace data loading)
- Pre-trained helpfulness reward model (OpenAssistant/reward-model-deberta-v3 or equivalent)

---

## 7. Out of Scope

- Full AlpacaEval benchmark (use 100-sample spot-check only)
- Multi-GPU distributed training
- Hyperparameter sweeps beyond listed ablations
- Production deployment considerations

---

## 8. Failure Response Plan

| Failure Mode | Detection | Response |
|--------------|-----------|----------|
| KL > 10.0 | Training monitor | Reduce LR to 5e-6, increase KL coeff to 0.1 |
| NaN losses | Loss monitor | Gradient clipping, reduce LR |
| Reward hacking | Eval check | Add reward ensemble, reduce β |
| No convergence | Reward plateau | PIVOT to DPO/IPO alternatives |

---

**Next Step:** Architecture document specifying module structure and Epic-level tasks.
