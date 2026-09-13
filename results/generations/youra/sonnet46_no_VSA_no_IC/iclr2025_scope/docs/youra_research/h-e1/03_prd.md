---
stepsCompleted:
  - Executive Summary
  - Problem Statement
  - Functional Requirements
  - Non-Functional Requirements
  - Success Criteria
hypothesis_id: h-e1
date: 2026-08-22
author: yoon303@etri.re.kr
---

# PRD: h-e1 — Per-Layer Attention Entropy Stability in Llama-2-7B

## 1. Executive Summary

This experiment verifies that per-layer attention entropy in Llama-2-7B produces a stable layer ranking (Spearman ρ ≥ 0.8) across 3 independent 100-sequence calibration subsets drawn from the WikiText-103 validation split. It is a pure measurement experiment (EXISTENCE/PoC): no model training, no architecture modification. The output is a ranked list of Llama-2-7B's 32 attention layers by mean entropy, confirmed stable across random calibration subsets. A positive result enables downstream entropy-guided layer selection for Sliding Window Attention Adaptation (H-EntropySWA-v1).

**Hypothesis gate:** MUST_WORK — failure (min ρ < 0.7) blocks all downstream hypotheses (h-e2, h-m1, h-m2, h-c1).

---

## 2. Problem Statement

**Background:** Entropy-based layer selection requires the entropy criterion to be *consistent* — if different calibration subsets yield different layer rankings, the selection criterion is noise and cannot be trusted for downstream adaptation.

**Problem:** It is unknown whether 100-sequence calibration subsets of WikiText-103 yield stable per-layer attention entropy rankings in Llama-2-7B. If they do not, entropy-based SWA layer selection is invalid.

**Scope:** Single model (Llama-2-7B), single dataset (WikiText-103 validation), inference-only, three non-overlapping 100-sequence subsets, Spearman ρ across all pairwise combinations.

---

## 3. Functional Requirements

### FR-1: Data Loading and Preprocessing

**Source:** HuggingFace Datasets — `Salesforce/wikitext`, config `wikitext-103-raw-v1`, split `validation`

**Implementation:**
```python
from datasets import load_dataset
ds = load_dataset("Salesforce/wikitext", "wikitext-103-raw-v1", split="validation")
```

**Preprocessing steps:**
1. Concatenate all text entries into one string
2. Tokenize using `AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")` with `truncation=False`
3. Chunk into non-overlapping windows of `seqlen=2048` tokens
4. Assign to 3 non-overlapping subsets: indices [0:100], [100:200], [200:300]
5. No padding; batch_size=1

**Note:** WikiText-103 auto-downloads via HuggingFace cache — no manual download task needed.

### FR-2: Model Loading

**Model:** `meta-llama/Llama-2-7b-hf`

**Loading configuration:**
```python
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    attn_implementation="eager",   # required for output_attentions=True
    torch_dtype=torch.float16,
    device_map="auto"
)
```

**Constraint:** Must use `attn_implementation="eager"` — flash_attention_2 does not support `output_attentions=True`.

### FR-3: Per-Layer Attention Entropy Computation

For each input sequence and each of the 32 Llama-2-7B layers:

1. Run forward pass with `output_attentions=True`
2. Extract `output.attentions` — tuple of 32 tensors, each `(1, 32, seq_len, seq_len)`
3. For each layer tensor: compute Shannon entropy `H = -Σ p·log(p + ε)` where ε=1e-9, averaged over all heads and all query positions
4. Accumulate entropies across 100 sequences; compute mean per layer → `entropy_subset: (32,)` vector

**Reference implementation (GAIR-NLP/Entropy-ABF pattern):**
```python
def compute_layer_entropy(model, input_ids):
    with torch.no_grad():
        output = model(input_ids, output_attentions=True)
    n_layers = len(output.attentions)
    entropy_per_layer = np.zeros(n_layers)
    for layer_idx, attn in enumerate(output.attentions):
        attn_np = attn.squeeze(0).float().cpu().numpy()  # (32, seq_len, seq_len)
        eps = 1e-9
        H = -np.sum(attn_np * np.log(attn_np + eps), axis=-1)  # (32, seq_len)
        entropy_per_layer[layer_idx] = H.mean()
    return entropy_per_layer
```

