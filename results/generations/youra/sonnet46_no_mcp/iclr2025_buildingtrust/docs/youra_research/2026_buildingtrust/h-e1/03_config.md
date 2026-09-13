# Configuration: H-E1 — Epistemic Reliability as a Latent Dimension

**Hypothesis:** H-E1 (EXISTENCE / MUST_WORK)
**Date:** 2026-04-30
**Tier:** LIGHT

Applied: minimal-flat-structure

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict

---

## 1. config.py — Complete Implementation

```python
# h-e1/code/config.py

# ---------------------------------------------------------------------------
# Model population — 30 open-weight instruction-tuned LLMs
# ---------------------------------------------------------------------------
MODELS: list[dict] = [
    # Llama-2 family
    {"id": "llama2-7b-chat",   "hf_id": "meta-llama/Llama-2-7b-chat-hf",    "params": "7B",  "family": "llama2",   "requires_4bit": False},
    {"id": "llama2-13b-chat",  "hf_id": "meta-llama/Llama-2-13b-chat-hf",   "params": "13B", "family": "llama2",   "requires_4bit": False},
    {"id": "llama2-70b-chat",  "hf_id": "meta-llama/Llama-2-70b-chat-hf",   "params": "70B", "family": "llama2",   "requires_4bit": True},
    # Llama-3 family
    {"id": "llama3-8b-instruct",  "hf_id": "meta-llama/Meta-Llama-3-8B-Instruct",  "params": "7B",  "family": "llama3",   "requires_4bit": False},
    {"id": "llama3-70b-instruct", "hf_id": "meta-llama/Meta-Llama-3-70B-Instruct", "params": "70B", "family": "llama3",   "requires_4bit": True},
    # Mistral family
    {"id": "mistral-7b-instruct-v01",  "hf_id": "mistralai/Mistral-7B-Instruct-v0.1",  "params": "7B",  "family": "mistral",  "requires_4bit": False},
    {"id": "mistral-7b-instruct-v02",  "hf_id": "mistralai/Mistral-7B-Instruct-v0.2",  "params": "7B",  "family": "mistral",  "requires_4bit": False},
    {"id": "mistral-7b-instruct-v03",  "hf_id": "mistralai/Mistral-7B-Instruct-v0.3",  "params": "7B",  "family": "mistral",  "requires_4bit": False},
    {"id": "mixtral-8x7b-instruct",    "hf_id": "mistralai/Mixtral-8x7B-Instruct-v0.1","params": "40B", "family": "mistral",  "requires_4bit": False},
    # Falcon family
    {"id": "falcon-7b-instruct",  "hf_id": "tiiuae/falcon-7b-instruct",   "params": "7B",  "family": "falcon",   "requires_4bit": False},
    {"id": "falcon-40b-instruct", "hf_id": "tiiuae/falcon-40b-instruct",  "params": "40B", "family": "falcon",   "requires_4bit": False},
    # Vicuna family
    {"id": "vicuna-7b-v15",   "hf_id": "lmsys/vicuna-7b-v1.5",    "params": "7B",  "family": "vicuna",   "requires_4bit": False},
    {"id": "vicuna-13b-v15",  "hf_id": "lmsys/vicuna-13b-v1.5",   "params": "13B", "family": "vicuna",   "requires_4bit": False},
    # Zephyr family
    {"id": "zephyr-7b-beta",  "hf_id": "HuggingFaceH4/zephyr-7b-beta",  "params": "7B",  "family": "zephyr",   "requires_4bit": False},
    {"id": "zephyr-7b-alpha", "hf_id": "HuggingFaceH4/zephyr-7b-alpha", "params": "7B",  "family": "zephyr",   "requires_4bit": False},
    # OpenHermes / Nous family
    {"id": "openhermes-25-mistral-7b", "hf_id": "teknium/OpenHermes-2.5-Mistral-7B", "params": "7B", "family": "nous", "requires_4bit": False},
    {"id": "nous-hermes2-mistral-7b",  "hf_id": "NousResearch/Nous-Hermes-2-Mistral-7B-DPO", "params": "7B", "family": "nous", "requires_4bit": False},
    # WizardLM family
    {"id": "wizardlm-13b-v12",  "hf_id": "WizardLM/WizardLM-13B-V1.2",  "params": "13B", "family": "wizardlm", "requires_4bit": False},
    {"id": "wizardlm-70b-v10",  "hf_id": "WizardLM/WizardLM-70B-V1.0",  "params": "70B", "family": "wizardlm", "requires_4bit": True},
    # Qwen family
    {"id": "qwen15-7b-chat",   "hf_id": "Qwen/Qwen1.5-7B-Chat",    "params": "7B",  "family": "qwen",     "requires_4bit": False},
    {"id": "qwen15-14b-chat",  "hf_id": "Qwen/Qwen1.5-14B-Chat",   "params": "13B", "family": "qwen",     "requires_4bit": False},
    {"id": "qwen15-72b-chat",  "hf_id": "Qwen/Qwen1.5-72B-Chat",   "params": "70B", "family": "qwen",     "requires_4bit": True},
    # Yi family
    {"id": "yi-6b-chat",   "hf_id": "01-ai/Yi-6B-Chat",    "params": "7B",  "family": "yi",       "requires_4bit": False},
    {"id": "yi-34b-chat",  "hf_id": "01-ai/Yi-34B-Chat",   "params": "30B", "family": "yi",       "requires_4bit": False},
    # DeepSeek family
    {"id": "deepseek-7b-chat",   "hf_id": "deepseek-ai/deepseek-llm-7b-chat",   "params": "7B",  "family": "deepseek", "requires_4bit": False},
    {"id": "deepseek-67b-chat",  "hf_id": "deepseek-ai/deepseek-llm-67b-chat",  "params": "70B", "family": "deepseek", "requires_4bit": True},
    # Internlm family
    {"id": "internlm2-7b-chat",   "hf_id": "internlm/internlm2-chat-7b",    "params": "7B",  "family": "internlm", "requires_4bit": False},
    {"id": "internlm2-20b-chat",  "hf_id": "internlm/internlm2-chat-20b",   "params": "30B", "family": "internlm", "requires_4bit": False},
    # Phi family
    {"id": "phi2",        "hf_id": "microsoft/phi-2",           "params": "7B",  "family": "phi",      "requires_4bit": False},
    # Solar family
    {"id": "solar-10-7b-instruct", "hf_id": "upstage/SOLAR-10.7B-Instruct-v1.0", "params": "13B", "family": "solar", "requires_4bit": False},
]

# ---------------------------------------------------------------------------
# Evaluation tasks
# ---------------------------------------------------------------------------
TASKS: list[str] = ["mmlu", "truthfulqa_mc1", "adv_glue", "anli_r3", "humaneval"]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
RESULTS_DIR: str = "h-e1/results/"
FIGURES_DIR: str = "h-e1/figures/"

# ---------------------------------------------------------------------------
# Decoding settings
# ---------------------------------------------------------------------------
GREEDY_SEED: int = 42
STOCHASTIC_SEEDS: list[int] = [42, 123, 456]
STOCHASTIC_TEMPERATURE: float = 0.7

# ---------------------------------------------------------------------------
# Calibration settings
# ---------------------------------------------------------------------------
ECE_BINS: int = 10

# ---------------------------------------------------------------------------
# Bootstrap settings
# ---------------------------------------------------------------------------
N_BOOTSTRAP: int = 10000

# ---------------------------------------------------------------------------
# Batch sizes by model size (memory-constrained single GPU)
# ---------------------------------------------------------------------------
BATCH_SIZE: dict = {"7B": 8, "13B": 8, "30B": 4, "40B": 4, "70B": 1}

# ---------------------------------------------------------------------------
# Statistical analysis settings
# ---------------------------------------------------------------------------
INDICATORS: list[str] = ["ECE", "Brier", "TruthfulQA_pct", "AdvGLUE_drop", "ANLI_drop"]
COVARIATE: str = "MMLU_acc"
GATE_PAIRS: list[tuple] = [("ECE", "TruthfulQA_pct"), ("ECE", "AdvGLUE_drop")]
GATE_THRESHOLD: float = 0.40
MIN_MODELS: int = 25  # Minimum valid models to proceed with statistical analysis

# ---------------------------------------------------------------------------
# Factor analysis settings
# ---------------------------------------------------------------------------
N_FACTORS: int = 1
FA_METHOD: str = "ml"       # Maximum likelihood estimation
FA_ROTATION: str = "promax"
TUCKER_CONGRUENCE_THRESHOLD: float = 0.85  # Greedy vs. T=0.7 stability check

# ---------------------------------------------------------------------------
# Visualization settings
# ---------------------------------------------------------------------------
FIGURE_DPI: int = 150
FIGURE_FORMAT: str = "png"

FIGURE_NAMES: dict = {
    "partial_corr_heatmap":    "fig1_partial_corr_heatmap.png",
    "factor_loadings":         "fig2_factor_loadings.png",
    "ece_truthfulqa_scatter":  "fig3_ece_truthfulqa_scatter.png",
    "ece_advglue_scatter":     "fig4_ece_advglue_scatter.png",
    "ece_anli_scatter":        "fig5_ece_anli_scatter.png",
    "loo_roc_curve":           "fig6_loo_roc_curve.png",
}
```

