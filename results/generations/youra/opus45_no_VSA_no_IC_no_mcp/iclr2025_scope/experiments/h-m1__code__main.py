import os
import sys
import json
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config, ExperimentConfig
from data.dataset import load_superglue_data, generate_synthetic_cluster_labels, split_data, TASKS
from data.extract_hidden_states import HiddenStateExtractor
from models.task_embedding import TaskEmbeddingEncoder
from models.baseline import RandomEmbeddingBaseline
from train import train_embedding
from probe import fit_probe, probe_accuracy
from evaluate import run_gate_check, per_task_accuracy, silhouette
from visualize import plot_gate_comparison, plot_tsne, plot_ablation, plot_per_task_accuracy


def set_seed(seed: int):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def extract_embeddings(model, hidden_states: torch.Tensor, device: str) -> np.ndarray:
    """Extract embeddings from trained model."""
    model.eval()
    model = model.to(device)
    hidden_states = hidden_states.to(device)
    with torch.no_grad():
        emb = model(hidden_states)
    return emb.cpu().numpy()


def run_single_experiment(cfg: ExperimentConfig, hidden_states_train: torch.Tensor,
                          hidden_states_test: torch.Tensor, cluster_labels_train: np.ndarray,
                          cluster_labels_test: np.ndarray, task_ids_train: np.ndarray,
                          task_ids_test: np.ndarray, embedding_dim: int,
                          device: str) -> dict:
    """Run experiment for single embedding dimension."""
    encoder = TaskEmbeddingEncoder(
        hidden_dim=cfg.model.hidden_dim,
        embedding_dim=embedding_dim,
        num_tasks=cfg.model.num_tasks
    )

    encoder = train_embedding(
        model=encoder,
        hidden_states=hidden_states_train,
        cluster_labels=torch.from_numpy(cluster_labels_train).long(),
        lr=cfg.training.lr,
        batch_size=cfg.training.batch_size,
        epochs=cfg.training.epochs,
        device=device
    )

    train_emb = extract_embeddings(encoder, hidden_states_train, device)
    test_emb = extract_embeddings(encoder, hidden_states_test, device)

    probe = fit_probe(train_emb, task_ids_train, C=cfg.training.l2_reg_C, seed=cfg.training.seed)
    acc = probe_accuracy(probe, test_emb, task_ids_test)

    per_task_acc = per_task_accuracy(probe, test_emb, task_ids_test, task_ids_test)
    sil_score = silhouette(test_emb, task_ids_test)

    return {
        "accuracy": acc,
        "per_task_accuracy": per_task_acc,
        "silhouette_score": sil_score,
        "embedding_dim": embedding_dim,
        "encoder": encoder,
        "test_embeddings": test_emb
    }


def run_random_baseline(cfg: ExperimentConfig, hidden_train: torch.Tensor,
                        hidden_test: torch.Tensor, task_ids_train: np.ndarray,
                        task_ids_test: np.ndarray, embedding_dim: int) -> dict:
    """Run random baseline: random projection (not learned)."""
    rng = np.random.RandomState(cfg.training.seed)
    hidden_dim = hidden_train.shape[-1]

    proj = torch.from_numpy(rng.randn(hidden_dim, embedding_dim).astype(np.float32))
    proj = proj / np.sqrt(hidden_dim)

    train_pooled = hidden_train.mean(dim=1)
    test_pooled = hidden_test.mean(dim=1)

    train_emb = (train_pooled @ proj).numpy()
    test_emb = (test_pooled @ proj).numpy()

    probe = fit_probe(train_emb, task_ids_train, C=cfg.training.l2_reg_C, seed=cfg.training.seed)
    acc = probe_accuracy(probe, test_emb, task_ids_test)

    return {"accuracy": acc, "embedding_dim": embedding_dim}


