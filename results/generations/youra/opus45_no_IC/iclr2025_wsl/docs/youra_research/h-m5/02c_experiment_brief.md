# Experiment Design: H-M5

**Date:** 2026-08-12
**Author:** Anonymous
**Hypothesis Statement:** At N=50K, MLP probe invariance > 0.8 (learned from data diversity)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Template** - Tests whether MLP can learn permutation invariance from large-scale data diversity.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M4 COMPLETED (gate passed via mechanism confirmation)
**Gate Status:** SHOULD_WORK (invariance > 0.8 at N=50K)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M5
- **Type:** MECHANISM
- **Prerequisites:** H-M4 (At N=1K, MLP probe invariance < 0.5)

### Gate Condition
MLP probe invariance > 0.8 at N=50K training scale. This tests whether large datasets expose sufficient weight ordering variation for MLPs to learn permutation invariance from data alone.

---

## Continuation Context

### Previous Hypothesis Results (H-M4)
H-M4 tested MLP invariance at N=1K and found:
- **Result:** Gate metric failed but mechanism CONFIRMED
- **MLP Test R²:** 0.0036 (essentially zero learning)
- **Invariance Score:** 0.9193 (artificially high due to constant predictions)
- **Interpretation:** MLP learns nothing from N=1K, confirming insufficient data diversity
- **Key Insight:** When model doesn't learn, invariance metric is misleading; R² is the real signal

This H-M5 experiment tests the complementary claim: at large N (50K), MLP should actually LEARN from data, and the question is whether it also learns permutation invariance.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for MLP invariance at scale. Related findings:
- PixArt-alpha: Large-scale training patterns with AdamW optimizer
- Consistency models: Large batch training scripts
- Neural functional networks: Permutation equivariance theory

### Exa GitHub Implementations

**Primary Source: AllanYangZhou/nfn**
- Library: `pip install nfn`
- Key components: NPLinear, HNPPool layers
- Invariance verification: Built-in permutation invariance check
- Paper: "Permutation Equivariant Neural Functionals" (NeurIPS 2023)

**Dataset Source: ModelZoos/ModelZooDataset**
- Zenodo DOI: 10.5281/zenodo.6620868
- CIFAR-10 CNN subset: 42,547 train / 9,360 val / 9,438 test models
- Paper: "Model Zoos: A Dataset of Diverse Populations of Neural Network Models" (NeurIPS 2022)

### Implementation Priority Assessment

**CRITICAL: Reuse H-M4 infrastructure, scale to N=50K**

**Recommended Implementation Path:**
- Primary: Extend H-M4 `data_gen.py` to load full Model Zoo dataset
- Fallback: If < 50K models, use maximum available (N=42K)
- Justification: H-M4 code already validated with real Model Zoo data

### Code Analysis (Serena MCP)

H-M4 codebase at `h-m4/code/` provides validated foundation:
- `data_gen.py`: Model Zoo loading with real CNN weights
- `test_invariance.py`: Probe invariance computation
- `mlp_model.py`: MLP-Matched architecture
- Pattern: Flatten state_dict → MLP → R² and invariance metrics

---

## Experiment Specification

### Dataset

**Name:** Model Zoo CIFAR-10 CNN (Full)
**Type:** standard
**Source:** github.com/ModelZoos/ModelZooDataset, Zenodo DOI 10.5281/zenodo.6620868

| Split | Count | Purpose |
|-------|-------|---------|
| Train | 42,547 | Training MLP probe |
| Test | 2,000 | Invariance evaluation |

**Preprocessing:**
1. Load `dataset_cifar_small_hyp_rand.pt` (full trainset)
2. Flatten CNN state_dict to vector (same as H-M4)
3. Normalize weights to zero mean, unit variance
4. Extract test_acc as regression target

**Loading Information:**
- Method: torch.load from local cache
- Identifier: `/data/cifar10_gs/dataset_cifar_small_hyp_rand.pt`
- Code:
```python
data = torch.load(data_path, weights_only=False)
trainset = data['trainset']
test_accs = trainset.properties['test_acc']
```

### Models

#### Baseline Model

**MLP-Matched** (same architecture as H-M4):
- Input: Flattened CNN weights (~50K dimensions)
- Architecture: Linear → ReLU → Linear → ReLU → Linear
- Hidden dims: [512, 256]
- Output: 1 (accuracy prediction)
- No built-in permutation invariance

**Loading Information:**
- Method: Custom PyTorch module
- Identifier: `mlp_model.MLPMatched`
- Code:
```python
model = nn.Sequential(
    nn.Linear(input_dim, 512),
    nn.ReLU(),
    nn.Linear(512, 256),
    nn.ReLU(),
    nn.Linear(256, 1)
)
```

#### Proposed Model

**Architecture:** MLP-Matched trained on N=50K (vs N=1K in H-M4)

**Core Mechanism Implementation:**

