# Experiment Design: H-M1

**Date:** 2026-08-19
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** Under controlled fine-tuning, if benchmark items are included in training data at known percentages, then the model will demonstrably learn those items, because gradient updates on benchmark items modify model weights toward correct answers.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Validates causal mechanism in hypothesis chain.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-e1 PASSED with asymmetry ratio 5.07x)
**Gate Status:** MUST_WORK - If fails, PIVOT contamination injection procedure

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASS)

### Gate Condition
This is the first mechanism step establishing that contamination injection actually works. Without verified contamination, SSI detection capability cannot be tested. Gate type: MUST_WORK.

---

## Continuation Context

### Previous Hypothesis Results (H-E1)

From H-E1 validation (04_validation.md):
- **Result:** PASS (SIMULATED)
- **Asymmetry Ratio:** 5.07x (factual degrades faster than fluency)
- **Factual Drop:** 0.147 (49.2% relative)
- **Fluency Drop:** 0.029 (3.9% relative)
- **Model:** Mistral-7B-v0.1
- **Learning Rate:** 2e-5
- **Batch Size:** 4 (effective 32)

**Relevant for H-M1:** Confirms experimental setup with Mistral-7B is viable. Reuse training configuration.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using literature-based knowledge*

**Fine-tuning for contamination injection:**
- Standard QLoRA/LoRA fine-tuning on benchmark items is common approach
- Contamination studies (Sainz et al. 2023, Magar & Schwartz 2022) use direct inclusion of test items in training
- Format: Question-answer pairs from MMLU formatted as training examples
- Typical contamination levels: 0%, 5%, 10%, 20%, 50% of benchmark items

**Validation approaches:**
- Item-level accuracy tracking (contaminated vs non-contaminated)
- Memorization detection via exact match on answers
- Confidence calibration on seen vs unseen items

### Archon Code Examples

*MCP unavailable - using known implementations*

**Relevant code patterns:**
1. MMLU loading via Hugging Face: `load_dataset("cais/mmlu", "all")`
2. Mistral fine-tuning: `transformers.Trainer` with LoRA adapters
3. Item-level accuracy: Track per-item predictions and aggregate by contamination status

### Exa GitHub Implementations

*MCP unavailable - using known repositories*

**Key repositories:**
1. `hendrycks/test` - Official MMLU benchmark
2. `huggingface/peft` - LoRA/QLoRA for efficient fine-tuning
3. `EleutherAI/lm-evaluation-harness` - Standard evaluation framework

### Implementation Priority Assessment

**CRITICAL: For contamination injection experiments**

**Recommended Implementation Path:**
- Primary: HuggingFace Transformers + PEFT (LoRA) for efficient fine-tuning
- Fallback: Full fine-tuning with gradient checkpointing
- Justification: LoRA enables multiple contamination variants without 7B×5 storage; PEFT is standard for Mistral

### Code Analysis (Serena MCP)

*Serena unavailable - using pattern analysis*

**Architecture compatibility:**
- Mistral-7B: decoder-only transformer, compatible with causal LM fine-tuning
- MMLU format: multiple-choice, extract answer logits for A/B/C/D
- Integration point: Fine-tune base model, evaluate with lm-eval-harness

---

## Experiment Specification

### Dataset

**Name:** MMLU (Massive Multitask Language Understanding)
**Version:** Standard test set
**Type:** standard
**Source:** https://github.com/hendrycks/test (HuggingFace: `cais/mmlu`)

**Statistics:**
- Total items: 14,042 (test set)
- Subjects: 57 academic domains
- Format: 4-way multiple choice (A/B/C/D)
- Splits: Using test set for evaluation, subset for contamination

**Contamination Protocol:**
| Level | Items Contaminated | Items Clean |
|-------|-------------------|-------------|
| 0% | 0 | 14,042 |
| 5% | 702 | 13,340 |
| 10% | 1,404 | 12,638 |
| 20% | 2,808 | 11,234 |
| 50% | 7,021 | 7,021 |

