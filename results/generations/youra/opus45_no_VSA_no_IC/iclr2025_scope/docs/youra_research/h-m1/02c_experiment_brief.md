# Experiment Design: h-m1

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis Statement:** Attention entropy at optimal rank correlates positively with model size (Pearson r > 0.6, p < 0.05)
**Phase 2B Source:** 02b_context.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** None (independent)

### Gate Condition
SHOULD_WORK: Failure logs limitation but does not block pipeline. Success provides mechanistic insight into why optimal rank scales with model size.

---

## Continuation Context

This is an independent mechanism hypothesis. No prior hypothesis results required.

### Previous Hypothesis Results (if applicable)
N/A - h-m1 runs in Wave 1 (parallel with h-e1)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

- T-GATE (attention gating in transformers): provides attention analysis patterns
- Transformer attention entropy computation: standard Shannon entropy over attention weights
- Apple Neural Engine research: attention head importance analysis methods

### Archon Code Examples

```python
# Attention entropy computation
def attention_entropy(attn_weights):
    # attn_weights: [batch, heads, seq, seq]
    # Add small epsilon for numerical stability
    eps = 1e-10
    entropy = -torch.sum(attn_weights * torch.log(attn_weights + eps), dim=-1)
    return entropy.mean()  # Average over heads and positions
```

### Exa GitHub Implementations

- PEFT library (huggingface/peft): Standard LoRA implementation
- EleutherAI/pythia: Model checkpoints on HuggingFace Hub

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

- No specific paper being reproduced; this is novel hypothesis testing
- Use standard PEFT library for LoRA, standard PyTorch for entropy computation

**Recommended Implementation Path:**
- Primary: HuggingFace PEFT + custom attention entropy hook
- Fallback: Manual LoRA implementation if PEFT incompatible
- Justification: PEFT is well-tested, Pythia models have native HF support

### Code Analysis (Serena MCP)

No existing codebase to analyze - fresh implementation required.

---

## Experiment Specification

### Dataset

| Field | Value |
|-------|-------|
| Dataset Name | SQuAD v2.0 |
| Dataset Type | Standard benchmark (extractive QA) |
| Source | HuggingFace Datasets |
| Split | train[:5000] for training, validation[:1000] for eval |
| Task | Question Answering |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `squad_v2`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("squad_v2")
train_data = dataset["train"].select(range(5000))
val_data = dataset["validation"].select(range(1000))
```

### Models

#### Baseline Model

| Field | Value |
|-------|-------|
| Model Name | Pythia family (1B, 2.8B, 6.9B, 12B) |
| Source | EleutherAI on HuggingFace |
| Type | Causal LM |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `EleutherAI/pythia-{size}`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_SIZES = ["1b", "2.8b", "6.9b", "12b"]
models = {}
for size in MODEL_SIZES:
    model_name = f"EleutherAI/pythia-{size}"
    models[size] = AutoModelForCausalLM.from_pretrained(
        model_name, 
        torch_dtype=torch.float16,
        device_map="auto"
    )
```

#### Proposed Model

**Architecture:** Baseline + LoRA adapters at various ranks

**Core Mechanism Implementation:**

```python
from peft import LoraConfig, get_peft_model, TaskType

def create_lora_model(base_model, rank):
    """Create LoRA adapter with specified rank."""
    config = LoraConfig(
        r=rank,
        lora_alpha=2 * rank,
        target_modules=["query_key_value"],  # Pythia uses fused QKV
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    return get_peft_model(base_model, config)

def compute_attention_entropy(model, input_ids, attention_mask):
    """Extract attention entropy from model forward pass."""
    outputs = model(
        input_ids=input_ids,
        attention_mask=attention_mask,
        output_attentions=True
    )
    
    all_entropies = []
    for layer_attn in outputs.attentions:
        # layer_attn: [batch, heads, seq, seq]
        # Mask padding positions
        masked_attn = layer_attn * attention_mask.unsqueeze(1).unsqueeze(2)
        # Renormalize
        masked_attn = masked_attn / (masked_attn.sum(dim=-1, keepdim=True) + 1e-10)
        # Compute entropy
        eps = 1e-10
        entropy = -torch.sum(masked_attn * torch.log(masked_attn + eps), dim=-1)
        all_entropies.append(entropy.mean().item())
    
    return np.mean(all_entropies)  # Average across layers
```

### Training Protocol

| Parameter | Value |
|-----------|-------|
| Epochs | 3 |
| Learning Rate | 1e-4 |
| Batch Size | 4 (gradient accumulation 4) |
| Optimizer | AdamW |
| Scheduler | Linear warmup (10%) + cosine decay |
| Max Sequence Length | 512 |
| LoRA Ranks | [4, 8, 16, 32, 64, 128] |

```python
RANKS = [4, 8, 16, 32, 64, 128]
MODEL_SIZES = ["1b", "2.8b", "6.9b", "12b"]
MODEL_PARAMS = {"1b": 1e9, "2.8b": 2.8e9, "6.9b": 6.9e9, "12b": 12e9}

results = {}
for size in MODEL_SIZES:
    results[size] = {"ranks": [], "f1_scores": [], "entropies": []}
    base_model = load_model(size)
    
    for rank in RANKS:
        lora_model = create_lora_model(base_model, rank)
        trainer = train_qa(lora_model, train_data, val_data, epochs=3, lr=1e-4)
        f1 = evaluate_qa(lora_model, val_data)
        entropy = compute_attention_entropy(lora_model, val_data)
        
        results[size]["ranks"].append(rank)
        results[size]["f1_scores"].append(f1)
        results[size]["entropies"].append(entropy)
```

### Evaluation

| Metric | Description | Target |
|--------|-------------|--------|
| Optimal Rank | Rank with best validation F1 per model | Identified per model |
| Attention Entropy | Average attention entropy at optimal rank | Measured value |
| Pearson r | Correlation between entropy and model size | r > 0.6 |
| p-value | Statistical significance | p < 0.05 |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Correlation analysis
- Library: scipy.stats
- Code:
```python
from scipy.stats import pearsonr

def compute_correlation(results, model_params):
    """Compute correlation between attention entropy at optimal rank and model size."""
    entropies_at_optimal = []
    sizes = []
    
    for size, data in results.items():
        optimal_idx = np.argmax(data["f1_scores"])
        optimal_entropy = data["entropies"][optimal_idx]
        entropies_at_optimal.append(optimal_entropy)
        sizes.append(model_params[size])
    
    r, p = pearsonr(sizes, entropies_at_optimal)
    return {"pearson_r": r, "p_value": p, "pass": r > 0.6 and p < 0.05}
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Scatter plot of model size vs attention entropy at optimal rank with regression line

#### Additional Figures (LLM Autonomous)

1. **Rank-F1 curves per model**: Line plots showing F1 vs rank for each model size
2. **Entropy heatmap**: Heatmap of attention entropy across (model_size, rank) combinations
3. **Optimal rank vs model size**: Bar chart showing optimal rank per model

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Pearson r > 0.6 AND p < 0.05

---

## Appendix: Reference Implementations

| Component | Reference |
|-----------|-----------|
| LoRA | huggingface/peft |
| Pythia Models | EleutherAI/pythia |
| SQuAD Dataset | rajpurkar/squad_v2 |
| Attention Analysis | T-GATE (attention gating patterns) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- 2026-08-24: Phase 2C experiment design started
- 2026-08-24: Phase 2C experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
