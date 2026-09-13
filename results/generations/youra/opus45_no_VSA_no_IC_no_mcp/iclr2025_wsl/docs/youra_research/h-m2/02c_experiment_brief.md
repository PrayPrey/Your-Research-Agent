# Experiment Design: h-m2

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Locality bias reduces sample complexity for local patterns: DWS should match or exceed NFT on backdoor detection with same training data.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates sample efficiency claim for locality bias.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m1 VALIDATED)
**Gate Status:** SHOULD_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1

### Gate Condition
SHOULD_WORK - If fails, EXPLORE whether effect appears at different data scales

---

## Continuation Context

Building on h-m1 validation which confirmed:
- DWS locality score: CoV 1.44 > NFT CoV 1.35
- Architecture-specific inductive biases measurable
- Training dynamics differ between architectures

### Previous Hypothesis Results (if applicable)
h-m1 PASS: Architecture encodes different inductive biases. DWS shows more localized weight update patterns than NFT during training.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Sample Complexity + Locality Bias**
- DWS locality inductive bias should reduce sample complexity for detecting localized patterns
- Analogous to CNN vs ViT: CNN needs less data for spatial patterns due to locality bias
- Sample efficiency curves (AUC vs training size) are standard evaluation protocol

**Query 2: Backdoor Detection Implementation**
- Backdoors typically manifest as localized weight perturbations in specific layers
- Detection often focuses on later convolutional/FC layers
- Binary classification (backdoored vs clean) with AUC metric
- Data splits: 25%, 50%, 100% training to show sample efficiency

**Query 3: Weight-Space Learning Benchmarks**
- TrojAI Round 10+: Image classification CNNs (1000+ models)
- Standard baseline: MLP on flattened weights (~0.70 AUC)
- Equivariant methods (DWS, NFT): 0.80-0.90 AUC range

### Archon Code Examples

**Pattern 1: Sample Efficiency Evaluation**
```python
# Standard sample efficiency evaluation
for frac in [0.25, 0.50, 1.0]:
    train_subset = sample(train_data, frac)
    model.train(train_subset)
    auc = evaluate(model, test_data)
    results[frac] = auc
```

**Pattern 2: AUC Computation**
```python
from sklearn.metrics import roc_auc_score
auc = roc_auc_score(y_true, y_pred_proba)
```

### Exa GitHub Implementations

**Repository 1**: AvivNavon/DWS (Official DWS)
- **URL**: https://github.com/AvivNavon/DWS
- **Relevance**: Official DWS implementation from paper authors
- **Architecture**: Equivariant weight-space layers
- **Key Code**:
  ```python
  # DWS Training with sample efficiency evaluation
  class DWSClassifier(nn.Module):
      def __init__(self, in_features, hidden_dims, out_features):
          self.layers = nn.ModuleList([
              EquivariantLinear(in_features, hidden_dims[0])
          ])
  ```
- **Training Config**:
  - Optimizer: AdamW (lr=1e-4, weight_decay=0.01)
  - Learning rate: Cosine decay
  - Batch size: 32
  - Epochs: 100
- **Dataset**: TrojAI, ModelZoo benchmarks
- **Results**: Superior to MLP baseline on backdoor detection

**Repository 2**: TrojAI Benchmark (NIST Official)
- **URL**: https://pages.nist.gov/trojai/
- **Relevance**: Official TrojAI benchmark with labeled backdoor models
- **Architecture**: CNN image classifiers (backdoored and clean)
- **Dataset Statistics**:
  - Round 10+: 1000+ models per round
  - Labels: Binary (backdoor/clean)
  - Model architectures: ResNet, DenseNet, VGG variants
- **Standard Evaluation**: ROC-AUC on held-out test set

**Serena Analysis Needed**: false (architectures understood from h-m1)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Both DWS and NFT have official implementations already validated in h-m1.

**Recommended Implementation Path:**
- Primary: Extend h-m1 validated code (DWS and NFT already working)
- Fallback: Official AvivNavon/DWS repository
- Justification: h-m1 code proven to produce measurable inductive bias differences

### Code Analysis (Serena MCP)

*Skipped* - Code from h-m1 implementation was sufficiently clear. Both DWS equivariant layers and NFT transformer encoder already validated in previous hypothesis.

---

## Experiment Specification

### Dataset

**Dataset**: TrojAI Benchmark (NIST)
**Type**: standard
**Source**: https://trojai.nist.gov/

**Statistics**:
- Training: 1000+ neural network models (backdoored and clean)
- Validation: 200 models
- Test: 500 models (held out for all evaluations)
- Each model: CNN weights for image classification tasks
- Labels: Binary (backdoor/clean)

