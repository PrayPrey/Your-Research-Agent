# Evaluation Protocol for H-E1
# lean-auto Baseline Measurement on miniF2F

**Version**: 1.0  
**Date**: 2026-08-20  
**Hypothesis**: h-e1 (EXISTENCE - lean-auto baseline)

---

## Protocol Overview

Measure lean-auto success rate on miniF2F Lean 4 test set (N=244) with 300s timeout per problem. Zero-shot evaluation (no premise selection). Parallel execution across 8 workers.

---

## Pre-Experiment Setup

### 1. Environment Preparation

**Lean Installation**:
```bash
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh -s -- -y
elan install leanprover/lean4:v4.15.0
elan default leanprover/lean4:v4.15.0
```

**miniF2F Setup**:
```bash
git clone https://github.com/google-deepmind/miniF2F
cd miniF2F
git checkout <alphaproof-eval-sha>  # Pin to AlphaProof version
lake build  # Build mathlib (~30 min)
```

**lean-auto Installation**:
```bash
git clone https://github.com/leanprover-community/lean-auto
cd lean-auto
git checkout <pinned-sha>  # Pin version for reproducibility
lake build
```

**Integration**:
Edit `miniF2F/lakefile.lean`:
```lean
require auto from git
  "https://github.com/leanprover-community/lean-auto" @ "<pinned-sha>"
```

Rebuild miniF2F:
```bash
cd miniF2F
lake update auto
lake build
```

### 2. Infrastructure Validation

**Test Lean Installation**:
```bash
lean --version  # Should show 4.15.0
```

**Test lean-auto**:
```lean
-- test_auto.lean
import Auto
set_option auto.native true
example : 2 + 2 = 4 := by auto
```

Run: `lean test_auto.lean` (should succeed)

**Test miniF2F Loading**:
```lean
import Minif2f.Test
#check Minif2f.amc12a_2000_p1  -- Should resolve
```

### 3. Pilot Run (N=20)

**Select Random Sample**:
```bash
# Extract first 20 theorems from Test.lean
head -n 100 Minif2f/Test.lean | grep "^theorem" | head -20 > pilot_problems.txt
```

**Run Pilot Evaluation**:
- Execute evaluation harness on 20 problems
- Expected: 2-5 solves (10-25%)
- Validate: logs captured, no crashes, tactic count extracted

**Gate Decision**:
- ✅ PASS: 2-5 solves, < 1 error, logs complete → Proceed to full run
- ❌ FAIL: Infrastructure issues → Debug before full run

---

## Evaluation Execution

### 4. Problem Loading

**Parse Test Set**:
```python
import re

def load_minif2f_problems(filepath):
    with open(filepath) as f:
        content = f.read()
    
    # Extract theorem statements
    pattern = r'theorem\s+(\w+)\s*:(.+?)(?=theorem|$)'
    problems = re.findall(pattern, content, re.DOTALL)
    
    return [
        {
            "id": name,
            "statement": stmt.strip(),
            "source": extract_source(name)  # AMC/AIME/IMO from name
        }
        for name, stmt in problems
    ]

problems = load_minif2f_problems("Minif2f/Test.lean")
assert len(problems) == 244
```

### 5. Worker Pool Setup

**Partition Problems**:
```python
n_workers = 8
chunk_size = 244 // n_workers  # 30 problems per worker
chunks = [
    problems[i:i+chunk_size]
    for i in range(0, 244, chunk_size)
]
# Worker 7 gets 34 problems (244 = 7*30 + 34)
```

**Spawn Workers**:
```python
from multiprocessing import Pool

def worker(problems):
    results = []
    for problem in problems:
        result = evaluate_single_problem(problem)
        results.append(result)
    return results

with Pool(8) as pool:
    all_results = pool.map(worker, chunks)
```

### 6. Single Problem Evaluation

