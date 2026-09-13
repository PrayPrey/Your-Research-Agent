# Experiment Design: H-M1

**Date:** 2026-08-09
**Author:** Anonymous
**Hypothesis Statement:** Zero-shot IPCR routing achieves ≥90% of oracle task-specific LoRA performance on held-out FLAN tasks
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates core routing mechanism performance.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (VALIDATED - Top-1 72.67%, Top-3 95.78%)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (linear probe validates adapter selection via instruction embeddings)

### Gate Condition
MUST_WORK: If performance < 80% of oracle OR not significant vs uniform → core claim fails

---

## Continuation Context

### H-E1 Validated Findings (Prerequisite)
- Linear probe on frozen MiniLM embeddings achieves 72.67% top-1 accuracy (exceeds 70% threshold)
- Top-3 accuracy 95.78% far exceeds 85% threshold
- 14.8x improvement over random baseline
- This validates that instruction embeddings can reliably predict optimal adapter selection

### Previous Hypothesis Results
H-E1 provides the routing mechanism foundation. The linear probe trained in H-E1 will be used as the IPCR router in H-M1 to select adapters based on instruction prefix embeddings.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**LoRA Adapter Concepts (PEFT Documentation):**
- LoRA injects low-rank matrices into transformer layers, enabling parameter-efficient fine-tuning
- Multiple adapters can be loaded simultaneously via `PeftModel.load_adapter()`
- Adapter switching via `model.set_adapter(adapter_name)` is O(1) operation (~5ms)
- Source: HuggingFace PEFT conceptual guides

**Multi-Adapter Inference Pattern:**
- Load base model once, add multiple named adapters
- Switch adapters at inference time without model reload
- Use `model.set_adapters([list])` for weighted ensemble mode (PEFT 0.8.0+)

### Archon Code Examples

**Multi-LoRA Inference (PEFT examples):**
```python
model = PeftModel.from_pretrained(base_model, "adapter1", adapter_name="task1")
model.load_adapter("adapter2", adapter_name="task2")
model.set_adapter("task1")  # Switch to task1 adapter
output = model.generate(**inputs)
```

### Exa GitHub Implementations

**1. LoraHub (COLM 2024) - sail-sg/lorahub:**
- Dynamic LoRA composition for cross-task generalization
- Gradient-free composition using few examples
- Key insight: LoRA modules can be composed without retraining
- Source: https://github.com/sail-sg/lorahub

**2. MoLoRA (arxiv 2603.15965) - Per-token adapter routing:**
- Learned gating for Mixture of LoRA experts
- 2-layer MLP router classifies tokens → selects adapter per-token
- Qwen3-1.7B + MoLoRA exceeds Qwen3-8B on reasoning benchmarks
- Demonstrates: specialization beats scale

**3. TASA - Adapters Selector (tirant35/TASA):**
- Trains selector (middleman adapter) to route inputs to task-specific adapters
- Uses sentence embeddings (M3E/BERT) for input classification
- Supports COS/IP/L2 distance metrics for routing
- Source: https://github.com/tirant35/TASA

**4. Polytropon (PEFT native):**
- Multi-task model with adapter "inventory"
- Learnable routing function selects adapter subset
- Supports Multi-Head Adapter Routing (MHR) for finer-grained control

**5. HardLoRAMixer (sar-molavi/hard-routed-mor-lora):**
- Hard-routed mixtures of reasoning LoRA experts
- Trains classifier router to select among frozen LoRA experts
- Architecture: train experts → freeze → train router

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Implementation | Rationale |
|----------|---------------|-----------|
| 1 | TASA (tirant35/TASA) | Most similar to IPCR: embedding-based selector for adapter routing |
| 2 | HardLoRAMixer | Hard routing (not soft mixing) aligns with our linear probe approach |
| 3 | PEFT native multi-adapter | Proven infrastructure, official HuggingFace support |
| 4 | LoraHub | Gradient-free composition, useful baseline comparison |

**Recommended Implementation Path:**
- Primary: PEFT multi-adapter + custom MiniLM router (from H-E1 linear probe)
- Fallback: Adapt TASA selector architecture if PEFT native insufficient
- Justification: H-E1 validated linear probe on MiniLM achieves 72.67% accuracy; reuse that trained probe as IPCR router

