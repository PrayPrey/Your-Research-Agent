"""
H-E1: LoRA-KV Misalignment Diagnostic Experiment
Spearman rank correlation between LoRA attention weights and Locret CIS scores.
"""
import os
import sys
import json
import torch
import numpy as np

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ExperimentConfig
from data_loader import MNLIDataLoader
from lora_extractor import LoRAExtractor
from locret_extractor import LocretExtractor
from correlate import SpearmanCorrelator
from visualize import ResultVisualizer


def check_borderline(mean_rho: float, config: ExperimentConfig) -> bool:
    return config.borderline_low <= mean_rho <= config.borderline_high


def save_results(results: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✓ Results saved: {path}")


def run_on_dataset(config: ExperimentConfig, n: int):
    """Run the full extraction + correlation pipeline on n examples."""
    loader = MNLIDataLoader(config)
    correlator = SpearmanCorrelator(config)

    print(f"\n{'='*60}")
    print(f"H-E1: Loading {n} MNLI examples (seed={config.seed})")
    print(f"{'='*60}")

    dataset = loader.load(n)

    # ── Step 1: Extract LoRA attention scores ─────────────────────
    print("\n[Step 1/2] Loading LoRA model and extracting attention scores...")
    lora_ext = LoRAExtractor(config)
    model, tokenizer = lora_ext.load_model()

    tokenized = loader.tokenize(dataset, tokenizer)

    lora_all_examples = []
    for i in range(len(tokenized)):
        if i % 10 == 0:
            print(f"  LoRA extraction: {i}/{len(tokenized)}")
        batch = loader.get_batch(tokenized, i)
        input_ids = batch["input_ids"].to(next(model.parameters()).device)
        attention_mask = batch["attention_mask"].to(next(model.parameters()).device)
        scores = lora_ext.extract_attention_scores(model, input_ids, attention_mask)
        lora_all_examples.append((scores, batch["attention_mask"]))

    lora_ext.unload()

    # ── Step 2: Extract Locret CIS scores ─────────────────────────
    print("\n[Step 2/2] Loading Locret model and extracting CIS scores...")
    locret_ext = LocretExtractor(config)
    locret_model = locret_ext.load_model()

    cis_all_examples = []
    for i in range(len(tokenized)):
        if i % 10 == 0:
            print(f"  Locret extraction: {i}/{len(tokenized)}")
        batch = loader.get_batch(tokenized, i)
        input_ids = batch["input_ids"].to(next(locret_model.parameters()).device)
        attention_mask = batch["attention_mask"].to(next(locret_model.parameters()).device)
        cis_scores = locret_ext.extract_cis_scores(locret_model, input_ids, attention_mask)
        cis_all_examples.append(cis_scores)

    locret_ext.unload()

    # ── Step 3: Compute Spearman ρ ────────────────────────────────
    print("\n[Step 3] Computing Spearman correlations...")
    per_example_rho = []
    per_example_per_head = []
    per_example_per_layer = []

    for i in range(len(lora_all_examples)):
        lora_scores, attention_mask = lora_all_examples[i]
        cis_scores = cis_all_examples[i]
        mean_rho, per_head, per_layer = correlator.compute_example_rho(
            lora_scores, cis_scores, attention_mask
        )
        per_example_rho.append(mean_rho)
        per_example_per_head.append(per_head)
        per_example_per_layer.append(per_layer)

    return correlator.aggregate_results(per_example_rho, per_example_per_head, per_example_per_layer), \
           lora_all_examples, cis_all_examples


def run(config: ExperimentConfig = None) -> dict:
    if config is None:
        config = ExperimentConfig()

    # Set GPU
    if torch.cuda.is_available():
        os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
        print(f"✓ GPU available: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠ No GPU detected, running on CPU")

    torch.manual_seed(config.seed)
    np.random.seed(config.seed)

    # Primary run: 100 examples
    results, lora_samples, cis_samples = run_on_dataset(config, config.primary_n)
    mean_rho = results["mean_rho"]

    print(f"\n{'='*60}")
    print(f"Primary result (n={config.primary_n}): mean_rho = {mean_rho:.4f}")

    # Borderline extension: 500 examples
    if check_borderline(mean_rho, config):
        print(f"⚠ Borderline ρ={mean_rho:.4f} ∈ [{config.borderline_low}, {config.borderline_high}]")
        print(f"  Extending to {config.extended_n} examples...")
        results, lora_samples, cis_samples = run_on_dataset(config, config.extended_n)
        mean_rho = results["mean_rho"]
        print(f"Extended result (n={config.extended_n}): mean_rho = {mean_rho:.4f}")

    # Gate evaluation
    passed = mean_rho < config.misalignment_threshold
    results["pass"] = passed
    results["mean_rho"] = mean_rho
    results["hypothesis_id"] = "H-E1"
    results["misalignment_threshold"] = config.misalignment_threshold
    results["n_examples"] = config.primary_n if not check_borderline(mean_rho, config) else config.extended_n

    # Build full results structure
    full_results = {
        "hypothesis_id": "H-E1",
        "primary_n": config.primary_n,
        "seed": config.seed,
        "misalignment_threshold": config.misalignment_threshold,
        "summary": {
            "mean_spearman_rho": mean_rho,
            "std_spearman_rho": results["std_rho"],
            "fraction_below_threshold": float(np.mean(np.array(results["all_example_rhos"]) < config.misalignment_threshold)),
            "misalignment_confirmed": passed,
        },
        "per_layer": [
            {
                "layer": i,
                "mean_rho": float(np.mean(row)),
                "std_rho": float(np.std(row)),
                "per_head_rho": [float(v) for v in row],
            }
            for i, row in enumerate(results["per_layer_mean"])
        ],
        "borderline_examples": [],
        "figures": {},
        "pass": passed,
        "mean_rho": mean_rho,
        "std_rho": results["std_rho"],
        "all_example_rhos": results["all_example_rhos"],
        "per_layer_mean": results["per_layer_mean"],
    }

    # Save results
    results_path = config.get_results_path()
    save_results(full_results, results_path)

    # Generate figures
    print("\n[Figures] Generating visualizations...")
    try:
        viz = ResultVisualizer(config)
        # Prepare sample data for scatter
        lora_sample_scores = []
        cis_sample_scores = []
        if lora_samples:
            lora_layer0 = [s[layer_i] for s in [lora_samples[i][0] for i in range(min(5, len(lora_samples)))] for layer_i in [0]]
            lora_sample_scores = [[s.float().numpy().mean(axis=0) for s in lora_samples[i][0][:1]] for i in range(min(5, len(lora_samples)))]
            cis_sample_scores = [[s.float().numpy().mean(axis=0) for s in cis_samples[i][:1]] for i in range(min(5, len(cis_samples)))]

        figure_paths = viz.save_all(full_results, lora_sample_scores, cis_sample_scores, [])
        full_results["figures"] = {k: v for k, v in figure_paths.items() if v is not None}
        save_results(full_results, results_path)
        print("✓ Figures generated")
    except Exception as e:
        print(f"⚠ Figure generation failed: {e}")

    verdict = "PASS (misalignment confirmed)" if passed else "FAIL (no misalignment)"
    print(f"\n{'='*60}")
    print(f"H-E1 RESULT: mean_rho={mean_rho:.4f} | Gate: {verdict}")
    print(f"  threshold={config.misalignment_threshold} | pass={passed}")
    print(f"{'='*60}\n")

    return full_results


if __name__ == "__main__":
    config = ExperimentConfig()
    # Set hypothesis folder to parent of code/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config.hypothesis_folder = os.path.dirname(script_dir)
    results = run(config)
    print(f"mean_rho={results['mean_rho']:.4f} | PASS={results['pass']}")
