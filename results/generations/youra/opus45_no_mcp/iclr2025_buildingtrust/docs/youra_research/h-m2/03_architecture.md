# Architecture: H-M2 Hedging Marker Detection

**Type**: MECHANISM (standard tier)
**Applied**: keyword-matching epistemic hedging detection (Hyland 1998; Lakoff 1973) + cached API client pattern (from H-M1)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: H-M1 code exists and was analyzed directly (file read, not Serena — MCP unavailable in this run; manual equivalent performed).
**Analyzed Path**: `../h-m1/code/`
**Findings**: H-M1's `data.py` loads TruthfulQA `multiple_choice` (mc2) split — **not reusable**, H-M2 PRD requires the `generation` config (817 open-ended questions, no MC options). H-M1's `prompts.py` builds MC-letter-answer prompts — **not reusable**, H-M2 needs free-text CoT+confidence prompts ending in a `confidence:` statement for chain-splitting. H-M1's `api_client.py` (cached OpenAI wrapper, retry/backoff) IS directly reusable as a pattern; H-M2 copies it unmodified (same interface). No cross-hypothesis import — each hypothesis folder is self-contained per H-M1 precedent; H-M2 duplicates `api_client.py` rather than importing across folders.

---

## Component Overview

- `data.py` -> loads TruthfulQA generation split (817 questions, no options)
- `prompts.py` -> CoT+confidence prompt template (free-text reasoning + confidence statement)
- `api_client.py` -> OpenAI call wrapper + disk cache + retry/backoff (copied from H-M1 pattern)
- `hedging_detect.py` -> reasoning-chain extraction (split at confidence marker) + keyword-based hedging detection
- `metrics.py` -> hedging_presence_rate, mean_hedging_count, marker frequency distribution, gate check
- `run_experiment.py` -> orchestrates generation over 817 items, saves results
- `visualize.py` -> gate bar chart, marker frequency bar, hedging count histogram

Data flow:
`data.py` -> questions -> `prompts.py` (CoT+confidence template) -> `api_client.py` (cached call) -> raw text -> `hedging_detect.py` (extract_reasoning_chain -> count_hedging_markers) -> `run_experiment.py` (assemble per-item results) -> `metrics.py` (rates, gate check) -> `visualize.py` (figures) + results JSON/YAML.

---

## Modules

### DataLoader (`data.py`)

**Dependencies**: datasets (HF)

```python
def load_truthfulqa_generation() -> list[dict]: ...  # [{"question": str}] x 817, generation config
```

### Prompts (`prompts.py`)

**Dependencies**: None

```python
def build_cot_confidence_prompt(question: str) -> str: ...
# "Let's think step by step... conclude with: My confidence: <0-100>"
```

### APIClient (`api_client.py`)

**Dependencies**: openai (copied pattern from H-M1, same interface)

```python
class APIClient:
    def __init__(self, model: str = "gpt-3.5-turbo", cache_path: str = ".cache/responses.jsonl", max_retries: int = 3): ...
    def call(self, prompt: str, cache_key: str) -> str: ...  # temp=0, max_tokens=500, exp backoff
```

### HedgingDetector (`hedging_detect.py`)

**Dependencies**: None (re, stdlib)

```python
HEDGING_MARKERS: list[str]  # 17 markers per PRD FR-3
EXTENDED_HEDGING_MARKERS: list[str]  # fallback dict for EXPLORE if gate fails

def extract_reasoning_chain(output: str) -> str: ...  # split at 'confidence:'/'my confidence'/'i am confident'
def count_hedging_markers(text: str, markers: list[str] = HEDGING_MARKERS) -> dict: ...  # markers_found, total_count, has_hedging
def analyze_hedging(cot_output: str) -> dict: ...  # reasoning_text + hedging_result
def extract_confidence(text: str) -> float | None: ...  # reuse H-M1 regex pattern for confidence value
```

### Metrics (`metrics.py`)

