"""
Dataset loaders for CNN Zoo and Transformer Zoo checkpoints.
CNN Zoo: Ray Tune checkpoint format from HSG-AIML/MultiZoo-SANE (cifar10_cnn_sample_ep21-25)
Transformer Zoo: pt files from MathematicalAI-NUS/Transformer-NFN (MNIST + AG-News splits)
"""
import os
import glob
import json
import csv
import copy
from typing import Any, Dict, List, Optional

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


# ─────────────────────────────────────────────────────────────────────────────
# CNN Zoo
# ─────────────────────────────────────────────────────────────────────────────

class SimpleCNN(nn.Module):
    """Minimal CNN model matching the CNN Zoo architecture (CNN3 from zoo)."""
    def __init__(self, channels_in=3, o_dim=10, nlin="gelu", use_bias=False):
        super().__init__()
        nlin_fn = {"gelu": nn.GELU, "relu": nn.ReLU, "tanh": nn.Tanh}.get(nlin, nn.GELU)
        self.module_list = nn.Sequential(
            nn.Conv2d(channels_in, 32, 3, padding=1, bias=use_bias),
            nlin_fn(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1, bias=use_bias),
            nlin_fn(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1, bias=use_bias),
            nlin_fn(),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(128 * 4 * 4, 256, bias=use_bias) if channels_in == 3 else nn.Linear(128 * 3 * 3, 256, bias=use_bias),
            nlin_fn(),
            nn.Linear(256, o_dim, bias=use_bias),
        )

    def forward(self, x):
        return self.module_list(x)


def _load_cnn_checkpoint(model_dir: str) -> Optional[Dict]:
    """Load a single CNN checkpoint from its model directory (Ray Tune format)."""
    # Find the latest epoch checkpoint
    checkpoint_dirs = sorted(
        glob.glob(os.path.join(model_dir, "checkpoint_*")),
        key=lambda p: int(p.split("checkpoint_")[-1])
    )
    if not checkpoint_dirs:
        return None

    latest_dir = checkpoint_dirs[-1]
    ckpt_path = os.path.join(latest_dir, "checkpoints")
    if not os.path.exists(ckpt_path):
        return None

    try:
        state_dict = torch.load(ckpt_path, map_location="cpu", weights_only=True)
    except Exception:
        try:
            state_dict = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        except Exception:
            return None

    if not isinstance(state_dict, dict):
        return None

    # Extract val_acc from result.json
    result_path = os.path.join(model_dir, "result.json")
    val_acc = 0.0
    task = "cifar10"
    if os.path.exists(result_path):
        try:
            with open(result_path) as f:
                lines = f.readlines()
            # last line has the final epoch result
            last = json.loads(lines[-1])
            val_acc = last.get("test_acc", 0.0)
        except Exception:
            pass

    # Extract task from params.json
    params_path = os.path.join(model_dir, "params.json")
    if os.path.exists(params_path):
        try:
            with open(params_path) as f:
                params = json.load(f)
            dataset = params.get("dataset", "cifar10")
            if isinstance(dataset, str):
                task = dataset.lower()
        except Exception:
            pass

    checkpoint_id = os.path.basename(model_dir)
    return {
        "state_dict": state_dict,
        "val_acc": val_acc,
        "checkpoint_id": checkpoint_id,
        "task": task,
    }


class CNNZooLoader:
    def __init__(self, zoo_dir: str, n_checkpoints: int = 100, seed: int = 42):
        self.zoo_dir = zoo_dir
        self.n_checkpoints = n_checkpoints
        self.seed = seed

    def _sample_checkpoint_paths(self) -> List[str]:
        """Find all model directories and sample n_checkpoints."""
        # Each model is a directory containing checkpoint_* subdirs
        model_dirs = sorted([
            d for d in glob.glob(os.path.join(self.zoo_dir, "*"))
            if os.path.isdir(d) and "checkpoint_" not in d
        ])
        rng = np.random.default_rng(self.seed)
        n = min(self.n_checkpoints, len(model_dirs))
        indices = rng.choice(len(model_dirs), size=n, replace=False)
        return [model_dirs[i] for i in sorted(indices)]

    def load_checkpoints(self) -> List[Dict[str, Any]]:
        """Returns list of {state_dict, val_acc, checkpoint_id, task}."""
        paths = self._sample_checkpoint_paths()
        checkpoints = []
        for path in paths:
            result = _load_cnn_checkpoint(path)
            if result is not None:
                checkpoints.append(result)
        print(f"✓ CNNZooLoader: loaded {len(checkpoints)} checkpoints from {self.zoo_dir}")
        return checkpoints

    def get_val_loader(self, task: str = "cifar10", batch_size: int = 256) -> DataLoader:
        """Returns a real validation DataLoader for the given task."""
        import torchvision
        import torchvision.transforms as transforms

        data_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "torchvision")
        os.makedirs(data_root, exist_ok=True)

        if task in ("cifar10",):
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
            ])
            dataset = torchvision.datasets.CIFAR10(root=data_root, train=False, download=True, transform=transform)
        elif task == "svhn":
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
            ])
            dataset = torchvision.datasets.SVHN(root=data_root, split="test", download=True, transform=transform)
        elif task == "mnist":
            transform = transforms.Compose([
                transforms.Resize(32),
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,)),
            ])
            dataset = torchvision.datasets.MNIST(root=data_root, train=False, download=True, transform=transform)
        else:
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
            ])
            dataset = torchvision.datasets.CIFAR10(root=data_root, train=False, download=True, transform=transform)

        return DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)