### Code Analysis (Serena MCP)

*Serena analysis not performed - using Exa/Archon findings for implementation guidance.*

**Key Implementation Pattern (from TASA + PEFT):**
```python
# 1. Load base model + multiple task-specific LoRAs
# 2. Embed instruction with MiniLM
# 3. Linear probe predicts best adapter
# 4. set_adapter(predicted_adapter)
# 5. Generate with selected adapter
```

---

## Experiment Specification

### Dataset

**Name:** Open-Orca/FLAN (instruction collection)
**Type:** standard
**Source:** HuggingFace Hub
**Task Categories:** 62 FLAN task families
**Split Strategy:** Held-out task family split (train on N-k families, test on k held-out families)

**Dataset Details:**
- Use same FLAN subset as H-E1 for consistency
- Minimum 500 samples per held-out task family for statistical significance
- Task families grouped by semantic similarity (from H-E0 clustering)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `Open-Orca/FLAN`
- Code: 
```python
from datasets import load_dataset
dataset = load_dataset("Open-Orca/FLAN", streaming=True)
```

### Models

#### Baseline Models (Comparison Set)

| Model | Description | Expected Performance |
|-------|-------------|---------------------|
| **Oracle** | Task-specific LoRA (knows correct adapter) | 100% (upper bound) |
| **Random** | Random adapter selection | ~12.5% of oracle (1/k for k=8 adapters) |
| **Uniform** | Equal weight combination of all adapters | Baseline for naive mixing |

**Base LLM:** Llama-2-7B-chat or Mistral-7B-Instruct
**Adapter Bank:** k=8 task-specific LoRAs, rank r=16

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers + PEFT
- Identifier: `meta-llama/Llama-2-7b-chat-hf`
- Code:
```python
from transformers import AutoModelForCausalLM
from peft import PeftModel
base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
# Load each task-specific LoRA
for task_name, lora_path in adapter_bank.items():
    model.load_adapter(lora_path, adapter_name=task_name)
```

#### Proposed Model: IPCR Router

**Architecture:** Base LLM + k Task-LoRAs + MiniLM Router (from H-E1)

**Integration Point:**
- Router operates BEFORE generation
- Embeds instruction prefix → linear probe → select adapter → generate

**Core Mechanism Implementation:**

```python
# IPCR Router: Instruction-Prefix-Conditioned Routing
# Based on: H-E1 validated linear probe (72.67% top-1, 95.78% top-3)

class IPCRRouter:
    """
    Routes instructions to task-specific LoRA adapters
    using frozen MiniLM embeddings + trained linear probe.
    """
    def __init__(self, encoder, linear_probe, adapter_names):
        self.encoder = encoder  # sentence-transformers/all-MiniLM-L6-v2
        self.probe = linear_probe  # from H-E1 (input: 384, output: k)
        self.adapter_names = adapter_names  # k adapter names
    
    def route(self, instruction: str) -> str:
        """
        Args:
            instruction: Input instruction text
        Returns:
            adapter_name: Selected adapter for this instruction
        """
        # Step 1: Embed instruction prefix
        embedding = self.encoder.encode(instruction)  # (384,)
        
        # Step 2: Linear probe prediction
        logits = self.probe(embedding)  # (k,)
        adapter_idx = logits.argmax()
        
        # Step 3: Return selected adapter
        return self.adapter_names[adapter_idx]

# Integration with PEFT model
def ipcr_generate(model, router, instruction, **gen_kwargs):
    adapter_name = router.route(instruction)
    model.set_adapter(adapter_name)
    return model.generate(instruction, **gen_kwargs)
```

### Training Protocol

**Note:** IPCR router is already trained (H-E1 linear probe). This experiment evaluates routing quality, not training.

**LoRA Adapters (pre-trained):**
- Each task-specific LoRA trained on its task family
- Optimizer: AdamW
- Learning rate: 2e-4
- LoRA rank: r=16
- LoRA alpha: 32
- Target modules: q_proj, v_proj
- Epochs: 3 per task family
- Batch size: 8

