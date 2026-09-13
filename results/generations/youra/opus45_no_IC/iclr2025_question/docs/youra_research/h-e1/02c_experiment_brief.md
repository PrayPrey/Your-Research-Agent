# Experiment Design: H-E1

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** Benchmarks cluster meaningfully (silhouette > 0.5) based on uncertainty distribution similarity
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites - first hypothesis)
**Gate Status:** MUST_WORK | Pass: silhouette > 0.5 | Fail: ABANDON

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (root hypothesis)

### Gate Condition
**Type:** MUST_WORK
**Pass Condition:** Silhouette score > 0.5 on benchmark clustering
**Fail Action:** ABANDON entire verification plan (this is the foundation hypothesis)

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous context to inherit.

### Previous Hypothesis Results (if applicable)
*None* - H-E1 is the root hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "semantic entropy hallucination clustering benchmark"**
- Limited direct results for this specific combination
- Found general references to uncertainty quantification and clustering methods
- Key insight: Need to rely on primary source (Kuhn et al. 2023/2024 Nature paper)

**Query 2: "silhouette score clustering scipy sklearn"**
- Found standard sklearn clustering evaluation patterns
- `sklearn.metrics.silhouette_score(X, labels, metric='precomputed')` for precomputed distance matrices
- Ward hierarchical clustering common for divergence-based clustering

### Archon Code Examples

Limited code examples for semantic entropy clustering specifically. Standard sklearn patterns apply.

### Exa GitHub Implementations

**Repository 1**: jlko/semantic_uncertainty (Official - Kuhn et al. Nature 2024)
- **URL**: https://github.com/jlko/semantic_uncertainty
- **Relevance**: Official implementation of semantic entropy for hallucination detection
- **Architecture**: 
  - `generate_answers.py`: Sample N responses per query
  - `compute_uncertainty_measures.py`: Compute semantic entropy via bidirectional entailment clustering
  - `analyze_results.py`: Aggregate metrics
- **Key Code**:
  ```python
  # From semantic_uncertainty/generate_answers.py
  python generate_answers.py --model_name=Llama-2-7b-chat --dataset=trivia_qa
  
  # Supported datasets: trivia_qa, squad, bioasq, nq, svamp
  # Supported models: Llama-2-7b, Llama-2-13b, Mistral-7B-v0.1, etc.
  ```
- **Dependencies**: Python 3.11, PyTorch 2.1, HuggingFace Transformers

**Repository 2**: cvs-health/uqlm
- **URL**: https://github.com/cvs-health/uqlm
- **Relevance**: Clean API for semantic entropy computation
- **Key Code**:
  ```python
  from uqlm import SemanticEntropy
  se = SemanticEntropy(llm=llm)
  result = se.generate_and_score(prompts, num_responses=5)
  # Returns: entropy values, confidence scores per prompt
  ```

**Repository 3**: OATML/semantic-entropy-probes
- **URL**: https://github.com/OATML/semantic-entropy-probes
- **Relevance**: Efficient SE approximation from hidden states
- **Note**: Beyond PoC scope, but useful reference

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

1. **jlko/semantic_uncertainty** (Official - HIGHEST PRIORITY)
   - Ground truth implementation from Nature 2024 paper
   - Supports exact benchmarks we need: TriviaQA, NQ, SQuAD
   - Already implements semantic entropy via bidirectional entailment

**Recommended Implementation Path:**
- Primary: Use jlko/semantic_uncertainty to generate entropy distributions per benchmark
- Fallback: Adapt cvs-health/uqlm if simpler API needed
- Justification: Official implementation ensures methodology fidelity; benchmarks already supported

### Code Analysis (Serena MCP)

*Skipped* - Code from jlko/semantic_uncertainty is well-documented and sufficiently clear. The workflow is:
1. Generate N responses per query
2. Cluster responses via bidirectional entailment (DeBERTa-based NLI)
3. Compute entropy over semantic clusters
4. Output per-query entropy values

No complex code requiring deeper Serena analysis.

---

## Experiment Specification

### Dataset

**Multi-Benchmark Suite for Cross-Distribution Analysis**

| Benchmark | Source | Samples | Error Type | Domain |
|-----------|--------|---------|------------|--------|
| TriviaQA | HuggingFace | 1,000 | Factual recall | Trivia |
| NaturalQuestions (NQ) | HuggingFace | 1,000 | Factual recall | Wikipedia |
| SQuAD | HuggingFace | 1,000 | Reading comprehension | Wikipedia |
| PopQA | HuggingFace | 1,000 | Entity knowledge | Popular |
| HaluEval-QA | HuggingFace | 1,000 | Hallucination detection | Mixed |
| FEVER | HuggingFace | 1,000 | Claim verification | Wikipedia |

**Total:** 6 benchmarks × 1,000 queries = 6,000 queries

