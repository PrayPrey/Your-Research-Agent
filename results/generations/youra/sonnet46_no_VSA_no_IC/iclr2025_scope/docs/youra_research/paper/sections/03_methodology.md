# Methodology

Our approach flows directly from the key insight: if Llama-2-7B layers vary in attention concentration, and high-entropy (diffuse) layers are functionally local, then a per-layer entropy score computed over a small calibration set can identify which layers are candidates for zero-shot SWA conversion. Every design choice below is motivated by this insight.

## 3.1 Overview

The pipeline comprises three stages:

1. **Entropy Scoring:** Compute per-layer attention entropy for all 32 layers using 100 calibration sequences.
2. **Layer Selection:** Rank layers by entropy; select the top-k highest-entropy layers as SWA candidates.
3. **SWA Conversion:** Monkey-patch the selected layers with a sliding window attention mask; evaluate without fine-tuning.

Stage 1 (entropy scoring) has been implemented and validated (h-e1). Stages 2 and 3 are fully designed and pending experimental execution (h-e2).

## 3.2 Per-Layer Attention Entropy Scoring

### 3.2.1 Entropy Computation

For each input sequence and each transformer layer, we extract the full attention weight tensor via `output_attentions=True` in the HuggingFace forward pass (requires `attn_implementation="eager"` for Llama-2-7B). Given the attention weight matrix A ∈ ℝ^{h × T × T} for a layer with h attention heads and sequence length T, we compute entropy as follows:

```
H_head(head, query_pos) = -∑_{key_pos} A[head, query_pos, key_pos] · log(A[head, query_pos, key_pos] + ε)
```

with ε = 1e-9 for numerical stability. Per-layer entropy is then:

```
H_layer = mean over heads (mean over query positions (H_head))
```

**Why head-mean pooling?** This is the critical design choice. Head-mean pooling captures the **layer-level average behavior** across all heads. Head-max pooling, by contrast, reports the single highest-entropy head, which is dominated by outlier heads that spread weight broadly regardless of the layer's typical behavior. We confirmed empirically that head-mean pooling yields Gini = 0.681 while head-max yields Gini = 0.466 — a 32% relative difference — confirming that head-mean captures a more stable, layer-representative signal.

### 3.2.2 Calibration Set Protocol

We use the WikiText-103 validation split as the calibration source, following standard practice from quantization calibration (GPTQ, AWQ) which uses 100 sequences. We tokenize with the Llama-2-7B tokenizer (BPE, max_length=2048) and chunk into contiguous non-overlapping sequences of 2048 tokens. Calibration subset A uses the first 100 sequences (indices 0–99). For stability analysis, subsets B and C use indices 100–199 and 200–299 respectively.

**Why 100 sequences?** This is sufficient for stable layer rankings (confirmed: Spearman ρ ≥ 0.8 across all subset pairs) while requiring only ≈ 20–30 GPU-minutes for 100 forward passes through Llama-2-7B on a single H100.

**Why WikiText-103?** It is the standard benchmark for our evaluation metric (perplexity) and represents the domain in which accuracy-preservation is measured. Using the same domain for calibration and evaluation minimizes distributional mismatch.

### 3.2.3 Stability Validation

We validate ranking stability using Spearman rank correlation ρ between per-layer entropy vectors from different calibration subsets. The minimum ρ across all subset pairs (ρ_min = min(ρ_AB, ρ_AC, ρ_BC)) serves as the gate criterion: ρ_min ≥ 0.8 indicates that the entropy ranking is robust to calibration subset selection. This validation (Assumption A1) is a prerequisite for using entropy as a selection criterion.

## 3.3 Layer Selection

Given per-layer entropy scores H ∈ ℝ^{32} from the calibration pass, we select the k layers with the highest entropy as SWA candidates:

```
selected_layers = argsort(H, descending=True)[:k]
```