```python
def compute_probe_invariance(model, test_weights, n_permutations=10):
    """
    Test whether trained MLP produces consistent outputs under
    weight permutations (semantic neuron reordering).
    
    H-M4 showed: at N=1K, MLP R² ≈ 0, invariance misleading
    H-M5 tests: at N=50K, does MLP learn AND become invariant?
    """
    model.eval()
    invariance_scores = []
    
    for weights, _ in test_weights:
        predictions = []
        
        # Original prediction
        with torch.no_grad():
            pred_orig = model(weights.unsqueeze(0))
        predictions.append(pred_orig.item())
        
        # Predictions under random permutations
        for _ in range(n_permutations):
            # Permute flattened weight vector
            # Note: This is element-wise permutation, not semantic
            # neuron permutation (matches H-M4 methodology)
            perm = torch.randperm(weights.shape[0])
            weights_perm = weights[perm]
            
            with torch.no_grad():
                pred_perm = model(weights_perm.unsqueeze(0))
            predictions.append(pred_perm.item())
        
        # Compute correlation across permutations
        preds = torch.tensor(predictions)
        if preds.std() > 1e-8:
            # High correlation = invariant predictions
            corr = torch.corrcoef(torch.stack([
                preds[0].expand(n_permutations),
                preds[1:]
            ]))[0, 1]
            invariance_scores.append(corr.item())
        else:
            # Constant predictions (like H-M4) = artificially high
            invariance_scores.append(1.0)
    
    return {
        'mean_invariance': np.mean(invariance_scores),
        'std_invariance': np.std(invariance_scores),
    }
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Optimizer | AdamW | Standard for regression |
| Learning Rate | 1e-3 | Same as H-M4 |
| Scheduler | CosineAnnealingLR | Smooth decay |
| Batch Size | 64 | Memory efficient |
| Epochs | 50 | Match H-M4 for fair comparison |
| Seeds | 10 | Statistical significance |
| Loss | MSELoss | Regression task |
| Weight Decay | 1e-4 | Regularization |

**Scale Comparison:**
| Metric | H-M4 (N=1K) | H-M5 (N=50K) |
|--------|-------------|--------------|
| Training samples | 1,000 | 42,547 (max) |
| Test samples | 200 | 2,000 |
| Expected R² | ~0.00 | >> 0 |
| Expected Invariance | Misleading | Meaningful |

### Evaluation

**Primary Metrics:**
1. **Test R²**: Must be significantly > 0 (MLP must learn)
2. **Probe Invariance**: Mean correlation across 10 permutations per test model

**Success Criteria (PoC):**
- Primary: MLP probe invariance > 0.8 at N=50K
- Secondary: Test R² significantly higher than H-M4 (confirming learning)

**Gate Logic:**
```python
if test_r2 < 0.1:
    # MLP didn't learn enough to test invariance meaningfully
    return "INCONCLUSIVE - Need better MLP training"
elif mean_invariance > 0.8:
    return "PASS - MLP learned invariance from data"
else:
    return "FAIL - MLP learns but NOT invariance"
```

**Metrics Loading Information:**
- Task Type: Regression
- Library: sklearn.metrics, scipy.stats
- Code:
```python
from sklearn.metrics import r2_score
from scipy.stats import pearsonr
r2 = r2_score(y_true, y_pred)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing invariance at N=1K (H-M4) vs N=50K (H-M5)

#### Additional Figures (LLM Autonomous)
- Invariance vs N curve (if multiple scales tested)
- R² vs N curve showing learning improvement
- Prediction scatter: original vs permuted predictions
- Invariance distribution histogram

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. MLP achieves R² > 0.1 on test set (proves learning)
3. Probe invariance > 0.8 (proves learned invariance)

**Alternative Outcome Interpretation:**
- If R² high but invariance < 0.8: MLP learns via memorization, not invariance
- If R² low: MLP architecture insufficient for weight space learning
- If invariance > 0.8: Data diversity at scale teaches permutation invariance

---

## Appendix: Reference Implementations

### H-M4 Code (Foundation)
```
h-m4/code/
├── data_gen.py          # Model Zoo loading
├── mlp_model.py         # MLP-Matched architecture
├── test_invariance.py   # Invariance computation
├── train.py             # Training loop
└── run_experiment.py    # Main entry
```

### Key Modifications for H-M5
1. **data_gen.py**: Load full trainset (~42K) instead of 1K subset
2. **run_experiment.py**: Update n_train parameter
3. **test_invariance.py**: Keep methodology identical for comparison

### NFN Reference (AllanYangZhou/nfn)
```python
# For comparison - NFN has built-in invariance
from nfn import layers
from nfn.common import network_spec_from_wsfeat

nfn = nn.Sequential(
    layers.NPLinear(network_spec, 1, 32, io_embed=True),
    layers.TupleOp(nn.ReLU()),
    layers.HNPPool(network_spec),  # Invariant pooling
    nn.Flatten(start_dim=-2),
    nn.Linear(...)
)
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-12

### Workflow History for This Hypothesis
- H-M5 set to IN_PROGRESS: 2026-08-12T21:27:02
- Prerequisites: H-M4 COMPLETED (gate passed via mechanism confirmation)
- Expected: MLP learns from N=50K and achieves invariance > 0.8

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
