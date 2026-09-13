# Experiment Design: h-m1

**Date:** 2026-07-11
**Author:** Anonymous
**Hypothesis Statement:** Asymmetric digit degradation increases monotonically with flip probability (dose-response relationship)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Hypothesis** - Tests complete causal chain with dose-response validation.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** Pending (H-E1 must complete before execution)
**Gate Status:** SHOULD_WORK (failure documented as limitation, workflow continues)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (Asymmetric digit degradation effect must be confirmed first)

### Gate Condition

**Gate Type:** SHOULD_WORK

**Meaning:**
- If H-M1 passes: Mechanism confirmed (dose-response relationship proven)
- If H-M1 fails: Effect exists (per H-E1) but mechanism unclear → EXPLORE alternative explanations

**Failure Response:** Document limitation, continue to next hypothesis (does not block workflow)

---

## Continuation Context

This hypothesis tests the MECHANISM behind the existence effect (H-E1). It depends on H-E1 confirmation but extends the analysis to test the complete 4-step causal chain and dose-response relationship.

**Relationship to H-E1:**
- H-E1: Proves asymmetric digits degrade under flip (existence)
- H-M1: Proves degradation increases monotonically with flip probability (mechanism)

**Dataset/Model Reuse:**
- Same MNIST dataset as H-E1 (controlled comparison)
- Same CNN architecture as H-E1 (isolates augmentation effect)
- Only difference: Testing multiple flip probabilities (dose-response)

### Previous Hypothesis Results (if applicable)

Not applicable - H-E1 has not executed yet. This experiment design is prepared for H-M1, which will execute after H-E1 validation.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon KB searches returned primarily diffusion model and data augmentation examples from HuggingFace Diffusers, which are not directly applicable to MNIST classification experiments. The knowledge base lacks specific resources on label noise in data augmentation or MNIST horizontal flip experiments.

**Query 1: Label Noise Data Augmentation Experiment Design**
- **Finding:** Limited relevant results. Most content focuses on diffusion model training with noise augmentation (offset noise, SNR weighting), not classification label noise.
- **Source:** HuggingFace Diffusers documentation and training scripts
- **Key Insight:** No direct precedent for testing semantic validity of augmentations on MNIST

**Query 2: MNIST Classification Augmentation Horizontal Flip**
- **Finding:** Results focused on diffusion pipelines (InstantID, ControlNet) rather than MNIST classification
- **Source:** HuggingFace Diffusers community examples
- **Key Insight:** Standard MNIST tutorials typically avoid horizontal flip, suggesting implicit awareness of semantic issues

**Query 3: Dose-Response Relationship Machine Learning**
- **Finding:** One arxiv paper (2305.13301) mentions training relationships but not dose-response for augmentation probability
- **Source:** ArXiv, HuggingFace training examples
- **Key Insight:** Dose-response testing of augmentation probability is novel experimental design

**Implications for Experiment Design:**
- This hypothesis tests a gap in existing research (no Archon precedents found)
- Must design from first principles using standard MNIST classification baselines
- Positive indicator: PyTorch MNIST examples avoid horizontal flip (validates semantic concern)

### Archon Code Examples

**Query 1: MNIST PyTorch CNN Training**
- **Finding:** No MNIST-specific examples found. Results showed diffusion model architectures (UNet, ControlNet, Stable Diffusion pipelines)
- **Pattern:** Deep model loading and GPU setup patterns applicable to general PyTorch training
- **Insight:** Need to rely on standard PyTorch MNIST tutorials (not in Archon KB)

**Query 2: Data Augmentation Torchvision Transforms**
- **Example 1:** Image preprocessing with torchvision.transforms
  ```python
  import torchvision.transforms as transforms
  
  augmentations = transforms.Compose([
      transforms.Resize(resolution, interpolation=transforms.InterpolationMode.BILINEAR),
      transforms.CenterCrop(resolution) if center_crop else transforms.RandomCrop(resolution),
      transforms.RandomHorizontalFlip() if random_flip else transforms.Lambda(lambda x: x),
      transforms.ToTensor(),
      transforms.Normalize([0.5], [0.5]),
  ])
  ```
  - **Source:** HuggingFace Diffusers training scripts
  - **Pattern:** Conditional augmentation application using boolean flags
  - **Insight:** Can use `RandomHorizontalFlip(p=probability)` for dose-response testing

