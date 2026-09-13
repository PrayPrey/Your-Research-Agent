# Fair Comparison Principle (Mode B)

> **Reference Guide for Phase 5 Baseline Comparison**
> Defines the principles and methodology for fair baseline comparison

---

## Core Principle

**We inject OUR ALGORITHM into BASELINE's environment.**

The ONLY difference between methods is the **ALGORITHM/METHODOLOGY** being compared.
Everything else (model, dataset, config) comes from the BASELINE repository.

---

## What We ARE Doing (Mode B)

| Component | Source | Description |
|-----------|--------|-------------|
| **Model Architecture** | BASELINE's model | Use baseline's existing model as-is |
| **Dataset** | BASELINE's dataset | Use baseline's dataset as-is |
| **Hyperparameters** | BASELINE's config | Use baseline's LR, epochs, batch_size, etc. |
| **Training Loop** | BASELINE's code | Minimal modification to baseline's training loop |
| **Algorithm (Baseline)** | BASELINE repo | Baseline's original algorithm |
| **Algorithm (Ours)** | OUR hypothesis | Inject our algorithm into baseline's training loop |

---

## What We Are NOT Doing

| Incorrect Approach | Why It's Wrong |
|-------------------|----------------|
| Replacing baseline's model with ours | Confounds algorithm vs architecture |
| Replacing baseline's dataset with ours | Confounds algorithm vs data distribution |
| Overriding baseline's hyperparameters | Confounds algorithm vs tuning |
| Implementing baseline from scratch | Loses baseline's optimizations and nuances |

---

## Why This Is Fair

1. **Baseline's Home Turf**
   - We test our algorithm in baseline's environment
   - Baseline has every advantage (their model, their data, their tuning)
   - If we still win, it's strong evidence our algorithm is better

