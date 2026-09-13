---
hypothesis_id: h-e1
phase: 03_architecture
date: 2026-08-22
author: yoon303@etri.re.kr
---

# Architecture: h-e1 — Per-Layer Attention Entropy Stability

Applied: PyTorch scaled_dot_product_attention pattern (attention weight entropy via output_attentions=True)
Applied: HuggingFace inference-only forward pass pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No prior h-e* code to reuse.

---

## File Structure

```
h-e1/
  code/
    run.py          # entry point: load data, load model, run measurement, save outputs
    entropy.py      # compute_layer_entropy(), score_subset()
    data.py         # load_wikitext103(), chunk_and_split()
    report.py       # save_results_json(), generate_figures()
  figures/          # output figures (auto-created)
  results.json      # output metrics
```

---

## Module Definitions

### DataModule (`code/data.py`)

**Dependencies**: datasets, transformers (AutoTokenizer)

```python
def load_wikitext103() -> list[str]: ...
    # returns load_dataset("Salesforce/wikitext", "wikitext-103-raw-v1", split="validation")["text"]

def chunk_and_split(
    texts: list[str],
    tokenizer_name: str = "meta-llama/Llama-2-7b-hf",
    seqlen: int = 2048,
    n_subsets: int = 3,
    subset_size: int = 100,
) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
    # returns (subset_A, subset_B, subset_C) — each list of 100 (1, 2048) int64 tensors
    # subset_A = chunks[0:100], subset_B = chunks[100:200], subset_C = chunks[200:300]
```

### EntropyModule (`code/entropy.py`)

**Dependencies**: torch, numpy

```python
def compute_layer_entropy(
    model: AutoModelForCausalLM,
    input_ids: Tensor,      # (1, seq_len) on device
    eps: float = 1e-9,
) -> np.ndarray:            # (n_layers,) mean Shannon entropy per layer
    # forward with output_attentions=True
    # attn[i]: (1, 32, seq_len, seq_len) → H = -sum(p*log(p+eps), axis=-1).mean()

def score_subset(
    model: AutoModelForCausalLM,
    sequences: list[Tensor],
) -> np.ndarray:            # (n_layers,) mean over sequences
```

### ReportModule (`code/report.py`)

**Dependencies**: numpy, scipy, matplotlib, json, pathlib

```python
def compute_spearman(
    entropy_A: np.ndarray,   # (32,)
    entropy_B: np.ndarray,   # (32,)
    entropy_C: np.ndarray,   # (32,)
) -> dict:
    # returns {"rho_AB": float, "rho_AC": float, "rho_BC": float,
    #          "p_AB": float, "p_AC": float, "p_BC": float,
    #          "min_rho": float, "gate_pass": bool}

def save_results_json(
    spearman: dict,
    entropy_A: np.ndarray,
    entropy_B: np.ndarray,
    entropy_C: np.ndarray,
    out_path: str = "results.json",
) -> None: ...

def generate_figures(
    spearman: dict,
    entropy_A: np.ndarray,
    entropy_B: np.ndarray,
    entropy_C: np.ndarray,
    figures_dir: str = "figures/",
) -> None:
    # entropy_stability.png     — bar: min/mean ρ vs 0.8 threshold
    # layer_entropy_per_subset.png — 32-layer entropy overlay for 3 subsets
    # rank_correlation_scatter.png — 3 scatter plots with ρ annotated
    # top8_overlap.png           — table of top-8 layer overlap across subsets
```

### RunScript (`code/run.py`)

**Dependencies**: DataModule, EntropyModule, ReportModule, transformers, torch

```python
def main() -> None:
    # 1. load_wikitext103() + chunk_and_split()
    # 2. AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf",
    #        attn_implementation="eager", torch_dtype=torch.float16, device_map="auto")
    # 3. score_subset() for A, B, C
    # 4. compute_spearman() + save_results_json() + generate_figures()
    # 5. print GATE: PASS/FAIL (min_rho=X.XX)

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown (MS+D+A+I) |
|----|------|-------------|------------|----------------------|
| A-1 | Project Setup | Create h-e1/code/ structure, requirements.txt, verify HF_TOKEN access | 4 | 1+1+1+1 |
| A-2 | Data Loading | Implement data.py: load WikiText-103, tokenize, chunk into 300 seq, split 3×100 | 7 | 2+2+1+2 |
| A-3 | Model Loading | Load Llama-2-7b-hf with attn_implementation="eager", float16, device_map="auto" | 6 | 1+2+1+2 |
| A-4 | Entropy Computation | Implement entropy.py: compute_layer_entropy + score_subset (300 forward passes) | 10 | 3+2+3+2 |
| A-5 | Reporting & Figures | Implement report.py: Spearman ρ, results.json, 4 figures | 9 | 3+2+2+2 |
| A-6 | Integration & Gate | Wire run.py, end-to-end test, verify GATE PASS/FAIL printout and output files | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(15-20): [] | High(11-14): [] | Medium(6-10): [A-2, A-3, A-4, A-5, A-6] | Low(1-5): [A-1]

---

## Dependencies

```
torch>=2.0.0
transformers>=4.46.0
datasets>=2.0.0
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
```

Environment: `HF_TOKEN` or `HUGGING_FACE_HUB_TOKEN` must be set for Llama-2 access.

---

## Notes

- Memory: batch_size=1 required; delete `output.attentions` after entropy computation each step to avoid OOM
- Determinism: subset split is index-based ([0:100], [100:200], [200:300]) — no random seed needed
- Fallback: if GPU OOM, `mathispink/attention-saver` library provides hook-based extraction without materializing full attention tensor
