# Config: H-E1
# LLM Trustworthiness Benchmark Data Availability Audit

**Hypothesis:** H-E1 (EXISTENCE / LIGHT tier)
**Date:** 2026-08-20

Applied: Python dataclass configuration pattern — no Archon KB match for NLP evaluation domain (top similarity 0.37, unrelated content).

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project — no existing codebase. Serena analysis not applicable.
**Config Files Found**: None - new config
**Pattern Used**: dataclass + module-level constants

---

## C-1: Config Constants (E-1) [Complexity: 1, Budget: 1]

**Applied**: Standard Python module-level constants + dataclass

### Configuration (`code/config.py`)

```python
from dataclasses import dataclass, field
from pathlib import Path

# --- Benchmark constants ---
REQUIRED_COLS = [
    "BBQ-Disambig", "BBQ-Ambig",
    "GLUE", "AdvGLUE",
    "ANLI-R1", "ANLI-R3",
    "MMLU",
]

SOURCE_PRIORITY = ["TrustLLM", "DecodingTrust", "GLUE-X", "OOD_NLP", "HF"]

BENCHMARK_PAIRS = [
    ("BBQ-Disambig", "BBQ-Ambig"),
    ("GLUE", "AdvGLUE"),
    ("ANLI-R1", "ANLI-R3"),
]

# --- Audit thresholds ---
N_COMMON_GATE = 10                    # min models with full coverage to pass MUST_WORK gate
PROTOCOL_CONSISTENCY_THRESHOLD_PP = 5.0  # max pp delta for same benchmark across sources

# --- Paths ---
FIGURES_DIR = Path("figures")
RESULTS_DIR = Path("results")

# --- Model name normalization ---
# Keys: lowercase raw names from each source. Values: canonical display IDs.
CANONICAL_MAP: dict[str, str] = {
    # LLaMA-2 7B
    "llama-2-7b": "LLaMA-2-7B",
    "llama2-7b": "LLaMA-2-7B",
    "llama_2_7b": "LLaMA-2-7B",
    "meta-llama/llama-2-7b-hf": "LLaMA-2-7B",
    "meta-llama/llama-2-7b": "LLaMA-2-7B",
    # LLaMA-2 13B
    "llama-2-13b": "LLaMA-2-13B",
    "llama2-13b": "LLaMA-2-13B",
    "llama_2_13b": "LLaMA-2-13B",
    "meta-llama/llama-2-13b-hf": "LLaMA-2-13B",
    "meta-llama/llama-2-13b": "LLaMA-2-13B",
    # LLaMA-2 70B
    "llama-2-70b": "LLaMA-2-70B",
    "llama2-70b": "LLaMA-2-70B",
    "llama_2_70b": "LLaMA-2-70B",
    "meta-llama/llama-2-70b-hf": "LLaMA-2-70B",
    "meta-llama/llama-2-70b": "LLaMA-2-70B",
    # LLaMA-2 Chat variants
    "llama-2-7b-chat": "LLaMA-2-7B-Chat",
    "llama2-7b-chat": "LLaMA-2-7B-Chat",
    "meta-llama/llama-2-7b-chat-hf": "LLaMA-2-7B-Chat",
    "llama-2-13b-chat": "LLaMA-2-13B-Chat",
    "llama2-13b-chat": "LLaMA-2-13B-Chat",
    "meta-llama/llama-2-13b-chat-hf": "LLaMA-2-13B-Chat",
    "llama-2-70b-chat": "LLaMA-2-70B-Chat",
    "llama2-70b-chat": "LLaMA-2-70B-Chat",
    "meta-llama/llama-2-70b-chat-hf": "LLaMA-2-70B-Chat",
    # Vicuna
    "vicuna-7b": "Vicuna-7B",
    "vicuna-7b-v1.3": "Vicuna-7B",
    "vicuna-7b-v1.5": "Vicuna-7B",
    "lmsys/vicuna-7b-v1.3": "Vicuna-7B",
    "lmsys/vicuna-7b-v1.5": "Vicuna-7B",
    "vicuna-13b": "Vicuna-13B",
    "vicuna-13b-v1.3": "Vicuna-13B",
    "vicuna-13b-v1.5": "Vicuna-13B",
    "lmsys/vicuna-13b-v1.3": "Vicuna-13B",
    "lmsys/vicuna-13b-v1.5": "Vicuna-13B",
    # GPT-3.5
    "gpt-3.5-turbo": "GPT-3.5-Turbo",
    "gpt-3.5-turbo-0301": "GPT-3.5-Turbo",
    "gpt-3.5-turbo-0613": "GPT-3.5-Turbo",
    "chatgpt": "GPT-3.5-Turbo",
    # GPT-4
    "gpt-4": "GPT-4",
    "gpt-4-0314": "GPT-4",
    "gpt-4-0613": "GPT-4",
    # Claude
    "claude-1": "Claude-1",
    "claude-instant-1": "Claude-Instant-1",
    "claude-2": "Claude-2",
    # Falcon
    "falcon-7b": "Falcon-7B",
    "tiiuae/falcon-7b": "Falcon-7B",
    "falcon-7b-instruct": "Falcon-7B-Instruct",
    "tiiuae/falcon-7b-instruct": "Falcon-7B-Instruct",
    "falcon-40b": "Falcon-40B",
    "tiiuae/falcon-40b": "Falcon-40B",
    "falcon-40b-instruct": "Falcon-40B-Instruct",
    "tiiuae/falcon-40b-instruct": "Falcon-40B-Instruct",
    # Mistral
    "mistral-7b": "Mistral-7B",
    "mistralai/mistral-7b-v0.1": "Mistral-7B",
    "mistral-7b-instruct": "Mistral-7B-Instruct",
    "mistralai/mistral-7b-instruct-v0.1": "Mistral-7B-Instruct",
    # MPT
    "mpt-7b": "MPT-7B",
    "mosaicml/mpt-7b": "MPT-7B",
    "mpt-7b-chat": "MPT-7B-Chat",
    "mosaicml/mpt-7b-chat": "MPT-7B-Chat",
    "mpt-30b": "MPT-30B",
    "mosaicml/mpt-30b": "MPT-30B",
    # Dolly
    "dolly-v2-12b": "Dolly-v2-12B",
    "databricks/dolly-v2-12b": "Dolly-v2-12B",
    # FLAN-T5
    "flan-t5-xxl": "FLAN-T5-XXL",
    "google/flan-t5-xxl": "FLAN-T5-XXL",
    # Alpaca
    "alpaca-7b": "Alpaca-7B",
    "alpaca-13b": "Alpaca-13B",
    # WizardLM
    "wizardlm-13b": "WizardLM-13B",
    "wizardlm-7b": "WizardLM-7B",
}


@dataclass
class AuditConfig:
    n_common_gate: int = N_COMMON_GATE
    protocol_threshold_pp: float = PROTOCOL_CONSISTENCY_THRESHOLD_PP
    mmlu_coverage_target: float = 0.80  # fraction of REQUIRED_COLS models must cover


@dataclass
class VizConfig:
    dpi: int = 150
    figsize_bar: tuple = (8, 5)
    figsize_heatmap: tuple = (12, 8)
    figures_dir: Path = FIGURES_DIR
    gate_line_color: str = "red"
    pass_color: str = "green"
    fail_color: str = "orange"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Constants schema | Write `code/config.py` with CANONICAL_MAP, benchmark constants, AuditConfig dataclass |

---

## C-5: Visualization Config (E-5) [Complexity: 1, Budget: 1]

**Applied**: Standard matplotlib defaults

VizConfig dataclass is defined in `code/config.py` (see C-1 above, no separate file needed).

Usage in `visualize.py`:
```python
from config import VizConfig
cfg = VizConfig()

fig, ax = plt.subplots(figsize=cfg.figsize_bar)
ax.axhline(y=audit_cfg.n_common_gate, color=cfg.gate_line_color, linestyle="--")
fig.savefig(cfg.figures_dir / "gate_metrics.png", dpi=cfg.dpi)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Visualization settings | VizConfig dataclass wired into `visualize.py` figure calls |

---

## YAML Equivalent Schema

```yaml
audit:
  n_common_gate: 10
  protocol_threshold_pp: 5.0
  mmlu_coverage_target: 0.80

viz:
  dpi: 150
  figsize_bar: [8, 5]
  figsize_heatmap: [12, 8]
  figures_dir: "figures"
  gate_line_color: "red"
  pass_color: "green"
  fail_color: "orange"

sources:
  priority: ["TrustLLM", "DecodingTrust", "GLUE-X", "OOD_NLP", "HF"]

benchmarks:
  required_cols:
    - BBQ-Disambig
    - BBQ-Ambig
    - GLUE
    - AdvGLUE
    - ANLI-R1
    - ANLI-R3
    - MMLU
  pairs:
    - [BBQ-Disambig, BBQ-Ambig]
    - [GLUE, AdvGLUE]
    - [ANLI-R1, ANLI-R3]
```
