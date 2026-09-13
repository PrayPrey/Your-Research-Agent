# Experiment Design: H-E1

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Both matrix-level and token-level objectives can be implemented in unified Phi-Mamba framework
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (None required)
**Gate Status:** MUST_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
Both matrix-level (MOHAWK-style) and token-level (CAB-style) distillation objectives must train without errors for 100M tokens in a unified Phi-Mamba framework. Loss curves must show expected learning behavior (decreasing, no NaN/divergence).

---

## Continuation Context

This is the foundation hypothesis - no previous context required.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in verification chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct hits for Mamba/SSM distillation in indexed knowledge base. Primary knowledge sourced from Exa GitHub search and paper references.

### Archon Code Examples

No direct MOHAWK/CAB code examples in Archon KB. Diffusion model training examples found but not applicable.

### Exa GitHub Implementations

**Primary Sources Found:**

1. **MOHAWK/Phi-Mamba (goombalab/phi-mamba)**
   - Official implementation of matrix-level distillation
   - 3-stage progressive distillation: Matrix Orientation → Hidden-State Alignment → Weight-Transfer + KD
   - Uses Mamba-2 discrete variant as matrix mixer
   - Stage 1 loss: Frobenius norm between attention matrix and SSM transfer matrix
   - Stage 2 loss: L2 norm between block hidden states
   - Pretrained weights: `goombalab/Phi-Mamba` on HuggingFace

2. **CAB (wph6/CAB)**
   - Token-level distillation via Attention Bridge
   - Aligns Q/K (Transformer) with B/C (Mamba) via lightweight MLPs
   - Loss: L2 alignment between φ_B(B) and K, φ_C(C) and Q
   - Avoids O(L²) attention map materialization
   - Two-stage: 200M tokens attention alignment, then KL logits distillation

3. **MOHAWK Framework (goombalab/mohawk)**
   - General distillation framework supporting Llama, Qwen2, Falcon, Phi hybrids
   - YAML config system with LOAD-based inheritance
   - Supports: supervised, hstates, matrices, dpo objectives
   - DDP/FSDP distributed training

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Source | Priority | Rationale |
|--------|----------|-----------|
| goombalab/phi-mamba | **PRIMARY** | Official MOHAWK implementation, exact Phi-Mamba architecture |
| wph6/CAB | **PRIMARY** | Official CAB implementation, proven on Phi-Mamba |
| goombalab/mohawk | SECONDARY | Generic framework, may need adaptation |

**Recommended Implementation Path:**
- Primary: Fork `goombalab/phi-mamba`, integrate CAB attention bridge from `wph6/CAB`
- Fallback: Use `goombalab/mohawk` framework with custom objective modules
- Justification: Official repos provide exact architectures; CAB already tested on Phi-Mamba in paper

### Code Analysis (Serena MCP)

*Serena analysis skipped - no local codebase to analyze for this hypothesis. Implementation will clone external repos.*

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | C4 (Colossal Clean Crawled Corpus) |
| **Source** | HuggingFace: `allenai/c4` |
| **Split** | `en` subset, streaming mode |
| **Type** | standard |
| **Size** | 100M tokens for smoke test (1.5B for full H-M3) |
| **Preprocessing** | Tokenize with Phi-1.5 tokenizer, truncate/pad to 2048 |
| **Context Length** | 2048 tokens (matching Phi-1.5 training) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets streaming
- Identifier: `allenai/c4`, config `en`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("allenai/c4", "en", split="train", streaming=True)
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| **Name** | Phi-1.5 (Teacher) |
| **Architecture** | Transformer, 24 layers, 2048 hidden, 32 heads |
| **Parameters** | 1.3B |
| **Source** | HuggingFace: `microsoft/phi-1_5` |
| **Role** | Teacher model providing supervision signals |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `microsoft/phi-1_5`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
teacher = AutoModelForCausalLM.from_pretrained("microsoft/phi-1_5", attn_implementation="eager")
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1_5")
```

#### Proposed Model

**Architecture:** Phi-Mamba (Student) - Phi-1.5 with attention replaced by Mamba-2 mixer

**Core Mechanism Implementation:**

```python
# Unified Phi-Mamba Framework with Dual Objectives
# Supports both MOHAWK (matrix-level) and CAB (token-level) distillation

class UnifiedDistillationFramework:
    def __init__(self, teacher, student, objective_type="matrix"):
        self.teacher = teacher  # Phi-1.5
        self.student = student  # Phi-Mamba
        self.objective_type = objective_type
        
        if objective_type == "token":
            # CAB: MLP bridges for B/C to K/Q alignment
            self.phi_B = MLP(d_state, d_head)  # B -> K projection
            self.phi_C = MLP(d_state, d_head)  # C -> Q projection
    
    def compute_loss(self, input_ids, layer_idx):
        # Get teacher outputs
        teacher_out = self.teacher(input_ids, output_attentions=True, output_hidden_states=True)
        
        if self.objective_type == "matrix":
            # MOHAWK Stage 1: Matrix-level alignment
            attn_matrix = teacher_out.attentions[layer_idx]  # [B, H, L, L]
            student_out = self.student.layers[layer_idx](
                teacher_out.hidden_states[layer_idx], return_mixer_matrix=True
            )
            transfer_matrix = student_out["transfer_matrix"]  # [B, H, L, L]
            loss = torch.linalg.matrix_norm(transfer_matrix - attn_matrix, ord="fro").mean()
            
        elif self.objective_type == "token":
            # CAB: Token-level alignment (B/C to K/Q)
            K = teacher_out.hidden_states[layer_idx] @ self.teacher.layers[layer_idx].self_attn.k_proj.weight.T
            Q = teacher_out.hidden_states[layer_idx] @ self.teacher.layers[layer_idx].self_attn.q_proj.weight.T
            
            student_out = self.student.layers[layer_idx](
                teacher_out.hidden_states[layer_idx], return_bc=True
            )
            B, C = student_out["B"], student_out["C"]  # Mamba projections
            
            # Align via learned projections (avoids O(L²) matrix)
            loss = (
                F.mse_loss(self.phi_B(B), K) + 
                F.mse_loss(self.phi_C(C), Q)
            )
        
        return loss

