# Logic Design: H-E1 Joint Training Existence

**Hypothesis:** H-E1  
**Type:** EXISTENCE (PoC)  
**Author:** Logic Agent  
**Date:** 2026-07-13  
**Status:** Ready for Implementation

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch - no existing code to analyze  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation

**Rationale:** This is a foundational EXISTENCE hypothesis with no base hypothesis or existing codebase to reference. All APIs are designed from scratch based on DPO (Rafailov et al. 2023) and SteerLM (Dong et al. 2023) specifications.

---

## Applied Patterns

**Applied:** PyTorch torch.no_grad() decorator for frozen reference policy  
**Applied:** F.cross_entropy for attribute prediction loss  
**Applied:** Weighted loss summation for multi-task training  
**Applied:** Log-probability computation via log_softmax + gather pattern

---

## Epic-2: Model Implementation [12/20 Complexity, Budget: 4 Subtasks]

### L-2-1: BaselineDPO Model [1/4 used]

**Applied:** Standard PyTorch nn.Module pattern

#### API Signatures

```python
class BaselineDPO(nn.Module):
    def __init__(
        self,
        model_name: str = "gpt2-xl",
        beta: float = 0.1
    ):
        """Initialize DPO-only baseline model.
        
        Args:
            model_name: HuggingFace model identifier
            beta: DPO temperature parameter
        """
        ...
    
    def forward(
        self,
        chosen_ids: Tensor,
        rejected_ids: Tensor,
        ref_chosen_logprobs: Tensor,
        ref_rejected_logprobs: Tensor
    ) -> Tensor:
        """Compute DPO loss. Returns: scalar loss"""
        ...
    
    def compute_logprobs(
        self,
        input_ids: Tensor,
        attention_mask: Tensor
    ) -> Tensor:
        """Compute log P(y|x). input_ids: [B, L] -> [B]"""
        ...
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| chosen_ids | [B, L] | Chosen response tokens |
| rejected_ids | [B, L] | Rejected response tokens |
| ref_chosen_logprobs | [B] | Reference policy log P(chosen) |
| ref_rejected_logprobs | [B] | Reference policy log P(rejected) |
| output | [] | Scalar loss |

#### Pseudo-code

```
1. chosen_logprobs = compute_logprobs(chosen_ids, mask)  # [B]
2. rejected_logprobs = compute_logprobs(rejected_ids, mask)  # [B]
3. chosen_ratio = chosen_logprobs - ref_chosen_logprobs  # [B]
4. rejected_ratio = rejected_logprobs - ref_rejected_logprobs  # [B]
5. logits = beta * (chosen_ratio - rejected_ratio)  # [B]
6. loss = -log_sigmoid(logits).mean()  # []
```

### L-2-2: JointDPOAttribute Model [1/4 used]

**Applied:** Multi-head architecture with shared backbone

#### API Signatures

```python
class JointDPOAttribute(nn.Module):
    def __init__(
        self,
        model_name: str = "gpt2-xl",
        beta: float = 0.1,
        alpha: float = 0.7,
        num_attributes: int = 3,
        num_levels: int = 5
    ):
        """Initialize joint DPO + attribute model.
        
        Args:
            model_name: HuggingFace model identifier
            beta: DPO temperature
            alpha: Loss weight for DPO (1-alpha for attribute)
            num_attributes: Number of attributes (e.g., 3)
            num_levels: Levels per attribute (1-5 scale)
        """
        ...
    
    def forward(
        self,
        chosen_ids: Tensor,
        rejected_ids: Tensor,
        ref_chosen_logprobs: Tensor,
        ref_rejected_logprobs: Tensor,
        target_attrs: Tensor
    ) -> tuple[Tensor, Tensor, Tensor]:
        """Forward pass. Returns: (loss_total, loss_dpo, loss_attr)"""
        ...
    
    def compute_dpo_loss(
        self,
        chosen_logits: Tensor,
        rejected_logits: Tensor,
        ref_chosen: Tensor,
        ref_rejected: Tensor
    ) -> Tensor:
        """Compute DPO loss component. Returns: scalar"""
        ...
    
    def compute_attr_loss(
        self,
        chosen_hidden: Tensor,
        target_attrs: Tensor
    ) -> Tensor:
        """Compute attribute loss. chosen_hidden: [B, H] -> scalar"""
        ...
    
    def predict_attributes(
        self,
        hidden_state: Tensor
    ) -> Tensor:
        """Predict attributes. hidden: [B, H] -> [B, A, L]"""
        ...
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| chosen_ids | [B, L] | Chosen response tokens |
| rejected_ids | [B, L] | Rejected response tokens |
| target_attrs | [B, A] | Target attribute levels (A=3 attributes) |
| chosen_hidden | [B, H] | Final hidden state from chosen |
| attr_logits | [B, A, L] | Attribute predictions (L=5 levels) |
| loss_total | [] | Combined loss |
| loss_dpo | [] | DPO component |
| loss_attr | [] | Attribute component |

