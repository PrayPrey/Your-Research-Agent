# Experiment Design: h-c2

**Date:** 2026-08-24
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** Mode profiles transfer across model families: cross-model Pearson r > 0.7 (LLaMA, Mistral, Qwen)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **CONDITION Hypothesis** - Testing whether attribution method mode profiles (memorization, feature transfer, spurious) exhibit stable transfer across different model architectures.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m1 VALIDATED)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-c2
- **Type:** CONDITION
- **Prerequisites:** h-m1 (mode sensitivity mechanism established)

### Gate Condition
SHOULD_WORK: Failure does not block other hypotheses but reduces generalization claims.

---

## Continuation Context

### Previous Hypothesis Results (h-m1)
- **Status:** VALIDATED
- **Key Findings:**
  - All 3 attribution methods (TRAK, TracIn, Kronfluence) correctly integrated
  - Probe pairs cover 3 modes: memorization, feature transfer, spurious
  - Code validation passes - mechanism is testable
- **Implications for h-c2:** Mode profiles exist and are measurable; now test cross-model transfer

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "cross-model transfer attribution influence"**
- Limited direct results for attribution transfer
- Found diffusion model cross-architecture patterns (not directly applicable)

### Exa Web Search Findings

**Paper 1**: "Studying Large Language Model Generalization with Influence Functions" (Anthropic, arXiv:2308.03296)
- **Key Finding:** EK-FAC (Kronfluence) scales to 52B parameter LLMs
- **Relevance:** Influence functions work across LLM scales
- **Cross-lingual generalization:** Influences transfer across languages
- **URL:** https://arxiv.org/abs/2308.03296

**Paper 2**: "Cross-model Transferability among Large Language Models on the Platonic Representations" (ACL 2025)
- **Key Finding:** Concept representations across LLMs align via linear transformations
- **Correlation:** Cross-model transfer achieves strong alignment
- **Weak-to-strong transfer:** Smaller LLM representations control larger LLMs
- **URL:** https://aclanthology.org/2025.acl-long.185/

**Paper 3**: "Characterizing Linear Alignment Across Language Models" (arXiv:2603.18908)
- **Key Finding:** Independently trained models learn similar representations
- **Method:** Affine transformations between hidden states
- **Text generation:** Works across model pairs
- **URL:** https://arxiv.org/html/2603.18908

**Paper 4**: "Do Influence Functions Work on Large Language Models?" (EMNLP 2025 Findings)
- **Key Finding:** Influence functions have limitations on LLMs
- **Challenges:** IHVP approximation errors, uncertain convergence
- **Relevance:** Caveats for experimental design
- **URL:** https://aclanthology.org/2025.findings-emnlp.775.pdf

### 🎯 Implementation Priority Assessment

**CRITICAL: Cross-model transfer requires computing mode profiles on multiple model families**

| Model Family | Size | Source | Availability |
|--------------|------|--------|--------------|
| LLaMA-2 | 7B | meta-llama/Llama-2-7b-hf | HuggingFace |
| Mistral | 7B | mistralai/Mistral-7B-v0.1 | HuggingFace |
| Qwen | 7B | Qwen/Qwen-7B | HuggingFace |

**Recommended Implementation Path:**
- Primary: Use h-m1 CIFAR-10/ResNet framework to establish methodology
- Extension: Apply same probes to vision models from different families (ResNet, ViT, ConvNeXt)
- Alternative: If LLM-scale needed, use Kronfluence (proven LLM support)

---

## Experiment Specification

### Dataset

**Name:** CIFAR-10 (consistent with h-m1 for direct comparison)
**Type:** standard
**Source:** torchvision.datasets.CIFAR10
**Statistics:** 50,000 train / 10,000 test images, 10 classes, 32x32 RGB

**Contrastive Probes:** Same 1000 pairs per mode from h-m1
- **Memorization probes:** Near-duplicate train-test pairs
- **Feature transfer probes:** Same-class pairs with different visual features
- **Spurious probes:** Pairs sharing spurious correlation (e.g., background)

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `torchvision.datasets.CIFAR10`
- Code:
  ```python
  from torchvision.datasets import CIFAR10
  from torchvision import transforms
  
  transform = transforms.Compose([
      transforms.ToTensor(),
      transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
  ])
  train_dataset = CIFAR10(root='./data', train=True, download=True, transform=transform)
  test_dataset = CIFAR10(root='./data', train=False, download=True, transform=transform)
  ```

### Models

**Cross-Model Comparison:** 3 architecturally distinct vision model families

#### Model 1: ResNet-18 (Convolutional, residual connections)
**Architecture:** ResNet-18
**Configuration:** 
- Output classes: 10
- Final layer replaced for CIFAR-10

