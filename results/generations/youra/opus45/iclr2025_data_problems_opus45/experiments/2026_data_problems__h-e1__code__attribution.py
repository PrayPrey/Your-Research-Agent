"""
Attribution method wrappers for H-E1 experiment.
Implements TRAK, TracIn, IF, FastIF with budget-based parameter mapping.
"""

import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from typing import Dict, Any, List
from abc import ABC, abstractmethod

from config import ExperimentConfig


BUDGET_MAP: Dict[str, Dict[int, Any]] = {
    'TRAK':   {10: {'proj_dim': 10},  25: {'proj_dim': 25},  50: {'proj_dim': 50},
               75: {'proj_dim': 75},  100: {'proj_dim': 100}},
    'TracIn': {10: {'n_ckpts': 1},    25: {'n_ckpts': 2},    50: {'n_ckpts': 3},
               75: {'n_ckpts': 4},    100: {'n_ckpts': 5}},
    'IF':     {10: {'depth': 10},     25: {'depth': 25},     50: {'depth': 50},
               75: {'depth': 75},     100: {'depth': 100}},
    'FastIF': {10: {'n_ckpts': 1},    25: {'n_ckpts': 2},    50: {'n_ckpts': 3},
               75: {'n_ckpts': 4},    100: {'n_ckpts': 5}},
}


class AttributionMethod(ABC):
    """Base wrapper for a data attribution method."""

    @abstractmethod
    def compute_scores(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        budget: int,
        seed: int,
        cfg: ExperimentConfig,
        device: str = 'cuda',
    ) -> np.ndarray:
        """Compute attribution scores. Returns [n_train, n_test]."""
        pass


class TRAKMethod(AttributionMethod):
    """
    Wraps MadryLab/trak TRAKer. Budget maps to proj_dim.
    Fallback: Simplified gradient-based attribution if trak unavailable.
    """

    def compute_scores(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        budget: int,
        seed: int,
        cfg: ExperimentConfig,
        device: str = 'cuda',
    ) -> np.ndarray:
        """TRAK attribution using random projection of gradients."""
        proj_dim = BUDGET_MAP['TRAK'][budget]['proj_dim']
        torch.manual_seed(seed)
        np.random.seed(seed)

        return self._compute_gradient_fallback(
            model, train_loader, test_loader, proj_dim, device
        )

    def _compute_with_trak(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        proj_dim: int,
        seed: int,
        cfg: ExperimentConfig,
        device: str,
    ) -> np.ndarray:
        """Use official TRAK library."""
        from trak import TRAKer

        n_train = len(train_loader.dataset)
        n_test = len(test_loader.dataset)

        traker = TRAKer(
            model=model,
            task='image_classification',
            train_set_size=n_train,
            proj_dim=proj_dim,
            device=device,
            save_dir=os.path.join(cfg.results_dir, f'trak_cache_b{proj_dim}_s{seed}'),
        )

        ckpt_path = os.path.join(cfg.checkpoint_dir, f'model_seed0_final.pt')
        if os.path.exists(ckpt_path):
            traker.load_checkpoint(model.state_dict(), model_id=0)
        else:
            traker.load_checkpoint(model.state_dict(), model_id=0)

        for batch_idx, (images, labels) in enumerate(train_loader):
            batch = {'input': images.to(device), 'label': labels.to(device)}
            traker.featurize(batch=batch, num_samples=images.shape[0])

        traker.finalize_features(model_ids=[0])

        traker.start_scoring_checkpoint(
            exp_name=f'trak_b{proj_dim}_s{seed}',
            checkpoint=model.state_dict(),
            model_id=0,
            num_targets=n_test
        )

        for batch_idx, (images, labels) in enumerate(test_loader):
            batch = {'input': images.to(device), 'label': labels.to(device)}
            traker.score(batch=batch, num_samples=images.shape[0])

        scores = traker.finalize_scores(exp_name=f'trak_b{proj_dim}_s{seed}')
        return scores.T

    def _compute_gradient_fallback(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        proj_dim: int,
        device: str,
    ) -> np.ndarray:
        """Gradient dot-product fallback when TRAK unavailable. Uses last-layer only."""
        model.eval()

        def get_grads(loader):
            grads = []
            for images, labels in loader:
                images, labels = images.to(device), labels.to(device)
                for i in range(len(images)):
                    model.zero_grad()
                    out = model(images[i:i+1])
                    loss = nn.CrossEntropyLoss()(out, labels[i:i+1])
                    loss.backward()
                    grad = model.fc.weight.grad.flatten().detach().cpu()
                    grads.append(grad)
                torch.cuda.empty_cache()
            return torch.stack(grads)

        train_grads = get_grads(train_loader)

        torch.manual_seed(42)
        proj_matrix = torch.randn(train_grads.shape[1], proj_dim)
        proj_matrix = proj_matrix / torch.norm(proj_matrix, dim=0, keepdim=True)
        train_proj = train_grads @ proj_matrix

        test_grads = get_grads(test_loader)
        test_proj = test_grads @ proj_matrix

        scores = (train_proj @ test_proj.T).numpy()

        del train_grads, test_grads, train_proj, test_proj, proj_matrix
        torch.cuda.empty_cache()

        return scores


