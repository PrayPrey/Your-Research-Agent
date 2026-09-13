import difflib
from typing import Optional
from scipy import stats

def measure_edit_scope(old_code: str, new_code: str) -> dict:
    """Measure edit scope using difflib unified_diff."""
    old_lines = old_code.splitlines()
    new_lines = new_code.splitlines()

    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))

    lines_changed = 0
    for line in diff:
        if line.startswith('+') or line.startswith('-'):
            if not line.startswith('+++') and not line.startswith('---'):
                lines_changed += 1

    total_lines = max(len(old_lines), 1)
    change_ratio = lines_changed / total_lines

    return {
        "lines_changed": lines_changed,
        "total_lines": total_lines,
        "change_ratio": change_ratio,
        "is_global_rewrite": change_ratio > 0.5
    }

def aggregate_edit_metrics(edit_records: list[dict]) -> dict:
    """Aggregate edit metrics by feedback_type, compute t-test."""
    detailed = [e for e in edit_records if e.get("feedback_type") == "detailed"]
    binary = [e for e in edit_records if e.get("feedback_type") == "binary"]

    detailed_lines = [e["lines_changed"] for e in detailed] if detailed else [0]
    binary_lines = [e["lines_changed"] for e in binary] if binary else [0]

    d_avg = sum(detailed_lines) / max(len(detailed_lines), 1)
    b_avg = sum(binary_lines) / max(len(binary_lines), 1)

    d_rewrite = sum(1 for e in detailed if e.get("is_global_rewrite")) / max(len(detailed), 1)
    b_rewrite = sum(1 for e in binary if e.get("is_global_rewrite")) / max(len(binary), 1)

    if len(detailed_lines) > 1 and len(binary_lines) > 1:
        _, p_value = stats.ttest_ind(detailed_lines, binary_lines)
    else:
        p_value = 1.0

    edit_scope_ratio = d_avg / max(b_avg, 0.001)

    return {
        "detailed_avg_lines_changed": d_avg,
        "binary_avg_lines_changed": b_avg,
        "detailed_global_rewrite_rate": d_rewrite,
        "binary_global_rewrite_rate": b_rewrite,
        "edit_scope_ratio": edit_scope_ratio,
        "p_value": p_value,
        "detailed_n": len(detailed),
        "binary_n": len(binary)
    }
