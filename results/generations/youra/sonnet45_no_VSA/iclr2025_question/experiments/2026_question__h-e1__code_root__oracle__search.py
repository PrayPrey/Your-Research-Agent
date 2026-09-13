"""Oracle hyperparameter search via grid search."""

import numpy as np
from typing import List, Tuple, Dict
from sklearn.metrics import roc_auc_score
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uncertainty.semantic_entropy import SemanticEntropy
from uncertainty.kernel_entropy import KernelEntropy


class OracleSearch:
    """Grid search for optimal hyperparameters."""
    
    def __init__(self, dev_data: List[Dict], dev_labels: np.ndarray):
        self.dev_data = dev_data
        self.dev_labels = dev_labels
    
    def search_epsilon(self, grid: List[float], similarity_matrices: List[np.ndarray]) -> Tuple[float, float]:
        """Search optimal SE threshold.
        
        Args:
            grid: List of epsilon values to try
            similarity_matrices: List of similarity matrices for dev set
            
        Returns:
            (best_epsilon, best_auroc)
        """
        best_epsilon = None
        best_auroc = 0.0
        
        print(f"Oracle search for epsilon: {grid}")
        
        for eps in grid:
            se = SemanticEntropy(eps)
            entropies = []
            
            for S in similarity_matrices:
                H = se.compute(S)
                entropies.append(H)
            
            entropies = np.array(entropies)
            
            # Negative entropy: lower entropy = more confident
            auroc = roc_auc_score(self.dev_labels, -entropies)
            
            print(f"  epsilon={eps:.2f}: AUROC={auroc:.4f}")
            
            if auroc > best_auroc:
                best_auroc = auroc
                best_epsilon = eps
        
        print(f"Best epsilon: {best_epsilon} (AUROC={best_auroc:.4f})")
        return best_epsilon, best_auroc
    
    def search_sigma(self, grid: List[float], similarity_matrices: List[np.ndarray]) -> Tuple[float, float]:
        """Search optimal KLE bandwidth.
        
        Args:
            grid: List of sigma values to try
            similarity_matrices: List of similarity matrices for dev set
            
        Returns:
            (best_sigma, best_auroc)
        """
        best_sigma = None
        best_auroc = 0.0
        
        print(f"Oracle search for sigma: {grid}")
        
        for sig in grid:
            kle = KernelEntropy(sig)
            entropies = []
            
            for S in similarity_matrices:
                try:
                    H, _ = kle.compute(S)
                    entropies.append(H)
                except ValueError as e:
                    print(f"  Warning: sigma={sig:.2f} failed: {e}")
                    entropies.append(np.nan)
            
            entropies = np.array(entropies)
            
            # Skip if too many failures
            if np.isnan(entropies).sum() > len(entropies) * 0.1:
                print(f"  sigma={sig:.2f}: SKIPPED (too many failures)")
                continue
            
            # Filter NaNs
            valid = ~np.isnan(entropies)
            if valid.sum() < 0.9 * len(entropies):
                continue
            
            auroc = roc_auc_score(self.dev_labels[valid], -entropies[valid])
            
            print(f"  sigma={sig:.2f}: AUROC={auroc:.4f}")
            
            if auroc > best_auroc:
                best_auroc = auroc
                best_sigma = sig
        
        print(f"Best sigma: {best_sigma} (AUROC={best_auroc:.4f})")
        return best_sigma, best_auroc
    
    def pre_gate(self, kle_auroc: float, se_auroc: float, thresh: float = 0.03) -> bool:
        """Check oracle pre-gate: KLE improvement >= threshold.
        
        Args:
            kle_auroc: Best KLE AUROC on dev set
            se_auroc: Best SE AUROC on dev set
            thresh: Minimum required improvement
            
        Returns:
            True if gate passes
        """
        improvement = kle_auroc - se_auroc
        passed = improvement >= thresh
        
        print(f"\nOracle Pre-Gate:")
        print(f"  KLE AUROC: {kle_auroc:.4f}")
        print(f"  SE AUROC: {se_auroc:.4f}")
        print(f"  Improvement: {improvement:.4f} (threshold: {thresh:.2f})")
        print(f"  Result: {'PASS ✅' if passed else 'FAIL ❌ ROUTE_TO_PHASE_0'}")
        
        return passed
