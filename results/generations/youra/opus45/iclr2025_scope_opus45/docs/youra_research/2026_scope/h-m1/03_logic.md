# Logic: H-M1 — SSM Eigenvalue Memory Horizon Empirical Validation

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-E1)
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/20260327_scope/h-e1/code/model.py`
**Relevant Symbols**:
- `MambaProbe.__init__(self, config: ExperimentConfig) -> None`
- `MambaProbe.load_model(self, model_id: str) -> None`  ← **param is `model_id`, not implicit**
- `MambaProbe.extract_layer_A_log(self) -> list[Tensor]`  ← returns `list[Tensor]`, not `dict`
- `MambaProbe.compute_h_spec(self, input_ids: Optional[Tensor] = None) -> float`  ← returns `float`
- `MambaProbe.get_per_layer_h_spec(self) -> list[float]`
- `MambaProbe.get_per_layer_lambda_max(self) -> list[float]`
- `MambaProbe.unload(self) -> None`

---

## External Dependencies API (Base Hypothesis H-E1)

Signatures verified from `/h-e1/code/model.py` (actual code, NOT spec):

```python
# From: h-e1/code/model.py (ACTUAL CODE)
class MambaProbe:
    def __init__(self, config: ExperimentConfig) -> None: ...

    def load_model(self, model_id: str) -> None:
        # Loads MambaLMHeadModel.from_pretrained(model_id, dtype=..., device=...)
        ...

    def extract_layer_A_log(self) -> list[Tensor]:
        # Returns list of A_log tensors per layer, each [d_inner, d_state]
        ...

    def compute_h_spec(self, input_ids: Optional[Tensor] = None) -> float:
        # Returns scalar H_spec = 1/min(exp(A_log)) across all layers
        ...

    def get_per_layer_h_spec(self) -> list[float]:
        # Returns list of per-layer H_spec values
        ...

    def get_per_layer_lambda_max(self) -> list[float]:
        # Returns list of slowest discrete eigenvalue per layer
        ...

    def unload(self) -> None: ...
```

**Critical notes from actual code**:
- `load_model` takes `model_id: str` as positional arg (call: `probe.load_model(config.model_id)`)
- `compute_h_spec` returns `float` (not dict)
- `extract_layer_A_log` returns `list[Tensor]` (not dict keyed by name)
- H_spec formula: `h_spec = 1.0 / min_exp_a_log` where `min_exp_a_log = exp(min(A_log))`

---

## A-4: PerplexityEvaluator [Complexity: 10, Budget: 2]

**Applied**: Standard PyTorch cross-entropy perplexity pattern

### API Signatures

```python
class PerplexityEvaluator:
    """Measures perplexity at varying context lengths on Mamba model."""

    def __init__(
        self,
        model,                    # MambaLMHeadModel instance
        tokenizer,                # AutoTokenizer instance
        device: str = "cuda",
        dtype: str = "float32",
    ) -> None: ...

    def compute_perplexity(
        self,
        input_ids: Tensor,        # [B, L] input token ids
    ) -> float:
        # Returns scalar perplexity = exp(mean cross-entropy)
        # shift_logits: [B, L-1, V]; shift_labels: [B, L-1]
        ...

    def evaluate_at_context_length(
        self,
        sequences: Tensor,        # [N, max_len] full sequences
        context_length: int,
    ) -> float:
        # Truncates to sequences[:, -context_length:], averages PPL over N sequences
        # Returns scalar mean perplexity
        ...

    def run_context_sweep(
        self,
        sequences: Tensor,        # [N, max_len]
        context_lengths: list[int],
    ) -> dict[int, float]:
        # Returns {context_length: mean_perplexity} for each length
        ...

    def compute_degradation_ratio(
        self,
        ppl_curve: dict[int, float],
        h_spec: float,
    ) -> float:
        # ratio = mean(PPL where ctx < h_spec) / mean(PPL where ctx >= h_spec)
        # Returns 1.0 if either side is empty
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| sequences | [N, max_len] | N=1000, max_len=1024 |
| input_ids (batched) | [B, L] | B=1 for sequential eval |
| shift_logits | [B*(L-1), V] | flattened for cross_entropy |
| shift_labels | [B*(L-1)] | flattened targets |

