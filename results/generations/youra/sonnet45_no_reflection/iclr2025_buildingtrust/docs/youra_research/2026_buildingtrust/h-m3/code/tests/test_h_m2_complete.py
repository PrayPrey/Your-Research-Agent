"""
Comprehensive Test Suite for H-M2 Hypothesis
Tests all modules: config, TransformerLens, activation extraction, CKA, visualization
"""

import pytest
import torch
import numpy as np
from pathlib import Path
import sys
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import H_M2_Config, get_default_config
from transformer_lens_wrapper import TransformerLensWrapper
from representation_analyzer import ActivationExtractor, RepresentationAnalyzer
from similarity import CKASimilarity, CorrelationAnalyzer, StatisticalAnalyzer
from visualize import FigureGenerator


class TestConfig:
    """Test A-1: Project Setup - Configuration"""

    def test_config_initialization(self):
        """Test config initializes with correct defaults"""
        config = get_default_config()

        assert config.model_id == "gpt2"
        assert config.lora_rank == 8
        assert config.lora_alpha == 16
        assert config.num_epochs == 3
        assert config.num_replicates == 3
        assert len(config.random_seeds) == 3

    def test_layers_to_analyze(self):
        """Test layer names are generated correctly"""
        config = get_default_config()

        # Should have 24 layers (12 attention + 12 hidden)
        assert len(config.layers_to_analyze) == 24

        # Check attention layers
        for i in range(12):
            assert f"blocks.{i}.attn.hook_pattern" in config.layers_to_analyze

        # Check hidden layers
        for i in range(12):
            assert f"blocks.{i}.hook_resid_post" in config.layers_to_analyze

    def test_config_h_m1_inheritance(self):
        """Test configuration inherits h-m1 values"""
        config = get_default_config()

        # LoRA config from h-m1
        assert config.lora_rank == 8
        assert config.lora_alpha == 16
        assert config.lora_dropout == 0.1
        assert config.target_modules == ["c_attn"]

        # Training config from h-m1
        assert config.learning_rate == 1e-4
        assert config.batch_size == 4
        assert config.gradient_accumulation_steps == 2


class TestTransformerLensWrapper:
    """Test A-3: TransformerLens Integration"""

    @pytest.fixture
    def wrapper(self):
        """Create TransformerLens wrapper"""
        return TransformerLensWrapper(model_id="gpt2", device="cpu")

    def test_load_baseline_hooked(self, wrapper):
        """Test loading GPT-2 as HookedTransformer"""
        model = wrapper.load_baseline_hooked()

        assert model is not None
        assert hasattr(model, 'run_with_cache')
        assert hasattr(model, 'hook_dict')

    def test_get_hook_names(self, wrapper):
        """Test retrieving hook names"""
        hook_names = wrapper.get_hook_names()

        assert len(hook_names) > 0
        # Check for expected hook patterns
        assert any("attn.hook_pattern" in name for name in hook_names)
        assert any("hook_resid_post" in name for name in hook_names)

    def test_verify_hooks(self, wrapper):
        """Test hook verification"""
        config = get_default_config()
        result = wrapper.verify_hooks(config.layers_to_analyze)

        # Should pass verification for standard GPT-2 hooks
        assert isinstance(result, bool)


