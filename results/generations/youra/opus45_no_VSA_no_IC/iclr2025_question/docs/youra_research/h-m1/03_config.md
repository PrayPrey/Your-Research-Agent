# Configuration: h-m1 (MECHANISM - cross-dataset transfer)

Applied: fixed-single-config-poc pattern (KB search "DL config patterns" returned only unrelated diffusion/torch-inductor/JAX results; reused h-e1 dict convention).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena had no active project registered; base config verified via direct file Read (`h-e1/code/config.py`), same requirement satisfied.
**Config Files Found**: `h-e1/code/config.py` (module-level dict/constants, no dataclass)
**Pattern Used**: Hardcoded dict (module-level constants) — matches h-e1 and architecture spec

---

Fixed single config per architecture; no hyperparameter grid (probe hyperparams fixed from OATML SEP paper defaults). Layer ablation (M-7) sweeps `LAYER_IDX` as a loop variable, not a config grid.

## M-1: Setup + config [Complexity: 5, Budget: 4 subtasks]

**Applied**: Standard PyTorch/HF reproducibility defaults (fixed seed); sklearn LogisticRegression defaults from OATML SEP paper.

### Configuration (Hardcoded dict)

```python
# config.py
import os

SEED = 42

MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
N_LAYERS = 32
HIDDEN_DIM = 4096

TRAIN_DATASET = "trivia_qa"    # rc.nocontext, train[:11000]
TRAIN_N_SAMPLES = 11000
EVAL_DATASET = "truthful_qa"   # generation, validation (817 full split)

NLI_MODEL_ID = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"  # verified from h-e1 actual code

N_SAMPLES = 5          # generations per question for SE labels
TEMPERATURE = 1.0
LAYER_IDX = -1         # default last layer; M-7 ablation sweeps range(20, 32)
ABLATION_LAYERS = list(range(20, 32))

# Probe hyperparams (OATML SEP paper defaults, sklearn LogisticRegression)
PROBE_SOLVER = "lbfgs"
PROBE_MAX_ITER = 1000
PROBE_C = 1.0

TORCH_DTYPE = "float16"
DEVICE_MAP = "auto"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")

# Gate thresholds
AUROC_PASS_THRESHOLD = 0.70
AUROC_FAIL_THRESHOLD = 0.60
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Model + dataset IDs | `MODEL_ID`, `TRAIN_DATASET`, `EVAL_DATASET`, `NLI_MODEL_ID` constants |
| C-1-2 | SE generation params | `N_SAMPLES`, `TEMPERATURE`, `LAYER_IDX`, `ABLATION_LAYERS` |
| C-1-3 | Probe hyperparams | `PROBE_SOLVER`, `PROBE_MAX_ITER`, `PROBE_C` (sklearn LogisticRegression) |
| C-1-4 | Paths + gate thresholds | `RESULTS_DIR`, `FIGURES_DIR`, `AUROC_PASS_THRESHOLD`, `AUROC_FAIL_THRESHOLD` |

---

## Inherited Configuration (Base Hypothesis: h-e1)

### Config Values (From Actual Code — `h-e1/code/config.py`)

h-m1 reuses these exact values (verified from base code, not h-e1 spec which had a mismatch: `microsoft/deberta-v3-large-mnli` in spec vs. actual `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli`):

```python
SEED = 42
NLI_MODEL_ID = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"  # actual code value
N_SAMPLES = 5
TORCH_DTYPE = "float16"
DEVICE_MAP = "auto"
```

**Not reused** (h-m1 diverges by design):
- `TEMPERATURE`: h-e1 uses `0.7`; h-m1 spec (architecture + PRD FR-3) fixes `1.0` — kept as-is per h-m1 architecture, not inherited.
- `LAYER_FRACTION` (h-e1, `2/3` of `n_layers`): h-m1 uses absolute `LAYER_IDX = -1` (last layer) with explicit `ABLATION_LAYERS` sweep instead.
- `MODELS` dict (multi-model h-e1): h-m1 uses single `MODEL_ID` (Llama-3-8B only, per PRD out-of-scope: "Multi-model comparison").
- `TRAIN_SPLIT = 0.8` (in-distribution split in h-e1): not applicable — h-m1 trains on all of TriviaQA(11k), evaluates on separate TruthfulQA(817).

**Verified from**: `h-e1/code/config.py` (actual implementation, read directly).

### External Module Reuse (Not Config, See Architecture)

`ModelWrapper` (`h-e1/code/models.py`) and `SemanticEntropyProbe` (`h-e1/code/sep.py`) are imported/copied as-is; their internal defaults (`max_new_tokens=100` in `ModelWrapper.generate`) are hardcoded in that code, not part of h-m1's config surface.
