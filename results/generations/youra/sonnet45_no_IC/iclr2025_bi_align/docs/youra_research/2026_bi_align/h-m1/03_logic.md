# Logic Design: H-M1 Shared Representation Learning

**Hypothesis:** H-M1  
**Type:** MECHANISM (Analysis)  
**Author:** Logic Agent  
**Date:** 2026-07-13  
**Status:** Ready for Implementation

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from H-E1 actual code  
**Analyzed Path:** `/workspace/TEST_bi_align/docs/youra_research/h-e1/code/`  
**Relevant Symbols:** JointDPOAttribute, BaselineDPO, ReferencePolicy, AttributeHead

**Critical Finding:** H-E1 models use `output_hidden_states=True` in forward pass. Hidden states accessed via `outputs.hidden_states[-1]` (last transformer layer). AttributeHead returns **list of logits** (not stacked tensor).

---

## Applied Patterns

**Applied:** PyTorch `output_hidden_states=True` for hidden state extraction  
**Applied:** Mean pooling over sequence dimension for representation aggregation  
**Applied:** Single linear layer for linear probing (minimal capacity test)  
**Applied:** Centered Kernel Alignment (CKA) for representation similarity  
**Applied:** Cosine similarity for gradient alignment measurement

---

## Epic-3: Linear Probing [11/20 Complexity, Budget: 2 Subtasks]

### L-3-1: PreferenceProbe and AttributeProbe [1/2 used]

**Applied:** Standard PyTorch nn.Module pattern with single linear layer

#### API Signatures

```python
class PreferenceProbe(nn.Module):
    def __init__(self, hidden_dim: int = 1600, num_classes: int = 2):
        """Linear probe for preference classification.
        
        Args:
            hidden_dim: Input dimension from GPT-2 XL
            num_classes: Binary classification (2)
        """
        ...
    
    def forward(self, hidden_states: Tensor) -> Tensor:
        """Forward pass. hidden: [B, H] -> [B, 2]"""
        ...


class AttributeProbe(nn.Module):
    def __init__(self, hidden_dim: int = 1600, num_attributes: int = 3, num_levels: int = 5):
        """Linear probe for attribute regression.
        
        Args:
            hidden_dim: Input dimension (1600)
            num_attributes: Number of attributes (3)
            num_levels: Levels per attribute (5)
        """
        ...
    
    def forward(self, hidden_states: Tensor) -> List[Tensor]:
        """Forward pass. hidden: [B, H] -> List of 3 × [B, 5]"""
        ...


class ProbeTrainer:
    def __init__(
        self,
        probe: nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cuda"
    ):
        """Initialize probe trainer."""
        ...
    
    def train_epoch(
        self,
        hidden_states: Tensor,
        labels: Tensor
    ) -> float:
        """Single epoch training. Returns: average loss"""
        ...
    
    def evaluate(
        self,
        hidden_states: Tensor,
        labels: Tensor
    ) -> dict:
        """Evaluate probe. Returns: {'accuracy': float} or {'r2': float}"""
        ...
    
    def train(
        self,
        train_data: tuple,
        val_data: tuple,
        epochs: int = 20
    ) -> dict:
        """Full training loop. Returns: {'train_history': list, 'val_history': list}"""
        ...
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| hidden_states | [B, H=1600] | Extracted from layer 47 |
| preference_logits | [B, 2] | Binary classification |
| attr_logits | List of 3 × [B, 5] | Per-attribute predictions |
| labels (pref) | [B] | Binary labels (0/1) |
| labels (attr) | [B, 3] | Attribute levels (1-5, needs -1 for 0-indexing) |

#### Pseudo-code

```
# PreferenceProbe forward
1. logits = linear(hidden_states)  # [B, H] -> [B, 2]
2. return logits

# AttributeProbe forward
1. attr_logits = [linear_i(hidden_states) for i in range(3)]  # 3 × [B, 5]
2. return attr_logits

# ProbeTrainer.train_epoch (Preference)
1. probe.train()
2. optimizer.zero_grad()
3. logits = probe(hidden_states)  # [B, 2]
4. loss = F.cross_entropy(logits, labels)  # []
5. loss.backward()
6. optimizer.step()
7. return loss.item()