**Sample Efficiency Splits**:
- 25% training: ~250 models
- 50% training: ~500 models
- 100% training: ~1000 models

**Preprocessing**:
- Extract weight tensors from each layer
- Flatten/tokenize for NFT, structured tensors for DWS
- Normalize weight values per-layer

**Loading Information** (for Phase 4 download):
- Method: custom (TrojAI API download)
- Identifier: TrojAI Round 10 (image classification CNNs)
- Code: 
  ```python
  # Download TrojAI models via official API
  from trojai_api import download_round
  models = download_round(round_number=10)
  # Split: train/val/test
  train, val, test = split_models(models, [0.7, 0.15, 0.15])
  ```

### Models

#### Baseline Model

**Architecture**: MLP on Flattened Weights
**Type**: simple baseline

**Configuration**:
- Input: Flattened weight vector (concatenated all layers)
- Hidden: [512, 256, 128]
- Output: Binary (backdoor/clean)
- Activation: ReLU + BatchNorm

**Loading Information** (for Phase 4 download):
- Method: custom (defined in code, reuse from h-m1)
- Identifier: MLP-Baseline
- Code:
  ```python
  class MLPBaseline(nn.Module):
      def __init__(self, input_dim):
          super().__init__()
          self.fc = nn.Sequential(
              nn.Linear(input_dim, 512), nn.ReLU(), nn.BatchNorm1d(512),
              nn.Linear(512, 256), nn.ReLU(), nn.BatchNorm1d(256),
              nn.Linear(256, 128), nn.ReLU(),
              nn.Linear(128, 1), nn.Sigmoid()
          )
  ```

#### Proposed Models

**DWS (Deep Weight Space)**:
- Architecture: Equivariant layers on structured weight tensors
- Preserves layer-wise locality during processing
- Source: Navon et al. 2023, reuse from h-m1

**NFT (Neural Functional Transformer)**:
- Architecture: Transformer encoder on flattened weight tokens
- Full attention across all tokens (global receptive field)
- Source: Zhou et al. 2024, reuse from h-m1

**Core Mechanism Implementation:**

```python
# Core Mechanism: Sample Efficiency Evaluation for h-m2
# Tests: Locality bias reduces sample complexity for backdoor detection
# Based on: DWS/NFT implementations from h-m1, standard sample efficiency protocol

class SampleEfficiencyExperiment:
    """
    Compare DWS vs NFT backdoor detection AUC across training data sizes.
    Hypothesis: DWS achieves higher AUC with less data due to locality bias.
    """
    def __init__(self, train_data, test_data):
        self.models = {
            'dws': DWSClassifier(),
            'nft': NFTClassifier(),
            'mlp': MLPBaseline()
        }
        self.fractions = [0.25, 0.50, 1.0]
        self.train_data = train_data
        self.test_data = test_data
    
    def run_experiment(self, seeds=[42, 123, 456]):
        results = defaultdict(lambda: defaultdict(list))
        for frac in self.fractions:
            subset = self.sample_train_data(frac)
            for name, model in self.models.items():
                for seed in seeds:
                    set_seed(seed)
                    model.reset_parameters()
                    model.train_on(subset, epochs=100, lr=1e-4)
                    probs = model.predict_proba(self.test_data.weights)
                    auc = roc_auc_score(self.test_data.labels, probs)
                    results[frac][name].append(auc)
        return self.compute_statistics(results)
    
    def sample_train_data(self, fraction):
        n = int(len(self.train_data) * fraction)
        return random.sample(self.train_data, n)
```

### Training Protocol

**From Previous Hypothesis (h-m1)**:
- **Optimizer**: AdamW - Parameters: lr=1e-4, weight_decay=1e-2
- **Learning Rate**: 1e-4 with cosine decay
- **Batch Size**: 32
- **Epochs**: 100
- **Loss**: BCEWithLogitsLoss (backdoor detection)

**Sample Efficiency Protocol (h-m2 specific)**:
- Train each model on 25%, 50%, 100% of training data
- Use same held-out test set for all evaluations
- Repeat with 3 seeds for statistical reliability

**Seeds**: 3 (42, 123, 456)

### Evaluation

**Primary Metrics**:
- ROC-AUC: Backdoor detection performance (primary)
- Learning curve slope: AUC improvement per data fraction

**Success Criteria (MECHANISM hypothesis)**:
1. DWS AUC > NFT AUC on backdoor detection at 25% data (locality advantage)
2. Gap between DWS and NFT narrows with more data (NFT catches up)
3. Both equivariant methods outperform MLP baseline at all fractions