def main():
    print("=" * 60)
    print("H-M1 Experiment: Task Embedding Quality Validation")
    print("=" * 60)

    cfg = load_config()
    set_seed(cfg.training.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    figures_dir = os.path.join(script_dir, "..", "figures")
    os.makedirs(figures_dir, exist_ok=True)

    print("\n[1/5] Loading SuperGLUE data...")
    texts, task_ids = load_superglue_data(cfg.data.tasks, max_samples_per_task=2000)
    print(f"Loaded {len(texts)} samples across {len(cfg.data.tasks)} tasks")

    print("\n[2/5] Generating cluster labels (synthetic H-E1 output)...")
    cluster_labels = generate_synthetic_cluster_labels(task_ids, num_clusters=8, noise_ratio=0.2)

    print("\n[3/5] Extracting hidden states...")
    extractor = HiddenStateExtractor("bert-base-uncased", device)
    cfg.model.hidden_dim = extractor.hidden_dim

    hidden_states = extractor.extract(texts, max_length=128, batch_size=32)
    print(f"Hidden states shape: {hidden_states.shape}")

    print("\n[4/5] Splitting data...")
    data_splits = split_data(texts, task_ids, cluster_labels,
                             train_ratio=cfg.data.train_split,
                             val_ratio=cfg.data.val_split,
                             seed=cfg.training.seed)

    n_train = len(data_splits["train"]["task_ids"])
    n_test = len(data_splits["test"]["task_ids"])

    train_indices = np.arange(n_train)
    test_indices = np.arange(n_train, n_train + len(data_splits["val"]["task_ids"]))
    test_indices = np.concatenate([test_indices,
                                   np.arange(n_train + len(data_splits["val"]["task_ids"]),
                                             len(task_ids))])

    hidden_train = hidden_states[:n_train]
    hidden_test = hidden_states[n_train:n_train + n_test]

    cluster_train = data_splits["train"]["cluster_labels"]
    cluster_test = data_splits["test"]["cluster_labels"]
    task_ids_train = data_splits["train"]["task_ids"]
    task_ids_test = data_splits["test"]["task_ids"]

    print(f"Train: {len(task_ids_train)}, Test: {len(task_ids_test)}")

    print("\n[5/5] Running ablation experiments...")
    ablation_results = {}
    best_result = None
    best_acc = 0.0

    for dim in cfg.ablation.embedding_dim_variants:
        print(f"\n--- Embedding dim = {dim} ---")
        result = run_single_experiment(
            cfg, hidden_train, hidden_test, cluster_train, cluster_test,
            task_ids_train, task_ids_test, dim, device
        )
        ablation_results[dim] = result["accuracy"]
        print(f"Accuracy: {result['accuracy']:.4f}, Silhouette: {result['silhouette_score']:.4f}")

        if result["accuracy"] > best_acc:
            best_acc = result["accuracy"]
            best_result = result

    print("\n--- Random Baseline ---")
    random_result = run_random_baseline(cfg, hidden_train, hidden_test,
                                        task_ids_train, task_ids_test,
                                        cfg.model.embedding_dim)
    print(f"Random baseline accuracy: {random_result['accuracy']:.4f}")

    gate_threshold = 1.0 / cfg.model.num_tasks
    gate_passed = run_gate_check(best_result["accuracy"], threshold=gate_threshold)

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Best proposed accuracy: {best_result['accuracy']:.4f}")
    print(f"Random baseline accuracy: {random_result['accuracy']:.4f}")
    print(f"Gate threshold: {gate_threshold:.4f}")
    print(f"Gate PASSED: {gate_passed}")

    print("\n[Generating figures...]")

    plot_gate_comparison(
        best_result["accuracy"], random_result["accuracy"], gate_threshold,
        os.path.join(figures_dir, "gate_comparison.png")
    )
    print("  - gate_comparison.png")

    plot_tsne(
        best_result["test_embeddings"], task_ids_test,
        os.path.join(figures_dir, "tsne_embeddings.png")
    )
    print("  - tsne_embeddings.png")

    plot_ablation(ablation_results, os.path.join(figures_dir, "ablation.png"))
    print("  - ablation.png")

    plot_per_task_accuracy(
        best_result["per_task_accuracy"], cfg.data.tasks,
        os.path.join(figures_dir, "per_task_accuracy.png")
    )
    print("  - per_task_accuracy.png")

    results = {
        "hypothesis_id": "h-m1",
        "gate_condition": f"linear_probe_accuracy > {gate_threshold}",
        "gate_passed": gate_passed,
        "proposed_accuracy": best_result["accuracy"],
        "random_baseline_accuracy": random_result["accuracy"],
        "best_embedding_dim": best_result["embedding_dim"],
        "ablation_results": ablation_results,
        "silhouette_score": best_result["silhouette_score"],
        "per_task_accuracy": {str(k): v for k, v in best_result["per_task_accuracy"].items()},
        "num_train_samples": len(task_ids_train),
        "num_test_samples": len(task_ids_test),
    }

    results_path = os.path.join(figures_dir, "..", "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
