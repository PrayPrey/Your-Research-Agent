# Implementation Notes for h-m1
# NL Hint Ablation Experiment

**Generated**: 2026-08-20T04:17:00Z  
**For**: Phase 3 Implementation Planning

---

## Quick Reference

**Hypothesis**: h-m1 (NL Hint Ablation)  
**Gate Type**: MUST_WORK  
**Predicted Effect**: Δ = 30% (65% baseline → 35% ablated)  
**Dataset**: miniF2F-v2c, 244 test problems  
**Evaluation Time**: ~41 hours (2 days)

---

## Critical Implementation Details

### 1. Dataset Access

**Source**: HuggingFace Dataset  
**Path**: `roozbeh-yz/miniF2F_v2`  
**Config**: `v2c` (competition-level)  
**Split**: `test` (244 problems)

```python
from datasets import load_dataset
ds = load_dataset("roozbeh-yz/miniF2F_v2", "v2c")
test_set = ds["test"]
# Schema: formal_statement (str), informal_statement (str), ...
```

### 2. NL Ablation Preprocessing

**Goal**: Remove natural language hints while preserving Lean type-checking

**Regex Patterns**:
```python
import re

def strip_nl_hints(lean_code: str) -> str:
    # Remove docstrings /--! ... -/
    lean_code = re.sub(r'/--!.*?-/', '', lean_code, flags=re.DOTALL)
    # Remove inline comments -- ...
    lean_code = re.sub(r'--[^\n]*', '', lean_code)
    return lean_code.strip()
```

**Validation**: Every ablated file MUST compile with `lake build`

### 3. Pilot Validation (MANDATORY)

**Before Full Run**: Test on 20 randomly sampled problems

**Go/No-Go Criteria**:
- ✅ PASS: ≤3 type-check failures AND Δ ≥ 5%
- ❌ FAIL: >3 type-check failures OR Δ < 5%
- Fallback: Pivot to external Mathlib docs removal (not inline comments)

**Pilot Script**:
```bash
# Sample 20 problems
python sample_pilot.py --n 20 --seed 42

# Generate ablated Lean file
python preprocess.py --input pilot.lean --output pilot_ablated.lean

# Verify compilation
lake build pilot_ablated.lean

# Run LeanCopilot evaluation on both
python evaluate.py --dataset pilot.lean --output pilot_baseline.jsonl
python evaluate.py --dataset pilot_ablated.lean --output pilot_ablated.jsonl

# Check Δ
python check_delta.py --baseline pilot_baseline.jsonl --ablated pilot_ablated.jsonl
```

### 4. LeanCopilot Configuration

