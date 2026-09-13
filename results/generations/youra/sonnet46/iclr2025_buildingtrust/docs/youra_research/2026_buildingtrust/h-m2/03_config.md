# H-M2 Configuration: Pre-Softmax Logit Margin Inflation

Applied: N/A — KB contains only diffusion model content (diffusers, consistency models, SD-XL). No applicable patterns for statistical calibration experiment configs.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1 and h-m1)
**Status**: Serena MCP unavailable (no active project); config files read directly via file tool
**Config Files Found**:
- `/h-m1/code/config.py` — module-level constants (no dataclass), path anchoring pattern
- `/h-e1/code/calibration_analysis.py` — `MODEL_REGISTRY`, `CALIBRATION_CONFIG`, `GATE_CONFIG` dicts
**Pattern Used**: Module-level constants dict (h-m1 style) — extended with dataclasses for structured sub-configs

**Verified field names from actual code**:
- h-m1: `H_E1_RESULTS_DIR`, `H_E1_CODE_DIR`, `GATE_THRESHOLD`, `BASE_SIZES`, `SEED`, `FIGURE_DPI`, `LMEVAL_NUM_FEWSHOT`, `LMEVAL_TIMEOUT_SECONDS`
- h-e1: `MODEL_REGISTRY` keys use `"{size}-{alignment}"` format (e.g. `"1.4b-base"`, `"1.4b-sft"`), `n_bootstrap=1000`, `seed=42`

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual h-m1/code/config.py)

```python
# Verified field names from actual h-m1 code
_CODE_DIR = Path(__file__).parent.resolve()   # anchoring pattern (inherited)
H_E1_RESULTS_DIR: str      # str(_H_E1_DIR / "code" / "results")
H_E1_CODE_DIR: str         # str(_H_E1_DIR / "code")
H_E1_VALIDATION_PATH: str  # str(_H_E1_DIR / "04_validation.md")
SEED: int = 42
FIGURE_DPI: int = 150
LMEVAL_NUM_FEWSHOT: int = 0   # NOTE: h-m1 uses 0; h-m2 PRD requires 4 (see override below)
LMEVAL_TIMEOUT_SECONDS: int = 7200
```

### Model Registry Keys (From Actual h-e1/code/calibration_analysis.py)

```python
# h-e1 MODEL_REGISTRY key format: "{size}-{alignment}"
# h-m2 uses same key format for compatibility with load_lmeval_samples()
MODEL_REGISTRY = {
    "1.4b-base": "EleutherAI/pythia-1.4b",
    "2.8b-base": "EleutherAI/pythia-2.8b",
    "6.9b-base": "EleutherAI/pythia-6.9b",
    "1.4b-sft":  "lomahony/pythia-1.4b-deduped-tldr",   # PRD Risk R1 fallback IDs
    "1.4b-dpo":  "Leogrin/pythia-1.4b-sft-tldr-dpo",
    "1.4b-ppo":  "usvsnsp/pythia-1.4b-sft-tldr-ppo",
    "2.8b-sft":  "lomahony/pythia-2.8b-deduped-tldr",
    "2.8b-dpo":  "Leogrin/pythia-2.8b-sft-tldr-dpo",
    "2.8b-ppo":  "usvsnsp/pythia-2.8b-sft-tldr-ppo",
    "6.9b-sft":  "lomahony/pythia-6.9b-deduped-tldr",
    "6.9b-dpo":  "Leogrin/pythia-6.9b-sft-tldr-dpo",
    "6.9b-ppo":  "usvsnsp/pythia-6.9b-sft-tldr-ppo",
}
```

**Note**: h-m2 PRD specifies tldr-series HF IDs (different from h-e1 which uses helpful-sft/hh-dpo series). The h-m2 MODEL_REGISTRY above uses the PRD-specified IDs. `load_lmeval_samples(model_id, results_dir)` in h-e1 globs by model_id so keys must match the actual result directory names.

---

## A-2: Path A Data Loader [Complexity: 10, Budget: Medium]

Applied: N/A

### Configuration (Python — module constants in config.py)

