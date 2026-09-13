"""Reporting for H-M3."""
import json
from pathlib import Path

import numpy as np


class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        return super().default(obj)


def print_report(results: dict) -> None:
    gate = "PASS ✓" if results.get("gate_pass") else "FAIL ✗"
    print()
    print("=" * 60)
    print(f"H-M3 GATE RESULT: {gate}")
    print("=" * 60)
    print(f"  slope (β):   {results['slope']:.6f}  (threshold > 0)")
    print(f"  p-value:     {results['p_value']:.2e}  (threshold < 0.05)")
    print(f"  R²:          {results['r_squared']:.6f}  (threshold > 0.5)")
    print(f"  t-stat:      {results['t_stat']:.4f}")
    print(f"  n:           {results['n']}")
    ci_p = results.get("ci_parametric", (None, None))
    ci_b = results.get("ci_bootstrap", [None, None])
    print(f"  CI 95% (parametric):  [{ci_p[0]:.4f}, {ci_p[1]:.4f}]")
    print(f"  CI 95% (bootstrap):   [{ci_b[0]:.4f}, {ci_b[1]:.4f}]")
    print()
    print(f"Gate reason: {results.get('gate_reason', 'N/A')}")
    print("=" * 60)


def save_results(results: dict, out_path: str) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    # Exclude large arrays from JSON; keep scalar metrics + CI
    serializable = {k: v for k, v in results.items() if k != "boot_slopes"}
    with open(out_path, "w") as f:
        json.dump(serializable, f, indent=2, cls=_NumpyEncoder)
    print(f"✓ Results saved: {out_path}")
