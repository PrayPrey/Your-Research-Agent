from metrics import issue_reduction


def evaluate_condition(loop_results: list[dict]) -> dict:
    if not loop_results:
        return {
            "security_issue_reduction": 0.0,
            "reliability_issue_reduction": 0.0,
            "mean_iterations": 0.0,
            "initial_security": 0.0,
            "final_security": 0.0,
            "initial_reliability": 0.0,
            "final_reliability": 0.0,
            "sample_count": 0
        }

    sec_reductions = []
    rel_reductions = []
    iterations_list = []
    initial_secs = []
    final_secs = []
    initial_rels = []
    final_rels = []

    for r in loop_results:
        init = r["initial"]
        fin = r["final"]

        sec_reductions.append(issue_reduction(init["security_count"], fin["security_count"]))
        rel_reductions.append(issue_reduction(init["reliability_count"], fin["reliability_count"]))
        iterations_list.append(r["iterations"])
        initial_secs.append(init["security_count"])
        final_secs.append(fin["security_count"])
        initial_rels.append(init["reliability_count"])
        final_rels.append(fin["reliability_count"])

    n = len(loop_results)
    return {
        "security_issue_reduction": sum(sec_reductions) / n,
        "reliability_issue_reduction": sum(rel_reductions) / n,
        "mean_iterations": sum(iterations_list) / n,
        "initial_security": sum(initial_secs) / n,
        "final_security": sum(final_secs) / n,
        "initial_reliability": sum(initial_rels) / n,
        "final_reliability": sum(final_rels) / n,
        "sample_count": n,
        "total_initial_security": sum(initial_secs),
        "total_final_security": sum(final_secs),
        "total_initial_reliability": sum(initial_rels),
        "total_final_reliability": sum(final_rels)
    }


def check_gate(agg_results: dict) -> bool:
    return (
        agg_results["final_security"] < agg_results["initial_security"]
        and agg_results["final_reliability"] < agg_results["initial_reliability"]
    )
