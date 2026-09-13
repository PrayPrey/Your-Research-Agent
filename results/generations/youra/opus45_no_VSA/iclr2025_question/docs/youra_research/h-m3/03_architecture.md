# Architecture: h-m3 (MECHANISM)

**Hypothesis**: RCI flip pattern appears in >= 30% hallucinations and < 10% correct responses

Applied: tuned-lens trajectory-extraction pattern (layer-wise logit-lens projection, from experiment brief; no direct KB match for "RCI"/novel metric).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1), but base code not yet materialized
**Status**: `h-e1/code/` directory does not exist on disk (glob returned no files) — h-e1 architecture spec exists but implementation has not been generated yet. Serena symbol lookup skipped since there is no code to analyze; treated as green-field with spec-level reuse from `h-e1/03_architecture.md` only.
**Analyzed Path**: `h-e1/code/` (not found)
**Findings**: No actual code to verify import paths against. h-m3 will implement its own self-contained pipeline (data.py, model.py) mirroring h-e1's design rather than importing h-e1 modules, since no importable package exists.

---

## File Structure (MECHANISM)

```
h-m3/code/
├── config.py       # fixed config (seed, layers, model id, thresholds)
├── data.py         # TruthfulQA MC1 loading + correctness labeling (mirrors h-e1)
├── model.py        # HF model load + hidden state extraction
├── rci.py          # RCIFlipDetector: logit-lens projection + flip detection
├── evaluate.py      # flip rate computation, gate check
├── visualize.py     # required + optional figures
└── run.py           # orchestrates: data -> model -> rci -> evaluate -> visualize
```

---

## Module Interfaces

### config.py

```python
SEED = 42
MODEL_ID = "meta-llama/Llama-2-7b-hf"
LAYER_RANGE = (24, 32)  # inclusive, 9 layers
HALLUC_RATE_THRESHOLD = 0.30
CORRECT_RATE_THRESHOLD = 0.10
SEPARATION_THRESHOLD = 0.20
FIGURES_DIR = "figures/"
```

### data.py (`code/data.py`)

**Dependencies**: config

```python
def load_truthfulqa_mc1() -> list[dict]: ...
    # returns [{"question": str, "choices": list[str], "labels": list[int]}, ...]

def build_samples(items: list[dict]) -> list[dict]: ...
    # -> [{"prompt": str, "is_hallucination": bool}, ...]
    # is_hallucination = model's greedy top-1 answer != correct choice (resolved in model.py)
```

### model.py (`code/model.py`)

**Dependencies**: config, transformers

```python
def load_model(model_id: str, device: str = "cuda") -> tuple["AutoModelForCausalLM", "AutoTokenizer"]: ...
    # output_hidden_states=True, torch_dtype=float16, device_map="auto"

def get_hidden_states(model, tokenizer, prompt: str) -> tuple:
    # -> hidden_states tuple (33 layers incl. embedding, batch=1, seq, 4096)

def label_hallucination(model, tokenizer, prompt: str, correct_answer: str) -> bool: ...
    # greedy-decode final answer, compare to correct_answer (temp=0)
```

### rci.py (`code/rci.py`)

**Dependencies**: config, torch

```python
class RCIFlipDetector:
    def __init__(self, unembedding_weight: "Tensor", layer_range: tuple[int, int] = (24, 32)): ...

    def extract_layer_predictions(self, hidden_states: tuple, position: int = -1) -> "Tensor": ...
        # -> logits (9, batch, vocab_size), via h @ unembedding.T per layer

    def detect_flip_pattern(self, layer_logits: "Tensor") -> tuple["Tensor", "Tensor"]: ...
        # -> (num_flips[batch], flip_positions)

    def compute_sample(self, hidden_states: tuple) -> dict: ...
        # -> {"num_flips": int, "has_flip": bool, "flip_positions": list[int]}
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: config

```python
def compute_rates(results: list[dict]) -> dict: ...
    # results: [{"has_flip": bool, "is_hallucination": bool}, ...]
    # -> {"hallucination_flip_rate": float, "correct_flip_rate": float, "separation": float}

def check_gate(rates: dict) -> dict: ...
    # -> {"pass": bool, "poc_pass": bool}
    # full pass: halluc>=0.30 and correct<0.10
    # poc pass (direction only): halluc_rate > correct_rate
```

### visualize.py (`code/visualize.py`)

**Dependencies**: config, matplotlib

```python
def plot_gate_metrics(rates: dict, save_path: str) -> None: ...        # required
def plot_flip_position_heatmap(results: list[dict], save_path: str) -> None: ...
def plot_token_transition_sankey(results: list[dict], save_path: str) -> None: ...
def plot_confidence_distribution(results: list[dict], save_path: str) -> None: ...
```

### run.py (`code/run.py`)

**Dependencies**: all modules above

```python
def verify_mechanism(model, tokenizer, detector: "RCIFlipDetector", sample_prompt: str) -> bool: ...
    # asserts hidden_states>=33 layers, layer_logits.shape[0]==9, num_flips>=0

def main() -> None: ...
    # load data -> load model -> label hallucinations -> verify_mechanism (1 sample)
    # -> per-sample RCI compute -> compute_rates -> check_gate -> visualize -> print summary
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Setup & config | config.py, deps, seeding | 4 | 1+1+1+1 |
| M-2 | Data pipeline | Load TruthfulQA MC1, build prompts | 5 | 2+1+1+1 |
| M-3 | Model loading | HF causal LM load fp16 + hidden states | 6 | 2+2+1+1 |
| M-4 | Hallucination labeling | Greedy decode + compare to correct answer | 7 | 2+2+2+1 |
| M-5 | RCI flip detector | Logit-lens projection + flip detection (rci.py) | 9 | 3+2+3+1 |
| M-6 | Mechanism verification | verify_mechanism assertions on sample | 4 | 1+1+1+1 |
| M-7 | Batch pipeline | Run RCI over 817 samples, perf within 30min | 8 | 3+2+2+1 |
| M-8 | Rate computation & gate | compute_rates, check_gate, success/falsification logic | 5 | 2+1+1+1 |
| M-9 | Visualization | Required bar chart + 3 optional figures | 7 | 2+1+3+1 |
| M-10 | Integration run | run.py end-to-end orchestration + smoke test | 5 | 2+2+1+0 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-5, M-7], Low(4-8): [M-1, M-2, M-3, M-4, M-6, M-8, M-9, M-10]

---

## External Dependencies

None. h-e1's `code/` directory does not exist yet, so no import paths can be verified from actual implementation. h-m3 reimplements the minimal data/model pipeline locally (data.py, model.py) following h-e1's spec (same dataset, model, layer range) rather than importing from h-e1.

---

## Notes

- No training required (mechanism analysis experiment, post-inference only).
- No model modification — RCI detector operates on `hidden_states` output only.
- Falls back to logit-lens direct projection (h-e1 style) rather than tuned-lens library dependency, per brief's fallback recommendation — avoids new dependency.
