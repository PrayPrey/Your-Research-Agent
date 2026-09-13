import json
import logging
import sys
from pathlib import Path

import numpy as np

# Ensure code dir is importable when run from project root
sys.path.insert(0, str(Path(__file__).parent))

from config import CFG
from data_loader import load_h_e1_similarities, load_h_e2_pass_at_1, load_h_c1_pass_at_1, validate_inputs
from analysis import run_all_cells, evaluate_gate, cell_id
from visualize import save_all_figures

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

RESULTS_DIR = CFG.paths.results_dir
NULL_DIR = CFG.paths.null_dist_dir


def save_results(cell_results, gate):
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    Path(NULL_DIR).mkdir(parents=True, exist_ok=True)

    # correlation_results.json
    corr = []
    for c in cell_results:
        entry = {
            "encoder": c.encoder,
            "benchmark": c.benchmark,
            "model_size": c.model_size,
            "status": c.status,
        }
        if c.result:
            r = c.result
            entry.update({
                "rho": float(r.rho) if not np.isnan(r.rho) else None,
                "pvalue": float(r.pvalue) if not np.isnan(r.pvalue) else None,
                "significant": bool(r.significant),
                "ci_lo": float(r.ci_lo) if not np.isnan(r.ci_lo) else None,
                "ci_hi": float(r.ci_hi) if not np.isnan(r.ci_hi) else None,
                "tau": float(r.tau) if not np.isnan(r.tau) else None,
                "tau_p": float(r.tau_p) if not np.isnan(r.tau_p) else None,
                "can_test": r.can_test,
                "used_kendall": r.used_kendall,
            })
        corr.append(entry)

    with open(f"{RESULTS_DIR}/correlation_results.json", "w") as f:
        json.dump(corr, f, indent=2)

    # rank_comparison_table.csv
    with open(f"{RESULTS_DIR}/rank_comparison_table.csv", "w") as f:
        f.write("encoder,benchmark,model_size,status,rho,pvalue,significant,ci_lo,ci_hi\n")
        for e in corr:
            f.write(f"{e['encoder']},{e['benchmark']},{e['model_size']},{e['status']},"
                    f"{e.get('rho','')},{e.get('pvalue','')},{e.get('significant','')},{e.get('ci_lo','')},{e.get('ci_hi','')}\n")

    # gate_evaluation.json
    gate_dict = {
        "gate_status": gate.gate_status,
        "satisfied_cells": gate.satisfied_cells,
        "concordant_benchmarks": gate.concordant_benchmarks,
        "reason": gate.reason,
    }
    with open(f"{RESULTS_DIR}/gate_evaluation.json", "w") as f:
        json.dump(gate_dict, f, indent=2)

    # null distributions
    for c in cell_results:
        if c.result and c.result.can_test and len(c.result.null_distribution) > 0:
            fname = f"{NULL_DIR}/cell_{c.encoder}_{c.benchmark}_{c.model_size}.npy"
            np.save(fname, c.result.null_distribution)

    logger.info("Results saved to %s", RESULTS_DIR)


def main():
    logger.info("=== H-M2: Spearman Correlation Experiment ===")

    # S-0: verify environment
    import scipy
    logger.info("scipy version: %s", scipy.__version__)
    assert tuple(int(x) for x in scipy.__version__.split(".")[:2]) >= (1, 7), "scipy>=1.7 required"

    # A-2: load data
    sim_matrices = load_h_e1_similarities()
    pass_1b = load_h_e2_pass_at_1()
    pass_7b = load_h_c1_pass_at_1()

    validate_inputs(sim_matrices, pass_1b)

    pass_matrices = {"1b": pass_1b}
    model_sizes = list(CFG.model_sizes)
    if pass_7b is not None:
        pass_matrices["7b"] = pass_7b
        model_sizes.append("7b")

    # A-3: statistical analysis
    cell_results = run_all_cells(sim_matrices, pass_matrices, model_sizes=model_sizes)

    # A-4: gate evaluation
    gate = evaluate_gate(cell_results)
    logger.info("GATE RESULT: %s — %s", gate.gate_status, gate.reason)
    logger.info("Satisfied cells: %s", gate.satisfied_cells)
    logger.info("Concordant benchmarks: %s", gate.concordant_benchmarks)

    # A-5: save results
    save_results(cell_results, gate)

    # A-6: visualize
    save_all_figures(sim_matrices, pass_matrices, cell_results)

    # Summary
    print("\n=== RESULTS SUMMARY ===")
    for c in cell_results:
        if c.status == "TESTED":
            r = c.result
            print(f"  {cell_id(c)}: rho={r.rho:.4f} p={r.pvalue:.4f} sig={r.significant} CI=[{r.ci_lo:.3f},{r.ci_hi:.3f}]")
        else:
            print(f"  {cell_id(c)}: CANNOT_TEST")
    print(f"\n  GATE: {gate.gate_status}")
    print(f"  Reason: {gate.reason}")
    print("======================\n")


if __name__ == "__main__":
    main()