# Training loop (100M token smoke test)
def train_smoke_test(framework, dataloader, num_tokens=100_000_000):
    optimizer = torch.optim.AdamW(framework.student.parameters(), lr=1e-4)
    tokens_seen = 0
    
    for batch in dataloader:
        loss = sum(framework.compute_loss(batch, l) for l in range(num_layers)) / num_layers
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        
        tokens_seen += batch.numel()
        if tokens_seen >= num_tokens:
            break
    
    return {"final_loss": loss.item(), "converged": not torch.isnan(loss)}
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **Optimizer** | AdamW | Standard for transformer distillation |
| **Learning Rate** | 1e-4 (Stage 1/2), 5e-5 (Stage 3) | Following MOHAWK paper |
| **LR Schedule** | Cosine with warmup | 1000 step warmup |
| **Batch Size** | 32 (effective) | 8 per GPU × 4 grad accum |
| **Sequence Length** | 2048 | Phi-1.5 training length |
| **Tokens** | 100M (smoke test) | Minimum to verify convergence |
| **Precision** | BF16 mixed | Memory efficiency |
| **Gradient Clipping** | 1.0 | Stability |

**Stage-wise Protocol (MOHAWK):**
1. Stage 1 (Matrix): 40M tokens, train mixer only
2. Stage 2 (Hidden): 40M tokens, train full block
3. Stage 3 (E2E): 20M tokens, full model with KL loss

**Stage-wise Protocol (CAB):**
1. Stage 1 (Attention Bridge): 60M tokens, train φ_B, φ_C MLPs
2. Stage 2 (KL Distillation): 40M tokens, freeze bridges, train student

### Evaluation

| Metric | Target | Justification |
|--------|--------|---------------|
| **Training Loss** | Decreasing trend | Basic convergence check |
| **Loss Variance** | Stable (no spikes) | No divergence |
| **NaN Check** | Zero NaN values | Numerical stability |
| **Gradient Norm** | < 10.0 average | Not exploding |

**Success Criteria (PoC):**
1. ✅ Both objectives train without runtime errors
2. ✅ Loss decreases over 100M tokens for both
3. ✅ No NaN/Inf in loss or gradients
4. ✅ Final loss < initial loss by >50%

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Language modeling convergence validation
- Library: PyTorch native (loss tracking, gradient norms)
- Code:
```python
# No external metrics library needed for PoC
metrics = {
    "loss_history": [],
    "grad_norm_history": [],
    "nan_count": 0,
    "converged": lambda hist: hist[-1] < hist[0] * 0.5
}
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Loss curves for both objectives (matrix vs token) over 100M tokens

#### Additional Figures (LLM Autonomous)

1. **Loss Convergence Plot**: Training loss vs tokens for both MOHAWK and CAB
2. **Gradient Norm Distribution**: Histogram of gradient norms per objective
3. **Layer-wise Loss Heatmap**: Loss contribution per layer for both methods

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for 100M tokens (both objectives)
2. `final_loss_matrix < initial_loss_matrix * 0.5`
3. `final_loss_token < initial_loss_token * 0.5`
4. `nan_count == 0` for both

**Gate Decision:**
- PASS: Both objectives converge → Proceed to H-M1
- FAIL: Either objective fails → PIVOT to separate codebases with matched hyperparameters

---

## Appendix: Reference Implementations

### Primary References

| Reference | URL | Usage |
|-----------|-----|-------|
| **MOHAWK Paper** | https://arxiv.org/abs/2408.10189 | Matrix-level distillation theory |
| **CAB Paper** | https://arxiv.org/abs/2510.19266 | Token-level distillation theory |
| **Phi-Mamba Repo** | https://github.com/goombalab/phi-mamba | MOHAWK Stage 1/2 implementation |
| **CAB Repo** | https://github.com/wph6/CAB | Attention bridge implementation |
| **MOHAWK Framework** | https://github.com/goombalab/mohawk | General distillation utilities |

### Key Code Snippets

**MOHAWK Stage 1 (from phi-mamba/assets/mohawk_stage1.py):**
```python
loss = torch.linalg.matrix_norm(transfer_matrix - attn_matrix, ord="fro").mean()
```

**MOHAWK Stage 2 (from phi-mamba/assets/mohawk_stage2.py):**
```python
loss = torch.norm(student_output["hidden_states"] - teacher_hstate, p=2, dim=(-1,)).mean()
```

**CAB Attention Alignment:**
```python
L_attn = (1/L) * sum(
    ||phi_B(B[l]) - K[g(l)]||_2^2 + ||phi_C(C[l]) - Q[g(l)]||_2^2
    for l in range(L_student)
)
```

### Dependencies

```
torch==2.1.0
transformers>=4.36.0
mamba-ssm>=1.0.0
causal-conv1d==1.1.1
flash-attn==2.5.8  # for hybrid model only
datasets>=2.14.0
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18T14:00:00Z

### Workflow History for This Hypothesis
- 2026-08-18: H-E1 status set to IN_PROGRESS
- 2026-08-18: Phase 2C experiment design initiated
- 2026-08-18: MCP research completed (Archon KB, Exa GitHub)
- 2026-08-18: Experiment brief generated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
