# Experiment Design: h-m3

**Date:** 2026-03-26
**Author:** Anonymous
**Hypothesis Statement:** Methods with different design paradigms (random projection vs HVP iteration vs gradient similarity) show persistent relative advantages on different metrics across compute levels, with top-k Jaccard < 0.70 (>30% disagreement on influential examples).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Hypothesis** - Tests whether method design paradigm creates irreducible trade-offs in influential example identification.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m2 VALIDATED - R^2_deep = 0.034 < 0.80)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2

### Gate Condition
**SHOULD_WORK Gate:** Top-k Jaccard < 0.70 (>30% disagreement between methods on influential examples)

If different method design paradigms (random projection, HVP iteration, gradient similarity) consistently identify different sets of influential examples, this proves that trade-offs are tied to method design, not just metric measurement noise.

---

## Continuation Context

### Previous Hypothesis Results

**h-m2 (VALIDATED - PASS)**
- R^2_deep = 0.034 (< 0.80 threshold)
- Demonstrated structural metric decoupling in non-convex deep networks
- Cross-metric correlations vary wildly (-0.45 to 0.99) across budgets

**h-e1 (VALIDATED - PASS)**
- Found 5 metric crossings (IF vs FastIF) at all budget levels
- IF achieves higher rank preservation, FastIF achieves higher magnitude fidelity
- Model checkpoint available: `h-e1/code/checkpoints/model_seed0_final.pt`

**Reuse from Previous:**
- Dataset: CIFAR-10 (5,000 training samples, 100 test samples)
- Model: ResNet-18 (from h-e1)
- Attribution methods: TRAK, TracIn, IF, FastIF
- Compute budgets: [10, 25, 50, 75, 100]

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon MCP unavailable. Findings derived from Exa web search and academic literature.

**Query 1: Data Attribution Method Comparison**
- TRAK achieves 0.7-0.9 rank correlation with LOO on image classification
- TRAK is 100x faster than methods of comparable efficacy (datamodels)
- TracIn scores computed in 17 hours on single A100 achieve better correlation than 125 GPU-days of re-training
- Influence functions show fragility in deep networks (Basu et al. 2020)

**Query 2: Top-k Influential Examples Comparison**
- Different attribution methods can identify fundamentally different training examples as "most influential"
- TRAK removes top-400 examples → 36% alignment drop for CLIP
- TracIn removes top-400 → only 4% alignment drop
- This suggests methods disagree on what makes examples influential

### Archon Code Examples

**TRAK Implementation (MadryLab/trak)**
```python
from trak import TRAKer

traker = TRAKer(model=model, task='image_classification', train_set_size=...)

# Compute features on training data
for model_id, checkpoint in enumerate(checkpoints):
    traker.load_checkpoint(checkpoint, model_id=model_id)
    for batch in train_loader:
        traker.featurize(batch=batch, ...)

# Compute scores for targets
for model_id, checkpoint in enumerate(checkpoints):
    traker.start_scoring_checkpoint(checkpoint, model_id=model_id, ...)
    for batch in targets_loader:
        traker.score(batch=batch, ...)
scores = traker.finalize_scores(exp_name='test')
```

**TracIn Implementation (Captum)**
```python
from captum.influence import TracInCPFast

tracin = TracInCPFast(
    model=model,
    final_fc_layer=model.fc,
    train_dataset=train_dataset,
    checkpoints=checkpoint_paths,
    loss_fn=nn.CrossEntropyLoss(reduction="sum"),
    batch_size=64
)

# Get top-k influential examples
proponents = tracin.influence(test_batch, k=50, proponents=True)
```

### Exa GitHub Implementations

**Repository 1**: MadryLab/trak (⭐ 500+)
- **URL**: https://github.com/MadryLab/trak
- **Relevance**: Official TRAK implementation, random projection-based attribution
- **Key Feature**: Custom CUDA kernel for fast random projections
- **Installation**: `pip install traker[fast]`

**Repository 2**: pytorch/captum
- **URL**: https://captum.ai/
- **Relevance**: TracIn, Influence Functions implementations
- **Key Classes**: `TracInCP`, `TracInCPFast`, `TracInCPFastRandProj`
- **Installation**: `pip install captum`

**Repository 3**: dilyabareeva/quanda
- **URL**: https://github.com/dilyabareeva/quanda
- **Relevance**: Quantitative evaluation toolkit for data attribution
- **Key Metric**: `TopKCardinalityMetric` - measures cardinality of union of top-K sets
- **Supported Methods**: TRAK, TracIn, Similarity Influence, Arnoldi IF

### Implementation Priority Assessment

