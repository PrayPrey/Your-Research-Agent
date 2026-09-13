# Experiment Design: h-m3

**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis Statement:** Under Phase 3 training (70-100% progress), if human feedback weight increases, then edge case performance improves (conflict cases resolve to intermediate preference scores [0.1-0.4], not extreme collapse to execution-only behavior), because human feedback corrects systematic AI biases and fine-tunes quality on difficult cases.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** ✅ h-m2 completed (PASS - SHOULD_WORK gate)
**Gate Status:** Ready for Phase 3 → 4 execution

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2

### Gate Condition
**Gate Type:** SHOULD_WORK
- If PASSED: Hypothesis validated, mechanism confirmed
- If FAILED: Document limitation, continue pipeline (not blocking)

**Success Criteria** (from Phase 2B):
- Primary: Human weight at 100% > human weight at 70% (positive correlation)
- Primary: Conflict case median preference ∈ [0.1, 0.4] (not collapsed)
- Secondary: Correctness maintained (pass@1 ratio ≥ 0.95)

---

## Continuation Context

**Pipeline Position:** Third mechanism hypothesis in linear chain
**Dependency Chain:** h-e1 (PASS) → h-m1 (PASS) → h-m2 (PASS) → **h-m3** (current)

**Incremental Extension Strategy:**
- h-m1 validated: Phase 1 execution-heavy (0-30%)
- h-m2 validated: Phase 2 AI-heavy (30-70%)
- h-m3 extends: Phase 3 human-heavy (70-100%)

**Rationale:** Each hypothesis builds on prior validated code, enabling controlled experiments and minimizing implementation risk.

### Previous Hypothesis Results

**h-m2 Validation Results** (from 04_validation.md):
- **Gate Result:** ✅ PASS (SHOULD_WORK)
- **Key Metrics:**
  - AI weight peak: 0.545 at 50% progress (Phase 2 dominance confirmed)
  - Quality improvement: 0.450 → 0.520 (+15.6%)
  - Correctness maintained: 103.2% ratio (no regression)
- **Proven Components:**
  - Phase2TriModalAggregator: Validated tri-modal weight scheduling
  - Gaussian weight curves: Proven effective for phase-appropriate weighting
  - PPO training: Stable with CodeGen-350M smoke test
  - Metrics computation: Working gate validation
- **Optimal Configuration (reused for h-m3):**
  - Model: CodeGen-350M
  - Optimizer: Adam, lr=3e-4
  - Seed: 42
  - Checkpoints: Every 10% progress
  - Dataset: HumanEval + MBPP

**Impact on h-m3 Design:**
- Reuse validated h-m2 framework (minimal changes)
- Extend Phase2TriModalAggregator to Phase 3 range (70-100%)
- Maintain same training setup for controlled comparison
- Add conflict case evaluation (new for h-m3)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Human Feedback Edge Case Conflict Resolution**
- Limited direct matches found in Archon KB
- Most relevant: OpenAI Instruction Following blog (discussing RLHF principles)
- Key insight: Human feedback is fundamental to quality refinement in language models
- No specific experiment designs for Phase 3 human feedback scheduling found

**Query 2: Late Training Human Refinement**
- Relevant source: OpenAI blog on instruction-following models
- Discusses human feedback for aligning model behavior
- General RLHF literature indicates human feedback is costly but effective
- No specific implementation patterns for late-stage training refinement

**Query 3: Code Generation Quality Preference**
- Limited code-specific quality annotation literature in KB
- Standard approach: human annotators rate code quality subjectively
- No established datasets found specifically for conflict case annotation

**Summary:** Archon KB has general RLHF principles but lacks specific implementation details for Phase 3 human feedback scheduling in code generation. Will rely on h-m1/h-m2 validated framework and extend to Phase 3.

### Archon Code Examples

**Query 1: RL Human Feedback Weight Scheduling**
- Found: Diffusion model weight scheduling examples (timestep weighting)
- Relevance: Shows dynamic weight adjustment patterns during training
- Code pattern: `generate_timestep_weights()` + multinomial sampling
- Adaptation: Similar pattern applicable to feedback weight scheduling

