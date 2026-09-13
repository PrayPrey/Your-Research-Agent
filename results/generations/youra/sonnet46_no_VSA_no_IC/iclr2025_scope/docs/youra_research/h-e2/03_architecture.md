# Architecture: h-e2
# Entropy-Guided Selective SWA Conversion of Llama-2-7B

---
hypothesis_id: h-e2
type: EXISTENCE (PoC)
date: 2026-08-22
author: yoon303@etri.re.kr
---

Applied: single-file-per-concern flat module layout (diffusers PHILOSOPHY.md pattern)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase found — Serena could not locate an active project at h-e2/code/
**Analyzed Path**: docs/youra_research/h-e2 (Serena returned no active project error)
**Findings**: New implementation from scratch; pseudo-code fully specified in 02c_experiment_brief.md

---

## File Organization

```
docs/youra_research/h-e2/code/
├── run_experiment.py     # orchestrator: loads model, calls all modules in order
├── entropy_ranking.py    # FR-2: calibration-set entropy ranking
├── swa_patch.py          # FR-4, FR-5: mask construction + monkey-patch
├── evaluation.py         # FR-3, FR-8: stride-chunked perplexity
├── verification.py       # FR-6, FR-7: mask validation + hook-based mechanism check
├── visualization.py      # FR-10: bar chart + optional scatter
└── results/
    └── h-e2_results.json
```

---

## Modules

### EntropyRanker (`entropy_ranking.py`)

**Dependencies**: transformers, datasets, torch

```python
def compute_entropy_layer_ranking(
    model,
    tokenizer,
    calib_dataset,          # HF dataset, validation split
    n_sequences: int = 100,
    device: str = "cuda",
) -> list[int]:
    """
    Returns 32 layer indices sorted by mean head-pooled per-layer entropy descending.
    Head-mean pooling (NOT head-max — h-e1 lesson).
    Requires model loaded with output_attentions=True.
    """
    ...
```

---

### SWAPatch (`swa_patch.py`)

**Dependencies**: torch, transformers (LlamaDecoderLayer)

```python
def make_sliding_window_causal_mask(
    seq_len: int,
    window_size: int,
    dtype: torch.dtype,
    device: torch.device,
) -> torch.Tensor:
    """Additive float mask: 0.0 attend, -inf block. Shape: (seq_len, seq_len)."""
    ...

def patch_layer_with_swa(layer, window_size: int = 512) -> None:
    """Monkey-patches layer.self_attn.forward in-place."""
    ...

def apply_entropy_guided_swa(
    model,
    entropy_layer_ranking: list[int],
    k: int = 4,
    window_size: int = 512,
) -> list[int]:
    """Patches top-k entropy layers. Returns target_layers list."""
    ...
```

---

### Evaluator (`evaluation.py`)

**Dependencies**: torch, transformers, tqdm

```python
def compute_perplexity(
    model,
    tokenizer,
    text: str,
    max_length: int = 4096,
    stride: int = 512,
) -> float:
    """Stride-chunked NLL perplexity. torch.no_grad() throughout."""
    ...

def load_wikitext103_test_text() -> str:
    """load_dataset('wikitext','wikitext-103-v1')['test'], join with '\\n\\n'."""
    ...
```

---

### Verifier (`verification.py`)

**Dependencies**: torch

```python
def validate_swa_mask(mask: torch.Tensor, window_size: int = 512) -> None:
    """Spot-checks 10 positions; asserts attended range. Raises on failure."""
    ...

def verify_swa_mechanism(
    model,
    target_layers: list[int],
    window_size: int = 512,
    test_seq_len: int = 600,
) -> dict[int, int]:
    """
    Registers pre-forward hooks on target layers.
    Runs dummy forward, checks attended count == window_size at pos test_seq_len-1.
    Returns {layer_idx: attended_count}.
    """
    ...
```

---

### Visualizer (`visualization.py`)

**Dependencies**: matplotlib

```python
def plot_ppl_comparison(
    ppl_baseline: float,
    ppl_swa_k4: float,
    delta_threshold: float = 2.0,
    save_path: str = "figures/ppl_comparison.png",
) -> None:
    """Bar chart with Δ=2.0 threshold line."""
    ...

def plot_entropy_scatter(
    entropy_scores: list[float],   # per-layer mean entropy, len=32
    target_layers: list[int],
    save_path: str = "figures/entropy_scatter.png",
) -> None:
    """Optional: x=layer index, y=entropy, top-4 highlighted."""
    ...
```

---

### Orchestrator (`run_experiment.py`)

**Dependencies**: all above modules, json, os

```python
def main() -> None:
    """
    1. Load model + tokenizer (eager, bfloat16, device_map='auto')
    2. compute_entropy_layer_ranking → entropy_layer_ranking
    3. compute_perplexity (baseline) → ppl_baseline
    4. apply_entropy_guided_swa → target_layers
    5. validate_swa_mask + verify_swa_mechanism
    6. compute_perplexity (SWA) → ppl_swa_k4
    7. Compute delta_ppl, depth_positions; save results/h-e2_results.json
    8. plot_ppl_comparison; optionally plot_entropy_scatter
    """
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Environment & Model Loading | requirements.txt, model load (eager/bf16), dataset load, seed fixture | 6 | 2+1+1+2 |
| E-2 | Entropy Layer Ranking | `entropy_ranking.py`: forward pass with output_attentions, head-mean pool, sort | 10 | 3+2+3+2 |
| E-3 | SWA Mask + Monkey-Patch | `swa_patch.py`: mask construction, patch_layer_with_swa, apply_entropy_guided_swa | 11 | 3+2+4+2 |
| E-4 | Perplexity Evaluation | `evaluation.py`: stride-chunked NLL, load_wikitext103_test_text | 8 | 2+2+2+2 |
| E-5 | Mask Validation + Mechanism Verification | `verification.py`: validate_swa_mask, verify_swa_mechanism with hooks | 10 | 2+2+3+3 |
| E-6 | Orchestration + Results + Visualization | `run_experiment.py` pipeline, JSON save, bar chart, optional scatter | 9 | 2+3+2+2 |

**Distribution**: High(9-11): [E-2, E-3, E-4, E-5, E-6], Low(4-8): [E-1]

**Total subtask budget**: 6 epics × avg 4 subtasks = ~24 — fits LIGHT tier (15 task cap at epic level; subtask breakdown internal to coder).

---

## Key Constraints

- `attn_implementation="eager"` mandatory — flash attention cannot accept external sliding window masks
- Baseline and SWA evaluation use identical tokenization, chunking (max_length=4096, stride=512)
- No gradient computation anywhere (`torch.no_grad()` throughout)
- Head-mean pooling for entropy (not head-max — h-e1 lesson)
- `verify_swa_mechanism` MUST pass before SWA perplexity evaluation begins
- Results JSON must include `target_layers` field (needed downstream by h-m2)