**Prover**: LeanCopilot (https://github.com/lean-dojo/LeanCopilot)  
**Model**: ReProver (default, bundled)  
**Tactic**: `search_proof`  
**Sampling Budget**: @32 (32 tactic generations per problem)  
**Timeout**: 300 seconds per problem

**Lean Version**: 4.17.0 (consistency with miniF2F-v2c)

**LeanCopilot Invocation**:
```lean
import LeanCopilot

theorem problem_name ... := by
  search_proof
```

**Configuration Options** (if needed):
```lean
set_option leanCopilot.model "ReProver"
set_option leanCopilot.numSamples 32
set_option leanCopilot.timeout 300
```

### 5. Evaluation Harness

**Parallelization**: 8 workers (total ~41 hours → ~5 hours wall-clock)

**Per-Problem Logging**:
```json
{
  "problem_id": "test_001",
  "condition": "baseline",
  "success": true,
  "tactics_used": 8,
  "wall_time": 12.3,
  "error_type": null
}
```

**Output Files**:
- `baseline_results.jsonl` (244 rows)
- `ablated_results.jsonl` (244 rows)

### 6. Statistical Analysis

**Primary Test**: McNemar's test (paired proportions)
- H0: Δ = 0
- H1: Δ > 25%
- α = 0.05

**Confidence Interval**: Bootstrap with 10,000 resamples

**Decision Rules**:
- PASS: Δ ≥ 25% AND p < 0.05
- FAIL: Δ < 10% OR p ≥ 0.05
- INCONCLUSIVE: 10% ≤ Δ < 25%

---

## Infrastructure Requirements

### Compute
- **GPU**: 1× NVIDIA A5000 (24GB VRAM) or equivalent
- **CPU**: 32 cores (8 workers × 4 cores each)
- **RAM**: 128GB (LeanCopilot + Lean elaborator)
- **Storage**: 50GB (dataset, models, logs)

### Software Stack
```yaml
dependencies:
  - lean: 4.17.0
  - mathlib: latest compatible with miniF2F-v2c
  - leancopilot: main branch
  - reprover: bundled with LeanCopilot
  - python: 3.9+
  - datasets: latest (HuggingFace)
  - numpy, scipy, matplotlib: for analysis
```

### Estimated Runtime
- **Pilot**: 20 problems × 2 conditions × 300s ÷ 8 workers = 2.5 hours
- **Full**: 244 problems × 2 conditions × 300s ÷ 8 workers = 41 hours
- **Analysis**: 1 hour (statistical tests, plots)
- **Total**: 2 days (with pilot)

---

## Risk Mitigation

### Risk 1: Type-Check Failures After NL Removal
**Probability**: 30%  
**Mitigation**: 20-problem pilot BEFORE full run  
**Fallback**: Pivot to external docs removal (Mathlib informal docs, not inline comments)

### Risk 2: No Measurable Effect (Δ < 10%)
**Probability**: 20%  
**Impact**: Falsifies NL hypothesis  
**Action**: Accept negative result, report in 04_validation.md, revise main hypothesis

### Risk 3: Confound (NL Removal Also Removes Type Info)
**Probability**: 40%  
**Diagnostic**: Manual inspection of 20 ablated examples  
**Check**: IF type signatures preserved AND success drops → NL effect is real

### Risk 4: GPU Availability
**Probability**: 30%  
**Mitigation**: Queue overnight, request dedicated allocation

---

## Expected Deliverables

### Dataset Artifacts
1. `MiniF2F_v2c_Test.lean` (original, 244 problems)
2. `MiniF2F_v2c_Test_NoNL.lean` (ablated, 244 problems)
3. `ablation_pilot_results.json` (20-problem validation)

### Evaluation Results
1. `baseline_results.jsonl` (244 rows: problem_id, success, tactics, time)
2. `ablated_results.jsonl` (244 rows: same schema)
3. `comparison_stats.json` (Δ, p-value, 95% CI, stratified results if available)

### Analysis Report
1. `04_validation.md`:
   - Success rates: Baseline vs Ablated
   - McNemar's test results
   - Bootstrap 95% CI
   - Stratification by source (AMC/AIME/IMO) if metadata available
   - Falsification verdict: PASS/FAIL/INCONCLUSIVE
   - Gate decision for h-m1

### Visualizations
1. `success_rate_comparison.png` (bar chart)
2. `per_problem_scatter.png` (Baseline vs Ablated)
3. `delta_bootstrap_distribution.png` (histogram)

---

## Phase 3 Handoff Inputs

### PRD Requirements
- LeanCopilot integration (search_proof tactic)
- miniF2F-v2c dataset loading via HuggingFace
- NL ablation preprocessing module (regex-based)
- @32 sampling budget, 300s timeout configuration
- Parallel evaluation harness (8 workers)
- Statistical analysis pipeline (McNemar's, bootstrap CI)

### Architecture Components
1. **Dataset Loader**: HuggingFace → Lean files
2. **Preprocessor**: NL ablation (regex)
3. **Evaluator**: LeanCopilot harness (parallel)
4. **Analyzer**: Statistical tests + visualization

### PRP Complexity Assessment
**Tier 1 (LOW)**:
- Existing infrastructure: LeanCopilot, HuggingFace datasets
- Simple preprocessing: regex-based text manipulation
- Standard evaluation: off-the-shelf theorem prover
- Known dataset: widely-used benchmark

**Development Time**: 3-5 days (with pilot)

---

## Common Pitfalls to Avoid

1. **Don't skip pilot**: Type-check failures will block full run
2. **Don't use synthetic data**: miniF2F-v2c is real, curated benchmark
3. **Don't reduce sample size**: 244 is standard test set, provides statistical power
4. **Don't ignore variance**: Report CV alongside mean tactic count
5. **Don't forget verification**: All proofs must pass Lean kernel check
6. **Don't conflate conditions**: Keep baseline and ablated files separate, never merge

---

## Quick Checklist for Phase 3

- [ ] Install Lean 4.17.0 + Mathlib
- [ ] Clone LeanCopilot repository
- [ ] Download miniF2F-v2c via HuggingFace
- [ ] Implement NL ablation script (regex)
- [ ] Run 20-problem pilot (Go/No-Go decision)
- [ ] Generate full dataset (244 problems × 2 conditions)
- [ ] Verify both files compile (lake build)
- [ ] Implement parallel evaluation harness (8 workers)
- [ ] Run full evaluation (~41 hours)
- [ ] Statistical analysis (McNemar's, bootstrap)
- [ ] Generate report and visualizations
- [ ] Gate decision: PASS/FAIL/INCONCLUSIVE

---

## References

**Dataset**: https://huggingface.co/datasets/roozbeh-yz/miniF2F_v2  
**LeanCopilot**: https://github.com/lean-dojo/LeanCopilot  
**miniF2F-v2 Paper**: https://arxiv.org/abs/2511.03108  
**LeanCopilot Paper**: https://arxiv.org/abs/2404.12534
