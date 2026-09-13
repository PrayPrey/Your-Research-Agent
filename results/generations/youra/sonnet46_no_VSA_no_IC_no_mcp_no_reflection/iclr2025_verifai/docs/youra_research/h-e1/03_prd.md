---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
generated: 2026-08-31
author: yoon303@ust.ac.kr
---

# PRD: h-e1 — Multi-Verifier Activation Measurement

## 1. Executive Summary

This experiment implements and measures a 4-category formal feedback system applied to GPT-4o-mini-generated code on HumanEval+MBPP (538 problems). The goal is to verify that each feedback category (execution monitoring, static analysis, type checking, SMT solving) produces a measurably distinct signal on ≥10% of problems, establishing the existence of diverse formal feedback as a foundation for the YOURA repair loop.

This is a **measurement-only PoC** (no repair loop). Code is generated once, then 4 verifiers are applied independently. Results gate the entire research chain (H-E1 → H-M1 → H-M2 → H-M3 → H-M4).

## 2. Problem Statement

Automated code repair systems typically use a single feedback source (execution traces). YOURA hypothesizes that combining multiple formal feedback categories (execution, static analysis, type checking, SMT constraints) will improve repair quality. Before building the repair system, we must verify that each category actually activates on ≥10% of problems — this is hypothesis H-E1.

**Gate:** MUST_WORK — if any category fails ≥10% activation, stop the research chain.

## 3. Scope

### In Scope
- GPT-4o-mini code generation (single shot, 538 problems)
- 4 independent verifier applications per completion
- Activation rate measurement per category
- SMT pilot (20 problems, soundness check)
- Statistical analysis and visualization (5 figures)

### Out of Scope
- Repair iterations (H-M1+)
- Multiple LLM models
- Fine-tuning
- Hyperparameter search (single-run PoC)

## 4. Data Specification

### 4.1 HumanEval
- **Source:** openai/human-eval (GitHub)
- **Load method:** `pip install human-eval` → `from human_eval.data import read_problems`
- **Problems:** 164 (full test set, no subsampling)
- **Format:** dict with `task_id`, `prompt` (function signature + docstring), `test` (unit tests), `entry_point`
- **Download:** Auto (pip install)
- **Manual download required:** No

### 4.2 MBPP
- **Source:** google-research-datasets/mbpp (HuggingFace)
- **Load method:** `datasets.load_dataset("google-research-datasets/mbpp", "sanitized")["test"]`
- **Problems:** 374 (canonical test split)
- **Format:** dict with `task_id`, `text` (problem description), `code` (reference), `test_list` (assertions)
- **Download:** Auto (HuggingFace datasets)
- **Manual download required:** No

### 4.3 SMT Pilot Subset
- **Size:** 20 problems (randomly sampled from combined 538, seed=1)
- **Purpose:** Verify SMT constraint extraction soundness (A1 assumption) before full run
- **Selection:** `random.seed(1); pilot_ids = random.sample(all_problem_ids, 20)`

## 5. Functional Requirements

### FR-1: Dataset Loading
- Load HumanEval (164 problems) via human-eval package
- Load MBPP sanitized test split (374 problems) via HuggingFace datasets
- Combine into unified list of 538 problems with consistent schema: `{problem_id, prompt, test_code, source}`
- Assign sequential IDs: `HE_0001..HE_0164`, `MB_0001..MB_0374`

### FR-2: Code Generation
- Generate completions for all 538 problems using GPT-4o-mini
- Configuration: temperature=0.2, max_tokens=512, single sample per problem
- Prompt format: canonical (function signature + docstring for HumanEval; description for MBPP)
- Save raw completions to `results/completions.jsonl` (checkpoint for reproducibility)

### FR-3: SMT Pilot
- Sample 20 problems (seed=1) before full verifier run
- For each pilot problem: call GPT-4o-mini to generate Z3 constraints from docstring
- Measure: what fraction produce valid Z3 SAT result with counterexample
- **Gate:** ≥30% SAT rate (≥6/20) → proceed to full SMT run; else → scope to 3-category
- Log: `results/smt_pilot_results.json`

### FR-4: Verifier Application
Apply 4 verifiers independently to each of 538 completions:

**FR-4a: Execution Monitoring**
- Run completion against problem's unit tests in subprocess (timeout=3.0s)
- Activation: `not passed` (exception/assertion failure with non-empty trace)
- Output per problem: `{activated: bool, signal: str, latency_ms: float}`

**FR-4b: Static Analysis (mypy)**
- Write completion to temp `.py` file
- Run: `mypy --strict <file>` (timeout=10s)
- Activation: `returncode != 0` (≥1 error line in stdout)
- Output per problem: `{activated: bool, signal: str, latency_ms: float}`

**FR-4c: Type Checking (Pyright)**
- Run: `pyright --outputjson <file>` (timeout=10s)
- Parse JSON: activation = `len(generalDiagnostics) > 0`
- Output per problem: `{activated: bool, signal: str, latency_ms: float}`

**FR-4d: SMT Solving (Z3)**
- Call GPT-4o-mini to generate Z3 constraint encoding from problem docstring
- Execute Z3 solver with generated constraints (timeout=10s)
- Activation: `result == sat` (SAT with model, not UNSAT/unknown/timeout)
- Output per problem: `{activated: bool, signal: str, latency_ms: float}`
- Skip if SMT pilot failed gate (FR-3)

