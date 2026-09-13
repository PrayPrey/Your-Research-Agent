# Architecture: H-M2 — Projection-Only LoRA Eigenvalue Preservation

**Applied**: PEFT frozen-weights LoRA pattern, single-file PoC experiment pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-M1)
**Status**: patterns found from base code (read directly via filesystem)
**Analyzed Path**: `docs/youra_research/20260327_scope/h-m1/code/`
**Findings**: H-M1 has 4 files — `model.py` (MambaProbe with load_model, extract_layer_A_log, compute_h_spec, get_per_layer_h_spec, get_per_layer_lambda_max, unload; PerplexityEvaluator), `config.py` (ExperimentConfig dataclass), `evaluate.py` (standalone functions), `run_experiment.py` (entry point). Local imports used (`from config import ExperimentConfig`). MambaProbe.compute_h_spec uses `1/min(exp(A_log))` formula (H_spec = 256.18 tokens).

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Pattern | File Location |
|--------|---------------|---------------|
| MambaProbe | copy-and-extend (no cross-hyp import) | `h-m1/code/model.py` |
| ExperimentConfig | copy-and-adapt | `h-m1/code/config.py` |
| load_wikitext103 | copy-and-adapt | `h-m1/code/evaluate.py` |
| prepare_eval_sequences | copy-and-adapt | `h-m1/code/evaluate.py` |

**Verified from**: `docs/youra_research/20260327_scope/h-m1/code/` (actual implementation)

**Note**: H-M1 uses `from config import ExperimentConfig` (local import, no package prefix). H-M2 follows the same pattern — all imports are local within `code/`.

---

## File Structure

- `code/`
  - `config.py` — experiment configuration (extends H-M1 config with LoRA params)
  - `model.py` — MambaProbe (from H-M1) + LoRAAdapter + EigenvaluePreservationValidator
  - `train.py` — LoRA fine-tuning loop on WikiText-103
  - `evaluate.py` — data loading, eigenvalue comparison, metrics, visualization
  - `run_experiment.py` — entry point, orchestrates full pipeline
  - `figures/` — output figures directory

---

## Module Definitions

### ExperimentConfig (`code/config.py`)

**Dependencies**: none

```python
@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "state-spaces/mamba-1.4b-hf"
    tokenizer_id: str = "state-spaces/mamba-1.4b-hf"
    # Dataset
    dataset_name: str = "wikitext"
    dataset_config: str = "wikitext-103-raw-v1"
    max_seq_length: int = 1024
    seed: int = 42
    # LoRA
    lora_r: int = 16
    lora_alpha: int = 32
    lora_target_modules: tuple = ("in_proj", "out_proj")
    lora_dropout: float = 0.1
    # Training
    learning_rate: float = 1e-4
    weight_decay: float = 1e-4
    num_epochs: int = 3
    batch_size: int = 8
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 100
    # Gate
    delta_h_spec_threshold: float = 10.0   # percent
    eigenvalue_corr_threshold: float = 0.95
    h_spec_known: float = 256.18
    # Hardware
    device: str = "cuda"
    dtype: str = "float16"
    # Output
    figures_dir: str = "figures"
    results_path: str = "results.yaml"
    checkpoint_dir: str = "checkpoints"
```

---

### MambaProbe + LoRAAdapter + EigenvaluePreservationValidator (`code/model.py`)

**Dependencies**: ExperimentConfig, torch, transformers, peft

```python
class MambaProbe:
    """Eigenvalue extraction from Mamba-1.4B. Ported from H-M1."""
    def __init__(self, config: ExperimentConfig) -> None: ...
    def load_model(self) -> None: ...
    def extract_layer_A_log(self) -> List[Tensor]: ...
    def compute_h_spec(self) -> float: ...
    def get_per_layer_h_spec(self) -> List[float]: ...
    def get_per_layer_lambda_max(self) -> List[float]: ...
    def get_model(self):
        """Return loaded model reference for LoRA wrapping."""
        ...
    def get_tokenizer(self):
        """Return tokenizer reference."""
        ...
    def unload(self) -> None: ...


class LoRAAdapter:
    """Wraps base model with projection-only LoRA via PEFT."""
    def __init__(self, model, config: ExperimentConfig) -> None: ...
    def apply(self) -> any:
        """Apply LoraConfig to in_proj/out_proj only; return peft model."""
        ...
    def verify_mechanism(self) -> bool:
        """Assert A_log NOT in trainable_params; assert proj+lora ARE trainable."""
        ...
    def get_trainable_param_count(self) -> int: ...


class EigenvaluePreservationValidator:
    """Compare pre/post eigenvalues; compute preservation metrics."""
    def __init__(
        self,
        baseline_a_logs: List[Tensor],
        post_a_logs: List[Tensor],
        config: ExperimentConfig,
    ) -> None: ...
    def compute_delta_h_spec(self) -> float:
        """Return |ΔH_spec| percentage."""
        ...
    def compute_eigenvalue_correlation(self) -> float:
        """Return Pearson correlation between flattened pre/post eigenvalues."""
        ...
    def compute_a_log_max_diff(self) -> float:
        """Return max|A_log_post - A_log_pre| (should be ~0)."""
        ...
    def validate(self) -> dict:
        """Return full metrics dict with hypothesis_pass bool."""
        ...
```