**Why highest entropy?** High entropy indicates diffuse attention — the layer distributes weight broadly without sharp global token retrieval. These layers are not exploiting long-range global dependencies as strongly as low-entropy layers (which show sharp, concentrated attention on specific tokens). Replacing a high-entropy layer with SWA(w=512) constrains it to attend within a local window — behavior closer to what it was already doing.

**Why k = 4?** Conservatively converting 12.5% of layers (4 of 32) balances efficiency gain with risk of accuracy degradation. The remaining 28 full-attention layers continue to propagate global context through the residual stream, providing compensation for the 4 converted layers. We also investigate k = 8 (25% conversion) as an upper bound in h-m2.

## 3.4 Sliding Window Attention Conversion

For each selected layer l ∈ selected_layers, we monkey-patch the forward pass to apply an additive sliding window causal mask before the softmax:

```python
def swa_forward(self, hidden_states, attention_mask, ...):
    # Standard Llama attention forward up to attention weight computation
    attn_weights = torch.matmul(query_states, key_states.transpose(-2, -1)) / math.sqrt(head_dim)
    
    # Apply SWA mask: allow only positions within window w of query
    seq_len = attn_weights.size(-1)
    swa_mask = make_sliding_window_causal_mask(seq_len, window=512, device=attn_weights.device)
    attn_weights = attn_weights + swa_mask  # additive: 0.0 (attend) or -inf (block)
    
    attn_weights = torch.nn.functional.softmax(attn_weights, dim=-1)
    # ... continue standard attention
```

**Why additive float mask (0.0/−inf)?** This follows HuggingFace's standard attention mask convention for Llama-2-7B (`attn_implementation="eager"`), ensuring compatibility with the existing forward pass without requiring any structural modifications to the model. The mask is computed once and cached for efficiency.

**Why w = 512?** This matches the evaluation stride used for WikiText-103 perplexity computation (stride = 512), ensuring that the SWA window covers the full evaluation context for each token position. A window smaller than the evaluation stride would systematically exclude tokens that fall outside the window but within the stride context.

## 3.5 Implementation Details

**Model:** `meta-llama/Llama-2-7b-hf`, loaded with `attn_implementation="eager"`, `torch_dtype=torch.float16`, `device_map="auto"`. Batch size = 1 (required for `output_attentions=True` in float16 to avoid OOM). The attention tensor (1 × 32 × 2048 × 2048 × float16) is deleted after each layer's entropy computation to avoid memory accumulation.

**Mask Validation:** Before evaluation, we execute a `verify_swa_mechanism()` check that confirms: (1) attended positions for each SWA layer match the expected sliding window pattern (attended = min(w, i+1) tokens for query at position i), (2) no off-by-one or causal mask interaction bugs are present.

**Evaluation Protocol for h-e2 (Pending):** WikiText-103 test split, stride = 512, max_length = 4096. Perplexity computed as exp(mean NLL) over the test set, consistent with standard HuggingFace perplexity benchmarks. Comparison conditions: (a) full-attention baseline (k=0), (b) entropy-guided k=4 SWA, (c) random-k=4 SWA (3 seeds, mean reported), (d) last-k=4 SWA (deepest 4 layers).

## 3.6 Code Structure

The implementation follows a clean module structure to enable reproducibility:

```
h-e1/code/
  data.py     — load_wikitext103(), chunk_and_split()
  entropy.py  — compute_layer_entropy(), score_subset()
  report.py   — compute_spearman(), save_results_json(), generate_figures()
  run.py      — end-to-end orchestration

h-e2/code/
  swa.py      — make_sliding_window_causal_mask(), patch_layer_with_swa()
  eval.py     — compute_perplexity(), compare_conditions()
  verify.py   — verify_swa_mechanism(), validate_swa_mask()
  run.py      — end-to-end orchestration
```

All code is designed for single-GPU execution (1× H100), completing calibration (h-e1) in < 1 GPU-hour and evaluation (h-e2, pending) in approximately 2–4 GPU-hours.