**Evaluation Function**:
```python
import subprocess
import time
import json

def evaluate_single_problem(problem, timeout=300):
    # Create Lean script
    script = f"""
import Minif2f.Test
import Auto

set_option auto.smt false
set_option auto.tptp false
set_option auto.native true
set_option trace.auto true
set_option trace.auto.mono true

-- Target theorem: {problem['id']}
example : {problem['statement']} := by
  auto
"""
    
    # Write to temp file
    with open(f"/tmp/{problem['id']}.lean", "w") as f:
        f.write(script)
    
    # Execute with timeout
    start_time = time.time()
    try:
        proc = subprocess.run(
            ["lean", f"/tmp/{problem['id']}.lean"],
            capture_output=True,
            timeout=timeout,
            text=True
        )
        elapsed = time.time() - start_time
        
        # Parse outcome
        if proc.returncode == 0:
            outcome = "solved"
            tactic_count = extract_tactic_count(proc.stderr)
        else:
            outcome = "error"
            tactic_count = None
            
    except subprocess.TimeoutExpired:
        elapsed = timeout
        outcome = "timeout"
        tactic_count = None
    
    return {
        "problem_id": problem['id'],
        "source": problem['source'],
        "outcome": outcome,
        "time_s": elapsed,
        "tactic_count": tactic_count,
        "trace_log": proc.stderr if 'proc' in locals() else None
    }
```

### 7. Tactic Count Extraction

**Parse Trace Logs**:
```python
def extract_tactic_count(trace_log):
    """
    Count ATP solver invocations from trace.auto logs.
    
    Pattern: [auto.native] Invoking solver...
    """
    if not trace_log:
        return None
    
    # Count unique solver invocations
    invocations = re.findall(r'\[auto\.native\] Invoking', trace_log)
    
    if len(invocations) == 0:
        # Fallback: count monomorphization steps as proxy
        mono_steps = re.findall(r'\[auto\.mono\] Instantiating', trace_log)
        return len(mono_steps) if mono_steps else None
    
    return len(invocations)
```

**Validation** (on pilot):
- Manually inspect 5 solved problems
- Compare automated count with manual trace inspection
- Accept if 80%+ accuracy

### 8. Checkpointing

**Save Progress Every 10 Problems**:
```python
def worker_with_checkpoint(problems, worker_id):
    results = []
    checkpoint_freq = 10
    
    for i, problem in enumerate(problems):
        result = evaluate_single_problem(problem)
        results.append(result)
        
        if (i + 1) % checkpoint_freq == 0:
            save_checkpoint(worker_id, results)
    
    return results

def save_checkpoint(worker_id, results):
    with open(f"/data/checkpoints/worker_{worker_id}.json", "w") as f:
        json.dump({
            "worker_id": worker_id,
            "completed": len(results),
            "results": results
        }, f, indent=2)
```

**Recovery**:
```python
def load_checkpoint(worker_id):
    try:
        with open(f"/data/checkpoints/worker_{worker_id}.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"results": []}
```

---

## Post-Experiment Analysis

### 9. Result Aggregation

**Merge Worker Results**:
```python
import pandas as pd

# Load all worker results
all_results = []
for worker_id in range(8):
    checkpoint = load_checkpoint(worker_id)
    all_results.extend(checkpoint['results'])

assert len(all_results) == 244

# Create DataFrame
df = pd.DataFrame(all_results)
df.to_csv("/data/h-e1/results.csv", index=False)
```

### 10. Statistical Analysis

**Success Rate**:
```python
from scipy.stats import binomtest

n_solved = (df['outcome'] == 'solved').sum()
n_total = len(df)
success_rate = n_solved / n_total

# Wilson score confidence interval
ci = binomtest(n_solved, n_total).proportion_ci(confidence_level=0.95)

print(f"Success rate: {success_rate:.3f} [{ci.low:.3f}, {ci.high:.3f}]")
```

**Tactic Count Distribution**:
```python
solved_df = df[df['outcome'] == 'solved']

tactic_stats = {
    "mean": solved_df['tactic_count'].mean(),
    "median": solved_df['tactic_count'].median(),
    "std": solved_df['tactic_count'].std(),
    "cv": solved_df['tactic_count'].std() / solved_df['tactic_count'].mean(),
    "range": [solved_df['tactic_count'].min(), solved_df['tactic_count'].max()]
}
```

**Stratification by Source** (if available):
```python
if 'source' in df.columns:
    stratified = df.groupby('source')['outcome'].apply(
        lambda x: (x == 'solved').sum() / len(x)
    )
    print("Success rate by source:")
    print(stratified)
```

### 11. Summary Report Generation

