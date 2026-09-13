"""Data loading for H-M3. Bridges H-M1 results and adds load_exp_a_results."""
import json
import sys
from pathlib import Path

H1_CODE_DIR = Path(__file__).parent.parent.parent / "h-m1" / "code"
H1_RESULTS_DIR = H1_CODE_DIR / "results"

if str(H1_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(H1_CODE_DIR))


def load_exp_a_results(results_path: str = None) -> list[dict]:
    """Load Exp A per-triple static oracle results (from h-m3 own Exp A run).
    Falls back to H-M1 isolation_results.jsonl if h-m3 Exp A not yet computed.
    """
    # Prefer h-m3's own Exp A results
    hm3_exp_a = Path(__file__).parent.parent / "results" / "experiment_a_results.jsonl"
    path = results_path or (str(hm3_exp_a) if hm3_exp_a.exists() else str(H1_RESULTS_DIR / "isolation_results.jsonl"))

    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            # h-m3 Exp A has static_failure_rate directly; h-m1 has contract_failure_rate
            records.append({
                "task_id": d["task_id"],
                "model": d["model"],
                "program_idx": d["program_idx"],
                "static_failure_rate": d.get("static_failure_rate", d.get("contract_failure_rate", 0.0)),
                "task_type": d.get("task_type", "unknown"),
            })
    return records


def _get_h1_data_loader():
    import importlib.util
    spec = importlib.util.spec_from_file_location("h1_data_loader", H1_CODE_DIR / "data_loader.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_contracteval_tasks(jsonl_path: str = None) -> dict:
    """Returns {task_id: task_dict} using H-M1 data_loader."""
    return _get_h1_data_loader().load_contracteval(jsonl_path)


def load_llm_corpus(h1_samples_dir: str = None) -> dict:
    """Returns {model: {task_id: [code_str]}} using H-M1 data_loader."""
    return _get_h1_data_loader().load_h1_corpus(h1_samples_dir)
