# Product Requirements Document — H-M2

**Hypothesis ID**: h-m2  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK  
**Generated**: 2026-08-20

---

## Executive Summary

### Objective
Validate that diversity-aware passage selection (MMR-inspired scoring) improves multi-hop QA performance by ≥5% relative accuracy over pure relevance-based eviction at 25% cache budget.

### Success Criterion
ProvenanceCache-Full (diversity-aware) achieves ≥5% relative F1 gain over ProvenanceCache-RelevanceOnly baseline on HotpotQA bridge questions.

### Key Deliverables
1. **ProvenanceCache-Full**: Tiered eviction with MMR diversity scoring
2. **ProvenanceCache-RelevanceOnly**: Ablation baseline (pure relevance, no diversity)
3. **Evaluation Pipeline**: HotpotQA multi-hop QA with F1/EM metrics + statistical validation
4. **Ablation Studies**: Lambda sweep, diversity metric comparison, tier budget allocation

---

## System Requirements

### Functional Requirements

#### FR-1: Dataset Preprocessing Pipeline
**Priority**: P0  
**Description**: Filter and preprocess HotpotQA dev set for multi-hop bridge questions.

**Acceptance Criteria**:
- Download HotpotQA dev distractor set from official URL
- Filter for `type: "bridge"` questions (7,405 samples expected)
- Generate passage embeddings using Contriever model
- Cache embeddings to disk (pickle format) for reuse
- Validate embedding cache integrity (dimension check, sample count)

**API Specification**:
```python
class HotpotQADataset:
    def __init__(self, data_path: str, cache_dir: str):
        """Load HotpotQA dev set and filter bridge questions."""
        
    def filter_bridge_questions(self) -> List[Dict]:
        """Filter for type='bridge' questions.
        
        Returns:
            List of {question_id, question, context (10 paragraphs), answer, supporting_facts}
        """
        
    def embed_passages(self, model: SentenceTransformer) -> Dict[str, torch.Tensor]:
        """Embed all passages using Contriever.
        
        Returns:
            {question_id: {passage_id: embedding_tensor (768-dim)}}
        """
        
    def save_embeddings_cache(self, embeddings: Dict, cache_path: str):
        """Persist embeddings to disk (pickle format)."""
        
    def load_embeddings_cache(self, cache_path: str) -> Dict[str, torch.Tensor]:
        """Load cached embeddings from disk."""
```

**Edge Cases**:
- Malformed questions (missing context/answer): Skip with warning
- Embedding dimension mismatch: Raise validation error
- Cache file corruption: Re-embed all passages

---

#### FR-2: MMR Diversity Scoring Module
**Priority**: P0  
**Description**: Implement MMR-inspired diversity scoring for passage selection.

**Acceptance Criteria**:
- Greedy MMR selection algorithm (λ * relevance - (1-λ) * max_similarity)
- Cosine similarity computation between passage embeddings
- Configurable lambda parameter (default: 0.5)
- Return selected passage indices + MMR scores for analysis

**API Specification**:
```python
class MMRDiversityScorer:
    def __init__(self, lambda_param: float = 0.5):
        """Initialize MMR scorer with relevance-diversity tradeoff parameter.
        
        Args:
            lambda_param: Weight for relevance term (0=pure diversity, 1=pure relevance)
        """
        
    def select_diverse_passages(
        self,
        query_embedding: torch.Tensor,  # (768,)
        passage_embeddings: torch.Tensor,  # (n_passages, 768)
        passage_scores: torch.Tensor,  # (n_passages,) relevance scores
        k: int,
        budget_tokens: int
    ) -> Tuple[List[int], List[float]]:
        """Greedily select k diverse passages within token budget.
        
        Args:
            query_embedding: Query vector (768-dim)
            passage_embeddings: Passage vectors (n_passages × 768)
            passage_scores: Contriever relevance scores (n_passages,)
            k: Target passage count
            budget_tokens: Maximum tokens to retain
            
        Returns:
            (selected_indices, mmr_scores) where:
            - selected_indices: List of passage indices (ranked by MMR score)
            - mmr_scores: MMR score per selected passage
        """
        
    def compute_mmr_score(
        self,
        candidate_idx: int,
        query_embedding: torch.Tensor,
        passage_embeddings: torch.Tensor,
        passage_scores: torch.Tensor,
        selected_indices: List[int]
    ) -> float:
        """Compute MMR score for candidate passage.
        
        Returns:
            MMR score = λ * relevance - (1-λ) * max_similarity
        """
```

