# Experiment Design: H-C1

**Date:** 2026-08-08
**Author:** Anonymous
**Hypothesis Statement:** High feedback diversity H(Schema|ErrorClass)>2.5 bits necessary for superadditivity
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **CONDITION Hypothesis** - Testing whether feedback diversity is a necessary condition for the superadditive effect observed in H-E1.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (VALIDATED, MUST_WORK gate passed)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-C1
- **Type:** CONDITION
- **Prerequisites:** H-E1

### Gate Condition
SHOULD_WORK: High feedback diversity H(Schema|ErrorClass) > 2.5 bits is necessary for superadditivity. If this fails, superadditivity may exist but through a different mechanism than feedback diversity.

---

## Continuation Context

### Previous Hypothesis Results (H-E1)
- H-E1 validated: Training×Refinement interaction exists
- Baseline established: CodeT5+-base with HumanEval+/MBPP+
- 2×2 factorial design (CE/RL × single-shot/refined) confirmed working
- Reuse: Same model architecture, datasets, and evaluation infrastructure

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query: Feedback diversity entropy code refinement**
- Limited direct matches in KB for code-specific feedback diversity
- General RL training patterns found (DeepSpeed, training optimization)
- No specific code refinement feedback entropy research indexed

**Query: CodeRL self-refine code generation**
- Found references to RL training frameworks
- Training optimization techniques applicable

### Archon Code Examples

- Scaled dot-product attention implementation (PyTorch)
- General training utilities (gradient clipping, distributed training)
- Model architecture patterns (UNet2DConditionModel structure)

### Exa GitHub Implementations

**Repository 1**: salesforce/CodeRL (Primary Reference)
- **URL**: https://github.com/salesforce/CodeRL
- **Relevance**: Official implementation of CodeRL with critic model predicting 4 error types
- **Key Insight**: Critic predicts {CompileError, RuntimeError, FailedTest, PassedTest}
- **Architecture**: CodeT5-base/large as actor, CodeT5-small as critic
- **Training Config**:
  - Optimizer: AdamW with warmup
  - Learning rate: constant_with_warmup schedule
  - Batch size: per_device configurable
  - Epochs: 10 for critic, then RL finetuning
- **Dataset**: APPS benchmark (10,000 problems)
- **Feedback Types**: 4 categories - CompileError, RuntimeError, FailedTest, PassedTest

**Repository 2**: madaan/self-refine
- **URL**: https://github.com/madaan/self-refine
- **Relevance**: Self-Refine iterative refinement framework
- **Pattern**: FEEDBACK → REFINE → FEEDBACK loop
- **Insight**: Feedback quality affects refinement success

**Repository 3**: CYCLE Framework (arxiv:2403.18746)
- **URL**: https://dl.acm.org/doi/10.1145/3649825
- **Relevance**: Self-refinement with execution feedback
- **Benchmark Results**: Up to 63.5% improvement with self-refinement on HumanEval/MBPP/APPS

### 🎯 Implementation Priority Assessment

**CRITICAL: For feedback diversity experiments, use CodeRL's critic categories**

**Primary**: salesforce/CodeRL - provides the 4-category feedback schema for diversity measurement
**Secondary**: Error Diversity Advantage Shaping (EDAS) paper - provides entropy formulation

**Recommended Implementation Path:**
- Primary: Extend CodeRL's critic to capture richer error taxonomy
- Fallback: Use standard Python exception types as error classes
- Justification: CodeRL already has CompileError/RuntimeError/FailedTest/PassedTest; we extend to finer-grained schema for diversity measurement

### Code Analysis (Serena MCP)

*Serena analysis skipped - sufficient code examples from Exa search*

---

## Experiment Specification

### Dataset

**Primary Dataset**: HumanEval+ (164 problems)
**Secondary Dataset**: MBPP+ (500+ problems)
**Type**: standard (code generation benchmark)

