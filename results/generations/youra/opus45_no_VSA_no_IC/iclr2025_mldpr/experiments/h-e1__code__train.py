"""Training, feature extraction, and linear probe for H-E1."""
import json
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

import numpy as np
import torch
import torch.nn as nn
from torch.optim import SGD
from torch.optim.lr_scheduler import CosineAnnealingLR
from tqdm import tqdm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, GroupKFold
from sklearn.metrics import confusion_matrix
from scipy import stats
import matplotlib.pyplot as plt

from config import Config, set_seed
from data import build_dataloader, DATASET_NUM_CLASSES
from model import FeatureResNet50


def finetune_one(benchmark: str, seed: int, cfg: Config, device: torch.device) -> str:
    """Fine-tune ResNet-50 on one benchmark with one seed."""
    set_seed(seed)
    num_classes = DATASET_NUM_CLASSES[benchmark]
    model = FeatureResNet50(num_classes, pretrained=cfg.pretrained).to(device)

    train_loader = build_dataloader(benchmark, cfg.data_root, train=True,
                                    batch_size=cfg.batch_size, num_workers=cfg.num_workers)
    val_loader = build_dataloader(benchmark, cfg.data_root, train=False,
                                  batch_size=cfg.batch_size, num_workers=cfg.num_workers)

    optimizer = SGD(model.parameters(), lr=cfg.lr, momentum=cfg.momentum,
                    weight_decay=cfg.weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=cfg.epochs)
    criterion = nn.CrossEntropyLoss()

    best_acc = 0.0
    ckpt_path = Path(cfg.ckpt_dir) / f"{benchmark}_seed{seed}.pt"

    for epoch in range(cfg.epochs):
        model.train()
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
        scheduler.step()

        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                pred = model(x).argmax(1)
                correct += (pred == y).sum().item()
                total += y.size(0)
        acc = correct / total
        if acc > best_acc:
            best_acc = acc
            torch.save({
                "state_dict": model.state_dict(),
                "benchmark": benchmark,
                "seed": seed,
                "acc": acc,
                "epoch": epoch,
            }, ckpt_path)

    print(f"[{benchmark}][seed={seed}] Best val acc: {best_acc:.4f}")
    return str(ckpt_path)


def run_all_finetuning(cfg: Config, device: torch.device) -> List[str]:
    """Fine-tune 15 models (5 benchmarks x 3 seeds)."""
    ckpt_paths = []
    for benchmark in cfg.benchmarks:
        for seed in cfg.seeds:
            ckpt_path = Path(cfg.ckpt_dir) / f"{benchmark}_seed{seed}.pt"
            if ckpt_path.exists():
                print(f"[SKIP] {ckpt_path} exists")
                ckpt_paths.append(str(ckpt_path))
            else:
                path = finetune_one(benchmark, seed, cfg, device)
                ckpt_paths.append(path)
    return ckpt_paths


