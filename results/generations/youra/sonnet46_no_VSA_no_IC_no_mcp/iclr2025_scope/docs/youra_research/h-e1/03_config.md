# Configuration: H-E1
## Query-Aware KV Eviction — Existence (PoC)

Applied: Standard PyTorch/HuggingFace PoC dataclass pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## C-4-1: ExperimentConfig Dataclass [Complexity: 1, Budget: 1]

### Configuration (Python Dataclass)

```python
# experiment/config.py
from dataclasses import dataclass, field


@dataclass
class ExperimentConfig:
    # Model
    model_name: str = "meta-llama/Llama-2-7b-chat-hf"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    max_context_length: int = 4096

    # Dataset
    dataset_name: str = "THUDM/LongBench"
    tasks: list = field(default_factory=lambda: ["narrativeqa", "hotpotqa", "2wikimqa", "musique"])
    examples_per_task: int = 100
    seed: int = 42

    # KV Eviction
    methods: list = field(default_factory=lambda: ["M0", "M1", "M2", "M6"])
    retention_ratio: float = 0.5
    observation_window: int = 16   # M1 only; W=16 from SnapKV default
    streaming_sink_size: int = 4   # M6 only; standard StreamingLLM sink size

    # Generation
    max_new_tokens: int = 50

    # Evaluation
    n_bootstrap: int = 1000
    bootstrap_seed: int = 42
    gate_threshold: float = 2.0    # Non-standard: PoC pass criterion M1-M2 delta F1 >= 2.0

    # Output
    output_dir: str = "h-e1"
    results_file: str = "results.json"
    figures_dir: str = "figures"

    # Logging
    log_level: str = "INFO"
    log_eviction_details: bool = True
```

### YAML Config Schema (`config.yaml`)

```yaml
model:
  model_name: "meta-llama/Llama-2-7b-chat-hf"
  torch_dtype: "float16"
  device_map: "auto"
  max_context_length: 4096

dataset:
  dataset_name: "THUDM/LongBench"
  tasks: ["narrativeqa", "hotpotqa", "2wikimqa", "musique"]
  examples_per_task: 100
  seed: 42

eviction:
  methods: ["M0", "M1", "M2", "M6"]
  retention_ratio: 0.5
  observation_window: 16
  streaming_sink_size: 4

generation:
  max_new_tokens: 50

evaluation:
  n_bootstrap: 1000
  bootstrap_seed: 42
  gate_threshold: 2.0

output:
  output_dir: "h-e1"
  results_file: "results.json"
  figures_dir: "figures"

logging:
  log_level: "INFO"
  log_eviction_details: true
```

### Startup Validation

```python
def validate_config(cfg: ExperimentConfig) -> None:
    import torch
    assert torch.cuda.is_available(), "CUDA GPU required"
    assert cfg.retention_ratio > 0.0 and cfg.retention_ratio < 1.0
    assert cfg.observation_window > 0
    assert cfg.examples_per_task > 0
    assert cfg.n_bootstrap >= 100
    assert cfg.gate_threshold > 0.0
    # Verify model access (HF token may be needed for gated model)
    from huggingface_hub import model_info
    try:
        model_info(cfg.model_name)
    except Exception as e:
        raise RuntimeError(f"Model not accessible: {e}")
```

### PoC Fixed vs. Future-Tunable Fields

| Field | PoC Status | Future |
|---|---|---|
| `model_name` | Fixed | Extend to other models |
| `tasks` | Fixed (4 QA tasks) | Add summarization tasks |
| `examples_per_task` | Fixed (100) | Full LongBench |
| `seed` | Fixed (42, single run) | Multi-seed grid |
| `retention_ratio` | Fixed (0.5) | Grid: 0.3–0.8 |
| `observation_window` | Fixed (16) | Grid: 8–64 |
| `methods` | Fixed (M0–M6 subset) | Add M3–M5 |
| `gate_threshold` | Fixed (2.0 F1) | Adjusted per hypothesis |
| `n_bootstrap` | Fixed (1000) | Unchanged |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | ExperimentConfig | Dataclass + YAML schema + validation |