**Dependencies**: collections.Counter

```python
def compute_metrics(results: list[dict]) -> dict: ...  # hedging_presence_rate, mean_hedging_count, n_samples, gate_pass
def marker_frequency_distribution(results: list[dict]) -> dict: ...  # Counter across all markers_found
def check_gate(metrics: dict) -> dict: ...  # SHOULD_WORK: >0.30 -> PASS else EXPLORE
```

### ExperimentRunner (`run_experiment.py`)

**Dependencies**: DataLoader, Prompts, APIClient, HedgingDetector, Metrics

```python
def run_generation(dataset: list[dict], client: APIClient) -> list[dict]: ...  # 817 calls, single condition
def main() -> None:  # runs generation, computes metrics, writes results/h-m2_results.json + summary.yaml
    ...
```

### Visualizer (`visualize.py`)

**Dependencies**: matplotlib, ExperimentRunner output (results JSON)

```python
def plot_gate_metrics(hedging_rate: float, threshold: float, out_dir: str) -> None: ...
def plot_marker_frequency(freq_dist: dict, out_dir: str) -> None: ...  # horizontal bar
def plot_hedging_count_histogram(results: list[dict], out_dir: str) -> None: ...
```

---

## File Structure

```
h-m2/code/
  data.py
  prompts.py
  api_client.py
  hedging_detect.py
  metrics.py
  run_experiment.py
  visualize.py
  results/h-m2_results.json
  results/summary.yaml
  .cache/responses.jsonl
figures/
  gate_metrics.png
  marker_frequency.png
  hedging_count_histogram.png
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Reuse Status | File Location |
|--------|-------------|----------------|
| APIClient | Pattern copied (not imported) — identical interface | `h-m1/code/api_client.py` (reference) |
| DataLoader | NOT reusable — different HF config (mc2 vs generation) | `h-m1/code/data.py` (reference only) |
| Prompts | NOT reusable — MC-answer format vs free-text CoT+confidence | `h-m1/code/prompts.py` (reference only) |

**Verified from**: `h-m1/code/` (actual implementation, read directly)

No cross-folder Python imports; H-M2 is self-contained, following H-M1's own precedent of no cross-hypothesis imports.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load TruthfulQA generation split (817 questions) | 3 | 1+1+1+0 |
| A-2 | Prompt template | CoT+confidence free-text prompt builder | 2 | 1+0+1+0 |
| A-3 | API client + cache | OpenAI wrapper, JSONL cache, retry/backoff (H-M1 pattern) | 5 | 2+1+1+1 |
| A-4 | Reasoning chain extraction | Split at confidence markers, isolate reasoning text | 4 | 1+1+2+0 |
| A-5 | Hedging marker detection | Keyword counting, markers_found/total_count/has_hedging | 5 | 2+1+2+0 |
| A-6 | Metrics computation | hedging_presence_rate, mean_hedging_count, freq distribution, gate check | 5 | 2+1+1+1 |
| A-7 | Experiment orchestration | Run 817 calls, assemble results, save JSON+YAML | 6 | 2+2+1+1 |
| A-8 | Visualization | Gate chart, marker frequency bar, hedging histogram | 5 | 2+1+1+1 |

**Total tasks**: 8 (within 6-8 budget)
**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-3,A-4,A-5,A-6,A-7,A-8], VeryLow(1-3): [A-1,A-2]

---

## Notes

- No training; inference-only, 817 API calls, temperature=0, max_tokens=500.
- Cache mandatory to avoid re-billing on reruns (`api_client.py`), same pattern as H-M1/H-E1.
- Gate: `hedging_presence_rate > 0.30` (SHOULD_WORK). Fail -> EXPLORE with `EXTENDED_HEDGING_MARKERS` (in `hedging_detect.py`), do not halt pipeline.
- H-M1 `data.py`/`prompts.py` are NOT imported — different dataset config and prompt format required by this hypothesis; only `api_client.py`'s interface pattern is reused.
