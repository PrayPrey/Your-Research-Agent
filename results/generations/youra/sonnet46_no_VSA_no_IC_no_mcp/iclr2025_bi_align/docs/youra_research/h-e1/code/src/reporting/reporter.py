import json
from pathlib import Path


def print_report(results: list) -> None:
    print("\n" + "=" * 60)
    print("H-E1 VERIFICATION REPORT")
    print("=" * 60)
    overall = all(r["passed"] for r in results)
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"\n[{status}] {r['dataset']}")
        print(f"  KL levels : {r['n_kl_levels']}")
        print(f"  RM var    : {r['rm_variation']:.4f}")
        print(f"  Gold var  : {r['gold_variation']:.4f}")
        print(f"  Gate      : {'satisfied' if r['gate_satisfied'] else 'NOT satisfied'}")
        print(f"  Reason    : {r['reason']}")
    print("\n" + "-" * 60)
    print(f"OVERALL GATE: {'PASS' if overall else 'FAIL'}")
    print("=" * 60 + "\n")


def save_results(results: list, out_path: str) -> None:
    overall = all(r["passed"] for r in results)
    payload = {
        "hypothesis_id": "h-e1",
        "gate_type": "MUST_WORK",
        "overall_passed": overall,
        "datasets": results,
    }
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(payload, f, indent=2)
