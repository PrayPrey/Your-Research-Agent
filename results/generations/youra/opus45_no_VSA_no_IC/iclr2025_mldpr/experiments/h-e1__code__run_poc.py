#!/usr/bin/env python
"""
H-E1 PoC Experiment - Validates methodology with available torchvision datasets.

Uses 3 fine-grained datasets (Flowers102, Aircraft, CIFAR-100 as proxy) to test
if benchmark fingerprints are detectable. If >50% accuracy (chance=33%), methodology works.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

import numpy as np
import torch
import torch.nn as nn
from torch.optim import SGD
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms, models
from tqdm import tqdm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


@dataclass
class Config:
    benchmarks: list = field(default_factory=lambda: ["flowers", "aircraft", "cifar100"])
    seeds: list = field(default_factory=lambda: [0, 1, 2])
    epochs: int = 15
    lr: float = 0.01
    batch_size: int = 64
    weight_decay: float = 1e-4
    momentum: float = 0.9
    feature_dim: int = 2048
    data_root: str = "./data"
    num_workers: int = 4
    probe_C: float = 1.0
    bootstrap_resamples: int = 500
    ckpt_dir: str = "./models/finetuned"
    feature_dir: str = "./features"
    results_path: str = "./results/h_e1_results.json"
    figure_path: str = "./figures/confusion_matrix.png"

    def __post_init__(self):
        for d in [self.ckpt_dir, self.feature_dir,
                  str(Path(self.results_path).parent),
                  str(Path(self.figure_path).parent)]:
            Path(d).mkdir(parents=True, exist_ok=True)


def set_seed(seed: int):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True


DATASET_NUM_CLASSES = {"flowers": 102, "aircraft": 100, "cifar100": 100}


def get_transforms(train: bool, dataset: str = None) -> transforms.Compose:
    normalize = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    if train:
        return transforms.Compose([
            transforms.Resize(256),
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            normalize,
        ])
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        normalize,
    ])


def build_dataset(name: str, root: str, train: bool):
    transform = get_transforms(train, name)
    if name == "flowers":
        return datasets.Flowers102(root, split="train" if train else "test",
                                   transform=transform, download=True)
    elif name == "aircraft":
        return datasets.FGVCAircraft(root, split="train" if train else "test",
                                     transform=transform, download=True)
    elif name == "cifar100":
        ds = datasets.CIFAR100(root, train=train, transform=transform, download=True)
        return ds
    raise ValueError(f"Unknown dataset: {name}")


def build_dataloader(name: str, root: str, train: bool, batch_size: int,
                     num_workers: int = 4, max_samples: int = None) -> DataLoader:
    dataset = build_dataset(name, root, train)
    if max_samples and len(dataset) > max_samples:
        indices = np.random.choice(len(dataset), max_samples, replace=False)
        dataset = Subset(dataset, indices)
    return DataLoader(dataset, batch_size=batch_size, shuffle=train,
                      num_workers=num_workers, pin_memory=True, drop_last=train)


class FeatureResNet50(nn.Module):
    def __init__(self, num_classes: int, pretrained: bool = True):
        super().__init__()
        weights = models.ResNet50_Weights.IMAGENET1K_V1 if pretrained else None
        self.backbone = models.resnet50(weights=weights)
        self.backbone.fc = nn.Linear(2048, num_classes)

    def forward(self, x):
        return self.backbone(x)

    def extract_features(self, x):
        m = self.backbone
        x = m.conv1(x)
        x = m.bn1(x)
        x = m.relu(x)
        x = m.maxpool(x)
        x = m.layer1(x)
        x = m.layer2(x)
        x = m.layer3(x)
        x = m.layer4(x)
        x = m.avgpool(x)
        return torch.flatten(x, 1)


def finetune_one(benchmark: str, seed: int, cfg: Config, device: torch.device) -> str:
    set_seed(seed)
    num_classes = DATASET_NUM_CLASSES[benchmark]
    model = FeatureResNet50(num_classes, pretrained=True).to(device)

    train_loader = build_dataloader(benchmark, cfg.data_root, train=True,
                                    batch_size=cfg.batch_size, num_workers=cfg.num_workers)
    val_loader = build_dataloader(benchmark, cfg.data_root, train=False,
                                  batch_size=cfg.batch_size, num_workers=cfg.num_workers)

    optimizer = SGD(model.parameters(), lr=cfg.lr, momentum=cfg.momentum,
                    weight_decay=cfg.weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=cfg.epochs)
    criterion = nn.CrossEntropyLoss()

    ckpt_path = Path(cfg.ckpt_dir) / f"{benchmark}_seed{seed}.pt"
    best_acc = 0.0

    for epoch in range(cfg.epochs):
        model.train()
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
        scheduler.step()

        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                correct += (model(x).argmax(1) == y).sum().item()
                total += y.size(0)
        acc = correct / total
        if acc > best_acc:
            best_acc = acc
            torch.save({"state_dict": model.state_dict(), "benchmark": benchmark,
                        "seed": seed, "acc": acc}, ckpt_path)

    print(f"[{benchmark}][seed={seed}] Best val acc: {best_acc:.4f}")
    return str(ckpt_path)


def run_all_finetuning(cfg: Config, device: torch.device) -> List[str]:
    paths = []
    for benchmark in cfg.benchmarks:
        for seed in cfg.seeds:
            ckpt = Path(cfg.ckpt_dir) / f"{benchmark}_seed{seed}.pt"
            if ckpt.exists():
                print(f"[SKIP] {ckpt} exists")
                paths.append(str(ckpt))
            else:
                paths.append(finetune_one(benchmark, seed, cfg, device))
    return paths


def extract_all_features(ckpt_paths: List[str], cfg: Config, device: torch.device,
                         probe_dataset: str = "cifar100") -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract features from all models on held-out test set."""
    all_features, all_labels, all_model_ids = [], [], []
    benchmark_to_idx = {b: i for i, b in enumerate(cfg.benchmarks)}

    probe_loader = build_dataloader(probe_dataset, cfg.data_root, train=False,
                                    batch_size=cfg.batch_size, num_workers=cfg.num_workers,
                                    max_samples=5000)

    for model_idx, ckpt_path in enumerate(tqdm(ckpt_paths, desc="Extracting features")):
        ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
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

    return np.vstack(all_features), np.array(all_labels), np.array(all_model_ids)


