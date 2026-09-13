# Product Requirements Document: h-m1 Phase 1 Execution-Heavy Weight Validation

**Date:** 2026-07-12  
**Author:** Anonymous  
**Hypothesis:** h-m1 (MECHANISM)  
**Gate:** MUST_WORK  
**Project:** Deep Learning for Code

---

## Executive Summary

This PRD defines the requirements for implementing and validating h-m1: a mechanism hypothesis testing whether execution feedback weight is highest among three signals during Phase 1 training (0-30% progress) of a tri-modal reinforcement learning framework for code generation.

**Core Claim:** Under Phase 1 training conditions, if execution feedback weight is highest among three signals, then basic correctness (pass@1) improves fastest in early training, because functional code must be established before quality optimization can proceed.

**Implementation Approach:** Extend the validated h-e1 tri-modal RL framework with Phase 1 checkpoint monitoring and analysis capabilities. Reuse proven components while adding targeted weight trajectory logging and pass@1 improvement rate tracking.

**Success Metric:** Execution weight remains highest in Phase 1 (0-30%) AND pass@1 improvement rate in Phase 1 exceeds later phases.

---

## Problem Statement

### Research Question

Does the tri-modal RL framework exhibit execution-heavy weight scheduling in early training (Phase 1, 0-30% progress), and does this correlate with faster pass@1 improvement compared to later training phases?

### Hypothesis Context

- **Type:** MECHANISM hypothesis
- **Prerequisite:** h-e1 (EXISTENCE - validated, gate PASSED)
- **Position:** Tests specific phase behavior of h-e1's tri-modal framework
- **Gate Condition:** MUST_WORK - failure requires mechanism redesign

### Known from h-e1

✅ Tri-modal aggregator functional (dynamic Gaussian weight scheduling)  
✅ Weight trajectories verified (sum to 1.0 at all training points)  
✅ Dataset pipeline operational (HumanEval 164 + MBPP 874 = 1128 samples)  
✅ Model: CodeGen-350M-mono baseline validated  
✅ All feedback collectors working (execution, AI, human)  
✅ Real evaluation with code execution (no mocking)

---

## Functional Requirements

### FR1: Phase 1 Weight Monitoring System

**Priority:** P0 (Critical for h-m1 validation)

Implement checkpoint logging at 0%, 10%, 20%, 30% training progress to track tri-modal weight coefficients.

**Acceptance Criteria:**
- Checkpoints trigger at exact training progress milestones: 0.0, 0.1, 0.2, 0.3
- Log all three weights: execution_weight, ai_weight, human_weight
- Verify weights sum to 1.0 at each checkpoint (±1e-6 tolerance)
- Save checkpoint data to file for post-training analysis
- Display weight values to console during training

**Dependencies:**
- h-e1 `tri_modal_aggregator.py` (reuse base implementation)
- Training progress tracking from PPO trainer

---

### FR2: Pass@1 Trajectory Tracking

**Priority:** P0 (Core metric for h-m1)

Track pass@1 correctness scores throughout training to measure improvement rates across phases.

**Acceptance Criteria:**
- Evaluate pass@1 at minimum checkpoints: 0%, 10%, 20%, 30%, 70%, 100% training progress
- Use real code execution (reuse h-e1 evaluator)
- Test on validation split (113 samples)
- Save pass@1 trajectory to file
- Calculate improvement rates: Phase 1 (0-30%), Phase 2 (30-70%), Phase 3 (70-100%)

**Dependencies:**
- h-e1 `evaluation/evaluator.py` (reuse)
- h-e1 `data/dataset.py` validation split (reuse)

---

### FR3: Baseline Model - Pretrained CodeGen-350M

**Priority:** P0 (Required for controlled experiment)

Use Salesforce CodeGen-350M-mono as baseline model, identical to h-e1.

**Acceptance Criteria:**
- Load from HuggingFace: `Salesforce/codegen-350M-mono`
- Verify 350M parameters, 2048 context, 51200 vocab
- Initialize from pretrained checkpoint (no random init)
- Device: CUDA (5x H100 NVL available)
- Precision: FP16 for training

**Dependencies:**
- HuggingFace Transformers library
- CUDA-compatible environment

---

### FR4: Dataset - HumanEval + MBPP

**Priority:** P0 (Required for continuity with h-e1)

Reuse HumanEval (164) + MBPP (874) = 1128 samples with 80/10/10 split.

**Acceptance Criteria:**
- Load from HuggingFace: `evalplus/humanevalplus`, `google-research-datasets/mbpp`
- Apply h-e1 preprocessing: GPT-2 tokenizer, 512 max length
- Use h-e1 prompt template: `"# Problem: {prompt}\n# Solution:\n"`
- Extract and cache test cases for execution feedback
- Train: 902, Val: 113, Test: 113 samples

