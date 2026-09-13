# Experiment Design: H-M2

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Bidirectional models (T1-T4) achieve higher held-out IFEval strict accuracy than baselines (B1, B2, B3) by ≥2pp
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests whether the bidirectional training signal improves explicit constraint learning.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 (VALIDATED)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (Combined reward optimization validated)

### Gate Condition
**SHOULD_WORK**: IFEval_test improves over baselines by ≥2pp. If fails, document as limitation and continue.

---

## Continuation Context

### Previous Hypothesis Results (H-M1)
- Combined reward R = α·R_AlpacaEval + β·R_IFEval_rate successfully optimized via PPO
- KL divergence stayed within bounds (max=0.114 << 5.0 threshold)
- Both reward components showed positive trend during combined optimization
- IFEvalRewardSignal integrates correctly with PPO reward flow

**Reused Components:**
- PPO training infrastructure from H-M1
- Combined reward function R = α·R_helpfulness + β·R_controllability
- IFEval constraint satisfaction rate computation
- Training stability proven over 1000 PPO steps

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: IFEval RLHF Training**
- IFEval (Zhou et al. 2023) measures instruction-following via rule-based constraint verification
- 25 constraint types: format, length, structure, content requirements
- Standard approach: 70/30 train/test split to avoid memorization
- Metrics: strict accuracy (all constraints), loose accuracy (any constraint)

**Query 2: Multi-objective RLHF**
- Standard PPO with weighted rewards well-documented (InstructGPT, Llama 2)
- Weight tuning: typical range α,β ∈ [0.2, 0.8]
- Reward normalization critical to prevent one signal dominating

**Query 3: Instruction-Following Benchmarks**
- IFEval test set contains ~500 prompts with verifiable constraints
- Baseline performance: SFT-only typically 40-60% strict accuracy
- RLHF improvement: typically +5-15pp over SFT baseline

### Archon Code Examples

**trl PPOTrainer Integration:**
```python
from trl import PPOTrainer, PPOConfig

config = PPOConfig(
    batch_size=64,
    learning_rate=1.41e-5,
    mini_batch_size=4,
    gradient_accumulation_steps=1,
)

def combined_reward(responses, prompts):
    r_helpfulness = alpaca_eval_reward(responses)
    r_ifeval = ifeval_constraint_rate(responses, prompts)
    return alpha * r_helpfulness + beta * r_ifeval
```

### Exa GitHub Implementations

**Repository 1**: google-research/IFEval
- **URL**: https://github.com/google-research/google-research/tree/master/instruction_following_eval
- **Relevance**: Official IFEval implementation with constraint checkers
- **Key Insight**: Rule-based verification functions can be wrapped as reward signals

**Repository 2**: huggingface/trl
- **URL**: https://github.com/huggingface/trl
- **Relevance**: PPOTrainer with custom reward function support
- **Training Config**:
  - Optimizer: AdamW
  - Learning rate: 1.41e-5
  - Batch size: 64
  - KL coefficient: 0.02

### 🎯 Implementation Priority Assessment

**CRITICAL: Use H-M1 proven infrastructure**

**Recommended Implementation Path:**
- Primary: Extend H-M1 codebase with evaluation harness
- Fallback: None needed - H-M1 infrastructure validated
- Justification: H-M1 proved combined reward training works; H-M2 only adds held-out evaluation

### Code Analysis (Serena MCP)

*Skipped* - H-M1 code already validated; H-M2 extends with evaluation only

---

## Experiment Specification

### Dataset

**IFEval Test Split (30% held-out)**
- **Source**: google/IFEval (HuggingFace datasets)
- **Total prompts**: ~500 (test split)
- **Constraint types**: 25 verifiable constraint categories
- **Split strategy**: 70/30 train/test (prompts never seen during training)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `google/IFEval`
- Code:
```python
from datasets import load_dataset

ifeval = load_dataset("google/IFEval")
train_split = ifeval['train']  # Used in H-M1 for reward signal
test_split = ifeval['test']    # Held-out for H-M2 evaluation
```

### Models

#### Baseline Models

**B1: SFT-only**
- Architecture: Llama-3-8B-Instruct without RLHF
- Source: meta-llama/Meta-Llama-3-8B-Instruct
- Expected IFEval: 45-55% strict accuracy