### FR-4: Spearman ρ Computation

Compute 3 pairwise Spearman rank correlations:

```python
from scipy.stats import spearmanr
rho_AB, p_AB = spearmanr(entropy_A, entropy_B)
rho_AC, p_AC = spearmanr(entropy_A, entropy_C)
rho_BC, p_BC = spearmanr(entropy_B, entropy_C)
gate_passes = min(rho_AB, rho_AC, rho_BC) >= 0.8
```

### FR-5: Result Reporting and Visualization

**Required outputs:**
1. `results.json` — all 3 ρ values, p-values, gate pass/fail, per-layer entropy vectors for all 3 subsets
2. `figures/entropy_stability.png` — bar chart: min(ρ), mean(ρ) vs threshold (0.8); 3 pairwise ρ values side-by-side
3. `figures/layer_entropy_per_subset.png` — per-layer mean entropy bar/line chart: 32 layers × 3 subsets overlaid
4. `figures/rank_correlation_scatter.png` — scatter plots: entropy_A vs entropy_B, entropy_A vs entropy_C, entropy_B vs entropy_C with ρ annotated
5. `figures/top8_overlap.png` — Venn or table showing top-8 highest-entropy layers per subset and overlap

All figures saved to `h-e1/figures/`. Stdout prints gate result at end: `GATE: PASS (min_rho=X.XX)` or `GATE: FAIL (min_rho=X.XX)`.

---

## 4. Data Specification

| Property | Value |
|----------|-------|
| Dataset | WikiText-103 |
| HuggingFace identifier | `Salesforce/wikitext` / `wikitext-103-raw-v1` |
| Split | `validation` |
| Download method | Auto (HuggingFace datasets cache) |
| Tokenizer | `meta-llama/Llama-2-7b-hf` |
| Sequence length | 2048 tokens |
| Subsets | 3 × 100 contiguous sequences (indices [0:100], [100:200], [200:300]) |
| Total sequences | 300 |
| Total tokens processed | 614,400 |

No static/manual download datasets. No preprocessing artifacts to cache.

---

## 5. Evaluation Metrics

### Primary Metrics (Gate Criteria)

| Metric | Computation | Gate Threshold |
|--------|-------------|----------------|
| Spearman ρ (A,B) | `spearmanr(entropy_A, entropy_B)` | ≥ 0.8 |
| Spearman ρ (A,C) | `spearmanr(entropy_A, entropy_C)` | ≥ 0.8 |
| Spearman ρ (B,C) | `spearmanr(entropy_B, entropy_C)` | ≥ 0.8 |
| **min(ρ)** | `min(rho_AB, rho_AC, rho_BC)` | **≥ 0.8 (GATE)** |

### Secondary Diagnostics

- Per-layer mean entropy values (32-dim) for each subset
- Top-8 highest-entropy layer indices per subset
- Overlap count in top-8 sets across subsets
- p-values for each Spearman correlation

---

## 6. Success Criteria

| Criterion | Condition |
|-----------|-----------|
| **GATE PASS** | `min(rho_AB, rho_AC, rho_BC) >= 0.8` |
| Code runs without error | All 300 forward passes complete |
| Results reproducible | Deterministic subset assignment (index-based, no random sampling) |

**GATE FAIL condition:** min ρ < 0.7 → entropy ranking is noise; invalidates H-EntropySWA-v1.

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.46.0
datasets>=2.0.0
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
```

### 7.2 External Model (HuggingFace Hub)

- `meta-llama/Llama-2-7b-hf` — requires HuggingFace token with Llama-2 access approved
- Environment variable: `HF_TOKEN` or `HUGGING_FACE_HUB_TOKEN`

### 7.3 Hardware Requirements

- GPU: ≥24GB VRAM (H100/A100/RTX 3090) recommended
- Storage: ~14GB for Llama-2-7B weights (float16)
- RAM: ≥32GB system memory

---

## 8. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | Deterministic subset assignment via fixed index ranges (no random seed dependency) |
| Memory efficiency | Batch size 1; delete attention tensors after entropy computation |
| Runtime | ≤60 min on A100/H100; CPU fallback acceptable (slower) |
| Output completeness | All figures + results.json must be generated even if gate fails |
| Scope | Inference-only; no training, no gradient computation |
