# Logic Design: H-M3

**Hypothesis:** Positional Analysis of Marker-Confidence Ordering
**Date:** 2026-08-19

---

## Codebase Analysis (Serena)

**Note:** Serena MCP unavailable. Design based on H-M2 patterns.

---

## Applied Patterns

Applied: Dataclass Result Pattern
Applied: Regex Position Extraction Pattern
Applied: Gate Validation Pattern

---

## API Signatures

### 1. Data Loading API

```python
# data_loader.py

from typing import List, Dict, Any, Optional
from pathlib import Path

def load_h_m2_cache(cache_path: Path) -> List[Dict[str, Any]]:
    """
    Load cached H-M2 experiment outputs.
    
    Args:
        cache_path: Path to h-m2_results.json or similar cache file
        
    Returns:
        List of dicts with keys: 'output_id', 'output_text', 'confidence', etc.
        
    Raises:
        FileNotFoundError: If cache file doesn't exist
        ValueError: If cache format is invalid
    """
    pass

def validate_cache_format(data: List[Dict]) -> bool:
    """Validate cache has required fields."""
    pass
```

### 2. Position Extraction API

```python
# position_extractor.py

import re
from typing import Tuple, List, Optional

HEDGING_MARKERS = [
    'might', 'possibly', 'could', 'perhaps', 'may', 'likely', 
    'unlikely', 'however', 'uncertain', 'although', 'but',
    'difficult to determine', 'not certain', 'hard to say',
    'alternatively', 'on the other hand', 'it depends'
]

def extract_confidence_position(output: str) -> Tuple[int, int]:
    """
    Extract confidence statement position and value.
    
    Args:
        output: Full model output text
        
    Returns:
        Tuple of (character_position, confidence_value)
        Returns (-1, -1) if no confidence found
    """
    pattern = r'Confidence:\s*(\d+)%'
    match = re.search(pattern, output, re.IGNORECASE)
    if match:
        return match.start(), int(match.group(1))
    return -1, -1

def extract_hedging_positions(output: str) -> List[Tuple[str, int]]:
    """
    Find all hedging markers and their positions.
    
    Args:
        output: Full model output text
        
    Returns:
        List of (marker_text, character_position) tuples, sorted by position
    """
    markers_found = []
    for marker in HEDGING_MARKERS:
        pattern = rf'\b{re.escape(marker)}\b'
        for match in re.finditer(pattern, output, re.IGNORECASE):
            markers_found.append((marker, match.start()))
    return sorted(markers_found, key=lambda x: x[1])
```

### 3. Positional Analysis API

```python
# positional_analysis.py

from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class PositionalAnalysis:
    """Result container for single output analysis."""
    output_id: str
    has_confidence: bool
    confidence_position: int
    confidence_value: int
    hedging_markers: List[Tuple[str, int]]  # (marker, position)
    markers_before_confidence: int
    markers_after_confidence: int
    cot_then_confidence_order: bool
    output_length: int
    
def analyze_output(output_id: str, output: str) -> PositionalAnalysis:
    """
    Analyze single output for marker-confidence positioning.
    
    Args:
        output_id: Identifier for this output
        output: Full model output text
        
    Returns:
        PositionalAnalysis with all computed metrics
    """
    conf_pos, conf_val = extract_confidence_position(output)
    markers = extract_hedging_positions(output)
    
    has_conf = conf_pos >= 0
    if has_conf:
        before = [(m, p) for m, p in markers if p < conf_pos]
        after = [(m, p) for m, p in markers if p >= conf_pos]
    else:
        before, after = [], []
    
    # CoT-then-confidence: confidence appears in latter portion of output
    # Threshold: 30% into output (reasoning should precede confidence)
    cot_order = has_conf and conf_pos > len(output) * 0.3
    
    return PositionalAnalysis(
        output_id=output_id,
        has_confidence=has_conf,
        confidence_position=conf_pos,
        confidence_value=conf_val,
        hedging_markers=markers,
        markers_before_confidence=len(before),
        markers_after_confidence=len(after),
        cot_then_confidence_order=cot_order,
        output_length=len(output)
    )

def analyze_all_outputs(outputs: List[Dict]) -> List[PositionalAnalysis]:
    """Analyze all outputs in batch."""
    return [
        analyze_output(o.get('output_id', str(i)), o.get('output_text', ''))
        for i, o in enumerate(outputs)
    ]
```

### 4. Gate Metrics API

