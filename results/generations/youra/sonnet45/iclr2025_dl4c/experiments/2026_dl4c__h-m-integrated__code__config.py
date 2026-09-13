"""
Configuration for H-M-integrated Mechanism Analysis
"""
from pathlib import Path

# Get project root
CODE_DIR = Path(__file__).parent
HYPOTHESIS_DIR = CODE_DIR.parent
RESEARCH_DIR = HYPOTHESIS_DIR.parent

class AnalysisConfig:
    # Data paths
    H_E1_RESULTS_PATH = str(RESEARCH_DIR / "h-e1" / "results" / "signatures.csv")
    
    # Dimensions for analysis
    DIMENSIONS = ["correctness", "cyclomatic", "ast_depth", "runtime_ms", "memory_kb"]
    
    # Mechanism thresholds
    M1_THRESHOLD = 15.0   # Execution models should be in top 15% for correctness
    M2_THRESHOLD = 30.0   # Preference models should be in top 30% across all dimensions
    M3_PVALUE_THRESHOLD = 0.05  # Statistical significance threshold
    
    # Random seed for reproducibility
    RANDOM_SEED = 42
    
    # Output directories  
    OUTPUT_DIR = str(CODE_DIR / "results")
    FIGURE_DIR = str(CODE_DIR / "figures")
    
    # Alignment method types
    ALIGNMENT_METHODS = ["execution", "preference", "baseline"]
