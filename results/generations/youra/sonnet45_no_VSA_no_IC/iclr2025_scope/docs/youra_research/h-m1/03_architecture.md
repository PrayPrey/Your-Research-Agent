# Architecture: H-M1 ProvenanceCache

**Date:** 2026-08-20  
**Hypothesis:** Provenance-aware tiered KV cache eviction  
**Applied Pattern:** Flash-attention KV cache, HuggingFace transformers

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: No existing code, implementing from spec + H2O baseline reference

---

## System Overview

Single-script comparison experiment: 4 cache policies (FullKV, H2O, ProvenanceCache, Random) on LongBench single-hop QA with Llama-2-7B.

**Data Flow:**
```
LongBench → Contriever retrieval → Provenance metadata → Generate (4 cache policies) → F1 eval
```

**Core Components:**
1. Dataset loader (LongBench)
2. Retrieval pipeline (Contriever)
3. Cache policies (4 implementations)
4. Generation harness
5. Evaluation (F1 scoring)

---

## Module Specifications

### DataLoader (`data.py`)

**Dependencies:** datasets, transformers

```python
class LongBenchLoader:
    def __init__(self, tasks: list[str], tokenizer): ...
    def load(self) -> list[dict]: ...  # Returns [{"input": q, "context": doc, "answers": [a]}]
```

### RetrievalPipeline (`retrieval.py`)

**Dependencies:** transformers (Contriever)

```python
class ContrieverRetriever:
    def __init__(self, model_name: str = "facebook/contriever-msmarco"): ...
    def retrieve(self, query: str, document: str, top_k: int = 5) -> list[tuple[str, float]]: ...  # (passage, score)
    def chunk_document(self, doc: str, chunk_size: int = 512, overlap: int = 128) -> list[str]: ...
```

### CachePolicies (`cache.py`)

**Dependencies:** torch

```python
class FullKVCache:
    def evict(self, k: Tensor, v: Tensor) -> tuple[Tensor, Tensor]: ...

class H2OCache:
    def __init__(self, heavy_ratio: float = 0.125, recent_ratio: float = 0.125, n_sink: int = 4): ...
    def update_attention(self, attn_weights: Tensor): ...
    def evict(self, k: Tensor, v: Tensor, max_len: int) -> tuple[Tensor, Tensor]: ...

class ProvenanceCache:
    def __init__(self, budget_ratio: float = 0.25): ...
    def register_provenance(self, token_indices: list[int], types: list[str], scores: list[float]): ...
    def evict(self, k: Tensor, v: Tensor, max_len: int) -> tuple[Tensor, Tensor]: ...

class RandomCache:
    def __init__(self, budget_ratio: float = 0.25): ...
    def evict(self, k: Tensor, v: Tensor, max_len: int) -> tuple[Tensor, Tensor]: ...
```

### GenerationHarness (`generate.py`)

**Dependencies:** transformers, cache.py

```python
class CachedGenerator:
    def __init__(self, model, tokenizer, cache_policy): ...
    def generate(self, prompt: str, max_new_tokens: int = 100) -> str: ...
```

### Evaluation (`evaluate.py`)

**Dependencies:** scipy

```python
def compute_f1(prediction: str, ground_truths: list[str]) -> float: ...
def normalize_answer(s: str) -> str: ...
def run_evaluation(results: list[dict]) -> dict: ...  # Returns {"f1": float, "em": float, ...}
```

### Visualization (`visualize.py`)

**Dependencies:** matplotlib

