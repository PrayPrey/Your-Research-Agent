# Architecture: H-M2 (MECHANISM)

**Applied**: Paired A/B ablation with content-preserving control (McNemar paired-binary pattern)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1/H-M1)
**Status**: Serena MCP unavailable this session; read H-E1/H-M1 code directly via file tools.
**Analyzed Path**: `docs/youra_research/h-e1/code/`, `docs/youra_research/h-m1/code/`
**Findings**: H-E1 has working `StructuredError` dataclass (`errors.py`), `format_structured_prompt`/`format_raw_prompt` (`prompts.py`), `generate_code`/`load_hf_model` (`models.py`), and a full `repair_problem` self-repair loop (`repair_loop.py`) using `execute_and_check` for pass/fail. H-M1's `03_architecture.md` referenced `format_structured_prompt` from H-E1 correctly. H-M2 reuses `errors.py`, `models.py`, `repair_loop.py` (execute_and_check, extract_code_block) almost unchanged; only the prompt-formatting step needs a new `format_scrambled_prompt` and a section-scrambler. Note: H-E1's `format_structured_prompt` hardcodes 3 sections (Error Info/Code Context/Full Code), not the PRD's 4-section PROBLEM/LOCATION/CONTEXT/ROOT_CAUSE layout — H-M2 must define its own 4-section formatter matching PRD FR-2.1, built from `StructuredError` fields, rather than reuse H-E1's prompt format verbatim.

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| StructuredError, parse_compiler_output | `from errors import StructuredError, parse_compiler_output` | `h-e1/code/errors.py` |
| generate_code, load_hf_model | `from models import generate_code, load_hf_model` | `h-e1/code/models.py` |
| execute_and_check, extract_code_block, initial_prompt | `from repair_loop import execute_and_check, extract_code_block, initial_prompt` | `h-e1/code/repair_loop.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

Copy these three files verbatim into `h-m2/code/` (no cross-folder imports) rather than adding sys.path hacks.

## File Organization

- `h-m2/code/errors.py` (copied from H-E1)
- `h-m2/code/models.py` (copied from H-E1)
- `h-m2/code/repair_loop.py` (copied from H-E1, reused helpers only)
- `h-m2/code/config.py` (new)
- `h-m2/code/sections.py` (new — 4-section format + scrambling)
- `h-m2/code/dataset.py` (new — EvalPlus loading + failure collection)
- `h-m2/code/experiment.py` (new — paired repair execution)
- `h-m2/code/analysis.py` (new — McNemar + bootstrap)
- `h-m2/code/visualize.py` (new)
- `h-m2/code/run_poc.py` (new — orchestration)
- `h-m2/data/failed_samples.json` (generated)
- `h-m2/data/paired_results.json` (generated)

## Modules

### config.py (`h-m2/code/config.py`)

**Dependencies**: none

```python
CONFIG = {
    "base_model_id": "codellama/CodeLlama-7b-Instruct-hf",
    "temperature": 0.8,
    "top_p": 0.95,
    "max_new_tokens": 512,
    "min_samples": 500,
    "bootstrap_replicas": 10000,
    "significance_alpha": 0.05,
    "sections": ["PROBLEM", "LOCATION", "CONTEXT", "ROOT_CAUSE"],
    "exec_timeout_sec": 5,
    "failed_samples_path": "data/failed_samples.json",
    "results_path": "data/paired_results.json",
    "figures_dir": "outputs/figures/",
}
```

### sections.py (`h-m2/code/sections.py`)

**Dependencies**: errors.py (StructuredError)

```python
def to_sections(error: "StructuredError", original_code: str) -> list[tuple[str, str]]:
    """Build [(PROBLEM, ...), (LOCATION, ...), (CONTEXT, ...), (ROOT_CAUSE, ...)]."""
    ...

def format_sections(sections: list[tuple[str, str]]) -> str: ...