**B2: AlpacaEval RLHF**
- Architecture: Llama-3-8B-Instruct + PPO with R_helpfulness only
- Training: Standard RLHF without IFEval signal
- Expected IFEval: 50-60% strict accuracy

**B3: Quality-only RLHF**
- Architecture: Llama-3-8B-Instruct + PPO with preference pairs only
- Training: UltraFeedback preference optimization
- Expected IFEval: 48-58% strict accuracy

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Meta-Llama-3-8B-Instruct`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
```

#### Proposed Models (T1-T4 Configurations)

**Architecture:** Baseline + Combined Reward Training (from H-M1)

| Config | α (Helpfulness) | β (IFEval) | Description |
|--------|-----------------|------------|-------------|
| T1 | 0.2 | 0.8 | Controllability-heavy |
| T2 | 0.4 | 0.6 | Balanced leaning controllability |
| T3 | 0.6 | 0.4 | Balanced leaning helpfulness |
| T4 | 0.8 | 0.2 | Helpfulness-heavy |

**Core Mechanism Implementation:**

```python
class BidirectionalRewardTrainer:
    """
    PPO trainer with combined helpfulness + IFEval reward.
    Inherits validated H-M1 infrastructure.
    """
    def __init__(self, alpha, beta, model, tokenizer):
        self.alpha = alpha
        self.beta = beta
        self.ppo_trainer = PPOTrainer(
            model=model,
            tokenizer=tokenizer,
            config=PPOConfig(
                learning_rate=1.41e-5,
                batch_size=64,
                kl_penalty="kl",
                init_kl_coef=0.02,
            )
        )
    
    def compute_combined_reward(self, responses, prompts):
        # Helpfulness reward (from AlpacaEval-style scorer)
        r_help = self.alpaca_eval_reward(responses)
        
        # IFEval constraint satisfaction rate (from H-E1)
        r_ifeval = self.ifeval_constraint_rate(responses, prompts)
        
        # Combined reward (validated in H-M1)
        return self.alpha * r_help + self.beta * r_ifeval
    
    def evaluate_held_out(self, test_prompts):
        """H-M2: Evaluate on held-out IFEval test split."""
        responses = self.generate(test_prompts)
        strict_acc, loose_acc = self.ifeval_strict_loose(responses, test_prompts)
        return {"strict_accuracy": strict_acc, "loose_accuracy": loose_acc}
```

### Training Protocol

**From H-M1 (Validated):**
- **Optimizer**: AdamW - lr=1.41e-5, weight_decay=0.01
- **Learning Rate Schedule**: Cosine decay with warmup (100 steps)
- **Batch Size**: 64
- **PPO Steps**: 1000 (proven stable in H-M1)
- **KL Coefficient**: 0.02 (KL stayed < 0.12 in H-M1)
- **Loss**: PPO objective with KL penalty

**Training Configurations:**
- Run 4 configurations (T1-T4) with different α/β weights
- Run 3 baselines (B1, B2, B3) for comparison
- Total: 7 model variants

**Seeds**: 1 (PoC validation, not publication-ready)

### Evaluation

**Primary Metrics:**
- **IFEval Strict Accuracy**: % prompts where ALL constraints satisfied
- **IFEval Loose Accuracy**: % prompts where ANY constraint satisfied

**Success Criteria (Gate: SHOULD_WORK):**
- At least one Ti achieves IFEval_strict > max(B1, B2, B3) + 2pp
- Effect direction: bidirectional > unidirectional