```python
# gate_metrics.py

from typing import List, Dict, Any

def compute_gate_metrics(analyses: List[PositionalAnalysis]) -> Dict[str, Any]:
    """
    Compute H-M3 gate validation metrics.
    
    Args:
        analyses: List of PositionalAnalysis results
        
    Returns:
        Dict with gate metrics and pass/fail status
    """
    valid = [a for a in analyses if a.has_confidence]
    with_markers = [a for a in valid if len(a.hedging_markers) > 0]
    
    # Gate 1: >99% CoT-then-confidence ordering
    cot_order_count = sum(1 for a in valid if a.cot_then_confidence_order)
    cot_order_rate = cot_order_count / len(valid) if valid else 0.0
    
    # Gate 2: >95% markers precede confidence (when markers exist)
    if with_markers:
        all_precede_count = sum(1 for a in with_markers 
                                if a.markers_after_confidence == 0)
        all_precede_rate = all_precede_count / len(with_markers)
    else:
        all_precede_rate = 1.0  # Vacuously true
    
    return {
        'total_outputs': len(analyses),
        'valid_outputs': len(valid),
        'outputs_with_markers': len(with_markers),
        'cot_order_rate': round(cot_order_rate, 4),
        'markers_precede_rate': round(all_precede_rate, 4),
        'gate_1_threshold': 0.99,
        'gate_2_threshold': 0.95,
        'gate_1_pass': cot_order_rate > 0.99,
        'gate_2_pass': all_precede_rate > 0.95,
        'all_gates_pass': cot_order_rate > 0.99 and all_precede_rate > 0.95
    }
```

### 5. Visualization API

```python
# visualization.py

import matplotlib.pyplot as plt
from typing import Dict, Any
from pathlib import Path

def plot_gate_comparison(metrics: Dict[str, Any], output_path: Path) -> None:
    """
    Generate gate metrics comparison bar chart.
    
    Args:
        metrics: Gate metrics dict from compute_gate_metrics
        output_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    labels = ['CoT Order Rate', 'Markers Precede Rate']
    values = [metrics['cot_order_rate'], metrics['markers_precede_rate']]
    thresholds = [metrics['gate_1_threshold'], metrics['gate_2_threshold']]
    
    x = range(len(labels))
    bars = ax.bar(x, values, color=['#2ecc71' if v > t else '#e74c3c' 
                                     for v, t in zip(values, thresholds)])
    
    # Add threshold lines
    for i, t in enumerate(thresholds):
        ax.axhline(y=t, xmin=i/len(labels)-0.1, xmax=(i+1)/len(labels)+0.1,
                   color='red', linestyle='--', linewidth=2)
    
    ax.set_ylabel('Rate')
    ax.set_title('H-M3 Gate Metrics vs Thresholds')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.1)
    
    # Add value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.1%}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
```

### 6. Experiment Runner API

```python
# run_experiment.py

import json
import yaml
from pathlib import Path
from typing import Dict, Any

def run_h_m3_experiment(
    cache_path: Path,
    output_dir: Path,
    figures_dir: Path
) -> Dict[str, Any]:
    """
    Run complete H-M3 positional analysis experiment.
    
    Args:
        cache_path: Path to H-M2 results cache
        output_dir: Directory for results output
        figures_dir: Directory for figures output
        
    Returns:
        Complete experiment results dict
    """
    # 1. Load data
    outputs = load_h_m2_cache(cache_path)
    
    # 2. Analyze all outputs
    analyses = analyze_all_outputs(outputs)
    
    # 3. Compute gate metrics
    gate_metrics = compute_gate_metrics(analyses)
    
    # 4. Generate figures
    plot_gate_comparison(gate_metrics, figures_dir / 'gate_comparison.png')
    
    # 5. Save results
    results = {
        'hypothesis_id': 'H-M3',
        'experiment_date': '2026-08-19',
        'gate_metrics': gate_metrics,
        'analysis_summary': {
            'total_analyzed': len(analyses),
            'with_confidence': sum(1 for a in analyses if a.has_confidence),
            'with_markers': sum(1 for a in analyses if a.hedging_markers),
        }
    }
    
    with open(output_dir / 'h-m3_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    with open(output_dir / 'gate_metrics.yaml', 'w') as f:
        yaml.dump(gate_metrics, f)
    
    return results

if __name__ == '__main__':
    results = run_h_m3_experiment(
        cache_path=Path('../h-m2/code/results/h-m2_results.json'),
        output_dir=Path('results'),
        figures_dir=Path('figures')
    )
    print(f"Gate Pass: {results['gate_metrics']['all_gates_pass']}")
```

---

## Tensor Shapes

**N/A** - This is a text analysis hypothesis with no tensor operations.

---

## Algorithm Details

### Position Comparison Algorithm

```
For each output:
  1. Find confidence position P_c using regex
  2. Find all marker positions [P_m1, P_m2, ...]
  3. Count markers where P_mi < P_c (before)
  4. Count markers where P_mi >= P_c (after)
  5. CoT order = P_c > 0.3 * len(output)

Gate 1: mean(cot_order) > 0.99
Gate 2: mean(all_markers_before) > 0.95
```

---

## Subtask Breakdown

### E2-S1: Confidence Extraction Implementation
- Implement `extract_confidence_position()`
- Handle edge cases (missing confidence, multiple matches)

### E3-S1: Analysis Dataclass Implementation
- Implement `PositionalAnalysis` dataclass
- Implement `analyze_output()` function

### E3-S2: Batch Analysis Implementation
- Implement `analyze_all_outputs()`
- Add progress logging for large datasets

---

*Logic design for H-M3 positional analysis experiment*
