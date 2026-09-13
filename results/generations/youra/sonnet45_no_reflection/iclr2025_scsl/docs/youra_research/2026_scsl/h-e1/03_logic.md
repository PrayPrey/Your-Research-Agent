# Logic Specification: h-e1
# Jacobian Stable Rank Regularization - EXISTENCE Proof-of-Concept

**Date:** 2026-05-12  
**Hypothesis Type:** EXISTENCE (PoC)  
**Allocated Tasks:** A-3, A-4  
**Budget:** 7 subtasks (A-3: 4, A-4: 3)

---

## Codebase Analysis (Serena)

**Project Type**: Green-field  
**Status**: New implementation from scratch - designing new APIs  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - new implementation

---

## A-3: Stable Rank Regularization [Complexity: 16, Budget: 4]

**Applied**: PyTorch autograd (Jacobian-vector products), Power iteration spectral norm

### API Signatures

```python
class StableRankRegularizer(nn.Module):
    """Residual-corrected Jacobian stable rank regularizer."""
    
    def __init__(
        self,
        n_power_iterations: int = 5,
        n_hutchinson_probes: int = 10,
        epsilon: float = 1e-12
    ):
        """Initialize regularizer."""
        super().__init__()
        self.n_power_iter = n_power_iterations
        self.n_probes = n_hutchinson_probes
        self.eps = epsilon
        
    def hutchinson_trace(
        self,
        layer_output: Tensor,
        layer_input: Tensor
    ) -> Tensor:
        """Estimate ||J̃_ℓ||_F^2 via Hutchinson trace estimator.
        
        Args:
            layer_output: [B, L, H] layer output
            layer_input: [B, L, H] layer input (requires_grad=True)
            
        Returns:
            frobenius_norm_sq: [] scalar trace estimate
        """
        ...
        
    def power_iteration_spectral_norm(
        self,
        layer_output: Tensor,
        layer_input: Tensor
    ) -> Tensor:
        """Estimate ||J̃_ℓ||_2 via power iteration with residual correction.
        
        Args:
            layer_output: [B, L, H] layer output
            layer_input: [B, L, H] layer input (requires_grad=True)
            
        Returns:
            spectral_norm: [] scalar largest singular value
        """
        ...
        
    def compute_stable_rank(
        self,
        layer_output: Tensor,
        layer_input: Tensor
    ) -> Tensor:
        """Compute sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2.
        
        Args:
            layer_output: [B, L, H] layer output
            layer_input: [B, L, H] layer input (requires_grad=True)
            
        Returns:
            stable_rank: [] scalar stable rank
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| layer_output | [B, L, H] | Transformer layer output (B=32, L=512, H=768) |
| layer_input | [B, L, H] | Transformer layer input |
| v_probe | [B*L*H] | Flattened Rademacher probe vector |
| Jv | [B*L*H] | Jacobian-vector product |
| frobenius_norm_sq | [] | Trace estimate (scalar) |
| spectral_norm | [] | Largest singular value (scalar) |
| stable_rank | [] | sr_ℓ^res (scalar) |

### Pseudo-code

#### Hutchinson Trace Estimator

```
Input: layer_output [B, L, H], layer_input [B, L, H], n_probes
Output: frobenius_norm_sq []

1. trace_estimates = []
2. For i in range(n_probes):
   a. v = sample_rademacher([B, L, H])  # Sample ±1 uniformly
   b. v.requires_grad = False
   c. # Compute Jv via autograd
   d. Jv = torch.autograd.grad(
         outputs=layer_output,
         inputs=layer_input,
         grad_outputs=v,
         create_graph=True,
         retain_graph=True
      )[0]
   e. # Apply residual correction: J̃v = Jv - v
   f. Jv_res = Jv - v
   g. # Trace estimate: ⟨v, J̃v⟩
   h. trace_est = torch.sum(v * Jv_res)
   i. trace_estimates.append(trace_est)
3. frobenius_norm_sq = torch.mean(torch.stack(trace_estimates))
4. Return frobenius_norm_sq
```

#### Power Iteration for Spectral Norm

```
Input: layer_output [B, L, H], layer_input [B, L, H], n_iter
Output: spectral_norm []

1. # Initialize random vector
2. v = torch.randn([B, L, H])
3. v = v / (torch.norm(v) + eps)
4. For i in range(n_iter):
   a. # Compute Jv
   b. Jv = torch.autograd.grad(
         outputs=layer_output,
         inputs=layer_input,
         grad_outputs=v,
         create_graph=True,
         retain_graph=True
      )[0]
   c. # Residual correction: J̃v = Jv - v
   d. Jv_res = Jv - v
   e. # Compute J̃^T J̃v (transpose via VJP)
   f. JTJv = torch.autograd.grad(
         outputs=layer_input,
         inputs=layer_input,
         grad_outputs=Jv_res,
         create_graph=True,
         retain_graph=True
      )[0]
   g. # Update v
   h. v = JTJv / (torch.norm(JTJv) + eps)
