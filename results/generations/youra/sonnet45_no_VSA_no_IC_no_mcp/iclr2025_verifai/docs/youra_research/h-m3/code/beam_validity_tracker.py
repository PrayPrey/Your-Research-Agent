"""Beam validity tracker for temporal pruning analysis."""

from ast_validator import validate_syntax_timed
import numpy as np


class BeamValidityTracker:
    """Track beam validity states over generation timeline."""

    def __init__(self):
        self.step_log = []  # [{step, invalid_count, invalid_proportion}]
        self.beam_states = []  # [{step, beam_id, validity}]

    def track_step(self, step_id: int, beams: list[str]) -> None:
        """
        Log validity for all beams at generation step.
        beams: [k] code strings
        """
        invalid_count = 0
        for i, code in enumerate(beams):
            valid, _ = validate_syntax_timed(code)
            self.beam_states.append({
                'step': step_id,
                'beam_id': i,
                'validity': valid
            })
            if not valid:
                invalid_count += 1

        invalid_proportion = invalid_count / len(beams) if beams else 0.0
        self.step_log.append({
            'step': step_id,
            'invalid_count': invalid_count,
            'invalid_proportion': invalid_proportion
        })

    def compute_reduction(self) -> float:
        """
        Reduction rate: (initial_invalid - final_invalid) / initial_invalid.
        Returns: 0.0 if initial=0 (no invalid beams to prune)
        """
        if len(self.step_log) < 2:
            return 0.0
        initial = self.step_log[0]['invalid_proportion']
        final = self.step_log[-1]['invalid_proportion']
        if initial == 0.0:
            return 0.0
        return (initial - final) / initial

    def get_temporal_log(self) -> list[dict]:
        """Returns step_log."""
        return self.step_log

    def get_phase_stats(self, total_steps: int) -> dict:
        """
        Compute early/middle/late phase statistics.
        Returns: {early, middle, late} with invalid_proportion means
        """
        early_end = total_steps // 3
        middle_end = 2 * total_steps // 3

        early = [s['invalid_proportion'] for s in self.step_log if s['step'] < early_end]
        middle = [s['invalid_proportion'] for s in self.step_log if early_end <= s['step'] < middle_end]
        late = [s['invalid_proportion'] for s in self.step_log if s['step'] >= middle_end]

        return {
            'early': float(np.mean(early)) if early else 0.0,
            'middle': float(np.mean(middle)) if middle else 0.0,
            'late': float(np.mean(late)) if late else 0.0
        }

    def reset(self):
        self.step_log = []
        self.beam_states = []
