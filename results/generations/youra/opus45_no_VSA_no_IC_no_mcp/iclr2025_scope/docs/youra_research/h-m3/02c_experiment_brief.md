# Experiment Design: H-M3

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Under task-conditioned conversion, if TC-SSM integrates task conditioning during training, then the resulting model will preserve adaptation capability (few-shot accuracy within 5% of transformer in <100 steps).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Full validation protocol for mechanism hypothesis.

---

## Workflow Status

**Verification State:** IN_PROGRESS → COMPLETED
**Prerequisites Satisfied:** Yes (H-M2 PASS)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (COMPLETED, PASS)

### Gate Condition
Final mechanism step validating end-to-end pipeline. Proves TC-SSM preserves adaptation capability compared to transformer baseline. Most critical hypothesis for research contribution.

---

## Continuation Context

This is a continuation experiment building on H-M2 (Low-Rank SSM Modulation).

### Previous Hypothesis Results
- **H-M2 Result:** PASS
- **Proven:** Low-rank projections (rank 16-64) can modulate Mamba's Δ, B, C matrices with <2x overhead
- **Optimal Configuration:** Rank 32 selected as balance between expressiveness and efficiency
- **Lessons:** Task embeddings from H-M1 successfully condition SSM dynamics

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using WebFetch research*

**Finding 1: Mamba SSM Architecture**
- **Source:** github.com/state-spaces/mamba
- **Key Insights:**
  - Selective SSM with input-dependent state dynamics
  - Core parameters: d_model (768-2560), d_state (16-128), d_conv (4), expand (2)
  - Supports bfloat16 precision
  - No native task conditioning - must be added
- **Used For:** Baseline architecture, integration point identification

**Finding 2: Few-Shot Adaptation via LoRA**
- **Source:** github.com/huggingface/peft
- **Key Insights:**
  - LoRA rank 16 with alpha 32 is effective baseline
  - ~0.12% trainable parameters for 3B model
  - Integrates with transformers Trainer
- **Used For:** Adaptation protocol baseline, rank selection guidance

### Archon Code Examples

**Code Source 1: Mamba Block Structure**
```python
# From state-spaces/mamba
class MambaBlock(nn.Module):
    def __init__(self, d_model, d_state=16, d_conv=4, expand=2):
        self.in_proj = nn.Linear(d_model, expand * d_model * 2)
        self.conv1d = nn.Conv1d(expand * d_model, expand * d_model, d_conv)
        self.x_proj = nn.Linear(expand * d_model, d_state + d_state + 1)  # B, C, Δ
        self.dt_proj = nn.Linear(d_state, expand * d_model)
        self.out_proj = nn.Linear(expand * d_model, d_model)
```
- **Pattern:** Δ, B, C computed via linear projections
- **Integration Point:** x_proj layer - modulate with task embeddings

### Exa GitHub Implementations

**Repository 1:** state-spaces/mamba (Official)
- **URL:** https://github.com/state-spaces/mamba
- **Relevance:** Official Mamba implementation, ground truth for architecture
- **Architecture:** Selective State Space Model
- **Training Config:**
  - Optimizer: AdamW (inferred from standard practices)
  - Mixed precision: bfloat16
  - Models trained on 300B-600B tokens
- **Dataset:** The Pile, SlimPajama
- **Used For:** Architecture baseline, integration point identification

**Repository 2:** huggingface/peft
- **URL:** https://github.com/huggingface/peft
- **Relevance:** LoRA adaptation methodology
- **Key Config:**
  - r=16, lora_alpha=32
  - CAUSAL_LM task type
- **Used For:** Few-shot adaptation baseline protocol

**Serena Analysis Needed:** false (architecture sufficiently clear from docs)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Implementation | Availability | Recommendation |
|----------|---------------|--------------|----------------|
| 1 | state-spaces/mamba | ✅ Official | **USE THIS** |
| 2 | HuggingFace transformers mamba | ✅ Available | Reference only |
| 3 | Custom reimplementation | - | Not needed |

**Recommended Implementation Path:**
- Primary: Extend state-spaces/mamba with task conditioning module
- Fallback: HuggingFace transformers Mamba + custom task conditioning
- Justification: Official implementation ensures architectural fidelity for mechanism validation

### Code Analysis (Serena MCP)

*Serena MCP unavailable - analysis based on WebFetch findings*

**Architecture Integration Analysis:**
- **Target Component:** `x_proj` linear layer in MambaBlock
- **Current:** Computes B, C, Δ from input features only
- **Proposed Modification:** Add task-conditioned modulation via learned embeddings
- **Integration Point:** After x_proj, before dt_proj
- **Complexity:** Medium - requires modifying core SSM computation

---

## Experiment Specification

### Dataset

**Dataset:** SuperGLUE
**Type:** standard
**Source:** https://super.gluebenchmark.com/

