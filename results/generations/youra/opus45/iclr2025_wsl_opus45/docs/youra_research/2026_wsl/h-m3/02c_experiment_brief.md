# Experiment Design: H-M3

**Date:** 2026-04-13
**Author:** Anonymous
**Hypothesis Statement:** Under identical training conditions, if two tasks are semantically similar (same FLAN category), then their LoRA adapters will have similar B matrix column spaces (Spearman ρ > 0.3 with FLAN taxonomy distances), because similar tasks require similar functional transformations in the output dimension.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM (KEY TENSION) Template** - Tests correlation between geometric distance and semantic similarity.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 VALIDATED - existence proven)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (existence of clustering - VALIDATED)

### Gate Condition
**MUST_WORK Gate:** If H-M3 fails, pivot to alternative similarity metrics before proceeding to H-M4.

**Success Criteria:**
- Primary: Spearman ρ > 0.3 with p < 0.05
- Secondary: Within-task distance < 0.5 × within-cluster distance (P3 control)

---

## Continuation Context

This is a **continuation experiment** from H-E1. The existence proof is validated - we now test the mechanism linking semantic similarity to geometric similarity.

### Previous Hypothesis Results (H-E1)

**From Phase 4 Validation Report (04_validation.md):**

| Metric | Value | Status |
|--------|-------|--------|
| Within-Cluster Mean | 7.6057 | - |
| Between-Cluster Mean | 7.7954 | - |
| P-Value | 8.63e-28 | PASS |
| Cohen's d | 0.7652 | PASS |
| 95% CI | [0.1553, 0.2263] | Excludes zero |

**Proven Components to Reuse:**
- LoRA training pipeline (`train.py`)
- Grassmann distance computation (`analyze.py`)
- Dataset preprocessing (`data.py`)
- 40 trained adapters (8 tasks × 5 seeds)

**Optimal Hyperparameters (from H-E1):**
```yaml
lora_config:
  r: 32
  lora_alpha: 64
  lora_dropout: 0.05
  target_modules: ["q_proj", "k_proj", "v_proj", "o_proj", "up_proj", "down_proj", "gate_proj"]

training_config:
  lr: 2e-4
  epochs: 3
  batch_size: 8
  warmup_ratio: 0.1
  max_samples: 2000
```

**Key Insight from H-E1:**
The existence proof demonstrates that LoRA adapters trained on semantically similar tasks do exhibit measurable geometric similarities. H-M3 now tests whether this correlation is systematic (Spearman ρ > 0.3) with FLAN taxonomy distances.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable during this session. Research conducted via Exa MCP.*

**Alternative Source - Exa Web Search:**

**Finding 1: FLAN Task Taxonomy**
- **Source:** github.com/google-research/FLAN/blob/main/flan/v2/flan_collection_info.csv
- **Key Insight:** FLAN v2 provides task categories (Reasoning, NLU, CoT, etc.) with detailed task groupings
- **Task Categories Used:**
  - Reasoning: GSM8K, ARC-Challenge, LogiQA, StrategyQA
  - NLU: MNLI, QQP, SST-2, MRPC

**Finding 2: Spearman Correlation Implementation**
- **Source:** scipy.stats.spearmanr documentation
- **Usage:** `scipy.stats.spearmanr(x, y)` returns correlation coefficient and p-value
- **Key Insight:** Non-parametric rank correlation ideal for comparing distance matrices

### Archon Code Examples

*Archon MCP unavailable. Code examples sourced from Exa.*

**Code Example 1: Task-Aware LoRA Adapter Composition**
- **Source:** arxiv.org/html/2602.21222v1
- **Purpose:** Task similarity retrieval for LoRA adapter selection
- **Relevance:** Demonstrates task similarity measurement in LoRA weight space

**Code Example 2: LoRAGen Weight Space Learning**
- **Source:** github.com/tsinghua-fib-lab/LoRAGen
- **Purpose:** Structure-aware weight space learning for LoRA generation
- **Relevance:** Shows how task similarity can be measured via LoRA weight space analysis

### Exa GitHub Implementations

**Repository 1: scipy.stats.spearmanr**
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- **Relevance:** Standard implementation for Spearman rank correlation
- **Key Code:**
```python
from scipy.stats import spearmanr

# Compute Spearman correlation
rho, p_value = spearmanr(geometric_distances, taxonomy_distances)
```
- **Key Insight:** Returns both correlation coefficient (ρ) and two-sided p-value