def train_linear_probe(features: np.ndarray, labels: np.ndarray,
                       model_ids: np.ndarray, cfg: Config) -> Dict:
    unique_models = np.unique(model_ids)
    n_models = len(unique_models)
    np.random.shuffle(unique_models)

    n_train = max(1, int(n_models * 0.7))
    train_models = set(unique_models[:n_train])
    test_models = set(unique_models[n_train:])

    train_mask = np.isin(model_ids, list(train_models))
    test_mask = np.isin(model_ids, list(test_models))

    X_train, y_train = features[train_mask], labels[train_mask]
    X_test, y_test = features[test_mask], labels[test_mask]

    clf = LogisticRegression(C=cfg.probe_C, max_iter=1000, n_jobs=-1)
    clf.fit(X_train, y_train)
    test_acc = clf.score(X_test, y_test)

    boot_accs = []
    for _ in range(cfg.bootstrap_resamples):
        idx = np.random.choice(len(X_test), len(X_test), replace=True)
        boot_accs.append(clf.score(X_test[idx], y_test[idx]))
    boot_accs = np.array(boot_accs)
    ci_low, ci_high = np.percentile(boot_accs, [2.5, 97.5])

    chance = 1.0 / len(cfg.benchmarks)
    t_stat, p_value = stats.ttest_1samp(boot_accs, chance)
    cohens_d = (np.mean(boot_accs) - chance) / np.std(boot_accs)

    y_pred = clf.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)

    return {
        "test_acc": float(test_acc),
        "ci_95": [float(ci_low), float(ci_high)],
        "p_value": float(p_value),
        "t_stat": float(t_stat),
        "cohens_d": float(cohens_d),
        "confusion_matrix": cm.tolist(),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "chance_level": float(chance),
    }


def run_baselines(features: np.ndarray, labels: np.ndarray,
                  model_ids: np.ndarray, cfg: Config) -> Dict:
    shuffled = labels.copy()
    np.random.shuffle(shuffled)
    return {"shuffled_labels": train_linear_probe(features, shuffled, model_ids, cfg)}


def plot_confusion_matrix(cm: np.ndarray, labels: List[str], save_path: str):
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title("Benchmark Fingerprint Confusion Matrix")
    plt.colorbar()
    tick_marks = np.arange(len(labels))
    plt.xticks(tick_marks, labels, rotation=45, ha="right")
    plt.yticks(tick_marks, labels)

    cm_norm = cm.astype("float") / (cm.sum(axis=1, keepdims=True) + 1e-8)
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


def main():
    cfg = Config()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(f"Benchmarks: {cfg.benchmarks}")
    print(f"Seeds: {cfg.seeds} ({len(cfg.benchmarks) * len(cfg.seeds)} models)")

    print("\n=== Phase 1: Fine-tuning ===")
    ckpt_paths = run_all_finetuning(cfg, device)

    print("\n=== Phase 2: Feature Extraction ===")
    features, labels, model_ids = extract_all_features(ckpt_paths, cfg, device)
    print(f"Features: {features.shape}, Labels: {labels.shape}")

    np.save(Path(cfg.feature_dir) / "features.npy", features)
    np.save(Path(cfg.feature_dir) / "labels.npy", labels)
    np.save(Path(cfg.feature_dir) / "model_ids.npy", model_ids)

    print("\n=== Phase 3: Linear Probe ===")
    probe_results = train_linear_probe(features, labels, model_ids, cfg)
    print(f"Test Accuracy: {probe_results['test_acc']:.4f}")
    print(f"95% CI: [{probe_results['ci_95'][0]:.4f}, {probe_results['ci_95'][1]:.4f}]")
    print(f"Chance level: {probe_results['chance_level']:.4f}")
    print(f"p-value (vs chance): {probe_results['p_value']:.2e}")
    print(f"Cohen's d: {probe_results['cohens_d']:.4f}")

    print("\n=== Phase 4: Baselines ===")
    baseline_results = run_baselines(features, labels, model_ids, cfg)
    print(f"Shuffled labels acc: {baseline_results['shuffled_labels']['test_acc']:.4f}")

    results = {
        "probe": probe_results,
        "baselines": baseline_results,
        "config": {"benchmarks": cfg.benchmarks, "seeds": cfg.seeds, "epochs": cfg.epochs}
    }

    with open(cfg.results_path, "w") as f:
        json.dump(results, f, indent=2)

    plot_confusion_matrix(np.array(probe_results["confusion_matrix"]),
                          cfg.benchmarks, cfg.figure_path)

    print(f"\nResults saved: {cfg.results_path}")
    print(f"Figure saved: {cfg.figure_path}")

    threshold = 0.50
    passed = probe_results["test_acc"] > threshold
    print(f"\n{'='*50}")
    print(f"GATE CHECK: {'PASS' if passed else 'FAIL'}")
    print(f"Accuracy {probe_results['test_acc']:.4f} {'>' if passed else '<='} {threshold} threshold")
    print(f"(Note: PoC uses 3 benchmarks, full experiment uses 5)")
    print(f"{'='*50}")

    return results, passed


if __name__ == "__main__":
    results, passed = main()
    sys.exit(0 if passed else 1)