```python
# h-m2/code/config.py  (full file)
"""
config.py — H-M2 Pre-Softmax Logit Margin Inflation
Single fixed config: paths, constants, model registry.
"""
from pathlib import Path

# ── Directory anchoring (same pattern as h-m1/code/config.py) ─────────────────
_CODE_DIR = Path(__file__).parent.resolve()
_H_M2_DIR = _CODE_DIR.parent
_H_E1_DIR = _H_M2_DIR.parent / "h-e1"
_H_M1_DIR = _H_M2_DIR.parent / "h-m1"

# ── External paths (h-e1 artifacts) ──────────────────────────────────────────
H_E1_RESULTS_DIR: str = str(_H_E1_DIR / "code" / "results")
H_E1_CODE_DIR: str = str(_H_E1_DIR / "code")
H_E1_VALIDATION_PATH: str = str(_H_E1_DIR / "04_validation.md")

# ── H-M2 output paths ─────────────────────────────────────────────────────────
H_M2_RESULTS_DIR: str = str(_H_M2_DIR / "results")
H_M2_FIGURES_DIR: str = str(_H_M2_DIR / "figures")
H_M2_REPORT_PATH: str = str(_H_M2_DIR / "04_validation.md")
H_M2_EXPERIMENT_RESULTS_JSON: str = str(_H_M2_DIR / "experiment_results.json")
VERIFICATION_STATE_PATH: str = str(_H_M2_DIR.parent / "verification_state.yaml")

# ── Gate configuration ────────────────────────────────────────────────────────
GATE_TYPE: str = "SHOULD_WORK"
MIN_PPO_SIZES_PASSING: int = 2       # >= 2/3 PPO sizes must pass
N_BOOTSTRAP: int = 1000
SEED: int = 42
SIZES: list = ["1.4b", "2.8b", "6.9b"]
ALIGNMENTS: list = ["sft", "dpo", "ppo"]
N_ITEMS_EXPECTED: int = 14042        # MMLU full test set

# ── lm-eval Path B configuration ──────────────────────────────────────────────
LMEVAL_TASKS: list = ["mmlu"]
LMEVAL_NUM_FEWSHOT: int = 4          # Non-standard vs h-m1 (0): PRD requires 4-shot for MMLU
LMEVAL_BATCH_SIZE: str = "auto"
LMEVAL_LOG_SAMPLES: bool = True      # Required for per-item logprob extraction
LMEVAL_TIMEOUT_SECONDS: int = 7200

# ── Figure configuration ───────────────────────────────────────────────────────
FIGURE_DPI: int = 150                # Inherited from h-m1; PRD requests 300 — see FigureConfig
FIGURE_FORMAT: str = "png"

# ── Model Registry (12 models: 3 sizes × 4 alignments) ────────────────────────
# Key format: "{size}-{alignment}" — matches h-e1 load_lmeval_samples() glob pattern
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

BASE_MODEL_KEYS: list = [f"{s}-base" for s in SIZES]
ALIGNED_MODEL_KEYS: list = [f"{s}-{a}" for s in SIZES for a in ALIGNMENTS]
ALL_MODEL_KEYS: list = BASE_MODEL_KEYS + ALIGNED_MODEL_KEYS
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Path anchor verification | Verify _H_E1_DIR resolves correctly relative to code/ |
| C-2-2 | Model key format | Confirm "{size}-{alignment}" keys match h-e1 results dir structure |
| C-2-3 | N_ITEMS_EXPECTED constant | 14042 for shape validation in load_data.py |
| C-2-4 | Path B lm-eval args | LMEVAL_NUM_FEWSHOT=4 (non-standard; h-m1 uses 0, h-m2 PRD requires 4-shot) |

---

## A-7: Figure 1 (Gate Chart) [Complexity: 9, Budget: Medium]

Applied: N/A

### Configuration (Python dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class FigureConfig:
    dpi: int = 150                          # Inherited from h-m1; use 300 for publication quality
    figsize_bar: tuple = (12, 6)            # Figure 1 grouped bar chart
    figsize_violin: tuple = (10, 6)         # Figure 2 violin plot
    figsize_scatter: tuple = (8, 6)         # Figure 3 scatter
    figsize_heatmap: tuple = (8, 6)         # Figure 4 heatmap
    figsize_cdf: tuple = (8, 6)             # Figure 5 CDF
    colors: dict = field(default_factory=lambda: {
        "ppo": "red",
        "dpo": "orange",
        "sft": "blue",
        "base": "gray",
    })
    output_format: str = "png"
    bar_width: float = 0.25                 # Width per group bar in Figure 1
    zero_line_style: str = "--"             # Dashed zero reference line in Figure 1
    zero_line_color: str = "black"
    zero_line_alpha: float = 0.5
    figure_01_filename: str = "figure_01_delta_margin_gate.png"
    figure_02_filename: str = "figure_02_margin_violin.png"
    figure_03_filename: str = "figure_03_delta_margin_vs_delta_ece.png"
    figure_04_filename: str = "figure_04_gradient_ordering_heatmap.png"
    figure_05_filename: str = "figure_05_margin_cdf.png"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Color mapping | PPO=red, DPO=orange, SFT=blue — consistent across all 5 figures |
| C-7-2 | Bar chart geometry | figsize_bar=(12,6), bar_width=0.25 for 3 groups × 3 sizes |

---

## A-9: Validation Report [Complexity: 9, Budget: Medium]

Applied: N/A

### Configuration (Python dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class ReportConfig:
    output_path: str = ""                   # Set from H_M2_REPORT_PATH at runtime
    hypothesis_id: str = "h-m2"
    hypothesis_type: str = "MECHANISM"
    gate_type: str = "SHOULD_WORK"
    required_sections: list = field(default_factory=lambda: [
        "gate_result",
        "delta_margin_table",        # 9 Δmargin values (3 sizes × 3 alignments)
        "bootstrap_ci_ppo",          # 3 CI lower bounds for PPO
        "gradient_ordering_stats",   # Wilcoxon p-values
        "execution_path",            # "Path A" or "Path B"
        "key_findings",              # >= 3 findings
        "figure_paths",
        "exploration_notes",         # populated only if gate FAIL
    ])
    min_key_findings: int = 3
    date_format: str = "%Y-%m-%d"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Required sections list | 8 sections; exploration_notes populated only on FAIL |
| C-9-2 | delta_margin_table format | 9 values keyed as "{alignment}_{size}" e.g. "ppo_1.4b" |

---

## A-11: Main Orchestrator [Complexity: 10, Budget: Medium]

Applied: N/A

### Configuration (Python dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-m2"
    hypothesis_folder: str = ""             # Set from _H_M2_DIR at runtime
    h_e1_results_dir: str = ""             # Set from H_E1_RESULTS_DIR at runtime
    h_m2_results_dir: str = ""             # Set from H_M2_RESULTS_DIR at runtime
    model_registry: dict = field(default_factory=dict)   # Populated from MODEL_REGISTRY
    bootstrap_n: int = 1000
    bootstrap_seed: int = 42
    n_items_expected: int = 14042
    gate_min_sizes_passing: int = 2
    figures_dir: str = ""                  # Set from H_M2_FIGURES_DIR at runtime
    validation_report_path: str = ""       # Set from H_M2_REPORT_PATH at runtime
    smoke_test: bool = False               # If True: run on 10 items only
    smoke_test_n_items: int = 10           # Non-standard: minimal for CI validation
    device: str = "cuda"


@dataclass
class MarginConfig:
    n_choices: int = 4                     # MMLU answer choices
    size_labels: list = field(default_factory=lambda: ["1.4b", "2.8b", "6.9b"])
    alignment_methods: list = field(default_factory=lambda: ["sft", "dpo", "ppo"])
    wilcoxon_alternative: str = "greater"  # One-sided: PPO > DPO, DPO > SFT
    ci_percentiles: tuple = (2.5, 97.5)   # Bootstrap 95% CI bounds
    gate_threshold_delta: float = 0.0      # Δmargin must be > 0
    gate_threshold_ci_lower: float = 0.0   # CI lower must be > 0
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-11-1 | ExperimentConfig runtime population | hypothesis_folder, h_e1_results_dir etc. set from config.py constants |
| C-11-2 | smoke_test flag | smoke_test_n_items=10 enables fast CI/validation run |
| C-11-3 | MarginConfig defaults | wilcoxon_alternative="greater" for one-sided test; ci_percentiles=(2.5, 97.5) |

---

## A-12: Integration Test [Complexity: 9, Budget: Medium]

Applied: N/A

### Configuration (Python — hardcoded dict)

```python
SMOKE_TEST_CONFIG = {
    "n_items": 10,
    "seed": 42,
    "expected_output_files": [
        "figure_01_delta_margin_gate.png",
        "figure_02_margin_violin.png",
        "figure_03_delta_margin_vs_delta_ece.png",
        "figure_04_gradient_ordering_heatmap.png",
        "figure_05_margin_cdf.png",
        "04_validation.md",
        "experiment_results.json",
    ],
    "required_report_sections": [
        "gate_result",
        "delta_margin_table",
        "bootstrap_ci_ppo",
        "gradient_ordering_stats",
        "execution_path",
        "key_findings",
        "figure_paths",
    ],
    "gate_result_values": ["PASS", "FAIL"],   # either is valid for smoke test
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-12-1 | Expected output file list | 5 figures + 04_validation.md + experiment_results.json |
| C-12-2 | Smoke test n_items=10 | Subsample for speed; gate result not meaningful at n=10 |

---

## YAML Config Schema

```yaml
# h-m2/config.yaml — mirrors all dataclasses above
experiment:
  hypothesis_id: "h-m2"
  bootstrap_n: 1000
  bootstrap_seed: 42
  n_items_expected: 14042
  gate_min_sizes_passing: 2
  smoke_test: false
  smoke_test_n_items: 10
  device: "cuda"

margin:
  n_choices: 4
  size_labels: ["1.4b", "2.8b", "6.9b"]
  alignment_methods: ["sft", "dpo", "ppo"]
  wilcoxon_alternative: "greater"
  ci_percentiles: [2.5, 97.5]
  gate_threshold_delta: 0.0
  gate_threshold_ci_lower: 0.0

figure:
  dpi: 150
  figsize_bar: [12, 6]
  figsize_violin: [10, 6]
  figsize_scatter: [8, 6]
  figsize_heatmap: [8, 6]
  figsize_cdf: [8, 6]
  output_format: "png"
  bar_width: 0.25
  colors:
    ppo: "red"
    dpo: "orange"
    sft: "blue"
    base: "gray"

report:
  hypothesis_id: "h-m2"
  hypothesis_type: "MECHANISM"
  gate_type: "SHOULD_WORK"
  min_key_findings: 3

lmeval:
  tasks: ["mmlu"]
  num_fewshot: 4
  batch_size: "auto"
  log_samples: true
  timeout_seconds: 7200

model_registry:
  "1.4b-base": "EleutherAI/pythia-1.4b"
  "2.8b-base": "EleutherAI/pythia-2.8b"
  "6.9b-base": "EleutherAI/pythia-6.9b"
  "1.4b-sft":  "lomahony/pythia-1.4b-deduped-tldr"
  "1.4b-dpo":  "Leogrin/pythia-1.4b-sft-tldr-dpo"
  "1.4b-ppo":  "usvsnsp/pythia-1.4b-sft-tldr-ppo"
  "2.8b-sft":  "lomahony/pythia-2.8b-deduped-tldr"
  "2.8b-dpo":  "Leogrin/pythia-2.8b-sft-tldr-dpo"
  "2.8b-ppo":  "usvsnsp/pythia-2.8b-sft-tldr-ppo"
  "6.9b-sft":  "lomahony/pythia-6.9b-deduped-tldr"
  "6.9b-dpo":  "Leogrin/pythia-6.9b-sft-tldr-dpo"
  "6.9b-ppo":  "usvsnsp/pythia-6.9b-sft-tldr-ppo"
```

---

## Summary of Non-Standard Values

| Field | Value | Reason |
|-------|-------|--------|
| `LMEVAL_NUM_FEWSHOT` | 4 | H-M2 PRD requires 4-shot MMLU; h-m1 used 0-shot (different task design) |
| `smoke_test_n_items` | 10 | Minimal subsample for fast integration validation only |
| `wilcoxon_alternative` | "greater" | One-sided test: PPO > DPO, DPO > SFT directional hypothesis |
| `MODEL_REGISTRY` keys | tldr-series | H-M2 PRD uses tldr-finetuned fallback ladder; differs from h-e1 helpful-sft/hh series |