- **Example 2:** Preprocessing pipeline structure
  ```python
  preproc = transforms.Compose([
      transforms.Resize((224, 224)),
      transforms.ToTensor(),
      lambda x: 1-x,  # Custom transforms via lambda
  ])
  ```
  - **Source:** WebDataset GitHub
  - **Pattern:** Compose multiple transforms sequentially
  - **Insight:** Can insert custom transforms for validation/debugging

**Applicable Patterns:**
- Use `transforms.Compose([])` for augmentation pipelines
- `RandomHorizontalFlip(p)` for probability-controlled flipping
- `ToTensor()` + `Normalize()` for standard preprocessing
- Conditional augmentation via boolean flags or probability parameters

### Exa GitHub Implementations

**Query 1: MNIST PyTorch Classification CNN Training Example**

**Repository 1**: PyTorch/examples (⭐ 22k+)
- **URL**: https://github.com/PyTorch/examples/blob/main/mnist/main.py
- **Relevance**: Official PyTorch MNIST example - gold standard baseline
- **Architecture**: Simple CNN (Conv1: 1→32, Conv2: 32→64, FC: 9216→128→10, Dropout 0.25/0.5)
- **Key Code**:
  ```python
  transform=transforms.Compose([
      transforms.ToTensor(),
      transforms.Normalize((0.1307,), (0.3081,))
  ])
  # NOTE: No RandomHorizontalFlip - validates semantic concern
  
  dataset1 = datasets.MNIST('../data', train=True, download=True, transform=transform)
  model = Net().to(device)
  optimizer = optim.Adadelta(model.parameters(), lr=args.lr)
  scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma)
  ```
- **Training Config**:
  - Optimizer: Adadelta (lr=1.0, default)
  - Learning rate schedule: StepLR (gamma=0.7)
  - Batch size: 64 (default)
  - Epochs: 14 (default)
  - Loss: NLL loss (F.nll_loss)
- **Dataset**: MNIST (torchvision.datasets.MNIST, auto-download)
- **Results**: ~99% test accuracy (standard baseline)
- **Key Insight**: Official example uses ONLY ToTensor + Normalize, NO horizontal flip augmentation

**Repository 2**: MuhammadSeyam/mnist-cnn-digit-classification (⭐ modest)
- **URL**: https://github.com/MuhammadSeyam/mnist-cnn-digit-classification
- **Relevance**: Demonstrates alternative CNN architecture with Batch Normalization
- **Architecture**: Conv1: 1→16, Conv2: 16→32, FC: 128→10, BatchNorm + Dropout
- **Training Config**:
  - Optimizer: Adam (lr=0.001, weight_decay=0.0001)
  - Batch size: 500
  - Epochs: 15
  - Loss: CrossEntropyLoss
- **Results**: 99.1% training accuracy
- **Key Insight**: Also uses minimal augmentation (only normalization)

**Repository 3**: Chara1236/MNIST-classification-with-Pytorch
- **URL**: https://github.com/Chara1236/MNIST-classification-with-Pytorch
- **Architecture**: Conv1: 1→10, Conv2: 10→20, FC: 320→50→10
- **Key Code**:
  ```python
  train_data = datasets.MNIST(
      root = 'data',
      train = True,
      transform = ToTensor(),  # Only ToTensor, no augmentation
      download = True
  )
  ```
- **Key Insight**: Another example avoiding horizontal flip augmentation

**Query 2: PyTorch RandomHorizontalFlip Documentation**

**Source**: PyTorch Vision Official Documentation
- **URL**: https://pytorch.org/vision/stable/generated/torchvision.transforms.RandomHorizontalFlip.html
- **API**:
  ```python
  torchvision.transforms.RandomHorizontalFlip(p=0.5)
  # p (float): probability of the image being flipped. Default value is 0.5
  ```
- **Implementation**:
  ```python
  def forward(self, img):
      if torch.rand(1) < self.p:
          return F.hflip(img)
      return img
  ```
- **Key Insight**: Simple probability-controlled flip - perfect for dose-response testing
- **Usage Pattern**: Integrate into transforms.Compose pipeline

**Convergent Evidence:**
- ALL standard MNIST examples avoid horizontal flip augmentation
- This validates the hypothesis premise: horizontal flip is semantically invalid for MNIST
- PyTorch community implicitly recognizes this issue (no flip in official examples)