2. **Isolation of Variables**
   - The ONLY variable is the algorithm/methodology
   - Model architecture is controlled (baseline's)
   - Data distribution is controlled (baseline's)
   - Hyperparameters are controlled (baseline's)

3. **Reproducibility**
   - Baseline repo is public on GitHub
   - Anyone can clone and verify our results
   - No hidden confounds from custom environments

4. **Academic Credibility**
   - Reviewers can't claim we "rigged" the environment
   - Demonstrates our algorithm generalizes to other setups
   - Shows robustness across different model/data combinations

---

## Algorithm Injection Strategy

When injecting our algorithm into baseline's code:

### 1. Identify Injection Points

```python
# Find where baseline creates optimizer
# Original: optimizer = SGD(model.parameters(), lr=lr)
# Inject: optimizer = OurOptimizer(model.parameters(), lr=lr)

# Find where baseline computes loss/backward
# Original: loss.backward()
# Inject: loss.backward(); our_algorithm_step(model)
```

### 2. Minimal Modification Principle

```python
# BEFORE (baseline's original code)
optimizer = torch.optim.SGD(model.parameters(), lr=args.lr)
for epoch in range(epochs):
    for batch in dataloader:
        loss = criterion(model(batch), targets)
        loss.backward()
        optimizer.step()

# AFTER (with our algorithm injected)
from youra_algorithm import OurOptimizer # Only import added
optimizer = OurOptimizer(model.parameters(), lr=args.lr) # Only optimizer changed
for epoch in range(epochs):
    for batch in dataloader:
        loss = criterion(model(batch), targets)
        loss.backward()
        optimizer.step() # Our algorithm handles the rest
```

### 3. Metric Injection (for comparison)

```python
# Add metric tracking without changing baseline logic
from youra_metrics import compute_psi, MetricTracker

tracker = MetricTracker()
# ... training loop ...
psi = compute_psi(model, dataloader)
tracker.log({"epoch": epoch, "psi": psi, "loss": loss.item()})
```

### 4. Results Saver (for comparison format)

```python
# Save results in standardized format for comparison
from youra_results import ResultsSaver

saver = ResultsSaver(output_path="results.csv", method_name="baseline_name")
saver.save_run(metrics=tracker.get_all())
```

---

## Boundaries: What to Modify vs Preserve

| Component | Modify? | Reason |
|-----------|---------|--------|
| Optimizer class | YES | This is our algorithm |
| Learning rate schedule | NO | Part of baseline's methodology |
| Model architecture | NO | Controlled variable |
| Dataset loading | NO | Controlled variable |
| Data augmentation | NO | Part of baseline's methodology |
| Loss function | NO | Part of baseline's methodology |
| Training loop structure | MINIMAL | Only inject our optimizer/metrics |
| Evaluation code | MINIMAL | Add our metrics alongside baseline's |

---

## Required Analysis Before Injection

### 1. README.md Analysis (MANDATORY)

Before injecting our algorithm, MUST read and understand:
- Model architecture description
- Dataset requirements and format
- Training procedure
- Expected results/benchmarks
- Dependencies and environment setup

### 2. Code Analysis (MANDATORY)

Use Serena MCP to understand:
- Where optimizer is created
- Where backward() is called
- Training loop structure
- How results are saved

### 3. Compatibility Check

Verify our algorithm can work with:
- Baseline's optimizer interface
- Baseline's gradient computation
- Baseline's model parameter structure

---

## Validation Checklist

Before running comparison experiments, verify:

- [ ] Baseline code runs unmodified (sanity check)
- [ ] Our algorithm is injected at correct location
- [ ] Baseline's model architecture is UNCHANGED
- [ ] Baseline's dataset loading is UNCHANGED
- [ ] Baseline's hyperparameters are UNCHANGED
- [ ] Only optimizer/algorithm component is replaced
- [ ] Metric tracking is added without affecting training
- [ ] Results are saved in comparison format

---

## Report Requirements

When generating comparison report, MUST include:

1. **Clear Statement of Fair Comparison**
   - State that baseline's environment was used
   - List what was preserved (model, data, config)
   - List what was changed (only algorithm)

2. **Baseline Documentation**
   - Link to original GitHub repository
   - Commit hash used
   - Any environment setup notes

3. **Injection Documentation**
   - Exactly what code was modified
   - Diff or CHANGES.md showing modifications
   - Verification that baseline still runs correctly

4. **Reproducibility Information**
   - Exact commands to run each method
   - Environment setup instructions
   - Random seeds used

---

## Common Mistakes to Avoid

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Replacing baseline's model | Invalid comparison | Use baseline's model as-is |
| Using different hyperparameters | Unfair advantage | Use baseline's exact config |
| Modifying data augmentation | Confounded results | Preserve baseline's data pipeline |
| Changing training epochs | Training budget confound | Use baseline's exact epochs |
| Adding regularization | Algorithm vs regularization confound | Only inject algorithm |

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────────┐
│ FAIR COMPARISON SETUP (Mode B) │
├─────────────────────────────────────────────────────────────────────┤
│ │
│ ┌───────────────────────────────────────────────────────────┐ │
│ │              BASELINE's ENVIRONMENT │    │
│ │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │    │
│ │  │ Baseline │  │ Baseline │  │ Baseline │        │ │
│ │  │ Model │  │ Dataset │  │ Config │        │ │
│ │  └─────────────┘ └─────────────┘ └─────────────┘ │    │
│ │                                                            │ │
│ │   ┌─────────────────────────────────────────────────┐ │    │
│ │   │ Training Loop │     │ │
│ │   │ │     │ │
│ │   │ ┌─────────────┐ ┌─────────────┐ │     │ │
│ │   │ │  Baseline │  VS │    OUR │          │ │    │
│ │   │ │  Algorithm │      │ Algorithm │ ← INJECT │ │    │
│ │   │ └─────────────┘ └─────────────┘ │     │ │
│ │   │ │     │ │
│ │   └─────────────────────────────────────────────────┘ │    │
│ │                                                            │ │
│ └───────────────────────────────────────────────────────────┘ │
│ │
│ ONLY DIFFERENCE: The algorithm/methodology being compared │
│ EVERYTHING ELSE: From baseline repository (model, data, config) │
│ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Related Files

| File | Purpose |
|------|---------|
| `step-04-evaluate.md` | Evaluates baseline environment suitability |
| `step-06-setup.md` | Sets up baseline environment, identifies injection points |
| `step-07-adaptation-coding.md` | Implements algorithm injection |
| `algorithm-injection.md` | Algorithm injection template |
| `adapter-metrics.md` | Metric tracking template |
| `adapter-results.md` | Results saver template |
| `adapter-training-script.md` | Training script modification guide |