5. # Final spectral norm
6. Jv_final = torch.autograd.grad(
      outputs=layer_output,
      inputs=layer_input,
      grad_outputs=v,
      create_graph=True
   )[0]
7. Jv_res_final = Jv_final - v
8. spectral_norm = torch.norm(Jv_res_final)
9. Return spectral_norm
```

#### Stable Rank Computation

```
Input: layer_output, layer_input
Output: stable_rank []

1. frob_sq = hutchinson_trace(layer_output, layer_input)
2. spec_norm = power_iteration_spectral_norm(layer_output, layer_input)
3. stable_rank = frob_sq / (spec_norm ** 2 + eps)
4. Return stable_rank
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | HutchinsonTraceEstimator | Rademacher sampling + Jacobian-vector products |
| L-3-2 | PowerIterationSpectralNorm | Power iteration with residual correction |
| L-3-3 | StableRankComputation | Combine trace and spectral norm |
| L-3-4 | NumericalStability | Epsilon guards, gradient detachment |

---

## A-4: Proposed Model Training [Complexity: 14, Budget: 3]

**Applied**: Adaptive regularization training, PyTorch training loop patterns

### API Signatures

```python
class RegularizedGPT2(nn.Module):
    """GPT-2 with stable rank regularization."""
    
    def __init__(
        self,
        config: GPT2Config,
        lambda_reg: float = 0.01,
        n_power_iter: int = 5,
        n_hutchinson: int = 10
    ):
        """Initialize regularized GPT-2."""
        super().__init__()
        self.transformer = GPT2Model(config)
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False)
        self.regularizer = StableRankRegularizer(n_power_iter, n_hutchinson)
        self.lambda_reg = lambda_reg
        self.layer_outputs = []  # Hook storage
        self.layer_inputs = []
        
    def forward(
        self,
        input_ids: Tensor,
        labels: Optional[Tensor] = None
    ) -> dict:
        """Forward pass with regularization.
        
        Args:
            input_ids: [B, L] token IDs
            labels: [B, L] target tokens (optional)
            
        Returns:
            dict: {loss: [], logits: [B, L, V], reg_loss: [], stable_ranks: [12]}
        """
        ...
        
    def compute_regularization_loss(self) -> Tensor:
        """Compute mean stable rank across layers.
        
        Returns:
            reg_loss: [] mean sr_ℓ^res across 12 layers
        """
        ...
        
    def adaptive_lambda_update(
        self,
        current_ppl: float,
        baseline_ppl: float,
        tolerance: float = 0.01
    ) -> None:
        """Adjust lambda to maintain perplexity within tolerance."""
        ...
```

```python
class GPT2Trainer:
    """Training loop for GPT-2 variants."""
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        config: dict,
        variant: str
    ):
        """Initialize trainer."""
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.variant = variant
        
        self.optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=config['learning_rate'],
            betas=config['betas'],
            weight_decay=config['weight_decay']
        )
        
        self.scheduler = get_cosine_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=config['warmup_steps'],
            num_training_steps=config['total_steps']
        )
        
        self.grad_accum_steps = config['gradient_accumulation_steps']
        self.checkpoint_dir = f"checkpoints/{variant}/"
        
    def train_step(self, batch: dict) -> dict:
        """Single training step with gradient accumulation.
        
        Args:
            batch: {input_ids: [B, L], labels: [B, L]}
            
        Returns:
            metrics: {loss: float, reg_loss: float, lr: float}
        """
        ...
        
    def validation_step(self) -> dict:
        """Validation pass for perplexity and stable rank.
        
        Returns:
            metrics: {perplexity: float, mean_stable_rank: float, layer_variance: float}
        """
        ...
        
    def train(self, total_steps: int) -> None:
        """Main training loop. total_steps: ~78,125 for 10B tokens"""
        ...
        
    def save_checkpoint(self, step: int, metrics: dict) -> None:
        """Save model checkpoint with metrics."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | Input token IDs (B=32, L=512) |
| labels | [B, L] | Target token IDs |
| logits | [B, L, V] | Output logits (V=50257) |
| loss_clm | [] | Causal language modeling loss |
| reg_loss | [] | Mean stable rank across 12 layers |
| loss_total | [] | loss_clm + λ * reg_loss |
| stable_ranks | [12] | Per-layer stable rank values |

### Pseudo-code

#### Forward Pass with Regularization

```
Input: input_ids [B, L]
Output: {loss: [], logits: [B, L, V], reg_loss: []}

1. # Register hooks to capture layer inputs/outputs
2. self.layer_outputs.clear()
3. self.layer_inputs.clear()
4. For layer in transformer.h:  # 12 layers
   a. Register forward hook:
      - On forward: store (layer_input, layer_output)
