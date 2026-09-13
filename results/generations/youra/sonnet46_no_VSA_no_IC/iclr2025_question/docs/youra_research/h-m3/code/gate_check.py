from typing import Dict


def evaluate_gates(
    auroc_table: Dict,
    p1_threshold: float = 0.02,
    p2_threshold: float = 0.02,
) -> Dict:
    auroc = auroc_table["auroc"]
    diff  = auroc_table["diff"]
    MODELS  = ["llama2", "mistral"]
    P1_DS   = ["trivia_qa", "nq"]
    P2_DS   = ["truthful_qa"]
    ALL_DS  = ["trivia_qa", "nq", "truthful_qa"]

    # P1: AUROC(min) - AUROC(mean) >= threshold AND ci_lower > 0, trivia_qa AND nq, both models
    p1_evidence = {}
    p1_checks = []
    for model in MODELS:
        p1_evidence[model] = {}
        for ds in P1_DS:
            d = diff.get((model, ds))
            if d is None:
                ok = False
                p1_evidence[model][ds] = {"diff": None, "ci_lower": None, "met": False, "reason": "missing"}
            else:
                ok = d["diff"] >= p1_threshold and d["ci_lower"] > 0
                p1_evidence[model][ds] = {**d, "met": ok}
            p1_checks.append(ok)
    p1_met = all(p1_checks)

    # P2: AUROC(mean) - AUROC(min) >= threshold AND ci_lower > 0, truthful_qa, both models
    p2_evidence = {}
    p2_checks = []
    for model in MODELS:
        p2_evidence[model] = {}
        ds = "truthful_qa"
        d_fwd = diff.get((model, ds))
        if d_fwd is None:
            ok = False
            p2_evidence[model][ds] = {"diff": None, "ci_lower": None, "met": False, "reason": "missing"}
        else:
            diff_mean_min = -d_fwd["diff"]
            ci_lo_mean_min = -d_fwd["ci_upper"]
            ok = diff_mean_min >= p2_threshold and ci_lo_mean_min > 0
            p2_evidence[model][ds] = {
                "diff": diff_mean_min,
                "ci_lower": ci_lo_mean_min,
                "ci_upper": -d_fwd["ci_lower"],
                "met": ok,
            }
        p2_checks.append(ok)
    p2_met = all(p2_checks)

    # P3: AUROC(raw_sum) < AUROC(min) AND AUROC(raw_sum) < AUROC(mean), all datasets, directional
    p3_evidence = {}
    p3_checks = []
    for model in MODELS:
        for ds in ALL_DS:
            a_sum  = auroc.get((model, ds, "raw_sum"), {}).get("auroc")
            a_min  = auroc.get((model, ds, "min"),     {}).get("auroc")
            a_mean = auroc.get((model, ds, "mean"),    {}).get("auroc")
            if a_sum is None or a_min is None or a_mean is None:
                ok = False
                p3_evidence[(model, ds)] = {"raw_sum_vs_min": None, "raw_sum_vs_mean": None, "met": False, "reason": "missing"}
            else:
                ok = a_sum < a_min and a_sum < a_mean
                p3_evidence[(model, ds)] = {
                    "raw_sum_vs_min": a_sum - a_min,
                    "raw_sum_vs_mean": a_sum - a_mean,
                    "met": ok,
                }
            p3_checks.append(ok)
    p3_met = all(p3_checks)

    n = sum([p1_met, p2_met, p3_met])
    gate = "PASS" if n == 3 else ("PARTIAL_PASS" if n >= 1 else "FAIL")

    return {
        "p1_met": p1_met, "p1_evidence": p1_evidence,
        "p2_met": p2_met, "p2_evidence": p2_evidence,
        "p3_met": p3_met, "p3_evidence": p3_evidence,
        "gate": gate, "n_gates_met": n,
    }
