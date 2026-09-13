# Architecture: H-E1

**Type:** EXISTENCE (PoC)
**Applied:** Baseline-vs-Proposed comparison pattern (single fixed config, no ablations)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze (foundation hypothesis, no base_hypothesis_folder, no MCP tools available)
**Analyzed Path:** N/A
**Findings:** New implementation from scratch

---

## Module Structure

```
h-e1/code/
├── config.py
├── data.py
├── model.py
├── train.py
├── evaluate.py
└── visualize.py
```

### config.py

**Dependencies**: none

```python
LORA_CONFIG_TRANSFORMER = dict(r=16, lora_alpha=32,
    target_modules=["q_proj","k_proj","v_proj","o_proj"], lora_dropout=0.0)
LORA_CONFIG_MAMBA = dict(r=16, lora_alpha=32,
    target_modules=["in_proj","out_proj"], lora_dropout=0.0)
TRAIN_CONFIG = dict(lr=2e-4, weight_decay=0.01, betas=(0.9,0.999),
    warmup_steps=100, batch_size=4, grad_accum=4, epochs=3, seed=42)
BENCHMARKS = {
    "gsm8k": dict(hf_id="openai/gsm8k", subset="main", metric="exact_match", density=0.1),
    "nq": dict(hf_id="google-research-datasets/natural_questions", subset=None, metric="f1", density=0.9),
    "mmlu": dict(hf_id="cais/mmlu", subset="all", metric="accuracy", density=0.5),
    "hotpotqa": dict(hf_id="hotpot_qa", subset="fullwiki", metric="f1", density=0.7),
}
```

### data.py (`code/data.py`)

**Dependencies**: config.py

```python
def load_benchmark(name: str) -> "DatasetDict": ...
def format_for_causal_lm(dataset, tokenizer) -> "Dataset": ...
```

### model.py (`code/model.py`)

**Dependencies**: config.py

```python
def load_baseline_model(lora_config: dict) -> "PeftModel":
    """Llama-2-7B + LoRA on q/k/v/o_proj"""
    ...

class MambaWithLoRA(nn.Module):
    def __init__(self, d_model: int = 4096, d_state: int = 64,
                 n_layers: int = 32, d_conv: int = 4, expand: int = 2): ...
    def forward(self, x: "Tensor") -> "Tensor": ...

def load_proposed_model(lora_config: dict) -> "PeftModel":
    """MambaWithLoRA + LoRA on in_proj/out_proj"""
    ...

def verify_mechanism_active(model: "MambaWithLoRA", sample_input: "Tensor") -> bool:
    """Asserts A_log/D exist per layer; checks output shape == input shape"""
    ...
```

### train.py (`code/train.py`)

**Dependencies**: config.py, data.py, model.py

```python
def train_one_benchmark(model, tokenizer, dataset, train_config: dict) -> dict:
    """Returns {'loss_curve': [...], 'checkpoint_path': str}"""
    ...

def run_all_training(model_fn, lora_config: dict, tag: str) -> dict:
    """Loop over BENCHMARKS, train each, save checkpoints + loss curves. tag in {'transformer','mamba'}"""
    ...
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: config.py, data.py

```python
def evaluate_benchmark(model, tokenizer, dataset, metric_name: str) -> float: ...

def compute_deltas(transformer_scores: dict, mamba_scores: dict) -> dict:
    """Per-benchmark: mamba_acc - transformer_acc"""
    ...

def spearman_correlation(deltas: dict, densities: dict) -> float: ...

def check_gate_conditions(deltas: dict, correlation: float) -> dict:
    """GSM8K delta>=-5%, NQ delta<=-15%, correlation>0.5"""
    ...
```

### visualize.py (`code/visualize.py`)

**Dependencies**: evaluate.py

```python
def plot_gate_metrics_comparison(transformer_scores: dict, mamba_scores: dict, out_path: str) -> None: ...
def plot_delta_vs_density(deltas: dict, densities: dict, correlation: float, out_path: str) -> None: ...
def plot_loss_curves(transformer_losses: dict, mamba_losses: dict, out_path: str) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & data loading | Download 4 HF datasets, tokenize/format for causal LM | 8 | 2+3+1+2 |
| A-2 | Baseline model + LoRA | Load Llama-2-7B, apply LoRA config, verify forward pass | 7 | 2+3+1+1 |
| A-3 | Proposed model (Mamba+LoRA) | Implement MambaWithLoRA, apply LoRA to in/out_proj, mechanism verification | 12 | 4+3+3+2 |
| A-4 | Training loop | AdamW + warmup/cosine, grad accum, run both models × 4 benchmarks, save checkpoints/loss curves | 10 | 3+2+2+3 |
| A-5 | Evaluation suite | Per-benchmark metrics (EM/F1/accuracy), delta calc, Spearman correlation, gate check | 8 | 2+2+2+2 |
| A-6 | Visualization | 3 required figures (gate comparison, delta-vs-density scatter, loss curves) | 5 | 2+1+1+1 |
| A-7 | End-to-end integration run | Wire config→data→model→train→evaluate→visualize, produce final gate report | 6 | 1+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-3, A-4, A-5], Low(4-8): [A-2, A-6, A-7]