### Pseudo-code (compute_perplexity)

```
1. with torch.no_grad():
2.     outputs = model(input_ids)
3.     logits = outputs.logits  # [B, L, V]
4.     shift_logits = logits[:, :-1, :].contiguous().view(-1, V)
5.     shift_labels = input_ids[:, 1:].contiguous().view(-1)
6.     loss = F.cross_entropy(shift_logits, shift_labels, reduction='mean')
7.     return exp(loss).item()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | compute_perplexity + evaluate_at_context_length | Single-sequence PPL + context truncation |
| L-4-2 | run_context_sweep + compute_degradation_ratio | Sweep loop + ratio computation |

---

## A-6: Context Sweep Experiment [Complexity: 10, Budget: 2]

**Applied**: Inference-only PoC evaluation pattern

### API Signatures

```python
# In evaluate.py

def load_wikitext103(config: ExperimentConfig):
    # Returns HuggingFace Dataset (validation split)
    ...

def prepare_eval_sequences(
    dataset,
    tokenizer,
    config: ExperimentConfig,
) -> Tensor:
    # Concatenates all tokens, chunks to non-overlapping [max_seq_length] windows
    # Returns Tensor[num_eval_sequences, max_seq_length]
    ...

def compute_context_lengths(
    h_spec: float,
    multipliers: tuple,           # e.g. (0.1, 0.25, 0.5, 1.0, 2.0, 4.0)
    min_tokens: int = 16,
) -> list[int]:
    # Returns [max(min_tokens, int(h_spec * m)) for m in multipliers]
    ...

def save_results(results: dict, path: str) -> None: ...

def generate_figures(
    ppl_curve: dict[int, float],
    h_spec: float,
    degradation_ratio: float,
    per_layer_h_specs: list[float],
    output_dir: str,
) -> None:
    # Figure 1: PPL vs context length (line plot, vertical line at h_spec)
    # Figure 2: Gate metrics bar chart (degradation_ratio vs threshold 1.1)
    # Optional: per-layer eigenvalue distribution, decay rate profile
    ...

# In run_experiment.py

def main(config: ExperimentConfig) -> dict:
    # Returns results dict with keys:
    # h_spec, per_layer_h_specs, per_layer_lambda_max,
    # ppl_curve, degradation_ratio, gate_pass, baseline_ppl
    ...
```

### Pseudo-code (main)

```
1. dataset = load_wikitext103(config)
2. tokenizer = AutoTokenizer.from_pretrained(config.tokenizer_id)
3. sequences = prepare_eval_sequences(dataset, tokenizer, config)  # [1000, 1024]

4. probe = MambaProbe(config)
5. probe.load_model(config.model_id)            # ← use model_id positional arg
6. h_spec = probe.compute_h_spec()             # float ~256.18
7. per_layer_h_specs = probe.get_per_layer_h_spec()
8. per_layer_lambda_max = probe.get_per_layer_lambda_max()

9. evaluator = PerplexityEvaluator(probe.model, tokenizer, config.device, config.dtype)
10. context_lengths = compute_context_lengths(h_spec, config.context_length_multipliers)
11. ppl_curve = evaluator.run_context_sweep(sequences, context_lengths)  # {ctx: ppl}
12. degradation_ratio = evaluator.compute_degradation_ratio(ppl_curve, h_spec)

13. gate_pass = degradation_ratio > config.degradation_ratio_threshold  # 1.1
14. results = {h_spec, per_layer_h_specs, ppl_curve, degradation_ratio, gate_pass, ...}

15. save_results(results, config.results_path)
16. generate_figures(ppl_curve, h_spec, degradation_ratio, per_layer_h_specs, config.figures_dir)
17. probe.unload()
18. return results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Data loading pipeline | load_wikitext103 + prepare_eval_sequences + compute_context_lengths |
| L-6-2 | Full pipeline wiring | main() orchestration + save_results + generate_figures |