# ProbeTrainer.train_epoch (Attribute)
1. probe.train()
2. optimizer.zero_grad()
3. attr_logits = probe(hidden_states)  # List of 3 × [B, 5]
4. loss = sum([F.cross_entropy(logits, labels[:, i] - 1) for i, logits in enumerate(attr_logits)]) / 3
5. loss.backward()
6. optimizer.step()
7. return loss.item()
```

### L-3-2: HiddenStateExtractor [1/2 used]

**Applied:** torch.no_grad() for frozen model inference

#### API Signatures

```python
class HiddenStateExtractor:
    def __init__(self, model: nn.Module, device: str = "cuda"):
        """Initialize extractor with frozen model."""
        ...
    
    def extract_from_batch(
        self,
        input_ids: Tensor,
        attention_mask: Tensor
    ) -> Tensor:
        """Extract hidden states from batch. input_ids: [B, L] -> [B, H=1600]"""
        ...
    
    def extract_from_dataset(
        self,
        dataloader: DataLoader
    ) -> Tensor:
        """Extract from full dataset. Returns: [N, H] where N=500"""
        ...
    
    def save_hidden_states(
        self,
        hidden_states: Tensor,
        save_path: str
    ):
        """Save extracted states to disk."""
        ...
```

#### Pseudo-code

```
# extract_from_batch
1. model.eval()
2. with torch.no_grad():
3.     outputs = model.model(input_ids, attention_mask=attention_mask, output_hidden_states=True)
4.     last_hidden = outputs.hidden_states[-1]  # [B, L, H=1600] (layer 47)
5.     pooled = last_hidden.mean(dim=1)  # [B, H] (mean over sequence)
6.     return pooled

# extract_from_dataset
1. all_hidden = []
2. for batch in dataloader:
3.     hidden = extract_from_batch(batch['input_ids'], batch['attention_mask'])  # [B, H]
4.     all_hidden.append(hidden)
5. return torch.cat(all_hidden, dim=0)  # [N, H]
```

---

## Epic-5: Gradient Alignment [10/20 Complexity, Budget: 2 Subtasks]

### L-5-1: GradientAnalyzer [1/2 used]

**Applied:** Cosine similarity for gradient angle measurement

#### API Signatures

```python
class GradientAnalyzer:
    def __init__(
        self,
        model: JointDPOAttribute,
        ref_policy: ReferencePolicy,
        device: str = "cuda"
    ):
        """Initialize gradient analyzer."""
        ...
    
    def compute_alignment(self, batch: dict) -> float:
        """Compute cosine similarity between DPO and attr gradients. Returns: cos(θ) ∈ [-1, 1]"""
        ...
    
    def analyze_dataset(
        self,
        dataloader: DataLoader,
        num_batches: int = 10
    ) -> dict:
        """Analyze multiple batches. Returns: {'mean': float, 'std': float, 'min': float, 'max': float}"""
        ...
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| grad_dpo | [P] | Flattened DPO gradients (P = total params) |
| grad_attr | [P] | Flattened attr gradients |
| cos_sim | [] | Scalar cosine similarity |

#### Pseudo-code

```
# compute_alignment
1. # Compute reference logits (frozen)
2. ref_chosen = ref_policy(batch['chosen_ids'])  # [B, L, V]
3. ref_rejected = ref_policy(batch['rejected_ids'])  # [B, L, V]

4. # Forward pass to get losses
5. loss_total, loss_dpo, loss_attr = model(
6.     batch['chosen_ids'], batch['rejected_ids'],
7.     ref_chosen, ref_rejected, batch['attributes']
8. )

9. # Extract DPO gradient
10. model.zero_grad()
11. loss_dpo.backward(retain_graph=True)
12. grad_dpo = torch.cat([p.grad.flatten() for p in model.parameters() if p.grad is not None])  # [P]

13. # Extract attr gradient
14. model.zero_grad()
15. loss_attr.backward()
16. grad_attr = torch.cat([p.grad.flatten() for p in model.parameters() if p.grad is not None])  # [P]

17. # Compute cosine similarity
18. cos_sim = F.cosine_similarity(grad_dpo.unsqueeze(0), grad_attr.unsqueeze(0), dim=1)  # []
19. return cos_sim.item()
```

### L-5-2: CKAComputer [1/2 used]

**Applied:** Centered Kernel Alignment formula

#### API Signatures

```python
class CKAComputer:
    @staticmethod
    def center_gram_matrix(K: Tensor) -> Tensor:
        """Center Gram matrix. K: [N, N] -> [N, N]"""
        ...
    
    @staticmethod
    def compute_cka(repr_a: Tensor, repr_b: Tensor) -> float:
        """Compute CKA similarity. repr: [N, H] -> scalar ∈ [0, 1]"""
        ...
    
    def compute_all_pairs(
        self,
        repr_joint: Tensor,
        repr_dpo: Tensor,
        repr_attr: Tensor
    ) -> dict:
        """Compute all pairwise CKA scores. Returns: 3×3 matrix as dict"""
        ...
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| repr_a, repr_b | [N=500, H=1600] | Representation matrices |
| K | [N, N] | Gram matrix |
| K_centered | [N, N] | Centered Gram matrix |
| cka_score | [] | Scalar similarity |

#### Pseudo-code

```
# center_gram_matrix
1. n = K.size(0)
2. H = torch.eye(n) - torch.ones(n, n) / n  # Centering matrix
3. K_centered = H @ K @ H  # [N, N]
4. return K_centered

