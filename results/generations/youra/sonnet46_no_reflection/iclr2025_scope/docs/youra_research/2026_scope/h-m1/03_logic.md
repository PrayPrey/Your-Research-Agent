# Logic Design: H-M1
# JointLoRA-KV — Task CE Loss Joint Training of LoRA Adapters and Locret Retaining Heads

**Applied: PyTorch tensor shape documentation pattern (Archon KB)**
**Applied: PEFT LoRA parameter group optimizer pattern (Archon KB)**

---

## Codebase Analysis (Serena)

**Analysis of H-E1 base code at `docs/youra_research/20260520_scope/h-e1/code/`**

Key findings from H-E1 actual implementation:

**RetainingHead (from h-e1/code/locret_extractor.py):**
- Class: `RetainingHead(nn.Module)` with `fc1: nn.Linear` and `fc2: nn.Linear`
- Forward: receives `q, k, v` tensors after attention projection
- CIS formula: `sigmoid(torch.cat([q, k, v], dim=-1) @ fc1.T) @ fc2.T`
- Checkpoint keys: `model.layers.{i}.self_attn.fc1.weight` and `model.layers.{i}.self_attn.fc2.weight`
- fc1 shape: `(1024, 6144)` → weight matrix W1 transposed
- fc2 shape: `(8, 1024)` → weight matrix W2 transposed

**ExperimentConfig (from h-e1/code/config.py):**
- Flat dataclass, no nested objects
- Field `hypothesis_folder: str = "."` — used as relative path root
- Scripts run from `h-m1/code/` directory with flat imports
- No `__init__.py` — not a package

**LoRA loading (from h-e1/code/lora_extractor.py):**
- Pattern: `PeftModel.from_pretrained(base_model, lora_path)` for loading
- For new training: `get_peft_model(model, LoraConfig(...))`
- LoRA params identified by `"lora_"` in param name

**GQA expansion (verified from H-E1):**
- `repeat_interleave(4)` for 8 KV heads → 32 Q heads
- `kv_repeat = num_query_heads // num_kv_heads = 32 // 8 = 4`

---

## External Dependencies API

### HuggingFace PEFT
```python
from peft import LoraConfig, TaskType, get_peft_model, PeftModel

# Create LoRA config for training
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj"],
    lora_dropout=0.1,
    task_type=TaskType.CAUSAL_LM,
    inference_mode=False,
)

# Wrap base model
peft_model = get_peft_model(base_model, lora_config)

# Identify LoRA parameters
lora_params = [p for n, p in peft_model.named_parameters() if "lora_" in n]
```

### HuggingFace Transformers
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, get_linear_schedule_with_warmup

# Load base model (verified from H-E1)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    torch_dtype=torch.float16,
    attn_implementation="eager",  # REQUIRED for Q/K/V tensor access
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3.1-8B-Instruct")

# LR scheduler
scheduler = get_linear_schedule_with_warmup(
    optimizer=optimizer,
    num_warmup_steps=int(warmup_ratio * total_steps),
    num_training_steps=total_steps,
)
```

### HuggingFace Hub
```python
from huggingface_hub import hf_hub_download

# Download Locret checkpoint (verified pattern from H-E1)
local_path = hf_hub_download(
    repo_id="hyx21/Locret-llama-3.1-8B-instruct",
    filename="pytorch_model.bin",
)
state_dict = torch.load(local_path, map_location="cpu")
# Keys: "model.layers.{i}.self_attn.fc1.weight", "model.layers.{i}.self_attn.fc2.weight"
```

### HuggingFace Datasets + Evaluate
```python
from datasets import load_dataset
import evaluate

# GLUE loading
mnli = load_dataset("glue", "mnli")   # train, validation_matched, validation_mismatched
sst2 = load_dataset("glue", "sst2")   # train, validation
qnli = load_dataset("glue", "qnli")   # train, validation

# Metric
metric = evaluate.load("glue", "mnli")  # or "sst2", "qnli"
result = metric.compute(predictions=preds, references=labels)  # {"accuracy": float}

# LongBench
lb = load_dataset("THUDM/LongBench", "narrativeqa", split="test")
```

### THUDM LongBench Metric
```python
# qa_f1_score from LongBench/metrics.py (must be copied or cloned)
def qa_f1_score(prediction: str, ground_truths: List[str]) -> float:
    # Token-level F1 between prediction and best-matching ground truth
    ...
