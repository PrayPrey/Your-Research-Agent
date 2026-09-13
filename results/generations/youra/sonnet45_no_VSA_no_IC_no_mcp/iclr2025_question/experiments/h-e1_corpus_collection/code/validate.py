"""Corpus validation and stratification module."""

import numpy as np
from typing import Dict, List, Tuple


def validate_hypothesis_entry(entry: Dict) -> Tuple[bool, List[str]]:
    """Check completeness of overhead measurements."""
    errors = []

    required_fields = ["paper_id", "title", "venue", "year", "hypothesis_type", "overhead_measurements"]
    for field in required_fields:
        if field not in entry or not entry[field]:
            errors.append(f"Missing field: {field}")

    if "overhead_measurements" in entry:
        for scale in ["micro_pilot", "full_scale"]:
            if scale not in entry["overhead_measurements"]:
                errors.append(f"Missing {scale} measurements")
            else:
                measurement = entry["overhead_measurements"][scale]
                for field in ["sample_size", "time_seconds", "baseline_time", "overhead_percent"]:
                    if field not in measurement:
                        errors.append(f"Missing {scale}.{field}")

    return len(errors) == 0, errors


def compute_stratification(corpus: List[Dict]) -> Dict:
    """Stratify corpus by overhead bins."""
    bins = {"low": 0, "mid": 0, "high": 0}

    for entry in corpus:
        overhead = entry["overhead_measurements"]["full_scale"]["overhead_percent"]

        if overhead < 20:
            bins["low"] += 1
        elif overhead < 80:
            bins["mid"] += 1
        else:
            bins["high"] += 1

    bin_values = list(bins.values())
    mean_val = np.mean(bin_values) if bin_values else 0
    std_val = np.std(bin_values) if bin_values else 0
    cv = std_val / mean_val if mean_val > 0 else 0

    return {**bins, "cv": cv}


def spot_check_sample(corpus: List[Dict], sample_rate: float) -> List[Dict]:
    """Select random sample for manual verification."""
    sample_size = max(1, int(len(corpus) * sample_rate))
    indices = np.random.choice(len(corpus), size=sample_size, replace=False)
    return [corpus[i] for i in indices]


def generate_validation_report(corpus: List[Dict], config: Dict, output_path: str) -> Dict:
    """Generate validation report with gate decision."""
    valid_entries = []
    invalid_entries = []

    for entry in corpus:
        is_valid, errors = validate_hypothesis_entry(entry)
        if is_valid:
            valid_entries.append(entry)
        else:
            invalid_entries.append((entry, errors))

    valid_count = len(valid_entries)
    stratification = compute_stratification(valid_entries)

    # Gate decision
    pass_threshold = config["validation"]["pass_threshold"]
    fail_threshold = config["validation"]["fail_threshold"]
    cv_threshold = config["validation"]["stratification"]["cv_threshold"]

    if valid_count >= pass_threshold and stratification["cv"] < cv_threshold:
        decision = "PASS"
        next_step = "Proceed to H-M1 (correlation analysis)"
    elif valid_count >= fail_threshold:
        decision = "PARTIAL"
        next_step = "Extend collection or supplement with prospective"
    else:
        decision = "FAIL"
        next_step = "PIVOT to prospective validation"

    # Write report
    report = f"""# Validation Report: H-E1 Retrospective Corpus Collection

## Summary

**Total papers processed**: {len(corpus)}
**Valid hypotheses**: {valid_count}
**Invalid entries**: {len(invalid_entries)}

## Gate Decision

**Decision**: {decision}
**Next Step**: {next_step}

## Stratification

- Low overhead (<20%): {stratification['low']}
- Mid overhead (20-80%): {stratification['mid']}
- High overhead (>80%): {stratification['high']}
- Coefficient of Variation: {stratification['cv']:.3f}

## Quality Metrics

- Completeness: {valid_count}/{len(corpus)} ({100*valid_count/len(corpus) if corpus else 0:.1f}%)
- CV threshold: <{cv_threshold} (actual: {stratification['cv']:.3f})

## Invalid Entries

"""

    for entry, errors in invalid_entries[:5]:
        report += f"\n### {entry.get('title', 'Unknown')}\n"
        for error in errors:
            report += f"- {error}\n"

    with open(output_path, "w") as f:
        f.write(report)

    return {
        "valid_count": valid_count,
        "decision": decision,
        "next_step": next_step,
        "stratification": stratification
    }
