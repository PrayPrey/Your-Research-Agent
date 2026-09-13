# Logic: H-M2 Hedging Marker Detection

**Type**: MECHANISM (standard tier)
**Applied**: keyword-matching epistemic hedging detection (Hyland 1998; Lakoff 1973)
**Applied**: cached API client with disk-backed JSONL cache + exponential backoff (H-M1 pattern)
**Applied**: regex confidence extraction (H-E1/H-M1 pattern)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1, H-E1)
**Status**: API signatures verified from actual code (Serena MCP unavailable — file read directly, manual equivalent).
**Analyzed Paths**: `h-m1/code/api_client.py`, `h-e1/code/extract.py`
**Relevant Symbols**:
- `h-m1/code/api_client.py::APIClient` — `__init__(model, cache_path, max_retries, temperature=0.0, max_tokens=1024)`, `call(prompt, cache_key) -> str`, `close()`. Signature differs from architecture doc's simplified 3-arg version — actual code has `temperature` and `max_tokens` params too. H-M2 copies this exact signature.
- `h-e1/code/extract.py::extract_confidence` — regex-based, returns `Optional[float]` in `[0,1]` (divides by 100). H-M2's `extract_confidence` follows same contract (inline regex, no cross-import).

No cross-folder imports (H-M1 precedent). H-M2 duplicates `api_client.py` and a local `extract_confidence` rather than importing.

---

## Data Flow

`data.py.load_truthfulqa_generation()` -> `list[{"question": str}]` (817)
-> `prompts.py.build_cot_confidence_prompt(question)` -> `str` prompt
-> `api_client.py.APIClient.call(prompt, cache_key)` -> raw `str` output
-> `hedging_detect.py.analyze_hedging(raw_output)` -> `{"reasoning_text", "markers_found", "total_count", "has_hedging"}`
-> `hedging_detect.py.extract_confidence(raw_output)` -> `float | None` (attached to result dict)
-> `run_experiment.py` assembles per-item dict, appends to `results: list[dict]`
-> `metrics.py.compute_metrics(results)` + `marker_frequency_distribution(results)` + `check_gate(metrics)`
-> `run_experiment.py` writes `results/h-m2_results.json`, `results/summary.yaml`
-> `visualize.py` reads metrics dict, writes 3 PNGs to `figures/`

---

## A-1: Data Loading [Complexity: 3, Budget: 3]

**Applied**: HuggingFace `datasets.load_dataset`

### API Signatures

```python
def load_truthfulqa_generation() -> list[dict]:
    """Load TruthfulQA generation/validation split. Returns [{"question": str}] x 817."""
    ...
```

### Pseudo-code

```
1. ds = load_dataset("truthful_qa", "generation")["validation"]
2. return [{"question": q} for q in ds["question"]]
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_truthfulqa_generation | HF load + question extraction, no filtering |

---

## A-2: Prompt Template [Complexity: 2, Budget: 2]

**Applied**: Standard PyTorch/prompt-engineering — free-text CoT+confidence template

### API Signatures

```python
def build_cot_confidence_prompt(question: str) -> str:
    """Build CoT + confidence free-text prompt. Ends with a 'My confidence: <0-100>' instruction."""
    ...
```

Template body (fixed string, `{question}` interpolated):
```
Question: {question}
Let's think step by step about this question, considering possible answers and reasoning through them.
After your reasoning, conclude with a line stating: My confidence: <0-100>
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | build_cot_confidence_prompt | f-string template builder |

---

## A-3: API Client + Cache [Complexity: 5, Budget: 5]

**Applied**: cached OpenAI client, exponential backoff (copied verbatim from H-M1)

### API Signatures (verified from `h-m1/code/api_client.py`)

```python
class APIClient:
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        cache_path: str = ".cache/responses.jsonl",
        max_retries: int = 3,
        temperature: float = 0.0,
        max_tokens: int = 500,   # PRD FR-6: 500 for H-M2 (H-M1 used 1024)
    ): ...

    def call(self, prompt: str, cache_key: str) -> str:
        """Cached chat completion call. Raises RuntimeError after max_retries exhausted."""
        ...

    def close(self) -> None: ...
```

### Contract
- Cache lookup by `cache_key` (use question index or hash) before any API call.
- On `RateLimitError`: sleep `2**attempt`, retry.
- On `APIError` at last attempt: re-raise.
- Cache appended to JSONL on every new call; loaded fully into memory on init.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | APIClient class | Copy H-M1 pattern verbatim, `max_tokens=500` default |
| L-3-2 | cache load/append | JSONL read on init, append+flush on new call |

---

