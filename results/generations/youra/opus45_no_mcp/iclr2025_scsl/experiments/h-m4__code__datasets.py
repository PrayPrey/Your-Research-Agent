"""H-M4 Datasets: WILDS Waterbirds/CelebA + ColoredMNIST loaders with WGA computation"""
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path

try:
    from wilds import get_dataset
    from wilds.common.data_loaders import get_train_loader, get_eval_loader
    WILDS_AVAILABLE = True
except ImportError:
    WILDS_AVAILABLE = False

from torchvision import transforms
import torchvision.datasets as tv_datasets

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

_dataset_cache = {}


def get_train_transform(image_size: int = 224):
    if image_size == 32:
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_eval_transform(image_size: int = 224):
    if image_size == 32:
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_waterbirds_loaders(config, seed: int = 0):
    if not WILDS_AVAILABLE:
        raise ImportError("wilds package required: pip install wilds")
    root_dir = config.data_root
    if root_dir not in _dataset_cache:
        _dataset_cache[root_dir] = get_dataset(dataset="waterbirds", download=True, root_dir=root_dir)
    dataset = _dataset_cache[root_dir]
    train_data = dataset.get_subset("train", transform=get_train_transform(224))
    val_data = dataset.get_subset("val", transform=get_eval_transform(224))
    train_loader = get_train_loader("standard", train_data, batch_size=config.batch_size, num_workers=4)
    val_loader = get_eval_loader("standard", val_data, batch_size=config.batch_size, num_workers=4)
    return train_loader, val_loader


def get_celeba_loaders(config, seed: int = 0):
    if not WILDS_AVAILABLE:
        raise ImportError("wilds package required: pip install wilds")
    root_dir = config.data_root
    cache_key = f"{root_dir}_celeba"
    if cache_key not in _dataset_cache:
        _dataset_cache[cache_key] = get_dataset(dataset="celebA", download=True, root_dir=root_dir)
    dataset = _dataset_cache[cache_key]
    train_data = dataset.get_subset("train", transform=get_train_transform(224))
    val_data = dataset.get_subset("val", transform=get_eval_transform(224))
    train_loader = get_train_loader("standard", train_data, batch_size=config.batch_size)
    val_loader = get_eval_loader("standard", val_data, batch_size=config.batch_size)
    return train_loader, val_loader


def construct_colored_mnist(correlation: float = 0.95, root: str = "./data", train: bool = True, seed: int = 0):
    """Construct ColoredMNIST with spurious color correlation."""
    np.random.seed(seed)
    mnist = tv_datasets.MNIST(root=root, train=train, download=True)
    images = mnist.data.numpy()
    labels = mnist.targets.numpy()
    n = len(labels)

    spurious_color = np.zeros(n, dtype=np.int64)
    for i in range(n):
        if np.random.rand() < correlation:
            spurious_color[i] = labels[i] % 2
        else:
            spurious_color[i] = 1 - (labels[i] % 2)

    colored_images = np.zeros((n, 3, 32, 32), dtype=np.float32)
    for i in range(n):
        img = images[i].astype(np.float32) / 255.0
        img_resized = np.zeros((32, 32), dtype=np.float32)
        img_resized[2:30, 2:30] = np.array(
            [[img[max(0, min(27, int(y * 28 / 28))), max(0, min(27, int(x * 28 / 28)))]
              for x in range(28)] for y in range(28)]
        )
        if spurious_color[i] == 0:
            colored_images[i, 0] = img_resized
        else:
            colored_images[i, 2] = img_resized

    groups = labels * 2 + spurious_color
    return TensorDataset(
        torch.from_numpy(colored_images),
        torch.from_numpy(labels),
        torch.from_numpy(groups)
    )


def get_coloredmnist_loaders(config, seed: int = 0):
    train_ds = construct_colored_mnist(correlation=0.95, root=config.data_root, train=True, seed=seed)
    val_ds = construct_colored_mnist(correlation=0.95, root=config.data_root, train=False, seed=seed)
    train_loader = DataLoader(train_ds, batch_size=config.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_ds, batch_size=config.batch_size, shuffle=False, num_workers=2)
    return train_loader, val_loader


def get_loaders(benchmark: str, config, seed: int = 0):
    if benchmark == "waterbirds":
        return get_waterbirds_loaders(config, seed)
    elif benchmark == "celeba":
        return get_celeba_loaders(config, seed)
    elif benchmark == "coloredmnist":
        return get_coloredmnist_loaders(config, seed)
    else:
        raise ValueError(f"Unknown benchmark: {benchmark}")


@torch.no_grad()
def compute_wga(model: nn.Module, val_loader: DataLoader, device: torch.device) -> float:
    """Compute worst-group accuracy."""
    model.eval()
    all_preds, all_labels, all_groups = [], [], []
    for batch in val_loader:
        x, y = batch[0], batch[1]
        meta = batch[2]
        # WILDS: metadata is [N, 3] with group_id in last column
        # ColoredMNIST TensorDataset: already 1D groups
        if meta.dim() > 1:
            groups = meta[:, -1]  # group_id is last column in WILDS
        else:
            groups = meta
        x = x.to(device)
        logits = model(x)
        preds = logits.argmax(dim=1).cpu()
        all_preds.append(preds)
        all_labels.append(y)
        all_groups.append(groups)

    preds = torch.cat(all_preds)
    labels = torch.cat(all_labels)
    groups = torch.cat(all_groups)

    unique_groups = torch.unique(groups)
    group_accs = []
    for g in unique_groups:
        mask = groups == g
        if mask.sum() > 0:
            acc = (preds[mask] == labels[mask]).float().mean().item()
            group_accs.append(acc)
    return min(group_accs) if group_accs else 0.0
