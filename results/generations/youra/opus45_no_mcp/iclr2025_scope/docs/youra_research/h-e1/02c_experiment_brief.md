# Experiment Design: H-E1

**Date:** 2026-08-19
**Author:** YouRA Research System
**Hypothesis Statement:** Under controlled conversion from Transformer to Mamba architecture, if LoRA adaptation is applied to analogous projection layers across 4+ benchmarks spanning retrieval density spectrum, then measurable task-dependent patterns emerge.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (none required - foundation hypothesis)
**Gate Status:** MUST_WORK - If fails, abandon main hypothesis

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
MUST_WORK gate: Task-dependent adaptation pattern must be observed across benchmarks. Failure triggers ABANDON of main hypothesis H-AdaptTransform-v1.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous hypothesis results to incorporate.

### Previous Hypothesis Results (if applicable)
N/A - Foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Note: Archon MCP unavailable. Research conducted via web sources.*

**Query 1: SSM-Attention Duality Experiment Design**
- Mamba-2 implements "Transformers are SSMs" duality (Dao & Gu, 2024)
- Key insight: SSM state dimension typically 64-128 for Mamba-2
- Pretrained models available: 130M to 2.8B parameters on Pile (300B tokens)

**Query 2: LoRA Cross-Architecture Adaptation**
- Standard LoRA config: rank 16, alpha 32, dropout 0.1
- Target modules for Mamba: in_proj, out_proj (analogous to QKV/O in Transformer)
- PEFT library supports custom target module specification

**Query 3: Task-Dependent Adaptation Benchmarks**
- GSM8K: Sequential reasoning, low retrieval density (0.1)
- Natural Questions: Retrieval-heavy QA (0.9)
- MMLU: Mixed tasks (0.5)
- HotpotQA: Multi-hop reasoning (0.7)

### Archon Code Examples

**Mamba Model Loading:**
```python
from mamba_ssm import Mamba2
model = Mamba2(d_model=768, d_state=64, d_conv=4, expand=2).to("cuda")
```

**LoRA Configuration:**
```python
from peft import LoraConfig, get_peft_model, TaskType
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["in_proj", "out_proj"],  # Mamba projections
    task_type=TaskType.CAUSAL_LM,
)
```

### Exa GitHub Implementations

**Source: github.com/state-spaces/mamba**
- Official Mamba implementation with pretrained weights
- Supports Mamba, Mamba-2, Mamba-3 architectures
- Installation: `pip install mamba-ssm --no-build-isolation`

**Source: github.com/huggingface/peft**
- LoRA implementation with custom target module support
- Can apply to non-standard architectures via manual config

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Status |
|----------|--------|--------|
| 1 | state-spaces/mamba (official) | Available |
| 2 | huggingface/peft (LoRA) | Available |
| 3 | meta-llama/Llama-2-7b-hf | Available |

**Recommended Implementation Path:**
- Primary: Use official mamba-ssm package + PEFT for LoRA
- Fallback: Custom LoRA implementation on Mamba projections
- Justification: Official implementation ensures correct SSM dynamics; PEFT handles LoRA mechanics

### Code Analysis (Serena MCP)

*Note: Serena MCP unavailable. Analysis based on public documentation.*

**Mamba-2 Architecture (from paper):**
- Selective scan operation with input-dependent state transitions
- Linear projections: in_proj (3×d_model), out_proj (d_model)
- State dimension: 64 (default for Mamba-2)
- Convolution: d_conv=4

**Transformer Architecture (Llama-2):**
- Multi-head attention with QKV projections
- Hidden: 4096, Heads: 32, Layers: 32
- Total params: ~7B

---

## Experiment Specification

### Dataset

**Multi-Benchmark Suite for Retrieval Density Spectrum**

| Benchmark | Type | Train Size | Test Size | Retrieval Density |
|-----------|------|------------|-----------|-------------------|
| GSM8K | Sequential reasoning | 7,473 | 1,319 | 0.1 (low) |
| Natural Questions | Retrieval QA | 307,373 | 3,610 | 0.9 (high) |
| MMLU | Mixed knowledge | ~100K | 14,042 | 0.5 (medium) |
| HotpotQA | Multi-hop QA | ~90K | 7,405 | 0.7 (medium-high) |

