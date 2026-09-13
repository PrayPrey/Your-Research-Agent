# Experiment Design: H-M2

**Date:** 2026-04-21
**Author:** Anonymous
**Hypothesis Statement:** Under pretrained CNN architectures, if residual connections (ResNet), dense connections (DenseNet), and bottleneck layers exist in deep models but not shallow models, then weight structures will exhibit depth-specific patterns, because architectural constraints shape weight organization.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Hypothesis** - Tests architectural constraints as mechanism for depth classification.

---

## Workflow Status

**Verification State:** IN_PROGRESS (Phase 2C - Experiment Design)
**Prerequisites Satisfied:** ✅ H-M1 COMPLETED (100% test accuracy, gate PASS)
**Gate Status:** SHOULD_WORK (test accuracy > 50%)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** Mechanism
- **Prerequisites:** H-M1 (Gradient Accumulation Creates Depth-Specific Patterns)

### Gate Condition

**Gate Type:** SHOULD_WORK  
**Condition:** Architecture features contribute to classification (within-family accuracy ≥ 65%)  
**Consequence if Fails:** Document as limitation, focus on H-M1/H-M3

---

## Continuation Context

**This is a CONTINUATION experiment building on H-M1.**

H-M2 tests the second mechanism hypothesis in the sequential causal chain:
- H-E1 validated: Weight statistics enable 100% depth classification
- H-M1 tested gradient accumulation: 100% accuracy but MECHANISM REJECTED (random models also achieved 100%)
- **H-M2 focuses on: Architectural constraints** (residual/dense connections, bottleneck layers)

**Key Insight from H-M1:** Features are **architectural, not training-induced**. Random initialization test showed 100% accuracy on random models, indicating the discriminative patterns exist in architecture itself, not gradient flow during training.

**H-M2 Strategy:** Directly extract architectural features (residual blocks, dense connections, bottleneck ratios) instead of gradient-flow proxies. This aligns with H-M1's unexpected finding.

### Previous Hypothesis Results (H-M1)

**H-M1 Results Summary:**
- **Test Accuracy:** 100% (4/4 correct) ✓ GATE PASS
- **Random Test Accuracy:** 100% (4/4 correct) ✗ MECHANISM REJECTED
- **Key Finding:** Gradient-flow features are actually architectural proxies
- **Mechanism Conclusion:** Gradient accumulation is NOT the mechanism; architectural depth is the true discriminator

**Optimal Configuration (reused for H-M2):**
- Classifier: LogisticRegression (C=1.0, solver='lbfgs')
- Feature normalization: StandardScaler
- Train/test split: 80/20 stratified, seed=42
- Achieved: 100% accuracy

**Implications for H-M2:**
- **HIGH PRIORITY:** Architectural mechanisms dominate (confirmed by H-M1 random test)
- **Feature Design:** Extract explicit architectural features (residual blocks, bottleneck ratios)
- **Validation:** Must use random initialization test to verify training vs architecture effects
- **Within-Family Test:** Critical to isolate depth signal from architecture type confounds

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Architectural Constraints Experiment Design**

- **ResNet Deep Residual Learning (He et al. 2016)**
  - Datasets: ImageNet, CIFAR-10
  - Key Insights: Residual connections enable 50-152 layer networks; identity shortcuts introduce no parameters; batch normalization after each conv; He initialization
  - Hyperparameters: SGD momentum 0.9, LR 0.1 (decay 10× at epochs 30/60), batch 256, weight decay 1e-4

- **DenseNet Densely Connected Networks (Huang et al. 2017)**
  - Datasets: ImageNet, CIFAR-100
  - Key Insights: Dense connections (each layer → all subsequent); growth rate k=32; bottleneck layers (1×1 conv); transition layers compress features
  - Hyperparameters: SGD Nesterov momentum 0.9, LR 0.1 (decay 0.1× at epochs 150/225), batch 64, weight decay 1e-4

- **VGG Architecture (Simonyan & Zisserman 2015)**
  - Dataset: ImageNet
  - Key Insights: Sequential architecture WITHOUT skip connections; VGG16/19 have 16-19 layers but no residual paths; 3×3 convs, max pooling
  - Critical: VGG is deep but lacks architectural constraints (control group for H-M2)

- **Architecture-Specific Weight Distributions (Network Dissection)**
  - Finding: Residual networks show DIFFERENT weight norm distributions than sequential networks
  - Mechanism: Skip connections preserve gradient flow, affecting weight magnitudes
  - Pattern: Bottleneck layers create distinct weight patterns
  - Correlation: Architectural depth correlates with layer-wise weight statistics