**Type:** standard (public benchmarks)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: See per-benchmark identifiers
- Code: 
  ```python
  from datasets import load_dataset
  
  trivia_qa = load_dataset("trivia_qa", "unfiltered.nocontext", split="validation[:1000]")
  natural_questions = load_dataset("natural_questions", split="validation[:1000]")
  squad = load_dataset("squad", split="validation[:1000]")
  pop_qa = load_dataset("akariasai/PopQA", split="test[:1000]")
  halueval = load_dataset("pminervini/HaluEval", "qa", split="test[:1000]")
  fever = load_dataset("fever", "v1.0", split="labelled_dev[:1000]")
  ```

### Models

#### Baseline Model

**Architecture:** Llama-2-7B (open-weight, accessible logits)
**Type:** Decoder-only Transformer
**Source:** meta-llama/Llama-2-7b-hf via HuggingFace

**Justification:** 
- Same model used in Kuhn et al. 2023/2024
- Open-weight allows access to generation logits for Rao-Blackwell SE estimation
- Standard reference for uncertainty quantification research

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: meta-llama/Llama-2-7b-hf
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-2-7b-hf",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
  ```

#### Proposed Model

**Architecture:** N/A (EXISTENCE hypothesis tests clustering structure, not model modification)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Benchmark Clustering via JS-Divergence
# Based on: Kuhn et al. 2024, Phase 2B verification protocol

import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.metrics import silhouette_score
from scipy.stats import gaussian_kde

class BenchmarkClusteringAnalyzer:
    """
    Cluster benchmarks based on semantic entropy distribution similarity.
    Uses JS-divergence as distance metric, hierarchical clustering.
    """
    def __init__(self, n_generations: int = 10):
        self.n_generations = n_generations
        self.kde_bandwidth = 'scott'
    
    def compute_entropy_distribution(self, entropies: np.ndarray) -> callable:
        """Fit KDE to entropy values for a benchmark."""
        return gaussian_kde(entropies, bw_method=self.kde_bandwidth)
    
    def compute_js_divergence(self, kde1: callable, kde2: callable, 
                               support: np.ndarray = None) -> float:
        """Compute JS-divergence between two entropy distributions."""
        if support is None:
            support = np.linspace(0, 3, 1000)  # entropy range
        p = kde1(support)
        q = kde2(support)
        p = p / p.sum()  # normalize to probability
        q = q / q.sum()
        return jensenshannon(p, q)
    
    def cluster_benchmarks(self, js_matrix: np.ndarray) -> tuple:
        """
        Hierarchical clustering with Ward linkage.
        Returns: (labels, silhouette_score)
        """
        # Convert to condensed distance matrix
        condensed = squareform(js_matrix, checks=False)
        Z = linkage(condensed, method='ward')
        
        # Find optimal number of clusters (2-4 per hypothesis)
        best_score = -1
        best_labels = None
        for n_clusters in range(2, 5):
            labels = fcluster(Z, n_clusters, criterion='maxclust')
            score = silhouette_score(js_matrix, labels, metric='precomputed')
            if score > best_score:
                best_score = score
                best_labels = labels
        
        return best_labels, best_score

# Integration: Run after semantic entropy computation for all benchmarks
# Input: Dict[benchmark_name] -> np.array of entropy values
# Output: silhouette_score (gate metric), cluster_labels
```

### Training Protocol

**N/A for EXISTENCE hypothesis** - This is an analysis experiment, not a training experiment.

**Computation Protocol:**
1. **Generation Phase**: 
   - For each benchmark: sample 1,000 queries
   - For each query: generate 10 responses at temperature=0.7
   - Total: 60,000 generations (6 benchmarks × 1,000 queries × 10 responses)

2. **Entropy Computation Phase**:
   - For each query: cluster responses via bidirectional entailment (DeBERTa-v3-large)
   - Compute semantic entropy per query
   - Output: 6 × 1,000 = 6,000 entropy values (1,000 per benchmark)

3. **Clustering Phase**:
   - Fit KDE to each benchmark's entropy distribution
   - Compute 6×6 JS-divergence matrix
   - Apply hierarchical clustering (Ward linkage)
   - Compute silhouette score

**Seeds:** 1 (fixed at 42 for reproducibility)

**Computational Requirements:**
- GPU: 1× A100 (80GB) or 2× A6000 for Llama-2-7B inference
- Time estimate: ~6-8 hours for generation, ~1 hour for entropy/clustering
- Storage: ~10GB for generations cache

### Evaluation

**Primary Metrics:**
- **Silhouette Score**: Clustering quality measure (target: > 0.5)
  - Range: [-1, 1], higher is better
  - > 0.5 indicates meaningful cluster structure

**Secondary Metrics:**
- Number of clusters discovered (expected: 2-4)
- Within-cluster vs cross-cluster JS-divergence difference

**Success Criteria (PoC: Direction-based):**
- `silhouette_score > 0.5` (GATE CONDITION)
- Clusters align with intuited benchmark families

