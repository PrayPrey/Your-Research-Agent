# Experiment Design: H-M4

**Date:** 2026-08-12
**Author:** Anonymous
**Hypothesis Statement:** At N=1K, MLP probe invariance < 0.5 (insufficient data diversity)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests MLP's inability to learn permutation invariance from limited data.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M3 PASSED (MLP lacks built-in invariance, CV=0.194)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** H-M3 (Untrained MLP shows no permutation invariance)

### Gate Condition
MLP trained on N=1K must show probe invariance < 0.5 (meaning it has NOT learned permutation invariance from limited data).

**Success Metric:** Probe invariance score < 0.5
**Failure Response:** If invariance >= 0.5, revise mechanism theory (MLP learns faster than expected)

---

## Continuation Context

This experiment follows H-M3 which established that an **untrained** MLP has no built-in permutation invariance (CV=0.194, max deviation=0.0229). H-M4 now tests whether training on N=1K samples is sufficient for MLP to **learn** permutation invariance from data.

### Previous Hypothesis Results (H-M3)
- **MLP Coefficient of Variation:** 0.1943 (high variance = no invariance)
- **Max Deviation:** 0.0229
- **Conclusion:** Untrained MLP lacks architectural invariance, must learn from data

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for probe invariance testing. Relevant patterns from general ML knowledge base:
- **Probe methodology:** Feed permuted inputs, measure output correlation
- **Invariance quantification:** Use coefficient of variation or correlation metrics
- **Sample efficiency research:** Standard techniques for measuring data requirements

### Archon Code Examples

No directly relevant code examples found for MLP probe invariance testing. Experiment must be designed from first principles based on H-M1/M2/M3 established patterns.

### Exa GitHub Implementations

**Primary Source: NFN Library (AllanYangZhou/nfn)**
- URL: https://github.com/AllanYangZhou/nfn
- Paper: "Permutation Equivariant Neural Functionals" (NeurIPS 2023)
- Provides: WeightSpaceFeatures, NPLinear, HNPPool for processing neural network weights
- Key insight: NFN achieves probe invariance ~1.0 architecturally; MLP must learn it

**Secondary Source: ProbeGen (ICLR 2025)**
- Paper: "Deep Linear Probe Generators for Weight Space Learning"
- URL: https://proceedings.iclr.cc/paper_files/paper/2025/file/2aab8a76c7e761b66eccaca0927787de-Paper-Conference.pdf
- Relevant finding: Probing approaches require sufficient data diversity

**Tertiary Source: Permutation Invariance Blog**
- URL: https://www.marti.ai/ml/2019/09/01/correl-invariance-permutations-nn.html
- Key insight: n! equivalent inputs for dimension n means standard NNs are extremely data-inefficient

### Implementation Priority Assessment

**CRITICAL: Reuse H-E1/H-M3 code infrastructure**

**Recommended Implementation Path:**
- Primary: Extend H-M3 `test_variance.py` with trained MLP evaluation
- Fallback: Standalone probe invariance tester
- Justification: H-M3 established MLP architecture and permutation testing; H-M4 adds training step

### Code Analysis (Serena MCP)

Not applicable - no existing codebase to analyze. Fresh implementation using patterns from prior hypotheses.

---

## Experiment Specification

### Dataset

**Name:** Model Zoo CIFAR-10 CNN Subset (N=1K sample)
**Type:** standard
**Source:** github.com/ModelZoos/ModelZooDataset

| Attribute | Value |
|-----------|-------|
| Total Models | ~50,000 (CIFAR-10 CNN family) |
| Training Sample | N=1,000 (random subset) |
| Test Set | 20% holdout (~200 models) |
| Input Format | Flattened weight vectors |
| Target | Test accuracy (0-100%) |

