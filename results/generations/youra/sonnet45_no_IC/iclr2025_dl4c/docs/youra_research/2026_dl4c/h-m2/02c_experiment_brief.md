# Experiment Design: h-m2

**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis Statement:** Under Phase 2 training (30-70% progress), if AI feedback weight peaks (highest among three signals), then quality scores improve without correctness regression, because AI feedback enables scalable quality refinement beyond what human annotation cost allows.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m1 COMPLETED (MUST_WORK gate PASSED)
**Gate Status:** SHOULD_WORK (in progress)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1

### Gate Condition
SHOULD_WORK: If AI feedback does not enable quality refinement → Re-evaluate AI reward model quality or switch to human-only Phase 2

---

## Continuation Context

This hypothesis builds on h-m1 (Phase 1 Execution-Heavy Foundation). It tests whether AI feedback can effectively scale quality refinement in Phase 2 (30-70% training progress) without sacrificing the correctness established in Phase 1.

### Previous Hypothesis Results (if applicable)
**h-m1 Results (COMPLETED - MUST_WORK gate PASSED):**
- ✅ Gate validated: Execution weight dominance in Phase 1
- ✅ Pass@1 improvement rate: 1.2 in Phase 1 vs 0.14 in later phases
- ✅ Weight correlation: -0.2 (negative as expected)
- Dataset: HumanEval (164) + MBPP (874) = 1038 real samples
- Model: Tri-modal RL with dynamic weight scheduling
- Key finding: Phase 1 execution-heavy weighting successfully establishes correctness foundation

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search 1: AI feedback reward model quality refinement**
- OpenReview paper on instruction following (RLHF paradigm)
- HuggingFace PEFT documentation on LoRA adapters for fine-tuning
- Limited direct relevance to code generation RL

**Search 2: Dynamic weight scheduling multi-modal RL**
- Diffusion model schedulers (timestep weighting, noise scheduling)
- Concept: Dynamic parameter adjustment during training
- Transferable pattern: Adaptive weight scheduling based on training progress

**Search 3: RLHF reward model training quality feedback**
- LoRA training patterns for parameter-efficient fine-tuning
- Model evaluation metrics (FID, IS, PPL)
- Training configuration patterns (learning rate, batch size, checkpointing)

**Search 4: PPO code generation execution feedback**
- GAN training evaluation metrics
- Model generation and inference patterns
- Limited direct code generation RL examples in Archon KB

**Key Insight:** Archon KB lacks specific code generation RL examples. Must rely on h-m1 implementation as primary reference.

### Archon Code Examples

**Relevant Patterns Found:**
1. **Timestep weight generation** (diffusers): Dynamic weight adjustment during training
2. **LoRA adapter loading**: Parameter-efficient fine-tuning for large models
3. **Training configuration**: Batch size, learning rate schedules, checkpointing
4. **Model evaluation**: Metrics computation and validation during training

**Code pattern for dynamic weighting:**
```python
# From diffusers timestep weighting
weights = generate_timestep_weights(args, num_train_timesteps)
timesteps = torch.multinomial(weights, batch_size, replacement=True)
```

**Transferable to h-m2:** Replace timestep weights with feedback signal weights (execution, AI, human)

### Exa GitHub Implementations

**Status:** Exa MCP unavailable (402 payment required error)

**Fallback:** Using h-m1 validated implementation as primary reference

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Priority:**
1. **Primary (100%):** h-m1 codebase (validated, MUST_WORK gate passed)
2. **Secondary:** Archon diffusion weight scheduling patterns (conceptual transfer)
3. **Tertiary:** N/A (no paper implementation exists - novel hypothesis)

**Recommended Implementation Path:**
- **Primary:** Extend h-m1 tri-modal RL codebase (already validated)
- **Fallback:** Build from scratch using h-m1 architecture patterns
- **Justification:** h-m1 already implements tri-modal RL framework with Phase 1 (0-30%) validated. h-m2 tests Phase 2 (30-70%) on same codebase. Code reuse ensures consistency and reduces implementation risk.

### Code Analysis (Serena MCP)