**Repository 2: torchmetrics SpearmanCorrCoef**
- **URL:** https://github.com/Lightning-AI/metrics/blob/master/src/torchmetrics/regression/spearman.py
- **Relevance:** PyTorch-native Spearman correlation for GPU computation
- **Key Code:**
```python
from torchmetrics.regression import SpearmanCorrCoef
spearman = SpearmanCorrCoef()
rho = spearman(preds, target)
```

**Repository 3: google-research/FLAN**
- **URL:** https://github.com/google-research/FLAN/blob/main/flan/v2/flan_collection_info.csv
- **Relevance:** FLAN task taxonomy for defining semantic similarity ground truth
- **Task Categories:**
  - CoT (Chain-of-Thought): reasoning tasks
  - Dialog: conversational tasks
  - NLI: natural language inference
  - QA: question answering
  - Sentiment: sentiment analysis
- **Key Insight:** Tasks in same category share instructional similarity → expected geometric similarity

### Implementation Priority Assessment

**CRITICAL: Reuse H-E1 infrastructure with new correlation analysis**

**Primary Implementation Path:**
- Primary: Extend H-E1 analysis with Spearman correlation against FLAN taxonomy distances
- Fallback: If FLAN taxonomy fails, use task embedding cosine similarity (R1 mitigation)
- Justification: H-E1 proved clustering exists; H-M3 tests whether correlation is systematic

**Recommended Implementation Path:**
- Primary: Build on H-E1 `analyze.py` with FLAN taxonomy distance matrix
- Fallback: Alternative similarity metrics (task embedding cosine distance)
- Justification: Controlled comparison using same adapters ensures only IV changes

### Code Analysis (Serena MCP)

*Serena analysis not required - code patterns from H-E1 and Exa search are sufficiently clear:*

1. **FLAN taxonomy distance matrix** - binary (0=same category, 1=different category) or hierarchical
2. **Grassmann distance matrix** - already computed in H-E1
3. **Spearman rank correlation** - scipy.stats.spearmanr for non-parametric correlation
4. **P3 control condition** - within-task variance baseline from H-E1

---

## Experiment Specification

### Dataset

**Dataset**: LoRA Zoo (In-House Generated) - Reused from H-E1
**Type**: custom (same adapters from H-E1)

**Reuse from H-E1:**
| Category | Dataset | Task Type | FLAN Classification |
|----------|---------|-----------|---------------------|
| Reasoning | GSM8K | Math word problems | Reasoning |
| Reasoning | ARC-Challenge | Science QA | Reasoning |
| Reasoning | LogiQA | Logical reasoning | Reasoning |
| Reasoning | StrategyQA | Multi-hop reasoning | Reasoning |
| NLU | MNLI | NLI | NLU |
| NLU | QQP | Paraphrase detection | NLU |
| NLU | SST-2 | Sentiment | NLU |
| NLU | MRPC | Paraphrase detection | NLU |

**Configuration (from H-E1):**
- 8 tasks total (4 Reasoning, 4 NLU)
- 40 adapters (8 tasks × 5 seeds)
- All adapters already trained and validated in H-E1

**Loading Information** (for Phase 4):
- Method: Load pre-trained adapters from H-E1
- Path: `../h-e1/adapters/`
- Code:
```python
from peft import PeftModel

# Load adapter from H-E1
adapter_path = f"../h-e1/adapters/{task_name}_seed{seed}"
model = PeftModel.from_pretrained(base_model, adapter_path)
```

### Models

#### Baseline Model

**Architecture:** TinyLlama-1.1B-Chat-v1.0 (frozen) - Same as H-E1
**Type:** Causal LLM
**Source:** TinyLlama/TinyLlama-1.1B-Chat-v1.0

**Configuration (from H-E1):**
- Parameters: ~1.1B
- All weights frozen during LoRA training
- Verified working in H-E1 validation

**Loading Information** (for Phase 4):
- Method: HuggingFace transformers
- Identifier: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```

#### Proposed Model

**Architecture:** H-E1 Grassmann Analysis + FLAN Taxonomy Correlation

**Core Mechanism Implementation:**

```python
# Core Mechanism: Spearman Correlation Between Geometric and Taxonomy Distances
# Based on: scipy.stats.spearmanr, FLAN task taxonomy, H-E1 Grassmann distance

