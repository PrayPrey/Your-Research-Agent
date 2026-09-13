# Validation Protocol: H-E1 Coverage Audit

**Hypothesis:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Date:** 2026-08-20

---

## Validation Objective

Determine whether ModelZooDataset, SANE, and ViTModelZoo collectively provide sufficient architecture-task cell coverage for statistically valid hierarchical VAE experiments.

**Primary Metric:** Percentage of architecture-task cells containing ≥30 models  
**Threshold:** ≥70% for PASS

---

## Validation Steps

### Step 1: Data Collection Validation

**Objective:** Verify all datasets downloaded and accessible.

**Protocol:**
```bash
# Check ModelZooDataset
test -d data/modelzoo/mnist && echo "MNIST: OK" || echo "MNIST: MISSING"
test -d data/modelzoo/cifar10 && echo "CIFAR10: OK" || echo "CIFAR10: MISSING"
test -d data/modelzoo/cifar100 && echo "CIFAR100: OK" || echo "CIFAR100: MISSING"

# Check SANE
test -d data/sane/SANE && echo "SANE: OK" || echo "SANE: MISSING"

# Check ViT
test -f data/vit_zoo/manifest.json && echo "ViT: OK" || echo "ViT: MISSING"

# Check metadata files
test -f data/zoo_metadata.parquet && echo "Metadata: OK" || echo "Metadata: MISSING"
```

**Success Criteria:**
- All three dataset sources present
- Unified metadata file exists
- File sizes reasonable (ModelZooDataset >100GB, metadata >10MB)

---

### Step 2: Metadata Quality Validation

**Objective:** Verify metadata accuracy and completeness.

**Protocol:**
```python
import pandas as pd

df = pd.read_parquet("data/zoo_metadata.parquet")

# Check 1: Required fields present
required_fields = ['model_id', 'architecture', 'task', 'source']
missing_counts = df[required_fields].isnull().sum()
print("Missing field counts:")
print(missing_counts)

# Success: <1% missing values
missing_rate = missing_counts.sum() / (len(df) * len(required_fields)) * 100
assert missing_rate < 1.0, f"High missing rate: {missing_rate:.2f}%"

# Check 2: Architecture-task compatibility
incompatible = [
    ('ResNet', 'MNIST'),
    ('ResNet', 'FMNIST'),
    ('ResNet', 'USPS'),
]
for arch, task in incompatible:
    count = len(df[(df['architecture'] == arch) & (df['task'] == task)])
    assert count == 0, f"Invalid {arch}-{task} pair found: {count} models"

# Check 3: Unique model IDs
assert df['model_id'].nunique() == len(df), "Duplicate model IDs detected"

print("Metadata quality: PASS")
```

**Success Criteria:**
- <1% missing required fields
- Zero incompatible architecture-task pairs
- 100% unique model IDs

---

### Step 3: Coverage Matrix Validation

**Objective:** Calculate and validate coverage percentage.

**Protocol:**
```python
import pandas as pd

df = pd.read_parquet("data/zoo_metadata.parquet")

# Generate coverage matrix
coverage_matrix = df.groupby(['architecture', 'task']).size().unstack(fill_value=0)

# Calculate coverage
sufficient_mask = coverage_matrix >= 30
total_cells = coverage_matrix.size
sufficient_cells = sufficient_mask.sum().sum()
coverage_pct = sufficient_cells / total_cells * 100

print(f"Coverage: {coverage_pct:.1f}% ({sufficient_cells}/{total_cells} cells)")
print(f"Threshold: ≥70%")
print(f"Status: {'PASS' if coverage_pct >= 70 else 'PARTIAL' if coverage_pct >= 50 else 'FAIL'}")

# Save for gate decision
coverage_result = {
    'coverage_pct': coverage_pct,
    'sufficient_cells': int(sufficient_cells),
    'total_cells': int(total_cells),
    'threshold': 70.0,
    'status': 'PASS' if coverage_pct >= 70 else 'PARTIAL' if coverage_pct >= 50 else 'FAIL'
}

import json
json.dump(coverage_result, open("h-e1/coverage_result.json", "w"), indent=2)
```

**Success Criteria:**
- **PASS:** ≥70% of cells with ≥30 models
- **PARTIAL:** 50-70% of cells with ≥30 models
- **FAIL:** <50% of cells with ≥30 models

---

### Step 4: Critical Cell Validation

**Objective:** Verify critical architecture-task cells meet threshold.

