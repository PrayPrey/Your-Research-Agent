import numpy as np
from typing import NamedTuple
from evaluation.logit_extractor import CellResult, extract_cell
from evaluation.ece import compute_ece


class ValidationResult(NamedTuple):
    passed: bool
    indicators: dict


def verify_logit_extraction(cell_result: CellResult, ece_15: float, min_examples: int = 50, min_confidence_uniform: float = 0.30) -> ValidationResult:
    c = cell_result.confidences
    indicators = {
        "coverage_met":     len(c) >= min_examples,
        "non_degenerate":   float((c < 0.999).mean()) > 0.90,
        "non_uniform":      float(c.mean()) > min_confidence_uniform,
        "ece_plausible":    0.0 <= ece_15 <= 0.5,
        "probs_sum_to_one": abs(float(cell_result.prob_sums.mean()) - 1.0) < 1e-3,
    }
    return ValidationResult(passed=all(indicators.values()), indicators=indicators)


def prevalidate_cell(model, tokenizer, dataset, task: str, model_id: str, n: int = 10, min_confidence_uniform: float = 0.30) -> ValidationResult:
    subset = dataset.select(range(min(n, len(dataset))))
    result = extract_cell(model, tokenizer, subset, task, model_id)
    indicators = {
        "coverage_met":     len(result.confidences) >= min(n, len(dataset)),
        "non_degenerate":   float((result.confidences < 0.999).mean()) > 0.90,
        "non_uniform":      float(result.confidences.mean()) > min_confidence_uniform,
        "ece_plausible":    True,
        "probs_sum_to_one": abs(float(result.prob_sums.mean()) - 1.0) < 1e-3,
    }
    return ValidationResult(passed=all(indicators.values()), indicators=indicators)


def check_clean_sanity(ece_clean_by_model: dict, clean_ece_min=0.05, clean_ece_max=0.15, min_models=1):
    details = {}
    passing_models = 0
    for model_id, task_eces in ece_clean_by_model.items():
        model_pass = any(clean_ece_min <= v <= clean_ece_max for v in task_eces.values() if v is not None)
        details[model_id] = {"task_eces": task_eces, "passes_range": model_pass}
        if model_pass:
            passing_models += 1
    passed = passing_models >= min_models
    return passed, details
