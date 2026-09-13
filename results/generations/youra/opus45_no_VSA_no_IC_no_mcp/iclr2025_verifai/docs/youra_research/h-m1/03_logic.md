# Logic: H-M1 (MECHANISM)

**Applied**: LLM-as-judge reconstruction evaluation pattern (Archon KB: "LLM judge JSON extraction with retry/backoff")

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena MCP unavailable — read H-E1 `code/` directly via file tools (matches architecture.md note).
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**: `StructuredError` (dataclass, errors.py), `parse_compiler_output(raw_output, source_code)` (errors.py), `format_structured_prompt(error, original_code)` (prompts.py), `CONFIG`/`OPENAI_API_KEY` (config.py), `generate_code(...)` (models.py)

**Critical finding**: No `error_pairs.json` or any stored (raw_error, structured_error) pairs exist anywhere in H-E1 output. `repair_loop.py` calls `parse_compiler_output` inline per-attempt but never persists raw tracebacks. **M-2 must generate pairs synthetically** — run known buggy code snippets, capture real Python tracebacks via `execute_and_check`-style exec, then derive structured form with `parse_compiler_output`. No "load H-E1 error_pairs.json" path exists; budget accordingly.

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/errors.py (ACTUAL CODE — copy verbatim into h-m1/code/errors.py)
@dataclass
class StructuredError:
    line_number: int
    error_type: str
    error_message: str      # NOTE: architecture.md said "message" — actual field is error_message
    code_context: List[str] # NOTE: architecture.md said "context" — actual field is code_context

def parse_compiler_output(raw_output: str, source_code: str) -> StructuredError: ...

# From: h-e1/code/prompts.py (ACTUAL CODE — copy verbatim)
def format_structured_prompt(error: StructuredError, original_code: str) -> str: ...
```

**Verified from**: `docs/youra_research/h-e1/code/errors.py`, `prompts.py` (actual implementation, not spec)

**Field name correction**: FR-2 of PRD lists fields `error_type, line_number, message, context` — actual dataclass uses `error_message`, `code_context`. All h-m1 code (config `fields` list, judge prompt, accuracy computation) must use the real field names: `line_number, error_type, error_message, code_context`.

## File Organization

Matches architecture.md: `errors.py` (copied), `config.py`, `judge.py`, `reconstruction.py`, `build_pairs.py`, `evaluate.py`, `visualize.py`, `run_poc.py`, `data/error_pairs.json` (generated).

---

## L-1: Port infra + config [Complexity: 5, Budget: 5]

**Applied**: Standard PyTorch/Python project config pattern

```python
# config.py
CONFIG = {
    "judge_model": "gpt-4",
    "judge_provider": "openai",       # "openai" | "anthropic"
    "temperature": 0.0,
    "max_tokens": 500,
    "fields": ["line_number", "error_type", "error_message", "code_context"],  # matches StructuredError
    "min_samples": 500,
    "accuracy_threshold": 0.95,
    "pass_rate_threshold": 0.90,
    "max_retries": 5,
    "backoff_base_sec": 2.0,
    "error_pairs_path": "data/error_pairs.json",
    "results_path": "outputs/results.json",
    "figures_dir": "outputs/figures/",
}
```
`errors.py` copied byte-for-byte from `h-e1/code/errors.py`.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Copy errors.py | Verbatim copy from h-e1/code/errors.py |
| L-1-2 | Write config.py | As above, field names verified against StructuredError |

---

## L-2: build_pairs.py — synthesize error pairs [Complexity: 10, Budget: 10]

**Applied**: exception-capture-via-exec pattern (same as h-e1 repair_loop.execute_and_check)

No source pairs exist in H-E1. Generate pairs by executing known-buggy snippets and capturing `traceback.format_exc()` as `raw_error`, then deriving `StructuredError` via `parse_compiler_output`.

```python
def generate_buggy_snippets(n: int = 500) -> list[dict]:
    """Return list of {"source_code": str, "error_type": str} synthetic snippets
    covering common Python error types (NameError, TypeError, IndexError, etc.)."""
    ...

def capture_raw_error(source_code: str) -> str:
    """Exec source_code, catch exception, return traceback.format_exc() string."""
    ...

def build_error_pairs(n_samples: int = 500) -> list[dict]:
    """Generate snippets -> capture raw errors -> parse_compiler_output ->
    return [{"raw_error": str, "structured_error": StructuredError, "source_code": str}, ...]"""
    ...

def save_pairs(pairs: list[dict], out_path: str) -> None:
    """Serialize StructuredError via dataclasses.asdict; json.dump to out_path."""
    ...

def load_or_build_error_pairs(out_path: str, n_samples: int = 500) -> list[dict]:
    """If out_path exists, json.load and return. Else build_error_pairs + save_pairs."""
    ...