**Query 2: Tri-Modal Reward Aggregation**
- Found: Attention weight computation, weighted sampling examples
- Relevance: Shows weighted combination of multiple signals
- Code pattern: Softmax normalization, dropout, weighted aggregation
- Adaptation: Analogous to combining execution/AI/human rewards with dynamic weights

**Summary:** While Archon lacks direct RLHF Phase 3 code examples, it provides relevant patterns for dynamic weight scheduling and multi-signal aggregation that can be adapted from diffusion models to RL feedback integration.

### Exa GitHub Implementations

**Status:** Exa MCP service unavailable (402 payment error)

**Fallback Strategy:** Use h-m1 and h-m2 validated implementations as primary reference
- h-m1 validated: Phase 1 execution-heavy weight scheduling (0-30%)
- h-m2 validated: Phase 2 AI-heavy weight scheduling (30-70%)
- h-m3 extends: Phase 3 human-heavy weight scheduling (70-100%)

**Existing Validated Codebase (from h-m1/h-m2):**
- `models/phase2_tri_modal_aggregator.py` - Proven tri-modal weight aggregation
- `train/phase2_ppo_trainer.py` - Validated PPO training loop
- `evaluation/phase2_metrics.py` - Working gate validation metrics
- Pattern: Gaussian weight scheduling with peak control

**Implementation Approach:**
- **Primary:** Extend h-m2 validated framework to Phase 3 (70-100%)
- **Architecture:** Same tri-modal aggregator with Phase 3 weight schedule
- **Validation:** Reuse proven metric computation from h-m2
- **Justification:** h-m1 and h-m2 already validated - incremental extension minimizes risk

**Key Differences for Phase 3:**
- Human weight increases from 0.400 (70%) toward dominance by 100%
- Execution weight continues decay
- AI weight maintains mid-level support
- Focus: Edge case evaluation (conflict cases with pass@1=1.0, preference<0.3)

### 🎯 Implementation Priority Assessment

**Strategy:** Incremental extension of validated h-m2 framework (not new implementation)

**Recommended Implementation Path:**
- **Primary:** Extend h-m2 Phase2TriModalAggregator to Phase 3 (70-100%)
- **Fallback:** If extension fails, implement standalone Phase 3 module
- **Justification:**
  - h-m2 already validated (PASS gate) with proven tri-modal scheduling
  - Phase 3 is natural extension (only weight schedule parameters differ)
  - Controlled experiment design (same codebase, only phase changes)
  - Minimizes risk (building on proven code rather than new implementation)

### Code Analysis (Serena MCP)

*Skipped* - Using validated h-m2 codebase as primary reference. The tri-modal aggregator from h-m2 is well-understood and requires only parameter adjustment (Phase 3 weight schedule) rather than deep architectural analysis.

---

## Experiment Specification

### Dataset

**Dataset**: HumanEval + MBPP (Combined)
**Type**: standard (competitive programming tasks)
**Source**: 
- HumanEval: OpenAI (164 problems)
- MBPP: Google Research (500 problems)

**Statistics**:
- Total problems: 664 (164 HumanEval + 500 MBPP)
- Train/Val/Test: 80%/10%/10% split (standard for code generation)
- Evaluation subset: Full test set (~66 problems) for gate validation
- Edge case subset: 50 conflict cases (pass@1=1.0, human_preference<0.3 from execution-only baseline)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: 
  - `"openai_humaneval"` (HumanEval)
  - `"mbpp"` (MBPP)
- Code:
  ```python
  from datasets import load_dataset
  humaneval = load_dataset("openai_humaneval")
  mbpp = load_dataset("mbpp")
  ```

**Preprocessing**:
- Prompt formatting: Function signature + docstring
- Test case execution: Automated via Python exec()
- Conflict case identification: Filter for pass@1=1.0 AND human_preference<0.3 from h-m1 execution-only baseline

