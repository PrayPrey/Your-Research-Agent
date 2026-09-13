"""Main orchestration for H-M1 experiment."""
import json
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForSeq2SeqLM, RobertaTokenizer
from peft import PeftModel

from config import MINEConfig
from traces import extract_refinement_pairs

# Load H-E1 modules via importlib.util to avoid name conflicts
import sys

def _load_he1_module(name: str):
    """Load H-E1 module by full path, isolated from h-m1 config."""
    cfg = MINEConfig()
    file_path = cfg.h_e1_dir / "code" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"he1_{name}", file_path)
    module = importlib.util.module_from_spec(spec)
    # Temporarily add h-e1/code to path so relative imports work
    old_path = sys.path.copy()
    sys.path.insert(0, str(cfg.h_e1_dir / "code"))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path = old_path
    return module

# Load H-E1 config first (data.py imports it)
_he1_config_mod = _load_he1_module("config")
he1_Config = _he1_config_mod.Config

# Inject it into sys.modules so data.py can find it
sys.modules["config_backup"] = sys.modules.get("config")
sys.modules["config"] = _he1_config_mod
_he1_data_mod = _load_he1_module("data")
he1_load_humaneval_plus = _he1_data_mod.load_humaneval_plus
# Restore our config
if sys.modules.get("config_backup"):
    sys.modules["config"] = sys.modules["config_backup"]
del sys.modules["config_backup"]

from embed import embed_text, Projector
from mine import MINEEstimator, train_mine
from stats import control_for_edit_length, compute_cohens_d, evaluate_hypothesis
from visualize import plot_mi_comparison_bar, plot_mi_vs_edit_length, plot_permutation_distribution


def load_model_with_adapter(adapter_path: Path, base_model, tokenizer):
    """Load LoRA adapter onto base model."""
    print(f"Loading adapter from {adapter_path}")
    model = PeftModel.from_pretrained(base_model, str(adapter_path))
    return model


