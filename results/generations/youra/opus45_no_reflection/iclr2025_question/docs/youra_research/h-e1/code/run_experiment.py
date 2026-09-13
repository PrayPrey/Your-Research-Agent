#!/usr/bin/env python
import os
import sys
import json
import torch
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CFG, set_seed
from data import load_triviaqa, build_labeled_dataset_batched
from model import HiddenStateExtractor, LinearProbe, extract_hidden_states, train_probe
from evaluate import evaluate_auroc, plot_gate_comparison, plot_roc_curve, plot_loss_curve, plot_hidden_state_pca


def main():
    set_seed(CFG.seed)

    code_dir = os.path.dirname(os.path.abspath(__file__))
    hypothesis_dir = os.path.dirname(code_dir)
    figures_dir = os.path.join(hypothesis_dir, "figures")
    cache_dir = os.path.join(code_dir, "cache")
    outputs_dir = os.path.join(code_dir, "outputs")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)

    train_cache = os.path.join(cache_dir, "train_hidden_states.pt")
    val_cache = os.path.join(cache_dir, "val_hidden_states.pt")

    print(f"Loading model: {CFG.model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        CFG.model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    tokenizer = AutoTokenizer.from_pretrained(CFG.model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if os.path.exists(train_cache) and os.path.exists(val_cache):
        print("Loading cached hidden states...")
        train_data = torch.load(train_cache)
        val_data = torch.load(val_cache)
        train_hidden = train_data["hidden_states"]
        train_labels = train_data["labels"]
        val_hidden = val_data["hidden_states"]
        val_labels = val_data["labels"]
    else:
        print(f"Loading TriviaQA train ({CFG.train_size}) and val ({CFG.val_size})...")
        train_ds = load_triviaqa("train", CFG.train_size)
        val_ds = load_triviaqa("val", CFG.val_size)

        print("Generating answers and labels for training set...")
        train_examples = build_labeled_dataset_batched(model, tokenizer, train_ds, CFG.train_size, batch_size=16)
        print(f"Train: {sum(e['label'] for e in train_examples)}/{len(train_examples)} correct")

        print("Generating answers and labels for validation set...")
        val_examples = build_labeled_dataset_batched(model, tokenizer, val_ds, CFG.val_size, batch_size=16)
        print(f"Val: {sum(e['label'] for e in val_examples)}/{len(val_examples)} correct")

        print(f"Extracting hidden states from layer {CFG.target_layer}...")
        extractor = HiddenStateExtractor(model, CFG.target_layer)
        train_hidden, train_labels = extract_hidden_states(model, tokenizer, extractor, train_examples)

        extractor = HiddenStateExtractor(model, CFG.target_layer)
        val_hidden, val_labels = extract_hidden_states(model, tokenizer, extractor, val_examples)

        print("Caching hidden states...")
        torch.save({"hidden_states": train_hidden, "labels": train_labels}, train_cache)
        torch.save({"hidden_states": val_hidden, "labels": val_labels}, val_cache)

    print(f"Train hidden states: {train_hidden.shape}, Labels: {train_labels.shape}")
    print(f"Val hidden states: {val_hidden.shape}, Labels: {val_labels.shape}")

    print(f"\nTraining linear probe (epochs={CFG.epochs}, lr={CFG.lr})...")
    probe, loss_per_epoch = train_probe(train_hidden, train_labels, CFG)

    print("\nEvaluating on validation set...")
    auroc, preds, labels_np = evaluate_auroc(probe, val_hidden, val_labels)

    print(f"\n{'='*50}")
    print(f"AUROC: {auroc:.4f}")
    print(f"Gate Threshold: {CFG.auroc_gate}")
    print(f"Baseline: {CFG.auroc_baseline}")
    gate_pass = auroc > CFG.auroc_gate
    print(f"Gate Result: {'PASS' if gate_pass else 'FAIL'}")
    print(f"{'='*50}")

    print("\nGenerating figures...")
    plot_gate_comparison(auroc, CFG.auroc_baseline, CFG.auroc_gate,
                        os.path.join(figures_dir, "gate_comparison.png"))
    plot_roc_curve(labels_np, preds, auroc,
                  os.path.join(figures_dir, "roc_curve.png"))
    plot_loss_curve(loss_per_epoch,
                   os.path.join(figures_dir, "loss_curve.png"))
    plot_hidden_state_pca(val_hidden, val_labels,
                         os.path.join(figures_dir, "hidden_state_pca.png"))

    results = {
        "hypothesis_id": "h-e1",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "model_name": CFG.model_name,
            "target_layer": CFG.target_layer,
            "hidden_dim": CFG.hidden_dim,
            "train_size": CFG.train_size,
            "val_size": CFG.val_size,
            "lr": CFG.lr,
            "epochs": CFG.epochs,
            "batch_size": CFG.batch_size,
            "seed": CFG.seed
        },
        "metrics": {
            "auroc": float(auroc),
            "auroc_gate": CFG.auroc_gate,
            "auroc_baseline": CFG.auroc_baseline,
            "train_correct_ratio": float(train_labels.float().mean().item()),
            "val_correct_ratio": float(val_labels.float().mean().item()),
            "final_train_loss": loss_per_epoch[-1] if loss_per_epoch else None
        },
        "gate": {
            "type": "MUST_WORK",
            "condition": f"AUROC > {CFG.auroc_gate}",
            "satisfied": gate_pass,
            "result": "PASS" if gate_pass else "FAIL"
        },
        "loss_per_epoch": loss_per_epoch,
        "figures": [
            "figures/gate_comparison.png",
            "figures/roc_curve.png",
            "figures/loss_curve.png",
            "figures/hidden_state_pca.png"
        ]
    }

    results_path = os.path.join(hypothesis_dir, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    csv_path = os.path.join(outputs_dir, "results.csv")
    with open(csv_path, "w") as f:
        f.write("epoch,loss\n")
        for i, loss in enumerate(loss_per_epoch, 1):
            f.write(f"{i},{loss:.6f}\n")
    print(f"Training log saved to: {csv_path}")

    probe_path = os.path.join(cache_dir, "probe.pt")
    torch.save(probe.state_dict(), probe_path)
    print(f"Probe saved to: {probe_path}")

    return results


if __name__ == "__main__":
    results = main()
    print("\nExperiment completed.")