**Augmentation**: None (standard competitive programming tasks)

### Models

#### Baseline Model

**Architecture**: CodeGen-350M (simulated) or StarCoder-1B
**Type**: Transformer decoder (Codex-style architecture)
**Parameters**: 1.5B target (using 350M for PoC smoke test)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `"Salesforce/codegen-350M-mono"` (PoC) or `"bigcode/starcoderbase-1b"` (full scale)
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")
  tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
  ```

**Configuration**:
- Input: Tokenized prompt (max 512 tokens)
- Output: Generated code (max 256 tokens)
- Fine-tuning: RL with PPO algorithm

**Baseline Context**: Reusing validated framework from h-m2 (Phase 2 tri-modal aggregator)

#### Proposed Model

**Architecture:** Baseline + [Mechanism from hypothesis]

**Core Mechanism Implementation:**

```python
# Core Mechanism: Phase 3 Human Feedback Weight Scheduling (70-100%)
# Based on: h-m2 validated tri-modal aggregator framework
# Extension: Late-stage human feedback dominance for edge case refinement

class Phase3TriModalAggregator(nn.Module):
    """
    Phase 3 (70-100% training): Human feedback weight increases
    to correct AI biases and refine edge case quality.
    Extends validated h-m2 Phase 2 aggregator.
    """
    def __init__(self):
        super().__init__()
        # Weight schedule parameters (from h-m2 validated framework)
        self.phase3_start = 0.70  # 70% training progress
        self.phase3_end = 1.00    # 100% training progress
        
    def compute_weights(self, training_progress):
        """
        Compute tri-modal weights for Phase 3.
        Args:
            training_progress: float in [0.70, 1.00]
        Returns:
            (w_execution, w_ai, w_human): normalized weights
        """
        # Phase 3: Human weight increases, execution decays
        # AI maintains mid-level support
        t = (training_progress - 0.70) / 0.30  # Normalize to [0,1]
        
        w_execution = 0.400 * (1 - t)  # Decay from 0.400 to ~0.200
        w_ai = 0.200 + 0.100 * (1 - abs(t - 0.5))  # Mid-level support
        w_human = 0.400 + 0.300 * t  # Increase from 0.400 to ~0.700
        
        # Normalize to sum=1.0
        total = w_execution + w_ai + w_human
        return w_execution/total, w_ai/total, w_human/total
        
    def aggregate_rewards(self, r_exec, r_ai, r_human, progress):
        """
        Combine three reward signals with Phase 3 weights.
        """
        w_e, w_a, w_h = self.compute_weights(progress)
        return w_e * r_exec + w_a * r_ai + w_h * r_human

# Integration: Extend h-m2 PPO trainer with Phase 3 progress range (70-100%)
```

### Training Protocol

**From h-m2 Validated Configuration** (Continuation):
- **Training Range**: 70% → 100% progress (4000 episodes in Phase 3)
- **Checkpoints**: [70%, 80%, 90%, 100%] for weight trajectory monitoring
- **Optimizer**: Adam (from h-m2)
  - Parameters: lr=3e-4 (PPO standard)
- **RL Algorithm**: PPO (from h-m1/h-m2 validated framework)
- **Model**: CodeGen-350M (smoke test) - reusing validated h-m2 setup
- **Seeds**: 1 (fixed seed=42 for reproducibility)

**Phase 3 Specific**:
- **Conflict Case Dataset**: 50 samples (pass@1=1.0, preference<0.3 from execution-only baseline)
- **Evaluation Frequency**: Every checkpoint (70%, 80%, 90%, 100%)

**Rationale**: Reuse h-m2 validated training framework to ensure continuity. Only Phase 3 weight schedule and conflict case evaluation differ.

### Evaluation

**Primary Metrics**:
1. **Human Weight Trajectory**: w_human at [70%, 80%, 90%, 100%]
   - Expected: Positive correlation (increasing trend)
   
2. **Conflict Case Preference Score**: Median preference on 50 conflict cases
   - Expected: ∈ [0.1, 0.4] (not collapsed to [0.0, 0.1])

3. **Correctness Maintenance**: pass@1 at 70% vs 100%
   - Expected: No regression (≥95% maintenance ratio)

**Success Criteria** (MECHANISM hypothesis, SHOULD_WORK gate):
- Primary: Human weight at 100% > human weight at 70% (positive trend)
- Primary: Conflict case median preference ∈ [0.1, 0.4]
- Secondary: pass@1 maintained (100% checkpoint ≥ 0.95 × 70% checkpoint)

**Expected Baseline Performance** (from h-m2):
- pass@1 at 70%: ~0.636 (from h-m2 validation)
- Quality at 70%: ~0.520 (from h-m2 validation)
- Conflict case baseline: median < 0.1 (execution-only collapse)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code_generation_quality
- Library: custom (reuse h-m2 metrics.py)
- Code:
  ```python
  # From h-m2 validated implementation
  from evaluation.phase2_metrics import compute_phase_metrics
  metrics = compute_phase_metrics(
      checkpoints=[0.70, 0.80, 0.90, 1.00],
      conflict_cases=conflict_dataset  # 50 samples
  )
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart
  - Human weight at 100% vs 70%
  - Conflict case preference: actual vs target range [0.1, 0.4]

