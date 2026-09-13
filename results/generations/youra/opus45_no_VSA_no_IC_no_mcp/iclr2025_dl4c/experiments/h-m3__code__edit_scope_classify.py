THRESHOLD_LINES = 5

def classify_edit_scope(edit_record: dict, threshold_lines: int = THRESHOLD_LINES) -> str:
    """'targeted' if lines_changed <= threshold_lines else 'global'."""
    return "targeted" if edit_record.get("lines_changed", 0) <= threshold_lines else "global"

def label_edit_records(edit_records: list[dict], threshold_lines: int = THRESHOLD_LINES) -> list[dict]:
    """Adds 'edit_scope' key in place to each record; returns same list."""
    for record in edit_records:
        record["edit_scope"] = classify_edit_scope(record, threshold_lines)
    return edit_records
