"""Positional analysis module for H-M3."""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
from position_extractor import extract_confidence_position, extract_hedging_positions


@dataclass
class PositionalAnalysis:
    """Result container for single output analysis."""
    output_id: str
    has_confidence: bool
    confidence_position: int
    confidence_value: int
    hedging_markers: List[Tuple[str, int]]
    markers_before_confidence: int
    markers_after_confidence: int
    cot_then_confidence_order: bool
    output_length: int


def analyze_output(output_id: str, output: str, cot_threshold: float = 0.3) -> PositionalAnalysis:
    """Analyze single output for marker-confidence positioning."""
    conf_pos, conf_val = extract_confidence_position(output)
    markers = extract_hedging_positions(output)

    has_conf = conf_pos >= 0
    if has_conf:
        before = [m for m in markers if m[1] < conf_pos]
        after = [m for m in markers if m[1] >= conf_pos]
    else:
        before, after = [], []

    cot_order = has_conf and conf_pos > len(output) * cot_threshold

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


def analyze_all_outputs(outputs: List[Dict[str, Any]], cot_threshold: float = 0.3) -> List[PositionalAnalysis]:
    """Analyze all outputs in batch."""
    results = []
    for i, o in enumerate(outputs):
        output_id = o.get('output_id', o.get('id', o.get('question', str(i))))
        text = o.get('raw_output', o.get('output_text', o.get('response', o.get('output', ''))))
        results.append(analyze_output(output_id, text, cot_threshold))
    return results
