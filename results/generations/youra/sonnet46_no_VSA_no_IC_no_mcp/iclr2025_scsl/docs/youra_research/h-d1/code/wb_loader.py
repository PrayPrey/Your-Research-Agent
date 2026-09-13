import csv
import json
import os
import numpy as np
from config import WB_RATIOS_CSV


def load_wb_results(path=None):
    """
    Load H-E1 WB results from CSV (h-e1_ratios.csv).
    Returns {'erm': [...], 'moco': [...], 'dino': [...], 'barlowtwins': [...]}
    """
    if path is None:
        path = WB_RATIOS_CSV

    results = {}
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            paradigm = row['paradigm']
            ratio = float(row['ratio'])
            if paradigm not in results:
                results[paradigm] = []
            results[paradigm].append(ratio)

    # Validate
    expected = {'erm', 'moco', 'dino', 'barlowtwins'}
    if not expected.issubset(set(results.keys())):
        raise ValueError(f"Missing paradigms in WB results: {expected - set(results.keys())}")
    for p, ratios in results.items():
        if len(ratios) != 5:
            raise ValueError(f"Expected 5 seeds for {p}, got {len(ratios)}")

    return results


def extract_primary(wb_results):
    """Returns (erm_ratios, moco_ratios) as np.ndarray shape (5,)."""
    return np.array(wb_results['erm']), np.array(wb_results['moco'])