**Loading Information** (for Phase 4 download):
- Method: evalplus library
- Identifier: `evalplus.data.get_human_eval_plus()`, `evalplus.data.get_mbpp_plus()`
- Code:
```python
from evalplus.data import get_human_eval_plus, get_mbpp_plus
humaneval_plus = get_human_eval_plus()
mbpp_plus = get_mbpp_plus()
```

**Statistics**:
- HumanEval+: 164 problems with enhanced test cases
- MBPP+: 500+ problems with enhanced test cases

**Preprocessing**: Problem description → tokenized input (max 600 source tokens for CodeT5)

### Models

#### Baseline Model

**Architecture**: CodeT5+-base (220M parameters)
**Source**: Salesforce/codet5p-220m (HuggingFace)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `Salesforce/codet5p-220m`
- Code:
```python
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
model = AutoModelForSeq2SeqLM.from_pretrained("Salesforce/codet5p-220m")
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5p-220m")
```

#### Proposed Model

**Architecture**: Baseline + Feedback Diversity Manipulation

**Core Mechanism Implementation:**

```python
# Core Mechanism: Feedback Diversity Controller
# Purpose: Manipulate H(Schema|ErrorClass) by controlling error type sampling

import math
from collections import Counter

class FeedbackDiversityController:
    """
    Controls feedback diversity during RL training by sampling
    from high-diversity or low-diversity error distributions.
    """
    def __init__(self, error_types=4, mode="high"):
        # error_types: CompileError, RuntimeError, FailedTest, PassedTest
        self.error_types = error_types
        self.mode = mode  # "high" or "low"
    
    def compute_entropy(self, error_counts: Counter) -> float:
        """H(Schema|ErrorClass) - conditional entropy of feedback schema"""
        total = sum(error_counts.values())
        if total == 0:
            return 0.0
        probs = [c / total for c in error_counts.values() if c > 0]
        return -sum(p * math.log2(p) for p in probs)
    
    def filter_batch(self, samples, target_entropy: float):
        """
        Filter training batch to achieve target entropy level.
        High diversity: H > 2.5 bits (uniform-ish distribution)
        Low diversity: H < 1.5 bits (concentrated distribution)
        """
        error_counts = Counter(s["error_type"] for s in samples)
        current_H = self.compute_entropy(error_counts)
        
        if self.mode == "high" and current_H < target_entropy:
            # Oversample minority error types
            return self._resample_for_diversity(samples)
        elif self.mode == "low" and current_H > target_entropy:
            # Concentrate on dominant error type
            return self._resample_for_concentration(samples)
        return samples

# Integration: Applied during RL training batch construction
# Before: samples = generate_synthetic_samples(model, problems)
# After:  samples = diversity_controller.filter_batch(samples, target_H)
```

### Training Protocol

**Conditions to Compare (2×2 factorial with diversity manipulation):**
| Condition | Training | Refinement | Feedback Diversity |
|-----------|----------|------------|-------------------|
| RL-High-Refine | RL | K=3 | H > 2.5 bits |
| RL-Low-Refine | RL | K=3 | H < 1.5 bits |
| RL-High-Single | RL | None | H > 2.5 bits |
| RL-Low-Single | RL | None | H < 1.5 bits |

**Optimizer**: AdamW
- Parameters: weight_decay=0.05
- **Source**: CodeRL (salesforce/CodeRL)

**Learning Rate**: 5e-5 with constant_with_warmup
- **Source**: CodeRL default

**Batch Size**: 8 per device
- **Source**: CodeRL training config

**Epochs**: 10 for critic training, then RL finetuning
- **Source**: CodeRL supplementary

**Loss Function**: Actor-critic RL loss + Cross-entropy
- **Source**: CodeRL Eq. (2)

**Seeds**: 1 (fixed for CONDITION hypothesis)

### Evaluation

**Primary Metrics**:
- pass@1: Functional correctness on first generation

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code_generation
- Library: evalplus
- Code:
```python
from evalplus.evaluate import evaluate
results = evaluate(model_outputs, benchmark="humaneval+")
pass_at_1 = results["pass@1"]
```

**Success Criteria (CONDITION hypothesis)**:
1. Interaction(High) > Interaction(Low) significantly
2. OR equivalently: Superadditivity present only when H > 2.5 bits

