# H-M3 Configuration: Mechanism Discrimination

Applied: flat-dict-module-level-constants (inherited from h-m2/code/config.py pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code (h-m2/code/config.py read directly)
**Config Files Found**: `h-m2/code/config.py` (flat dict pattern, module-level constants)
**Pattern Used**: hardcoded dict / module-level constants (NOT dataclass)

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual h-m2/code/config.py)

```python
# Verified field names and defaults from h-m2/code/config.py

GATE_TYPE: str = "SHOULD_WORK"
N_BOOTSTRAP: int = 1000
SEED: int = 42
SIZES: list = ["1.4b", "2.8b", "6.9b"]
ALIGNMENTS: list = ["sft", "dpo", "ppo"]
N_ITEMS_EXPECTED: int = 14042

LMEVAL_NUM_FEWSHOT: int = 4          # MMLU (verified: h-m2 uses 4-shot)
LMEVAL_BATCH_SIZE: str = "auto"
LMEVAL_LOG_SAMPLES: bool = True
LMEVAL_TIMEOUT_SECONDS: int = 7200

FIGURE_DPI: int = 150
FIGURE_FORMAT: str = "png"

MODEL_REGISTRY: dict = {
    "1.4b-base": "EleutherAI/pythia-1.4b",
    "2.8b-base": "EleutherAI/pythia-2.8b",
    "6.9b-base": "EleutherAI/pythia-6.9b",
    "1.4b-sft":  "lomahony/pythia-1.4b-deduped-tldr",
    "1.4b-dpo":  "Leogrin/pythia-1.4b-sft-tldr-dpo",
    "1.4b-ppo":  "usvsnsp/pythia-1.4b-sft-tldr-ppo",
    "2.8b-sft":  "lomahony/pythia-2.8b-deduped-tldr",
    "2.8b-dpo":  "Leogrin/pythia-2.8b-sft-tldr-dpo",
    "2.8b-ppo":  "usvsnsp/pythia-2.8b-sft-tldr-ppo",
    "6.9b-sft":  "lomahony/pythia-6.9b-deduped-tldr",
    "6.9b-dpo":  "Leogrin/pythia-6.9b-sft-tldr-dpo",
    "6.9b-ppo":  "usvsnsp/pythia-6.9b-sft-tldr-ppo",
}

HF_MODEL_IDS: dict = {
    "1.4b": {"base": "EleutherAI/pythia-1.4b", "sft": "lomahony/pythia-1.4b-deduped-tldr",
             "dpo": "Leogrin/pythia-1.4b-sft-tldr-dpo", "ppo": "usvsnsp/pythia-1.4b-sft-tldr-ppo"},
    "2.8b": {"base": "EleutherAI/pythia-2.8b", "sft": "lomahony/pythia-2.8b-deduped-tldr",
             "dpo": "Leogrin/pythia-2.8b-sft-tldr-dpo", "ppo": "usvsnsp/pythia-2.8b-sft-tldr-ppo"},
    "6.9b": {"base": "EleutherAI/pythia-6.9b", "sft": "lomahony/pythia-6.9b-deduped-tldr",
             "dpo": "Leogrin/pythia-6.9b-sft-tldr-dpo", "ppo": "usvsnsp/pythia-6.9b-sft-tldr-ppo"},
}
```

**Verified from**: `/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/h-m2/code/config.py`

---

## A-4: Argmax Partition + Brier Subsets [Complexity: 12, Budget: 3 subtasks]

Applied: flat-dict-module-level-constants

### Configuration (h-m3/code/config.py additions)

```python
# ── Argmax partition + Brier decomposition constants ─────────────────────────
N_BINS: int = 15                       # Brier reliability bins (from h-e1 calibration_analysis.py)
H1_COHENS_D_THRESHOLD: float = 0.1    # Minimum Cohen's d for H1 signature detection
N_BOOTSTRAP: int = 1000               # inherited from h-m2
SEED: int = 42                        # inherited from h-m2

# H1 signature: cohens_d_shared < H1_COHENS_D_THRESHOLD
# (small effect = argmax-shared items have stable calibration across base/aligned)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | argmax_partition constants | N_BINS=15, H1_COHENS_D_THRESHOLD=0.1 in config.py |
| C-4-2 | Bootstrap CI parameters | N_BOOTSTRAP=1000, SEED=42 (inherited, verify in config.py) |
| C-4-3 | H1 signature detection criteria | cohens_d_shared < H1_COHENS_D_THRESHOLD logic constant |

---

## A-6: Mechanism Report [Complexity: 12, Budget: 3 subtasks]

Applied: flat-dict-module-level-constants

### Configuration (h-m3/code/config.py additions)

```python
# ── Gate thresholds ───────────────────────────────────────────────────────────
GATE_TYPE: str = "SHOULD_WORK"        # inherited from h-m2
H1_RHO_THRESHOLD: float = 0.9        # Non-standard: H1 requires very high rank correlation
H2_RHO_THRESHOLD: float = 0.85       # H2 secondary threshold (all 9 pairs must pass H1)

# ── Report output paths ───────────────────────────────────────────────────────
# (resolved from _CODE_DIR anchor in config.py)
H_M3_REPORT_PATH: str = str(_H_M3_DIR / "04_validation.md")
H_M3_EXPERIMENT_RESULTS_JSON: str = str(_H_M3_DIR / "experiment_results.json")
VERIFICATION_STATE_PATH: str = str(_H_M3_DIR.parent / "verification_state.yaml")

# ── verification_state.yaml field mappings ────────────────────────────────────
VERIFICATION_STATE_H_M3_KEY: str = "h-m3"
VERIFICATION_STATE_FIELDS: dict = {
    "gate_pass": "gate_pass",
    "dominant_mechanism": "dominant_mechanism",
    "mean_rho_min": "mean_rho_min",
    "cohens_d_shared_max": "cohens_d_shared_max",
    "h3_flag": "h3_flag",
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Gate threshold config | H1_RHO_THRESHOLD=0.9, H2_RHO_THRESHOLD=0.85 in config.py |
| C-6-2 | Report paths and sections | H_M3_REPORT_PATH, H_M3_EXPERIMENT_RESULTS_JSON, VERIFICATION_STATE_PATH |
| C-6-3 | verification_state.yaml field mappings | VERIFICATION_STATE_H_M3_KEY and VERIFICATION_STATE_FIELDS dict |

---

## A-7: Visualization [Complexity: 11, Budget: 2 subtasks]

Applied: flat-dict-module-level-constants

### Configuration (h-m3/code/config.py + visualization.py additions)

```python
# ── Figure configuration (config.py) ─────────────────────────────────────────
FIGURE_DPI: int = 150                 # inherited from h-m2
FIGURE_FORMAT: str = "png"            # inherited from h-m2
H_M3_FIGURES_DIR: str = str(_H_M3_DIR / "figures")

# ── Visualization module-level constants (visualization.py) ──────────────────
# Color scheme matches h-m2/code/visualization.py COLORS dict pattern
COLORS: dict = {
    "ppo": "red",
    "dpo": "orange",
    "sft": "blue",
    "base": "gray",
}

# Threshold annotation values for figure_01_spearman_rho.png
H1_THRESHOLD_ANNOTATION: float = 0.9   # drawn as horizontal dashed line
H2_THRESHOLD_ANNOTATION: float = 0.85  # drawn as horizontal dashed line (secondary)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Figure configuration | FIGURE_DPI=150, FIGURE_FORMAT="png", COLORS dict, threshold annotation values |
| C-7-2 | Figure output path config | H_M3_FIGURES_DIR resolved from _H_M3_DIR anchor in config.py |
