# Experiment Design: H-M1

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** L_agency integrates stably with DPO loss (training completes, loss decreases)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests that BiDPO training remains stable with auxiliary agency loss.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 PASSED: correlation=-0.026 < 0.7)
**Gate Status:** MUST_WORK (training must complete without NaN, loss must decrease)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASSED)

### Gate Condition
Training completes without NaN errors AND total loss decreases over training steps. This validates that L_agency can be combined with L_DPO without destabilizing optimization.

---

## Continuation Context

This experiment builds on H-E1 results showing collaboration score is orthogonal to preference labels (r=-0.026). The validated collab_score_v2 function from H-E1 will be reused to compute L_agency = 1 - collab_score during training.

### Previous Hypothesis Results
**H-E1 (Existence) - PASSED:**
- Correlation: -0.026 (well below 0.7 threshold)
- p-value: 0.25 (not statistically significant correlation)
- Conclusion: Collaboration score extracts agency signals orthogonal to preference labels

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct DPO training examples in KB. Found general training loop patterns:
- Standard PyTorch training loop with `optimizer.zero_grad()`, `loss.backward()`, `optimizer.step()`
- Loss computation patterns supporting L2 and Huber loss variants
- Multi-loss combination via weighted sum is standard approach

### Archon Code Examples

Training loop pattern identified:
```python
loss = torch.sum((model_pred - target) ** 2)
optimizer.zero_grad()
loss.backward()
optimizer.step()
```

### Exa GitHub Implementations

**TRL DPOTrainer (Primary Source):**
- HuggingFace TRL library provides production-ready DPOTrainer
- Supports multiple loss types via `loss_type` parameter
- **Multi-loss combination supported:** `loss_type=["sigmoid", "bco_pair", "sft"]` with `loss_weights=[0.8, 0.2, 1.0]`
- Key hyperparameters: `beta=0.1`, `learning_rate=5e-7`

**DPO Loss Formula:**
```
L_DPO = -E[log σ(β(log π_θ(y+|x)/π_ref(y+|x) - log π_θ(y-|x)/π_ref(y-|x)))]
```

**torchtune DPOLoss Implementation:**
```python
pi_logratios = policy_chosen_logps - policy_rejected_logps
ref_logratios = reference_chosen_logps - reference_rejected_logps
logits = pi_logratios - ref_logratios
losses = -F.logsigmoid(self.beta * logits) * (1 - self.label_smoothing)
         - F.logsigmoid(-self.beta * logits) * self.label_smoothing
```

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

TRL DPOTrainer is the de-facto standard for DPO training. The multi-loss combination feature (`loss_type`, `loss_weights`) directly supports adding auxiliary objectives.

**Recommended Implementation Path:**
- Primary: Extend TRL DPOTrainer with custom L_agency loss
- Fallback: Custom training loop using torchtune DPOLoss module
- Justification: TRL handles gradient checkpointing, mixed precision, LoRA reference models automatically

### Code Analysis (Serena MCP)

Not applicable - no existing codebase to analyze. This is new implementation.

---

## Experiment Specification

### Dataset

**Name:** HH-RLHF (Anthropic Human Preference Dataset)
**Source:** HuggingFace Hub
**Version:** Standard release
**Type:** standard

| Split | Size | Purpose |
|-------|------|---------|
| Train | ~170K pairs | BiDPO training |
| Test | ~8.5K pairs | Held-out validation |

**Preprocessing:**
1. Load preference pairs (chosen, rejected responses)
2. Tokenize with Mistral tokenizer (max_length=1024)
3. Compute collab_score_v2 for each response pair (reuse H-E1 implementation)
4. Store scores for L_agency computation during training

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: Anthropic/hh-rlhf
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("Anthropic/hh-rlhf")
train_data = dataset["train"]  # ~170K pairs
```

### Models

#### Baseline Model

**Name:** Mistral-7B-Instruct-v0.2
**Source:** HuggingFace Hub
**Type:** Instruction-tuned LLM (7B parameters)

This serves as both:
1. Initial policy model (π_θ) - will be trained
2. Reference model (π_ref) - frozen copy for DPO

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: mistralai/Mistral-7B-Instruct-v0.2
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
```

#### Proposed Model

**Architecture:** Mistral-7B + BiDPO Training (DPO + L_agency auxiliary loss)

**Core Mechanism Implementation:**