```

---

## Module Overview

| Module | Role | Dependencies |
|--------|------|--------------|
| `config.py` | All hyperparameters, paths | none |
| `data_loader.py` | GLUE + LongBench dataset loading | config |
| `locret_heads.py` | RetainingHead nn.Module, load/freeze | config |
| `model.py` | JointLoRAKVModel, B2KvpressModel, build_* factories | config, locret_heads |
| `trainer.py` | JointLoRAKVTrainer: optimizer, train loop | config, model |
| `evaluate.py` | GLUE eval, LongBench eval, mechanism verification | config |
| `visualize.py` | 5 required figures | config |
| `run_experiment.py` | Orchestration entry point | all modules |

---

## API Signatures

### `locret_heads.py`

#### `RetainingHead`

```python
class RetainingHead(nn.Module):
    """Per-layer Locret retaining head implementing CIS = sigmoid([Q;K;V] @ W1) @ W2."""

    def __init__(self, fc1_weight: Tensor, fc2_weight: Tensor) -> None:
        """
        Args:
            fc1_weight: W1 matrix, shape (1024, 6144) — loaded from checkpoint as fc1.weight
            fc2_weight: W2 matrix, shape (8, 1024) — loaded from checkpoint as fc2.weight
        Note: Stored as nn.Linear with weight=fc1_weight (transposed internally by Linear)
        """

    def forward(self, q: Tensor, k: Tensor, v: Tensor) -> Tensor:
        """
        Compute CIS (Contextual Importance Score) for each token.

        Args:
            q: Query tensor after projection, shape (B, L, D_model) = (B, L, 4096)
            k: Key tensor after projection, shape (B, L, D_kv) = (B, L, 1024)
               Note: D_kv = num_kv_heads * head_dim = 8 * 128 = 1024
            v: Value tensor after projection, shape (B, L, D_kv) = (B, L, 1024)

        Returns:
            cis: CIS scores, shape (B, L, 8) — one score per KV head per token
                 Values in (0, 1) after sigmoid activation

        Internal computation:
            qkv = cat([q, k, v], dim=-1)  # (B, L, 6144) = (B, L, 4096+1024+1024)
            cis = sigmoid(qkv @ fc1.T) @ fc2.T  # (B, L, 1024) → (B, L, 8)
        """
```

#### `LocretHeadCollection`

```python
class LocretHeadCollection(nn.Module):
    """Container for all 32 per-layer RetainingHead modules."""

    def __init__(self, heads: List[RetainingHead]) -> None:
        """
        Args:
            heads: List of 32 RetainingHead instances, one per transformer layer
        """

    def __getitem__(self, layer_idx: int) -> RetainingHead:
        """
        Args:
            layer_idx: Transformer layer index, 0 to 31
        Returns:
            RetainingHead for that layer
        """

    def parameters(self) -> Iterator[nn.Parameter]:
        """Yields all W1/W2 parameters across all 32 heads."""
```

#### `load_locret_heads`

```python
def load_locret_heads(
    checkpoint: str,          # "hyx21/Locret-llama-3.1-8B-instruct"
    num_layers: int,          # 32 for LLaMA-3.1-8B
    device: torch.device,
) -> LocretHeadCollection:
    """
    Download and load Locret retaining head weights.

    Args:
        checkpoint: HuggingFace Hub repo ID
        num_layers: Number of transformer layers
        device: Target device

    Returns:
        LocretHeadCollection with requires_grad=True on all parameters

    Checkpoint key format (verified from H-E1):
        f"model.layers.{i}.self_attn.fc1.weight"  # shape (1024, 6144)
        f"model.layers.{i}.self_attn.fc2.weight"  # shape (8, 1024)

    Raises:
        KeyError: If checkpoint missing expected layer keys
        RuntimeError: If shape mismatch (wrong model config)
    """
```

#### `freeze_locret_heads`

```python
def freeze_locret_heads(heads: LocretHeadCollection) -> None:
    """
    Set requires_grad=False on all head parameters (for B1 baseline).

    Args:
        heads: LocretHeadCollection to freeze
    Side effect: Modifies requires_grad in-place
    """
