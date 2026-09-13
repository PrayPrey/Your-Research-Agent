---
title: "PRD: H-M2 Pylint/Mypy Coverage on HumanEval Baseline Failures — Mechanism Analysis"
hypothesis_id: h-m2
hypothesis_type: MECHANISM
phase: 3
date: "2026-08-05"
status: complete
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - success_criteria
  - data_specification
  - dependencies
---

# Product Requirements Document: H-M2

## 1. Executive Summary

**Hypothesis:** Under the HumanEval baseline failure cases (problems that fail in no-feedback single-pass generation with Llama 3.1 8B), if pylint+mypy is run on the failing code without execution, then fewer than 50% of failure cases receive at least one pylint/mypy warning or error, because HumanEval failures are predominantly logic/runtime errors that pylint cannot detect without executing the code.

**Gate:** SHOULD_WORK (pipeline continues regardless of outcome)
**Pass Condition:** coverage < 0.50 (pylint+mypy flags fewer than 50% of HumanEval baseline failures)
**Tier:** FULL (≤30 tasks total, 6-12 Epics)
**Prerequisite:** H-M1 COMPLETED — baseline failure artifacts already collected; no new LLM inference required

H-M2 is a **post-hoc measurement experiment**. It reuses existing code artifacts from H-E1/H-M1 and measures what fraction of HumanEval baseline failures are detectable by pylint+mypy. The hypothesis provides the causal explanation for why execution feedback dominates pylint feedback (H-M1 finding): pylint simply does not flag the majority of logic/runtime failures.

---

## 2. Problem Statement

**Research Gap:** H-M1 demonstrated that execution feedback significantly outperforms pylint feedback (McNemar HumanEval p=0.0001: exec_only=15, pylint_only=0; MBPP p<0.0001: exec_only=85, pylint_only=2). The causal explanation in the main hypothesis states that pylint covers a smaller error distribution. H-M2 empirically validates this claim by directly measuring pylint+mypy coverage on the known baseline failure set.

**Key Literature Context:**
- AssertionError = 63.64% of HumanEval errors (arxiv 2409.00676) — NOT catchable by pylint
- Most LLM code failures are compilable/runnable (NSF study): static analysis misses them
- Pylint primarily catches Convention/Warning issues, not functional logic errors (SCAM 2025)
- Expected coverage: ~20-40% based on error type distribution

**What We Need to Build:**
1. Coverage measurement script: run pylint+mypy on each HumanEval baseline failure code file
2. Bootstrap 95% CI on coverage fraction
3. Per-category breakdown (E/W/C/R) of pylint flags
4. Venn analysis: pylint-only vs mypy-only vs both
5. Figures: coverage bar chart vs 50% threshold, category breakdown, Venn diagram

---

## 3. Functional Requirements

### FR-1: Load Baseline Failure Cases
**Description:** Load HumanEval baseline failure code artifacts from H-E1/H-M1 runs. No new LLM inference required.

**Data Sources (priority order):**
```python
# Priority 1: h-m1 results (most recent)
BASELINE_SOURCES = [
    "docs/youra_research/h-m1/results/baseline_results.json",
    "docs/youra_research/h-e1/results/baseline_results.json",
    "docs/youra_research/h-m1/results/baseline_humaneval.jsonl",
    "docs/youra_research/h-e1/results/baseline_humaneval.jsonl",
]

def load_baseline_failures() -> list[dict]:
    """Load HumanEval baseline failures from H-E1/H-M1 results."""
    for source in BASELINE_SOURCES:
        if os.path.exists(source):
            if source.endswith('.json'):
                with open(source) as f:
                    data = json.load(f)
                # Handle both list format and dict format
                if isinstance(data, list):
                    failing = [r for r in data if not r.get('passed', True)]
                else:
                    failing = [v for v in data.values() if not v.get('passed', True)]
            elif source.endswith('.jsonl'):
                with open(source) as f:
                    data = [json.loads(l) for l in f if l.strip()]
                failing = [r for r in data if not r.get('passed', True)]
            print(f"Loaded {len(failing)} baseline failures from {source}")
            return failing
    raise FileNotFoundError("No baseline failure artifacts found. Run H-E1/H-M1 first.")
```

