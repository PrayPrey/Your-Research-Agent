"""
Unit tests for Operation-Specific Encoders (Task A-2)
"""

import pytest
import torch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from models.operation_encoders import SANEConvEncoder, UNFAttentionEncoder, MLPEncoder


class TestSANEConvEncoder:
    """Test SANEConvEncoder"""

    def test_initialization(self):
        """Test encoder initialization"""
        encoder = SANEConvEncoder(d_out=256, d_token=64)
        assert encoder.d_out == 256
        assert encoder.d_token == 64

    def test_spatial_tokenization(self):
        """Test spatial tokenization of conv weights"""
        encoder = SANEConvEncoder(d_out=256, d_token=64)

        # Test conv weight: [C_out=16, C_in=3, K=3, K=3]
        weight = torch.randn(16, 3, 3, 3)
        tokens = encoder.spatial_tokenize(weight)

        # Should produce N_tokens = 16*3*3*3 = 432 tokens
        assert tokens.shape == (432, 64), f"Expected (432, 64), got {tokens.shape}"

    def test_forward_single_layer(self):
        """Test forward pass with single conv layer"""
        encoder = SANEConvEncoder(d_out=256, d_token=64)

        # Single conv layer
        conv_weights = [torch.randn(16, 3, 3, 3)]
        output = encoder(conv_weights)

        assert output.shape == (256,), f"Expected (256,), got {output.shape}"

    def test_forward_multiple_layers(self):
        """Test forward pass with multiple conv layers"""
        encoder = SANEConvEncoder(d_out=256, d_token=64)

        # Multiple conv layers with different shapes
        conv_weights = [
            torch.randn(16, 3, 3, 3),
            torch.randn(32, 16, 3, 3),
            torch.randn(64, 32, 3, 3)
        ]
        output = encoder(conv_weights)

        assert output.shape == (256,), f"Expected (256,), got {output.shape}"

    def test_empty_input(self):
        """Test with no conv layers"""
        encoder = SANEConvEncoder(d_out=256)
        output = encoder([])

        assert output.shape == (256,), f"Expected (256,), got {output.shape}"
        assert torch.all(output == 0), "Empty input should produce zero embedding"


class TestUNFAttentionEncoder:
    """Test UNFAttentionEncoder"""

    def test_initialization(self):
        """Test encoder initialization"""
        encoder = UNFAttentionEncoder(d_out=256, d_hidden=128)
        assert encoder.d_out == 256
        assert encoder.d_hidden == 128

    def test_equivariant_processing(self):
        """Test permutation-equivariant processing"""
        encoder = UNFAttentionEncoder(d_out=256, d_hidden=128)

        # Attention weight: [N_heads=8, D=64, D=64]
        weight = torch.randn(8, 64, 64)
        features = encoder.equivariant_process(weight)

        assert features.shape == (8, 128), f"Expected (8, 128), got {features.shape}"

    def test_forward_single_layer(self):
        """Test forward pass with single attention layer"""
        encoder = UNFAttentionEncoder(d_out=256, d_hidden=128)

        # Single attention layer
        attn_weights = [torch.randn(8, 64, 64)]
        output = encoder(attn_weights)

        assert output.shape == (256,), f"Expected (256,), got {output.shape}"

    def test_forward_non_square(self):
        """Test with non-square attention matrices (Q-K-V)"""
        encoder = UNFAttentionEncoder(d_out=256, d_hidden=128)

        # Non-square: [N_heads, D_qk, D_v]
        attn_weights = [torch.randn(8, 64, 32)]
        output = encoder(attn_weights)

        assert output.shape == (256,), f"Expected (256,), got {output.shape}"

    def test_empty_input(self):
        """Test with no attention layers"""
        encoder = UNFAttentionEncoder(d_out=256)
        output = encoder([])

        assert output.shape == (256,), f"Expected (256,), got {output.shape}"
        assert torch.all(output == 0), "Empty input should produce zero embedding"


class TestMLPEncoder:
    """Test MLPEncoder"""

    def test_initialization(self):
        """Test encoder initialization"""
        encoder = MLPEncoder(d_out=256, d_hidden=128)
        assert encoder.d_out == 256
        assert encoder.d_hidden == 128

    def test_embed_weight_matrix(self):
        """Test embedding single weight matrix"""
        encoder = MLPEncoder(d_out=256, d_hidden=128)

        # FC layer weight: [D_out=512, D_in=256]
        weight = torch.randn(512, 256)
        embedding = encoder.embed_weight_matrix(weight)

        assert embedding.shape == (128,), f"Expected (128,), got {embedding.shape}"

    def test_forward_single_layer(self):
        """Test forward pass with single MLP layer"""
        encoder = MLPEncoder(d_out=256, d_hidden=128)

        # Single MLP layer
        mlp_weights = [torch.randn(512, 256)]
        output = encoder(mlp_weights)

        assert output.shape == (256,), f"Expected (256,), got {output.shape}"

    def test_forward_multiple_layers(self):
        """Test forward pass with multiple MLP layers"""
        encoder = MLPEncoder(d_out=256, d_hidden=128)

        # Multiple MLP layers
        mlp_weights = [
            torch.randn(512, 256),
            torch.randn(256, 128),
            torch.randn(128, 10)
        ]
        output = encoder(mlp_weights)

        assert output.shape == (256,), f"Expected (256,), got {output.shape}"

    def test_empty_input(self):
        """Test with no MLP layers"""
        encoder = MLPEncoder(d_out=256)
        output = encoder([])

        assert output.shape == (256,), f"Expected (256,), got {output.shape}"
        assert torch.all(output == 0), "Empty input should produce zero embedding"


class TestOperationEncoderIntegration:
    """Test integration of all operation encoders"""

    def test_consistent_output_dimensions(self):
        """Test all encoders produce same output dimension"""
        d_out = 256

        conv_enc = SANEConvEncoder(d_out=d_out)
        attn_enc = UNFAttentionEncoder(d_out=d_out)
        mlp_enc = MLPEncoder(d_out=d_out)

        # Test inputs
        conv_weights = [torch.randn(16, 3, 3, 3)]
        attn_weights = [torch.randn(8, 64, 64)]
        mlp_weights = [torch.randn(512, 256)]

        z_conv = conv_enc(conv_weights)
        z_attn = attn_enc(attn_weights)
        z_mlp = mlp_enc(mlp_weights)

        assert z_conv.shape == z_attn.shape == z_mlp.shape == (d_out,)

    def test_mean_aggregation(self):
        """Test mean aggregation across operation types"""
        d_out = 256

        conv_enc = SANEConvEncoder(d_out=d_out)
        attn_enc = UNFAttentionEncoder(d_out=d_out)
        mlp_enc = MLPEncoder(d_out=d_out)

        # Test inputs
        conv_weights = [torch.randn(16, 3, 3, 3)]
        attn_weights = [torch.randn(8, 64, 64)]
        mlp_weights = [torch.randn(512, 256)]

        z_conv = conv_enc(conv_weights)
        z_attn = attn_enc(attn_weights)
        z_mlp = mlp_enc(mlp_weights)

        # Mean pooling across operations
        z_op = torch.stack([z_conv, z_attn, z_mlp], dim=0).mean(dim=0)

        assert z_op.shape == (d_out,)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