```python
def plot_gate_metrics(scores: dict[str, float], threshold: float = 1.05): ...
def plot_cache_budget_curve(budget_scores: dict): ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup | Environment + model download | 6 | 1(clone)+1(deps)+2(llama)+2(contriever) |
| A-2 | Data | LongBench loader + tokenization | 8 | 2(load)+2(tokenize)+2(format)+2(validate) |
| A-3 | Retrieval | Contriever chunking + scoring | 10 | 3(chunk)+3(retrieve)+2(score)+2(test) |
| A-4 | Baselines | FullKV + H2O + Random | 14 | 2(full)+5(h2o)+3(random)+4(test) |
| A-5 | ProvenanceCache | Tiered eviction logic | 12 | 3(register)+4(evict)+3(tier)+2(test) |
| A-6 | Generation | Harness with 4 policies | 9 | 3(integrate)+3(loop)+2(collect)+1(checkpoint) |
| A-7 | Evaluation | F1 + stats + validation.md | 11 | 3(f1)+2(stats)+3(plots)+3(report) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-3, A-5, A-6, A-7], Low(4-8): [A-1, A-2]

---

## Integration Strategy

### H2O Baseline Adaptation

**Source:** FMInference/H2O (github.com/FMInference/H2O)  
**Approach:** Extract eviction algorithm, adapt for LongBench

**Key Implementation:**
```python
# From H2O utils_real_drop/
class H2OCache:
    accumulated_attention = {}  # token_idx -> cumulative_score
    
    def update_attention(self, attn_weights):
        # Sum attention received by each token
        token_importance = attn_weights.sum(dim=(1, 2))
        for idx in range(token_importance.shape[1]):
            self.accumulated_attention[idx] = self.accumulated_attention.get(idx, 0.0) + token_importance[0, idx].item()
    
    def evict(self, k, v, max_len):
        # Tier 0: sinks (first n_sink tokens)
        # Tier 1: heavy hitters (top-K by accumulated attention)
        # Tier 2: recent (sliding window)
        # Return: compressed k, v
```

### Provenance Metadata Flow

1. **Retrieval:** Contriever scores passages
2. **Registration:** Map token positions to (type, score)
3. **Eviction:** Use metadata instead of attention for tier assignment

```python
# Provenance registration
retriever = ContrieverRetriever()
passages, scores = retriever.retrieve(query, document, top_k=5)
token_types = ["query"] * len(query_tokens) + ["high_rel_passage"] * len(top3_tokens) + ["low_rel_passage"] * len(rest_tokens)
provenance_cache.register_provenance(token_indices, token_types, scores)

# Later: eviction without attention tracking
k_compressed, v_compressed = provenance_cache.evict(k, v, max_len)
```

---

## Deployment Considerations

### GPU/CPU Support

**GPU (Preferred):**
- Llama-2-7B in FP16: ~14GB VRAM
- Contriever: ~2GB VRAM
- Total: ~16GB (single GPU)

**CPU Fallback:**
- Load models with `device_map="cpu"`
- FP32 precision (no mixed precision)
- Runtime: ~10x slower (80 GPU-hours → 800 CPU-hours)

### Checkpointing

**Save every 50 samples:**
```python
checkpoint = {
    "results": accumulated_results,
    "sample_idx": current_idx,
    "condition": current_condition
}
torch.save(checkpoint, f"checkpoint_{condition}_{idx}.pt")
```

**Resume logic:**
```python
if checkpoint_exists:
    checkpoint = torch.load(checkpoint_path)
    start_idx = checkpoint["sample_idx"]
    results = checkpoint["results"]
```

### Error Handling

**Graceful degradation:**
- Single sample failure → log + continue
- Out of memory → reduce batch size to 1
- CUDA unavailable → fallback to CPU

**Logging:**
```python
logging.info(f"Sample {idx}: cache_size={k.shape[2]}, evicted={evicted_count}, latency={time:.2f}s")
```

---

## File Structure

```
h-m1/code/
├── data.py          # LongBench loader
├── retrieval.py     # Contriever retrieval
├── cache.py         # 4 cache policies
├── generate.py      # Generation harness
├── evaluate.py      # F1 scoring + stats
├── visualize.py     # Plots
├── main.py          # Orchestration
└── requirements.txt
```

---

**Total Complexity:** 70 (moderate, within Tier 2.5 budget)  
**Critical Path:** A-4 (H2O baseline) → A-5 (ProvenanceCache) → A-6 (generation) → A-7 (eval)
