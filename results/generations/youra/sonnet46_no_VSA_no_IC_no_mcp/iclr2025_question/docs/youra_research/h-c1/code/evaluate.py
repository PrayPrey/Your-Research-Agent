import sys
import os
import json
import numpy as np


def load_bootstrap_auroc(hm2_code_dir):
    """Load bootstrap_auroc from h-m2 via importlib to avoid local shadowing."""
    import importlib.util
    # resolve relative to this file
    abs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), hm2_code_dir))
    spec = importlib.util.spec_from_file_location(
        "hm2_evaluate",
        os.path.join(abs_dir, "evaluate.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.bootstrap_auroc


def load_hm4_baselines(hm4_results_path):
    """Returns dict with h-m4 TriviaQA AUROC baselines."""
    try:
        with open(hm4_results_path) as f:
            data = json.load(f)
        return {
            "auroc_se": data.get("auroc_se", 0.286),
            "auroc_te": data.get("auroc_te", 0.4381),
            "auroc_vc": data.get("auroc_vc", 0.4463),
            "n": data.get("n_questions", 98),
        }
    except Exception as e:
        print(f"Warning: could not load h-m4 baselines from {hm4_results_path}: {e}")
        return {"auroc_se": 0.286, "auroc_te": 0.4381, "auroc_vc": 0.4463, "n": 98}


def evaluate_gate(auroc_se, auroc_scg, auroc_te, auroc_vc):
    """Three-tier gate evaluation for H-C1."""
    gate_primary = auroc_se > auroc_te
    gate_secondary = auroc_vc < auroc_te
    gate_tertiary = (auroc_se >= auroc_scg) and (auroc_scg > auroc_te) and (auroc_te > auroc_vc)
    gate_passed = gate_primary

    print(f"H-C1 TruthfulQA: SE={auroc_se:.4f}, SCG={auroc_scg:.4f}, "
          f"TE={auroc_te:.4f}, VC={auroc_vc:.4f}")
    print(f"Gate primary (SE>TE): {gate_primary} | secondary (VC<TE): {gate_secondary} | "
          f"tertiary (full ranking): {gate_tertiary}")
    print(f"Gate result: {'PASS' if gate_passed else 'FAIL'}")

    return {
        "gate_primary": gate_primary,
        "gate_secondary": gate_secondary,
        "gate_tertiary": gate_tertiary,
        "gate_passed": gate_passed,
    }


def compute_all_aurocs(se_scores, scg_scores, te_scores, vc_scores, em_labels, cfg):
    """Bootstrap AUROC for all 4 methods. Returns comprehensive results dict."""
    bootstrap_auroc = load_bootstrap_auroc(cfg.hm2_code_dir)

    results = {}
    bootstrap_samples = {}

    method_scores = [
        ("se", se_scores),
        ("scg", scg_scores),
        ("te", te_scores),
        ("vc", vc_scores),
    ]

    for method, scores in method_scores:
        print(f"Computing AUROC for {method.upper()}...")
        auroc, ci_lo, ci_hi = bootstrap_auroc(scores, em_labels, cfg.n_bootstrap, cfg.seed)
        results[f"auroc_{method}"] = auroc
        results[f"auroc_{method}_ci"] = [ci_lo, ci_hi]
        bootstrap_samples[method] = {"auroc": auroc, "ci": [ci_lo, ci_hi]}

    gate_results = evaluate_gate(
        results["auroc_se"], results["auroc_scg"],
        results["auroc_te"], results["auroc_vc"]
    )
    results.update(gate_results)

    method_aurocs = {
        "SE": results["auroc_se"],
        "SCG": results["auroc_scg"],
        "TE": results["auroc_te"],
        "VC": results["auroc_vc"],
    }
    sorted_methods = sorted(method_aurocs.items(), key=lambda x: x[1], reverse=True)
    results["ranking"] = " > ".join(f"{m}({a:.4f})" for m, a in sorted_methods)
    results["bootstrap_samples"] = bootstrap_samples

    return results
