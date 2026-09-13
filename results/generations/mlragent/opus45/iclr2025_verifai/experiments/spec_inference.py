"""Specification Inference Module for SpecBridge.

This module implements the specification inference component that:
1. Translates natural language requirements to formal specifications
2. Generates multiple specification candidates for ensemble analysis
3. Detects ambiguities through disagreement detection
"""

import json
import re
from config import NUM_SPEC_CANDIDATES, TEMPERATURE_SAMPLING, ENSEMBLE_THRESHOLD
from model_wrapper import get_llm

SPEC_INFERENCE_PROMPT = """You are a formal specification expert. Given a natural language description of a function,
generate a formal specification with:
1. Precondition: Conditions that must be true before the function executes
2. Postcondition: Conditions that must be true after the function executes
3. Invariants (if applicable): Loop invariants for iterative algorithms

Respond ONLY in JSON format without any markdown or explanation:
{{"precondition": "<Python boolean expression>", "postcondition": "<Python boolean expression using 'result'>", "invariants": []}}

Natural Language Description: {description}

JSON specification:"""

def generate_specification(description: str, temperature: float = 0.0) -> dict:
    """Generate a formal specification from natural language description."""
    try:
        llm = get_llm()
        prompt = SPEC_INFERENCE_PROMPT.format(description=description)
        response = llm.generate(prompt, max_new_tokens=256, temperature=temperature)

        # Extract JSON from response
        # Try to find JSON object
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            try:
                spec = json.loads(json_match.group())
                # Ensure required fields
                spec.setdefault("precondition", "True")
                spec.setdefault("postcondition", "True")
                spec.setdefault("invariants", [])
                return spec
            except json.JSONDecodeError:
                pass

        return {"precondition": "True", "postcondition": "True", "invariants": []}
    except Exception as e:
        print(f"Error generating specification: {e}")
        return {"precondition": "True", "postcondition": "True", "invariants": []}

def generate_specification_ensemble(description: str, k: int = NUM_SPEC_CANDIDATES) -> list:
    """Generate multiple diverse specification candidates."""
    candidates = []
    # First one with low temperature
    candidates.append(generate_specification(description, temperature=0.0))
    # Rest with higher temperature for diversity
    for _ in range(k - 1):
        candidates.append(generate_specification(description, temperature=TEMPERATURE_SAMPLING))
    return candidates

def compute_disagreement_score(candidates: list) -> float:
    """Compute disagreement score between specification candidates.

    Higher score indicates more disagreement (potential ambiguity).
    """
    if len(candidates) <= 1:
        return 0.0

    # Compare specifications based on string similarity
    total_pairs = 0
    agreement_count = 0

    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            total_pairs += 1
            # Simple comparison: check if pre/post conditions are similar
            pre_i = candidates[i].get("precondition", "").lower().strip()
            pre_j = candidates[j].get("precondition", "").lower().strip()
            post_i = candidates[i].get("postcondition", "").lower().strip()
            post_j = candidates[j].get("postcondition", "").lower().strip()

            if pre_i == pre_j and post_i == post_j:
                agreement_count += 1

    if total_pairs == 0:
        return 0.0

    agreement_rate = agreement_count / total_pairs
    return 1.0 - agreement_rate

def is_ambiguous(candidates: list, threshold: float = ENSEMBLE_THRESHOLD) -> bool:
    """Detect if the specification is ambiguous based on ensemble disagreement."""
    score = compute_disagreement_score(candidates)
    return score > threshold

def select_best_specification(candidates: list) -> dict:
    """Select the best specification from candidates.

    For simplicity, we use the first (greedy) candidate.
    In practice, this could use voting or other selection methods.
    """
    if not candidates:
        return {"precondition": "True", "postcondition": "True", "invariants": []}
    return candidates[0]