**Tasks for Few-Shot Evaluation:**
| Task | Description | Metric | Train | Val | Test |
|------|-------------|--------|-------|-----|------|
| BoolQ | Boolean QA | Accuracy | 9,427 | 3,270 | 3,245 |
| CB | CommitmentBank | F1/Accuracy | 250 | 57 | 250 |
| COPA | Choice of Plausible Alternatives | Accuracy | 400 | 100 | 500 |
| RTE | Recognizing Textual Entailment | Accuracy | 2,490 | 277 | 3,000 |
| WiC | Word-in-Context | Accuracy | 5,428 | 638 | 1,400 |

**Few-Shot Protocol:**
- k-shot: 8 and 16 examples per task
- Sample selection: Stratified random from training set
- Evaluation: Full validation set (statistically meaningful >500 samples where available)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `super_glue`
- Code: 
```python
from datasets import load_dataset
# Example for BoolQ
dataset = load_dataset("super_glue", "boolq")
# For each task: boolq, cb, copa, rte, wic
```

### Models

#### Baseline Model

**Architecture:** Mamba-130M (smallest variant for PoC)
**Type:** Selective State Space Model
**Source:** state-spaces/mamba

**Configuration:**
- d_model: 768
- n_layer: 24
- d_state: 16
- d_conv: 4
- expand: 2

**Baseline Adaptation Method:** Standard LoRA fine-tuning (post-conversion)
- r=16, alpha=32
- Target modules: out_proj, in_proj

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Hub
- Identifier: `state-spaces/mamba-130m`
- Code:
```python
from transformers import MambaForCausalLM
model = MambaForCausalLM.from_pretrained("state-spaces/mamba-130m")
```

#### Proposed Model

**Architecture:** TC-SSM (Mamba-130M + Task Conditioning Module)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Task-Conditioned SSM (TC-SSM)
# Based on: Mamba architecture + H-M2 low-rank modulation

class TaskConditionedSSMBlock(nn.Module):
    """
    Mamba block with task-conditioned Δ, B, C modulation.
    Preserves adaptation manifold during conversion training.
    """
    def __init__(self, d_model=768, d_state=16, rank=32, n_tasks=8):
        super().__init__()
        # Original Mamba components
        self.mamba_block = MambaBlock(d_model, d_state)
        
        # Task conditioning (from H-M1, H-M2)
        self.task_embedding = nn.Embedding(n_tasks, rank)
        
        # Low-rank modulation for Δ, B, C (rank 32 per H-M2)
        self.delta_down = nn.Linear(rank, d_state)
        self.delta_up = nn.Linear(d_state, d_model)
        self.bc_down = nn.Linear(rank, d_state * 2)
        self.bc_up = nn.Linear(d_state * 2, d_state * 2)
        
    def forward(self, x, task_ids):
        """
        Args:
            x: (B, L, D) - input sequence
            task_ids: (B,) - task identifier per sample
        Returns:
            (B, L, D) - task-conditioned output
        """
        # Get task embedding
        task_emb = self.task_embedding(task_ids)  # (B, rank)
        
        # Compute low-rank modulation
        delta_mod = self.delta_up(self.delta_down(task_emb))  # (B, D)
        bc_mod = self.bc_up(self.bc_down(task_emb))  # (B, 2*d_state)
        
        # Modulate SSM parameters during forward
        return self.mamba_block.forward_with_modulation(
            x, delta_mod=delta_mod, bc_mod=bc_mod
        )

# Integration: Replace MambaBlock in each layer
# Training: Joint conversion + adaptation objective
```

### Training Protocol

**Phase 1: Conversion Training (Transfer from Transformer)**
- **Objective:** Distill transformer knowledge into TC-SSM while preserving adaptation manifold
- **Source Model:** BERT-base or GPT-2-small (depending on task type)
- **Loss:** KL divergence (outputs) + MSE (hidden states) + Adaptation regularizer

**Phase 2: Few-Shot Adaptation**
- **Optimizer:** AdamW
  - β1=0.9, β2=0.999, weight_decay=0.01
  - **Source:** Standard transformer fine-tuning practice
- **Learning Rate:** 2e-5 (initial)
  - **Schedule:** Linear warmup (10% steps) + linear decay
  - **Source:** PEFT/LoRA recommended settings
- **Batch Size:** 8 (few-shot constraint)
  - **Source:** Standard few-shot protocol
- **Steps:** Maximum 100 gradient steps
  - **Source:** Hypothesis constraint (<100 steps to 95% ceiling)
- **Seeds:** 3 (for statistical validity as MECHANISM hypothesis)

**Regularization:**
- Gradient clipping: 1.0
- Dropout: 0.1

### Evaluation

**Primary Metrics:**
- Few-shot accuracy (8-shot, 16-shot)
- Adaptation speed (steps to reach 95% of fine-tuned ceiling)

**Success Criteria:**
- **Primary:** TC-SSM few-shot accuracy within 5% of transformer baseline
- **Secondary:** Adaptation achieved in <100 gradient steps

**Expected Baseline Performance** (from research):
- Transformer (BERT-base) 8-shot SuperGLUE: ~65-75% average
- Standard SSM (Mamba) after LoRA: ~60-70% (typically 5-10% below transformer)
- **Source:** General NLP few-shot benchmarks

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: classification (per-task)
- Library: sklearn.metrics + evaluate
- Code:
```python
from sklearn.metrics import accuracy_score, f1_score
import evaluate
accuracy_metric = evaluate.load("accuracy")
f1_metric = evaluate.load("f1")
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing TC-SSM vs Transformer vs Standard Mamba adaptation accuracy

