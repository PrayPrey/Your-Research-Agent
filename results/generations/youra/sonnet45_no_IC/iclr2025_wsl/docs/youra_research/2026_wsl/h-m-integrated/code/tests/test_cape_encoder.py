"""
Unit tests for CAPE Encoder (Task A-6)
"""

import pytest
import torch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from models.cape_encoder import CAPEEncoder


class TestCAPEEncoder:
    """Test full CAPE encoder"""

    def test_initialization_full(self):
        """Test initialization with all components enabled"""
        encoder = CAPEEncoder(
            d_z=256,
            d_arch=64,
            enable_operation_encoders=True,
            enable_contrastive=True,
            enable_gnn=True
        )

        assert hasattr(encoder, 'conv_encoder')
        assert hasattr(encoder, 'attn_encoder')
        assert hasattr(encoder, 'mlp_encoder')
        assert hasattr(encoder, 'projector')
        assert hasattr(encoder, 'gnn')
        assert hasattr(encoder, 'alpha')

    def test_initialization_ablation(self):
        """Test initialization with components disabled"""
        # Operation-only variant
        encoder = CAPEEncoder(
            enable_operation_encoders=True,
            enable_contrastive=False,
            enable_gnn=False
        )

        assert hasattr(encoder, 'conv_encoder')
        assert not hasattr(encoder, 'projector')
        assert not hasattr(encoder, 'gnn')

    def test_get_operation_embeddings(self):
        """Test operation embedding extraction"""
        encoder = CAPEEncoder(d_z=256, enable_operation_encoders=True)

        model_weights = {
            "conv": [torch.randn(16, 3, 3, 3)],
            "attention": [torch.randn(8, 64, 64)],
            "mlp": [torch.randn(512, 256)]
        }

        z_op = encoder.get_operation_embeddings(model_weights)

        assert z_op.shape == (256,), f"Expected (256,), got {z_op.shape}"

    def test_get_contrastive_embeddings(self):
        """Test contrastive projection"""
        encoder = CAPEEncoder(d_z=256, enable_contrastive=True)

        z_op = torch.randn(256)
        z_proj = encoder.get_contrastive_embeddings(z_op)

        assert z_proj.shape == (256,)
        # Should be L2 normalized
        norm = torch.norm(z_proj, p=2)
        assert torch.allclose(norm, torch.tensor(1.0), atol=1e-5)

    def test_forward_without_gnn(self):
        """Test forward pass without architecture graph"""
        encoder = CAPEEncoder(
            d_z=256,
            enable_operation_encoders=True,
            enable_contrastive=True,
            enable_gnn=False
        )

        model_weights = {
            "conv": [torch.randn(16, 3, 3, 3)],
            "attention": [torch.randn(8, 64, 64)],
            "mlp": [torch.randn(512, 256)]
        }

        z_final = encoder(model_weights, arch_graph=None)

        assert z_final.shape == (256,)

    def test_forward_with_gnn(self):
        """Test forward pass with architecture graph"""
        encoder = CAPEEncoder(
            d_z=256,
            d_arch=64,
            enable_operation_encoders=True,
            enable_contrastive=True,
            enable_gnn=True
        )

        model_weights = {
            "conv": [torch.randn(16, 3, 3, 3)],
            "attention": [torch.randn(8, 64, 64)],
            "mlp": [torch.randn(512, 256)]
        }

        # Mock architecture graph
        node_features = torch.randn(10, 64)  # 10 nodes, d_arch=64
        edge_index = torch.tensor([[0, 1, 2], [1, 2, 3]], dtype=torch.long)  # 3 edges
        arch_graph = (node_features, edge_index)

        z_final = encoder(model_weights, arch_graph=arch_graph)

        assert z_final.shape == (256,)

    def test_compute_infonce_loss(self):
        """Test InfoNCE loss computation"""
        encoder = CAPEEncoder(d_z=256, enable_contrastive=True)

        # Batch of normalized embeddings
        z_proj = torch.randn(8, 256)
        z_proj = torch.nn.functional.normalize(z_proj, p=2, dim=-1)

        loss = encoder.compute_infonce_loss(z_proj)

        assert loss.dim() == 0, "Loss should be scalar"
        assert loss.item() >= 0, "Loss should be non-negative"

    def test_diagnostic_metrics(self):
        """Test diagnostic metrics computation"""
        encoder = CAPEEncoder(
            d_z=256,
            enable_operation_encoders=True,
            enable_gnn=True
        )

        model_weights = {
            "conv": [torch.randn(16, 3, 3, 3)],
            "attention": [torch.randn(8, 64, 64)],
            "mlp": [torch.randn(512, 256)]
        }

        diagnostics = encoder.get_diagnostic_metrics(model_weights)

        assert "conv_attn_similarity" in diagnostics
        assert "alpha" in diagnostics
        assert -1 <= diagnostics["conv_attn_similarity"] <= 1, "Cosine similarity should be in [-1, 1]"

    def test_batched_forward(self):
        """Test batched forward pass (for training)"""
        encoder = CAPEEncoder(d_z=256, enable_operation_encoders=True, enable_contrastive=True)

        # Simulate batch processing
        batch_embeddings = []
        for _ in range(4):  # Batch size 4
            model_weights = {
                "conv": [torch.randn(16, 3, 3, 3)],
                "attention": [torch.randn(8, 64, 64)],
                "mlp": [torch.randn(512, 256)]
            }
            z_final = encoder(model_weights)
            batch_embeddings.append(z_final)

        z_batch = torch.stack(batch_embeddings, dim=0)

        assert z_batch.shape == (4, 256), f"Expected (4, 256), got {z_batch.shape}"

    def test_alpha_parameter_learnable(self):
        """Test that alpha parameter is learnable"""
        encoder = CAPEEncoder(d_z=256, enable_gnn=True)

        # Check alpha is a parameter
        assert isinstance(encoder.alpha, torch.nn.Parameter)
        assert encoder.alpha.requires_grad, "Alpha should require gradients"

    def test_empty_model_weights(self):
        """Test handling of empty model weights"""
        encoder = CAPEEncoder(d_z=256)

        model_weights = {"conv": [], "attention": [], "mlp": []}
        z_final = encoder(model_weights)

        assert z_final.shape == (256,)


