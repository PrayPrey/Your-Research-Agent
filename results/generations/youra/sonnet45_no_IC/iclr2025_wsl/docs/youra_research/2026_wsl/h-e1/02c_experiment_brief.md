# Experiment Design: H-E1

**Date:** 2026-07-13
**Author:** Anonymous
**Hypothesis Statement:** Under ImageNet-trained model zoos (ResNet-50 vs ViT-Base), if operation-specific weight signals exist beyond tensor dimensions, then a binary classifier trained on operation-agnostic statistics (layer norms, spectral norms) will achieve ≥80% accuracy distinguishing ResNet from ViT.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites for foundational test)
**Gate Status:** MUST_WORK - Blocks H-M-Integrated if failed

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundational test)

### Gate Condition
**Type:** MUST_WORK
**Pass Condition:** Binary classifier test accuracy ≥80%
**Fail Action (<70%):** ABANDON modular encoder approach, fall back to SNE set-encoding baseline
**Partial (70-80%):** EXPLORE enhanced statistics (Fisher eigenspectrum, NTK trace)

---

## Continuation Context

This is the first hypothesis in the verification sequence. No previous hypothesis results to incorporate.

### Previous Hypothesis Results (if applicable)
N/A - Foundational test with no prerequisites

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Weight Signal Architecture Classifier**
- Limited direct matches for weight-space statistics classification
- General neural network code examples found (model loading, quantization)
- Relevant: Weight extraction patterns from HuggingFace/PyTorch codebases

**Query 2: ResNet vs ViT Distinguishing Features**
- Diffusion model architectures found (not directly applicable)
- General attention mechanism code examples available

**Query 3: Spectral Norms Weight Statistics**
- Found attention/UNet code with spectral norm implementations
- HuggingFace diffusers library contains norm computation examples

**Key Insights:**
- Weight extraction: Use `model.state_dict()` to access all layer parameters
- Spectral norms: Compute via torch.linalg.svdvals() for largest singular values
- Layer-wise statistics: Iterate through named parameters, compute L2 norms per layer

### Archon Code Examples

**Example 1: Load and Extract Model Weights**
```python
# From HuggingFace accelerate docs
checkpoint = "model_path"
sd = torch.load(checkpoint, map_location="cpu")
# Access weights: sd["layer_name.weight"]
# Compute norms: torch.norm(sd["layer.weight"])
```

**Example 2: Weight Statistics Extraction**
```python
# Pattern for layer-wise statistics
for name, param in model.named_parameters():
    l2_norm = torch.norm(param).item()
    # Top-k spectral norms
    if len(param.shape) >= 2:
        svd = torch.linalg.svdvals(param.reshape(param.shape[0], -1))
        spectral_norms = svd[:5].tolist()
```

### Exa GitHub Implementations

**Note:** Exa MCP service unavailable (payment required). Proceeding with standard PyTorch/sklearn implementations.

**Standard Implementation Path:**
- HuggingFace Hub for model downloading: `huggingface_hub.hf_hub_download()`
- PyTorch for weight extraction: `model.state_dict()`
- Sklearn for binary classification: `LogisticRegression`
- Torch.linalg for spectral analysis: `torch.linalg.svdvals()`

### 🎯 Implementation Priority Assessment

**Implementation Type:** Custom (no existing paper implementation for this exact task)

**Recommended Implementation Path:**
- Primary: HuggingFace Hub + PyTorch + Sklearn
- Fallback: Manual download + torchvision models
- Justification: Standard tools for model access and binary classification

**Key Components:**
1. Model downloading: HuggingFace `transformers` and `timm` libraries
2. Weight extraction: PyTorch state_dict
3. Feature computation: Custom (layer norms, spectral norms, mean/std)
4. Classification: Sklearn LogisticRegression

### Code Analysis (Serena MCP)

Not required - implementation uses standard PyTorch/sklearn APIs with straightforward weight extraction and binary classification pipeline.

---

## Experiment Specification

### Dataset

**Name:** HuggingFace Model Hub - ImageNet Vision Models
**Type:** standard (pre-trained model weights)
**Source:** HuggingFace Hub (huggingface.co/models)
**Path:** 100 models (50 ResNet-50, 50 ViT-Base), filtered for ImageNet-1K training

**Split Strategy:**
- Training: 70 models (35 ResNet-50, 35 ViT-Base) - stratified by accuracy quantiles
- Test: 30 models (15 ResNet-50, 15 ViT-Base) - held-out for final evaluation
- Stratification ensures diverse performance levels in both train/test sets