# ─────────────────────────────────────────────────────────────────────────────
# Transformer Zoo
# ─────────────────────────────────────────────────────────────────────────────

class SimpleTransformer(nn.Module):
    """Minimal Transformer model matching Transformer Zoo (Transformer-NFN) architecture.

    Architecture from state dict: no LayerNorm, separate Q/K/V (no bias),
    MLP fc1/fc2 at block level, 2-layer MLP classifier.
    """
    def __init__(self, embed_dim=32, n_heads=2, n_layers=2, n_classes=10,
                 n_patches=49, patch_size=4, n_channels=1, forward_mul=2):
        super().__init__()
        self.embedding = SimpleEmbedding(n_channels, patch_size, embed_dim, n_patches)
        self.encoder = nn.ModuleList([
            SimpleTransformerBlock(embed_dim, n_heads, forward_mul)
            for _ in range(n_layers)
        ])
        self.classifier = SimpleClassifier(embed_dim, n_classes)

    def forward(self, x):
        x = self.embedding(x)
        for block in self.encoder:
            x = block(x)
        return self.classifier(x.mean(dim=1))


class SimpleEmbedding(nn.Module):
    def __init__(self, n_channels, patch_size, embed_dim, n_patches):
        super().__init__()
        self.conv1 = nn.Conv2d(n_channels, embed_dim, patch_size, stride=patch_size)
        self.pos_embedding = nn.Parameter(torch.zeros(n_patches, embed_dim))

    def forward(self, x):
        x = self.conv1(x)  # [B, embed_dim, H', W']
        B, C, H, W = x.shape
        x = x.view(B, C, H * W).transpose(1, 2)  # [B, n_patches, embed_dim]
        x = x + self.pos_embedding
        return x


class SimpleTransformerBlock(nn.Module):
    """Block matching Transformer-NFN: attention + fc1/fc2, no LayerNorm."""
    def __init__(self, embed_dim, n_heads, forward_mul=2):
        super().__init__()
        head_dim = embed_dim // n_heads
        self.attention = SeparateQKVAttention(embed_dim, n_heads, head_dim)
        self.fc1 = nn.Linear(embed_dim, embed_dim * forward_mul)
        self.fc2 = nn.Linear(embed_dim * forward_mul, embed_dim)
        self.act = nn.GELU()

    def forward(self, x):
        x = x + self.attention(x)
        x = x + self.fc2(self.act(self.fc1(x)))
        return x


class SimpleClassifier(nn.Module):
    """Two-layer MLP classifier matching zoo's classifier.fc1/fc2."""
    def __init__(self, embed_dim, n_classes):
        super().__init__()
        self.fc1 = nn.Linear(embed_dim, embed_dim)
        self.fc2 = nn.Linear(embed_dim, n_classes)

    def forward(self, x):
        return self.fc2(nn.functional.gelu(self.fc1(x)))