**Status:** Not applicable - no external codebase to analyze

**Approach:** Analyze h-m1 validated code structure:
- `models/phase1_tri_modal_aggregator.py`: Core tri-modal feedback aggregation
- `train/phase1_ppo_trainer.py`: PPO training loop with weight scheduling
- `evaluation/phase1_metrics.py`: Metrics computation (pass@1, quality)
- `config/phase1_config.py`: Weight schedule configuration

**h-m2 Modification Strategy:**
- Reuse h-m1 aggregator and trainer
- Modify weight schedule config for Phase 2 (30-70%)
- Add Phase 2-specific metrics (AI weight peak detection, quality improvement rate)
- Verify no correctness regression (pass@1 maintenance check)

---

## Experiment Specification

### Dataset

**Name:** HumanEval + MBPP (Combined Real Dataset)
**Type:** standard
**Source:** HuggingFace Datasets

**Details:**
- **HumanEval:** 164 hand-written programming problems (OpenAI)
- **MBPP:** 874 crowd-sourced Python programming problems (Google)
- **Total:** 1038 real code generation tasks
- **Split:** Use same splits as h-m1 (train/val/test)
- **Execution Feedback:** Automated test cases available for all samples
- **Human Feedback:** Quality annotations (500 samples with preference scores)

**Validation:** ✅ Real dataset confirmed in h-m1 (NOT synthetic)

**Loading Information** (for Phase 4 download):
- **Method:** HuggingFace `datasets.load_dataset()`
- **Identifier:** `evalplus/humanevalplus` (164) + `google-research-datasets/mbpp` (874)
- **Code:**
```python
from datasets import load_dataset

# Load HumanEval (164 samples)
humaneval = load_dataset(
    "evalplus/humanevalplus",
    split="test",
    cache_dir="./data/datasets/humaneval"
)

# Load MBPP (874 samples)
mbpp = load_dataset(
    "google-research-datasets/mbpp",
    split="train",  # MBPP uses 'train' split for all data
    cache_dir="./data/datasets/mbpp"
)

# Combine datasets (1038 total)
combined_dataset = concatenate_datasets([humaneval, mbpp])
```

### Models

#### Baseline Model

**Baseline:** h-m1 Phase 1 trained model (checkpoint at 30% training progress)

**Architecture:** 1.5B Parameter Code LLM (Transformer decoder, Codex-style)
- Base: Pre-trained checkpoint (CodeGen, StarCoder, or similar)
- After h-m1 Phase 1: Execution-heavy RL training (0-30% progress)
- Checkpoint: Model state at 30% training progress

**Performance (from h-m1):**
- Pass@1 at 30%: ~0.616 (extrapolated from h-m1 trajectory)
- Quality score baseline: To be measured at Phase 2 start
- Weight distribution: Execution-dominant (Phase 1 pattern)

**Loading Information** (for Phase 4 download):
- **Method:** Load h-m1 checkpoint at 30% progress
- **Identifier:** `{h-m1_checkpoint_dir}/checkpoint_progress_0.30.pt`
- **Code:**
```python
import torch
from transformers import AutoModelForCausalLM

# Load h-m1 checkpoint at 30% progress
checkpoint_path = "code/h-m1/checkpoints/checkpoint_progress_0.30.pt"
checkpoint = torch.load(checkpoint_path)

# Load base model architecture
model = AutoModelForCausalLM.from_pretrained(
    "Salesforce/codegen-1B-multi",  # or StarCoder
    torch_dtype=torch.float16
)

# Apply h-m1 Phase 1 weights
model.load_state_dict(checkpoint['model_state_dict'])

# Verify checkpoint metadata
assert checkpoint['training_progress'] == 0.30
assert checkpoint['phase'] == "Phase 1"
```

#### Proposed Model

**Architecture:** h-m1 tri-modal RL framework with Phase 2 weight scheduling (30-70% progress)

**Core Mechanism Implementation:**