def extract_all_features(ckpt_paths: List[str], cfg: Config,
                         device: torch.device) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract features from all models on NABirds test set.

    Returns:
        features: [N_total, 2048]
        labels: [N_total] benchmark index (0-4)
        model_ids: [N_total] model index (0-14)
    """
    all_features = []
    all_labels = []
    all_model_ids = []

    benchmark_to_idx = {b: i for i, b in enumerate(cfg.benchmarks)}
    probe_loader = build_dataloader(cfg.probe_dataset, cfg.data_root, train=False,
                                    batch_size=cfg.batch_size, num_workers=cfg.num_workers)

    for model_idx, ckpt_path in enumerate(tqdm(ckpt_paths, desc="Extracting features")):
        ckpt = torch.load(ckpt_path, map_location=device)
        benchmark = ckpt["benchmark"]
        benchmark_idx = benchmark_to_idx[benchmark]
        num_classes = DATASET_NUM_CLASSES[benchmark]

        model = FeatureResNet50(num_classes, pretrained=False).to(device)
        model.load_state_dict(ckpt["state_dict"])
        model.eval()

        with torch.no_grad():
            for x, _ in probe_loader:
                x = x.to(device)
                feats = model.extract_features(x)
                all_features.append(feats.cpu().numpy())
                all_labels.extend([benchmark_idx] * x.size(0))
                all_model_ids.extend([model_idx] * x.size(0))

    features = np.vstack(all_features)
    labels = np.array(all_labels)
    model_ids = np.array(all_model_ids)
    return features, labels, model_ids


def train_linear_probe(features: np.ndarray, labels: np.ndarray,
                       model_ids: np.ndarray, cfg: Config) -> Dict:
    """Train linear probe with model-level splits and statistical analysis."""
    unique_models = np.unique(model_ids)
    n_models = len(unique_models)
    np.random.shuffle(unique_models)

    n_train = int(n_models * cfg.train_split)
    n_val = int(n_models * cfg.val_split)

    train_models = set(unique_models[:n_train])
    val_models = set(unique_models[n_train:n_train + n_val])
    test_models = set(unique_models[n_train + n_val:])

    train_mask = np.isin(model_ids, list(train_models))
    val_mask = np.isin(model_ids, list(val_models))
    test_mask = np.isin(model_ids, list(test_models))

    X_train, y_train = features[train_mask], labels[train_mask]
    X_val, y_val = features[val_mask], labels[val_mask]
    X_test, y_test = features[test_mask], labels[test_mask]

    clf = LogisticRegression(C=cfg.probe_C, max_iter=cfg.probe_max_iter, n_jobs=-1)

    groups = model_ids[train_mask]
    gkf = GroupKFold(n_splits=min(cfg.cv_folds, len(train_models)))
    cv_scores = cross_val_score(clf, X_train, y_train, cv=gkf, groups=groups)

    clf.fit(X_train, y_train)
    val_acc = clf.score(X_val, y_val)
    test_acc = clf.score(X_test, y_test)

    boot_accs = []
    for _ in range(cfg.bootstrap_resamples):
        idx = np.random.choice(len(X_test), len(X_test), replace=True)
        boot_accs.append(clf.score(X_test[idx], y_test[idx]))
    boot_accs = np.array(boot_accs)
    ci_low, ci_high = np.percentile(boot_accs, [2.5, 97.5])

    t_stat, p_value = stats.ttest_1samp(boot_accs, cfg.chance_accuracy)
    cohens_d = (np.mean(boot_accs) - cfg.chance_accuracy) / np.std(boot_accs)

    y_pred = clf.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)

    return {
        "cv_scores": cv_scores.tolist(),
        "cv_mean": float(np.mean(cv_scores)),
        "val_acc": float(val_acc),
        "test_acc": float(test_acc),
        "ci_95": [float(ci_low), float(ci_high)],
        "p_value": float(p_value),
        "t_stat": float(t_stat),
        "cohens_d": float(cohens_d),
        "confusion_matrix": cm.tolist(),
        "n_train": int(len(X_train)),
        "n_val": int(len(X_val)),
        "n_test": int(len(X_test)),
    }


def run_baselines(features: np.ndarray, labels: np.ndarray,
                  model_ids: np.ndarray, cfg: Config, device: torch.device) -> Dict:
    """Run baseline experiments."""
    results = {}

    shuffled_labels = labels.copy()
    np.random.shuffle(shuffled_labels)
    results["shuffled_labels"] = train_linear_probe(features, shuffled_labels, model_ids, cfg)

    random_model = FeatureResNet50(1000, pretrained=False).to(device)
    random_model.eval()
    probe_loader = build_dataloader(cfg.probe_dataset, cfg.data_root, train=False,
                                    batch_size=cfg.batch_size, num_workers=cfg.num_workers)
    random_feats = []
    with torch.no_grad():
        for x, _ in probe_loader:
            x = x.to(device)
            f = random_model.extract_features(x)
            random_feats.append(f.cpu().numpy())
    random_features = np.vstack(random_feats)

    n_samples = features.shape[0]
    n_random = random_features.shape[0]
    if n_random < n_samples:
        repeats = (n_samples // n_random) + 1
        random_features = np.tile(random_features, (repeats, 1))[:n_samples]

    results["random_init"] = train_linear_probe(random_features, labels, model_ids, cfg)
    return results


def plot_confusion_matrix(cm: np.ndarray, labels: List[str], save_path: str):
    """Plot and save confusion matrix."""
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title("Benchmark Fingerprint Confusion Matrix")
    plt.colorbar()
    tick_marks = np.arange(len(labels))
    plt.xticks(tick_marks, labels, rotation=45, ha="right")
    plt.yticks(tick_marks, labels)

    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, f"{cm[i, j]}\n({cm_norm[i, j]:.2f})",
                     ha="center", va="center",
                     color="white" if cm_norm[i, j] > 0.5 else "black")

    plt.ylabel("True Benchmark")
    plt.xlabel("Predicted Benchmark")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def main(cfg: Config = None):
    """Main experiment pipeline."""
    if cfg is None:
        cfg = Config()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    print("\n=== Phase 1: Fine-tuning ===")
    ckpt_paths = run_all_finetuning(cfg, device)

    print("\n=== Phase 2: Feature Extraction ===")
    features, labels, model_ids = extract_all_features(ckpt_paths, cfg, device)
    print(f"Features shape: {features.shape}, Labels shape: {labels.shape}")

    np.save(Path(cfg.feature_dir) / "features.npy", features)
    np.save(Path(cfg.feature_dir) / "labels.npy", labels)
    np.save(Path(cfg.feature_dir) / "model_ids.npy", model_ids)

    print("\n=== Phase 3: Linear Probe ===")
    probe_results = train_linear_probe(features, labels, model_ids, cfg)
    print(f"Test Accuracy: {probe_results['test_acc']:.4f}")
    print(f"95% CI: [{probe_results['ci_95'][0]:.4f}, {probe_results['ci_95'][1]:.4f}]")
    print(f"p-value (vs chance): {probe_results['p_value']:.2e}")
    print(f"Cohen's d: {probe_results['cohens_d']:.4f}")

    print("\n=== Phase 4: Baselines ===")
    baseline_results = run_baselines(features, labels, model_ids, cfg, device)
    print(f"Shuffled labels acc: {baseline_results['shuffled_labels']['test_acc']:.4f}")
    print(f"Random init acc: {baseline_results['random_init']['test_acc']:.4f}")

    results = {
        "probe": probe_results,
        "baselines": baseline_results,
        "config": {
            "benchmarks": cfg.benchmarks,
            "seeds": cfg.seeds,
            "epochs": cfg.epochs,
            "probe_dataset": cfg.probe_dataset,
        }
    }

    with open(cfg.results_path, "w") as f:
        json.dump(results, f, indent=2)

    plot_confusion_matrix(
        np.array(probe_results["confusion_matrix"]),
        cfg.benchmarks,
        cfg.figure_path
    )

    print(f"\n=== Results saved to {cfg.results_path} ===")
    print(f"=== Figure saved to {cfg.figure_path} ===")

    passed = probe_results["test_acc"] > 0.60
    print(f"\n=== GATE CHECK: {'PASS' if passed else 'FAIL'} ===")
    print(f"Accuracy {probe_results['test_acc']:.4f} {'>' if passed else '<='} 0.60 threshold")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root", type=str, default="./data")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch_size", type=int, default=32)
    args = parser.parse_args()

    cfg = Config(data_root=args.data_root, epochs=args.epochs, batch_size=args.batch_size)
    main(cfg)
