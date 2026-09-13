# Step 8 Validation Templates

> **Referenced by:** step-08-validation.md
> **Purpose:** Templates for validator prompt and validation log

---

## Validator Prompt Template

Use this template to construct the prompt for the baseline-validator-agent:

```markdown
You are the Baseline Validator Agent for Phase 5.

## Inputs
- baseline_folder: {baseline_folder}
- adaptations_folder: {baseline_folder}/adaptations/{repo_name}/
- clone_path: {baseline_folder}/baselines/{repo_name}/
- tasks_file: {baseline_folder}/05_tasks.yaml
- review_tasks: {review_tasks}
- conda_env_name: {checkpoint.adaptation.conda_env}
- conda_path: {checkpoint.conda_path}
- repo_name: {repo_name}

## CRITICAL: Conda Environment Setup (MUST DO FIRST!)

Before ANY Python/pip/pytest command, you MUST:

1. **Initialize conda and install pytest:**
```bash
source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} pip install pytest
```

2. **All subsequent Python commands MUST source conda first:**
```bash
source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} pytest tests/ -v
source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} python -c "import module"
```

**DO NOT use raw `pip install` or `pytest` without `source conda.sh && conda run -n {conda_env_name}`!**

## Your Mission

Execute validation phases in order:

1. **Phase 0: Test Gate** - Run pytest FIRST (IN CONDA ENV!)
   ```bash
   source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} pip install pytest
   source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} pytest {adaptations_folder}/tests/ -v --tb=short
   ```
   - If tests fail → STOP and return immediately

2. **Phase 1: Static** - Use Serena MCP
   - mcp__serena__list_dir for adaptations folder
   - mcp__serena__get_symbols_overview for each file
   - mcp__serena__find_symbol to verify Mode B symbols: OurOptimizer/OurAlgorithmWrapper, compute_psi, MetricTracker, ResultsSaver

3. **Phase 2: Runtime** - Use Bash (IN CONDA ENV!)
   ```bash
   source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} python -c "
   import sys, os
   sys.path.insert(0, os.path.abspath('{adaptations_folder}'))
   from algorithm_injection import get_our_optimizer
   from metrics import compute_psi, MetricTracker
   from results_saver import ResultsSaver
   print('All imports successful')
   "
   ```
   - Run 1-epoch integration test (both methods):
   ```bash
   source {conda_path}/etc/profile.d/conda.sh && cd {clone_path} && conda run -n {conda_env_name} python train.py --method baseline --epochs 1 --seed 0
   source {conda_path}/etc/profile.d/conda.sh && cd {clone_path} && conda run -n {conda_env_name} python train.py --method ours --epochs 1 --seed 0
   ```

4. **Phase 3: Error Analysis**
   - Map errors to task types
   - Return task status updates in output JSON

## Return Format

Return a JSON object:
{
  "validation_result": {
    "passed": true|false,
    "test_gate_passed": true|false,
    "static_passed": true|false,
    "runtime_passed": true|false,
    "passed_tasks": ["task-id-1"],
    "failed_tasks": [{
      "task_id": "task-id-2",
      "failure_phase": "test|static|runtime",
      "error_details": {
        "error_type": "ImportError",
        "file": "algorithm_injection.py",
        "line": 5,
        "traceback": "..."
      }
    }],
    "auto_fixes_applied": []
  }
}

## Full Instructions
Read and follow: .claude/agents/phase5-baseline/baseline-validator-agent.md
```

---

## Validation Log Template

Create `{baseline_folder}/validation_log.md`:

```markdown
# Adaptation Validation Log

## Date: {timestamp}
## Cycle: {coder_validator_cycles}

---

## Test Gate Results

| Test File | Tests | Passed | Failed |
|-----------|-------|--------|--------|
| test_algorithm_injection.py | {n} | {n} | {n} |
| test_metrics.py | {n} | {n} | {n} |
| test_results_saver.py | {n} | {n} | {n} |

**Test Gate:** {PASS/FAIL}

---

## Static Analysis Results

| File | Symbols Found | Expected | Status |
|------|---------------|----------|--------|
| algorithm_injection.py | {list} | OurOptimizer/OurAlgorithmWrapper, get_our_optimizer/wrap_baseline_optimizer | {OK/FAIL} |
| metrics.py | {list} | compute_psi, MetricTracker | {OK/FAIL} |
| results_saver.py | {list} | ResultsSaver | {OK/FAIL} |

---

## Runtime Validation Results

| Check | Status | Details |
|-------|--------|---------|
| Import Check | {PASS/FAIL} | {error if any} |
| 1-Epoch Test | {PASS/FAIL} | {error if any} |

---

## Task Status Updates

| Task | Previous | New | Reason |
|------|----------|-----|--------|
| {task_id} | review | done | Validation passed |
| {task_id} | review | todo | {error_type} |

---

## Next Action

{Proceed to Step 9 / Return to Step 7 for fixes}
```
