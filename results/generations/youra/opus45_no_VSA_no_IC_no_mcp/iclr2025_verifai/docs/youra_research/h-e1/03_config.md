# Configuration: h-e1 (EXISTENCE / PoC)

**Applied**: Standard PyTorch/HF inference defaults + evalplus conventions

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: hardcoded dict

---

## A-1 to A-8: Shared Experiment Config

Single fixed config for the whole PoC (no hyperparameter grid — EXISTENCE hypothesis).

### Configuration (`code/config.py`)

```python
import os

CONFIG = {
    # Models
    "models": [
        "codellama/CodeLlama-7b-Instruct-hf",
        "codellama/CodeLlama-34b-Instruct-hf",
        "gpt-4",
    ],
    "openai_models": {"gpt-4"},  # set of model names routed to OpenAI backend

    # Benchmarks
    "benchmarks": ["humaneval", "mbpp"],
    "benchmark_datasets": {
        "humaneval": "evalplus/humanevalplus",
        "mbpp": "evalplus/mbppplus",
    },

    # Inference (NFR-1: reproducibility)
    "temperature": 0.0,        # greedy decoding
    "max_new_tokens": 512,
    "batch_size": 1,           # sequential evaluation
    "seed": 42,

    # HF model loading (NFR-2: resource efficiency)
    "torch_dtype": "float16",
    "device_map": "auto",

    # Repair loop
    "max_repair_attempts": 5,
    "prompt_formats": ["structured", "raw"],

    # Execution / evaluation
    "exec_timeout_sec": 3.0,
    "eval_k": [1],
    "n_workers": 4,

    # OpenAI retry (NFR-3)
    "openai_max_retries": 5,
    "openai_backoff_base_sec": 2.0,

    # Output
    "results_path": "results.json",
    "figures_dir": "figures/",
}

# Environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # required for gpt-4 calls
```

### Subtasks [8/8 used — one per architecture task, no further breakdown per EXISTENCE rules]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1 | Error parser config | No config needed; uses stdlib `re` only |
| C-2 | Prompt formatter config | No config needed; pure string templating |
| C-3 | Data loading config | `benchmark_datasets` dict above |
| C-4 | Model loading config | `models`, `openai_models`, `torch_dtype`, `device_map` |
| C-5 | Repair loop config | `max_repair_attempts`, `temperature`, `max_new_tokens` |
| C-6 | Evaluation config | `exec_timeout_sec`, `eval_k`, `n_workers` |
| C-7 | Visualization config | `figures_dir` (no tunables) |
| C-8 | Orchestration config | `results_path`, iterates `models` x `benchmarks` x `prompt_formats` |

---

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes (for gpt-4) | OpenAI client auth in `models.generate_code` |

No `.env` file/config layer added — single `os.environ.get` read is sufficient for a PoC with one external key.