**Preprocessing:**
1. Extract single-architecture CNN family from Model Zoo
2. Random sample N=1,000 for training
3. Hold out 20% for test (consistent with H-E1)
4. Flatten weights to vector representation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets / direct download
- Identifier: github.com/ModelZoos/ModelZooDataset
- Code:
```python
from datasets import load_dataset
# Or direct download from ModelZoos repo
dataset = load_dataset("model_zoo_cifar10_cnn", split="train")
train_subset = dataset.shuffle(seed=42).select(range(1000))
```

### Models

#### Baseline Model

**MLP-Matched** (same as H-E1/H-M3)

| Attribute | Value |
|-----------|-------|
| Architecture | Input → 256 → 128 → 1 |
| Input Dim | Flattened weight vector size |
| Hidden Layers | 2 |
| Activation | ReLU |
| Output | Single regression value |
| Parameters | Matched to NFN parameter count |

**Loading Information** (for Phase 4 download):
- Method: Custom PyTorch implementation (from H-M3)
- Identifier: `MLPMatched` class
- Code:
```python
class MLPMatched(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
    
    def forward(self, x):
        return self.net(x)
```

#### Proposed Model

**Architecture:** Same MLP-Matched, but TRAINED on N=1K

**Core Mechanism Implementation:**

```python
def compute_probe_invariance(model, weight_vector, num_permutations=10):
    """
    Compute probe invariance score for trained MLP.
    
    Probe invariance = mean correlation of outputs across permutations.
    High invariance (>0.9) = model learned permutation invariance
    Low invariance (<0.5) = model did NOT learn invariance
    
    Args:
        model: Trained MLP model
        weight_vector: Original CNN weight vector [D]
        num_permutations: Number of random permutations to test
    
    Returns:
        invariance_score: float in [0, 1]
        predictions: list of predictions for each permutation
    """
    model.eval()
    predictions = []
    
    with torch.no_grad():
        # Original prediction
        pred_original = model(weight_vector.unsqueeze(0)).item()
        predictions.append(pred_original)
        
        # Permuted predictions
        for i in range(num_permutations):
            # Create random permutation
            perm = torch.randperm(weight_vector.size(0))
            weight_permuted = weight_vector[perm]
            
            # Predict on permuted weights
            pred_permuted = model(weight_permuted.unsqueeze(0)).item()
            predictions.append(pred_permuted)
    
    # Compute invariance metrics
    predictions = np.array(predictions)
    mean_pred = predictions.mean()
    std_pred = predictions.std()
    
    # Coefficient of variation (lower = more invariant)
    cv = std_pred / abs(mean_pred) if abs(mean_pred) > 1e-8 else float('inf')
    
    # Invariance score = 1 - normalized_cv (higher = more invariant)
    # Cap CV contribution at 1.0
    invariance_score = max(0.0, 1.0 - min(cv, 1.0))
    
    return invariance_score, predictions, cv


def run_hm4_experiment(train_data, test_data, n_train=1000, num_seeds=10):
    """
    Full H-M4 experiment: Train MLP on N=1K, measure probe invariance.
    
    Expected result: invariance_score < 0.5 (MLP hasn't learned invariance)
    """
    results = []
    
    for seed in range(num_seeds):
        torch.manual_seed(seed)
        
        # Sample N=1K training data
        indices = torch.randperm(len(train_data))[:n_train]
        train_subset = train_data[indices]
        
        # Initialize MLP
        input_dim = train_subset[0][0].numel()
        model = MLPMatched(input_dim)
        
        # Train MLP
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        criterion = nn.MSELoss()
        
        model.train()
        for epoch in range(50):
            for weights, accuracy in DataLoader(train_subset, batch_size=32):
                optimizer.zero_grad()
                pred = model(weights.flatten(1))
                loss = criterion(pred.squeeze(), accuracy)
                loss.backward()
                optimizer.step()
        
        # Test probe invariance on test models
        invariance_scores = []
        for test_weights, _ in test_data:
            score, _, cv = compute_probe_invariance(model, test_weights.flatten())
            invariance_scores.append(score)
        
        results.append({
            'seed': seed,
            'mean_invariance': np.mean(invariance_scores),
            'std_invariance': np.std(invariance_scores)
        })
    
    return results
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Optimizer | AdamW | Standard for regression tasks |
| Learning Rate | 1e-3 | Default; H-E1 validated |
| Scheduler | None | Short training, not needed |
| Batch Size | 32 | Fits in memory |
| Epochs | 50 | Match H-E1 protocol |
| Loss | MSE | Regression target |
| Seeds | 10 | Statistical power |

### Evaluation

**Primary Metric:** Probe Invariance Score
- Definition: 1 - (normalized coefficient of variation across permutations)
- Range: 0 (no invariance) to 1 (perfect invariance)
- Threshold: < 0.5 for PASS

**Secondary Metrics:**
- Coefficient of Variation (CV) across permutations
- Max deviation from mean prediction
- Test R² on accuracy prediction

**Success Criteria (PoC):**
1. Mean probe invariance < 0.5 across 10 seeds
2. NFN probe invariance > 0.95 (contrast with architectural invariance)
3. CV > 0.2 (significant prediction variance under permutation)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Regression + Invariance Testing
- Library: numpy, scipy
- Code:
```python
from scipy import stats

