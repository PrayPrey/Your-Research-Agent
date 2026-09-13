# Experiment Design: H-E1

**Date:** 2026-08-28
**Author:** PrayPrey
**Hypothesis Statement:** Mamba-130M pretrained checkpoint exists, loads correctly, and produces non-random outputs on GLUE zero-shot evaluation
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None required (foundational hypothesis)
**Gate Status:** MUST_WORK - Failure blocks entire pipeline

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK gate: If checkpoint fails to load or produces random outputs, entire Mamba experiment pipeline is blocked. Mitigation requires identifying alternative SSM checkpoint or architecture pivot.

---

## Continuation Context

H-E1 is the foundational hypothesis. No previous hypothesis results to incorporate.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in verification sequence

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP server unavailable during design - using manual research*

Key findings for Mamba checkpoint loading:
- Mamba models available on HuggingFace Hub under `state-spaces` organization
- Official repository: https://github.com/state-spaces/mamba
- Pretrained checkpoints use standard HuggingFace format
- Common loading pattern: `MambaForCausalLM.from_pretrained()`

### Archon Code Examples

*MCP server unavailable - manual code pattern identification*

Standard checkpoint loading pattern:
```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("state-spaces/mamba-130m-hf")
tokenizer = AutoTokenizer.from_pretrained("state-spaces/mamba-130m-hf")
```

### Exa GitHub Implementations

*MCP server unavailable - using known implementations*

Reference implementations:
1. Official Mamba repository (state-spaces/mamba)
2. HuggingFace Transformers integration (v4.35+)
3. GLUE evaluation examples in HuggingFace evaluate library

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Priority: Use HuggingFace Hub checkpoint with official HuggingFace Transformers library

**Recommended Implementation Path:**
- Primary: HuggingFace `state-spaces/mamba-130m-hf` checkpoint
- Fallback: Load original checkpoint and convert to HF format
- Justification: HF integration provides standardized interface, automatic mixed precision, device management

### Code Analysis (Serena MCP)

*Serena MCP unavailable - skipped*

---

## Experiment Specification

### Dataset

**Name:** GLUE Benchmark (MNLI, QQP, SST-2 tasks)
**Type:** Standard benchmark
**Source:** HuggingFace datasets library
**Splits:** validation sets only (zero-shot evaluation)
**Sizes:**
- MNLI validation: 9,815 examples
- QQP validation: 40,430 examples  
- SST-2 validation: 872 examples

**Preprocessing:**
- Tokenization: Use model's pretrained tokenizer
- Max length: 512 tokens (truncate longer sequences)
- Padding: Dynamic to batch max length
- No augmentation (zero-shot evaluation)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets library
- Identifier: `glue` dataset with task names
- Code:
```python
from datasets import load_dataset
mnli_data = load_dataset("glue", "mnli", split="validation_matched")
qqp_data = load_dataset("glue", "qqp", split="validation")
sst2_data = load_dataset("glue", "sst2", split="validation")
```

### Models

#### Baseline Model

**Architecture:** Mamba-130M (state-space model)
**Parameters:** 130M
**Pretrained:** Yes (on Pile dataset)
**Source:** HuggingFace Hub `state-spaces/mamba-130m-hf`

**Expected Zero-Shot Performance:**
- MNLI: 45-55% (vs 33% random baseline)
- QQP: 60-70% (vs 50% random baseline)
- SST-2: 65-75% (vs 50% random baseline)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `state-spaces/mamba-130m-hf`
- Code:
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "state-spaces/mamba-130m-hf",
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("state-spaces/mamba-130m-hf")
```

#### Proposed Model

**Architecture:** Same as baseline (zero-shot evaluation only)

**Core Mechanism Implementation:**

Zero-shot prompting for classification tasks:

```python
def zero_shot_classify(model, tokenizer, text, choices, device):
    """
    Evaluate model on classification by comparing log probabilities
    of answer choices given prompt.
    
    Args:
        text: Input text to classify
        choices: List of answer strings (e.g., ["entailment", "neutral", "contradiction"])
    
    Returns:
        predicted_class: Index of highest probability choice
    """
    # Format prompt based on task
    prompt = format_task_prompt(text, task_name)
    
    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    # Get model predictions for each choice
    choice_probs = []
    for choice in choices:
        # Tokenize choice continuation
        choice_tokens = tokenizer(choice, return_tensors="pt").input_ids
        
        # Compute log probability of choice given prompt
        with torch.no_grad():
            outputs = model(**inputs, labels=choice_tokens)
            log_prob = -outputs.loss.item()
        
        choice_probs.append(log_prob)
    
    # Return choice with highest probability
    predicted_class = np.argmax(choice_probs)
    return predicted_class
