# Paper Summary: SWAA — Sliding Window Attention Adaptation

**arXiv:** 2512.10411 | **Year:** 2025 | **Authors:** Yu et al. | **Citations:** 1
**Semantic Scholar ID:** e055a350053b00d53b558ebed30264705dce6bff

---

### Core Contribution

SWAA demonstrates full-attention (FA) to sliding window attention (SWA) adaptation in pre-trained LLMs without retraining from scratch. Key finding: naive FA→SWA replacement causes catastrophic quality collapse. The paper proposes 4 recovery strategies, with lightweight fine-tuning being the primary solution to restore model quality.

### Methodology

- Replaces full-attention layers with SWA in pre-trained transformer models
- Evaluates multiple recovery strategies after the conversion
- Primary recovery: lightweight fine-tuning post-conversion
- Code available at yuyijiong/sliding-window-attention-adaptation (12 stars, requires CUDA≥12.8)

### Experiments & Results

- Naive zero-shot conversion → catastrophic quality collapse
- With fine-tuning recovery: acceptable performance restored
- Reports 30-100% speedup for long-context inference (full-model conversion)
- Does NOT isolate per-layer FLOPS contribution or analyze selective k/32 layer conversion

### Relevance to Gap 1

SWAA defines the novelty gap for this research: it uses fine-tuning as a REQUIRED recovery step. The question this research asks is whether SELECTIVE conversion of k=4 or k=8 (of 32) highest-entropy layers — not all layers — avoids catastrophic collapse without any fine-tuning, since partial conversion may preserve sufficient full-attention context globally.

### Key Limitation (Gap Definition)

No work in SWAA measures zero-shot selective layer conversion accuracy bounds. SWAA converts all layers and then fine-tunes. Whether entropy-guided partial conversion (k/32 << 1) avoids collapse is the open question.