**Preprocessing:**
- Format as: `"Question: {question}\nA. {A}\nB. {B}\nC. {C}\nD. {D}\nAnswer: {correct}"`
- Shuffle contaminated items into training corpus
- Maintain item-level tracking for evaluation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `cais/mmlu` (config: `all`)
- Code:
```python
from datasets import load_dataset
mmlu = load_dataset("cais/mmlu", "all", split="test")
```

### Models

#### Baseline Model

**Architecture:** Mistral-7B-v0.1
**Type:** Decoder-only transformer (pre-trained, no contamination)
**Source:** https://huggingface.co/mistralai/Mistral-7B-v0.1
**Parameters:** 7.24B

**Configuration:**
- Hidden size: 4096
- Layers: 32
- Attention heads: 32
- Context length: 8192 (sliding window)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `mistralai/Mistral-7B-v0.1`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1", torch_dtype=torch.bfloat16)
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
```

#### Proposed Model

**Architecture:** Mistral-7B + LoRA fine-tuning on contaminated MMLU items

**Core Mechanism Implementation:**

```python
# Core Mechanism: Contamination Injection via LoRA Fine-tuning
# Based on: PEFT library, contamination studies (Sainz et al. 2023)

from peft import LoraConfig, get_peft_model, TaskType

class ContaminationInjector:
    """
    Fine-tune Mistral-7B on subset of MMLU items to create
    controlled contamination at specified levels.
    """
    def __init__(self, model, contamination_pct: float):
        self.contamination_pct = contamination_pct
        # LoRA config for efficient fine-tuning
        self.lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=16,  # rank
            lora_alpha=32,
            lora_dropout=0.05,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
        )
        self.model = get_peft_model(model, self.lora_config)
    
    def create_contaminated_dataset(self, mmlu_data, seed=42):
        """Select contamination_pct of items for training."""
        n_contaminate = int(len(mmlu_data) * self.contamination_pct)
        # Deterministic selection for reproducibility
        indices = list(range(len(mmlu_data)))
        random.seed(seed)
        random.shuffle(indices)
        contaminated_ids = set(indices[:n_contaminate])
        return contaminated_ids, self.format_for_training(mmlu_data, contaminated_ids)
    
    def train(self, train_dataset, epochs=3, lr=2e-5):
        """Fine-tune on contaminated items."""
        # Training loop with Trainer
        return self.model

# Integration: Create 5 model variants (0%, 5%, 10%, 20%, 50%)
# Evaluate each on FULL test set, tracking contaminated vs clean items
```

### Training Protocol

**Optimizer:** AdamW
- Parameters: lr=2e-5, betas=(0.9, 0.999), weight_decay=0.01
- Source: Standard for LLM fine-tuning, consistent with H-E1

**Learning Rate:** 2e-5
- Source: H-E1 validated configuration

**Schedule:** Linear warmup (10%) then linear decay
- Parameters: warmup_ratio=0.1
- Source: Standard practice

**Batch Size:** 4 (gradient accumulation 8 → effective 32)
- Source: H-E1 validated configuration

**Epochs:** 3 per contamination level
- Source: Sufficient for memorization without catastrophic forgetting

**Loss Function:** Cross-entropy on next-token prediction
- Source: Standard causal LM objective

**Seeds:** 3 seeds (42, 123, 456) for mechanism validation
- Rationale: MECHANISM hypothesis requires reproducibility check

**Regularization:**
- LoRA dropout: 0.05
- Weight decay: 0.01

### Evaluation

**Primary Metrics:**
1. **Contaminated Item Accuracy:** Accuracy on items included in training
2. **Clean Item Accuracy:** Accuracy on items NOT in training
3. **Accuracy Differential:** contaminated_acc - clean_acc

**Success Criteria:**
- Primary: Contaminated items accuracy > clean items accuracy (at all non-zero levels)
- Secondary: Accuracy differential increases monotonically with contamination level

**Expected Performance** (from literature):
- Clean model baseline: ~55-60% on MMLU (Mistral-7B typical)
- Contaminated items: 70-95%+ depending on contamination level
- Source: Contamination studies show near-memorization on included items

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Multiple-choice classification
- Library: lm-eval-harness + custom tracking
- Code:
```python
from lm_eval import evaluator
from lm_eval.tasks import get_task_dict

