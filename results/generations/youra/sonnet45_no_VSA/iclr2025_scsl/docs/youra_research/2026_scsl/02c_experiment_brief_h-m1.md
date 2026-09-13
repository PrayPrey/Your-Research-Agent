# Phase 2C: Experiment Design Brief

**Generated:** 2026-07-11  
**Hypothesis ID:** h-m1  
**Hypothesis Type:** MECHANISM  
**Pipeline Project:** Anonymous Pipeline: Minimal Research Scope Test  

---

## Executive Summary

This experiment brief provides implementation-ready specifications for testing the dose-response mechanism hypothesis (h-m1): "Asymmetric digit degradation increases monotonically with flip probability (dose-response relationship)". The design leverages standard MNIST classification with varying horizontal flip augmentation probabilities to establish a causal dose-response relationship between augmentation intensity and performance degradation on asymmetric digits.

**Key Design Decisions:**
- **Dataset:** MNIST (standard split: 60k train, 10k test)
- **Model:** Standard CNN (2 conv layers, proven baseline for MNIST)
- **Experimental Conditions:** 4 flip probabilities {0.0, 0.3, 0.5, 0.9} × 5 random seeds
- **Primary Metric:** Spearman rank correlation between flip probability and asymmetric digit accuracy degradation
- **Statistical Power:** n=5 seeds per condition, Cohen's d≥0.5 threshold

---

## Section 1: Hypothesis Context

### 1.1 Hypothesis Statement

**ID:** h-m1  
**Type:** MECHANISM  
**Statement:** Asymmetric digit degradation increases monotonically with flip probability (dose-response relationship)

**Expanded Causal Chain:**
1. Horizontal flip creates non-canonical asymmetric digit images
2. Invalid images retain original labels → label noise
3. Training on label noise degrades test accuracy on affected classes
4. **Degradation magnitude increases monotonically with flip probability** (dose-response)

**Prerequisites:** h-e1 (Existence hypothesis - asymmetric digit degradation effect)

**Gate Type:** SHOULD_WORK (mechanism strengthens claim but effect may exist without full mechanistic understanding)

### 1.2 Research Question

**Primary:** Does asymmetric digit test accuracy decrease monotonically as horizontal flip probability increases from 0.0 to 0.9?

**Secondary:**
- Is the dose-response relationship statistically significant (Spearman ρ < 0, p < 0.05)?
- Can we observe graded degradation at intermediate probabilities (p=0.3, p=0.5)?
- Does the mechanism hold across multiple random seeds (n=5)?

### 1.3 Success Criteria

**Primary:**
- Spearman rank correlation ρ significantly negative (p < 0.05)
- Monotonic degradation pattern: Acc(p=0.0) > Acc(p=0.3) > Acc(p=0.5) > Acc(p=0.9)

**Secondary:**
- Degradation visible at p=0.3 (early dose-response detection)
- Effect size increases with probability (dose-dependent magnitude)
- Consistent pattern across all 5 random seeds

**Failure Modes:**
- Non-monotonic relationship (e.g., Acc(p=0.5) > Acc(p=0.3))
- No significant correlation (p ≥ 0.05)
- High variance across seeds obscures trend

---

## Section 2: Dataset Specification

### 2.1 Dataset Selection

**Dataset Name:** MNIST  
**Type:** standard  
**Source:** torchvision.datasets.MNIST (auto-download)  
**Justification:**
- Standard benchmark for image classification with well-established baselines (~99% accuracy)
- Contains both symmetric {0,1,8} and asymmetric {2,3,5,6,7,9} digits
- Horizontal flip creates semantically invalid transformations for asymmetric digits
- Fast training cycles (~2 hours for all conditions) enable dose-response sweep

**Dataset Statistics:**
- Training samples: 60,000
- Test samples: 10,000 (statistically meaningful - NO synthetic data)
- Classes: 10 (digits 0-9)
- Image size: 28×28 grayscale
- Channel: 1 (grayscale)
- Value range: [0, 255] (normalized to [0, 1])

**Split Strategy:**
- **Train:** 50,000 samples (first 50k of MNIST train)
- **Validation:** 10,000 samples (last 10k of MNIST train)
- **Test:** 10,000 samples (official MNIST test set)
- **No custom splits:** Use consistent splits for reproducibility