```

---

### `model.py`

#### `JointLoRAKVModel`

```python
class JointLoRAKVModel(nn.Module):
    """LLaMA-3.1-8B + LoRA (trainable) + Locret retaining heads.

    Used for:
        - JointLoRA-KV: freeze_locret=False (both LoRA and Locret trained)
        - B1 baseline: freeze_locret=True (only LoRA trained)
    """

    def __init__(
        self,
        base_model,                          # PeftModel wrapping LLaMA-3.1-8B
        locret_heads: LocretHeadCollection,  # 32 RetainingHead instances
        num_labels: int,                     # GLUE task num_labels (2 or 3)
        config: ExperimentConfig,
    ) -> None: ...

    def forward(
        self,
        input_ids: Tensor,                   # (B, L) — token IDs
        attention_mask: Tensor,              # (B, L) — 1=attend, 0=pad
        labels: Optional[Tensor] = None,     # (B,) — class indices for CE loss
        budget_ratio: Optional[float] = None,  # KV retention ratio (default config.budget_ratio)
        training_mode: bool = True,          # True=soft mask, False=hard eviction
    ) -> Dict[str, Tensor]:
        """
        Forward pass with KV eviction.

        Returns:
            {
                "loss": scalar Tensor (CE loss, only if labels provided),
                "logits": (B, num_labels) — classification logits,
                "cis_scores": List[Tensor] — 32 tensors of shape (B, L, 8),
                "tokens_retained_ratio": float — fraction of tokens retained
            }

        Training mode (training_mode=True):
            - Uses soft budget mask (differentiable) for gradient flow
            - CIS scores used to compute importance-weighted representation
        Inference mode (training_mode=False):
            - Uses hard top-k eviction on KV cache
            - Only top budget_ratio*L tokens retained per layer
        """

    def compute_cis(
        self,
        layer_idx: int,
        hidden_states: Tensor,   # (B, L, 4096)
        q_proj: Tensor,          # (B, L, 4096) after q_proj
        k_proj: Tensor,          # (B, L, 1024) after k_proj
        v_proj: Tensor,          # (B, L, 1024) after v_proj
    ) -> Tensor:
        """
        Compute CIS scores for a single transformer layer.

        Returns:
            (B, L, 8) CIS scores, values in (0, 1)
        """

    def apply_soft_budget_mask(
        self,
        hidden_states: Tensor,   # (B, L, D) = (B, L, 4096)
        cis_scores: Tensor,      # (B, L, 8)
        budget_ratio: float,     # e.g. 0.5
    ) -> Tensor:
        """
        Differentiable soft masking for training gradient flow.

        Args:
            hidden_states: Layer hidden states (B, L, 4096)
            cis_scores: Per-head importance scores (B, L, 8)
            budget_ratio: Fraction to retain

        Returns:
            (B, L, 4096) — importance-weighted hidden states

        Algorithm: See pseudo-code section below
        """

    def apply_hard_eviction(
        self,
        kv_cache: Tuple[Tensor, Tensor],  # (key: (B, n_kv_heads, L, head_dim), value: same)
        cis_scores: Tensor,               # (B, L, 8)
        budget_ratio: float,
    ) -> Tuple[Tensor, Tensor]:
        """
        Hard top-k KV cache eviction for inference.

        Args:
            kv_cache: (key_states, value_states) tensors
            cis_scores: (B, L, 8)
            budget_ratio: Fraction of tokens to retain

        Returns:
            Pruned (key_states, value_states) with L' = int(L * budget_ratio) tokens
        """
```

#### `build_joint_model`

```python
def build_joint_model(
    config: ExperimentConfig,
    num_labels: int,     # GLUE task specific (mnli=3, sst2/qnli=2)
    task: str,           # "mnli", "sst2", "qnli"
    freeze_locret: bool = False,  # False=JointLoRA-KV, True=B1
) -> Tuple[JointLoRAKVModel, AutoTokenizer]:
    """
    Factory: build model + tokenizer for training.

    Args:
        freeze_locret: True → B1 (LoRA only trains); False → JointLoRA-KV (both train)

    Returns:
        (model, tokenizer) tuple

    Steps:
        1. Load LLaMA-3.1-8B with eager attention + float16
        2. Add classification head (nn.Linear(4096, num_labels))
        3. Wrap with PEFT LoRA config
        4. Load Locret heads from checkpoint
        5. If freeze_locret: freeze_locret_heads(heads)
        6. Move to CUDA
    """