**Create summary.json**:
```python
summary = {
    "hypothesis_id": "h-e1",
    "dataset": {
        "name": "miniF2F Lean 4 Test",
        "size": n_total
    },
    "results": {
        "success_rate": float(success_rate),
        "ci_95": [float(ci.low), float(ci.high)],
        "solved_count": int(n_solved),
        "timeout_count": int((df['outcome'] == 'timeout').sum()),
        "error_count": int((df['outcome'] == 'error').sum())
    },
    "tactic_count": tactic_stats,
    "execution": {
        "total_time_hours": df['time_s'].sum() / 3600,
        "mean_time_per_problem": df['time_s'].mean()
    }
}

with open("/data/h-e1/summary.json", "w") as f:
    json.dump(summary, f, indent=2)
```

---

## Validation Checks

### 12. Quality Gates

**Gate 1: Completeness**
- [ ] All 244 problems evaluated (no missing data)
- [ ] All results logged (problem_id, outcome, time_s)
- [ ] Checkpoints consistent (sum of worker results = 244)

**Gate 2: Error Rate**
- [ ] Error count < 12 (5% of 244)
- [ ] No systematic errors (not all from one source/worker)

**Gate 3: Tactic Count Validity**
- [ ] Tactic count captured for ≥80% of solved problems
- [ ] CV < 100% (variance not excessive)
- [ ] Manual validation on pilot subset matches automated extraction

**Gate 4: Reproducibility**
- [ ] Rerun 24 problems (10% random sample)
- [ ] 100% match on deterministic outcomes
- [ ] (Lean is deterministic; different outcomes = bug)

### 13. Hypothesis Validation

**Gate Type: MUST_WORK**

**Success Criteria**:
- Success rate in [10%, 25%] range
- Error rate < 5%
- Tactic count distribution captured (for H-C1)

**Decision Rules**:
- ✅ PASS: 10% ≤ success_rate ≤ 25% AND error < 5% → Foundation established
- ⚠️ REVISE: success_rate < 10% OR > 25% → Update predictions for H-M1/M2/M3
- ❌ FAIL: error ≥ 10% OR infrastructure unstable → Fix before proceeding

---

## Troubleshooting

### Common Issues

**Issue 1: Lean REPL Crash**
- Symptom: Worker terminates mid-execution
- Diagnosis: Check OOM (memory > 16GB per worker)
- Fix: Reduce concurrent workers OR increase memory

**Issue 2: lean-auto Timeout Ineffective**
- Symptom: Problems run beyond 300s
- Diagnosis: Internal timeout not enforced
- Fix: Use OS-level timeout (subprocess.run with timeout param)

**Issue 3: Tactic Count Extraction Fails**
- Symptom: tactic_count = None for all solved problems
- Diagnosis: Trace logs not captured OR pattern mismatch
- Fix: Verify `set_option trace.auto true` OR use fallback proxy

**Issue 4: High Error Rate (> 10%)**
- Symptom: Many problems result in "error" outcome
- Diagnosis: Check error messages (type-checking vs ATP crash)
- Fix: If type-checking: lean-auto bug, report upstream
       If ATP crash: Try alternative backend OR skip ATP features

---

## Data Archival

### 14. Output Files

**Directory Structure**:
```
/data/h-e1/
├── raw_logs/
│   ├── problem_test_001_trace.txt
│   ├── problem_test_002_trace.txt
│   └── ...
├── checkpoints/
│   ├── worker_0.json
│   ├── worker_1.json
│   └── ...
├── results.csv
├── summary.json
└── evaluation_report.md
```

**Compression**:
- Compress raw_logs/ (tar.gz)
- Keep results.csv and summary.json uncompressed
- Archive checkpoints/ after successful completion

**Version Control**:
- Commit summary.json and results.csv to git
- Store raw_logs.tar.gz in DVC or S3
- Document git SHA for Lean/lean-auto/miniF2F in README

---

## Timeline

**Total Duration**: 1 week (7 days)

| Day | Task | Duration |
|-----|------|----------|
| 1-2 | Setup (Lean, miniF2F, lean-auto) | 16 hours |
| 3 | Pilot run + validation | 4 hours |
| 4 | Full evaluation (244 problems) | 3 hours |
| 5 | Analysis + summary | 4 hours |
| 6-7 | Report + archival | 8 hours |

**Critical Path**: Infrastructure setup (Days 1-2)

---

## References

- Experiment Brief: `experiment_brief.md`
- Dataset Spec: `dataset_spec.yaml`
- Implementation Notes: `implementation_notes.md`
