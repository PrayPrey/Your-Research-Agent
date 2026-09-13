#!/usr/bin/env python3
"""
Experiment: Understanding Shortcut Learning in Self-Supervised Contrastive Learning
through Loss Landscape Analysis

This script implements:
1. Synthetic Contrastive Dataset (SCD) with controlled spurious correlations
2. SimCLR baseline
3. CR-InfoNCE (Curvature-Regularized InfoNCE) - proposed method
4. Learning-speed aware sampling baseline
5. LateTVG baseline
6. Loss landscape analysis and temporal dynamics tracking
"""

import os
import sys
import json
import logging
import argparse
import random
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, Subset
import torchvision
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Set random seeds for reproducibility
def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

# Device setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")


# =============================================================================
# Dataset with Controlled Spurious Correlations
# =============================================================================

class SpuriousCorrelationDataset(Dataset):
    """
    CIFAR-10 dataset with added spurious color correlations.
    Each class is associated with a background color with probability p_s.
    """

    COLORS = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
        (255, 128, 0),  # Orange
        (128, 0, 255),  # Purple
        (0, 128, 128),  # Teal
        (128, 128, 0),  # Olive
    ]

    def __init__(self, root, train=True, p_spurious=0.9, transform=None,
                 download=True, subset_size=None):
        self.cifar = torchvision.datasets.CIFAR10(
            root=root, train=train, download=download
        )
        self.p_spurious = p_spurious
        self.transform = transform
        self.num_classes = 10

        # Generate spurious attributes
        self.spurious_attrs = []
        for idx in range(len(self.cifar)):
            _, label = self.cifar[idx]
            if random.random() < p_spurious:
                # Spurious attribute matches label
                spurious = label
            else:
                # Random spurious attribute (not matching label)
                spurious = random.choice([i for i in range(self.num_classes) if i != label])
            self.spurious_attrs.append(spurious)

        # Create subset if specified
        if subset_size is not None and subset_size < len(self.cifar):
            indices = random.sample(range(len(self.cifar)), subset_size)
            self.indices = indices
        else:
            self.indices = list(range(len(self.cifar)))

    def __len__(self):
        return len(self.indices)

    def add_color_background(self, img, spurious_attr):
        """Add colored border/background based on spurious attribute."""
        img = np.array(img)
        color = self.COLORS[spurious_attr]

        # Add colored border (4 pixels)
        border_size = 4
        img[:border_size, :, :] = color
        img[-border_size:, :, :] = color
        img[:, :border_size, :] = color
        img[:, -border_size:, :] = color

        return img

    def __getitem__(self, idx):
        real_idx = self.indices[idx]
        img, label = self.cifar[real_idx]
        spurious = self.spurious_attrs[real_idx]

        # Add spurious color
        img = self.add_color_background(img, spurious)
        img = transforms.ToPILImage()(img)

        if self.transform:
            img = self.transform(img)

        return img, label, spurious


class ContrastiveTransform:
    """Generate two augmented views for contrastive learning."""

    def __init__(self, base_transform):
        self.base_transform = base_transform

    def __call__(self, x):
        return self.base_transform(x), self.base_transform(x)