**Expected output:** List of ~64 failure cases (HumanEval baseline pass@1=0.6098 → ~64 failures from 164 total)

**Outputs:**
- In-memory: `failing_cases: list[dict]` with `task_id`, `generated_code`
- Logged: count of failures loaded, source file used

---

### FR-2: Static Analysis Coverage Measurement (CORE MECHANISM)
**Description:** For each failing code artifact, run pylint+mypy and record whether ≥1 warning/error is emitted. This is the primary measurement.

**Algorithm:**
```python
import tempfile, os
from io import StringIO
from mypy import api as mypy_api
from pylint import lint
from pylint.reporters.text import TextReporter

def has_static_analysis_flag(code_str: str, task_id: str) -> dict:
    """
    Check if pylint+mypy flags ≥1 warning/error on generated code.
    Returns detailed breakdown by tool and category.
    """
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
        f.write(code_str)
        tmp_path = f.name
    
    result = {
        'task_id': task_id,
        'pylint_flagged': False,
        'mypy_flagged': False,
        'flagged': False,
        'pylint_categories': {'E': 0, 'W': 0, 'C': 0, 'R': 0, 'I': 0},
        'pylint_message_count': 0,
        'mypy_error_count': 0,
        'pylint_output': '',
        'mypy_output': '',
    }
    
    try:
        # --- Run pylint ---
        buf = StringIO()
        reporter = TextReporter(buf)
        runner = lint.Run(
            [tmp_path, '--score=no', '--output-format=text'],
            reporter=reporter,
            exit=False
        )
        pylint_output = buf.getvalue()
        result['pylint_output'] = pylint_output[:1000]
        
        # Parse categories from pylint output lines (format: "file:line:col: X#### message")
        for line in pylint_output.splitlines():
            # pylint message format: path:line:col: category-id message
            # category = first char after ': ' that is E/W/C/R/I
            parts = line.split(':')
            if len(parts) >= 4:
                msg_part = parts[-1].strip() if len(parts) > 4 else ''
                for cat in ['E', 'W', 'C', 'R', 'I']:
                    if f' {cat}' in line or line.strip().startswith(cat):
                        result['pylint_categories'][cat] += 1
                        break
        
        result['pylint_message_count'] = sum(result['pylint_categories'].values())
        result['pylint_flagged'] = result['pylint_message_count'] > 0
        
        # --- Run mypy ---
        mypy_out, mypy_err, mypy_exit = mypy_api.run([
            '--ignore-missing-imports',
            '--no-strict-optional',
            '--no-error-summary',
            tmp_path
        ])
        result['mypy_output'] = mypy_out[:500]
        result['mypy_flagged'] = (mypy_exit != 0)
        # Count actual error lines (exclude "Found N errors" summary)
        result['mypy_error_count'] = len([
            l for l in mypy_out.splitlines()
            if l.strip() and 'error:' in l and not l.startswith('Found')
        ])
        
        # Combined flag: either tool fires
        result['flagged'] = result['pylint_flagged'] or result['mypy_flagged']
        
    except Exception as e:
        result['error'] = str(e)
        result['flagged'] = False
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
    return result

def run_coverage_measurement(failing_cases: list[dict]) -> list[dict]:
    """Run static analysis on all failing cases."""
    results = []
    for case in tqdm(failing_cases, desc="Static analysis"):
        code = case.get('generated_code') or case.get('completion') or case.get('code', '')
        task_id = case.get('task_id', f'unknown_{len(results)}')
        if not code.strip():
            results.append({'task_id': task_id, 'flagged': False, 'error': 'empty_code'})
            continue
        results.append(has_static_analysis_flag(code, task_id))
    return results
```

**Fallback (if pylint API fails):**
```python
import subprocess, json

def pylint_subprocess_fallback(filepath: str) -> dict:
    """Subprocess fallback for pylint invocation."""
    cmd = ['python', '-m', 'pylint', '--output-format=json', '--score=no', filepath]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        messages = json.loads(result.stdout) if result.stdout.strip() else []
    except json.JSONDecodeError:
        messages = []
    return {
        'pylint_flagged': len(messages) > 0,
        'pylint_message_count': len(messages),
        'pylint_categories': {
            cat: sum(1 for m in messages if m.get('type', '').upper().startswith(cat))
            for cat in ['E', 'W', 'C', 'R']
        }
    }
```

