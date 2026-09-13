# Config: H-M2 (Instruction-Tuning Effect on BSI & PC1,residual)

**Applied**: Standard PyTorch/HF eval-script constants pattern (no dataclass needed — module-level dict, per architecture spec).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 referenced) — but per `03_architecture.md`, H-E1's `code/` directory does not exist on disk (0 files found). No config classes to verify; H-E1's residualize/PCA algorithm is re-implemented from spec, not imported.
**Status**: Green-field for H-M2 config — no existing config.py in this repo, no base config code to inherit fields from.
**Config Files Found**: None
**Pattern Used**: Hardcoded dict (module constants) — matches architecture's explicit choice: "No separate config.py — model list lives in model_pairs.yaml; benchmark list and seed (42) are module constants."

---

## Config (Hardcoded Dict)

Single fixed config, no tuning/grid — this is a statistical mechanism test on fixed pretrained models, not a trainable model.

```python
# src/config.py

CONFIG = {
    "seed": 42,
    "decode_temperature": 0.0,   # greedy decoding, per NFR-2
    "few_shot_k": 3,             # FR-5.1 ablation: 3-shot base
    "benchmarks": [
        "truthfulqa", "mmlu", "advglue", "bbh", "gsm8k", "winogrande",
    ],
    "n_pairs_expected": 16,      # FR-1.1, warn if fewer after failures
    "paws_wiki_path": "data/paws_wiki_test.json",
    "paws_qqp_path": "data/paws_qqp_dev.json",
    "model_pairs_path": "data/model_pairs.yaml",
    "results_dir": "results/",
    "alpha": 0.05,                # significance threshold, Success Criteria
}
```

`data/model_pairs.yaml` holds the 16 `{family, base_model, instruct_model, params}` rows (static data, not Python config — see architecture).

### Subtasks [0/0 used]

Budget is 0 — no subtask decomposition; config is a single file, copy-paste ready.
