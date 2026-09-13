import json
import os
import itertools
from dataclasses import asdict
from typing import List, Dict
from tqdm import tqdm

from data_loader import Problem
from verifiers import VerifierResult
import verifiers.execution_monitor as execution_monitor
import verifiers.static_analysis as static_analysis
import verifiers.type_checker as type_checker
import verifiers.smt_solver as smt_solver


def run_all_verifiers(
    problems: List[Problem],
    completions: Dict[str, str],
    smt_enabled: bool = True,
    out_path: str = "results/verifier_results.jsonl",
) -> Dict[str, Dict[str, VerifierResult]]:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # Load already-processed IDs (checkpoint resume)
    processed = set()
    results: Dict[str, Dict[str, VerifierResult]] = {}
    if os.path.exists(out_path):
        with open(out_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                pid = obj["problem_id"]
                processed.add(pid)
                r = obj["results"]
                results[pid] = {
                    cat: VerifierResult(**r[cat]) for cat in r
                }
        print(f"✓ Resuming: {len(processed)} problems already processed")

    to_process = [p for p in problems if p.problem_id not in processed]
    print(f"Processing {len(to_process)} problems...")

    with open(out_path, "a") as f:
        for problem in tqdm(to_process, desc="Running verifiers"):
            pid = problem.problem_id
            completion = completions.get(pid, "")

            if not completion:
                print(f"  ⚠ Missing completion for {pid}, skipping")
                continue

            try:
                exec_r = execution_monitor.run(pid, completion, problem.test_code)
            except Exception as e:
                exec_r = VerifierResult(False, f"VERIFIER_ERROR: {e}", 0.0)

            try:
                static_r = static_analysis.run(completion)
            except Exception as e:
                static_r = VerifierResult(False, f"VERIFIER_ERROR: {e}", 0.0)

            try:
                type_r = type_checker.run(completion)
            except Exception as e:
                type_r = VerifierResult(False, f"VERIFIER_ERROR: {e}", 0.0)

            if smt_enabled:
                try:
                    smt_r = smt_solver.run(problem.prompt, completion)
                except Exception as e:
                    smt_r = VerifierResult(False, f"VERIFIER_ERROR: {e}", 0.0)
            else:
                smt_r = VerifierResult(False, "DISABLED", 0.0)

            row = {
                "problem_id": pid,
                "source": problem.source,
                "results": {
                    "execution": asdict(exec_r),
                    "static_analysis": asdict(static_r),
                    "type_checking": asdict(type_r),
                    "smt_solving": asdict(smt_r),
                }
            }
            f.write(json.dumps(row) + "\n")
            f.flush()
            results[pid] = {
                "execution": exec_r,
                "static_analysis": static_r,
                "type_checking": type_r,
                "smt_solving": smt_r,
            }

    return results


def compute_stats(results: Dict[str, Dict[str, VerifierResult]], problems: List[Problem]) -> dict:
    cats = ["execution", "static_analysis", "type_checking", "smt_solving"]
    n = max(len(results), 1)

    # Build activated sets
    act = {cat: {pid for pid, r in results.items() if r[cat].activated} for cat in cats}
    activation_rates = {cat: len(act[cat]) / n for cat in cats}

    # Pairwise overlap
    pairwise_overlap = {}
    for a, b in itertools.combinations(cats, 2):
        key = f"{a}_{b}"
        pairwise_overlap[key] = len(act[a] & act[b]) / n

    # Per-source breakdown
    source_map: Dict[str, str] = {p.problem_id: p.source for p in problems}
    he_ids = {pid for pid, src in source_map.items() if src == "humaneval" and pid in results}
    mb_ids = {pid for pid, src in source_map.items() if src == "mbpp" and pid in results}

    def _rates(ids):
        n_src = max(len(ids), 1)
        return {cat: len(act[cat] & ids) / n_src for cat in cats}

    per_source = {
        "humaneval": _rates(he_ids),
        "mbpp": _rates(mb_ids),
    }

    return {
        "activation_rates": activation_rates,
        "pairwise_overlap": pairwise_overlap,
        "per_source": per_source,
        "n_total": len(results),
        "n_per_source": {"humaneval": len(he_ids), "mbpp": len(mb_ids)},
    }


def gate_check(stats: dict) -> bool:
    cats = ["execution", "static_analysis", "type_checking", "smt_solving"]
    rates = stats["activation_rates"]
    print("\n=== GATE CHECK (≥10% activation required) ===")
    all_pass = True
    for cat in cats:
        rate = rates.get(cat, 0.0)
        status = "PASS" if rate >= 0.10 else "FAIL"
        if rate < 0.10:
            all_pass = False
        print(f"  {cat}: {rate:.1%}  [{status}]")
    print(f"\nOverall: {'PASS ✅' if all_pass else 'FAIL ❌'}")
    return all_pass