5. # Forward pass
6. outputs = transformer(input_ids)  # [B, L, H]
7. logits = lm_head(outputs)  # [B, L, V]
8. loss_clm = cross_entropy(logits.view(-1, V), labels.view(-1))
9. # Compute regularization
10. reg_loss = compute_regularization_loss()
11. loss_total = loss_clm + lambda_reg * reg_loss
12. Return {loss: loss_total, logits, reg_loss}
```

#### Regularization Loss Computation

```
Input: layer_outputs (12 × [B, L, H]), layer_inputs (12 × [B, L, H])
Output: reg_loss []

1. stable_ranks = []
2. For i in range(12):  # For each transformer layer
   a. sr = regularizer.compute_stable_rank(
         layer_outputs[i],
         layer_inputs[i]
      )
   b. stable_ranks.append(sr)
3. reg_loss = torch.mean(torch.stack(stable_ranks))
4. Return reg_loss
```

#### Adaptive Lambda Tuning

```
Input: current_ppl, baseline_ppl, tolerance=0.01
Output: Updated lambda_reg

1. ppl_ratio = current_ppl / baseline_ppl
2. If ppl_ratio > (1 + tolerance):  # Exceeds 1% threshold
   a. lambda_reg *= 0.95  # Reduce regularization
3. Else if ppl_ratio < (1 - tolerance):
   a. lambda_reg *= 1.05  # Increase regularization
4. lambda_reg = torch.clamp(lambda_reg, 0.001, 0.1)  # Safety bounds
```

#### Training Loop

```
Input: total_steps, train_loader, val_loader
Output: Trained model

1. baseline_ppl = load_baseline_ppl()  # From baseline checkpoint
2. For step in range(total_steps):
   a. batch = next(train_loader)
   b. outputs = model(batch['input_ids'], batch['labels'])
   c. loss = outputs['loss'] / grad_accum_steps
   d. loss.backward()
   
   e. If (step + 1) % grad_accum_steps == 0:
      i. torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
      ii. optimizer.step()
      iii. scheduler.step()
      iv. optimizer.zero_grad()
   
   f. If step % 500 == 0:  # Perplexity check
      i. current_ppl = validation_step()['perplexity']
      ii. model.adaptive_lambda_update(current_ppl, baseline_ppl)
   
   g. If step % 1000 == 0:  # Stable rank measurement
      i. metrics = validation_step()
      ii. log_metrics(step, metrics)
   
   h. If step % 10000 == 0:  # Checkpoint
      i. save_checkpoint(step, metrics)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | RegularizedForwardPass | Integrate regularizer with GPT-2, hook layer I/O |
| L-4-2 | AdaptiveLambdaTuning | Adjust lambda based on perplexity deviation |
| L-4-3 | TrainingLoopWithMetrics | Main loop with checkpointing, logging |

---

## External Dependencies

### HuggingFace Transformers

```python
from transformers import GPT2Config, GPT2Model, GPT2LMHeadModel
from transformers import get_cosine_schedule_with_warmup

# Model initialization
config = GPT2Config(
    vocab_size=50257,
    n_positions=1024,
    n_embd=768,
    n_layer=12,
    n_head=12
)
model = GPT2Model(config)
```

### PyTorch Autograd

```python
import torch.autograd as autograd

# Jacobian-vector product
Jv = autograd.grad(
    outputs=layer_output,
    inputs=layer_input,
    grad_outputs=v,
    create_graph=True,
    retain_graph=True
)[0]
```

---

## Implementation Notes

### Critical Numerical Stability

1. **Epsilon Guards:**
   - Division: `frob_sq / (spec^2 + eps)` with eps=1e-12
   - Normalization: `v / (||v||_2 + eps)`

2. **Gradient Detachment:**
   - Rademacher vectors: `v.requires_grad = False`
   - Power iteration: detach intermediate v where appropriate

3. **Gradient Clipping:**
   - Global norm: `clip_grad_norm_(model.parameters(), 1.0)`
   - Prevents instability from regularization term

### Memory Optimization

1. **Hook Management:**
   - Clear `layer_outputs` and `layer_inputs` after regularization computation
   - Use `retain_graph=True` only when necessary

2. **Gradient Accumulation:**
   - Scale loss by `1 / grad_accum_steps` before backward
   - Effective batch size 128 with micro-batch 32

3. **Mixed Precision (Optional):**
   - Use `torch.cuda.amp.autocast()` for forward pass
   - GradScaler for backward pass

### Measurement Frequency

| Operation | Cost | Frequency |
|-----------|------|-----------|
| Stable rank (full) | Very High | Every 1000 steps |
| Perplexity | Medium | Every 500 steps |
| Training loss | Low | Every step |
| Checkpoint | High (I/O) | Every 10,000 steps |

---

## Self-Validation Checklist

- [x] No ASCII diagrams
- [x] KB patterns applied: "PyTorch autograd", "Adaptive regularization training"
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count: A-3 (4/4), A-4 (3/3) - within budget
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included
- [x] Pseudo-code only for complex algorithms (Hutchinson, power iteration, training loop)
- [x] No external base hypothesis dependencies

---

**Status:** Ready for Phase 4 Implementation  
**Total Subtasks:** 7/7 used  
**Next Phase:** Phase 4 - Code Generation