**Outputs:**
- `results/h-m2/coverage_results.json`: per-task analysis results
- In-memory: list of result dicts for metric computation

---

### FR-3: Metric Computation
**Description:** Compute all primary and secondary metrics from coverage results.

**Primary Metric:**
```python
import numpy as np

def compute_metrics(results: list[dict]) -> dict:
    n_total = len(results)
    n_flagged = sum(1 for r in results if r.get('flagged', False))
    n_pylint_only = sum(1 for r in results if r.get('pylint_flagged') and not r.get('mypy_flagged'))
    n_mypy_only = sum(1 for r in results if r.get('mypy_flagged') and not r.get('pylint_flagged'))
    n_both = sum(1 for r in results if r.get('pylint_flagged') and r.get('mypy_flagged'))
    
    coverage = n_flagged / n_total
    
    # Bootstrap 95% CI
    flags = np.array([1 if r.get('flagged') else 0 for r in results])
    rng = np.random.default_rng(42)
    bootstrap_means = [rng.choice(flags, len(flags)).mean() for _ in range(10000)]
    ci_lower, ci_upper = np.percentile(bootstrap_means, [2.5, 97.5])
    
    # Category distribution
    all_cats = {'E': 0, 'W': 0, 'C': 0, 'R': 0, 'I': 0}
    for r in results:
        for cat, count in r.get('pylint_categories', {}).items():
            all_cats[cat] = all_cats.get(cat, 0) + count
    
    return {
        'n_total_failures': n_total,
        'n_flagged': n_flagged,
        'n_unflagged': n_total - n_flagged,
        'coverage': coverage,
        'coverage_ci_lower': ci_lower,
        'coverage_ci_upper': ci_upper,
        'coverage_passes_gate': coverage < 0.50,
        'gate_type': 'SHOULD_WORK',
        'n_pylint_only': n_pylint_only,
        'n_mypy_only': n_mypy_only,
        'n_both_flagged': n_both,
        'n_neither': n_total - n_flagged,
        'pylint_coverage': sum(1 for r in results if r.get('pylint_flagged')) / n_total,
        'mypy_coverage': sum(1 for r in results if r.get('mypy_flagged')) / n_total,
        'pylint_category_totals': all_cats,
    }
```

**Outputs:**
- `results/h-m2/metrics.json`: all metrics
- `results/h-m2/summary.md`: human-readable summary

---

### FR-4: Visualization Generation
**Description:** Generate required figures.

**Figure 1 (MANDATORY — Gate Metrics):** Bar chart showing coverage fractions:
- pylint+mypy combined vs 50% threshold line
- pylint-only coverage
- mypy-only coverage
Annotate with bootstrap 95% CI and gate result.

**Figure 2:** Pylint category breakdown — stacked/grouped bar chart showing fraction of failures flagged by E (Error), W (Warning), C (Convention), R (Refactor). Distinguishes functional detection from style detection.

**Figure 3:** Venn diagram — overlap between pylint-flagged and mypy-flagged failure cases (using matplotlib_venn or manual matplotlib patches).

