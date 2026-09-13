# Implementation Notes for H-E1
# lean-auto Baseline Measurement

**Hypothesis ID**: h-e1  
**Generated**: 2026-08-20  
**Status**: Experiment Design Complete, Ready for Phase 3

---

## Key Implementation Considerations

### 1. Dataset Access

**Repository**: google-deepmind/miniF2F  
**Branch**: Use AlphaProof evaluation version (post-v2 corrections)

**Critical Files**:
- `Minif2f/Test.lean` - Contains all 244 test theorems
- `lean-toolchain` - Specifies Lean version (should be 4.15.0+)
- `lakefile.lean` - Build configuration for mathlib dependencies

**Setup Commands**:
```bash
git clone https://github.com/google-deepmind/miniF2F
cd miniF2F
lake build  # Build mathlib dependencies (~10-30 min)
```

### 2. lean-auto Installation

**Repository**: leanprover-community/lean-auto  
**Compatibility**: Lean 4.15.0+

**Installation**:
```bash
git clone https://github.com/leanprover-community/lean-auto
cd lean-auto
lake build
```

**Integration with miniF2F**:
Add lean-auto as dependency in miniF2F's `lakefile.lean`:
```lean
require auto from git
  "https://github.com/leanprover-community/lean-auto" @ "main"
```

### 3. Evaluation Harness Architecture

**Design Pattern**: Parallel worker pool

```
Master Process
├── Load 244 theorem statements from Test.lean
├── Partition into 8 work queues (~30 problems each)
├── Spawn 8 worker processes
└── Aggregate results

Worker Process (×8)
├── For each assigned problem:
│   ├── Create isolated Lean environment
│   ├── Load theorem statement
│   ├── Invoke lean-auto with timeout
│   ├── Log outcome + metadata
│   └── Checkpoint progress
└── Return results to master
```

**Isolation Strategy**: Each problem gets fresh Lean REPL instance to avoid cross-contamination.

### 4. Timeout Implementation

**Mechanism**: OS-level process timeout (SIGTERM at 300s, SIGKILL at 310s)

**Rationale**: 
- lean-auto internal timeout may not be reliable for all ATP backends
- OS-level ensures hard deadline enforcement
- 10s grace period for cleanup

**Code Sketch**:
```python
import subprocess
import signal

def evaluate_problem(theorem_statement, timeout=300):
    proc = subprocess.Popen(
        ["lean", "--run", "evaluate.lean"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    try:
        stdout, stderr = proc.communicate(
            input=theorem_statement.encode(),
            timeout=timeout
        )
        return parse_result(stdout, stderr)
    except subprocess.TimeoutExpired:
        proc.kill()
        return {"outcome": "timeout"}
```

### 5. Tactic Count Extraction

**Challenge**: lean-auto doesn't directly expose tactic evaluation count

**Primary Method**: Parse trace logs
```lean
set_option trace.auto true
set_option trace.auto.mono true
```

Look for patterns in logs:
- `[auto.mono] Instantiating lemma X with args Y`
- `[auto.native] Invoking ATP solver`
- Count unique ATP invocations

**Fallback Method**: Proxy metrics
- Wall-clock time (assume ~30s per tactic evaluation)
- Proof term size (lines in generated proof)
- ATP backend invocation count from system logs

**Validation**: On pilot run (N=20), manually verify tactic count extraction for 5 solved problems.

### 6. Logging Schema

**Per-Problem JSON**:
```json
{
  "problem_id": "test_001",
  "source": "AMC",
  "statement": "theorem test_001 : ...",
  "outcome": "solved",
  "wall_clock_time": 12.3,
  "tactic_count": 8,
  "proof_term": "by auto using lemma1, lemma2",
  "proof_size": 156,
  "atp_backend": "Duper",
  "trace_log": "path/to/test_001_trace.txt"
}
```

**Aggregate CSV**:
```csv
problem_id,source,outcome,time_s,tactic_count,proof_size,atp_backend
test_001,AMC,solved,12.3,8,156,Duper
test_002,AIME,timeout,300.0,,,
```

### 7. Error Handling

**Categories**:
1. **Infrastructure Errors**: Lean REPL crash, OOM, disk full
   - Mitigation: Retry up to 3 times with fresh environment
   - If still fails: Log as "error" and continue

2. **Type-Checking Failures**: lean-auto produces invalid proof
   - Expected rate: ~1-2%
   - Log as "error", include type error message

3. **ATP Backend Crashes**: Z3/CVC5/Zipperposition crashes
   - lean-auto should handle gracefully, fallback to other backends
   - If all backends fail: Log as "error"