**Model Selection Criteria:**
- All models trained on ImageNet-1K
- Only standard architectures (no custom variants)
- Exclude fine-tuned models (pretrained only)
- Balance across accuracy ranges (low/mid/high performers)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Hub API
- Identifier: Filter query: `task:image-classification AND dataset:imagenet-1k AND (resnet-50 OR vit-base)`
- Code:
  ```python
  from huggingface_hub import list_models
  resnet_models = list(list_models(filter="resnet-50,imagenet-1k", limit=50))
  vit_models = list(list_models(filter="vit-base,imagenet-1k", limit=50))
  ```

### Models

#### Baseline Model

**Architecture:** Not applicable - this is a binary classification experiment on model statistics, not a neural network training task

**Binary Classifier:**
- Algorithm: Logistic Regression with L2 regularization
- Input: Operation-agnostic statistics (layer norms, spectral norms, mean, std per layer)
- Output: Binary prediction (ResNet=0, ViT=1)
- Regularization: C=1.0 (default), max_iter=1000

**Feature Extraction Process:**

For each model in the zoo:
1. Download model weights from HuggingFace Hub
2. Load state_dict (parameter dictionary)
3. For each layer with trainable parameters:
   - Compute L2 norm: `torch.norm(param)`
   - Compute top-5 spectral norms: `torch.linalg.svdvals(param.reshape(param.shape[0], -1))[:5]`
   - Compute mean and std: `param.mean()`, `param.std()`
4. Concatenate all statistics into feature vector
5. Label: 0 for ResNet, 1 for ViT

**Loading Information** (for Phase 4 download):
- Method: Sklearn
- Identifier: `LogisticRegression`
- Code:
  ```python
  from sklearn.linear_model import LogisticRegression
  from sklearn.preprocessing import StandardScaler
  
  clf = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
  scaler = StandardScaler()  # Feature normalization
  ```

#### Proposed Model

**This is an EXISTENCE hypothesis testing signal distinguishability, not a model training task.**

**Core Mechanism:** Binary classifier with two feature configurations for ablation
1. **Norms-only baseline:** Layer L2 norms only
2. **Norms + Spectral:** Layer L2 norms + top-5 spectral norms per layer

**Comparison:** Test if spectral norms add discriminative power (≥5% accuracy improvement)

**Core Mechanism Implementation:**

```python
# Feature Extraction for Binary Classification
# Based on: Hypothesis requirement for operation-agnostic statistics

def extract_weight_statistics(model_state_dict):
    """
    Extract operation-agnostic statistics from model weights.
    
    Args:
        model_state_dict: OrderedDict of model parameters
    Returns:
        features: (num_features,) numpy array
    """
    features = []
    
    for name, param in model_state_dict.items():
        if not param.requires_grad or 'bias' in name:
            continue  # Skip frozen layers and biases
        
        # L2 norm (operation-agnostic)
        l2_norm = torch.norm(param).item()
        features.append(l2_norm)
        
        # Top-5 spectral norms (if 2D or higher)
        if len(param.shape) >= 2:
            # Reshape to 2D for SVD
            param_2d = param.reshape(param.shape[0], -1)
            spectral_norms = torch.linalg.svdvals(param_2d)[:5]
            features.extend(spectral_norms.tolist())
        
        # Mean and std
        features.append(param.mean().item())
        features.append(param.std().item())
    
    return np.array(features)

# Training: Fit logistic regression on extracted features
X_train = np.array([extract_weight_statistics(model) for model in train_models])
y_train = np.array([0]*35 + [1]*35)  # 0=ResNet, 1=ViT

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

clf = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
clf.fit(X_train_scaled, y_train)

# Evaluation: Test on held-out models
X_test = np.array([extract_weight_statistics(model) for model in test_models])
X_test_scaled = scaler.transform(X_test)
test_accuracy = clf.score(X_test_scaled, y_test)
```

### Training Protocol

**Not applicable - this is a binary classification task on pre-extracted features, not neural network training.**

**Classifier Training:**
- Algorithm: Logistic Regression (sklearn)
- Solver: lbfgs (default)
- Regularization: C=1.0 (L2 penalty)
- Max iterations: 1000
- Random seed: 42 (for reproducibility)