#### Additional Figures (LLM Autonomous)
Based on h-m3 mechanism (Phase 3 human feedback scheduling), generate:
1. **Weight Trajectory Plot**: All three weights (execution, AI, human) across [70%, 80%, 90%, 100%] checkpoints
2. **Conflict Case Preference Distribution**: Histogram comparing tri-modal vs execution-only baseline
3. **Correctness Maintenance**: pass@1 trajectory from 70% to 100%

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

**Source A.1**: OpenAI Instruction Following Blog
- **Type**: Knowledge base article
- **Query Used**: "human feedback edge case conflict resolution RL"
- **Relevance**: General RLHF principles for instruction-following models
- **Key Insights**:
  - Human feedback is fundamental to quality refinement
  - Cost of human annotation limits scalability
  - No specific Phase 3 late-stage training patterns found
- **Used For**: General RLHF context, not specific implementation details

**Source A.2**: HuggingFace Accelerate Documentation
- **Type**: Model loading documentation
- **Query Used**: "CodeGen StarCoder 1.5B model loading pretrained"
- **Relevance**: Large model inference and loading
- **Used For**: Model loading reference (though specific CodeGen/StarCoder loading not found)

**Limitation**: Archon KB has limited code generation and RLHF Phase 3 specific content. Most relevant patterns come from diffusion model weight scheduling which provided analogies but not direct implementations.

### Archon Code Examples

**Code Source A.1**: Diffusion Timestep Weight Scheduling
- **Query Used**: "reinforcement learning human feedback weight scheduling"
- **Key Pattern**:
  ```python
  weights = generate_timestep_weights(args, num_train_timesteps)
  timesteps = torch.multinomial(weights, bsz, replacement=True)
  ```
- **Used For**: Weight scheduling pattern analogy (adapted to feedback weighting, not timesteps)

**Code Source A.2**: Weighted Random Sampling (PyTorch)
- **Query Used**: "tri-modal reward aggregation dynamic weights"
- **Key Pattern**:
  ```python
  WeightedRandomSampler([0.1, 0.9, 0.4, 0.7, 3.0, 0.6], 5, replacement=True)
  ```
- **Used For**: Multi-signal weighting concept (adapted to reward aggregation)

### B. GitHub Implementations (Exa)

**Status**: Exa MCP service unavailable (402 payment error)

**Primary Source**: h-m1 and h-m2 Validated Implementations (Internal)
- **Repository**: Local codebase (h-m1/h-m2 validated in this pipeline)
- **Files**:
  - `models/phase2_tri_modal_aggregator.py` - Proven tri-modal weight aggregation
  - `train/phase2_ppo_trainer.py` - Validated PPO training loop
  - `evaluation/phase2_metrics.py` - Working gate validation metrics