def run_condition(
    model,
    tokenizer,
    problems: dict,
    cfg: MINEConfig,
    projector: Projector,
    label: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Extract traces, embed, train MINE, return per-sample MI + edit_lengths."""
    print(f"\n{'='*50}")
    print(f"Running condition: {label}")
    print(f"{'='*50}")

    all_pairs = []
    for seed in cfg.seeds:
        print(f"  Extracting traces with seed={seed}...")
        pairs = extract_refinement_pairs(model, tokenizer, problems, cfg, seed)
        all_pairs.extend(pairs)
        print(f"    Extracted {len(pairs)} pairs")

    print(f"  Total pairs for {label}: {len(all_pairs)}")

    if len(all_pairs) < 10:
        print(f"  WARNING: Too few pairs ({len(all_pairs)}), using dummy MI values")
        return np.zeros(len(all_pairs)), np.zeros(len(all_pairs))

    # Embed feedback and edit text
    feedbacks = [p["feedback"] for p in all_pairs]
    edits = [p["edit"] for p in all_pairs]
    edit_lengths = np.array([p["edit_length"] for p in all_pairs], dtype=np.float32)

    # Filter empty strings
    valid_idx = [i for i, (f, e) in enumerate(zip(feedbacks, edits)) if f.strip() and e.strip()]
    if len(valid_idx) < len(all_pairs):
        print(f"  Filtered {len(all_pairs) - len(valid_idx)} empty pairs")

    feedbacks = [feedbacks[i] for i in valid_idx]
    edits = [edits[i] for i in valid_idx]
    edit_lengths = edit_lengths[valid_idx]

    if len(feedbacks) < 10:
        print(f"  WARNING: Too few valid pairs ({len(feedbacks)}), using dummy MI values")
        return np.zeros(len(valid_idx)), edit_lengths

    print(f"  Embedding {len(feedbacks)} feedback texts...")
    # Batch embedding
    batch_size = 32
    feedback_embs = []
    edit_embs = []
    device = next(model.parameters()).device

    for i in range(0, len(feedbacks), batch_size):
        fb_batch = feedbacks[i:i+batch_size]
        ed_batch = edits[i:i+batch_size]
        fb_emb = embed_text(model.base_model, tokenizer, fb_batch, projector)
        ed_emb = embed_text(model.base_model, tokenizer, ed_batch, projector)
        feedback_embs.append(fb_emb)
        edit_embs.append(ed_emb)

    feedback_emb = torch.cat(feedback_embs, dim=0)
    edit_emb = torch.cat(edit_embs, dim=0)

    # Train MINE
    print(f"  Training MINE estimator...")
    estimator = MINEEstimator(
        feedback_dim=cfg.embed_dim,
        code_dim=cfg.embed_dim,
        hidden_dim=cfg.hidden_dim,
    ).to(device)

    estimator, losses = train_mine(
        estimator,
        feedback_emb,
        edit_emb,
        lr=cfg.mine_lr,
        batch_size=cfg.mine_batch_size,
        n_iters=cfg.mine_iters,
    )

    # Compute per-sample MI estimates
    print(f"  Computing per-sample MI estimates...")
    with torch.no_grad():
        mi_values = []
        for i in range(len(feedback_emb)):
            fb = feedback_emb[i:i+1]
            ed = edit_emb[i:i+1]
            # Use all other edits as marginal samples
            marginal_idx = torch.tensor([j for j in range(len(edit_emb)) if j != i], device=device)
            if len(marginal_idx) > 0:
                marginal_ed = edit_emb[marginal_idx[:min(128, len(marginal_idx))]]
                # Repeat feedback for marginal comparison
                fb_repeated = fb.repeat(len(marginal_ed), 1)
                joint_score = estimator(fb, ed).item()
                marginal_scores = estimator(fb_repeated, marginal_ed)
                mi = joint_score - torch.logsumexp(marginal_scores, dim=0).item() + np.log(len(marginal_ed))
            else:
                mi = 0.0
            mi_values.append(mi)

    mi_values = np.array(mi_values, dtype=np.float32)
    print(f"  Mean MI for {label}: {mi_values.mean():.4f}")

    return mi_values, edit_lengths


def main():
    print("="*60)
    print("H-M1 Experiment: I(F;E)_RL > I(F;E)_CE")
    print("="*60)

    cfg = MINEConfig()

    # Verify H-E1 adapters exist
    if not cfg.ce_path.exists():
        raise FileNotFoundError(f"CE adapter not found: {cfg.ce_path}")
    if not cfg.rl_path.exists():
        raise FileNotFoundError(f"RL adapter not found: {cfg.rl_path}")

    # Load base model and tokenizer
    print("\nLoading base model and tokenizer...")
    he1_cfg = he1_Config()
    # Use local snapshot path to avoid tokenizer download issues
    snapshot_path = cfg.cache_dir / "models--Salesforce--codet5p-220m" / "snapshots" / "2b92f36e2782341a50551759fdba0dd15e821f99"
    tokenizer = RobertaTokenizer.from_pretrained(str(snapshot_path), local_files_only=True)
    use_cuda = torch.cuda.is_available()
    base_model = AutoModelForSeq2SeqLM.from_pretrained(
        str(snapshot_path),
        local_files_only=True,
        torch_dtype=torch.float16 if use_cuda else torch.float32,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    base_model = base_model.to(device)
    print(f"Device: {device}")

    # Load problems
    print("\nLoading HumanEval+ problems...")
    problems = he1_load_humaneval_plus(he1_cfg)
    # Subset for CPU feasibility
    if cfg.max_problems and cfg.max_problems < len(problems):
        problem_ids = list(problems.keys())[:cfg.max_problems]
        problems = {k: problems[k] for k in problem_ids}
    print(f"Using {len(problems)} problems (max_problems={cfg.max_problems})")

    # Create projector
    hidden_dim = base_model.config.d_model
    projector = Projector(hidden_dim, cfg.embed_dim).to(device)

    # Run CE condition
    ce_model = load_model_with_adapter(cfg.ce_path, base_model, tokenizer)
    ce_model = ce_model.to(device)
    mi_ce, edit_len_ce = run_condition(ce_model, tokenizer, problems, cfg, projector, "CE")
    del ce_model
    torch.cuda.empty_cache()

    # Run RL condition
    rl_model = load_model_with_adapter(cfg.rl_path, base_model, tokenizer)
    rl_model = rl_model.to(device)
    mi_rl, edit_len_rl = run_condition(rl_model, tokenizer, problems, cfg, projector, "RL")
    del rl_model
    torch.cuda.empty_cache()

    # Combine results
    mi_values = np.concatenate([mi_ce, mi_rl])
    edit_lengths = np.concatenate([edit_len_ce, edit_len_rl])
    condition_labels = np.array(["CE"] * len(mi_ce) + ["RL"] * len(mi_rl))

    # Statistical analysis
    print("\n" + "="*50)
    print("Statistical Analysis")
    print("="*50)

    results = control_for_edit_length(mi_values, edit_lengths, condition_labels, cfg.n_permutations)
    cohens_d = compute_cohens_d(results["residuals"], condition_labels)
    results["cohens_d"] = cohens_d

    gate = evaluate_hypothesis(results)

    print(f"  MI (CE, raw): {results['mi_ce_raw']:.4f}")
    print(f"  MI (RL, raw): {results['mi_rl_raw']:.4f}")
    print(f"  MI (CE, controlled): {results['mi_ce_controlled']:.4f}")
    print(f"  MI (RL, controlled): {results['mi_rl_controlled']:.4f}")
    print(f"  Observed diff (RL - CE): {results['observed_diff']:.4f}")
    print(f"  p-value: {results['p_value']:.4f}")
    print(f"  Cohen's d: {cohens_d:.4f}")
    print(f"  Gate: {gate['gate_status']}")

    # Visualization
    print("\nGenerating visualizations...")
    plot_mi_comparison_bar(results, str(cfg.figures_dir / "mi_comparison.png"))
    plot_mi_vs_edit_length(
        mi_values, edit_lengths, condition_labels,
        results["slope"], results["intercept"],
        str(cfg.figures_dir / "mi_vs_edit_length.png")
    )
    plot_permutation_distribution(
        results["perm_diffs"],
        results["observed_diff"],
        results["p_value"],
        str(cfg.figures_dir / "permutation_dist.png")
    )

    # Save results
    print("\nSaving results...")
    output_results = {
        "hypothesis": "H-M1: I(F;E)_RL > I(F;E)_CE controlling for edit length",
        "gate_status": gate["gate_status"],
        "mi_ce_raw": float(results["mi_ce_raw"]),
        "mi_rl_raw": float(results["mi_rl_raw"]),
        "mi_ce_controlled": float(results["mi_ce_controlled"]),
        "mi_rl_controlled": float(results["mi_rl_controlled"]),
        "observed_diff": float(results["observed_diff"]),
        "p_value": float(results["p_value"]),
        "cohens_d": float(cohens_d),
        "n_ce_samples": int(len(mi_ce)),
        "n_rl_samples": int(len(mi_rl)),
        "seeds": cfg.seeds,
        "n_permutations": cfg.n_permutations,
    }

    with open(cfg.output_dir / "results.json", "w") as f:
        json.dump(output_results, f, indent=2)

    # CSV for detailed results
    df = pd.DataFrame({
        "condition": condition_labels,
        "mi_value": mi_values,
        "edit_length": edit_lengths,
        "residual": results["residuals"],
    })
    df.to_csv(cfg.output_dir / "results.csv", index=False)

    print(f"\nResults saved to {cfg.output_dir}")
    print("="*60)
    print(f"EXPERIMENT COMPLETE - Gate: {gate['gate_status']}")
    print("="*60)

    return output_results


if __name__ == "__main__":
    main()
