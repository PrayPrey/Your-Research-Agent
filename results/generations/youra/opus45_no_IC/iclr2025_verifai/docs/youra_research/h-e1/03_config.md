# Config: H-E1 (Error Class Independence Verification)

**Type:** EXISTENCE (PoC) | **Format:** Hardcoded dict (single fixed config, no tuning)

**Applied**: No close KB match for DL config patterns (best hits: latent-diffusion, torch inductor config — unrelated). Using standard Python dict config for PoC per YouRA EXISTENCE convention.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design, Serena skipped (no existing code)
**Config Files Found**: None
**Pattern Used**: Hardcoded dict

---

## Config (`code/config.py`)

Single fixed PoC config — no hyperparameter grid, no ablations, 1 seed.

```python
CONFIG = {
    "SEED": 42,
    "TEMPERATURE": 0.2,
    "N_SAMPLES": 10,
    "MODELS": ["codellama/CodeLlama-7b-hf", "gpt-4"],
    "JACCARD_THRESHOLD": 0.30,
    "MEAN_JACCARD_THRESHOLD": 0.25,  # secondary success criterion

    # Dataset
    "HUMANEVAL_SIZE": 164,
    "VERUS_SUBSET_SOURCE": "secure-foundations/human-eval-verus",  # 23/164 problems, SMT strategy only

    # Paths (relative to hypothesis folder)
    "FIGURES_DIR": "figures/",
    "RESULTS_DIR": "results/",
}
```

## Example `config.yaml` (optional, for reference — code uses CONFIG dict above)

```yaml
seed: 42
temperature: 0.2
n_samples: 10
models:
  - codellama/CodeLlama-7b-hf
  - gpt-4
jaccard_threshold: 0.30
mean_jaccard_threshold: 0.25
humaneval_size: 164
figures_dir: figures/
results_dir: results/
```

---

## Paths

| Key | Value | Notes |
|-----|-------|-------|
| `FIGURES_DIR` | `{hypothesis_folder}/figures/` | 3 required figures (bar, venn, per-model) |
| `RESULTS_DIR` | `{hypothesis_folder}/results/` | Jaccard overlap JSON, sample sets |

---

## Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1 | Define CONFIG dict | Single fixed dict in `config.py` with all hyperparameters above |
| C-2 | Path resolution | Resolve `FIGURES_DIR`/`RESULTS_DIR` relative to hypothesis folder at runtime, ensure dirs exist (`os.makedirs(..., exist_ok=True)`) |