- **Model Fingerprinting Research**
  - Result: Architecture family can be inferred from weight statistics (85-95% accuracy)
  - Key: Residual connections create characteristic weight signatures
  - Features: Layer count + connection patterns are discriminative
  - Benchmark: Within-family classification achieves 80-95% accuracy

**Query 2: Implementation Challenges & Best Practices**

**Challenges Identified:**
- Confounding: Depth, width, and architecture type are correlated
- Within-family variance: ResNet18 vs ResNet152 differ in both depth AND residual block count
- Training variance: Different initializations affect weight distributions
- Feature isolation: Separating architectural effects from training effects

**Best Practices:**
- ✓ Control for architecture family (within-family validation)
- ✓ Use standardized pretrained models (torchvision reduces training variance)
- ✓ Random initialization test (isolate architectural vs training effects) ← **CRITICAL from H-M1**
- ✓ Extract architecture-specific features (residual blocks, skip connections)

**Implementation Tips:**
- Residual blocks: Detect via layer naming patterns ("layer1.0.downsample")
- Bottleneck layers: 1×1 → 3×3 → 1×1 convolution patterns
- DenseNet: Concatenation vs ResNet addition
- VGG pitfall: Deep (VGG19=19 layers) but NO residual connections

**Validation Protocol:**
- Within-family accuracy ≥ 65% → depth signal is real
- VGG classification success → validates depth over architecture type
- Feature importance analysis → reveals which architectural patterns matter

**Query 3: PyTorch Torchvision Benchmark**

**Available Models (20+):**
- ResNet family: resnet18 (18 layers), resnet34 (34), resnet50 (50), resnet101 (101), resnet152 (152)
- VGG family: vgg11 (11), vgg13 (13), vgg16 (16), vgg19 (19)
- DenseNet family: densenet121 (121), densenet161 (161), densenet169 (169), densenet201 (201)

**Shallow models (≤34 layers):** ResNet18, ResNet34, VGG11, VGG13, VGG16
**Deep models (≥50 layers):** ResNet50, ResNet101, ResNet152, DenseNet121, DenseNet169, DenseNet201

**Expected Performance:**
- Weight-based model family classification: 85-95% accuracy
- Depth classification (shallow vs deep): 70-80% with good features
- Within-family depth classification: 60-75% (harder, reduced variance)
- Random baseline: 50%

**Standardization:** All ImageNet-1K pretrained, standard preprocessing (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])

### Archon Code Examples

**Example 1: ResNet Residual Block Detection**
```python
# Detect residual blocks in ResNet
def count_residual_blocks(model):
    residual_blocks = 0
    for name, module in model.named_modules():
        # ResNet bottleneck blocks have downsample attribute
        if hasattr(module, 'downsample'):
            residual_blocks += 1
    return residual_blocks

# Extract residual path weight norms
def extract_residual_features(model):
    features = []
    for name, param in model.named_parameters():
        if 'downsample' in name or 'shortcut' in name:
            features.append(param.norm().item())
    return features
```
**Pattern:** Residual block counting via module inspection  
**Insight:** Residual blocks detectable by downsample/shortcut attributes

**Example 2: DenseNet Dense Connection Analysis**
```python
# Count dense connections in DenseNet
def count_dense_connections(model):
    dense_connections = 0
    for name, module in model.named_modules():
        if 'denselayer' in name.lower():
            dense_connections += 1
    return dense_connections

# Extract transition layer statistics
def extract_transition_features(model):
    transition_norms = []
    for name, param in model.named_parameters():
        if 'transition' in name.lower():
            transition_norms.append(param.norm().item())
    return transition_norms
```
**Pattern:** Dense connection counting via layer naming  
**Insight:** DenseNet has characteristic naming (denselayer, transition)

**Example 3: Bottleneck Layer Detection**
```python
# Detect bottleneck layers (1x1 convolutions)
def count_bottleneck_layers(model):
    bottleneck_count = 0
    total_conv = 0
    for module in model.modules():
        if isinstance(module, torch.nn.Conv2d):
            total_conv += 1
            if module.kernel_size == (1, 1):
                bottleneck_count += 1
    bottleneck_ratio = bottleneck_count / total_conv if total_conv > 0 else 0
    return bottleneck_count, bottleneck_ratio
```
**Pattern:** Bottleneck detection via kernel size  
**Insight:** 1×1 convs common in ResNet/DenseNet, absent in VGG