**Router (from H-E1):**
- Linear probe already trained
- Frozen MiniLM encoder (no fine-tuning)

**Evaluation Protocol:**
- Single seed (42)
- Held-out task families: k families not seen during LoRA training
- Samples per family: minimum 500

### Evaluation

**Primary Metric:** Relative performance vs Oracle
```
IPCR_score = (IPCR_metric / Oracle_metric) × 100%
```

**Task Metrics (per task family):**
| Task Type | Metric |
|-----------|--------|
| Classification | Accuracy |
| Generation | ROUGE-L |
| QA | Exact Match |

**Success Criteria (MUST_WORK gate):**
- IPCR achieves ≥90% of oracle performance on average across held-out tasks
- IPCR significantly outperforms Uniform baseline (p < 0.05, paired t-test)

**Falsification Threshold:**
- IPCR < 80% of oracle → core claim fails
- IPCR not significantly better than Uniform → routing provides no benefit

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Multi-task (classification + generation + QA)
- Library: evaluate (HuggingFace)
- Code:
```python
import evaluate
accuracy = evaluate.load("accuracy")
rouge = evaluate.load("rouge")
exact_match = evaluate.load("exact_match")
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: IPCR vs Oracle vs Uniform vs Random bar chart

#### Additional Figures (LLM Autonomous)
- Per-task-family performance breakdown (grouped bar chart)
- Routing confusion matrix (predicted adapter vs optimal adapter)
- Performance vs routing confidence scatter plot
- Ablation: top-1 vs top-3 routing accuracy impact

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. IPCR routing achieves ≥90% of oracle LoRA performance
3. IPCR significantly outperforms uniform adapter combination

---

## Appendix: Reference Implementations

### Primary References

| Source | URL | Relevance |
|--------|-----|-----------|
| **PEFT Multi-LoRA** | https://github.com/huggingface/peft/blob/main/examples/multi_adapter_examples/ | Official multi-adapter inference pattern |
| **LoraHub** | https://github.com/sail-sg/lorahub | Cross-task LoRA composition (COLM 2024) |
| **TASA** | https://github.com/tirant35/TASA | Embedding-based adapter selector |
| **MoLoRA** | arxiv:2603.15965 | Per-token learned routing for LoRA experts |
| **HardLoRAMixer** | https://github.com/sar-molavi/hard-routed-mor-lora | Hard-routed LoRA expert selection |
| **HMoRA** | https://github.com/LiaoMengqi/HMoRA | Hierarchical Mixture of LoRA (ICLR 2025) |
| **LD-MoLE** | https://github.com/eshentw/LD-MoLE | Learnable dynamic routing for MoLE (ICLR 2026) |
| **Polytropon** | HuggingFace PEFT docs | Native PEFT routing with Multi-Head Routing |

### Key Code Snippets

**PEFT Adapter Switching:**
```python
model.set_adapter("task_name")  # O(1) switch, ~5ms
model.set_adapters(["adapter1", "adapter2"], adapter_weights=[0.5, 0.5])  # Ensemble
```

**TASA Selector Pattern:**
```python
class ModelWithSelector:
    def generate_selector(self, datapoint):
        # Embed input → predict adapter → route
        embedding = self.encoder.encode(datapoint["instruction"])
        adapter_name = self.selector.predict(embedding)
        self.model.set_adapter(adapter_name)
        return self.model.generate(**datapoint)
```

### MCP Sources Used

1. **Archon KB:** PEFT conceptual guides, LoRA adapter documentation
2. **Archon Code:** Multi-LoRA inference examples, LCM scheduler patterns
3. **Exa GitHub:** LoraHub, TASA, MoLoRA, HardLoRAMixer implementations
4. **Exa Web:** Production adapter switching patterns, PEFT version compatibility

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-09

### Workflow History for This Hypothesis
- Phase 2C experiment design initiated
- Prerequisites: H-E1 VALIDATED (72.67% top-1, 95.78% top-3)
- MCP research completed: Archon KB + Exa GitHub
- Experiment specification synthesized (Level 1.5)
- 8 reference implementations documented

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
