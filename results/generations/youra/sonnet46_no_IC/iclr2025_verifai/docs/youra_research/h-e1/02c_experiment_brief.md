# Experiment Design: h-e1

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under HumanEval and MBPP benchmarks, if pylint/mypy static analysis feedback is applied in iterative repair mode at fixed token budget B=1000 output tokens per problem using Llama 3.1 8B Instruct, then a measurable pass@1 delta (positive, near-zero, or negative) over no-feedback baseline is produced.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (no prerequisites for H-E1)
**Gate Status:** MUST_WORK — pass condition: Δ_pylint is computable and finite

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation)

### Gate Condition

MUST_WORK: The pylint/mypy repair loop must run end-to-end on HumanEval + MBPP without systematic failure, producing a computable Δ_pylint value (positive, near-zero, or negative). A null result (Δ_pylint ≈ 0) is equally valid as a positive result — this PoC establishes that the experimental condition can be measured.

---

## Continuation Context

This is the first hypothesis in the verification chain (H-E1 → H-M1 → H-M2 → H-M3). No previous hypothesis context to load.

### Previous Hypothesis Results (if applicable)
N/A — H-E1 is the foundation hypothesis with no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: LLM iterative code repair feedback experiment design**
- No directly relevant past cases found in Archon KB for this specific domain (LLM code repair with pylint/execution feedback). Archon KB contains primarily diffusion model and image generation content.
- Key insight: This experiment is novel in the Archon KB context — no prior VerifAI cases to build on.

**Query 2: pylint static analysis feedback iterative repair**
- No matching past cases found.

**Query 3: HumanEval MBPP pass@1 code generation benchmark**
- No matching past cases found.

**Archon KB Assessment:** KB does not contain prior cases for this research domain. Experiment design relies on Exa GitHub research and established literature from Phase 2B.

### Archon Code Examples

**Query: HumanEval MBPP LLM code generation evaluation**
- No relevant code examples found in Archon KB for this domain.

### Exa GitHub Implementations

**Query 1: iterative code repair LLM pylint feedback HumanEval MBPP**

**Repository 1: Johin2/iterative-code-repair** (Primary Reference — Arimbur 2026)
- **URL:** https://github.com/Johin2/iterative-code-repair
- **Paper:** "How Many Tries Does It Take? Iterative Self-Repair in LLM Code Generation Across Model Scales and Benchmarks" (arxiv 2604.10508)
- **Relevance:** DIRECT — This is the exact paper cited in Phase 2B (Arimbur 2026). Tests Llama 3.1 8B on HumanEval (164) + MBPP Sanitized (257) with execution feedback.
- **Key Results for Llama 3.1 8B:**
  - HumanEval: 67.1% → 76.8% (+9.8pp) with execution self-repair, up to 5 rounds
  - MBPP Sanitized: 55.6% → 71.6% (+16.0pp) with execution self-repair
  - Most gains (76-95%) concentrate in first 2 rounds
  - Greedy decoding (temperature=0.0) for reproducibility
- **Protocol:** generate → execute in sandboxed subprocess → capture error type + traceback → construct repair prompt → repeat up to 4 repair rounds
- **Code Structure:**
  - `experiments/self_repair.py` — repair prompt construction and code extraction
  - `experiments/code_executor.py` — sandboxed Python execution with 15s timeout
  - `experiments/data_loader.py` — HumanEval/MBPP data loading
  - `experiments/run_experiment.py` — main experiment runner
- **Implementation Path:** This repo provides the execution repair framework; H-E1 needs pylint layer added on top of same data/model infrastructure.

