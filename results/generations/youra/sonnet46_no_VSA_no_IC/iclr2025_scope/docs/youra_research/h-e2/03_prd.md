# Product Requirements Document: h-e2
# Entropy-Guided Selective SWA Conversion of Llama-2-7B

---
stepsCompleted: [prd-executive-summary, prd-problem-statement, prd-functional-requirements, prd-nfr, prd-success-criteria]
hypothesis_id: h-e2
tier: LIGHT
date: 2026-08-22
author: yoon303@etri.re.kr
---

## Executive Summary

This PRD specifies the implementation requirements for h-e2: a zero-shot proof-of-concept that replaces exactly k=4 high-entropy attention layers in Llama-2-7B with Sliding Window Attention (SWA, window=512) and validates that WikiText-103 perplexity degrades by ≤2.0 points relative to the full-attention baseline. The experiment builds directly on h-e1 (entropy criterion validated) and contributes the first selective SWA feasibility measurement for Llama-2-7B.

**Gate:** MUST_WORK — `delta_ppl ≤ 2.0` on WikiText-103 full test set.

---

## 1. Problem Statement

Full-model zero-shot SWA conversion of LLMs produces catastrophic quality degradation (HF issue #28915: "doesn't even produce fluent text"). The hypothesis is that restricting SWA replacement to the k=4 layers with highest attention entropy (identified by h-e1) preserves model quality while reducing full-attention computation in those layers. This experiment directly tests that claim.

---

## 2. Scope

**In scope:**
- Entropy ranking reuse from h-e1 (top-4 layer indices by mean head-pooled per-layer entropy)
- Monkey-patch SWA mask injection into Llama-2-7B (eager mode)
- WikiText-103 perplexity evaluation on full test set
- Baseline (full attention) vs. SWA-k4 comparison
- Mask correctness validation and mechanism verification

**Out of scope:**
- Fine-tuning or weight modification
- Hyperparameter search over k or window size
- Flash attention (incompatible with mask injection)
- Downstream task evaluation (EXISTENCE PoC only)

---

## 3. Hypothesis & Gate

**Hypothesis Statement:** Entropy-guided k=4 SWA(w=512) conversion of Llama-2-7B zero-shot maintains WikiText-103 perplexity within 2.0 points of full-attention baseline.

**Gate Type:** MUST_WORK

**Prediction P1:** `ppl_swa_k4 - ppl_baseline ≤ 2.0`

**Gate Routing:**
- `delta_ppl ≤ 2.0` → GATE PASS → h-e2 VALIDATED
- `delta_ppl ∈ (2.0, 5.0]` → route to Phase 0 for threshold relaxation
- `delta_ppl > 5.0` → zero-shot selective SWA infeasible → route to Phase 0

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| **Name** | WikiText-103 |
| **Version** | wikitext-103-v1 |
| **Source** | HuggingFace Datasets (auto-download) |
| **HF identifier** | `load_dataset("wikitext", "wikitext-103-v1")` |
| **Splits** | Calibration: validation split, first 100 sequences (from h-e1); Evaluation: full test split |
| **Test size** | ~245K tokens (~60 articles) |
| **Preprocessing** | Concatenate test texts with `"\n\n"`, tokenize with Llama-2 BPE tokenizer, chunk to max_length=4096 with stride=512, discard trailing incomplete chunk |

**Note:** WikiText-103 auto-downloads via HF Datasets — no manual download task required.

### 4.2 Model

| Field | Value |
|-------|-------|
| **Model** | `meta-llama/Llama-2-7b-hf` |
| **Source** | HuggingFace Hub (requires HF token + model access) |
| **Precision** | bfloat16 |
| **Device** | 1× H100 GPU, device_map="auto" |
| **Attention impl** | `attn_implementation="eager"` (MANDATORY — flash attention blocks custom mask injection) |

---

## 5. Functional Requirements

### FR-1: Environment Setup
- Install Python dependencies: `transformers`, `datasets`, `torch`, `accelerate`, `tqdm`, `matplotlib`
- Verify HuggingFace token with access to `meta-llama/Llama-2-7b-hf`

### FR-2: Entropy Layer Ranking Loader
- Reuse or reproduce h-e1 entropy ranking: compute mean head-pooled per-layer attention entropy on 100-sequence calibration set (WikiText-103 validation split, first 100 sequences)
- Output: `entropy_layer_ranking` — list of 32 layer indices sorted by mean entropy descending
- **Requirement:** Head-mean pooling across 32 heads (NOT head-max; h-e1 lesson)

### FR-3: Baseline Perplexity Evaluation
- Load Llama-2-7b-hf with `attn_implementation="eager"`, bfloat16
- Compute WikiText-103 test perplexity using stride-based chunked evaluation (max_length=4096, stride=512)
- Record `ppl_baseline`

### FR-4: SWA Mask Construction
- Implement `make_sliding_window_causal_mask(seq_len, window_size, dtype, device)` — additive float mask: 0.0 for attended positions, −inf for blocked
- Window: position i attends to `[max(0, i − window_size + 1), i]`
- No flash attention; no SDPA — use eager attention mode

### FR-5: Layer Monkey-Patch
- Implement `patch_layer_with_swa(layer, window_size=512)` — overrides `layer.self_attn.forward` with `swa_forward` that injects the SWA causal mask
- Implement `apply_entropy_guided_swa(model, entropy_layer_ranking, k=4, window_size=512)` — patches exactly the top-k entropy layers, returns `target_layers` list

### FR-6: Mask Validation (MANDATORY)
- Implement `validate_swa_mask(mask, window_size=512)` — spot-checks 10 positions
- Run before SWA perplexity evaluation

### FR-7: Mechanism Verification
- Implement `verify_swa_mechanism(model, target_layers, window_size=512, test_seq_len=600)` — uses forward hooks to verify attended position count equals `window_size` at target layers
- Run after patching, before full evaluation

### FR-8: SWA Perplexity Evaluation
- Apply entropy-guided SWA (FR-5) to the loaded model
- Compute WikiText-103 test perplexity with identical stride/chunking as baseline
- Record `ppl_swa_k4`

### FR-9: Results & Diagnostics
- Compute `delta_ppl = ppl_swa_k4 - ppl_baseline`
- Record `target_layers` (4 layer indices — needed for h-m2 depth analysis)
- Record `depth_positions` statistics (early/mid/late distribution of converted layers)
- Save results to JSON: `results/h-e2_results.json`

### FR-10: Visualization
- **Mandatory:** Bar chart — `ppl_baseline` vs `ppl_swa_k4` with Δ=2.0 threshold line
- **Optional:** Layer entropy scatter plot (x=layer index, y=entropy, top-4 highlighted)
- Save to `figures/` directory

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| **Precision** | bfloat16 throughout (baseline and SWA model identical precision) |
| **Reproducibility** | Fixed seed=1; deterministic chunking; no sampling |
| **Runtime** | ≤ 60 min on 1× H100 (estimated 30 min) |
| **Memory** | Llama-2-7B in bfloat16 ≈ 14GB VRAM |
| **No fine-tuning** | Zero-shot only — no gradient computation |
| **Parity** | Baseline and SWA evaluation must use identical tokenization, chunking, and stride |

---

## 7. Dependencies

### 7.1 Python Packages
```
transformers>=4.37.0
datasets>=2.16.0
torch>=2.1.0
accelerate>=0.26.0
tqdm>=4.66.0
matplotlib>=3.8.0
numpy>=1.26.0
```

### 7.2 External Access
- HuggingFace Hub account with `meta-llama/Llama-2-7b-hf` model access
- `HUGGINGFACE_TOKEN` environment variable (or `huggingface-cli login`)

### 7.3 From h-e1
- Calibration set definition: WikiText-103 validation split, first 100 sequences, same tokenization
- Head-mean entropy pooling method (not head-max)

### 7.4 Reference Implementations
- SWAA (arXiv 2512.10411): monkey-patch pattern for selective SWA layer replacement
- HF Transformers `modeling_llama.py`: eager attention mode, attention_mask parameter interface

---

## 8. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Code runs without error | TRUE | Full pipeline executes |
| SWA mechanism activated | TRUE | Log confirms target layers; `verify_swa_mechanism` PASSES |
| Mask correct | window_size attended positions at pos≥512 | `validate_swa_mask` + `verify_swa_mechanism` |
| **Gate: delta_ppl ≤ 2.0** | `ppl_swa_k4 - ppl_baseline ≤ 2.0` | WikiText-103 full test set |
| Results saved | JSON + figures | `results/h-e2_results.json`, `figures/*.png` |

---

## 9. File Structure

```
docs/youra_research/h-e2/
├── 02c_experiment_brief.md      # Phase 2C input
├── 03_prd.md                    # This document
├── 03_architecture.md           # Phase 3 architecture
├── 03_logic.md                  # Phase 3 logic
├── 03_config.md                 # Phase 3 config
├── 03_tasks.yaml                # Phase 3 tasks
└── code/
    ├── run_experiment.py        # Main entry point
    ├── entropy_ranking.py       # FR-2: entropy layer ranking
    ├── swa_patch.py             # FR-4, FR-5: SWA mask + monkey-patch
    ├── evaluation.py            # FR-3, FR-8: perplexity evaluation
    ├── verification.py          # FR-6, FR-7: mask + mechanism validation
    ├── visualization.py         # FR-10: plots
    └── results/
        └── h-e2_results.json
```
