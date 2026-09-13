# Config: H-M1 (Execution Trace Collection)

**Format**: Hardcoded dict (`config.py`) — no training, no sweep, MECHANISM validation with fixed pipeline params.

**Applied**: No matching KB pattern found (searched "DL experiment config patterns") — used standard fixed-dict config for non-training mechanism validation.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (confirmed in architecture doc)
**Config Files Found**: None
**Pattern Used**: dict

---

## A-1: Data Loading Config [Complexity: 8, Budget: 8]

**Applied**: Standard HF `datasets`/`transformers` defaults per PRD Section 4-5.

### Configuration (`config.py`)
```python
DATA_CONFIG = {
    "humaneval_dataset": "openai_humaneval",
    "mbpp_dataset": "mbpp",
    "mbpp_split": "test",          # 500 of 974 problems, per PRD 4.1
    "total_problems": 664,         # 164 + 500
    "model_name": "meta-llama/CodeLlama-7b-Instruct-hf",
    "max_new_tokens": 512,
    "generation_temperature": 0.2, # low temp for deterministic-ish code gen
    "generation_top_p": 0.95,
    "device": "cuda",
    "dtype": "bfloat16",
}
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | HumanEval loader | Load via `datasets.load_dataset("openai_humaneval")` |
| C-1-2 | MBPP loader | Load via `datasets.load_dataset("mbpp", split="test")` |
| C-1-3 | Model/tokenizer init | Load CodeLlama-7B-Instruct + tokenizer with DATA_CONFIG |
| C-1-4 | Code sample generation | `generate_code_sample()` using generation params above |

---

## A-8: Pipeline Orchestration Config [Complexity: 8, Budget: 8]

**Applied**: Fixed-seed reproducibility pattern (NFR-3).

### Configuration (`config.py`)
```python
PIPELINE_CONFIG = {
    "seed": 42,                    # NFR-3, mandatory
    "trace_timeout_sec": 5.0,      # per-sample sandbox timeout
    "overhead_bench_samples": 100, # min samples per PRD FR-5
    "batch_size": 1,               # trace collection is inherently sequential/sandboxed
    "output_dir": "./results/h-m1",
    "log_every": 50,               # progress logging interval (problems)
}

GATE_THRESHOLDS = {
    "accuracy_min": 0.95,          # PRD Section 9
    "overhead_max": 20.0,          # PRD Section 9
}
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-8-1 | Seed + timeout wiring | Set seed=42 globally (random/numpy/torch), pass timeout to `collect_trace` |
| C-8-2 | Gate check | Compare final metrics to `GATE_THRESHOLDS`, emit PASS/FAIL |

---

## Notes

- No hyperparameter sweep — this is a MECHANISM validation, not model training; single fixed config per NFR-3.
- `batch_size=1` for trace collection because `sys.settrace` is per-process/thread; parallelization (if needed) is a subprocess-pool concern outside config scope, not batching.
- No YAML — single small dict is copy-paste ready and avoids an unneeded parsing dependency (pyyaml only used if PRD deps mandate it; not required here).