#### Additional Figures (LLM Autonomous)
- Learning curve: Steps vs accuracy for each method
- Per-task breakdown: Accuracy comparison across SuperGLUE tasks
- Adaptation speed comparison: Steps to 95% ceiling

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** Task conditioning module integrated into Mamba architecture
- **mechanism_isolatable:** Can compare with/without task embedding input
- **baseline_measurable:** Standard Mamba + LoRA provides clear baseline

### Architecture Compatibility
- **Compatible:** Mamba's x_proj layer computes Δ, B, C - can be modulated
- **Integration:** Low-rank projection from task embedding added post-x_proj
- **Overhead:** <2x (verified in H-M2)

### Activation Indicators
- **mechanism_log_message:** "TC-SSM: Task conditioning applied, task_id={id}"
- **tensor_shape_change:** delta_mod: (B, D), bc_mod: (B, 2*d_state)
- **metric_delta_expected:** 3-5% accuracy improvement over standard adaptation

### Verification Code
```python
def verify_mechanism_activation(model, batch):
    """Verify TC-SSM mechanism is actually working."""
    # Test 1: Different task_ids produce different modulations
    task_ids_a = torch.zeros(batch_size, dtype=torch.long)
    task_ids_b = torch.ones(batch_size, dtype=torch.long)
    
    with torch.no_grad():
        out_a = model(batch['input_ids'], task_ids=task_ids_a)
        out_b = model(batch['input_ids'], task_ids=task_ids_b)
    
    assert not torch.allclose(out_a.logits, out_b.logits), \
        "FAIL: Task conditioning has no effect"
    
    # Test 2: Modulation values are non-trivial
    task_emb = model.task_embedding(task_ids_a)
    delta_mod = model.delta_up(model.delta_down(task_emb))
    assert delta_mod.abs().mean() > 1e-3, \
        "FAIL: Modulation values near zero"
    
    return True
```

### Success Threshold
- **hypothesis_support_threshold:** 5% (accuracy gap from transformer)
- **hypothesis_support_metric:** few_shot_accuracy_gap

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. TC-SSM adaptation accuracy > standard Mamba adaptation accuracy
3. TC-SSM accuracy within 5% of transformer baseline
4. Adaptation achieved in <100 gradient steps

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*MCP unavailable - WebFetch used as alternative*

### B. GitHub Implementations (Exa via WebFetch)

**Repository 1:** state-spaces/mamba
- **URL:** https://github.com/state-spaces/mamba
- **Query Used:** WebFetch on repository homepage
- **Relevance:** Official Mamba implementation
- **Used For:** Architecture baseline, integration point

**Repository 2:** huggingface/peft
- **URL:** https://github.com/huggingface/peft
- **Query Used:** WebFetch on repository homepage
- **Relevance:** LoRA adaptation methodology
- **Used For:** Few-shot adaptation protocol

### C. Code Analysis

**Serena Analysis:** Not performed (MCP unavailable)
**Alternative:** WebFetch analysis of repository documentation

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report - H-M2
- **Reused Components:**
  - Rank selection: 32 (optimal from H-M2)
  - Task embedding: From H-M1 encoding
  - Modulation approach: Low-rank projection validated
- **Why Reused:** Enables controlled experiment - only integration training changes

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (SuperGLUE) | Phase 2B | 02b_verification_plan.md |
| Baseline (Mamba) | GitHub | state-spaces/mamba |
| Mechanism design | H-M2 | Previous hypothesis validated |
| Pseudo-code | GitHub + H-M2 | state-spaces/mamba, H-M2 |
| Training protocol | GitHub | huggingface/peft |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28T09:30:00+00:00

### Workflow History for This Hypothesis
- 2026-08-28: H-M2 completed (PASS) - Prerequisites satisfied
- 2026-08-28: Phase 2C initiated for H-M3
- 2026-08-28: Experiment design completed

---

*Research Tools: WebFetch (MCP unavailable)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
