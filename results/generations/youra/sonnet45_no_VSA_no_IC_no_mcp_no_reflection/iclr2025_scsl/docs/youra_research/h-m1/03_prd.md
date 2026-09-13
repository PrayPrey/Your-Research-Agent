# Product Requirements Document: h-m1 Layer-Neuron Consistency Analysis

**Date:** 2026-08-29  
**Author:** Anonymous  
**Hypothesis:** Temporal gap driven by feature complexity difference (simpler spurious features converge faster) - validated via layer-neuron consistency test  
**Type:** MECHANISM  
**Prerequisites:** h-e1 (VALIDATED ✅)

---

## Executive Summary

### Purpose
Validate the mechanistic explanation for why spurious features converge before core features (observed in h-e1). Test hypothesis: temporal gap driven by feature complexity difference via layer-wise neuron-spurious correlation analysis on h-e1 trained models.

### Success Criteria
- **MUST_WORK Gate:** Early layers (conv1, layer1) show significantly higher spurious correlation than late layers (layer3, layer4)
- **Statistical Requirement:** p < 0.05 (one-sided t-test) AND mean(ρ_early) > mean(ρ_late)
- **Expected Effect Size:** ~2-3× higher correlation in early vs late layers

### Scope
- **In Scope:** Post-hoc analysis on h-e1 ResNet-18 checkpoints, layer-wise activation extraction, neuron-spurious correlation computation, statistical testing
- **Out of Scope:** New model training, dataset collection, GradCAM visualization (future h-e3)

---

## Problem Statement

### Research Question
Does the 4-epoch temporal gap (E_spurious=13, E_core=17) observed in h-e1 result from feature complexity difference, where simpler spurious features (color) are learned by early CNN layers while complex core features (digit shape) require deeper layers?

### Hypothesis
Early CNN layers correlate more with spurious features (color) than late layers, supporting the complexity-driven mechanism for temporal convergence ordering.

### Context
- **Prerequisite:** h-e1 validated temporal ordering (Δ=4 epochs, PASS)
- **Asset:** Trained ResNet-18 checkpoints from h-e1 (baseline, spurious-only, core-only variants)
- **Reuse:** Same CMNIST dataset, no new training required
- **Execution:** ~5 min (single forward pass + correlation computation)

---

## Functional Requirements

### FR-1: Load h-e1 Trained Models
**Priority:** CRITICAL  
**Description:** Load pre-trained ResNet-18 checkpoint from h-e1 validation  
**Acceptance Criteria:**
- Model loaded from `docs/youra_research/h-e1/checkpoints/baseline_seed0.pt`
- State dict correctly mapped to ResNet-18 architecture
- Model in eval mode

**Technical Details:**
```python
import torchvision.models as models
model = models.resnet18(pretrained=False, num_classes=10)
checkpoint = torch.load('./docs/youra_research/h-e1/checkpoints/baseline_seed0.pt')
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()
```

### FR-2: Register Layer-wise Activation Hooks
**Priority:** CRITICAL  
**Description:** Extract activations from conv1, layer1, layer2, layer3, layer4 via forward hooks  
**Acceptance Criteria:**
- Forward hooks registered for all 5 layers
- Activations captured in dictionary format
- Spatial pooling applied (mean over H×W dimensions)

**Technical Details:**
```python
activations = {}
def get_activation(name):
    def hook(model, input, output):
        activations[name] = output.detach()
    return hook

for layer_name in ['conv1', 'layer1', 'layer2', 'layer3', 'layer4']:
    getattr(model, layer_name).register_forward_hook(get_activation(layer_name))
```

### FR-3: Load CMNIST Dataset (from h-e1)
**Priority:** CRITICAL  
**Description:** Load CMNIST test set (10K samples) with spurious feature labels  
**Acceptance Criteria:**
- Dataset loaded from `./data/mnist`
- Color labels (spurious feature) extracted
- Same preprocessing as h-e1 (ToTensor, no augmentation)

**Technical Details:**
- Reuse h-e1 data loading code
- Extract spurious labels from color corruption mapping

### FR-4: Compute Per-Neuron Correlations
**Priority:** CRITICAL  
**Description:** Compute Pearson correlation between each neuron's activations and spurious feature labels  
**Acceptance Criteria:**
- One correlation value (ρ_j) per neuron per layer
- Scipy pearsonr used for computation
- Results stored in layer_rho_j dict

**Technical Details:**
```python
from scipy.stats import pearsonr
layer_rho_j = {}
for layer_name, acts in layer_activations.items():
    acts = torch.cat(acts, dim=0).numpy()  # (10000, num_channels)
    rho_j = [pearsonr(acts[:, i], spurious_labels)[0] 
             for i in range(acts.shape[1])]
    layer_rho_j[layer_name] = np.array(rho_j)
```

### FR-5: Layer Consistency Statistical Test
**Priority:** CRITICAL  
**Description:** Test if early layers have higher mean(ρ_j) than late layers  
**Acceptance Criteria:**
- Early group: concat(conv1, layer1) correlations
- Late group: concat(layer3, layer4) correlations
- One-sided t-test (alternative='greater')
- Report t-statistic and p-value

