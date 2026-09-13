import csv
import json
import os


def append_cell_row(path: str, row: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_header = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def write_cell_jsonl(path: str, cell_result) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w") as f:
        for conf, pred, true in zip(cell_result.confidences, cell_result.pred_labels, cell_result.true_labels):
            record = {
                "confidence": float(conf),
                "pred_label": int(pred),
                "true_label": int(true),
                "correct": int(pred) == int(true),
            }
            f.write(json.dumps(record) + "\n")


def write_gate_result(path: str, passed_cells: int, failed_cells: list, clean_sanity: bool, gate_passed: bool = None, summary: dict = None) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    data = {
        "passed_cells": passed_cells,
        "failed_cells": failed_cells,
        "clean_sanity": clean_sanity,
        "gate_passed": gate_passed,
        "summary": summary or {},
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def write_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
