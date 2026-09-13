"""
Percentile Ranking Analyzer for Mechanism Analysis
"""
from scipy.stats import percentileofscore
import numpy as np
from typing import Dict
from config import AnalysisConfig

class PercentileRankingAnalyzer:
    """Compute percentile ranks for each model on each dimension"""
    
    def __init__(self, data: Dict[str, dict]):
        self.data = data
        self.ranks = {}
    
    def compute_dimension_ranks(self, dimension: str) -> Dict[str, float]:
        """
        Compute percentile rank for all models on a single dimension
        
        LOWER percentile rank = BETTER performance (top 15% means rank ≤ 15)
        
        - Correctness: HIGHER score is better
          → Use percentileofscore normally, then INVERT (100 - percentile)
        - Cyclomatic/AST/Runtime/Memory: LOWER score is better
          → Use percentileofscore directly (lower values naturally get lower percentiles)
        
        Args:
            dimension: Dimension name (e.g., 'correctness')
        
        Returns:
            Dict mapping model names to percentile ranks (0-100)
        """
        # Extract scores for this dimension
        scores = [info[dimension] for info in self.data.values()]
        
        # Compute percentile for each model
        ranks = {}
        for model, info in self.data.items():
            score = info[dimension]
            
            if dimension == 'correctness':
                # Higher correctness is better → invert percentile
                # Score 0.95 in [0.5, 0.6, 0.7, 0.95] → 100th percentile → inv to 0% (best)
                percentile = 100.0 - percentileofscore(scores, score, kind='rank')
            else:
                # Lower complexity/runtime/memory is better → use direct percentile
                # Score 5 in [5, 10, 15, 20] → 25th percentile (best, lowest rank)
                percentile = percentileofscore(scores, score, kind='rank')
            
            ranks[model] = percentile
        
        return ranks
    
    def compute_all_ranks(self) -> Dict[str, Dict[str, float]]:
        """
        Compute percentile ranks for all dimensions
        
        Returns:
            Dict mapping model names to dict of dimension:rank pairs
        """
        all_ranks = {}
        
        for dimension in AnalysisConfig.DIMENSIONS:
            dim_ranks = self.compute_dimension_ranks(dimension)
            
            for model, rank in dim_ranks.items():
                if model not in all_ranks:
                    all_ranks[model] = {}
                all_ranks[model][dimension] = rank
        
        self.ranks = all_ranks
        return all_ranks
