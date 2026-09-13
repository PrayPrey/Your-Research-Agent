# Adapter: Training Script Modification (Mode B)

> **Reference Guide for Phase 5 Step 7 - Training Script Task**
> Template for modifying baseline's train.py to use OUR algorithm

---

## Purpose

Modify baseline's train.py to inject OUR algorithm while preserving baseline's model, dataset, and configuration.

---

## Mode B Principle

```
PRESERVE (DO NOT MODIFY):
  ✗ Data loading code → Keep baseline's exactly as-is
  ✗ Model creation code → Keep baseline's exactly as-is
  ✗ Hyperparameters → Keep baseline's exactly as-is
  ✗ Training loop structure → Keep baseline's structure

INJECT (MINIMAL ADDITIONS):
  ✓ Our algorithm (optimizer replacement/wrapper)
  ✓ Metric tracking (psi computation)
  ✓ Results saver (comparison format output)
```

---

## Modification Pattern

```python
# ============================================================================
# BASELINE TRAINING SCRIPT MODIFICATIONS FOR MODE B COMPARISON
# ============================================================================
#
# Original file: {clone_path}/train.py
# Modified for: YouRA fair comparison (Mode B - Algorithm Injection)
# See: _references/fair-comparison-principle.md
#
# ============================================================================

# === STEP 0: ADD PATH FOR ADAPTATIONS MODULE ===
# CRITICAL: This must be added FIRST, before any adapter imports!

import sys
import os

# Get adaptations folder path
_current_file = os.path.abspath(__file__)
_baseline_folder = os.path.dirname(os.path.dirname(os.path.dirname(_current_file)))
sys.path.insert(0, _baseline_folder)

# === STEP 1: ADD IMPORTS (ONLY ALGORITHM + METRICS + RESULTS) ===
# Note: NO data adapter or model adapter imports!

from adaptations.{repo_name}.algorithm_injection import get_our_optimizer
from adaptations.{repo_name}.metrics import compute_psi, MetricTracker
from adaptations.{repo_name}.results_saver import ResultsSaver

# === STEP 2: ADD ARGUMENT FOR METHOD SELECTION ===
# This allows running baseline or our algorithm from same script

parser.add_argument('--method', type=str, default='ours',
                    choices=['baseline', 'ours'],
                    help='Method to use: baseline (original) or ours (injected)')

# === STEP 3: DATA LOADING - DO NOT MODIFY! ===
# Keep baseline's data loading exactly as-is
#
# train_loader = baseline_data_loader(...) ← UNCHANGED
# test_loader = baseline_test_loader(...) ← UNCHANGED

# === STEP 4: MODEL CREATION - DO NOT MODIFY! ===
# Keep baseline's model creation exactly as-is
#
# model = BaselineModel(...) ← UNCHANGED
# model = model.to(device) ← UNCHANGED

# === STEP 5: OPTIMIZER - CONDITIONAL REPLACEMENT ===
# This is the ONLY training component that changes

if args.method == 'ours':
    # Use our algorithm
    optimizer = get_our_optimizer(model.parameters(), lr=args.lr, momentum=args.momentum)
else:
    # Use baseline's original optimizer (unchanged)
    optimizer = torch.optim.SGD(model.parameters(), lr=args.lr, momentum=args.momentum)

# === STEP 6: ADD METRIC TRACKING ===
# Initialize trackers (does not affect training)

metric_tracker = MetricTracker()
results_saver = ResultsSaver(
    output_path=f"{results_dir}/results.csv",
    method_name=args.method
)

# === STEP 7: TRAINING LOOP - MINIMAL MODIFICATION ===
# Only add metric computation at end of epoch

for epoch in range(args.epochs):
    # ---- BASELINE'S TRAINING CODE (UNCHANGED) ----
    for batch_idx, (data, target) in enumerate(train_loader):
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
    # ---- END OF BASELINE'S TRAINING CODE ----

    # ---- ADDED: Metric computation (does not affect training) ----
    psi = compute_psi(model, train_loader, device=device)
    metric_tracker.record(
        epoch=epoch,
        lr=args.lr,
        method=args.method,
        psi=psi,
        loss=avg_loss
    )

# === STEP 8: SAVE RESULTS AT END ===
# Save in comparison format

results_saver.add_from_tracker(
    tracker=metric_tracker,
    lr=args.lr,
    seed=args.seed
)
results_saver.save()
```