```

#### `build_lora_model` (for B2)

```python
def build_lora_model(
    config: ExperimentConfig,
    num_labels: int,
    task: str,
) -> Tuple[nn.Module, AutoTokenizer]:
    """
    Factory: build LoRA-only model for B2 (kvpress heuristic eviction at inference).
    No Locret heads loaded.
    """
```

---

### `trainer.py`

#### `JointLoRAKVTrainer`

```python
class JointLoRAKVTrainer:
    """Trains JointLoRA-KV (or B1 frozen) via task CE loss with separate LRs."""

    def __init__(
        self,
        model: JointLoRAKVModel,
        train_loader: DataLoader,
        config: ExperimentConfig,
        task: str,               # "mnli", "sst2", "qnli"
        seed: int,               # 42, 123, or 456
        is_b1: bool = False,     # True = B1 (frozen Locret, single param group)
    ) -> None: ...

    def build_optimizer(self) -> AdamW:
        """
        Build AdamW with separate parameter groups.

        Param group 1 (always):
            params: LoRA A/B matrices (identified by "lora_" in name)
            lr: config.lora_lr = 1e-4

        Param group 2 (only if not is_b1):
            params: Locret W1/W2 weights (from model.locret_heads.parameters())
            lr: config.locret_lr = 5e-4

        Common: weight_decay=0.01, betas=(0.9, 0.999), eps=1e-8

        Returns: Configured AdamW optimizer
        """

    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """
        Train one epoch.

        Returns:
            {
                "loss": float — mean CE loss for epoch,
                "locret_grad_norm": float — mean Locret gradient norm,
                "step_count": int
            }

        Required log format per step:
            "JointLoRA-KV: Locret heads receiving CE gradients — step {step}, locret_grad_norm={norm:.4f}"
        """

    def train(self) -> List[Dict[str, float]]:
        """
        Full training loop for config.get_epochs(task) epochs.

        Returns:
            List of per-epoch metrics dicts (from train_epoch)
        """

    def save_checkpoint(self, output_dir: str) -> None:
        """Save LoRA adapter + Locret head weights to output_dir."""
```

---

### `evaluate.py`

#### `evaluate_glue`

```python
def evaluate_glue(
    model,
    val_loader: DataLoader,
    task: str,                      # "mnli", "sst2", "qnli"
    budget_ratio: float,            # 0.5 for primary eval
    config: ExperimentConfig,
    collect_cis_samples: bool = False,  # If True, collect sample CIS tensors
) -> Dict[str, object]:
    """
    Evaluate model on GLUE validation set with hard KV eviction.

    Args:
        model: JointLoRAKVModel in eval mode (training_mode=False)
        collect_cis_samples: If True, collect up to 10 CIS sample tensors for shape verification

    Returns:
        {
            "accuracy": float,           # task accuracy
            "task": str,
            "budget_ratio": float,
            "cis_samples": Optional[List[Tensor]],  # List of (B, L, 8) tensors
            "tokens_retained_ratio": float  # actual fraction retained (verify < 0.55)
        }

    Uses: evaluate.load("glue", task).compute(predictions=..., references=...)
    """
```

#### `evaluate_longbench`

```python
def evaluate_longbench(
    model,
    loader: DataLoader,
    task: str,                   # "narrativeqa", "qasper", "multifieldqa_en"
    budget_ratio: float,
    config: ExperimentConfig,
) -> Dict[str, float]:
    """
    Evaluate model on LongBench test set.

    Args:
        model: In generation mode with hard KV eviction

    Returns:
        {
            "f1": float,         # mean QA F1 score
            "task": str,
            "budget_ratio": float
        }

    Uses: qa_f1_score(prediction, ground_truths) from THUDM/LongBench metrics.py
    """
```

#### `evaluate_budget_sensitivity`

```python
def evaluate_budget_sensitivity(
    model,
    val_loader: DataLoader,
    task: str,
    config: ExperimentConfig,
) -> Dict[float, float]:
    """
    Sweep budget_ratio values to produce sensitivity curve.

    Returns:
        {0.3: accuracy, 0.5: accuracy, 0.7: accuracy}
        Keys from config.budget_ratios_sweep = [0.3, 0.5, 0.7]
    """
