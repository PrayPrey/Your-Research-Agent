# Product Requirements Document: h-m2 Phase 2 AI Feedback Peak Validation

**Date:** 2026-07-12  
**Author:** Anonymous  
**Hypothesis:** h-m2 (MECHANISM)  
**Gate:** SHOULD_WORK  
**Project:** Deep Learning for Code

---

## Executive Summary

This PRD defines the requirements for implementing and validating h-m2: a mechanism hypothesis testing whether AI feedback weight peaks (highest among three signals) during Phase 2 training (30-70% progress) of a tri-modal reinforcement learning framework for code generation, enabling quality improvement without correctness regression.

**Core Claim:** Under Phase 2 training (30-70% progress), if AI feedback weight peaks (highest among three signals), then quality scores improve without correctness regression, because AI feedback enables scalable quality refinement beyond what human annotation cost allows.

**Implementation Approach:** Extend the validated h-m1 tri-modal RL framework to Phase 2 (30-70% training progress). Load h-m1 checkpoint at 30% progress, continue training with Phase 2 weight schedule (AI weight peaks), and track quality improvement while maintaining correctness.

**Success Metric:** AI weight peaks in Phase 2 (30-70%) AND quality score improves from 30%→70% AND pass@1 does not regress more than 5%.

---

## Problem Statement

### Research Question

Does the tri-modal RL framework exhibit AI-heavy weight scheduling in Phase 2 (30-70% progress), and does this enable quality refinement without sacrificing the correctness foundation established in Phase 1?

### Hypothesis Context

- **Type:** MECHANISM hypothesis
- **Prerequisite:** h-m1 (MECHANISM - validated, gate PASSED)
- **Position:** Tests Phase 2 behavior of h-e1's tri-modal framework
- **Gate Condition:** SHOULD_WORK - if AI feedback fails to improve quality, re-evaluate AI reward model or switch to human-only Phase 2

### Known from h-m1

✅ Phase 1 execution-heavy pattern validated (0-30% progress)  
✅ Pass@1 improvement rate: 1.2 in Phase 1 vs 0.14 in later phases  
✅ Checkpoint at 30% progress exists and verified  
✅ Dataset: HumanEval (164) + MBPP (874) = 1038 real samples  
✅ Model: Tri-modal RL with dynamic weight scheduling functional  
✅ Weight dominance detection working (0 violations in Phase 1)

---

## Functional Requirements

### FR1: Phase 2 Weight Monitoring System

**Priority:** P0 (Critical for h-m2 validation)

Implement checkpoint logging at 30%, 40%, 50%, 60%, 70% training progress to track tri-modal weight coefficients during Phase 2.

**Acceptance Criteria:**
- Checkpoints trigger at exact training progress milestones: 0.30, 0.40, 0.50, 0.60, 0.70
- Log all three weights: execution_weight, ai_weight, human_weight
- Verify weights sum to 1.0 at each checkpoint (±1e-6 tolerance)
- Detect AI weight peak (argmax of AI weight trajectory in Phase 2)
- Save checkpoint data to file for post-training analysis
- Display weight values to console during training

**Dependencies:**
- h-m1 `tri_modal_aggregator.py` (reuse and extend to Phase 2)
- Training progress tracking from PPO trainer

---

### FR2: Quality Score Trajectory Tracking

**Priority:** P0 (Core metric for h-m2)

Track human preference quality scores throughout Phase 2 training to measure quality improvement rate.

**Acceptance Criteria:**
- Evaluate quality at minimum checkpoints: 30%, 40%, 50%, 60%, 70% training progress
- Use cached human annotations (500 samples with preference scores from h-e1/h-m1)
- Test on validation split (104 samples)
- Save quality trajectory to file
- Calculate quality improvement rate: (quality_70% - quality_30%) / 0.40
- Verify positive improvement (quality_70% > quality_30%)

**Dependencies:**
- h-m1 `evaluation/evaluator.py` (reuse)
- h-m1 human annotation cache
- h-m1 validation split (reuse)

---

### FR3: Correctness Maintenance Tracking

**Priority:** P0 (No-regression requirement)

Track pass@1 correctness scores throughout Phase 2 to ensure AI feedback doesn't sacrifice correctness for quality.

