# Logic Design: H-E1 ECE Measurability Validation

**Type:** EXISTENCE (PoC) — minimal logic only.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - designing new APIs (no existing code/base hypothesis)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: ECE Measurement Pipeline [Complexity: 3, Budget: 8]

**Applied**: Standard PyTorch/NumPy calibration pattern (Guo et al. 2017 ECE)

### Data Structures

```python
from dataclasses import dataclass, field
from typing import Optional, TypedDict

class TruthfulQAItem(TypedDict):
    question: str
    choices: list[str]        # e.g. ["A) ...", "B) ...", ...]
    correct_idx: int          # index into choices

class TrialResult(TypedDict):
    question_idx: int
    condition: str
    confidence: Optional[float]   # [0,1] or None on failure
    answer: Optional[str]         # letter or None on failure
    correct: Optional[bool]       # None if extraction failed
    raw_response: str

@dataclass
class ConditionSummary:
    condition: str
    n_total: int
    n_extracted: int
    extraction_rate: float        # n_extracted / n_total
    ece: Optional[float]          # None if extraction_rate too low to compute
    results: list[TrialResult] = field(default_factory=list)
```

### API Signatures

```python
def load_truthfulqa() -> list[TruthfulQAItem]:
    """Load TruthfulQA mc1 (validation split, 817 items) from HF datasets."""
    ...

def format_prompt(question: str, choices: list[str], condition: str) -> str:
    """Fill PROMPTS[condition] template. condition in PROMPTS.keys()."""
    ...

def call_api(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    cache: dict[str, str] | None = None,
) -> str:
    """OpenAI chat completion, temperature=0, max_tokens=512. Returns raw text.
    cache keyed by hash(model + prompt); reused across re-runs."""
    ...

def extract_confidence(response: str) -> Optional[float]:
    """Regex r'Confidence:\\s*(\\d+)%' -> value/100.0, else None."""
    ...

def extract_answer(response: str, num_choices: int) -> Optional[str]:
    """Regex r'Answer:\\s*([A-Z])' (IGNORECASE) -> uppercase letter if
    ord(letter)-ord('A') < num_choices, else None."""
    ...

def compute_ece(
    confidences: "np.ndarray",   # [N] float in [0,1]
    accuracies: "np.ndarray",    # [N] float 0.0/1.0
    n_bins: int = 15,
) -> float:
    """Equal-width binning ECE per Guo et al. 2017. Returns scalar in [0,1]."""
    ...

def run_condition(
    dataset: list[TruthfulQAItem],
    condition: str,
    model: str = "gpt-3.5-turbo",
    cache: dict[str, str] | None = None,
) -> ConditionSummary:
    """Run one prompting condition across full dataset; aggregate extraction
    rate and ECE."""
    ...

def run_experiment(
    conditions: list[str] = ["baseline", "cot_only", "confidence_only", "cot_confidence", "token_padding"],
    output_dir: str = "results",
) -> dict[str, ConditionSummary]:
    """Orchestrate: load data -> run each condition -> compute ECE ->
    save results.json + figures -> return summaries."""
    ...
```

### Pseudo-code: compute_ece

```
1. bin_boundaries = linspace(0, 1, n_bins + 1)
2. ece = 0.0
3. for i in range(n_bins):
     in_bin = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i+1])
     prop_in_bin = mean(in_bin)
     if prop_in_bin > 0:
       avg_conf = mean(confidences[in_bin])
       avg_acc  = mean(accuracies[in_bin])
       ece += abs(avg_acc - avg_conf) * prop_in_bin
4. return ece
```

### Pseudo-code: run_experiment

```
1. dataset = load_truthfulqa()                      # 817 items
2. cache = load_cache_from_disk() or {}
3. summaries = {}
4. for condition in conditions:
     summary = run_condition(dataset, condition, cache=cache)
     summaries[condition] = summary
     save_cache_to_disk(cache)                       # incremental, survives crash
5. save results.json (all summaries, raw + aggregated)
6. for condition, summary in summaries: plot_reliability_diagram(summary)
7. plot_ece_comparison_bar(summaries)
8. plot_extraction_rate_bar(summaries)                # gate metric figure
9. return summaries
```

### Tensor/Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| confidences | [N] | N = successfully extracted trials for a condition (<=817) |
| accuracies | [N] | float 0.0/1.0, aligned with confidences |
| bin_boundaries | [16] | n_bins+1 edges, 0 to 1 |

### Error Handling Strategy

- `call_api`: wrap in try/except with exponential backoff retry (3 attempts) on
  rate-limit/timeout errors; on final failure, return `""` (treated as
  extraction failure downstream, not a crash).
- `extract_confidence` / `extract_answer`: never raise; return `None` on any
  non-match — caller counts as extraction failure, logged, loop continues
  (per NFR-3).
- `run_condition`: if `n_extracted == 0`, skip `compute_ece` (avoid div-by-zero
  on empty arrays) and set `ece=None` in summary; still records
  `extraction_rate=0.0` so gate check fails explicitly rather than crashing.
- `run_experiment`: cache persisted after each condition so a crash mid-run
  does not lose completed API calls (NFR-2 re-run efficiency).

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A1-1 | load_truthfulqa | HF datasets load + mc1 field mapping |
| L-A1-2 | PROMPTS dict + format_prompt | 5 templates from experiment brief |
| L-A1-3 | call_api + cache | OpenAI client, retry/backoff, dict cache |
| L-A1-4 | extract_confidence | Regex extraction |
| L-A1-5 | extract_answer | Regex extraction + bounds check |
| L-A1-6 | compute_ece | Binned ECE, numpy |
| L-A1-7 | run_condition | Per-condition loop + aggregation |
| L-A1-8 | run_experiment + figures | Orchestration, results.json, plots |