#### Pseudo-code

```
1. chosen_output = lm_model(chosen_ids)  # [B, L, H]
2. rejected_output = lm_model(rejected_ids)  # [B, L, H]
3. chosen_hidden = chosen_output[:, -1, :]  # [B, H] (final token)
4. loss_dpo = compute_dpo_loss(chosen_output, rejected_output, refs)  # []
5. attr_logits = attr_head(chosen_hidden)  # [B, A, L]
6. loss_attr = F.cross_entropy(attr_logits.view(B*A, L), target_attrs.view(B*A))  # []
7. loss_total = alpha * loss_dpo + (1 - alpha) * loss_attr  # []
```

### L-2-3: ReferencePolicy (Frozen) [1/4 used]

**Applied:** torch.no_grad() decorator for frozen inference

#### API Signatures

```python
class ReferencePolicy(nn.Module):
    def __init__(self, model_name: str = "gpt2-xl"):
        """Initialize frozen reference policy.
        
        Args:
            model_name: Same as training model for PoC
        """
        ...
    
    @torch.no_grad()
    def compute_logprobs(
        self,
        input_ids: Tensor,
        attention_mask: Tensor
    ) -> Tensor:
        """Compute log P(y|x) without gradients. input_ids: [B, L] -> [B]"""
        ...
```

#### Pseudo-code

```
1. with torch.no_grad():
2.     logits = model(input_ids, attention_mask=mask).logits  # [B, L, V]
3.     log_probs = F.log_softmax(logits, dim=-1)  # [B, L, V]
4.     token_log_probs = log_probs.gather(2, input_ids.unsqueeze(-1)).squeeze(-1)  # [B, L]
5.     sequence_log_prob = token_log_probs.sum(dim=1)  # [B]
6.     return sequence_log_prob
```

### L-2-4: Attribute Prediction Head [1/4 used]

**Applied:** Standard classification head with separate outputs per attribute

#### API Signatures

```python
class AttributeHead(nn.Module):
    def __init__(
        self,
        hidden_dim: int = 1600,
        num_attributes: int = 3,
        num_levels: int = 5
    ):
        """Multi-attribute prediction head.
        
        Args:
            hidden_dim: Input dimension from LM
            num_attributes: Number of attributes (3)
            num_levels: Levels per attribute (5)
        """
        ...
    
    def forward(self, hidden_state: Tensor) -> Tensor:
        """Predict attributes. hidden: [B, H] -> [B, A, L]"""
        ...
```

#### Pseudo-code

```
1. attr_logits = []
2. for i in range(num_attributes):
3.     logit = linear_layers[i](hidden_state)  # [B, L]
4.     attr_logits.append(logit)
5. return torch.stack(attr_logits, dim=1)  # [B, A, L]
```

---

## Epic-3: Training Loop [10/20 Complexity, Budget: 2 Subtasks]

### L-3-1: JointTrainer [1/2 used]

**Applied:** Standard training loop with multi-loss monitoring

#### API Signatures

```python
class JointTrainer:
    def __init__(
        self,
        model: JointDPOAttribute,
        ref_policy: ReferencePolicy,
        train_loader: DataLoader,
        optimizer: Optimizer,
        scheduler: LRScheduler,
        device: str,
        log_dir: str,
        checkpoint_dir: str
    ):
        """Initialize trainer with all components."""
        ...
    
    def train_step(self, batch: dict) -> dict:
        """Single training step. Returns: metrics dict"""
        ...
    
    def train(
        self,
        num_steps: int,
        log_interval: int = 100,
        checkpoint_interval: int = 1000
    ):
        """Main training loop."""
        ...
    
    def save_checkpoint(self, step: int, metrics: dict):
        """Save model checkpoint with metadata."""
        ...
```

#### train_step Pseudo-code

```
1. # Get reference logprobs (frozen)
2. ref_chosen = ref_policy.compute_logprobs(batch['chosen_ids'], batch['chosen_mask'])  # [B]
3. ref_rejected = ref_policy.compute_logprobs(batch['rejected_ids'], batch['rejected_mask'])  # [B]

4. # Forward pass
5. loss_total, loss_dpo, loss_attr = model(
6.     batch['chosen_ids'], batch['rejected_ids'],
7.     ref_chosen, ref_rejected, batch['attributes']
8. )  # 3 scalars

9. # Backward pass
10. optimizer.zero_grad()
11. loss_total.backward()
12. torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
13. optimizer.step()
14. scheduler.step()

15. # Return metrics
16. return {
17.     'loss_total': loss_total.item(),
18.     'loss_dpo': loss_dpo.item(),
19.     'loss_attr': loss_attr.item(),
20.     'lr': scheduler.get_last_lr()[0]
21. }
```

