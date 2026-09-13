---
hypothesis: H-E1
type: EXISTENCE (PoC)
tier: LIGHT
date: 2026-08-31
author: yoon303@ust.ac.kr
---

# Config: H-E1 — SMC-NLI Existence Proof

Applied: inference-only flat dataclass pattern (Archon KB unavailable — MCP not active in this context)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new config design, no existing codebase
**Config Files Found**: None — new config
**Pattern Used**: dataclass

---

## Config Groups

### Full `config.py`

```python
from dataclasses import dataclass, field


@dataclass
class DataConfig:
    dataset_name: str = "pminervini/HaluEval"
    dataset_split: str = "qa"
    n_questions: int = 1000       # 500 correct + 500 hallucinated
    seed: int = 42
    stratify: bool = True
    data_path: str = "data/halueval_qa_1000.json"


@dataclass
class LLMConfig:
    model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    temperature: float = 0.7
    top_p: float = 0.9
    max_new_tokens: int = 50
    n_samples: int = 10
    samples_path: str = "data/llama_samples.json"


@dataclass
class NLIConfig:
    model_id: str = "cross-encoder/nli-deberta-v3-large"
    batch_size: int = 16
    max_length: int = 512
    # Non-standard: label order matches HuggingFace cross-encoder output index
    label_map: dict = field(default_factory=lambda: {
        "contradiction": 0,
        "entailment": 1,
        "neutral": 2,
    })


@dataclass
class EmbedConfig:
    model_id: str = "sentence-transformers/all-mpnet-base-v2"
    batch_size: int = 32


@dataclass
class EvalConfig:
    auroc_gate_threshold: float = 0.60
    std_threshold: float = 0.05
    output_path: str = "results/h-e1/results.json"


@dataclass
class VizConfig:
    output_dir: str = "docs/youra_research/h-e1/figures/"
    dpi: int = 150
    figsize: tuple = (8, 5)
    color_correct: str = "#2196F3"      # blue
    color_hallucinated: str = "#F44336" # red
    fig_bar: str = "auroc_bar.png"
    fig_hist: str = "score_dist.png"
    fig_roc: str = "roc_curve.png"
    fig_scatter: str = "nli_vs_embed_scatter.png"


@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    nli: NLIConfig = field(default_factory=NLIConfig)
    embed: EmbedConfig = field(default_factory=EmbedConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
    viz: VizConfig = field(default_factory=VizConfig)
```

---

## YAML Schema (`experiment.yaml`)

```yaml
data:
  dataset_name: "pminervini/HaluEval"
  dataset_split: "qa"
  n_questions: 1000
  seed: 42
  stratify: true
  data_path: "data/halueval_qa_1000.json"

llm:
  model_id: "meta-llama/Meta-Llama-3-8B-Instruct"
  temperature: 0.7
  top_p: 0.9
  max_new_tokens: 50
  n_samples: 10
  samples_path: "data/llama_samples.json"

nli:
  model_id: "cross-encoder/nli-deberta-v3-large"
  batch_size: 16
  max_length: 512
  label_map:
    contradiction: 0
    entailment: 1
    neutral: 2

embed:
  model_id: "sentence-transformers/all-mpnet-base-v2"
  batch_size: 32

eval:
  auroc_gate_threshold: 0.60
  std_threshold: 0.05
  output_path: "results/h-e1/results.json"

viz:
  output_dir: "docs/youra_research/h-e1/figures/"
  dpi: 150
  figsize: [8, 5]
  color_correct: "#2196F3"
  color_hallucinated: "#F44336"
  fig_bar: "auroc_bar.png"
  fig_hist: "score_dist.png"
  fig_roc: "roc_curve.png"
  fig_scatter: "nli_vs_embed_scatter.png"
```

---

## E-6: Evaluation + Visualization [Complexity: 9, Budget: 2]

Applied: inference-only flat dataclass pattern

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | EvalConfig | AUROC gate threshold (0.60), std threshold (0.05), results output path |
| C-6-2 | VizConfig | Figure output dir, DPI=150, figsize, color palette, 4 figure filenames |