**Expected Baseline Performance** (from research):
- MLP baseline: ~0.70 AUC on TrojAI backdoor detection
- DWS at 100% data: 0.80-0.85 AUC (estimated from prior work)
- NFT at 100% data: 0.80-0.85 AUC (estimated, comparable to DWS at full data)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (backdoor detection)
- Library: sklearn.metrics
- Code:
  ```python
  from sklearn.metrics import roc_auc_score
  auc = roc_auc_score(y_true, y_pred_proba)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Sample efficiency curves (AUC vs training fraction) for DWS/NFT/MLP

#### Additional Figures (LLM Autonomous)
- **Learning Curve Plot**: AUC (y-axis) vs Data Fraction (x-axis) with error bars for all architectures
- **25% Data Bar Chart**: AUC comparison at lowest data regime
- **Gap Closure Plot**: DWS-NFT AUC difference vs data fraction (should decrease)
- **Box Plots**: AUC distribution at each fraction across seeds

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. DWS AUC > NFT AUC at 25% training data
3. DWS-NFT gap reduces at higher data fractions (learning curve convergence)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: Sample Complexity and Inductive Bias
- **Type**: Knowledge base article
- **Query Used**: "sample complexity locality bias backdoor detection"
- **Key Insights**:
  - DWS locality bias should reduce sample complexity for detecting localized patterns
  - Analogous to CNN vs ViT: locality helps with less data
- **Used For**: Hypothesis rationale, experiment design

**Source 2**: TrojAI Benchmark Setup
- **Type**: Best practices
- **Query Used**: "TrojAI benchmark backdoor detection implementation"
- **Key Insights**:
  - Standard evaluation: ROC-AUC on held-out test
  - Binary classification (backdoor/clean)
- **Used For**: Dataset specification, evaluation metrics

**Source 3**: Weight-Space Learning Benchmarks
- **Type**: Benchmark results
- **Query Used**: "backdoor detection benchmark weight-space"
- **Key Insights**:
  - MLP baseline ~0.70 AUC
  - Equivariant methods achieve 0.80-0.90 AUC
- **Used For**: Expected baseline performance

### B. GitHub Implementations (Exa)

**Repository 1**: AvivNavon/DWS
- **URL**: https://github.com/AvivNavon/DWS
- **Query Used**: "Navon DWS deep weight space official implementation"
- **Relevance**: Official author implementation
- **Key Code**:
  ```python
  # DWS equivariant layer structure
  class EquivariantMLP(nn.Module):
      # Maintains weight locality through structured operations
  ```
- **Configuration Extracted**: AdamW optimizer, lr=1e-4, cosine decay
- **Used For**: DWS implementation, training protocol

**Repository 2**: TrojAI Benchmark (NIST)
- **URL**: https://pages.nist.gov/trojai/
- **Query Used**: "TrojAI benchmark dataset models"
- **Relevance**: Official backdoor detection benchmark
- **Used For**: Dataset specification, model architectures

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from h-m1 implementation sufficiently clear.

### D. Previous Hypothesis Context

**Source**: h-m1 Validation Results
- **Status**: VALIDATED (PASS)
- **Reused Components**:
  - DWS/NFT implementations (both working)
  - TrojAI dataset loading pipeline
  - Training protocol (AdamW, cosine decay)
  - Weight preprocessing pipeline
- **Why Reused**: Controlled experiment - same architectures, now testing sample efficiency

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (TrojAI) | Phase 2B | 02b_verification_plan.md Section 1.3 |
| DWS architecture | GitHub + h-m1 | AvivNavon/DWS, h-m1 validation |
| NFT architecture | GitHub + h-m1 | Zhou et al. 2024, h-m1 validation |
| Sample efficiency protocol | Archon KB | Standard ML practice |
| Training protocol | h-m1 | Previous validation (AdamW, cosine) |
| Evaluation metrics (AUC) | Phase 2B | Success criteria Section 2.2 |
| Expected baseline | Archon KB | ~0.70 AUC MLP, 0.80+ equivariant |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- 2026-08-28: Experiment design initiated (Phase 2C Step 1)
- 2026-08-28: Archon KB search completed (Step 2)
- 2026-08-28: GitHub implementations documented (Step 3)
- 2026-08-28: Serena analysis skipped - code clear from h-m1 (Step 4)
- 2026-08-28: Dataset/baseline confirmed from h-m1 (Step 5)
- 2026-08-28: Experiment specification synthesized (Step 6)
- 2026-08-28: References documented (Step 7)
- 2026-08-28: Quality validation PASSED (Step 8)
- 2026-08-28: **Experiment design COMPLETED**

### Quality Validation
- ✅ All hyperparameters justified (from h-m1 + Archon KB)
- ✅ Dataset choice justified (TrojAI standard benchmark)
- ✅ Mechanism grounded in code (sample efficiency protocol standard)
- ✅ No unsupported assumptions
- ✅ Full traceability

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis - skipped)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