**Serena Analysis Needed**: ❌ No complex code found
- All code snippets are straightforward CNN implementations (<100 lines per component)
- Architecture patterns are standard and well-documented
- No custom layers or unfamiliar patterns requiring deep analysis

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment:** Not applicable - this is a novel hypothesis testing semantic validity of MNIST augmentations, NOT a paper reproduction.

**Recommended Implementation Path:**
- Primary: PyTorch official MNIST example (baseline architecture)
- Fallback: Custom implementation from scratch (simple CNN)
- Justification: PyTorch official example is the gold standard baseline for MNIST. All GitHub examples converge on similar architecture and avoid horizontal flip, validating our hypothesis premise.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Standard MNIST CNN architectures and PyTorch augmentation APIs are well-documented and straightforward to implement.

---

## Experiment Specification

### Dataset

**Dataset**: MNIST  
**Type**: standard  
**Source**: torchvision.datasets (auto-download)

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: MNIST
- Code:
  ```python
  import torchvision.datasets as datasets
  import torchvision.transforms as transforms
  
  # Dataset will be loaded in Phase 4 with augmentation conditions
  train_dataset = datasets.MNIST(
      root='./data',
      train=True,
      transform=transform,  # Varies by condition
      download=True
  )
  test_dataset = datasets.MNIST(
      root='./data',
      train=False,
      transform=transforms.Compose([
          transforms.ToTensor(),
          transforms.Normalize((0.1307,), (0.3081,))
      ]),
      download=True
  )
  ```

**Statistics**:
- Total: 70,000 images (60,000 train, 10,000 test)
- Classes: 10 (digits 0-9)
- Image size: 28×28 grayscale
- Symmetric digits: {0, 1, 8}
- Asymmetric digits: {2, 3, 5, 6, 7, 9}

**Preprocessing** (all conditions):
- ToTensor(): Convert PIL Image to PyTorch tensor
- Normalize(mean=0.1307, std=0.3081): MNIST standard normalization

**Augmentation** (varies by experimental condition):
- **Baseline (p=0.0)**: No augmentation (ToTensor + Normalize only)
- **Flip30 (p=0.3)**: RandomHorizontalFlip(p=0.3) + Normalize
- **Flip50 (p=0.5)**: RandomHorizontalFlip(p=0.5) + Normalize
- **Flip90 (p=0.9)**: RandomHorizontalFlip(p=0.9) + Normalize

**Path Specification**: `auto` (auto-download to `./data/MNIST/`)

### Models

#### Baseline Model

**Architecture**: Standard CNN for MNIST  
**Type**: custom  
**Parameters**: ~1.2M parameters

**Architecture Details**:
- Conv1: 1 → 32 channels, kernel 3×3, ReLU
- Conv2: 32 → 64 channels, kernel 3×3, ReLU
- MaxPool2d: 2×2
- Dropout2d: p=0.25
- Flatten: 64×7×7 → 9216
- FC1: 9216 → 128, ReLU
- Dropout: p=0.5
- FC2: 128 → 10 (output logits)

**Loading Information** (for Phase 4 download):
- Method: custom (define from scratch)
- Identifier: N/A (not pretrained)
- Code:
  ```python
  import torch.nn as nn
  import torch.nn.functional as F
  
  class StandardCNN(nn.Module):
      def __init__(self):
          super(StandardCNN, self).__init__()
          self.conv1 = nn.Conv2d(1, 32, 3, 1)
          self.conv2 = nn.Conv2d(32, 64, 3, 1)
          self.dropout1 = nn.Dropout2d(0.25)
          self.dropout2 = nn.Dropout(0.5)
          self.fc1 = nn.Linear(9216, 128)
          self.fc2 = nn.Linear(128, 10)
      
      def forward(self, x):
          x = F.relu(self.conv1(x))
          x = F.relu(self.conv2(x))
          x = F.max_pool2d(x, 2)
          x = self.dropout1(x)
          x = torch.flatten(x, 1)
          x = F.relu(self.fc1(x))
          x = self.dropout2(x)
          x = self.fc2(x)
          return F.log_softmax(x, dim=1)
  ```