# compute_cka
1. # Center representations
2. repr_a_c = repr_a - repr_a.mean(dim=0)  # [N, H]
3. repr_b_c = repr_b - repr_b.mean(dim=0)  # [N, H]

4. # Compute Gram matrices
5. K_a = repr_a_c @ repr_a_c.T  # [N, N]
6. K_b = repr_b_c @ repr_b_c.T  # [N, N]

7. # CKA formula: HSIC(K_a, K_b) / sqrt(HSIC(K_a, K_a) * HSIC(K_b, K_b))
8. hsic = (K_a * K_b).sum()  # []
9. var_a = (K_a ** 2).sum()  # []
10. var_b = (K_b ** 2).sum()  # []
11. cka = hsic / torch.sqrt(var_a * var_b)  # []
12. return cka.item()

# compute_all_pairs
1. pairs = [
2.     ('joint_dpo', repr_joint, repr_dpo),
3.     ('joint_attr', repr_joint, repr_attr),
4.     ('dpo_attr', repr_dpo, repr_attr)
5. ]
6. results = {}
7. for name, repr_1, repr_2 in pairs:
8.     results[name] = compute_cka(repr_1, repr_2)
9. return results
```

---

## External Dependencies API (Base Hypothesis H-E1)

### API Signatures (From Actual Code)

The following APIs are called from H-E1. Signatures verified from actual implementation at `/workspace/TEST_bi_align/docs/youra_research/h-e1/code/models/model.py`:

```python
# JointDPOAttribute (Primary model for analysis)
class JointDPOAttribute(nn.Module):
    def __init__(self, model_name="gpt2-xl", beta=0.1, alpha=0.7):
        """
        Args:
            model_name: HuggingFace model ID
            beta: DPO temperature (0.1)
            alpha: Loss weight for DPO (0.7)
        """
        ...
    
    def forward(
        self,
        chosen_ids: Tensor,
        rejected_ids: Tensor,
        ref_chosen_logits: Tensor,
        ref_rejected_logits: Tensor,
        target_attrs: Tensor
    ) -> tuple[Tensor, Tensor, Tensor]:
        """
        Forward pass with output_hidden_states=True internally.
        
        Returns:
            loss_total: Combined loss (scalar)
            loss_dpo: DPO component (scalar)
            loss_attr: Attribute component (scalar)
        
        NOTE: To extract hidden states, call model.model() directly:
            outputs = model.model(input_ids, output_hidden_states=True)
            hidden_states = outputs.hidden_states[-1]  # [B, L, 1600]
        """
        ...
    
    def compute_dpo_loss(
        self,
        chosen_logits: Tensor,
        rejected_logits: Tensor,
        ref_chosen_logits: Tensor,
        ref_rejected_logits: Tensor
    ) -> Tensor:
        """DPO loss computation. Returns: scalar"""
        ...
    
    def compute_attr_loss(
        self,
        hidden_states: Tensor,
        target_attrs: Tensor
    ) -> Tensor:
        """
        Attribute loss computation.
        
        Args:
            hidden_states: [B, L, H=1600] (full sequence)
            target_attrs: [B, 3] (attribute levels 1-5)
        
        Returns: scalar loss
        """
        ...


# BaselineDPO (DPO-only baseline)
class BaselineDPO(nn.Module):
    def __init__(self, model_name="gpt2-xl", beta=0.1):
        """DPO-only baseline."""
        ...
    
    def forward(
        self,
        chosen_ids: Tensor,
        rejected_ids: Tensor,
        ref_chosen_logits: Tensor,
        ref_rejected_logits: Tensor
    ) -> Tensor:
        """Returns: loss_dpo (scalar)"""
        ...


# ReferencePolicy (Frozen reference model)
class ReferencePolicy(nn.Module):
    def __init__(self, model_name="gpt2-xl"):
        """Frozen reference policy."""
        ...
    
    @torch.no_grad()
    def forward(self, input_ids: Tensor, attention_mask: Optional[Tensor] = None) -> Tensor:
        """
        Compute reference logits without gradients.
        
        Returns:
            logits: [B, L, V=50257]
        """
        ...


