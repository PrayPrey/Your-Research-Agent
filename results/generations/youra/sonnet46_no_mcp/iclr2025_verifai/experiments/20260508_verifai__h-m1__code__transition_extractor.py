import json
from typing import Dict, List


class TransitionExtractor:

    def extract(
        self,
        baseline_pool: Dict[str, List[dict]],
        syncode_pool: Dict[str, List[dict]],
    ) -> List[dict]:
        transitions = []
        for task_id in baseline_pool:
            if task_id not in syncode_pool:
                continue
            b_records = {r.get("sample_idx", i): r for i, r in enumerate(baseline_pool[task_id])}
            s_records = {r.get("sample_idx", i): r for i, r in enumerate(syncode_pool[task_id])}

            for sample_idx in b_records:
                if sample_idx not in s_records:
                    continue
                b_rec = b_records[sample_idx]
                s_rec = s_records[sample_idx]
                if not b_rec.get("ast_valid", True) and s_rec.get("ast_valid", False):
                    transitions.append({
                        "task_id": task_id,
                        "problem_idx": b_rec.get("problem_idx"),
                        "sample_idx": sample_idx,
                    })
        return transitions

    def compute_coverage_by_problem(
        self,
        transitions: List[dict],
        n_problems: int = 164,
    ) -> List[dict]:
        counts: Dict[str, int] = {}
        task_to_idx: Dict[str, int] = {}
        for t in transitions:
            tid = t["task_id"]
            counts[tid] = counts.get(tid, 0) + 1
            if t.get("problem_idx") is not None:
                task_to_idx[tid] = t["problem_idx"]

        coverage = [
            {
                "task_id": tid,
                "problem_idx": task_to_idx.get(tid),
                "transitions_count": cnt,
            }
            for tid, cnt in counts.items()
        ]
        return coverage

    def save_results(
        self,
        transitions: List[dict],
        coverage: List[dict],
        output_path: str,
    ) -> dict:
        total = len(transitions)
        # Total possible: each problem × 20 samples = n_problems * 20
        # Use coverage length for rate denominator if known
        n_total = 164 * 20
        result = {
            "transitions": transitions,
            "transition_count": total,
            "transition_rate": total / n_total if n_total > 0 else 0.0,
            "coverage_by_problem": coverage,
        }
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        return result
