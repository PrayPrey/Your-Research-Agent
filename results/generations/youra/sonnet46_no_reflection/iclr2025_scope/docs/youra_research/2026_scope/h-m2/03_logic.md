# Logic: H-M2 — JointLoRA-KV Joint Training

**Date:** 2026-05-20
**Phase:** 3 — Logic Design

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No local codebase — green-field implementation
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## Applied Patterns

Applied: PEFT dual-parameter-group AdamW (diffusers SDXL dual-LoRA pattern)
Applied: Standard PyTorch sigmoid relaxation for differentiable top-k

---

## A-2: Locret Retaining Head + Model Registration [Complexity: 14, Budget: 3 subtasks]

### API Signatures

```python
# code/model.py

class LocretRetainingHead(nn.Module):
    def __init__(
        self,
        d_model: int = 4096,
        d_kv: int = 1024,          # n_kv_heads * d_head = 8 * 128
        hidden_dim: int = 1024,
        num_scores: int = 8,        # = n_kv_heads
    ) -> None:
        """CIS MLP: S̃ = σ([Q,K_exp,V_exp] @ W1) @ W2."""
        # W1: Linear(d_model + 2*d_kv, hidden_dim)  → (6144, 1024)
        # W2: Linear(hidden_dim, num_scores)         → (1024, 8)
        ...

    def forward(
        self,
        q: Tensor,   # [B, 32, S, 128]
        k: Tensor,   # [B,  8, S, 128]
        v: Tensor,   # [B,  8, S, 128]
    ) -> Tensor:
        """Returns CIS scores. Output: [B, 8, S]"""
        # 1. k_exp = k.repeat_interleave(4, dim=1)  # [B, 32, S, 128]
        # 2. v_exp = v.repeat_interleave(4, dim=1)  # [B, 32, S, 128]
        # 3. qkv = cat([q, k_exp, v_exp], dim=-1)   # [B, 32, S, 384]
        # 4. qkv_flat = qkv.mean(dim=1)              # [B, S, 384]  (head-mean pool)
        # 5. h = sigmoid(W1(qkv_flat))               # [B, S, 1024]
        # 6. scores = W2(h)                          # [B, S, 8]
        # 7. return scores.permute(0, 2, 1)          # [B, 8, S]
        ...


class JointLoRAKVModel(nn.Module):
    def __init__(
        self,
        base_model_name: str,
        lora_config: "LoRAConfig",
        locret_config: "LocretConfig",
    ) -> None:
        """Wrap LLaMA-3.1-8B with PEFT LoRA + per-layer Locret heads."""
        ...

    def register_retaining_heads(self) -> None:
        """Attach LocretRetainingHead to each LLaMA attention layer.

        Registers under self.retaining_heads[i]; sets requires_grad=True.
        Hooks into model.model.layers[i].self_attn via forward_hook.
        """
        ...

    def load_locret_warm_init(self, checkpoint_path: str) -> None:
        """Load W1/W2 weights from hyx21/Locret-llama-3.1-8B-instruct.

        Maps checkpoint keys to self.retaining_heads[i].W1/W2.
        GQA: checkpoint trained on n_kv_heads=8 — no shape mismatch.
        Silently skips missing keys; logs warning for shape mismatch.
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| q | [B, 32, S, 128] | LLaMA-3.1-8B n_heads=32 |
| k, v | [B, 8, S, 128] | GQA n_kv_heads=8 |
| k_exp, v_exp | [B, 32, S, 128] | repeat_interleave(4, dim=1) |
| qkv_cat | [B, 32, S, 384] | cat on last dim |
| qkv_flat | [B, S, 384] | mean over head dim |
| h (hidden) | [B, S, 1024] | W1 output after sigmoid |
| cis_scores | [B, 8, S] | Final per-KV-head scores |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | LocretRetainingHead MLP | Implement W1/W2 linear layers, GQA repeat_interleave, sigmoid CIS formula |
| L-2-2 | Per-layer registration hook | forward_hook on each LLaMA attention layer to capture Q/K/V and run retaining head |
| L-2-3 | Warm init from checkpoint | Load hyx21/Locret checkpoint, map keys, handle shape validation |

---

## A-3: JointLoRAKVModel Forward Pass [Complexity: 16, Budget: 4 subtasks]

### API Signatures

```python
# code/model.py (continued)

    def get_lora_params(self) -> List[nn.Parameter]:
        """Return [p for n,p in named_parameters() if 'lora_' in n and p.requires_grad]."""
        ...

    def get_locret_params(self) -> List[nn.Parameter]:
        """Return [p for n,p in named_parameters() if 'retaining_head' in n and p.requires_grad]."""
        ...

    def compute_soft_kv_mask(
        self,
        cis_scores: Tensor,   # [B, 8, S]
        budget_ratio: float,
    ) -> Tensor:
        """Differentiable soft top-k via sigmoid with temperature scaling.

        Returns soft mask in [0,1]. Shape: [B, 8, S]
        """
        # k_retain = int(S * budget_ratio)
        # threshold = kth value via topk (no grad)
        # margin = cis_scores - threshold.unsqueeze(-1)
        # soft_mask = sigmoid(margin / temperature)   temperature=0.1
        # return soft_mask  # [B, 8, S]
        ...

    def apply_hard_kv_eviction(
        self,
        kv_cache: Tensor,     # [B, n_kv_heads, S, d_head]
        cis_scores: Tensor,   # [B, n_kv_heads, S]
        budget_ratio: float,
    ) -> Tensor:
        """Hard top-k selection. Returns retained KV cache: [B, n_kv_heads, K, d_head]"""
        # k_retain = int(S * budget_ratio)
        # top_indices = torch.topk(cis_scores, k_retain, dim=-1).indices  # [B, H, K]
        # top_indices_sorted = top_indices.sort(dim=-1).values
        # return kv_cache.gather(2, top_indices_sorted.unsqueeze(-1).expand(...))
        ...

    def forward(
        self,
        input_ids: Tensor,                    # [B, S]
        attention_mask: Optional[Tensor],     # [B, S]
        labels: Optional[Tensor] = None,      # [B, S]
        kv_budget_ratio: float = 0.5,
        training_mode: bool = True,
    ) -> Tuple[Tensor, Optional[Tensor], Optional[Tensor]]:
        """Unified forward pass.

        Returns: (logits [B, S, vocab], cis_scores [B, 32, S] or None, loss scalar or None)
        Soft mask applied if training_mode=True; hard eviction if False.
        """
        ...


