"""Task M1-5: Aggregate H-M1 results and verify signal void mechanism."""
import json
from pathlib import Path


def load_all_results(results_dir: str) -> dict:
    """Load all three analysis JSONs from results_dir."""
    base = Path(results_dir)
    out = {}

    lcb_path = base / "sft_lcb_hard.json"
    if lcb_path.exists():
        with open(lcb_path) as f:
            out["lcb"] = json.load(f)
    else:
        out["lcb"] = None

    loss_path = base / "apps_difficulty_loss.json"
    if loss_path.exists():
        with open(loss_path) as f:
            out["loss"] = json.load(f)
    else:
        out["loss"] = None

    cov_path = base / "apps_hard_coverage.json"
    if cov_path.exists():
        with open(cov_path) as f:
            out["coverage"] = json.load(f)
    else:
        out["coverage"] = None

    return out


def verify_signal_void_mechanism(results: dict, gate_threshold: float = 0.60, coverage_threshold: float = 0.30) -> tuple:
    """Primary: pass1 < 0.60. Secondary: competition_loss > introductory_loss.
    Returns (success, indicators_dict)."""
    indicators = {
        "sft_lcb_hard_pass1": None,
        "signal_void_primary": False,
        "apps_difficulty_loss": {},
        "loss_gradient_secondary": False,
        "apps_competition_coverage": None,
        "coverage_void_secondary": False,
        "gate_satisfied": False,
    }

    # Primary gate
    lcb = results.get("lcb")
    if lcb is not None:
        pass1 = lcb.get("pass@1", lcb.get("pass1", None))
        if pass1 is None and "gate" in lcb:
            pass1 = lcb["gate"].get("pass1")
        indicators["sft_lcb_hard_pass1"] = pass1
        if pass1 is not None:
            indicators["signal_void_primary"] = pass1 < gate_threshold

    # Secondary: loss gradient
    loss = results.get("loss")
    if loss is not None:
        indicators["apps_difficulty_loss"] = {
            "introductory": loss.get("introductory", {}).get("mean"),
            "interview": loss.get("interview", {}).get("mean"),
            "competition": loss.get("competition", {}).get("mean"),
            "counts": {
                "introductory": loss.get("introductory", {}).get("count", 0),
                "interview": loss.get("interview", {}).get("count", 0),
                "competition": loss.get("competition", {}).get("count", 0),
            },
        }
        intro = loss.get("introductory", {}).get("mean")
        comp = loss.get("competition", {}).get("mean")
        if intro is not None and comp is not None:
            indicators["loss_gradient_secondary"] = comp > intro

    # Secondary: coverage
    cov = results.get("coverage")
    if cov is not None:
        coverage_pct = cov.get("coverage_pct", 100)
        indicators["apps_competition_coverage"] = coverage_pct / 100.0
        indicators["coverage_void_secondary"] = (coverage_pct / 100.0) < coverage_threshold

    indicators["gate_satisfied"] = indicators["signal_void_primary"]
    success = indicators["gate_satisfied"]
    return success, indicators


def write_signal_void_analysis(indicators: dict, output_path: str = "results/h-m1/signal_void_analysis.json") -> None:
    """Write combined gate decision + all indicators to JSON."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(indicators, f, indent=2)
    print(f"Signal void analysis written to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--results_dir", default="results/h-m1")
    parser.add_argument("--output", default="results/h-m1/signal_void_analysis.json")
    args = parser.parse_args()

    results = load_all_results(args.results_dir)
    success, indicators = verify_signal_void_mechanism(results)

    print("\n=== H-M1 Gate Evaluation ===")
    print(f"SFT LCB-Hard pass@1: {indicators['sft_lcb_hard_pass1']}")
    print(f"Signal void (primary gate): {indicators['signal_void_primary']}")
    print(f"Loss gradient (secondary): {indicators['loss_gradient_secondary']}")
    print(f"Coverage void (secondary): {indicators['coverage_void_secondary']}")
    print(f"\nGate SATISFIED: {indicators['gate_satisfied']}")
    print(f"Overall: {'PASS' if success else 'FAIL'}")

    write_signal_void_analysis(indicators, args.output)
