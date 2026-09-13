# Configuration Document: H-M1 Feature-Ranking Correlation Analysis

**Date:** 2026-07-13
**Hypothesis:** H-M1 (MECHANISM)
**Type:** Statistical Correlation Analysis
**Tier:** STANDARD (Data processing pipeline)

Applied: Standard Python Statistical Analysis Pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config patterns verified from H-E1 implementation
**Config Files Found:** `h-e1/code/collect_benchmarks.py` (hardcoded dict pattern)
**Pattern Used:** Hardcoded dict (consistent with H-E1)

**Key Findings:**
- H-E1 uses hardcoded dict in `main()` function
- Output path: `output/benchmarks_collection.jsonl`
- Config structure: single dict with all parameters
- No dataclass pattern found in H-E1 code

---

## Inherited Configuration (Base Hypothesis)

### H-E1 Output Format (From Actual Code)

The following data schema is inherited from H-E1:

```python
# From: h-e1/code/collect_benchmarks.py (lines 92-103)
BENCHMARK_SCHEMA = {
    'benchmark_id': str,          # Format: "ogb_arxiv" or "pwc_dataset_id"
    'dataset_name': str,          # Original dataset name
    'domain': str,                # "vision", "time-series", "tabular", "graph", "federated-learning"
    'sample_size': int | None,    # Total samples (may be None for some sources)
    'dimensionality': int | None, # Feature count (may be None)
    'num_classes': int | None,    # Target classes (may be None)
    'method_rankings': {          # Method performance data
        'MethodName': {
            'family': str,        # "Linear", "RNN", "Polynomial", "Augmentation"
            'accuracy': float,    # Raw accuracy score
            'ranking_percentile': float  # Percentile rank 0-100
        }
    },
    'source_paper': str,
    'year': int
}
```

**Input Data Path (Verified):**
- Location: `../h-e1/code/output/benchmarks_collection.jsonl`
- Format: JSONL (one JSON object per line)
- Expected Count: ~10-20 benchmarks (H-E1 POC collects verified sources)

---

## M1-4: Tier 2 Features [Complexity: 9, Budget: 2]

Applied: Hardcoded dict pattern for domain-specific feature configuration

### Configuration (Python Dict)