**Example 4: Comprehensive Architectural Feature Extractor**
```python
def extract_architectural_features(model):
    features = {}
    
    # Layer counts
    conv_layers = sum(1 for m in model.modules() if isinstance(m, nn.Conv2d))
    features['total_conv_layers'] = conv_layers
    
    # Residual blocks (ResNet)
    features['residual_blocks'] = count_residual_blocks(model)
    
    # Bottleneck ratio
    features['bottleneck_ratio'] = count_bottleneck_layers(model)[1]
    
    # Dense connections (DenseNet)
    features['dense_connections'] = count_dense_connections(model)
    
    # Architecture family detection
    model_name = model.__class__.__name__.lower()
    features['is_resnet'] = 'resnet' in model_name
    features['is_vgg'] = 'vgg' in model_name
    features['is_densenet'] = 'densenet' in model_name
    
    return features
```
**Pattern:** Multi-signal architectural feature extraction  
**Insight:** Combining residual blocks, bottlenecks, architecture family creates rich features

**Example 5: Within-Family Classification**
```python
# Within-family depth classification
def within_family_classification(models, labels, families):
    results = {}
    for family in set(families):
        # Filter models by family
        family_mask = [f == family for f in families]
        family_models = [m for m, mask in zip(models, family_mask) if mask]
        family_labels = [l for l, mask in zip(labels, family_mask) if mask]
        
        if len(family_models) < 4:
            continue  # Skip if too few samples
        
        # Train classifier on this family only
        X = extract_features(family_models)
        clf = LogisticRegression()
        
        # 80/20 split
        X_train, X_test, y_train, y_test = train_test_split(
            X, family_labels, test_size=0.2, stratify=family_labels
        )
        clf.fit(X_train, y_train)
        accuracy = clf.score(X_test, y_test)
        results[family] = accuracy
    
    return results
```
**Pattern:** Family-specific training and evaluation  
**Insight:** Within-family validation isolates depth signal from architecture type confounds

### Exa GitHub Implementations

**Query 1: ResNet/DenseNet Architectural Feature Extraction**

**Repository 1: pytorch/vision** (⭐ 14,800)
- **URL**: https://github.com/pytorch/vision
- **Relevance**: Official PyTorch torchvision library - reference implementations used by H-E1 and H-M1
- **Architecture**: ResNet (BasicBlock with downsample for residual connections), DenseNet (_DenseLayer with concatenation)
- **Key Architectural Patterns**:
  - **ResNet**: `self.downsample` attribute identifies residual connections, `out += identity` performs residual addition
  - **DenseNet**: `torch.cat([x, new_features], 1)` performs dense concatenation, bottleneck layers use 1×1 convolutions
- **Training Config**: SGD with momentum, batch size 256 (ImageNet), 90-120 epochs
- **Dataset**: ImageNet-1K pretrained weights (same as H-E1/H-M1)
- **Results**: Provides the exact pretrained models analyzed in H-E1 and H-M1

**Repository 2: kuangliu/pytorch-cifar** (⭐ 5,200)
- **URL**: https://github.com/kuangliu/pytorch-cifar
- **Relevance**: Clean comparison of ResNet, VGG, DenseNet architectures
- **Architecture**: Multi-family comparison with clear architectural differences
- **Key Code**:
  - **ResNet**: `_make_layer()` method creates residual blocks with stride control
  - **VGG**: Sequential architecture with NO skip connections (control group for H-M2)
- **Training Config**: SGD momentum 0.9, LR 0.1 (decay 0.1× at epochs 150/250), batch 128, 350 epochs, weight decay 5e-4
- **Dataset**: CIFAR-10/100
- **Results**: Demonstrates architectural differences across families

**Repository 3: weiaicunzai/pytorch-cifar100** (⭐ 3,100)
- **URL**: https://github.com/weiaicunzai/pytorch-cifar100
- **Relevance**: Provides weight statistics extraction utilities directly applicable to H-M2
- **Key Code**:
```python
def get_network_params(net):
    \"\"\"Extract network parameter statistics\"\"\"
    layer_params = []
    for name, param in net.named_parameters():
        layer_params.append({
            'name': name,
            'shape': list(param.shape),
            'mean': param.data.mean().item(),
            'std': param.data.std().item(),
            'norm': param.data.norm().item()
        })
    return layer_params
```
- **Pattern**: Layer-wise statistics extraction matching H-M2 feature requirements
- **Training Config**: SGD momentum 0.9, LR 0.1 (decay at milestones [60,120,160]), batch 128, 200 epochs, weight decay 5e-4

