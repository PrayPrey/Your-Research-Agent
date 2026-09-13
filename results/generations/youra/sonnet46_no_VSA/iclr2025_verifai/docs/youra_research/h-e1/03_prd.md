# Product Requirements Document: H-E1
## ContractEval Contract-Strength Gap Existence Verification

**Hypothesis:** H-E1 (EXISTENCE, FOUNDATION)
**Date:** 2026-08-03
**Tier:** LIGHT (≤15 tasks)
**Source:** 02c_experiment_brief.md

---

## 1. Executive Summary

Verify that LLM-generated programs which pass all unit tests on ContractEval's 364 HumanEval+/MBPP+ tasks still exhibit a non-zero **contract-strength gap** — i.e., a non-trivial fraction fail ≥1 contract when checked via Hypothesis PBT with `icontract-hypothesis` strategy inference. This is a PoC existence experiment: we need mean_gap > 0 with bootstrap 95% CI lower bound > 0.01.

---

## 2. Problem Statement

Existing LLM code evaluation benchmarks (EvalPlus) measure whether generated code passes unit tests, not whether it satisfies formal contracts (pre/postconditions). ContractEval (Lim et al., ACL 2026) showed 0% contract satisfaction under standard prompting using Z3-based CVT generation — but only 25.82% of tasks are Z3-tractable. H-E1 replaces Z3 with execution-based Hypothesis PBT (100% tractable) to confirm the gap holds across all 364 tasks.

---

## 3. Scope

- **In scope:** 364 ContractEval tasks (HumanEval+ subset + MBPP+ subset); 5 LLMs; n=10 samples per (model, task); Hypothesis PBT with 5k budget; bootstrap CI; oracle soundness pre-check
- **Out of scope:** Model fine-tuning; contract-aware prompting (H-M hypotheses); tasks that fail oracle soundness pre-check (quarantined)

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | ContractEval |
| Source | github.com/suhanmen/ContractEval |
| Access | `git clone https://github.com/suhanmen/ContractEval.git` (manual download required) |
| Size | 364 tasks |
| Format | JSON per task: task_id, entry_point, prompt, contracts (icontract pre/postconditions), reference_impl |
| Splits | No train/val/test split — all 364 tasks used |
| Preprocessing | Parse JSON; extract icontract-decorated reference_impl; associate with evalplus task_id |

```python
import json, os
def load_contracteval(data_dir="./ContractEval/data"):
    tasks = {}
    for fname in os.listdir(data_dir):
        if fname.endswith(".json"):
            with open(os.path.join(data_dir, fname)) as f:
                task = json.load(f)
                tasks[task["task_id"]] = task
    return tasks  # keys: task_id, entry_point, prompt, contracts, reference_impl
```

### 4.2 Code Generation

- **Pipeline:** evalplus/evalplus (NeurIPS 2023)
- **Models:** GPT-4o-mini (OpenAI), Claude-3-haiku (Anthropic), DeepSeek-Coder-V2-Lite (vLLM), CodeLlama-13B (vLLM), CodeLlama-34B (vLLM)
- **Sampling:** n=10 per (model, task), temperature=0.8
- **Output:** JSONL per model per dataset

---

## 5. Functional Requirements

### FR-1: Dataset Acquisition
- Clone ContractEval repo; verify 364 tasks load correctly
- Store in `data/contracteval/`

### FR-2: Environment Setup
- Install: `icontract`, `icontract-hypothesis`, `hypothesis`, `evalplus[vllm]`, `scipy`, `numpy`
- Set API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY

### FR-3: Oracle Soundness Pre-check
- Run Hypothesis PBT on ContractEval **reference implementations** (budget=100k, seed=42, timeout=2h wall-clock total)
- Any task where reference_impl violates its own contracts → quarantine (exclude from experiment)
- Log quarantined task count; must be ≤ 5% of 364

### FR-4: Code Generation (5 Models × 364 Tasks × n=10)
- Use evalplus.codegen pipeline for all 5 models
- Save raw samples to `data/samples/{model}/{dataset}.jsonl`
- Total: 5 models × 364 tasks × 10 samples = 18,200 generated programs

