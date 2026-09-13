"""
Centered Kernel Alignment (CKA)
Measure representation similarity between models
"""

import torch
from typing import Dict

class CKAComputer:
    """Compute Centered Kernel Alignment between representation spaces."""

    @staticmethod
    def center_gram_matrix(K: torch.Tensor) -> torch.Tensor:
        """
        Center a Gram matrix.

        Args:
            K: [N, N] Gram matrix

        Returns:
            [N, N] centered Gram matrix
        """
        n = K.shape[0]
        H = torch.eye(n) - torch.ones(n, n) / n
        return H @ K @ H

    @staticmethod
    def compute_cka(repr_a: torch.Tensor, repr_b: torch.Tensor) -> float:
        """
        Compute CKA similarity between two representation spaces.

        Args:
            repr_a: [N, H] representations from model A
            repr_b: [N, H] representations from model B

        Returns:
            CKA score in [0, 1] (0=divergent, 1=identical)
        """
        # Center representations
        repr_a = repr_a - repr_a.mean(dim=0, keepdim=True)
        repr_b = repr_b - repr_b.mean(dim=0, keepdim=True)

        # Compute Gram matrices
        K_a = repr_a @ repr_a.T  # [N, N]
        K_b = repr_b @ repr_b.T  # [N, N]

        # CKA formula: HSIC(K_a, K_b) / sqrt(HSIC(K_a, K_a) * HSIC(K_b, K_b))
        hsic_ab = (K_a * K_b).sum()
        hsic_aa = (K_a * K_a).sum()
        hsic_bb = (K_b * K_b).sum()

        cka = hsic_ab / torch.sqrt(hsic_aa * hsic_bb)
        return cka.item()

    def compute_all_pairs(
        self,
        repr_joint: torch.Tensor,
        repr_dpo: torch.Tensor,
        repr_attr: torch.Tensor
    ) -> Dict[str, float]:
        """
        Compute CKA for all model pairs.

        Args:
            repr_joint: Joint model representations
            repr_dpo: DPO-only model representations
            repr_attr: Attr-only model representations

        Returns:
            Dictionary of CKA scores
        """
        return {
            'joint_dpo': self.compute_cka(repr_joint, repr_dpo),
            'joint_attr': self.compute_cka(repr_joint, repr_attr),
            'dpo_attr': self.compute_cka(repr_dpo, repr_attr),
            'joint_joint': 1.0,  # Self-similarity
            'dpo_dpo': 1.0,
            'attr_attr': 1.0
        }
