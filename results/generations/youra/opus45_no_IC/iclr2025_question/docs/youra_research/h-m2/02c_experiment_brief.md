# Experiment Design: H-M2

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** Benchmarks testing similar error processes exhibit similar uncertainty distributions (JS-divergence < 0.15)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing causal relationship between error families and distribution similarity.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 PASS: p=0.000144, d=1.325)
**Gate Status:** SHOULD_WORK (Fail Action: EXPLORE)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (COMPLETED)

### Gate Condition
**Primary:** Same-family JS-divergence < Cross-family JS-divergence (p < 0.05)
**Secondary:** Mean same-family JS-div < 0.15

---

## Continuation Context

H-M2 validates that the clustering structure observed in H-E1 aligns with *intuited* error families. H-E1 showed silhouette=0.8245 with 2 clusters, but this was data-driven. H-M2 tests whether benchmarks we *expect* to test similar error processes (based on task semantics) actually produce similar uncertainty distributions.

### Previous Hypothesis Results

**H-E1 (Foundation):**
- Silhouette score: 0.8245 > 0.5 (PASS)
- Two clusters emerged: Factual Recall (TriviaQA, NQ, SQuAD) and Entity/Claim (PopQA, HaluEval, FEVER)
- Within-cluster mean JS-div: 0.056 (Cluster 1), 0.108 (Cluster 2)
- Cross-cluster mean JS-div: 0.471

**H-M1 (Mechanism - Uncertainty-Error Link):**
- Semantic entropy separates correct/incorrect responses (d=1.325)
- AUROC: 0.793 for hallucination detection

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No directly relevant past cases for JS-divergence benchmark comparison. General KDE/distribution comparison patterns found in diffusion model literature but not applicable.

### Archon Code Examples

scipy.spatial.distance.jensenshannon available for distribution comparison. KDE implementations compared: scipy.stats.gaussian_kde (simple), KDEpy.FFTKDE (fastest for large N).

### Exa GitHub Implementations

**Primary Source:** scipy.spatial.distance.jensenshannon
- Computes Jensen-Shannon distance (square root of divergence)
- Normalizes probability arrays automatically
- Supports axis parameter for batch computation

**KDE Options:**
- `scipy.stats.gaussian_kde` - Scott/Silverman bandwidth, single kernel
- `KDEpy.FFTKDE` - 100x faster, ISJ bandwidth selection, 9 kernels

### 🎯 Implementation Priority Assessment

**CRITICAL: Reuse H-E1 computed JS-divergence matrix**

**Recommended Implementation Path:**
- Primary: Load H-E1 JS-divergence matrix from saved artifacts
- Fallback: Recompute from H-E1 entropy distributions if artifacts unavailable
- Justification: H-E1 already computed full 6×6 JS-divergence matrix with validated pipeline

### Code Analysis (Serena MCP)

No existing codebase analysis needed. H-M2 is a statistical analysis of H-E1 outputs.

---

## Experiment Specification

### Dataset

**Type:** Computed artifact from H-E1
**Source:** `h-e1/results/js_divergence_matrix.npy` (or recompute from entropy distributions)

**Benchmark Categorization (Intuited Error Families):**

| Family | Benchmarks | Error Type |
|--------|------------|------------|
| Factual Recall | TriviaQA, NaturalQuestions, SQuAD | Knowledge gaps, memory errors |
| Entity/Claim | PopQA, HaluEval-QA, FEVER | Entity confusion, claim fabrication |

**All 15 Pairwise Comparisons:**

| Pair | Intuited Category |
|------|-------------------|
| TriviaQA-NQ | Same (Factual) |
| TriviaQA-SQuAD | Same (Factual) |
| NQ-SQuAD | Same (Factual) |
| PopQA-HaluEval | Same (Entity/Claim) |
| PopQA-FEVER | Same (Entity/Claim) |
| HaluEval-FEVER | Same (Entity/Claim) |
| TriviaQA-PopQA | Cross |
| TriviaQA-HaluEval | Cross |
| TriviaQA-FEVER | Cross |
| NQ-PopQA | Cross |
| NQ-HaluEval | Cross |
| NQ-FEVER | Cross |
| SQuAD-PopQA | Cross |
| SQuAD-HaluEval | Cross |
| SQuAD-FEVER | Cross |

**Loading Information** (for Phase 4 download):
- Method: File load (numpy)
- Identifier: `h-e1/results/js_divergence_matrix.npy`
- Code:
```python
import numpy as np
js_matrix = np.load("h-e1/results/js_divergence_matrix.npy")
benchmark_names = ["trivia_qa", "natural_questions", "squad", "pop_qa", "halueval_qa", "fever"]
```

### Models

#### Baseline Model

**No model required** - H-M2 is statistical analysis of H-E1 outputs.

**Loading Information** (for Phase 4 download):
- Method: N/A
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** Statistical hypothesis test on pre-computed JS-divergence values

**Core Mechanism Implementation:**

