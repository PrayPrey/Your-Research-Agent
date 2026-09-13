"""
Variance Analyzer for Within/Between-Method Clustering
"""
import numpy as np
from scipy.stats import mannwhitneyu
from typing import Dict, List
from config import AnalysisConfig

class VarianceAnalyzer:
    """Analyze intra/inter variance by alignment method"""
    
    def __init__(self, data: Dict[str, dict]):
        self.data = data
    
    def group_by_alignment_method(self, dimension: str) -> Dict[str, List[float]]:
        """Group scores by alignment method for a specific dimension"""
        groups = {method: [] for method in AnalysisConfig.ALIGNMENT_METHODS}
        
        for model, info in self.data.items():
            alignment_type = info['alignment_type']
            score = info[dimension]
            if alignment_type in groups:
                groups[alignment_type].append(score)
        
        return groups
    
    def compute_intra_variance(self, group_scores: List[float]) -> float:
        """Compute within-group variance"""
        return np.var(group_scores, ddof=1) if len(group_scores) > 1 else 0.0
    
    def compute_inter_distance(self, group1: List[float], group2: List[float]) -> float:
        """Compute between-group distance (mean difference)"""
        return abs(np.mean(group1) - np.mean(group2))
    
    def test_m3_clustering(self, dimension: str = 'correctness') -> dict:
        """
        Test M3: Training dynamics create consistent within-method clustering
        (intracluster variance < intercluster distance)
        
        Returns:
            dict with test results and statistics
        """
        groups = self.group_by_alignment_method(dimension)
        
        # Compute intra-cluster variance for each group
        intra_variances = {
            method: self.compute_intra_variance(scores)
            for method, scores in groups.items() if len(scores) > 0
        }
        
        # Compute inter-cluster distances
        execution_scores = groups.get('execution', [])
        baseline_scores = groups.get('baseline', [])
        
        # Mann-Whitney U test between execution and baseline
        if len(execution_scores) > 0 and len(baseline_scores) > 0:
            stat, pvalue = mannwhitneyu(execution_scores, baseline_scores, alternative='two-sided')
        else:
            stat, pvalue = None, 1.0
        
        # M3 passes if p < 0.05 (significant clustering difference)
        m3_passed = pvalue < AnalysisConfig.M3_PVALUE_THRESHOLD if pvalue is not None else False
        
        return {
            'intra_variances': intra_variances,
            'mean_intra_variance': np.mean(list(intra_variances.values())) if intra_variances else 0.0,
            'mannwhitneyu_stat': stat,
            'mannwhitneyu_pvalue': pvalue,
            'm3_passed': m3_passed
        }