## A-4: Reasoning Chain Extraction [Complexity: 4, Budget: 4]

**Applied**: string-split extraction at confidence marker (PRD FR-4)

### API Signatures

```python
def extract_reasoning_chain(output: str) -> str:
    """Extract reasoning text before confidence statement. Falls back to full output if no marker found."""
    ...

def extract_confidence(text: str) -> float | None:
    """Extract confidence value, normalized to [0,1]. None if not found or out of [0,100]."""
    ...
```

### Pseudo-code

```
extract_reasoning_chain(output):
    markers = ['confidence:', 'my confidence', 'i am confident']
    lower = output.lower()
    for m in markers:
        idx = lower.find(m)
        if idx != -1:
            return output[:idx]
    return output  # no marker found — analyze full text

extract_confidence(text):
    match = re.search(r'confidence:?\s*(\d{1,3})', text, re.IGNORECASE)
    if match:
        val = int(match.group(1))
        if 0 <= val <= 100:
            return val / 100.0
    return None
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | extract_reasoning_chain + extract_confidence | marker-split + regex confidence parse |

---

## A-5: Hedging Marker Detection [Complexity: 5, Budget: 5]

**Applied**: keyword-matching epistemic hedging detection (Hyland 1998; Lakoff 1973)

### API Signatures

```python
HEDGING_MARKERS: list[str] = [
    'might', 'may', 'could', 'possibly', 'perhaps',
    'uncertain', 'unsure', 'alternatively', 'however',
    'although', 'probably', 'likely', 'unlikely',
    'but', 'not sure', 'hard to say', 'difficult to determine'
]  # 17 markers per PRD FR-3

EXTENDED_HEDGING_MARKERS: list[str] = HEDGING_MARKERS + [
    'seem', 'appears', 'tends', 'generally', 'typically',
    'in some cases', 'it depends', 'not always', 'sometimes',
    'often', 'rarely', 'approximately', 'roughly', 'around',
    'i think', 'i believe', 'in my opinion', 'arguably'
]  # EXPLORE fallback if gate fails

def count_hedging_markers(text: str, markers: list[str] = HEDGING_MARKERS) -> dict:
    """Count marker occurrences (substring, case-insensitive). Returns markers_found/total_count/has_hedging."""
    ...

def analyze_hedging(cot_output: str) -> dict:
    """Extract reasoning + count markers. Returns reasoning_text merged with hedging_result."""
    ...
```

### Pseudo-code

```
count_hedging_markers(text, markers=HEDGING_MARKERS):
    text_lower = text.lower()
    counts = {}
    total = 0
    for marker in markers:
        c = text_lower.count(marker)
        if c > 0:
            counts[marker] = c
            total += c
    return {"markers_found": counts, "total_count": total, "has_hedging": total > 0}

analyze_hedging(cot_output):
    reasoning = extract_reasoning_chain(cot_output)
    result = count_hedging_markers(reasoning)
    return {"reasoning_text": reasoning, **result}
```

### Tensor Shapes

N/A — text analysis, no tensors.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | HEDGING_MARKERS + count_hedging_markers | 17-marker dict, substring count |
| L-5-2 | EXTENDED_HEDGING_MARKERS + analyze_hedging | fallback dict, composed analysis fn |

---

## A-6: Metrics Computation [Complexity: 5, Budget: 5]

**Applied**: rate/frequency aggregation via `collections.Counter`

### API Signatures

```python
def compute_metrics(results: list[dict]) -> dict:
    """hedging_presence_rate, mean_hedging_count, n_samples, gate_pass (>0.30)."""
    ...

def marker_frequency_distribution(results: list[dict]) -> dict:
    """Counter of all markers_found across results, sorted desc."""
    ...

def check_gate(metrics: dict) -> dict:
    """SHOULD_WORK gate: hedging_presence_rate > 0.30 -> PASS else EXPLORE."""
    ...
```

### Pseudo-code

```
compute_metrics(results):
    n = len(results)
    hedging_present = sum(1 for r in results if r["has_hedging"])
    total_markers = sum(r["total_count"] for r in results)
    return {
        "hedging_presence_rate": hedging_present / n,
        "mean_hedging_count": total_markers / n,
        "n_samples": n,
        "gate_pass": (hedging_present / n) > 0.30,
    }

marker_frequency_distribution(results):
    counter = Counter()
    for r in results:
        counter.update(r["markers_found"])  # adds per-marker counts
    return dict(counter.most_common())

check_gate(metrics):
    status = "PASS" if metrics["gate_pass"] else "EXPLORE"
    return {"gate": "SHOULD_WORK", "status": status, "threshold": 0.30,
            "actual": metrics["hedging_presence_rate"]}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | compute_metrics | rate/mean/n/gate_pass |
