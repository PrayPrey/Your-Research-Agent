"""
H-E1 Results Loader for Mechanism Analysis
"""
import pandas as pd
from typing import Dict, List
from config import AnalysisConfig

class H_E1_ResultsLoader:
    """Load and parse H-E1 profiling results"""
    
    def __init__(self, csv_path: str = AnalysisConfig.H_E1_RESULTS_PATH):
        self.csv_path = csv_path
        self.data = None
    
    def load_results(self) -> Dict[str, dict]:
        """
        Load signatures.csv from H-E1 and return structured data
        
        Returns:
            Dict mapping model names to their metrics and alignment type
        """
        df = pd.read_csv(self.csv_path)
        
        # Convert to dictionary format
        data = {}
        for _, row in df.iterrows():
            model = row['model']
            data[model] = {
                'alignment_type': row['alignment_type'],
                'correctness': row['correctness'],
                'cyclomatic': row['cyclomatic'],
                'ast_depth': row['ast_depth'],
                'runtime_ms': row['runtime_ms'],
                'memory_kb': row['memory_kb']
            }
        
        self.data = data
        return data
    
    def get_models_by_type(self, alignment_type: str) -> List[str]:
        """Get list of models for a specific alignment type"""
        if self.data is None:
            self.load_results()
        
        return [model for model, info in self.data.items() 
                if info['alignment_type'] == alignment_type]