**CRITICAL: For method comparison experiments, use consistent evaluation framework**

**Recommended Implementation Path:**
- Primary: Reuse h-e1 attribution infrastructure (TRAK, TracIn, IF, FastIF implementations)
- Fallback: quanda toolkit for standardized evaluation
- Justification: h-e1 already validated these methods work; reusing ensures controlled comparison

### Code Analysis (Serena MCP)

*Skipped* - Code from h-e1 is sufficiently clear and already validated.

**Key Implementation from h-e1:**
- Attribution methods implemented as gradient-based proxies
- Ground truth: FC-layer gradient similarity (proxy for LOO retraining)
- Methods differentiated by transformation:
  - TRAK: Random projection (dimension reduction)
  - TracIn: Direct dot-product with checkpoint scaling
  - IF: Eigenvalue-weighted gradients (Hessian approximation)
  - FastIF: Gradient similarity with structured noise

---

## Experiment Specification

### Dataset

**Dataset**: CIFAR-10 (from h-e1)
**Type**: standard
**Source**: torchvision.datasets.CIFAR10

**Statistics**:
- Training samples: 5,000 (subset for LOO feasibility)
- Test samples: 100
- Classes: 10
- Image size: 32x32x3

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: CIFAR10
- Code:
```python
import torchvision.datasets as datasets
import torchvision.transforms as transforms

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
])
train_dataset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
```

**Preprocessing**: Normalization with CIFAR-10 mean/std
**Augmentation**: None (evaluation mode only)

### Models

#### Baseline Model

**Architecture**: ResNet-18 (pretrained from h-e1)
**Type**: CNN classifier
**Source**: `h-e1/code/checkpoints/model_seed0_final.pt`

**Loading Information** (for Phase 4 download):
- Method: Local checkpoint
- Identifier: h-e1/code/checkpoints/model_seed0_final.pt
- Code:
```python
import torchvision.models as models
model = models.resnet18(num_classes=10)
model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
model.maxpool = nn.Identity()
model.load_state_dict(torch.load('h-e1/code/checkpoints/model_seed0_final.pt'))
```

**Configuration**:
- Modified for CIFAR-10: conv1 kernel=3, no maxpool
- Training: 200 epochs, SGD (lr=0.1, momentum=0.9, weight_decay=5e-4)

#### Proposed Model

**Architecture**: Same as baseline (no model modification for h-m3)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Top-k Jaccard Computation for Method Disagreement
# Based on: quanda toolkit TopKCardinalityMetric concept

def compute_topk_jaccard(attribution_scores_dict, k=50):
    """
    Compute pairwise Jaccard similarity between top-k influential sets.

    Args:
        attribution_scores_dict: {method_name: (n_test, n_train) scores}
        k: Number of top influential examples to consider

    Returns:
        jaccard_matrix: (n_methods, n_methods) pairwise Jaccard
        min_jaccard: Minimum pairwise Jaccard across all pairs
    """
    methods = list(attribution_scores_dict.keys())
    n_methods = len(methods)
    n_test = attribution_scores_dict[methods[0]].shape[0]

    # Get top-k indices for each method and test example
    topk_sets = {}
    for method in methods:
        scores = attribution_scores_dict[method]  # (n_test, n_train)
        topk_indices = np.argsort(-scores, axis=1)[:, :k]  # (n_test, k)
        topk_sets[method] = [set(topk_indices[i]) for i in range(n_test)]

    # Compute pairwise Jaccard
    jaccard_matrix = np.zeros((n_methods, n_methods))
    for i, m1 in enumerate(methods):
        for j, m2 in enumerate(methods):
            jaccards = []
            for t in range(n_test):
                set1, set2 = topk_sets[m1][t], topk_sets[m2][t]
                intersection = len(set1 & set2)
                union = len(set1 | set2)
                jaccards.append(intersection / union if union > 0 else 1.0)
            jaccard_matrix[i, j] = np.mean(jaccards)

    # Min Jaccard (excluding diagonal)
    mask = ~np.eye(n_methods, dtype=bool)
    min_jaccard = jaccard_matrix[mask].min()

    return jaccard_matrix, min_jaccard