```

#### `verify_mechanism_activated`

```python
def verify_mechanism_activated(
    training_log: List[str],       # Lines from training log file
    b1_results: Dict,              # {"mean_glue_acc": float, ...}
    joint_results: Dict,           # {"mean_glue_acc": float, "cis_samples": [...], ...}
) -> Tuple[bool, Dict[str, bool]]:
    """
    Verify all four mechanism activation indicators.

    Returns:
        gate_passed: True if all indicators pass AND accuracy gap >= 2.0 pp
        indicators: {
            "locret_grad_received": bool,   # any locret_grad_norm > 1e-6 in log
            "cis_shape_correct": bool,      # all cis_samples have shape[-1] == 8
            "eviction_active": bool,        # tokens_retained_ratio < 0.55
            "accuracy_improved": bool,      # joint_mean_glue > b1_mean_glue
        }

    Gate condition:
        gate_passed = (
            indicators["locret_grad_received"] AND
            indicators["cis_shape_correct"] AND
            indicators["eviction_active"] AND
            indicators["accuracy_improved"] AND
            (joint_results["mean_glue_acc"] - b1_results["mean_glue_acc"]) >= 2.0
        )
    """
```

#### `aggregate_seed_results`

```python
def aggregate_seed_results(
    results_per_seed: List[Dict],   # One dict per seed, each with per-task accuracy
) -> Dict[str, float]:
    """
    Aggregate results across 3 seeds.

    Returns:
        {
            "mean_glue_acc": float,    # Mean of MNLI/SST-2/QNLI accuracies across seeds
            "std_glue_acc": float,     # Std across seeds
            "mnli_mean": float,
            "sst2_mean": float,
            "qnli_mean": float,
        }
    """
```

---

### `data_loader.py`

#### `GLUEDataset`

```python
class GLUEDataset(Dataset):
    def __init__(
        self,
        task: str,               # "mnli", "sst2", "qnli"
        split: str,              # "train", "validation" (or "validation_matched" for mnli)
        tokenizer,
        config: ExperimentConfig,
    ) -> None: ...

    def __len__(self) -> int: ...    # Number of examples

    def __getitem__(self, idx: int) -> Dict[str, object]:
        """
        Returns:
            {
                "input_ids": Tensor (L,),
                "attention_mask": Tensor (L,),
                "labels": int — class index
            }
        Max length: config.max_seq_len = 512
        """
```

#### `get_glue_loaders`

```python
def get_glue_loaders(
    task: str,
    tokenizer,
    config: ExperimentConfig,
    seed: int,
) -> Tuple[DataLoader, DataLoader]:
    """
    Returns (train_loader, val_loader) for given GLUE task.

    train_loader: shuffle=True, batch_size=config.per_device_batch_size
    val_loader: shuffle=False, batch_size=config.per_device_batch_size
    """
```

#### `get_num_labels`

```python
def get_num_labels(task: str) -> int:
    """
    Returns:
        mnli → 3 (entailment, neutral, contradiction)
        sst2 → 2 (negative, positive)
        qnli → 2 (entailment, not_entailment)
    """
```

---

### `visualize.py`

#### Visualization Functions

```python
def plot_gate_metrics_comparison(
    joint_results: Dict,   # {"mean_glue_acc": float, "std_glue_acc": float}
    b1_results: Dict,
    b2_results: Dict,
    output_dir: str,       # config.get_figures_dir()
) -> None:
    """FR-8.1 (Mandatory): Bar chart — JointLoRA-KV vs B1 vs B2 mean GLUE accuracy ± std.
    Saves: {output_dir}/gate_metrics_comparison.png"""

def plot_training_curves(
    training_history: Dict[str, List],  # {"seed_42": [{loss, locret_grad_norm}, ...], ...}
    output_dir: str,
) -> None:
    """FR-8.2: Loss per epoch curves for all 3 seeds.
    Saves: {output_dir}/training_curves.png"""

def plot_per_task_glue(
    joint_results: Dict,   # {"mnli_mean": float, "sst2_mean": float, "qnli_mean": float}
    b1_results: Dict,
    b2_results: Dict,
    output_dir: str,
) -> None:
    """FR-8.3: Per-task accuracy bars for MNLI/SST-2/QNLI.
    Saves: {output_dir}/per_task_glue.png"""

def plot_budget_sensitivity(
    joint_sensitivity: Dict[float, float],   # {0.3: acc, 0.5: acc, 0.7: acc}
    b1_sensitivity: Dict[float, float],
    output_dir: str,
) -> None:
    """FR-8.4: Accuracy vs budget_ratio curve.
    Saves: {output_dir}/budget_sensitivity.png"""