**Performance Requirements**:
- Embedding similarity computation: <10ms per passage pair (GPU-accelerated)
- Greedy selection loop: <100ms for 10 passages
- Memory: O(n_passages²) for pairwise similarity matrix

**Edge Cases**:
- Empty selected set (first passage): max_similarity = 0.0
- Lambda = 1.0: Collapse to pure relevance ranking
- Lambda = 0.0: Pure diversity (max dissimilarity)

---

#### FR-3: Tiered Eviction Cache Manager
**Priority**: P0  
**Description**: Implement tiered KV cache eviction with provenance metadata and diversity-aware scoring.

**Acceptance Criteria**:
- Three-tier eviction policy: query tokens > high-relevance > low-relevance
- Configurable tier budget allocation (default: 10% query, 60% high-rel, 30% low-rel)
- Diversity-aware variant: MMR scoring within each tier
- Relevance-only variant: Pure Contriever score sorting (ablation baseline)

**API Specification**:
```python
class ProvenanceCache:
    def __init__(
        self,
        budget_percent: float = 0.25,
        tier_allocation: Tuple[float, float, float] = (0.1, 0.6, 0.3),
        diversity_scorer: Optional[MMRDiversityScorer] = None
    ):
        """Initialize tiered cache with provenance-aware eviction.
        
        Args:
            budget_percent: Cache budget as fraction of full context (0.25 = 25%)
            tier_allocation: Budget split (query, high_rel, low_rel) — must sum to 1.0
            diversity_scorer: Optional MMR scorer (None = relevance-only variant)
        """
        
    def evict_to_budget(
        self,
        kv_cache: torch.Tensor,  # (n_layers, n_tokens, hidden_dim)
        provenance_map: Dict[int, str],  # {token_idx: 'query' | 'passage_0' | ...}
        passage_scores: Dict[str, float],  # {'passage_0': relevance_score, ...}
        passage_embeddings: Dict[str, torch.Tensor],  # {'passage_0': embedding, ...}
        query_embedding: torch.Tensor
    ) -> Tuple[torch.Tensor, Dict[int, str]]:
        """Evict KV cache entries to meet budget constraint.
        
        Returns:
            (retained_kv_cache, retained_provenance_map)
        """
        
    def assign_tier(self, provenance: str, relevance_score: float) -> int:
        """Assign tier based on provenance and relevance threshold.
        
        Returns:
            0 = query tokens (always retained)
            1 = high-relevance passages (top-5 by Contriever score)
            2 = low-relevance passages (remaining)
        """
        
    def select_passages_for_tier(
        self,
        tier: int,
        passages: List[str],
        passage_scores: Dict[str, float],
        passage_embeddings: Dict[str, torch.Tensor],
        query_embedding: torch.Tensor,
        budget_tokens: int
    ) -> List[str]:
        """Select passages within tier budget.
        
        Logic:
            - If diversity_scorer is None: Sort by relevance, greedily retain until budget
            - If diversity_scorer is not None: MMR-based selection within budget
        """
```

**Performance Requirements**:
- Eviction decision: <500ms per inference step
- Memory overhead: <10% of KV cache size (provenance metadata)

**Edge Cases**:
- Query tokens exceed Tier 0 budget: Clip Tier 0, warn user
- Tier allocation sum ≠ 1.0: Raise ValueError
- No high-relevance passages: Tier 1 budget rolls to Tier 2

---

#### FR-4: HotpotQA Evaluation Harness
**Priority**: P0  
**Description**: Run inference with ProvenanceCache variants and compute F1/EM metrics.

**Acceptance Criteria**:
- Load Llama-2-7B model in FP16 precision
- Generate answers for 7,405 bridge questions (batch inference)
- Compute F1 and EM scores using official HotpotQA normalization
- Statistical validation: Paired t-test (diversity vs relevance-only)
- Save predictions to JSON (reproducibility)