```

### Tensor/Data Shapes

| Variable | Type | Note |
|----------|------|------|
| pairs | `list[dict]`, len >= 500 | keys: raw_error, structured_error, source_code |
| structured_error (serialized) | `dict` | `{line_number, error_type, error_message, code_context}` |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | generate_buggy_snippets | Template-based buggy code generator, >=500 across error types |
| L-2-2 | capture_raw_error | Safe exec + traceback capture |
| L-2-3 | build_error_pairs | Orchestrate snippet -> raw -> structured |
| L-2-4 | save_pairs / load_or_build_error_pairs | Persist + idempotent load |

---

## L-3: judge.py — JudgeLLM [Complexity: 9, Budget: 9]

**Applied**: retry+backoff OpenAI client pattern (from h-e1/code/models.py `generate_code`)

```python
class JudgeLLM:
    def __init__(self, provider: str, model: str, temperature: float = 0.0, max_tokens: int = 500): ...

    def extract(self, prompt: str) -> dict:
        """Call provider API with retry+backoff (mirrors models.generate_code retry loop),
        parse JSON response body. Returns dict with keys matching CONFIG['fields'].
        On JSON parse failure, returns {} (counted as full miss in accuracy)."""
        ...

def build_extraction_prompt(structured_error_text: str, fields: list[str]) -> str:
    """Prompt LLM to return JSON with exactly `fields` keys, extracted from structured_error_text."""
    ...
```

### Pseudo-code (retry/backoff, mirrors h-e1 models.py)

```
for attempt in range(max_retries):
    try:
        resp = client.chat.completions.create(model, messages=[prompt], temperature=0.0, max_tokens=500)
        return json.loads(resp.content)
    except RateLimitError:
        sleep(backoff_base_sec ** attempt)
raise RuntimeError("Judge call failed after max retries")
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | build_extraction_prompt | JSON-schema instruction prompt from fields list |
| L-3-2 | JudgeLLM.extract (OpenAI) | client.chat.completions + retry/backoff + JSON parse |
| L-3-3 | JudgeLLM.extract (Anthropic branch) | anthropic.Anthropic() equivalent, same retry contract |

---

## L-4: reconstruction.py + evaluate.py [Complexity: 18 combined (10+8), Budget: 15]

**Applied**: exact-match field accuracy pattern

```python
class ReconstructionTest:
    def __init__(self, judge: JudgeLLM, fields: list[str]): ...

    def extract_from_raw(self, raw_error: str, source_code: str) -> dict:
        """Ground truth: dataclasses.asdict(parse_compiler_output(raw_error, source_code))"""
        ...

    def extract_from_structured(self, structured_error: dict) -> dict:
        """LLM extraction: judge.extract(build_extraction_prompt(format(structured_error), fields))"""
        ...

    def compute_accuracy(self, original: dict, reconstructed: dict) -> float:
        """Fraction of self.fields where original[f] == reconstructed.get(f) (str-normalized)."""
        ...

    def run(self, error_pairs: list[dict]) -> dict:
        """For each pair: original = extract_from_raw(...); recon = extract_from_structured(...);
        acc = compute_accuracy. Returns {mean_accuracy, per_sample: [...], per_field: {...}, pass: bool}"""
        ...

def compute_reconstruction_metrics(per_sample: list[dict], fields: list[str]) -> dict:
    """mean_accuracy, std, pass_rate (samples with 100% field match), per_field accuracy dict."""
    ...

def per_error_type_breakdown(pairs: list[dict], per_sample: list[dict]) -> dict:
    """Group per_sample accuracy by pairs[i]['structured_error']['error_type']."""
    ...

def gate_check(metrics: dict, acc_thresh: float = 0.95, pass_thresh: float = 0.90) -> bool:
    """return metrics['mean_accuracy'] > acc_thresh and metrics['pass_rate'] > pass_thresh"""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | ReconstructionTest.extract_from_raw/structured | ground-truth + LLM extraction |
| L-4-2 | compute_accuracy + run loop | per-sample field comparison over all pairs |
| L-4-3 | compute_reconstruction_metrics | mean/std/pass_rate/per_field aggregation |
| L-4-4 | per_error_type_breakdown + gate_check | grouping + threshold gate |

---

## L-5: visualize.py + run_poc.py [Complexity: 15 combined (7+8), Budget: 12]

**Applied**: matplotlib bar-chart gate visualization (h-e1 visualize.py pattern)

```python
def plot_gate_comparison(metrics: dict, out_path: str = None) -> None:
    """Bar: mean_accuracy & pass_rate vs their thresholds."""
    ...

def plot_per_field_accuracy(metrics: dict, out_path: str = None) -> None:
    """Bar chart of metrics['per_field'] accuracy per field."""
    ...

def plot_accuracy_by_error_type(breakdown: dict, out_path: str = None) -> None:
    """Bar chart of mean accuracy per error_type."""
    ...

def main() -> None:
    """load_or_build_error_pairs -> JudgeLLM -> ReconstructionTest.run ->
    compute_reconstruction_metrics -> per_error_type_breakdown -> gate_check ->
    json.dump results -> call all 3 plot_* -> print PASS/FAIL, sys.exit(0/1)"""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | plot_gate_comparison + plot_per_field_accuracy | 2 bar charts |
| L-5-2 | plot_accuracy_by_error_type | grouped bar chart |
| L-5-3 | run_poc.main orchestration | wire pipeline, save results.json, gate exit code |

---

## Budget Note

Architecture allocated 8 tasks (M-1..M-8); consolidated to 5 logic groups (L-1..L-5) to fit the 6-subtask-group ceiling while preserving all functional requirements. M-8 (gate verification + logging) folded into L-4 (`gate_check`) and L-5 (`main`'s PASS/FAIL print + exit code) — no standalone logging module needed (YAGNI: a `mechanism_log_message` helper adds no behavior beyond `print`/`json.dump` already present).
