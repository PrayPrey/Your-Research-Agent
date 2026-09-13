# Evaluation Protocol: h-m1 (NL Hint Ablation)

**Generated**: 2026-08-20T04:17:00Z  
**Hypothesis**: h-m1 (NL Hint Ablation)  
**Dataset**: miniF2F-v2c (244 test problems)  
**Prover**: LeanCopilot (ReProver model)

---

## Overview

This protocol defines step-by-step evaluation procedures for testing h-m1:
- **Condition 1**: Baseline (NL-Intact) — Original miniF2F-v2c with docstrings/comments
- **Condition 2**: Ablated (NL-Removed) — Preprocessed Lean files with NL stripped

**Key Requirement**: Pilot validation (20 problems) BEFORE full run to verify ablation feasibility

---

## Phase 1: Setup and Dataset Preparation

### 1.1 Software Installation

```bash
# Install Lean 4.17.0
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
elan install leanprover/lean4:v4.17.0
elan default leanprover/lean4:v4.17.0

# Clone LeanCopilot
git clone https://github.com/lean-dojo/LeanCopilot.git
cd LeanCopilot
lake build

# Install Python dependencies
pip install datasets transformers torch numpy scipy matplotlib
```

### 1.2 Dataset Download

```python
from datasets import load_dataset

# Load miniF2F-v2c from HuggingFace
ds = load_dataset("roozbeh-yz/miniF2F_v2", "v2c")
test_set = ds["test"]  # 244 problems

# Verify schema
print(test_set.features)
# Expected: formal_statement (str), informal_statement (str), ...
print(f"Total problems: {len(test_set)}")  # Should be 244
```

### 1.3 NL Ablation Preprocessing

**Create `preprocess.py`**:

```python
import re
from typing import List, Dict

def strip_nl_hints(lean_code: str) -> str:
    """Remove docstrings and comments from Lean 4 code."""
    # Strip /--! docstrings -/
    lean_code = re.sub(r'/--!.*?-/', '', lean_code, flags=re.DOTALL)
    # Strip -- inline comments
    lean_code = re.sub(r'--[^\n]*', '', lean_code)
    return lean_code.strip()

def generate_lean_file(problems: List[Dict], output_path: str, ablate: bool = False):
    """Generate .lean file from problem list."""
    with open(output_path, 'w') as f:
        for i, prob in enumerate(problems):
            lean_code = prob['formal_statement']
            if ablate:
                lean_code = strip_nl_hints(lean_code)
            f.write(f"-- Problem {i+1}\n")
            f.write(lean_code)
            f.write("\n\n")
```

---

## Phase 2: Pilot Validation (20 Problems)

### 2.1 Sample Pilot Dataset

```python
import random

# Sample 20 problems randomly (seed for reproducibility)
random.seed(42)
pilot_indices = random.sample(range(len(test_set)), 20)
pilot_problems = [test_set[i] for i in pilot_indices]

# Generate pilot files
generate_lean_file(pilot_problems, "Pilot_Baseline.lean", ablate=False)
generate_lean_file(pilot_problems, "Pilot_Ablated.lean", ablate=True)
```

### 2.2 Type-Check Validation

```bash
# Verify both files compile
cd LeanCopilot
lake build ../Pilot_Baseline.lean  # Should succeed
lake build ../Pilot_Ablated.lean   # Check for errors

# Count errors
lake build ../Pilot_Ablated.lean 2>&1 | grep -c "error"
# PASS: ≤3 errors
# FAIL: >3 errors → escalate fallback
```

### 2.3 Pilot Evaluation

**Run LeanCopilot on pilot problems**:

```bash
# Baseline condition
python evaluate_leancopilot.py \
  --dataset Pilot_Baseline.lean \
  --output pilot_baseline_results.jsonl \
  --budget 32 \
  --timeout 300

# Ablated condition
python evaluate_leancopilot.py \
  --dataset Pilot_Ablated.lean \
  --output pilot_ablated_results.jsonl \
  --budget 32 \
  --timeout 300
```

### 2.4 Go/No-Go Decision

```python
import json

# Load results
with open("pilot_baseline_results.jsonl") as f:
    baseline = [json.loads(line) for line in f]
with open("pilot_ablated_results.jsonl") as f:
    ablated = [json.loads(line) for line in f]

# Compute success rates
baseline_success = sum(p['success'] for p in baseline) / len(baseline)
ablated_success = sum(p['success'] for p in ablated) / len(ablated)
delta = baseline_success - ablated_success

print(f"Pilot Δ: {delta:.2%}")

# Go/No-Go
if delta >= 0.05:
    print("✅ GO: Proceed to full evaluation")
else:
    print("❌ NO-GO: Δ < 5%, escalate fallback")
```

---

## Phase 3: Full Dataset Evaluation

**Only proceed if pilot passed Go/No-Go criteria**

### 3.1 Generate Full Datasets

