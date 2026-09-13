# Experiment Design: H-M3

**Date:** 2026-08-19
**Author:** PrayPrey
**Hypothesis Statement:** Under sequential generation, if hedging markers appear before confidence verbalization, then the confidence estimate has access to these signals, because autoregressive generation keeps prior tokens in context.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing positional relationship in autoregressive generation.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M2 (VALIDATED - hedging_presence_rate 82.0%)
**Gate Status:** SHOULD_WORK (pending)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (hedging marker detection)

### Gate Condition
- **Primary:** >99% of outputs have correct CoT-then-confidence ordering
- **Secondary:** Hedging markers precede confidence in >95% of cases where markers exist
- **Gate Type:** SHOULD_WORK
- **Failure Response:** PIVOT (enforce stricter output format)

---

## Continuation Context

This hypothesis validates Step 3 of the causal chain: autoregressive generation ensures prior tokens (including hedging markers) remain in context when confidence is verbalized.

### Previous Hypothesis Results (H-M2)
| Metric | Value |
|--------|-------|
| Hedging Presence Rate | 82.0% |
| Mean Hedging Count | 2.84 markers/output |
| Total Samples | 817 (TruthfulQA) |
| Top Markers | may (787), could (619), but (337), however (255) |

**Key Insight:** 82% of CoT outputs contain hedging markers. H-M3 must verify these markers appear BEFORE the confidence statement in token sequence.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon MCP unavailable in this execution.

**Domain Knowledge Applied:**
- Autoregressive LLMs (GPT, Llama) generate tokens left-to-right
- Prior tokens are always in context for subsequent generation
- CoT+confidence prompt structure enforces reasoning → answer → confidence ordering
- Positional analysis requires parsing output structure, not new API calls

### Archon Code Examples

**Pattern: Positional Token Analysis**
```python
def analyze_marker_confidence_positions(output: str) -> dict:
    # Find confidence statement position
    confidence_match = re.search(r'Confidence:\s*(\d+)%', output)
    confidence_pos = confidence_match.start() if confidence_match else -1
    
    # Find all hedging marker positions
    markers = ['might', 'possibly', 'could', 'perhaps', 'may', 'however', 'uncertain']
    marker_positions = []
    for marker in markers:
        for match in re.finditer(rf'\b{marker}\b', output, re.I):
            marker_positions.append(match.start())
    
    # Calculate precedence
    markers_before = [p for p in marker_positions if p < confidence_pos]
    return {
        'confidence_position': confidence_pos,
        'marker_positions': marker_positions,
        'markers_before_confidence': len(markers_before),
        'total_markers': len(marker_positions),
        'all_markers_precede': len(markers_before) == len(marker_positions)
    }
```

### Exa GitHub Implementations

**Note:** Exa MCP unavailable in this execution.

**Implementation Approach:**
No external code needed—this is a text parsing/analysis task on H-M2 outputs.

### Implementation Priority Assessment

**For H-M3 (positional analysis):**
- This is NOT a paper reproduction task
- Implementation is straightforward text parsing
- No external dependencies required

**Recommended Implementation Path:**
- Primary: Parse H-M2 CoT+confidence outputs from cache
- Fallback: Re-generate subset if cache unavailable
- Justification: H-M3 is analysis of H-M2 outputs, not new generation

### Code Analysis (Serena MCP)

**Note:** Serena MCP optional and not required for this hypothesis.

H-M3 requires only:
1. Text parsing for output structure
2. Position detection for hedging markers
3. Position detection for confidence statement
4. Comparison of positions

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | TruthfulQA (Generation Split) |
| **Type** | standard |
| **Source** | HuggingFace `truthful_qa` |
| **Size** | 817 items (full generation split) |
| **Split** | Full test set (no train split for this benchmark) |
| **Preprocessing** | None (reuse H-M2 generated outputs) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthful_qa` (generation config)
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "generation")
# Use cached outputs from H-M2 experiment
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| **Model** | GPT-3.5-turbo (via OpenAI API) |
| **Mode** | Reuse H-M2 cached outputs |
| **Source** | H-M2 experiment cache |

**Loading Information** (for Phase 4 download):
- Method: Load from H-M2 cache
- Identifier: `../h-m2/code/results/` or API cache
- Code:
```python
import json
with open('../h-m2/code/results/h-m2_results.json', 'r') as f:
    cached_outputs = json.load(f)
```

#### Proposed Model

**Architecture:** Text parsing pipeline for positional analysis

**Core Mechanism Implementation:**

```python
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class PositionalAnalysis:
    output_id: str
    has_confidence: bool
    confidence_position: int
    hedging_markers: List[Tuple[str, int]]  # (marker, position)
    markers_before_confidence: int
    markers_after_confidence: int
    cot_then_confidence_order: bool
    
HEDGING_MARKERS = [
    'might', 'possibly', 'could', 'perhaps', 'may', 'likely', 
    'unlikely', 'however', 'uncertain', 'although', 'but',
    'difficult to determine', 'not certain', 'hard to say',
    'alternatively', 'on the other hand', 'it depends'
]

