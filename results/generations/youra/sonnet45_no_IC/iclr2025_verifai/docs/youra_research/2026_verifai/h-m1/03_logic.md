# Logic Design: h-m1
## Natural Language Content Validation

**Date:** 2026-07-14
**Hypothesis Type:** MECHANISM (Data Analysis)
**Complexity Tier:** LIGHT
**Subtask Budget:** 5 subtasks (for M2, M3, M5, M7)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Extending h-e1 validation pipeline with NL-specific logic
**Analyzed Path:** docs/youra_research/h-e1/code/
**Relevant Symbols:** TraceParser, CompletenessValidator (base for NLContentValidator), MetricsCalculator, Evaluator, Visualizer

**Key Findings:**
- TraceParser reused without modification (Path parameter, sorted results)
- CompletenessValidator provides extract_nl_content() and count_words() - will enhance with regex
- MetricsCalculator uses validator instance for rate calculations
- Actual parameter names verified from implementation

---

## Applied Patterns

**Applied:** Regex-based NL word counting (LAION-5B text quality filtering)
**Applied:** Modular validation pipeline (reuse H-E1 structure)
**Applied:** Matplotlib subplot visualization patterns

---

## M2: NL Content Validator [Complexity: 10, Budget: 1]

**Applied:** Regex word extraction with recursive text aggregation

### API Signatures

```python
import re
from typing import Tuple

class NLContentValidator:
    """Validate natural language content in tool calls."""
    
    NL_WORD_PATTERN = r'\b[a-zA-Z]{2,}\b'
    
    def __init__(self, min_word_count: int = 10):
        """Initialize validator."""
        self.min_word_count = min_word_count
        self.pattern = re.compile(self.NL_WORD_PATTERN)
    
    def count_nl_words(self, text: str) -> int:
        """Count NL words (≥2 alphabetic chars). text -> word_count"""
        if not isinstance(text, str):
            return 0
        return len(self.pattern.findall(text))
    
    def extract_text_from_dict(self, obj) -> str:
        """Recursively extract strings. obj -> concatenated_text"""
        if obj is None:
            return ""
        if isinstance(obj, str):
            return obj
        if isinstance(obj, dict):
            return " ".join(self.extract_text_from_dict(v) for v in obj.values())
        if isinstance(obj, list):
            return " ".join(self.extract_text_from_dict(item) for item in obj)
        return str(obj)
    
    def validate_nl_presence(self, tool_call: dict) -> Tuple[bool, int, int]:
        """Validate NL content in params and results.
        
        Returns:
            (is_valid, query_words, result_words)
        """
        params_text = self.extract_text_from_dict(tool_call.get('parameters', {}))
        result_text = self.extract_text_from_dict(tool_call.get('result', ''))
        
        query_words = self.count_nl_words(params_text)
        result_words = self.count_nl_words(result_text)
        total_words = query_words + result_words
        
        return (total_words >= self.min_word_count, query_words, result_words)
    
    def get_source_type(self, query_words: int, result_words: int) -> str:
        """Classify NL source type."""
        has_query = query_words >= 5
        has_result = result_words >= 5
        
        if has_query and has_result:
            return "both"
        elif has_query:
            return "query_only"
        elif has_result:
            return "result_only"
        else:
            return "neither"
```

### Pseudo-code

```
count_nl_words(text):
    if not isinstance(text, str):
        return 0
    matches = re.findall(r'\b[a-zA-Z]{2,}\b', text)
    return len(matches)

extract_text_from_dict(obj):
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        texts = [extract_text_from_dict(v) for v in obj.values()]
        return " ".join(texts)
    if isinstance(obj, list):
        texts = [extract_text_from_dict(item) for item in obj]
        return " ".join(texts)
    return str(obj)

validate_nl_presence(tool_call):
    params_text = extract_text_from_dict(tool_call['parameters'])
    result_text = extract_text_from_dict(tool_call['result'])
    
    query_words = count_nl_words(params_text)
    result_words = count_nl_words(result_text)
    total_words = query_words + result_words
    
    return (total_words >= 10, query_words, result_words)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-1 | Regex NL extraction | Implement regex pattern matching, recursive text aggregation, source type detection |

---

## M3: Metrics Calculator [Complexity: 11, Budget: 2]

**Applied:** Source breakdown analysis, statistical binning

### API Signatures

```python
from typing import List, Dict
from .nl_content_validator import NLContentValidator