**API Specification**:
```python
class HotpotQAEvaluator:
    def __init__(
        self,
        model: AutoModelForCausalLM,
        tokenizer: AutoTokenizer,
        cache_policy: ProvenanceCache
    ):
        """Initialize evaluator with model and cache policy."""
        
    def run_inference(
        self,
        dataset: List[Dict],
        embeddings_cache: Dict[str, torch.Tensor],
        contriever_model: SentenceTransformer
    ) -> List[Dict]:
        """Run inference with cache eviction.
        
        Returns:
            [{question_id, predicted_answer, retained_passages, cache_stats}]
        """
        
    def compute_f1(self, prediction: str, ground_truth: str) -> float:
        """Token-level F1 score (HotpotQA official implementation).
        
        Normalization:
            - Lowercase
            - Strip articles (a/an/the)
            - Remove punctuation
        """
        
    def compute_exact_match(self, prediction: str, ground_truth: str) -> bool:
        """Binary exact match after normalization."""
        
    def evaluate(self, predictions: List[Dict], dataset: List[Dict]) -> Dict:
        """Compute aggregate metrics.
        
        Returns:
            {
                'f1_mean': float,
                'em_mean': float,
                'diversity_coverage': float,  # Avg unique passages retained
                'redundancy_rate': float  # % passages with >0.8 cosine sim
            }
        """
        
    def statistical_test(
        self,
        predictions_a: List[Dict],
        predictions_b: List[Dict],
        dataset: List[Dict]
    ) -> Dict:
        """Paired t-test for F1 score difference.
        
        Returns:
            {
                't_statistic': float,
                'p_value': float,
                'effect_size': float,  # Cohen's d
                'ci_95': (float, float)  # 95% confidence interval
            }
        """
```

**Performance Requirements**:
- Inference throughput: ≥0.25 questions/sec (8 hours for 7,405 questions)
- Checkpoint saving: Every 1,000 questions (recovery from crashes)

**Edge Cases**:
- Model generates empty string: F1 = 0.0, EM = 0.0
- Ground truth list (multiple valid answers): Max F1 across all references
- Prediction timeout (>30s per question): Skip with warning, log failure

---

#### FR-5: Ablation Study Orchestration
**Priority**: P1  
**Description**: Run ablation studies for lambda sweep, diversity metric comparison, tier budget allocation.

**Acceptance Criteria**:
- Lambda sweep: λ ∈ {0.3, 0.5, 0.7, 0.9} (4 runs)
- Diversity metric variants: Embedding cosine, entity overlap, lexical Jaccard (3 runs)
- Tier budget variants: 50/40/10, 60/30/10, 70/20/10 (3 runs)
- Each ablation produces separate predictions JSON + metrics

**API Specification**:
```python
class AblationRunner:
    def __init__(self, base_config: Dict):
        """Initialize ablation runner with base configuration."""
        
    def lambda_sweep(self, lambda_values: List[float]) -> Dict[float, Dict]:
        """Run experiments with varying lambda parameters.
        
        Returns:
            {lambda_value: {f1, em, diversity_coverage, redundancy_rate}}
        """
        
    def diversity_metric_sweep(self, metrics: List[str]) -> Dict[str, Dict]:
        """Run experiments with different diversity metrics.
        
        Args:
            metrics: ['embedding_cosine', 'entity_jaccard', 'lexical_jaccard']
        """
        
    def tier_budget_sweep(
        self,
        allocations: List[Tuple[float, float, float]]
    ) -> Dict[Tuple, Dict]:
        """Run experiments with different tier budget allocations."""
```

---

### Non-Functional Requirements

#### NFR-1: Reproducibility
- Fixed random seed (42) for all stochastic operations
- Deterministic CUDA operations (`torch.backends.cudnn.deterministic = True`)
- Checkpoint saving: Model predictions, intermediate cache states
- Version pinning: transformers==4.36.0, torch==2.1.0, sentence-transformers==2.2.2

#### NFR-2: Performance
- GPU memory: ≤36GB (fit on A100 40GB or V100 32GB)
- Inference throughput: ≥0.25 questions/sec (full dataset in 8 hours)
- Embedding cache size: ≤5GB (74,050 passages × 768 dim × 4 bytes/float)