import numpy as np
from scipy.stats import spearmanr
from typing import Dict, List, Tuple

class FLANTaxonomyCorrelationAnalyzer:
    """
    Computes Spearman correlation between Grassmann distances and FLAN taxonomy distances.
    Tests whether geometric similarity correlates with semantic similarity.
    """
    
    # FLAN Task Categories (ground truth)
    FLAN_CATEGORIES = {
        'gsm8k': 'Reasoning',
        'arc': 'Reasoning',
        'logiqa': 'Reasoning',
        'strategyqa': 'Reasoning',
        'mnli': 'NLU',
        'qqp': 'NLU',
        'sst2': 'NLU',
        'mrpc': 'NLU'
    }
    
    def __init__(self, grassmann_distances: np.ndarray, task_labels: List[str]):
        """
        Args:
            grassmann_distances: (N, N) pairwise Grassmann distance matrix from H-E1
            task_labels: List of task names for each adapter
        """
        self.grassmann_distances = grassmann_distances
        self.task_labels = task_labels
        self.n = len(task_labels)
    
    def compute_taxonomy_distances(self) -> np.ndarray:
        """
        Compute FLAN taxonomy distance matrix.
        0 = same category, 1 = different category (binary)
        """
        taxonomy_distances = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(self.n):
                cat_i = self.FLAN_CATEGORIES[self.task_labels[i]]
                cat_j = self.FLAN_CATEGORIES[self.task_labels[j]]
                taxonomy_distances[i, j] = 0 if cat_i == cat_j else 1
        return taxonomy_distances
    
    def compute_spearman_correlation(self) -> Tuple[float, float]:
        """
        Compute Spearman rank correlation between Grassmann and taxonomy distances.
        
        Returns:
            (rho, p_value): Spearman correlation coefficient and p-value
        """
        # Flatten upper triangle (exclude diagonal)
        triu_indices = np.triu_indices(self.n, k=1)
        grassmann_flat = self.grassmann_distances[triu_indices]
        taxonomy_flat = self.compute_taxonomy_distances()[triu_indices]
        
        # Spearman rank correlation
        rho, p_value = spearmanr(grassmann_flat, taxonomy_flat)
        return rho, p_value
    
    def compute_p3_control(self, within_task_distances: np.ndarray,
                           within_cluster_distances: np.ndarray) -> bool:
        """
        P3 Control: Within-task distance < 0.5 × within-cluster distance
        
        Returns:
            True if control condition passes (stochasticity does not dominate)
        """
        within_task_mean = np.mean(within_task_distances)
        within_cluster_mean = np.mean(within_cluster_distances)
        return within_task_mean < 0.5 * within_cluster_mean

# Integration: Load Grassmann distances from H-E1, compute correlation
```

### Training Protocol

**NO NEW TRAINING REQUIRED** - Reuse H-E1 adapters

**From Previous Hypothesis (H-E1):**
- **Adapters:** 40 pre-trained adapters (8 tasks × 5 seeds)
- **Location:** `../h-e1/adapters/`
- **Status:** Validated in H-E1 Phase 4

**Rationale:** Controlled comparison - only analysis changes, not adapters.

**Analysis Protocol:**
1. Load Grassmann distance matrix from H-E1 (or recompute from adapters)
2. Construct FLAN taxonomy distance matrix
3. Compute Spearman rank correlation
4. Validate P3 control condition
5. Report results with confidence intervals

**Seeds:** Use same 5 seeds from H-E1 (42, 43, 44, 45, 46)

### Evaluation

**Primary Metrics:**
- **Spearman ρ:** Rank correlation between Grassmann distances and FLAN taxonomy distances
- **P-value:** Statistical significance of correlation

**Success Criteria:**
- `Spearman ρ > 0.3` AND `p < 0.05`
- P3 Control: `within_task_mean < 0.5 × within_cluster_mean`

**Expected Performance (based on H-E1):**
- H-E1 showed Cohen's d = 0.7652 for within vs between cluster
- This suggests positive correlation expected (similar tasks → smaller distances)
- **Source:** H-E1 04_validation.md

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical correlation
- Library: scipy.stats
- Code:
```python
from scipy.stats import spearmanr
import numpy as np