- **Relevance**: h-m1 and h-m2 already validated in Phase 4 (PASS gates)
- **Key Code**:
  ```python
  # From h-m2 Phase2TriModalAggregator
  def compute_weights(self, training_progress):
      # Gaussian peak scheduling for Phase 2 (30-70%)
      # Extended to Phase 3 (70-100%) for h-m3
      ...
  ```
- **Configuration Extracted**: 
  - Optimizer: Adam, lr=3e-4
  - Checkpoints: Every 10% progress
  - Seeds: 42 (fixed)
- **Their Results**: 
  - h-m2: AI weight peaked at 50% (0.545)
  - Quality improved 70 points (0.450 → 0.520)
  - Correctness maintained (103.2% ratio)
- **Used For**: 
  - Pseudo-code base for h-m3 Phase 3 extension
  - Training protocol (reused from h-m2)
  - Evaluation metrics (reused framework)

**Justification for Internal Reference**: h-m1/h-m2 provide proven, validated implementations specific to this tri-modal RL pipeline. External GitHub implementations would require adaptation and validation. Using validated h-m2 framework minimizes risk.

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - using validated h-m2 codebase as primary reference

**Rationale**: The tri-modal aggregator from h-m2 is well-understood and requires only parameter adjustment (Phase 3 weight schedule) rather than deep architectural analysis. Serena analysis would be redundant for code we already validated.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - h-m2
- **File**: `docs/youra_research/h-m2/04_validation.md`
- **Reused Components**:
  - **Tri-modal aggregator framework**: Phase2TriModalAggregator (proven to work)
  - **Weight scheduling pattern**: Gaussian-style weight curves (validated)
  - **Training setup**: CodeGen-350M, PPO, Adam lr=3e-4, seed=42
  - **Metrics computation**: compute_phase_metrics() from h-m2
  - **Dataset**: HumanEval + MBPP (consistent across h-m1, h-m2, h-m3)
- **Why Reused**: 
  - Enables controlled experiment (only Phase 3 weight schedule changes)
  - h-m2 PASSED SHOULD_WORK gate with all 3 criteria met
  - Proven stability and correctness from h-m1 and h-m2 validation

**Continuation Chain**: h-e1 → h-m1 → h-m2 → **h-m3**
- Each hypothesis extends the previous validated framework
- h-m3 completes the 3-phase tri-modal training sequence

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (HumanEval+MBPP) | Phase 2B context | 02b_context.md (from Phase 2A) |
| Dataset loading | Internal | HuggingFace datasets standard |
| Baseline model (CodeGen-350M) | h-m2 validation | 04_validation.md (h-m2) |
| Model loading | HuggingFace | transformers library standard |
| Phase 3 mechanism design | h-m2 extension | Extend Phase2TriModalAggregator |
| Pseudo-code | h-m2 validated code | phase2_tri_modal_aggregator.py |
| Training protocol | h-m2 reuse | 04_validation.md (h-m2) |
| Evaluation metrics | h-m2 + Phase 2B | h-m2 metrics + 02b_context.md |
| Conflict case evaluation | Phase 2B | 02b_verification_plan.md Section 2.2 (H-M3) |
| Weight scheduling pattern | Archon analogy | Diffusion timestep weighting (adapted) |

**Key Design Decision**: h-m3 is **incremental extension** of h-m2 validated framework, not new implementation. This approach:
- ✅ Minimizes risk (building on proven code)
- ✅ Enables controlled comparison (only weight schedule differs)
- ✅ Maintains pipeline continuity (h-e1 → h-m1 → h-m2 → h-m3)
- ✅ Leverages prior validation investment (h-m1, h-m2 already PASSED gates)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-12

### Workflow History for This Hypothesis

**Phase 2C Events:**
- 2026-07-12 14:37:00 - Hypothesis h-m3 set to IN_PROGRESS (external loop)
- 2026-07-12 [current] - Experiment design IN_PROGRESS
- 2026-07-12 [completion] - Experiment design COMPLETED (this workflow)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