def scramble_sections(sections: list[tuple[str, str]], seed: int) -> list[tuple[str, str]]:
    """random.Random(seed).shuffle copy; preserves content, reorders only."""
    ...

def format_structured_prompt(error: "StructuredError", original_code: str) -> str: ...
def format_scrambled_prompt(error: "StructuredError", original_code: str, seed: int) -> str: ...
```

### dataset.py (`h-m2/code/dataset.py`)

**Dependencies**: models.py, repair_loop.py (execute_and_check, initial_prompt, extract_code_block), errors.py

```python
def load_benchmark_problems() -> list[dict]:
    """evalplus.data.get_human_eval_plus() + get_mbpp_plus(), tag with 'source'."""
    ...

def collect_failed_samples(model_ref, tokenizer, problems: list[dict],
                            min_samples: int) -> list[dict]:
    """Generate once per problem; keep failures with parseable errors until min_samples."""
    ...

def save_failed_samples(samples: list[dict], out_path: str) -> None: ...
def load_failed_samples(path: str) -> list[dict]: ...
```

### experiment.py (`h-m2/code/experiment.py`)

**Dependencies**: sections.py, models.py, repair_loop.py (execute_and_check, extract_code_block)

```python
def run_repair(model_ref, tokenizer, sample: dict, prompt: str) -> bool:
    """generate_code -> extract_code_block -> execute_and_check -> bool passed."""
    ...

def run_paired_condition(model_ref, tokenizer, sample: dict, seed: int) -> dict:
    """Returns {'id', 'structured_passed', 'scrambled_passed', 'scramble_seed'}."""
    ...

def run_all_paired(model_ref, tokenizer, samples: list[dict]) -> list[dict]: ...
```

### analysis.py (`h-m2/code/analysis.py`)

**Dependencies**: none (numpy, scipy)

```python
def analyze_structure_effect(paired_results: list[dict]) -> dict:
    """McNemar chi2 + BCa-approx bootstrap CI + Cohen's d. Returns fields per
    02c spec: structured_rate, scrambled_rate, delta, p_value, ci_95,
    discordant_structured_wins, discordant_scrambled_wins, gate_pass."""
    ...

def gate_check(results: dict, alpha: float) -> bool: ...
```

### visualize.py (`h-m2/code/visualize.py`)

**Dependencies**: config.py

```python
def plot_gate_comparison(results: dict, out_path: str = None) -> None: ...
def plot_discordant_pairs(results: dict, out_path: str = None) -> None: ...
```

### run_poc.py (`h-m2/code/run_poc.py`)

**Dependencies**: all above

```python
def main() -> None:
    """load_hf_model -> collect/load failed samples -> run_all_paired ->
    analyze_structure_effect -> gate_check -> save results.json -> figures."""
    ...
```

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Port H-E1 infra | Copy errors.py, models.py, repair_loop.py; write config.py | 5 | 2+1+1+1 |
| M2-2 | Implement sections.py | 4-section formatter, deterministic per-sample scrambling | 9 | 2+2+3+2 |
| M2-3 | Implement dataset.py loading | EvalPlus load + initial generation to collect >=500 failures | 10 | 3+3+2+2 |
| M2-4 | Implement experiment.py paired repair | Single-turn repair per condition, pass/fail via execute_and_check | 10 | 3+2+3+2 |
| M2-5 | Implement analysis.py | McNemar test, bootstrap CI (10k), Cohen's d, gate_check | 11 | 2+2+4+3 |
| M2-6 | Implement visualize.py | Gate comparison bar chart + discordant pair viz | 6 | 2+1+1+2 |
| M2-7 | Implement run_poc.py orchestration | Wire full pipeline, save paired_results.json | 8 | 2+3+1+2 |
| M2-8 | Gate verification + logging | mechanism_log_message, verify_representational_alignment assertions | 5 | 1+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M2-2, M2-3, M2-4, M2-5], Low(4-8): [M2-1, M2-6, M2-7, M2-8]