```

### Training Protocol

**No training required** - zero-shot evaluation only

**Inference Settings:**
- Batch size: 16 (for efficient evaluation)
- Mixed precision: FP16 (reduce memory usage)
- Device: Single GPU (requires <16GB VRAM)
- Random seed: 42 (for reproducibility)

### Evaluation

**Metrics:**
- Accuracy (primary metric for all three tasks)
- Per-task breakdown (MNLI, QQP, SST-2)
- Inference time (secondary - validate <5 min per task)

**Success Criteria:**
- Checkpoint loads without errors
- Model fits in <16GB GPU memory
- Zero-shot accuracy > random baseline on ALL tasks:
  - MNLI: >33.3% (3-class)
  - QQP: >50% (binary)
  - SST-2: >50% (binary)

**Statistical Testing:**
None required - deterministic zero-shot evaluation (no training variance)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Classification (multi-class for MNLI, binary for QQP/SST-2)
- Library: HuggingFace evaluate or sklearn.metrics
- Code:
```python
from evaluate import load
accuracy_metric = load("accuracy")

# Compute accuracy
results = accuracy_metric.compute(predictions=preds, references=labels)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing zero-shot accuracy vs random baseline for each GLUE task

#### Additional Figures (LLM Autonomous)

1. **Per-Task Performance Table**: Accuracy breakdown with sample counts
2. **Inference Time Analysis**: Time per example by task (validate efficiency)
3. **Confusion Matrix** (optional): For MNLI 3-class classification

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (checkpoint loads, inference completes)
2. Zero-shot accuracy > random baseline on ALL three tasks

**Specific Thresholds:**
- MNLI: accuracy > 0.333
- QQP: accuracy > 0.50
- SST-2: accuracy > 0.50

---

## Appendix: Reference Implementations

### Primary References

1. **Mamba Official Repository**
   - URL: https://github.com/state-spaces/mamba
   - License: Apache 2.0
   - Key files: `mamba_ssm/models/mixer_seq_simple.py`

2. **HuggingFace GLUE Evaluation**
   - URL: https://huggingface.co/docs/evaluate/main/en/index
   - Examples: GLUE task evaluation scripts
   - Key pattern: Zero-shot prompting for classification

3. **Mamba HuggingFace Integration**
   - Model card: https://huggingface.co/state-spaces/mamba-130m-hf
   - Integration PR: transformers v4.35+
   - Usage: Standard AutoModel loading

### Code Snippets

**Complete Evaluation Loop:**
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset
from evaluate import load

# Load model
model = AutoModelForCausalLM.from_pretrained("state-spaces/mamba-130m-hf")
tokenizer = AutoTokenizer.from_pretrained("state-spaces/mamba-130m-hf")
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Load GLUE task
dataset = load_dataset("glue", "mnli", split="validation_matched")
metric = load("accuracy")

# Evaluate
predictions = []
for example in dataset:
    pred = zero_shot_classify(model, tokenizer, example["premise"], 
                               example["hypothesis"], task="mnli")
    predictions.append(pred)

# Compute accuracy
accuracy = metric.compute(predictions=predictions, references=dataset["label"])
print(f"MNLI accuracy: {accuracy['accuracy']:.3f}")
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28T22:30:00Z

### Workflow History for This Hypothesis
- 2026-08-28T22:30:00Z: Created in Phase 2B
- 2026-08-28T22:35:00Z: Phase 2C experiment design started

---

*MCP Tools Used: Manual research (MCP servers unavailable)*
*All specifications grounded in official Mamba documentation and HuggingFace standards*
*Next Phase: Phase 3 - Implementation Planning*