---

### Training Loop (`code/train.py`)

**Dependencies**: ExperimentConfig, torch, transformers, datasets

```python
def load_wikitext103_train(config: ExperimentConfig) -> any:
    """Load and tokenize WikiText-103 train split; chunk to max_seq_length."""
    ...

def build_dataloader(tokenized_dataset, config: ExperimentConfig) -> any:
    """Return DataLoader with batch_size, collate, shuffle=True."""
    ...

def build_optimizer_and_scheduler(
    model,
    config: ExperimentConfig,
    num_training_steps: int,
) -> Tuple[any, any]:
    """Return (AdamW optimizer, cosine scheduler with warmup)."""
    ...

def train(
    model,
    dataloader,
    optimizer,
    scheduler,
    config: ExperimentConfig,
) -> List[float]:
    """Run training loop; return per-step loss list."""
    ...
```

---

### Evaluation and Visualization (`code/evaluate.py`)

**Dependencies**: ExperimentConfig, torch, datasets, transformers, scipy, matplotlib

```python
def load_wikitext103_valid(config: ExperimentConfig) -> any:
    """Load and tokenize WikiText-103 validation split."""
    ...

def compute_perplexity(model, tokenizer, dataset, config: ExperimentConfig) -> float:
    """Compute validation perplexity on WikiText-103."""
    ...

def save_results(results: dict, path: str) -> None: ...

def generate_figures(
    baseline_a_logs: List[Tensor],
    post_a_logs: List[Tensor],
    preservation_metrics: dict,
    train_losses: List[float],
    per_layer_baseline_h_spec: List[float],
    per_layer_post_h_spec: List[float],
    output_dir: str,
) -> None:
    """Generate: (1) gate metrics bar chart [REQUIRED],
    (2) eigenvalue distribution overlay,
    (3) per-layer H_spec change bar chart,
    (4) A_log diff heatmap,
    (5) eigenvalue scatter pre vs post,
    (6) training loss curve.
    """
    ...
```

---

### Experiment Entry Point (`code/run_experiment.py`)

**Dependencies**: ExperimentConfig, MambaProbe, LoRAAdapter, EigenvaluePreservationValidator, train.py, evaluate.py

```python
def main(config: ExperimentConfig) -> dict: ...

if __name__ == "__main__":
    config = ExperimentConfig()
    results = main(config)
```

**Execution flow**:
1. Load Mamba-1.4B via MambaProbe; extract baseline A_log tensors; compute baseline H_spec (verify ~256.18)
2. Apply projection-only LoRA via LoRAAdapter; run verify_mechanism()
3. Load WikiText-103 train split; build dataloader
4. Fine-tune for 3 epochs; record train loss
5. Extract post-training A_log tensors (from base model params)
6. Validate eigenvalue preservation via EigenvaluePreservationValidator
7. Compute validation perplexity (secondary metric)
8. Generate figures; save results.yaml with PASS/FAIL gate verdict

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup project structure | File skeleton, config.py with all LoRA + training params | 5 | 1+1+1+2 |
| A-2 | Port MambaProbe from H-M1 | Copy MambaProbe, add get_model()/get_tokenizer() accessors, verify H_spec ≈ 256.18 | 7 | 2+2+2+1 |
| A-3 | Implement LoRAAdapter | apply() with PEFT LoraConfig targeting in_proj/out_proj; verify_mechanism() assertions | 10 | 3+2+3+2 |
| A-4 | Dataset loading and DataLoader | Load WikiText-103 train+valid, tokenize, chunk, build DataLoader | 8 | 2+2+2+2 |
| A-5 | Implement training loop | AdamW + cosine scheduler + warmup, gradient accumulation, 3 epochs | 11 | 3+2+4+2 |
| A-6 | Implement EigenvaluePreservationValidator | compute_delta_h_spec, eigenvalue_correlation, a_log_max_diff, validate() | 10 | 3+2+3+2 |
| A-7 | Post-training eigenvalue extraction | Extract A_log after training, confirm A_log unchanged numerically | 7 | 2+2+2+1 |
| A-8 | Visualization | 6 figures including mandatory gate metrics bar chart | 9 | 2+1+3+3 |
| A-9 | Results saving and gate evaluation | YAML output, PASS/FAIL on |ΔH_spec| < 10%, perplexity check | 6 | 1+1+2+2 |
| A-10 | Wire run_experiment.py | Orchestrate full pipeline end-to-end; error handling | 7 | 2+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-5, A-6, A-8], Low(4-8): [A-1, A-2, A-4, A-7, A-9, A-10]