**Acceptance Criteria:**
- Evaluate pass@1 at same checkpoints as quality: 30%, 40%, 50%, 60%, 70%
- Use real code execution (reuse h-m1 evaluator)
- Test on validation split (104 samples)
- Calculate correctness maintenance: pass1_70% ≥ 0.95 × pass1_30%
- Maximum allowed regression: 5%
- Save pass@1 trajectory to file

**Dependencies:**
- h-m1 `evaluation/evaluator.py` (reuse)
- h-m1 `data/dataset.py` validation split (reuse)

---

### FR4: Baseline Model - h-m1 Checkpoint at 30% Progress

**Priority:** P0 (Required for controlled experiment)

Load h-m1 checkpoint at 30% training progress as starting point for Phase 2.

**Acceptance Criteria:**
- Load from h-m1 output: `{h-m1_checkpoint_dir}/checkpoint_progress_0.30.pt`
- Verify checkpoint metadata: `training_progress == 0.30`, `phase == "Phase 1"`
- Model architecture: Same as h-m1 (CodeGen-350M-mono with tri-modal adapters)
- Verify pass@1 at 30%: ~0.616 (extrapolated from h-m1 trajectory)
- Device: CUDA (5x H100 NVL available)
- Precision: FP16 for training

**Dependencies:**
- h-m1 checkpoint file
- HuggingFace Transformers library
- CUDA-compatible environment

---

### FR5: Dataset - HumanEval + MBPP

**Priority:** P0 (Required for continuity with h-m1)

Reuse HumanEval (164) + MBPP (874) = 1038 samples with same splits as h-m1.

**Acceptance Criteria:**
- Load from HuggingFace: `evalplus/humanevalplus`, `google-research-datasets/mbpp`
- Apply h-m1 preprocessing: GPT-2 tokenizer, 512 max length
- Use h-m1 prompt template: `"# Problem: {prompt}\n# Solution:\n"`
- Extract and cache test cases for execution feedback
- Use h-m1 splits: Train: 830, Val: 104, Test: 104 samples
- Reuse cached human annotations (500 samples with quality scores)

**Dependencies:**
- HuggingFace Datasets library
- h-m1 `data/dataset.py` (reuse)
- h-m1 human annotation cache

---

### FR6: Phase 2 Tri-Modal Aggregator with AI Peak

**Priority:** P0 (Core mechanism for h-m2)

Extend h-m1 tri-modal aggregator with Phase 2 weight schedule (AI weight peaks).

**Acceptance Criteria:**
- Reuse Gaussian weight curves from h-m1 validated implementation
- Add Phase 2 weight schedule:
  - AI weight peaks at 50% training progress (mid-Phase 2)
  - Execution weight decays gradually: 0.50 → 0.20
  - Human weight increases slowly: 0.10 → 0.20
- Phase 2 checkpoints: [0.30, 0.40, 0.50, 0.60, 0.70]
- Log weight coefficients at checkpoints
- Maintain weight normalization (sum to 1.0)
- Detect AI weight peak location (argmax in Phase 2)

**Dependencies:**
- h-m1 `models/tri_modal_aggregator.py` base class
- PyTorch nn.Module

**Implementation Note:**
```python
class Phase2TriModalAggregator(TriModalAggregator):
    def __init__(self, config):
        super().__init__(config)
        self.phase2_start = 0.30
        self.phase2_end = 0.70
        self.ai_peak_progress = 0.50
        self.phase2_checkpoints = [0.30, 0.40, 0.50, 0.60, 0.70]
    
    def compute_dynamic_weights(self, training_progress):
        phase2_progress = (training_progress - self.phase2_start) / \
                          (self.phase2_end - self.phase2_start)
        phase2_progress = np.clip(phase2_progress, 0.0, 1.0)
        
        # AI weight: Gaussian peak centered at 50% Phase 2 progress
        ai_weight = 0.50 * np.exp(-((phase2_progress - 0.5)**2) / 0.05)
        ai_weight = max(0.30, ai_weight)
        
        # Execution weight: Gradual decay
        exec_weight = 0.50 - 0.30 * phase2_progress  # 0.50 → 0.20
        
        # Human weight: Slow increase
        human_weight = 0.10 + 0.10 * phase2_progress  # 0.10 → 0.20
        
        # Normalize
        total = exec_weight + ai_weight + human_weight
        return {
            'execution': exec_weight / total,
            'ai': ai_weight / total,
            'human': human_weight / total
        }
```