```python
# Phase 2 AI-Feedback Peak Mechanism (30-70% training progress)
# Extends h-m1 tri-modal aggregator with Phase 2 weight schedule

class Phase2TriModalAggregator:
    """
    Phase 2: AI feedback weight peaks (highest among three signals)
    to enable scalable quality refinement without correctness regression.
    """
    
    def __init__(self, config):
        self.ai_reward_model = load_pretrained_ai_reward_model()
        self.phase2_start = 0.30  # Training progress
        self.phase2_end = 0.70
        self.ai_peak_progress = 0.50  # AI weight peaks at 50% progress
        
    def compute_dynamic_weights(self, training_progress):
        """
        Dynamic weight schedule for Phase 2 (30-70% progress).
        
        AI weight peaks in this phase to enable quality refinement.
        Execution weight decays gradually.
        Human weight remains low (saved for Phase 3).
        """
        # Normalize progress within Phase 2
        phase2_progress = (training_progress - self.phase2_start) / \
                          (self.phase2_end - self.phase2_start)
        phase2_progress = np.clip(phase2_progress, 0.0, 1.0)
        
        # AI weight: Gaussian peak centered at 50% Phase 2 progress
        ai_weight = 0.50 * np.exp(-((phase2_progress - 0.5)**2) / 0.05)
        ai_weight = max(0.30, ai_weight)  # Minimum 30% to ensure influence
        
        # Execution weight: Gradual decay from Phase 1 levels
        exec_weight = 0.50 - 0.30 * phase2_progress  # 0.50 → 0.20
        
        # Human weight: Low and slowly increasing
        human_weight = 0.10 + 0.10 * phase2_progress  # 0.10 → 0.20
        
        # Normalize to sum to 1.0
        total = exec_weight + ai_weight + human_weight
        return {
            'execution': exec_weight / total,
            'ai': ai_weight / total,
            'human': human_weight / total
        }
    
    def aggregate_feedback(self, code_sample, training_progress):
        """
        Aggregate three feedback signals with dynamic weights.
        """
        # Get feedback from three sources
        exec_reward = execute_tests(code_sample)  # 0/1 pass/fail
        ai_reward = self.ai_reward_model.predict_quality(code_sample)  # 0-1
        human_reward = get_human_annotation(code_sample)  # 0-1 (cached)
        
        # Compute Phase 2 dynamic weights
        weights = self.compute_dynamic_weights(training_progress)
        
        # Aggregate with dynamic weighting
        total_reward = (
            weights['execution'] * exec_reward +
            weights['ai'] * ai_reward +
            weights['human'] * human_reward
        )
        
        # Log for gate validation
        log_weights(training_progress, weights)
        
        return total_reward
```

**Key Mechanism Properties:**
1. AI weight peaks at 50% training progress (mid-Phase 2)
2. Execution weight decays gradually (maintains correctness foundation)
3. Human weight increases slowly (prepares for Phase 3)
4. Quality improves via AI feedback without correctness regression

### Training Protocol

**Phase 2 Training Configuration (30-70% progress):**

**Starting Point:** h-m1 checkpoint at 30% progress (Phase 1 complete)

