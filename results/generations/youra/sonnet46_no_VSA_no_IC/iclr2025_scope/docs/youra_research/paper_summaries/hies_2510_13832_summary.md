# Paper Summary: HIES — Head Importance-Entropy Score

**arXiv:** 2510.13832 | **Year:** 2025 | **Authors:** Choi et al. | **Citations:** 1
**Semantic Scholar ID:** bf7171b89dfae23c357db155343292b525f28cb1

---

### Core Contribution

HIES proposes combining attention entropy with gradient-based importance scores for attention HEAD pruning. Key result: entropy provides complementary signal to importance scores, yielding +15.2% quality improvement over importance-only pruning.

### Methodology

- Computes per-head entropy: H = -Σ p·log(p) over attention distributions
- Combines entropy with gradient importance: HIES = α·entropy + (1-α)·importance
- Calibration set: standard sentences; output_attentions=True for entropy extraction
- Validated primarily on encoder-based transformers (BERT-family)

### Experiments & Results

- +15.2% quality improvement vs importance-only pruning
- Entropy signal is complementary, not redundant, to gradient importance
- Head-level granularity (not layer-level)
- Encoder-focused (not causal decoder LLMs like Llama-2-7B)

### Relevance to Gap 2

HIES validates entropy as a useful selection signal for attention operations — but at HEAD level in encoders, not LAYER level in causal decoders. The extension question for this research: does aggregating head-level entropy to layer-level (mean across heads and positions) produce a valid layer-level convertibility signal for SWA replacement in causal decoder LLMs?

### Key Transfer Assumption

Gap 2 asks whether per-layer entropy (averaged across all heads and all positions) in Llama-2-7B, measured on 100 calibration sequences, predicts which layers tolerate SWA conversion. HIES shows entropy works at head level — the layer-level aggregation transfer is the novel claim.