**Repository 2: cyb3rlab/CodeEnhancer**
- **URL:** https://github.com/cyb3rlab/CodeEnhancer
- **Relevance:** DIRECT — Referenced in Phase 2B (Assumption A4) as the pylint feedback framework to adapt. Uses pylint + Bandit in iterative validation loop.
- **Mechanism:** Code generation → Pylint syntax check → Bandit security check → LLM functional assessment → refine if issues found → repeat up to configurable limit (default: 5)
- **Key Code Pattern:**
  ```python
  # code_validator.py pattern (simplified)
  import pylint.lint
  import subprocess
  
  def run_pylint(code_file: str) -> dict:
      result = subprocess.run(
          ["pylint", "--output-format=json", code_file],
          capture_output=True, text=True
      )
      return parse_pylint_output(result.stdout)
  
  def iterative_repair(code: str, max_iter: int = 5) -> str:
      for i in range(max_iter):
          pylint_issues = run_pylint(write_temp_file(code))
          if not pylint_issues:
              return code  # passes pylint
          feedback = format_pylint_feedback(pylint_issues)
          code = llm_repair(code, feedback)
      return code
  ```
- **Limitation:** CodeEnhancer uses security-focused datasets, not HumanEval/MBPP. Adaptation required to load HumanEval problems and compute pass@1.

**Repository 3: NEUIR/INTERVENOR** (ACL 2024)
- **URL:** https://github.com/NEUIR/INTERVENOR
- **Relevance:** MEDIUM — Interactive chain-of-repairing on HumanEval + MBPP with execution feedback. Shows how to structure multi-round repair prompts.
- **Key Insight:** Execution repair on HumanEval/MBPP uses `evaluate_functional_correctness` from `openai/human-eval` package.

**Repository 4: Patchwork (tejaskhot/patchwork)**
- **URL:** https://github.com/tejaskhot/patchwork
- **Relevance:** MEDIUM — Uses both pylint (`lint` tool) AND execution (`run_tests` tool) in same agent. Demonstrates how to format pylint output for LLM consumption.
- **Key Code — pylint tool:**
  ```python
  def lint(code: str) -> str:
      """Static code analysis using pylint."""
      # Returns quality scores (0-10) and specific issue reports
      # Output formatted for LLM interpretation
  ```

**Query 2: LLM code generation iterative self-repair execution feedback pass@1**

**Repository 5: Blyth et al. 2025 (arxiv 2508.14419) — "Static Analysis as a Feedback Loop"**
- **URL:** https://arxiv.org/html/2508.14419v1
- **Relevance:** DIRECT for mechanism — Uses pylint iteratively on PythonSecurityEval with GPT-4o. Demonstrates pylint reduces security/readability issues but uses security benchmark (NOT HumanEval/MBPP).
- **Algorithm:**
  ```python
  # SelectIssues prompting strategy
  for iteration in range(max_iter=10):
      issues = run_pylint_and_bandit(code)  # get I issues per iteration
      if not issues: break
      code = llm.repair(code, selected_issues[:I])  # LLM resolves I issues at a time
  ```
- **Key Insight:** Pylint reduces readability violations >80% → 11% and reliability warnings >50% → 11% — but these are CODE QUALITY metrics, not FUNCTIONAL CORRECTNESS. This is precisely the gap H-E1 tests.

**Repository 6: FeedbackEval (arxiv 2504.06939)**
- **Relevance:** MEDIUM — Compares test feedback vs compiler feedback vs human feedback on HumanEval. Most similar to our comparison but uses GPT-4o/Claude-3.5/etc. and does NOT include pylint/mypy as a condition. Validates that test feedback > compiler feedback.

**Serena Analysis Needed:** false — no local codebase to analyze. Code from search results is sufficiently clear.

### 🎯 Implementation Priority Assessment

**CRITICAL: No paper author official implementation for the pylint feedback condition exists — this is a novel experiment.**

- The execution repair framework: Use `Johin2/iterative-code-repair` as the base infrastructure (HumanEval/MBPP loading, sandboxed execution, greedy decoding setup).
- The pylint layer: Adapt `cyb3rlab/CodeEnhancer`'s pylint integration pattern, but replace security benchmark with HumanEval/MBPP and replace pass@k metric with functional correctness via unit test execution.
- Fallback: Implement custom 50-100 line pylint wrapper (per Phase 2B Assumption A4 fallback plan).