**Protocol:**
```python
# Critical cells for downstream experiments
critical_cells = [
    ('CNN', 'CIFAR10'),
    ('CNN', 'MNIST'),
    ('ResNet', 'CIFAR100'),
    ('ResNet', 'TinyImageNet'),
]

critical_results = {}
all_pass = True

for arch, task in critical_cells:
    if arch in coverage_matrix.index and task in coverage_matrix.columns:
        count = coverage_matrix.loc[arch, task]
    else:
        count = 0
    
    status = "PASS" if count >= 30 else "FAIL"
    critical_results[f"{arch}-{task}"] = {
        'count': int(count),
        'threshold': 30,
        'status': status
    }
    
    if status == "FAIL":
        all_pass = False
    
    print(f"{arch}-{task}: {count} models [{status}]")

# Save results
json.dump(critical_results, open("h-e1/critical_cells.json", "w"), indent=2)

print(f"\nCritical cells: {'ALL PASS' if all_pass else 'SOME FAILED'}")
```

**Success Criteria:**
- **PRIMARY:** CNN-CIFAR10 ≥30 models
- **SECONDARY:** ResNet-CIFAR100 ≥30 models
- **TERTIARY:** At least 2 out of 4 critical cells ≥30 models

---

### Step 5: Statistical Power Validation

**Objective:** Confirm n=30 threshold provides adequate bootstrap test power.

**Protocol:**
```python
from scipy.stats import bootstrap
import numpy as np

def wcss(data):
    """Within-cluster sum of squares."""
    return np.sum((data - np.mean(data))**2)

def estimate_power(n_samples=30, effect_size=0.5, trials=1000):
    """Estimate bootstrap test power via simulation."""
    detections = 0
    
    for _ in range(trials):
        # Simulate two groups with Cohen's d effect
        group_a = np.random.normal(0, 1, n_samples)
        group_b = np.random.normal(effect_size, 1, n_samples)
        
        # Bootstrap confidence intervals
        res_a = bootstrap((group_a,), wcss, n_resamples=100, random_state=None)
        res_b = bootstrap((group_b,), wcss, n_resamples=100, random_state=None)
        
        # Check for separation at α=0.01
        if res_a.confidence_interval.high < res_b.confidence_interval.low:
            detections += 1
    
    power = detections / trials
    return power

# Test n=30 threshold
power_30 = estimate_power(n_samples=30, effect_size=0.5, trials=1000)
print(f"Bootstrap power (n=30, d=0.5): {power_30:.3f}")
print(f"Threshold: ≥0.80")
print(f"Status: {'PASS' if power_30 >= 0.80 else 'FAIL'}")

# Save result
power_result = {
    'n_samples': 30,
    'effect_size': 0.5,
    'power': power_30,
    'threshold': 0.80,
    'status': 'PASS' if power_30 >= 0.80 else 'FAIL'
}
json.dump(power_result, open("h-e1/power_validation.json", "w"), indent=2)
```

**Success Criteria:**
- Bootstrap power ≥0.80 for n=30, Cohen's d=0.5
- Justifies ≥30 models threshold for WCSS clustering test

---

### Step 6: Sparse Cell Analysis

**Objective:** Identify and document sparse cells for robustness testing.

**Protocol:**
```python
# Identify sparse cells (<30 models)
sparse_cells = coverage_matrix[coverage_matrix < 30].stack()

print(f"Sparse cells (<30 models): {len(sparse_cells)}")
print("\nSparse cell breakdown:")
print(sparse_cells.sort_values())

# Categorize by density
density_categories = {
    'dense': coverage_matrix[coverage_matrix >= 100].stack(),
    'sufficient': coverage_matrix[(coverage_matrix >= 30) & (coverage_matrix < 100)].stack(),
    'sparse': sparse_cells
}

for category, cells in density_categories.items():
    print(f"\n{category.upper()}: {len(cells)} cells")

# Save for natural experiment design
sparse_analysis = {
    'sparse_count': len(sparse_cells),
    'sparse_cells': [(idx[0], idx[1], int(count)) for idx, count in sparse_cells.items()],
    'robustness_test': 'Treat sparse cells as natural experiment for generalization'
}
json.dump(sparse_analysis, open("h-e1/sparse_analysis.json", "w"), indent=2)
```

**Success Criteria:**
- Sparse cells identified and documented
- Natural experiment plan created for robustness testing

---

## Gate Decision Logic