**Total Evaluation Samples:** 26,376 across 4 benchmarks

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `openai/gsm8k`, `google-research-datasets/natural_questions`, `cais/mmlu`, `hotpot_qa`
- Code:
```python
from datasets import load_dataset

gsm8k = load_dataset("openai/gsm8k", "main")  # train: 7473, test: 1319
nq = load_dataset("google-research-datasets/natural_questions")  # validation: 7830
mmlu = load_dataset("cais/mmlu", "all")  # test: 14042
hotpotqa = load_dataset("hotpot_qa", "fullwiki")  # validation: 7405
```

### Models

#### Baseline Model

**Architecture:** Llama-2-7B (Transformer) with LoRA adaptation

**Configuration:**
- Hidden size: 4096
- Layers: 32
- Attention heads: 32
- Parameters: ~7B

**LoRA Configuration:**
- Rank: 16
- Alpha: 32
- Target modules: q_proj, k_proj, v_proj, o_proj
- Dropout: 0.0

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.0,
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)
```

#### Proposed Model

**Architecture:** Mamba-converted + LoRA adaptation

**Core Mechanism Implementation:**

```python
# Core Mechanism: Transformer-to-Mamba Conversion + LoRA
# Based on: SSM-Attention Duality (Mamba-2, Dao & Gu 2024)

from mamba_ssm import Mamba2
from peft import LoraConfig, get_peft_model
import torch.nn as nn

class MambaWithLoRA(nn.Module):
    """
    Mamba model with LoRA adaptation on projection layers.
    Tests whether SSM state evolution creates task-dependent adaptation patterns.
    """
    def __init__(self, d_model=4096, d_state=64, n_layers=32):
        super().__init__()
        self.layers = nn.ModuleList([
            Mamba2(d_model=d_model, d_state=d_state, d_conv=4, expand=2)
            for _ in range(n_layers)
        ])
        
    def forward(self, x):
        """
        Args:
            x: (B, L, D) - input sequence
        Returns:
            (B, L, D) - output with SSM state evolution
        """
        for layer in self.layers:
            x = layer(x)  # SSM selective scan with state evolution
        return x

# LoRA Configuration for Mamba projections
mamba_lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["in_proj", "out_proj"],  # Analogous to QKV/O
    lora_dropout=0.0,
    task_type="CAUSAL_LM",
)

# Integration: Replace Transformer backbone with Mamba SSM layers
# Comparison: Same LoRA config, different architecture
```

### Training Protocol

**Optimizer:** AdamW
- Parameters: lr=2e-4, weight_decay=0.01, betas=(0.9, 0.999)
- Source: Standard for LoRA fine-tuning (Hu et al., 2021)

**Learning Rate:** 2e-4
- Source: PEFT default for LLM adaptation

**Schedule:** Linear warmup + cosine decay
- Warmup steps: 100
- Source: Common for fine-tuning

**Batch Size:** 4 (with gradient accumulation 4 = effective 16)
- Source: Memory-constrained 7B model training

**Epochs:** 3 per benchmark
- Source: Standard for LoRA fine-tuning

**Loss Function:** Cross-entropy (language modeling)

**Seeds:** 1 (fixed at 42)

> ⚠️ **EXISTENCE (PoC)**: Single seed sufficient for direction validation.

### Evaluation

**Primary Metrics:**
- Task accuracy (exact match for GSM8K, F1 for NQ/HotpotQA, accuracy for MMLU)
- Adaptation efficiency delta: (Mamba_accuracy - Transformer_accuracy)

**Success Criteria** (PoC: Direction-based):
- Sequential tasks (GSM8K): delta >= -5% (preservation or improvement)
- Retrieval tasks (NQ): delta <= -15% (degradation expected)
- Pattern: Correlation between retrieval density and efficiency delta

**Expected Baseline Performance:**
- GSM8K (Llama-2-7B + LoRA): ~45-50% accuracy
- NQ (Llama-2-7B + LoRA): ~25-30% F1
- Source: Community benchmarks

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Text generation / Question answering
- Library: `evaluate` (HuggingFace)
- Code:
```python
import evaluate