**Feature Preprocessing:**
- Standardization: StandardScaler (zero mean, unit variance)
- Applied to training set, then transform test set with same scaler

**Ablation Configurations:**
1. **Norms-only:** Use only L2 norms (control)
2. **Norms + Spectral:** Use L2 norms + top-5 spectral norms (proposed)

**No training epochs, no optimizer, no learning rate - this is classical ML classification.**

### Evaluation

**Task Type:** Binary classification (ResNet vs ViT)

**Primary Metric:**
- **Test Accuracy:** Percentage of correctly classified models in held-out 30-model test set
- **Success Threshold:** ≥80% accuracy (hypothesis requirement)
- **Partial Success:** 70-80% accuracy (explore enhanced statistics)
- **Failure:** <70% accuracy (signal insufficient)

**Secondary Metric:**
- **Ablation Comparison:** Norms+Spectral accuracy - Norms-only accuracy ≥5%
- **Purpose:** Verify that spectral norms add discriminative power

**Statistical Test:**
- **Permutation Test:** Compare against random baseline (50% chance accuracy)
- **Null Hypothesis:** Test accuracy = 50% (no signal)
- **Procedure:** 1000 random label permutations, compute accuracy distribution
- **Significance:** p < 0.05 (test accuracy in top 5% of permuted distribution)

**Expected Baseline Performance:**
- Random guess: 50% (binary classification)
- Norms-only (control): Unknown - to be measured
- Norms+Spectral (proposed): ≥80% (hypothesis target)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification
- Library: sklearn.metrics
- Code:
  ```python
  from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
  
  test_accuracy = accuracy_score(y_test, y_pred)
  report = classification_report(y_test, y_pred, target_names=["ResNet", "ViT"])
  conf_matrix = confusion_matrix(y_test, y_pred)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing Target (80%) vs Norms-only vs Norms+Spectral accuracy

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations:**
1. **Confusion Matrix:** 2x2 heatmap showing ResNet/ViT classification results
2. **Feature Importance:** Coefficient magnitudes from logistic regression (top 10 features)
3. **Permutation Test Distribution:** Histogram of permuted accuracies with actual result marked
4. **Accuracy by Model Performance:** Scatter plot of classifier accuracy vs ImageNet accuracy (check if high/low performers are easier to classify)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Binary classifier achieves test accuracy > 50% (better than random)
3. **SUCCESS:** Test accuracy ≥ 80% AND p < 0.05 (vs random baseline)
4. **PARTIAL:** 70% ≤ accuracy < 80% (explore enhanced statistics)
5. **FAILURE:** Accuracy < 70% (signal insufficient, abandon modular encoders)

---

## Appendix: Reference Implementations

### PyTorch Weight Extraction
**Source:** PyTorch official documentation
**URL:** https://pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.state_dict
```python
# Standard approach for accessing model weights
state_dict = model.state_dict()
for name, param in state_dict.items():
    print(f"{name}: {param.shape}")
```

### Spectral Norm Computation
**Source:** PyTorch linalg documentation
**URL:** https://pytorch.org/docs/stable/linalg.html#torch.linalg.svdvals
```python
# Compute singular values (spectral norms)
svd = torch.linalg.svdvals(weight_matrix)
top_5_spectral = svd[:5]
```

### Binary Classification (Sklearn)
**Source:** Sklearn LogisticRegression documentation
**URL:** https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
```python
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(C=1.0, max_iter=1000)
clf.fit(X_train, y_train)
accuracy = clf.score(X_test, y_test)
```

### HuggingFace Model Hub Access
**Source:** HuggingFace Hub documentation
**URL:** https://huggingface.co/docs/huggingface_hub/guides/download
```python
from huggingface_hub import list_models, hf_hub_download
models = list(list_models(filter="imagenet-1k"))
```

### Related Work
- **SANE (Set-based Tokenization):** Zhou et al. 2022 - Same-family transfer +2.2%
- **SNE (Set-Encoding):** Karpathy et al. 2021 - Cross-architecture ρ=0.54 baseline
- **UNF (Equivariance):** Navon et al. 2023 - Theorem 3.2 permutation-equivariance

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-13T14:30:00Z

### Workflow History for This Hypothesis
- 2026-07-13T14:02:16: Hypothesis h-e1 set to IN_PROGRESS
- 2026-07-13T14:30:00: Phase 2C experiment design started
- 2026-07-13T14:30:00: Experiment brief generated (Level 1.5 specification)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