### 2.2 Data Preprocessing

**Normalization:**
```python
transforms.Normalize(mean=(0.1307,), std=(0.3081,))
```
- Standard MNIST normalization constants (computed on training set)
- Applied AFTER augmentation to ensure valid pixel ranges

**No Additional Preprocessing:**
- No resizing (images already 28×28)
- No cropping (full digit visible)
- No color transformations (grayscale dataset)

### 2.3 Augmentation Strategy (Experimental Manipulation)

**Baseline Condition (p=0.0):**
```python
transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])
```

**Flip Conditions (p ∈ {0.3, 0.5, 0.9}):**
```python
transforms.Compose([
    transforms.RandomHorizontalFlip(p=FLIP_PROB),  # EXPERIMENTAL VARIABLE
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])
```

**Dose-Response Levels:**
1. **p=0.0:** No augmentation (baseline)
2. **p=0.3:** Low dose (30% of training samples flipped)
3. **p=0.5:** Medium dose (50% of training samples flipped)
4. **p=0.9:** High dose (90% of training samples flipped)

**Rationale for Dose Selection:**
- **p=0.3:** Detects early-stage degradation (sensitivity check)
- **p=0.5:** Standard augmentation probability in literature
- **p=0.9:** Near-maximal label noise (ceiling effect check)
- **Spacing:** Non-uniform to capture potential non-linear relationships

**Implementation Note:**
- Apply flip BEFORE ToTensor (operates on PIL Image)
- Flip probability applied per-sample during each epoch (stochastic augmentation)
- Same augmentation pipeline for all training epochs (no curriculum)

### 2.4 Data Loading

**DataLoader Configuration:**
```python
train_loader = DataLoader(
    dataset=train_dataset,
    batch_size=64,
    shuffle=True,
    num_workers=4,
    pin_memory=True  # GPU acceleration
)

test_loader = DataLoader(
    dataset=test_dataset,
    batch_size=256,  # Larger batch for inference
    shuffle=False,
    num_workers=4,
    pin_memory=True
)
```

**Memory Requirements:**
- Training set: ~11 MB (60k × 28×28 × 1 byte)
- Test set: ~1.8 MB (10k × 28×28 × 1 byte)
- Total: ~13 MB (fits in memory, no streaming required)

---

## Section 3: Model Architecture

### 3.1 Architecture Selection

**Model Name:** Standard CNN  
**Type:** custom  
**Justification:**
- Proven baseline for MNIST (~99% accuracy without augmentation)
- Simple architecture minimizes confounding factors
- Fast training (~4-6 minutes per condition on GPU)
- Sufficient capacity to learn MNIST patterns without overfitting

**Architecture Specification:**
```
Input: [batch_size, 1, 28, 28]

Conv Block 1:
  Conv2d(in_channels=1, out_channels=32, kernel_size=3, padding=1)
  ReLU()
  Conv2d(in_channels=32, out_channels=32, kernel_size=3, padding=1)
  ReLU()
  MaxPool2d(kernel_size=2, stride=2)  # [batch, 32, 14, 14]
  Dropout(p=0.25)

Conv Block 2:
  Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
  ReLU()
  Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1)
  ReLU()
  MaxPool2d(kernel_size=2, stride=2)  # [batch, 64, 7, 7]
  Dropout(p=0.25)

Classifier:
  Flatten()  # [batch, 64*7*7] = [batch, 3136]
  Linear(3136, 128)
  ReLU()
  Dropout(p=0.5)
  Linear(128, 10)

Output: [batch_size, 10] (logits)
```

**Parameter Count:** ~470k parameters
- Conv1: (3×3×1×32) + (3×3×32×32) = 9,536
- Conv2: (3×3×32×64) + (3×3×64×64) = 55,360
- FC1: 3136×128 = 401,408
- FC2: 128×10 = 1,280
- **Total:** ~467k parameters

### 3.2 Initialization