**Recommended Implementation Path:**
- Primary: Adapt Johin2/iterative-code-repair infrastructure + add pylint feedback layer (replacing execution traceback with pylint/mypy output in repair prompt)
- Fallback: Custom pylint wrapper with HumanEval/MBPP loaders from `openai/openai_humaneval` (HuggingFace)
- Justification: Johin2 provides validated HumanEval/MBPP infrastructure, greedy decoding, sandboxed execution, and pass@1 computation — only the feedback signal changes for H-E1 (pylint instead of execution traceback)

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. No local codebase to analyze. All key patterns extracted directly from Exa search results.

---

## Experiment Specification

### Dataset

**Dataset 1: HumanEval**
- **Name:** HumanEval
- **Version:** v2 (human-eval-v2-20210705.jsonl)
- **Source:** Chen et al. 2021 — openai/human-eval GitHub repo
- **HuggingFace:** `openai/openai_humaneval`
- **Problems:** 164 algorithmic Python problems
- **Format:** Each problem has: task_id, prompt (function signature + docstring), canonical_solution, test (unit tests), entry_point
- **Splits:** No train/val split — all 164 used as test set (standard evaluation protocol)
- **Evaluation:** `evaluate_functional_correctness` from human-eval package
- **Type:** standard ✅ (real dataset, not synthetic)

**Dataset 2: MBPP**
- **Name:** MBPP (Mostly Basic Python Problems)
- **Version:** Sanitized subset (374 problems per Phase 2B specification; note: Johin2 uses 257 sanitized, full MBPP is 374 — we use full 374 per Phase 2B)
- **Source:** Austin et al. 2021 — google-research/mbpp GitHub repo
- **HuggingFace:** `evalplus/mbppplus` or `google-research-datasets/mbpp`
- **Problems:** 374 problems (full standard test set per Phase 2B Section 1.3)
- **Format:** Each problem has: task_id, text (natural language description), code (reference solution), test_list (unit test assertions), test_setup_code, challenge_test_list
- **Splits:** Full set used for evaluation
- **Evaluation:** Execute code against test_list assertions
- **Type:** standard ✅ (real dataset, not synthetic)

**Total Evaluation Scale:** 538 problems × 2 conditions (no-feedback baseline + pylint repair) × 1 model (Llama 3.1 8B) = 1,076 problem-condition evaluations for H-E1

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + evalplus pip package
- Identifier HumanEval: `"openai/openai_humaneval"` or `pip install evalplus` then `evalplus.data.get_human_eval_plus()`
- Identifier MBPP: `"evalplus/mbppplus"` or `evalplus.data.get_mbpp_plus()`
- Code:
  ```python
  # Option A: HuggingFace datasets
  from datasets import load_dataset
  humaneval = load_dataset("openai/openai_humaneval", split="test")
  mbpp = load_dataset("evalplus/mbppplus", split="test")
  
  # Option B: evalplus package (recommended — includes augmented tests)
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  humaneval_problems = get_human_eval_plus()  # dict: task_id -> problem
  mbpp_problems = get_mbpp_plus()             # dict: task_id -> problem
  ```

### Models

#### Baseline Model

**Architecture:** Llama 3.1 8B Instruct
- **Type:** Open-source instruction-tuned decoder-only transformer (dense, 8B parameters)
- **Source:** Meta AI — HuggingFace: `meta-llama/Llama-3.1-8B-Instruct`
- **Configuration:**
  - Decoding: Greedy (temperature=0, do_sample=False)
  - Token budget: B=1000 output tokens total per problem across all repair rounds
  - Random seed: 42
  - Max repair rounds: 3 (within B=1000 token budget)