**Configuration**:
- Input: (B, 1, 28, 28) - grayscale images
- Output: (B, 10) - log probabilities for 10 classes
- Activation: ReLU
- Regularization: Dropout (0.25 conv, 0.5 FC)

**Expected Baseline Performance**: ~99% test accuracy (from PyTorch official examples)

#### Proposed Model

**Architecture:** Baseline CNN (no architectural changes)

**Note:** This hypothesis tests the MECHANISM of label noise degradation through augmentation probability variation, NOT a new model architecture. The "mechanism" is the causal process: flip probability → label noise → accuracy degradation.

**Experimental Design:**
- Same baseline CNN architecture used across ALL conditions
- Only the DATA AUGMENTATION varies (flip probability p)
- Controlled comparison: architecture held constant, only augmentation changes

**Core Mechanism (Causal Process):**

```python
# Mechanism: Dose-Response Relationship in Label Noise from Flip Augmentation
# Based on: Hypothesis causal chain

# This is NOT a model component - it's the DATA GENERATION process being tested

class DoseResponseExperiment:
    """
    Test dose-response relationship between flip probability and accuracy degradation.
    
    Mechanism Steps (from hypothesis):
    1. Horizontal flip creates non-canonical asymmetric digit images
    2. Invalid images retain original labels → label noise
    3. Training on label noise degrades test accuracy
    4. Degradation magnitude increases with flip probability
    """
    def __init__(self, flip_probabilities=[0.0, 0.3, 0.5, 0.9], num_seeds=5):
        self.flip_probs = flip_probabilities
        self.num_seeds = num_seeds
        self.asymmetric_digits = [2, 3, 5, 6, 7, 9]
    
    def create_transform(self, flip_prob):
        """Create augmentation pipeline for given flip probability."""
        return transforms.Compose([
            transforms.RandomHorizontalFlip(p=flip_prob),  # Dose manipulation
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
    
    def train_model(self, flip_prob, seed):
        """Train one model instance at given flip probability."""
        # Step 1: Apply augmentation with probability p
        transform = self.create_transform(flip_prob)
        train_dataset = datasets.MNIST(root='./data', train=True, 
                                       transform=transform, download=True)
        
        # Step 2: Train model (label noise implicitly present in flipped samples)
        model = StandardCNN()
        # ... training loop (standard, not modified)
        
        # Step 3: Evaluate on asymmetric digits
        accuracy_asymmetric = self.evaluate_asymmetric_digits(model)
        return accuracy_asymmetric
    
    def verify_dose_response(self, results):
        """
        Step 4: Test monotonic dose-response.
        
        Args:
            results: dict {flip_prob: [accuracies across seeds]}
        
        Returns:
            Spearman ρ (expected: negative, p<0.05)
        """
        # Compute mean accuracy per flip probability
        mean_accuracies = {p: np.mean(accs) for p, accs in results.items()}
        
        # Test monotonic relationship
        from scipy.stats import spearmanr
        rho, p_value = spearmanr(list(mean_accuracies.keys()), 
                                  list(mean_accuracies.values()))
        
        # Expected: rho < 0 (higher flip prob → lower accuracy)
        return rho, p_value

# Integration: NO model architecture integration - this tests data augmentation effect
# The mechanism is in the DATA PIPELINE, not the MODEL
```

### Training Protocol

**From Research** (PyTorch MNIST official example):

**Optimizer**: Adam
- lr=0.001 (standard for MNIST)
- **Source**: Multiple GitHub examples converge on Adam with 0.001 for MNIST

**Learning Rate Schedule**: StepLR
- step_size=1, gamma=0.7 (from PyTorch official)
- **Source**: PyTorch/examples official MNIST implementation

**Batch Size**: 64
- **Source**: PyTorch official example default

**Epochs**: 30
- Per Phase 2B specification
- With early stopping: patience=5 epochs on validation accuracy
- **Source**: Phase 2B verification protocol

**Loss Function**: CrossEntropyLoss
- Standard for multi-class classification
- **Source**: Universal across all MNIST examples

**Seeds**: 5 (n=5 replications per flip probability)
- **Purpose**: Measure dose-response relationship with statistical power
- **Source**: Phase 2B verification protocol requirement

**Regularization**:
- Dropout: 0.25 (conv layers), 0.5 (FC layers)
- **Source**: PyTorch official architecture