**Weight Initialization:** PyTorch default (Kaiming uniform for Conv2d, Xavier for Linear)  
**Bias Initialization:** Zeros  
**Random Seed Control:**
```python
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)
np.random.seed(seed)
random.seed(seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

**Seeds:** {42, 123, 456, 789, 2024} (5 independent runs per condition)

---

## Section 4: Training Protocol

### 4.1 Optimization

**Optimizer:** Adam  
**Learning Rate:** 0.001 (PyTorch default, proven for MNIST)  
**Beta Parameters:** β₁=0.9, β₂=0.999  
**Weight Decay:** 0.0 (no L2 regularization, dropout suffices)  
**Epsilon:** 1e-8  

**Loss Function:** CrossEntropyLoss (combines LogSoftmax + NLLLoss)

**Batch Size:** 64 (training), 256 (evaluation)  
**Epochs:** 30 (with early stopping)

### 4.2 Early Stopping

**Metric:** Validation accuracy  
**Patience:** 5 epochs  
**Direction:** Maximize  
**Min Delta:** 0.001 (0.1% improvement threshold)

**Rationale:**
- Prevents overfitting under high flip probabilities (p=0.9)
- Ensures fair comparison (models stopped at peak generalization)
- Reduces computational cost (~20% fewer epochs on average)

### 4.3 Learning Rate Scheduling

**Scheduler:** None  
**Rationale:** MNIST converges quickly with fixed learning rate; scheduling adds complexity without clear benefit for this hypothesis test

### 4.4 Training Loop Pseudocode

```python
for epoch in range(max_epochs):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
    
    # Validation
    model.eval()
    val_loss, val_acc = evaluate(model, val_loader)
    
    # Early stopping check
    if val_acc > best_val_acc + min_delta:
        best_val_acc = val_acc
        patience_counter = 0
        save_checkpoint(model)
    else:
        patience_counter += 1
        if patience_counter >= patience:
            break  # Stop training
    
    # Test evaluation (NOT used for early stopping)
    test_loss, test_acc, per_class_acc = evaluate_per_class(model, test_loader)
    log_metrics(epoch, train_loss, val_acc, test_acc, per_class_acc)
```

---

## Section 5: Evaluation Protocol

### 5.1 Metrics

**Primary Metric: Asymmetric Digit Accuracy**
```python
asymmetric_digits = [2, 3, 5, 6, 7, 9]
asymmetric_acc = mean([per_class_acc[d] for d in asymmetric_digits])
```

**Secondary Metrics:**
- **Per-Class Accuracy:** Accuracy for each digit 0-9 (granular analysis)
- **Symmetric Digit Accuracy:** mean([per_class_acc[d] for d in [0, 1, 8]])
- **Overall Test Accuracy:** Standard top-1 accuracy
- **Accuracy Degradation:** Baseline_acc - Flip_acc

**Statistical Metrics:**
- **Spearman Rank Correlation:** ρ between flip probability and asymmetric accuracy
- **P-value:** Statistical significance of correlation
- **Cohen's d:** Effect size between conditions

### 5.2 Evaluation Procedure

**Test Set Evaluation:**
1. Load best checkpoint (highest validation accuracy)
2. Set model to eval mode (disable dropout)
3. Disable gradient computation (torch.no_grad())
4. Predict on full test set (10k samples)
5. Compute per-class accuracy for all 10 digits
6. Aggregate asymmetric digit accuracy

**Per-Class Accuracy Computation:**
```python
def compute_per_class_accuracy(model, test_loader, num_classes=10):
    class_correct = [0] * num_classes
    class_total = [0] * num_classes
    
    with torch.no_grad():
        for data, target in test_loader:
            output = model(data.to(device))
            pred = output.argmax(dim=1)
            
            for i in range(num_classes):
                class_mask = (target == i)
                class_correct[i] += (pred[class_mask] == i).sum().item()
                class_total[i] += class_mask.sum().item()
    
    per_class_acc = [correct / total for correct, total in zip(class_correct, class_total)]
    return per_class_acc
```

### 5.3 Statistical Analysis

**Dose-Response Analysis:**
```python
from scipy.stats import spearmanr

# Collect data across all seeds
flip_probs = [0.0, 0.3, 0.5, 0.9]
asymmetric_accs = []  # Shape: [n_conditions, n_seeds]

for prob in flip_probs:
    for seed in seeds:
        acc = load_result(prob, seed)['asymmetric_acc']
        asymmetric_accs.append((prob, acc))

# Compute Spearman correlation
rho, p_value = spearmanr([x[0] for x in asymmetric_accs], 
                         [x[1] for x in asymmetric_accs])