#### NFR-3: Observability
- Progress logging: Questions processed, time per question, cache hit rate
- Error handling: Log failed questions (timeout, OOM, invalid predictions)
- Metrics tracking: Optional W&B integration for experiment monitoring

---

## Data Specifications

### Dataset: HotpotQA Dev Distractor
- **Source**: http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json
- **License**: CC BY-SA 4.0
- **Size**: 7,405 bridge questions (filtered from 7,405 total dev samples)
- **Format**: JSON with {question, context (10 paragraphs), answer, supporting_facts, type}

### Model: Llama-2-7B
- **HuggingFace ID**: `meta-llama/Llama-2-7b-hf`
- **License**: Llama 2 Community License
- **Precision**: FP16 (mixed precision)
- **Context Window**: 4096 tokens

### Retriever: Contriever
- **HuggingFace ID**: `sentence-transformers/contriever-base-msmarco`
- **Embedding Dimension**: 768
- **Purpose**: Passage relevance scoring + MMR diversity computation

---

## Configuration Schema

### ProvenanceCache-Full (Diversity-Aware)
```yaml
cache_policy:
  type: "provenance_tiered_diversity"
  budget_percent: 0.25
  tier_allocation:
    query: 0.10
    high_relevance: 0.60
    low_relevance: 0.30
  diversity:
    enabled: true
    lambda: 0.5
    metric: "embedding_cosine"
    
model:
  name: "meta-llama/Llama-2-7b-hf"
  precision: "fp16"
  max_new_tokens: 32
  temperature: 0.0
  
retriever:
  name: "sentence-transformers/contriever-base-msmarco"
  top_k: 10
  
evaluation:
  metrics: ["f1", "em", "diversity_coverage", "redundancy_rate"]
  statistical_test: "paired_t_test"
```

### ProvenanceCache-RelevanceOnly (Ablation Baseline)
```yaml
cache_policy:
  type: "provenance_tiered_relevance"
  budget_percent: 0.25
  tier_allocation:
    query: 0.10
    high_relevance: 0.60
    low_relevance: 0.30
  diversity:
    enabled: false  # Only difference from diversity-aware variant
```

---

## Success Metrics

### Primary Metric
**F1 Score Gain**: ProvenanceCache-Full achieves ≥5% relative F1 improvement over ProvenanceCache-RelevanceOnly
- Example: Relevance-only = 58% F1 → Diversity-aware ≥ 61% F1

### Secondary Metrics
1. **Exact Match (EM)**: Binary correctness score
2. **Diversity Coverage**: Avg unique passages retained per question (target: ≥3 for diversity variant vs ≤2.5 for relevance-only)
3. **Redundancy Rate**: % passages with >0.8 cosine similarity (target: ≤20% for diversity variant vs ≥40% for relevance-only)
4. **Statistical Significance**: p < 0.05 on paired t-test (null hypothesis: no F1 difference)

### Failure Criterion
If diversity-aware variant achieves <5% relative gain (or negative gain), fall back to relevance-only tiering (simpler, still novel vs H2O).

---

## Deliverables Checklist

### Code Artifacts
- [ ] `dataset_loader.py`: HotpotQA filtering, embedding cache
- [ ] `mmr_diversity.py`: MMR scoring module
- [ ] `provenance_cache.py`: Tiered eviction policy (diversity + relevance-only variants)
- [ ] `evaluation.py`: F1/EM computation, statistical tests
- [ ] `run_experiment.py`: Main orchestration script
- [ ] `ablation_runner.py`: Lambda sweep, diversity metric comparison

### Data Artifacts
- [ ] `hotpotqa_bridge_filtered.json`: Filtered dataset
- [ ] `passage_embeddings_cache.pkl`: Precomputed Contriever embeddings
- [ ] `predictions_provenance_full.json`: Diversity-aware predictions
- [ ] `predictions_relevance_only.json`: Relevance-only predictions

### Analysis Artifacts
- [ ] `metrics.json`: F1, EM, diversity stats per condition
- [ ] `statistical_tests.json`: t-test results, effect size, confidence intervals
- [ ] `ablation_results.json`: Lambda sweep, diversity metric comparison, tier budget sweep
- [ ] `04_validation.md`: Qualitative analysis (10 success cases, 10 failure cases)