### FR-5: Test-Passing Filter
- Run `evalplus.evaluate --base-only` on each sample set
- Retain only programs that pass all unit tests
- Log pass rates per model

### FR-6: Hypothesis PBT Contract Checking
- For each test-passing program, run `icontract_hypothesis.infer_strategy(reference_impl)` to get strategy
- Run `@given(strategy)` with budget=5000, seed=42, timeout=60s per check
- Record: violated (bool), n_failures (int), n_total (int), gap (float)
- Store results to `results/pbt_results_{model}_{dataset}.jsonl`

### FR-7: Aggregate Metrics
- Compute per-task gap = fraction of test-passing programs failing ≥1 contract
- Compute mean_gap across all tasks × models
- Bootstrap 95% CI (n=10000, seed=42)
- Check: CI_lower > 0.01 → PASS gate

### FR-8: Sanity Check
- Compute gap on Z3-tractable subset (from ContractEval paper appendix)
- Verify ≥ 5% on tractable subset (matches h-e1 pilot 7.42%)

### FR-9: Figure Generation
- Required: Bar chart — mean contract-strength gap vs 0 baseline, with 95% CI error bars
- Additional: Per-model box plot (5 models), per-task gap histogram (364 tasks), cumulative gap plot, soundness pre-check summary
- Save all figures to `h-e1/figures/`

### FR-10: Results Logging
- Save `results/summary.json`: mean_gap, CI_lower, CI_upper, n_tasks, n_programs, gate_passed
- Human-readable `results/summary_report.md`

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | All RNG seeded (seed=42); fixed n=10 samples; deterministic pipeline |
| Runtime | Oracle pre-check ≤ 2h; full experiment ≤ 24h wall-clock on single GPU node |
| Timeout | 60s per PBT check; skip and record timeout |
| Logging | JSON-Lines per result; full provenance chain |

---

## 7. Dependencies

### 7.1 Python Packages

```
icontract>=2.6
icontract-hypothesis>=1.1.7
hypothesis>=6.0
evalplus[vllm]>=0.3
scipy>=1.10
numpy>=1.24
matplotlib>=3.7
seaborn>=0.12
pandas>=2.0
tqdm>=4.65
```

### 7.2 External Repositories

| Repo | Purpose | Install |
|------|---------|---------|
| suhanmen/ContractEval | Dataset + contracts | `git clone` |
| evalplus/evalplus | Code generation pipeline | `pip install evalplus[vllm]` |
| mristin/icontract-hypothesis | PBT strategy inference | `pip install icontract-hypothesis` |

### 7.3 API Keys Required

- `OPENAI_API_KEY` — GPT-4o-mini
- `ANTHROPIC_API_KEY` — Claude-3-haiku

---

## 8. Success Criteria

| Criterion | Threshold | Gate |
|-----------|-----------|------|
| mean_contract_strength_gap > 0 | CI lower bound > 0.01 | MUST_WORK (blocks all H-M) |
| Gap on Z3-tractable subset | ≥ 5% | Sanity check only |
| Oracle soundness pre-check | ≤ 5% tasks quarantined | Data quality check |
| Code runs without error | PBT runs on ≥ 300/364 tasks | Technical baseline |

---

## 9. File Structure

```
h-e1/
├── 03_prd.md                    # This file
├── 03_architecture.md           # Module structure + epic tasks
├── 03_logic.md                  # API signatures + pseudo-code
├── 03_config.md                 # Configuration + hyperparameters
├── 03_tasks.yaml                # Phase 4 task list
├── code/                        # Implementation
│   ├── data_loader.py           # ContractEval loader
│   ├── code_generator.py        # evalplus wrapper
│   ├── contract_checker.py      # Hypothesis PBT checker
│   ├── metrics.py               # Gap computation + bootstrap CI
│   ├── figures.py               # Visualization
│   └── run_experiment.py        # Orchestration script
├── data/
│   ├── contracteval/            # Dataset
│   └── samples/                 # Generated code per model
├── results/                     # PBT results + summary
└── figures/                     # Saved plots
```

---

*stepsCompleted: [PRD]*
