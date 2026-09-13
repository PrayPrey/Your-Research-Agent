"""Data loading for H-M1 oracle isolation experiment."""
import json
import signal
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


CONTRACTEVAL_PATH = Path(__file__).parent.parent.parent / "_archive" / "20260803T121822_routing_recovery" / ".data_cache" / "datasets" / "ContractEval" / "data" / "ContractEval" / "ContractEval.jsonl"
H1_SAMPLES_DIR = Path(__file__).parent.parent.parent / "h-e1" / "code" / "data" / "samples"


def _timeout_handler(signum, frame):
    raise TimeoutError("timeout")


def load_contracteval(jsonl_path: Optional[str] = None) -> dict:
    """Load ContractEval from multi-object JSONL file. Returns {task_id: task_dict}."""
    path = jsonl_path or str(CONTRACTEVAL_PATH)
    tasks = []
    with open(path) as f:
        content = f.read()
    decoder = json.JSONDecoder()
    pos = 0
    content = content.strip()
    while pos < len(content):
        while pos < len(content) and content[pos] in ' \t\n\r':
            pos += 1
        if pos >= len(content):
            break
        obj, end = decoder.raw_decode(content, pos)
        tasks.append(obj)
        pos = end
    return {t["task_id"]: t for t in tasks}


def load_evalplus_data(task_ids: list) -> dict:
    """Load EvalPlus data for given task_ids.
    Returns {task_id: {inputs: [...], gt_source: str, entry_point: str}}.
    gt_source = prompt + canonical_solution (complete function definition).
    """
    from evalplus.data import get_human_eval_plus, get_mbpp_plus
    he = get_human_eval_plus()
    mb = get_mbpp_plus()
    all_evalplus = {**he, **mb}

    result = {}
    for tid in task_ids:
        if tid not in all_evalplus:
            continue
        ep = all_evalplus[tid]
        inputs = list(ep.get("base_input", [])) + list(ep.get("plus_input", []))
        gt_source = ep.get("prompt", "") + ep.get("canonical_solution", "")
        result[tid] = {
            "inputs": inputs,
            "gt_source": gt_source,
            "entry_point": ep.get("entry_point", ""),
        }
    return result


def load_evalplus_inputs(task_ids: list) -> dict:
    """Load EvalPlus base_input + plus_input. Returns {task_id: list_of_input_lists}."""
    data = load_evalplus_data(task_ids)
    return {tid: d["inputs"] for tid, d in data.items()}


def load_h1_corpus(h1_samples_dir: Optional[str] = None) -> dict:
    """Load H-E1 test-passing programs per (model, task_id).
    Returns {model: {task_id: [code_str, ...]}}.
    """
    samples_dir = Path(h1_samples_dir or H1_SAMPLES_DIR)
    corpus = {}
    for jsonl_file in sorted(samples_dir.glob("*.jsonl")):
        model = jsonl_file.stem
        model_corpus = {}
        with open(jsonl_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                tid = d["task_id"]
                model_corpus.setdefault(tid, []).append(d["solution"])
        corpus[model] = model_corpus
    return corpus


def verify_task_overlap(ce_ids: set, ep_ids: set, threshold: float = 0.90) -> tuple:
    """Returns (matched_ids, unmatched_ids). Raises if overlap < threshold."""
    matched = ce_ids & ep_ids
    unmatched = ce_ids - ep_ids
    overlap_rate = len(matched) / max(len(ce_ids), 1)
    if overlap_rate < threshold:
        raise ValueError(
            f"Task ID overlap {overlap_rate:.1%} < {threshold:.0%} threshold. "
            f"Unmatched: {len(unmatched)}"
        )
    return matched, unmatched