**Dependencies:**
- HuggingFace Datasets library
- h-e1 `data/dataset.py` (reuse)

---

### FR5: Tri-Modal Aggregator with Phase 1 Analysis

**Priority:** P0 (Core mechanism for h-m1)

Extend h-e1 tri-modal aggregator with Phase 1 checkpoint logging.

**Acceptance Criteria:**
- Reuse Gaussian weight curves from h-e1 validated implementation
- Add Phase 1 checkpoints: [0.0, 0.1, 0.2, 0.3]
- Log weight coefficients at checkpoints
- Maintain weight normalization (sum to 1.0)
- Support learnable weight parameters (execution_initial, ai_initial, human_initial, peak times)

**Dependencies:**
- h-e1 `models/tri_modal_aggregator.py` base class
- PyTorch nn.Module

**Implementation Note:**
```python
class Phase1AnalysisTriModalAggregator(TriModalAggregator):
    def __init__(self, config):
        super().__init__(config)
        self.phase1_checkpoints = [0.0, 0.1, 0.2, 0.3]
    
    def forward(self, exec_r, ai_r, human_r, progress):
        exec_w, ai_w, human_w = self.compute_weights(progress)
        if progress in self.phase1_checkpoints:
            log_checkpoint(progress, exec_w, ai_w, human_w)
        return exec_w * exec_r + ai_w * ai_r + human_w * human_r
```

---

### FR6: PPO Training with Tri-Modal Integration

**Priority:** P0 (Training system)

Reuse h-e1 PPO trainer with tri-modal reward aggregation and Phase 1 monitoring.

**Acceptance Criteria:**
- Optimizer: AdamW (lr=5e-6, betas=(0.9, 0.999), weight_decay=1e-4)
- Learning rate schedule: Linear warmup (10% steps) + linear decay
- Batch size: 8 (H100 memory optimized)
- Episodes: 10,000 PPO episodes (sufficient for 100% training progress)
- PPO hyperparameters: clip_range=0.2, value_loss_coef=0.5, entropy_coef=0.01
- Seed: 42 (reproducibility)
- Training progress tracking: current_episode / total_episodes

**Dependencies:**
- h-e1 `train/ppo_trainer.py` (reuse)
- Tri-modal aggregator (FR5)
- Feedback collectors (FR7)

---

### FR7: Feedback Collectors (Execution, AI, Human)

**Priority:** P0 (Required for tri-modal system)

Reuse h-e1 feedback collectors for three modalities.

**Acceptance Criteria:**
- **Execution feedback**: Run generated code against test cases, return pass/fail scores
- **AI feedback**: GPT-4-based reward model scoring code quality
- **Human feedback**: Simulated preference scores (h-e1 proven implementation)
- All collectors return normalized rewards in [-1, 1] range

**Dependencies:**
- h-e1 `models/feedback_collectors.py` (reuse)
- Code execution sandbox
- OpenAI API (for AI feedback)

---

### FR8: Real Code Execution Evaluator

**Priority:** P0 (Gate validation metric)

Reuse h-e1 evaluator for real code execution-based pass@1 measurement.

**Acceptance Criteria:**
- Execute generated code against test cases
- Timeout: 5 seconds per test
- Safety: Sandbox execution environment
- Return: pass@1 score (fraction of problems with ≥1 passing solution)
- No mock data - actual execution required

**Dependencies:**
- h-e1 `evaluation/evaluator.py` (reuse)
- Sandboxed execution environment

---

### FR9: Phase 1 Analysis Metrics

**Priority:** P0 (h-m1 specific validation)

Implement metrics to validate h-m1 hypothesis claims.

**Acceptance Criteria:**

**Metric 1: Weight Dominance**
- At each Phase 1 checkpoint (0%, 10%, 20%, 30%), verify: execution_weight > max(ai_weight, human_weight)
- Report: Binary PASS/FAIL per checkpoint

**Metric 2: Pass@1 Improvement Rate**
- Phase 1 rate: (pass@1_30% - pass@1_0%) / 0.3
- Later phases rate: (pass@1_100% - pass@1_30%) / 0.7
- Report: Rate comparison, PASS if Phase 1 > later phases

**Metric 3: Weight Correlation (Secondary)**
- Pearson correlation between execution_weight and training_progress in Phase 1
- Expected: ρ < -0.6 (execution weight decreases)
- Library: scipy.stats.pearsonr

**Dependencies:**
- Weight checkpoint data (FR1)
- Pass@1 trajectory data (FR2)
- scipy library

---

### FR10: Visualization Generation

**Priority:** P1 (Analysis support)

Generate publication-quality plots for h-m1 analysis.

**Acceptance Criteria:**

