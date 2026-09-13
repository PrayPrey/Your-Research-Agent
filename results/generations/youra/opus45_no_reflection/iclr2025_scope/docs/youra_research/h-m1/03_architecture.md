# Architecture: H-M1 (Attention Entropy Analysis)

**Hypothesis:** Phi-1.5 attention exhibits extrapolation artifacts at 16K-32K sequence lengths (MECHANISM, analysis-only)

Applied: No relevant KB pattern found (diffusers/xDiT results unrelated) — design follows PRD/experiment brief spec directly.

## Codebase Analysis (Serena)

**Project Type**: green-field (analysis experiment)
**Status**: green-field - no existing code to analyze/modify
**Analyzed Path**: N/A
**Findings**: Reviewed H-E1 `03_architecture.md` for reference only (not code-verified, no `base_hypothesis_folder/code/` provided). H-E1 pattern for C4 streaming dataloader (`get_dataloader`, `tokenize_batch`) is reused conceptually but re-implemented here for length-filtered/truncated docs since requirements differ (filter ≥32K tokens, truncate to 5 fixed lengths vs fixed seq_len training loader).

---

## File Organization

- `code/config.py` — fixed analysis config (dataclass)
- `code/data.py` — C4 streaming loader with long-doc filter + multi-length truncation
- `code/model.py` — Phi-1.5 loader wrapper with attention extraction
- `code/metrics.py` — entropy + sparsity computation
- `code/analysis.py` — run pipeline across 5 lengths × 3 layers × 500 docs, aggregate stats
- `code/visualize.py` — all required figures
- `code/main.py` — orchestration entrypoint
- `figures/` — output plots
- `results/` — aggregated JSON/CSV stats

---

## Modules

### Config (`code/config.py`)

**Dependencies**: None

```python
@dataclass
class AnalysisConfig:
    model_name: str = "microsoft/phi-1_5"
    dataset_name: str = "allenai/c4"
    dataset_config: str = "en"
    dataset_split: str = "validation"
    target_lengths: List[int] = field(default_factory=lambda: [2048, 4096, 8192, 16384, 32768])
    middle_layers: List[int] = field(default_factory=lambda: [8, 12, 16])
    num_samples: int = 500
    min_doc_tokens: int = 32768
    top_k: int = 32
    entropy_clamp_min: float = 1e-10
    seed: int = 42
    output_dir: str = "results"
    figures_dir: str = "figures"
```

### Data (`code/data.py`)

**Dependencies**: Config

```python
def get_long_documents(config: AnalysisConfig, tokenizer) -> List[str]: ...
    # streams C4 validation, filters len(tokens) >= min_doc_tokens, takes num_samples, seeded order
def truncate_to_length(text: str, tokenizer, length: int) -> dict: ...
    # returns tokenizer output truncated to `length`, input_ids/attention_mask
```

### Model (`code/model.py`)

**Dependencies**: Config

```python
def load_model_and_tokenizer(config: AnalysisConfig) -> Tuple[nn.Module, "Tokenizer"]: ...
    # AutoModelForCausalLM.from_pretrained(..., trust_remote_code=True, torch_dtype=fp16,
    #   device_map="auto", output_attentions=True)

def extract_attentions(model, tokens: dict, middle_layers: List[int]) -> Dict[int, Tensor]: ...
    # runs forward(output_attentions=True), returns {layer_idx: attn (1,heads,seq,seq)}

def verify_attention_valid(attn: Tensor) -> None: ...
    # asserts finite, non-negative, rows sum to 1.0 (atol=1e-5)
```

### Metrics (`code/metrics.py`)

**Dependencies**: None

```python
def compute_entropy(attention_weights: Tensor, clamp_min: float = 1e-10) -> Tensor: ...
    # H = -sum(p*log(p)) dim=-1 -> (batch, heads, seq_len)

def compute_sparsity(attention_weights: Tensor, top_k: int = 32) -> Tensor: ...
    # topk mass fraction -> (batch, heads, seq_len)

def aggregate_stats(values: List[float]) -> dict: ...
    # {"mean", "std", "ci95_lo", "ci95_hi", "n"}

def entropy_change_pct(entropy_a: float, entropy_b: float) -> float: ...
    # (b - a) / a

def find_inflection_point(lengths: List[int], entropies: List[float]) -> int: ...
    # second derivative of entropy vs log(length), returns length index of max curvature
```

### Analysis Pipeline (`code/analysis.py`)

**Dependencies**: Config, Data, Model, Metrics

```python
def run_analysis(config: AnalysisConfig) -> dict: ...
    # for length in target_lengths:
    #   for doc in documents: truncate, forward pass, extract_attentions(middle_layers)
    #     per layer: compute_entropy, compute_sparsity -> append to accumulators
    #   aggregate_stats per (length, layer)
    # returns results[length][layer] = {entropy: {...}, sparsity: {...}}

def compute_gate_metrics(results: dict) -> dict: ...
    # entropy_change_pct(2048, 16384), pass/fail vs >20% threshold

def save_results(results: dict, gate_metrics: dict, config: AnalysisConfig) -> None: ...
    # writes JSON to output_dir
```

### Visualization (`code/visualize.py`)

**Dependencies**: Analysis (results dict)

```python
def plot_gate_bar_chart(results: dict, out_dir: str) -> None: ...
    # entropy at 2K vs 16K vs 32K bar chart (mandatory)

def plot_entropy_vs_length(results: dict, out_dir: str) -> None: ...
    # line plot, log-scale x-axis, per-layer lines

def plot_layer_length_heatmap(results: dict, out_dir: str) -> None: ...
    # layers x lengths entropy heatmap

def plot_sparsity_boxplots(results: dict, out_dir: str) -> None: ...
    # box plot per length

def plot_attention_samples(attn_2k: Tensor, attn_32k: Tensor, out_dir: str) -> None: ...
    # qualitative attention matrix comparison
```

### Main (`code/main.py`)

**Dependencies**: All modules

```python
def main() -> None: ...
    # load config, model/tokenizer, documents, run_analysis, compute_gate_metrics,
    # save_results, generate all figures, print PASS/FAIL summary
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + C4 streaming/filter pipeline | AnalysisConfig, filter ≥32K token docs, seeded sample of 500 | 8 | 2+2+2+2 |
| A-2 | Model loading + attention extraction | Load Phi-1.5 fp16/device_map, extract layers 8/12/16, validate normalization | 9 | 2+2+2+3 |
| A-3 | Multi-length truncation handling | Truncate docs to 5 target lengths, handle 32K memory constraints | 7 | 2+2+2+1 |
| A-4 | Entropy computation module | H = -sum(p*log(p)), clamp, per-position/layer aggregation | 6 | 1+1+2+2 |
| A-5 | Sparsity computation module | Top-k=32 mass fraction, per-layer aggregation | 5 | 1+1+2+1 |
| A-6 | Statistical analysis (CI, trend, inflection) | 95% CI, entropy change %, second-derivative inflection point | 9 | 2+2+3+2 |
| A-7 | Analysis pipeline orchestration | Loop 500 docs x 5 lengths x 3 layers, forward pass, accumulate | 12 | 3+3+3+3 |
| A-8 | Gate metric + results aggregation | Compute >20% gate check, save JSON results | 6 | 1+2+1+2 |
| A-9 | Visualization suite | 4 required figures + optional attention sample comparison | 10 | 3+2+2+3 |
| A-10 | Main orchestration + PASS/FAIL summary | Wire all modules end-to-end, print/report gate result | 6 | 2+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-6, A-7, A-8], Low(4-8): [A-1, A-3, A-4, A-5, A-9, A-10]