**Query 2: CNN Architecture Classification & Analysis**

**Repository 4: Cadene/pretrained-models.pytorch** (⭐ 8,900)
- **URL**: https://github.com/Cadene/pretrained-models.pytorch
- **Relevance**: Unified interface for 50+ pretrained models - simplifies batch loading
- **Architecture**: Supports ResNet, VGG, DenseNet, and many others with consistent API
- **Key Code**: `model = pretrainedmodels.__dict__[model_name](pretrained='imagenet')`
- **Batch Loading**: Enables loading multiple model families programmatically
- **Dataset**: ImageNet pretrained weights
- **Results**: Simplifies multi-model analysis workflow

**Repository 5: idiap/residual-networks-analysis** (⭐ 120)
- **URL**: https://github.com/idiap/residual-networks-analysis
- **Relevance**: Research on analyzing residual network properties - DIRECTLY RELEVANT TO H-M2
- **Architecture**: ResNet analysis with focus on residual connections
- **Key Code**:
```python
def analyze_residual_structure(model):
    \"\"\"Extract residual connection statistics\"\"\"
    residual_info = {
        'num_residual_blocks': 0,
        'residual_path_norms': [],
        'bottleneck_layers': 0
    }
    
    for name, module in model.named_modules():
        # Detect residual blocks
        if hasattr(module, 'downsample'):
            residual_info['num_residual_blocks'] += 1
            if module.downsample is not None:
                for param in module.downsample.parameters():
                    norm = param.data.norm().item()
                    residual_info['residual_path_norms'].append(norm)
        
        # Detect bottleneck layers (1x1 conv)
        if isinstance(module, nn.Conv2d) and module.kernel_size == (1, 1):
            residual_info['bottleneck_layers'] += 1
    
    return residual_info
```
- **Pattern**: Residual block detection via `downsample` attribute, bottleneck detection via kernel size
- **Within-Family Analysis**: Includes code for comparing shallow vs deep within same architecture family
- **Results**: Provides exact feature extraction methods needed for H-M2 architectural hypothesis

**Repository 6: sovrasov/flops-counter.pytorch** (⭐ 2,800)
- **URL**: https://github.com/sovrasov/flops-counter.pytorch
- **Relevance**: Model analysis toolkit - adaptable for architectural feature extraction
- **Architecture**: Generic CNN analysis tools
- **Key Code**: Layer-wise architecture analysis via `named_modules()` iteration
- **Pattern**: Module type inspection for architectural feature detection

**Serena Analysis Needed**: ❌ No - Code is clear and well-documented, standard PyTorch patterns

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**H-M2 is NOT a paper reproduction experiment** - it's a mechanism hypothesis testing architectural constraints in pretrained CNNs.

**Implementation Priority:**

1. **Primary (HIGHEST)**: `pytorch/vision` (torchvision official models)
   - Rationale: Official PyTorch implementations used by H-E1 and H-M1
   - Provides: Exact pretrained models from standardized ImageNet training
   - Status: ✅ Available and validated in previous hypotheses

2. **Secondary (FALLBACK)**: `idiap/residual-networks-analysis`
   - Rationale: Research code for analyzing residual network properties
   - Provides: Architectural feature extraction methods
   - Status: ✅ Available for reference

3. **Tertiary (REFERENCE)**: `kuangliu/pytorch-cifar`, `weiaicunzai/pytorch-cifar100`
   - Rationale: Clean architecture comparisons and weight extraction utilities
   - Provides: Code patterns for multi-architecture analysis
   - Status: ✅ Available for pattern reference

**Recommended Implementation Path:**
- **Primary**: Use `torchvision.models` for pretrained model loading (resnet18-152, vgg11-19, densenet121-201)
- **Fallback**: If torchvision models fail, use `Cadene/pretrained-models.pytorch` for unified interface
- **Justification**: torchvision is official PyTorch library, standardized training, already validated in H-E1/H-M1 with 100% accuracy

### Code Analysis (Serena MCP)

**Serena Analysis Status:** ❌ Not Required

**Rationale:** 
- Code from Exa/Archon is clear and well-documented
- Standard PyTorch patterns (model loading, parameter iteration, module inspection)
- Architectural feature extraction follows established patterns from `idiap/residual-networks-analysis`
- No complex or ambiguous implementations requiring semantic analysis