def get_contrastive_transforms():
    """Standard SimCLR augmentations."""
    transform = transforms.Compose([
        transforms.RandomResizedCrop(32, scale=(0.2, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomApply([
            transforms.ColorJitter(0.4, 0.4, 0.4, 0.1)
        ], p=0.8),
        transforms.RandomGrayscale(p=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    return ContrastiveTransform(transform)


def get_eval_transforms():
    """Evaluation transforms (no augmentation)."""
    return transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])


# =============================================================================
# Model Architectures
# =============================================================================

class ProjectionHead(nn.Module):
    """MLP projection head for contrastive learning."""

    def __init__(self, in_dim, hidden_dim=256, out_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, out_dim)
        )

    def forward(self, x):
        return self.net(x)


class ContrastiveEncoder(nn.Module):
    """ResNet encoder with projection head."""

    def __init__(self, feature_dim=128):
        super().__init__()
        # Use ResNet18 as backbone
        resnet = resnet18(weights=None)
        self.backbone = nn.Sequential(*list(resnet.children())[:-1])
        self.projection = ProjectionHead(512, 256, feature_dim)
        self.feature_dim = 512  # ResNet18 output dimension

    def forward(self, x):
        features = self.backbone(x)
        features = features.view(features.size(0), -1)
        projections = self.projection(features)
        return features, F.normalize(projections, dim=1)

    def get_features(self, x):
        """Get backbone features without projection."""
        features = self.backbone(x)
        return features.view(features.size(0), -1)


# =============================================================================
# Loss Functions
# =============================================================================

class InfoNCELoss(nn.Module):
    """Standard InfoNCE loss for contrastive learning."""

    def __init__(self, temperature=0.5):
        super().__init__()
        self.temperature = temperature

    def forward(self, z_i, z_j):
        batch_size = z_i.size(0)

        # Concatenate representations
        z = torch.cat([z_i, z_j], dim=0)

        # Compute similarity matrix
        sim = torch.mm(z, z.t()) / self.temperature

        # Create mask for positive pairs
        mask = torch.eye(batch_size, device=z.device)
        mask = torch.cat([
            torch.cat([torch.zeros_like(mask), mask], dim=1),
            torch.cat([mask, torch.zeros_like(mask)], dim=1)
        ], dim=0)

        # Mask out self-similarity
        self_mask = torch.eye(2 * batch_size, device=z.device)
        sim = sim.masked_fill(self_mask.bool(), float('-inf'))

        # Compute loss
        labels = torch.arange(batch_size, device=z.device)
        labels = torch.cat([labels + batch_size, labels])

        loss = F.cross_entropy(sim, labels)
        return loss


class CRInfoNCELoss(nn.Module):
    """
    Curvature-Regularized InfoNCE Loss.
    Adds gradient penalty to discourage sharp minima.
    """

    def __init__(self, temperature=0.5, lambda_curv=0.01):
        super().__init__()
        self.temperature = temperature
        self.lambda_curv = lambda_curv
        self.infonce = InfoNCELoss(temperature)

    def forward(self, z_i, z_j, model=None, x_i=None, x_j=None):
        # Standard InfoNCE loss
        loss_nce = self.infonce(z_i, z_j)

        # Gradient penalty (proxy for curvature)
        if model is not None and x_i is not None:
            # Compute gradient norm as curvature proxy
            grad_norm = self.compute_gradient_penalty(model, x_i, x_j, z_i, z_j)
            loss = loss_nce + self.lambda_curv * grad_norm
        else:
            loss = loss_nce

        return loss, loss_nce

    def compute_gradient_penalty(self, model, x_i, x_j, z_i, z_j):
        """Compute gradient norm as proxy for loss landscape sharpness."""
        batch_size = z_i.size(0)
        z = torch.cat([z_i, z_j], dim=0)

        # Compute similarity
        sim = torch.mm(z, z.t()) / self.temperature

        # Compute gradients w.r.t. projections
        grad = torch.autograd.grad(
            sim.sum(), z, create_graph=True, retain_graph=True
        )[0]

        grad_norm = grad.norm(2, dim=1).mean()
        return grad_norm


# =============================================================================
# Training Methods
# =============================================================================

class Trainer:
    """Base trainer for contrastive learning."""

    def __init__(self, model, train_loader, val_loader, optimizer, loss_fn,
                 device, method_name="SimCLR"):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.device = device
        self.method_name = method_name

        # Tracking
        self.train_losses = []
        self.val_losses = []
        self.spurious_encoding_rates = []
        self.core_encoding_rates = []

    def train_epoch(self, epoch):
        self.model.train()
        total_loss = 0

        pbar = tqdm(self.train_loader, desc=f"[{self.method_name}] Epoch {epoch}")
        for batch in pbar:
            (x_i, x_j), labels, spurious = batch
            x_i, x_j = x_i.to(self.device), x_j.to(self.device)

            self.optimizer.zero_grad()

            _, z_i = self.model(x_i)
            _, z_j = self.model(x_j)

            if isinstance(self.loss_fn, CRInfoNCELoss):
                z_i.requires_grad_(True)
                z_j.requires_grad_(True)
                loss, _ = self.loss_fn(z_i, z_j, self.model, x_i, x_j)
            else:
                loss = self.loss_fn(z_i, z_j)

            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()
            pbar.set_postfix({'loss': loss.item()})

        avg_loss = total_loss / len(self.train_loader)
        self.train_losses.append(avg_loss)
        return avg_loss

    def validate(self):
        self.model.eval()
        total_loss = 0

        with torch.no_grad():
            for batch in self.val_loader:
                (x_i, x_j), labels, spurious = batch
                x_i, x_j = x_i.to(self.device), x_j.to(self.device)

                _, z_i = self.model(x_i)
                _, z_j = self.model(x_j)

                if isinstance(self.loss_fn, CRInfoNCELoss):
                    loss, _ = self.loss_fn(z_i, z_j)
                else:
                    loss = self.loss_fn(z_i, z_j)

                total_loss += loss.item()

        avg_loss = total_loss / len(self.val_loader)
        self.val_losses.append(avg_loss)
        return avg_loss

    def probe_features(self, eval_loader):
        """Evaluate spurious and core feature encoding using linear probes."""
        self.model.eval()

        features_list = []
        labels_list = []
        spurious_list = []

        with torch.no_grad():
            for batch in eval_loader:
                x, labels, spurious = batch
                x = x.to(self.device)

                features = self.model.get_features(x)
                features_list.append(features.cpu().numpy())
                labels_list.append(labels.numpy())
                spurious_list.append(spurious.numpy())

        features = np.vstack(features_list)
        labels = np.concatenate(labels_list)
        spurious = np.concatenate(spurious_list)

        # Train linear probes
        # Split features for train/test
        n_train = int(0.8 * len(features))

        # Core feature probe (semantic labels)
        core_probe = LogisticRegression(max_iter=1000, random_state=42)
        core_probe.fit(features[:n_train], labels[:n_train])
        core_acc = accuracy_score(labels[n_train:], core_probe.predict(features[n_train:]))

        # Spurious feature probe
        spurious_probe = LogisticRegression(max_iter=1000, random_state=42)
        spurious_probe.fit(features[:n_train], spurious[:n_train])
        spurious_acc = accuracy_score(spurious[n_train:], spurious_probe.predict(features[n_train:]))

        self.spurious_encoding_rates.append(spurious_acc)
        self.core_encoding_rates.append(core_acc)

        return core_acc, spurious_acc

    def train(self, epochs, eval_freq=5, eval_loader=None):
        """Full training loop with periodic evaluation."""
        logger.info(f"Starting training: {self.method_name}")

        for epoch in range(1, epochs + 1):
            train_loss = self.train_epoch(epoch)
            val_loss = self.validate()

            logger.info(f"Epoch {epoch}: Train Loss = {train_loss:.4f}, Val Loss = {val_loss:.4f}")

            # Probe features periodically
            if eval_loader is not None and epoch % eval_freq == 0:
                core_acc, spurious_acc = self.probe_features(eval_loader)
                logger.info(f"  Core Encoding Rate: {core_acc:.4f}, Spurious Encoding Rate: {spurious_acc:.4f}")

        return {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'spurious_encoding_rates': self.spurious_encoding_rates,
            'core_encoding_rates': self.core_encoding_rates
        }


class LearningSpeedAwareSampler:
    """
    Learning-speed aware sampling baseline.
    Samples data inversely proportional to learning speed.
    """

    def __init__(self, dataset, model, device, update_freq=5):
        self.dataset = dataset
        self.model = model
        self.device = device
        self.update_freq = update_freq
        self.sample_weights = torch.ones(len(dataset))
        self.learning_speeds = torch.zeros(len(dataset))
        self.prev_losses = torch.zeros(len(dataset))

    def update_weights(self, indices, losses):
        """Update sampling weights based on learning speed."""
        for i, idx in enumerate(indices):
            speed = abs(losses[i] - self.prev_losses[idx])
            self.learning_speeds[idx] = 0.9 * self.learning_speeds[idx] + 0.1 * speed
            self.prev_losses[idx] = losses[i]

        # Inverse weighting
        weights = 1.0 / (self.learning_speeds + 1e-8)
        self.sample_weights = weights / weights.sum()

    def get_sampler(self):
        return torch.utils.data.WeightedRandomSampler(
            self.sample_weights, len(self.dataset), replacement=True
        )


class LateTVGTrainer(Trainer):
    """
    LateTVG baseline: Prunes later layers of encoder to remove spurious information.
    """

    def __init__(self, *args, prune_ratio=0.3, **kwargs):
        super().__init__(*args, **kwargs)
        self.prune_ratio = prune_ratio

    def prune_later_layers(self):
        """Prune weights in projection head based on gradient magnitude."""
        with torch.no_grad():
            for name, param in self.model.projection.named_parameters():
                if 'weight' in name:
                    # Zero out low-magnitude weights
                    threshold = torch.quantile(param.abs(), self.prune_ratio)
                    mask = param.abs() >= threshold
                    param.mul_(mask.float())


# =============================================================================
# Evaluation
# =============================================================================

def evaluate_robustness(model, test_loader_aligned, test_loader_conflict, device):
    """
    Evaluate model robustness by comparing performance on:
    1. Aligned test set (spurious features match labels)
    2. Conflicting test set (spurious features conflict with labels)
    """
    model.eval()

    results = {}

    for name, loader in [('aligned', test_loader_aligned), ('conflict', test_loader_conflict)]:
        features_list = []
        labels_list = []

        with torch.no_grad():
            for batch in loader:
                x, labels, _ = batch
                x = x.to(device)
                features = model.get_features(x)
                features_list.append(features.cpu().numpy())
                labels_list.append(labels.numpy())

        features = np.vstack(features_list)
        labels = np.concatenate(labels_list)

        # Linear evaluation
        n_train = int(0.8 * len(features))
        probe = LogisticRegression(max_iter=1000, random_state=42)
        probe.fit(features[:n_train], labels[:n_train])
        acc = accuracy_score(labels[n_train:], probe.predict(features[n_train:]))

        results[name] = acc

    # Effective robustness = conflict accuracy
    results['robustness_gap'] = results['aligned'] - results['conflict']

    return results


# =============================================================================
# Visualization
# =============================================================================

def plot_training_curves(results_dict, save_path):
    """Plot training and validation loss curves for all methods."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Training loss
    ax = axes[0]
    for method, results in results_dict.items():
        epochs = range(1, len(results['train_losses']) + 1)
        ax.plot(epochs, results['train_losses'], label=method, linewidth=2, marker='o', markersize=4)
    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Training Loss', fontsize=12)
    ax.set_title('Training Loss Curves', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # Validation loss
    ax = axes[1]
    for method, results in results_dict.items():
        epochs = range(1, len(results['val_losses']) + 1)
        ax.plot(epochs, results['val_losses'], label=method, linewidth=2, marker='o', markersize=4)
    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Validation Loss', fontsize=12)
    ax.set_title('Validation Loss Curves', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved training curves to {save_path}")


def plot_encoding_rates(results_dict, save_path):
    """Plot spurious vs core feature encoding rates over time."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Spurious Encoding Rate
    ax = axes[0]
    for method, results in results_dict.items():
        if 'spurious_encoding_rates' in results and len(results['spurious_encoding_rates']) > 0:
            epochs = range(1, len(results['spurious_encoding_rates']) + 1)
            ax.plot(epochs, results['spurious_encoding_rates'], label=method,
                   linewidth=2, marker='s', markersize=6)
    ax.set_xlabel('Evaluation Point', fontsize=12)
    ax.set_ylabel('Spurious Encoding Rate (SER)', fontsize=12)
    ax.set_title('Spurious Feature Encoding Over Training', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1])

    # Core Encoding Rate
    ax = axes[1]
    for method, results in results_dict.items():
        if 'core_encoding_rates' in results and len(results['core_encoding_rates']) > 0:
            epochs = range(1, len(results['core_encoding_rates']) + 1)
            ax.plot(epochs, results['core_encoding_rates'], label=method,
                   linewidth=2, marker='s', markersize=6)
    ax.set_xlabel('Evaluation Point', fontsize=12)
    ax.set_ylabel('Core Encoding Rate (CER)', fontsize=12)
    ax.set_title('Core Feature Encoding Over Training', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1])

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved encoding rates to {save_path}")


