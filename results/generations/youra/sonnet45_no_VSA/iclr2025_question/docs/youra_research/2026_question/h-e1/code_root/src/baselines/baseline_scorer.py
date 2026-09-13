"""Baseline uncertainty scoring methods."""

import torch
import torch.nn.functional as F
import logging
from typing import Dict, List
import numpy as np

logger = logging.getLogger(__name__)


class MSPScorer:
    """Maximum Softmax Probability baseline."""
    
    def compute_score(self, logits: torch.Tensor) -> float:
        """Compute MSP from final token logits.
        
        Returns uncertainty score = 1 - max(softmax(logits)).
        """
        if logits is None:
            return 0.0
        
        probs = F.softmax(logits, dim=-1)
        max_prob = torch.max(probs).item()
        return 1.0 - max_prob


class TokenEntropyScorer:
    """Token-level entropy baseline."""
    
    def compute_score(self, logits: torch.Tensor) -> float:
        """Compute entropy of final token distribution."""
        if logits is None:
            return 0.0
        
        probs = F.softmax(logits, dim=-1)
        log_probs = torch.log(probs + 1e-10)
        entropy = -torch.sum(probs * log_probs).item()
        return entropy


class BaselineRunner:
    """Run all baseline scorers on generated answers."""
    
    def __init__(self):
        self.msp_scorer = MSPScorer()
        self.entropy_scorer = TokenEntropyScorer()
    
    def compute_all_baselines(
        self,
        generations: Dict[int, List],
        samples: List[Dict]
    ) -> Dict[str, Dict[int, float]]:
        """Compute MSP and Token Entropy scores for all questions."""
        logger.info("Computing baseline uncertainty scores")
        
        msp_scores = {}
        entropy_scores = {}
        
        for sample in samples:
            example_id = sample['example_id']
            if example_id not in generations:
                continue
            
            answers = generations[example_id]
            
            # Average scores across all generated answers
            msp_vals = []
            entropy_vals = []
            
            for answer in answers:
                if answer.logits is not None:
                    msp_vals.append(self.msp_scorer.compute_score(answer.logits))
                    entropy_vals.append(self.entropy_scorer.compute_score(answer.logits))
            
            msp_scores[example_id] = np.mean(msp_vals) if msp_vals else 0.0
            entropy_scores[example_id] = np.mean(entropy_vals) if entropy_vals else 0.0
        
        logger.info(f"Computed baselines for {len(msp_scores)} questions")
        
        return {
            'msp': msp_scores,
            'token_entropy': entropy_scores
        }