class SeparateQKVAttention(nn.Module):
    """Attention with separate Q/K/V projections (no bias) matching Transformer-NFN style."""
    def __init__(self, embed_dim, n_heads, head_dim):
        super().__init__()
        self.n_heads = n_heads
        self.head_dim = head_dim
        self.queries = nn.Linear(embed_dim, n_heads * head_dim, bias=False)
        self.keys = nn.Linear(embed_dim, n_heads * head_dim, bias=False)
        self.values = nn.Linear(embed_dim, n_heads * head_dim, bias=False)
        self.out_projection = nn.Linear(n_heads * head_dim, embed_dim, bias=False)
        self.scale = head_dim ** -0.5

    def forward(self, x):
        B, N, _ = x.shape
        q = self.queries(x).view(B, N, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.keys(x).view(B, N, self.n_heads, self.head_dim).transpose(1, 2)
        v = self.values(x).view(B, N, self.n_heads, self.head_dim).transpose(1, 2)
        attn = torch.softmax(q @ k.transpose(-2, -1) * self.scale, dim=-1)
        out = (attn @ v).transpose(1, 2).reshape(B, N, -1)
        return self.out_projection(out)


def _parse_val_acc_from_filename(fname: str) -> float:
    """Parse val_acc from filename like 'abc123_50_9458.pt' -> 0.9458."""
    stem = os.path.splitext(fname)[0]
    parts = stem.split("_")
    if len(parts) >= 3:
        try:
            acc_int = int(parts[-1])
            if acc_int > 100:  # encoded as e.g. 9458 -> 0.9458
                return acc_int / 10000.0
            return acc_int / 100.0
        except ValueError:
            pass
    return 0.0


class TransformerZooLoader:
    def __init__(
        self,
        mnist_dir: str,
        agnews_dir: str = None,
        n_mnist: int = 100,
        n_agnews: int = 0,
        seed: int = 42,
    ):
        self.mnist_dir = mnist_dir
        self.agnews_dir = agnews_dir
        self.n_mnist = n_mnist
        self.n_agnews = n_agnews
        self.seed = seed

    def _load_split(self, split_dir: str, n_samples: int, task: str) -> List[Dict]:
        if not split_dir or not os.path.exists(split_dir):
            return []
        pt_files = sorted(glob.glob(os.path.join(split_dir, "*.pt")))
        rng = np.random.default_rng(self.seed)
        n = min(n_samples, len(pt_files))
        indices = rng.choice(len(pt_files), size=n, replace=False)
        selected = [pt_files[i] for i in sorted(indices)]

        checkpoints = []
        for path in selected:
            try:
                state_dict = torch.load(path, map_location="cpu", weights_only=True)
            except Exception:
                try:
                    state_dict = torch.load(path, map_location="cpu", weights_only=False)
                except Exception:
                    continue

            if not isinstance(state_dict, dict):
                continue

            fname = os.path.basename(path)
            val_acc = _parse_val_acc_from_filename(fname)
            checkpoint_id = os.path.splitext(fname)[0]

            # Default arch config for MNIST Transformers (from metadata)
            arch_config = {
                "embed_dim": 32,
                "n_heads": 2,
                "n_layers": 2,
                "n_classes": 10 if task == "mnist" else 4,
                "n_patches": 49,
                "patch_size": 4,
                "n_channels": 1 if task == "mnist" else 3,
                "forward_mul": 2,
            }

            checkpoints.append({
                "state_dict": state_dict,
                "val_acc": val_acc,
                "checkpoint_id": checkpoint_id,
                "task": task,
                "arch_config": arch_config,
            })

        return checkpoints

    def load_checkpoints(self) -> List[Dict[str, Any]]:
        """Returns list of {state_dict, val_acc, checkpoint_id, task, arch_config}."""
        mnist_ckpts = self._load_split(self.mnist_dir, self.n_mnist, "mnist")
        agnews_ckpts = []
        if self.n_agnews > 0 and self.agnews_dir:
            agnews_ckpts = self._load_split(self.agnews_dir, self.n_agnews, "agnews")
        all_ckpts = mnist_ckpts + agnews_ckpts
        print(f"✓ TransformerZooLoader: {len(mnist_ckpts)} MNIST + {len(agnews_ckpts)} AG-News = {len(all_ckpts)} total")
        return all_ckpts

    def build_model(self, arch_config: Dict[str, Any]) -> nn.Module:
        """Build minimal Transformer from arch_config dict."""
        return SimpleTransformer(
            embed_dim=arch_config.get("embed_dim", 32),
            n_heads=arch_config.get("n_heads", 2),
            n_layers=arch_config.get("n_layers", 2),
            n_classes=arch_config.get("n_classes", 10),
            n_patches=arch_config.get("n_patches", 49),
            patch_size=arch_config.get("patch_size", 4),
            n_channels=arch_config.get("n_channels", 1),
            forward_mul=arch_config.get("forward_mul", 2),
        )

    def get_val_loader(self, task: str = "mnist", batch_size: int = 256) -> DataLoader:
        """Returns a real validation DataLoader for given task."""
        import torchvision
        import torchvision.transforms as transforms

        data_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "torchvision")
        os.makedirs(data_root, exist_ok=True)

        if task == "mnist":
            transform = transforms.Compose([
                transforms.Resize(28),
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,)),
            ])
            dataset = torchvision.datasets.MNIST(root=data_root, train=False, download=True, transform=transform)
        elif task == "agnews":
            # AG-News is a text dataset; use CIFAR-10 as a proxy image input for the vision-based model
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
            ])
            dataset = torchvision.datasets.CIFAR10(root=data_root, train=False, download=True, transform=transform)
        else:
            transform = transforms.Compose([
                transforms.Resize(28),
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,)),
            ])
            dataset = torchvision.datasets.MNIST(root=data_root, train=False, download=True, transform=transform)

        return DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)