**Code Clarity:**
- ✅ ResNet residual block detection: `hasattr(module, 'downsample')`
- ✅ DenseNet layer detection: `'denselayer' in name.lower()`
- ✅ Bottleneck detection: `module.kernel_size == (1, 1)`
- ✅ All patterns are standard PyTorch module inspection

---

## Experiment Specification

### Dataset

**Dataset Specification** (from Phase 2A via Phase 2B):

**Name**: PyTorch Torchvision Pretrained Models  
**Type**: `standard` (real pretrained models from torchvision)  
**Source**: torchvision.models (PyTorch official repository)  
**Scope**: 20 pretrained ImageNet CNN models across 3 families

**Model Families & Depth Categories**:
- **Shallow (≤34 layers)**: ResNet18, ResNet34, VGG11, VGG13, VGG16, VGG19
- **Deep (≥50 layers)**: ResNet50, ResNet101, ResNet152, DenseNet121, DenseNet169, DenseNet201

**Statistics**:
- Total models: 20 (10 shallow, 10 deep)
- Train/test split: 80/20 stratified (16 train, 4 test, seed=42)
- All models: ImageNet-1K pretrained with standardized training

**Preprocessing**: 
- Models used as-is (pretrained weights)
- Weight extraction: Frobenius norm per layer via `torch.linalg.norm(param.data, ord='fro')`
- No data augmentation (weight analysis, not image training)

**Hypothesis Fit**: Provides multiple architecture families (ResNet with residual connections, VGG without residual connections, DenseNet with dense connections) enabling architectural constraint testing across standardized depth categories.

**Loading Information** (for Phase 4 download):
- Method: `torchvision.models` (built-in PyTorch)
- Identifier: Model function names (e.g., `resnet50`, `vgg16`, `densenet121`)
- Code:
```python
import torchvision.models as models

# Load pretrained models
shallow_models = [
    models.resnet18(pretrained=True),
    models.resnet34(pretrained=True),
    models.vgg11(pretrained=True),
    models.vgg13(pretrained=True),
    models.vgg16(pretrained=True),
    models.vgg19(pretrained=True),
]

deep_models = [
    models.resnet50(pretrained=True),
    models.resnet101(pretrained=True),
    models.resnet152(pretrained=True),
    models.densenet121(pretrained=True),
    models.densenet169(pretrained=True),
    models.densenet201(pretrained=True),
]
```

### Models

#### Baseline Model

**Architecture**: sklearn LogisticRegression  
**Type**: Binary linear classifier (shallow vs deep)  
**Source**: scikit-learn (built-in)

**Configuration**:
- Solver: `lbfgs` (L-BFGS optimization)
- Regularization: C=1.0 (inverse regularization strength)
- Max iterations: 1000
- Multi-class: Not applicable (binary classification)

**Input**: Architectural feature vector (dimension varies by feature set)  
**Output**: Binary prediction (0=shallow, 1=deep)

**Hypothesis Fit**: Simple linear classifier appropriate for mechanism validation. Interprets feature importance via logistic regression coefficients. Reuses optimal configuration from H-E1 and H-M1 for controlled comparison.

**Loading Information** (for Phase 4 download):
- Method: `sklearn.linear_model` (built-in scikit-learn)
- Identifier: `LogisticRegression`
- Code:
```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Initialize classifier
clf = LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000, random_state=42)
scaler = StandardScaler()

# Training pattern
X_scaled = scaler.fit_transform(X_train)
clf.fit(X_scaled, y_train)
```

#### Proposed Model

**Architecture**: LogisticRegression + Architectural Constraint Features

**Feature Set Design** (H-M2 Mechanism):

Based on H-M1 findings (architectural features, not gradient-induced) and Exa/Archon research, extract 8 architectural constraint features:

1. **Residual Block Count** (ResNet-specific)
2. **Dense Connection Count** (DenseNet-specific)  
3. **Bottleneck Layer Ratio** (1×1 conv count / total conv count)
4. **Layer Count** (total trainable layers)
5. **Skip Connection Presence** (binary: has residual/dense connections)
6. **Architecture Family** (one-hot: ResNet, VGG, DenseNet)
7. **Residual Path Weight Norm** (mean of downsample layer norms)
8. **Transition Layer Count** (DenseNet-specific)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Architectural Constraint Feature Extraction
# Based on: idiap/residual-networks-analysis, pytorch/vision

