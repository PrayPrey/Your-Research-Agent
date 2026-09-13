# Architecture — H-M2

**Hypothesis ID**: h-m2  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK  
**Generated**: 2026-08-20

Applied: tiered cache eviction, MMR diversity scoring

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Patterns found from h-m1 code  
**Analyzed Path**: docs/youra_research/h-m1/code/  
**Findings**: Reusable cache_policy.py (ProvenanceCacheConfig, tiered eviction structure), data.py (dataset loader pattern)

---

## System Overview

Three-tier KV cache eviction with MMR-based diversity scoring for multi-hop QA.

**Components**:
- Dataset loader (HotpotQA filtering, passage embedding cache)
- MMR diversity scorer (greedy selection with relevance-diversity tradeoff)
- Provenance cache manager (base class + diversity/relevance-only subclasses)
- Evaluation harness (F1/EM metrics, statistical tests)

**Data Flow**:
```
HotpotQA raw → filter bridge questions → embed passages (Contriever) → cache embeddings
→ inference loop (Llama-2-7B) → tiered eviction (MMR or relevance-only)
→ generate answer → compute F1/EM → statistical test
```

---

## Module Specifications

### HotpotQADataset (`data/hotpotqa_loader.py`)

**Dependencies**: datasets, sentence-transformers, pickle

```python
class HotpotQADataset:
    def __init__(self, data_path: str, cache_dir: str): ...
    def filter_bridge_questions(self) -> List[Dict]: ...
    def embed_passages(self, model: SentenceTransformer) -> Dict[str, Tensor]: ...
    def save_embeddings_cache(self, embeddings: Dict, path: str): ...
    def load_embeddings_cache(self, path: str) -> Dict[str, Tensor]: ...
```

---

### MMRDiversityScorer (`mmr_diversity.py`)

**Dependencies**: torch, sentence-transformers.util

```python
class MMRDiversityScorer:
    def __init__(self, lambda_param: float = 0.5): ...
    
    def select_diverse_passages(
        self,
        query_embedding: Tensor,
        passage_embeddings: Tensor,
        passage_scores: Tensor,
        k: int,
        budget_tokens: int
    ) -> Tuple[List[int], List[float]]: ...
    
    def compute_mmr_score(
        self,
        candidate_idx: int,
        query_embedding: Tensor,
        passage_embeddings: Tensor,
        passage_scores: Tensor,
        selected_indices: List[int]
    ) -> float: ...
```

**Greedy Algorithm**:
1. Start with empty selected set
2. For each iteration: compute `λ * relevance - (1-λ) * max_similarity` for all candidates
3. Select highest MMR score, add to selected set
4. Repeat until k passages selected or budget exhausted

---

### ProvenanceCache (`cache_policy.py`)

**Dependencies**: torch, MMRDiversityScorer

```python
@dataclass
class ProvenanceCacheConfig:
    budget_percent: float = 0.25
    tier_allocation: Tuple[float, float, float] = (0.1, 0.6, 0.3)
    high_rel_threshold: int = 5

class ProvenanceCacheBase:
    def __init__(self, config: ProvenanceCacheConfig): ...
    
    def evict_to_budget(
        self,
        kv_cache: Tensor,
        provenance_map: Dict[int, str],
        passage_scores: Dict[str, float],
        passage_embeddings: Dict[str, Tensor],
        query_embedding: Tensor
    ) -> Tuple[Tensor, Dict[int, str]]: ...
    
    def assign_tier(self, provenance: str, relevance_score: float) -> int: ...
    
    def select_passages_for_tier(
        self, tier: int, passages: List[str], budget_tokens: int
    ) -> List[str]: ...  # Abstract method

class ProvenanceCacheFull(ProvenanceCacheBase):
    def __init__(self, config: ProvenanceCacheConfig, mmr_scorer: MMRDiversityScorer): ...
    def select_passages_for_tier(self, ...) -> List[str]: 
        # Use mmr_scorer.select_diverse_passages()
        ...

class ProvenanceCacheRelevanceOnly(ProvenanceCacheBase):
    def select_passages_for_tier(self, ...) -> List[str]:
        # Sort by relevance score, greedily retain until budget
        ...
```