```python
# BiDPO Loss: L_total = L_DPO + lambda * L_agency
# Where L_agency = 1 - collab_score (lower agency -> higher loss)

def compute_bidpo_loss(
    policy_chosen_logps: torch.Tensor,
    policy_rejected_logps: torch.Tensor,
    reference_chosen_logps: torch.Tensor,
    reference_rejected_logps: torch.Tensor,
    chosen_collab_scores: torch.Tensor,
    rejected_collab_scores: torch.Tensor,
    beta: float = 0.1,
    lambda_agency: float = 0.5
) -> torch.Tensor:
    """
    Compute BiDPO loss combining DPO with agency-preservation signal.
    
    Args:
        policy_*_logps: Log probs from policy model (batch_size,)
        reference_*_logps: Log probs from frozen reference (batch_size,)
        *_collab_scores: Collaboration scores from collab_score_v2 (batch_size,)
        beta: DPO temperature (default 0.1)
        lambda_agency: Weight for agency loss (default 0.5)
    
    Returns:
        total_loss: Combined BiDPO loss (scalar)
    """
    # Standard DPO loss computation
    pi_logratios = policy_chosen_logps - policy_rejected_logps
    ref_logratios = reference_chosen_logps - reference_rejected_logps
    logits = pi_logratios - ref_logratios
    dpo_loss = -F.logsigmoid(beta * logits).mean()
    
    # Agency loss: penalize low-agency chosen responses
    # L_agency = 1 - collab_score (want to maximize collaboration)
    agency_loss_chosen = (1.0 - chosen_collab_scores).mean()
    agency_loss_rejected = (1.0 - rejected_collab_scores).mean()
    
    # Total agency loss: encourage chosen > rejected on agency
    agency_loss = agency_loss_chosen - 0.5 * agency_loss_rejected
    
    # Combined loss
    total_loss = dpo_loss + lambda_agency * agency_loss
    
    return total_loss, {
        "dpo_loss": dpo_loss.item(),
        "agency_loss": agency_loss.item(),
        "total_loss": total_loss.item()
    }
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **Optimizer** | AdamW | Standard for LLM fine-tuning |
| **Learning Rate** | 5e-7 | DPO standard (TRL default) |
| **LR Schedule** | Cosine with warmup | 10% warmup steps |
| **Batch Size** | 4 (effective 16 with grad accum) | Memory constraints for 7B model |
| **Gradient Accumulation** | 4 | Achieves effective batch 16 |
| **Epochs** | 1 | Standard DPO practice |
| **Beta (DPO)** | 0.1 | Standard temperature |
| **Lambda (agency)** | 0.5 | Middle of proposed range [0.25, 1.0] |
| **Max Length** | 1024 | Covers most HH-RLHF responses |
| **Precision** | bfloat16 | Memory efficiency |
| **Gradient Clipping** | 1.0 | Stability |

**Training Steps:**
1. Initialize policy model from Mistral-7B-Instruct-v0.2
2. Create frozen reference model copy
3. Precompute collab_score_v2 for all training pairs
4. Train with BiDPO loss for 1 epoch
5. Log loss components (dpo_loss, agency_loss, total_loss) every 100 steps
6. Save checkpoint at end

### Evaluation

**Primary Metrics:**

| Metric | Measurement | Success Criterion |
|--------|-------------|-------------------|
| Training Completion | No NaN/Inf in loss | Training runs to completion |
| Loss Decrease | Total loss at end < start | Loss decreases after warmup |
| DPO Loss Stability | DPO component stable | No divergence |
| Agency Loss Stability | Agency component stable | No divergence |

**Stability Checks:**
- Monitor for NaN/Inf every step
- Log gradient norms
- Track loss components separately

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Training stability monitoring
- Library: torch (native), wandb (logging)
- Code:
```python
# Loss monitoring
def check_stability(loss_dict: dict) -> bool:
    for name, value in loss_dict.items():
        if torch.isnan(torch.tensor(value)) or torch.isinf(torch.tensor(value)):
            return False
    return True

# Gradient norm tracking
total_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Training Loss Curves**: Plot dpo_loss, agency_loss, total_loss over training steps

#### Additional Figures (LLM Autonomous)

1. **Loss Component Breakdown**: Stacked area chart showing DPO vs agency contribution
2. **Gradient Norm Over Time**: Line plot tracking gradient magnitudes
3. **Learning Rate Schedule**: Cosine warmup visualization

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Training completes without NaN/Inf errors
2. `total_loss_final < total_loss_initial` (after warmup)

**Gate Decision:**
- PASS → Proceed to H-M2 (test if BiDPO generates higher-agency responses)
- FAIL → Debug training, try gradient clipping, lower lambda, or loss scaling

---

## Appendix: Reference Implementations

### TRL DPOTrainer Multi-Loss
```python
from trl import DPOConfig, DPOTrainer

# MPO-style multi-loss combination
training_args = DPOConfig(
    loss_type=["sigmoid", "bco_pair", "sft"],
    loss_weights=[0.8, 0.2, 1.0],
    beta=0.1,
    learning_rate=5e-7,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
)
```

### torchtune DPOLoss
```python
from torchtune.rlhf.loss import DPOLoss

dpo_loss_fn = DPOLoss(beta=0.1, label_smoothing=0.0)
losses, chosen_rewards, rejected_rewards = dpo_loss_fn(
    policy_chosen_logps,
    policy_rejected_logps,
    reference_chosen_logps,
    reference_rejected_logps
)
```

### Custom BiDPO Integration Pattern
```python
# Extend DPOTrainer.compute_loss() to add agency term
class BiDPOTrainer(DPOTrainer):
    def __init__(self, *args, lambda_agency=0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.lambda_agency = lambda_agency
    
    def compute_loss(self, model, inputs, return_outputs=False):
        # Get standard DPO loss
        dpo_loss, outputs = super().compute_loss(model, inputs, return_outputs=True)
        
        # Add agency loss
        agency_loss = self._compute_agency_loss(inputs)
        total_loss = dpo_loss + self.lambda_agency * agency_loss
        
        return (total_loss, outputs) if return_outputs else total_loss
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- H-E1 PASSED (correlation=-0.026): Collaboration score validated as orthogonal signal
- H-M1 IN_PROGRESS: Testing BiDPO training stability

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
