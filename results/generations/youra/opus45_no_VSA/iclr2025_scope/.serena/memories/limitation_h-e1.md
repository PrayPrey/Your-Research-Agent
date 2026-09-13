# Limitation Record: H-E1 Infrastructure Failure

**Hypothesis:** h-e1 - Needle tokens show normalized entropy < median haystack entropy by ≥0.5σ
**Date:** 2026-08-09
**Outcome:** INFRASTRUCTURE_FAILURE (not hypothesis falsification)

## Failure Summary

8K sequence attention entropy analysis on LLaMA-2-7B-chat failed due to CUDA OOM after 14/500 samples.

## Root Cause

`output_attentions=True` in HuggingFace Transformers stores full attention matrices regardless of hook-based extraction:
- Per-layer attention: 1 × 32 × 8192 × 8192 × 2 bytes = ~4GB
- 32 layers × 4GB = ~128GB theoretical (though only ~8GB concurrent due to sequential execution)
- Combined with 14GB model weights exceeded H100 95GB capacity

## Lessons for Future Experiments

1. **Pre-flight memory estimation required** before long-context attention analysis
2. **Hook optimization insufficient**: Transformers API stores attention regardless of hooks
3. **Alternatives for 8K+ entropy analysis:**
   - FlashAttention with custom CUDA kernels for entropy
   - Smaller models (Phi-3-mini, Qwen2-1.5B)
   - Sequence length reduction to 4K
   - Layer-wise processing with explicit memory management

## Retry Path

Hypothesis NOT falsified - retry with:
1. seq_len=4096 (4x memory reduction)
2. OR model=Qwen2-1.5B-Instruct (smaller, supports eager attention)
3. OR custom FlashAttention entropy kernel

## References

- `mem:entropy-guided-attention` for entropy computation patterns
- NVIDIA/RULER for NIAH benchmark