class MetricsCalculator:
    """Calculate NL content metrics."""
    
    def __init__(self, validator: NLContentValidator):
        """Initialize with validator instance."""
        self.validator = validator
    
    def calculate_nl_presence_rate(self, traces: List[Dict]) -> float:
        """Calculate NL presence rate. traces -> rate [0.0, 1.0]"""
        total_calls = 0
        calls_with_nl = 0
        
        for trace in traces:
            for tool_call in trace['tool_calls']:
                total_calls += 1
                is_valid, _, _ = self.validator.validate_nl_presence(tool_call)
                if is_valid:
                    calls_with_nl += 1
        
        if total_calls == 0:
            return 0.0
        return calls_with_nl / total_calls
    
    def calculate_source_breakdown(self, traces: List[Dict]) -> Dict[str, int]:
        """Count calls by source type.
        
        Returns:
            Dict with keys: query_only, result_only, both, neither
        """
        breakdown = {"query_only": 0, "result_only": 0, "both": 0, "neither": 0}
        
        for trace in traces:
            for tool_call in trace['tool_calls']:
                _, query_words, result_words = self.validator.validate_nl_presence(tool_call)
                source_type = self.validator.get_source_type(query_words, result_words)
                breakdown[source_type] += 1
        
        return breakdown
    
    def calculate_tool_type_breakdown(self, traces: List[Dict]) -> Dict[str, Dict]:
        """Calculate NL presence by tool type.
        
        Returns:
            Dict with keys: research, data_processing (each with total, with_nl, rate)
        """
        research_tools = ['rag_search', 'rag_read', 'mcp__archon']
        
        stats = {
            "research": {"total": 0, "with_nl": 0, "rate": 0.0},
            "data_processing": {"total": 0, "with_nl": 0, "rate": 0.0}
        }
        
        for trace in traces:
            for tool_call in trace['tool_calls']:
                tool_name = tool_call.get('tool_name', '')
                is_valid, _, _ = self.validator.validate_nl_presence(tool_call)
                
                is_research = any(rt in tool_name for rt in research_tools)
                category = "research" if is_research else "data_processing"
                
                stats[category]["total"] += 1
                if is_valid:
                    stats[category]["with_nl"] += 1
        
        # Calculate rates
        for category in stats:
            if stats[category]["total"] > 0:
                stats[category]["rate"] = stats[category]["with_nl"] / stats[category]["total"]
        
        return stats
    
    def calculate_word_count_distribution(self, traces: List[Dict]) -> Dict[str, int]:
        """Bin word counts.
        
        Returns:
            Dict with keys: 0-5, 5-10, 10-20, 20-50, 50+
        """
        bins = {"0-5": 0, "5-10": 0, "10-20": 0, "20-50": 0, "50+": 0}
        
        for trace in traces:
            for tool_call in trace['tool_calls']:
                _, query_words, result_words = self.validator.validate_nl_presence(tool_call)
                total_words = query_words + result_words
                
                if total_words < 5:
                    bins["0-5"] += 1
                elif total_words < 10:
                    bins["5-10"] += 1
                elif total_words < 20:
                    bins["10-20"] += 1
                elif total_words < 50:
                    bins["20-50"] += 1
                else:
                    bins["50+"] += 1
        
        return bins
```

### Pseudo-code

```
calculate_nl_presence_rate(traces):
    total = 0
    with_nl = 0
    for trace in traces:
        for tool_call in trace['tool_calls']:
            total += 1
            is_valid, _, _ = validator.validate_nl_presence(tool_call)
            if is_valid:
                with_nl += 1
    return with_nl / total if total > 0 else 0.0

calculate_source_breakdown(traces):
    breakdown = {query_only: 0, result_only: 0, both: 0, neither: 0}
    for trace in traces:
        for tool_call in trace['tool_calls']:
            _, query_words, result_words = validator.validate_nl_presence(tool_call)
            source_type = validator.get_source_type(query_words, result_words)
            breakdown[source_type] += 1
    return breakdown
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M3-1 | NL presence rate | Single-pass aggregation with NL validator |
| L-M3-2 | Breakdown metrics | Source type, tool type, word count distribution binning |