**Tier Assignment**:
- Tier 0: provenance == 'query' → always retained
- Tier 1: top-k passages by Contriever score (k=5)
- Tier 2: remaining passages

---

### HotpotQAEvaluator (`evaluate.py`)

**Dependencies**: transformers, scipy.stats

```python
class HotpotQAEvaluator:
    def __init__(
        self,
        model: AutoModelForCausalLM,
        tokenizer: AutoTokenizer,
        cache_policy: ProvenanceCacheBase
    ): ...
    
    def run_inference(
        self,
        dataset: List[Dict],
        embeddings_cache: Dict[str, Tensor],
        contriever: SentenceTransformer
    ) -> List[Dict]: ...
    
    def normalize_answer(self, s: str) -> str: ...
    def compute_f1(self, pred: str, gt: str) -> float: ...
    def compute_exact_match(self, pred: str, gt: str) -> bool: ...
    
    def evaluate(self, predictions: List[Dict], dataset: List[Dict]) -> Dict: ...
    
    def statistical_test(
        self, preds_a: List[Dict], preds_b: List[Dict], dataset: List[Dict]
    ) -> Dict: ...  # Paired t-test, Cohen's d
```

**Metrics**:
- F1: token-level overlap (precision + recall harmonic mean)
- EM: binary exact match after normalization
- Diversity coverage: unique passage count per question
- Redundancy rate: % passages with >0.8 cosine similarity

---

### AblationRunner (`ablation_runner.py`)

**Dependencies**: yaml, json

```python
class AblationRunner:
    def __init__(self, base_config_path: str): ...
    
    def lambda_sweep(self, lambda_values: List[float]) -> Dict[float, Dict]: ...
    def diversity_metric_sweep(self, metrics: List[str]) -> Dict[str, Dict]: ...
    def tier_budget_sweep(self, allocations: List[Tuple]) -> Dict[Tuple, Dict]: ...
    
    def save_results(self, results: Dict, output_path: str): ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-m1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ProvenanceCacheConfig | `from h_m1.cache_policy import ProvenanceCacheConfig` | `h-m1/code/cache_policy.py` |
| LongBenchLoader pattern | Reference only (different dataset) | `h-m1/code/data.py` |

**Note**: h-m2 implements new HotpotQA loader (h-m1 used LongBench), but reuses cache config structure.

---

## File Structure

```
h-m2/code/
├── data/
│   └── hotpotqa_loader.py
├── mmr_diversity.py
├── cache_policy.py
├── evaluate.py
├── ablation_runner.py
└── main.py

h-m2/configs/
├── provenance_full.yaml
├── provenance_relevance_only.yaml
└── ablation_lambda_sweep.yaml