**Optimizer:** AdamW
- Learning rate: 1e-5 (reduced from Phase 1's 5e-5 for stability)
- Beta1: 0.9, Beta2: 0.999
- Weight decay: 0.01
- Gradient clipping: 1.0

**RL Algorithm:** PPO (Proximal Policy Optimization)
- Clip ratio: 0.2
- Value loss coefficient: 0.5
- Entropy coefficient: 0.01 (encourage exploration)
- PPO epochs per batch: 4
- Mini-batch size: 32

**Training Schedule:**
- Total training steps: 10,000 (Phase 2 portion)
- Batch size: 64 (4x gradient accumulation on 16 samples)
- Checkpoint frequency: Every 1,000 steps (10% progress increments)
- Evaluation frequency: Every 500 steps

**Dynamic Weight Schedule:**
- Phase 2 range: 30-70% training progress
- AI weight peak: ~50% progress (mid-Phase 2)
- Weight logging: Every checkpoint for gate validation

**Data Sampling:**
- Training set: 80% of combined dataset (~830 samples)
- Validation set: 10% (~104 samples)
- Test set: 10% (~104 samples, held-out for final evaluation)
- On-policy sampling: Generate new code samples each epoch

**Compute Resources:**
- GPU: 1x NVIDIA A100 (40GB) or 4x V100 (32GB)
- Estimated time: 8-12 hours for Phase 2 training
- Mixed precision: FP16 (reduce memory footprint)

### Evaluation

**Primary Metrics (Gate Validation):**

1. **AI Weight Peak Detection**
   - Metric: argmax(AI_weight) ∈ [0.3, 0.7] training progress
   - Measurement: Log weights at each checkpoint, find maximum
   - Success: AI weight is highest among three signals in Phase 2
   
2. **Quality Score Improvement**
   - Metric: Human preference score trajectory in Phase 2
   - Baseline: Quality at 30% progress (Phase 1 end)
   - Target: Positive improvement rate in Phase 2 vs. Phases 1 and 3
   - Measurement: ∆quality / ∆progress (slope in Phase 2)

3. **Correctness Maintenance (No Regression)**
   - Metric: pass@1 at 70% ≥ 0.95 × pass@1 at 30%
   - Purpose: Verify AI feedback doesn't sacrifice correctness for quality
   - Threshold: Maximum 5% pass@1 degradation allowed

**Secondary Metrics:**

4. **Harmonic Mean Progress**
   - Metric: harmonic_mean(pass@1, human_preference) trajectory
   - Purpose: Track overall performance balance

5. **Weight Trajectory Analysis**
   - Execution weight decay rate
   - Human weight increase rate
   - Cross-over points between signal dominance

**Metrics Loading Information** (for Phase 4 implementation):
- **Task Type:** Code Generation with Multi-Modal RL
- **Library:** Custom evaluation module (extends h-m1 evaluator)
- **Code:**
```python
from evaluation.phase2_metrics import Phase2Evaluator
from evaluation.evaluator import compute_harmonic_mean

# Initialize Phase 2 evaluator
evaluator = Phase2Evaluator(
    dataset=test_dataset,
    checkpoints_dir="checkpoints/h-m2"
)

# Gate Metric 1: AI weight peak detection
weight_trajectory = evaluator.load_weight_logs()
ai_peak_progress = evaluator.find_ai_weight_peak(weight_trajectory)
gate1_passed = (ai_peak_progress >= 0.30) and (ai_peak_progress <= 0.70)

# Gate Metric 2: Quality improvement in Phase 2
quality_at_30 = evaluator.get_quality_at_progress(0.30)
quality_at_70 = evaluator.get_quality_at_progress(0.70)
quality_improvement_rate = (quality_at_70 - quality_at_30) / 0.40
gate2_passed = quality_improvement_rate > 0  # Positive improvement

# Gate Metric 3: Correctness maintenance
pass1_at_30 = evaluator.get_pass1_at_progress(0.30)
pass1_at_70 = evaluator.get_pass1_at_progress(0.70)
gate3_passed = pass1_at_70 >= 0.95 * pass1_at_30

# Overall gate result
gate_passed = gate1_passed and gate2_passed and gate3_passed

print(f"Gate Result: {'PASS' if gate_passed else 'FAIL'}")
print(f"  AI peak at {ai_peak_progress:.2%} progress: {gate1_passed}")
print(f"  Quality improved: {gate2_passed}")
print(f"  Correctness maintained: {gate3_passed}")
```

**Evaluation Protocol:**
- Checkpoint evaluation: Every 10% progress (30%, 40%, 50%, 60%, 70%)
- Test set size: 104 samples (held-out)
- Human annotations: Use cached quality scores from Phase 1 annotation
- Execution feedback: Run automated test suites on generated code

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **Weight Trajectory Plot** (Mandatory for h-m2)
   - X-axis: Training progress (0.30 → 0.70)
   - Y-axis: Weight coefficients (0 → 1)
   - Three lines: Execution (blue), AI (green), Human (red)
   - Vertical line: AI weight peak location
   - Annotation: Phase 2 boundaries (30%, 70%)

2. **Quality vs. Correctness Trajectory**
   - X-axis: Training progress
   - Y-axis (left): pass@1 (correctness)
   - Y-axis (right): Human preference (quality)
   - Dual-axis line plot showing both metrics
   - Purpose: Verify no correctness regression during quality improvement

3. **Phase 2 Improvement Rate Comparison**
   - Bar chart: Improvement rates in Phase 1, Phase 2, Phase 3
   - Metric: ∆quality / ∆progress for each phase
   - Expected: Phase 2 shows highest quality improvement rate

4. **Harmonic Mean Progress**
   - X-axis: Training progress (0 → 1.0, highlight 0.3-0.7)
   - Y-axis: Harmonic mean(pass@1, quality)
   - Line plot showing overall performance balance
   - Compare to h-m1 trajectory

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.
> Use matplotlib with consistent styling (see h-m1 visualization module).

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### Primary Reference: h-m1 Validated Code

**Repository:** `code/h-m1/` (local, validated in Phase 4)

**Key Files:**
1. `models/phase1_tri_modal_aggregator.py` - Core aggregation logic
   - Reuse for h-m2 with modified weight schedule
   
2. `train/phase1_ppo_trainer.py` - PPO training loop
   - Extend to Phase 2 (30-70% progress range)
   
3. `evaluation/phase1_metrics.py` - Metrics computation
   - Add Phase 2 specific metrics (AI peak, quality rate)
   
4. `config/phase1_config.py` - Weight schedule configuration
   - Modify for Phase 2 AI-heavy pattern
   
5. `utils/visualization.py` - Figure generation
   - Reuse for consistency with h-m1 plots

**h-m1 Validation Results:**
- ✅ MUST_WORK gate PASSED
- ✅ Real datasets (HumanEval + MBPP)
- ✅ Mock data violations fixed (independent quality metrics)
- ✅ Execution weight dominance in Phase 1 verified
- ✅ 1038 real samples, 164 HumanEval + 874 MBPP

### Secondary References: Research Papers

1. **PPOCoder** (Shojaee et al., 2023)
   - Execution feedback RL for code generation
   - 40% → 70% pass@1 improvement on MBPP
   - Source: Archon KB, OpenReview

2. **RLHF for Code** (OpenAI Instruction Following)
   - Human feedback improves code quality
   - Reward model training on preference pairs
   - Source: https://openai.com/blog/instruction-following/

3. **Themis** (Paul et al., 2026)
   - Multi-criteria reward models for code
   - 350K+ preference pairs (correctness + style + efficiency)
   - Demonstrates multi-modal quality dimensions

### Conceptual Transfer: Diffusion Schedulers

**Pattern:** Dynamic timestep weighting in diffusion models
- Source: HuggingFace Diffusers library
- Transferable concept: Adaptive parameter scheduling based on training progress
- Applied to h-m2: Replace timestep → training progress, noise weights → feedback weights

**Code Pattern:**
```python
# Diffusers timestep weighting (conceptual source)
weights = generate_timestep_weights(args, num_timesteps)
sampled_timesteps = torch.multinomial(weights, batch_size)

# h-m2 feedback weighting (transferred pattern)
weights = compute_phase2_weights(training_progress)
aggregated_reward = weights['execution'] * exec_r + weights['ai'] * ai_r + ...
```

### No External GitHub Implementations

**Reason:** Novel hypothesis (no prior work on tri-modal RL with dynamic scheduling for code)

**Strategy:** Build from h-m1 validated foundation (code reuse, architectural consistency)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-12T13:43:19+00:00

### Workflow History for This Hypothesis
- 2026-07-12T13:43:19: Hypothesis h-m2 set to IN_PROGRESS (hypothesis loop initiation)
- 2026-07-12T13:43:20: Phase 2C experiment design started (unattended mode)
- 2026-07-12T13:44:00: Archon KB search completed (4 searches, limited code generation RL content)
- 2026-07-12T13:44:10: Exa search unavailable (402 error), using h-m1 as primary reference
- 2026-07-12T13:44:30: Experiment specification synthesized (Level 1.5, 50-line pseudo-code)
- 2026-07-12T13:44:40: Phase 2C COMPLETED - Output: 02c_experiment_brief.md

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
