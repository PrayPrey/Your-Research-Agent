"""Custom beam search with combined scoring."""

import torch
from typing import Tuple
from scoring import combined_score, rank_beams


class CustomBeamScorer:
    """Track and score beam candidates with combined scoring."""

    def __init__(self, alpha: float = 0.7, beta: float = 0.3):
        self.alpha = alpha
        self.beta = beta
        self.step_logs = []

    def score_candidates(
        self,
        candidates: list,
        log_probs: list
    ) -> list:
        """
        Score each beam candidate.

        Args:
            candidates: List of k code strings
            log_probs: List of k log-likelihood values

        Returns:
            List of k final scores
        """
        final_scores = []
        for cand, logp in zip(candidates, log_probs):
            score, _, _ = combined_score(logp, cand, self.alpha, self.beta)
            final_scores.append(score)
        return final_scores

    def log_step(
        self,
        step: int,
        candidates: list,
        scores: list,
        ranks: list
    ):
        """
        Log beam state at generation step.

        Args:
            step: Generation step number
            candidates: List of k code strings
            scores: List of k final scores
            ranks: List of k rank indices
        """
        for i, (cand, score, rank) in enumerate(zip(candidates, scores, ranks)):
            _, validity, elapsed_ms = combined_score(0.0, cand, self.alpha, self.beta)
            self.step_logs.append({
                'step': step,
                'beam_id': i,
                'score': score,
                'rank': rank,
                'validity': validity,
                'elapsed_ms': elapsed_ms
            })

    def get_logs(self) -> list:
        return self.step_logs

    def reset(self):
        self.step_logs = []


def run_beam_search_scored(
    model,
    tokenizer,
    prompt: str,
    k: int,
    alpha: float,
    beta: float,
    max_tokens: int
) -> Tuple[list, list]:
    """
    Run beam search and score outputs with combined scoring.

    Args:
        model: HuggingFace model
        tokenizer: HuggingFace tokenizer
        prompt: Input prompt
        k: Beam width
        alpha: Log-likelihood weight
        beta: Syntax validity weight
        max_tokens: Max new tokens

    Returns:
        (outputs, logs): List of k generated outputs and scoring logs
    """
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            num_beams=k,
            num_return_sequences=k,
            max_new_tokens=max_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            output_scores=True,
            return_dict_in_generate=True
        )

    candidates = tokenizer.batch_decode(
        outputs.sequences,
        skip_special_tokens=True
    )
    candidates = [c[len(prompt):].strip() for c in candidates]

    # Score all candidates post-generation
    logs = []
    for i, cand in enumerate(candidates):
        # Use dummy log_prob=0.0 for AST-only validation
        final_score, validity, elapsed_ms = combined_score(0.0, cand, alpha, beta)
        logs.append({
            'beam_id': i,
            'score': final_score,
            'validity': validity,
            'elapsed_ms': elapsed_ms
        })

    return candidates, logs