---

## 2. YAML Configuration Schema (experiment_config.yaml)

```yaml
# h-e1/experiment_config.yaml

paths:
  results_dir: "h-e1/results/"    # lm-eval JSON output directory
  figures_dir: "h-e1/figures/"    # saved plot directory

decoding:
  greedy_seed: 42
  stochastic_seeds: [42, 123, 456]
  stochastic_temperature: 0.7

calibration:
  ece_bins: 10    # equal-width bins for ECE computation

bootstrap:
  n_bootstrap: 10000    # BCa bootstrap resamples

batch_sizes:    # per model size class (memory-constrained single GPU)
  "7B": 8
  "13B": 8
  "30B": 4
  "40B": 4
  "70B": 1

statistical_analysis:
  indicators: ["ECE", "Brier", "TruthfulQA_pct", "AdvGLUE_drop", "ANLI_drop"]
  covariate: "MMLU_acc"
  gate_pairs:
    - ["ECE", "TruthfulQA_pct"]
    - ["ECE", "AdvGLUE_drop"]
  gate_threshold: 0.40    # minimum partial rho for success gate
  min_models: 25          # minimum valid models for statistical analysis

factor_analysis:
  n_factors: 1
  method: "ml"            # maximum likelihood estimation
  rotation: "promax"
  tucker_congruence_threshold: 0.85

visualization:
  figure_dpi: 150
  figure_format: "png"
```

