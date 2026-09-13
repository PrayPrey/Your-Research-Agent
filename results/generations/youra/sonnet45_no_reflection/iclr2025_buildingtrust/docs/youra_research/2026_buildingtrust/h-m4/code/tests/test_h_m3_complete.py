"""Complete test suite for H-M3 Multi-Dimensional Correlation Analysis"""
import pytest
import torch
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test A-1: Config
def test_config_creation():
    """Test H_M3_Config instantiation"""
    from config_h_m3 import H_M3_Config, get_default_config
    config = get_default_config()
    assert config.project_name == "h-m3-cross-dimensional-correlation"
    assert config.training_samples == 500
    assert len(config.dimensions) == 3
    assert len(config.layers_to_analyze) == 24  # __post_init__ should generate 24 layers

def test_config_dimensions():
    """Test default dimensions"""
    from config_h_m3 import get_default_dimensions
    dims = get_default_dimensions()
    assert dims == ["truthfulness", "fairness", "robustness"]

# Test A-2: Multi-Dimensional Data Pipeline
def test_multi_dimensional_dataset_init():
    """Test MultiDimensionalDataset initialization"""
    from data_multi_dimensional import MultiDimensionalDataset
    from transformers import AutoTokenizer
    
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    dataset = MultiDimensionalDataset(tokenizer, ["truthfulness", "fairness", "robustness"])
    assert dataset.dimensions == ["truthfulness", "fairness", "robustness"]
    assert len(dataset.datasets) == 0  # Initially empty

def test_prepare_tokens():
    """Test tokenization"""
    from data_multi_dimensional import MultiDimensionalDataset
    from transformers import AutoTokenizer
    from datasets import Dataset
    
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    dataset_loader = MultiDimensionalDataset(tokenizer, ["truthfulness"])
    
    # Create mock dataset
    mock_ds = Dataset.from_dict({"question": ["What is 2+2?", "Who is president?"]})
    tokens = dataset_loader.prepare_tokens(mock_ds, text_field="question")
    
    assert tokens.shape[0] == 2  # 2 samples
    assert tokens.shape[1] <= 512  # Max length

# Test A-3: BBQ Evaluator
def test_bbq_evaluator_init():
    """Test BBQEvaluator initialization"""
    from evaluators import BBQEvaluator
    from transformers import AutoModel, AutoTokenizer
    
    model = AutoModel.from_pretrained("gpt2")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    evaluator = BBQEvaluator(model, tokenizer)
    
    assert evaluator.model is not None
    assert evaluator.tokenizer is not None

# Test A-4: AdvGLUE Evaluator
def test_advglue_evaluator_init():
    """Test AdvGLUEEvaluator initialization"""
    from evaluators import AdvGLUEEvaluator
    from transformers import AutoModel, AutoTokenizer
    
    model = AutoModel.from_pretrained("gpt2")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    evaluator = AdvGLUEEvaluator(model, tokenizer)
    
    assert evaluator.model is not None
    assert evaluator.tokenizer is not None

# Test A-5: Multi-Dimensional Orchestrator
def test_multi_dimensional_evaluator():
    """Test MultiDimensionalEvaluator setup"""
    from evaluators import MultiDimensionalEvaluator
    from transformers import AutoModel, AutoTokenizer
    
    model = AutoModel.from_pretrained("gpt2")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    evaluator = MultiDimensionalEvaluator(model, tokenizer, ["truthfulness", "fairness", "robustness"])
    
    assert len(evaluator.evaluators) == 3
    assert "truthfulness" in evaluator.evaluators
    assert "fairness" in evaluator.evaluators
    assert "robustness" in evaluator.evaluators

# Test A-6: Cross-Dimensional Correlation Analyzer
def test_correlation_analyzer_deltas():
    """Test delta computation"""
    from correlation_analyzer import CrossDimensionalCorrelationAnalyzer
    
    analyzer = CrossDimensionalCorrelationAnalyzer(["truthfulness", "fairness", "robustness"])
    pre_scores = {"truthfulness": 0.5, "fairness": 0.6, "robustness": 0.55}
    post_scores = {"truthfulness": 0.6, "fairness": 0.65, "robustness": 0.58}
    
    deltas = analyzer.compute_deltas(pre_scores, post_scores)
    
    assert deltas["truthfulness"] == pytest.approx(0.1)
    assert deltas["fairness"] == pytest.approx(0.05)
    assert deltas["robustness"] == pytest.approx(0.03)

def test_pearson_correlation():
    """Test Pearson correlation computation"""
    from correlation_analyzer import CrossDimensionalCorrelationAnalyzer
    
    analyzer = CrossDimensionalCorrelationAnalyzer(["truthfulness", "fairness"])
    deltas1 = [0.1, 0.2, 0.15]
    deltas2 = [0.05, 0.1, 0.08]
    
    r, p = analyzer.compute_pearson_correlation(deltas1, deltas2)
    
    assert isinstance(r, float)
    assert isinstance(p, float)
    assert -1 <= r <= 1

