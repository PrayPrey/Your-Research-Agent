# Config: H-M2 (Representation Invariance Mechanism)

Applied: LoRA fine-tuning config extension pattern (reused from H-M1)
Applied: Compute-matched training config pattern (epochs scaled by data multiplier)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code (`h-m1/03_config.md`, which itself verified `h-e1/code/config.py`)
**Config Files Found**: `h-m1/03_config.md` (flat `Config` dataclass; no `h-m2/code/` yet — pre-implementation)
**Pattern Used**: dataclass (split into `TrainingConfig`, `RepresentationConfig`, `EvaluationConfig` per FR-2/3, FR-4, FR-5/7)

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m1/03_config.md (ACTUAL CODE, traced to h-e1/code/config.py)
@dataclass
class Config:
    model_id: str = "mistralai/Mistral-7B-v0.1"
    dtype: str = "bfloat16"
    device_map: str = "auto"
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple = ("q_proj", "v_proj", "k_proj", "o_proj")
    lr: float = 2e-5
    batch_size: int = 4
    grad_accum: int = 8
    epochs: int = 3
    seeds: tuple = (42, 123, 456)
```

H-M2 reuses `model_id`, `dtype`, LoRA fields, `lr`, `batch_size`, `grad_accum`, `seeds` verbatim. `epochs` is overridden per training condition below.

---

## FR-2/FR-3: Training Config (Verbatim vs Paraphrase-Augmented) [Complexity: 8, Budget: 2 subtasks]

**Applied**: Compute-matched training config pattern

### YAML Schema

```yaml
training:
  model_id: mistralai/Mistral-7B-v0.1
  dtype: bfloat16
  lora_rank: 16
  lora_alpha: 32
  lora_dropout: 0.05
  lora_target_modules: [q_proj, v_proj, k_proj, o_proj]
  lr: 2.0e-5
  weight_decay: 0.01
  batch_size: 4
  grad_accum: 8
  warmup_ratio: 0.1
  contamination_pct: 0.10
  condition: verbatim  # or paraphrase
  epochs: 12           # verbatim=12, paraphrase=3 (compute-matched grad steps)
  paraphrases_per_item: 3
  seeds: [42, 123, 456]
```

### Configuration (Python Dataclass)

```python
@dataclass
class TrainingConfig:
    model_id: str = "mistralai/Mistral-7B-v0.1"
    dtype: str = "bfloat16"

    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple = ("q_proj", "v_proj", "k_proj", "o_proj")

    lr: float = 2e-5
    weight_decay: float = 0.01
    batch_size: int = 4
    grad_accum: int = 8
    warmup_ratio: float = 0.1

    contamination_pct: float = 0.10
    condition: str = "verbatim"  # "verbatim" | "paraphrase"
    epochs: int = 12             # Non-standard: verbatim=12 to match paraphrase's 4x data at 3 epochs (same grad steps)
    paraphrases_per_item: int = 3

    seeds: tuple = (42, 123, 456)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-FR23-1 | Verbatim trainer | Train LoRA model on 1,404 verbatim items, `epochs=12` |
| C-FR23-2 | Paraphrase-augmented trainer | Build 5,616-sample augmented dataset (orig + 3 paraphrases), train `epochs=3` |

---

## FR-4: Representation Extraction Config [Complexity: 6, Budget: 1 subtask]

**Applied**: Standard PyTorch defaults (last-layer hidden state, mean-pool)

### YAML Schema

```yaml
representation:
  hidden_layer_index: -1
  pooling: mean
  hidden_size: 4096
  max_seq_length: 512
  n_eval_items: 1000
  k_paraphrases: 5
```

### Configuration (Python Dataclass)

```python
@dataclass
class RepresentationConfig:
    hidden_layer_index: int = -1   # last transformer layer
    pooling: str = "mean"          # mean-pool over sequence, excluding padding
    hidden_size: int = 4096
    max_seq_length: int = 512
    n_eval_items: int = 1000
    k_paraphrases: int = 5
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-FR4-1 | Hidden state extractor | `output_hidden_states=True`, mean-pool masked last layer to `[4096]` per item |

---

## FR-5/FR-7: Evaluation Config (Similarity + Mechanism Verification) [Complexity: 7, Budget: 2 subtasks]

**Applied**: Threshold-based mechanism verification pattern (reused from H-M1 `MechanismThresholds`)

### YAML Schema

```yaml
evaluation:
  n_eval_items: 1000
  k_paraphrases: 5
  mps_diff_threshold: 0.05
  effect_size_target: 0.3
  p_value_threshold: 0.05
  log_prefix: "[MECHANISM CHECK]"
```

### Configuration (Python Dataclass)

```python
@dataclass
class EvaluationConfig:
    n_eval_items: int = 1000
    k_paraphrases: int = 5
    mps_diff_threshold: float = 0.05   # FR-7.1 gate: MPS_paraphrase - MPS_verbatim
    effect_size_target: float = 0.3    # Cohen's d, medium effect
    p_value_threshold: float = 0.05
    log_prefix: str = "[MECHANISM CHECK]"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-FR57-1 | MPS + similarity aggregation | Compute per-item cosine similarity to K=5 paraphrases, aggregate MPS distributions for both conditions |
| C-FR57-2 | Statistical mechanism check | `scipy.stats.ttest_ind`, Cohen's d, compare to thresholds, log via `log_prefix` |

---

## Non-Budgeted Items (Reference Only)

FR-1 (data pipeline), FR-6 (visualization) reuse `TrainingConfig`/`RepresentationConfig` fields (`contamination_pct`, `paraphrases_per_item`, `n_eval_items`, `k_paraphrases`); no additional config classes needed.