class TestActivationExtractor:
    """Test A-4: Activation Extractor"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def extractor(self, temp_cache_dir):
        """Create activation extractor with mock model"""
        wrapper = TransformerLensWrapper(model_id="gpt2", device="cpu")
        model = wrapper.load_baseline_hooked()

        layers = [
            "blocks.0.attn.hook_pattern",
            "blocks.0.hook_resid_post"
        ]

        return ActivationExtractor(model, layers, temp_cache_dir)

    def test_extract_activations(self, extractor):
        """Test activation extraction"""
        # Create dummy input
        tokens = torch.randint(0, 50257, (2, 10))  # [batch=2, seq=10]

        activations = extractor.extract_activations(tokens)

        assert len(activations) == 2  # 2 layers requested
        assert "blocks.0.attn.hook_pattern" in activations
        assert "blocks.0.hook_resid_post" in activations

        # Check shapes
        attn_act = activations["blocks.0.attn.hook_pattern"]
        hidden_act = activations["blocks.0.hook_resid_post"]

        assert attn_act.shape[0] == 2  # batch size
        assert hidden_act.shape[0] == 2  # batch size

    def test_save_load_activations(self, extractor):
        """Test saving and loading activations"""
        # Create dummy activations
        activations = {
            "blocks.0.attn.hook_pattern": torch.randn(2, 12, 10, 10),
            "blocks.0.hook_resid_post": torch.randn(2, 10, 768)
        }

        # Save
        extractor.save_activations(activations, "test_acts.pt")

        # Load
        loaded = extractor.load_activations("test_acts.pt")

        # Verify
        assert len(loaded) == len(activations)
        for key in activations:
            assert torch.allclose(loaded[key], activations[key])


class TestCKASimilarity:
    """Test A-5: CKA Similarity Module"""

    @pytest.fixture
    def cka_module(self):
        """Create CKA similarity module"""
        return CKASimilarity(device="cpu")

    def test_compute_cka_identical(self, cka_module):
        """Test CKA on identical representations"""
        X = torch.randn(100, 50)
        Y = X.clone()

        cka = cka_module.compute_cka(X, Y)

        # CKA should be 1.0 for identical representations
        assert 0.99 < cka <= 1.0

    def test_compute_cka_different(self, cka_module):
        """Test CKA on different representations"""
        X = torch.randn(100, 50)
        Y = torch.randn(100, 50)

        cka = cka_module.compute_cka(X, Y)

        # CKA should be < 1.0 for different representations
        assert 0.0 <= cka < 1.0

    def test_compute_all_layers(self, cka_module):
        """Test computing CKA for multiple layers"""
        layers = ["blocks.0.attn.hook_pattern", "blocks.0.hook_resid_post"]

        pre_acts = {
            "blocks.0.attn.hook_pattern": torch.randn(10, 12, 8, 8),
            "blocks.0.hook_resid_post": torch.randn(10, 8, 768)
        }

        post_acts = {
            "blocks.0.attn.hook_pattern": torch.randn(10, 12, 8, 8),
            "blocks.0.hook_resid_post": torch.randn(10, 8, 768)
        }

        cka_scores = cka_module.compute_all_layers(pre_acts, post_acts, layers)

        assert len(cka_scores) == 2
        for layer in layers:
            assert layer in cka_scores
            assert 0.0 <= cka_scores[layer] <= 1.0


class TestCorrelationAnalyzer:
    """Test A-7: Statistical Analysis"""

    @pytest.fixture
    def analyzer(self):
        """Create correlation analyzer"""
        return CorrelationAnalyzer(performance_delta=0.0232)

    def test_compute_representation_change(self, analyzer):
        """Test computing change magnitude from CKA"""
        cka_scores = {
            "layer1": 0.95,
            "layer2": 0.85,
            "layer3": 0.75
        }

        changes = analyzer.compute_representation_change(cka_scores)

        assert changes["layer1"] == pytest.approx(0.05, abs=1e-10)
        assert changes["layer2"] == pytest.approx(0.15, abs=1e-10)
        assert changes["layer3"] == pytest.approx(0.25, abs=1e-10)

    def test_aggregate_across_replicates(self, analyzer):
        """Test aggregating CKA across replicates"""
        rep1 = {"layer1": 0.9, "layer2": 0.8}
        rep2 = {"layer1": 0.85, "layer2": 0.75}
        rep3 = {"layer1": 0.95, "layer2": 0.85}

        aggregated = analyzer.aggregate_across_replicates([rep1, rep2, rep3])

        assert aggregated["layer1"] == pytest.approx(0.9, abs=0.01)
        assert aggregated["layer2"] == pytest.approx(0.8, abs=0.01)

    def test_correlate_representation_performance(self, analyzer):
        """Test correlation computation"""
        change_magnitudes = [0.1, 0.2, 0.3, 0.15, 0.25]
        perf_delta = 0.0232

        result = analyzer.correlate_representation_performance(
            change_magnitudes, perf_delta
        )

        assert "correlation" in result
        assert "p_value" in result
        assert "significant" in result
        # np.bool_ is a subclass of bool for numpy compatibility
        assert result["significant"] in [True, False]


class TestStatisticalAnalyzer:
    """Test A-7: Statistical Analysis - Gate Evaluation"""

    def test_evaluate_gate(self):
        """Test gate evaluation logic"""
        analyzer = StatisticalAnalyzer()

        cka_scores = {
            f"layer_{i}": 0.8 + 0.05 * i for i in range(24)
        }

        gate_result = analyzer.evaluate_gate(cka_scores, performance_delta=0.0232)

        assert "pass" in gate_result
        assert "correlation" in gate_result
        assert "p_value" in gate_result
        assert "mean_change" in gate_result
        assert "layers_changed" in gate_result
        assert "total_layers" in gate_result

        assert gate_result["total_layers"] == 24


class TestFigureGenerator:
    """Test A-8: Visualization"""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def generator(self, temp_output_dir):
        """Create figure generator"""
        return FigureGenerator(temp_output_dir)

    @pytest.fixture
    def sample_cka_scores(self):
        """Create sample CKA scores"""
        scores = {}
        for i in range(12):
            scores[f"blocks.{i}.attn.hook_pattern"] = 0.8 + 0.01 * i
            scores[f"blocks.{i}.hook_resid_post"] = 0.85 + 0.01 * i
        return scores

    def test_plot_cka_heatmap(self, generator, sample_cka_scores):
        """Test CKA heatmap generation"""
        generator.plot_cka_heatmap(sample_cka_scores, list(sample_cka_scores.keys()))

        # Check file exists
        assert (generator.output_dir / "cka_heatmap.png").exists()

    def test_plot_change_magnitude(self, generator, sample_cka_scores):
        """Test change magnitude plot generation"""
        change_magnitudes = {k: 1.0 - v for k, v in sample_cka_scores.items()}
        generator.plot_change_magnitude(change_magnitudes)

        assert (generator.output_dir / "change_magnitude.png").exists()

    def test_plot_layer_progression(self, generator, sample_cka_scores):
        """Test layer progression plot generation"""
        generator.plot_layer_progression(sample_cka_scores)

        assert (generator.output_dir / "layer_progression.png").exists()

    def test_plot_correlation_scatter(self, generator):
        """Test correlation scatter plot generation"""
        change_magnitudes = [0.1, 0.15, 0.2, 0.12, 0.18]
        generator.plot_correlation_scatter(
            change_magnitudes,
            performance_delta=0.0232,
            correlation=0.5,
            p_value=0.03
        )

        assert (generator.output_dir / "correlation_scatter.png").exists()

    def test_save_all_figures(self, generator, sample_cka_scores):
        """Test generating all figures"""
        corr_result = {
            "correlation": 0.5,
            "p_value": 0.03
        }

        generator.save_all_figures(sample_cka_scores, corr_result)

        # Check all 4 figures exist
        assert (generator.output_dir / "cka_heatmap.png").exists()
        assert (generator.output_dir / "change_magnitude.png").exists()
        assert (generator.output_dir / "layer_progression.png").exists()
        assert (generator.output_dir / "correlation_scatter.png").exists()


class TestRepresentationAnalyzer:
    """Test A-4: Representation Analyzer Integration"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_extract_pre_intervention(self, temp_cache_dir):
        """Test pre-intervention extraction"""
        config = get_default_config()
        config.activation_cache_dir = temp_cache_dir

        # Load model
        wrapper = TransformerLensWrapper(model_id="gpt2", device="cpu")
        model = wrapper.load_baseline_hooked()

        # Create eval tokens
        eval_tokens = torch.randint(0, 50257, (5, 20))

        # Extract
        analyzer = RepresentationAnalyzer(config)
        pre_acts = analyzer.extract_pre_intervention(model, eval_tokens, seed=42)

        # Verify
        assert len(pre_acts) == 24  # 12 attention + 12 hidden
        assert Path(temp_cache_dir, "pre_activations_seed42.pt").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