- **Known baseline:** 67.1% pass@1 on HumanEval (single-shot, greedy) — Arimbur 2026
- **Hypothesis Fit:** 7B-scale instruction-tuned; Arimbur 2026 confirms this model follows repair instructions with prompting alone at 8B scale

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers (local inference) or Groq API (remote inference)
- Identifier: `"meta-llama/Llama-3.1-8B-Instruct"`
- Code:
  ```python
  # Option A: Local inference (transformers)
  from transformers import AutoTokenizer, AutoModelForCausalLM
  import torch
  
  model_name = "meta-llama/Llama-3.1-8B-Instruct"
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  model = AutoModelForCausalLM.from_pretrained(
      model_name, torch_dtype=torch.bfloat16, device_map="auto"
  )
  
  # Option B: Groq API (matches Johin2 implementation)
  from groq import Groq
  client = Groq()
  response = client.chat.completions.create(
      model="llama-3.1-8b-instant",
      messages=[{"role": "user", "content": prompt}],
      temperature=0.0,
      max_tokens=1000
  )
  ```

#### Proposed Model

**Architecture:** Llama 3.1 8B Instruct + pylint/mypy feedback loop

**Core Mechanism Implementation:**

```python
# Core Mechanism: Pylint/Mypy Iterative Repair Loop for H-E1
# Based on: cyb3rlab/CodeEnhancer + Johin2/iterative-code-repair patterns
# Token budget: B=1000 total output tokens per problem

import subprocess, tempfile, os

def run_pylint_mypy(code: str) -> str:
    """Run pylint + mypy on code, return formatted feedback string."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code); tmp_path = f.name
    try:
        # Run pylint
        pylint_out = subprocess.run(
            ["pylint", "--output-format=text", "--score=no", tmp_path],
            capture_output=True, text=True, timeout=30
        ).stdout.strip()
        # Run mypy
        mypy_out = subprocess.run(
            ["mypy", "--ignore-missing-imports", tmp_path],
            capture_output=True, text=True, timeout=30
        ).stdout.strip()
        feedback = ""
        if pylint_out: feedback += f"Pylint:\n{pylint_out}\n"
        if mypy_out and "Success" not in mypy_out: feedback += f"Mypy:\n{mypy_out}\n"
        return feedback.strip() if feedback.strip() else None  # None = no issues
    finally:
        os.unlink(tmp_path)

def pylint_repair_loop(problem: dict, model, tokenizer, B: int = 1000) -> dict:
    """Iterative pylint/mypy repair within token budget B."""
    code = generate_code(problem, model, tokenizer)  # Round 0: initial generation
    tokens_used = count_tokens(code)
    round_results = [{"round": 0, "code": code, "passed": evaluate(code, problem)}]
    
    repair_round = 1
    while tokens_used < B:
        feedback = run_pylint_mypy(code)
        if feedback is None:
            break  # No pylint/mypy issues — stop repair
        remaining = B - tokens_used
        repair_prompt = build_pylint_repair_prompt(problem, code, feedback)
        repaired_code = generate_code_with_budget(repair_prompt, model, tokenizer, remaining)
        tokens_used += count_tokens(repaired_code)
        code = repaired_code
        round_results.append({
            "round": repair_round, "code": code,
            "passed": evaluate(code, problem), "feedback": feedback
        })
        repair_round += 1
    
    return {"final_code": code, "passed": evaluate(code, problem), "rounds": round_results}
```

### Training Protocol

**Note:** H-E1 is an INFERENCE-ONLY experiment. No model training occurs. Llama 3.1 8B Instruct is used as-is (pretrained weights). The "training protocol" below describes the inference configuration.

**Inference Configuration:**
- **Model:** Llama 3.1 8B Instruct (frozen pretrained weights, no fine-tuning)
- **Decoding:** Greedy (temperature=0.0, do_sample=False)
  - Source: Arimbur 2026 — uses temperature=0.0 for reproducibility
