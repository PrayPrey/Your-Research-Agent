"""Analysis pipeline for H-M1."""
import json
import os
import torch
from collections import defaultdict
from tqdm import tqdm
from config import AnalysisConfig, GATE_ENTROPY_INCREASE_PCT, GATE_BASE_LENGTH, GATE_TARGET_LENGTH
from data import get_long_documents, truncate_to_length
from model import load_model_and_tokenizer, extract_attentions, verify_attention_valid
from metrics import compute_entropy, compute_sparsity, aggregate_stats, entropy_change_pct

def run_analysis(config: AnalysisConfig, model, tokenizer, documents: list) -> dict:
    """Loop target_lengths x documents x middle_layers, compute entropy/sparsity."""
    acc = defaultdict(lambda: defaultdict(lambda: {"entropy": [], "sparsity": []}))

    for length in config.target_lengths:
        print(f"\nProcessing length {length}...")
        for doc_idx, doc in enumerate(tqdm(documents, desc=f"Length {length}")):
            tokens = truncate_to_length(doc, tokenizer, length)
            actual_len = tokens["input_ids"].shape[1]
            if actual_len < length:
                continue

            try:
                attns = extract_attentions(model, tokens, config.middle_layers)
                for layer, attn in attns.items():
                    verify_attention_valid(attn)
                    H = compute_entropy(attn, config.entropy_clamp_min)
                    S = compute_sparsity(attn, config.top_k)
                    acc[length][layer]["entropy"].append(H.mean().item())
                    acc[length][layer]["sparsity"].append(S.mean().item())
                del attns
                torch.cuda.empty_cache()
            except RuntimeError as e:
                if "out of memory" in str(e).lower():
                    print(f"OOM at doc {doc_idx}, length {length}, skipping")
                    torch.cuda.empty_cache()
                    continue
                raise

    results = {
        length: {
            layer: {
                "entropy": aggregate_stats(acc[length][layer]["entropy"]),
                "sparsity": aggregate_stats(acc[length][layer]["sparsity"])
            }
            for layer in config.middle_layers
        }
        for length in config.target_lengths
    }
    return results

def compute_gate_metrics(results: dict, config: AnalysisConfig) -> dict:
    """Compute gate metrics: entropy change from 2K to 16K."""
    per_layer = {}
    overall_entropies_base = []
    overall_entropies_target = []

    for layer in config.middle_layers:
        base_entropy = results[GATE_BASE_LENGTH][layer]["entropy"]["mean"]
        target_entropy = results[GATE_TARGET_LENGTH][layer]["entropy"]["mean"]
        change_pct = entropy_change_pct(base_entropy, target_entropy)
        per_layer[layer] = {
            "base_entropy": base_entropy,
            "target_entropy": target_entropy,
            "change_pct": change_pct,
            "pass": change_pct > GATE_ENTROPY_INCREASE_PCT
        }
        overall_entropies_base.append(base_entropy)
        overall_entropies_target.append(target_entropy)

    overall_base = sum(overall_entropies_base) / len(overall_entropies_base)
    overall_target = sum(overall_entropies_target) / len(overall_entropies_target)
    overall_pct = entropy_change_pct(overall_base, overall_target)

    return {
        "per_layer": per_layer,
        "overall_base_entropy": overall_base,
        "overall_target_entropy": overall_target,
        "overall_change_pct": overall_pct,
        "gate_threshold": GATE_ENTROPY_INCREASE_PCT,
        "pass": overall_pct > GATE_ENTROPY_INCREASE_PCT
    }

def save_results(results: dict, gate_metrics: dict, config: AnalysisConfig) -> None:
    """Save results to JSON."""
    os.makedirs(config.output_dir, exist_ok=True)
    output_path = os.path.join(config.output_dir, "results.json")

    output = {
        "results": results,
        "gate_metrics": gate_metrics,
        "config": {
            "model_name": config.model_name,
            "target_lengths": config.target_lengths,
            "middle_layers": config.middle_layers,
            "num_samples": config.num_samples,
            "seed": config.seed
        }
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to {output_path}")