---

### FR7: PPO Training with Phase 2 Configuration

**Priority:** P0 (Training system)

Reuse h-m1 PPO trainer, resume from 30% checkpoint with Phase 2 configuration.

**Acceptance Criteria:**
- Starting checkpoint: h-m1 at 30% progress
- Optimizer: AdamW (lr=1e-5, reduced from Phase 1's 5e-5 for stability)
- Learning rate schedule: Linear decay (no warmup, already past Phase 1)
- Batch size: 64 (4x gradient accumulation on 16 samples)
- Episodes: 10,000 (Phase 2 portion, 30%→70%)
- PPO hyperparameters: clip_range=0.2, value_loss_coef=0.5, entropy_coef=0.01
- Seed: 42 (reproducibility)
- Training progress tracking: (current_episode - 3000) / 10000 = 0.30→0.70
- Checkpoint frequency: Every 1,000 steps (10% progress increments)
- Evaluation frequency: Every 500 steps

**Dependencies:**
- h-m1 `train/ppo_trainer.py` (reuse)
- Phase 2 tri-modal aggregator (FR6)
- Feedback collectors (FR8)

---

### FR8: Feedback Collectors (Execution, AI, Human)

**Priority:** P0 (Required for tri-modal system)

Reuse h-m1 feedback collectors for three modalities.

**Acceptance Criteria:**
- **Execution feedback**: Run generated code against test cases, return pass/fail scores
- **AI feedback**: Pretrained AI reward model scoring code quality
- **Human feedback**: Cached preference scores from h-m1 annotation (500 samples)
- All collectors return normalized rewards in [0, 1] range
- AI reward model uses GPT-4-based quality assessment (reuse from h-m1)

**Dependencies:**
- h-m1 `models/feedback_collectors.py` (reuse)
- Code execution sandbox
- AI reward model checkpoint
- Cached human annotations

---

### FR9: Real Code Execution Evaluator

**Priority:** P0 (Gate validation)

Reuse h-m1 evaluator for real code execution during Phase 2.

**Acceptance Criteria:**
- Execute generated code in sandboxed environment
- Run test cases extracted from dataset
- Compute pass@1 (fraction of problems with at least 1 passing sample)
- No mocking or simulation (real execution only)
- Timeout: 5 seconds per test case
- Error handling: Capture runtime errors, syntax errors, timeouts

**Dependencies:**
- h-m1 `evaluation/evaluator.py` (reuse)
- Code execution sandbox

---

### FR10: Phase 2 Gate Validator

**Priority:** P0 (SHOULD_WORK gate check)

Implement gate validation logic to verify h-m2 success criteria.

**Acceptance Criteria:**
- **Gate Metric 1**: AI weight peak detection
  - Find argmax(AI_weight) in Phase 2 range [0.30, 0.70]
  - Success: AI weight is highest among three signals at peak
- **Gate Metric 2**: Quality improvement in Phase 2
  - Calculate: quality_improvement_rate = (quality_70% - quality_30%) / 0.40
  - Success: quality_improvement_rate > 0 (positive improvement)
- **Gate Metric 3**: Correctness maintenance
  - Calculate: pass1_70% / pass1_30%
  - Success: ratio ≥ 0.95 (max 5% regression allowed)
- **Overall Gate Result**: PASS if all 3 metrics pass, else FAIL

**Dependencies:**
- Weight trajectory logs (FR1)
- Quality trajectory (FR2)
- Pass@1 trajectory (FR3)

**Implementation Note:**
```python
class Phase2GateValidator:
    def validate(self, weight_trajectory, quality_trajectory, pass1_trajectory):
        # Gate 1: AI weight peak detection
        ai_weights = [w['ai'] for w in weight_trajectory if 0.30 <= w['progress'] <= 0.70]
        ai_peak_idx = np.argmax(ai_weights)
        peak_weights = weight_trajectory[ai_peak_idx]
        gate1_passed = peak_weights['ai'] > peak_weights['execution'] and \
                      peak_weights['ai'] > peak_weights['human']
        
        # Gate 2: Quality improvement
        quality_30 = quality_trajectory[0]  # First Phase 2 checkpoint
        quality_70 = quality_trajectory[-1]  # Last Phase 2 checkpoint
        quality_improvement_rate = (quality_70 - quality_30) / 0.40
        gate2_passed = quality_improvement_rate > 0
        
        # Gate 3: Correctness maintenance
        pass1_30 = pass1_trajectory[0]
        pass1_70 = pass1_trajectory[-1]
        gate3_passed = pass1_70 >= 0.95 * pass1_30
        
        return {
            'gate1_ai_peak': gate1_passed,
            'gate2_quality_improved': gate2_passed,
            'gate3_correctness_maintained': gate3_passed,
            'overall': gate1_passed and gate2_passed and gate3_passed
        }
```

---

### FR11: Visualization Suite

**Priority:** P1 (Required for analysis)

Generate 4 mandatory figures for h-m2 analysis.

**Acceptance Criteria:**

1. **Gate Metrics Comparison** (Mandatory)
   - Bar chart: Target vs actual for 3 gate metrics
   - X-axis: {AI Peak Detected, Quality Improved, Correctness Maintained}
   - Y-axis: Binary (0/1)
   - Colors: Green (pass), Red (fail)

2. **Weight Trajectory Plot** (Mandatory for h-m2)
   - X-axis: Training progress (0.30 → 0.70)
   - Y-axis: Weight coefficients (0 → 1)
   - Three lines: Execution (blue), AI (green), Human (red)
   - Vertical line: AI weight peak location
   - Annotation: Phase 2 boundaries (30%, 70%)

3. **Quality vs. Correctness Trajectory** (Mandatory)
   - X-axis: Training progress (0.30 → 0.70)
   - Y-axis (left): pass@1 (correctness)
   - Y-axis (right): Human preference (quality)
   - Dual-axis line plot
   - Purpose: Verify no correctness regression during quality improvement

4. **Harmonic Mean Progress** (Mandatory)
   - X-axis: Training progress (0 → 1.0, highlight 0.3-0.7)
   - Y-axis: Harmonic mean(pass@1, quality)
   - Line plot showing overall performance balance
   - Compare to h-m1 trajectory (dotted line)

**Dependencies:**
- matplotlib, seaborn
- h-m2 checkpoint logs
- h-m1 trajectory for comparison

**Output Location:** `{hypothesis_folder}/figures/`

---

## Non-Functional Requirements

### NFR1: Performance

**Training Time:**
- Phase 2 training: 8-12 hours on 1x NVIDIA A100 (40GB)
- Checkpoint evaluation: < 10 minutes per checkpoint
- Total Phase 2 runtime: ~15 hours including evaluation

**Compute Resources:**
- GPU: 1x NVIDIA A100 (40GB) or 4x V100 (32GB)
- Memory: 40GB GPU, 128GB system RAM
- Storage: 50GB for checkpoints, logs, figures

### NFR2: Reproducibility

**Determinism:**
- Fixed random seed: 42
- Deterministic CUDA operations: `torch.use_deterministic_algorithms(True)`
- Version pinning: PyTorch 2.x, Transformers 4.x, Numpy 1.x

**Checkpointing:**
- Save full model state_dict at each Phase 2 checkpoint
- Include metadata: training_progress, phase, episode, optimizer_state

### NFR3: Data Quality

**No Mock Data:**
- Real datasets only (HumanEval + MBPP, total 1038 samples)
- Real code execution (no simulated pass/fail)
- Cached human annotations from h-m1 (500 samples with quality scores)
- Minimum 500+ evaluation samples (statistically meaningful)

**Data Integrity:**
- Verify checkpoint at 30% from h-m1 exists before starting
- Verify human annotation cache contains 500 samples
- Verify test cases extracted for all dataset samples

### NFR4: Reliability

**Failure Handling:**
- Graceful degradation: If evaluation fails, log error and continue training
- Checkpoint recovery: Resume from last valid checkpoint if training interrupted
- Timeout handling: 5-second timeout per code execution, skip on timeout

**Monitoring:**
- Log weight values at every checkpoint
- Log quality and pass@1 scores at every evaluation
- Save trajectories to file for post-training analysis

---

## Data Specifications

### Input Data

**Datasets:**
- **Source:** HuggingFace Datasets
- **Identifiers:** 
  - HumanEval: `evalplus/humanevalplus` (164 samples)
  - MBPP: `google-research-datasets/mbpp` (874 samples)
- **Total:** 1038 samples
- **Splits:** Train (830), Val (104), Test (104)
- **Preprocessing:** GPT-2 tokenizer, 512 max length, h-m1 prompt template
- **Storage:** `./data/datasets/humaneval/` + `./data/datasets/mbpp/`

**h-m1 Checkpoint:**
- **Source:** h-m1 output directory
- **File:** `{h-m1_checkpoint_dir}/checkpoint_progress_0.30.pt`
- **Metadata Required:** training_progress=0.30, phase="Phase 1"
- **Size:** ~1.5GB (model weights + optimizer state)

**Human Annotations:**
- **Source:** h-m1 annotation cache
- **File:** `{h-m1_output}/human_annotations.json`
- **Format:** `{"sample_id": str, "preference_score": float (0-1)}`
- **Count:** 500 samples with quality scores
- **Storage:** `./data/annotations/`

### Output Data

**Checkpoints:**
- **Files:** `checkpoint_progress_{0.30,0.40,0.50,0.60,0.70}.pt`
- **Location:** `{hypothesis_folder}/checkpoints/`
- **Size:** ~1.5GB per checkpoint (total ~7.5GB)

**Trajectories:**
- **Files:** `weight_trajectory.csv`, `quality_trajectory.csv`, `pass1_trajectory.csv`
- **Location:** `{hypothesis_folder}/logs/`
- **Format:** CSV with columns: progress, metric_value

**Figures:**
- **Files:** `gate_metrics.png`, `weight_trajectory.png`, `quality_vs_correctness.png`, `harmonic_mean.png`
- **Location:** `{hypothesis_folder}/figures/`
- **Format:** PNG (300 DPI)

**Gate Results:**
- **File:** `gate_validation.json`
- **Location:** `{hypothesis_folder}/`
- **Format:** JSON with gate metrics and overall result

---

## Success Criteria

### Primary Metrics (SHOULD_WORK Gate)

1. **AI Weight Peak Detection** (Gate 1)
   - Metric: argmax(AI_weight) ∈ [0.3, 0.7] training progress
   - Measurement: AI weight is highest among three signals at peak
   - Success: Gate 1 PASSED

2. **Quality Score Improvement** (Gate 2)
   - Metric: Quality improvement rate = (quality_70% - quality_30%) / 0.40
   - Target: Positive improvement rate (> 0)
   - Success: Gate 2 PASSED

3. **Correctness Maintenance** (Gate 3)
   - Metric: pass1_70% / pass1_30% ≥ 0.95
   - Target: Maximum 5% pass@1 regression
   - Success: Gate 3 PASSED

**Overall Gate Result:** PASS if all 3 gates pass, else FAIL

### Secondary Metrics

4. **Harmonic Mean Progress**
   - Metric: harmonic_mean(pass@1, quality) at 70%
   - Comparison: vs h-m1 at 30% (baseline)
   - Expected: Improvement due to quality gains

5. **Weight Trajectory Smoothness**
   - Metric: Weight curves are smooth (no abrupt jumps)
   - Verification: Visual inspection of weight_trajectory.png

---

## Dependencies and Constraints

### Technical Dependencies

**From h-m1 (Reuse):**
- Tri-modal aggregator base class
- PPO trainer implementation
- Feedback collectors (execution, AI, human)
- Evaluation pipeline
- Dataset preprocessing
- Human annotation cache

**External Libraries:**
- Python 3.8+
- PyTorch 2.x (CUDA 11.8+)
- HuggingFace Transformers 4.x
- HuggingFace Datasets
- NumPy, Pandas
- Matplotlib, Seaborn

**MCP Services:**
- Archon MCP (project management)
- Serena MCP (code analysis, optional)

### Constraints

**Prerequisite Constraint:**
- h-m1 must be completed (MUST_WORK gate PASSED)
- h-m1 checkpoint at 30% must exist
- Human annotation cache from h-m1 must be available

**Resource Constraint:**
- GPU memory: 40GB minimum (A100 or equivalent)
- Training time: 8-12 hours for Phase 2
- Storage: 50GB for checkpoints and logs

**Data Constraint:**
- Real datasets only (no synthetic data)
- Real code execution (no mocking)
- Minimum 500 cached human annotations

---

## Timeline and Milestones

**Phase 3 Complete:** PRD, Architecture, Logic, Config generated  
**Phase 4 Target:** Working implementation with SHOULD_WORK gate validation

**Estimated Phase 4 Timeline:**
1. **Setup** (1 hour): Load h-m1 checkpoint, verify data
2. **Training** (10 hours): Phase 2 PPO training with monitoring
3. **Evaluation** (2 hours): Checkpoint evaluations, trajectory analysis
4. **Validation** (1 hour): Gate validation, figure generation
5. **Total:** ~15 hours

---

## Risks and Mitigation

### Risk 1: AI Feedback Doesn't Improve Quality

**Impact:** High - Core hypothesis invalidated  
**Likelihood:** Medium - AI reward model quality is uncertain  
**Mitigation:**
- Verify AI reward model quality on validation set before training
- Monitor quality trajectory early (at 40% checkpoint)
- Fallback: If quality doesn't improve by 50%, consider switching to human-only Phase 2

### Risk 2: Correctness Regression > 5%

**Impact:** High - Gate 3 failure  
**Likelihood:** Low - Phase 1 established strong correctness foundation  
**Mitigation:**
- Monitor pass@1 at every checkpoint (30%, 40%, 50%, 60%, 70%)
- If regression detected early, reduce AI weight peak or increase execution weight floor
- Fallback: Revert to h-m1 checkpoint and adjust weight schedule

### Risk 3: h-m1 Checkpoint Missing or Corrupted

**Impact:** High - Cannot start Phase 2  
**Likelihood:** Low - h-m1 validated and checkpoints saved  
**Mitigation:**
- Verify checkpoint file exists before starting Phase 2
- Verify checkpoint metadata (training_progress=0.30)
- Fallback: Re-run h-m1 if checkpoint missing

### Risk 4: Insufficient Cached Human Annotations

**Impact:** Medium - Quality evaluation unreliable  
**Likelihood:** Low - h-m1 already cached 500 annotations  
**Mitigation:**
- Verify annotation cache contains ≥500 samples before training
- Fallback: Use AI feedback as proxy for human feedback (with disclaimer)

---

## Appendix

### Reference: Phase 2C Experiment Brief

**Source:** `docs/youra_research/h-m2/02c_experiment_brief.md`

**Key Insights:**
- Archon KB lacks specific code generation RL examples
- h-m1 implementation is primary reference
- Diffusion weight scheduling patterns transferable to feedback weighting
- No external GitHub implementations (novel hypothesis)

### Reference: h-m1 Validation Results

**Source:** `docs/youra_research/h-m1/04_validation.md` (via verification_state.yaml)

**Key Results:**
- ✅ MUST_WORK gate PASSED
- ✅ Execution weight dominance in Phase 1 (0 violations)
- ✅ Pass@1 improvement rate: 1.2 in Phase 1 vs 0.14 in later phases
- ✅ Weight correlation: -0.2 (negative as expected)
- ✅ Dataset: Real (HumanEval + MBPP, 1038 samples)

### Archon Knowledge Base Findings

**Search Results:**
1. Instruction following (RLHF paradigm)
2. Dynamic weight scheduling (diffusion schedulers)
3. LoRA training patterns
4. Model evaluation metrics

**Key Pattern:** Diffusion timestep weighting → Feedback signal weighting (conceptual transfer)

### Hypothesis Context

- **Type:** MECHANISM
- **Prerequisites:** h-m1 (MECHANISM - validated, gate PASSED)
- **Gate:** SHOULD_WORK
- **Next Hypothesis:** h-m3 (depends on h-m2, tests Phase 3 human feedback)

---

**End of PRD**