- **Token Budget:** B=1000 total output tokens per problem (across all repair rounds)
  - Source: Phase 2B Section 1.3 controlled variables
  - Rationale: HumanEval solutions ~50-200 lines; allows 2-3 repair rounds at typical generation lengths
- **Max Repair Rounds:** 3 (within B=1000 budget constraint)
  - Source: Phase 2B Verification Protocol step 2
- **Seed:** 42
- **Prompt Template:**
  ```
  Round 0 (initial generation):
  Complete the following Python function:
  {problem_prompt}
  
  Repair rounds (pylint feedback):
  The following Python code has static analysis issues:
  {previous_code}
  
  Static analysis feedback:
  {pylint_mypy_output}
  
  Please fix the code to address these issues while maintaining functional correctness.
  Return only the corrected function.
  ```
- **Code Extraction:** Extract Python function from model output (strip markdown fences, extract function body)
  - Source: Johin2/iterative-code-repair `self_repair.py` — handles markdown fences, unclosed fences, chain-of-thought traces
- **Execution Sandbox:** Isolated Python subprocess with 15-second timeout per test case
  - Source: Arimbur 2026 experimental setup
- **Seeds:** 1 (fixed at 42)
  - Note: Single seed sufficient for PoC (greedy decoding is deterministic)

### Evaluation