### L-3-2: GradientMonitor [1/2 used]

**Applied:** Cosine similarity for gradient angle computation

#### API Signatures

```python
class GradientMonitor:
    def __init__(self, model: nn.Module, alert_threshold: float = 120.0):
        """Initialize gradient conflict monitor.
        
        Args:
            model: Model to monitor
            alert_threshold: Angle threshold in degrees (120° = catastrophic)
        """
        ...
    
    def compute_gradient_angle(
        self,
        loss_dpo: Tensor,
        loss_attr: Tensor
    ) -> float:
        """Compute angle between DPO and attribute gradients. Returns: degrees [0, 180]"""
        ...
    
    def log_angle(self, angle: float, step: int):
        """Log gradient angle to file."""
        ...
```

#### compute_gradient_angle Pseudo-code

```
1. # Compute DPO gradient
2. optimizer.zero_grad()
3. loss_dpo.backward(retain_graph=True)
4. grad_dpo = torch.cat([p.grad.flatten() for p in model.parameters() if p.grad is not None])  # [P]

5. # Compute attribute gradient
6. optimizer.zero_grad()
7. loss_attr.backward()
8. grad_attr = torch.cat([p.grad.flatten() for p in model.parameters() if p.grad is not None])  # [P]

9. # Compute angle
10. cos_sim = F.cosine_similarity(grad_dpo.unsqueeze(0), grad_attr.unsqueeze(0))  # []
11. angle_rad = torch.acos(cos_sim.clamp(-1, 1))  # []
12. angle_deg = angle_rad * 180 / math.pi  # []
13. return angle_deg.item()
```

---

## Implementation Notes

### Critical Paths

**Model Dependency Chain:**
1. ReferencePolicy (frozen copy) → BaselineDPO → JointDPOAttribute
2. AttributeHead integrated into JointDPOAttribute
3. GradientMonitor operates on JointDPOAttribute

**Data Flow:**
```
batch → ref_policy.compute_logprobs() → model.forward() → losses → backward() → optimizer.step()
                                              ↓
                                      (every 100 steps)
                                              ↓
                                  gradient_monitor.compute_angle()
```

### Tensor Shape Validation

**Key invariants:**
- All sequence lengths L ≤ 512 (max_length constraint)
- Batch size B = 128 (fixed)
- Hidden dim H = 1600 (GPT-2 XL)
- Vocab size V = 50257 (GPT-2 tokenizer)
- Attributes A = 3 (helpfulness, verbosity, creativity)
- Levels L = 5 (1-5 scale)

### Error Handling

**NaN Detection:**
```python
if torch.isnan(loss_total):
    raise RuntimeError(f"NaN loss at step {step}. Stopping training.")
```

**Gradient Explosion:**
```python
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

**Checkpoint Corruption:**
```python
try:
    checkpoint = torch.load(path)
except Exception as e:
    logger.warning(f"Checkpoint {path} corrupted, reverting to previous")
    path = previous_checkpoint_path
```

### Logging Format

**Training logs (JSONL):**
```json
{
  "step": 100,
  "loss_total": 0.523,
  "loss_dpo": 0.412,
  "loss_attr": 0.372,
  "gradient_angle": 45.2,
  "lr": 9.8e-6
}
```

### Checkpoint Structure

```python
{
    'step': int,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'scheduler_state_dict': scheduler.state_dict(),
    'metrics': {
        'loss_total': float,
        'loss_dpo': float,
        'loss_attr': float
    }
}
```

---

## Subtask Budget Summary

| Epic | Task | Subtasks Used | Budget |
|------|------|---------------|--------|
| Epic-2 | L-2-1: BaselineDPO | 1 | 4 |
| Epic-2 | L-2-2: JointDPOAttribute | 1 | |
| Epic-2 | L-2-3: ReferencePolicy | 1 | |
| Epic-2 | L-2-4: AttributeHead | 1 | |
| Epic-3 | L-3-1: JointTrainer | 1 | 2 |
| Epic-3 | L-3-2: GradientMonitor | 1 | |
| **Total** | | **6** | **6** |

---

**Logic Design Status:** Complete - Ready for Phase 4 Implementation  
**Next Step:** Phase 4 Coder Agent