**Loading Information**:
```python
import torchvision.models as models
model_resnet = models.resnet18(pretrained=True)
model_resnet.fc = torch.nn.Linear(model_resnet.fc.in_features, 10)
```

#### Model 2: ViT-Small (Transformer, attention-based)
**Architecture:** Vision Transformer (ViT-S/16)
**Configuration:**
- Patch size: 16
- Output classes: 10

**Loading Information**:
```python
from timm import create_model
model_vit = create_model('vit_small_patch16_224', pretrained=True, num_classes=10)
```

#### Model 3: ConvNeXt-Tiny (Modern convolutional, transformer-inspired)
**Architecture:** ConvNeXt-Tiny
**Configuration:**
- Output classes: 10

**Loading Information**:
```python
from timm import create_model
model_convnext = create_model('convnext_tiny', pretrained=True, num_classes=10)
```

**Core Mechanism Implementation:**

```python
import torch
import numpy as np
from scipy.stats import pearsonr
from trak import TRAKer
from kronfluence.analyzer import Analyzer, prepare_model

def compute_cross_model_transfer(models, train_loader, probes, method='trak'):
    """
    Compute mode profiles across model families and measure transfer correlation.
    
    Args:
        models: Dict[family_name -> trained_model]
        train_loader: Training data
        probes: Dict[mode_name -> List[probe_pairs]]
        method: Attribution method to use ('trak', 'tracin', 'kronfluence')
    
    Returns:
        Dict containing:
          - profiles: Dict[model -> Dict[mode -> score]]
          - correlations: Dict[(model_a, model_b) -> pearson_r]
          - transfer_success: bool (all r > 0.7)
    """
    profiles = {}
    
    for family, model in models.items():
        if method == 'trak':
            traker = TRAKer(model=model, task='image_classification',
                           train_set_size=len(train_loader.dataset), proj_dim=2048)
            # Featurize training set
            for batch in train_loader:
                traker.featurize(batch=batch, num_samples=batch[0].shape[0])
            traker.finalize_features()
        
        # Compute mode scores
        mode_scores = {}
        for mode, pairs in probes.items():
            scores = []
            for train_idx, test_idx in pairs:
                # Get influence of train_idx on test_idx
                score = compute_influence(traker, train_idx, test_idx)
                scores.append(score)
            mode_scores[mode] = np.mean(scores)
        
        profiles[family] = mode_scores
    
    # Compute pairwise correlations
    model_names = list(profiles.keys())
    correlations = {}
    for i, m1 in enumerate(model_names):
        for m2 in model_names[i+1:]:
            # Profile vector: [mem_score, transfer_score, spurious_score]
            profile1 = np.array([profiles[m1][mode] for mode in ['memorization', 'feature_transfer', 'spurious']])
            profile2 = np.array([profiles[m2][mode] for mode in ['memorization', 'feature_transfer', 'spurious']])
            r, p = pearsonr(profile1, profile2)
            correlations[(m1, m2)] = {'r': r, 'p': p}
    
    # Check transfer criterion: all pairwise r > 0.7
    transfer_success = all(c['r'] > 0.7 for c in correlations.values())
    
    return {
        'profiles': profiles,
        'correlations': correlations,
        'transfer_success': transfer_success
    }
```

### Training Protocol

**Model Training:**
- Train each model family (ResNet-18, ViT-Small, ConvNeXt-Tiny) on CIFAR-10
- **Optimizer:** AdamW (lr=1e-4 for ViT/ConvNeXt, 0.1 for ResNet)
- **Epochs:** 100 (ResNet), 50 (pretrained ViT/ConvNeXt fine-tuning)
- **Batch Size:** 128
- **Checkpoints:** Save every 10 epochs

**Attribution Computation:**
- Use same probe set across all models (1000 pairs × 3 modes)
- Primary method: TRAK (fastest, proven cross-architecture)
- Verification: Kronfluence (more accurate, slower)

**Sources:** TRAK paper, timm library documentation, ACL 2025 cross-model paper

### Evaluation

**Primary Metrics:**
- Cross-model Pearson correlation (r) for mode profiles
- Mode profile vectors: [memorization_sensitivity, transfer_sensitivity, spurious_sensitivity]

**Success Criteria (CONDITION hypothesis):**
- **Pass:** All pairwise cross-model correlations r > 0.7
- **Partial:** Mean r > 0.7, some pairs below threshold
- **Fail:** Mean r < 0.7

**Statistical Tests:**
- Pearson correlation with p-value
- Bootstrap confidence intervals (95% CI)
- Multiple comparison correction (Bonferroni for 3 pairs)