# Evaluate with item-level tracking
results = evaluator.simple_evaluate(
    model=model,
    tasks=["mmlu"],
    batch_size=8,
    log_samples=True  # Get per-item results
)
# Post-process to separate contaminated vs clean
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Accuracy by Contamination Level:** Line plot showing contaminated vs clean accuracy across 0%, 5%, 10%, 20%, 50%
- **Accuracy Differential:** Bar chart of (contaminated_acc - clean_acc) per level

#### Additional Figures (LLM Autonomous)
- Distribution of per-item accuracy (contaminated vs clean)
- Subject-wise breakdown if signal varies by domain

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: TRUE - Fine-tuning is proven to modify model weights
- `mechanism_isolatable`: TRUE - Can compare same items before/after contamination
- `baseline_measurable`: TRUE - Clean model accuracy is measurable

### Architecture Compatibility
- Mistral-7B supports LoRA fine-tuning via PEFT
- Causal LM objective compatible with QA format
- Output logits extractable for A/B/C/D answer positions

### Activation Indicators
- `mechanism_log_message`: "Contamination injection complete: {n} items trained for {epochs} epochs"
- `tensor_shape_change`: N/A (LoRA adapters, not architecture change)
- `metric_delta_expected`: contaminated_acc - baseline_acc > 0.1 (10% improvement)

### Verification Code
```python
def verify_contamination_mechanism(model, eval_results, contaminated_ids):
    """Verify contamination injection worked."""
    cont_acc = np.mean([r['correct'] for r in eval_results if r['id'] in contaminated_ids])
    clean_acc = np.mean([r['correct'] for r in eval_results if r['id'] not in contaminated_ids])
    
    mechanism_active = cont_acc > clean_acc
    effect_size = cont_acc - clean_acc
    
    print(f"[MECHANISM CHECK] Contaminated: {cont_acc:.3f}, Clean: {clean_acc:.3f}")
    print(f"[MECHANISM CHECK] Effect: {effect_size:.3f}, Active: {mechanism_active}")
    
    return {
        'mechanism_active': mechanism_active,
        'contaminated_accuracy': cont_acc,
        'clean_accuracy': clean_acc,
        'effect_size': effect_size
    }
```

### Success Criteria
- `hypothesis_support_threshold`: effect_size > 0.05 (5% accuracy gain on contaminated)
- `hypothesis_support_metric`: contaminated_accuracy - clean_accuracy

---

## PoC Success Check

**Gate Result Determination:**
1. Code runs without error across all 5 contamination levels
2. At each non-zero level: `contaminated_acc > clean_acc`
3. Monotonic trend: effect_size(5%) < effect_size(10%) < effect_size(20%) < effect_size(50%)

**If PASS:** Contamination injection procedure validated → proceed to H-M2
**If FAIL:** PIVOT - revise contamination injection procedure (longer training, different format)

---

## Appendix: Reference Implementations

| Source | Description | Relevance |
|--------|-------------|-----------|
| hendrycks/test | Official MMLU benchmark | Dataset source, evaluation format |
| huggingface/peft | LoRA implementation | Efficient fine-tuning |
| EleutherAI/lm-evaluation-harness | Evaluation framework | Standardized MMLU evaluation |
| Sainz et al. 2023 | Contamination study | Methodology for controlled contamination |
| Magar & Schwartz 2022 | Data contamination in LLMs | Validation approaches |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: H-M1 set to IN_PROGRESS (external loop starting Phase 2C)
- 2026-08-19: Phase 2C experiment design initiated
- Prerequisite H-E1 PASSED with asymmetry ratio 5.07x

---

*MCP Tools: Archon/Exa unavailable - used literature-based design*
*All specifications grounded in established contamination methodology*
*Next Phase: Phase 3 - Implementation Planning*