**Figure 1: Gate Metrics Bar Chart** (Mandatory)
- Three bars: Execution dominance, Pass@1 improvement ratio, Weight correlation
- Target vs actual values
- Save to: `h-m1/figures/gate_metrics.png`

**Figure 2: Weight Trajectory Plot**
- Line chart: Training progress (0-100%) vs weights
- Three lines: execution_weight, ai_weight, human_weight
- Highlight Phase 1 region (0-30%)
- Save to: `h-m1/figures/weight_trajectory.png`

**Figure 3: Pass@1 Trajectory**
- Line chart: Training progress vs pass@1
- Mark phases: Phase 1 (0-30%), Phase 2 (30-70%), Phase 3 (70-100%)
- Save to: `h-m1/figures/pass_at_1_trajectory.png`

**Figure 4: Phase Improvement Rates**
- Bar chart: Three bars (Phase 1, 2, 3 improvement rates)
- Save to: `h-m1/figures/phase_improvement_rates.png`

**Dependencies:**
- matplotlib, seaborn
- Checkpoint data (FR1, FR2)

---

## Non-Functional Requirements

### NFR1: Reproducibility

**Requirement:** Experiment must be exactly reproducible.

**Acceptance Criteria:**
- Fixed seed: 42 (all random operations)
- Deterministic CUDA operations: torch.backends.cudnn.deterministic=True
- Version pinning: PyTorch, transformers, datasets
- Save all hyperparameters to config file

---

### NFR2: Computational Efficiency

**Requirement:** Training completes within reasonable time on available hardware.

**Acceptance Criteria:**
- Target: <12 hours for 10k episodes on 5x H100 NVL
- FP16 precision for 2x speedup
- Batch size optimized for H100 memory (8 samples)
- Checkpoint saving: every 10% training progress

---

### NFR3: Code Quality

**Requirement:** Implementation follows h-e1 proven patterns.

**Acceptance Criteria:**
- Reuse h-e1 modules where possible (models/, data/, evaluation/)
- Type hints for all functions
- Docstrings for public APIs
- Unit tests for new checkpoint logging code
- Integration test: Full training run with 100 episodes (smoke test)

---

### NFR4: Observability

**Requirement:** Training progress and metrics visible during execution.

**Acceptance Criteria:**
- Console logging: epoch, loss, pass@1, weights
- Progress bar: tqdm for episodes
- WandB logging (optional): loss, pass@1, weights, learning rate
- Checkpoint files: saved every 10% progress with full model state

---

## Data Requirements

### Dataset 1: HumanEval

- **Source:** HuggingFace `evalplus/humanevalplus`
- **Size:** 164 programming problems
- **Format:** JSON with prompts and test cases
- **Preprocessing:** GPT-2 tokenization, 512 max tokens
- **Split:** 80/10/10 (train/val/test)

### Dataset 2: MBPP

- **Source:** HuggingFace `google-research-datasets/mbpp`
- **Size:** 874 samples (extended MBPP)
- **Format:** JSON with prompts and test cases
- **Preprocessing:** GPT-2 tokenization, 512 max tokens
- **Split:** 80/10/10 (train/val/test)

**Combined Total:** 1128 samples (902 train, 113 val, 113 test)

---

## Technical Dependencies

### Required Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| PyTorch | ≥2.0 | Deep learning framework |
| transformers | ≥4.30 | CodeGen model loading |
| datasets | ≥2.10 | HumanEval/MBPP loading |
| scipy | ≥1.10 | Pearson correlation |
| matplotlib | ≥3.7 | Visualization |
| seaborn | ≥0.12 | Publication-quality plots |
| tqdm | ≥4.65 | Progress bars |
| wandb | ≥0.15 (optional) | Experiment tracking |

### Computational Resources

- **GPU:** 5x NVIDIA H100 NVL (80GB each)
- **CUDA:** ≥11.8
- **Storage:** ~50GB (model checkpoints, datasets)
- **Memory:** 32GB RAM minimum

---

## Success Criteria

### Gate Validation (MUST_WORK)

**Primary Criteria (All Required):**

1. **Execution weight dominance in Phase 1**
   - execution_weight > max(ai_weight, human_weight) at ALL checkpoints [0%, 10%, 20%, 30%]
   - Threshold: Must hold for all 4 checkpoints

2. **Pass@1 improvement rate Phase 1 > Later**
   - Phase 1 rate: (pass@1_30% - pass@1_0%) / 0.3
   - Later rate: (pass@1_100% - pass@1_30%) / 0.7
   - Threshold: Phase 1 rate > Later rate

**Secondary Criteria (Supporting Evidence):**

3. **Weight correlation**
   - Pearson ρ(execution_weight, training_progress) < -0.6 in Phase 1
   - p-value < 0.05

