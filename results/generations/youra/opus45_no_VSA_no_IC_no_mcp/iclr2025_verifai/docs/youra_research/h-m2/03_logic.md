# Logic: H-M2 (MECHANISM)

**Applied**: McNemar paired-binary test pattern for causal ablation (Archon KB: DL API design patterns — standard PyTorch/scipy statistical testing, no deep-learning-specific pattern needed; this is inference + stats, not model training).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1)
**Status**: Serena unavailable — verified actual API signatures by reading H-E1 code files directly.
**Analyzed Path**: `docs/youra_research/h-e1/code/errors.py`, `models.py`, `prompts.py`, `repair_loop.py`
**Relevant Symbols**: `StructuredError` (dataclass), `parse_compiler_output`, `format_structured_prompt`, `format_raw_prompt`, `load_hf_model`, `generate_code`, `execute_and_check`, `extract_code_block`, `initial_prompt`, `repair_problem`

**Critical correction vs 03_architecture.md**: architecture doc lists `format_structured_prompt`/`extract_code_block`/`initial_prompt` as importable from `repair_loop.py`. Actual code: `format_structured_prompt`/`format_raw_prompt` live in **`prompts.py`** (imported by `repair_loop.py`, not re-exported elsewhere); `extract_code_block`/`initial_prompt`/`execute_and_check` are correctly in `repair_loop.py`. **`prompts.py` must also be copied into `h-m2/code/`** (architecture's file list omitted it). `StructuredError` fields are `line_number: int, error_type: str, error_message: str, code_context: List[str]` — no free-form "root cause" field exists; H-M2's `to_sections()` must derive ROOT_CAUSE text from `error_type` + `error_message` (no separate LLM call).

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/errors.py (ACTUAL CODE)
@dataclass
class StructuredError:
    line_number: int
    error_type: str
    error_message: str
    code_context: List[str]

def parse_compiler_output(raw_output: str, source_code: str) -> StructuredError: ...

# From: h-e1/code/prompts.py (ACTUAL CODE) — NOT in repair_loop.py!
def format_structured_prompt(error: StructuredError, original_code: str) -> str: ...
def format_raw_prompt(raw_output: str, original_code: str) -> str: ...

# From: h-e1/code/models.py (ACTUAL CODE)
def load_hf_model(model_id: str): ...  # returns (model, tokenizer)
def generate_code(model_ref, tokenizer, prompt: str, is_openai: bool = False,
                   max_new_tokens: int = None, temperature: float = None) -> str: ...

# From: h-e1/code/repair_loop.py (ACTUAL CODE)
def execute_and_check(code: str, problem: Dict) -> Tuple[bool, str]: ...
def extract_code_block(text: str) -> str: ...
def initial_prompt(problem: Dict) -> str: ...
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation). Copy `errors.py`, `models.py`, `prompts.py`, `repair_loop.py` verbatim into `h-m2/code/` (repair_loop.py's own `from prompts import ...` line then resolves locally, no path hacks).

---

## M2-1: Port H-E1 infra [Complexity: 5, Budget: 5]

**Applied**: Standard PyTorch (no new logic, file copy + config)

### API Signatures

```python
# config.py (new)
CONFIG = {
    "base_model_id": "codellama/CodeLlama-7b-Instruct-hf",
    "temperature": 0.8, "top_p": 0.95, "max_new_tokens": 512,
    "min_samples": 500, "bootstrap_replicas": 10000, "significance_alpha": 0.05,
    "sections": ["PROBLEM", "LOCATION", "CONTEXT", "ROOT_CAUSE"],
    "exec_timeout_sec": 5,
    "failed_samples_path": "data/failed_samples.json",
    "results_path": "data/paired_results.json",
    "figures_dir": "outputs/figures/",
}
```

### Subtasks [4/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-1-1 | Copy base files | errors.py, models.py, prompts.py, repair_loop.py -> h-m2/code/ verbatim |
| L-M2-1-2 | Write config.py | Dict above, no class needed |
| L-M2-1-3 | Adjust models.py CONFIG usage | Confirm max_new_tokens/temperature keys match local config.py |
| L-M2-1-4 | Smoke import test | `python -c "from repair_loop import execute_and_check"` in h-m2/code/ |

---

## M2-2: Implement sections.py [Complexity: 9, Budget: 9]

**Applied**: Standard PyTorch (pure Python, no tensors)

### API Signatures

```python
from errors import StructuredError
import random

def to_sections(error: StructuredError, original_code: str) -> list[tuple[str, str]]:
    """PROBLEM=error_message, LOCATION=f'Line {line_number}', CONTEXT='\n'.join(code_context),
    ROOT_CAUSE=error_type. No new LLM call — derived from existing StructuredError fields."""
    ...

def format_sections(sections: list[tuple[str, str]], original_code: str) -> str:
    """Render '## {NAME}\n{content}\n\n' per section, then '## Full Code:\n```python\n{original_code}\n```\n\nProvide the corrected complete code:'"""
    ...

def scramble_sections(sections: list[tuple[str, str]], seed: int) -> list[tuple[str, str]]:
    """random.Random(seed).shuffle on a copy; content unchanged, order only."""
    rng = random.Random(seed)
    out = sections.copy()
    rng.shuffle(out)
    return out

def format_structured_prompt(error: StructuredError, original_code: str) -> str:
    return format_sections(to_sections(error, original_code), original_code)

def format_scrambled_prompt(error: StructuredError, original_code: str, seed: int) -> str:
    return format_sections(scramble_sections(to_sections(error, original_code), seed), original_code)
```

**Note**: Shadows name `format_structured_prompt` from H-E1's `prompts.py` intentionally — H-M2 uses its own 4-section version (PRD FR-2.1), not H-E1's 3-section one. Do not import H-E1's `format_structured_prompt` in `sections.py`; import only `StructuredError`.

### Tensor Shapes

N/A — pure string/list operations, no tensors.

### Subtasks [8/9 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-2-1 | to_sections | Map StructuredError fields to 4 fixed-name tuples |
| L-M2-2-2 | format_sections | Deterministic section-name headers + code footer |
| L-M2-2-3 | scramble_sections | Seeded shuffle, copy-safe (no in-place mutation of input) |
| L-M2-2-4 | format_structured_prompt/format_scrambled_prompt | Thin wrappers per API above |
| L-M2-2-5 | Content-equivalence check | Assert `sorted(sections) == sorted(scrambled)` in a test |
| L-M2-2-6 | Per-sample seed derivation | seed = hash(sample_id) % 2**32 in dataset.py caller, not here |
| L-M2-2-7 | Edge case: empty code_context | to_sections handles `code_context=[]` -> CONTEXT="" |
| L-M2-2-8 | Unit test file | test_sections.py: assert scramble != order but same set |

---

## M2-3: Implement dataset.py loading [Complexity: 10, Budget: 10]

**Applied**: Standard PyTorch (HF inference loop, batching optional)

### API Signatures

```python
def load_benchmark_problems() -> list[dict]:
    """evalplus.data.get_human_eval_plus() + get_mbpp_plus(); each dict tagged
    problem['source'] = 'humaneval' | 'mbpp'. Returns 164+378=542 problems."""
    ...

def collect_failed_samples(model_ref, tokenizer, problems: list[dict],
                            min_samples: int) -> list[dict]:
    """For each problem: initial_prompt -> generate_code -> extract_code_block ->
    execute_and_check. On failure, parse_compiler_output(raw_error, code); keep
    {'id', 'problem': problem, 'code': code, 'error': StructuredError-as-dict}
    until len(kept) >= min_samples or problems exhausted."""
    ...

def save_failed_samples(samples: list[dict], out_path: str) -> None: ...
def load_failed_samples(path: str) -> list[dict]: ...
```

### Pseudo-code (collect_failed_samples)

```
1. kept = []
2. for problem in problems:
3.     if len(kept) >= min_samples: break
4.     code = extract_code_block(generate_code(model_ref, tok, initial_prompt(problem)))
5.     passed, raw_error = execute_and_check(code, problem)
6.     if not passed:
7.         err = parse_compiler_output(raw_error, code)
8.         kept.append({id, problem, code, error: asdict(err)})
9. return kept
```

### Subtasks [7/10 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-3-1 | load_benchmark_problems | evalplus get_human_eval_plus/get_mbpp_plus, tag source |
| L-M2-3-2 | collect_failed_samples loop | Sequential generation + failure filtering |
| L-M2-3-3 | StructuredError JSON serialization | dataclasses.asdict for save, reconstruct on load |
| L-M2-3-4 | save_failed_samples / load_failed_samples | json.dump/load, create parent dirs |
| L-M2-3-5 | Resume/skip-if-exists check | run_poc.py calls load_failed_samples if path exists |
| L-M2-3-6 | Min-samples shortfall handling | If <500 after full pass, log warning, proceed with what's collected |
| L-M2-3-7 | Unique id assignment | `f"{problem['source']}_{idx}"` |

---

## M2-4: Implement experiment.py paired repair [Complexity: 10, Budget: 10]

**Applied**: Standard PyTorch (single forward-generate call per condition)

### API Signatures

```python
from sections import format_structured_prompt, format_scrambled_prompt

def run_repair(model_ref, tokenizer, sample: dict, prompt: str) -> bool:
    """generate_code -> extract_code_block -> execute_and_check -> bool passed."""
    code = extract_code_block(generate_code(model_ref, tokenizer, prompt))
    passed, _ = execute_and_check(code, sample["problem"])
    return passed

def run_paired_condition(model_ref, tokenizer, sample: dict, seed: int) -> dict:
    """Returns {'id', 'structured_passed', 'scrambled_passed', 'scramble_seed'}."""
    err = StructuredError(**sample["error"])
    s_prompt = format_structured_prompt(err, sample["code"])
    sc_prompt = format_scrambled_prompt(err, sample["code"], seed)
    return {
        "id": sample["id"],
        "structured_passed": run_repair(model_ref, tokenizer, sample, s_prompt),
        "scrambled_passed": run_repair(model_ref, tokenizer, sample, sc_prompt),
        "scramble_seed": seed,
    }

def run_all_paired(model_ref, tokenizer, samples: list[dict]) -> list[dict]:
    """seed = hash(sample['id']) % 2**32 per sample; sequential loop."""
    ...
```

### Subtasks [7/10 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-4-1 | run_repair | Single-attempt generate+check (no multi-turn loop, unlike H-E1's repair_problem) |
| L-M2-4-2 | run_paired_condition | Both conditions on same sample, same base code |
| L-M2-4-3 | run_all_paired loop + seed derivation | Deterministic per-sample seed via hash |
| L-M2-4-4 | Order-bias mitigation | Randomize which condition (structured/scrambled) runs first per sample using seed |
| L-M2-4-5 | Progress checkpointing | Append each result to paired_results.json incrementally (crash-safe) |
| L-M2-4-6 | Error isolation | try/except around each run_repair call; treat exceptions as failed=False |
| L-M2-4-7 | temperature/top_p wiring | Pass CONFIG["temperature"]/top_p into generate_code call |

---

## M2-5: Implement analysis.py [Complexity: 11, Budget: 11]

**Applied**: Standard PyTorch (scipy.stats.mcnemar-style contingency table, no torch needed)

### API Signatures

```python
def analyze_structure_effect(paired_results: list[dict]) -> dict:
    """McNemar chi2 (scipy.stats.contingency or manual 2x2) + bootstrap CI
    (10k resamples of paired deltas) + Cohen's d. Returns:
    {structured_rate, scrambled_rate, delta, p_value, ci_95: (lo, hi),
     discordant_structured_wins, discordant_scrambled_wins, cohens_d, gate_pass}"""
    ...

def gate_check(results: dict, alpha: float) -> bool:
    """True iff delta > 0 and p_value < alpha and ci_95[0] > 0."""
    return results["delta"] > 0 and results["p_value"] < alpha and results["ci_95"][0] > 0
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| structured | [N] bool array | pass/fail per sample |
| scrambled | [N] bool array | pass/fail per sample |
| bootstrap_deltas | [10000] float | resampled rate differences |

### Pseudo-code

```
1. structured = [r['structured_passed'] for r in paired_results]
2. scrambled  = [r['scrambled_passed'] for r in paired_results]
3. b = sum(s and not c for s,c in zip(structured, scrambled))  # struct wins
4. c = sum(c and not s for s,c in zip(structured, scrambled))  # scrambled wins
5. chi2, p_value = mcnemar_stat(b, c)  # exact binomial if b+c<25 else chi2 with continuity correction
6. deltas = bootstrap_resample(structured, scrambled, n=10000)  # paired resample with replacement
7. ci_95 = (percentile(deltas, 2.5), percentile(deltas, 97.5))
8. cohens_d = (mean(structured) - mean(scrambled)) / pooled_std
9. gate_pass = delta > 0 and p_value < 0.05 and ci_95[0] > 0
```

### Subtasks [8/11 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-5-1 | Contingency table (b, c) | Discordant pair counts from paired bool lists |
| L-M2-5-2 | McNemar p-value | scipy.stats binomtest(b, b+c) if b+c<25 else chi2 continuity-corrected |
| L-M2-5-3 | Bootstrap resampling loop | 10000 paired resamples, delta distribution |
| L-M2-5-4 | Percentile CI | np.percentile(deltas, [2.5, 97.5]) |
| L-M2-5-5 | Cohen's d | Pooled-std formula on binary rates |
| L-M2-5-6 | analyze_structure_effect assembly | Combine into single dict per spec |
| L-M2-5-7 | gate_check | Three-condition boolean per PRD Gate Pass |
| L-M2-5-8 | Unit test | Synthetic paired data with known b,c -> assert p_value matches scipy reference |

---

## M2-6: Implement visualize.py [Complexity: 6, Budget: 6]

**Applied**: Standard PyTorch (matplotlib only, no DL-specific pattern)

### API Signatures

```python
def plot_gate_comparison(results: dict, out_path: str = None) -> None:
    """Bar chart: structured_rate vs scrambled_rate with 95% CI error bars."""
    ...

def plot_discordant_pairs(results: dict, out_path: str = None) -> None:
    """Bar chart: discordant_structured_wins vs discordant_scrambled_wins."""
    ...
```

### Subtasks [4/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-6-1 | plot_gate_comparison | matplotlib bar + errorbar from ci_95 |
| L-M2-6-2 | plot_discordant_pairs | matplotlib bar, two categories |
| L-M2-6-3 | Save-to-path handling | mkdir -p CONFIG["figures_dir"]; savefig if out_path given |
| L-M2-6-4 | Style consistency | Reuse H-E1/H-M1 color scheme if present, else default matplotlib |

---

## M2-7: Implement run_poc.py orchestration [Complexity: 8, Budget: 8]

**Applied**: Standard PyTorch (pipeline orchestration script)

### API Signatures

```python
def main() -> None:
    """load_hf_model -> load or collect failed samples -> run_all_paired ->
    analyze_structure_effect -> gate_check -> save paired_results.json -> figures."""
    ...

if __name__ == "__main__":
    main()
```

### Pseudo-code

```
1. model, tok = load_hf_model(CONFIG["base_model_id"])
2. if exists(CONFIG["failed_samples_path"]): samples = load_failed_samples(...)
3. else: problems = load_benchmark_problems(); samples = collect_failed_samples(model, tok, problems, CONFIG["min_samples"]); save_failed_samples(samples, ...)
4. paired = run_all_paired(model, tok, samples)
5. save paired to CONFIG["results_path"]
6. results = analyze_structure_effect(paired)
7. results["gate_pass"] = gate_check(results, CONFIG["significance_alpha"])
8. save results (json) alongside paired_results.json
9. plot_gate_comparison(results); plot_discordant_pairs(results)
10. print gate_pass and key metrics
```

### Subtasks [5/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-7-1 | main() skeleton | Wire steps 1-3 (model + data load/collect) |
| L-M2-7-2 | main() experiment+analysis | Wire steps 4-8 (run_all_paired, analyze, gate_check, save) |
| L-M2-7-3 | main() visualization | Wire step 9 (both plots) |
| L-M2-7-4 | CLI entrypoint | `if __name__ == "__main__"` + optional argparse for --resume |
| L-M2-7-5 | Result JSON schema | Ensure both paired_results.json and analysis results saved distinctly |

---

## M2-8: Gate verification + logging [Complexity: 5, Budget: 5]

**Applied**: Standard PyTorch (assertions + logging only)

### API Signatures

```python
def mechanism_log_message(results: dict) -> str:
    """One-line summary: 'H-M2 gate={pass/fail} delta={:.3f} p={:.4f} ci=({:.3f},{:.3f})'"""
    ...

def verify_representational_alignment(results: dict) -> None:
    """Asserts required keys present in results dict; raises AssertionError with
    field name if any of structured_rate/scrambled_rate/delta/p_value/ci_95/gate_pass missing."""
    ...
```

### Subtasks [4/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-8-1 | mechanism_log_message | Format string per spec, called at end of run_poc.main |
| L-M2-8-2 | verify_representational_alignment | Assert all required result dict keys exist and are correct types |
| L-M2-8-3 | Wire into run_poc.py | Call verify then log before script exit |
| L-M2-8-4 | Non-zero exit on gate fail | `sys.exit(1)` if `not results["gate_pass"]` for CI integration |