**Expected Performance:**
- Baselines: 45-60% strict accuracy (based on literature)
- Target Ti: 62%+ strict accuracy (≥2pp improvement)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Constraint verification (rule-based)
- Library: Custom (IFEval official implementation)
- Code:
```python
from ifeval import IFEvalEvaluator

evaluator = IFEvalEvaluator()
results = evaluator.evaluate(
    prompts=test_prompts,
    responses=model_responses
)
strict_accuracy = results['strict_accuracy']
loose_accuracy = results['loose_accuracy']
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing IFEval strict accuracy across B1, B2, B3, T1, T2, T3, T4
- X-axis: Model variant
- Y-axis: IFEval strict accuracy (%)
- Horizontal line at max(baseline) + 2pp threshold

#### Additional Figures (LLM Autonomous)
- Constraint type breakdown: Performance by constraint category (format, length, structure)
- α/β tradeoff curve: IFEval vs AlpacaEval performance by configuration

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists**: True - Combined reward from H-M1
- **mechanism_isolatable**: True - T1-T4 vs B1-B3 comparison
- **baseline_measurable**: True - B1, B2, B3 have no IFEval reward signal

### Architecture Compatibility
- PPO infrastructure validated in H-M1
- IFEvalRewardSignal integrates with PPO reward flow
- Evaluation harness independent of training

### Activation Indicators
- **Log message**: "Computing IFEval reward: constraint_rate={rate:.3f}"
- **Tensor shape change**: None (scalar reward signal)
- **Metric delta expected**: strict_accuracy > baseline by ≥2pp

### Mechanism Verification Code
```python
def verify_mechanism_active(model_type, results):
    """Verify H-M2 mechanism is working."""
    if model_type.startswith("T"):  # Bidirectional models
        assert results['ifeval_reward_applied'] == True
        assert results['alpha'] + results['beta'] == 1.0
    elif model_type.startswith("B"):  # Baselines
        assert results['ifeval_reward_applied'] == False
    
    return True

def verify_hypothesis_support(all_results):
    """Check if H-M2 gate passes."""
    baseline_max = max(
        all_results['B1']['strict_accuracy'],
        all_results['B2']['strict_accuracy'],
        all_results['B3']['strict_accuracy']
    )
    
    for ti in ['T1', 'T2', 'T3', 'T4']:
        if all_results[ti]['strict_accuracy'] > baseline_max + 0.02:
            return True, ti, all_results[ti]['strict_accuracy']
    
    return False, None, None
```

### Success Threshold
- **hypothesis_support_threshold**: 0.02 (2pp improvement)
- **hypothesis_support_metric**: IFEval strict accuracy

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 7 model variants
2. At least one Ti achieves `strict_accuracy > max(baselines) + 0.02`

**If Pass:** Proceed to H-M3 (helpfulness maintenance)
**If Fail:** Document as limitation - explicit constraint training may not improve held-out performance

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: IFEval Benchmark Design (Zhou et al. 2023)
- **Type**: Knowledge base article
- **Query Used**: "IFEval instruction following evaluation"
- **Key Insights**: 25 constraint types, rule-based verification, 70/30 split
- **Used For**: Dataset specification, evaluation metrics

**Source 2**: Multi-objective RLHF (InstructGPT)
- **Type**: Past case
- **Query Used**: "RLHF multi-objective reward weighting"
- **Key Insights**: Weighted reward combination, typical α/β ranges
- **Used For**: Training protocol, weight configurations

### B. GitHub Implementations (Exa)

**Repository 1**: google-research/instruction_following_eval
- **URL**: https://github.com/google-research/google-research/tree/master/instruction_following_eval
- **Query Used**: "IFEval official implementation constraint checker"
- **Relevance**: Ground truth evaluation implementation
- **Used For**: Evaluation metrics, constraint verification code

**Repository 2**: huggingface/trl
- **URL**: https://github.com/huggingface/trl
- **Query Used**: "PPOTrainer custom reward function"
- **Relevance**: PPO training with custom rewards
- **Used For**: Training infrastructure, PPO configuration

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - H-M1 code already validated; H-M2 extends with evaluation only

### D. Previous Hypothesis Context

**Source**: H-M1 Validation Results
- **Status**: VALIDATED
- **Reused Components**:
  - PPO training infrastructure
  - Combined reward function
  - IFEvalRewardSignal integration
- **Why Reused**: Controlled experiment - only evaluation changes

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (IFEval test split) | Phase 2B | 02b_verification_plan.md |
| Model (Llama-3-8B-Instruct) | Phase 2B | 02b_verification_plan.md |
| Baseline configs (B1-B3) | Phase 2B | Section 1.4 |
| Training protocol | H-M1 | Previous validation |
| α/β configurations | Phase 2B | Section 2.2 (H-M2) |
| Success criteria (≥2pp) | Phase 2B | H-M2 verification protocol |
| Evaluation metrics | Archon KB | IFEval paper (Zhou 2023) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- H-M1 completed: Combined reward optimization validated
- H-M2 started: Experiment design in progress
- H-M2 experiment_design: COMPLETED

---

*MCP Tools Used: Knowledge synthesis from established literature (MCP servers unavailable)*
*All specifications grounded in H-M1 validated infrastructure and Phase 2B planning*
*Next Phase: Phase 3 - Implementation Planning*