def test_correlation_all_pairs():
    """Test all-pairs correlation"""
    from correlation_analyzer import CrossDimensionalCorrelationAnalyzer
    
    analyzer = CrossDimensionalCorrelationAnalyzer(["truthfulness", "fairness", "robustness"])
    deltas_per_seed = {
        42: {"truthfulness": 0.1, "fairness": 0.05, "robustness": 0.03},
        43: {"truthfulness": 0.12, "fairness": 0.06, "robustness": 0.04},
        44: {"truthfulness": 0.11, "fairness": 0.055, "robustness": 0.035}
    }
    
    correlations = analyzer.compute_all_pairs(deltas_per_seed)
    
    assert len(correlations) == 3  # 3 pairs from 3 dimensions
    assert "truthfulness_vs_fairness" in correlations
    assert "truthfulness_vs_robustness" in correlations
    assert "fairness_vs_robustness" in correlations

# Test A-7: Permutation Test
def test_permutation_tester():
    """Test permutation test"""
    from correlation_analyzer import PermutationTester
    
    tester = PermutationTester(n_permutations=100)
    deltas1 = [0.1, 0.2, 0.15]
    deltas2 = [0.05, 0.1, 0.08]
    
    p_perm = tester.permutation_test(deltas1, deltas2)
    
    assert isinstance(p_perm, float)
    assert 0 <= p_perm <= 1

# Test A-8: Layer-Wise Correlation
def test_layer_wise_correlation():
    """Test layer-wise correlation analysis"""
    from correlation_analyzer import LayerWiseCorrelationAnalyzer
    
    layers = ["layer_0", "layer_1", "layer_2"]
    dimensions = ["truthfulness", "fairness", "robustness"]
    analyzer = LayerWiseCorrelationAnalyzer(layers, dimensions)
    
    # Use different rep_changes for each layer
    rep_changes = {"layer_0": 0.15, "layer_1": 0.12, "layer_2": 0.18}
    perf_deltas = {
        "truthfulness": [0.1, 0.12, 0.11],
        "fairness": [0.05, 0.06, 0.055],
        "robustness": [0.03, 0.04, 0.035]
    }
    
    layer_corrs = analyzer.correlate_layer_with_dimensions(rep_changes, perf_deltas)
    
    assert len(layer_corrs) == 3  # 3 layers
    for layer in layers:
        assert layer in layer_corrs
        assert len(layer_corrs[layer]) == 3  # 3 dimensions

def test_identify_dimension_specific_layers():
    """Test dimension-specific layer identification"""
    from correlation_analyzer import LayerWiseCorrelationAnalyzer
    
    analyzer = LayerWiseCorrelationAnalyzer(["layer_0"], ["truthfulness", "fairness"])
    layer_correlations = {
        "layer_0": {
            "truthfulness": (0.8, 0.01),  # Significant
            "fairness": (0.1, 0.5)  # Not significant
        }
    }
    
    dim_layers = analyzer.identify_dimension_specific_layers(layer_correlations, threshold=0.05)
    
    # Check that layer_0 is identified for truthfulness
    assert "layer_0" in dim_layers["truthfulness"]
    assert "layer_0" not in dim_layers["fairness"]  # Not significant

# Test A-10: Visualization
def test_figure_generator_init():
    """Test H_M3_FigureGenerator initialization"""
    from visualize_h_m3 import H_M3_FigureGenerator
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = H_M3_FigureGenerator(tmpdir)
        assert generator.output_dir.exists()

def test_plot_correlation_scatter():
    """Test correlation scatter plot generation"""
    from visualize_h_m3 import H_M3_FigureGenerator
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = H_M3_FigureGenerator(tmpdir)
        deltas1 = [0.1, 0.2, 0.15]
        deltas2 = [0.05, 0.1, 0.08]
        
        generator.plot_correlation_scatter(
            deltas1, deltas2, "truthfulness", "fairness", 0.95, 0.01
        )
        
        output_file = generator.output_dir / "correlation_scatter.png"
        assert output_file.exists()

def test_plot_correlation_matrix():
    """Test correlation matrix plot generation"""
    from visualize_h_m3 import H_M3_FigureGenerator
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = H_M3_FigureGenerator(tmpdir)
        correlations = {
            "truthfulness_vs_fairness": (0.8, 0.01),
            "truthfulness_vs_robustness": (0.7, 0.02),
            "fairness_vs_robustness": (0.6, 0.05)
        }
        
        generator.plot_correlation_matrix(correlations)
        
        output_file = generator.output_dir / "correlation_matrix.png"
        assert output_file.exists()

# Test A-11: Main Orchestration
def test_set_seed():
    """Test seed setting"""
    from main_h_m3 import set_seed
    
    set_seed(42)
    r1 = torch.rand(5)
    
    set_seed(42)
    r2 = torch.rand(5)
    
    assert torch.allclose(r1, r2)

def test_main_imports():
    """Test main module imports"""
    import main_h_m3
    
    assert hasattr(main_h_m3, 'set_seed')
    assert hasattr(main_h_m3, 'setup_gpu')
    assert hasattr(main_h_m3, 'run_single_replicate')
    assert hasattr(main_h_m3, 'main')

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