```python
# Generate full .lean files (244 problems)
generate_lean_file(test_set, "MiniF2F_v2c_Test.lean", ablate=False)
generate_lean_file(test_set, "MiniF2F_v2c_Test_NoNL.lean", ablate=True)
```

### 3.2 Verify Compilation

```bash
lake build MiniF2F_v2c_Test.lean
lake build MiniF2F_v2c_Test_NoNL.lean
# Both must compile with 0 errors
```

### 3.3 Parallel Evaluation Harness

**Create `evaluate_leancopilot.py`** (simplified example):

```python
import subprocess
import json
import time
from multiprocessing import Pool

def evaluate_problem(args):
    problem_id, lean_code, budget, timeout = args
    
    # Write temporary .lean file
    with open(f"temp_{problem_id}.lean", 'w') as f:
        f.write(lean_code)
    
    start_time = time.time()
    try:
        # Run LeanCopilot search_proof
        result = subprocess.run(
            ["lake", "env", "lean", f"temp_{problem_id}.lean"],
            timeout=timeout,
            capture_output=True,
            text=True
        )
        wall_time = time.time() - start_time
        success = result.returncode == 0
        error_type = None if success else "proof_failed"
        
    except subprocess.TimeoutExpired:
        wall_time = timeout
        success = False
        error_type = "timeout"
    
    return {
        "problem_id": problem_id,
        "success": success,
        "wall_time": wall_time,
        "error_type": error_type
    }

# Parallel execution
with Pool(8) as pool:
    results = pool.map(evaluate_problem, problem_args)

# Save results
with open("results.jsonl", 'w') as f:
    for r in results:
        f.write(json.dumps(r) + "\n")
```

### 3.4 Run Full Evaluation

```bash
# Baseline condition (NL-Intact)
python evaluate_leancopilot.py \
  --dataset MiniF2F_v2c_Test.lean \
  --output baseline_results.jsonl \
  --budget 32 \
  --timeout 300 \
  --workers 8

# Ablated condition (NL-Removed)
python evaluate_leancopilot.py \
  --dataset MiniF2F_v2c_Test_NoNL.lean \
  --output ablated_results.jsonl \
  --budget 32 \
  --timeout 300 \
  --workers 8
```

**Estimated Runtime**: 244 problems × 2 conditions × 300s ÷ 8 workers = ~41 hours

---

## Phase 4: Statistical Analysis

### 4.1 Success Rate Comparison

```python
import json
import numpy as np
from scipy.stats import mcnemar
from scipy.stats import bootstrap

# Load results
with open("baseline_results.jsonl") as f:
    baseline = [json.loads(line) for line in f]
with open("ablated_results.jsonl") as f:
    ablated = [json.loads(line) for line in f]

# Compute success rates
baseline_success = [p['success'] for p in baseline]
ablated_success = [p['success'] for p in ablated]

rate_baseline = sum(baseline_success) / len(baseline_success)
rate_ablated = sum(ablated_success) / len(ablated_success)
delta = rate_baseline - rate_ablated

print(f"Baseline success: {rate_baseline:.2%}")
print(f"Ablated success: {rate_ablated:.2%}")
print(f"Delta: {delta:.2%}")
```

### 4.2 McNemar's Test (Paired Proportions)

```python
# Build contingency table
# Rows: Baseline (success/fail), Cols: Ablated (success/fail)
both_success = sum(b and a for b, a in zip(baseline_success, ablated_success))
baseline_only = sum(b and not a for b, a in zip(baseline_success, ablated_success))
ablated_only = sum(not b and a for b, a in zip(baseline_success, ablated_success))
both_fail = sum(not b and not a for b, a in zip(baseline_success, ablated_success))

contingency = [[both_success, baseline_only],
               [ablated_only, both_fail]]

# McNemar's test
result = mcnemar(contingency, exact=False)
print(f"McNemar's χ² = {result.statistic:.3f}, p = {result.pvalue:.4f}")
```

### 4.3 Bootstrap Confidence Interval

```python
def delta_statistic(baseline, ablated):
    return np.mean(baseline) - np.mean(ablated)

# Bootstrap with 10,000 resamples
rng = np.random.default_rng(seed=42)
res = bootstrap(
    (np.array(baseline_success), np.array(ablated_success)),
    delta_statistic,
    n_resamples=10000,
    confidence_level=0.95,
    random_state=rng
)

print(f"95% CI: [{res.confidence_interval.low:.2%}, {res.confidence_interval.high:.2%}]")
```

### 4.4 Gate Decision

