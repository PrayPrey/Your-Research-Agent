# Logic: H-M1 CoT Reasoning Chain Detection

**Applied**: regex-based multi-pattern text classification (stdlib `re`), disk-cached API client w/ exponential backoff

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: H-E1 (prerequisite) has no `code/` directory — nothing to analyze. H-M1 is fully self-contained new implementation.
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Loading [Complexity: 4, Budget: 4]

**Applied**: Standard PyTorch/HF dataset loading

```python
def load_truthfulqa_mc2() -> list[dict]:
    """Load TruthfulQA mc2 validation split from HF datasets."""
    ...

def format_options(mc2_targets: dict) -> tuple[str, list[str]]:
    """Format mc2_targets choices as 'A) text\nB) text...'. Returns (formatted_str, ['A','B',...])."""
    ...
```

### Tensor Shapes

N/A (no tensors; list[dict] of `{question: str, mc2_targets: {choices: list[str], labels: list[int]}}`).

### Pseudo-code

```
1. ds = datasets.load_dataset("truthful_qa", "multiple_choice")["validation"]
2. items = [{"question": r["question"], "mc2_targets": r["mc2_targets"]} for r in ds]
3. format_options: enumerate choices -> letters A..E via string.ascii_uppercase; join "LETTER) choice"
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | HF load call | `load_dataset("truthful_qa", "multiple_choice")` |
| L-1-2 | Item extraction | Map raw rows to `{question, mc2_targets}` dicts |
| L-1-3 | Option formatting | Letter-labeled option string builder |
| L-1-4 | Letter list return | Return `["A","B",...]` matching num choices |

---

## A-2: Prompt Templates [Complexity: 2, Budget: 2]

**Applied**: Standard PyTorch (zero-shot CoT elicitation, Kojima et al. 2022)

```python
def build_baseline_prompt(question: str, options: str) -> str:
    """Direct-answer prompt: no CoT trigger."""
    ...

def build_cot_prompt(question: str, options: str) -> str:
    """CoT prompt: includes 'Let's think step by step.' trigger."""
    ...
```

### Pseudo-code

```
build_baseline_prompt:
  return f"Question: {question}\nOptions:\n{options}\nAnswer directly with the letter of the correct option. Format: Answer: <letter> Confidence: <0-100>"

build_cot_prompt:
  return f"Question: {question}\nOptions:\n{options}\nLet's think step by step. Provide numbered reasoning steps, then conclude with: Answer: <letter> Confidence: <0-100>"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Baseline template | f-string, no reasoning trigger |
| L-2-2 | CoT template | f-string with "step by step" trigger + numbered-steps instruction |

---

## A-3: API Client + Cache [Complexity: 6, Budget: 6]

**Applied**: Disk-cached wrapper w/ exponential backoff (standard retry pattern)

```python
class APIClient:
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        cache_path: str = ".cache/responses.jsonl",
        max_retries: int = 3,
    ):
        """Loads existing cache into dict; opens append handle for new entries."""
        ...

    def call(self, prompt: str, cache_key: str) -> str:
        """Cached completion call. temperature=0, max_tokens=1024. Retries w/ exp backoff on rate limit."""
        ...
```

### Pseudo-code

```
__init__:
  self._cache = {}  # cache_key -> response text
  if os.path.exists(cache_path):
    for line in open(cache_path): rec = json.loads(line); self._cache[rec["key"]] = rec["response"]
  self._cache_file = open(cache_path, "a")

call(prompt, cache_key):
  if cache_key in self._cache: return self._cache[cache_key]
  for attempt in range(max_retries):
    try:
      resp = openai.ChatCompletion.create(model=self.model, messages=[{"role":"user","content":prompt}],
                                           temperature=0, max_tokens=1024)
      text = resp.choices[0].message.content
      self._cache[cache_key] = text
      self._cache_file.write(json.dumps({"key": cache_key, "response": text}) + "\n"); self._cache_file.flush()
      return text
    except RateLimitError:
      time.sleep(2 ** attempt)
  raise RuntimeError(f"API call failed after {max_retries} retries: {cache_key}")
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Cache load | Read JSONL into in-memory dict on init |
| L-3-2 | Cache write | Append new responses, flush per call |
| L-3-3 | OpenAI call | ChatCompletion request, temp=0, max_tokens=1024 |
| L-3-4 | Retry loop | Exponential backoff on rate limit (2**attempt sleep) |
| L-3-5 | Cache hit short-circuit | Return cached response w/o API call |
| L-3-6 | Failure raise | RuntimeError after max_retries exhausted |

---

## A-4: Reasoning Chain Detection [Complexity: 7, Budget: 7]

**Applied**: Multi-pattern regex classification (Wei et al. 2022 CoT step markers)

```python
def detect_reasoning_chain(text: str) -> bool:
    """True if text contains any numbered/ordinal/logical reasoning marker."""
    ...