def evaluate_probe_invariance(predictions):
    """Compute invariance from prediction list."""
    mean = np.mean(predictions)
    std = np.std(predictions)
    cv = std / abs(mean) if abs(mean) > 1e-8 else float('inf')
    invariance = max(0.0, 1.0 - min(cv, 1.0))
    return invariance, cv
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Probe Invariance Comparison**: Bar chart comparing MLP (N=1K) invariance vs NFN invariance
  - Expected: MLP << 0.5, NFN >> 0.95

#### Additional Figures (LLM Autonomous)
1. **Prediction Scatter (Permuted vs Original)**: MLP predictions should scatter widely; NFN tight on diagonal
2. **Invariance Distribution**: Histogram of invariance scores across test models
3. **CV Comparison**: MLP CV >> NFN CV

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m4/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. MLP probe invariance < 0.5 at N=1K
3. NFN probe invariance > 0.95 (control)
4. Clear separation between MLP and NFN invariance

**Gate Type:** SHOULD_WORK
**Failure Action:** If MLP invariance >= 0.5, revise mechanism theory - MLP learns invariance faster than expected

---

## Appendix: Reference Implementations

### 1. NFN Official Library
- **Source:** https://github.com/AllanYangZhou/nfn
- **Relevance:** Provides WeightSpaceFeatures, state_dict_to_tensors for processing weights
- **Usage:** NFN as invariance control (should achieve ~1.0)

### 2. H-M3 Codebase (Prior Hypothesis)
- **Source:** h-m3/code/
- **Relevance:** MLPMatched class, permutation generation, variance metrics
- **Usage:** Extend with training loop and probe invariance computation

### 3. Permutation Equivariant Neural Functionals Paper
- **Source:** https://arxiv.org/abs/2302.14040
- **Relevance:** Mathematical framework for equivariance; explains why NFN is invariant
- **Usage:** Background theory; validation that NFN should show invariance ~1.0

### 4. Model Zoo Dataset
- **Source:** github.com/ModelZoos/ModelZooDataset
- **Relevance:** 50K+ trained CNN models with accuracy labels
- **Usage:** Training data (N=1K subset) and test data

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-12

### Workflow History for This Hypothesis
- H-E1 COMPLETED: NFN R² advantage confirmed (0.5995 > 0.05 threshold)
- H-M1 COMPLETED: NFN equivariant layers produce invariant outputs (correlation 0.9999999)
- H-M2 COMPLETED: NFN predictions identical under permutation (max_dev 1.19e-07)
- H-M3 COMPLETED: Untrained MLP lacks invariance (CV 0.1943)
- H-M4 IN_PROGRESS: Testing if trained MLP (N=1K) learns invariance

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