```python
# Decision criteria
if delta >= 0.25 and result.pvalue < 0.05:
    verdict = "PASS"
    print("✅ h-m1 PASSED: NL mechanism confirmed (Δ ≥ 25%, p < 0.05)")
elif delta < 0.10 or result.pvalue >= 0.05:
    verdict = "FAIL"
    print("❌ h-m1 FAILED: Reject 60% NL contribution claim")
else:
    verdict = "INCONCLUSIVE"
    print("⚠️ h-m1 INCONCLUSIVE: Weaker effect than predicted (10% ≤ Δ < 25%)")

# Save verdict
with open("comparison_stats.json", 'w') as f:
    json.dump({
        "baseline_success_rate": rate_baseline,
        "ablated_success_rate": rate_ablated,
        "delta": delta,
        "mcnemar_statistic": result.statistic,
        "p_value": result.pvalue,
        "ci_95_low": res.confidence_interval.low,
        "ci_95_high": res.confidence_interval.high,
        "verdict": verdict
    }, f, indent=2)
```

---

## Phase 5: Reporting

### 5.1 Generate 04_validation.md

**Template**:

```markdown
# Phase 4 Validation Report: h-m1 (NL Hint Ablation)

## Results Summary

**Hypothesis**: h-m1 (NL hint removal drops LLM success by 25-35 pp)

**Primary Metric**: Success Rate Delta (Δ)
- Baseline (NL-Intact): XX.X%
- Ablated (NL-Removed): XX.X%
- **Δ = XX.X pp** (95% CI: [XX.X%, XX.X%])

**Statistical Test**: McNemar's test
- χ² = X.XXX, p = 0.XXXX

**Verdict**: PASS/FAIL/INCONCLUSIVE

## Gate Decision

[PASS/FAIL/INCONCLUSIVE explanation]

## Detailed Results

[Tables, stratified analysis if available]

## Visualizations

[Embed plots: success_rate_comparison.png, etc.]
```

### 5.2 Generate Visualizations

```python
import matplotlib.pyplot as plt

# Bar chart: Success rate by condition
plt.figure(figsize=(8, 6))
plt.bar(["Baseline\n(NL-Intact)", "Ablated\n(NL-Removed)"], 
        [rate_baseline, rate_ablated], 
        color=['steelblue', 'coral'])
plt.ylabel("Success Rate")
plt.title("h-m1: NL Hint Ablation Effect")
plt.ylim(0, 1)
plt.axhline(y=rate_baseline, color='steelblue', linestyle='--', alpha=0.5)
plt.savefig("success_rate_comparison.png", dpi=300)

# Scatter: Per-problem success (Baseline vs Ablated)
plt.figure(figsize=(8, 8))
plt.scatter(baseline_success, ablated_success, alpha=0.5)
plt.xlabel("Baseline Success")
plt.ylabel("Ablated Success")
plt.title("Per-Problem Success Comparison")
plt.xlim(-0.1, 1.1)
plt.ylim(-0.1, 1.1)
plt.plot([0, 1], [0, 1], 'k--', alpha=0.3)
plt.savefig("per_problem_scatter.png", dpi=300)
```

---

## Deliverables Checklist

- [ ] `Pilot_Baseline.lean` (20 problems)
- [ ] `Pilot_Ablated.lean` (20 problems, NL stripped)
- [ ] `pilot_baseline_results.jsonl` (20 rows)
- [ ] `pilot_ablated_results.jsonl` (20 rows)
- [ ] Pilot Go/No-Go decision documented
- [ ] `MiniF2F_v2c_Test.lean` (244 problems, original)
- [ ] `MiniF2F_v2c_Test_NoNL.lean` (244 problems, NL stripped)
- [ ] `baseline_results.jsonl` (244 rows)
- [ ] `ablated_results.jsonl` (244 rows)
- [ ] `comparison_stats.json` (Δ, p-value, CI, verdict)
- [ ] `04_validation.md` (full report)
- [ ] `success_rate_comparison.png`
- [ ] `per_problem_scatter.png`
- [ ] `delta_bootstrap_distribution.png`

---

## Troubleshooting

### Issue: Type-check failures after NL removal

**Diagnosis**: Check if comments contain semantic type information

**Solution**: 
1. Manually inspect 5 failed examples
2. IF comments are load-bearing → escalate to fallback (external docs only)
3. ELSE → refine regex patterns to preserve semantic comments

### Issue: Pilot Δ < 5%

**Diagnosis**: NL ablation may not affect this prover configuration

**Solution**:
1. Verify preprocessing worked (inspect ablated files)
2. Check if LeanCopilot uses docstrings (inspect model inputs)
3. IF ablation confirmed correct → report negative result (falsification)

### Issue: Evaluation timeout

**Runtime**: Each problem allowed 300s, but evaluation may stall

**Solution**:
1. Monitor worker processes (`htop`)
2. Kill stuck processes after 360s (300s + 60s buffer)
3. Mark as timeout in results.jsonl

---

## References

**miniF2F-v2c**: https://huggingface.co/datasets/roozbeh-yz/miniF2F_v2  
**LeanCopilot**: https://github.com/lean-dojo/LeanCopilot  
**McNemar's Test**: scipy.stats.mcnemar documentation