# Gate Check: min_jaccard < 0.70 → PASS (>30% disagreement)
```

### Training Protocol

**From Previous Hypothesis (h-e1)**:
- **Optimizer**: SGD
  - momentum=0.9
  - weight_decay=5e-4
- **Learning Rate**: 0.1 with MultiStepLR
  - milestones=[100, 150]
  - gamma=0.1
- **Batch Size**: 128
- **Epochs**: 200
- **Loss**: CrossEntropyLoss

**For h-m3**: No training required. Uses pretrained model from h-e1. Only attribution computation and Jaccard analysis.

**Rationale**: Optimal in h-e1, reusing for controlled experiment.

### Evaluation

**Primary Metrics**:
- **Top-k Jaccard Similarity**: Pairwise Jaccard between top-k influential sets
- **Method Disagreement**: 1 - min(Jaccard) across method pairs

**Success Criteria** (SHOULD_WORK Gate):
- **Primary**: min(top-k Jaccard) < 0.70 (>30% disagreement)
- **Secondary**: Persistent relative advantages observed across compute budgets

**Expected Values** (from research):
- TRAK vs TracIn: Expected low Jaccard (different paradigms)
- TRAK identifies examples that cause 36% alignment drop when removed
- TracIn identifies examples that cause only 4% alignment drop
- This suggests fundamentally different example selection

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Set similarity
- Library: Custom (see pseudo-code above)
- Code:
```python
# Jaccard similarity for sets
def jaccard_similarity(set_a, set_b):
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 1.0
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Top-k Jaccard heatmap showing pairwise method disagreement

#### Additional Figures (LLM Autonomous)

Recommended visualizations based on hypothesis type:
1. **jaccard_heatmap.png**: Pairwise Jaccard matrix between methods
2. **topk_overlap_venn.png**: Venn diagram of overlapping top-k sets
3. **disagreement_by_budget.png**: How Jaccard varies with compute budget
4. **method_ranking_persistence.png**: Relative metric rankings across budgets

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. min(top-k Jaccard) < 0.70 (>30% method disagreement)

**Additional Success Indicators:**
- Methods show persistent relative advantages on different metrics
- Design paradigm (projection vs HVP vs gradient) correlates with metric strength

---

## Appendix: Reference Implementations

### A. Exa Web Search Sources

**Source 1**: TRAK Paper & Implementation
- **URL**: https://gradientscience.org/trak/
- **Type**: Official method documentation
- **Query Used**: "TRAK data attribution PyTorch implementation"
- **Key Insights**:
  - TRAK is 100x faster than comparable methods
  - Uses random projection of "after kernel"
  - Top-k removal causes 36% alignment drop for CLIP
- **Used For**: Understanding TRAK paradigm and expected behavior

**Source 2**: MadryLab/trak GitHub
- **URL**: https://github.com/MadryLab/trak
- **Type**: Official implementation
- **Key Code**: TRAKer API for computing attribution scores
- **Used For**: Reference for TRAK implementation pattern

**Source 3**: Captum TracIn Tutorial
- **URL**: https://captum.ai/tutorials/TracInCP_Tutorial
- **Type**: Library documentation
- **Key Classes**: TracInCP, TracInCPFast, TracInCPFastRandProj
- **Used For**: TracIn implementation reference

**Source 4**: quanda Toolkit
- **URL**: https://github.com/dilyabareeva/quanda
- **Type**: Evaluation framework
- **Key Metric**: TopKCardinalityMetric
- **Used For**: Top-k cardinality evaluation methodology

**Source 5**: FastIF Paper
- **URL**: https://aclanthology.org/2021.emnlp-main.808/
- **Type**: Academic paper
- **Key Finding**: FastIF achieves 80x speedup with >95% correlation to full IF
- **Used For**: Understanding FastIF paradigm

### B. Previous Hypothesis Context

**Source**: Phase 4 Validation Reports
- **h-e1**: Demonstrated Pareto trade-offs exist (IF vs FastIF crossings)
- **h-m1**: Established convex baseline coupling (correlation >= 0.95)
- **h-m2**: Proved metric decoupling in deep networks (R^2_deep = 0.034)

**Reused Components**:
- Dataset: CIFAR-10 (5000 train, 100 test)
- Model: ResNet-18 from h-e1
- Attribution methods: TRAK, TracIn, IF, FastIF
- Compute budgets: [10, 25, 50, 75, 100]

### C. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Previous | h-e1 validation |
| Model checkpoint | Previous | h-e1/code/checkpoints/ |
| TRAK implementation | Exa | MadryLab/trak |
| TracIn implementation | Exa | Captum |
| Top-k Jaccard metric | Exa | quanda, Geeksforgeeks |
| Compute budgets | Previous | h-e1 |
| Gate threshold (0.70) | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-26T10:09:00+00:00

### Workflow History for This Hypothesis
- h-m3 set to IN_PROGRESS (2026-03-26T10:08:59)
- Phase 2C experiment design started
- Prerequisites verified: h-m2 VALIDATED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Exa (web_search_exa, get_code_context_exa)*
*Archon unavailable - used web search fallback*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