def extract_confidence_position(output: str) -> Tuple[int, int]:
    """Extract confidence statement position and value."""
    pattern = r'Confidence:\s*(\d+)%'
    match = re.search(pattern, output, re.IGNORECASE)
    if match:
        return match.start(), int(match.group(1))
    return -1, -1

def extract_hedging_positions(output: str) -> List[Tuple[str, int]]:
    """Find all hedging markers and their positions."""
    markers_found = []
    for marker in HEDGING_MARKERS:
        pattern = rf'\b{re.escape(marker)}\b'
        for match in re.finditer(pattern, output, re.IGNORECASE):
            markers_found.append((marker, match.start()))
    return sorted(markers_found, key=lambda x: x[1])

def analyze_output(output_id: str, output: str) -> PositionalAnalysis:
    """Analyze single output for marker-confidence positioning."""
    conf_pos, conf_val = extract_confidence_position(output)
    markers = extract_hedging_positions(output)
    
    has_conf = conf_pos >= 0
    before = [(m, p) for m, p in markers if p < conf_pos] if has_conf else []
    after = [(m, p) for m, p in markers if p >= conf_pos] if has_conf else []
    
    # CoT-then-confidence = confidence appears after reasoning content
    # Check: confidence not at start, and most content precedes it
    cot_order = has_conf and conf_pos > len(output) * 0.3
    
    return PositionalAnalysis(
        output_id=output_id,
        has_confidence=has_conf,
        confidence_position=conf_pos,
        hedging_markers=markers,
        markers_before_confidence=len(before),
        markers_after_confidence=len(after),
        cot_then_confidence_order=cot_order
    )

def compute_gate_metrics(analyses: List[PositionalAnalysis]) -> Dict:
    """Compute H-M3 gate metrics."""
    valid = [a for a in analyses if a.has_confidence]
    with_markers = [a for a in valid if len(a.hedging_markers) > 0]
    
    # Gate 1: >99% CoT-then-confidence ordering
    cot_order_rate = sum(1 for a in valid if a.cot_then_confidence_order) / len(valid)
    
    # Gate 2: >95% markers precede confidence (when markers exist)
    if with_markers:
        all_precede = sum(1 for a in with_markers 
                        if a.markers_after_confidence == 0) / len(with_markers)
    else:
        all_precede = 1.0  # vacuously true
    
    return {
        'total_outputs': len(analyses),
        'valid_outputs': len(valid),
        'outputs_with_markers': len(with_markers),
        'cot_order_rate': cot_order_rate,
        'markers_precede_rate': all_precede,
        'gate_1_pass': cot_order_rate > 0.99,
        'gate_2_pass': all_precede > 0.95,
        'all_gates_pass': cot_order_rate > 0.99 and all_precede > 0.95
    }
```

### Training Protocol

| Attribute | Value |
|-----------|-------|
| **Type** | Analysis only (no training) |
| **Input** | H-M2 cached CoT+confidence outputs |
| **Processing** | Sequential text parsing |
| **Compute** | CPU only (~5 seconds for 817 items) |

**No training required.** This is a positional analysis hypothesis validating autoregressive generation properties.

### Evaluation

| Metric | Description | Threshold |
|--------|-------------|-----------|
| **cot_order_rate** | % outputs with CoT-then-confidence ordering | >99% (Gate 1) |
| **markers_precede_rate** | % outputs where all markers precede confidence | >95% (Gate 2) |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: text_analysis
- Library: Built-in Python (re, dataclasses)
- Code:
```python
# No external metrics library needed
# Gate metrics computed in analyze_output() and compute_gate_metrics()
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing cot_order_rate and markers_precede_rate vs thresholds

#### Additional Figures (LLM Autonomous)
1. **Position Distribution**: Histogram of confidence statement positions (relative to output length)
2. **Marker Position Timeline**: Scatter plot showing marker positions vs confidence position per output
3. **Marker Type by Position**: Stacked bar showing which markers appear before vs after confidence

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `cot_order_rate > 0.99` (Gate 1)
3. `markers_precede_rate > 0.95` (Gate 2)

**Expected Outcome:** PASS - Autoregressive generation inherently produces tokens sequentially, and the prompt format enforces reasoning-before-confidence structure.

---

## Appendix: Reference Implementations

### Text Parsing Reference
- Standard Python `re` module for regex matching
- Position-based analysis straightforward

### Output Format Enforced by Prompt (from H-M2)
```
Let's think step by step.
[Reasoning content with potential hedging markers]

Answer: [A/B/C/D]

Confidence: [X]%
```

This format guarantees:
1. Reasoning content appears before answer
2. Answer appears before confidence
3. Hedging markers (in reasoning) precede confidence by construction

### Position Verification Logic
```python
# Simple sanity check: confidence at end of output
assert confidence_position > len(output) * 0.5, "Confidence should be in latter half"
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19T02:15:00Z

### Workflow History for This Hypothesis
- 2026-08-19T02:09:57: H-M3 set to IN_PROGRESS (external loop)
- 2026-08-19T02:15:00: Phase 2C experiment design initiated

---

*MCP Tools Used: None (MCP unavailable)*
*Implementation based on text parsing of H-M2 outputs*
*Next Phase: Phase 3 - Implementation Planning*