**Figure 4 (optional):** Per-task flag count distribution — histogram of number of pylint messages per failing code file.

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def generate_figures(metrics: dict, results: list[dict], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    # Figure 1: Coverage comparison with threshold
    fig, ax = plt.subplots(figsize=(8, 5))
    coverages = [metrics['coverage'], metrics['pylint_coverage'], metrics['mypy_coverage']]
    labels = ['Combined\n(pylint+mypy)', 'Pylint only', 'Mypy only']
    colors = ['#2196F3', '#FF9800', '#4CAF50']
    bars = ax.bar(labels, coverages, color=colors, alpha=0.8, edgecolor='black')
    ax.axhline(0.5, color='red', linestyle='--', linewidth=2, label='50% threshold (H-M2 gate)')
    # CI error bar on combined
    ci_err = [[metrics['coverage'] - metrics['coverage_ci_lower']],
              [metrics['coverage_ci_upper'] - metrics['coverage']]]
    ax.errorbar([0], [metrics['coverage']], yerr=ci_err, fmt='none', color='black', capsize=5)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel('Coverage Fraction')
    ax.set_title(f'Pylint+Mypy Coverage on HumanEval Failures\n'
                 f'(n={metrics["n_total_failures"]} failures, coverage={metrics["coverage"]:.3f}, '
                 f'gate: {"PASS" if metrics["coverage_passes_gate"] else "FAIL"})')
    ax.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/figure1_coverage_comparison.png', dpi=150)
    plt.close()
    
    # Figure 2: Pylint category breakdown
    cats = metrics['pylint_category_totals']
    fig, ax = plt.subplots(figsize=(7, 4))
    cat_labels = ['E (Error)', 'W (Warning)', 'C (Convention)', 'R (Refactor)']
    cat_values = [cats.get('E', 0), cats.get('W', 0), cats.get('C', 0), cats.get('R', 0)]
    ax.bar(cat_labels, cat_values, color=['#f44336', '#FF9800', '#2196F3', '#9C27B0'], alpha=0.8)
    ax.set_ylabel('Total Flag Count')
    ax.set_title('Pylint Message Categories on HumanEval Failures')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/figure2_pylint_categories.png', dpi=150)
    plt.close()
    
    # Figure 3: Venn diagram (manual)
    fig, ax = plt.subplots(figsize=(6, 5))
    # pylint circle
    c1 = plt.Circle((0.4, 0.5), 0.3, color='#FF9800', alpha=0.4, label='Pylint')
    c2 = plt.Circle((0.6, 0.5), 0.3, color='#4CAF50', alpha=0.4, label='Mypy')
    ax.add_patch(c1); ax.add_patch(c2)
    ax.text(0.25, 0.5, str(metrics['n_pylint_only']), ha='center', va='center', fontsize=14, fontweight='bold')
    ax.text(0.75, 0.5, str(metrics['n_mypy_only']), ha='center', va='center', fontsize=14, fontweight='bold')
    ax.text(0.5, 0.5, str(metrics['n_both_flagged']), ha='center', va='center', fontsize=14, fontweight='bold')
    ax.text(0.5, 0.88, f'Neither: {metrics["n_neither"]}', ha='center', fontsize=11)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('Pylint vs Mypy Coverage Overlap\n(HumanEval Baseline Failures)')
    handles = [mpatches.Patch(color='#FF9800', alpha=0.6, label='Pylint'),
               mpatches.Patch(color='#4CAF50', alpha=0.6, label='Mypy')]
    ax.legend(handles=handles)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/figure3_venn_overlap.png', dpi=150)
    plt.close()
```

**Output location:** `docs/youra_research/h-m2/figures/`

---

### FR-5: Summary Report Generation
**Description:** Generate human-readable markdown summary of results.

**Output:** `results/h-m2/summary.md` with:
- Primary metric: coverage fraction + 95% CI
- Gate assessment: PASS (coverage < 0.50) or NULL (coverage ≥ 0.50)
- Category breakdown
- Key finding statement
- Connection to H-M1 causal explanation

---

### FR-6: Experiment Orchestration
**Description:** Single entry-point script.

**Script:** `experiments/h-m2/run_experiment.py`

**CLI:**
```bash
python run_experiment.py \
  --h-m1-results docs/youra_research/h-m1/results/ \
  --h-e1-results docs/youra_research/h-e1/results/ \
  --output-dir results/h-m2/ \
  --figures-dir docs/youra_research/h-m2/figures/ \
  --seed 42 \
  --n-bootstrap 10000
```

**Steps:**
1. Load baseline failures from H-M1/H-E1 results
2. Run pylint+mypy coverage measurement on all failures
3. Compute metrics + bootstrap CI
4. Generate figures
5. Write metrics.json + summary.md
6. Print gate assessment

---

## 4. Data Specification

### Dataset: HumanEval Baseline Failures (Derived)
| Field | Value |
|-------|-------|
| Name | HumanEval Baseline Failures (derived from H-E1/H-M1) |
| Source | `docs/youra_research/h-e1/results/` or `h-m1/results/` |
| Problems | ~64 failures (HumanEval 164 total, baseline pass@1≈0.6098) |
| Format | JSON/JSONL: task_id, generated_code, passed=False |
| Download | **None** — reuse H-E1/H-M1 artifacts (no new LLM inference) |
| Evaluation | pylint + mypy static analysis (CPU-only, <5 minutes for 64 files) |
| Split | Full HumanEval failure set (no sampling) |

**No manual download required.** All data reused from prior hypotheses.

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Bootstrap seed: 42 (fixed)
- Pylint/mypy versions pinned in requirements.txt
- Deterministic measurement (static analysis has no randomness)
- All intermediate results saved to JSON

### NFR-2: Safety
- Temp file cleanup after each analysis (finally block)
- No code execution in main process (static analysis only)
- Subprocess fallback if API fails

### NFR-3: Performance
- Expected runtime: <5 minutes for 64 files (CPU-only)
- No GPU required
- No API calls (purely local static analysis)

### NFR-4: Data Integrity
- Verify loaded failure count is within expected range [50, 100] (sanity check)
- Warn if count < 10 (suspiciously low — may indicate data loading issue)
- Preserve original task_id for traceability

---

## 6. Success Criteria

### PoC Pass (SHOULD_WORK gate — pipeline continues either way):
1. Script runs end-to-end on all HumanEval failure artifacts without crash
2. Coverage fraction computed and saved to metrics.json
3. Bootstrap 95% CI computed (n=10000)
4. All 3 required figures generated

### Gate Evaluation:
- **coverage < 0.50 → GATE PASS:** Confirms causal explanation (pylint misses most failures)
- **coverage ≥ 0.50 → NULL RESULT:** Publishable challenge finding; pipeline continues (SHOULD_WORK)
- Expected value: ~20-40% based on literature (AssertionError=63.64% of HumanEval errors)

### Secondary:
5. Category breakdown shows C (Convention) or W (Warning) dominate over E (Error) — confirms pylint bias
6. Pylint-only coverage substantially > mypy-only (pylint is primary tool for this codebase)
7. summary.md generated with clear gate assessment

### Failure Fallback:
- If pylint API unavailable → use subprocess fallback (`python -m pylint --output-format=json`)
- If H-E1/H-M1 artifacts not found → error message with clear instructions to run prerequisite phases

---

## 7. Dependencies

### 7.1 Python Packages
```
# Static analysis (likely already installed from H-E1)
pylint>=3.0.0
mypy>=1.0.0

# Data
numpy>=1.24.0

# Statistics
scipy>=1.11.0         # bootstrap CI

# Visualization
matplotlib>=3.7.0

# Utilities
tqdm>=4.65.0
pyyaml>=6.0
```

**No new packages beyond H-E1/H-M1 environment.**

### 7.2 External References
- arxiv.org/abs/2409.00676: Error type distribution (AssertionError=63.64%)
- mypy.readthedocs.io: Programmatic mypy API
- stackoverflow.com/questions/2028268: Pylint lint.Run() pattern

### 7.3 H-E1/H-M1 Result Dependencies (REQUIRED)
- `docs/youra_research/h-e1/results/baseline_results.json` OR
- `docs/youra_research/h-m1/results/baseline_results.json` OR
- `docs/youra_research/h-e1/results/baseline_humaneval.jsonl` OR
- `docs/youra_research/h-m1/results/baseline_humaneval.jsonl`

At least one of the above must exist (from H-E1 or H-M1 runs).

---

## 8. File Structure

```
experiments/h-m2/
├── run_experiment.py              # Main entry point
├── data_loader.py                 # Load baseline failures from H-E1/H-M1
├── static_analyzer.py             # pylint+mypy coverage measurement
├── metrics.py                     # Coverage fraction + bootstrap CI
├── visualizer.py                  # Figure generation
├── requirements.txt
└── README.md

results/h-m2/
├── coverage_results.json          # Per-task analysis results
├── metrics.json                   # All computed metrics
└── summary.md                     # Human-readable summary

docs/youra_research/h-m2/figures/
├── figure1_coverage_comparison.png
├── figure2_pylint_categories.png
└── figure3_venn_overlap.png
```

---

## 9. Out of Scope

- Any new LLM inference (H-M2 reuses H-E1/H-M1 artifacts)
- MBPP coverage analysis (H-M2 focuses on HumanEval baseline failures as specified)
- Dynamic code execution (static analysis only — no sandbox needed)
- WandB tracking (CPU experiment, no GPU needed)
- Comparison to execution feedback coverage (that is H-M1's job)
- Fine-tuning or model modification
