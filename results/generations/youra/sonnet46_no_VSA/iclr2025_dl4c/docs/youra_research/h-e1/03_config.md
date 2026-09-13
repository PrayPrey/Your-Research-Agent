# Configuration: H-E1
# Code Embedding Distribution Distinctiveness Analysis

**Hypothesis Type**: EXISTENCE (PoC)
**Phase**: 3 — Configuration Design

Applied: HuggingFace argparse inline-defaults pattern
Applied: YAML flat config pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase — green-field implementation
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict + YAML file + argparse CLI schema

---

## C-E4-1: Experiment Configuration Schema [Complexity: 10, Budget: 1]

### Hyperparameters

| Parameter | Type | Default | Rationale |
|-----------|------|---------|-----------|
| `batch_size` | int | 32 | Standard HF inference batch; reduce to 8 on OOM |
| `device` | str | "cuda" | Auto-detected; falls back to "cpu" |
| `seed` | int | 42 | Reproducible Equal-mix sampling (164 from MBPP-train, LeetCode) |
| `max_length_codebert` | int | 512 | CodeBERT hard max per tokenizer |
| `max_length_minilm` | int | 256 | all-MiniLM-L6-v2 effective practical max (model supports 256) |
| `gate_threshold` | float | 0.95 | Gate: any pairwise mean cosine sim < 0.95 satisfies EXISTENCE |
| `equal_mix_per_source` | int | 164 | Matches HumanEval-train full size (164 problems) for balanced mix |
| `figures_dir` | str | "docs/youra_research/h-e1/figures" | Output path for all saved figures |
| `skip_tsne` | bool | False | t-SNE is slow; set True to skip optional visualization |
| `skip_histograms` | bool | False | Per-source histograms optional; set True to skip |

### Dataset Identifiers

| Corpus Name | HuggingFace Dataset ID | Config Name | Split | Role |
|-------------|----------------------|-------------|-------|------|
| `humaneval_train` | `openai/openai_humaneval` | None | `test` | SFT source (all 164) |
| `mbpp_train` | `google-research-datasets/mbpp` | `sanitized` | `train` | SFT source (~374, seed-sampled) |
| `leetcode` | `newfacade/LeetCodeDataset` | None | `train` | SFT source (~2500, seed-sampled) |
| `humaneval_plus` | `evalplus/humanevalplus` | None | `test` | Test benchmark (164) |
| `mbpp_plus` | `evalplus/mbppplus` | None | `test` | Test benchmark (378) |

### Model Identifiers

```python
MODELS = {
    "codebert": "microsoft/codebert-base",       # 768-dim output
    "minilm":   "sentence-transformers/all-MiniLM-L6-v2",  # 384-dim output
}
```

### Inline Config Dict (run_experiment.py)

```python
CONFIG = {
    "batch_size": 32,
    "device": "cuda",
    "seed": 42,
    "max_length_codebert": 512,
    "max_length_minilm": 256,
    "gate_threshold": 0.95,
    "equal_mix_per_source": 164,
    "figures_dir": "docs/youra_research/h-e1/figures",
    "skip_tsne": False,
    "skip_histograms": False,
    "codebert_model_id": "microsoft/codebert-base",
    "minilm_model_id": "sentence-transformers/all-MiniLM-L6-v2",
}
```

### YAML Config File (experiment_config.yaml)

```yaml
batch_size: 32
device: "cuda"
seed: 42
max_length_codebert: 512
max_length_minilm: 256
gate_threshold: 0.95
equal_mix_per_source: 164
figures_dir: "docs/youra_research/h-e1/figures"
skip_tsne: false
skip_histograms: false
codebert_model_id: "microsoft/codebert-base"
minilm_model_id: "sentence-transformers/all-MiniLM-L6-v2"
```

### argparse CLI Schema (run_experiment.py)

```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="H-E1: Code Embedding Distinctiveness Analysis")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-length-codebert", type=int, default=512)
    parser.add_argument("--max-length-minilm", type=int, default=256)
    parser.add_argument("--gate-threshold", type=float, default=0.95)
    parser.add_argument("--equal-mix-per-source", type=int, default=164)
    parser.add_argument("--figures-dir", type=str, default="docs/youra_research/h-e1/figures")
    parser.add_argument("--skip-tsne", action="store_true", default=False)
    parser.add_argument("--skip-histograms", action="store_true", default=False)
    return parser.parse_args()
```

**Device auto-detect pattern** (use in main):
```python
args = parse_args()
if args.device == "cuda" and not torch.cuda.is_available():
    args.device = "cpu"
```

### Expected Output Files

| File | Description |
|------|-------------|
| `figures/heatmap_codebert.png` | 4x2 cosine similarity heatmap, CodeBERT encoder |
| `figures/heatmap_minilm.png` | 4x2 cosine similarity heatmap, MiniLM encoder |
| `figures/hist_codebert.png` | Per-source pairwise similarity histograms, CodeBERT (optional) |
| `figures/hist_minilm.png` | Per-source pairwise similarity histograms, MiniLM (optional) |
| `figures/tsne_codebert.png` | t-SNE 2D projection of all 6 corpora, CodeBERT (optional) |
| `figures/tsne_minilm.png` | t-SNE 2D projection of all 6 corpora, MiniLM (optional) |
| stdout | Gate result: SATISFIED / FAIL + min/max/mean of 16 similarity values |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E4-1 | Experiment Config Schema | Hyperparameters, dataset IDs, model IDs, YAML, CLI args, output files |