**Primary Metrics:**
- **Δ_pylint:** pass@1(pylint_condition) - pass@1(no_feedback_baseline)
  - Computed separately for HumanEval and MBPP
  - Expected range: -5pp to +10pp (highly uncertain — this is what we're measuring)
  - Known baseline: 67.1% pass@1 on HumanEval (Llama 3.1 8B, single-shot, Arimbur 2026)
- **pass@1(pylint_condition):** Fraction of problems where final repaired code passes all unit tests
- **pass@1(no_feedback_baseline):** Fraction of problems solved on single-shot generation (greedy)
- **Per-round pass@1:** pass@1 after each repair round (rounds 0, 1, 2, 3) to track improvement trajectory
- **Pylint Coverage Fraction:** Fraction of no-feedback baseline failures that receive ≥1 pylint/mypy warning/error (pre-execution; supports H-M2 mechanistic analysis)

**Success Criteria (PoC):**
1. Code runs without error (pylint repair loop executes end-to-end on all 538 problems)
2. Δ_pylint is finite and computable (not NaN, not undefined)
3. Secondary: |Δ_pylint| > 0 on at least one benchmark (any measurable effect, positive or negative)

**Expected Baseline Performance** (from Exa research):
- HumanEval no-feedback baseline (Llama 3.1 8B): ~67.1% pass@1 (Arimbur 2026)
- MBPP no-feedback baseline (Llama 3.1 8B): ~55.6% pass@1 (Arimbur 2026, sanitized 257 — full 374 may differ slightly)
- Execution self-repair delta HumanEval: +9.8pp (Arimbur 2026, upper reference bound)
- Pylint functional correctness delta: UNKNOWN (novel contribution of this experiment)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Code generation functional correctness (pass@1)
- Library: `openai/human-eval` package (`evaluate_functional_correctness`) + custom MBPP evaluator
- Code:
  ```python
  # HumanEval evaluation
  from human_eval.evaluation import evaluate_functional_correctness
  # Write results to JSONL, then:
  results = evaluate_functional_correctness("results.jsonl", problem_file="HumanEval_v2.jsonl")
  
  # MBPP evaluation (custom — execute test assertions)
  def evaluate_mbpp(code: str, test_list: list) -> bool:
      namespace = {}
      try:
          exec(code, namespace)
          for test in test_list:
              exec(test, namespace)
          return True
      except Exception:
          return False
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Δ_pylint Comparison Bar Chart:** Show pass@1 for no-feedback baseline vs pylint repair condition on HumanEval and MBPP (2 benchmarks × 2 conditions = 4 bars)

#### Additional Figures (LLM Autonomous)
- **Per-Round Improvement Trajectory:** Line plot of cumulative pass@1 after each repair round (rounds 0-3) for pylint condition on both benchmarks
- **Token Budget Distribution:** Histogram of total tokens used per problem (shows how many problems exhaust B=1000 budget at each round)
- **Pylint Coverage Analysis:** Bar chart showing fraction of baseline failures flagged by pylint (Error/Warning/Convention categories) vs not flagged — mechanistic evidence for H-M2

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (pylint repair loop executes on all 538 problems without crashing)
2. `Δ_pylint is computable` (finite value, not systematic failure)

**Gate (MUST_WORK):** If pylint wrapper fails to execute on ≥50% of problems due to infrastructure issues → PIVOT to custom 50-100 line wrapper per Phase 2B fallback plan.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB Assessment:** No relevant past cases found in Archon KB for LLM code repair domain. KB contents are primarily focused on diffusion models and image generation. All experiment design grounded in Exa GitHub research and Phase 2B literature.

### B. GitHub Implementations (Exa)

**Repository 1: Johin2/iterative-code-repair** ⭐ PRIMARY REFERENCE
- **URL:** https://github.com/Johin2/iterative-code-repair
- **Paper:** arxiv 2604.10508 (Arimbur 2026) — "How Many Tries Does It Take? Iterative Self-Repair in LLM Code Generation Across Model Scales and Benchmarks"
- **Query Used:** "LLM code generation iterative self-repair execution feedback pass@1 HumanEval evaluation Python"
- **Relevance:** Exact paper cited in Phase 2B. Validates Llama 3.1 8B can follow repair instructions at 8B scale with prompting alone. Provides infrastructure for HumanEval/MBPP loading, sandboxed execution, and pass@1 computation.
- **Key Protocol Extracted:**
  - Data: HumanEval (164) + MBPP Sanitized (257) via data_loader.py
  - Model: greedy decoding (temperature=0.0), Groq API for open-weight models
  - Execution: sandboxed Python subprocess, 15-second timeout per test case
  - Repair loop: problem + previous code + error message → repair prompt → new code
- **Results Used:** Llama 3.1 8B baseline 67.1% HumanEval (used as expected baseline in experiment design)
- **Used For:** Baseline performance expectations, protocol design, infrastructure reference

**Repository 2: cyb3rlab/CodeEnhancer** ⭐ PYLINT REFERENCE
- **URL:** https://github.com/cyb3rlab/CodeEnhancer
- **Query Used:** "iterative code repair LLM pylint feedback HumanEval MBPP Python implementation GitHub"
- **Relevance:** Directly referenced in Phase 2B (Assumption A4). Provides pylint + Bandit iterative validation loop. Key adaptation target for H-E1 pylint condition.
- **Key Code Pattern:** pylint subprocess call → parse output → format feedback → LLM repair → repeat (max 5 iterations)
- **Limitation:** Uses security-focused datasets (not HumanEval/MBPP). Needs HumanEval/MBPP loader and pass@1 metric substitution.
- **Used For:** Pylint/mypy integration pattern in core mechanism pseudocode

**Repository 3: NEUIR/INTERVENOR (ACL 2024)**
- **URL:** https://github.com/NEUIR/INTERVENOR
- **Query Used:** "iterative code repair LLM pylint feedback HumanEval MBPP Python"
- **Relevance:** Shows HumanEval/MBPP multi-round repair with execution feedback. Confirms `evaluate_functional_correctness` from human-eval package for evaluation.
- **Used For:** HumanEval evaluation methodology reference

**Repository 4: Static Analysis as Feedback Loop (arxiv 2508.14419 — Blyth et al. 2025)**
- **URL:** https://arxiv.org/html/2508.14419v1
- **Relevance:** Pylint/Bandit iterative repair on PythonSecurityEval. Uses SelectIssues strategy (I issues per iteration). Demonstrates pylint reduces code quality violations but on security benchmark, not functional correctness.
- **Key Finding:** Pylint reduces readability >80%→11%, reliability >50%→11% — but these are static analysis metrics, not pass@k. This is the gap our experiment measures.
- **Used For:** Pylint feedback loop algorithm design; justification for why pylint effect on functional correctness is unknown

**Repository 5: EvalPlus (evalplus/evalplus)**
- **URL:** https://github.com/evalplus/evalplus + https://huggingface.co/datasets/evalplus/mbppplus
- **Relevance:** Rigorous HumanEval+/MBPP+ evaluation framework. Provides HuggingFace dataset loading.
- **Used For:** Dataset loading code (evalplus package approach)

**Repository 6: FeedbackEval (arxiv 2504.06939)**
- **Relevance:** Compares test feedback vs compiler feedback vs human feedback on HumanEval. Closest prior work. Does NOT include pylint/mypy as a condition. Validates test feedback produces highest repair success.
- **Used For:** Research gap justification; confirms pylint/mypy is unstudied on functional correctness

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear for pseudo-code generation. No local codebase to analyze via Serena.

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first (foundation) hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (HumanEval 164 + MBPP 374) | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Dataset loading (HuggingFace + evalplus) | GitHub/Exa | EvalPlus repo + openai/openai_humaneval |
| Model (Llama 3.1 8B Instruct) | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Model loading (Groq API / HuggingFace) | GitHub/Exa | Johin2/iterative-code-repair config.py |
| Baseline pass@1 (67.1% HumanEval) | GitHub/Exa | Johin2/iterative-code-repair Table I |
| Greedy decoding (temperature=0.0) | GitHub/Exa | Johin2/iterative-code-repair experiments/run_experiment.py |
| Token budget B=1000 | Phase 2B | 02b_verification_plan.md controlled_variables |
| Max repair rounds: 3 | Phase 2B | Verification Protocol step 2 |
| Pylint subprocess pattern | GitHub/Exa | cyb3rlab/CodeEnhancer code_validator.py |
| Mypy integration | GitHub/Exa | MarcusJellinghaus/mcp-tools-py |
| Pylint repair prompt structure | GitHub/Exa | tejaskhot/patchwork lint tool |
| Sandboxed execution (subprocess, 15s timeout) | GitHub/Exa | Johin2/iterative-code-repair code_executor.py |
| HumanEval evaluation (evaluate_functional_correctness) | GitHub/Exa | NEUIR/INTERVENOR + human-eval package |
| MBPP evaluation (test_list assertion execution) | Phase 2B | Standard MBPP evaluation protocol |
| Pylint coverage analysis metric | Phase 2B | Verification Protocol step 4 (H-M2 pre-analysis) |
| Token budget tracking | Phase 2B | Assumption A3 — verify B=1000 allows ≥2 rounds |
| Pseudo-code design | GitHub/Exa | CodeEnhancer + Johin2 patterns combined |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05

### Workflow History for This Hypothesis
- 2026-08-05T04:44:29Z — h-e1 set to IN_PROGRESS (external hypothesis loop starting Phase 2C)
- 2026-08-05 — Phase 2C experiment design initiated (UNATTENDED mode)
- 2026-08-05 — Step 1: State loaded, JIT context generated from 02b_verification_plan.md
- 2026-08-05 — Step 2: Archon KB searched (3 queries) — no relevant past cases found
- 2026-08-05 — Step 3: Exa GitHub searched (2 queries) — 6 relevant repositories found
- 2026-08-05 — Step 4: Serena skipped (no complex code requiring analysis)
- 2026-08-05 — Step 5: Dataset confirmed (HumanEval 164 + MBPP 374, both standard real datasets ✅)
- 2026-08-05 — Step 6: Experiment specification synthesized
- 2026-08-05 — Step 7: References compiled with traceability matrix
- 2026-08-05 — Step 8: Quality validation and state update

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub — 6 repositories found), Serena (Code Analysis — skipped)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