---

## What NOT to Modify

| Section | Why Preserve |
|---------|--------------|
| Data loading | Baseline's dataset is the controlled variable |
| Model creation | Baseline's model is the controlled variable |
| Loss function | Part of baseline's methodology |
| Learning rate schedule | Part of baseline's methodology |
| Data augmentation | Part of baseline's methodology |
| Batch size | Part of baseline's config |
| Number of epochs | Part of baseline's config |

---

## Verification Checklist

After modification, verify:

- [ ] **sys.path setup is added FIRST** (STEP 0)
- [ ] **NO data adapter import** - we use baseline's data
- [ ] **NO model adapter import** - we use baseline's model
- [ ] Baseline's data loading is UNCHANGED
- [ ] Baseline's model creation is UNCHANGED
- [ ] `--method` argument is added for comparison
- [ ] Optimizer is conditionally replaced (ours vs baseline)
- [ ] MetricTracker is recording psi values
- [ ] ResultsSaver is saving results

---

## Diff Example

```diff
# train.py modifications for Mode B comparison

+ import sys
+ import os
+ _baseline_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
+ sys.path.insert(0, _baseline_folder)
+ from adaptations.repo_name.algorithm_injection import get_our_optimizer
+ from adaptations.repo_name.metrics import compute_psi, MetricTracker
+ from adaptations.repo_name.results_saver import ResultsSaver

  parser.add_argument('--lr', type=float, default=0.01)
+ parser.add_argument('--method', type=str, default='ours', choices=['baseline', 'ours'])

  # Data loading - UNCHANGED
  train_loader = get_data_loader(...)

  # Model creation - UNCHANGED
  model = BaselineModel(...)

  # Optimizer - CONDITIONAL
- optimizer = torch.optim.SGD(model.parameters(), lr=args.lr)
+ if args.method == 'ours':
+ optimizer = get_our_optimizer(model.parameters(), lr=args.lr)
+ else:
+ optimizer = torch.optim.SGD(model.parameters(), lr=args.lr)

+ metric_tracker = MetricTracker()
+ results_saver = ResultsSaver(output_path=f"results.csv", method_name=args.method)

  for epoch in range(epochs):
      for batch in train_loader:
          optimizer.zero_grad()
          loss = criterion(model(batch), target)
          loss.backward()
          optimizer.step()
+
+ psi = compute_psi(model, train_loader, device=device)
+ metric_tracker.record(epoch=epoch, psi=psi, loss=loss.item())

+ results_saver.add_from_tracker(metric_tracker, lr=args.lr, seed=args.seed)
+ results_saver.save()
```

---

## Running Comparison

```bash
# Run baseline's original algorithm
python train.py --method baseline --lr 0.01 --seed 42

# Run our algorithm (injected)
python train.py --method ours --lr 0.01 --seed 42
```

Both runs use:
- Same model (baseline's)
- Same dataset (baseline's)
- Same hyperparameters (baseline's)
- Only the optimizer/algorithm differs

---

## Related Files

| File | Purpose |
|------|---------|
| `fair-comparison-principle.md` | Why we preserve baseline's environment |
| `algorithm-injection.md` | Our algorithm implementation |
| `adapter-metrics.md` | Metric tracking (psi computation) |
| `adapter-results.md` | Results saver for comparison format |
| `step-07-adaptation-coding.md` | Orchestration step |