import torch
import torch.nn as nn

def extract_architectural_features(model):
    """
    Extract architectural constraint features for depth classification.
    
    Args:
        model: PyTorch model (ResNet, VGG, or DenseNet)
    
    Returns:
        features: (8,) numpy array of architectural features
    """
    features = {}
    
    # Detect architecture family
    model_name = model.__class__.__name__.lower()
    features['is_resnet'] = 1 if 'resnet' in model_name else 0
    features['is_vgg'] = 1 if 'vgg' in model_name else 0
    features['is_densenet'] = 1 if 'densenet' in model_name else 0
    
    # Count layers and architectural components
    total_conv = 0
    bottleneck_count = 0
    residual_blocks = 0
    dense_connections = 0
    transition_layers = 0
    residual_norms = []
    
    for name, module in model.named_modules():
        # Count convolution layers
        if isinstance(module, nn.Conv2d):
            total_conv += 1
            # Bottleneck layers (1x1 conv)
            if module.kernel_size == (1, 1):
                bottleneck_count += 1
        
        # Residual blocks (ResNet)
        if hasattr(module, 'downsample'):
            residual_blocks += 1
            if module.downsample is not None:
                for param in module.downsample.parameters():
                    residual_norms.append(param.data.norm().item())
        
        # Dense connections (DenseNet)
        if 'denselayer' in name.lower():
            dense_connections += 1
        
        # Transition layers (DenseNet)
        if 'transition' in name.lower():
            transition_layers += 1
    
    # Compute features
    features['layer_count'] = total_conv
    features['residual_blocks'] = residual_blocks
    features['dense_connections'] = dense_connections
    features['bottleneck_ratio'] = bottleneck_count / total_conv if total_conv > 0 else 0
    features['skip_connection_present'] = 1 if (residual_blocks > 0 or dense_connections > 0) else 0
    features['residual_path_norm'] = np.mean(residual_norms) if residual_norms else 0
    features['transition_layers'] = transition_layers
    
    # Return as array (8 features)
    feature_vector = np.array([
        features['residual_blocks'],
        features['dense_connections'],
        features['bottleneck_ratio'],
        features['layer_count'],
        features['skip_connection_present'],
        features['residual_path_norm'],
        features['transition_layers'],
        features['is_resnet'] + features['is_densenet']  # Has architectural constraints
    ])
    
    return feature_vector

# Integration: Replace H-E1 global statistics with architectural features
```

### Training Protocol

**From Previous Hypothesis (H-M1)**:

Since H-M2 is a continuation of H-M1 testing a different mechanism, we reuse the optimal training configuration for controlled comparison:

- **Optimizer**: Not applicable (LogisticRegression uses L-BFGS solver)
- **Feature Normalization**: StandardScaler (mean=0, std=1) - from H-E1/H-M1
- **Train/Test Split**: 80/20 stratified (16 train, 4 test) - from H-E1/H-M1
- **Random Seed**: 42 (fixed) - from H-E1/H-M1
- **Classifier Parameters**: C=1.0, solver='lbfgs', max_iter=1000 - from H-E1/H-M1

**Rationale**: Optimal in H-E1 and H-M1 (both achieved 100% accuracy), reusing for controlled experiment. Only feature extraction changes (architectural constraints vs gradient-flow or global statistics).

**Additional Protocol**:
- **Random Initialization Test**: Test on randomly initialized models (pretrained=False) to verify architectural vs training effects (following H-M1 protocol)
- **Within-Family Validation**: Train separate classifiers for ResNet-only, VGG-only, DenseNet-only subsets to test depth signal within architecture families

### Evaluation

**Primary Metrics**:
- **Test Accuracy**: Classification accuracy on 4 held-out models
- **Gate Threshold**: >50% (SHOULD_WORK gate for mechanism hypothesis)

**Success Criteria** (MECHANISM Hypothesis):
- **Gate Pass**: Test accuracy > 50% (mechanism features contribute)
- **Mechanism Validation**: Random initialization test - pretrained and random should differ
  - Expected: Pretrained accuracy >> random accuracy (architectural constraints shaped by training)
  - H-M1 baseline: Both achieved 100% (features were purely architectural, not training-induced)
- **Within-Family Validation**: Within-family accuracy ≥ 65% indicates depth signal exists independent of architecture type

**Expected Baseline Performance** (from research and H-M1):
- H-E1 (global statistics): 100% test accuracy
- H-M1 (gradient-flow features): 100% test accuracy, 100% random accuracy
- Within-family classification: 60-75% (from Archon KB research)
- Random baseline: 50%

**Source**: H-M1 validation report, Archon KB findings on within-family classification

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: `binary_classification`
- Library: `sklearn.metrics`
- Code:
```python
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Evaluation
y_pred = clf.predict(scaler.transform(X_test))
test_accuracy = accuracy_score(y_test, y_pred)
print(f"Test Accuracy: {test_accuracy:.2%}")
print(classification_report(y_test, y_pred, target_names=['shallow', 'deep']))
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Test accuracy vs 50% gate threshold bar chart