def count_reasoning_steps(text: str) -> int:
    """Count of distinct numbered-step markers (1. / 2) / Step 3:)."""
    ...

def classify_patterns(text: str) -> dict[str, bool]:
    """Returns {'numbered': bool, 'ordinal': bool, 'logical': bool} for pattern breakdown pie."""
    ...
```

### Pseudo-code

```
Regex patterns (module-level constants):
  NUMBERED = re.compile(r'(?:^|\n)\s*(?:\d+[\.\)]|Step\s+\d+:)', re.IGNORECASE)
  ORDINAL  = re.compile(r'\b(First|Second|Third|Fourth|Fifth|Finally|Next|Then)\b', re.IGNORECASE)
  LOGICAL  = re.compile(r'\b(therefore|thus|hence|because|so)\b', re.IGNORECASE)

detect_reasoning_chain(text):
  return bool(NUMBERED.search(text) or ORDINAL.search(text) or LOGICAL.search(text))

count_reasoning_steps(text):
  return len(NUMBERED.findall(text))  # count distinct numbered markers; 0 if none

classify_patterns(text):
  return {"numbered": bool(NUMBERED.search(text)),
          "ordinal": bool(ORDINAL.search(text)),
          "logical": bool(LOGICAL.search(text))}
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Numbered regex | `\d+[\.\)]` / `Step N:` pattern |
| L-4-2 | Ordinal regex | First/Second/.../Finally/Next/Then pattern |
| L-4-3 | detect_reasoning_chain | OR-combine all three patterns |
| L-4-4 | Logical connector regex | therefore/thus/hence/because/so |
| L-4-5 | count_reasoning_steps | findall on numbered pattern, len() |
| L-4-6 | classify_patterns dict | bool per pattern type |
| L-4-7 | Edge case: no markers | Return False/0/{all False} on empty match |

---

## A-5: Answer/Confidence Extraction [Complexity: 3, Budget: 3]

**Applied**: Standard regex extraction, graceful None on failure

```python
def extract_answer(text: str, num_choices: int) -> str | None:
    """Extract letter answer (A..num_choices'th letter). None if not found."""
    ...

def extract_confidence(text: str) -> float | None:
    """Extract confidence 0-100 from 'Confidence: N' pattern. None if not found."""
    ...
```

### Pseudo-code

```
extract_answer(text, num_choices):
  valid_letters = string.ascii_uppercase[:num_choices]
  m = re.search(rf'Answer:\s*\(?([{valid_letters}])\)?', text, re.IGNORECASE)
  return m.group(1).upper() if m else None

extract_confidence(text):
  m = re.search(r'Confidence:\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
  return float(m.group(1)) if m else None
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Answer regex | `Answer:\s*LETTER` bounded by num_choices |
| L-5-2 | Confidence regex | `Confidence:\s*NUMBER` |
| L-5-3 | Failure handling | Return None on no-match, log for review |

---

## A-6: Metrics Computation [Complexity: 4, Budget: 4]

**Applied**: Standard aggregation, threshold gate check

```python
def compute_metrics(results: list[dict]) -> dict:
    """results: [{has_reasoning, step_count, answer, ...}]. Returns {reasoning_presence_rate, mean_step_count}."""
    ...

def check_gate(cot_metrics: dict, baseline_metrics: dict) -> dict:
    """3 PoC gates: cot_rate>0.90, cot_rate-baseline_rate>0.50, cot_mean_step_count>2.0."""
    ...
```

### Pseudo-code

```
compute_metrics(results):
  n = len(results)
  reasoning_presence_rate = sum(r["has_reasoning"] for r in results) / n
  mean_step_count = sum(r["step_count"] for r in results) / n
  return {"reasoning_presence_rate": reasoning_presence_rate, "mean_step_count": mean_step_count}

check_gate(cot_metrics, baseline_metrics):
  gate_1 = cot_metrics["reasoning_presence_rate"] > 0.90
  gate_2 = (cot_metrics["reasoning_presence_rate"] - baseline_metrics["reasoning_presence_rate"]) > 0.50
  gate_3 = cot_metrics["mean_step_count"] > 2.0
  return {"gate_1_rate": gate_1, "gate_2_delta": gate_2, "gate_3_steps": gate_3, "all_pass": all([gate_1, gate_2, gate_3])}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | reasoning_presence_rate | Mean of has_reasoning bools |
| L-6-2 | mean_step_count | Mean of step_count ints |
| L-6-3 | Gate thresholds | Compare against 0.90 / 0.50 delta / 2.0 |
| L-6-4 | all_pass aggregation | AND of all 3 gates |

---