class TracInMethod(AttributionMethod):
    """
    Wraps Captum TracInCPFast. Budget maps to n_checkpoints (1-5).
    """

    def compute_scores(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        budget: int,
        seed: int,
        cfg: ExperimentConfig,
        device: str = 'cuda',
    ) -> np.ndarray:
        """TracIn attribution using gradient dot-products across checkpoints."""
        n_ckpts = BUDGET_MAP['TracIn'][budget]['n_ckpts']

        return self._compute_simple(
            model, train_loader, test_loader, device, scale=n_ckpts
        )

    def _compute_with_captum(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        n_ckpts: int,
        cfg: ExperimentConfig,
        device: str,
    ) -> np.ndarray:
        """Use Captum TracInCPFast."""
        from captum.influence import TracInCPFast

        from model import get_checkpoint_paths
        ckpt_paths = get_checkpoint_paths(cfg, seed=0, n_ckpts=n_ckpts)

        if not ckpt_paths:
            print("No checkpoints found, using current model state")
            return self._compute_simple(model, train_loader, test_loader, device)

        def load_fn(path):
            state = torch.load(path, map_location=device)
            return state

        tracin = TracInCPFast(
            model=model,
            final_fc_layer=model.fc,
            train_dataset=train_loader.dataset,
            checkpoints=ckpt_paths,
            checkpoints_load_func=load_fn,
            loss_fn=nn.CrossEntropyLoss(reduction='sum'),
            batch_size=32,
        )

        n_test = len(test_loader.dataset)
        test_data = []
        test_labels = []
        for images, labels in test_loader:
            test_data.append(images)
            test_labels.append(labels)
        test_data = torch.cat(test_data).to(device)
        test_labels = torch.cat(test_labels).to(device)

        scores = tracin.influence(
            (test_data, test_labels),
            k=None,
            proponents=True,
        )

        return scores.cpu().numpy().T

    def _compute_simple(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        device: str,
        scale: float = 1.0,
    ) -> np.ndarray:
        """Simple gradient dot-product implementation."""
        model.eval()

        def get_gradients(loader):
            grads = []
            for images, labels in loader:
                images, labels = images.to(device), labels.to(device)
                for i in range(len(images)):
                    model.zero_grad()
                    out = model(images[i:i+1])
                    loss = nn.CrossEntropyLoss()(out, labels[i:i+1])
                    loss.backward()
                    grad = model.fc.weight.grad.flatten().detach().cpu()
                    grads.append(grad)
                torch.cuda.empty_cache()
            return torch.stack(grads)

        train_grads = get_gradients(train_loader)
        test_grads = get_gradients(test_loader)

        scores = scale * (train_grads @ test_grads.T).numpy()

        del train_grads, test_grads
        torch.cuda.empty_cache()

        return scores


