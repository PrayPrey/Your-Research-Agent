import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from typing import Dict, List

class ErrorAnalyzer:
    def __init__(self):
        pass
    
    def compute_relative_error(self, predicted: float, ground_truth: float) -> float:
        return abs(predicted - ground_truth) / ground_truth
    
    def aggregate_errors(self, errors: List[float]) -> Dict[str, float]:
        errors_array = np.array(errors)
        return {
            'median': float(np.median(errors_array)),
            'p95': float(np.percentile(errors_array, 95)),
            'mean': float(np.mean(errors_array)),
            'std': float(np.std(errors_array))
        }
    
    def compare_methods(self, method_a: List[float], method_b: List[float]) -> Dict:
        statistic, p_value = wilcoxon(method_a, method_b, alternative='less')
        
        return {
            'statistic': float(statistic),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'method_a_median': float(np.median(method_a)),
            'method_b_median': float(np.median(method_b))
        }
    
    def generate_report(self, results: pd.DataFrame) -> Dict:
        cnn_results = results[results['model'].isin([
            'resnet18', 'resnet34', 'resnet50', 'vgg16',
            'densenet121', 'mobilenet_v2', 'efficientnet_b0', 'shufflenet_v2_x1_0'
        ])]
        
        transformer_results = results[~results['model'].isin(cnn_results['model'].unique())]
        
        cnn_errors = cnn_results['relative_error'].tolist()
        transformer_errors = transformer_results['relative_error'].tolist()
        all_errors = results['relative_error'].tolist()
        
        return {
            'cnn': self.aggregate_errors(cnn_errors) if cnn_errors else None,
            'transformer': self.aggregate_errors(transformer_errors) if transformer_errors else None,
            'all': self.aggregate_errors(all_errors)
        }
    
    def export_to_csv(self, results: pd.DataFrame, filepath: str) -> None:
        results.to_csv(filepath, index=False)