### FR-5: Activation Measurement
- Compute `activation_rate[category] = count(activated) / 538` for all 4 categories
- Compute pairwise overlap: for each pair (cat_a, cat_b), fraction of problems where both activate
- Compute per-source breakdown: HumanEval (164) and MBPP (374) separately

### FR-6: Result Persistence
- Save per-problem results: `results/verifier_results.jsonl`
- Save aggregated stats: `results/activation_stats.json`
- Save figures: `figures/` directory (5 figures, see Section 8)

### FR-7: PoC Gate Check
- Check `all(activation_rate[cat] >= 0.10 for cat in four_categories)`
- Print pass/fail status clearly
- Exit code 0 if all pass, 1 if any fail

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed (1) for all random sampling
- Completions cached to `results/completions.jsonl` (re-run skips generation)
- All intermediate results checkpointed

### NFR-2: Performance
- Total runtime < 4 hours (538 × 4 verifiers + LLM calls)
- LLM calls: 538 (generation) + 20 (SMT pilot) + 538 (SMT constraints if pilot passes) ≤ 1096 API calls
- Parallelism: verifiers run sequentially per problem (no async required for PoC)

### NFR-3: Error Handling
- Verifier timeout → record as `{activated: False, signal: "TIMEOUT", latency_ms: timeout*1000}`
- LLM API error → retry 3× with exponential backoff, then skip + log
- JSON parse error (Pyright) → treat as no diagnostics

### NFR-4: Cost
- Estimated API cost: $2–5 (GPT-4o-mini, 538+20+538 calls at ~500 tokens each)
- Requires `OPENAI_API_KEY` environment variable

## 7. Dependencies

### 7.1 Python Packages
```
python>=3.10
openai>=1.0.0
datasets>=2.14.0
human-eval>=1.0  # pip install human-eval (from openai/human-eval)
mypy>=1.0.0
pyright>=1.1.300  # or latest
z3-solver>=4.12.0
matplotlib>=3.7.0
pandas>=2.0.0
numpy>=1.24.0
tqdm>=4.65.0
pyyaml>=6.0
```

### 7.2 External Tools (CLI)
- `pyright` — must be on PATH (installed via npm or pip install pyright)
- `mypy` — must be on PATH (pip install mypy)

### 7.3 External APIs
- OpenAI API (GPT-4o-mini): requires `OPENAI_API_KEY`

### 7.4 External Repositories (Reference Only)
- openai/human-eval: https://github.com/openai/human-eval
- google-research-datasets/mbpp: HuggingFace hub

## 8. Visualization Requirements

### Figure 1 (Mandatory): Gate Metrics Bar Chart
- Bar chart: activation_rate per category vs. 10% threshold line
- x: 4 categories; y: activation_rate [0,1]; threshold line at y=0.10
- Color: green (pass) / red (fail) per bar
- Save: `figures/activation_rates.png`

### Figure 2: Pairwise Overlap Heatmap
- 4×4 matrix showing pairwise overlap fraction between activated sets
- Save: `figures/overlap_matrix.png`

### Figure 3: Activation by Source
- Grouped bar chart: HumanEval vs. MBPP breakdown per category
- Save: `figures/activation_by_source.png`

### Figure 4: Signal Length Distribution
- Box plot of `len(signal)` per category (non-trivial signals only)
- Save: `figures/signal_length_dist.png`

### Figure 5: SMT Pilot Soundness
- Bar chart: SAT/UNSAT/timeout/error breakdown for 20 pilot problems
- Save: `figures/smt_pilot.png`

## 9. Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Execution activation | ≥10% of 538 | `activation_rate["execution"] >= 0.10` |
| Static analysis activation | ≥10% of 538 | `activation_rate["static_analysis"] >= 0.10` |
| Type checking activation | ≥10% of 538 | `activation_rate["type_checking"] >= 0.10` |
| SMT solving activation | ≥10% of 538 | `activation_rate["smt_solving"] >= 0.10` |
| SMT pilot soundness | ≥30% of 20 | `smt_pilot_sat_rate >= 0.30` |
| Pipeline completion | 0 crashes | All 538 problems processed |

**Gate type:** MUST_WORK — all criteria must pass.

## 10. File Structure

```
h-e1/
├── code/
│   ├── run_experiment.py        # Main entry point
│   ├── data_loader.py           # HumanEval + MBPP loading
│   ├── generate_completions.py  # GPT-4o-mini generation
│   ├── verifiers/
│   │   ├── execution_monitor.py
│   │   ├── static_analysis.py
│   │   ├── type_checker.py
│   │   └── smt_solver.py
│   ├── measure_activation.py    # Aggregation + gate check
│   ├── visualize.py             # All 5 figures
│   └── requirements.txt
├── results/
│   ├── completions.jsonl        # Cached completions
│   ├── smt_pilot_results.json
│   ├── verifier_results.jsonl
│   └── activation_stats.json
└── figures/
    ├── activation_rates.png
    ├── overlap_matrix.png
    ├── activation_by_source.png
    ├── signal_length_dist.png
    └── smt_pilot.png
```
