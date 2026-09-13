"""
Utility functions for the experiment
"""
import logging
import sys
from datetime import datetime

def setup_logging(log_file: str = "log.txt"):
    """Setup logging configuration"""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    logger.handlers = []

    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def log_experiment_start(logger, config_dict: dict):
    """Log experiment start with configuration"""
    logger.info("="*80)
    logger.info("NEURAL-SYMBOLIC REPAIR EXPERIMENT")
    logger.info("="*80)
    logger.info(f"Start time: {datetime.now()}")
    logger.info("")
    logger.info("Configuration:")
    for key, value in config_dict.items():
        logger.info(f"  {key}: {value}")
    logger.info("="*80)

def log_experiment_end(logger):
    """Log experiment end"""
    logger.info("="*80)
    logger.info(f"Experiment completed at: {datetime.now()}")
    logger.info("="*80)

def extract_function_from_code(code: str) -> str:
    """Extract just the function definition from code"""
    lines = code.split('\n')
    function_lines = []
    in_function = False

    for line in lines:
        if line.strip().startswith('def '):
            in_function = True
        if in_function:
            function_lines.append(line)
            # Simple heuristic: stop at next function or class definition
            if line.strip() and not line.strip().startswith('#') and \
               (line.strip().startswith('def ') or line.strip().startswith('class ')) \
               and len(function_lines) > 1:
                function_lines.pop()
                break

    return '\n'.join(function_lines) if function_lines else code

def code_similarity(code1: str, code2: str) -> float:
    """Simple code similarity metric (normalized edit distance)"""
    if code1 == code2:
        return 1.0

    # Simple character-level similarity
    len_max = max(len(code1), len(code2))
    if len_max == 0:
        return 1.0

    # Count matching characters
    matches = sum(1 for a, b in zip(code1, code2) if a == b)
    return matches / len_max