class TestCAPEAblationVariants:
    """Test different ablation variants"""

    def test_sne_baseline_equivalent(self):
        """Test that disabling all components acts like SNE baseline"""
        encoder = CAPEEncoder(
            d_z=256,
            enable_operation_encoders=False,
            enable_contrastive=False,
            enable_gnn=False
        )

        model_weights = {
            "conv": [torch.randn(16, 3, 3, 3)],
            "attention": [torch.randn(8, 64, 64)],
            "mlp": [torch.randn(512, 256)]
        }

        z_final = encoder(model_weights)

        assert z_final.shape == (256,)

    def test_operation_only_variant(self):
        """Test operation-only variant (no contrastive, no GNN)"""
        encoder = CAPEEncoder(
            d_z=256,
            enable_operation_encoders=True,
            enable_contrastive=False,
            enable_gnn=False
        )

        model_weights = {
            "conv": [torch.randn(16, 3, 3, 3)],
            "attention": [torch.randn(8, 64, 64)],
            "mlp": [torch.randn(512, 256)]
        }

        z_final = encoder(model_weights)

        assert z_final.shape == (256,)

    def test_op_contrastive_variant(self):
        """Test operation + contrastive variant (no GNN)"""
        encoder = CAPEEncoder(
            d_z=256,
            enable_operation_encoders=True,
            enable_contrastive=True,
            enable_gnn=False
        )

        model_weights = {
            "conv": [torch.randn(16, 3, 3, 3)],
            "attention": [torch.randn(8, 64, 64)],
            "mlp": [torch.randn(512, 256)]
        }

        z_final = encoder(model_weights)

        assert z_final.shape == (256,)
        # Should be normalized from contrastive projection
        norm = torch.norm(z_final, p=2)
        assert torch.allclose(norm, torch.tensor(1.0), atol=1e-5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