print(f"Spearman ρ = {rho:.3f}, p = {p_value:.4f}")
# Expected: ρ < 0 (negative correlation), p < 0.05 (significant)
```

**Pairwise Comparisons:**
- Wilcoxon signed-rank test between consecutive dose levels
- Cohen's d effect size for practical significance
- Bonferroni correction for multiple comparisons (k=3 pairs)

---

## Section 6: Experimental Design

### 6.1 Experimental Conditions

**Independent Variable:** Horizontal flip probability (p)  
**Levels:** {0.0, 0.3, 0.5, 0.9}  
**Replication:** 5 random seeds per condition  
**Total Runs:** 4 conditions × 5 seeds = 20 training runs

**Controlled Variables:**
- Model architecture (fixed)
- Optimizer hyperparameters (fixed)
- Dataset split (fixed)
- Evaluation protocol (fixed)
- Random seed (varied systematically)

**Dependent Variable:** Asymmetric digit test accuracy (%)

### 6.2 Experimental Matrix

```
┌─────────────┬──────┬──────┬──────┬──────┬──────┐
│ Condition   │ Seed │ Seed │ Seed │ Seed │ Seed │
│             │  42  │ 123  │ 456  │ 789  │ 2024 │
├─────────────┼──────┼──────┼──────┼──────┼──────┤
│ Baseline    │ Run1 │ Run2 │ Run3 │ Run4 │ Run5 │
│ (p=0.0)     │      │      │      │      │      │
├─────────────┼──────┼──────┼──────┼──────┼──────┤
│ Low Flip    │ Run6 │ Run7 │ Run8 │ Run9 │ Run10│
│ (p=0.3)     │      │      │      │      │      │
├─────────────┼──────┼──────┼──────┼──────┼──────┤
│ Medium Flip │ Run11│ Run12│ Run13│ Run14│ Run15│
│ (p=0.5)     │      │      │      │      │      │
├─────────────┼──────┼──────┼──────┼──────┼──────┤
│ High Flip   │ Run16│ Run17│ Run18│ Run19│ Run20│
│ (p=0.9)     │      │      │      │      │      │
└─────────────┴──────┴──────┴──────┴──────┴──────┘
```

### 6.3 Execution Strategy

**Parallel Execution:**
- All 20 runs are independent (no dependencies)
- Can run in parallel on multi-GPU setup
- Estimated wall-clock time: ~6 minutes per run × 20 runs / n_gpus

**Sequential Fallback:**
- Single GPU: ~2 hours total (6 min × 20)
- CPU only: ~6 hours total (estimated 3× slower)

**Checkpointing:**
- Save best model checkpoint per run
- Log per-epoch metrics to CSV
- Store final test results in JSON

---

## Section 7: Implementation Plan

### 7.1 Code Structure

```
experiments/h-m1/
├── config.py                 # Hyperparameters and experimental settings
├── data.py                   # Dataset loading and augmentation
├── model.py                  # CNN architecture definition
├── train.py                  # Training loop with early stopping
├── evaluate.py               # Test evaluation and per-class metrics
├── run_experiments.py        # Main script (runs all 20 conditions)
├── analyze_dose_response.py  # Statistical analysis (Spearman, plots)
└── results/
    ├── checkpoints/          # Saved model weights
    ├── logs/                 # Training logs (CSV)
    └── analysis/             # Final results (JSON, plots)