#### Additional Figures (LLM Autonomous)

Based on H-M2's mechanism hypothesis (architectural constraints), generate:

1. **Feature Importance Bar Chart**: Logistic regression coefficients for 8 architectural features
2. **Within-Family Accuracy Comparison**: Bar chart showing accuracy for ResNet-only, VGG-only, DenseNet-only, and All-families
3. **Architectural Feature Distributions**: Box plots of 8 features split by shallow vs deep
4. **Random vs Pretrained Comparison**: Side-by-side bar chart (pretrained accuracy vs random accuracy)
5. **Confusion Matrix**: 2×2 matrix for test set predictions
6. **H-E1 vs H-M1 vs H-M2 Comparison**: Three-way accuracy comparison across hypotheses

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1: ResNet Deep Residual Learning Experiments**
- **Type**: Knowledge base article (He et al. 2016)
- **Query Used**: "architectural constraints residual connections dense connections experiment design"
- **Key Insights**:
  - Residual connections enable 50-152 layer networks
  - Identity shortcuts introduce no additional parameters
  - Batch normalization after each convolution layer
  - He initialization for residual blocks
- **Used For**: Understanding residual connection architecture, hyperparameters

**Source 2: DenseNet Densely Connected Convolutional Networks**
- **Type**: Knowledge base article (Huang et al. 2017)
- **Query Used**: Same as Source 1
- **Key Insights**:
  - Dense connections: each layer connects to all subsequent layers
  - Growth rate k=32 controls channel expansion
  - Bottleneck layers (1×1 conv) reduce parameters
  - Transition layers compress feature maps
- **Used For**: Understanding dense connection architecture, DenseNet-specific features

**Source 3: VGG Architecture Analysis**
- **Type**: Knowledge base article (Simonyan & Zisserman 2015)
- **Key Insights**:
  - Sequential architecture WITHOUT skip connections
  - VGG16/19 are deep (16-19 layers) but lack residual connections
  - Critical for H-M2: VGG serves as control group (no architectural constraints)
- **Used For**: Identifying control group architecture for hypothesis testing

**Source 4: Challenges in Deep Architecture Analysis**
- **Type**: Best practices documentation
- **Query Used**: "architectural constraints implementation challenges best practices CNN"
- **Key Insights**:
  - Confounding factors: depth, width, architecture type are correlated
  - Best practice: Within-family validation to isolate depth signal
  - Recommendation: Random initialization test to separate architectural vs training effects
- **Used For**: Validation protocol design, within-family testing strategy

**Source 5: Within-Family Classification Strategy**
- **Type**: Implementation guidance
- **Query Used**: Same as Source 4
- **Success Criteria**: Within-family accuracy ≥ 65% indicates depth signal is real
- **Used For**: Evaluation metrics, success criteria design

### B. Archon Code Examples

**Code Source 1: ResNet Residual Block Detection**
- **Query Used**: "residual connections dense connections PyTorch feature extraction"
- **Key Code**:
```python
def count_residual_blocks(model):
    residual_blocks = 0
    for name, module in model.named_modules():
        if hasattr(module, 'downsample'):
            residual_blocks += 1
    return residual_blocks
```
- **Used For**: Core mechanism pseudo-code (residual block counting)

**Code Source 2: DenseNet Dense Connection Analysis**
- **Query Used**: Same as Code Source 1
- **Key Code**:
```python
def count_dense_connections(model):
    dense_connections = 0
    for name, module in model.named_modules():
        if 'denselayer' in name.lower():
            dense_connections += 1
    return dense_connections
```
- **Used For**: Core mechanism pseudo-code (dense connection counting)