## A-7: Experiment Orchestration [Complexity: 7, Budget: 7]

**Applied**: Standard sequential experiment loop

```python
def run_condition(dataset: list[dict], condition: str, client: APIClient) -> list[dict]:
    """condition: 'baseline' | 'cot'. Returns per-item result dicts."""
    ...

def main() -> None:
    """Load data, run both conditions (817x2), compute metrics/gate, write results/h-m1_results.json."""
    ...
```

### Tensor Shapes

N/A (no tensors; result dict per item: `{question, raw_output, has_reasoning, step_count, patterns, answer, confidence}`).

### Pseudo-code

```
run_condition(dataset, condition, client):
  results = []
  for i, item in enumerate(dataset):
    options_str, letters = format_options(item["mc2_targets"])
    prompt = build_cot_prompt(item["question"], options_str) if condition == "cot" \
             else build_baseline_prompt(item["question"], options_str)
    cache_key = f"{condition}_{i}"
    raw = client.call(prompt, cache_key)
    has_reasoning = detect_reasoning_chain(raw)
    step_count = count_reasoning_steps(raw)
    patterns = classify_patterns(raw)
    answer = extract_answer(raw, len(letters))
    confidence = extract_confidence(raw)
    results.append({"question": item["question"], "raw_output": raw, "has_reasoning": has_reasoning,
                     "step_count": step_count, "patterns": patterns, "answer": answer, "confidence": confidence})
  return results

main():
  dataset = load_truthfulqa_mc2()
  client = APIClient()
  baseline_results = run_condition(dataset, "baseline", client)
  cot_results = run_condition(dataset, "cot", client)
  baseline_metrics = compute_metrics(baseline_results)
  cot_metrics = compute_metrics(cot_results)
  gate = check_gate(cot_metrics, baseline_metrics)
  json.dump({"baseline": baseline_results, "cot": cot_results,
             "baseline_metrics": baseline_metrics, "cot_metrics": cot_metrics, "gate": gate},
            open("results/h-m1_results.json", "w"), indent=2)
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | run_condition loop | Iterate dataset, build prompt per condition |
| L-7-2 | Per-item extraction pipeline | detect/count/classify/extract_answer/extract_confidence chain |
| L-7-3 | Cache key scheme | `{condition}_{index}` for reproducible dedup |
| L-7-4 | main() data+client setup | load_truthfulqa_mc2 + APIClient init |
| L-7-5 | main() dual-condition run | baseline then cot run_condition calls |
| L-7-6 | Metrics + gate assembly | compute_metrics x2, check_gate |
| L-7-7 | Results JSON write | Full results + metrics + gate to disk |

---

## A-8: Visualization [Complexity: 6, Budget: 6]

**Applied**: Standard matplotlib bar/hist/pie plots

```python
def plot_gate_metrics(baseline_rate: float, cot_rate: float, out_dir: str) -> None:
    """Bar chart: baseline vs CoT reasoning_presence_rate."""
    ...

def plot_step_count_histogram(cot_results: list[dict], out_dir: str) -> None:
    """Histogram of step_count across CoT results."""
    ...

def plot_example_comparison(baseline_results: list[dict], cot_results: list[dict], out_dir: str) -> None:
    """Side-by-side text panel: 3 example question/baseline/cot triples."""
    ...

def plot_pattern_breakdown(cot_results: list[dict], out_dir: str) -> None:
    """Pie chart: numbered/ordinal/logical pattern frequency across CoT results."""
    ...
```

### Pseudo-code

```
plot_gate_metrics: plt.bar(["Baseline","CoT"], [baseline_rate, cot_rate]); axhline(0.90); savefig(out_dir/"gate_metrics.png")
plot_step_count_histogram: plt.hist([r["step_count"] for r in cot_results], bins=range(0,15)); savefig(...)
plot_example_comparison: pick 3 random indices; text subplot per pair (question, baseline raw_output, cot raw_output)
plot_pattern_breakdown: counts = sum bool per pattern key across cot_results; plt.pie(counts.values(), labels=counts.keys())
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | Gate bar chart | Baseline vs CoT rate bars + 0.90 threshold line |
| L-8-2 | Step histogram | step_count distribution bins |
| L-8-3 | Example selection | Sample 3 items present in both result sets |
| L-8-4 | Example text panel | Multi-subplot text comparison figure |
| L-8-5 | Pattern counts | Aggregate numbered/ordinal/logical bool counts |
| L-8-6 | Pie chart render | plt.pie + savefig for pattern_breakdown.png |

---

## External Dependencies (Base Hypothesis)

None. H-E1 has no implemented code (`code/` directory absent); no cross-hypothesis import. H-M1 reuses only H-E1's *design conventions* (disk-cached API client, regex extraction style) as reference, not as callable API.