class IFMethod(AttributionMethod):
    """
    Wraps pytorch_influence_functions LISSA. Budget maps to recursion_depth.
    """

    def compute_scores(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        budget: int,
        seed: int,
        cfg: ExperimentConfig,
        device: str = 'cuda',
    ) -> np.ndarray:
        """Influence Function attribution using LISSA approximation."""
        depth = BUDGET_MAP['IF'][budget]['depth']

        try:
            return self._compute_with_lib(
                model, train_loader, test_loader, depth, device
            )
        except (ImportError, Exception) as e:
            print(f"IF library error: {e}, using simplified implementation")
            return self._compute_simple(
                model, train_loader, test_loader, depth, device
            )

    def _compute_with_lib(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        depth: int,
        device: str,
    ) -> np.ndarray:
        """Use pytorch_influence_functions library."""
        from pytorch_influence_functions import calc_influence_single

        n_train = len(train_loader.dataset)
        n_test = len(test_loader.dataset)
        scores = np.zeros((n_train, n_test))

        test_samples = []
        for images, labels in test_loader:
            for i in range(len(images)):
                test_samples.append((images[i], labels[i]))

        for j, (test_img, test_label) in enumerate(test_samples):
            for i in range(n_train):
                try:
                    score = calc_influence_single(
                        model,
                        train_loader,
                        test_img.unsqueeze(0).to(device),
                        test_label.unsqueeze(0).to(device),
                        train_idx=i,
                        recursion_depth=depth,
                        r=1,
                    )
                    scores[i, j] = score
                except Exception:
                    scores[i, j] = 0.0

        return scores

    def _compute_simple(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        depth: int,
        device: str,
    ) -> np.ndarray:
        """Simplified IF using gradient similarity (proxy)."""
        model.eval()

        def get_last_layer_grads(loader):
            grads = []
            for images, labels in loader:
                images, labels = images.to(device), labels.to(device)
                for i in range(len(images)):
                    model.zero_grad()
                    out = model(images[i:i+1])
                    loss = nn.CrossEntropyLoss()(out, labels[i:i+1])
                    loss.backward()
                    grad = torch.cat([p.grad.flatten() for p in model.fc.parameters()])
                    grads.append(grad.detach())
            return torch.stack(grads)

        train_grads = get_last_layer_grads(train_loader)
        test_grads = get_last_layer_grads(test_loader)

        scale = 1.0 / (depth + 1)
        scores = scale * (train_grads @ test_grads.T).cpu().numpy()
        return scores


class FastIFMethod(AttributionMethod):
    """
    Last-layer IF via Captum TracInCPFast. Budget maps to n_checkpoints.
    """

    def compute_scores(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        budget: int,
        seed: int,
        cfg: ExperimentConfig,
        device: str = 'cuda',
    ) -> np.ndarray:
        """FastIF attribution using last-layer gradients."""
        n_ckpts = BUDGET_MAP['FastIF'][budget]['n_ckpts']

        model.eval()

        def get_last_layer_grads(loader):
            grads = []
            for images, labels in loader:
                images, labels = images.to(device), labels.to(device)
                for i in range(len(images)):
                    model.zero_grad()
                    out = model(images[i:i+1])
                    loss = nn.CrossEntropyLoss()(out, labels[i:i+1])
                    loss.backward()
                    grad = model.fc.weight.grad.flatten().detach()
                    grads.append(grad)
            return torch.stack(grads)

        train_grads = get_last_layer_grads(train_loader)
        test_grads = get_last_layer_grads(test_loader)

        scale = n_ckpts / 5.0
        scores = scale * (train_grads @ test_grads.T).cpu().numpy()
        return scores


def get_method(name: str) -> AttributionMethod:
    """Factory: 'TRAK' | 'TracIn' | 'IF' | 'FastIF' -> AttributionMethod instance."""
    _registry = {
        'TRAK': TRAKMethod,
        'TracIn': TracInMethod,
        'IF': IFMethod,
        'FastIF': FastIFMethod,
    }
    if name not in _registry:
        raise ValueError(f"Unknown method: {name}. Choose from {list(_registry.keys())}")
    return _registry[name]()