**Technical Details:**
```python
from scipy.stats import ttest_ind
early = np.concatenate([layer_rho_j['conv1'], layer_rho_j['layer1']])
late = np.concatenate([layer_rho_j['layer3'], layer_rho_j['layer4']])
t_stat, p_value = ttest_ind(early, late, alternative='greater')
```

### FR-6: Visualization - Mean ρ_j Bar Chart
**Priority:** CRITICAL  
**Description:** Bar chart showing mean(ρ_j) per layer with 95% CI  
**Acceptance Criteria:**
- X-axis: 5 layers (conv1, layer1, layer2, layer3, layer4)
- Y-axis: Mean Pearson correlation
- Error bars: 95% confidence intervals
- Saved to `{hypothesis_folder}/figures/layer_correlation_means.png`

### FR-7: Visualization - Per-Neuron Heatmap
**Priority:** HIGH  
**Description:** Heatmap (layers × neurons) showing individual ρ_j values  
**Acceptance Criteria:**
- Rows: Layers
- Columns: Neurons (subsampled if >100 neurons/layer)
- Color scale: -1 to +1 (correlation range)
- Saved to `{hypothesis_folder}/figures/neuron_correlation_heatmap.png`

### FR-8: Visualization - CDF Comparison
**Priority:** MEDIUM  
**Description:** Cumulative distribution of ρ_j for early vs late layer groups  
**Acceptance Criteria:**
- Two curves: Early (conv1+layer1), Late (layer3+layer4)
- X-axis: Correlation value
- Y-axis: Cumulative probability
- Expected: Early curve shifted right (higher correlations)
- Saved to `{hypothesis_folder}/figures/correlation_cdf.png`

### FR-9: Validation Report Generation
**Priority:** CRITICAL  
**Description:** Generate 04_validation.md with test results  
**Acceptance Criteria:**
- Gate verdict: PASS/FAIL based on p < 0.05 AND mean(ρ_early) > mean(ρ_late)
- Per-layer statistics table (mean, std, CI)
- Statistical test results (t-stat, p-value, effect size)
- Figure references with interpretation

---

## Non-Functional Requirements

### NFR-1: Reproducibility
**Priority:** CRITICAL  
**Requirement:** Deterministic results with fixed random seed  
**Metric:** Same ρ_j values across runs with seed=0

### NFR-2: Execution Time
**Priority:** HIGH  
**Requirement:** Analysis completes in <10 minutes  
**Metric:** Single forward pass + correlation computation (no training)

### NFR-3: Memory Efficiency
**Priority:** MEDIUM  
**Requirement:** Fit on single GPU with 8GB VRAM  
**Metric:** Activation storage ~500MB (5 layers × 10K samples × channels)

### NFR-4: Code Clarity
**Priority:** HIGH  
**Requirement:** Clear separation between activation extraction and correlation analysis  
**Metric:** Modular LayerNeuronAnalyzer class

---

## Dependencies

### Internal Dependencies
- **h-e1 Checkpoints:** `docs/youra_research/h-e1/checkpoints/baseline_seed0.pt` (MUST exist)
- **CMNIST Dataset:** `./data/mnist` (auto-download if missing)
- **h-e1 Data Loading:** Reuse spurious feature label extraction logic

### External Dependencies
- PyTorch >= 1.9 (model loading, forward hooks)
- torchvision (ResNet-18 architecture)
- scipy >= 1.7 (pearsonr, ttest_ind)
- numpy (array operations)
- matplotlib (visualization)

---

## Success Metrics

### Primary Gate Metric
**Layer Consistency Test:**
- **Pass Condition:** p < 0.05 AND mean(ρ_early) > mean(ρ_late)
- **Expected Values:**
  - Early layers: mean(ρ_j) ≈ 0.3-0.5
  - Late layers: mean(ρ_j) ≈ 0.05-0.15
  - p-value < 0.01 (strong significance)

### Secondary Metrics
- **Monotonic Decrease:** mean(ρ_conv1) > mean(ρ_layer1) > mean(ρ_layer2) > mean(ρ_layer3) > mean(ρ_layer4)
- **Effect Size:** Cohen's d > 0.8 (large effect)
- **Visualization Quality:** Clear separation in CDF curves

---

## Risk Assessment

### Technical Risks
1. **h-e1 Checkpoint Missing:** Mitigation: Verify file exists in Step 1, fallback to h-e1 re-run if necessary
2. **Weak Correlation Signal:** Mitigation: Use full test set (10K samples) for statistical power
3. **Confounding Layers:** Mitigation: Exclude intermediate layer2 from early/late grouping

### Scientific Risks
1. **Mechanism Alternative:** If test fails (late > early), suggests different mechanism (e.g., gradient magnitude, not complexity)
2. **Baseline Dependency:** Results specific to ResNet-18 architecture (may not generalize to other CNNs)

---

## Appendix

### Traceability to Phase 2C
- **Dataset:** Section "Dataset" → CMNIST from h-e1
- **Models:** Section "Models" → ResNet-18 checkpoints from h-e1
- **Evaluation:** Section "Evaluation" → Pearson correlation + t-test
- **Ablation:** Section "Models" → Layer groups (early vs late)

### Reused Components from h-e1
- Trained model checkpoints (baseline_seed0.pt)
- CMNIST dataset with spurious labels
- Training configuration (for context only, no new training)

---

**Version:** 1.0  
**Status:** Ready for Phase 3 Architecture Design
