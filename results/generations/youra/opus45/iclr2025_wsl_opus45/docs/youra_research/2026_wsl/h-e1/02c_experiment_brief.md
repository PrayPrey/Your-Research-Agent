# Experiment Design: H-E1

**Date:** 2026-04-13
**Author:** Anonymous
**Hypothesis Statement:** Under controlled experimental conditions with verified identical base model and fixed LoRA hyperparameters, within-cluster Grassmann distances between LoRA adapter B matrix column spaces will be significantly smaller than between-cluster distances (p < 0.05, Cohen's d > 0.5).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 has no prerequisites)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**MUST_WORK Gate:** If H-E1 fails, the core claim is falsified and the pipeline stops.

**Success Criteria (PoC):**
- Primary: p < 0.05 AND Cohen's d > 0.5 for within-cluster vs between-cluster Grassmann distance comparison
- Secondary: 95% CI excludes zero

---

## Continuation Context

This is the **first hypothesis** in the verification chain. No previous context to inherit.

### Previous Hypothesis Results (if applicable)
*Not applicable - H-E1 is the foundation hypothesis*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable during this session. Research conducted via Exa MCP.*

**Alternative Source - Exa Web Search:**

**Finding 1: Grassmann Distance Implementation**
- **Source:** jyopari.github.io/posts/grassman
- **Key Implementation Pattern:**
```python
import torch

def grassman(A, B):
    # Get orthogonal basis via QR decomposition
    Q_A, R = torch.linalg.qr(A)
    Q_B, R = torch.linalg.qr(B)
    
    # Get singular values of Q_A^T @ Q_B
    _, S, _ = torch.svd(Q_A.T @ Q_B)
    
    # Principal angles = arccos of singular values
    thetas = torch.arccos(S)
    
    # Grassmann distance = L2 norm of principal angles
    return torch.norm(thetas, p=2)
```
- **Key Insight:** Grassmann distance is computed as L2 norm of principal angles between subspaces

**Finding 2: SciPy subspace_angles Function**
- **Source:** scipy.org documentation
- **Usage:** `scipy.linalg.subspace_angles(A, B)` returns principal angles in radians
- **Key Insight:** Standard implementation for computing principal angles between two matrices

### Archon Code Examples

*Archon MCP unavailable. Code examples sourced from Exa.*

**Code Example 1: Gradience Library**
- **Source:** github.com/johntnanney/gradience (PyPI: gradience v0.11.0)
- **Purpose:** Spectral analysis of low-rank adaptation dynamics
- **Features:**
  - Per-layer SVD analysis
  - Subspace alignment measurement
  - Merge compatibility analysis via principal angles
  - Multi-seed experimental infrastructure
- **Relevance:** Provides production-ready infrastructure for LoRA spectral analysis

**Code Example 2: Weight Space LoRA Analysis**
- **Source:** github.com/JacekDuszenko/weightspace-lora-for-diffusion
- **Purpose:** Weight-space interpretation of LoRA adapters
- **Features:**
  - Dataset of controlled LoRA adapters (1k, 10k, 50k variants)
  - Layer ablation experiments
  - Multiple representation methods including spectral features
- **Relevance:** Demonstrates controlled LoRA generation methodology

### Exa GitHub Implementations

**Repository 1: SonyResearch/stella** (15 stars)
- **URL:** https://github.com/SonyResearch/stella
- **Relevance:** Demonstrates Stiefel manifold constraints on LoRA subspaces (U, V orthonormality)
- **Architecture:** Three-factor decomposition USV^T with geometric optimization
- **Key Code:**
```python
# StelLA maintains orthonormality during training
# U, V constrained to Stiefel manifold
# Demonstrates geometric structure of LoRA subspaces
import stella  # monkey-patches peft library
```
- **Key Insight:** LoRA subspaces have exploitable geometric structure; orthonormality ensures stable column space analysis

**Repository 2: doem97/ICLR26_mtLoRA** (12 stars)
- **URL:** https://github.com/doem97/ICLR26_mtLoRA
- **Relevance:** Multi-task LoRA with spectral-aware regularization
- **Key Insight:** Task interference can be analyzed via spectral properties; high-SV components carry shared knowledge

**Repository 3: microsoft/LoRA** (13.4k stars)
- **URL:** https://github.com/microsoft/LoRA
- **Relevance:** Original LoRA implementation, reference for loralib
- **Key Configuration:**
```python
# Standard LoRA configuration
r = 8  # rank
lora_alpha = 16  # scaling
lora_dropout = 0.1
```

**Repository 4: google-research/FLAN**
- **URL:** https://github.com/google-research/FLAN/blob/main/flan/v2/README.md
- **Relevance:** FLAN task taxonomy for defining semantic similarity ground truth
- **Key Insight:** FLAN collection provides established task categories (reasoning, NLU, CoT) for clustering ground truth

### Implementation Priority Assessment

**CRITICAL: For this controlled experiment, we generate our own adapters**

**Primary Implementation Path:**
- Primary: Generate controlled LoRA adapters in-house using HuggingFace PEFT + Llama-3.2-1B
- Fallback: Use gradience library for spectral analysis infrastructure
- Justification: Controlled provenance (identical base model, fixed hyperparameters) is essential for hypothesis validity; public adapters have confounded provenance

**Recommended Implementation Path:**
- Primary: In-house LoRA generation with PEFT library
- Fallback: Adapt gradience spectral analysis tools
- Justification: Only in-house generation can guarantee controlled experimental conditions

### Code Analysis (Serena MCP)

*Serena analysis not required - code patterns from Exa search are sufficiently clear:*

1. **QR decomposition** for orthonormal basis extraction
2. **SVD** for principal angle computation
3. **PEFT library** for LoRA training with controlled configuration
4. **scipy.linalg.subspace_angles** for reference validation

---

## Experiment Specification

### Dataset

**Dataset**: LoRA Zoo (In-House Generated)
**Type**: custom (programmatic generation from existing benchmarks)

**Source Datasets for LoRA Training:**
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

**Configuration:**
- 8 tasks total (4 Reasoning, 4 NLU)
- 20 adapters per task = 160 total adapters
- Seed variants: 5 seeds × 4 tasks = 20 adapters for within-task variance control (P3)
- **Total:** 200 LoRA adapters

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `gsm8k`, `allenai/ai2_arc:ARC-Challenge`, `lucasmccabe/logiqa`, `wics/strategy-qa`, `nyu-mll/multi_nli`, `SetFit/qqp`, `SetFit/sst2`, `SetFit/mrpc`
- Code: 
```python
from datasets import load_dataset
# Example for each task
gsm8k = load_dataset("gsm8k", "main", split="train")
arc = load_dataset("allenai/ai2_arc", "ARC-Challenge", split="train")
logiqa = load_dataset("lucasmccabe/logiqa", split="train")
strategyqa = load_dataset("wics/strategy-qa", split="train")
mnli = load_dataset("nyu-mll/multi_nli", split="train")
qqp = load_dataset("SetFit/qqp", split="train")
sst2 = load_dataset("SetFit/sst2", split="train")
mrpc = load_dataset("SetFit/mrpc", split="train")
```

### Models

#### Baseline Model

**Architecture:** Llama-3.2-1B-Instruct (frozen)
**Type:** Causal LLM
**Source:** meta-llama/Llama-3.2-1B-Instruct

**Configuration:**
- Parameters: ~1.2B
- SHA-256 verification required for provenance
- All weights frozen during LoRA training

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-3.2-1B-Instruct`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_id = "meta-llama/Llama-3.2-1B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Verify provenance
import hashlib
# SHA-256 hash verification of model weights
```

#### Proposed Model

**Architecture:** Baseline + Grassmann Distance Analysis

**Core Mechanism Implementation:**

```python
# Core Mechanism: Grassmann Distance Between LoRA B Matrix Column Spaces
# Based on: jyopari.github.io/posts/grassman, scipy.linalg.subspace_angles

import torch
import numpy as np
from scipy.linalg import subspace_angles

class GrassmannDistanceAnalyzer:
    """
    Computes Grassmann geodesic distance between LoRA B matrix column spaces.
    """
    
    def __init__(self, lora_adapters: dict):
        """
        Args:
            lora_adapters: Dict mapping adapter_id -> {layer_name: B_matrix}
        """
        self.adapters = lora_adapters
    
    def extract_b_column_space(self, B: np.ndarray) -> np.ndarray:
        """
        Extract orthonormal basis for B matrix column space via QR.
        
        Args:
            B: LoRA B matrix (d_out × r)
        Returns:
            Q: Orthonormal basis (d_out × r)
        """
        Q, _ = np.linalg.qr(B)
        return Q
    
    def grassmann_distance(self, B1: np.ndarray, B2: np.ndarray) -> float:
        """
        Compute Grassmann geodesic distance between two B matrix column spaces.
        
        Args:
            B1, B2: LoRA B matrices (d_out × r)
        Returns:
            distance: sqrt(sum of squared principal angles)
        """
        Q1 = self.extract_b_column_space(B1)
        Q2 = self.extract_b_column_space(B2)
        
        # Principal angles via scipy
        thetas = subspace_angles(Q1, Q2)
        
        # Grassmann geodesic distance
        return np.sqrt(np.sum(thetas ** 2))
    
    def compute_pairwise_distances(self, layer_name: str) -> np.ndarray:
        """
        Compute pairwise Grassmann distances for all adapters at a layer.
        """
        adapter_ids = list(self.adapters.keys())
        n = len(adapter_ids)
        distances = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i+1, n):
                B_i = self.adapters[adapter_ids[i]][layer_name]
                B_j = self.adapters[adapter_ids[j]][layer_name]
                d = self.grassmann_distance(B_i, B_j)
                distances[i, j] = d
                distances[j, i] = d
        
        return distances

# Integration: Apply to all LoRA layers after training
```

### Training Protocol

**LoRA Configuration (Fixed for all adapters):**
- **Optimizer:** AdamW
  - Parameters: betas=(0.9, 0.999), eps=1e-8, weight_decay=0.01
  - **Source:** Standard for LLM fine-tuning (HuggingFace defaults)

- **Learning Rate:** 2e-4
  - **Source:** PEFT/QLoRA standard for LoRA training (10x higher than full fine-tuning)

- **Schedule:** Linear warmup + cosine decay
  - Warmup: 10% of total steps
  - **Source:** Standard practice for transformer fine-tuning

- **Batch Size:** 8
  - **Source:** Phase 2B specification

- **Epochs:** 3
  - **Source:** Phase 2B specification, sufficient for task adaptation

- **LoRA Hyperparameters:**
  - r = 32 (rank)
  - alpha = 64 (scaling)
  - dropout = 0.05
  - bias = "none"
  - target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "up_proj", "down_proj", "gate_proj"]
  - **Source:** Phase 2B specification