# AttributeHead (Used inside JointDPOAttribute)
class AttributeHead(nn.Module):
    def __init__(self, hidden_dim=1600, num_attributes=3, num_levels=5):
        """Multi-attribute classifier."""
        ...
    
    def forward(self, hidden_states: Tensor) -> List[Tensor]:
        """
        Args:
            hidden_states: [B, L, H=1600]
        
        Returns:
            List of 3 × [B, 5] (one per attribute)
        
        NOTE: Returns LIST, not stacked tensor!
        """
        ...
```

**Critical Notes:**
1. **Hidden State Access:** Use `model.model(input_ids, output_hidden_states=True).hidden_states[-1]` (access inner AutoModelForCausalLM)
2. **AttributeHead Output:** Returns **list of tensors**, not single stacked tensor
3. **Target Attributes:** 1-indexed (1-5), needs `-1` for cross_entropy loss
4. **Reference Logits:** Shape `[B, L, V]`, not sequence log-probs

**Verified from:** `/workspace/TEST_bi_align/docs/youra_research/h-e1/code/models/model.py` (lines 116-203)

---

## Implementation Notes

### Critical Paths

**Checkpoint Loading → Hidden State Extraction → Probing/CKA/Gradient Analysis**

1. Load 3 models (joint, DPO-only, attr-only) from H-E1 checkpoints
2. Extract hidden states (500 × 1600) per model
3. Train probing classifiers (20 epochs, lr=1e-3)
4. Compute CKA between model pairs
5. Analyze gradient alignment (10 batches)

### Data Flow

```
H-E1 checkpoints → Load models → Extract hidden states [500, 1600]
                                           ↓
                    ┌──────────────────────┼──────────────────────┐
                    ↓                      ↓                      ↓
            Linear Probing              CKA Computation    Gradient Alignment
          (Pref + Attr probes)         (3 model pairs)    (Cos similarity)
                    ↓                      ↓                      ↓
            Accuracy, R²                CKA scores           Mean, std, range
                    └──────────────────────┴──────────────────────┘
                                           ↓
                                  Gate Metrics Evaluation
                                  (PASS if all thresholds met)
```

### Tensor Shape Validation

**Key invariants:**
- Hidden states: `[N=500, H=1600]` per model
- Preference labels: `[N=500]` (binary 0/1)
- Attribute labels: `[N=500, A=3]` (1-5 scale)
- Gram matrices: `[N=500, N=500]` for CKA
- Gradient vectors: `[P]` where P = total trainable params (~1.56B)

### Error Handling

**Checkpoint Not Found:**
```python
if not os.path.exists(checkpoint_path):
    raise FileNotFoundError(f"H-E1 checkpoint missing: {checkpoint_path}. Run H-E1 first.")
```

**Shape Mismatch:**
```python
assert hidden_states.shape == (500, 1600), f"Expected [500, 1600], got {hidden_states.shape}"
```

**Probing NaN Loss:**
```python
if torch.isnan(loss):
    logger.warning("NaN loss detected, reducing learning rate")
    optimizer.param_groups[0]['lr'] *= 0.5
```

### Logging Format

**Probing metrics (JSON):**
```json
{
  "preference_probe": {
    "train_acc": [0.52, 0.61, 0.68, ..., 0.73],
    "val_acc": [0.50, 0.58, 0.64, ..., 0.71],
    "final_acc": 0.71
  },
  "attribute_probe": {
    "train_r2": [[0.21, 0.18, 0.25], ..., [0.65, 0.62, 0.68]],
    "val_r2": [[0.19, 0.16, 0.23], ..., [0.63, 0.60, 0.65]],
    "final_r2": [0.63, 0.60, 0.65]
  }
}
```

**CKA results (JSON):**
```json
{
  "joint_dpo": 0.65,
  "joint_attr": 0.58,
  "dpo_attr": 0.42
}
```

**Gradient alignment (JSON):**
```json
{
  "mean": 0.12,
  "std": 0.18,
  "min": -0.25,
  "max": 0.45,
  "values": [0.15, -0.03, 0.22, ...]
}
```

---

## Subtask Budget Summary

| Epic | Task | Subtasks Used | Budget |
|------|------|---------------|--------|
| Epic-3 | L-3-1: Probing Classifiers | 1 | 2 |
| Epic-3 | L-3-2: Hidden State Extractor | 1 | |
| Epic-5 | L-5-1: Gradient Analyzer | 1 | 2 |
| Epic-5 | L-5-2: CKA Computer | 1 | |
| **Total** | | **4** | **4** |

---

**Logic Design Status:** Complete - Ready for Phase 4 Implementation  
**Next Step:** Phase 4 Coder Agent
