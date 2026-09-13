"""Beam search with validity tracking."""

from beam_search_custom import run_beam_search_scored
from beam_validity_tracker import BeamValidityTracker


def run_beam_search_with_tracking(
    model,
    tokenizer,
    prompt: str,
    k: int,
    alpha: float,
    beta: float,
    max_tokens: int
) -> tuple[list[str], dict]:
    """
    Run beam search with per-step validity tracking.

    Returns:
        (outputs, tracking_data):
            outputs: [k] generated code strings
            tracking_data: {
                'reduction_rate': float,
                'temporal_log': list[dict],
                'phase_stats': dict,
                'final_validity': list[bool]
            }
    """
    tracker = BeamValidityTracker()

    # Run standard beam search (h-m2)
    outputs, logs = run_beam_search_scored(
        model, tokenizer, prompt, k, alpha, beta, max_tokens
    )

    # Track final beams (simulate per-step with single final state)
    # Note: HuggingFace generate() doesn't expose intermediate beams,
    # so we track only final k outputs as "step T"
    tracker.track_step(step_id=0, beams=outputs)

    reduction_rate = tracker.compute_reduction()
    temporal_log = tracker.get_temporal_log()
    phase_stats = tracker.get_phase_stats(total_steps=1)  # Single step for final

    # Extract final validity
    final_validity = [log['validity'] for log in logs]

    return outputs, {
        'reduction_rate': reduction_rate,
        'temporal_log': temporal_log,
        'phase_stats': phase_stats,
        'final_validity': final_validity
    }