def build_joint_model(config: "ExperimentConfig") -> JointLoRAKVModel:
    """Instantiate + PEFT-wrap + register heads + optional warm init."""
    ...

def build_baseline_b3_model(config: "ExperimentConfig") -> JointLoRAKVModel:
    """Same architecture; training procedure differs (sequential stages in trainer)."""
    ...
```

### Pseudo-code: Soft KV Mask (differentiable top-k)

```
compute_soft_kv_mask(cis_scores, budget_ratio, temperature=0.1):
  S = cis_scores.shape[-1]
  k = max(1, int(S * budget_ratio))
  # find kth-largest threshold (no grad)
  with torch.no_grad():
      threshold = torch.topk(cis_scores, k, dim=-1).values[..., -1]  # [B, 8]
  margin = cis_scores - threshold.unsqueeze(-1)                       # [B, 8, S]
  soft_mask = torch.sigmoid(margin / temperature)                     # [B, 8, S] in (0,1)
  return soft_mask
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | PEFT LoRA injection | get_peft_model call, verify lora_ param names, freeze base params |
| L-3-2 | Soft KV mask | compute_soft_kv_mask with sigmoid relaxation and temperature |
| L-3-3 | Hard top-k eviction | apply_hard_kv_eviction with torch.topk + gather |
| L-3-4 | Unified forward | Branch on training_mode; collect CIS scores via hooks; compute CE loss |

---

## A-4: StabilityMonitor [Complexity: 10, Budget: 1 subtask]

### API Signatures