**Error Budget**: < 5% total errors (< 12 problems out of 244)

### 8. Checkpointing

**Frequency**: Every 10 problems completed per worker

**Checkpoint Format**:
```json
{
  "worker_id": 3,
  "problems_completed": 10,
  "results": [...]
}
```

**Recovery**: On restart, skip already-completed problems from checkpoint.

**Benefit**: If run crashes at 200/244 problems, only rerun 44, not all 244.

### 9. Pilot Run Protocol

**Before Full Run**:
1. Select 20 random problems from test set
2. Run evaluation harness
3. Validate:
   - No infrastructure crashes
   - Logs captured correctly
   - Tactic count extraction works
   - 2-5 problems solved (10-25% of 20)

**If Pilot Fails**:
- Debug infrastructure issues
- Verify lean-auto installation
- Check miniF2F build
- Fix before proceeding to full run

### 10. Resource Requirements

**Compute**:
- 64 CPU cores (8 workers × 8 cores each)
- 128GB RAM (8 workers × 16GB each)
- 50GB disk (miniF2F + mathlib + logs)

**Time**:
- Full run: 2-3 hours
- Pilot run: 10-15 minutes
- Infrastructure setup: 1-2 hours (one-time)

**Cost Estimate** (AWS EC2 c5ad.16xlarge):
- Instance: $2.464/hour
- Full experiment: ~$8 (setup + pilot + full run)

### 11. Reproducibility Checklist

**Version Pinning**:
- [ ] Lean version: 4.15.0 (exact)
- [ ] lean-auto: git SHA or release tag
- [ ] miniF2F: git SHA (AlphaProof fork)
- [ ] mathlib: version from miniF2F's lean-toolchain

**Code Archive**:
- [ ] Evaluation harness code committed to git
- [ ] Configuration files (dataset_spec.yaml, etc.)
- [ ] Launch scripts and Dockerfiles (if applicable)

**Data Archive**:
- [ ] Raw logs (per-problem JSON)
- [ ] Aggregated results (CSV + summary.json)
- [ ] Trace logs (compressed, for debugging)

### 12. Known Limitations

**Limitation 1**: Stratification metadata may be incomplete
- **Impact**: Can only report aggregate success rate, not AMC/AIME/IMO breakdown
- **Mitigation**: Extract source from filenames (e.g., `minif2f_amc_001`)
- **Fallback**: Report aggregate results only

**Limitation 2**: Tactic count extraction heuristic
- **Impact**: May undercount if trace logs incomplete
- **Mitigation**: Validate on pilot run, use fallback proxy if needed
- **Risk**: Medium (affects H-C1 budget setting)

**Limitation 3**: lean-auto version in active development
- **Impact**: Behavior may change between versions
- **Mitigation**: Pin exact git SHA, document in reproducibility checklist
- **Risk**: Low (affects reproducibility, not validity)

### 13. Success Criteria for Phase 3

**Inputs to PRD**:
- [x] Dataset specification complete (dataset_spec.yaml)
- [x] Baseline configuration defined (lean-auto settings)
- [x] Metrics clearly specified (success rate, tactic count, solve time)
- [x] Evaluation protocol documented (timeout, logging, checkpointing)

**Outputs for Phase 4**:
- [ ] Evaluation harness implementation (Python/Lean code)
- [ ] Infrastructure setup scripts (Docker, setup.sh)
- [ ] Pilot run validation (N=20, 2-5 solves)
- [ ] Full run results (N=244, success rate measured)

**Gate for Phase 5**:
- [ ] Baseline success rate in 10-25% range
- [ ] Tactic count distribution captured (CV < 100%)
- [ ] Error rate < 5%
- [ ] Results reproducible (rerun 10% subset)

---

## Next Steps (Phase 3)

1. **PRD Generation**: Translate experiment brief into product requirements
2. **Architecture Design**: Specify evaluation harness components
3. **Complexity Assessment**: Estimate implementation effort (person-days)
4. **PRP Creation**: Step-by-step implementation plan with validation gates
5. **Archon Task Creation**: Link to Archon project for tracking

**Estimated Timeline**: Phase 3 (1 week) → Phase 4 (1 week) → Baseline measured

---

## References

- Experiment Brief: `experiment_brief.md`
- Dataset Spec: `dataset_spec.yaml`
- Phase 2B Verification Plan: `../02b_verification_plan.md`
- Archon Task: b1cf534c-c7ff-48e5-a432-1d260d9ec129