def plot_longbench_comparison(
    joint_results: Dict,   # {"narrativeqa": f1, "qasper": f1, "multifieldqa_en": f1}
    b1_results: Dict,
    b2_results: Dict,
    output_dir: str,
) -> None:
    """FR-8.5: NarrativeQA/Qasper/MultiFieldQA F1 bars.
    Saves: {output_dir}/longbench_comparison.png"""
```

---

### `run_experiment.py`

```python
def set_seed(seed: int) -> None:
    """Set torch.manual_seed, numpy.random.seed, random.seed, cuda seed."""

def run_joint_training(
    config: ExperimentConfig,
    task: str,       # "mnli", "sst2", "qnli"
    seed: int,
) -> Dict:
    """
    Train JointLoRA-KV for one task+seed combo.
    Returns: {training_history, val_results, model_checkpoint_path}
    """

def run_b1_training(
    config: ExperimentConfig,
    task: str,
    seed: int,
) -> Dict:
    """
    Train B1 (LoRA only, frozen Locret) for one task+seed combo.
    Returns: {val_results, model_checkpoint_path}
    """

def run_b2_inference(
    config: ExperimentConfig,
    task: str,
    seed: int,
) -> Dict:
    """
    B2: Run LoRA model with kvpress heuristic eviction at inference.
    Returns: {val_results}
    """

def run_longbench_eval(
    config: ExperimentConfig,
    seed: int,
    model_tag: str,   # "joint", "b1", "b2"
) -> Dict:
    """Evaluate model on all 3 LongBench tasks. Returns per-task F1 scores."""

def main() -> None:
    """
    Orchestration entry point.
    Iterates: seeds × glue_tasks × models {joint, b1, b2}
    Saves JSON results per seed per task.
    Calls aggregate_seed_results, verify_mechanism_activated, visualize.
    """
```

---

## Pseudo-code: Key Algorithms

### Soft Budget Masking (Training Mode)

```
FUNCTION apply_soft_budget_mask(hidden_states, cis_scores, budget_ratio):
    # hidden_states: (B, L, 4096)
    # cis_scores: (B, L, 8)
    # budget_ratio: float, e.g. 0.5

    # 1. Aggregate CIS across KV heads → token-level importance
    token_importance = mean(cis_scores, dim=-1)  # (B, L)

    # 2. Hard top-k selection (for forward pass values)
    k = int(L * budget_ratio)
    topk_vals, topk_idx = topk(token_importance, k=k, dim=-1)  # (B, k)
    hard_mask = zeros(B, L)
    hard_mask.scatter_(1, topk_idx, 1.0)  # (B, L) binary

    # 3. Straight-through estimator for gradient flow
    #    Forward: use hard_mask values
    #    Backward: gradient flows through soft token_importance
    soft_mask = token_importance / token_importance.detach()  # STE: forward=1, backward=grad
    ste_mask = hard_mask + (soft_mask - soft_mask.detach())   # STE trick

    # 4. Apply mask
    masked_hidden = hidden_states * ste_mask.unsqueeze(-1)  # (B, L, 4096)
    RETURN masked_hidden
```

### Hard KV Cache Eviction (Inference Mode)

```
FUNCTION apply_hard_eviction(kv_cache, cis_scores, budget_ratio):
    # kv_cache: (key: (B, n_kv_heads, L, head_dim), value: same)
    # cis_scores: (B, L, 8)

    # 1. Aggregate importance
    token_importance = mean(cis_scores, dim=-1)  # (B, L)

    # 2. Top-k indices (retain budget_ratio fraction)
    k = int(L * budget_ratio)
    retain_idx = argsort(token_importance, dim=-1, descending=True)[:, :k]  # (B, k)
    retain_idx = sort(retain_idx, dim=-1).values  # keep causal order

    # 3. Index into KV cache
    # key: (B, n_kv_heads, L, head_dim) → (B, n_kv_heads, k, head_dim)
    pruned_key = key[:, :, retain_idx, :]   # gather along seq dim
    pruned_value = value[:, :, retain_idx, :]

    RETURN (pruned_key, pruned_value)