```python
# code/stability.py

class StabilityMonitor:
    def __init__(
        self,
        seed: int,
        moving_avg_window: int = 100,
        divergence_factor: float = 2.0,
    ) -> None:
        """Track NaN events, divergence events, loss/grad history."""
        ...

    def update(self, loss: float, step: int) -> None:
        """Record loss, update moving average deque, check stability."""
        ...

    def check_nan(self, loss: Tensor) -> bool:
        """Return True and increment nan_events if torch.isnan(loss)."""
        ...

    def check_divergence(self, loss: float, window: int = 100) -> bool:
        """Return True if loss > divergence_factor * moving_average."""
        ...

    def record_grad_norms(
        self,
        step: int,
        lora_norm: float,
        locret_norm: float,
    ) -> None:
        """Store grad norms every 50 steps."""
        ...

    def get_moving_average(self) -> float:
        """Mean of last `moving_avg_window` loss values."""
        ...

    def is_stable(self) -> bool:
        """Return nan_events == 0 AND divergence_events == 0."""
        ...

    def get_report(self) -> Dict[str, Any]:
        """Return {seed, nan_events, divergence_events, final_loss,
                   loss_history, grad_norm_history}."""
        ...

    def save_report(self, path: str) -> None:
        """Write JSON to {seed}/stability_log.json."""
        ...


class StabilityError(Exception):
    """Raised when NaN detected; halts current seed training."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | StabilityMonitor full impl | deque-based moving avg, NaN/divergence checks, JSON report, StabilityError |

---

## A-5: JointLoRAKVTrainer [Complexity: 15, Budget: 4 subtasks]

### API Signatures

```python
# code/trainer.py

class JointLoRAKVTrainer:
    def __init__(
        self,
        model: JointLoRAKVModel,
        data_manager: "DataManager",
        stability_monitor: StabilityMonitor,
        training_config: "TrainingConfig",
        seed: int,
    ) -> None:
        """Initialize trainer; build optimizer + scheduler after init."""
        ...

    def build_optimizer(self) -> AdamW:
        """Two param groups: LoRA lr=1e-4, Locret lr=5e-4, shared AdamW.

        param_groups = [
            {"params": model.get_lora_params(),    "lr": 1e-4},
            {"params": model.get_locret_params(),  "lr": 5e-4},
        ]
        """
        ...

    def build_scheduler(
        self,
        optimizer: AdamW,
        total_steps: int,
    ) -> LambdaLR:
        """Linear warmup for warmup_ratio*total_steps, then cosine decay."""
        # warmup_steps = int(total_steps * warmup_ratio)
        # lambda: linear ramp [0, warmup_steps], cosine [warmup_steps, total_steps]
        ...

    def train_step(
        self,
        batch: Dict[str, Tensor],
        step: int,
    ) -> float:
        """Single forward+backward+clip+step. Returns loss.item().

        Raises StabilityError if NaN detected.
        Every 50 steps: compute + log grad norms to stability_monitor.
        """
        # logits, cis_scores, loss = model.forward(..., training_mode=True)
        # if monitor.check_nan(loss): raise StabilityError
        # loss.backward()
        # clip_grad_norm_(params, max_norm=1.0)
        # optimizer.step(); scheduler.step(); optimizer.zero_grad()
        ...

    def train_epoch(self, epoch: int) -> Dict[str, Any]:
        """Full epoch over GLUE combined loader. Returns {epoch, mean_loss,
           nan_events, divergence_events}."""
        ...

    def train(self) -> Dict[str, Any]:
        """Run all epochs; return stability_monitor.get_report()."""
        ...

    def save_checkpoint(self, path: str) -> None:
        """Save model state_dict + optimizer state to path."""
        ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Dual param group optimizer | build_optimizer with LoRA/Locret groups, AdamW kwargs |
| L-5-2 | LR scheduler | build_scheduler linear warmup + cosine decay LambdaLR |
| L-5-3 | train_step | forward, NaN check, backward, grad clip, optimizer step, grad norm logging |
| L-5-4 | Epoch + full train loop | accumulate loss, divergence check, stability event accumulation |

---

## A-6: BaselineB3Trainer [Complexity: 14, Budget: 3 subtasks]

### API Signatures

