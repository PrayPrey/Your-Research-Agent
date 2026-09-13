"""Strategy comparison for selection methods."""

import sys
sys.path.insert(0, '../../h-m3/code')

import random
import numpy as np
from ast_validator import validate_syntax_timed


class StrategyComparator:
    """Compare alternative selection strategies."""

    @staticmethod
    def compare_strategies(
        all_beams: list[list[str]],
        all_scores: list[list[float]]
    ) -> dict:
        """
        Test argmax, validity-first, random-valid strategies.

        Args:
            all_beams: [N][k] beam candidates
            all_scores: [N][k] final scores

        Returns:
            {
                'argmax_validity': float,
                'validity_first_validity': float,
                'random_valid_validity': float,
                'best_strategy': str
            }
        """
        # Strategy 1: argmax(final_score) - current
        argmax_selected = [beams[int(np.argmax(scores))] for beams, scores in zip(all_beams, all_scores)]
        argmax_valid = sum(validate_syntax_timed(b)[0] for b in argmax_selected) / len(argmax_selected)

        # Strategy 2: validity-first (argmax validity, tie-break by score)
        validity_first_selected = []
        for beams, scores in zip(all_beams, all_scores):
            validity = [validate_syntax_timed(b)[0] for b in beams]
            if any(validity):
                # Pick highest-scoring valid beam
                valid_indices = [i for i, v in enumerate(validity) if v]
                best_valid = max(valid_indices, key=lambda i: scores[i])
                validity_first_selected.append(beams[best_valid])
            else:
                # Fallback to argmax score
                validity_first_selected.append(beams[int(np.argmax(scores))])
        vf_valid = sum(validate_syntax_timed(b)[0] for b in validity_first_selected) / len(validity_first_selected)

        # Strategy 3: random from valid beams
        random.seed(42)
        random_valid_selected = []
        for beams in all_beams:
            validity = [validate_syntax_timed(b)[0] for b in beams]
            valid_beams = [b for b, v in zip(beams, validity) if v]
            if valid_beams:
                random_valid_selected.append(random.choice(valid_beams))
            else:
                random_valid_selected.append(random.choice(beams))
        rv_valid = sum(validate_syntax_timed(b)[0] for b in random_valid_selected) / len(random_valid_selected)

        results = {
            'argmax': argmax_valid,
            'validity_first': vf_valid,
            'random_valid': rv_valid
        }
        best_strategy = max(results, key=results.get)

        return {
            'argmax_validity': argmax_valid,
            'validity_first_validity': vf_valid,
            'random_valid_validity': rv_valid,
            'best_strategy': best_strategy
        }