```python
import numpy as np
from scipy import stats

def test_error_family_hypothesis(js_matrix: np.ndarray, benchmark_names: list) -> dict:
    """
    Test H-M2: Same-family benchmarks have lower JS-divergence than cross-family.
    
    Args:
        js_matrix: 6x6 symmetric JS-divergence matrix
        benchmark_names: List of benchmark names in matrix order
    
    Returns:
        dict with p_value, same_family_mean, cross_family_mean, effect_size
    """
    # Define intuited error families
    factual_family = {"trivia_qa", "natural_questions", "squad"}
    entity_family = {"pop_qa", "halueval_qa", "fever"}
    
    same_family_js = []
    cross_family_js = []
    
    n = len(benchmark_names)
    for i in range(n):
        for j in range(i + 1, n):
            js_val = js_matrix[i, j]
            b1, b2 = benchmark_names[i], benchmark_names[j]
            
            # Determine if same family
            both_factual = b1 in factual_family and b2 in factual_family
            both_entity = b1 in entity_family and b2 in entity_family
            
            if both_factual or both_entity:
                same_family_js.append(js_val)
            else:
                cross_family_js.append(js_val)
    
    # Mann-Whitney U test (non-parametric, handles small samples)
    statistic, p_value = stats.mannwhitneyu(
        same_family_js, cross_family_js, alternative='less'
    )
    
    # Effect size (Cliff's delta for non-parametric)
    def cliffs_delta(x, y):
        n1, n2 = len(x), len(y)
        count = sum(1 if xi < yj else (-1 if xi > yj else 0)
                    for xi in x for yj in y)
        return count / (n1 * n2)
    
    effect_size = cliffs_delta(same_family_js, cross_family_js)
    
    return {
        "p_value": p_value,
        "same_family_mean": np.mean(same_family_js),
        "cross_family_mean": np.mean(cross_family_js),
        "same_family_values": same_family_js,  # [0.056, 0.041, 0.072, 0.142, 0.139, 0.043]
        "cross_family_values": cross_family_js,  # 9 values
        "effect_size_cliffs_d": effect_size,
        "n_same": len(same_family_js),  # 6
        "n_cross": len(cross_family_js),  # 9
    }
```

### Training Protocol

**No training required** - Pure statistical analysis.

| Parameter | Value |
|-----------|-------|
| Training epochs | N/A |
| Optimizer | N/A |
| Learning rate | N/A |
| Batch size | N/A |
| Loss function | N/A |
| Regularization | N/A |

### Evaluation

**Primary Metrics:**
| Metric | Target | Description |
|--------|--------|-------------|
| p-value (Mann-Whitney U) | < 0.05 | Same-family < Cross-family |
| Same-family mean JS-div | < 0.15 | Secondary criterion |

**Success Criteria (PoC - Direction-based):**
1. Same-family JS-divergence distribution is significantly lower than cross-family (p < 0.05)
2. Mean same-family JS-div < 0.15

**Expected Results (from H-E1 data):**
- Same-family pairs: [0.056, 0.041, 0.072, 0.142, 0.139, 0.043] → mean ≈ 0.082
- Cross-family pairs: [0.422, 0.526, 0.530, 0.388, 0.498, 0.501, 0.418, 0.522, 0.526] → mean ≈ 0.481

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical hypothesis testing
- Library: scipy.stats
- Code:
```python
from scipy.stats import mannwhitneyu
statistic, p_value = mannwhitneyu(same_family_js, cross_family_js, alternative='less')
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Box plot comparing same-family vs cross-family JS-divergence distributions

#### Additional Figures (LLM Autonomous)

1. **JS-Divergence Heatmap** (from H-E1): Annotated with family boundaries
2. **Distribution Comparison**: Violin/box plot with individual points overlaid
3. **Effect Size Visualization**: Forest plot showing Cliff's delta with CI

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `p_value < 0.05` (same-family < cross-family)
3. `same_family_mean < 0.15`

**Pre-computed Check (from H-E1 matrix):**
- Same-family mean: 0.082 < 0.15 ✓
- Visual inspection: Clear separation between same/cross categories

---

## Appendix: Reference Implementations

### scipy.spatial.distance.jensenshannon
```python
from scipy.spatial.distance import jensenshannon
import numpy as np

# For two probability distributions
p = np.array([0.1, 0.4, 0.5])
q = np.array([0.2, 0.3, 0.5])
js_dist = jensenshannon(p, q)  # Returns distance (sqrt of divergence)
js_div = js_dist ** 2  # Convert to divergence
```

### Mann-Whitney U Test
```python
from scipy.stats import mannwhitneyu

# For comparing two groups
same_family = [0.056, 0.041, 0.072, 0.142, 0.139, 0.043]
cross_family = [0.422, 0.526, 0.530, 0.388, 0.498, 0.501, 0.418, 0.522, 0.526]

stat, p = mannwhitneyu(same_family, cross_family, alternative='less')
print(f"p-value: {p}")  # Expected: very small (< 0.001)
```

### KDE for Distribution Estimation (if recomputation needed)
```python
from scipy.stats import gaussian_kde
import numpy as np

def compute_js_divergence(entropy_dist_1, entropy_dist_2, n_points=1000):
    """Compute JS-divergence between two entropy distributions."""
    kde1 = gaussian_kde(entropy_dist_1)
    kde2 = gaussian_kde(entropy_dist_2)
    
    # Common support
    x_min = min(entropy_dist_1.min(), entropy_dist_2.min())
    x_max = max(entropy_dist_1.max(), entropy_dist_2.max())
    x = np.linspace(x_min, x_max, n_points)
    
    # Evaluate PDFs
    p = kde1(x)
    q = kde2(x)
    
    # Normalize to ensure valid probability distributions
    p = p / np.trapz(p, x)
    q = q / np.trapz(q, x)
    
    # JS-divergence
    from scipy.spatial.distance import jensenshannon
    return jensenshannon(p, q) ** 2
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10T22:30:00Z

### Workflow History for This Hypothesis
- 2026-08-10T22:17:03Z: H-M2 set to IN_PROGRESS (Phase 2C start)
- Prerequisite H-M1: PASS (p=0.000144, d=1.325, AUROC=0.793)
- Prerequisite H-E1: PASS (silhouette=0.8245, k=2)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in H-E1 computed results*
*Next Phase: Phase 3 - Implementation Planning*