h-m2/outputs/
├── predictions_provenance_full.json
├── predictions_relevance_only.json
├── metrics.json
└── statistical_tests.json
```

---

## Memory Management

### GPU Memory Budget (≤36GB)

| Component | Size | Notes |
|-----------|------|-------|
| Llama-2-7B FP16 | ~14GB | Model weights |
| KV cache (full) | ~8GB | 4096 tokens × 32 layers |
| KV cache (25% budget) | ~2GB | After eviction |
| Passage embeddings | ~5GB | 74,050 passages × 768 dim × 4 bytes |
| Working memory | ~7GB | Inference buffers |
| **Total** | **~28GB** | Fits A100 40GB, V100 32GB |

### Embedding Cache Strategy

- **Precompute**: Embed all HotpotQA passages once, cache to disk (pickle format)
- **Load on demand**: Memory-map embeddings, load per-question subsets
- **Cache hit rate**: 100% (all passages pre-embedded)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Dataset preprocessing | Filter HotpotQA bridge questions, embed passages, save cache | 9 | 2+3+2+2 (download+filter+embed+validate) |
| M2-2 | MMR diversity module | Implement greedy MMR selection, cosine similarity computation | 12 | 3+4+3+2 (algorithm+scoring+selection+tests) |
| M2-3 | Cache base class | Tiered eviction framework, provenance tier assignment | 11 | 3+4+2+2 (structure+tiers+budget+integration) |
| M2-4 | Diversity cache variant | ProvenanceCacheFull with MMR passage selection | 10 | 3+3+2+2 (subclass+MMR integration+tier logic+tests) |
| M2-5 | Relevance-only variant | ProvenanceCacheRelevanceOnly with pure relevance sorting | 8 | 2+2+2+2 (subclass+sorting+tier logic+tests) |
| M2-6 | Evaluation harness | Inference loop, F1/EM computation, statistical tests | 14 | 4+3+3+2+2 (inference+metrics+normalization+t-test+save) |
| M2-7 | Ablation orchestration | Lambda sweep, diversity metric comparison, tier budget variants | 13 | 4+3+3+3 (config loading+lambda sweep+metric sweep+budget sweep) |
| M2-8 | Main experiment script | Orchestrate data loading, inference, evaluation, save results | 10 | 3+3+2+2 (integration+logging+checkpoints+error handling) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [M2-6], Medium(9-13): [M2-1,M2-2,M2-3,M2-4,M2-7,M2-8], Low(4-8): [M2-5]

**Total Complexity**: 87 (Medium-High)

**Breakdown Guide**:
- Module_Size: 1-5 (lines of code, interface complexity)
- Dependencies: 1-5 (external libs, module coupling)
- Algorithm: 1-5 (logic complexity, greedy vs optimal)
- Integration: 1-5 (system coupling, testing burden)

---

## Component Interaction

**Inference Flow**:
1. HotpotQADataset loads bridge questions, loads cached embeddings
2. HotpotQAEvaluator constructs prompt from question + context
3. Llama-2-7B generates tokens autoregressively
4. After each forward pass:
   - ProvenanceCache assigns tier to new KV entries (based on passage provenance)
   - Eviction triggered if total tokens > budget
   - ProvenanceCacheFull: MMR scoring within each tier
   - ProvenanceCacheRelevanceOnly: relevance sorting within each tier
5. Generate answer (greedy decoding)
6. Compute F1/EM vs ground truth
7. Statistical test: paired t-test between diversity vs relevance-only

**Ablation Flow**:
1. AblationRunner loads base config
2. Sweep lambda ∈ {0.3, 0.5, 0.7, 0.9}: 4 ProvenanceCacheFull runs
3. Sweep diversity metric: embedding/entity/lexical: 3 runs
4. Sweep tier budget allocation: 3 allocations × 1 run
5. Save per-ablation metrics to JSON

---

## Performance Constraints

### NFR-2 Targets

| Metric | Target | Notes |
|--------|--------|-------|
| GPU memory | ≤36GB | Fit A100 40GB, V100 32GB |
| Inference throughput | ≥0.25 questions/sec | 7,405 questions in 8 hours |
| Eviction latency | <500ms per step | MMR greedy selection overhead |
| Embedding cache size | ≤5GB | 74,050 passages × 768 dim |

### Bottleneck Analysis

- **MMR selection**: O(k × n²) pairwise similarity → GPU-accelerate cosine similarity
- **Embedding lookup**: Memory-mapped file → avoid loading full 5GB cache
- **KV cache eviction**: Tier sorting O(n log n) → acceptable for n=2000 tokens

---

## Validation Checks

**Architecture Completeness**:
- [x] No ASCII diagrams (bullet lists only)
- [x] Module sections = interface code only
- [x] 6-12 Epic tasks (8 tasks)
- [x] Total length < 500 lines
- [x] Codebase Analysis (Serena) section included
- [x] External Dependencies section (h-m1 reference)
- [x] Import paths verified from actual code (cache_policy.py structure)

**Serena MCP Validation**:
- [x] Base hypothesis exists → Serena called on h-m1 code
- [x] Import paths verified from actual files (not specs)

**Base Hypothesis Checks**:
- [x] Read actual code structure from h-m1/code/
- [x] Import paths verified (ProvenanceCacheConfig, cache_policy.py pattern)
- [x] External Dependencies section included with file locations
