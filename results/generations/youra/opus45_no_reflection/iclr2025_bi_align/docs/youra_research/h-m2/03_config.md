# Config: H-M2 (MECHANISM - inference-only comparison)

Applied: No directly relevant KB pattern found (searched "inference generation config seed reproducibility" — only training-loop results); standard PyTorch seeding + HF `generate()` defaults used instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: config classes verified from base code (read directly via Read tool)
**Config Files Found**: `docs/youra_research/h-m1/code/config.py` (`BiDPOConfig` dataclass)
**Pattern Used**: Dataclass (module-level constants for H-M2, matching architecture spec's flat style)

---

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-m1/code/config.py (ACTUAL CODE)
@dataclass
class BiDPOConfig:
    seed: int = 42
    model_name: str = "mistralai/Mistral-7B-Instruct-v0.2"
    dtype: str = "bfloat16"
    device_map: str = "auto"
    output_dir: str = "outputs/"
    figures_dir: str = "outputs/figures/"
    results_path: str = "outputs/results.json"
```

**Verified from**: `docs/youra_research/h-m1/code/config.py` (actual implementation)
**Checkpoint note**: `final.pt` is a raw `model.state_dict()` (verified from H-M1 `train.py`'s `save_checkpoint`), NOT a dict with `"model_state_dict"` key. Load via `model.load_state_dict(torch.load(path, map_location="cpu"), strict=False)`.

---

## G-1: Config + Generation/Comparison Setup [Complexity: 4, Budget: 2 subtasks]

**Applied**: Standard PyTorch/HF inference defaults; no tuning (MECHANISM = single fixed run, no grid).

### Configuration (module-level constants, matches architecture spec)

```python
"""H-M2 inference comparison configuration."""
import os

SEED: int = 42
BASELINE_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"
BIDPO_MODEL_BASE: str = "mistralai/Mistral-7B-Instruct-v0.2"
BIDPO_CHECKPOINT_PATH: str = "../h-m1/code/outputs/final.pt"

DTYPE: str = "bfloat16"
DEVICE_MAP: str = "auto"

N_PROMPTS: int = 500
MAX_PROMPT_LENGTH: int = 768
MAX_NEW_TOKENS: int = 256
TEMPERATURE: float = 0.7
TOP_P: float = 0.9
DO_SAMPLE: bool = True

ALPHA_ONE_SIDED: float = 0.05
COHENS_D_THRESHOLD: float = 0.2

OUTPUT_DIR: str = "outputs/"
FIGURES_DIR: str = "figures/"
RESULTS_PATH: str = "outputs/results.json"


def ensure_dirs() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)
```

Non-standard: `DO_SAMPLE=True` required — greedy decoding with fixed temperature/top_p params would be contradictory (HF ignores temp/top_p if `do_sample=False`).

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Write config.py | Module constants above + `ensure_dirs()` |
| C-1-2 | Copy collab_score.py | Copy verbatim from `h-m1/code/collab_score.py` (no config changes) |

---

## Self-Validation

- [x] ONE format only (module-level constants, matching architecture — not a dataclass, per architecture spec's flat interface)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard value (`DO_SAMPLE`)
- [x] Subtask count within budget (2/2)
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section with verified field names from actual H-M1 code