**Gate Decision:**
- **PASS:** Primary criteria 1 AND 2 satisfied
- **FAIL:** Either primary criterion fails → MUST redesign mechanism

---

## Deliverables

### Code Deliverables

1. **Models**
   - `models/phase1_tri_modal_aggregator.py` - Extended aggregator with checkpoints
   - `models/feedback_collectors.py` - Reused from h-e1

2. **Training**
   - `train/ppo_trainer_phase1.py` - PPO with Phase 1 monitoring
   - `train/config.yaml` - All hyperparameters

3. **Data**
   - `data/dataset.py` - Reused from h-e1
   - `data/splits.json` - Train/val/test indices

4. **Evaluation**
   - `evaluation/evaluator.py` - Reused from h-e1
   - `evaluation/phase1_metrics.py` - h-m1 specific metrics

5. **Utilities**
   - `utils/checkpoint_logger.py` - Phase 1 checkpoint management
   - `utils/visualization.py` - Figure generation

6. **Main**
   - `run_h_m1_experiment.py` - Entry point
   - `requirements.txt` - Dependencies

### Data Deliverables

1. **Checkpoints**
   - `checkpoints/progress_0.0.pt` through `progress_1.0.pt`
   - Each contains: model state, optimizer state, weights, pass@1

2. **Logs**
   - `logs/training.log` - Console output
   - `logs/weights_phase1.csv` - Checkpoint data
   - `logs/pass_at_1_trajectory.csv` - Pass@1 over time

3. **Figures**
   - `figures/gate_metrics.png` (mandatory)
   - `figures/weight_trajectory.png`
   - `figures/pass_at_1_trajectory.png`
   - `figures/phase_improvement_rates.png`

### Validation Report

**File:** `04_validation.md`

**Required Sections:**
- Gate Metrics: execution dominance, pass@1 improvement, correlation
- Gate Decision: PASS/FAIL with justification
- Weight Trajectory: Analysis of Phase 1 behavior
- Comparison to h-e1: Any deviations from baseline
- Limitations: Known issues or caveats
- Next Steps: Implications for h-m2, h-m3

---

## Risks and Mitigation

### Risk 1: Phase 1 Too Short

**Risk:** 30% training progress insufficient to observe meaningful weight dynamics.

**Likelihood:** Low  
**Impact:** High (gate failure)

**Mitigation:**
- Monitor weight changes at finer granularity (5% intervals) if needed
- Extend training to 15k episodes if convergence slow
- Validate against h-e1 weight trajectory for comparison

---

### Risk 2: Pass@1 Improvement Noisy

**Risk:** Small sample size (113 val) causes high variance in pass@1 estimates.

**Likelihood:** Medium  
**Impact:** Medium (uncertain gate decision)

**Mitigation:**
- Use test split (113) for final gate decision
- Report 95% confidence intervals via bootstrap
- Run 3 seeds (42, 43, 44) and aggregate results

---

### Risk 3: Execution Weight Not Dominant

**Risk:** Weight scheduling learned differently than expected (h-m1 FAIL).

**Likelihood:** Medium  
**Impact:** High (requires mechanism redesign)

**Mitigation:**
- Acceptable outcome - hypothesis testing purpose
- If FAIL: Analyze why execution weight not dominant
- Inform h-m2, h-m3 design or trigger reflection to Phase 2A

---

## Timeline Estimate

**Note:** Research pipeline operates on "as long as it takes" principle. No hard deadlines.

**Rough Breakdown:**
- Data preparation: Reuse h-e1 (0 hours)
- Model setup: Reuse h-e1 (0 hours)
- Checkpoint logging: 2-4 hours implementation
- Training run: 8-12 hours compute
- Analysis & validation: 2-4 hours
- Report writing: 1-2 hours

**Total:** ~1-2 days elapsed (mostly compute)

---

## Appendix: Reuse from h-e1

The following components are proven and validated from h-e1 (gate PASSED):

**Data Pipeline** (100% reuse):
- `data/dataset.py` - HumanEval + MBPP loading
- Train/val/test splits (902/113/113)
- Preprocessing (GPT-2 tokenizer, 512 max)

**Model Architecture** (100% reuse):
- CodeGen-350M-mono baseline
- Tri-modal aggregator base class
- Feedback collectors (execution, AI, human)

**Training Infrastructure** (100% reuse):
- PPO trainer base
- AdamW optimizer configuration
- Learning rate schedule

**Evaluation** (100% reuse):
- Code execution evaluator
- Pass@1 metric implementation
- Sandbox environment

**Modifications for h-m1** (New):
- Phase 1 checkpoint logging (FR1)
- Pass@1 trajectory tracking (FR2)
- Phase 1 analysis metrics (FR9)
- Visualization (FR10)

---

**End of PRD**
