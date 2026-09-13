"""
Statistical Tests for M1, M2, M3 Mechanism Hypotheses
"""
import numpy as np
from typing import Dict
from config import AnalysisConfig

class MechanismTester:
    """Test M1, M2, M3 mechanism hypotheses"""
    
    def __init__(self, data: Dict[str, dict], ranks: Dict[str, Dict[str, float]]):
        self.data = data
        self.ranks = ranks
    
    def test_m1_execution_dominance(self) -> dict:
        """
        Test M1: Execution-focused models dominate correctness dimension
        (top 15% pass@k rank)
        
        Criterion: mean(execution_correctness_ranks) ≤ 15.0
        """
        # Get execution models
        execution_models = [
            model for model, info in self.data.items()
            if info['alignment_type'] == 'execution'
        ]
        
        # Get their correctness ranks
        correctness_ranks = [
            self.ranks[model]['correctness'] 
            for model in execution_models
            if model in self.ranks
        ]
        
        # Compute mean rank
        mean_rank = np.mean(correctness_ranks) if correctness_ranks else 100.0
        
        # M1 passes if mean rank ≤ 15%
        m1_passed = mean_rank <= AnalysisConfig.M1_THRESHOLD
        
        return {
            'execution_models': execution_models,
            'correctness_ranks': correctness_ranks,
            'mean_rank': mean_rank,
            'threshold': AnalysisConfig.M1_THRESHOLD,
            'm1_passed': m1_passed
        }
    
    def test_m2_preference_balance(self) -> dict:
        """
        Test M2: Preference-focused models show balanced performance
        (top 30% across all dimensions)
        
        Criterion: mean(preference_all_dimension_ranks) ≤ 30.0
        """
        # Get preference models
        preference_models = [
            model for model, info in self.data.items()
            if info['alignment_type'] == 'preference'
        ]
        
        # Get all dimension ranks for preference models
        all_ranks = []
        for model in preference_models:
            if model in self.ranks:
                model_ranks = list(self.ranks[model].values())
                all_ranks.extend(model_ranks)
        
        # Compute mean across all dimensions
        mean_rank = np.mean(all_ranks) if all_ranks else 100.0
        
        # M2 passes if mean rank ≤ 30%
        m2_passed = mean_rank <= AnalysisConfig.M2_THRESHOLD
        
        return {
            'preference_models': preference_models,
            'all_dimension_ranks': all_ranks,
            'mean_rank': mean_rank,
            'threshold': AnalysisConfig.M2_THRESHOLD,
            'm2_passed': m2_passed
        }
    
    def test_all_mechanisms(self, variance_results: dict) -> dict:
        """
        Test all three mechanisms
        
        Returns:
            Combined results for M1, M2, M3
        """
        m1_results = self.test_m1_execution_dominance()
        m2_results = self.test_m2_preference_balance()
        
        return {
            'm1': m1_results,
            'm2': m2_results,
            'm3': variance_results,
            'gate_passed': m1_results['m1_passed'] and m2_results['m2_passed']
        }