**Expected Baseline Performance** (from literature):
- No direct prior work on benchmark clustering via SE
- Silhouette > 0.5 is standard threshold for meaningful clustering
- **Source**: sklearn documentation, general clustering literature

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Clustering evaluation
- Library: sklearn.metrics
- Code:
  ```python
  from sklearn.metrics import silhouette_score
  from scipy.cluster.hierarchy import linkage, fcluster
  from scipy.spatial.distance import squareform
  
  # JS-divergence matrix already computed
  silhouette = silhouette_score(js_matrix, cluster_labels, metric='precomputed')
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Silhouette score vs 0.5 threshold bar chart

#### Additional Figures (LLM Autonomous)
Based on clustering analysis:
1. **JS-Divergence Heatmap**: 6×6 matrix showing benchmark distances
2. **Dendrogram**: Hierarchical clustering tree visualization
3. **Entropy Distribution Violin Plot**: Per-benchmark entropy distributions
4. **Silhouette Plot**: Per-sample silhouette coefficients

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- [x] **mechanism_exists**: JS-divergence clustering is a standard, well-defined method
- [x] **mechanism_isolatable**: Clustering is the sole variable; SE computation is established
- [x] **baseline_measurable**: Silhouette score is a standard metric

### Architecture Compatibility
- **Compatible**: No model training required; pure analysis on SE outputs
- **Dependencies**: scipy, sklearn, numpy (standard scientific Python)

### Activation Indicators
- **mechanism_log_message**: "Computing JS-divergence matrix..." → "Clustering complete. Silhouette: X.XX"
- **tensor_shape_change**: KDE distributions: (1000,) per benchmark → (6,6) distance matrix → (6,) cluster labels
- **metric_delta_expected**: silhouette_score ∈ [-1, 1], target > 0.5

### Mechanism Verification Code
```python
def verify_mechanism_activation(js_matrix, cluster_labels, silhouette):
    """Verify clustering mechanism actually executed."""
    checks = {
        'js_matrix_shape': js_matrix.shape == (6, 6),
        'js_matrix_symmetric': np.allclose(js_matrix, js_matrix.T),
        'js_matrix_diagonal_zero': np.allclose(np.diag(js_matrix), 0),
        'cluster_labels_valid': len(np.unique(cluster_labels)) >= 2,
        'silhouette_in_range': -1 <= silhouette <= 1,
    }
    print(f"Mechanism Verification: {all(checks.values())}")
    for check, passed in checks.items():
        print(f"  {check}: {'✓' if passed else '✗'}")
    return all(checks.values())
```

### Hypothesis Support Criteria
- **hypothesis_support_threshold**: silhouette > 0.5
- **hypothesis_support_metric**: sklearn.metrics.silhouette_score

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `silhouette_score > 0.5`

**Gate Outcome:**
- PASS (silhouette > 0.5): Proceed to H-M1 (mechanism hypotheses)
- FAIL (silhouette ≤ 0.5): ABANDON entire verification plan

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

Limited direct sources for semantic entropy benchmark clustering. General clustering methodology well-established.

### B. GitHub Implementations (Exa)

**Repository 1**: jlko/semantic_uncertainty (Official)
- **URL**: https://github.com/jlko/semantic_uncertainty
- **Query Used**: "semantic entropy hallucination detection LLM Python implementation"
- **Relevance**: Official implementation from Kuhn et al. Nature 2024
- **Key Code**: Generation pipeline, entropy computation, entailment clustering
- **Used For**: Semantic entropy computation methodology

**Repository 2**: cvs-health/uqlm
- **URL**: https://github.com/cvs-health/uqlm
- **Query Used**: Same search
- **Relevance**: Clean API for SE computation
- **Used For**: Alternative implementation reference

**Repository 3**: sklearn silhouette_score documentation
- **URL**: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html
- **Query Used**: "JS divergence clustering benchmark silhouette score Python sklearn"
- **Relevance**: Standard clustering evaluation
- **Used For**: Silhouette score computation with precomputed distance matrix

### C. Code Analysis (Serena)

*Skipped* - Code from search results sufficiently clear.

### D. Previous Hypothesis Context

*None* - H-E1 is the root hypothesis.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---------------|-------------|------------------|
| Dataset selection | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Model (Llama-2-7B) | Phase 2B + Exa | Kuhn et al. 2024, jlko/semantic_uncertainty |
| SE computation | Exa | jlko/semantic_uncertainty |
| JS-divergence | Standard | scipy.spatial.distance.jensenshannon |
| Hierarchical clustering | Standard | scipy.cluster.hierarchy.linkage |
| Silhouette score | Standard | sklearn.metrics.silhouette_score |
| Gate threshold (0.5) | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- 2026-08-10: H-E1 set to IN_PROGRESS
- 2026-08-10: Phase 2C experiment design started
- 2026-08-10: Phase 2C experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Skipped - code clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
