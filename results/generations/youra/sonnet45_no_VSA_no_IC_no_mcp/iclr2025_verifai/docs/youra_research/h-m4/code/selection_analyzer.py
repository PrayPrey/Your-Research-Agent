"""Selection quality analyzer for h-m4."""

import sys
sys.path.insert(0, '../../h-m3/code')

from ast_validator import validate_syntax_timed


class SelectionAnalyzer:
    """Analyze selection quality by beam availability."""

    @staticmethod
    def compute_selection_accuracy(
        all_beams: list[list[str]],
        selected_indices: list[int]
    ) -> dict:
        """
        Compute selection accuracy when valid beams available.

        Args:
            all_beams: [N][k] all beam candidates per problem
            selected_indices: [N] selected beam index per problem

        Returns:
            {
                'accuracy_1plus': float,  # ≥1 valid beam available
                'accuracy_3plus': float,  # ≥3 valid beams available
                'miss_rate': float
            }
        """
        correct_1plus = 0
        total_1plus = 0
        correct_3plus = 0
        total_3plus = 0
        misses = 0

        for beams, selected_idx in zip(all_beams, selected_indices):
            validity = [validate_syntax_timed(b)[0] for b in beams]
            valid_count = sum(validity)
            selected_valid = validity[selected_idx]

            if valid_count >= 1:
                total_1plus += 1
                if selected_valid:
                    correct_1plus += 1
                else:
                    misses += 1

            if valid_count >= 3:
                total_3plus += 1
                if selected_valid:
                    correct_3plus += 1

        return {
            'accuracy_1plus': correct_1plus / total_1plus if total_1plus > 0 else 0.0,
            'accuracy_3plus': correct_3plus / total_3plus if total_3plus > 0 else 0.0,
            'miss_rate': misses / total_1plus if total_1plus > 0 else 0.0
        }