---

## M5: Visualizer [Complexity: 12, Budget: 1]

**Applied:** Matplotlib bar charts, histograms, stacked bar charts

### API Signatures

```python
from pathlib import Path
from typing import List, Dict
import matplotlib.pyplot as plt

class Visualizer:
    """Generate NL content analysis figures."""
    
    def __init__(self, output_dir: Path, dpi: int = 300):
        """Initialize with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
    
    def plot_gate_metrics(self, results: Dict) -> None:
        """Generate figure 1: Gate metrics bar chart.
        
        Args:
            results: Dict with nl_presence_rate, threshold, gate_passed
        
        Saves:
            {output_dir}/fig1_gate_metrics.png
        """
        ...
    
    def plot_word_count_distribution(self, traces: List[Dict], validator) -> None:
        """Generate figure 2: Word count histogram.
        
        Saves:
            {output_dir}/fig2_word_count_distribution.png
        """
        ...
    
    def plot_nl_source_breakdown(self, results: Dict) -> None:
        """Generate figure 3: Source breakdown stacked bar.
        
        Saves:
            {output_dir}/fig3_nl_source_breakdown.png
        """
        ...
    
    def plot_nl_by_tool_type(self, results: Dict) -> None:
        """Generate figure 4: NL rate by tool type.
        
        Saves:
            {output_dir}/fig4_nl_by_tool_type.png
        """
        ...
    
    def generate_all_figures(self, traces: List[Dict], results: Dict, validator) -> None:
        """Generate all 4 figures."""
        self.plot_gate_metrics(results)
        self.plot_word_count_distribution(traces, validator)
        self.plot_nl_source_breakdown(results)
        self.plot_nl_by_tool_type(results)
```

### Pseudo-code

```
plot_gate_metrics(results):
    fig, ax = plt.subplots(figsize=(8, 6))
    
    actual_rate = results['nl_presence_rate'] * 100
    threshold = results['threshold'] * 100
    
    colors = ['green' if results['gate_passed'] else 'red', 'blue']
    ax.bar(['Actual', 'Threshold'], [actual_rate, threshold], color=colors)
    ax.axhline(y=90, color='red', linestyle='--', label='Gate: 90%')
    ax.set_ylabel('NL Presence Rate (%)')
    ax.set_title('H-M1: Gate Metrics')
    ax.legend()
    
    plt.savefig(output_dir / 'fig1_gate_metrics.png', dpi=300)
    plt.close()

plot_word_count_distribution(traces, validator):
    word_counts = []
    for trace in traces:
        for tool_call in trace['tool_calls']:
            _, query_words, result_words = validator.validate_nl_presence(tool_call)
            word_counts.append(query_words + result_words)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(word_counts, bins=[0, 5, 10, 20, 50, 100, 200], edgecolor='black')
    ax.axvline(x=10, color='red', linestyle='--', label='Threshold: 10 words')
    ax.set_xlabel('Total Word Count')
    ax.set_ylabel('Number of Tool Calls')
    ax.set_title('Word Count Distribution')
    ax.legend()
    
    plt.savefig(output_dir / 'fig2_word_count_distribution.png', dpi=300)
    plt.close()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M5-1 | NL-specific figures | 4 matplotlib plots (gate bar chart, histogram, source breakdown, tool type) |

---

## M7: Integration & Testing [Complexity: 9, Budget: 1]

**Applied:** Unit testing for regex patterns, orchestration with progress tracking

### API Signatures

```python
import argparse
from pathlib import Path
from typing import List, Dict

