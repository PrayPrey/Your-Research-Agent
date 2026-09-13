# Product Requirements Document: Adaptive KV Cache (h-m4)

**Date:** 2026-08-20  
**Author:** Anonymous  
**Hypothesis:** h-m4 - Adaptive cache (grow/shrink based on retrieval density) matches static 25% cache accuracy while using ≤20% budget on average  
**Gate:** SHOULD_WORK  
**Budget:** FULL (30 tasks max, 6-12 epics)

---

## Executive Summary

### Purpose
Implement and validate an adaptive KV cache mechanism that dynamically adjusts cache size based on retrieval passage density, aiming to match the accuracy of static 25% cache (H2O baseline) while using ≤20% average memory budget.

### Scope
- Adaptive cache sizing algorithm based on retrieval density tracking
- Integration with Llama-2-7B model
- Evaluation on LongBench TriviaQA dataset (~200 samples)
- Comparison against H2O baseline (static 25% cache)

### Success Criteria
1. Code runs without error (PoC validation)
2. Adaptive F1 ≥ H2O baseline F1
3. Average cache budget ≤ 20%

---

## Problem Statement

### Background
Static KV cache budgets (e.g., H2O's 25%) achieve good accuracy but waste memory when retrieval density is low. Prior work (h-m1, h-m2, h-m3) established:
- h-m1: Tiered eviction achieves 6.16% F1 gain over H2O at 25% budget
- h-m2: Diversity-aware scoring improves multi-hop QA
- h-m3: Query complexity does NOT predict attention (FAILED)

### Problem
Need adaptive mechanism that:
- Grows cache when retrieval density is high (many unique passages)
- Shrinks cache when retrieval density is low (few unique passages)
- Matches static 25% accuracy at lower average budget

### Constraints
- No CUDA available (CPU-only validation, mock data calibrated per h-m1/h-e1)
- Single-seed PoC (seed=42)
- ~200 sample evaluation (LongBench TriviaQA test set)

---

## Functional Requirements

### FR-1: Adaptive Cache Sizing
**Priority:** P0  
**Description:** Implement dynamic cache budget adjustment based on retrieval passage density.

**Acceptance Criteria:**
- Track unique passage count over sliding window (default: 10 queries)
- Compute density = unique_passages / window_size
- Adjust budget:
  - High density (>0.7): grow budget by 1.1× (max 30%)
  - Low density (<0.3): shrink budget by 0.9× (min 10%)
  - Base budget: 25%

**Dependencies:** None (foundation mechanism)

---

### FR-2: H2O Baseline Implementation
**Priority:** P0  
**Description:** Implement H2O heavy-hitter oracle eviction as static 25% cache baseline.

**Acceptance Criteria:**
- Heavy-hitter ratio: 0.125 (12.5% of total tokens)
- Recent-window ratio: 0.125 (12.5% of total tokens)
- Total cache: 25% of full KV cache
- Eviction based on accumulated attention scores

**Dependencies:** None

---

### FR-3: Retrieval Density Tracking
**Priority:** P0  
**Description:** Track retrieval passage access frequency over sliding window.

**Acceptance Criteria:**
- Maintain passage access count dictionary
- Sliding window size: 10 queries
- Update density metric after each retrieval event
- Return cache size target based on current density

**Dependencies:** FR-1

---

### FR-4: LongBench TriviaQA Evaluation
**Priority:** P0  
**Description:** Evaluate both baseline and proposed models on LongBench TriviaQA test set.

**Acceptance Criteria:**
- Load dataset: `THUDM/LongBench`, task='triviaqa', split='test'
- ~200 samples from test set
- F1 score computation (token-level overlap)
- Statistical comparison (two-tailed t-test, p<0.05)

**Dependencies:** FR-1, FR-2

---

### FR-5: Visualization Generation
**Priority:** P1  
**Description:** Generate required figures for validation report.

**Acceptance Criteria:**
- Figure 1 (mandatory): F1 score bar chart (H2O vs Adaptive)
- Figure 2: Cache budget over time (line plot)
- Figure 3: Retrieval density vs cache budget (scatter plot)
- Figure 4: Cumulative average budget (line plot with 20% threshold)
- All figures saved to `{hypothesis_folder}/figures/`

**Dependencies:** FR-4

---

### FR-6: Model Integration (Llama-2-7B)
**Priority:** P0  
**Description:** Load and configure Llama-2-7B for cache mechanism evaluation.

**Acceptance Criteria:**
- Load from `meta-llama/Llama-2-7b-hf`
- FP16 precision
- Device map: auto
- Tokenizer: Llama tokenizer
- Context length: 4096 tokens (base), extended for long-context

**Dependencies:** None

---

## Non-Functional Requirements

### NFR-1: Performance
- Inference time: Best effort (CPU-only, no hard target)
- Memory: Fit in available RAM (adaptive cache should reduce peak usage)

### NFR-2: Reproducibility
- Seed: 42 (single-seed PoC)
- Deterministic operations where possible (torch.manual_seed)

### NFR-3: Code Quality
- Type hints for public APIs
- Docstrings for cache classes and eviction functions
- Clear variable names (avoid single-letter except loop counters)

### NFR-4: Validation Mode
- Use mock data calibrated per h-m1/h-e1 correlation (ρ=0.612)
- Document mock vs real-world gap in validation report

---

## Data Specifications

### Dataset: LongBench TriviaQA
**Source:** `THUDM/LongBench`  
**Task:** `triviaqa`  
**Split:** `test`  
**Size:** ~200 samples  
**Avg Context Length:** 8,209 tokens

**Loading Code:**
```python
from datasets import load_dataset
dataset = load_dataset('THUDM/LongBench', 'triviaqa', split='test')
```

**Preprocessing:** None (raw long-context QA)

---

### Model: Llama-2-7B
**Source:** `meta-llama/Llama-2-7b-hf`  
**Parameters:** ~7B  
**Layers:** 32  
**Hidden Size:** 4096  
**Attention Heads:** 32

**Loading Code:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

---

## Evaluation Metrics

### Primary Metric: F1 Score
**Definition:** Token-level overlap between generated answer and ground truth

**Computation:**
```python
def compute_f1(prediction, ground_truth):
    pred_tokens = prediction.split()
    gt_tokens = ground_truth.split()
    
    common = Counter(pred_tokens) & Counter(gt_tokens)
    num_common = sum(common.values())
    
    if num_common == 0:
        return 0.0
    
    precision = num_common / len(pred_tokens)
    recall = num_common / len(gt_tokens)
    f1 = 2 * (precision * recall) / (precision + recall)
    return f1
```

**Success Threshold:** Adaptive F1 ≥ H2O F1 (direction test)

---

### Secondary Metric: Average Cache Budget
**Definition:** Mean cache budget percentage across all evaluation samples

**Computation:**
```python
avg_budget = sum(cache_budgets) / len(cache_budgets)
```

**Success Threshold:** avg_budget ≤ 20%

---

### Statistical Test
**Method:** Two-tailed t-test  
**Significance:** p < 0.05  
**Samples:** ~200 (LongBench TriviaQA test set)

---

## Dependencies

### Internal Dependencies
- h-m1 (tiered eviction): Provides H2O baseline implementation reference
- h-e1 (attention-relevance correlation): Provides mock data calibration (ρ=0.612)

### External Dependencies
- HuggingFace Transformers ≥4.35.0
- HuggingFace Datasets
- PyTorch ≥2.0.0
- NumPy, SciPy (statistical tests)

### Optional Dependencies
- Matplotlib/Seaborn (visualization)

---

## Implementation References

### Primary: DynamicKV (arXiv:2412.14838)
**Pattern:** Progressive budget redistribution
- Top-K tokens per layer (attention-scored)
- Global renormalization every m layers
- Proven 1.7% → 90% compression

### Secondary: AKVCache (Arvind679715/adaptive-kv-memory)
**Pattern:** 3-tier adaptive architecture (hot/warm/cold)
- Attention-based tier migration
- Production-ready API

### Baseline: H2O (FMInference/H2O)
**Pattern:** Heavy-hitter oracle eviction
- Reused from h-m1 validation

---

## Acceptance Criteria

### Code Completion
- [ ] AdaptiveKVCache class with retrieval density tracking
- [ ] H2O baseline integration (from h-m1)
- [ ] LongBench TriviaQA evaluation loop
- [ ] F1 score computation
- [ ] Statistical comparison (t-test)
- [ ] Visualization generation (4 figures)

### Validation Completion
- [ ] Code runs without error
- [ ] Adaptive F1 ≥ H2O F1 (direction test)
- [ ] Average cache budget ≤ 20%
- [ ] Figures saved to `{hypothesis_folder}/figures/`
- [ ] 04_validation.md generated with results

---

## Out of Scope

- Multi-seed evaluation (PoC uses seed=42 only)
- CUDA execution (CPU-only due to library incompatibility)
- Real-world attention data (mock calibrated per h-e1)
- Production optimization (memory pooling, kernel fusion)
- Multi-hop QA datasets (focus on single-hop TriviaQA)

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Mock data diverges from real attention | Medium | Medium | Document gap, calibrate per h-e1 correlation |
| CPU execution too slow | Low | Low | Reduce sample count if needed (min 100) |
| Adaptive cache no better than static | Medium | Low | SHOULD_WORK gate - document limitation |
| Retrieval density metric unstable | Low | Medium | Tune window size (default 10, test 5/15) |

---

## Glossary

- **H2O:** Heavy-Hitter Oracle eviction policy (static 25% cache)
- **Retrieval Density:** Unique passages / sliding window size
- **Adaptive Cache:** Dynamic cache sizing based on retrieval density
- **PoC:** Proof of Concept (direction test, not production-ready)
- **Mock Data:** Simulated attention scores calibrated per h-e1 correlation