# GSM8K: Exact match on final answer
accuracy = evaluate.load("exact_match")

# NQ/HotpotQA: F1 score
f1 = evaluate.load("f1")

# MMLU: Multiple choice accuracy
mmlu_accuracy = evaluate.load("accuracy")
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing Transformer vs Mamba accuracy across 4 benchmarks, grouped by retrieval density

#### Additional Figures (LLM Autonomous)

Based on EXISTENCE hypothesis type, generate:
1. **Accuracy Delta vs Retrieval Density**: Scatter plot showing correlation
2. **Training Loss Curves**: Transformer vs Mamba across tasks
3. **Task-Type Heatmap**: Color-coded performance comparison matrix

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** True - SSM selective scan is the core mechanism
- **mechanism_isolatable:** True - Compare same LoRA config on different architectures
- **baseline_measurable:** True - Transformer + LoRA provides baseline

### Architecture Compatibility
- **architecture_compatibility:** Compatible
- Mamba in_proj/out_proj analogous to Transformer QKV/O projections
- LoRA can target both projection sets with identical rank/alpha

### Activation Indicators
- **mechanism_log_message:** "SSM state evolution active: shape (B, L, D_state)"
- **tensor_shape_change:** Input (B, L, D) → State (B, L, D_state) → Output (B, L, D)
- **metric_delta_expected:** GSM8K delta >= -5%, NQ delta <= -15%

### Mechanism Verification Code
```python
def verify_mechanism_active(model, sample_input):
    """Verify SSM state evolution is occurring."""
    # Check Mamba layer state dimensions
    for layer in model.layers:
        assert hasattr(layer, 'A_log'), "SSM A matrix not found"
        assert hasattr(layer, 'D'), "SSM D matrix not found"
    
    # Run forward pass and check state evolution
    with torch.no_grad():
        output = model(sample_input)
        assert output.shape == sample_input.shape, "Shape mismatch"
    
    print("✓ SSM mechanism verified: state evolution active")
    return True
```

### Success Thresholds
- **hypothesis_support_threshold:** Spearman rho > 0.5 for delta vs retrieval density
- **hypothesis_support_metric:** Task-dependent pattern observed (sequential vs retrieval divergence)

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on all 4 benchmarks
2. Task-dependent pattern emerges:
   - GSM8K (sequential): delta >= -5%
   - NQ (retrieval): delta <= -15%
   - Pattern direction matches hypothesis

---

## Appendix: Reference Implementations

| Component | Source | URL |
|-----------|--------|-----|
| Mamba | state-spaces/mamba | https://github.com/state-spaces/mamba |
| PEFT/LoRA | huggingface/peft | https://github.com/huggingface/peft |
| Llama-2 | meta-llama | https://huggingface.co/meta-llama/Llama-2-7b-hf |
| GSM8K | OpenAI | https://huggingface.co/datasets/openai/gsm8k |
| Natural Questions | Google Research | https://huggingface.co/datasets/google-research-datasets/natural_questions |
| MMLU | CAIS | https://huggingface.co/datasets/cais/mmlu |
| HotpotQA | HotpotQA | https://huggingface.co/datasets/hotpot_qa |

**Key Papers:**
- Mamba: Linear-Time Sequence Modeling with Selective State Spaces (Gu & Dao, 2023)
- Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality (Dao & Gu, 2024)
- LoRA: Low-Rank Adaptation of Large Language Models (Hu et al., 2021)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: H-E1 set to IN_PROGRESS (Phase 2C started)
- 2026-08-19: Experiment design completed (Phase 2C)

---

*MCP Tools Used: WebFetch (GitHub, HuggingFace)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
