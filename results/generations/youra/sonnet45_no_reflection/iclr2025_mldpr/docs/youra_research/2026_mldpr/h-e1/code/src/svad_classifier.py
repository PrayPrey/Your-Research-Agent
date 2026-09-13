import torch
import numpy as np
from sklearn.decomposition import PCA
from scipy.stats import ks_2samp
from typing import Tuple, Dict


class SVADDriftClassifier:
    def __init__(self, n_pca_components: int = 2, thresholds: dict = None):
        """Initialize PCA and detectors. thresholds: {MAJOR: 0.07, MINOR: 0.02, PATCH: 0.005}"""
        self.n_components = n_pca_components
        self.pca = PCA(n_components=n_pca_components, random_state=42)
        self.thresholds = thresholds or {"MAJOR": 0.07, "MINOR": 0.02, "PATCH": 0.005}
        self.ref_features_pca = None

    def fit_reference(self, ref_features: torch.Tensor) -> None:
        """Fit PCA on v_old. ref_features: [N, F]"""
        # Convert to numpy
        ref_np = ref_features.cpu().numpy()

        # Fit PCA
        self.pca.fit(ref_np)

        # Transform and store
        self.ref_features_pca = self.pca.transform(ref_np)

    def classify_version_change(self, new_features: torch.Tensor) -> Tuple[str, Dict[str, float]]:
        """Classify v_new. Returns: (label, {ks_score: float, mmd_score: float})"""
        if self.ref_features_pca is None:
            raise ValueError("Must call fit_reference() before classify_version_change()")

        # Transform new features
        new_np = new_features.cpu().numpy()
        new_features_pca = self.pca.transform(new_np)

        # Compute drift scores
        ks_score = self._compute_ks_score(new_features_pca)
        mmd_score = self._compute_mmd_score(new_features_pca)

        # Take maximum of both scores
        max_score = max(ks_score, mmd_score)

        # Classify based on thresholds
        if max_score >= self.thresholds["MAJOR"]:
            label = "MAJOR"
        elif max_score >= self.thresholds["MINOR"]:
            label = "MINOR"
        else:
            label = "PATCH"

        scores = {"ks_score": ks_score, "mmd_score": mmd_score, "max_score": max_score}

        return label, scores

    def _compute_ks_score(self, features: np.ndarray) -> float:
        """KS test on PCA features. features: [N, 2] -> ks_stat"""
        # Apply KS test on each PCA component
        ks_stats = []

        for i in range(self.n_components):
            ref_component = self.ref_features_pca[:, i]
            new_component = features[:, i]

            stat, pval = ks_2samp(ref_component, new_component)
            ks_stats.append(stat)

        # Apply Bonferroni correction by taking max statistic
        max_ks_stat = max(ks_stats)

        return max_ks_stat

    def _compute_mmd_score(self, features: np.ndarray) -> float:
        """MMD with Gaussian RBF kernel. features: [N, 2] -> mmd_stat"""
        # Convert to torch tensors
        X = torch.tensor(self.ref_features_pca, dtype=torch.float32)
        Y = torch.tensor(features, dtype=torch.float32)

        # Compute MMD with Gaussian RBF kernel
        mmd_value = self._mmd_rbf(X, Y)

        return mmd_value.item()

    def _mmd_rbf(self, X: torch.Tensor, Y: torch.Tensor, gamma: float = None) -> torch.Tensor:
        """Compute MMD with RBF kernel using median heuristic for bandwidth."""
        m = X.size(0)
        n = Y.size(0)

        # Compute pairwise distances for bandwidth estimation
        if gamma is None:
            XY = torch.cat([X, Y], dim=0)
            dists = torch.cdist(XY, XY, p=2)
            median_dist = torch.median(dists[dists > 0])
            gamma = 1.0 / (2 * median_dist ** 2)

        # Compute kernel matrices
        XX = self._gaussian_kernel(X, X, gamma)
        YY = self._gaussian_kernel(Y, Y, gamma)
        XY = self._gaussian_kernel(X, Y, gamma)

        # Compute MMD^2
        mmd_sq = XX.mean() + YY.mean() - 2 * XY.mean()

        return torch.sqrt(torch.clamp(mmd_sq, min=0))

    def _gaussian_kernel(self, X: torch.Tensor, Y: torch.Tensor, gamma: float) -> torch.Tensor:
        """Compute Gaussian RBF kernel matrix."""
        # Compute pairwise squared distances
        X_norm = (X ** 2).sum(1).view(-1, 1)
        Y_norm = (Y ** 2).sum(1).view(1, -1)
        dists_sq = X_norm + Y_norm - 2.0 * torch.mm(X, Y.T)

        # Apply Gaussian kernel
        return torch.exp(-gamma * dists_sq)