def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments.
    
    Returns:
        Namespace with trace_folder, hypothesis_folder
    """
    parser = argparse.ArgumentParser(description='H-M1: Natural Language Content Validation')
    parser.add_argument('--trace_folder', type=str, required=True, help='Path to mcp_traces directory')
    parser.add_argument('--hypothesis_folder', type=str, required=True, help='Path to h-m1 output directory')
    return parser.parse_args()

def setup_logging() -> None:
    """Configure logging with timestamps."""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main() -> int:
    """Main orchestration.
    
    Returns:
        Exit code (0 for PASS, 1 for FAIL)
    """
    ...
```

### Pseudo-code

```
main():
    args = parse_arguments()
    setup_logging()
    
    # Phase 1: Load traces (reuse H-E1 TraceParser)
    from src.trace_parser import TraceParser
    parser = TraceParser(Path(args.trace_folder))
    traces = parser.load_all_traces()
    
    # Phase 2: Validate NL content
    validator = NLContentValidator(min_word_count=10)
    calculator = MetricsCalculator(validator)
    
    nl_rate = calculator.calculate_nl_presence_rate(traces)
    source_breakdown = calculator.calculate_source_breakdown(traces)
    tool_type_breakdown = calculator.calculate_tool_type_breakdown(traces)
    word_distribution = calculator.calculate_word_count_distribution(traces)
    
    # Phase 3: Evaluate gate
    evaluator = Evaluator(calculator, threshold=0.90)
    results = evaluator.evaluate_hypothesis(traces)
    
    # Phase 4: Output
    output_path = Path(args.hypothesis_folder) / 'h_m1_results.json'
    evaluator.save_results(results, output_path)
    
    visualizer = Visualizer(Path(args.hypothesis_folder) / 'figures')
    visualizer.generate_all_figures(traces, results, validator)
    
    # Console summary
    print("\n" + "="*60)
    print("H-M1: NATURAL LANGUAGE CONTENT VALIDATION")
    print("="*60)
    print(f"NL Presence Rate: {results['nl_presence_rate']:.2%}")
    print(f"Threshold: {results['threshold']:.0%}")
    print(f"Gate Result: {'PASS' if results['gate_passed'] else 'FAIL'}")
    print("="*60 + "\n")
    
    return 0 if results['gate_passed'] else 1
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M7-1 | Integration & tests | CLI orchestration, unit tests for regex word counting and source type detection |

---

## Supporting Module APIs (Low Complexity - No Subtasks)

### TraceParser (M1 - Reused from H-E1)

```python
from pathlib import Path
from typing import List, Dict
import json

class TraceParser:
    """Parse MCP trace files in JSONL format."""
    
    def __init__(self, trace_folder: Path):
        """Initialize parser."""
        self.trace_folder = Path(trace_folder)
    
    def discover_traces(self) -> List[Path]:
        """Find all .jsonl files. -> List[Path]"""
        if not self.trace_folder.exists():
            raise FileNotFoundError(f"Trace folder not found: {self.trace_folder}")
        traces = list(self.trace_folder.glob("*.jsonl"))
        if not traces:
            raise FileNotFoundError(f"No .jsonl files found in {self.trace_folder}")
        return sorted(traces)
    
    def parse_trace_file(self, file_path: Path) -> Dict:
        """Parse single JSONL file. file_path -> Dict(file, outcome, tool_calls)"""
        tool_calls = []
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    tool_call = json.loads(line)
                    tool_calls.append(tool_call)
                except json.JSONDecodeError as e:
                    print(f"Warning: {file_path.name} line {line_num} malformed - {e}")
                    continue
        
        outcome = "fail" if "fail" in file_path.name.lower() else "success"
        return {"file": file_path.name, "outcome": outcome, "tool_calls": tool_calls}
    
    def load_all_traces(self) -> List[Dict]:
        """Load all traces. -> List[Dict]"""
        trace_files = self.discover_traces()
        traces = []
        for i, trace_file in enumerate(trace_files, 1):
            print(f"  Loading trace {i}/{len(trace_files)}: {trace_file.name}")
            trace = self.parse_trace_file(trace_file)
            traces.append(trace)
        return traces
```

### Evaluator (M4 - Modified from H-E1)

```python
from pathlib import Path
from typing import Dict, List
import json

class Evaluator:
    """Evaluate NL content hypothesis."""
    
    def __init__(self, calculator, threshold: float = 0.90):
        """Initialize with calculator and threshold."""
        self.calculator = calculator
        self.threshold = threshold
    
    def evaluate_hypothesis(self, traces: List[Dict]) -> Dict:
        """Run evaluation.
        
        Returns:
            Dict with nl_presence_rate, threshold, gate_passed, source_breakdown, etc.
        """
        nl_rate = self.calculator.calculate_nl_presence_rate(traces)
        source_breakdown = self.calculator.calculate_source_breakdown(traces)
        tool_type_breakdown = self.calculator.calculate_tool_type_breakdown(traces)
        word_distribution = self.calculator.calculate_word_count_distribution(traces)
        
        gate_passed = nl_rate >= self.threshold
        
        return {
            'nl_presence_rate': nl_rate,
            'threshold': self.threshold,
            'gate_passed': gate_passed,
            'source_breakdown': source_breakdown,
            'tool_type_breakdown': tool_type_breakdown,
            'word_count_distribution': word_distribution,
            'total_calls': sum(len(t['tool_calls']) for t in traces)
        }
    
    def check_gate_condition(self, results: Dict) -> bool:
        """Check gate condition. results -> bool"""
        return results['gate_passed']
    
    def save_results(self, results: Dict, output_path: Path) -> None:
        """Save results to JSON."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
