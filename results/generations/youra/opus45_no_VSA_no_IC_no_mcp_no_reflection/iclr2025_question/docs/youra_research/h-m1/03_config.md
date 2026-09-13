# Configuration: h-m1

**Type:** MECHANISM (fixed hyperparameters — no tuning, per PRD "Out of Scope")
**Format:** Python module-level constants (matches h-e1 base pattern)

Applied: Fixed single-run mechanism config (KB: standard PyTorch/HF defaults, no sweep)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: Verified from actual code at `docs/youra_research/h-e1/code/config.py` and `model.py`
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` (module-level constants, not dataclass)
**Pattern Used**: flat module constants (`NAME = value`), imported directly by other modules

**Field name discrepancies found (spec vs actual code)**:
| Field | h-e1 actual code | h-m1 required (PRD/brief) |
|-------|-------------------|----------------------------|
| `NLI_MODEL_ID` | `"microsoft/deberta-v3-large"` (no `-mnli`) | `"microsoft/deberta-v3-large-mnli"` |
| `MAX_NEW_TOKENS` | `256` | `128` (per brief inference protocol) |
| `AUROC_THRESHOLD` | `0.55` | `0.70` (h-m1 gate) |

h-m1 uses its **own** `config.py` (does not import h-e1's) since these values diverge. Only `generate_samples(model, tokenizer, prompt, n, temperature)` signature from h-e1 `model.py` is reused as-is — it accepts `max_tokens` implicitly via its own `MAX_NEW_TOKENS` import, so h-m1 calls it with explicit override or reimplements with h-m1's own `MAX_NEW_TOKENS`. See note below.

---

## h-m1/code/config.py

```python
# config.py - h-m1 semantic entropy configuration (MECHANISM, fixed hyperparams)

SEED = 42

# LLM (reused loader from h-e1, own generation params here)
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
DTYPE = "bfloat16"
DEVICE_MAP = "auto"
MAX_NEW_TOKENS = 128          # Non-standard: brief specifies 128, differs from h-e1's 256

# Multi-sample generation for semantic entropy
NUM_SAMPLES = 10
TEMPERATURE = 0.7

# NLI model for bidirectional entailment clustering
NLI_MODEL_ID = "microsoft/deberta-v3-large-mnli"   # Note: differs from h-e1's base NLI id (no -mnli suffix)
NLI_MAX_LENGTH = 512
ENTAILMENT_THRESHOLD = 0.7    # min(P(entail A->B), P(entail B->A)) > threshold => same cluster

# Gate
AUROC_GATE = 0.70

# Dataset (reused from h-e1)
DATASET_NAME = "truthful_qa"
DATASET_CONFIG = "multiple_choice"
CACHE_DIR = "../../h-e1/code/.cache"   # reuse h-e1's cached dataset

# Baseline scores (from h-e1 validated run)
BASELINE_SCORES_CSV = "../../h-e1/code/outputs/scores.csv"
BASELINE_METRICS_JSON = "../../h-e1/code/outputs/metrics.json"

# Output
RESULTS_DIR = "results"
FIGURES_DIR = "../figures"
```

**Note on `generate_samples` reuse**: h-e1's `generate_samples(model, tokenizer, prompt, n, temperature)` hardcodes `max_new_tokens=MAX_NEW_TOKENS` from **h-e1's own config** (256) inside `model.py`. Since h-m1 needs 128, h-m1 must NOT import `generate_samples` as-is — instead reimplement a thin local wrapper in `semantic_entropy.py` calling `model.generate(..., max_new_tokens=config.MAX_NEW_TOKENS)` directly, reusing only `load_model_and_tokenizer` from h-e1's `model.py` unchanged.

---

## Baseline Score Field Mapping (h-e1 `outputs/scores.csv`)

Actual columns: `idx, label, token_entropy, p_true` (NOT `max_prob`/`choice_entropy` as brief names them).

Mapping for h-m1 `baselines.py`:
- `max_prob` proxy → `1 - p_true` (or check h-e1 `evaluate.py`/`metrics.json` for exact derivation used to get AUROC=0.8068)
- `choice_entropy` proxy → `token_entropy`

`baselines.py` must load `metrics.json` for the authoritative validated AUROC values (0.8068, 0.7703) rather than recomputing, and use `scores.csv` columns only for the correlation-scatter and ROC-overlay figures.

---

## Subtasks Reference (from Architecture Epic Tasks — unchanged, config supports all)

| ID | Task | Config fields used |
|----|------|---------------------|
| M-1 | Wire h-e1 imports | `MODEL_ID`, `DTYPE`, `DEVICE_MAP` (via h-e1 `load_model_and_tokenizer`) |
| M-2 | Load NLI model | `NLI_MODEL_ID`, `NLI_MAX_LENGTH` |
| M-3 | Bidirectional entailment + clustering | `ENTAILMENT_THRESHOLD` |
| M-4 | SemanticEntropy class | `NUM_SAMPLES`, `TEMPERATURE`, `MAX_NEW_TOKENS` |
| M-5 | Score full dataset | `DATASET_NAME`, `DATASET_CONFIG`, `CACHE_DIR`, `SEED` |
| M-6 | Load h-e1 baselines | `BASELINE_SCORES_CSV`, `BASELINE_METRICS_JSON` |
| M-7 | AUROC + gate | `AUROC_GATE` |
| M-8 | Visualizations | `FIGURES_DIR` |
| M-9 | End-to-end run | `RESULTS_DIR`, all above |