**Metrics Loading Information**:
```python
import numpy as np
from scipy.stats import pearsonr
from scipy.stats import bootstrap

def evaluate_transfer(profiles):
    """Compute cross-model correlations."""
    model_names = list(profiles.keys())
    results = []
    
    for i, m1 in enumerate(model_names):
        for m2 in model_names[i+1:]:
            v1 = np.array(list(profiles[m1].values()))
            v2 = np.array(list(profiles[m2].values()))
            r, p = pearsonr(v1, v2)
            results.append({
                'pair': f'{m1}-{m2}',
                'pearson_r': r,
                'p_value': p,
                'transfer_success': r > 0.7
            })
    
    return results
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Cross-Model Profile Heatmap**: 3×3 matrix showing mode sensitivities per model family
- **Correlation Bar Chart**: Pairwise r values with 0.7 threshold line

#### Additional Figures (LLM Autonomous)
- Mode profile radar charts (one per model)
- Bootstrap confidence interval plot for correlations
- Scatter plot of profile vectors across models

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-c2/figures/`.

---

## 🔬 Condition Verification Protocol

**Pre-conditions:**
- prerequisite_satisfied: True (h-m1 VALIDATED)
- models_compatible: True (all support gradient computation)
- probes_consistent: True (same probe set across models)

**Architecture Compatibility:**
- TRAK: Supports all architectures via gradient hooks
- Kronfluence: Requires nn.Linear/nn.Conv2d (all models compatible)

**Transfer Indicators:**
- cross_model_r: Pearson correlation between profile vectors
- profile_consistency: Variance within model < variance across models
- threshold: r > 0.7 for all pairs

**Verification Code:**
```python
def verify_transfer(results):
    """Verify cross-model transfer succeeds."""
    correlations = results['correlations']
    
    # Check 1: All correlations significant (p < 0.05)
    all_significant = all(c['p'] < 0.05 for c in correlations.values())
    
    # Check 2: All r > 0.7
    all_above_threshold = all(c['r'] > 0.7 for c in correlations.values())
    
    # Check 3: Mean r
    mean_r = np.mean([c['r'] for c in correlations.values()])
    
    return {
        'pass': all_above_threshold,
        'mean_r': mean_r,
        'significant': all_significant,
        'details': correlations
    }
```

**Hypothesis Support:**
- threshold: All pairwise r > 0.7
- metric: Pearson correlation of mode profile vectors

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs for all 3 model families without error
2. Mode profiles computed for each model
3. Pairwise correlations computed
4. Statistical tests executed (Pearson r with p-values)

**Minimum Viable Result:**
- 3 model profiles computed
- 3 pairwise correlations (ResNet-ViT, ResNet-ConvNeXt, ViT-ConvNeXt)
- Clear pass/fail determination based on r > 0.7 criterion

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

Limited direct results for cross-model attribution transfer.

### B. Exa Web Search Sources

**Paper 1**: "Studying Large Language Model Generalization with Influence Functions"
- **URL**: https://arxiv.org/abs/2308.03296
- **Used For**: Kronfluence scaling methodology, cross-lingual transfer patterns

**Paper 2**: "Cross-model Transferability among LLMs on Platonic Representations"
- **URL**: https://aclanthology.org/2025.acl-long.185/
- **Used For**: Linear transformation alignment methodology, r > 0.7 threshold justification

**Paper 3**: "Characterizing Linear Alignment Across Language Models"
- **URL**: https://arxiv.org/html/2603.18908
- **Used For**: Cross-model representation alignment theory

### C. GitHub Implementations

**Repository 1**: MadryLab/trak
- **URL**: https://github.com/MadryLab/trak
- **Used For**: Primary attribution method (TRAK)

**Repository 2**: pomonam/kronfluence
- **URL**: https://github.com/pomonam/kronfluence
- **Used For**: Verification attribution method (Kronfluence)

**Repository 3**: huggingface/pytorch-image-models (timm)
- **URL**: https://github.com/huggingface/pytorch-image-models
- **Used For**: ViT and ConvNeXt model loading

### D. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| TRAK implementation | GitHub | MadryLab/trak |
| Kronfluence implementation | GitHub | pomonam/kronfluence |
| ViT/ConvNeXt models | GitHub | huggingface/pytorch-image-models |
| Dataset (CIFAR-10) | Standard | torchvision |
| Cross-model theory | Research | ACL 2025 (Huang et al.) |
| r > 0.7 threshold | Research | ACL 2025 cross-model paper |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- 2026-08-24: Phase 2C experiment design started
- 2026-08-24: Exa search completed (4 papers on cross-model transfer)
- 2026-08-24: Archon KB search (limited results)
- 2026-08-24: Experiment specification synthesized
- 2026-08-24: Phase 2C experiment design completed

---

*MCP Tools Used: Archon (Knowledge Base), Exa (Web Search)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