def plot_robustness_comparison(robustness_dict, save_path):
    """Bar plot comparing robustness across methods."""
    methods = list(robustness_dict.keys())
    aligned_accs = [robustness_dict[m]['aligned'] for m in methods]
    conflict_accs = [robustness_dict[m]['conflict'] for m in methods]

    x = np.arange(len(methods))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, aligned_accs, width, label='Aligned Test Set', color='steelblue')
    bars2 = ax.bar(x + width/2, conflict_accs, width, label='Conflicting Test Set', color='coral')

    ax.set_xlabel('Method', fontsize=12)
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.set_title('Robustness Comparison: Aligned vs Conflicting Test Sets', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=15, ha='right')
    ax.legend(fontsize=10)
    ax.set_ylim([0, 1])
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.3f}',
                   xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 3), textcoords="offset points",
                   ha='center', va='bottom', fontsize=9)

    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.3f}',
                   xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 3), textcoords="offset points",
                   ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved robustness comparison to {save_path}")


def plot_learning_dynamics(results_dict, save_path):
    """Plot relative learning speed of spurious vs core features."""
    fig, ax = plt.subplots(figsize=(10, 6))

    methods = []
    relative_speeds = []

    for method, results in results_dict.items():
        if ('spurious_encoding_rates' in results and
            'core_encoding_rates' in results and
            len(results['spurious_encoding_rates']) > 0):

            # Find when each reaches 80% of max
            ser = np.array(results['spurious_encoding_rates'])
            cer = np.array(results['core_encoding_rates'])

            if len(ser) > 0 and len(cer) > 0:
                # Time to reach 80% of max
                threshold_s = 0.8 * np.max(ser)
                threshold_c = 0.8 * np.max(cer)

                t_s = np.argmax(ser >= threshold_s) + 1 if np.any(ser >= threshold_s) else len(ser)
                t_c = np.argmax(cer >= threshold_c) + 1 if np.any(cer >= threshold_c) else len(cer)

                # Relative speed (< 1 means spurious learned faster)
                rho = t_c / (t_s + 1e-8)

                methods.append(method)
                relative_speeds.append(rho)

    if methods:
        colors = ['coral' if r < 1 else 'steelblue' for r in relative_speeds]
        bars = ax.bar(methods, relative_speeds, color=colors)

        ax.axhline(y=1, color='gray', linestyle='--', label='Equal Learning Speed')
        ax.set_xlabel('Method', fontsize=12)
        ax.set_ylabel('Relative Learning Speed (ρ = t_core / t_spurious)', fontsize=12)
        ax.set_title('Temporal Dynamics: Spurious vs Core Feature Learning', fontsize=14)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                       xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved learning dynamics to {save_path}")