```python
# code/trainer.py (continued)

class BaselineB3Trainer:
    def __init__(
        self,
        model: JointLoRAKVModel,
        data_manager: "DataManager",
        training_config: "TrainingConfig",
        seed: int,
    ) -> None:
        """Two-stage sequential trainer."""
        ...

    def stage1_lora_finetune(self) -> Dict[str, Any]:
        """Stage 1: LoRA CE fine-tune. Locret heads: requires_grad=False.

        Optimizer: AdamW on get_lora_params() only, lr=1e-4.
        Loss: CE cross-entropy on GLUE labels.
        Returns {stage, epochs, final_loss, glue_accuracy}.
        """
        ...

    def stage2_locret_finetune(self) -> Dict[str, Any]:
        """Stage 2: Locret LM distillation. LoRA params: requires_grad=False.

        Optimizer: AdamW on get_locret_params() only, lr=5e-4.
        Loss: KL divergence between teacher (full-KV) and student (evicted-KV) logits.
        Teacher logits: forward with kv_budget_ratio=1.0 (no eviction).
        Student logits: forward with kv_budget_ratio=0.5 (hard eviction).
        Returns {stage, epochs, final_loss}.
        """
        ...

    def train(self) -> Dict[str, Any]:
        """Run stage1 then stage2. Returns combined report."""
        ...

    def save_checkpoint(self, path: str) -> None:
        """Save stage1 checkpoint; save stage2 checkpoint separately."""
        ...
```

### Pseudo-code: Stage 2 LM Distillation Loss

```
stage2_train_step(batch):
  with torch.no_grad():
      teacher_logits, _, _ = model.forward(..., kv_budget_ratio=1.0, training_mode=False)
  student_logits, _, _ = model.forward(..., kv_budget_ratio=0.5, training_mode=False)
  # KL divergence: KL(student || teacher)
  loss = F.kl_div(
      F.log_softmax(student_logits / T, dim=-1),
      F.softmax(teacher_logits / T, dim=-1),
      reduction="batchmean",
  )  # T=1.0 (temperature)
  return loss
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Stage 1 LoRA CE fine-tune | Single-group optimizer, CE loss loop, freeze Locret |
| L-6-2 | Stage 2 Locret LM distillation | Freeze LoRA, KL-div teacher/student logits, Locret optimizer |
| L-6-3 | Checkpoint save/load between stages | Save after stage1, load for stage2 init |

---

## A-7: LongBenchEvaluator [Complexity: 13, Budget: 2 subtasks]

### API Signatures

```python
# code/evaluator.py

class LongBenchEvaluator:
    TASKS: List[str] = ["narrativeqa", "qasper", "multifieldqa_en"]

    def __init__(
        self,
        model: JointLoRAKVModel,
        data_manager: "DataManager",
        budget_ratio: float = 0.5,
    ) -> None:
        ...

    def evaluate_task(self, task_name: str) -> float:
        """Run inference with hard KV eviction; compute mean qa_f1_score.

        Uses model.forward(..., training_mode=False, kv_budget_ratio=0.5).
        Decodes with greedy generation (max_new_tokens=50).
        Returns mean F1 float.
        """
        ...

    def evaluate_all(self) -> Dict[str, float]:
        """Evaluate all 3 tasks. Returns {task_name: f1, 'mean_f1': float}."""
        ...

    @staticmethod
    def qa_f1_score(prediction: str, ground_truth: str) -> float:
        """Token-level F1 from THUDM/LongBench metrics.py.

        Normalizes: lowercase, remove punctuation/articles.
        Returns F1 in [0.0, 1.0].
        """
        ...

    def _generate_with_hard_eviction(
        self,
        input_ids: Tensor,          # [1, S]
        attention_mask: Tensor,     # [1, S]
        max_new_tokens: int = 50,
    ) -> str:
        """Autoregressive generation; KV cache evicted at each decode step."""
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Generation loop with hard eviction | _generate_with_hard_eviction, evaluate_task, evaluate_all |
| L-7-2 | qa_f1_score integration | Token F1 from THUDM metrics.py, normalization, multi-answer max |

---

## Tensor Shape Reference (LLaMA-3.1-8B)

| Symbol | Shape | Source |
|--------|-------|--------|
| input_ids | [B, S] | tokenizer output |
| Q | [B, 32, S, 128] | n_heads=32, d_head=128 |
| K, V | [B, 8, S, 128] | GQA n_kv_heads=8 |
| K_exp, V_exp | [B, 32, S, 128] | repeat_interleave(4, dim=1) |
| CIS input flat | [B, S, 384] | cat([Q,K_exp,V_exp], dim=-1).mean(1) |
| W1 | [6144, 1024] | d_model+2*d_kv = 4096+1024+1024 |
| W2 | [1024, 8] | hidden→n_kv_heads |
| cis_scores | [B, 8, S] | per KV head |
| soft_mask | [B, 8, S] | sigmoid relaxation during training |
| logits | [B, S, vocab_size] | LLaMA output |