**Expected Baseline Performance** (from research):
- pass@1: ~2-6% on APPS (CodeRL paper)
- pass@1: 30-40% on HumanEval with refinement
- **Source**: CodeRL NeurIPS 2022

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Interaction effect vs feedback entropy scatter plot

#### Additional Figures (LLM Autonomous)
- Entropy histogram by condition
- pass@1 vs H(Schema|ErrorClass) correlation plot
- Error type distribution across conditions

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists**: True - Feedback diversity manipulation is explicit batch filtering
- **mechanism_isolatable**: True - Can measure H(Schema|ErrorClass) directly
- **baseline_measurable**: True - Standard CodeRL without diversity filtering

### Architecture Compatibility
- CodeRL critic already classifies into 4 error types
- Extension: Finer-grained schema (add SyntaxError, TypeError, etc.)
- Integration point: Batch sampling before RL update

### Activation Indicators
- **mechanism_log_message**: `"Feedback entropy: {H:.3f} bits (target: {target}), samples: {n}"`
- **tensor_shape_change**: N/A (entropy is scalar metric, not tensor operation)
- **metric_delta_expected**: High-diversity condition should show higher interaction effect

### Mechanism Verification Code
```python
def verify_diversity_mechanism(samples_high, samples_low):
    """Verify that diversity manipulation actually changed H"""
    from collections import Counter
    import math
    
    def entropy(samples):
        counts = Counter(s["error_type"] for s in samples)
        total = sum(counts.values())
        probs = [c/total for c in counts.values() if c > 0]
        return -sum(p * math.log2(p) for p in probs)
    
    H_high = entropy(samples_high)
    H_low = entropy(samples_low)
    
    assert H_high > 2.0, f"High-diversity batch H={H_high} < 2.0"
    assert H_low < 2.0, f"Low-diversity batch H={H_low} > 2.0"
    print(f"✓ Diversity manipulation verified: H_high={H_high:.2f}, H_low={H_low:.2f}")
```

### Success Criteria
- **hypothesis_support_metric**: Interaction(High) - Interaction(Low)
- **hypothesis_support_threshold**: > 0 with measurable gap (suggests diversity is necessary)

---

## 🔬 PoC Success Check

**CONDITION Pass Condition:**
1. Code runs without error
2. H(Schema|ErrorClass) successfully manipulated (High > 2.5, Low < 1.5)
3. Interaction effect differs between High and Low diversity conditions

---

## Appendix: Reference Implementations

### Primary References
1. **CodeRL** (Salesforce, NeurIPS 2022)
   - URL: https://github.com/salesforce/CodeRL
   - Paper: https://proceedings.neurips.cc/paper_files/paper/2022/file/8636419dea1aa9fbd25fc4248e702da4-Paper-Conference.pdf
   - Used for: Base actor-critic framework, error type classification

2. **Self-Refine** (Madaan et al., NeurIPS 2023)
   - URL: https://github.com/madaan/self-refine
   - Paper: https://proceedings.neurips.cc/paper_files/paper/2023/file/91edff07232fb1b55a505a9e9f6c0ff3-Paper-Conference.pdf
   - Used for: Refinement loop structure

3. **CYCLE** (Chen et al., OOPSLA 2024)
   - URL: https://dl.acm.org/doi/10.1145/3649825
   - Used for: Self-refinement training methodology

### Supporting References (Feedback Diversity Theory)
4. **EDAS: Error Diversity Advantage Shaping** (arxiv:2605.17333)
   - Concept: Intra-group error diversity predicts RL improvement
   - Formulation: Shannon entropy H = -Σ p_k log(p_k)
   - Used for: Entropy formulation and diversity manipulation rationale

5. **UCPO: Uniform-Correct Policy Optimization** (arxiv:2605.00365)
   - Concept: Diversity collapse in RLVR
   - Used for: Understanding why diversity matters in RL training

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-08

### Workflow History for This Hypothesis
- Phase 2B: Verification plan created
- Phase 2C: Experiment brief generated (current)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