```

### 7.2 Key Implementation Details

**Config Management:**
```python
# config.py
FLIP_PROBS = [0.0, 0.3, 0.5, 0.9]
SEEDS = [42, 123, 456, 789, 2024]
BATCH_SIZE = 64
LEARNING_RATE = 0.001
MAX_EPOCHS = 30
EARLY_STOP_PATIENCE = 5
ASYMMETRIC_DIGITS = [2, 3, 5, 6, 7, 9]
SYMMETRIC_DIGITS = [0, 1, 8]
```

**Augmentation Factory:**
```python
def get_transform(flip_prob):
    if flip_prob == 0.0:
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
    else:
        return transforms.Compose([
            transforms.RandomHorizontalFlip(p=flip_prob),
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
```

**Result Logging:**
```python
# Per-run results (JSON)
{
    "flip_prob": 0.5,
    "seed": 42,
    "final_epoch": 23,
    "best_val_acc": 0.9856,
    "test_acc": 0.9842,
    "per_class_acc": [0.991, 0.996, 0.972, ...],
    "asymmetric_acc": 0.978,
    "symmetric_acc": 0.994,
    "training_time_sec": 312.5
}
```

### 7.3 Computational Requirements

**Hardware:**
- GPU: NVIDIA GPU with ≥4GB VRAM (e.g., GTX 1650, RTX 2060)
- CPU: 4+ cores (for DataLoader workers)
- RAM: 8GB minimum
- Storage: ~500MB (checkpoints + logs)

**Software:**
- Python 3.8+
- PyTorch 1.12+ (with CUDA 11.6+)
- torchvision 0.13+
- NumPy, SciPy, Matplotlib (for analysis)

**Time Estimate:**
- Single run: ~6 minutes (GPU) / ~18 minutes (CPU)
- All 20 runs: ~2 hours (sequential, GPU) / ~6 hours (CPU)
- Parallel (4 GPUs): ~30 minutes

---

## Section 8: Expected Results

### 8.1 Predicted Outcomes

**Baseline (p=0.0):**
- Overall test accuracy: ~99.0%
- Asymmetric digit accuracy: ~98.8%
- Symmetric digit accuracy: ~99.5%

**Low Flip (p=0.3):**
- Overall test accuracy: ~98.5%
- Asymmetric digit accuracy: ~98.0% (−0.8% vs baseline)
- Symmetric digit accuracy: ~99.4% (stable)

**Medium Flip (p=0.5):**
- Overall test accuracy: ~98.0%
- Asymmetric digit accuracy: ~97.2% (−1.6% vs baseline)
- Symmetric digit accuracy: ~99.3% (stable)

**High Flip (p=0.9):**
- Overall test accuracy: ~97.0%
- Asymmetric digit accuracy: ~95.8% (−3.0% vs baseline)
- Symmetric digit accuracy: ~99.0% (slight degradation from extreme noise)

**Dose-Response Relationship:**
- Spearman ρ ≈ −0.85 to −0.95 (strong negative correlation)
- p-value < 0.001 (highly significant)
- Monotonic degradation pattern confirmed

### 8.2 Visualization Plan

**Figure 1: Dose-Response Curve**
- X-axis: Flip probability (0.0, 0.3, 0.5, 0.9)
- Y-axis: Asymmetric digit accuracy (%)
- Data: Mean ± std across 5 seeds
- Expected: Monotonic decreasing trend

**Figure 2: Per-Class Accuracy Heatmap**
- Rows: Conditions (Baseline, p=0.3, p=0.5, p=0.9)
- Columns: Digits (0-9)
- Color: Accuracy (%)
- Expected: Asymmetric digits show progressive degradation

**Figure 3: Degradation Magnitude**
- X-axis: Flip probability
- Y-axis: Accuracy degradation (Baseline - Flip)
- Expected: Linear or slightly accelerating relationship

---

## Section 9: Risk Mitigation

### 9.1 Known Risks

**R1: Insufficient Statistical Power**
- **Risk:** n=5 seeds may not detect small effects (d<0.5)
- **Mitigation:** Use non-parametric tests (Wilcoxon, Spearman) robust to small samples
- **Fallback:** Increase to n=10 seeds if initial results inconclusive

**R2: Extreme Flip Probability (p=0.9) Collapse**
- **Risk:** Model fails to learn meaningful features (accuracy <50%)
- **Mitigation:** Monitor baseline accuracy during training; reduce to p=0.7 if needed
- **Early Warning:** Baseline accuracy <90% at p=0.9

**R3: Non-Monotonic Relationship**
- **Risk:** Degradation plateaus or reverses at high probabilities
- **Mitigation:** Analyze per-class trends; may indicate complex mechanism
- **Response:** Transition to EXPLORE gate (mechanism unclear but effect exists)

**R4: High Variance Across Seeds**
- **Risk:** Random seed variation obscures dose-response trend
- **Mitigation:** Report confidence intervals; check for outliers
- **Fallback:** Increase seeds or use bootstrapping for robust estimates

**R5: Symmetric Digit Degradation**
- **Risk:** High flip probabilities degrade even symmetric digits (confounds hypothesis)
- **Mitigation:** Separate analysis for symmetric vs asymmetric groups
- **Response:** Revise hypothesis to account for general label noise effects

### 9.2 Validation Checks

**Sanity Checks:**
1. Baseline (p=0.0) achieves ~99% test accuracy (confirms model capacity)
2. Symmetric digits remain stable across conditions (confirms semantic specificity)
3. Training loss decreases monotonically (confirms optimization stability)
4. Validation accuracy correlates with test accuracy (confirms early stopping validity)

**Data Quality Checks:**
1. Visual inspection: Ensure flipped images are semantically invalid for asymmetric digits
2. Label preservation: Verify labels unchanged after flip transformation
3. Class balance: Confirm ~1000 samples per digit in test set

---

## Section 10: Success Criteria & Decision Rules

### 10.1 Hypothesis Acceptance

**PRIMARY CRITERION (MUST SATISFY):**
- Spearman rank correlation ρ significantly negative (p < 0.05)

**SECONDARY CRITERIA (2 of 3 REQUIRED):**
1. Monotonic degradation pattern across all 4 dose levels
2. Cohen's d ≥ 0.5 between baseline and p=0.9 condition
3. Degradation visible at early dose (p=0.3 shows >0.5% drop vs baseline)

**HYPOTHESIS PASSES IF:** Primary + 2 secondary criteria satisfied

### 10.2 Hypothesis Rejection

**REJECTION CRITERIA (ANY TRIGGERS FAIL):**
1. Spearman p-value ≥ 0.05 (no significant correlation)
2. Non-monotonic relationship (e.g., Acc(p=0.5) > Acc(p=0.3))
3. Effect size trivial (Cohen's d < 0.2 between baseline and p=0.9)

**HYPOTHESIS FAILS IF:** Any rejection criterion satisfied

### 10.3 Decision Tree

```
START
  │
  ├─ Is Spearman ρ < 0 AND p < 0.05?
  │   ├─ YES → Are ≥2 secondary criteria satisfied?
  │   │         ├─ YES → HYPOTHESIS PASSES (mechanism confirmed)
  │   │         └─ NO → PARTIAL PASS (weak mechanism, route to EXPLORE)
  │   └─ NO → HYPOTHESIS FAILS (no dose-response detected)
```

**Gate Transition:**
- **PASS:** Mark h-m1 as COMPLETED, proceed to Phase 3 (implementation planning)
- **PARTIAL PASS:** Mark as EXPLORE (mechanism unclear), consider alternative mechanisms
- **FAIL:** Mark as FAILED, revisit h-e1 results (existence may be spurious)

---

## Section 11: Timeline & Deliverables

### 11.1 Timeline

**Phase 3 (Implementation Planning):** 2-3 hours
- Task decomposition (PRD, Architecture, PRP)
- Archon project initialization

**Phase 4 (Coding & Validation):** 3-4 hours
- Code implementation
- Experiment execution (20 runs)
- Statistical analysis
- Validation report

**Total Estimated Time:** 5-7 hours (end-to-end)

### 11.2 Deliverables

**Phase 3 Outputs:**
- [ ] PRD (Product Requirements Document)
- [ ] Architecture document
- [ ] PRP (Pre-Registration Protocol)
- [ ] Archon task list (breakdown of implementation steps)

**Phase 4 Outputs:**
- [ ] Implemented codebase (experiments/h-m1/)
- [ ] Trained models (20 checkpoints)
- [ ] Raw results (JSON logs)
- [ ] Statistical analysis report
- [ ] Dose-response visualizations
- [ ] 04_validation.md (hypothesis verdict)

---

## Section 12: References & Prior Work

### 12.1 Archon Knowledge Base Findings

**Relevant Past Cases:** None directly matching MNIST dose-response experiments in Archon KB (searched: "MNIST dose-response augmentation experiments")

**Code Examples:** Training loop patterns from diffusion model repositories (HuggingFace diffusers) applicable to standard supervised training

### 12.2 Implementation References (Exa Search)

**Key Findings:**
1. **MNIST Augmentation Standards:**
   - Rotation ±10-15° is common (positive control)
   - Horizontal flip avoided in official PyTorch examples (implicit semantic concern)
   - Standard normalization: mean=0.1307, std=0.3081

2. **Dose-Response Analysis in ML:**
   - Machine learning dose-response prediction is active research area (pharmaceutical applications)
   - Spearman correlation standard metric for monotonic relationships
   - Multi-output Gaussian Processes used for dose-response curve modeling

3. **Data Augmentation Best Practices:**
   - Probability-based augmentation (p parameter) standard in torchvision.transforms
   - Test-time augmentation (TTA) distinct from training augmentation (not applicable here)
   - Cross-validation with augmentation requires careful split handling (we use fixed splits)

### 12.3 Baseline Performance Expectations

**Literature Baselines:**
- Standard CNN on MNIST: 99.0-99.5% test accuracy (no augmentation)
- With rotation augmentation: 99.3-99.6% (slight improvement)
- With horizontal flip: Not reported (semantically invalid for MNIST)

**Expected Degradation Magnitude:**
- Small effect size (1-3%) anticipated due to high baseline accuracy
- Statistical power critical (n=5 seeds, Cohen's d≥0.5 threshold)

---

## Appendix A: Detailed Statistical Plan

### A.1 Spearman Rank Correlation

**Formula:**
```
ρ = 1 - (6 Σ d²) / (n(n² - 1))
```
where d = rank difference between flip probability and accuracy

**Interpretation:**
- ρ ∈ [−1, 1]
- ρ < 0: Negative correlation (higher flip → lower accuracy)
- ρ ≈ −1: Perfect monotonic decrease
- p < 0.05: Statistically significant relationship

**Implementation:**
```python
from scipy.stats import spearmanr

flip_probs_repeated = [0.0]*5 + [0.3]*5 + [0.5]*5 + [0.9]*5
asymmetric_accs = [result['asymmetric_acc'] for result in all_results]

rho, p_value = spearmanr(flip_probs_repeated, asymmetric_accs)
```

### A.2 Cohen's d Effect Size

**Formula:**
```
d = (μ₁ - μ₂) / σ_pooled
σ_pooled = sqrt((σ₁² + σ₂²) / 2)
```

**Interpretation:**
- d < 0.2: Trivial effect
- 0.2 ≤ d < 0.5: Small effect
- 0.5 ≤ d < 0.8: Medium effect
- d ≥ 0.8: Large effect

**Threshold:** d ≥ 0.5 (medium effect required for acceptance)

### A.3 Wilcoxon Signed-Rank Test

**Purpose:** Pairwise comparisons between consecutive dose levels  
**Null Hypothesis:** No difference in median asymmetric accuracy  
**Alternative:** Median accuracy decreases with dose

**Bonferroni Correction:**
- 3 pairwise tests: p=0.0 vs p=0.3, p=0.3 vs p=0.5, p=0.5 vs p=0.9
- Adjusted α = 0.05 / 3 ≈ 0.017

---

## Appendix B: File Format Specifications

### B.1 Training Log (CSV)

```csv
flip_prob,seed,epoch,train_loss,val_loss,val_acc,test_acc,test_loss,asymmetric_acc,symmetric_acc,duration_sec
0.0,42,1,0.4523,0.1234,0.9623,0.9598,0.1345,0.9512,0.9701,18.3
0.0,42,2,0.2156,0.0987,0.9712,0.9689,0.1012,0.9634,0.9789,18.1
...
```

### B.2 Final Results (JSON)

```json
{
  "hypothesis_id": "h-m1",
  "experiment_date": "2026-07-11",
  "results": [
    {
      "flip_prob": 0.0,
      "seed": 42,
      "final_epoch": 23,
      "best_val_acc": 0.9856,
      "test_acc": 0.9842,
      "asymmetric_acc": 0.9823,
      "symmetric_acc": 0.9945,
      "per_class_acc": [0.991, 0.996, 0.972, 0.985, 0.968, 0.980, 0.987, 0.983, 0.993, 0.976],
      "training_time_sec": 312.5
    }
  ],
  "statistical_analysis": {
    "spearman_rho": -0.89,
    "spearman_p": 0.0001,
    "cohens_d_baseline_vs_high": 0.67,
    "monotonic_pattern": true
  },
  "verdict": "PASS"
}
```

---

**Document Status:** COMPLETE  
**Ready for Phase 3:** YES  
**Next Step:** Implementation Planning (PRD, Architecture, PRP generation)
