import numpy as np
from dataclasses import dataclass


@dataclass
class GateResult:
    log_slope: float
    pct90: float
    gate_pass: bool
    decision: str
    mean_errors: dict


def compute_scaling_metrics(
    errors_by_N: dict,
    slope_threshold: float = 0.5,
    pct90_threshold: float = 0.3,
) -> GateResult:
    """Compute gate metrics from raw error dict."""
    Ns = sorted(errors_by_N.keys())
    mean_errors = {N: float(np.mean(errors_by_N[N])) for N in Ns}

    log_Ns = np.log(Ns)
    log_Es = np.log([max(mean_errors[N], 1e-9) for N in Ns])
    log_slope = float(np.polyfit(log_Ns, log_Es, 1)[0])

    max_N = max(Ns)
    pct90 = float(np.percentile(errors_by_N[max_N], 90))

    gate_pass = (log_slope <= slope_threshold) and (pct90 <= pct90_threshold)
    return GateResult(
        log_slope=log_slope,
        pct90=pct90,
        gate_pass=gate_pass,
        decision="PASS" if gate_pass else "STOP",
        mean_errors=mean_errors,
    )


def compute_log_log_slope(errors_by_N: dict) -> float:
    Ns = sorted(errors_by_N.keys())
    mean_errors = [float(np.mean(errors_by_N[N])) for N in Ns]
    log_Ns = np.log(Ns)
    log_Es = np.log([max(e, 1e-9) for e in mean_errors])
    return float(np.polyfit(log_Ns, log_Es, 1)[0])


def compute_pct90_at_8k(errors_by_N: dict) -> float:
    max_N = max(errors_by_N.keys())
    return float(np.percentile(errors_by_N[max_N], 90))


def compute_mean_errors(errors_by_N: dict) -> dict:
    return {N: float(np.mean(v)) for N, v in errors_by_N.items()}