```python
def gate_decision(coverage_pct, critical_cells_pass, power_pass):
    """Determine gate decision based on validation results."""
    
    if coverage_pct >= 70 and critical_cells_pass and power_pass:
        decision = "PASS"
        action = "Proceed to Phase 1 (H-M-integrated CKA feasibility gate)"
        
    elif coverage_pct >= 50 and critical_cells_pass:
        decision = "PARTIAL"
        action = "Proceed with scope reduction (restrict to well-covered architectures)"
        
    elif coverage_pct < 50 or not critical_cells_pass:
        decision = "FAIL"
        action = "ABORT Phase 1 (insufficient data for statistical validity)"
        
    else:
        decision = "REVIEW"
        action = "Manual review required (edge case)"
    
    return {
        'decision': decision,
        'action': action,
        'coverage_pct': coverage_pct,
        'critical_cells_pass': critical_cells_pass,
        'power_pass': power_pass
    }

# Load validation results
coverage_result = json.load(open("h-e1/coverage_result.json"))
critical_result = json.load(open("h-e1/critical_cells.json"))
power_result = json.load(open("h-e1/power_validation.json"))

# Make decision
critical_pass = all(v['status'] == 'PASS' for v in critical_result.values())
decision = gate_decision(
    coverage_pct=coverage_result['coverage_pct'],
    critical_cells_pass=critical_pass,
    power_pass=(power_result['status'] == 'PASS')
)

# Save decision
json.dump(decision, open("h-e1/gate_decision.json", "w"), indent=2)

print("\n" + "="*60)
print("GATE DECISION")
print("="*60)
print(f"Decision: {decision['decision']}")
print(f"Action: {decision['action']}")
print("="*60)
```

---

## Validation Report Template

```markdown
# H-E1 Validation Report

**Date:** 2026-08-20  
**Hypothesis:** h-e1 (Dataset Coverage Audit)  
**Gate Type:** MUST_WORK

---

## Summary

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Overall coverage | X% | ≥70% | PASS/PARTIAL/FAIL |
| Critical cells | X/4 | All ≥30 | PASS/FAIL |
| Metadata quality | X% errors | <5% | PASS/FAIL |
| Bootstrap power (n=30) | X | ≥0.80 | PASS/FAIL |

---

## Coverage Results

- **Total models:** X
- **Architecture families:** X (CNN, ResNet, ViT, MLP, RNN)
- **Task categories:** X (MNIST, CIFAR10, CIFAR100, ...)
- **Total cells:** X
- **Sufficient cells (≥30):** X (X%)
- **Sparse cells (<30):** X (X%)

---

## Critical Cells

| Cell | Count | Status |
|------|-------|--------|
| CNN-CIFAR10 | X | PASS/FAIL |
| CNN-MNIST | X | PASS/FAIL |
| ResNet-CIFAR100 | X | PASS/FAIL |
| ResNet-TinyImageNet | X | PASS/FAIL |

---

## Gate Decision

**Decision:** PASS / PARTIAL / FAIL

**Action:** [Gate decision action from logic above]

**Justification:** [Brief explanation of decision]

---

## Fallback Actions (if applicable)

- [ ] Scope reduction to [architectures]
- [ ] External augmentation for [cells]
- [ ] Natural experiment for sparse [cells]
- [ ] None (full coverage achieved)

---

## Next Steps

**If PASS:**
1. Proceed to Phase 1 (H-M-integrated)
2. Train architecture-specific encoders (NFN/UNF)
3. Run CKA feasibility gate

**If PARTIAL:**
1. Apply scope reduction
2. Update verification plan with reduced scope
3. Proceed to Phase 1 with caution

**If FAIL:**
1. Return to Phase 0 or Phase 2A-Dialogue
2. Options: (a) Collect additional data, (b) Reduce to homogeneous setting
```

---

## Validation Checklist

**Pre-execution:**
- [ ] Environment set up (conda env activated)
- [ ] Datasets downloaded (ModelZooDataset, SANE, ViT)
- [ ] Scripts ready (extract_*.py, coverage_audit.py)

**Execution:**
- [ ] Step 1: Data collection validated
- [ ] Step 2: Metadata quality validated
- [ ] Step 3: Coverage matrix generated
- [ ] Step 4: Critical cells validated
- [ ] Step 5: Bootstrap power validated
- [ ] Step 6: Sparse cells analyzed

**Post-execution:**
- [ ] Gate decision made
- [ ] Validation report generated
- [ ] Results saved to h-e1/ folder
- [ ] State updated in verification_state.yaml

---

## Success Criteria Summary

| Criterion | Type | Threshold |
|-----------|------|-----------|
| Overall coverage | PRIMARY | ≥70% cells with ≥30 models |
| Critical cells | SECONDARY | All 4 critical cells ≥30 models |
| Metadata quality | VALIDATION | <5% error rate |
| Bootstrap power | STATISTICAL | ≥0.80 power for n=30 |
| Architecture-task compatibility | QUALITY | 100% valid pairs |

**Gate passes if:** PRIMARY + SECONDARY + STATISTICAL met  
**Gate partial if:** 50-70% coverage + SECONDARY + STATISTICAL met  
**Gate fails if:** <50% coverage OR SECONDARY fails

---

**Validation Status:** Ready to execute  
**Estimated Duration:** 0.5 days (automated scripts)