- **Seeds:** 42 (fixed) + [43, 44, 45, 46] for P3 control condition

- **Deterministic Training:**
```python
import torch
torch.manual_seed(42)
torch.cuda.manual_seed_all(42)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

> **EXISTENCE (PoC)**: Single primary seed (42) is sufficient. Seed variants only for P3 control.

### Evaluation

**Primary Metrics:**
- **Within-cluster Grassmann distance:** Mean pairwise distance between adapters trained on same FLAN category
- **Between-cluster Grassmann distance:** Mean pairwise distance between adapters trained on different FLAN categories

**Success Criteria:**
- `within_cluster_mean < between_cluster_mean` (effect direction)
- **Statistical test:** Mann-Whitney U test
- **Effect size:** Cohen's d > 0.5
- **Significance:** p < 0.05

**Expected Baseline Performance** (from previous underpowered study):
- Cohen's d ≈ 0.91 (but CI was wide due to n=8)
- Effect direction: within < between (confirmed)
- **Source:** Phase 2B Section 1.4 baseline analysis

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical comparison
- Library: scipy.stats
- Code:
```python
from scipy.stats import mannwhitneyu
import numpy as np

def compute_cohens_d(group1, group2):
    """Compute Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std

# Mann-Whitney U test
stat, p_value = mannwhitneyu(within_distances, between_distances, alternative='less')

# Effect size
cohens_d = compute_cohens_d(between_distances, within_distances)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing within-cluster vs between-cluster mean Grassmann distances with error bars and significance annotation

#### Additional Figures (LLM Autonomous)

Based on hypothesis type and evaluation metrics:
1. **Distance Distribution Plot:** Histogram/KDE of within-cluster vs between-cluster distances
2. **Heatmap:** Pairwise Grassmann distance matrix with task category annotations
3. **Box Plot:** Per-category distance distributions

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `within_cluster_mean < between_cluster_mean` (effect direction)
3. p < 0.05 AND Cohen's d > 0.5

---

## Appendix: Reference Implementations

### A. Exa Web Search Sources

**Source 1: Grassmann Distance Implementation**
- **Type:** Tutorial/Blog
- **Query Used:** "LoRA adapter weight space analysis Grassmann distance subspace angles PyTorch implementation"
- **URL:** https://jyopari.github.io/posts/grassman
- **Relevance:** Core algorithm for Grassmann distance computation
- **Key Insights:**
  - QR decomposition for orthonormal basis
  - SVD of Q1^T @ Q2 gives cosine of principal angles
  - L2 norm of arccos(singular values) = Grassmann distance
- **Used For:** Core mechanism pseudo-code

**Source 2: SciPy subspace_angles Documentation**
- **Type:** Library documentation
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.subspace_angles.html
- **Relevance:** Reference implementation for validation
- **Used For:** Principal angle computation

**Source 3: Gradience Library**
- **Type:** PyPI package
- **URL:** https://pypi.org/project/gradience/
- **GitHub:** https://github.com/johntnanney/gradience
- **Relevance:** Production-ready LoRA spectral analysis infrastructure
- **Used For:** Infrastructure patterns, multi-seed experimental design

**Source 4: StelLA (Stiefel LoRA)**
- **Type:** Research paper + code
- **URL:** https://github.com/SonyResearch/stella
- **Paper:** NeurIPS 2025 Spotlight
- **Relevance:** Demonstrates geometric structure of LoRA subspaces
- **Used For:** Understanding LoRA geometry

### B. FLAN Task Taxonomy Sources

**Source 5: FLAN Collection**
- **Type:** Research paper + dataset
- **URL:** https://github.com/google-research/FLAN/blob/main/flan/v2/README.md
- **Paper:** ICML 2023
- **Relevance:** Task taxonomy for defining semantic similarity
- **Used For:** Ground truth clustering (Reasoning vs NLU categories)

### C. LoRA Training Sources

**Source 6: HuggingFace PEFT Documentation**
- **Type:** Library documentation
- **URL:** https://huggingface.co/docs/peft/en/quicktour
- **Relevance:** Standard LoRA training implementation
- **Used For:** Training protocol, LoraConfig parameters

**Source 7: Microsoft LoRA (Original)**
- **Type:** Original paper implementation
- **URL:** https://github.com/microsoft/LoRA
- **Paper:** ICLR 2022
- **Relevance:** Reference LoRA implementation
- **Used For:** Baseline configuration

### D. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Grassmann distance algorithm | Tutorial | Source A.1 (jyopari.github.io) |
| Principal angle computation | Library docs | Source A.2 (scipy docs) |
| LoRA spectral analysis patterns | Library | Source A.3 (gradience) |
| Task taxonomy (FLAN) | Research paper | Source B.5 (FLAN Collection) |
| LoRA training configuration | Library docs | Source C.6 (PEFT docs) |
| Baseline LoRA config | Original paper | Source C.7 (microsoft/LoRA) |
| Controlled variables | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Success criteria | Phase 2B | 02b_verification_plan.md H-E1 specification |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-13

### Workflow History for This Hypothesis
1. Phase 2B: H-E1 defined as EXISTENCE hypothesis with MUST_WORK gate
2. Phase 2C: Experiment design generated with MCP-backed research

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Exa (GitHub + Web Search)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