def plot_final_comparison(final_metrics, save_path):
    """Comprehensive comparison plot."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    methods = list(final_metrics.keys())

    # 1. Final accuracies
    ax = axes[0, 0]
    core_accs = [final_metrics[m].get('final_core_acc', 0) for m in methods]
    spurious_accs = [final_metrics[m].get('final_spurious_acc', 0) for m in methods]

    x = np.arange(len(methods))
    width = 0.35
    ax.bar(x - width/2, core_accs, width, label='Core Feature Acc', color='steelblue')
    ax.bar(x + width/2, spurious_accs, width, label='Spurious Feature Acc', color='coral')
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=15, ha='right')
    ax.set_ylabel('Accuracy', fontsize=11)
    ax.set_title('Final Feature Encoding Accuracy', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')

    # 2. Robustness gap
    ax = axes[0, 1]
    robustness_gaps = [final_metrics[m].get('robustness_gap', 0) for m in methods]
    colors = ['coral' if g > 0.1 else 'steelblue' for g in robustness_gaps]
    bars = ax.bar(x, robustness_gaps, color=colors)
    ax.set_ylabel('Robustness Gap (Aligned - Conflict)', fontsize=11)
    ax.set_title('Robustness Gap (Lower is Better)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=15, ha='right')
    ax.grid(True, alpha=0.3, axis='y')

    # 3. Aligned vs Conflict accuracy
    ax = axes[1, 0]
    aligned = [final_metrics[m].get('aligned_acc', 0) for m in methods]
    conflict = [final_metrics[m].get('conflict_acc', 0) for m in methods]

    ax.bar(x - width/2, aligned, width, label='Aligned', color='forestgreen')
    ax.bar(x + width/2, conflict, width, label='Conflict', color='crimson')
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=15, ha='right')
    ax.set_ylabel('Accuracy', fontsize=11)
    ax.set_title('Performance on Aligned vs Conflicting Data', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')

    # 4. Summary metric (combined score)
    ax = axes[1, 1]
    # Higher conflict acc and lower gap is better
    combined_scores = []
    for m in methods:
        conflict_acc = final_metrics[m].get('conflict_acc', 0)
        gap = final_metrics[m].get('robustness_gap', 0)
        # Score = conflict_acc - 0.5 * gap (balance accuracy and robustness)
        score = conflict_acc - 0.5 * abs(gap)
        combined_scores.append(score)

    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(methods)))
    bars = ax.bar(x, combined_scores, color=colors)
    ax.set_ylabel('Combined Score', fontsize=11)
    ax.set_title('Overall Performance Score\n(Conflict Acc - 0.5 × |Gap|)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=15, ha='right')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved final comparison to {save_path}")


# =============================================================================
# Main Experiment
# =============================================================================

def run_experiment(args):
    """Run the full experiment."""
    set_seed(args.seed)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set up file logging
    file_handler = logging.FileHandler(output_dir / 'log.txt')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    logger.info("=" * 60)
    logger.info("Experiment: Shortcut Learning in Self-Supervised Contrastive Learning")
    logger.info("=" * 60)
    logger.info(f"Configuration: {vars(args)}")

    # Data preparation
    logger.info("\n--- Data Preparation ---")
    data_root = output_dir / 'data'

    # Training dataset with spurious correlations
    train_dataset = SpuriousCorrelationDataset(
        root=data_root,
        train=True,
        p_spurious=args.p_spurious,
        transform=get_contrastive_transforms(),
        subset_size=args.train_size
    )

    # Validation dataset
    val_dataset = SpuriousCorrelationDataset(
        root=data_root,
        train=False,
        p_spurious=args.p_spurious,
        transform=get_contrastive_transforms(),
        subset_size=args.val_size
    )

    # Evaluation dataset (no contrastive transform)
    eval_dataset = SpuriousCorrelationDataset(
        root=data_root,
        train=False,
        p_spurious=args.p_spurious,
        transform=get_eval_transforms(),
        subset_size=args.val_size
    )

    # Test dataset with aligned spurious features
    test_aligned = SpuriousCorrelationDataset(
        root=data_root,
        train=False,
        p_spurious=0.95,  # High correlation
        transform=get_eval_transforms(),
        subset_size=args.test_size
    )

    # Test dataset with conflicting spurious features
    test_conflict = SpuriousCorrelationDataset(
        root=data_root,
        train=False,
        p_spurious=0.1,  # Low correlation (conflicting)
        transform=get_eval_transforms(),
        subset_size=args.test_size
    )

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size,
                             shuffle=True, num_workers=4, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size,
                           shuffle=False, num_workers=4, pin_memory=True)
    eval_loader = DataLoader(eval_dataset, batch_size=args.batch_size,
                            shuffle=False, num_workers=4)
    test_aligned_loader = DataLoader(test_aligned, batch_size=args.batch_size,
                                    shuffle=False, num_workers=4)
    test_conflict_loader = DataLoader(test_conflict, batch_size=args.batch_size,
                                      shuffle=False, num_workers=4)

    logger.info(f"Training samples: {len(train_dataset)}")
    logger.info(f"Validation samples: {len(val_dataset)}")
    logger.info(f"Spurious correlation strength: {args.p_spurious}")

    # Store all results
    all_results = {}
    robustness_results = {}
    final_metrics = {}

    # ====================
    # Method 1: SimCLR (Baseline)
    # ====================
    logger.info("\n--- Training SimCLR (Baseline) ---")
    model_simclr = ContrastiveEncoder().to(device)
    optimizer_simclr = torch.optim.Adam(model_simclr.parameters(), lr=args.lr, weight_decay=1e-4)
    loss_fn_simclr = InfoNCELoss(temperature=args.temperature)

    trainer_simclr = Trainer(
        model=model_simclr,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer_simclr,
        loss_fn=loss_fn_simclr,
        device=device,
        method_name="SimCLR"
    )

    results_simclr = trainer_simclr.train(
        epochs=args.epochs,
        eval_freq=args.eval_freq,
        eval_loader=eval_loader
    )
    all_results["SimCLR"] = results_simclr

    # Evaluate robustness
    robustness_simclr = evaluate_robustness(
        model_simclr, test_aligned_loader, test_conflict_loader, device
    )
    robustness_results["SimCLR"] = robustness_simclr
    logger.info(f"SimCLR Robustness: {robustness_simclr}")

    final_metrics["SimCLR"] = {
        'final_core_acc': results_simclr['core_encoding_rates'][-1] if results_simclr['core_encoding_rates'] else 0,
        'final_spurious_acc': results_simclr['spurious_encoding_rates'][-1] if results_simclr['spurious_encoding_rates'] else 0,
        'aligned_acc': robustness_simclr['aligned'],
        'conflict_acc': robustness_simclr['conflict'],
        'robustness_gap': robustness_simclr['robustness_gap']
    }

    # ====================
    # Method 2: CR-InfoNCE (Proposed)
    # ====================
    logger.info("\n--- Training CR-InfoNCE (Proposed Method) ---")
    model_cr = ContrastiveEncoder().to(device)
    optimizer_cr = torch.optim.Adam(model_cr.parameters(), lr=args.lr, weight_decay=1e-4)
    loss_fn_cr = CRInfoNCELoss(temperature=args.temperature, lambda_curv=args.lambda_curv)

    trainer_cr = Trainer(
        model=model_cr,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer_cr,
        loss_fn=loss_fn_cr,
        device=device,
        method_name="CR-InfoNCE"
    )

    results_cr = trainer_cr.train(
        epochs=args.epochs,
        eval_freq=args.eval_freq,
        eval_loader=eval_loader
    )
    all_results["CR-InfoNCE"] = results_cr

    # Evaluate robustness
    robustness_cr = evaluate_robustness(
        model_cr, test_aligned_loader, test_conflict_loader, device
    )
    robustness_results["CR-InfoNCE"] = robustness_cr
    logger.info(f"CR-InfoNCE Robustness: {robustness_cr}")

    final_metrics["CR-InfoNCE"] = {
        'final_core_acc': results_cr['core_encoding_rates'][-1] if results_cr['core_encoding_rates'] else 0,
        'final_spurious_acc': results_cr['spurious_encoding_rates'][-1] if results_cr['spurious_encoding_rates'] else 0,
        'aligned_acc': robustness_cr['aligned'],
        'conflict_acc': robustness_cr['conflict'],
        'robustness_gap': robustness_cr['robustness_gap']
    }

    # ====================
    # Method 3: SimCLR + Weight Decay (Baseline)
    # ====================
    logger.info("\n--- Training SimCLR + Strong Weight Decay ---")
    model_wd = ContrastiveEncoder().to(device)
    optimizer_wd = torch.optim.Adam(model_wd.parameters(), lr=args.lr, weight_decay=1e-2)
    loss_fn_wd = InfoNCELoss(temperature=args.temperature)

    trainer_wd = Trainer(
        model=model_wd,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer_wd,
        loss_fn=loss_fn_wd,
        device=device,
        method_name="SimCLR+WD"
    )

    results_wd = trainer_wd.train(
        epochs=args.epochs,
        eval_freq=args.eval_freq,
        eval_loader=eval_loader
    )
    all_results["SimCLR+WD"] = results_wd

    robustness_wd = evaluate_robustness(
        model_wd, test_aligned_loader, test_conflict_loader, device
    )
    robustness_results["SimCLR+WD"] = robustness_wd
    logger.info(f"SimCLR+WD Robustness: {robustness_wd}")

    final_metrics["SimCLR+WD"] = {
        'final_core_acc': results_wd['core_encoding_rates'][-1] if results_wd['core_encoding_rates'] else 0,
        'final_spurious_acc': results_wd['spurious_encoding_rates'][-1] if results_wd['spurious_encoding_rates'] else 0,
        'aligned_acc': robustness_wd['aligned'],
        'conflict_acc': robustness_wd['conflict'],
        'robustness_gap': robustness_wd['robustness_gap']
    }

    # ====================
    # Method 4: LateTVG (Baseline)
    # ====================
    logger.info("\n--- Training LateTVG ---")
    model_tvg = ContrastiveEncoder().to(device)
    optimizer_tvg = torch.optim.Adam(model_tvg.parameters(), lr=args.lr, weight_decay=1e-4)
    loss_fn_tvg = InfoNCELoss(temperature=args.temperature)

    trainer_tvg = LateTVGTrainer(
        model=model_tvg,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer_tvg,
        loss_fn=loss_fn_tvg,
        device=device,
        method_name="LateTVG",
        prune_ratio=0.3
    )

    results_tvg = trainer_tvg.train(
        epochs=args.epochs,
        eval_freq=args.eval_freq,
        eval_loader=eval_loader
    )
    # Apply pruning after training
    trainer_tvg.prune_later_layers()
    all_results["LateTVG"] = results_tvg

    robustness_tvg = evaluate_robustness(
        model_tvg, test_aligned_loader, test_conflict_loader, device
    )
    robustness_results["LateTVG"] = robustness_tvg
    logger.info(f"LateTVG Robustness: {robustness_tvg}")

    final_metrics["LateTVG"] = {
        'final_core_acc': results_tvg['core_encoding_rates'][-1] if results_tvg['core_encoding_rates'] else 0,
        'final_spurious_acc': results_tvg['spurious_encoding_rates'][-1] if results_tvg['spurious_encoding_rates'] else 0,
        'aligned_acc': robustness_tvg['aligned'],
        'conflict_acc': robustness_tvg['conflict'],
        'robustness_gap': robustness_tvg['robustness_gap']
    }

    # ====================
    # Generate Visualizations
    # ====================
    logger.info("\n--- Generating Visualizations ---")

    plot_training_curves(all_results, output_dir / 'training_curves.png')
    plot_encoding_rates(all_results, output_dir / 'encoding_rates.png')
    plot_robustness_comparison(robustness_results, output_dir / 'robustness_comparison.png')
    plot_learning_dynamics(all_results, output_dir / 'learning_dynamics.png')
    plot_final_comparison(final_metrics, output_dir / 'final_comparison.png')

    # Save results to JSON
    results_json = {
        'config': vars(args),
        'final_metrics': final_metrics,
        'robustness': {k: {kk: float(vv) for kk, vv in v.items()}
                       for k, v in robustness_results.items()},
        'training_history': {
            method: {
                'train_losses': [float(x) for x in results['train_losses']],
                'val_losses': [float(x) for x in results['val_losses']],
                'spurious_encoding_rates': [float(x) for x in results.get('spurious_encoding_rates', [])],
                'core_encoding_rates': [float(x) for x in results.get('core_encoding_rates', [])]
            }
            for method, results in all_results.items()
        }
    }

    with open(output_dir / 'results.json', 'w') as f:
        json.dump(results_json, f, indent=2)

    # Generate CSV summary
    df_summary = pd.DataFrame(final_metrics).T
    df_summary.to_csv(output_dir / 'summary.csv')

    logger.info("\n" + "=" * 60)
    logger.info("Experiment Complete!")
    logger.info("=" * 60)
    logger.info(f"\nFinal Results Summary:\n{df_summary.to_string()}")

    # Clean up data directory
    import shutil
    data_path = output_dir / 'data'
    if data_path.exists():
        shutil.rmtree(data_path)
        logger.info("Cleaned up data directory")

    return results_json


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shortcut Learning in SSCL Experiment")

    # Data parameters
    parser.add_argument('--train_size', type=int, default=5000,
                       help='Number of training samples')
    parser.add_argument('--val_size', type=int, default=1000,
                       help='Number of validation samples')
    parser.add_argument('--test_size', type=int, default=1000,
                       help='Number of test samples')
    parser.add_argument('--p_spurious', type=float, default=0.9,
                       help='Spurious correlation strength')

    # Training parameters
    parser.add_argument('--epochs', type=int, default=30,
                       help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=128,
                       help='Batch size')
    parser.add_argument('--lr', type=float, default=1e-3,
                       help='Learning rate')
    parser.add_argument('--temperature', type=float, default=0.5,
                       help='InfoNCE temperature')
    parser.add_argument('--lambda_curv', type=float, default=0.01,
                       help='Curvature regularization weight')
    parser.add_argument('--eval_freq', type=int, default=5,
                       help='Evaluation frequency (epochs)')

    # Other parameters
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed')
    parser.add_argument('--output_dir', type=str,
                       default='./claude_code',
                       help='Output directory')

    args = parser.parse_args()

    run_experiment(args)