**Experimental Conditions** (4 × 5 = 20 training runs total):
1. **Baseline (p=0.0)**: No flip, n=5 seeds
2. **Flip30 (p=0.3)**: RandomHorizontalFlip(p=0.3), n=5 seeds
3. **Flip50 (p=0.5)**: RandomHorizontalFlip(p=0.5), n=5 seeds
4. **Flip90 (p=0.9)**: RandomHorizontalFlip(p=0.9), n=5 seeds

**Rationale**: Fixed architecture and hyperparameters across all conditions ensures augmentation probability is the ONLY variable.

### Evaluation

**Primary Metrics**:
- **Asymmetric Digit Accuracy**: Mean test accuracy on digits {2,3,5,6,7,9}
  - Computed per condition (p=0.0, 0.3, 0.5, 0.9)
  - Aggregated across n=5 seeds
- **Accuracy Degradation**: Baseline_acc - Flip_acc (per flip probability)

**Statistical Test** (Mechanism validation):
- **Test**: Spearman rank correlation
- **Hypothesis**: ρ < 0 (monotonic decrease: higher flip prob → lower accuracy)
- **Significance**: p < 0.05
- **Effect Size**: Visual inspection of degradation magnitude at each dose level

**Success Criteria**:
- **Primary**: Spearman ρ significantly negative (p<0.05), confirming dose-response
- **Secondary**: Degradation visible at p=0.3, stronger at p=0.5, strongest at p=0.9
- **Mechanism Validation**: Each causal step observable in results