def compute_spearman_with_ci(grassmann_flat, taxonomy_flat, n_bootstrap=1000):
    """Compute Spearman correlation with bootstrap confidence interval."""
    rho, p_value = spearmanr(grassmann_flat, taxonomy_flat)
    
    # Bootstrap for 95% CI
    n = len(grassmann_flat)
    rhos = []
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        rho_boot, _ = spearmanr(grassmann_flat[idx], taxonomy_flat[idx])
        rhos.append(rho_boot)
    ci_low, ci_high = np.percentile(rhos, [2.5, 97.5])
    
    return rho, p_value, ci_low, ci_high

# Compute correlation
rho, p, ci_low, ci_high = compute_spearman_with_ci(grassmann_flat, taxonomy_flat)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing Spearman ρ vs threshold (0.3) with significance annotation

#### Additional Figures (LLM Autonomous)

Based on hypothesis type and evaluation metrics:
1. **Scatter Plot:** Grassmann distance vs FLAN taxonomy distance with regression line
2. **Correlation Heatmap:** Task-level correlation matrix
3. **P3 Control Plot:** Within-task vs within-cluster distance distributions

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Spearman ρ > 0.3
3. p < 0.05
4. P3 Control passes (within-task < 0.5 × within-cluster)

---

## Appendix: Reference Implementations

### A. Exa Web Search Sources

**Source 1: SciPy spearmanr Documentation**
- **Type:** Library documentation
- **Query Used:** "Spearman rank correlation task embedding similarity PyTorch scipy implementation"
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- **Relevance:** Standard implementation for Spearman correlation
- **Key Insights:**
  - Returns both ρ and two-sided p-value
  - Handles tied ranks appropriately
  - Non-parametric (no normality assumption)
- **Used For:** Core correlation computation

**Source 2: FLAN Task Taxonomy**
- **Type:** Research dataset
- **Query Used:** "FLAN task taxonomy distance matrix hierarchical task similarity NLP benchmark categories"
- **URL:** https://github.com/google-research/FLAN/blob/main/flan/v2/flan_collection_info.csv
- **Relevance:** Ground truth for task semantic similarity
- **Key Insights:**
  - Tasks organized by category (Reasoning, NLU, CoT, etc.)
  - Same category → semantically similar tasks
  - External validation from multi-task learning literature
- **Used For:** Taxonomy distance matrix construction

**Source 3: Task-Aware LoRA Adapter Composition**
- **Type:** Research paper
- **URL:** https://arxiv.org/html/2602.21222v1
- **Relevance:** Demonstrates task similarity measurement in LoRA weight space
- **Used For:** Understanding task similarity retrieval patterns

**Source 4: torchmetrics SpearmanCorrCoef**
- **Type:** Library implementation
- **URL:** https://github.com/Lightning-AI/metrics/blob/master/src/torchmetrics/regression/spearman.py
- **Relevance:** PyTorch-native correlation for potential GPU acceleration
- **Used For:** Alternative implementation reference

### B. Previous Hypothesis Context (H-E1)

**Source 5: H-E1 Phase 4 Validation Report**
- **Type:** Previous hypothesis output
- **File:** `../h-e1/04_validation.md`
- **Relevance:** Provides validated Grassmann distance analysis and trained adapters
- **Reused Components:**
  - 40 trained LoRA adapters
  - Grassmann distance computation code
  - Statistical analysis infrastructure
- **Used For:** Continuation experiment baseline

### C. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Spearman correlation algorithm | Library docs | Source A.1 (scipy docs) |
| FLAN taxonomy categories | Research dataset | Source A.2 (FLAN v2) |
| Task similarity patterns | Research paper | Source A.3 (arxiv) |
| Grassmann distances | Previous hypothesis | Source B.5 (H-E1) |
| Trained adapters | Previous hypothesis | Source B.5 (H-E1) |
| Success criteria | Phase 2B | 02b_verification_plan.md H-M3 specification |
| Control condition (P3) | Phase 2B | 02b_verification_plan.md Section 3.3 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-13

### Workflow History for This Hypothesis
1. Phase 2B: H-M3 defined as MECHANISM hypothesis with MUST_WORK gate
2. Prerequisite H-E1: VALIDATED (p = 8.63e-28, Cohen's d = 0.7652)
3. Phase 2C: Experiment design generated with MCP-backed research (Exa)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Exa (Web Search)*
*All specifications grounded in researched implementations*
*Continuation Experiment: Builds on H-E1 validated infrastructure*
*Next Phase: Phase 3 - Implementation Planning*
