# Logic Design: h-e1 Temporal Convergence Validation

**Hypothesis:** h-e1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-28  
**Author:** yoon303@ust.ac.kr  

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - no existing codebase to analyze  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - designing new APIs from scratch  

---

## Knowledge Base Patterns Applied

**Applied**: Standard PyTorch training loop pattern  
**Applied**: DataLoader factory pattern  
**Applied**: Gradient accumulation pattern for convergence detection  

---

## A-3: Ablation Trainer [Complexity: 13, Budget: 3]

### API Signatures

```python
class AblationTrainer:
    """Trains models with gradient-based convergence tracking."""
    
    def __init__(
        self,
        model: nn.Module,
        dataset_name: str,
        device: str = 'cuda',
        lr: float = 0.001,
        weight_decay: float = 1e-4,
        convergence_threshold: float = 0.1,
        convergence_window: int = 3
    ):
        """Initialize trainer with model and hyperparameters."""
        ...
    
    def train_variant(
        self,
        variant: str,
        dataloader: DataLoader,
        max_epochs: int
    ) -> Optional[int]:
        """
        Train model variant until convergence.
        variant: 'spurious' | 'core' | 'baseline'
        Returns: convergence epoch or None
        """
        ...
    
    def compute_gradient_norm(self) -> float:
        """Compute L2 norm of all model gradients. Returns: scalar float"""
        ...
    
    def check_convergence(self) -> bool:
        """Check if gradient norm < threshold × peak for window epochs."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| images | [B, 3, 224, 224] | Batch of images |
| labels | [B] | Binary labels |
| logits | [B, 2] | Model output |
| grad_norm | scalar | L2 norm of all gradients |

### Pseudo-code

```
train_variant(variant, dataloader, max_epochs):
    1. optimizer = SGD(model.params, lr, momentum=0.9, wd)
    2. criterion = BCEWithLogitsLoss()
    3. grad_history = []
    4. peak_grad = 0
    
    5. for epoch in range(max_epochs):
        6. for batch in dataloader:
            7. logits = model(images)  # [B, 2]
            8. loss = criterion(logits, labels)
            9. optimizer.zero_grad()
            10. loss.backward()
            11. optimizer.step()
        
        12. grad_norm = compute_gradient_norm()  # scalar
        13. grad_history.append(grad_norm)
        14. peak_grad = max(peak_grad, grad_norm)
        
        15. if check_convergence():
            16. return epoch
    
    17. return None

compute_gradient_norm():
    1. total = 0.0
    2. for p in model.parameters():
        3. if p.grad is not None:
            4. total += (p.grad ** 2).sum()
    5. return sqrt(total)

check_convergence():
    1. if len(grad_history) < window:
        2. return False
    3. recent = grad_history[-window:]
    4. threshold_val = peak_grad * threshold
    5. return all(g < threshold_val for g in recent)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Gradient tracking | Compute and store L2 norm per epoch |
| L-3-2 | Convergence detection | 3-epoch window check against 10% threshold |
| L-3-3 | Training loop | Standard ERM with optimizer and loss |

---

## Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in comments
- [x] Subtask count within budget (3/3)
- [x] Total length < 600 lines
- [x] Codebase Analysis section included
- [x] Green-field project noted
- [x] EXISTENCE PoC: minimal API only (single forward pass, no variants)

---

**Output for Phase 4 Coder:**
- File: `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/h-e1/03_logic.md`
- Allocated: Task A-3 (Ablation Trainer)
- Budget: 3 subtasks, all used
- API signatures match architecture spec exactly