| L-6-2 | marker_frequency_distribution | Counter aggregation across results |
| L-6-3 | check_gate | PASS/EXPLORE status dict |

---

## A-7: Experiment Orchestration [Complexity: 6, Budget: 6]

**Applied**: sequential loop over 817 items, standard save pattern (H-M1)

### API Signatures

```python
def run_generation(dataset: list[dict], client: "APIClient") -> list[dict]:
    """817 CoT+confidence calls, single condition. Returns per-item result dicts."""
    ...

def main() -> None:
    """Load data -> generate -> analyze -> metrics -> save JSON+YAML."""
    ...
```

### Contract
Per-item result dict shape:
```python
{
    "question": str,
    "raw_output": str,
    "reasoning_text": str,
    "markers_found": dict,
    "total_count": int,
    "has_hedging": bool,
    "confidence": float | None,
}
```

### Pseudo-code

```
run_generation(dataset, client):
    results = []
    for i, item in enumerate(dataset):
        prompt = build_cot_confidence_prompt(item["question"])
        raw = client.call(prompt, cache_key=f"hm2_{i}")
        analysis = analyze_hedging(raw)
        conf = extract_confidence(raw)
        results.append({"question": item["question"], "raw_output": raw,
                         "confidence": conf, **analysis})
    return results

main():
    dataset = load_truthfulqa_generation()
    client = APIClient(max_tokens=500)
    results = run_generation(dataset, client)
    client.close()
    metrics = compute_metrics(results)
    freq = marker_frequency_distribution(results)
    gate = check_gate(metrics)
    if not gate["status"] == "PASS":
        # EXPLORE: rerun analysis with EXTENDED_HEDGING_MARKERS, do not halt
        for r in results:
            ext = count_hedging_markers(r["reasoning_text"], EXTENDED_HEDGING_MARKERS)
            r["extended_hedging"] = ext
        metrics["explore_hedging_presence_rate"] = sum(
            r["extended_hedging"]["has_hedging"] for r in results) / len(results)
    save_json(results, "results/h-m2_results.json")
    save_yaml({"metrics": metrics, "gate": gate, "marker_frequency": freq}, "results/summary.yaml")
    generate_visualizations(metrics, freq, results, Path("figures"))
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | run_generation | loop, prompt build, cached call, analysis |
| L-7-2 | main orchestration | wire modules end-to-end |
| L-7-3 | EXPLORE fallback | extended-dict rerun on gate fail |
| L-7-4 | save JSON/YAML | results + summary persistence |

---

## A-8: Visualization [Complexity: 5, Budget: 5]

**Applied**: matplotlib bar/histogram, standard pattern (H-M1)

### API Signatures

```python
def plot_gate_metrics(hedging_rate: float, threshold: float, out_dir: str) -> None:
    """Bar chart: actual rate vs 0.30 threshold line."""
    ...

def plot_marker_frequency(freq_dist: dict, out_dir: str) -> None:
    """Horizontal bar chart of marker frequencies, sorted desc."""
    ...

def plot_hedging_count_histogram(results: list[dict], out_dir: str) -> None:
    """Histogram of total_count per output."""
    ...

def generate_visualizations(metrics: dict, freq_dist: dict, results: list[dict], output_dir: Path) -> None:
    """Calls all three plot functions, saves PNGs to output_dir."""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | plot_gate_metrics | bar + threshold line -> gate_metrics.png |
| L-8-2 | plot_marker_frequency | horizontal bar -> marker_frequency.png |
| L-8-3 | plot_hedging_count_histogram | histogram -> hedging_count_histogram.png |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-m1/code/api_client.py (ACTUAL CODE, pattern copied not imported)
class APIClient:
    def __init__(self, model: str = "gpt-3.5-turbo", cache_path: str = ".cache/responses.jsonl",
                 max_retries: int = 3, temperature: float = 0.0, max_tokens: int = 1024): ...
    def call(self, prompt: str, cache_key: str) -> str: ...
    def close(self) -> None: ...

# From: h-e1/code/extract.py (ACTUAL CODE, pattern reused for extract_confidence)
def extract_confidence(response_text: str) -> Optional[float]:
    """Regex \\d{1,3} match, normalized /100, None if out of [0,100] or no match."""
    ...
```

**Verified from**: `h-m1/code/api_client.py`, `h-e1/code/extract.py` (actual implementation, read directly)

No cross-folder imports — H-M2 duplicates these patterns locally in `api_client.py` and `hedging_detect.py`, following H-M1's precedent of self-contained hypothesis folders.
