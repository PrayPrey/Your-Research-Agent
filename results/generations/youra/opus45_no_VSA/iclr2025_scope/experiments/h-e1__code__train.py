"""H-E1 Experiment Orchestration - Main entrypoint"""
import os
import json
import sys

# Add code dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG, TOP1_PASS, TOP3_PASS, TOP3_FAIL
from data import stream_instructions, encode_labels, stratified_split
from model import AdapterSelectionProbe
from evaluate import (
    random_baseline, majority_baseline,
    plot_gate_metrics, plot_confusion_matrix,
    plot_per_class_accuracy, plot_embedding_tsne,
)


def main():
    print("=" * 60)
    print("H-E1 Experiment: Linear Probe Adapter Selection")
    print("=" * 60)

    # Setup paths
    code_dir = os.path.dirname(os.path.abspath(__file__))
    hypothesis_dir = os.path.dirname(code_dir)
    figures_dir = os.path.join(hypothesis_dir, "figures")
    outputs_dir = os.path.join(code_dir, "outputs")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)

    # Step 1: Load data
    print("\n[1/6] Loading dataset...")
    samples, task_families = stream_instructions(CONFIG)
    if len(samples) < 100:
        print(f"ERROR: Only {len(samples)} samples collected. Need more data.")
        sys.exit(1)

    labels = encode_labels(samples, task_families)
    num_classes = len(task_families)
    print(f"  Classes: {num_classes}")

    # Step 2: Split data
    print("\n[2/6] Splitting data...")
    splits = stratified_split(samples, labels, CONFIG)
    X_train, y_train = splits["train"]
    X_val, y_val = splits["val"]
    X_test, y_test = splits["test"]

    # Step 3: Train linear probe
    print("\n[3/6] Training linear probe...")
    probe = AdapterSelectionProbe(
        encoder_name=CONFIG.encoder_name,
        num_classes=num_classes,
        max_iter=CONFIG.max_iter,
        solver=CONFIG.solver,
        random_state=CONFIG.random_state,
    )
    probe.fit(X_train, y_train)

    # Step 4: Evaluate
    print("\n[4/6] Evaluating...")
    test_results = probe.evaluate(X_test, y_test, k=CONFIG.top_k)
    top1_acc = test_results["top1_accuracy"]
    top3_acc = test_results["top3_accuracy"]

    print(f"  Top-1 Accuracy: {top1_acc:.4f} (threshold: {TOP1_PASS})")
    print(f"  Top-3 Accuracy: {top3_acc:.4f} (threshold: {TOP3_PASS})")

    # Baselines
    print("\n[5/6] Computing baselines...")
    random_acc = random_baseline(y_test, num_classes, CONFIG.random_state)
    majority_acc = majority_baseline(y_train, y_test)
    print(f"  Random baseline: {random_acc:.4f}")
    print(f"  Majority baseline: {majority_acc:.4f}")

    # Gate check
    gate_pass = (top1_acc >= TOP1_PASS) or (top3_acc >= TOP3_PASS)
    gate_fail = top3_acc < TOP3_FAIL

    if gate_pass:
        gate_result = "PASS"
    elif gate_fail:
        gate_result = "FAIL"
    else:
        gate_result = "PARTIAL"

    print(f"\n  GATE RESULT: {gate_result}")

    # Step 6: Generate figures
    print("\n[6/6] Generating figures...")
    y_pred = probe.predict(X_test).tolist()

    plot_gate_metrics(top1_acc, top3_acc, os.path.join(figures_dir, "gate_metrics.png"))
    plot_confusion_matrix(y_test, y_pred, task_families, os.path.join(figures_dir, "confusion_matrix.png"))
    plot_per_class_accuracy(y_test, y_pred, task_families, os.path.join(figures_dir, "per_class_accuracy.png"))

    # t-SNE on test embeddings
    test_embeddings = probe.encode(X_test)
    plot_embedding_tsne(test_embeddings, y_test, task_families, os.path.join(figures_dir, "tsne_embeddings.png"))

    # Save results
    results = {
        "hypothesis_id": "h-e1",
        "top1_accuracy": top1_acc,
        "top3_accuracy": top3_acc,
        "random_baseline": random_acc,
        "majority_baseline": majority_acc,
        "gate_result": gate_result,
        "gate_thresholds": {
            "top1_pass": TOP1_PASS,
            "top3_pass": TOP3_PASS,
            "top3_fail": TOP3_FAIL,
        },
        "num_classes": num_classes,
        "class_names": task_families,
        "n_train": len(X_train),
        "n_val": len(X_val),
        "n_test": len(X_test),
        "config": {
            "encoder_name": CONFIG.encoder_name,
            "max_iter": CONFIG.max_iter,
            "solver": CONFIG.solver,
        }
    }

    results_path = os.path.join(hypothesis_dir, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    # CSV output
    import csv
    csv_path = os.path.join(outputs_dir, "results.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        writer.writerow(["top1_accuracy", top1_acc])
        writer.writerow(["top3_accuracy", top3_acc])
        writer.writerow(["random_baseline", random_acc])
        writer.writerow(["majority_baseline", majority_acc])
        writer.writerow(["gate_result", gate_result])
    print(f"CSV saved: {csv_path}")

    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE - Gate: {gate_result}")
    print("=" * 60)

    return gate_result


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result in ["PASS", "PARTIAL"] else 1)