---

## Open Questions & Risks

### Risk 1: Embedding Diversity ≠ Reasoning Diversity
**Concern**: Semantically dissimilar passages may share critical temporal/causal links (Prof. Rex feedback).  
**Mitigation**: Ablation with entity overlap diversity metric (entities capture temporal dependencies).

### Risk 2: 25% Budget Too Small for Diversity
**Concern**: Diversity variant evicts high-relevance passages to fit diverse low-relevance passages.  
**Detection**: Tier 1 retention rate < 80% in diversity variant.  
**Mitigation**: Budget sweep ablation (30%, 35%, 40% cache budgets).

### Risk 3: Lambda Miscalibration
**Concern**: λ=0.5 over-penalizes relevance, retains low-quality diverse passages.  
**Detection**: Diversity variant F1 drops below H2O baseline.  
**Mitigation**: Lambda sweep ablation (λ=0.7, 0.8, 0.9 toward relevance).

---

## Implementation Timeline

| **Phase** | **Duration** | **Deliverables** |
|----------|-------------|-----------------|
| Dataset Preprocessing | 2 hours | Filtered dataset, embedding cache |
| MMR Module | 3 hours | `mmr_diversity.py`, unit tests |
| Cache Manager | 4 hours | `provenance_cache.py`, diversity + relevance variants |
| Evaluation Harness | 3 hours | `evaluation.py`, F1/EM computation |
| Main Experiment | 8 hours | Predictions JSON, metrics JSON (GPU inference) |
| Ablation Studies | 12 hours | Lambda sweep, diversity metric comparison (GPU) |
| Analysis & Reporting | 2 hours | `04_validation.md`, qualitative case studies |

**Total Estimated Time**: ~34 hours (includes 28 GPU-hours for inference)

---

## Appendix: API Usage Examples

### Example 1: Dataset Preprocessing
```python
from dataset_loader import HotpotQADataset
from sentence_transformers import SentenceTransformer

# Load dataset
dataset = HotpotQADataset(
    data_path="data/hotpot_dev_distractor_v1.json",
    cache_dir="data/cache"
)

# Filter bridge questions
bridge_questions = dataset.filter_bridge_questions()
print(f"Filtered {len(bridge_questions)} bridge questions")

# Embed passages
contriever = SentenceTransformer('sentence-transformers/contriever-base-msmarco')
embeddings = dataset.embed_passages(contriever)

# Cache embeddings
dataset.save_embeddings_cache(embeddings, "data/passage_embeddings_cache.pkl")
```

### Example 2: MMR Diversity Scoring
```python
from mmr_diversity import MMRDiversityScorer
import torch

# Initialize scorer
mmr_scorer = MMRDiversityScorer(lambda_param=0.5)

# Select diverse passages
query_emb = torch.randn(768)  # Query embedding
passage_embs = torch.randn(10, 768)  # 10 passage embeddings
relevance_scores = torch.rand(10)  # Contriever scores

selected_indices, mmr_scores = mmr_scorer.select_diverse_passages(
    query_emb, passage_embs, relevance_scores, k=3, budget_tokens=300
)

print(f"Selected passages: {selected_indices}")
print(f"MMR scores: {mmr_scores}")
```

### Example 3: Tiered Cache Eviction
```python
from provenance_cache import ProvenanceCache
from mmr_diversity import MMRDiversityScorer

# Diversity-aware variant
diversity_scorer = MMRDiversityScorer(lambda_param=0.5)
cache_full = ProvenanceCache(
    budget_percent=0.25,
    tier_allocation=(0.1, 0.6, 0.3),
    diversity_scorer=diversity_scorer
)

# Relevance-only variant (ablation)
cache_relevance = ProvenanceCache(
    budget_percent=0.25,
    tier_allocation=(0.1, 0.6, 0.3),
    diversity_scorer=None  # No diversity scoring
)

# Run eviction
retained_kv, retained_prov = cache_full.evict_to_budget(
    kv_cache, provenance_map, passage_scores, passage_embeddings, query_emb
)
```

---

**Document Status**: READY FOR ARCHITECTURE DESIGN  
**Next Phase**: Generate Architecture, Logic, Config documents in parallel