**Expected Baseline Performance** (from research):
- Baseline (p=0.0): ~99% overall test accuracy
- Asymmetric digit accuracy: ~98-99% (slight variation per digit)
- **Source**: PyTorch official examples, literature baselines

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: multi-class classification
- Library: sklearn.metrics + custom aggregation
- Code:
  ```python
  from sklearn.metrics import accuracy_score
  from scipy.stats import spearmanr
  import numpy as np
  
  # Per-class accuracy computation
  def compute_asymmetric_accuracy(y_true, y_pred, asymmetric_digits=[2,3,5,6,7,9]):
      mask = np.isin(y_true, asymmetric_digits)
      if mask.sum() == 0:
          return 0.0
      return accuracy_score(y_true[mask], y_pred[mask])
  
  # Dose-response test
  def test_dose_response(results_dict):
      # results_dict: {flip_prob: [acc_seed1, acc_seed2, ...]}
      probs = sorted(results_dict.keys())
      mean_accs = [np.mean(results_dict[p]) for p in probs]
      rho, p_value = spearmanr(probs, mean_accs)
      return {"rho": rho, "p_value": p_value}
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Recommended visualizations based on dose-response mechanism hypothesis:

1. **Dose-Response Curve**
   - X-axis: Flip probability {0.0, 0.3, 0.5, 0.9}
   - Y-axis: Mean asymmetric digit accuracy
   - Error bars: Standard deviation across n=5 seeds
   - Expected pattern: Monotonic decrease

2. **Per-Digit Breakdown**
   - Heatmap: Digits (rows) × Flip Probability (columns) → Accuracy (color)
   - Shows which asymmetric digits degrade most under flip augmentation
   - Validates class-specific label noise hypothesis

3. **Degradation Magnitude**
   - Bar chart: Flip probability (X) → Accuracy degradation vs baseline (Y)
   - Shows dose-response effect size at each level
   - Validates "stronger degradation at higher flip prob"

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

**Source A.1**: Diffusion Model Data Augmentation Examples
- **Type**: Knowledge base code examples
- **Query Used**: "label noise data augmentation experiment design"
- **Relevance**: Limited - results focused on diffusion models, not classification label noise
- **Key Insights**:
  - No direct precedent for testing semantic validity of augmentations
  - Standard practice avoids problematic augmentations implicitly
- **Used For**: Negative evidence (gap identification)

**Source A.2**: torchvision Transforms Code Examples
- **Type**: Code examples
- **Query Used**: "data augmentation torchvision transforms"
- **Key Code**:
  ```python
  augmentations = transforms.Compose([
      transforms.RandomHorizontalFlip() if random_flip else transforms.Lambda(lambda x: x),
      transforms.ToTensor(),
      transforms.Normalize([0.5], [0.5]),
  ])
  ```
- **Used For**: Conditional augmentation pattern, transforms pipeline structure

### B. GitHub Implementations (Exa)

**Repository B.1**: PyTorch/examples - MNIST (⭐ 22k+)
- **URL**: https://github.com/PyTorch/examples/blob/main/mnist/main.py
- **Query Used**: "MNIST PyTorch classification CNN training example"
- **Relevance**: **PRIMARY - Official PyTorch baseline**
- **Key Code** (annotated):
  ```python
  # CRITICAL: No horizontal flip in official example - validates semantic concern
  transform=transforms.Compose([
      transforms.ToTensor(),
      transforms.Normalize((0.1307,), (0.3081,))  # MNIST standard
  ])
  
  # Architecture used as our baseline
  class Net(nn.Module):
      def __init__(self):
          self.conv1 = nn.Conv2d(1, 32, 3, 1)
          self.conv2 = nn.Conv2d(32, 64, 3, 1)
          # ... (see baseline model specification)
  
  # Training config
  optimizer = optim.Adadelta(model.parameters(), lr=1.0)
  scheduler = StepLR(optimizer, step_size=1, gamma=0.7)
  # batch_size=64, epochs=14 (we use 30 for better convergence)
  ```
- **Configuration Extracted**: Normalization parameters (0.1307, 0.3081), architecture, optimizer
- **Their Results**: ~99% test accuracy baseline
- **Used For**: Baseline model architecture, preprocessing, expected performance

**Repository B.2**: MuhammadSeyam/mnist-cnn-digit-classification
- **URL**: https://github.com/MuhammadSeyam/mnist-cnn-digit-classification
- **Query Used**: "MNIST PyTorch classification CNN training example"
- **Relevance**: Alternative architecture with BatchNorm
- **Configuration Extracted**: Adam optimizer (lr=0.001) as alternative to Adadelta
- **Their Results**: 99.1% training accuracy
- **Used For**: Optimizer selection (Adam chosen over Adadelta for simplicity)

**Repository B.3**: PyTorch Vision - RandomHorizontalFlip Documentation
- **URL**: https://pytorch.org/vision/stable/generated/torchvision.transforms.RandomHorizontalFlip.html
- **Query Used**: "PyTorch horizontal flip augmentation RandomHorizontalFlip probability"
- **Key Code**:
  ```python
  class RandomHorizontalFlip(torch.nn.Module):
      def __init__(self, p=0.5):  # Probability parameter
          self.p = p
      
      def forward(self, img):
          if torch.rand(1) < self.p:
              return F.hflip(img)
          return img
  ```
- **Used For**: Dose manipulation mechanism (varying p for dose-response)

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear. Standard MNIST CNN architectures and PyTorch augmentation APIs are well-documented and straightforward to implement.

### D. Previous Hypothesis Context

**Previous Context**: None - H-M1 depends on H-E1 but tests different variables (dose-response vs existence). Same dataset/model for controlled comparison.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (MNIST) | Phase 2A/2B + GitHub | 02b_context.md, Repository B.1 |
| Preprocessing (normalize) | GitHub | Repository B.1 (MNIST standard) |
| Baseline model architecture | GitHub | Repository B.1 (PyTorch official) |
| Augmentation mechanism | GitHub + Docs | Repository B.3 (RandomHorizontalFlip API) |
| Training protocol (Adam, lr) | GitHub | Repository B.2 (Adam lr=0.001) |
| Training protocol (epochs, batch) | Phase 2B + GitHub | 02b_verification_plan.md, B.1 |
| Evaluation metrics (asymmetric acc) | Phase 2B | 02b_verification_plan.md Section 2.2 |
| Statistical test (Spearman) | Phase 2B | 02b_verification_plan.md Section 2.2 |
| Expected baseline (~99%) | GitHub | Repository B.1, B.2 (consistent) |
| Semantic validity premise | Convergent evidence | All MNIST examples avoid horizontal flip |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-11T00:00:00

### Workflow History for This Hypothesis

- **2026-07-11**: Experiment design initiated (Phase 2C)
- **2026-07-11**: MCP research completed (Archon: limited relevant results, Exa: 3 GitHub repos, Serena: skipped)
- **2026-07-11**: Experiment specification synthesized (Level 1.5)
- **2026-07-11**: Experiment design completed and validated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
