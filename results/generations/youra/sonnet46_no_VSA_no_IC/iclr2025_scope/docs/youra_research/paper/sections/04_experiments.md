# Experimental Setup

We design experiments to progressively validate the causal chain underlying the entropy-guided selective SWA framework. The chain has three steps: (1) the entropy criterion identifies layers with stable, meaningful concentration structure; (2) entropy-guided SWA conversion preserves model quality; (3) entropy-based selection is superior to uninformed baselines. Our experiments test each step in order.

## 4.1 Research Questions

**RQ1 (h-e1, Confirmed):** Does head-mean per-layer attention entropy produce stable layer rankings across independent calibration subsets of WikiText-103 (Spearman ρ ≥ 0.8)?

**RQ2 (h-e1, Confirmed):** Do Llama-2-7B layers exhibit measurable within-layer attention concentration (Gini > 0.5, top-10% token share > 0.5) consistently across diverse evaluation examples?

**RQ3 (h-e1, Confirmed):** Is head-mean pooling substantially more stable than head-max pooling for layer-level entropy concentration measurement?

**RQ4 (h-e2, Pending):** Does entropy-guided k=4 SWA conversion maintain WikiText-103 perplexity within 2 points of the full-attention Llama-2-7B baseline, zero-shot?

**RQ5 (h-m1, Pending):** Does entropy-guided k=4 layer selection produce lower perplexity degradation than random-k=4 and last-k=4 selection under identical SWA conversion conditions?

**RQ6 (h-m2, Pending):** How does perplexity degradation scale from k=4 to k=8 converted layers, and where does it exceed the 2-point threshold?

RQ1–RQ3 address validity of the entropy criterion (the prerequisite stage). RQ4–RQ6 address the main accuracy-preservation and comparative superiority claims of H-EntropySWA-v1.

## 4.2 Model and Dataset

**Model:** `meta-llama/Llama-2-7b-hf` (7 billion parameters, 32 transformer layers, 32 attention heads per layer, head dimension = 128, RoPE position encoding, multi-head full attention, no grouped-query attention). Loaded with `attn_implementation="eager"` (required for `output_attentions=True`), `torch_dtype=torch.float16`, `device_map="auto"`.

We specifically target Llama-2-7B because: (1) it uses standard multi-head full attention without architectural modifications that would complicate SWA conversion (no GQA, no sliding window by design); (2) it is a widely-studied benchmark model for efficiency research; (3) its 32-layer structure provides sufficient per-layer heterogeneity to test the entropy criterion.

**Calibration Dataset:** WikiText-103 validation split (Salesforce/wikitext, wikitext-103-raw-v1). Tokenized with the Llama-2-7B BPE tokenizer (vocabulary size 32,000). Chunked into contiguous non-overlapping sequences of 2,048 tokens. Three non-overlapping 100-sequence subsets extracted: A (indices 0–99), B (indices 100–199), C (indices 200–299). The split is deterministic (index-based) and requires no random seed.

*Why WikiText-103?* It is the standard perplexity benchmark for this model class, enabling direct comparison with published baselines. Using the same domain for calibration and evaluation minimizes distributional mismatch.

**Evaluation Dataset (h-e2, pending):** WikiText-103 test split. Perplexity computed with stride = 512, max_length = 4,096, following standard HuggingFace perplexity evaluation protocol.

## 4.3 Baselines

**Full-attention Baseline (k=0):** Unmodified Llama-2-7B with all 32 layers using full quadratic attention. This is the quality reference point; Δperplexity = 0 by definition.

**Random-k=4 Baseline:** Four layers selected uniformly at random from the 32 available layers. Three random seeds are used; mean Δperplexity reported. This tests whether any 4-layer SWA conversion is harmful, and whether the entropy criterion outperforms random selection (RQ5, pending).

**Last-k=4 Baseline:** The 4 deepest layers (layer indices 28–31) converted to SWA(w=512). This is a common default strategy for structured pruning (remove last layers first), providing a depth-based comparison for the entropy criterion.

*Why these baselines?* Full-attention baseline is the quality reference. Random and last-k baselines together test whether the entropy criterion's selection is principled (better than random) and better than the simplest heuristic (deepest layers). Together, they isolate the contribution of the entropy-based ranking from the contribution of converting any 4 layers.

## 4.4 Evaluation Metrics

**Spearman Rank Correlation (ρ):** Measures consistency of per-layer entropy rankings across calibration subsets. Computed pairwise across subsets A, B, C; gate criterion is min(ρ_AB, ρ_AC, ρ_BC) ≥ 0.8. A correlation above 0.8 indicates that the top-k selected layers are stable across calibration choices, making the criterion practically deterministic.

**Gini Coefficient:** Measures concentration of attention weight distribution within each example: Gini = (∑_{i,j} |w_i - w_j|) / (2 × n × ∑_i w_i), where w_i are the attention weights summed over all heads and positions. Higher Gini indicates more unequal distribution (more concentrated). We use Gini > 0.5 as a practical threshold for "measurable concentration."

**Top-10% Token Share:** The fraction of total attention weight captured by the top-10% highest-weight tokens, averaged across all heads and positions in a layer. Top-10% share > 0.5 means the minority of tokens receives the majority of attention weight — a "heavy-hitter" pattern.

**WikiText-103 Perplexity (PPL):** Standard next-token prediction perplexity on the WikiText-103 test set. Lower is better. We report absolute perplexity and Δperplexity relative to the full-attention baseline. Gate criterion for h-e2: |Δperplexity| ≤ 2.0.

## 4.5 Implementation Details

**Hardware:** Single NVIDIA H100 (80GB). All experiments run with batch size = 1 (required for `output_attentions=True` in float16 without OOM). Attention tensors (1 × 32 × 2048 × 2048) are deleted after entropy computation for each sequence to prevent memory accumulation.

**Entropy Scoring (h-e1):** 100 sequences × 32 layers × single forward pass with `output_attentions=True`. Runtime: approximately 20–30 minutes per subset on H100. Total calibration: ~1 GPU-hour for all three subsets.

**SWA Conversion (h-e2, pending):** Monkey-patch via `swa_forward` override for selected layers. SWA mask: additive float (0.0 for attend, −∞ for block), shape (seq_len × seq_len), computed once and cached. Mask validation via `verify_swa_mechanism()` before evaluation. Evaluation runtime: approximately 2–4 GPU-hours for perplexity on WikiText-103 test set.

**Statistical Significance (h-m1, pending):** Entropy vs random comparison assessed using paired Wilcoxon signed-rank test over per-sequence NLL values, p < 0.05.