```

### Joint Training Loop

```
FUNCTION train_epoch(model, train_loader, optimizer, scheduler, config, epoch):
    model.train()
    losses = []
    locret_norms = []

    FOR step, batch IN enumerate(train_loader):
        IF step % grad_accum_steps == 0:
            optimizer.zero_grad()

        # Forward pass (soft budget mask active)
        outputs = model.forward(
            input_ids=batch["input_ids"].cuda(),
            attention_mask=batch["attention_mask"].cuda(),
            labels=batch["labels"].cuda(),
            budget_ratio=config.budget_ratio,
            training_mode=True,
        )
        loss = outputs["loss"] / grad_accum_steps
        loss.backward()

        IF (step + 1) % grad_accum_steps == 0:
            # Compute Locret gradient norm before clipping
            locret_norm = compute_grad_norm(model.locret_heads.parameters())
            LOG f"JointLoRA-KV: Locret heads receiving CE gradients — step {step}, locret_grad_norm={locret_norm:.4f}"

            clip_grad_norm_(all_trainable_params, max_norm=1.0)
            optimizer.step()
            scheduler.step()

        losses.append(loss.item() * grad_accum_steps)
        locret_norms.append(locret_norm)

    RETURN {"loss": mean(losses), "locret_grad_norm": mean(locret_norms), "step_count": step}
```

---

## Data Flow Diagram

```
INPUT:
  input_ids: (B, L)
  attention_mask: (B, L)
  labels: (B,)

STEP 1: LLaMA-3.1-8B forward (with LoRA adapters)
  → For each layer 0..31:
      q_proj: (B, L, 4096)  [LoRA modifies q_proj weights]
      k_proj: (B, L, 1024)
      v_proj: (B, L, 1024)

STEP 2: CIS scoring (per layer, via RetainingHead)
  qkv = cat([q_proj, k_proj, v_proj], dim=-1)  # (B, L, 6144)
  cis = sigmoid(qkv @ W1.T) @ W2.T             # (B, L, 8)

STEP 3: Training (soft mask) / Inference (hard eviction)
  TRAIN: apply_soft_budget_mask(hidden_states, cis, 0.5)  → (B, L, 4096)
  INFER: apply_hard_eviction(kv_cache, cis, 0.5)          → pruned KV

STEP 4: Classification
  final_hidden: (B, 4096)  [last token or [CLS]-equivalent]
  logits = classification_head(final_hidden)  # (B, num_labels)

STEP 5: Loss
  loss = F.cross_entropy(logits, labels)  # scalar
  loss.backward()  # gradients → LoRA A/B AND Locret W1/W2

OUTPUT:
  {loss: scalar, logits: (B, num_labels), cis_scores: List[32 × (B, L, 8)]}
```

---

## Error Handling

| Error Scenario | Detection | Handler |
|----------------|-----------|---------|
| OOM during joint training | CUDA OOM exception | Reduce per_device_batch_size; use gradient checkpointing |
| Locret checkpoint key mismatch | KeyError on state_dict access | Log available keys; check model name |
| GQA head count mismatch | cis shape[-1] ≠ 8 | Assert num_kv_heads==8 at load time |
| Training divergence (NaN loss) | loss.isnan() check | Stop training, log seed and step |
| Locret grad norm == 0 | Logged per step | Check optimizer param groups include Locret params |
| GLUE metric task name mismatch | ValueError from evaluate.load | Map "mnli" → "mnli", "sst2" → "sst2", "qnli" → "qnli" |

---

## Tensor Shape Reference

| Tensor | Shape | Description |
|--------|-------|-------------|
| input_ids | (B, L) | Token IDs, L ≤ 512 (GLUE) or 15360 (LongBench) |
| attention_mask | (B, L) | 1=attend, 0=pad |
| labels | (B,) | Class indices |
| q_proj output | (B, L, 4096) | Query after projection (D_model=4096) |
| k_proj output | (B, L, 1024) | Key after projection (8 heads × 128 dim) |
| v_proj output | (B, L, 1024) | Value after projection |
| qkv_concat | (B, L, 6144) | Concatenated input to RetainingHead |
| W1 (fc1.weight) | (1024, 6144) | Retaining head input projection |
| W2 (fc2.weight) | (8, 1024) | Retaining head output projection |
| cis_scores per layer | (B, L, 8) | Per-KV-head importance scores in (0,1) |
| token_importance | (B, L) | Aggregated CIS across heads (mean) |
| logits | (B, num_labels) | Classification logits |
| loss | scalar | Cross-entropy classification loss |

*Note: B=batch_size (8), L=sequence_length (≤512 GLUE), D_model=4096, D_kv=1024, n_kv_heads=8*