```python
# Tier 2 feature computation configuration
TIER2_CONFIG = {
    # Domain-specific feature definitions
    'vision_features': {
        'image_resolution': lambda b: b.get('dimensionality'),  # Proxy: use dimensionality
        'channel_count': lambda b: 3 if b.get('domain') == 'vision' else None
    },
    
    'nlp_features': {
        'sequence_length': lambda b: None,  # Not available in H-E1 data
        'vocabulary_size': lambda b: None
    },
    
    'tabular_features': {
        'feature_variance': lambda b: None,  # Requires raw data access
        'categorical_ratio': lambda b: None
    },
    
    'graph_features': {
        'edge_density': lambda b: None,     # Not available in H-E1 data
        'avg_degree': lambda b: None
    },
    
    # Domains to attempt Tier 2 computation
    'enabled_domains': ['vision', 'graph', 'tabular', 'time-series'],
    
    # Tier 2 computation timeout per benchmark (seconds)
    'computation_timeout': 5,
    
    # Skip Tier 2 if missing metadata
    'skip_on_missing_metadata': True
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Domain classifier | Map H-E1 domain strings to Tier 2 feature sets |
| C-4-2 | Feature extractors | Implement domain-specific feature extraction with missing data handling |

---

## M1-8: Visualizations [Complexity: 9, Budget: 2]

Applied: Matplotlib/Seaborn configuration for scientific figures

### Configuration (Python Dict)

```python
# Visualization configuration
VISUALIZATION_CONFIG = {
    # Figure output settings
    'output_dir': '../figures',
    'figure_dpi': 300,
    'figure_format': 'png',
    
    # Style settings
    'style': 'seaborn-v0_8-darkgrid',  # Matplotlib 3.6+ style name
    'context': 'paper',                # Seaborn context
    'palette': 'husl',                 # Color palette
    'font_scale': 1.2,
    
    # Figure-specific settings
    'gate_metrics_plot': {
        'figsize': (10, 6),
        'threshold_color': 'red',
        'threshold_linestyle': '--',
        'bar_color': 'steelblue'
    },
    
    'heatmap_plot': {
        'figsize': (12, 8),
        'cmap': 'coolwarm',
        'center': 0.0,
        'vmin': -1.0,
        'vmax': 1.0,
        'annot': True,
        'fmt': '.2f'
    },
    
    'significance_plot': {
        'figsize': (10, 5),
        'threshold_color': 'orange',
        'bar_color': 'teal'
    },
    
    'scatter_plot': {
        'figsize': (15, 5),
        'subplot_cols': 3,
        'marker_size': 50,
        'marker_alpha': 0.6,
        'regression_color': 'red'
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Gate metrics plot | Bar chart of top correlations vs ρ=0.3 threshold |
| C-8-2 | Correlation heatmap | Feature-method correlation matrix with significance markers |

---

## Complete Analysis Configuration

```python
# Main configuration for run_analysis.py
ANALYSIS_CONFIG = {
    # Data source (from H-E1)
    'h_e1_data_path': '../h-e1/code/output/benchmarks_collection.jsonl',
    
    # Correlation thresholds
    'alpha': 0.05,                    # p-value significance threshold
    'rho_threshold': 0.3,             # Spearman correlation threshold (moderate correlation)
    
    # Feature specifications
    'tier1_features': [
        'sample_size',
        'dimensionality', 
        'num_classes',
        'class_imbalance'
    ],
    
    'tier2_enabled': True,            # Enable Tier 2 feature computation
    'tier2_config': TIER2_CONFIG,
    
    # Method family specification
    'method_families': ['Linear', 'RNN', 'Polynomial', 'Augmentation'],
    
    # Gate criteria
    'min_significant_pairs': 3,       # Success requires ≥3 significant correlations
    'max_inverse_correlations': 0,    # Flag if any significant negative correlations
    
    # Output paths
    'output_dir': './output',
    'features_csv': './output/features.csv',
    'rankings_csv': './output/rankings.csv',
    'correlations_json': './output/correlations.json',
    'summary_json': './output/summary_stats.json',
    
    # Visualization
    'figures_dir': '../figures',
    'visualization_config': VISUALIZATION_CONFIG,
    
    # Error handling
    'skip_benchmarks_with_missing_rankings': True,
    'skip_features_with_zero_variance': True,
    'log_file': './output/analysis.log'
}
```

---

## Feature Computation Settings

```python
# Tier 1 (universal) feature computation
TIER1_COMPUTATION = {
    'sample_size': {
        'source_field': 'sample_size',
        'default_value': None,
        'validation': lambda x: x > 0 if x is not None else False
    },
    
    'dimensionality': {
        'source_field': 'dimensionality',
        'default_value': None,
        'validation': lambda x: x > 0 if x is not None else False
    },
    
    'num_classes': {
        'source_field': 'num_classes',
        'default_value': None,
        'validation': lambda x: x >= 2 if x is not None else False
    },
    
    'class_imbalance': {
        'computation': 'gini_coefficient',
        'requires': 'method_rankings',
        'fallback': 0.0,  # Assume balanced if no data
        'note': 'Computed from method accuracy distribution as proxy'
    }
}
```

---

## Correlation Analysis Settings

```python
# Spearman correlation configuration
CORRELATION_CONFIG = {
    # Statistical test parameters
    'test_type': 'two-tailed',        # Two-tailed p-value test
    'alpha': 0.05,                     # Significance level
    'rho_threshold': 0.3,              # Effect size threshold
    
    # Correlation computation
    'method': 'spearman',              # scipy.stats.spearmanr
    'handle_ties': 'average',          # Tie-breaking method
    'nan_policy': 'omit',              # Skip pairs with NaN values
    
    # Multiple testing correction (optional)
    'apply_bonferroni': False,         # Set True if >30 pairs tested
    'bonferroni_alpha': 0.05,
    
    # Result filtering
    'filter_significant_only': False,  # Report all pairs in JSON
    'min_valid_samples': 10,           # Minimum benchmarks for valid correlation
    
    # Inverse correlation detection
    'flag_inverse_threshold': -0.3,    # Flag negative correlations below this
    'inverse_warning_enabled': True
}
```

---

## Gate Decision Logic

```python
# Success criteria configuration
GATE_CONFIG = {
    'primary_threshold': {
        'min_significant_pairs': 3,
        'rho_threshold': 0.3,
        'p_threshold': 0.05
    },
    
    'gate_levels': {
        'PASS': lambda metrics: metrics['significant_count'] >= 3,
        'PARTIAL': lambda metrics: 1 <= metrics['significant_count'] < 3,
        'FAIL': lambda metrics: metrics['significant_count'] == 0
    },
    
    'additional_checks': {
        'warn_on_inverse': True,
        'min_mean_abs_rho': 0.15,      # Diagnostic: overall correlation strength
        'min_features_computed': 4,     # At least Tier 1 features must succeed
        'min_methods_available': 2      # Need at least 2 method families
    }
}
```

---

## Validation Logic

```python
# Data validation configuration
VALIDATION_CONFIG = {
    # Input data validation
    'min_benchmarks': 5,               # Minimum for statistical analysis
    'required_fields': ['benchmark_id', 'domain', 'method_rankings'],
    
    # Feature validation
    'allow_missing_features': True,
    'max_missing_rate': 0.5,           # Warn if >50% missing for a feature
    
    # Rankings validation
    'min_methods_per_benchmark': 2,
    'validate_percentile_range': True, # Check 0-100 range
    
    # Correlation validation
    'check_numerical_stability': True,
    'warn_on_zero_variance': True,
    'warn_on_perfect_correlation': True  # ρ = ±1.0 may indicate data issues
}
```

---

## Error Handling Configuration

```python
# Error handling strategy (STANDARD tier)
ERROR_HANDLING = {
    # Critical errors (raise exception)
    'critical': [
        'h_e1_data_not_found',
        'invalid_jsonl_format',
        'no_valid_benchmarks',
        'scipy_import_error'
    ],
    
    # Warnings (log and continue)
    'warnings': [
        'missing_tier2_features',
        'insufficient_method_rankings',
        'zero_variance_feature',
        'high_missing_rate'
    ],
    
    # Logging configuration
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(levelname)s - %(message)s',
    'log_to_console': True,
    'log_to_file': True,
    'log_file_path': './output/analysis.log'
}
```

---

## Usage Example (Phase 4 Implementation)

```python
# Main script: code/run_analysis.py
from load_data import BenchmarkDataLoader
from compute_features import FeatureAggregator, Tier1FeatureComputer, Tier2FeatureComputer
from analyze_correlations import SpearmanCorrelator, CorrelationReporter
from visualize import generate_all_figures

def main():
    # Load configuration
    config = ANALYSIS_CONFIG
    
    # Step 1: Load H-E1 data
    loader = BenchmarkDataLoader(config['h_e1_data_path'])
    benchmarks = loader.load_benchmarks()
    print(f"Loaded {len(benchmarks)} benchmarks from H-E1")
    
    # Step 2: Compute features
    tier1 = Tier1FeatureComputer()
    tier2 = Tier2FeatureComputer(config['tier2_config'])
    aggregator = FeatureAggregator(tier1, tier2)
    features_df = aggregator.compute_all_features(benchmarks)
    features_df.to_csv(config['features_csv'], index=False)
    print(f"Computed {len(features_df.columns)} features")
    
    # Step 3: Extract rankings
    rankings_df = loader.extract_method_rankings(benchmarks)
    rankings_df.to_csv(config['rankings_csv'], index=False)
    print(f"Extracted rankings for {len(rankings_df.columns)} method families")
    
    # Step 4: Correlation analysis
    correlator = SpearmanCorrelator(
        alpha=config['alpha'],
        rho_threshold=config['rho_threshold']
    )
    correlations = correlator.compute_correlation_matrix(features_df, rankings_df)
    significant_correlations = correlator.filter_significant_correlations(correlations)
    
    # Step 5: Generate report
    reporter = CorrelationReporter()
    significant_count = reporter.count_significant_pairs(significant_correlations)
    summary = reporter.generate_summary_stats(correlations)
    summary['significant_count'] = significant_count
    
    # Determine gate result
    if significant_count >= config['min_significant_pairs']:
        gate_result = 'PASS'
    elif significant_count >= 1:
        gate_result = 'PARTIAL'
    else:
        gate_result = 'FAIL'
    
    summary['gate_result'] = gate_result
    
    # Step 6: Save results
    import json
    with open(config['correlations_json'], 'w') as f:
        json.dump(correlations, f, indent=2)
    with open(config['summary_json'], 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Step 7: Generate visualizations
    generate_all_figures(
        features_df, 
        rankings_df, 
        significant_correlations,
        config['figures_dir'],
        config['visualization_config']
    )
    
    print(f"\nGate Result: {gate_result}")
    print(f"Significant correlations: {significant_count}")
    
    return 0 if gate_result != 'FAIL' else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
```

---

## Output File Specifications

```python
# Expected output files
OUTPUT_SCHEMA = {
    'features.csv': {
        'format': 'CSV with header',
        'rows': 'N benchmarks',
        'columns': '~10 features (Tier 1 + Tier 2)',
        'index': 'benchmark_id'
    },
    
    'rankings.csv': {
        'format': 'CSV with header',
        'rows': 'N benchmarks',
        'columns': '4 method families',
        'values': 'ranking_percentile (0-100)'
    },
    
    'correlations.json': {
        'format': 'JSON',
        'structure': {
            'feature_vs_method': {
                'rho': 'float',
                'p_value': 'float',
                'significant': 'bool',
                'n_samples': 'int'
            }
        }
    },
    
    'summary_stats.json': {
        'format': 'JSON',
        'fields': [
            'significant_count',
            'mean_abs_rho',
            'median_p_value',
            'top_5_correlations',
            'inverse_correlations',
            'gate_result'
        ]
    },
    
    'analysis.log': {
        'format': 'Plain text',
        'content': 'Execution logs with timestamps'
    }
}

# Figure output specifications
FIGURE_OUTPUTS = {
    'gate_metrics.png': {
        'title': 'Gate Metrics: Top Correlations vs Threshold',
        'x_axis': 'Feature-Method Pairs',
        'y_axis': 'Spearman ρ',
        'mandatory': True
    },
    
    'heatmap.png': {
        'title': 'Feature-Method Correlation Matrix',
        'x_axis': 'Method Families',
        'y_axis': 'Features',
        'mandatory': True
    },
    
    'significance.png': {
        'title': 'Statistical Significance (p-values)',
        'x_axis': 'Feature-Method Pairs',
        'y_axis': 'p-value',
        'mandatory': True
    },
    
    'scatter.png': {
        'title': 'Top 3 Feature-Method Scatter Plots',
        'subplots': 3,
        'mandatory': True
    }
}
```

---

## Self-Validation Checklist

- [x] ONE format only (hardcoded dict, consistent with H-E1)
- [x] No ASCII diagrams
- [x] KB search result noted ("Applied: Standard Python Statistical Analysis Pattern")
- [x] Rationale only for non-standard values (all are standard scipy/matplotlib defaults)
- [x] Subtask count within budget (2+2 = 4/4 used for M1-4 and M1-8)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Inherited Configuration section with verified H-E1 schema
- [x] Field names verified from actual H-E1 code (lines 92-103)
- [x] Focus on statistical analysis configuration (no ML hyperparameters)

---

**Document Status:** Ready for Implementation (Phase 4)
**Next Step:** Phase 4 Coder Agent - Implement correlation analysis pipeline with these configurations