**Code Source 3: Bottleneck Layer Detection**
- **Query Used**: Same as Code Source 1
- **Key Code**:
```python
def count_bottleneck_layers(model):
    bottleneck_count = 0
    for module in model.modules():
        if isinstance(module, torch.nn.Conv2d):
            if module.kernel_size == (1, 1):
                bottleneck_count += 1
    return bottleneck_count
```
- **Used For**: Core mechanism pseudo-code (bottleneck ratio feature)

### C. GitHub Implementations (Exa)

**Repository 1: pytorch/vision** (⭐ 14,800)
- **URL**: https://github.com/pytorch/vision
- **Query Used**: "ResNet DenseNet architectural feature extraction PyTorch implementation GitHub"
- **Relevance**: Official PyTorch torchvision library - reference implementations
- **Key Architecture Patterns**:
  - ResNet: `self.downsample` attribute for residual connections
  - DenseNet: `torch.cat([x, new_features], 1)` for dense concatenation
  - Bottleneck layers: 1×1 convolutions in DenseNet and ResNet
- **Used For**: Dataset specification (pretrained model loading), baseline model configuration

**Repository 2: idiap/residual-networks-analysis** (⭐ 120)
- **URL**: https://github.com/idiap/residual-networks-analysis
- **Query Used**: "CNN architecture classification weight statistics PyTorch GitHub"
- **Relevance**: DIRECTLY RELEVANT - research on analyzing residual network properties
- **Key Code**:
```python
def analyze_residual_structure(model):
    residual_info = {
        'num_residual_blocks': 0,
        'residual_path_norms': [],
        'bottleneck_layers': 0
    }
    for name, module in model.named_modules():
        if hasattr(module, 'downsample'):
            residual_info['num_residual_blocks'] += 1
        if isinstance(module, nn.Conv2d) and module.kernel_size == (1, 1):
            residual_info['bottleneck_layers'] += 1
    return residual_info
```
- **Used For**: Core mechanism pseudo-code synthesis, architectural feature extraction pattern

**Repository 3: kuangliu/pytorch-cifar** (⭐ 5,200)
- **URL**: https://github.com/kuangliu/pytorch-cifar
- **Query Used**: Same as Repository 1
- **Relevance**: Clean comparison of ResNet, VGG, DenseNet architectures
- **Used For**: Understanding architectural differences, VGG as control group (no skip connections)

**Repository 4: weiaicunzai/pytorch-cifar100** (⭐ 3,100)
- **URL**: https://github.com/weiaicunzai/pytorch-cifar100
- **Query Used**: Same as Repository 1
- **Key Utility**:
```python
def get_network_params(net):
    layer_params = []
    for name, param in net.named_parameters():
        layer_params.append({
            'name': name,
            'norm': param.data.norm().item()
        })
    return layer_params
```
- **Used For**: Weight statistics extraction pattern

### D. Previous Hypothesis Context

**H-M1 Validation Report** (h-m1/04_validation.md)
- **Key Result**: 100% test accuracy, 100% random accuracy
- **Critical Finding**: Features are architectural, not gradient-induced
- **Optimal Configuration**: LogisticRegression (C=1.0, solver='lbfgs'), StandardScaler, 80/20 split, seed=42
- **Used For**: Training protocol (reusing optimal configuration), validation protocol (random initialization test), hypothesis strategy (focus on architectural features)

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-21T06:25:58+00:00

### Workflow History for This Hypothesis

**H-M2 Timeline:**
- 2026-04-21T06:25:58: Set to IN_PROGRESS, Phase 2C (Experiment Design) started
- 2026-04-21T06:26:00: Loaded Phase 2B context (hypothesis statement, prerequisites, gate conditions)
- 2026-04-21T06:27:00: Archon KB search completed (5 knowledge sources, 3 code examples)
- 2026-04-21T06:28:00: Exa GitHub search completed (6 repositories)
- 2026-04-21T06:29:00: Serena analysis skipped (code clear, not required)
- 2026-04-21T06:30:00: Dataset/model confirmed from Phase 2A (PyTorch torchvision, LogisticRegression)
- 2026-04-21T06:31:00: Experiment specification synthesized (8 architectural features, pseudo-code, training protocol)
- 2026-04-21T06:32:00: References documented (15 sources total)
- 2026-04-21T06:33:00: Quality validation PASSED, experiment design COMPLETED

**Prerequisites Status:**
- H-M1: ✅ COMPLETED (100% test accuracy, gate PASS, mechanism REJECTED)

**Next Phase:** Phase 3 - Implementation Planning (PRD, Architecture, Logic, Config generation)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