```

### Config (M1 - Modified from H-E1)

```python
from pathlib import Path

class Config:
    """Configuration constants."""
    
    TRACE_FOLDER: str = None
    HYPOTHESIS_FOLDER: str = None
    
    @property
    def FIGURES_DIR(self) -> Path:
        return Path(self.HYPOTHESIS_FOLDER) / 'figures'
    
    @property
    def RESULTS_FILE(self) -> Path:
        return Path(self.HYPOTHESIS_FOLDER) / 'h_m1_results.json'
    
    NL_THRESHOLD: float = 0.90
    MIN_WORD_COUNT: int = 10
    NL_WORD_PATTERN: str = r'\b[a-zA-Z]{2,}\b'
    REQUIRED_FIELDS: List[str] = ['tool_name', 'parameters', 'result']
    FIGURE_DPI: int = 300
```

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are reused from h-e1. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-e1/code/src/trace_parser.py (ACTUAL CODE)
class TraceParser:
    def __init__(self, trace_folder: Path):
        """Initialize parser with trace folder path."""
        ...
    
    def discover_traces(self) -> List[Path]:
        """Discover all .jsonl trace files."""
        ...
    
    def parse_trace_file(self, file_path: Path) -> Dict:
        """Parse single JSONL file into Trace dict.
        
        Returns:
            Dict with keys: file, outcome, tool_calls
        """
        ...
    
    def load_all_traces(self) -> List[Dict]:
        """Load and parse all traces."""
        ...
```

**Verified from:** docs/youra_research/h-e1/code/ (actual implementation)

**Reuse Strategy:** Copy trace_parser.py directly from H-E1 (no modifications required)

---

## Data Structures

### Tool Call Schema
```python
ToolCall = {
    "tool_name": str,
    "parameters": dict,
    "result": Any
}
```

### Trace Schema
```python
Trace = {
    "file": str,
    "outcome": str,
    "tool_calls": List[ToolCall]
}
```

### Results Schema
```python
Results = {
    "nl_presence_rate": float,
    "threshold": float,
    "gate_passed": bool,
    "source_breakdown": Dict[str, int],
    "tool_type_breakdown": Dict[str, Dict],
    "word_count_distribution": Dict[str, int],
    "total_calls": int
}
```

---

## Error Handling

### Regex Pattern Failures
```python
if not isinstance(text, str):
    return 0
```

### Empty Tool Calls
```python
if total_calls == 0:
    return 0.0
```

### Visualization Edge Cases
```python
if not word_counts:
    word_counts = [0]  # Prevent empty histogram
```

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] Applied patterns documented
- [x] Docstrings 1-2 lines
- [x] Tensor shapes in comments (N/A for data pipeline)
- [x] Subtask count within budget (5/5 used)
- [x] Total length < 600 lines
- [x] Codebase Analysis section included
- [x] External Dependencies API section included
- [x] Actual code verified from h-e1/code/

---

**Document Status:** Ready for Phase 4 Implementation
**Next Phase:** Phase 4 Coder - Implement NL validation modules
**Estimated Effort:** 6-8 hours (7 Epic tasks, LIGHT complexity tier)
