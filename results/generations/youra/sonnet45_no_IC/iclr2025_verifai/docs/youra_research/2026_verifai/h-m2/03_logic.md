# Logic Design: h-m2
## LLM Semantic Extraction Validation

**Date:** 2026-07-14
**Hypothesis Type:** MECHANISM (Extraction Quality Evaluation)
**Complexity Tier:** STANDARD
**Subtask Budget:** 7 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-m1 actual code
**Analyzed Path:** docs/youra_research/h-m1/code/src/
**Relevant Symbols:** TraceParser, NLContentValidator (reused without modification)

**Key Findings:**
- TraceParser API verified: `__init__(trace_folder: Path)`, `load_all_traces() -> List[Dict]`
- NLContentValidator API verified: `__init__(min_word_count: int = 10)`, `validate_nl_presence(tool_call: dict) -> Tuple[bool, int, int]`
- Both modules will be copied directly from h-m1 (no modifications required)
- Parameter names match spec: `trace_folder`, `min_word_count`, `tool_call`

---

## Applied Patterns

**Applied:** Google Python API style (class-based, type hints)
**Applied:** OpenReview M3Y74vmsMcY (Cohen's Kappa for inter-rater agreement)
**Applied:** sklearn metrics patterns (precision/recall computation)

---

## M2-2: Sample Selector [Complexity: 9, Budget: 1]

**Applied:** Stratified sampling with outcome/tool-type balancing

### API Signatures

```python
import random
from typing import List, Dict
from nl_content_validator import NLContentValidator

class SampleSelector:
    """Stratified sampling for LLM extraction validation."""
    
    def __init__(self, validator: NLContentValidator, random_seed: int = 42):
        """Initialize selector. validator: NLContentValidator, random_seed: int"""
        self.validator = validator
        random.seed(random_seed)
    
    def stratified_sample(
        self,
        traces: List[Dict],
        n_queries: int = 25,
        n_results: int = 25
    ) -> Dict[str, List[Dict]]:
        """Sample tool calls with balancing. -> {"queries": [...], "results": [...]}"""
        ...
    
    def filter_by_outcome(self, traces: List[Dict], outcome: str) -> List[Dict]:
        """Filter traces by success/fail. outcome: "success" | "fail" -> filtered_traces"""
        ...
    
    def get_tool_type(self, tool_name: str) -> str:
        """Classify tool type. -> "research" | "data" | "other" """
        ...
```

### Pseudo-code

```
stratified_sample(traces, n_queries=25, n_results=25):
    # Flatten tool calls with metadata
    all_calls = []
    for trace in traces:
        for call in trace['tool_calls']:
            is_valid, query_words, result_words = validator.validate_nl_presence(call)
            if is_valid:
                all_calls.append({
                    'call': call,
                    'outcome': trace['outcome'],
                    'tool_type': get_tool_type(call['tool_name']),
                    'query_words': query_words,
                    'result_words': result_words
                })
    
    # Sample queries (query_words >= 10)
    query_candidates = [c for c in all_calls if c['query_words'] >= 10]
    queries = stratified_sample_by_groups(query_candidates, n_queries, keys=['outcome', 'tool_type'])
    
    # Sample results (result_words >= 10)
    result_candidates = [c for c in all_calls if c['result_words'] >= 10]
    results = stratified_sample_by_groups(result_candidates, n_results, keys=['outcome', 'tool_type'])
    
    return {"queries": queries, "results": results}

get_tool_type(tool_name):
    research_tools = ['rag_search', 'exa_search', 'arxiv_search']
    data_tools = ['read_file', 'glob', 'grep']
    
    if any(t in tool_name.lower() for t in research_tools):
        return "research"
    elif any(t in tool_name.lower() for t in data_tools):
        return "data"
    else:
        return "other"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-2-1 | Stratified sampling | Implement outcome/tool-type balancing, NL content filtering |

---

## M2-3: LLM Extractor [Complexity: 14, Budget: 2]

**Applied:** Few-shot prompting with multi-vote consensus

### API Signatures

```python
import json
from typing import List, Dict, Optional
from anthropic import Anthropic

class LLMExtractor:
    """LLM-based semantic extraction with consensus voting."""
    
    def __init__(
        self,
        model_name: str = "claude-sonnet-4-5",
        temperature: float = 0.0,
        api_key: Optional[str] = None
    ):
        """Initialize extractor. model_name: str, temperature: float, api_key: Optional[str]"""
        self.model = model_name
        self.temperature = temperature
        self.client = Anthropic(api_key=api_key)
    
    def extract_assumptions(self, query_text: str, prompt_template: str) -> List[str]:
        """Extract assumptions from query. query_text: str -> ["assumption1", ...]"""
        ...
    
    def extract_claims(self, result_text: str, prompt_template: str) -> List[str]:
        """Extract claims from result. result_text: str -> ["claim1", ...]"""
        ...
    
    def multi_vote_extract(
        self,
        text: str,
        prompt_template: str,
        n_votes: int = 3
    ) -> List[str]:
        """Multi-vote consensus extraction. -> consensus_items (≥2/3 votes)"""
        ...
    
    def _call_llm_api(self, prompt: str, max_retries: int = 3) -> str:
        """Call LLM API with retry. prompt: str -> response_text"""
        ...
    
    def _parse_json_response(self, response: str) -> List[str]:
        """Parse JSON list from response. response: str -> ["item1", "item2", ...]"""
        ...
```

### Pseudo-code

```
multi_vote_extract(text, prompt_template, n_votes=3):
    extracts = []
    
    for vote_id in range(n_votes):
        prompt = prompt_template.format(text=text)
        response = _call_llm_api(prompt)
        items = _parse_json_response(response)
        extracts.append(items)
    
    # Consensus: items in ≥2/3 votes
    item_counts = Counter([item for extract in extracts for item in extract])
    consensus = [item for item, count in item_counts.items() if count >= 2]
    
    return consensus

_call_llm_api(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise

_parse_json_response(response):
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Fallback: regex extraction for list-like strings
        matches = re.findall(r'"([^"]+)"', response)
        return matches
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-3-1 | LLM API client | Implement Anthropic/OpenAI client, retry logic, JSON parsing |
| L-M2-3-2 | Multi-vote consensus | Implement 3-vote extraction, ≥2/3 agreement filtering |

---

## M2-4: Annotation Manager [Complexity: 12, Budget: 2]

**Applied:** Cohen's Kappa for inter-rater agreement (sklearn)

### API Signatures

```python
import json
from pathlib import Path
from typing import Dict, List
from sklearn.metrics import cohen_kappa_score

class AnnotationManager:
    """Manage human annotations and compute consensus."""
    
    def __init__(self, annotation_dir: Path):
        """Initialize manager. annotation_dir: Path"""
        self.annotation_dir = Path(annotation_dir)
    
    def create_annotation_template(
        self,
        samples: Dict[str, List[Dict]],
        output_path: Path
    ) -> None:
        """Generate annotation template JSON. samples: Dict -> template.json"""
        ...
    
    def load_annotations(self, annotator_id: str) -> Dict[str, List[str]]:
        """Load annotator file. annotator_id: "1" | "2" -> {sample_id: [items]}"""
        ...
    
    def compute_inter_rater_kappa(
        self,
        annotations_1: Dict[str, List[str]],
        annotations_2: Dict[str, List[str]]
    ) -> float:
        """Compute Cohen's Kappa. -> kappa_score (≥0.70 threshold)"""
        ...
    
    def compute_consensus(
        self,
        annotations_1: Dict[str, List[str]],
        annotations_2: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Resolve disagreements via union. -> {sample_id: consensus_items}"""
        ...
```

### Pseudo-code

```
compute_inter_rater_kappa(annotations_1, annotations_2):
    # Convert to binary presence vectors
    all_items = set()
    for sample_id in annotations_1.keys():
        all_items.update(annotations_1[sample_id])
        all_items.update(annotations_2[sample_id])
    
    y1, y2 = [], []
    for sample_id in annotations_1.keys():
        for item in all_items:
            y1.append(1 if item in annotations_1[sample_id] else 0)
            y2.append(1 if item in annotations_2[sample_id] else 0)
    
    return cohen_kappa_score(y1, y2)

compute_consensus(annotations_1, annotations_2):
    consensus = {}
    for sample_id in annotations_1.keys():
        # Union of both annotators (majority rule for disagreements)
        consensus[sample_id] = list(set(annotations_1[sample_id]) | set(annotations_2[sample_id]))
    return consensus
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-4-1 | Annotation loading | Implement JSON template generation, validation, loading |
| L-M2-4-2 | Kappa computation | Implement Cohen's Kappa calculation, consensus resolution |

---

## M2-5: Extraction Evaluator [Complexity: 10, Budget: 1]

**Applied:** sklearn precision/recall patterns

### API Signatures

```python
import json
from pathlib import Path
from typing import Dict, List

class ExtractionEvaluator:
    """Evaluate LLM extraction quality against human gold standard."""
    
    def __init__(
        self,
        precision_threshold: float = 0.70,
        recall_threshold: float = 0.80,
        kappa_threshold: float = 0.70
    ):
        """Initialize evaluator. precision_threshold: 0.70, recall_threshold: 0.80"""
        self.precision_threshold = precision_threshold
        self.recall_threshold = recall_threshold
        self.kappa_threshold = kappa_threshold
    
    def evaluate_extraction(
        self,
        llm_items: List[str],
        human_items: List[str]
    ) -> Dict[str, float]:
        """Compute precision/recall. -> {"precision": 0.XX, "recall": 0.XX, "f1": 0.XX}"""
        ...
    
    def check_gate_condition(
        self,
        precision: float,
        recall: float,
        kappa: float
    ) -> bool:
        """Check MUST_WORK gate. -> True if ALL thresholds met"""
        ...
    
    def aggregate_results(
        self,
        per_sample_results: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """Aggregate across samples. -> {"precision_mean": 0.XX, "recall_mean": 0.XX, ...}"""
        ...
    
    def save_results(self, results: Dict, output_path: Path) -> None:
        """Save results JSON. results: Dict -> h_m2_results.json"""
        ...
```

### Pseudo-code

```
evaluate_extraction(llm_items, human_items):
    llm_set = set(llm_items)
    human_set = set(human_items)
    
    tp = len(llm_set & human_set)
    fp = len(llm_set - human_set)
    fn = len(human_set - llm_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}

check_gate_condition(precision, recall, kappa):
    return (
        precision >= self.precision_threshold and
        recall >= self.recall_threshold and
        kappa >= self.kappa_threshold
    )
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-5-1 | Metrics computation | Implement precision/recall calculation, gate check, aggregation |

---

## M2-6: Visualizer [Complexity: 11, Budget: 1]

**Applied:** Matplotlib subplot patterns

### API Signatures

```python
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict

class Visualizer:
    """Generate validation figures."""
    
    def __init__(self, output_dir: Path, dpi: int = 300):
        """Initialize visualizer. output_dir: Path, dpi: 300"""
        self.output_dir = Path(output_dir)
        self.dpi = dpi
    
    def plot_gate_metrics(
        self,
        precision: float,
        recall: float,
        kappa: float,
        thresholds: Dict[str, float]
    ) -> None:
        """Bar chart with threshold lines. -> fig1_gate_metrics.png"""
        ...
    
    def plot_confusion_matrix(self, results: Dict[str, int]) -> None:
        """Heatmap of TP/FP/FN/TN. results: {"tp": X, "fp": Y, ...} -> fig2_confusion.png"""
        ...
    
    def plot_per_category_performance(
        self,
        assumptions_results: Dict,
        claims_results: Dict
    ) -> None:
        """Grouped bar chart. -> fig3_per_category.png"""
        ...
    
    def plot_error_examples(self, errors: Dict[str, List[str]]) -> None:
        """Sample FP/FN examples. errors: {"false_positives": [...], ...} -> fig4_errors.png"""
        ...
    
    def generate_all_figures(
        self,
        results: Dict,
        errors: Dict
    ) -> None:
        """Generate all 4 figures. results: Dict, errors: Dict -> 4 PNG files"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-6-1 | Figure generation | Implement 4 plots (gate metrics, confusion matrix, per-category, errors) |

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from base hypothesis. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-m1/code/src/trace_parser.py (ACTUAL CODE)
class TraceParser:
    """Parse MCP trace files in JSONL format."""
    
    def __init__(self, trace_folder: Path):
        """Initialize parser. trace_folder: Path"""
        ...
    
    def discover_traces(self) -> List[Path]:
        """Discover .jsonl files. -> List[Path]"""
        ...
    
    def parse_trace_file(self, file_path: Path) -> Dict:
        """Parse single trace. -> {"file": str, "outcome": str, "tool_calls": List[Dict]}"""
        ...
    
    def load_all_traces(self) -> List[Dict]:
        """Load all traces. -> List[Dict]"""
        ...

# From: docs/youra_research/h-m1/code/src/nl_content_validator.py (ACTUAL CODE)
class NLContentValidator:
    """Validate natural language content in tool calls."""
    
    NL_WORD_PATTERN = r'\b[a-zA-Z]{2,}\b'
    
    def __init__(self, min_word_count: int = 10):
        """Initialize validator. min_word_count: int"""
        ...
    
    def count_nl_words(self, text: str) -> int:
        """Count NL words. text: str -> word_count: int"""
        ...
    
    def extract_text_from_dict(self, obj: Any) -> str:
        """Recursively extract strings. obj: Any -> concatenated_text: str"""
        ...
    
    def validate_nl_presence(self, tool_call: dict) -> Tuple[bool, int, int]:
        """Validate NL content. tool_call: dict -> (is_valid, query_words, result_words)"""
        ...
    
    def get_source_type(self, query_words: int, result_words: int) -> str:
        """Classify NL source. -> "both" | "query_only" | "result_only" | "neither" """
        ...
```

**Verified from:** `docs/youra_research/h-m1/code/src/` (actual implementation, NOT spec)

---

## Self-Validation

### Quick Checks
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes N/A (non-training pipeline)
- [x] Subtask count: 7/7 used
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Base hypothesis API signatures verified from actual code
- [x] External Dependencies API section included

### Serena MCP Validation
- [x] Base hypothesis exists → Actual code verified from h-m1/code/
- [x] API signatures match actual implementation (TraceParser, NLContentValidator)
- [x] Parameter names exactly match actual code

### Base Hypothesis Checks
- [x] Read actual code from h-m1/code/src/
- [x] API signatures verified from implementation (not specs)
- [x] Parameter names exactly match: `trace_folder`, `min_word_count`, `tool_call`
- [x] External Dependencies API section included

---

**Document Status:** Ready for Phase 4 Implementation
**Next Phase:** Phase 4 Coder - Implement all modules per logic design
**Estimated Effort:** 10-12 hours (STANDARD complexity tier)
