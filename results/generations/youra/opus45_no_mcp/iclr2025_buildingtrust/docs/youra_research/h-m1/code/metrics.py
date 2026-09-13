"""A-6: Metrics Computation - reasoning_presence_rate, mean_step_count, gate check"""


def compute_metrics(results: list[dict]) -> dict:
    """Compute reasoning presence rate and mean step count from results."""
    if not results:
        return {"reasoning_presence_rate": 0.0, "mean_step_count": 0.0, "n": 0}

    n = len(results)
    reasoning_presence_rate = sum(1 for r in results if r["has_reasoning"]) / n
    mean_step_count = sum(r["step_count"] for r in results) / n

    return {
        "reasoning_presence_rate": reasoning_presence_rate,
        "mean_step_count": mean_step_count,
        "n": n,
    }


def check_gate(cot_metrics: dict, baseline_metrics: dict) -> dict:
    """Check 3 PoC gates: cot_rate>0.90, cot_rate-baseline_rate>0.50, cot_mean_step_count>2.0."""
    cot_rate = cot_metrics["reasoning_presence_rate"]
    baseline_rate = baseline_metrics["reasoning_presence_rate"]
    cot_steps = cot_metrics["mean_step_count"]

    gate_1 = cot_rate > 0.90
    gate_2 = (cot_rate - baseline_rate) > 0.50
    gate_3 = cot_steps > 2.0

    return {
        "cot_reasoning_rate": cot_rate,
        "baseline_reasoning_rate": baseline_rate,
        "rate_difference": cot_rate - baseline_rate,
        "mean_step_count": cot_steps,
        "gate_1_rate_pass": gate_1,
        "gate_2_delta_pass": gate_2,
        "gate_3_steps_pass": gate_3,
        "all_pass": all([gate_1, gate_2, gate_3]),
    }


if __name__ == "__main__":
    cot = {"reasoning_presence_rate": 0.95, "mean_step_count": 3.5, "n": 100}
    baseline = {"reasoning_presence_rate": 0.20, "mean_step_count": 0.5, "n": 100}
    gate = check_gate(cot, baseline)
    print(f"Gate results: {gate}")