---

## 3. Dataclass Definitions

```python
from dataclasses import dataclass, field

@dataclass
class ModelConfig:
    id: str
    hf_id: str
    params: str            # "7B", "13B", "30B", "40B", "70B"
    family: str
    requires_4bit: bool = False

@dataclass
class EvalConfig:
    tasks: list[str] = field(default_factory=lambda: [
        "mmlu", "truthfulqa_mc1", "adv_glue", "anli_r3", "humaneval"
    ])
    greedy_seed: int = 42
    stochastic_seeds: list[int] = field(default_factory=lambda: [42, 123, 456])
    stochastic_temperature: float = 0.7
    batch_sizes: dict = field(default_factory=lambda: {
        "7B": 8, "13B": 8, "30B": 4, "40B": 4, "70B": 1
    })

@dataclass
class StatConfig:
    indicators: list[str] = field(default_factory=lambda: [
        "ECE", "Brier", "TruthfulQA_pct", "AdvGLUE_drop", "ANLI_drop"
    ])
    covariate: str = "MMLU_acc"
    gate_pairs: list[tuple] = field(default_factory=lambda: [
        ("ECE", "TruthfulQA_pct"), ("ECE", "AdvGLUE_drop")
    ])
    gate_threshold: float = 0.40
    n_bootstrap: int = 10000
    min_models: int = 25
    n_factors: int = 1
    fa_method: str = "ml"
    fa_rotation: str = "promax"
    tucker_congruence_threshold: float = 0.85
```

---

## 4. Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E4-1 | MODELS list implementation | Implement complete MODELS list in config.py with all 30 HuggingFace model IDs, parameter counts, family labels, and requires_4bit flags |
| C-E6-1 | Figure output configuration | Implement FIGURE_NAMES dict, FIGURE_DPI, FIGURE_FORMAT; enforce file naming convention for all 6 required figures |

---

## 5. Environment Configuration

### requirements.txt

```
lm-eval==0.4.3
torch==2.2.2
transformers==4.40.2
accelerate==0.29.3
bitsandbytes==0.43.1
netcal==1.3.5
factor-analyzer==0.5.1
scipy==1.13.0
pandas==2.2.2
numpy==1.26.4
matplotlib==3.8.4
seaborn==0.13.2
scikit-learn==1.4.2
pyyaml==6.0.1
```

### Environment Setup

```bash
conda create -n h-e1 python=3.10 -y
conda activate h-e1
pip install -r requirements.txt

# Select single GPU with lowest memory usage
nvidia-smi
export CUDA_VISIBLE_DEVICES=0  # replace with empty GPU id

python main.py
```
